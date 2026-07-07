# Phased Architecture — Zomato AI Restaurant Recommendation System

This document is the canonical phase reference. Each phase maps directly to a
package under `src/milestone1/phase{N}_*/`.

---

## Phase 0 — Scope and foundations

| Item | Outcome |
|---|---|
| Product slice | Basic web UI is the sole source of user input (Phase 7). CLI for dev/diagnostics only. |
| Stack | Python 3.11 · pip + pyproject.toml · FastAPI · Next.js · Groq LLM |
| Dataset contract | HuggingFace `ManikaSaini/zomato-restaurant-recommendation` |
| Secrets | `.env` locally · env vars in cloud · never committed |
| Non-goals | User accounts · live Zomato API · maps · images · bookings |

**Exit criteria:** written assumptions, `.env.example`, working `milestone1 info` and `milestone1 doctor` CLI commands.

**Artifacts:** `phase0/paths.py` · `phase0/settings.py` · `phase0/doctor.py` · `phase0/cli.py` · `.env.example` · `README.md`

---

## Phase 1 — Data ingestion and canonical model

| Layer | Responsibility |
|---|---|
| Acquisition | Stream `ManikaSaini/zomato-restaurant-recommendation` from HuggingFace Hub; cache locally |
| Normalization | Parse ratings (`4.1/5` → `4.1`; `NEW` → `0.0`); clamp to `[0, 5]`; split cuisines; map cost → budget band |
| Canonical schema | `Restaurant(restaurant_id, name, location, cuisines, cost_raw, budget, rating, votes, ...)` |
| Deduplication | Keep highest-rated row per `(name, location)` pair |

**Exit criteria:** `load_restaurants()` returns a typed list; unit tests on parsing; `milestone1 ingest-smoke --limit N` CLI.

**Artifacts:** `phase1_ingestion/models.py` · `phase1_ingestion/normalizer.py` · `phase1_ingestion/loader.py`

---

## Phase 2 — User preferences and validation

| Component | Responsibility |
|---|---|
| Preference model | `UserPreferences(location, budget, cuisines, min_rating, additional_preferences)` |
| Validation | Reject/coerce invalid input; fuzzy city matching with "Did you mean?" suggestion |
| Free-text safety | Truncate to 500 chars; strip control characters and newlines |
| City corpus | `allowed_cities_from_restaurants()` builds the allowed set from loaded corpus |

**Exit criteria:** preferences deserialize from form/API/CLI into one object; field-level `PreferencesError` raised on bad input; `milestone1 prefs-parse` CLI.

**Artifacts:** `phase2_preferences/models.py` · `phase2_preferences/parser.py` · `phase2_preferences/cities.py`

---

## Phase 3 — Integration layer (retrieval + prompt assembly)

| Component | Responsibility |
|---|---|
| Deterministic filter | Hard filters in order: location → min rating → budget → cuisine overlap |
| Ranking hint | Pre-sort by rating desc so LLM sees the best candidates first |
| Candidate cap | Truncate to `candidate_cap` (default 20) before building prompt |
| Prompt builder | System prompt + user message with preferences JSON + candidate table |
| Zero-candidate guard | Return `has_candidates=False` immediately; skip LLM call entirely |

**Exit criteria:** given preferences + dataset, produce `(candidates[], prompt_payload)` without calling the LLM; tests for edge cases (no match, single match, cap hit); `milestone1 prompt-build` CLI.

**Artifacts:** `phase3_integration/filter.py` · `phase3_integration/prompt.py` · `phase3_integration/output.py`

---

## Phase 4 — Recommendation engine (LLM)

| Concern | Approach |
|---|---|
| Model | Groq `llama-3.3-70b-versatile` via OpenAI-compatible API |
| Structured output | Prompt requests `{"rankings": [{restaurant_id, rank, explanation}]}` |
| Grounding | System prompt forbids inventing restaurants not in the candidate list |
| Hallucination guard | Validate every `restaurant_id` against candidate map; discard unknowns |
| Resilience | Retry on `429`; timeout after 30 s; deterministic top-k fallback on any failure |
| Fallback | `source="fallback"` — rating-sorted top-k with template explanations |

**Exit criteria:** end-to-end call returns ranked items with explanations; parser validates structure; failures degrade gracefully; `milestone1 recommend` CLI.

**Artifacts:** `phase4_llm/client.py` · `phase4_llm/models.py` · `phase4_llm/recommend.py`

---

## Phase 5 — Output and experience

| Surface | Responsibility |
|---|---|
| Rendering | `render_markdown()` and `render_plain()` — name, cuisine, rating, cost, AI explanation |
| Empty states | `no_candidates` ("no filter match") vs `llm_no_picks` ("model returned nothing") — distinct copy |
| Fallback notice | `source="fallback"` → banner: "AI ranking unavailable — showing top matches by rating." |
| Telemetry | Single-line JSON to stderr: counts, latency, token usage — no PII |

