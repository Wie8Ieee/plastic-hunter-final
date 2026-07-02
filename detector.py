"""
Plastic Hunter AI - Detection Engine

Uses a lightweight deployable computer-vision demo interface built on
Pillow + NumPy. The live interface analyses image colour statistics,
texture gradients, and connected foreground regions to place conservative
bounding boxes, while the research-backed CV validation is based on real
marine debris dataset experiments documented in the evidence sheet.
"""

import io
import os
import time
import uuid
from collections import deque
from pathlib import Path
from typing import Any, Dict, List, Tuple

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont, ImageOps

RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)
MODEL_PATH = Path("models") / "best.pt"
COCO_ASSIST_MODEL_PATH = Path(os.getenv("PLASTIC_COCO_ASSIST_MODEL", "yolov8s.pt"))

LOW_CONFIDENCE_WARNING = (
    "Low-confidence scene: objects may be too small, dark, or visually ambiguous."
)
YOLO_FALLBACK_WARNING = "YOLO inference failed; falling back to lightweight detector."
YOLO_WEIGHTS_MISSING_WARNING = (
    "YOLO weights not found. Running lightweight demo detector."
)
COCO_ASSIST_WARNING = (
    "Custom plastic YOLO found no plastic; COCO YOLO assist mapped generic bottle/cup detections."
)
LIGHTWEIGHT_ASSIST_WARNING = (
    "YOLO found no plastic; using lightweight demo detector as a conservative fallback."
)
MIN_CONFIDENCE = float(os.getenv("PLASTIC_MIN_CONFIDENCE", "0.55"))
MAX_DETECTIONS = int(os.getenv("PLASTIC_MAX_DETECTIONS", "5"))
NMS_IOU_THRESHOLD = float(os.getenv("PLASTIC_NMS_IOU", "0.35"))
YOLO_CONFIDENCE = float(os.getenv("PLASTIC_YOLO_CONFIDENCE", "0.20"))
YOLO_IOU_THRESHOLD = float(os.getenv("PLASTIC_YOLO_IOU", "0.45"))
YOLO_IMAGE_SIZE = int(os.getenv("PLASTIC_YOLO_IMGSZ", "640"))
YOLO_MAX_DETECTIONS = int(os.getenv("PLASTIC_YOLO_MAX_DET", "20"))
PROCESS_MAX_DIM = 720
PLASTIC_CLASS_KEYWORDS = (
    "plastic",
    "debris",
    "trash",
    "litter",
    "bottle",
    "bag",
    "net",
    "rope",
    "foam",
    "cap",
    "wrapper",
)
_YOLO_MODEL = None
_YOLO_LOAD_WARNING = None
_COCO_ASSIST_MODEL = None
_COCO_ASSIST_LOAD_WARNING = None


def _load_yolo_model():
    if not MODEL_PATH.exists():
        return None, None

    try:
        from ultralytics import YOLO
    except Exception as exc:
        return None, f"YOLO weights found but ultralytics is not available: {exc}"

    try:
        return YOLO(str(MODEL_PATH)), None
    except Exception as exc:
        return None, f"YOLO weights found but model could not be loaded: {exc}"


_YOLO_MODEL, _YOLO_LOAD_WARNING = _load_yolo_model()


def _load_coco_assist_model():
    global _COCO_ASSIST_MODEL, _COCO_ASSIST_LOAD_WARNING
    if _COCO_ASSIST_MODEL is not None or _COCO_ASSIST_LOAD_WARNING is not None:
        return _COCO_ASSIST_MODEL

    try:
        from ultralytics import YOLO
        _COCO_ASSIST_MODEL = YOLO(str(COCO_ASSIST_MODEL_PATH))
    except Exception as exc:
        _COCO_ASSIST_LOAD_WARNING = f"COCO YOLO assist unavailable: {exc}"
        _COCO_ASSIST_MODEL = None
    return _COCO_ASSIST_MODEL


def _severity_color(confidence: float) -> Tuple[int, int, int]:
    if confidence >= 0.75:
        return (220, 38, 38)
    if confidence >= 0.50:
        return (234, 179, 8)
    return (34, 197, 94)


