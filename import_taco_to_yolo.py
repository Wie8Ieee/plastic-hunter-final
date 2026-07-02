"""
Import plastic-related TACO annotations into the Plastic Hunter YOLO dataset.

Source dataset:
    https://github.com/pedropro/TACO

This script downloads only images that have mapped plastic-related annotations
and converts their COCO bounding boxes to normalized YOLO labels. It does not
invent annotations.
"""

from __future__ import annotations

import argparse
import json
import shutil
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Tuple

import requests


TACO_ANNOTATIONS = Path("external") / "TACO" / "data" / "annotations.json"
DATASET_ROOT = Path("datasets") / "plastic_hunter"
SOURCE_DIR = Path("external") / "TACO" / "data"
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

TARGET_CLASS_IDS = {name: idx for idx, name in enumerate(CLASS_NAMES)}

TACO_TO_PLASTIC_HUNTER = {
    "Other plastic bottle": "plastic_bottle",
    "Clear plastic bottle": "plastic_bottle",
    "Plastic bottle cap": "plastic_cap",
    "Disposable plastic cup": "plastic_debris",
    "Foam cup": "foam_piece",
    "Other plastic cup": "plastic_debris",
    "Plastic lid": "plastic_debris",
    "Other plastic": "plastic_debris",
    "Plastic film": "plastic_bag",
    "Six pack rings": "plastic_bag",
    "Garbage bag": "plastic_bag",
    "Other plastic wrapper": "plastic_bag",
    "Single-use carrier bag": "plastic_bag",
    "Polypropylene bag": "plastic_bag",
    "Crisp packet": "plastic_bag",
    "Spread tub": "plastic_debris",
    "Tupperware": "plastic_debris",
    "Disposable food container": "plastic_debris",
    "Foam food container": "foam_piece",
    "Other plastic container": "plastic_debris",
    "Plastic glooves": "plastic_debris",
    "Plastic utensils": "plastic_debris",
    "Rope & strings": "rope_fishing_line",
    "Plastic straw": "plastic_debris",
    "Styrofoam piece": "foam_piece",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Import TACO plastic annotations into YOLO format.")
    parser.add_argument("--annotations", default=str(TACO_ANNOTATIONS), help="Path to TACO annotations.json.")
    parser.add_argument("--limit", type=int, default=0, help="Optional max number of images to import. 0 imports all.")
    parser.add_argument("--timeout", type=int, default=20, help="Download timeout in seconds.")
    parser.add_argument("--clear", action="store_true", help="Clear existing Plastic Hunter images/labels before import.")
    return parser.parse_args()


def ensure_dirs(clear: bool) -> None:
    for split in ("train", "val", "test"):
        for kind in ("images", "labels"):
            path = DATASET_ROOT / kind / split
            path.mkdir(parents=True, exist_ok=True)
            if clear:
                for item in path.iterdir():
                    if item.name == ".gitkeep":
                        continue
                    if item.is_file():
                        item.unlink()


def split_for_index(index: int, total: int) -> str:
    if total <= 1:
        return "train"
    ratio = index / total
    if ratio < 0.80:
        return "train"
    if ratio < 0.90:
        return "val"
    return "test"


def yolo_line(bbox: List[float], width: int, height: int, class_id: int) -> str | None:
    x, y, bw, bh = bbox
    if width <= 0 or height <= 0 or bw <= 0 or bh <= 0:
        return None
    x_center = (x + bw / 2.0) / width
    y_center = (y + bh / 2.0) / height
    norm_w = bw / width
    norm_h = bh / height
    values = [x_center, y_center, norm_w, norm_h]
    if not all(0.0 <= value <= 1.0 for value in values):
        values = [min(1.0, max(0.0, value)) for value in values]
    if values[2] <= 0.0 or values[3] <= 0.0:
        return None
    return f"{class_id} " + " ".join(f"{value:.6f}" for value in values)


def download_image(image: Dict, target_path: Path, timeout: int) -> bool:
    source_path = SOURCE_DIR / image["file_name"]
    if source_path.exists():
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, target_path)
        return True

    url = image.get("flickr_url") or image.get("flickr_640_url")
    if not url:
        return False

    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()
    except requests.RequestException:
        return False

    target_path.parent.mkdir(parents=True, exist_ok=True)
    target_path.write_bytes(response.content)
    return True


def main() -> int:
    args = parse_args()
    annotation_path = Path(args.annotations)
    if not annotation_path.exists():
        print(f"TACO annotations not found: {annotation_path}")
        print("Run: git clone --depth 1 https://github.com/pedropro/TACO.git external/TACO")
        return 1

    ensure_dirs(clear=args.clear)

    data = json.loads(annotation_path.read_text(encoding="utf-8"))
    categories = {cat["id"]: cat["name"] for cat in data["categories"]}
    images = {image["id"]: image for image in data["images"]}
    annotations_by_image: Dict[int, List[Tuple[int, List[float]]]] = defaultdict(list)

    for ann in data["annotations"]:
        category_name = categories.get(ann["category_id"])
        target_name = TACO_TO_PLASTIC_HUNTER.get(category_name)
        if not target_name:
            continue
        image = images.get(ann["image_id"])
        if not image:
            continue
        line = yolo_line(
            ann["bbox"],
            int(image["width"]),
            int(image["height"]),
            TARGET_CLASS_IDS[target_name],
        )
        if line is None:
            continue
        annotations_by_image[ann["image_id"]].append((TARGET_CLASS_IDS[target_name], line))

    selected_ids = sorted(annotations_by_image)
    if args.limit > 0:
        selected_ids = selected_ids[:args.limit]

    imported = 0
    failed = 0
    class_counts = defaultdict(int)
    split_counts = defaultdict(int)

    for index, image_id in enumerate(selected_ids):
        image = images[image_id]
        suffix = Path(image["file_name"]).suffix.lower()
        if suffix not in IMAGE_EXTENSIONS:
            suffix = ".jpg"
        split = split_for_index(index, len(selected_ids))
        stem = f"taco_{image_id:05d}"
        image_target = DATASET_ROOT / "images" / split / f"{stem}{suffix}"
        label_target = DATASET_ROOT / "labels" / split / f"{stem}.txt"

        if not download_image(image, image_target, args.timeout):
            failed += 1
            print(f"download failed: image_id={image_id} url={image.get('flickr_url')}")
            continue

        label_lines = [line for _class_id, line in annotations_by_image[image_id]]
        label_target.write_text("\n".join(label_lines) + "\n", encoding="utf-8")

        for class_id, _line in annotations_by_image[image_id]:
            class_counts[class_id] += 1
        imported += 1
        split_counts[split] += 1
        print(f"imported {imported}/{len(selected_ids)} -> {split}/{image_target.name}")

    print()
    print("TACO import complete.")
    print(f"Imported images: {imported}")
    print(f"Failed downloads: {failed}")
    print("Split counts:")
    for split in ("train", "val", "test"):
        print(f"- {split}: {split_counts[split]}")
    print("Class counts:")
    for class_id, class_name in enumerate(CLASS_NAMES):
        print(f"- {class_id} {class_name}: {class_counts[class_id]}")
    return 0 if imported > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
