import os
import random
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

from database import get_all_results, get_stats, init_db, save_detection
from detector import run_detection

app = FastAPI(title="Plastic Hunter AI", version="1.0.0")

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
        result = run_detection(image_bytes, file.filename or "upload.jpg")
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
    )

    return JSONResponse({
        "id": record_id,
        "plastic_count": result["plastic_count"],
        "avg_confidence": result["avg_confidence"],
        "severity": result["severity"],
        "detections": result["detections"],
        "annotated_image": f"/results/{result['annotated_image']}",
        "detection_mode": result["detection_mode"],
        "location": {"latitude": lat, "longitude": lon},
    })


@app.get("/results")
async def get_results():
    rows = get_all_results()
    return JSONResponse(rows)


@app.get("/stats")
async def stats():
    data = get_stats()
    return JSONResponse(data)


@app.get("/results/{filename}")
async def get_result_image(filename: str):
    path = RESULTS_DIR / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="Image not found.")
    return FileResponse(str(path), media_type="image/jpeg")


app.mount("/", StaticFiles(directory="static", html=True), name="static")