def _resize_for_processing(image: Image.Image) -> Tuple[Image.Image, float, float]:
    w, h = image.size
    scale = min(1.0, PROCESS_MAX_DIM / max(w, h))
    if scale < 1.0:
        nw, nh = max(1, int(w * scale)), max(1, int(h * scale))
        return image.resize((nw, nh), Image.LANCZOS), w / nw, h / nh
    return image.copy(), 1.0, 1.0


def _preprocess(image: Image.Image) -> Dict[str, np.ndarray]:
    raw_gray = np.asarray(image.convert("L"), dtype=np.float32) / 255.0
    normalized = ImageOps.autocontrast(image, cutoff=1)
    denoised = normalized.filter(ImageFilter.MedianFilter(size=3))
    rgb = np.asarray(denoised, dtype=np.float32) / 255.0

    gray_img = denoised.convert("L").filter(ImageFilter.GaussianBlur(radius=0.6))
    gray = np.asarray(gray_img, dtype=np.float32) / 255.0
    blur = np.asarray(
        gray_img.filter(ImageFilter.GaussianBlur(radius=3.0)), dtype=np.float32
    ) / 255.0

    gy, gx = np.gradient(gray)
    edges = np.sqrt(gx * gx + gy * gy)
    contrast = np.abs(gray - blur)

    mx = rgb.max(axis=2)
    mn = rgb.min(axis=2)
    saturation = np.divide(mx - mn, mx + 1e-6)

    return {
        "rgb": rgb,
        "raw_gray": raw_gray,
        "gray": gray,
        "edges": edges,
        "contrast": contrast,
        "saturation": saturation,
        "brightness": mx,
    }


def _quality_score(features: Dict[str, np.ndarray], image: Image.Image) -> float:
    gray = features["raw_gray"]
    w, h = image.size
    exposure = 1.0 - min(1.0, abs(float(gray.mean()) - 0.52) / 0.42)
    contrast = min(1.0, float(gray.std()) / 0.22)
    gy, gx = np.gradient(gray)
    raw_edges = np.sqrt(gx * gx + gy * gy)
    edge_strength = min(1.0, float(np.percentile(raw_edges, 92)) / 0.12)
    size_score = min(1.0, (w * h) / (480 * 360))
    score = 0.30 * exposure + 0.30 * contrast + 0.25 * edge_strength + 0.15 * size_score
    return round(float(score), 4)


def _foreground_mask(features: Dict[str, np.ndarray]) -> np.ndarray:
    h, w = features["gray"].shape
    y = np.linspace(0.0, 1.0, h, dtype=np.float32)[:, None]
    rgb = features["rgb"]

    blue_bias = rgb[:, :, 2] - np.maximum(rgb[:, :, 0], rgb[:, :, 1])
    low_texture = features["edges"] < np.percentile(features["edges"], 58)
    horizon_like = (y < 0.45) & (blue_bias > 0.05) & low_texture

    foreground = np.repeat(y >= 0.30, w, axis=1)
    foreground[horizon_like] = False
    foreground[: max(2, int(h * 0.18)), :] = False
    return foreground


def _majority_filter(mask: np.ndarray) -> np.ndarray:
    padded = np.pad(mask.astype(np.uint8), 1, mode="constant")
    count = np.zeros(mask.shape, dtype=np.uint8)
    for dy in range(3):
        for dx in range(3):
            count += padded[dy:dy + mask.shape[0], dx:dx + mask.shape[1]]
    return mask & (count >= 3)


def _candidate_mask(features: Dict[str, np.ndarray]) -> np.ndarray:
    edges = features["edges"]
    contrast = features["contrast"]
    sat = features["saturation"]
    bright = features["brightness"]
    gray = features["gray"]
    foreground = _foreground_mask(features)

    if np.any(foreground):
        edge_thr = max(0.035, float(np.percentile(edges[foreground], 74)))
        contrast_thr = max(0.045, float(np.percentile(contrast[foreground], 70)))
    else:
        edge_thr = 0.05
        contrast_thr = 0.06

    textured = (edges > edge_thr) & (contrast > contrast_thr)
    bright_plastic = (bright > 0.60) & (contrast > 0.025) & (edges > edge_thr * 0.55)
    white_reflective = (gray > 0.55) & (sat < 0.38) & (contrast > 0.025)
    colored_plastic = (sat > 0.22) & (bright > 0.34) & (edges > edge_thr * 0.55)
    candidates = foreground & (textured | bright_plastic | white_reflective | colored_plastic)
    return _majority_filter(candidates)


