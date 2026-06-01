"""NBA 2K Legacy Vault Backend - FastAPI + MongoDB"""
import os, re, uuid, json, asyncio
from datetime import datetime, timezone
from typing import Optional, List
from pathlib import Path
from fastapi import FastAPI, APIRouter, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import httpx
from bs4 import BeautifulSoup

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / ".env")

client = AsyncIOMotorClient(os.environ["MONGO_URL"])
db = client[os.environ["DB_NAME"]]
app = FastAPI()
api_router = APIRouter(prefix="/api")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "A@070610")
CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*").split(",")

app.add_middleware(CORSMiddleware, allow_credentials=True, allow_origins=CORS_ORIGINS, allow_methods=["*"], allow_headers=["*"])

# ============ HELPERS ============
def _now(): return datetime.now(timezone.utc).isoformat()

def verify_admin(req: Request):
    if req.headers.get("X-Admin-Password", "") != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")

async def fetch_url_content(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.get(url, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            for t in soup(["script", "style"]): t.decompose()
            return soup.get_text(separator=" ", strip=True)[:12000]
    except: return ""

def detect_media(message: str) -> bool:
    patterns = [r"youtube\.com", r"youtu\.be", r"twitter\.com", r"x\.com", r"reddit\.com", r"tiktok\.com", r"instagram\.com"]
    return any(re.search(p, message) for p in patterns)

async def call_llm(session_id: str, system: str, message: str, model: str = "gemini") -> str:
    """Call LLM via emergentintegrations - ONE key routes to Claude or Gemini"""
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        api_key = os.environ.get("EMERGENT_LLM_KEY", "")
        if not api_key: return None
        is_claude = "claude" in model
        model_name = "claude-sonnet-4-5-20250929" if is_claude else "gemini-2.5-flash"
        chat = LlmChat(api_key=api_key, session_id=session_id, system_message=system).with_model("anthropic" if is_claude else "gemini", model_name)
        return await chat.send_message(UserMessage(text=message))
    except: return None

def demo_response(msg: str) -> str:
    l = msg.lower()
    if "licensing" in l or "music" in l: return "Modular asset layers handle licensing."
    if "pilot" in l or "throwback" in l: return "48-hour NBA 2K16 Throwback Weekend. Budget under $750K."
    if "vault" in l or "legacy" in l: return "Legacy Vault = game-within-a-game."
    return "I am Vault AI! Ask about the Legacy Vault."

# Models
class GameBase(BaseModel):
    title: str; year: str; cover_image: str = ""; hook_text: str = ""; cover_athletes: str = ""; description: str = ""; order: int = 0; is_active: bool = True
class Game(GameBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
class GameUpdate(BaseModel):
    title: Optional[str] = None; year: Optional[str] = None; cover_image: Optional[str] = None; hook_text: Optional[str] = None; cover_athletes: Optional[str] = None; description: Optional[str] = None; order: Optional[int] = None; is_active: Optional[bool] = None

class ClipBase(BaseModel):
    title: str; url: str; platform: str = "youtube"; game_id: Optional[str] = None; order: int = 0; is_active: bool = True
class Clip(ClipBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class MockupBase(BaseModel):
    title: str; image_url: str; description: str = ""; order: int = 0; is_active: bool = True
class Mockup(MockupBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ProofBase(BaseModel):
    title: str; image_url: str; source_url: str = ""; is_active: bool = True
class Proof(ProofBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SubscriberCreate(BaseModel):
    email: str; subscribed: bool = True
class Subscriber(SubscriberCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class CommentCreate(BaseModel):
    author: str; content: str; game_id: Optional[str] = None
class Comment(CommentCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class PetitionCreate(BaseModel):
    name: str; handle: str = ""; location: str = ""
class Petition(PetitionCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class SubmissionCreate(BaseModel):
    name: str; email: str; content: str; type: str = "general"
class Submission(SubmissionCreate):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    status: str = "pending"
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

class ContentUpdate(BaseModel):
    key: str; value: str
class AdminLogin(BaseModel):
    password: str
class ChatRequest(BaseModel):
    message: str; session_id: str = ""
class ChatResponse(BaseModel):
    response: str; session_id: str; model_used: str = "gemini"
class DeployRunRequest(BaseModel):
    github_token: str = ""; github_repo: str = ""; atlas_token: str = ""; render_token: str = ""; vercel_token: str = ""

# Helpers
def _now(): return datetime.now(timezone.utc).isoformat()

def verify_admin(req: Request):
    if req.headers.get("X-Admin-Password", "") != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")

async def fetch_url(url: str) -> str:
    try:
        async with httpx.AsyncClient(timeout=15.0) as c:
            r = await c.get(url, follow_redirects=True, headers={"User-Agent": "Mozilla/5.0"})
            soup = BeautifulSoup(r.text, "html.parser")
            for t in soup(["script", "style"]): t.decompose()
            return soup.get_text(separator=" ", strip=True)[:12000]
    except: return ""

def has_media(msg: str) -> bool:
    patterns = [r"youtube\.com", r"youtu\.be", r"twitter\.com", r"x\.com", r"reddit\.com", r"tiktok\.com", r"instagram\.com"]
    return any(re.search(p, msg) for p in patterns)

def demo(msg: str) -> str:
    l = msg.lower()
    if "licensing" in l or "music" in l: return "Modular asset layers handle licensing. Expired music replaced, jerseys as packs."
    if "pilot" in l or "throwback" in l: return "48-hour NBA 2K16 Throwback Weekend. Budget under $750K. Target: 15-20% DAU uplift."
    if "scal" in l or "kubernetes" in l: return "Kubernetes = automatic scaling. Build once, run anywhere."
    if "vault" in l or "legacy" in l: return "Legacy Vault = game-within-a-game. Launch 2K15-2K20 inside modern 2K."
    return "I'm Vault AI! Ask about the Legacy Vault."

# Health
@app.get("/")
@app.get("/api/health")
async def health():
    try:
        await client.admin.command("ping")
        return {"status": "ok", "backend": "ok", "database": "ok", "timestamp": _now()}
    except:
        return {"status": "degraded", "backend": "ok", "database": "error", "timestamp": _now()}

@app.get("/api/health/pulse")
async def pulse(): return {"backend": "ok", "db": "ok"}

# Admin Auth
@api_router.post("/admin/login")
async def admin_login(body: AdminLogin):
    if body.password != ADMIN_PASSWORD: raise HTTPException(status_code=401, detail="Invalid password")
    return {"success": True, "message": "Login successful"}

# AI Chat (Dual Engine)
PLAIN_SYSTEM = "You are Vault AI for the NBA 2K Legacy Vault. Keep responses concise and helpful."

@api_router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    anthropic_key = os.environ.get("ANTHROPIC_API_KEY", "")
    google_key = os.environ.get("GOOGLE_API_KEY", "")
    response_text = ""; model_used = "demo"
    
    if has_media(req.message):
        scraped = [{"url": u, "content": await fetch_url(u)[:6000]} for u in re.findall(r"https?://\S+", req.message)[:3]]
        if anthropic_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as c:
                    r = await c.post("https://api.anthropic.com/v1/messages", headers={"Content-Type": "application/json", "x-api-key": anthropic_key, "anthropic-version": "2023-06-01"}, json={"model": "claude-3-haiku-20240307", "max_tokens": 500, "messages": [{"role": "user", "content": f"{PLAIN_SYSTEM}\n\nUser shared: {req.message}"}]})
                    data = r.json()
                    response_text = data.get("content", [{}])[0].get("text", "") or demo(req.message)
                model_used = "claude"
            except: response_text = demo(req.message)
        else: response_text = demo(req.message)
    else:
        if google_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as c:
                    r = await c.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_key}", headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": f"{PLAIN_SYSTEM}\n\nUser: {req.message}"}]}], "generationConfig": {"maxOutputTokens": 500}})
                    data = r.json()
                    response_text = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "") or demo(req.message)
                model_used = "gemini"
            except: response_text = demo(req.message)
        else: response_text = demo(req.message)
    
    await db.vault_chat_history.insert_one({"id": str(uuid.uuid4()), "session_id": session_id, "role": "user", "content": req.message, "timestamp": _now()})
    await db.vault_chat_history.insert_one({"id": str(uuid.uuid4()), "session_id": session_id, "role": "assistant", "content": response_text, "model_used": model_used, "timestamp": _now()})
    return ChatResponse(response=response_text, session_id=session_id, model_used=model_used)

@api_router.post("/vault-guide")
async def vault_guide(msg: ChatRequest):
    google_key = os.environ.get("GOOGLE_API_KEY", "")
    if google_key:
        try:
            async with httpx.AsyncClient(timeout=30.0) as c:
                r = await c.post(f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_key}", headers={"Content-Type": "application/json"}, json={"contents": [{"parts": [{"text": f"Vault Guide: {msg.message}"}]}], "generationConfig": {"maxOutputTokens": 300}})
                data = r.json()
                return {"response": data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "") or "Ready!"}
        except: pass
    return {"response": "Vault Guide ready!"}

