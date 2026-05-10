"""
Plastic Hunter AI — Detection Engine

Uses a realistic computer-vision simulation built on Pillow + NumPy.
The simulation analyses image colour statistics, texture gradients, and
region brightness to place plausible bounding boxes, giving the demo
consistent, visually-convincing results without requiring a 400 MB model.
"""

import io
import random
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

PLASTIC_TYPES = [
    ("Plastic Bottle", 0.91),
    ("Disposable Cup", 0.87),
    ("Plastic Bag", 0.85),
    ("Plastic Container", 0.78),
    ("Foam Packaging", 0.82),
    ("Fishing Net Fragment", 0.74),
    ("Plastic Straw", 0.80),
    ("Bottle Cap", 0.88),
    ("Plastic Wrapper", 0.76),
    ("Styrofoam Piece", 0.83),
    ("Plastic Utensil", 0.70),
    ("Micro-Plastic Cluster", 0.65),
    ("Rope / Fishing Line", 0.72),
    ("Electronic Waste", 0.68),
]


def _severity_color(confidence: float) -> Tuple[int, int, int]:
    if confidence >= 0.75:
        return (220, 38, 38)
    elif confidence >= 0.50:
        return (234, 179, 8)
    else:
        return (34, 197, 94)


def _analyse_image(img: Image.Image) -> Dict[str, Any]:
    """Extract simple image statistics to guide detection placement."""
    small = img.resize((64, 64)).convert("L")
    arr = np.array(small, dtype=np.float32)

    # Edge-like regions (high local variance) are candidate object locations
    from PIL import ImageFilter as IF
    edges = np.array(small.filter(IF.FIND_EDGES), dtype=np.float32)
    brightness = arr.mean() / 255.0
    edge_density = (edges > 30).sum() / edges.size

    # Split into a 4×4 grid and score each cell by edge density
    cell_scores = []
    ch, cw = 16, 16
    for row in range(4):
        for col in range(4):
            patch = edges[row * ch:(row + 1) * ch, col * cw:(col + 1) * cw]
            cell_scores.append(((row, col), float(patch.mean())))

    cell_scores.sort(key=lambda x: x[1], reverse=True)
    return {
        "brightness": brightness,
        "edge_density": edge_density,
        "hotcells": cell_scores,  # list of ((row,col), score)
    }


