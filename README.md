# NBA 2K Legacy Vault Backend 🏀

The complete backend system for the NBA 2K Legacy Vault campaign. This is a **self-editing, self-healing, self-deploying** platform.

## What Makes It Special

This isn't just a backend — it's an autonomous platform:

| Feature | Description |
|---------|-------------|
| **Self-Editing** | Acceleration Agent rewrites the codebase via AI |
| **Self-Healing** | Monitor detects issues and dispatches fixes automatically |
| **Self-Cloning** | Full System Export creates a redeployable zip anywhere |
| **Self-Deploying** | One button → GitHub → Atlas → Render → Vercel |
| **Self-Explaining** | Vault Guide answers questions about the system |

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     NBA 2K Legacy Vault                      │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐     ┌──────────────┐     ┌─────────────┐ │
│  │   Public     │     │   Admin      │     │   Backend   │ │
│  │   Site (/)   │     │   (/admin)   │     │  (8001)     │ │
│  └──────────────┘     └──────────────┘     └──────┬──────┘ │
│                                                    │        │
│                                            ┌───────▼───────┐ │
│                                            │    MongoDB    │ │
│                                            └───────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Tech Stack

- **Backend**: FastAPI + Uvicorn (Python 3.11)
- **Database**: MongoDB 7 (Motor async driver)
- **AI**: `emergentintegrations` library (ONE key → Claude/Gemini routing)
- **Frontend**: React 19 + Vite (see admin-frontend/)

## ONE AI Key

This project uses **`EMERGENT_LLM_KEY`** — a single key that routes to Claude or Gemini automatically:

```bash
pip install emergentintegrations --extra-index-url https://d33sy5i8bnduwe.cloudfront.net/simple/
```

- **Claude Sonnet**: For media URLs (YouTube, Twitter, Reddit analysis)
- **Gemini Flash**: For fast text responses

## Quick Start

### 1. Backend

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Admin Panel

```bash
cd admin-frontend
npm install
npm run dev
```

### 3. Docker (Everything at once!)

```bash
docker compose up
```

## Environment Variables

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017
DB_NAME=vault_legacy

# ONE AI Key (from emergentintegrations dashboard)
EMERGENT_LLM_KEY=sk-emergent-your-key-here

# Admin password
ADMIN_PASSWORD=A@070610

# CORS origins (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Monitor interval (seconds)
MONITOR_INTERVAL=60
```

## MongoDB Collections (19 total)

| Collection | Purpose |
|------------|---------|
| `games` | Game era entries (2K15-2K20) |
| `clips` | Video clips |
| `mockups` | UI mockup assets |
| `proofs` | Evidence images |
| `comments` | User comments |
| `subscribers` | Email subscriptions |
| `submissions` | Creator submissions |
| `petition_signatures` | Petition signatures |
| `content` | Site copy (key-value) |
| `community_posts` | Social posts |
| `social_feed` | Live social feed |
| `era_votes` | Era voting |
| `vault_chat_history` | AI chat logs |
| `acceleration_agent_sessions` | Agent sessions |
| `monitor_observations` | Health alerts |
| `monitor_heartbeats` | Monitor timestamps |
| `deploy_runs` | Deploy history |
| `deploy_tokens` | Saved API tokens |
| `secrets_vault` | Encrypted credentials |

## API Endpoints (Full List)

### Public Site

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/games` | List active games |
| GET | `/api/clips` | List clips |
| GET | `/api/mockups` | List mockups |
| GET | `/api/proofs` | List proofs |
| GET | `/api/comments` | List comments |
| POST | `/api/comments` | Add comment |
| GET | `/api/subscribers` | List (admin) |
| POST | `/api/subscribers` | Subscribe |
| GET | `/api/petition/count` | Signature count |
| GET | `/api/petition/signatures` | All signatures |
| POST | `/api/petition/sign` | Sign petition |
| GET | `/api/votes` | Vote counts |
| POST | `/api/votes` | Cast vote |
| GET | `/api/community-posts` | Social posts |
| POST | `/api/community-posts` | Create post |
| GET | `/api/social-feed` | Live feed |
| POST | `/api/social-feed` | Add to feed |
| GET | `/api/content` | Site content |
| GET | `/api/submissions` | List (admin) |
| POST | `/api/submissions` | Submit |
| POST | `/api/chat` | AI chat (dual engine) |
| GET | `/api/health` | Health check |
| GET | `/api/health/pulse` | Lightweight ping |

