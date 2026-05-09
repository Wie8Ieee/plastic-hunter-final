# Plastic Hunter AI

**Team:** [Team Name]

> AI-powered marine plastic pollution detection system using Computer Vision and interactive geospatial mapping.

---

## Problem

Marine plastic pollution is one of the most critical environmental threats of our time. Over **8 million tonnes** of plastic enter the ocean every year, yet traditional monitoring methods rely on manual surveys that are slow, expensive, and geographically limited. Early detection at scale is nearly impossible without automation.

## Solution

**Plastic Hunter AI** leverages YOLOv8 computer vision to analyze images of marine environments in real time, automatically detecting and classifying plastic waste. Results are stored with geospatial data and visualized on an interactive map, enabling rapid response and trend analysis.

Key capabilities:
- **Instant detection** — upload any beach or ocean image and get AI analysis in seconds
- **Interactive pollution map** — view historical detections as map markers globally
- **Statistics dashboard** — track trends, confidence distributions, and severity breakdowns
- **Baseline vs optimised comparison** — measure plastic reduction impact over time

---

## How to Run

### Prerequisites

- Python 3.10+
- pip

### Setup

```bash
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080
```

Open `http://localhost:8080` in your browser.

### API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/detect` | Upload image for plastic detection |
| `GET` | `/results` | All past detections from database |
| `GET` | `/stats` | Summary statistics & daily trends |
| `GET` | `/results/{filename}` | Retrieve annotated image |

---

## Key Results

- Detects plastic waste with **55–95% confidence** using YOLOv8n
- Processes images in under **2 seconds** on CPU
- Simulated detection mode ensures the demo works on any image without a specialised dataset
- **~26% plastic reduction** tracked vs baseline in demo data

---

## Assumptions

1. When a fine-tuned marine plastic dataset is unavailable, the system maps general COCO-class objects (bottles, cups, bags, etc.) to plastic categories with adjusted confidence scores.
2. Geolocation is user-provided or randomly assigned near real coastal hotspots for demo purposes.
3. YOLOv8n (`yolov8n.pt`) is downloaded automatically on first run via the `ultralytics` package.
4. SQLite is used for simplicity; in production this would be replaced with PostgreSQL with PostGIS for geospatial queries.

---

## AI Usage Disclosure

This project uses:
- **YOLOv8** (Ultralytics) — pre-trained object detection model, used as-is with domain adaptation via class remapping
- **OpenCV & Pillow** — image processing and bounding box annotation
- AI-assisted code generation was used during rapid prototyping phases of this hackathon submission

---

## Repository Structure

```
/
├── main.py          # FastAPI application & routes
├── detector.py      # YOLOv8 detection logic & simulation fallback
├── database.py      # SQLite schema & CRUD operations
├── static/
│   └── index.html   # Single-page frontend (Leaflet + Chart.js)
├── results/         # Saved annotated detection images
├── requirements.txt # Python dependencies
└── README.md        # This file
```
