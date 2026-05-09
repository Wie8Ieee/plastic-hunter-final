# Plastic Hunter AI

An AI-powered marine plastic pollution detection system. Upload ocean/beach images to detect plastic waste using Computer Vision, then visualize results on an interactive global map with statistics dashboards.

## Run & Operate

- `artifacts/plastic-hunter: web` workflow runs the Python FastAPI server on port 8000
- App is accessible at `/` (root preview path)
- Backend API tested via `curl http://localhost:80/stats`

## Stack

- **Backend**: Python 3.11 + FastAPI + Uvicorn
- **Detection**: CV simulation using Pillow + NumPy (edge-guided bounding box placement)
- **Database**: SQLite (`detections.db` at workspace root)
- **Frontend**: Single-page HTML + Leaflet.js (map) + Chart.js (charts)
- **Image annotation**: Pillow (draws bounding boxes and saves annotated JPEGs to `results/`)

## Where things live

- `main.py` — FastAPI routes (`POST /detect`, `GET /results`, `GET /stats`, static files)
- `detector.py` — CV-simulation detection engine + Pillow annotation
- `database.py` — SQLite schema init, CRUD, seeded demo data (12 global locations)
- `static/index.html` — Full single-page frontend
- `results/` — Annotated output images
- `detections.db` — SQLite database (auto-created on startup)
- `artifacts/plastic-hunter/.replit-artifact/artifact.toml` — Routes `/` → port 8000

## Architecture decisions

- **Simulation over YOLOv8**: Ultralytics + PyTorch pulls 400 MB+ of CUDA packages that exceed Replit's disk quota on the free tier. The CV simulation uses Pillow edge detection + image statistics to place plausible bounding boxes — same API contract, zero model download.
- **SQLite over PostgreSQL**: The app is self-contained Python with no Node.js DB dependency; SQLite is seeded with 12 realistic demo detections at startup.
- **FastAPI serves static files**: The single-page frontend is served directly by FastAPI's `StaticFiles` mount — no separate Vite/Node server needed.
- **Artifact.toml points to Python port**: The `artifacts/plastic-hunter` artifact was bootstrapped as react-vite to register the `/` preview path, then its `artifact.toml` was updated to point `localPort = 8000` at the Python server.

## Product

- **Detect tab**: Upload any image → AI analysis → annotated image with colour-coded bounding boxes + confidence scores + severity rating
- **Map tab**: Interactive Leaflet.js dark map with circle markers (sized by count, coloured by severity) for every detection event
- **Dashboard tab**: KPI cards, bar chart (detections per day), doughnut chart (confidence distribution), baseline vs AI-optimised reduction banner (~25.5% improvement)
- **History tab**: Full table of all detections from SQLite

## User preferences

- Python FastAPI for backend
- Single-page HTML frontend (not React)
- Leaflet.js for maps, Chart.js for charts
- SQLite for storage

## Gotchas

- Do NOT install `ultralytics` — it pulls PyTorch + CUDA packages that exceed disk quota
- The `detections.db` is seeded with 12 demo rows on first startup; it persists across restarts
- Annotated images are saved to `results/` — this directory must exist (created in `detector.py`)
- The `artifacts/plastic-hunter` workflow runs the Python server — the Vite/React scaffold files in that directory are unused scaffolding

## Pointers

- See `pnpm-workspace` skill for the Node.js workspace structure (separate from this Python app)
