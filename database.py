import sqlite3
from datetime import datetime, timedelta
from typing import Any, Dict, List

DB_PATH = "detections.db"


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS detections (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            image_name TEXT NOT NULL,
            plastic_count INTEGER NOT NULL,
            avg_confidence REAL NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            severity TEXT NOT NULL
        )
    """)
    conn.commit()

    for col, definition in [
        ("processing_time_ms",  "REAL DEFAULT 0.0"),
        ("sonar_mode",          "TEXT DEFAULT 'cv-only'"),
        ("energy_reduction_pct","REAL DEFAULT 0.0"),
        ("acoustic_exposure_dB","REAL DEFAULT 0.0"),
    ]:
        try:
            cursor.execute(f"ALTER TABLE detections ADD COLUMN {col} {definition}")
            conn.commit()
        except sqlite3.OperationalError:
            pass

    cursor.execute("CREATE INDEX IF NOT EXISTS idx_detections_timestamp ON detections(timestamp)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_detections_severity ON detections(severity)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_detections_location ON detections(latitude, longitude)")
    conn.commit()

    cursor.execute("SELECT COUNT(*) FROM detections")
    count = cursor.fetchone()[0]
    if count == 0:
        _seed_demo_data(cursor)
        conn.commit()

    conn.close()


def reset_and_reseed() -> int:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM detections")
    conn.commit()
    _seed_demo_data(cursor)
    conn.commit()
    cursor.execute("SELECT COUNT(*) FROM detections")
    count = cursor.fetchone()[0]
    conn.close()
    return count


def _seed_demo_data(cursor):
    demo_locations = [
        (36.8065, 10.1815, "demo_beach_tunisia.jpg", 7, 0.81),
        (37.9838, 23.7275, "demo_coast_greece.jpg", 3, 0.67),
        (41.9028, 12.4964, "demo_bay_italy.jpg", 11, 0.88),
        (35.6762, 139.6503, "demo_ocean_japan.jpg", 2, 0.55),
        (25.7617, -80.1918, "demo_beach_miami.jpg", 5, 0.74),
        (51.5074, -0.1278, "demo_thames_uk.jpg", 4, 0.70),
        (1.3521, 103.8198, "demo_coast_singapore.jpg", 9, 0.85),
        (19.4326, -99.1332, "demo_lake_mexico.jpg", 6, 0.77),
        (48.8566, 2.3522, "demo_seine_france.jpg", 1, 0.48),
        (55.7558, 37.6173, "demo_moscow_river.jpg", 8, 0.83),
        (40.7128, -74.0060, "demo_nyc_harbor.jpg", 13, 0.91),
        (34.0522, -118.2437, "demo_la_beach.jpg", 10, 0.86),
    ]

    base_date = datetime.now() - timedelta(days=11)
    base_dates = [
        (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        for i in range(12)
    ]

    for i, (lat, lon, img, count, conf) in enumerate(demo_locations):
        severity = _compute_severity(count)
        ts = f"{base_dates[i]} {10 + i % 8:02d}:00:00"
        cursor.execute(
            "INSERT INTO detections (timestamp, image_name, plastic_count, avg_confidence, latitude, longitude, severity) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (ts, img, count, conf, lat, lon, severity),
        )


def _compute_severity(count: int) -> str:
    if count <= 3:
        return "Low"
    elif count <= 8:
        return "Medium"
    else:
        return "High"


def save_detection(
    image_name: str,
    plastic_count: int,
    avg_confidence: float,
    latitude: float,
    longitude: float,
    processing_time_ms: float = 0.0,
    sonar_mode: str = "cv-only",
    energy_reduction_pct: float = 0.0,
    acoustic_exposure_dB: float = 0.0,
) -> int:
    severity = _compute_severity(plastic_count)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO detections
           (timestamp, image_name, plastic_count, avg_confidence, latitude, longitude, severity,
            processing_time_ms, sonar_mode, energy_reduction_pct, acoustic_exposure_dB)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (timestamp, image_name, plastic_count, round(avg_confidence, 4),
         latitude, longitude, severity,
         round(processing_time_ms, 1), sonar_mode,
         round(energy_reduction_pct, 2), round(acoustic_exposure_dB, 1)),
    )
    conn.commit()
    row_id = cursor.lastrowid
    conn.close()
    return row_id


def get_all_results() -> List[Dict[str, Any]]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM detections ORDER BY timestamp DESC")
    rows = [dict(r) for r in cursor.fetchall()]
    conn.close()
    return rows


def get_stats() -> Dict[str, Any]:
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*), SUM(plastic_count), AVG(avg_confidence) FROM detections")
    row = cursor.fetchone()
    total_scans = row[0] or 0
    total_plastics = row[1] or 0
    avg_confidence = round(row[2] or 0, 4)

    cursor.execute("""
        SELECT DATE(timestamp) as day, SUM(plastic_count) as daily_count
        FROM detections
        GROUP BY day
        ORDER BY day ASC
        LIMIT 30
    """)
    daily = [{"date": r[0], "count": r[1]} for r in cursor.fetchall()]

    cursor.execute("""
        SELECT
            CASE
                WHEN avg_confidence < 0.5 THEN 'Low (<50%)'
                WHEN avg_confidence < 0.75 THEN 'Medium (50-75%)'
                ELSE 'High (>75%)'
            END as band,
            COUNT(*) as cnt
        FROM detections
        GROUP BY band
    """)
    conf_dist = [{"label": r[0], "value": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT COUNT(*) FROM detections WHERE severity='High'")
    high_severity = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM detections WHERE severity='Medium'")
    med_severity = cursor.fetchone()[0] or 0
    cursor.execute("SELECT COUNT(*) FROM detections WHERE severity='Low'")
    low_severity = cursor.fetchone()[0] or 0

    cursor.execute("SELECT COUNT(DISTINCT printf('%.4f,%.4f', latitude, longitude)) FROM detections")
    active_sites = cursor.fetchone()[0] or 0

    cursor.execute("""
        SELECT image_name, plastic_count, avg_confidence, latitude, longitude, severity, timestamp
        FROM detections
        ORDER BY plastic_count DESC, avg_confidence DESC
        LIMIT 1
    """)
    hotspot_row = cursor.fetchone()
    top_hotspot = None
    if hotspot_row:
        top_hotspot = {
            "image_name": hotspot_row[0],
            "plastic_count": hotspot_row[1],
            "avg_confidence": round(hotspot_row[2] or 0, 4),
            "latitude": hotspot_row[3],
            "longitude": hotspot_row[4],
            "severity": hotspot_row[5],
            "timestamp": hotspot_row[6],
        }

    baseline_plastics = int(total_plastics * 1.35)
    reduction_pct = round(((baseline_plastics - total_plastics) / max(baseline_plastics, 1)) * 100, 1)
    baseline_method = (
        "Estimated manual-survey baseline using a transparent 1.35 multiplier for demo comparison; "
        "not a measured environmental impact result."
    )

    # Estimated type mix for seeded demo rows. Live detections return per-object labels,
    # but historical rows store only counts, so this chart is explicitly marked estimated.
    type_weights = [
        ("Plastic Bottle",      18),
        ("Plastic Bag",         14),
        ("Foam Packaging",      11),
        ("Bottle Cap",          12),
        ("Plastic Container",   10),
        ("Styrofoam Piece",      9),
        ("Plastic Wrapper",      8),
        ("Fishing Net Fragment",  8),
        ("Micro-Plastic Cluster", 6),
        ("Other",                4),
    ]
    total_w = sum(w for _, w in type_weights)
    plastic_type_distribution = [
        {"label": lbl, "count": max(1, round(total_plastics * w / total_w))}
        for lbl, w in type_weights
    ] if total_plastics > 0 else []
    if plastic_type_distribution:
        diff = total_plastics - sum(item["count"] for item in plastic_type_distribution)
        plastic_type_distribution[0]["count"] += diff

    # Processing time stats
    cursor.execute("SELECT AVG(processing_time_ms) FROM detections WHERE processing_time_ms > 0")
    avg_proc = round(cursor.fetchone()[0] or 0.0, 1)

    conn.close()

    return {
        "total_scans":              total_scans,
        "total_plastics_detected":  total_plastics,
        "active_sites":             active_sites,
        "top_hotspot":              top_hotspot,
        "avg_confidence":           avg_confidence,
        "avg_processing_time_ms":   avg_proc,
        "severity_breakdown":       {"High": high_severity, "Medium": med_severity, "Low": low_severity},
        "detections_per_day":       daily,
        "confidence_distribution":  conf_dist,
        "plastic_type_distribution": plastic_type_distribution,
        "plastic_type_distribution_method": "Estimated from demo class weights; not ground-truth class counts.",
        "baseline_plastics":        baseline_plastics,
        "optimized_plastics":       total_plastics,
        "reduction_percentage":     reduction_pct,
        "baseline_method":          baseline_method,
        "mission_summary": {
            "observed_scans": total_scans,
            "observed_plastic_items": total_plastics,
            "active_sites": active_sites,
            "high_severity_events": high_severity,
        },
    }
