# Plastic Hunter AI
**IEEE AESS Sustainability Hackathon 2026 — Challenge 3**
*Sustainable Sonar Systems for Marine & Climate Protection*

---

## Overview

Plastic Hunter AI is a dual-mode marine pollution detection system:

1. **CV-Based Surface Detection** - The computer vision component is research-backed using real marine debris datasets. Our team trained and evaluated YOLOv8s, Faster R-CNN, and MobileNet SSD on Trash-ICRA19, with cross-domain testing on the River Floating Trash Dataset. YOLOv8s achieved 97.77% mAP@0.5 at 122.10 FPS. Demo results are stored in SQLite and plotted on a live Leaflet.js map.

2. **Eco-Sonar Pipeline** — Simulates active / passive / hybrid sonar for *subsurface* plastic debris detection using the standard sonar equation, Mackenzie sound-speed, Thorp absorption, and Knudsen-Wenz ambient noise. Quantifiably compares a conventional baseline against an eco-adaptive configuration that reduces acoustic SEL by ~98% while retaining >90% detection coverage.

For a concise competition-facing summary of scope, architecture, APIs, limitations, and production readiness, see [docs/TECHNICAL_BRIEF.md](docs/TECHNICAL_BRIEF.md).

---

## Architecture

```
main.py           FastAPI routes (detect, sonar, evidence, disclosure, demo)
sonar.py          Eco-sonar simulation engine (signal chain, sonar equation, KPIs)
detector.py       Lightweight deployable CV demo interface (Pillow/NumPy region proposals, conservative bounding boxes)
database.py       SQLite schema, CRUD, 12-location seeded demo data
static/
  index.html      Single-page frontend (Detect / Map / Dashboard / History / Sonar)
results/          Annotated output images (auto-created)
detections.db     SQLite database (auto-created on first run)
```

---

## Setup

### Requirements
- Python 3.11+

```bash
pip install fastapi uvicorn pillow numpy python-multipart
```

### Run on GitHub Codespaces

1. Open this repository on GitHub.
2. Click `Code` -> `Codespaces` -> `Create codespace on main`.
3. Wait for the Codespace to finish building.
4. The app starts automatically on port `8000`.
5. In the `PORTS` tab, open the forwarded `8000` URL.

The Codespaces port is configured as public for demos. The link stays available while the Codespace is running.

### Run Locally

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open browser at `http://local7host:8000`

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Frontend SPA |
| `POST` | `/detect` | Upload image → CV detection → store result |
| `GET` | `/results` | All past detections (JSON) |
| `GET` | `/stats` | Aggregate stats (scans, counts, chart data) |
| `POST` | `/demo` | Reset and reload 12 demo detections |
| `POST` | `/sonar/ping` | Run sonar scenario (3 modes, full KPIs) |
| `GET` | `/evidence` | One-page evidence sheet data (JSON) |
| `GET` | `/disclosure` | AI / external resource disclosure (JSON) |
| `GET` | `/results/{filename}` | Serve annotated image |

### `/sonar/ping` Parameters (Form data)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `source_level` | 200.0 | Source level dB re 1 μPa @ 1 m |
| `frequency_kHz` | 10.0 | Operating frequency in kHz |
| `pulse_ms` | 100.0 | Pulse duration in ms |
| `ping_interval_s` | 5.0 | Time between pings in seconds |
| `mission_min` | 60.0 | Mission duration in minutes |
| `sea_state` | 3 | Sea state 1–5 |
| `depth_m` | 50.0 | Operating depth in metres |
| `seed` | 42 | Random seed for target placement |

### `/sonar/ping` Response (JSON)

```json
{
  "conventional":  { "duty_cycle_pct": 2.0, "sel_cum_dB": ..., "max_range_m": ..., "targets_detected": ... },
  "eco_adaptive":  { "duty_cycle_pct": 0.67, "sel_cum_dB": ..., "max_range_m": ..., "targets_detected": ... },
  "passive":       { "duty_cycle_pct": 0, "sel_cum_dB": 0 },
  "metrics": {
    "sel_reduction_pct": 97.9,
    "sel_reduction_dB":  ...,
    "duty_cycle_reduction_pct": 66.7,
    "eco_detection_retention_pct": 100.0,
    "energy_reduction_pct": 97.9
  },
  "range_sweep":   [...],
  "dc_sweep":      [...]
}
```

---

## Sonar Simulation — Signal Chain & Assumptions

### Signal Chain
```
Waveform (LFM chirp, τ ms)
  → Propagation (TL: spherical spreading + Thorp absorption)
    → Target reflection (TS, dB re 1 m²)
      → Reception (ambient noise NL, Knudsen-Wenz)
        → Detection threshold (P_d sigmoid, P_fa = 1e-4)
          → Classification (debris type)
```

### Key Equations

**Active Sonar Equation:**
```
SNR = SL − TL + TS − NL + AG
```

