"""
Validate the Plastic Hunter YOLO dataset.

Checks YOLO image/label structure, normalized boxes, valid class IDs, split
counts, and class distribution. This script does not create or infer labels.
Manual annotation is required when label files are missing or empty.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


DATASET_ROOT = Path("datasets") / "plastic_hunter"
DATA_YAML = DATASET_ROOT / "data.yaml"
SPLITS = ("train", "val", "test")
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}
CLASS_NAMES = [
    "plastic_bottle",
    "plastic_bag",
    "fishing_net",
    "rope_fishing_line",
    "foam_piece",
    "plastic_cap",
    "plastic_debris",
]


def _images_in(path: Path) -> List[Path]:
    if not path.exists():
        return []
    return sorted(
        p for p in path.iterdir()
        if p.is_file() and p.suffix.lower() in IMAGE_EXTENSIONS
    )


def _label_for(image_path: Path, split: str) -> Path:
    return DATASET_ROOT / "labels" / split / f"{image_path.stem}.txt"


def _parse_label_file(label_path: Path) -> Tuple[List[int], List[str]]:
    class_ids: List[int] = []
    errors: List[str] = []

    try:
        lines = label_path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        lines = label_path.read_text().splitlines()

    if not lines:
        return class_ids, [f"{label_path}: empty label file"]

    for line_no, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not stripped:
            errors.append(f"{label_path}:{line_no}: blank line")
            continue

        parts = stripped.split()
        if len(parts) != 5:
            errors.append(f"{label_path}:{line_no}: expected 5 values, got {len(parts)}")
            continue

        try:
            cls_raw = float(parts[0])
            if not cls_raw.is_integer():
                raise ValueError("class id must be an integer")
            cls_id = int(cls_raw)
            values = [float(v) for v in parts[1:]]
        except ValueError as exc:
            errors.append(f"{label_path}:{line_no}: invalid number ({exc})")
            continue

        if cls_id < 0 or cls_id >= len(CLASS_NAMES):
            errors.append(f"{label_path}:{line_no}: class id {cls_id} is outside 0-{len(CLASS_NAMES) - 1}")
            continue

        x_center, y_center, width, height = values
        if not all(0.0 <= v <= 1.0 for v in values):
            errors.append(f"{label_path}:{line_no}: box values must be normalized between 0 and 1")
            continue
        if width <= 0.0 or height <= 0.0:
            errors.append(f"{label_path}:{line_no}: width and height must be positive")
            continue

        class_ids.append(cls_id)

    return class_ids, errors


def _find_orphan_labels(split: str, image_stems: Iterable[str]) -> List[Path]:
    labels_dir = DATASET_ROOT / "labels" / split
    if not labels_dir.exists():
        return []
    known = set(image_stems)
    return sorted(
        p for p in labels_dir.glob("*.txt")
        if p.stem not in known
    )


def validate_dataset() -> int:
    errors: List[str] = []
    warnings: List[str] = []
    split_counts: Dict[str, Dict[str, int]] = {}
    class_distribution = Counter()
    split_distribution: Dict[str, Counter] = defaultdict(Counter)

    print("Plastic Hunter YOLO Dataset Validation")
    print("=" * 44)
    print(f"Dataset root: {DATASET_ROOT}")
    print(f"data.yaml: {'FOUND' if DATA_YAML.exists() else 'MISSING'}")
    print()

    if not DATA_YAML.exists():
        errors.append(f"Missing {DATA_YAML}")

    for split in SPLITS:
        images_dir = DATASET_ROOT / "images" / split
        labels_dir = DATASET_ROOT / "labels" / split
        images = _images_in(images_dir)
        labels = sorted(labels_dir.glob("*.txt")) if labels_dir.exists() else []
        split_counts[split] = {"images": len(images), "labels": len(labels)}

        if not images_dir.exists():
            errors.append(f"Missing image directory: {images_dir}")
        if not labels_dir.exists():
            errors.append(f"Missing label directory: {labels_dir}")
        if not images:
            errors.append(f"No images found in {images_dir}")

        image_stems = [p.stem for p in images]
        for image_path in images:
            label_path = _label_for(image_path, split)
            if not label_path.exists():
                errors.append(f"Missing label for image: {image_path} -> {label_path}")
                continue

            class_ids, label_errors = _parse_label_file(label_path)
            errors.extend(label_errors)
            class_distribution.update(class_ids)
            split_distribution[split].update(class_ids)

        for orphan in _find_orphan_labels(split, image_stems):
            errors.append(f"Label has no matching image: {orphan}")

    print("Split Counts")
    for split in SPLITS:
        counts = split_counts.get(split, {"images": 0, "labels": 0})
        print(f"- {split}: {counts['images']} image(s), {counts['labels']} label file(s)")

    print()
    print("Class Distribution")
    for class_id, class_name in enumerate(CLASS_NAMES):
        total = class_distribution[class_id]
        per_split = ", ".join(
            f"{split}={split_distribution[split][class_id]}" for split in SPLITS
        )
        print(f"- {class_id} {class_name}: {total} ({per_split})")

    print()
    if warnings:
        print("Warnings")
        for warning in warnings:
            print(f"- {warning}")
        print()

    if errors:
        print("Errors")
        for error in errors:
            print(f"- {error}")
        print()
        print("Dataset is NOT ready for YOLO training.")
        print("Manual labeling is required using Roboflow, CVAT, LabelImg, or Label Studio.")
        return 1

    print("Dataset looks valid for YOLO training.")
    return 0


if __name__ == "__main__":
    raise SystemExit(validate_dataset())
