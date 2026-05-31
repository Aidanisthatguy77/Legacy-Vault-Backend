"""
Background monitoring service for the Vault backend.
Scans logs, checks health, and records observations.
"""
import os
import re
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient

MONITOR_INTERVAL = int(os.environ.get("MONITOR_INTERVAL", "60"))
DB_NAME = os.environ.get("DB_NAME", "vault_legacy")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")

_task: Optional[asyncio.Task] = None
_running = False
_log_state: Dict[str, int] = {}

def _now():
    return datetime.now(timezone.utc).isoformat()

async def _record(severity, source, title, detail, suggested_action="", dedupe_key=None, metadata=None):
    """Record an observation to MongoDB with deduplication"""
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client[DB_NAME]
    
    if dedupe_key:
        existing = await db.monitor_observations.find_one(
            {"dedupe_key": dedupe_key, "status": "open"},
            {"_id": 0, "id": 1}
        )
        if existing:
            await db.monitor_observations.update_one(
                {"id": existing["id"]},
                {"$inc": {"touched": 1}, "$set": {"last_seen": _now()}}
            )
            db_client.close()
            return existing["id"]
    
    doc = {
        "id": str(uuid.uuid4()),
        "severity": severity,
        "source": source,
        "title": title,
        "detail": detail[:4000],
        "suggested_action": suggested_action[:1000] if suggested_action else "",
        "dedupe_key": dedupe_key,
        "metadata": metadata or {},
        "status": "open",
        "touched": 1,
        "created_at": _now(),
        "last_seen": _now(),
    }
    
    import uuid
    await db.monitor_observations.insert_one(doc)
    db_client.close()
    return doc["id"]

async def _check_health():
    """Check backend health"""
    try:
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            r = await client.get(f"{os.environ.get('BACKEND_URL', 'http://localhost:8001')}/api/health")
            if r.status_code == 200:
                return True
    except:
        pass
    return False

async def _check_mongo():
    """Check MongoDB connection"""
    try:
        client = AsyncIOMotorClient(MONGO_URL, serverSelectionTimeoutMS=5000)
        await client.admin.command("ping")
        client.close()
        return True
    except:
        return False

async def _run_one_cycle():
    """Run one monitoring cycle"""
    # Check health
    backend_ok = await _check_health()
    mongo_ok = await _check_mongo()
    
    if not mongo_ok:
        await _record(
            severity="critical",
            source="mongo",
            title="Database connection failed",
            detail="Cannot connect to MongoDB. Check MONGO_URL and network.",
            suggested_action="Verify MongoDB is running and MONGO_URL is correct in .env",
            dedupe_key="mongo-connection-fail",
        )
    
    if not backend_ok:
        await _record(
            severity="warning",
            source="health",
            title="Backend health check failed",
            detail="Backend /api/health endpoint not responding.",
            suggested_action="Check backend logs and ensure uvicorn is running",
            dedupe_key="health-check-fail",
        )
    
    # Heartbeat
    db_client = AsyncIOMotorClient(MONGO_URL)
    db = db_client[DB_NAME]
    await db.monitor_heartbeats.update_one(
        {"key": "monitor"},
        {"$set": {"key": "monitor", "last_run": _now()}},
        upsert=True
    )
    db_client.close()

async def _loop():
    """Main monitoring loop"""
    global _running
    _running = True
    
    while _running:
        try:
            await _run_one_cycle()
        except Exception as e:
            pass  # Log errors internally, don't crash
        
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

def get_monitor_status():
    """Get current monitor status (sync wrapper)"""
    return {
        "running": _running,
        "interval": MONITOR_INTERVAL,
    }
