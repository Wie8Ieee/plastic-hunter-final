"""
Train a YOLOv8 model for Plastic Hunter AI.

Usage:
    python train_yolo.py

The script expects a YOLO-format dataset at:
    datasets/plastic_hunter/data.yaml

After training, the script copies best.pt to:
    models/best.pt
"""

from __future__ import annotations

import argparse
import shutil
from pathlib import Path

from validate_dataset import validate_dataset


DATA_YAML = Path("datasets") / "plastic_hunter" / "data.yaml"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Plastic Hunter YOLOv8 detector.")
    parser.add_argument("--data", default=str(DATA_YAML), help="Path to YOLO data.yaml.")
    parser.add_argument("--model", default="yolov8n.pt", help="Base model, e.g. yolov8n.pt or yolov8s.pt.")
    parser.add_argument("--epochs", type=int, default=50, help="Training epochs.")
    parser.add_argument("--imgsz", type=int, default=640, help="Training image size.")
    parser.add_argument("--batch", default="-1", help="Batch size. Use -1 for Ultralytics AutoBatch.")
    parser.add_argument("--workers", type=int, default=2, help="Data loader workers.")
    parser.add_argument("--device", default=None, help="Training device, e.g. 0, cpu. Defaults to Ultralytics auto.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_path = Path(args.data)
    if not data_path.exists():
        print(f"Dataset config not found: {data_path}")
        print("Create/label the dataset first, then run: python validate_dataset.py")
        return 1

    if data_path == DATA_YAML:
        print("Validating dataset before training...")
        validation_code = validate_dataset()
        if validation_code != 0:
            print()
            print("Training stopped because the dataset is not ready.")
            return validation_code

    try:
        from ultralytics import YOLO
    except Exception as exc:
        print("Ultralytics is not installed.")
        print("Install training dependencies with:")
        print("  pip install ultralytics torch torchvision")
        print(f"Import error: {exc}")
        return 1

    batch = int(args.batch) if str(args.batch).lstrip("-").isdigit() else args.batch
    model = YOLO(args.model)
    train_kwargs = {
        "data": str(data_path),
        "imgsz": args.imgsz,
        "epochs": args.epochs,
        "batch": batch,
        "project": "runs/detect",
        "name": "train",
        "exist_ok": True,
        "workers": args.workers,
    }
    if args.device:
        train_kwargs["device"] = args.device

    print("Starting YOLOv8 training...")
    print(f"Base model: {args.model}")
    print(f"Dataset: {data_path}")
    print(f"Epochs: {args.epochs}, imgsz: {args.imgsz}, batch: {batch}")

    results = model.train(**train_kwargs)

    save_dir = Path(getattr(getattr(results, "trainer", None), "save_dir", "runs/detect/train"))
    best_path = save_dir / "weights" / "best.pt"
    last_path = save_dir / "weights" / "last.pt"
    print()
    print("Training complete.")
    print(f"Best weights expected at: {best_path}")
    if best_path.exists():
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        shutil.copy2(best_path, models_dir / "best.pt")
        if last_path.exists():
            shutil.copy2(last_path, models_dir / "last.pt")
        print("YOLO weights copied for FastAPI inference:")
        print(f"  {models_dir / 'best.pt'}")
        if (models_dir / "last.pt").exists():
            print(f"  {models_dir / 'last.pt'}")
    else:
        print("best.pt was not found at the expected path. Check the Ultralytics run output above.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