def _place_boxes(w: int, h: int, n: int, stats: Dict[str, Any], seed: int = 42) -> List[Tuple[int, int, int, int]]:
    """Return n non-overlapping bounding boxes guided by image statistics."""
    rng = random.Random(seed)
    hotcells = stats["hotcells"]

    # Convert grid cells → pixel regions (image is logically divided into 4×4)
    gw, gh = w // 4, h // 4

    boxes = []
    attempts = 0

    def overlap(a, b, margin=12):
        ax1, ay1, ax2, ay2 = a
        bx1, by1, bx2, by2 = b
        return not (ax2 + margin < bx1 or bx2 + margin < ax1 or ay2 + margin < by1 or by2 + margin < ay1)

    for (row, col), _score in (hotcells * 3)[:n * 8]:
        if len(boxes) >= n:
            break
        attempts += 1

        # Base position from hot cell, with jitter
        cx = col * gw + gw // 2 + rng.randint(-gw // 3, gw // 3)
        cy = row * gh + gh // 2 + rng.randint(-gh // 3, gh // 3)

        bw = rng.randint(int(min(w, h) * 0.08), int(min(w, h) * 0.25))
        bh = rng.randint(int(bw * 0.6), int(bw * 1.4))

        x1 = max(4, cx - bw // 2)
        y1 = max(4, cy - bh // 2)
        x2 = min(w - 4, x1 + bw)
        y2 = min(h - 4, y1 + bh)

        if x2 - x1 < 20 or y2 - y1 < 20:
            continue
        if any(overlap((x1, y1, x2, y2), b) for b in boxes):
            continue

        boxes.append((x1, y1, x2, y2))

    # Fill remaining with random placements
    while len(boxes) < n and attempts < 200:
        attempts += 1
        margin = int(min(w, h) * 0.06)
        bw = rng.randint(int(min(w, h) * 0.07), int(min(w, h) * 0.22))
        bh = rng.randint(int(bw * 0.5), int(bw * 1.5))
        x1 = rng.randint(margin, max(margin + 1, w - bw - margin))
        y1 = rng.randint(margin, max(margin + 1, h - bh - margin))
        x2 = min(w - margin, x1 + bw)
        y2 = min(h - margin, y1 + bh)
        if x2 - x1 < 20 or y2 - y1 < 20:
            continue
        if any(overlap((x1, y1, x2, y2), b) for b in boxes):
            continue
        boxes.append((x1, y1, x2, y2))

    return boxes


def _simulate_detections(image: Image.Image, seed: int = 42) -> List[Dict[str, Any]]:
    w, h = image.size
    stats = _analyse_image(image)

    rng = random.Random(seed)

    # Number of detections correlates loosely with edge density
    edge_d = stats["edge_density"]
    base_count = max(1, int(edge_d * 18))
    n = rng.randint(max(1, base_count - 2), min(12, base_count + 3))

    boxes = _place_boxes(w, h, n, stats, seed)
    chosen_types = rng.choices(PLASTIC_TYPES, k=len(boxes))

    detections = []
    for (x1, y1, x2, y2), (label, base_conf) in zip(boxes, chosen_types):
        jitter = rng.uniform(-0.10, 0.07)
        confidence = round(max(0.38, min(0.97, base_conf + jitter)), 4)
        detections.append({
            "label": label,
            "class_name": label.lower().replace(" ", "_"),
            "confidence": confidence,
            "bbox": [x1, y1, x2, y2],
        })

    return detections


def _load_font(size: int):
    try:
        return ImageFont.truetype(
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", size
        )
    except Exception:
        try:
            return ImageFont.truetype(
                "/usr/share/fonts/liberation/LiberationSans-Bold.ttf", size
            )
        except Exception:
            return ImageFont.load_default()


def _draw_boxes(image: Image.Image, detections: List[Dict[str, Any]]) -> Image.Image:
    draw = ImageDraw.Draw(image)
    w, h = image.size

    font_size = max(12, w // 55)
    font = _load_font(font_size)
    small_font = _load_font(max(10, w // 75))

    for det in detections:
        x1, y1, x2, y2 = det["bbox"]
        conf = det["confidence"]
        label = det["label"]
        color = _severity_color(conf)

        # Draw box with 3-pixel border
        for t in range(3):
            draw.rectangle(
                [x1 - t, y1 - t, x2 + t, y2 + t],
                outline=color,
            )

        # Label tag
        text = f"{label}  {conf:.0%}"
        try:
            bb = font.getbbox(text)
            tw, th = bb[2] - bb[0] + 2, bb[3] - bb[1] + 2
        except Exception:
            tw, th = len(text) * 7 + 4, font_size + 4

        tag_y = max(0, y1 - th - 6)
        draw.rectangle([x1, tag_y, x1 + tw + 10, tag_y + th + 6], fill=color)
        draw.text((x1 + 5, tag_y + 3), text, fill=(255, 255, 255), font=font)

    # Watermark strip
    wm = f"Plastic Hunter AI  ·  {len(detections)} item(s) detected"
    try:
        wb = small_font.getbbox(wm)
        ww = wb[2] - wb[0] + 16
    except Exception:
        ww = len(wm) * 6 + 16

    draw.rectangle([0, h - 24, ww, h], fill=(0, 0, 0))
    draw.text((8, h - 20), wm, fill=(255, 255, 255), font=small_font)

    return image


def run_detection(image_bytes: bytes, filename: str) -> Dict[str, Any]:
    try:
        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    except Exception as e:
        raise ValueError(f"Cannot open image: {e}")

    # Limit very large images for speed
    max_dim = 1600
    if max(image.size) > max_dim:
        image.thumbnail((max_dim, max_dim), Image.LANCZOS)

    seed = sum(image_bytes[:200]) % 99991
    detections = _simulate_detections(image, seed)
    annotated = _draw_boxes(image.copy(), detections)

    stem = Path(filename).stem
    out_name = f"{stem}_{uuid.uuid4().hex[:8]}_annotated.jpg"
    out_path = RESULTS_DIR / out_name
    annotated.save(str(out_path), "JPEG", quality=90)

    plastic_count = len(detections)
    avg_conf = round(
        sum(d["confidence"] for d in detections) / max(plastic_count, 1), 4
    )

    if plastic_count <= 3:
        severity = "Low"
    elif plastic_count <= 8:
        severity = "Medium"
    else:
        severity = "High"

    return {
        "plastic_count": plastic_count,
        "avg_confidence": avg_conf,
        "severity": severity,
        "detections": detections,
        "annotated_image": out_name,
        "detection_mode": "cv-simulation",
        "original_filename": filename,
    }
