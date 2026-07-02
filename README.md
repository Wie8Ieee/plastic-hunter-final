# Plastic Hunter

Plastic Hunter is a marine pollution monitoring prototype for the IEEE AESS Sustainability Hackathon 2026. It combines a research-backed computer-vision validation track with a reproducible eco-sonar simulation and a browser-based mission dashboard.

The project is designed for a live technical demonstration: upload a surface image, inspect annotated detections, review geospatial monitoring data, run sonar trade-off scenarios, and generate a concise evidence sheet.

## What It Demonstrates

- Surface plastic monitoring through a lightweight deployable CV demo interface.
- Research-backed CV validation using real marine debris datasets.
- Eco-sonar sustainability trade-offs using reproducible physics-based simulation.
- SQLite-backed mission logging, dashboard analytics, map visualization, and evidence generation.

## Research Foundation

The computer vision component is research-backed using real marine debris datasets.
Our team trained and evaluated YOLOv8s, Faster R-CNN, and MobileNet SSD on Trash-ICRA19, with cross-domain testing on the River Floating Trash Dataset.
YOLOv8s achieved 97.77% mAP@0.5 at 122.10 FPS.

Cross-domain validation:

| Dataset | Best Model | Metric |
|---|---:|---:|
| Trash-ICRA19 | YOLOv8s | 97.77% mAP@0.5, 122.10 FPS |
| River Floating Trash Dataset | Faster R-CNN | 32.22% mAP@0.5 |

The live demo uses a lightweight Pillow/NumPy interface so it can run on constrained deployment environments without downloading large GPU model packages. This interface is not presented as hardware-validated or production CV inference.

## Architecture

```text
Browser SPA (static/index.html)
  -> FastAPI application (main.py)
    -> Lightweight CV demo interface (detector.py)
    -> Eco-sonar simulation engine (sonar.py)
    -> SQLite persistence and analytics (database.py)
    -> Evidence and disclosure endpoints
```

Runtime files:

- `results/` stores annotated upload images generated during use.
- `detections.db` is created automatically and seeded by `database.py`.

## Mission Workflow

1. Mission started with seeded or uploaded site evidence.
2. Passive sonar mode estimates low-impact acoustic anomaly detection.
3. Signal analysis computes SNR and detection probability.
4. Hybrid decision compares conventional and eco-adaptive active sonar.
5. CV verification logs surface image evidence.
6. SQLite stores detections and mission metadata.
7. Dashboard summarizes observed detections and sustainability KPIs.
8. Map shows geospatial detection hotspots.
9. Evidence Sheet generates a judge-ready technical summary.

## Backend API

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/` | Serve the single-page frontend |
| `GET` | `/healthz` | Health check |
| `POST` | `/detect` | Upload an image, run the lightweight CV demo, store the result |
| `GET` | `/results` | Return stored detections |
| `GET` | `/stats` | Return dashboard statistics and documented estimates |
| `POST` | `/demo` | Reset and reseed demo detections |
| `GET` | `/results/{filename}` | Serve an annotated result image |
| `GET` | `/evidence` | Return technical evidence sheet data |
| `GET` | `/disclosure` | Return technical scope, library, dataset, and limitation disclosure |
| `POST` | `/sonar/ping` | Run the sonar scenario simulation |

## Sonar Simulation

The sonar module is simulation-based. It implements:

- Mackenzie sound-speed calculation.
- Spherical spreading plus Thorp absorption.
- Knudsen-Wenz ambient noise approximation.
- Active sonar SNR and P(detect) estimates.
- Conservative passive acoustic-anomaly estimates.
- Cumulative SEL, duty-cycle, range, and energy proxy comparisons.

Default eco-adaptive comparison:

| Parameter | Conventional | Eco-Adaptive |
|---|---:|---:|
| Source level | 200 dB | 188 dB |
| Ping interval | 5 s | 15 s |
| Duty cycle | 2.00% | 0.67% |
| Mission duration | 60 min | 60 min |

All sonar values are reproducible calculations, not hardware test results.

## Dashboard Notes

Dashboard values are labeled by source:

- Observed values come from the SQLite `detections` table.
- CV validation metrics come from the team's research evaluation.
- Sonar KPIs come from `sonar.py` calculations.
- Manual-survey comparison values are explicitly marked as estimated demo assumptions, not measured environmental impact.
- Plastic type mix for seeded historical rows is estimated because historical rows store total counts, not per-object class labels.

## Setup

Requirements:

- Python 3.11+

Install dependencies:

```bash
pip install -r requirements.txt
```

Run locally:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Run with Docker:

```bash
docker build -t plastic-hunter .
docker run --rm -p 8000:8000 plastic-hunter
```

Open:

```text
http://localhost:8000
```

## Reproducibility Checks

```bash
python -m py_compile main.py database.py detector.py sonar.py
curl http://localhost:8000/healthz
curl http://localhost:8000/stats
curl http://localhost:8000/evidence
```

The default database seed is deterministic enough for demo use and can be regenerated with:

```bash
curl -X POST http://localhost:8000/demo
```

## Limitations

- The sonar component is currently simulation-based and requires hardware validation.
- The CV component is supported by real dataset experiments, but the live demo uses a lightweight deployable interface.
- The live demo does not run YOLOv8/PyTorch inference because deployment disk limits make that impractical.
- Sonar transmission loss does not include bathymetry, multipath, or ray tracing.
- Passive sonar mode is an acoustic-anomaly estimate, not semantic classification.
- Demo upload locations are user-supplied or selected from seeded coastal coordinates; production deployment should ingest trusted GPS metadata.

## Future Work

- Deploy the trained model pipeline on a GPU-capable environment.
- Add real sonar hardware trials and calibrated underwater acoustic datasets.
- Store per-object CV classes in the database for historical type analytics.
- Add authenticated multi-user monitoring workflows.
- Add exportable reports for cleanup operations and field validation.

## License

MIT License
