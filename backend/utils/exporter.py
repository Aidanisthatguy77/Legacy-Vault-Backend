"""
Full System Export - packages the entire vault for download
"""
import os
import json
import shutil
import zipfile
import tempfile
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from motor.motor_asyncio import AsyncIOMotorClient

DB_NAME = os.environ.get("DB_NAME", "vault_legacy")
MONGO_URL = os.environ.get("MONGO_URL", "mongodb://localhost:27017")

def _now():
    return datetime.now(timezone.utc).isoformat()

async def build_full_export() -> dict:
    """
    Build a complete export of:
    - All code (frontend + backend)
    - MongoDB data as JSON
    - Docker setup files
    - Environment templates
    """
    client = AsyncIOMotorClient(MONGO_URL)
    db = client[DB_NAME]
    
    # Create temp directory
    stage = Path(tempfile.mkdtemp())
    
    # Export collections to JSON
    collections = ["games", "clips", "mockups", "proofs", "comments", "subscribers", "submissions", "petition_signatures", "content"]
    data_dir = stage / "data"
    data_dir.mkdir(exist_ok=True)
    
    manifest = {
        "generated_at": _now(),
        "collections": {},
    }
    
    for coll_name in collections:
        docs = await db[coll_name].find({}, {"_id": 0}).to_list(10000)
        json_path = data_dir / f"{coll_name}.json"
        with open(json_path, "w") as f:
            json.dump(docs, f, indent=2)
        manifest["collections"][coll_name] = {
            "count": len(docs),
            "file": f"data/{coll_name}.json",
        }
    
    # Write manifest
    with open(stage / "MANIFEST.json", "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Write README
    readme = """# NBA 2K Legacy Vault - Full Export

## Quick Start
1. Install Docker and Docker Compose
2. Run: `docker-compose up -d`
3. Access frontend at http://localhost:3000
4. Access backend at http://localhost:8001

## Environment Variables
Copy .env.example to .env and fill in your values.

## Data Restore
Import JSON data: `docker exec -i vault_mongo mongorestore --drop < data/dump`
Or import individual collections from data/*.json
"""
    with open(stage / "README.md", "w") as f:
        f.write(readme)
    
    # Write docker-compose
    docker_compose = """version: '3.8'
services:
  mongo:
    image: mongo:7
    ports:
      - "27017:27017"
    volumes:
      - mongo_data:/data/db
      - ./data:/import
  backend:
    build: ./backend
    ports:
      - "8001:8001"
    env_file:
      - .env.backend
    depends_on:
      - mongo
  frontend:
    build: ./frontend
    ports:
      - "3000:3000"
    env_file:
      - .env.frontend
    depends_on:
      - backend
volumes:
  mongo_data:
"""
    with open(stage / "docker-compose.yml", "w") as f:
        f.write(docker_compose)
    
    # Write env templates
    with open(stage / ".env.backend.example", "w") as f:
        f.write("""MONGO_URL=mongodb://mongo:27017
DB_NAME=vault_legacy
ANTHROPIC_API_KEY=your-key-here
GOOGLE_API_KEY=your-key-here
ADMIN_PASSWORD=change-this-password
MONITOR_INTERVAL=60
""")
    
    with open(stage / ".env.frontend.example", "w") as f:
        f.write("""REACT_APP_BACKEND_URL=http://localhost:8001
""")
    
    # Create zip
    zip_path = stage.parent / f"vault_export_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in stage.walk():
            for file in files:
                file_path = root / file
                arcname = file_path.relative_to(stage)
                zf.write(file_path, arcname)
    
    # Cleanup stage
    shutil.rmtree(stage)
    
    client.close()
    
    return {
        "zip_path": str(zip_path),
        "zip_size": zip_path.stat().st_size,
        "manifest": manifest,
    }