# Games CRUD
@api_router.get("/games", response_model=List[Game])
async def get_games(): return await db.games.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.get("/games/all", response_model=List[Game])
async def get_all_games(): return await db.games.find({}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.post("/games", response_model=Game)
async def create_game(g: GameBase):
    game = Game(**g.model_dump())
    await db.games.insert_one(game.model_dump())
    return game

@api_router.put("/games/{game_id}", response_model=Game)
async def update_game(game_id: str, g: GameUpdate):
    patch = {k: v for k, v in g.model_dump().items() if v is not None}
    await db.games.update_one({"id": game_id}, {"$set": patch})
    return await db.games.find_one({"id": game_id}, {"_id": 0})

@api_router.delete("/games/{game_id}")
async def delete_game(game_id: str):
    await db.games.delete_one({"id": game_id})
    return {"deleted": True}

# Clips CRUD
@api_router.get("/clips", response_model=List[Clip])
async def get_clips(): return await db.clips.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.get("/clips/all", response_model=List[Clip])
async def get_all_clips(): return await db.clips.find({}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.post("/clips", response_model=Clip)
async def create_clip(c: ClipBase):
    clip = Clip(**c.model_dump())
    await db.clips.insert_one(clip.model_dump())
    return clip

@api_router.put("/clips/{clip_id}", response_model=Clip)
async def update_clip(clip_id: str, c: ClipBase):
    await db.clips.update_one({"id": clip_id}, {"$set": c.model_dump()})
    return await db.clips.find_one({"id": clip_id}, {"_id": 0})

@api_router.delete("/clips/{clip_id}")
async def delete_clip(clip_id: str):
    await db.clips.delete_one({"id": clip_id})
    return {"deleted": True}

# Mockups CRUD
@api_router.get("/mockups", response_model=List[Mockup])
async def get_mockups(): return await db.mockups.find({"is_active": True}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.get("/mockups/all", response_model=List[Mockup])
async def get_all_mockups(): return await db.mockups.find({}, {"_id": 0}).sort("order", 1).to_list(100)

@api_router.post("/mockups", response_model=Mockup)
async def create_mockup(m: MockupBase):
    mockup = Mockup(**m.model_dump())
    await db.mockups.insert_one(mockup.model_dump())
    return mockup

@api_router.put("/mockups/{mockup_id}", response_model=Mockup)
async def update_mockup(mockup_id: str, m: MockupBase):
    await db.mockups.update_one({"id": mockup_id}, {"$set": m.model_dump()})
    return await db.mockups.find_one({"id": mockup_id}, {"_id": 0})

@api_router.delete("/mockups/{mockup_id}")
async def delete_mockup(mockup_id: str):
    await db.mockups.delete_one({"id": mockup_id})
    return {"deleted": True}

# Proofs CRUD
@api_router.get("/proofs", response_model=List[Proof])
async def get_proofs(): return await db.proofs.find({"is_active": True}, {"_id": 0}).to_list(100)

@api_router.get("/proofs/all", response_model=List[Proof])
async def get_all_proofs(): return await db.proofs.find({}, {"_id": 0}).to_list(100)

@api_router.post("/proofs", response_model=Proof)
async def create_proof(p: ProofBase):
    proof = Proof(**p.model_dump())
    await db.proofs.insert_one(proof.model_dump())
    return proof

@api_router.delete("/proofs/{proof_id}")
async def delete_proof(proof_id: str):
    await db.proofs.delete_one({"id": proof_id})
    return {"deleted": True}

# Subscribers
@api_router.get("/subscribers")
async def get_subscribers(req: Request):
    verify_admin(req)
    return await db.subscribers.find({}, {"_id": 0}).to_list(1000)

@api_router.post("/subscribers", response_model=Subscriber)
async def subscribe(s: SubscriberCreate):
    existing = await db.subscribers.find_one({"email": s.email}, {"_id": 0})
    if existing: return existing
    sub = Subscriber(**s.model_dump())
    await db.subscribers.insert_one(sub.model_dump())
    return sub

@api_router.delete("/subscribers/{sub_id}")
async def unsubscribe(sub_id: str, req: Request):
    verify_admin(req)
    await db.subscribers.delete_one({"id": sub_id})
    return {"deleted": True}

# Comments
@api_router.get("/comments", response_model=List[Comment])
async def get_comments(): return await db.comments.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)

@api_router.post("/comments", response_model=Comment)
async def create_comment(c: CommentCreate):
    comment = Comment(**c.model_dump())
    await db.comments.insert_one(comment.model_dump())
    return comment

@api_router.delete("/comments/{comment_id}")
async def delete_comment(comment_id: str, req: Request):
    verify_admin(req)
    await db.comments.delete_one({"id": comment_id})
    return {"deleted": True}

# Petition
@api_router.get("/petition/count")
async def get_petition_count():
    count = await db.petition_signatures.count_documents({})
    return {"count": count}

@api_router.get("/petition/signatures")
async def get_signatures(): return await db.petition_signatures.find({}, {"_id": 0}).to_list(10000)

@api_router.post("/petition/sign", response_model=Petition)
async def sign_petition(p: PetitionCreate):
    sig = Petition(**p.model_dump())
    await db.petition_signatures.insert_one(sig.model_dump())
    return sig

# Submissions
@api_router.get("/submissions")
async def get_submissions(req: Request):
    verify_admin(req)
    return await db.submissions.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)

@api_router.post("/submissions", response_model=Submission)
async def create_submission(s: SubmissionCreate):
    sub = Submission(**s.model_dump())
    await db.submissions.insert_one(sub.model_dump())
    return sub

@api_router.put("/submissions/{sub_id}/status")
async def update_submission_status(sub_id: str, req: Request):
    verify_admin(req)
    data = await req.json()
    await db.submissions.update_one({"id": sub_id}, {"$set": {"status": data.get("status", "pending")}})
    return {"updated": True}

# Content
@api_router.get("/content")
async def get_content():
    items = await db.content.find({}, {"_id": 0}).to_list(100)
    return {item["key"]: item["value"] for item in items}

@api_router.put("/content")
async def update_content(item: ContentUpdate, req: Request):
    verify_admin(req)
    await db.content.update_one({"key": item.key}, {"$set": {"key": item.key, "value": item.value}}, upsert=True)
    return {"updated": True}

# Deploy
@api_router.get("/deploy/runs")
async def get_deploy_runs(req: Request):
    verify_admin(req)
    return await db.deploy_runs.find({}, {"_id": 0}).sort("created_at", -1).to_list(10)

@api_router.post("/deploy/run")
async def start_deploy(body: DeployRunRequest):
    import asyncio
    from services.deployer import deploy_live
    run_id = str(uuid.uuid4())
    await db.deploy_runs.insert_one({"id": run_id, "status": "queued", "created_at": _now()})
    asyncio.create_task(deploy_live(run_id, {"render_token": body.render_token, "vercel_token": body.vercel_token}, body.github_repo))
    return {"run_id": run_id, "status": "started"}

# Monitor
@api_router.get("/monitor/status")
async def get_monitor_status():
    open_obs = await db.monitor_observations.count_documents({"status": "open"})
    return {"open_count": open_obs, "status": "healthy" if open_obs == 0 else "warning"}

@api_router.get("/monitor/observations")
async def get_observations(req: Request):
    verify_admin(req)
    return await db.monitor_observations.find({}, {"_id": 0}).sort("created_at", -1).to_list(100)

@api_router.post("/monitor/observations/{obs_id}/dismiss")
async def dismiss_observation(obs_id: str, req: Request):
    verify_admin(req)
    await db.monitor_observations.update_one({"id": obs_id}, {"$set": {"status": "dismissed"}})
    return {"updated": True}

# Seed
@api_router.post("/seed")
async def seed_data():
    count = await db.games.count_documents({})
    if count == 0:
        for i, g in enumerate([
            {"title": "NBA 2K15", "year": "2014", "hook_text": "Where the modern 2K era truly began", "cover_athletes": "LeBron James", "description": "NBA 2K15 marked a new era.", "order": 1},
            {"title": "NBA 2K16", "year": "2015", "hook_text": "The one OGs still call the GOAT", "cover_athletes": "Stephen Curry", "description": "Widely considered one of the best.", "order": 2},
            {"title": "NBA 2K17", "year": "2016", "hook_text": "Pure basketball soul", "cover_athletes": "Kevin Durant", "description": "Perfected the on-court experience.", "order": 3},
            {"title": "NBA 2K20", "year": "2019", "hook_text": "The final masterpiece", "cover_athletes": "Anthony Davis", "description": "Last of the golden era.", "order": 4},
        ]):
            await db.games.insert_one(Game(**g).model_dump())
    return {"seeded": True}

app.include_router(api_router)

uploads = ROOT_DIR / "uploads"
if uploads.exists(): app.mount("/api/uploads", StaticFiles(directory=str(uploads)), name="uploads")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)