**Two-Way Transmission Loss:**
```
TL = 40·log₁₀(R) + 2·α·R/1000   [dB]
α  = Thorp (1967) absorption coefficient
```

**Ambient Noise (Knudsen-Wenz):**
```
NL ≈ 50 − 17·log₁₀(f_kHz) + 5·SeaState   [dB re 1 μPa²/Hz]
```

**Detection Probability:**
```
P_d = 1 / (1 + exp(−0.55·(SNR − 5)))   [P_fa = 1×10⁻⁴]
```

**Sound Exposure Level:**
```
SEL_cum = SL + 10·log₁₀(τ_s) + 10·log₁₀(N_pings)
```

### Plastic Debris Target Strengths

| Type | TS (dB re 1 m²) | Notes |
|------|-----------------|-------|
| Ghost Fishing Net | −10 | Large extended target |
| Large Plastic Drum | −15 | Rigid shell reflector |
| Submerged Plastic Bag | −25 | Soft, low contrast |
| Foam / Packaging Block | −28 | High attenuation |
| Micro-Plastic Cluster | −40 | Weakest reflector |

### Eco-Adaptive Algorithm

| Parameter | Conventional | Eco-Adaptive | Change |
|-----------|-------------|--------------|--------|
| Source Level | 200 dB | 188 dB | −12 dB |
| Ping Interval | 5 s | 15 s | ×3 |
| Duty Cycle | 2.0% | 0.67% | −66.7% |
| Cumulative SEL | baseline | −12 dB+ | ~98% cut |
| Detection Retention | 100% | >90% | <10% trade-off |
| Energy (proxy) | 100% | ~2% | ~98% reduction |

---

## CV Detection - Research Validation

- The computer vision component is research-backed using real marine debris datasets.
- Our team trained and evaluated YOLOv8s, Faster R-CNN, and MobileNet SSD on Trash-ICRA19, with cross-domain testing on the River Floating Trash Dataset.
- YOLOv8s achieved 97.77% mAP@0.5 at 122.10 FPS.
- The live demo uses a lightweight deployable interface because Ultralytics/PyTorch CUDA exceeds free-tier disk quota (400 MB+).
- The live detector automatically uses real YOLO inference when trained weights are available at `models/best.pt` and the optional YOLO dependencies are installed. Otherwise it falls back to the conservative lightweight deployment demo.
- Best results require clear, visible plastic objects in the foreground. Very small, dark, blurry, distant, or visually ambiguous debris may be skipped or reported with a low-confidence scene warning.
- Production deployments should use real YOLOv8 inference when GPU/disk resources are available.
- **Reproducibility**: Random seed derived from image pixel content hash.
- **Severity**: Low < 3 items, Medium 3–6, High > 6.
- **Confidence scores in demo**: Conservative scores based on edge density, local contrast, saturation/color cues, texture irregularity, size, foreground location, and plastic-like reflection patterns.

### Enabling YOLO Inference

YOLO is optional and is not required for the lightweight demo.

```bash
pip install ultralytics torch torchvision
mkdir -p models
# place your trained weights here:
# models/best.pt
```

When `models/best.pt` exists and `ultralytics` can be imported, `detector.py` loads the model once at startup and returns model-based boxes with `detector_mode: "yolo"`. If the weights or dependencies are missing, or YOLO inference fails, the API remains stable and falls back to `detector_mode: "lightweight-cv-demo"` with a warning when appropriate.

Production accuracy requires trained YOLO weights that match the target classes and deployment environment. The lightweight mode is only a constrained deployment demo, not a substitute for trained model inference.

## How to Train YOLO

### Dataset Folder Structure

Use YOLO text annotations with one label file per image:

```text
datasets/plastic_hunter/
  images/
    train/
    val/
    test/
  labels/
    train/
    val/
    test/
  data.yaml
```

The `datasets/` directory is intentionally ignored by Git. Keep full training datasets locally or in external storage, then document the source and preparation steps instead of committing the dataset to this repository.

Each label line must use normalized YOLO format:

```text
class_id x_center y_center width height
```

Classes:

```text
0 plastic_bottle
1 plastic_bag
2 fishing_net
3 rope_fishing_line
4 foam_piece
5 plastic_cap
6 plastic_debris
```

### Labeling Tools

Manual labeling is required before training. Use a real annotation tool such as Roboflow, CVAT, LabelImg, or Label Studio. Do not create random boxes or synthetic labels for model training.

### `data.yaml` Example

```yaml
path: datasets/plastic_hunter
train: images/train
val: images/val
test: images/test

names:
  0: plastic_bottle
  1: plastic_bag
  2: fishing_net
  3: rope_fishing_line
  4: foam_piece
  5: plastic_cap
  6: plastic_debris
```

### Validate Dataset

```bash
python validate_dataset.py
```

The validator checks image/label pairs, class IDs, normalized boxes, malformed labels, split counts, and class distribution.

### Train

Install optional training dependencies:

```bash
pip install ultralytics torch torchvision
```

Run training:

