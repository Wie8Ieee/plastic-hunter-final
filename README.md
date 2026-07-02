# Plastic Hunter AI
**IEEE AESS Sustainability Hackathon 2026 — Challenge 3**
*Sustainable Sonar Systems for Marine & Climate Protection*

---

## Overview

Plastic Hunter AI is a dual-mode marine pollution detection system:

1. **CV-Based Surface Detection** — Upload ocean/beach images → AI detects plastic debris using edge-guided bounding box placement (Pillow + NumPy) → results stored in SQLite and plotted on a live Leaflet.js map.

2. **Eco-Sonar Pipeline** — Simulates active / passive / hybrid sonar for *subsurface* plastic debris detection using the standard sonar equation, Mackenzie sound-speed, Thorp absorption, and Knudsen-Wenz ambient noise. Quantifiably compares a conventional baseline against an eco-adaptive configuration that reduces acoustic SEL by ~98% while retaining >90% detection coverage.

---

## Architecture

```
main.py           FastAPI routes (detect, sonar, evidence, disclosure, demo)
sonar.py          Eco-sonar simulation engine (signal chain, sonar equation, KPIs)
detector.py       CV simulation engine (Pillow edge detection, bounding boxes)
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

### Run Locally

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

Open browser at `http://localhost:8000`

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

## CV Detection — Assumptions

- **No ML model**: Ultralytics/PyTorch CUDA exceeds free-tier disk quota (400 MB+). Detection uses Pillow edge detection + image statistics to place plausible bounding boxes.
- **Reproducibility**: Random seed derived from image pixel content hash.
- **Severity**: Low < 3 items, Medium 3–6, High > 6.
- **Confidence scores**: Simulated 0.60–0.95 based on region contrast.

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

## Limitations

1. Spherical spreading TL only; no ray-tracing, multi-path, or bathymetry.
2. CV detection is edge-guided simulation, not a calibrated ML model.
3. Marine mammal exclusion zones not yet implemented.
4. Single operating frequency; no wideband mode.
5. No real underwater acoustic data; parameters from published literature.

---

## License

MIT License.

## Team

IEEE AESS Sustainability Hackathon 2026 — Challenge 3 Finalist
*Onsite Final, Egypt, 6–7 July 2026*