### Admin (requires X-Admin-Password header)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/login` | Login |
| PUT | `/api/content` | Update content |
| PUT | `/api/games/{id}` | Update game |
| DELETE | `/api/games/{id}` | Delete game |
| DELETE | `/api/clips/{id}` | Delete clip |
| DELETE | `/api/subscribers/{id}` | Unsubscribe |
| DELETE | `/api/comments/{id}` | Delete comment |
| PUT | `/api/submissions/{id}/status` | Update status |

### Acceleration Agent

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/acceleration/agent` | Run agent |
| GET | `/api/admin/acceleration/sessions` | List sessions |
| GET | `/api/admin/acceleration/history/{id}` | Get history |

### Deploy

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/acceleration/deploy/tokens` | Get token status |
| POST | `/api/admin/acceleration/deploy/tokens` | Save tokens |
| POST | `/api/admin/acceleration/deploy/run` | Start deploy |
| GET | `/api/admin/acceleration/deploy/runs` | List runs |
| GET | `/api/admin/acceleration/deploy/runs/{id}` | Run details |
| DELETE | `/api/admin/acceleration/deploy/runs/{id}` | Delete run |

### Monitor

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/acceleration/monitor/status` | Monitor status |
| GET | `/api/admin/acceleration/monitor/observations` | List observations |
| POST | `/api/admin/acceleration/monitor/observations/{id}/dismiss` | Dismiss |
| POST | `/api/admin/acceleration/monitor/observations/{id}/fix` | Run Fix |
| POST | `/api/admin/acceleration/monitor/observations/clear` | Clear fixed/dismissed |
| POST | `/api/admin/acceleration/monitor/apply-link` | Apply from URL |

### Vault Guide

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/vault-guide` | Ask about the system |

### Nep (Dev Partner)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/nep/chat` | Conversational help |

### Secrets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/admin/secrets` | List secret keys |
| PUT | `/api/admin/secrets` | Save secret |

### System

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/seed` | Seed initial data |

## Acceleration Agent

The centerpiece of the system — an embedded coding partner that can:

- Read/write/edit files
- Run shell commands
- Install dependencies
- Restart services
- Chain multi-step tasks autonomously

### Agent Tools

```
read_file     - Read any file in /app
write_file    - Write any file in /app
edit_file     - Edit specific text in a file
list_dir      - List directory contents
bash          - Run shell commands
pip_install   - Install Python packages
yarn_add      - Install Node packages
restart_service - Restart backend/frontend
```

### How It Works

1. You send a message
2. Agent responds with JSON tool calls
3. Tools execute and return results
4. Agent continues until task is done
5. Max 14 iterations per session

## Deploy Backend to Render (Free)

1. Go to [render.com](https://render.com) → Connect GitHub
2. Create Web Service → Root: `backend`
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `uvicorn server:app --host 0.0.0.0 --port 8001`
5. Add environment variables
6. Deploy!

## Deploy Admin Panel to Vercel (Free)

1. Go to [vercel.com](https://vercel.com) → Import `admin-frontend`
2. Add `VITE_API_URL` = your backend URL
3. Deploy!

## MongoDB Atlas Setup

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free **M0** cluster
3. Create database user
4. Whitelist IP `0.0.0.0/0`
5. Copy connection string → use as `MONGO_URL`

## Files

```
Legacy-Vault-Backend/
├── backend/
│   ├── server.py              # Main FastAPI app
│   ├── acceleration_agent.py  # AI coding agent
│   ├── requirements.txt       # Python deps
│   ├── .env.example           # Environment template
│   ├── Dockerfile             # Docker container
│   ├── services/
│   │   ├── monitor.py         # Background watchdog
│   │   └── deployer.py        # Deploy orchestration
│   └── utils/
│       └── exporter.py        # Full system export
├── admin-frontend/             # React admin panel
│   └── src/App.jsx            # All 15 admin tabs
├── docker-compose.yml          # Dev setup
├── docker-compose.prod.yml    # Production setup
└── README.md
```
