# 🍽️ Zomato AI Restaurant Recommendation System

An AI-powered restaurant recommendation system for Bangalore, built with Python, FastAPI, Next.js, and Groq LLM.

## Architecture

The system is structured across 10 phases, each in its own package under `src/milestone1/`:

| Phase | Package | Purpose |
|-------|---------|---------|
| 0 | `phase0/` | Foundation — settings, paths, CLI, doctor |
| 1 | `phase1_ingestion/` | HuggingFace data loading, normalisation, deduplication |
| 2 | `phase2_preferences/` | User preference validation, fuzzy city matching |
| 3 | `phase3_integration/` | Deterministic filtering, prompt assembly |
| 4 | `phase4_llm/` | Groq LLM client, hallucination guard, fallback |
| 5 | `phase5_output/` | Rendering (markdown/plain), empty states, telemetry |
| 6 | `phase6_api/` | FastAPI HTTP API (CORS, health, recommendations) |
| 7 | `frontend/` | Next.js 15 + TypeScript + Tailwind CSS |
| 8 | Config files | Render (backend) + Vercel (frontend) deployment |
| 9 | `phase9_streamlit/` | Single-process Streamlit demo |
| 10 | `tests/` | Automated tests for all phases |

## Quick Start

### 1. Clone and Install

```bash
git clone <repo-url>
cd zomato-ai-recommend
pip install -e ".[test]"
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your keys:
#   GROQ_API_KEY=your_groq_api_key_here
#   GROQ_MODEL=llama-3.3-70b-versatile
```

### 3. Verify Setup

```bash
milestone1 doctor
```

### 4. Run the API

```bash
uvicorn milestone1.phase6_api.app:app --host 0.0.0.0 --port 8000
# → Swagger docs at http://localhost:8000/docs
# → Health check at http://localhost:8000/health
```

### 5. Run the Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:3000
```

### 6. Run the Streamlit Demo (alternative)

```bash
pip install -e ".[streamlit]"
streamlit run streamlit_app.py
# → http://localhost:8501
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `milestone1 info` | Show project info |
| `milestone1 doctor` | Verify environment |
| `milestone1 ingest-smoke --limit N` | Test data loading |
| `milestone1 prefs-parse --location X` | Test preference parsing |
| `milestone1 prompt-build --location X` | Build LLM prompt (no API call) |
| `milestone1 recommend --location X` | Full recommendation pipeline |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | Health check (Groq status, corpus size) |
| `GET` | `/api/v1/meta` | Available locations and cuisines |
| `POST` | `/api/v1/recommendations` | Get AI-powered recommendations |

### Example Request

```bash
curl -X POST http://localhost:8000/api/v1/recommendations \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Koramangala",
    "budget": "Medium",
    "cuisines": ["North Indian", "Chinese"],
    "min_rating": 3.5
  }'
```

## Running Tests

```bash
pytest tests/ -v
```

## Deployment

### Backend → Render
- Build: `pip install -e .`
- Start: `uvicorn milestone1.phase6_api.app:app --host 0.0.0.0 --port $PORT`
- Set `GROQ_API_KEY`, `GROQ_MODEL`, `CORS_ORIGINS` as env vars

### Frontend → Vercel
- Root directory: `frontend/`
- Set `NEXT_PUBLIC_API_BASE_URL` env var to Render URL

### Streamlit → Streamlit Community Cloud
- Main file: `streamlit_app.py`
- Add `GROQ_API_KEY` in Streamlit secrets

## Tech Stack

- **Backend:** Python 3.11, FastAPI, Pydantic
- **Frontend:** Next.js 15, TypeScript, Tailwind CSS
- **AI:** Groq LLM (llama-3.3-70b-versatile)
- **Data:** HuggingFace `ManikaSaini/zomato-restaurant-recommendation`
- **Demo:** Streamlit

## Limitations

- Bangalore restaurants only (dataset scope)
- No user accounts or authentication
- No live Zomato API integration
- No maps, images, or booking features
- Render free tier sleeps after 15 min idle
