# Traffic Consequence AI

A local decision-support prototype for citizen-reported traffic complaints. Modules 1–3 collect reports, provide AI-assisted analysis, and connect related complaints in a NetworkX graph. Module 4 adds an authority review dashboard with metrics, filters, a coordinate-backed map, traceable AI summary records, and a human review-status workflow. It does not verify citizen statements, infer causation, make official decisions, or control traffic systems.

## Prerequisites

- Python 3.11 or newer
- Node.js 20 or newer and npm
- Optional: a Google Gemini API key for summaries; the app runs without one

## Setup and run

```powershell
cd traffic-consequence-ai
Copy-Item .env.example .env
python -m venv backend/.venv
backend/.venv/Scripts/Activate.ps1
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload
```

In a second terminal:

```powershell
cd traffic-consequence-ai/frontend
npm install
npm run dev
```

Open the Vite URL (normally http://localhost:5173). FastAPI Swagger docs are at http://localhost:8000/docs. SQLite is created at `backend/traffic_consequence.db` when launched from the repository root. Set `DATABASE_URL` in `.env` to change it.

## Configuration

Copy `.env.example` to `.env` and set values as needed. `GEMINI_API_KEY` is optional; absent credentials produce an explicit “AI summary unavailable” status. For Gemini, install `google-genai` in the backend venv, then provide the key. Optional Hugging Face zero-shot classification: install `transformers` and `torch`, set `ENABLE_HUGGINGFACE=true` and `CLASSIFIER_MODEL` to a compatible model. Optional Sentence Transformers: install `sentence-transformers` and set `ENABLE_SENTENCE_TRANSFORMERS=true`. These can download model weights on first use. The app defaults to deterministic keyword classification and token-Jaccard duplicate hints with no model download.

`FRONTEND_ORIGINS` accepts comma-separated allowed origins. `HOTSPOT_RADIUS_KM` and `HOTSPOT_MIN_REPORTS` configure geographic grouping.

## Demo data and CSV

Use the **Load synthetic demo** button or call `POST /api/demo/seed`. The bundled sample records are explicitly synthetic and use fictional location labels without coordinates. The supplied `backend/data/india_traffic_complaints_demo.csv` is bundled and also available to import through the CSV control. Its locality/city/state fields become a display location; because it contains no latitude/longitude, those rows are excluded from geographic hotspot clustering. Source category text is not treated as model output. Invalid rows are skipped and returned with row numbers and errors.

CSV required columns are `complaint_text`, `location_name` (aliases: `locality`, `location`) and `severity`. `latitude`, `longitude`, and `timestamp` are optional. For the supplied dataset, `reported_date` and `reported_time` are accepted aliases and city/state are appended to locality.

## API

- `POST /api/complaints`, `GET /api/complaints`, `GET /api/complaints/{id}`
- `POST /api/complaints/import` (multipart CSV)
- `GET /api/analysis/{id}`
- `GET /api/graph`, `GET /api/hotspots`, `GET /api/priority`
- `GET /api/dashboard/overview?recent_window_days=7&chart_days=30&priority_limit=8`
- `GET /api/dashboard/complaints?q=&category=&severity=&review_status=&sort_by=newest&page=1&page_size=20`
- `PATCH /api/dashboard/complaints/{id}/review-status` with `{"review_status":"under_review"}`
- `GET /api/dashboard/map`
- `GET /api/dashboard/summaries?page=1&page_size=20`
- `POST /api/demo/seed`, `GET /api/health`

Dashboard query bounds are validated by FastAPI/Pydantic. Complaint review states are `new`, `under_review`, and `reviewed`. Startup applies an idempotent SQLite migration for existing complaint tables. The review state is not identity-attributed.

## Priority score and assumptions

Prototype score per complaint, range 0–100:

`100 × (0.35 × normalized severity + 0.25 × category frequency + 0.25 × category recurrence + 0.15 × recency)`

Severity maps low/medium/high/critical to 1/4, 2/4, 3/4, 4/4. Frequency is category count divided by 10, capped at 1. Recurrence is other reports in the same category divided by 5, capped at 1. Recency uses a 30-day half-life. This is an explainable prototype ranking, not an official traffic-risk standard. Categories are coarse; hotspot clustering uses coordinate proximity plus matching category, and currently may be order-sensitive for chained nearby points. Missing coordinates mean no geographic hotspot determination. All hotspots are labelled potential and causes are citizen-reported until verified.

## Tests

```powershell
cd backend
python -m pip install -r requirements.txt
python -m pytest
```

Tests cover request validation, classifier fallback, graph relations, hotspot grouping, priority scoring, dashboard aggregation, search/filtering, pagination, review-state persistence, and empty results. The frontend has no test runner configured; its production TypeScript/Vite build is the frontend verification step.

## Scope and next module

## Module 4 dashboard

The **Overview** cards and charts are computed from stored complaints. **Complaints** combines the original submission/import tools with a review table supporting text/location search, category/severity/review filters, newest/severity/priority sorting, and server-side pagination. Selecting a row opens the original text, AI analysis, similarity hints, score, and a human-editable review state. **Map & Hotspots** maps only stored valid coordinates, shows potential hotspot radii and their source complaint IDs, and lists reports that cannot be mapped. **AI Summaries** shows stored summary status, source/related report IDs, related categories/locations, uncertainty notes, and any generated next steps. No next-step text is fabricated when the existing analysis did not provide it.

The review workflow has no authentication or role-based access control in this prototype; any client that can reach the API can change statuses. It does not record reviewer identity or provide an audit trail. OpenStreetMap tiles require network access in the browser. Missing coordinates are never inferred. Summary provenance is limited to the source complaint and existing similarity references. Potential hotspots do not prove causation, citizen-reported causes are not verified, and priority scores are not official traffic-risk standards. No automatic traffic-control actions are implemented.

Still incomplete for production authority use: authenticated staff roles, reviewer identity and immutable audit history, formal verification/evidence workflows, jurisdiction-specific policy and assignments, and accessible operational map/chart review. These require authority requirements and deployment controls beyond this prototype.
