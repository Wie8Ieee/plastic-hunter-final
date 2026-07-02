import os
import random
import sqlite3
import time
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from database import get_all_results, get_stats, init_db, reset_and_reseed, save_detection
from detector import run_detection
from sonar import run_sonar_scenario, trade_off_explanation

app = FastAPI(title="Plastic Hunter AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

STATIC_DIR = Path("static")
STATIC_DIR.mkdir(exist_ok=True)

init_db()

COASTAL_LOCATIONS = [
    (36.8065, 10.1815),
    (37.9838, 23.7275),
    (41.9028, 12.4964),
    (35.6762, 139.6503),
    (25.7617, -80.1918),
    (51.5074, -0.1278),
    (1.3521, 103.8198),
    (19.4326, -99.1332),
    (-33.8688, 151.2093),
    (22.3964, 114.1095),
    (14.0583, 108.2772),
    (-8.3405, 115.0920),
]


@app.get("/")
async def root():
    return FileResponse("static/index.html")


@app.get("/favicon.ico")
async def favicon():
    path = STATIC_DIR / "favicon.ico"
    if path.exists():
        return FileResponse(str(path))
    raise HTTPException(status_code=404, detail="Not found")


@app.post("/detect")
async def detect(
    file: UploadFile = File(...),
    latitude: float = Form(None),
    longitude: float = Form(None),
):
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Only image files are accepted.")

    image_bytes = await file.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty file uploaded.")

    try:
        t0 = time.time()
        result = run_detection(image_bytes, file.filename or "upload.jpg")
        processing_time_ms = round((time.time() - t0) * 1000, 1)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))

    if latitude is None or longitude is None:
        lat, lon = random.choice(COASTAL_LOCATIONS)
        jitter_lat = random.uniform(-2.0, 2.0)
        jitter_lon = random.uniform(-2.0, 2.0)
        lat = round(lat + jitter_lat, 4)
        lon = round(lon + jitter_lon, 4)
    else:
        lat = round(float(latitude), 4)
        lon = round(float(longitude), 4)

    record_id = save_detection(
        image_name=result["annotated_image"],
        plastic_count=result["plastic_count"],
        avg_confidence=result["avg_confidence"],
        latitude=lat,
        longitude=lon,
        processing_time_ms=processing_time_ms,
    )

    return JSONResponse({
        "id":                 record_id,
        "plastic_count":      result["plastic_count"],
        "avg_confidence":     result["avg_confidence"],
        "severity":           result["severity"],
        "detections":         result["detections"],
        "annotated_image":    f"/results/{result['annotated_image']}",
        "detection_mode":     result["detection_mode"],
        "processing_time_ms": processing_time_ms,
        "location":           {"latitude": lat, "longitude": lon},
    })


@app.get("/results")
async def get_results():
    rows = get_all_results()
    return JSONResponse(rows)


@app.get("/stats")
async def stats():
    data = get_stats()
    return JSONResponse(data)


@app.post("/demo")
async def reload_demo():
    count = reset_and_reseed()
    return JSONResponse({"message": "Demo data reloaded successfully", "records": count})


@app.get("/results/{filename}")
async def get_result_image(filename: str):
    path = RESULTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(str(path), media_type="image/jpeg")


