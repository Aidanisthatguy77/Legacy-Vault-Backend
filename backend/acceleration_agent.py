"""
Acceleration Agent - The embedded coding partner with JSON tool-calling loop
Provides full codebase access: read/write files, terminal, deps, services
"""
import os
import re
import json
import uuid
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Optional, Any
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter(prefix="/api/admin/acceleration")

ROOT = Path("/app").resolve()

# ============ SYSTEM PROMPT ============
SYSTEM_PROMPT = """You are the Acceleration Agent: embedded coding partner inside /app.

LAYOUT
- /app/backend  FastAPI on 8001 (supervisor, hot-reload). Main: server.py.
- /app/frontend React+Tailwind on 3000. Use yarn (NEVER npm).
- MongoDB via MONGO_URL. Restart backend after pip install or .env change.

OUTPUT FORMAT
Reply with EXACTLY ONE JSON object, no prose, no fences:
  {"action":"tool","tool":"<name>","args":{...},"thought":"<<=15 words>"}
or:
  {"action":"respond","message":"<short summary>"}

TOOLS
- read_file       {"path":"/app/..."}
- write_file      {"path":"/app/...","content":"..."}
- edit_file       {"path":"/app/...","old_str":"...","new_str":"..."}
- list_dir        {"path":"/app/..."}
- bash            {"command":"...","timeout":30}
- pip_install     {"package":"name"}
- yarn_add        {"package":"name"}
- restart_service {"service":"backend"|"frontend"}

RULES
1. JSON only. One tool per turn. Keep thought brief.
2. Paths must be inside /app.
3. After changes verify (read back or curl), then respond.
4. Be decisive. Tool results may be truncated; request a smaller slice if needed."""

# ============ SESSION STATE ============
_sessions: Dict[str, dict] = {}

def _get_session(session_id: str) -> dict:
    if session_id not in _sessions:
        _sessions[session_id] = {
            "id": session_id,
            "messages": [],
            "created_at": datetime.now(timezone.utc).isoformat(),
            "last_active": datetime.now(timezone.utc).isoformat(),
        }
    return _sessions[session_id]

def _safe_path(p: str) -> Path:
    path = Path(p).resolve()
    try:
        path.relative_to(ROOT)
        return path
    except:
        return ROOT / p

def _parse_action(text: str) -> dict:
    try:
        return json.loads(text)
    except:
        pass
    patterns = [r'```json\s*(\{.*?\})\s*```', r'```\s*(\{.*?\})\s*```', r'(\{[^}]*"action"[^}]*\})']
    for pattern in patterns:
        matches = re.findall(pattern, text, re.DOTALL)
        for match in matches:
            try:
                return json.loads(match)
            except:
                continue
    return {"action": "respond", "message": "Could not parse action"}

def _trim_result(result: Any, max_kb: int = 10) -> Any:
    s = json.dumps(result)
    if len(s) > max_kb * 1024:
        return {"result": f"[Output truncated]", "truncated": True}
    return result