**Exit criteria:** demo path from user input to readable results in one run; `milestone1 recommend-run` CLI.

**Artifacts:** `phase5_output/renderer.py` · `phase5_output/empty_states.py` · `phase5_output/telemetry.py`

---

## Phase 6 — Backend (HTTP API)

| Concern | Approach |
|---|---|
| Role | Thin FastAPI service owning server-side secrets, dataset access, and orchestration |
| Endpoints | `POST /api/v1/recommendations` · `GET /health` · `GET /api/v1/meta` |
| Contract | Pydantic request/response DTOs; `422` on bad input with field-level errors; `503` if LLM not configured |
| Corpus | Thread-safe singleton — `load_restaurants()` called once; second request returns cached list |
| Cross-cutting | CORS restricted to allowed origins · telemetry on stderr · no raw user text in logs |
| Start command | `uvicorn milestone1.phase6_api.app:app --host 0.0.0.0 --port $PORT` |

**Exit criteria:** frontend completes one recommendation flow using only the API; `/health` returns `groq_configured: true`; Swagger at `/docs`.

**Artifacts:** `phase6_api/app.py` · `phase6_api/schemas.py` · `phase6_api/corpus.py`

---

## Phase 7 — Frontend (Next.js)

| Concern | Approach |
|---|---|
| Role | Primary user-facing surface: preference form + results list |
| Stack | Next.js 15 · TypeScript · Tailwind CSS |
| Data flow | Browser calls Phase 6 API only — `NEXT_PUBLIC_API_BASE_URL` env var |
| Form fields | Location (autocomplete) · Budget (toggle) · Cuisine (chips) · Min rating (star buttons) · Additional preferences |
| Results | Ranked cards — name, cuisines, rating, cost, type, AI explanation |
| Empty states | Distinct copy for `no_candidates` vs `llm_no_picks` via `EmptyState` component |
| UX | Loading spinner · skeleton shimmer · inline validation · error banner on network failure |

**Exit criteria:** README demo path — start API + UI, submit preferences, see ranked results or intentional empty state.

**Artifacts:** `frontend/app/page.tsx` · `frontend/app/layout.tsx` · `frontend/components/PreferenceForm.tsx` · `frontend/components/ResultCard.tsx` · `frontend/components/ResultsList.tsx` · `frontend/components/SourceBadge.tsx` · `frontend/components/EmptyState.tsx` · `frontend/lib/api.ts` · `frontend/types/index.ts`

---

## Phase 8 — Deployment: Render (backend) + Vercel (frontend)

The production deployment path. The browser bundle is purely static and only
ever talks to the Render URL over HTTPS. Provider keys live only on Render.

### Services (all free tier)

| Service | Role | Free limit |
|---|---|---|
| Render | FastAPI backend | 750 hrs/month; sleeps after 15 min idle |
| Vercel | Next.js frontend | Unlimited static; 100 GB bandwidth |
| Groq | LLM inference | Free dev quota |
| HuggingFace | Dataset streaming | Free; anonymous |

### Deploy steps

**1. Push to GitHub**
```bash
git init && git add . && git commit -m "initial"
gh repo create zomato-ai --public --push
```

**2. Deploy backend on Render**
- Render dashboard → New → Web Service → connect repo
- Build command: `pip install -e .`
- Start command: `uvicorn milestone1.phase6_api.app:app --host 0.0.0.0 --port $PORT`
- Health check path: `/health`

**3. Set env vars on Render**
```
GROQ_API_KEY  = your-key
GROQ_MODEL    = llama-3.3-70b-versatile
CORS_ORIGINS  = https://your-app.vercel.app
HF_TOKEN      = optional, raises HuggingFace rate limits
```

**4. Deploy frontend on Vercel**
- Vercel dashboard → New Project → import same repo
- Root directory: `frontend/`
- Add env var: `NEXT_PUBLIC_API_BASE_URL = https://your-service.onrender.com`

**5. Wire CORS**
Update `CORS_ORIGINS` on Render with the exact Vercel URL (no trailing slash). Render restarts automatically.

**6. Smoke test**
```bash
curl https://your-service.onrender.com/health
# → {"status":"ok","groq_configured":true}
```

**Cold start note:** Render free tier sleeps after 15 min of inactivity. Hit `/health` before a demo to wake the dyno (~30 s).

**Exit criteria:** browser at Vercel URL completes one recommendation; Render logs show telemetry JSON; `/health` shows `groq_configured: true`.

**Artifacts:** `render.yaml` (optional IaC) · `frontend/vercel.json` · `runtime.txt`

---