@app.get("/evidence")
async def evidence():
    from datetime import datetime
    stats = get_stats()
    sonar = run_sonar_scenario()
    m = sonar["metrics"]
    c = sonar["conventional"]
    e = sonar["eco_adaptive"]
    return JSONResponse({
        "problem": (
            "Marine plastic debris accumulates below the surface, undetectable by visual methods alone. "
            "Conventional continuous-active sonar creates acoustic disturbance harmful to cetaceans and marine life."
        ),
        "core_function": (
            "Eco-adaptive sonar reduces source level −12 dB and duty cycle by 67% using adaptive ping management. "
            "Combined with CV-based surface detection, the system provides multi-layer marine pollution monitoring "
            "with quantifiable sustainability improvements."
        ),
        "baseline": {
            "description": "Conventional active sonar: fixed 200 dB SL, continuous pinging at 5 s interval (2% duty cycle).",
            "cumulative_sel_dB":    c["sel_cum_dB"],
            "duty_cycle_pct":       c["duty_cycle_pct"],
            "n_pings_per_mission":  c["n_pings"],
            "max_range_m":          c["max_range_m"],
        },
        "improved_case": {
            "description": "Eco-adaptive sonar: 188 dB SL (−12 dB), 15 s ping interval (0.67% duty cycle).",
            "cumulative_sel_dB":    e["sel_cum_dB"],
            "duty_cycle_pct":       e["duty_cycle_pct"],
            "n_pings_per_mission":  e["n_pings"],
            "max_range_m":          e["max_range_m"],
        },
        "test_conditions": {
            "frequency_kHz":       10,
            "sea_state":           3,
            "depth_m":             50,
            "mission_duration_min": 60,
            "propagation_model":   "Spherical spreading + Thorp absorption",
            "noise_model":         "Knudsen-Wenz ambient noise",
        },
        "primary_technical_kpi": {
            "metric":             "Detection retention vs conventional",
            "value":              f"{m['eco_detection_retention_pct']}%",
            "max_range_eco_m":    m["eco_max_range_m"],
            "max_range_conv_m":   m["conv_max_range_m"],
        },
        "primary_sustainability_kpi": {
            "metric":                      "Cumulative Sound Exposure Level reduction",
            "sel_reduction_dB":            m["sel_reduction_dB"],
            "sel_reduction_pct":           m["sel_reduction_pct"],
            "duty_cycle_reduction_pct":    m["duty_cycle_reduction_pct"],
            "energy_reduction_pct":        m.get("energy_reduction_pct", 0.0),
        },
        "trade_off_explanation": trade_off_explanation(m),
        "limitation": (
            "Spherical spreading TL only; no ray-tracing, multi-path, or bathymetry. "
            "CV detection is edge-guided simulation, not a calibrated ML model. "
            "Marine mammal avoidance not yet implemented."
        ),
        "repository_link":  "https://github.com/[team]/plastic-hunter-ai",
        "cv_stats": {
            "total_scans":        stats["total_scans"],
            "plastics_detected":  stats["total_plastics_detected"],
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
    })


@app.get("/disclosure")
async def disclosure():
    return JSONResponse({
        "ai_tools": [
            {"name": "Replit AI (Claude)", "use": "Code generation, architecture design, and debugging assistance"},
        ],
        "libraries": [
            {"name": "FastAPI",          "version": "0.115+",   "purpose": "REST API framework"},
            {"name": "Uvicorn",          "version": "0.30+",    "purpose": "ASGI server"},
            {"name": "Pillow (PIL)",     "version": "10+",      "purpose": "Image processing and bounding-box annotation"},
            {"name": "NumPy",            "version": "1.26+",    "purpose": "Numerical computation for CV simulation"},
            {"name": "SQLite3",          "version": "built-in", "purpose": "Detection record storage"},
            {"name": "Leaflet.js",       "version": "1.9.x",    "purpose": "Interactive geospatial map"},
            {"name": "Chart.js",         "version": "4.x",      "purpose": "Data visualization and dashboards"},
            {"name": "python-multipart", "version": "latest",   "purpose": "Form data parsing for file uploads"},
        ],
        "academic_references": [
            "Mackenzie K.V. (1981) — Nine-term equation for sound speed in seawater. JASA 70(3)",
            "Thorp W.H. (1967) — Analytic description of the low-frequency attenuation coefficient. JASA 42",
            "Wenz G.M. (1962) — Acoustic ambient noise in the ocean. JASA 34(12)",
            "Urick R.J. (1983) — Principles of Underwater Sound, 3rd ed. McGraw-Hill",
            "NOAA Marine Debris Program — Plastic debris statistics and coastal hotspots",
        ],
        "datasets": [
            {
                "name":        "Synthetic demo detections",
                "description": (
                    "12 seeded records at real coastal coordinates: Tunis, Athens, Rome, Tokyo, Miami, "
                    "London, Singapore, Mexico City, Sydney, Hong Kong, Vietnam, Bali."
                ),
                "source": "Coordinates from public geographic reference data",
            }
        ],
        "prior_work": "Extends the Phase 1 concept submitted to IEEE AESS Sustainability Hackathon 2026, Challenge 3.",
        "note": (
            "The acoustic detection simulation uses physically-motivated equations (sonar equation, TL models, Knudsen noise) "
            "rather than recorded underwater data. CV detection uses edge-guided simulation instead of YOLOv8/PyTorch "
            "to avoid 400 MB+ CUDA package disk limits on the free hosting tier."
        ),
    })


@app.post("/sonar/ping")
async def sonar_ping(
    source_level: float = Form(200.0),
    frequency_kHz: float = Form(10.0),
    pulse_ms: float = Form(100.0),
    ping_interval_s: float = Form(5.0),
    mission_min: float = Form(60.0),
    sea_state: int = Form(3),
    depth_m: float = Form(50.0),
    seed: int = Form(42),
):
    """Run a full sonar scenario and return metrics for all three operating modes."""
    result = run_sonar_scenario(
        source_level=source_level,
        frequency_kHz=frequency_kHz,
        pulse_ms=pulse_ms,
        ping_interval_s=ping_interval_s,
        mission_min=mission_min,
        sea_state=sea_state,
        depth_m=depth_m,
        seed=seed,
    )
    return JSONResponse(result)


app.mount("/static", StaticFiles(directory="static"), name="static")
