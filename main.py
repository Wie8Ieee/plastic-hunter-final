import logging
import random
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from database import get_all_results, get_stats, init_db, reset_and_reseed, save_detection
from detector import run_detection
from sonar import run_sonar_scenario, trade_off_explanation

app = FastAPI(title="Plastic Hunter AI", version="1.0.0")
logger = logging.getLogger("plastic_hunter")

REPOSITORY_URL = "https://github.com/Wie8Ieee/plastic-hunter-final"
MAX_UPLOAD_BYTES = 20 * 1024 * 1024
CV_VALIDATION = {
    "dataset": "Trash-ICRA19",
    "models": ["YOLOv8s", "Faster R-CNN", "MobileNet SSD"],
    "best_model": "YOLOv8s",
    "map_50": "97.77%",
    "fps": "122.10",
    "cross_domain_test": "River Floating Trash Dataset",
    "best_cross_domain_model": "Faster R-CNN",
    "best_cross_domain_map_50": "32.22%",
}
EVIDENCE_LIMITATION = (
    "Limitation: The sonar component is currently simulation-based and requires hardware validation. "
    "The CV component is supported by real dataset experiments. The live demonstration uses a lightweight "
    "deployment configuration optimized for rapid execution while preserving the research-backed detection workflow."
)

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


@app.get("/healthz")
async def healthz():
    return JSONResponse({"status": "ok", "service": "plastic-hunter-ai"})


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
    if len(image_bytes) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Image exceeds the 20 MB upload limit.")

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
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            raise HTTPException(status_code=422, detail="Latitude must be -90..90 and longitude must be -180..180.")

    record_id = save_detection(
        image_name=result["annotated_image"],
        plastic_count=result["plastic_count"],
        avg_confidence=result["avg_confidence"],
        latitude=lat,
        longitude=lon,
        processing_time_ms=processing_time_ms,
    )
    logger.info("stored detection id=%s image=%s count=%s", record_id, result["annotated_image"], result["plastic_count"])

    response = {
        "id":                 record_id,
        "plastic_count":      result["plastic_count"],
        "avg_confidence":     result["avg_confidence"],
        "severity":           result["severity"],
        "detections":         result["detections"],
        "annotated_image":    f"/results/{result['annotated_image']}",
        "detection_mode":     result["detection_mode"],
        "processing_time_ms": processing_time_ms,
        "location":           {"latitude": lat, "longitude": lon},
    }
    for key in (
        "detector_mode",
        "warning",
        "quality_score",
        "false_positive_filters_applied",
        "model_path",
        "model_classes",
    ):
        if key in result:
            response[key] = result[key]

    return JSONResponse(response)


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
    if Path(filename).name != filename:
        raise HTTPException(status_code=400, detail="Invalid image filename.")
    path = (RESULTS_DIR / filename).resolve()
    results_root = RESULTS_DIR.resolve()
    if results_root not in path.parents and path != results_root:
        raise HTTPException(status_code=400, detail="Invalid image path.")
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
            "Eco-adaptive sonar compares conventional, passive, and reduced-duty active modes in a reproducible "
            "simulation. CV-based surface detection is presented through a lightweight demo interface backed by "
            "separate real-dataset research validation."
        ),
        "baseline": {
            "description": "Conventional active sonar: fixed 200 dB SL, continuous pinging at 5 s interval (2% duty cycle).",
            "cumulative_sel_dB":    c["sel_cum_dB"],
            "duty_cycle_pct":       c["duty_cycle_pct"],
            "n_pings_per_mission":  c["n_pings"],
            "max_range_m":          c["max_range_m"],
        },
        "improved_case": {
            "description": "Eco-adaptive sonar: 188 dB SL (-12 dB), 15 s ping interval (0.67% duty cycle).",
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
        "technical_kpi": (
            "Technical KPI: YOLOv8s achieved 97.77% mAP@0.5 and 122.10 FPS on Trash-ICRA19 "
            "in our research evaluation."
        ),
        "cv_validation": CV_VALIDATION,
        "primary_sustainability_kpi": {
            "metric":                      "Cumulative Sound Exposure Level reduction",
            "sel_reduction_dB":            m["sel_reduction_dB"],
            "sel_reduction_pct":           m["sel_reduction_pct"],
            "duty_cycle_reduction_pct":    m["duty_cycle_reduction_pct"],
            "energy_reduction_pct":        m.get("energy_reduction_pct", 0.0),
        },
        "trade_off_explanation": trade_off_explanation(m),
        "limitation": EVIDENCE_LIMITATION,
        "assumptions": sonar.get("assumptions", []),
        "reproducibility": {
            "default_seed": sonar.get("validation_notes", {}).get("reproducible_seed", 42),
            "reference_target": sonar.get("validation_notes", {}).get("reference_target"),
            "threshold": sonar.get("validation_notes", {}).get("threshold"),
            "stats_source": "SQLite detections table seeded by database.py or updated by POST /detect",
        },
        "estimated_dashboard_method": stats.get("baseline_method"),
        "repository_link":  REPOSITORY_URL,
        "cv_stats": {
            "total_scans":        stats["total_scans"],
            "plastics_detected":  stats["total_plastics_detected"],
        },
        "generated_at": datetime.utcnow().isoformat() + "Z",
    })


@app.get("/disclosure")
async def disclosure():
    return JSONResponse({
        "ai_methods": [
            {
                "name": "Research-backed computer vision validation",
                "use": "YOLOv8s, Faster R-CNN, and MobileNet SSD were evaluated on marine debris datasets; the live interface remains lightweight for deployment.",
            },
            {
                "name": "Eco-sonar simulation",
                "use": "Physics-based sonar calculations estimate SNR, detection probability, duty cycle, and sound exposure trade-offs.",
            },
        ],
        "libraries": [
            {"name": "FastAPI",          "version": "0.115+",   "purpose": "REST API framework"},
            {"name": "Uvicorn",          "version": "0.30+",    "purpose": "ASGI server"},
            {"name": "Pillow (PIL)",     "version": "10+",      "purpose": "Image processing and bounding-box annotation"},
            {"name": "NumPy",            "version": "1.26+",    "purpose": "Numerical computation for the lightweight CV demo interface"},
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
                "name": "Trash-ICRA19",
                "description": "Research dataset used to train and evaluate YOLOv8s, Faster R-CNN, and MobileNet SSD.",
                "source": "Team research evaluation",
            },
            {
                "name": "River Floating Trash Dataset",
                "description": "Cross-domain dataset used to test generalization beyond Trash-ICRA19.",
                "source": "Team research evaluation",
            },
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
            "rather than recorded underwater data. The CV component is research-backed using real marine debris datasets, "
            "while the live demonstration uses a lightweight deployment configuration optimized for rapid execution while "
            "preserving the research-backed detection workflow."
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