## Phase 9 — Deployment: Streamlit (demo / course submission)

A single-process Python app that exposes the same recommendation flow as the
CLI and API — no Node build, no separate SPA host, no CORS configuration.
Ideal for course demos, stakeholder previews, and fast sharing.

### How it differs from Phase 8

| Aspect | Phase 8 (Render + Vercel) | Phase 9 (Streamlit) |
|---|---|---|
| Processes | 2 (backend + frontend) | 1 (Streamlit server) |
| Language | Python + TypeScript | Python only |
| Hosting | Render + Vercel | Streamlit Community Cloud |
| CORS | Required | Not needed |
| Best for | Production / graded review | Demo / quick share |

### Architecture

```
Browser
  └── Streamlit Community Cloud
        ├── st.form() — preference inputs (phases 0–2 logic)
        ├── filter_and_rank() — phase 3
        ├── recommend_with_groq() — phase 4
        └── st.expander() — render_markdown() output (phase 5)
```

Streamlit imports `milestone1` packages directly — no HTTP call to a separate
backend. Secrets (`GROQ_API_KEY`) live in Streamlit's secrets manager, not in
any committed file.

### UI components

| Widget | Field |
|---|---|
| `st.selectbox` | Location (populated from corpus) |
| `st.select_slider` | Budget — Low / Medium / High |
| `st.multiselect` | Cuisines |
| `st.slider` | Minimum rating 0.0 – 5.0 |
| `st.text_area` | Additional preferences (max 500 chars) |
| `st.button` | Find Restaurants |
| `st.spinner` | While LLM is running |
| `st.expander` | Raw JSON / telemetry (optional debug) |

### Result cards

Each ranked restaurant rendered as:
```
st.markdown(f"**#{rank} {name}**")
st.caption(f"{cuisines} · {rating} · {cost}")
st.info(explanation)
```

Empty states match Phase 5 copy — distinct messages for `no_candidates` vs
`llm_no_picks` vs `fallback`.

### Deploy steps

**1. Install Streamlit dependency**
```bash
pip install -e ".[streamlit]"   # adds streamlit to optional deps
```

**2. Create `streamlit_app.py` at repo root**
```python
# streamlit_app.py — Cloud entrypoint
from milestone1.phase9_streamlit.app import main
main()
```

**3. Run locally**
```bash
streamlit run streamlit_app.py
# → http://localhost:8501
```

**4. Deploy to Streamlit Community Cloud**
- Go to share.streamlit.io → New app → connect GitHub repo
- Main file path: `streamlit_app.py`
- Add secrets in the dashboard (Settings → Secrets):
  ```toml
  GROQ_API_KEY = "your-key-here"
  GROQ_MODEL   = "llama-3.3-70b-versatile"
  ```
- Click Deploy — app is live at `https://your-app.streamlit.app`

**5. Smoke test**
Open the URL, select Bellandur, set budget to High, rating to 4.0, click
Find Restaurants. Verify 5 ranked cards appear with AI explanations.

### Secrets handling

```python
# Inside the Streamlit app — reads from st.secrets in Cloud,
# falls back to .env locally
import streamlit as st
from milestone1.phase0.settings import load_settings

api_key = st.secrets.get("GROQ_API_KEY") or load_settings().groq_api_key
```

**Never put `GROQ_API_KEY` in `streamlit_app.py` or any committed file.**

### Resource limits (free tier)

| Limit | Value |
|---|---|
| RAM | 1 GB |
| CPU | Shared |
| Sleep | After ~5 min idle (wakes in ~30 s) |
| Dataset `load_limit` | Keep ≤ 5,000 rows to stay within RAM |
| `candidate_cap` | Keep ≤ 20 to control Groq token usage |

**Exit criteria:** `streamlit_app.py` documented in README; reviewer can open the hosted URL and complete one successful recommendation or see an intentional empty state; no API keys committed.

**Artifacts:** `src/milestone1/phase9_streamlit/app.py` · `streamlit_app.py` · `docs/streamlit-deploy.md` · `pyproject.toml [streamlit]` optional dep

---

## Phase 10 — Hardening and handoff (optional but recommended)

- Automated tests: filter edge cases, prompt shape, JSON parsing (fixture-based), API contract tests
- README: install → set `GROQ_API_KEY` → run API + UI → CLI fallbacks → limitations
- Cost/latency notes: candidate cap rationale, model id, when to raise load limits
- Caching: optional in-process LRU for repeated queries (only if measured need)
- PII audit: confirm no raw user text in logs at any level

---

## Appendix A — Edge Cases Matrix