def _connected_components(mask: np.ndarray) -> List[Tuple[int, int, int, int, int]]:
    h, w = mask.shape
    seen = np.zeros(mask.shape, dtype=bool)
    components: List[Tuple[int, int, int, int, int]] = []
    ys, xs = np.where(mask)

    for sy, sx in zip(ys.tolist(), xs.tolist()):
        if seen[sy, sx]:
            continue

        q = deque([(sx, sy)])
        seen[sy, sx] = True
        x1 = x2 = sx
        y1 = y2 = sy
        area = 0

        while q:
            x, y = q.popleft()
            area += 1
            x1, x2 = min(x1, x), max(x2, x)
            y1, y2 = min(y1, y), max(y2, y)

            for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                if 0 <= nx < w and 0 <= ny < h and mask[ny, nx] and not seen[ny, nx]:
                    seen[ny, nx] = True
                    q.append((nx, ny))

        components.append((x1, y1, x2 + 1, y2 + 1, area))

    return components


def _merge_boxes(boxes: List[Tuple[int, int, int, int]], max_gap: int) -> List[Tuple[int, int, int, int]]:
    merged = boxes[:]
    changed = True

    while changed:
        changed = False
        used = [False] * len(merged)
        out: List[Tuple[int, int, int, int]] = []

        for i, box in enumerate(merged):
            if used[i]:
                continue
            ax1, ay1, ax2, ay2 = box
            used[i] = True

            for j in range(i + 1, len(merged)):
                if used[j]:
                    continue
                bx1, by1, bx2, by2 = merged[j]
                near = not (
                    ax2 + max_gap < bx1
                    or bx2 + max_gap < ax1
                    or ay2 + max_gap < by1
                    or by2 + max_gap < ay1
                )
                if near:
                    ax1, ay1 = min(ax1, bx1), min(ay1, by1)
                    ax2, ay2 = max(ax2, bx2), max(ay2, by2)
                    used[j] = True
                    changed = True

            out.append((ax1, ay1, ax2, ay2))

        merged = out

    return merged


def _tighten_box(box: Tuple[int, int, int, int], mask: np.ndarray, pad: int) -> Tuple[int, int, int, int]:
    h, w = mask.shape
    x1, y1, x2, y2 = box
    crop = mask[y1:y2, x1:x2]
    ys, xs = np.where(crop)
    if len(xs) == 0:
        return box
    return (
        max(0, x1 + int(xs.min()) - pad),
        max(0, y1 + int(ys.min()) - pad),
        min(w, x1 + int(xs.max()) + 1 + pad),
        min(h, y1 + int(ys.max()) + 1 + pad),
    )


def _box_iou(a: Tuple[int, int, int, int], b: Tuple[int, int, int, int]) -> float:
    ax1, ay1, ax2, ay2 = a
    bx1, by1, bx2, by2 = b
    ix1, iy1 = max(ax1, bx1), max(ay1, by1)
    ix2, iy2 = min(ax2, bx2), min(ay2, by2)
    iw, ih = max(0, ix2 - ix1), max(0, iy2 - iy1)
    inter = iw * ih
    area_a = max(0, ax2 - ax1) * max(0, ay2 - ay1)
    area_b = max(0, bx2 - bx1) * max(0, by2 - by1)
    return inter / max(1.0, area_a + area_b - inter)