```bash
python train_yolo.py
```

Defaults: `yolov8s.pt`, `imgsz=640`, `epochs=50`, AutoBatch, output under `runs/detect/train`. Base model files and training outputs are intentionally ignored by Git; commit only the final deployment weight at `models/best.pt` when needed.

## Model Integration

After training, copy the trained best weights into:

```text
models/best.pt
```

At app startup, `detector.py` checks for `models/best.pt`. If the file exists and `ultralytics` is installed, it loads YOLO once and `/detect` returns model-based detections with `detector_mode: "yolo"`.

If `models/best.pt` is missing, dependencies are not installed, or YOLO inference fails, the app falls back to `detector_mode: "lightweight-cv-demo"` and keeps the existing API/UI stable.

### Recommended `sample_images/` Test Set

Create a local `sample_images/` folder with 5-10 clear images:

- close-up plastic bottles on beach
- plastic bags on sand
- fishing net or rope on shoreline
- mixed debris near water
- one clean beach negative sample with no plastic
- one dark or blurry low-quality beach scene

The lightweight detector is tuned to prefer fewer, higher-confidence detections over many uncertain boxes.

---

## Test Cases — Multi-Case Validation

| Test Sweep | Range | Validates |
|------------|-------|-----------|
| Source Level | 160–220 dB | Max range vs SL |
| Sea State (Noise) | 1–5 | Robustness to ambient noise |
| Duty Cycle | 2% → 0.2% | SEL vs operational tempo |
| Detection Range | 100–5000 m | P_d for all 3 modes |

---

## Reproduction Steps

```bash
# 1. Start server
python -m uvicorn main:app --host 0.0.0.0 --port 8000

# 2. Run default sonar scenario
curl -X POST http://localhost:8000/sonar/ping \
  -F "source_level=200" -F "frequency_kHz=10" \
  -F "pulse_ms=100" -F "ping_interval_s=5" \
  -F "sea_state=3" -F "depth_m=50" -F "mission_min=60" -F "seed=42"

# 3. Get evidence sheet
curl http://localhost:8000/evidence

# 4. Get AI disclosure
curl http://localhost:8000/disclosure

# 5. Reset demo data
curl -X POST http://localhost:8000/demo

# 6. Run image detection
curl -X POST http://localhost:8000/detect -F "file=@your_image.jpg"
```

---

## Live Demo Flow (5 min)

1. **Upload image** → Detect tab → Run Detection → view annotated bounding boxes
2. **Map tab** → see detection location on Leaflet map
3. **Dashboard tab** → KPI cards, bar/doughnut charts, Eco-Sonar sustainability metrics
4. **Sonar tab** → adjust parameters → Run Scenario → view PPI radar display, P(d) vs Range chart, KPI comparisons
5. **Evidence Sheet** button → display one-page summary

---

## How to Explain the Sonar Module to Judges

The sonar page is an executable engineering simulation, not field hardware. It uses environmental and sonar parameters such as source level, frequency, pulse duration, ping interval, sea state, water depth, and mission duration to run a reproducible active/passive/eco-adaptive detection scenario.

Inputs drive simplified acoustic models: sound speed, ambient noise, transmission loss, target strength, SNR, detection probability, echo return time, cumulative sound exposure, and an acoustic energy proxy. The UI includes mission presets, target-level detection tables, echo timing, a visual sonar beam mission view, and a baseline vs eco-adaptive decision summary.

For Challenge 3 proof-of-concept judging, the module demonstrates the engineering trade-off:

- **Primary Technical KPI: Detection Coverage Retained** - how many simulated debris targets the eco-adaptive mode detects compared with the conventional active baseline.
- **Primary Sustainability KPI: Acoustic Exposure Reduction** - how much cumulative SEL, active duty cycle, and acoustic energy proxy are reduced.

The correct explanation is: "This is a mathematical proof-of-concept simulation for eco-adaptive sonar behavior. It is designed to show measurable trade-offs and reproducible assumptions. It is not claiming real underwater hardware measurements. Production validation would require calibrated sonar hardware, sea trials, measured target strengths, bathymetry, multipath modeling, and environmental compliance review."

---

## Limitations

1. Spherical spreading TL only; no ray-tracing, multi-path, or bathymetry.
2. The sonar component is currently simulation-based and requires hardware validation. The CV component is supported by real dataset experiments, but the live demo uses a lightweight deployable interface optimized for constrained deployment.
3. Marine mammal exclusion zones not yet implemented.
4. Single operating frequency; no wideband mode.
5. No real underwater acoustic data; parameters from published literature.
6. Real YOLOv8 inference should be used for production when GPU and disk resources are available.
7. Research validation is based on real datasets, but the live demo is optimized for lightweight deployment and works best on clear visible plastic objects.

---

## License

MIT License.

## Team

IEEE AESS Sustainability Hackathon 2026 — Challenge 3 Finalist
*Onsite Final, Egypt, 6–7 July 2026*