# ============ TOOLS ============
async def tool_read_file(args: dict) -> dict:
    path = _safe_path(args["path"])
    if not path.exists() or not path.is_file():
        return {"success": False, "error": "Not found"}
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        if len(content) > 30000:
            return {"success": True, "content": content[:30000], "truncated": True}
        return {"success": True, "content": content}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def tool_write_file(args: dict) -> dict:
    path = _safe_path(args["path"])
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(args["content"], encoding="utf-8")
        return {"success": True, "path": str(path), "size": len(args["content"])}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def tool_edit_file(args: dict) -> dict:
    path = _safe_path(args["path"])
    if not path.exists():
        return {"success": False, "error": "File not found"}
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        old_str = args["old_str"]
        new_str = args["new_str"]
        if old_str not in content:
            return {"success": False, "error": "old_str not found in file"}
        new_content = content.replace(old_str, new_str, 1)
        path.write_text(new_content, encoding="utf-8")
        return {"success": True, "path": str(path)}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def tool_list_dir(args: dict) -> dict:
    path = _safe_path(args["path"])
    if not path.exists() or not path.is_dir():
        return {"success": False, "error": "Directory not found"}
    try:
        items = [{"name": i.name, "type": "dir" if i.is_dir() else "file"} for i in path.iterdir()]
        return {"success": True, "items": items}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def tool_bash(args: dict) -> dict:
    timeout = min(int(args.get("timeout", 30) or 30), 90)
    try:
        proc = await asyncio.create_subprocess_shell(
            args["command"], stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(ROOT)
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return {"success": proc.returncode == 0, "output": (stdout + stderr).decode()[-9000:]}
    except asyncio.TimeoutError:
        return {"success": False, "error": "Timeout"}
    except Exception as e:
        return {"success": False, "error": str(e)}

async def tool_pip_install(args: dict) -> dict:
    proc = await asyncio.create_subprocess_shell(
        f"pip install {args['package']}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(ROOT / "backend")
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
    return {"success": proc.returncode == 0, "output": (stdout + stderr).decode()[-5000:]}

async def tool_yarn_add(args: dict) -> dict:
    proc = await asyncio.create_subprocess_shell(
        f"yarn add {args['package']}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE, cwd=str(ROOT / "frontend")
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=60)
    return {"success": proc.returncode == 0, "output": (stdout + stderr).decode()[-5000:]}

async def tool_restart_service(args: dict) -> dict:
    proc = await asyncio.create_subprocess_shell(
        f"sudo supervisorctl restart {args['service']}", stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=15)
    return {"success": proc.returncode == 0, "output": (stdout + stderr).decode()[-2000:]}

TOOLS = {"read_file": tool_read_file, "write_file": tool_write_file, "edit_file": tool_edit_file,
         "list_dir": tool_list_dir, "bash": tool_bash, "pip_install": tool_pip_install,
         "yarn_add": tool_yarn_add, "restart_service": tool_restart_service}

# ============ LLM BRIDGE ============
async def call_llm(session_id: str, user_text: str) -> str:
    try:
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        api_key = os.environ.get("EMERGENT_LLM_KEY", "")
        if not api_key:
            return json.dumps({"action": "respond", "message": "EMERGENT_LLM_KEY not configured"})
        chat = LlmChat(api_key=api_key, session_id=f"acc-agent-{session_id}", system_message=SYSTEM_PROMPT)
        chat = chat.with_model("anthropic", "claude-sonnet-4-5-20250929")
        return await chat.send_message(UserMessage(text=user_text))
    except ImportError:
        return json.dumps({"action": "respond", "message": "emergentintegrations not installed"})
    except Exception as e:
        return json.dumps({"action": "respond", "message": f"LLM error: {str(e)}"})

# ============ AGENT LOOP ============
MAX_ITERATIONS = 14

async def run_agent(session_id: str, message: str, password: str) -> dict:
    ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "A@070610")
    if password != ADMIN_PASSWORD:
        raise HTTPException(status_code=403, detail="Invalid admin password")
    
    session = _get_session(session_id)
    session["messages"].append({"role": "user", "content": message})
    
    history = "PRIOR:\n" + "\n".join(f"[{m['role'].upper()}] {m['content'][:280]}" for m in session["messages"][-3:])
    user_text = f"{history}\nUSER:\n{message}\nReply with ONE JSON action."
    
    steps = []
    for _ in range(MAX_ITERATIONS):
        llm_out = await call_llm(session_id, user_text)
        action = _parse_action(llm_out)
        
        if action.get("action") == "respond":
            session["messages"].append({"role": "assistant", "content": action["message"]})
            return {"response": action["message"], "completed": True, "steps": steps, "session_id": session_id}
        
        tool_name = action.get("tool", "")
        tool_args = action.get("args", {})
        
        if tool_name not in TOOLS:
            user_text = f"Unknown tool. Available: {list(TOOLS.keys())}\nNext."
            continue
        
        try:
            result = await TOOLS[tool_name](tool_args)
        except Exception as e:
            result = {"success": False, "error": str(e)}
        
        steps.append({"tool": tool_name, "args": tool_args, "result": _trim_result(result)})
        user_text = f"RESULT [{tool_name}]:\n{json.dumps(_trim_result(result, 2))}\nNext."
    
    return {"response": f"Max {MAX_ITERATIONS} steps", "completed": False, "steps": steps, "session_id": session_id}

# ============ HTTP ENDPOINTS ============
class AgentRequest(BaseModel):
    message: str
    password: str = ""
    session_id: Optional[str] = None

@router.post("/agent")
async def acceleration_agent(req: AgentRequest):
    session_id = req.session_id or str(uuid.uuid4())
    result = await run_agent(session_id, req.message, req.password)
    try:
        from server import db
        await db.acceleration_agent_sessions.update_one(
            {"id": session_id}, {"$set": {"id": session_id, "messages": _sessions.get(session_id, {}).get("messages", []),
            "completed": result["completed"], "last_response": result["response"],
            "updated_at": datetime.now(timezone.utc).isoformat()}}, upsert=True)
    except:
        pass
    return result

@router.get("/sessions")
async def list_sessions():
    return [{"id": sid, "count": len(s.get("messages", []))} for sid, s in _sessions.items()][:20]

@router.get("/history/{session_id}")
async def get_history(session_id: str):
    return {"messages": _sessions.get(session_id, {}).get("messages", [])}