def _score_box(box: Tuple[int, int, int, int], features: Dict[str, np.ndarray], mask: np.ndarray) -> Tuple[float, str]:
    h, w = features["gray"].shape
    x1, y1, x2, y2 = box
    bw, bh = x2 - x1, y2 - y1
    area_ratio = (bw * bh) / float(w * h)
    aspect = bw / max(1, bh)

    region_edges = features["edges"][y1:y2, x1:x2]
    region_contrast = features["contrast"][y1:y2, x1:x2]
    region_sat = features["saturation"][y1:y2, x1:x2]
    region_bright = features["brightness"][y1:y2, x1:x2]
    region_gray = features["gray"][y1:y2, x1:x2]
    region_mask = mask[y1:y2, x1:x2]

    edge_density = float((region_edges > max(0.035, np.percentile(features["edges"], 72))).mean())
    local_contrast = min(1.0, float(region_contrast.mean()) / 0.12 + float(region_gray.std()) / 0.25)
    color_cue = min(1.0, float(((region_sat > 0.22) & (region_bright > 0.34)).mean()) * 2.2)
    reflection = min(1.0, float(((region_bright > 0.65) & (region_sat < 0.40)).mean()) * 2.4)
    texture = min(1.0, float(region_edges.std()) / 0.08 + float(region_mask.mean()) * 0.5)
    size_score = float(np.interp(area_ratio, [0.00045, 0.004, 0.045, 0.24], [0.0, 1.0, 0.85, 0.0]))
    location_score = float(np.interp(((y1 + y2) / 2) / h, [0.22, 0.45, 0.90, 1.0], [0.0, 0.85, 1.0, 0.65]))
    aspect_score = float(np.interp(aspect, [0.12, 0.25, 1.0, 4.5, 8.0], [0.0, 0.65, 1.0, 0.75, 0.0]))

    raw = (
        0.19 * edge_density
        + 0.17 * local_contrast
        + 0.16 * max(color_cue, reflection)
        + 0.15 * texture
        + 0.15 * size_score
        + 0.11 * location_score
        + 0.07 * aspect_score
    )
    confidence = round(float(np.clip(0.30 + raw * 0.62, 0.0, 0.94)), 4)

    if (aspect > 3.0 and color_cue > reflection) or (area_ratio > 0.08 and aspect > 1.5):
        label = "Rope / Fishing Line"
    elif reflection > 0.45 and aspect < 2.5:
        label = "Plastic Bottle"
    elif aspect > 1.8:
        label = "Plastic Wrapper"
    elif color_cue > 0.45:
        label = "Plastic Container"
    else:
        label = "Plastic Debris"

    return confidence, label


