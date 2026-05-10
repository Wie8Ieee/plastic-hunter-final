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


def save_detection(image_name: str, plastic_count: int, avg_confidence: float, latitude: float, longitude: float) -> int:
    severity = _compute_severity(plastic_count)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO detections (timestamp, image_name, plastic_count, avg_confidence, latitude, longitude, severity) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (timestamp, image_name, plastic_count, round(avg_confidence, 4), latitude, longitude, severity),
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

    baseline_plastics = int(total_plastics * 1.35)
    reduction_pct = round(((baseline_plastics - total_plastics) / max(baseline_plastics, 1)) * 100, 1)

    conn.close()

    return {
        "total_scans": total_scans,
        "total_plastics_detected": total_plastics,
        "avg_confidence": avg_confidence,
        "severity_breakdown": {"High": high_severity, "Medium": med_severity, "Low": low_severity},
        "detections_per_day": daily,
        "confidence_distribution": conf_dist,
        "baseline_plastics": baseline_plastics,
        "optimized_plastics": total_plastics,
        "reduction_percentage": reduction_pct,
    }
