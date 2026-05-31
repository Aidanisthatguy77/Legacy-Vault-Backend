# NBA 2K Legacy Vault Backend 🏀

FastAPI + MongoDB backend with React admin panel.

## Structure

```
├── backend/              # FastAPI backend
│   ├── server.py         # Main API
│   ├── requirements.txt  # Python deps
│   ├── services/         # Monitor, Deployer
│   └── utils/            # Exporter
├── admin-frontend/       # React admin panel
│   ├── src/App.jsx      # All 15 tabs
│   └── package.json     # JS deps
├── server.ts            # Deno version (alternative)
└── deno.json            # Deno config
```

## Quick Start

### Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # Edit with your values
uvicorn server:app --host 0.0.0.0 --port 8001
```

### Admin Panel (React)
```bash
cd admin-frontend
npm install
npm run dev
# Opens at http://localhost:3001
```

## Deploy to Render (Free Backend)

1. Create account at render.com
2. Connect GitHub repo
3. Create Web Service:
   - Root Directory: `backend`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `uvicorn server:app --host 0.0.0.0 --port 8001`
4. Add environment variables

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
| POST | `/api/subscribers` | Subscribe |
| GET | `/api/petition/count` | Signature count |
| POST | `/api/petition/sign` | Sign petition |
| GET | `/api/content` | Get content |
| PUT | `/api/content` | Update content |
| POST | `/api/admin/login` | Admin login |
| GET | `/api/monitor/status` | Monitor status |
| GET | `/api/deploy/runs` | Deploy history |