def _detect_lightweight(image: Image.Image) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    proc, sx, sy = _resize_for_processing(image)
    features = _preprocess(proc)
    quality = _quality_score(features, proc)
    if quality < 0.38:
        return [], {
            "quality_score": quality,
            "warning": LOW_CONFIDENCE_WARNING,
            "false_positive_filters_applied": {
                "tiny_components_removed": 0,
                "oversized_regions_removed": 0,
                "aspect_ratio_removed": 0,
                "low_confidence_removed": 0,
                "nms_duplicates_removed": 0,
                "horizon_foreground_mask": True,
                "quality_gate_applied": True,
                "min_confidence": MIN_CONFIDENCE,
                "max_detections": MAX_DETECTIONS,
                "nms_iou_threshold": NMS_IOU_THRESHOLD,
            },
        }
    mask = _candidate_mask(features)
    h, w = mask.shape

    min_area = max(18, int(w * h * 0.00035))
    max_area = int(w * h * 0.115)
    filters = {
        "tiny_components_removed": 0,
        "oversized_regions_removed": 0,
        "aspect_ratio_removed": 0,
        "low_confidence_removed": 0,
        "nms_duplicates_removed": 0,
        "horizon_foreground_mask": True,
        "min_confidence": MIN_CONFIDENCE,
        "max_detections": MAX_DETECTIONS,
        "nms_iou_threshold": NMS_IOU_THRESHOLD,
    }

    boxes: List[Tuple[int, int, int, int]] = []
    for x1, y1, x2, y2, area in _connected_components(mask):
        bw, bh = x2 - x1, y2 - y1
        if area < min_area or bw < 8 or bh < 8:
            filters["tiny_components_removed"] += 1
            continue
        if area > max_area or bw * bh > max_area * 2:
            filters["oversized_regions_removed"] += 1
            continue
        aspect = bw / max(1, bh)
        if aspect < 0.12 or aspect > 8.0:
            filters["aspect_ratio_removed"] += 1
            continue
        boxes.append((x1, y1, x2, y2))

    boxes = _merge_boxes(boxes, max(4, int(min(w, h) * 0.018)))
    candidates = []
    pad = max(2, int(min(w, h) * 0.004))

    for box in boxes:
        tight = _tighten_box(box, mask, pad=pad)
        x1, y1, x2, y2 = tight
        bw, bh = x2 - x1, y2 - y1
        area_ratio = (bw * bh) / float(w * h)
        aspect = bw / max(1, bh)

        if bw < 10 or bh < 10 or area_ratio < 0.00045:
            filters["tiny_components_removed"] += 1
            continue
        if area_ratio > 0.22 or y1 < int(h * 0.18):
            filters["oversized_regions_removed"] += 1
            continue
        if aspect < 0.12 or aspect > 8.0:
            filters["aspect_ratio_removed"] += 1
            continue

        confidence, label = _score_box(tight, features, mask)
        if confidence < MIN_CONFIDENCE:
            filters["low_confidence_removed"] += 1
            continue
        candidates.append((confidence, label, tight))

    candidates.sort(key=lambda item: item[0], reverse=True)
    kept = []
    for candidate in candidates:
        if any(_box_iou(candidate[2], existing[2]) > NMS_IOU_THRESHOLD for existing in kept):
            filters["nms_duplicates_removed"] += 1
            continue
        kept.append(candidate)
        if len(kept) >= MAX_DETECTIONS:
            break

    detections = []
    for confidence, label, (x1, y1, x2, y2) in kept:
        ox1 = max(0, int(round(x1 * sx)))
        oy1 = max(0, int(round(y1 * sy)))
        ox2 = min(image.size[0], int(round(x2 * sx)))
        oy2 = min(image.size[1], int(round(y2 * sy)))
        detections.append({
            "label": label,
            "class_name": label.lower().replace(" / ", "_").replace(" ", "_"),
            "confidence": confidence,
            "bbox": [ox1, oy1, ox2, oy2],
        })

    warning = LOW_CONFIDENCE_WARNING if quality < 0.38 or not detections else None
    return detections, {
        "quality_score": quality,
        "warning": warning,
        "false_positive_filters_applied": filters,
    }


