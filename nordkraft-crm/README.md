# NordKraft AI CRM

AI-native CRM for NordKraft Group — built on FastAPI + Next.js + Claude.

## Quick Start

### Backend
```bash
cd backend
pip install -r requirements.txt
cp .env.example .env  # fill in your keys
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local  # set NEXT_PUBLIC_API_URL
npm run dev
```

## Stack
- **Frontend**: Next.js 14, Tailwind CSS, React Query, Zustand
- **Backend**: FastAPI, SQLAlchemy async, Pydantic v2
- **Database**: PostgreSQL (Supabase), Redis
- **AI**: Anthropic Claude (primary), OpenAI (fallback)
- **Automation**: n8n webhooks
- **Auth**: Supabase JWT
- **Storage**: S3-compatible (Cloudflare R2)

## API Docs
Running backend → http://localhost:8000/docs

## Env Variables
See `backend/.env.example` and `frontend/.env.local.example` — created after deployment setup.

## Deployment
See Technical Specification document for full deployment guide.
