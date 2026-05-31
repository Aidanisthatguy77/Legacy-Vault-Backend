# NBA 2K Legacy Vault Backend 🏀

FastAPI + MongoDB backend with React admin panel - the complete backend system for the Legacy Vault campaign.

## What's Included

### Backend (`/backend`)
- **FastAPI** API server on port 8001
- **MongoDB** database with Motor async driver
- **AI Chat** with dual engine routing (Claude for URLs, Gemini for text)
- **Background monitoring** service
- **Deploy orchestrator** for Render + Vercel

### Admin Frontend (`/admin-frontend`)
- **React 18** app with Vite
- **15 admin tabs** with full CRUD operations
- **Red/Black/White** theme matching the site
- Login with password authentication

## Structure

```
Legacy-Vault-Backend/
├── backend/
│   ├── server.py              # Main FastAPI app (all routes)
│   ├── requirements.txt        # Python dependencies
│   ├── .env.example           # Environment template
│   ├── services/
│   │   ├── monitor.py         # Background health checker
│   │   └── deployer.py        # Deploy orchestration
│   └── utils/
│       └── exporter.py        # Full system export
├── admin-frontend/
│   ├── src/App.jsx            # All 15 admin tabs
│   ├── src/main.jsx           # React entry
│   ├── src/index.css          # Tailwind styles
│   ├── package.json           # JS dependencies
│   ├── vite.config.js         # Vite config
│   └── tailwind.config.js     # Tailwind config
└── README.md
```

## Quick Start

### 1. Backend (Python/FastAPI)

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values (see below)
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

### 2. Admin Panel (React)

```bash
cd admin-frontend
npm install
npm run dev
# Opens at http://localhost:3001
```

## Environment Variables

Create `backend/.env` with:

```env
# MongoDB (required)
MONGO_URL=mongodb://localhost:27017
DB_NAME=vault_legacy

# API Keys (optional - demo mode works without)
ANTHROPIC_API_KEY=sk-ant-your-claude-key
GOOGLE_API_KEY=your-gemini-key

# Admin (change this!)
ADMIN_PASSWORD=A@070610

# CORS (comma-separated)
CORS_ORIGINS=http://localhost:3000,http://localhost:3001

# Monitor interval (seconds)
MONITOR_INTERVAL=60
```

## Deploy Backend to Render (Free)

1. Go to [render.com](https://render.com) → Sign up with GitHub
2. Click **New** → **Web Service**
3. Connect your GitHub repo
4. Configure:
   - **Root Directory**: `backend`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn server:app --host 0.0.0.0 --port 8001`
   - **Plan**: Free
5. Add environment variables from `.env.example`
6. Click **Create Web Service**

## Deploy Admin Panel to Vercel (Free)

1. Go to [vercel.com](https://vercel.com) → Sign up with GitHub
2. Import `admin-frontend` project
3. Add environment variable:
   - `VITE_API_URL` = your backend URL (e.g., `https://vault-backend.onrender.com`)
4. Deploy!

## MongoDB Atlas Setup (Free)

1. Go to [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas)
2. Create free **M0** cluster
3. Create database user
4. Whitelist IP `0.0.0.0/0`
5. Copy connection string → use as `MONGO_URL`

## API Endpoints

### Health
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Full health check |
| GET | `/api/health/pulse` | Lightweight ping |

### Admin
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/admin/login` | Admin login |

### Games
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/games` | List active games |
| GET | `/api/games/all` | List all games |
| POST | `/api/games` | Create game |
| PUT | `/api/games/{id}` | Update game |
| DELETE | `/api/games/{id}` | Delete game |

### Clips
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/clips` | List active clips |
| GET | `/api/clips/all` | List all clips |
| POST | `/api/clips` | Create clip |
| PUT | `/api/clips/{id}` | Update clip |
| DELETE | `/api/clips/{id}` | Delete clip |

### Mockups
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/mockups` | List active mockups |
| POST | `/api/mockups` | Create mockup |
| PUT | `/api/mockups/{id}` | Update mockup |
| DELETE | `/api/mockups/{id}` | Delete mockup |

### Proofs
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/proofs` | List active proofs |
| POST | `/api/proofs` | Create proof |
| DELETE | `/api/proofs/{id}` | Delete proof |

### Subscribers
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/subscribers` | List all (admin) |
| POST | `/api/subscribers` | Subscribe email |
| DELETE | `/api/subscribers/{id}` | Unsubscribe (admin) |

### Comments
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/comments` | List comments |
| POST | `/api/comments` | Add comment |
| DELETE | `/api/comments/{id}` | Delete (admin) |

### Petition
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/petition/count` | Signature count |
| GET | `/api/petition/signatures` | All signatures |
| POST | `/api/petition/sign` | Sign petition |

### Submissions
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/submissions` | List (admin) |
| POST | `/api/submissions` | Submit |
| PUT | `/api/submissions/{id}/status` | Update status (admin) |

### Content
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/content` | Get all content |
| PUT | `/api/content` | Update content (admin) |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat` | AI chat (dual engine) |
| POST | `/api/vault-guide` | Admin AI helper |

### Deploy
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/deploy/runs` | Deploy history (admin) |
| POST | `/api/deploy/run` | Start deploy |

### Monitor
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/monitor/status` | Monitor status |
| GET | `/api/monitor/observations` | List observations (admin) |
| POST | `/api/monitor/observations/{id}/dismiss` | Dismiss (admin) |

### System
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/seed` | Seed initial data |

## AI Chat Routing

The `/api/chat` endpoint uses intelligent routing:

- **Media URLs** (YouTube, Twitter, Reddit, TikTok) → **Claude** (for analysis)
- **Text questions** → **Gemini** (fast responses)
- **No API keys** → Built-in demo responses

## Database Collections

- `games` - Game era entries (2K15-2K20)
- `clips` - Video clips
- `mockups` - UI mockup assets
- `proofs` - Evidence/proof images
- `comments` - User comments
- `subscribers` - Email subscriptions
- `submissions` - Creator submissions
- `petition_signatures` - Petition signatures
- `content` - Site content (key-value)
- `vault_chat_history` - Chat logs
- `monitor_observations` - Health alerts
- `deploy_runs` - Deploy history