def _detect_yolo(image: Image.Image) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if _YOLO_MODEL is None:
        raise RuntimeError(_YOLO_LOAD_WARNING or "YOLO model is not available.")

    model_names = getattr(_YOLO_MODEL, "names", {}) or {}
    results = _YOLO_MODEL.predict(
        source=np.asarray(image),
        conf=YOLO_CONFIDENCE,
        iou=YOLO_IOU_THRESHOLD,
        imgsz=YOLO_IMAGE_SIZE,
        max_det=YOLO_MAX_DETECTIONS,
        verbose=False,
    )
    if not results:
        return [], {
            "quality_score": None,
            "warning": LOW_CONFIDENCE_WARNING,
            "false_positive_filters_applied": {
                "model_confidence_threshold": YOLO_CONFIDENCE,
                "max_detections": YOLO_MAX_DETECTIONS,
                "nms_iou_threshold": YOLO_IOU_THRESHOLD,
                "imgsz": YOLO_IMAGE_SIZE,
            },
            "model_path": str(MODEL_PATH),
            "model_classes": dict(model_names) if isinstance(model_names, dict) else {},
        }

    result = results[0]
    names = getattr(result, "names", {}) or model_names
    boxes = getattr(result, "boxes", None)
    detections: List[Dict[str, Any]] = []
    if boxes is None:
        return detections, {
            "quality_score": None,
            "warning": LOW_CONFIDENCE_WARNING,
            "false_positive_filters_applied": {
                "model_confidence_threshold": YOLO_CONFIDENCE,
                "max_detections": YOLO_MAX_DETECTIONS,
                "nms_iou_threshold": YOLO_IOU_THRESHOLD,
                "imgsz": YOLO_IMAGE_SIZE,
            },
            "model_path": str(MODEL_PATH),
            "model_classes": dict(names) if isinstance(names, dict) else {},
        }

    xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, "cpu") else np.asarray(boxes.xyxy)
    confs = boxes.conf.cpu().numpy() if hasattr(boxes.conf, "cpu") else np.asarray(boxes.conf)
    classes = boxes.cls.cpu().numpy() if hasattr(boxes.cls, "cpu") else np.asarray(boxes.cls)
    w, h = image.size
    non_plastic_filtered = 0

    for coords, conf, cls_id in zip(xyxy, confs, classes):
        confidence = round(float(conf), 4)
        if confidence < YOLO_CONFIDENCE:
            continue

        x1, y1, x2, y2 = [int(round(float(v))) for v in coords[:4]]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            continue

        class_id = int(cls_id)
        label = str(names.get(class_id, f"class_{class_id}")) if isinstance(names, dict) else f"class_{class_id}"
        if not any(keyword in label.lower() for keyword in PLASTIC_CLASS_KEYWORDS):
            non_plastic_filtered += 1
            continue
        detections.append({
            "label": label,
            "class_name": label.lower().replace(" / ", "_").replace(" ", "_"),
            "confidence": confidence,
            "bbox": [x1, y1, x2, y2],
        })

    detections.sort(key=lambda det: det["confidence"], reverse=True)
    detections = detections[:YOLO_MAX_DETECTIONS]
    assist_warning = None
    assist_metadata = {}
    if not detections:
        detections, assist_metadata = _detect_coco_assist(image)
        if detections:
            assist_warning = COCO_ASSIST_WARNING

    return detections, {
        "quality_score": None,
        "warning": assist_warning if detections else LOW_CONFIDENCE_WARNING,
        "false_positive_filters_applied": {
            "model_confidence_threshold": YOLO_CONFIDENCE,
            "max_detections": YOLO_MAX_DETECTIONS,
            "nms_iou_threshold": YOLO_IOU_THRESHOLD,
            "imgsz": YOLO_IMAGE_SIZE,
            "non_plastic_classes_filtered": non_plastic_filtered,
            **assist_metadata.get("false_positive_filters_applied", {}),
        },
        "model_path": (
            f"{MODEL_PATH}; {assist_metadata.get('model_path')}"
            if assist_metadata.get("model_path") and detections and assist_warning
            else str(MODEL_PATH)
        ),
        "model_classes": (
            {"custom": dict(names), "assist": assist_metadata.get("model_classes", {})}
            if assist_metadata.get("model_classes") and detections and assist_warning and isinstance(names, dict)
            else dict(names) if isinstance(names, dict) else {}
        ),
    }


