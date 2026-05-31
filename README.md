# NBA 2K Legacy Vault Backend 🏀

FastAPI + MongoDB backend for the NBA 2K Legacy Vault admin panel.

## Features (15 Admin Tabs)

| Tab | Purpose |
|-----|---------|
| **Games** | Manage 2K15-2K20 game entries |
| **Clips** | Video clips management |
| **Mockups** | UI mockup assets |
| **Proof** | Evidence/proof images |
| **Community** | Social/community wall |
| **Live Feed** | Social media feed |
| **Submissions** | User submissions |
| **Content** | Site copy/text content |
| **Comments** | Comment management |
| **Emails** | Subscriber emails |
| **Petition** | Signature collection |
| **Deploy** | Live deploy to Render + Vercel |
| **Monitor** | System health monitoring |
| **Acceleration** | AI coding agent |
| **Neplit** | Build + export tools |

## Tech Stack

- **Framework**: FastAPI + Uvicorn
- **Database**: MongoDB (Motor async driver)
- **AI**: Claude + Gemini dual engine
- **Styling**: Red/Black/White

## Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your values
```

Required `.env` variables:
```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=vault_legacy
ANTHROPIC_API_KEY=sk-ant-your-key
GOOGLE_API_KEY=your-gemini-key
ADMIN_PASSWORD=A@070610
```

### 3. Run

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

## Deploy to Render (Free)

1. Create account at [render.com](https://render.com)
2. Connect GitHub repo
3. Create Web Service:
   - Build Command: `cd backend && pip install -r requirements.txt`
   - Start Command: `cd backend && uvicorn server:app --host 0.0.0.0 --port 8001`
4. Add environment variables from `.env.example`
5. Deploy!

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/chat` | AI chat (dual engine) |
| GET | `/api/games` | List games |
| POST | `/api/games` | Create game |
| PUT | `/api/games/{id}` | Update game |
| DELETE | `/api/games/{id}` | Delete game |
| GET | `/api/clips` | List clips |
| POST | `/api/clips` | Create clip |
| GET | `/api/subscribers` | List subscribers |
| POST | `/api/subscribers` | Subscribe email |
| GET | `/api/petition/count` | Signature count |
| POST | `/api/petition/sign` | Sign petition |
| GET | `/api/content` | Get site content |
| PUT | `/api/content` | Update content |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/monitor/status` | Monitor status |
| GET | `/api/deploy/runs` | Deploy history |
| POST | `/api/deploy/run` | Start deploy |

## AI Chat Routing

- **Media URLs** (YouTube, Twitter, Reddit) → Claude
- **Text questions** → Gemini
- **No API keys** → Built-in demo responses

## Database Collections

- `games` - Game era entries
- `clips` - Video clips
- `mockups` - UI mockups
- `proofs` - Evidence images
- `comments` - User comments
- `subscribers` - Email list
- `submissions` - User submissions
- `petition_signatures` - Petition signatures
- `content` - Site content (key-value)
- `vault_chat_history` - Chat logs
- `monitor_observations` - Health alerts
- `deploy_runs` - Deploy history
