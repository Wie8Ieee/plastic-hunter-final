# Plastic Hunter AI

## Runtime

- The production demo is the Python FastAPI app at the repository root.
- Run command: `python -m uvicorn main:app --host 0.0.0.0 --port 8000`
- Root path `/` serves `static/index.html`.
- Health check: `GET /healthz`.

## Stack

- Backend: Python 3.11, FastAPI, Uvicorn.
- CV demo interface: Pillow and NumPy.
- CV research validation: Trash-ICRA19 and River Floating Trash Dataset results documented in README and Evidence Sheet.
- Sonar: reproducible simulation in `sonar.py`; not hardware validated.
- Database: SQLite, auto-created and seeded by `database.py`.
- Frontend: single-page HTML/CSS/JavaScript with Leaflet.js and Chart.js.

## Core Files

- `main.py` - API routes, validation, evidence and disclosure endpoints.
- `detector.py` - lightweight deployable CV demo interface and annotation.
- `sonar.py` - eco-sonar simulation and sustainability KPI calculations.
- `database.py` - SQLite schema, indexes, seed data, dashboard analytics.
- `static/index.html` - commercial-style mission dashboard and demo UI.
- `README.md` - main technical documentation.
- `SUBMISSION_CONCEPT_DOCUMENT.md` - competition technical brief.

## Demo Flow

Mission Started -> Passive Sonar -> Signal Analysis -> Hybrid Decision -> CV Verification -> Database -> Dashboard -> Map -> Evidence Generated.

## Scientific Scope

- CV research metrics are real project evaluation results.
- Live CV demo is a lightweight deployable interface, not the trained GPU model.
- Sonar KPIs are simulation calculations and require hardware validation.
- Manual baseline and plastic type mix values are explicitly labeled estimated when shown.

## Operational Notes

- Do not install `ultralytics` in the constrained demo environment unless a larger GPU-capable target is available.
- `detections.db` and generated `results/` images are runtime artifacts and can be regenerated.
- Node/React workspace artifacts are scaffolding from earlier prototyping and are not required for the submitted FastAPI demo.