def _detect_coco_assist(image: Image.Image) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    model = _load_coco_assist_model()
    if model is None:
        return [], {
            "false_positive_filters_applied": {
                "coco_assist_attempted": True,
                "coco_assist_error": _COCO_ASSIST_LOAD_WARNING,
            }
        }

    results = model.predict(
        source=np.asarray(image),
        conf=0.15,
        iou=YOLO_IOU_THRESHOLD,
        imgsz=YOLO_IMAGE_SIZE,
        max_det=YOLO_MAX_DETECTIONS,
        verbose=False,
    )
    if not results:
        return [], {
            "false_positive_filters_applied": {"coco_assist_attempted": True}
        }

    result = results[0]
    names = getattr(result, "names", {}) or getattr(model, "names", {}) or {}
    boxes = getattr(result, "boxes", None)
    if boxes is None:
        return [], {
            "false_positive_filters_applied": {"coco_assist_attempted": True}
        }

    label_map = {
        "bottle": "Plastic Bottle",
        "cup": "Disposable Cup",
    }
    xyxy = boxes.xyxy.cpu().numpy() if hasattr(boxes.xyxy, "cpu") else np.asarray(boxes.xyxy)
    confs = boxes.conf.cpu().numpy() if hasattr(boxes.conf, "cpu") else np.asarray(boxes.conf)
    classes = boxes.cls.cpu().numpy() if hasattr(boxes.cls, "cpu") else np.asarray(boxes.cls)
    w, h = image.size
    detections: List[Dict[str, Any]] = []
    skipped = 0

    for coords, conf, cls_id in zip(xyxy, confs, classes):
        class_id = int(cls_id)
        raw_label = str(names.get(class_id, f"class_{class_id}")) if isinstance(names, dict) else f"class_{class_id}"
        mapped_label = label_map.get(raw_label.lower())
        if mapped_label is None:
            skipped += 1
            continue

        x1, y1, x2, y2 = [int(round(float(v))) for v in coords[:4]]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        if x2 <= x1 or y2 <= y1:
            continue

        confidence = round(float(conf), 4)
        detections.append({
            "label": mapped_label,
            "class_name": mapped_label.lower().replace(" ", "_"),
            "confidence": confidence,
            "bbox": [x1, y1, x2, y2],
        })

    detections.sort(key=lambda det: det["confidence"], reverse=True)
    return detections[:YOLO_MAX_DETECTIONS], {
        "model_path": str(COCO_ASSIST_MODEL_PATH),
        "model_classes": dict(names) if isinstance(names, dict) else {},
        "false_positive_filters_applied": {
            "coco_assist_attempted": True,
            "coco_assist_model": str(COCO_ASSIST_MODEL_PATH),
            "coco_assist_mapped_classes": sorted(label_map),
            "coco_assist_unmapped_classes_skipped": skipped,
        },
    }


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

        for t in range(3):
            draw.rectangle([x1 - t, y1 - t, x2 + t, y2 + t], outline=color)

        text = f"{label}  {conf:.0%}"
        try:
            bb = font.getbbox(text)
            tw, th = bb[2] - bb[0] + 2, bb[3] - bb[1] + 2
        except Exception:
            tw, th = len(text) * 7 + 4, font_size + 4

        tag_y = max(0, y1 - th - 6)
        draw.rectangle([x1, tag_y, x1 + tw + 10, tag_y + th + 6], fill=color)
        draw.text((x1 + 5, tag_y + 3), text, fill=(255, 255, 255), font=font)

    wm = f"Plastic Hunter AI - {len(detections)} item(s) detected"
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

    max_dim = 1600
    if max(image.size) > max_dim:
        image.thumbnail((max_dim, max_dim), Image.LANCZOS)

    t0 = time.time()
    detector_mode = "lightweight-cv-demo"
    fallback_warning = None

    if _YOLO_MODEL is not None:
        try:
            detections, metadata = _detect_yolo(image)
            detector_mode = "yolo"
            if not detections:
                lightweight_detections, lightweight_metadata = _detect_lightweight(image)
                if lightweight_detections:
                    detections, metadata = lightweight_detections, lightweight_metadata
                    detector_mode = "lightweight-cv-demo"
                    fallback_warning = LIGHTWEIGHT_ASSIST_WARNING
        except Exception as exc:
            detections, metadata = _detect_lightweight(image)
            fallback_warning = f"{YOLO_FALLBACK_WARNING} {exc}"
    else:
        detections, metadata = _detect_lightweight(image)
        if not MODEL_PATH.exists():
            fallback_warning = YOLO_WEIGHTS_MISSING_WARNING
        elif _YOLO_LOAD_WARNING:
            fallback_warning = _YOLO_LOAD_WARNING

    if fallback_warning:
        metadata["warning"] = (
            f"{fallback_warning} {metadata['warning']}"
            if metadata.get("warning")
            else fallback_warning
        )

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
        "detection_mode": detector_mode,
        "detector_mode": detector_mode,
        "warning": metadata["warning"],
        "quality_score": metadata["quality_score"],
        "false_positive_filters_applied": metadata["false_positive_filters_applied"],
        "model_path": metadata.get("model_path"),
        "model_classes": metadata.get("model_classes"),
        "detector_runtime_ms": round((time.time() - t0) * 1000, 1),
        "original_filename": filename,
    }