### Phase 1 — Data Ingestion Edge Cases
| # | Edge Case | Handling |
|---|-----------|----------|
| 1.1 | HuggingFace dataset unreachable / download failure | Catch `ConnectionError`; raise `DatasetLoadError` with clear message |
| 1.2 | Rating string `"NEW"`, empty, or `None` | Map to `0.0` |
| 1.3 | Rating string `"4.1/5"` format | Parse float before `/` |
| 1.4 | Rating value outside `[0, 5]` | Clamp to `[0.0, 5.0]` |
| 1.5 | `approx_cost` with commas or non-numeric | Strip commas, parse int; default `0` on failure |
| 1.6 | Empty or `None` cuisine string | Default to `["Unknown"]` |
| 1.7 | Duplicate restaurants `(name, location)` | Keep highest-rated row |
| 1.8 | Unicode / special chars in restaurant names | Preserve as-is; strip only control characters |
| 1.9 | Row with missing `name` or `location` | Skip row entirely |
| 1.10 | Dataset has zero valid rows after cleaning | Raise `EmptyDatasetError` |

### Phase 2 — User Preferences Edge Cases
| # | Edge Case | Handling |
|---|-----------|----------|
| 2.1 | Location is empty or `None` | Raise `PreferencesError("location is required")` |
| 2.2 | Location not in dataset | Fuzzy match top-3 suggestions; raise "Did you mean…?" |
| 2.3 | Budget value not in `[Low, Medium, High]` | Raise validation error |
| 2.4 | `min_rating` outside `[0.0, 5.0]` | Clamp to `[0.0, 5.0]` |
| 2.5 | `cuisines` list is empty | Treat as "no cuisine filter" — all cuisines match |
| 2.6 | `additional_preferences` exceeds 500 chars | Truncate to 500 |
| 2.7 | Control characters / newlines in free text | Strip `\x00-\x1f` except spaces |
| 2.8 | Script injection / HTML tags in free text | Strip `<…>` tags |

### Phase 3 — Integration Edge Cases
| # | Edge Case | Handling |
|---|-----------|----------|
| 3.1 | Zero candidates after all filters | Return `has_candidates=False`; skip LLM |
| 3.2 | Exactly 1 candidate | Proceed normally |
| 3.3 | Candidates exceed `candidate_cap` (default 20) | Truncate after rating sort |
| 3.4 | All restaurants share same rating | Stable sort preserves original order |
| 3.5 | Cuisine filter with no overlap in dataset | Return zero candidates gracefully |

### Phase 4 — LLM Edge Cases
| # | Edge Case | Handling |
|---|-----------|----------|
| 4.1 | `GROQ_API_KEY` missing or empty | Return fallback immediately with `source="fallback"` |
| 4.2 | Groq API returns `429` (rate limited) | Retry up to 2× with exponential backoff |
| 4.3 | Groq API timeout (> 30 s) | Abort; return fallback |
| 4.4 | LLM returns malformed / non-JSON response | Catch parse error; return fallback |
| 4.5 | LLM hallucinates restaurant IDs not in candidates | Discard unknown IDs; keep valid ones |
| 4.6 | LLM returns empty `rankings` array | Return `llm_no_picks` empty state |
| 4.7 | LLM returns more items than candidates | Truncate to candidate count |

### Phase 5 — Output Edge Cases
| # | Edge Case | Handling |
|---|-----------|----------|
| 5.1 | `source="fallback"` | Show banner: "AI ranking unavailable" |
| 5.2 | No candidates at all (`no_candidates`) | Distinct message: "No restaurants match" |
| 5.3 | LLM returned nothing (`llm_no_picks`) | Distinct message: "AI couldn't pick" |
| 5.4 | Very long AI explanation text | Truncate to 500 chars |
| 5.5 | Special characters in restaurant names | Escape for markdown rendering |

### Phase 6 — API Edge Cases
| # | Edge Case | Handling |
|---|-----------|----------|
| 6.1 | Missing required fields in request | `422` with field-level Pydantic errors |
| 6.2 | `GROQ_API_KEY` not configured | `/health` → `groq_configured: false`; `/recommendations` → fallback |
| 6.3 | Concurrent requests | Thread-safe corpus singleton |
| 6.4 | CORS from unknown origin | Blocked by CORSMiddleware |
| 6.5 | Very large request payload | Pydantic validation + 500-char limit |

### Phase 7 — Frontend Edge Cases
| # | Edge Case | Handling |
|---|-----------|----------|
| 7.1 | API unreachable / network error | Error banner: "Could not reach the server" |
| 7.2 | API returns `503` (Groq not configured) | Specific error message |
| 7.3 | API returns `422` (validation error) | Show inline field errors with suggestions |
| 7.4 | Slow API response (> 5 s) | Loading spinner + skeleton shimmer |
| 7.5 | Empty results (`no_candidates`) | `EmptyState` component with distinct copy |
| 7.6 | Fallback results (`source="fallback"`) | `SourceBadge` component with warning |

