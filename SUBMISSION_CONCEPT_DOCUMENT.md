# Plastic Hunter AI - Competition Technical Brief

## Executive Summary

Plastic Hunter AI is a marine pollution monitoring prototype for the IEEE AESS Sustainability Hackathon 2026. The system combines a lightweight browser demo, a FastAPI backend, SQLite mission logging, a research-backed CV validation track, and a reproducible eco-sonar simulation.

The project is not presented as deployed hardware. It is a software demonstration of an integrated monitoring workflow:

```text
Mission Started -> Passive Sonar -> Signal Analysis -> Hybrid Decision
-> CV Verification -> Database -> Dashboard -> Map -> Evidence Generated
```

## Technical Scope

### Computer Vision

The computer vision research track uses real marine debris datasets:

| Dataset | Models Evaluated | Best Result |
|---|---|---|
| Trash-ICRA19 | YOLOv8s, Faster R-CNN, MobileNet SSD | YOLOv8s: 97.77% mAP@0.5, 122.10 FPS |
| River Floating Trash Dataset | Cross-domain testing | Faster R-CNN: 32.22% mAP@0.5 |

The live web demo uses a lightweight Pillow/NumPy interface to keep the deployment portable. It preserves the user workflow and API contract but is not claimed to be the trained production model.

### Sonar

The sonar module is a simulation engine using:

- Mackenzie sound-speed equation.
- Spherical spreading plus Thorp absorption.
- Knudsen-Wenz ambient noise approximation.
- Active sonar SNR and detection probability.
- Conservative passive acoustic-anomaly estimates.
- Cumulative SEL, duty-cycle, range, and acoustic energy proxy comparisons.

The sonar results are reproducible calculations and require hardware validation before deployment claims.

## Architecture

```text
static/index.html        Browser dashboard and demo UI
main.py                  FastAPI routes, validation, evidence, disclosure
detector.py              Lightweight CV demo interface and annotation
sonar.py                 Eco-sonar simulation and KPI calculations
database.py              SQLite schema, indexes, seed data, analytics
requirements.txt         Python runtime dependencies
```

## API Summary

| Method | Endpoint | Description |
|---|---|---|
| GET | `/` | Frontend application |
| GET | `/healthz` | Health check |
| POST | `/detect` | Image upload and lightweight CV demo result |
| GET | `/results` | Stored detections |
| GET | `/stats` | Dashboard statistics and documented estimates |
| POST | `/demo` | Reset seeded demo data |
| GET | `/evidence` | Judge-ready evidence sheet data |
| GET | `/disclosure` | AI/tool/data disclosure |
| POST | `/sonar/ping` | Sonar scenario simulation |

## Dashboard Interpretation

The dashboard separates values by evidence type:

- Observed detections: stored in SQLite.
- CV metrics: research evaluation on real datasets.
- Sonar KPIs: reproducible simulation calculations.
- Manual baseline comparison: estimated demo assumption, explicitly labeled as not measured environmental impact.
- Plastic type mix: estimated for seeded historical rows because those rows store total counts rather than per-object labels.

## Limitations

| Area | Limitation |
|---|---|
| CV demo | Lightweight interface is not the trained YOLOv8s runtime model. |
| Sonar | Simulation only; no hardware validation yet. |
| Propagation | No bathymetry, ray tracing, or multipath. |
| Passive mode | Acoustic-anomaly estimate, not semantic target classification. |
| Database | Historical seeded rows store counts and confidence, not per-object labels. |
| Deployment | Large GPU model packages are intentionally avoided for constrained hosting. |

## Production Readiness Notes

- Runtime files such as `detections.db` and generated images are recreated automatically and should not be source-controlled.
- The backend validates upload type, upload size, latitude/longitude bounds, and result image filenames.
- SQLite indexes support dashboard, history, and map queries.
- `/evidence` and `/disclosure` expose the scientific scope and assumptions directly for judges.

## Recommended Next Steps

1. Run the trained CV pipeline on a GPU-capable deployment target.
2. Store per-object detection labels in SQLite for historical type analytics.
3. Validate sonar assumptions with real acoustic hardware trials.
4. Add authentication and project/team separation for multi-user field deployment.
5. Add exportable mission reports for cleanup teams and reviewers.
