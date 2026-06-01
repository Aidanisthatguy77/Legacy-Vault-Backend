"""
Background monitoring service for the Vault backend.
Scans logs, checks health, and records observations with deduplication.
"""
import os
import re
import asyncio
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient

MONITOR_INTERVAL = int(os.environ.get("MONITOR_INTERVAL", "60"))
DB_NAME = os.environ.get("DB_NAME", "vault_legacy")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")
BACKEND_URL = os.environ.get("BACKEND_URL", "http://localhost:8001")

_task: Optional[asyncio.Task] = None
_running = False
_log_state: Dict[str, int] = {}

def _now(): return datetime.now(timezone.utc).isoformat()

async def _record(severity, source, title, detail, suggested_action="", dedupe_key=None, metadata=None):
    """Record observation with deduplication"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    if dedupe_key:
        existing = await db.monitor_observations.find_one(
            {"dedupe_key": dedupe_key, "status": "open"}, {"_id": 0, "id": 1}
        )
        if existing:
            await db.monitor_observations.update_one(
                {"id": existing["id"]},
                {"$inc": {"touched": 1}, "$set": {"last_seen": _now()}}
            )
            client.close()
            return existing["id"]
    
    doc = {
        "id": str(uuid.uuid4()),
        "severity": severity, "source": source, "title": title,
        "detail": detail[:4000], "suggested_action": suggested_action[:1000] if suggested_action else "",
        "dedupe_key": dedupe_key, "metadata": metadata or {},
        "status": "open", "touched": 1,
        "created_at": _now(), "last_seen": _now(),
    }
    await db.monitor_observations.insert_one(doc)
    client.close()
    return doc["id"]

async def _check_health():
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{BACKEND_URL}/api/health")
            return r.status_code == 200
    except: return False

async def _check_mongo():
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        client.close()
        return True
    except: return False

async def _check_sample_endpoints():
    """Check sample endpoints"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{BACKEND_URL}/api/games")
            return r.status_code == 200
    except: return False

async def _run_one_cycle():
    """Run one monitoring cycle"""
    # Health checks
    backend_ok = await _check_health()
    mongo_ok = await _check_mongo()
    endpoints_ok = await _check_sample_endpoints()
    
    if not mongo_ok:
        await _record("critical", "mongo", "Database connection failed",
            "Cannot connect to MongoDB. Check MONGO_URL and network.",
            "Verify MongoDB is running and MONGO_URL is correct", "mongo-connection-fail")
    elif backend_ok and endpoints_ok:
        # Clear any previous mongo errors
        await _clear_alert("mongo-connection-fail")
    
    if not backend_ok:
        await _record("warning", "health", "Backend health check failed",
            "Backend /api/health endpoint not responding.",
            "Check backend logs and ensure uvicorn is running", "health-check-fail")
    elif endpoints_ok:
        await _clear_alert("health-check-fail")
    
    # Heartbeat
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await db.monitor_heartbeats.update_one(
        {"key": "monitor"}, {"$set": {"key": "monitor", "last_run": _now()}}, upsert=True
    )
    client.close()

async def _clear_alert(dedupe_key: str):
    """Mark observation as fixed when issue resolves"""
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    await db.monitor_observations.update_many(
        {"dedupe_key": dedupe_key, "status": "open"},
        {"$set": {"status": "fixed"}}
    )
    client.close()

async def _loop():
    """Main monitoring loop"""
    global _running
    _running = True
    
    # Snapshot log positions on boot
    for key, path in [("backend", Path("/var/log/backend.log")), ("frontend", Path("/var/log/frontend.log"))]:
        if path.exists():
            _log_state[key] = path.stat().st_size
    
    while _running:
        try:
            await _run_one_cycle()
        except Exception as e:
            pass  # Don't crash the monitor
        await asyncio.sleep(MONITOR_INTERVAL)

def start_monitor():
    """Start the background monitoring task"""
    global _task
    if _task and not _task.done():
        return
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _task = loop.create_task(_loop())
    loop.run_forever()

def get_status():
    return {"running": _running, "interval": MONITOR_INTERVAL}
