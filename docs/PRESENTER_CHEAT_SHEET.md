# Plastic Hunter AI - Presenter Cheat Sheet

## One-Sentence Summary

Plastic Hunter AI هو proof-of-concept لمنصة مراقبة تلوث بحري تجمع بين Computer Vision لفحص الصور السطحية وEco-Adaptive Sonar Simulation لمقارنة detection coverage مع acoustic exposure reduction.

## What To Say First

"This project is not claiming real sonar hardware. It is an executable software prototype that shows how a marine monitoring team could combine surface image inspection, geospatial logging, sonar trade-off simulation, and a final evidence report."

## Main Problem

- Marine plastic pollution يظهر على الشاطئ والسطح، وقد يوجد تحت الماء.
- Manual monitoring بطيء ومحدود.
- Cameras لا تكشف underwater debris.
- Conventional Active Sonar قد يرفع Acoustic Exposure بسبب frequent/high-power pings.

## Main Solution

- Surface Inspection: upload image and run detector.
- Monitoring Map: log inspection results geographically.
- Mission Overview: show inspection and sustainability metrics.
- Sonar Simulation: compare Conventional, Eco-Adaptive, Passive modes.
- Final Evidence Report: show baseline, improved case, KPIs, assumptions, limitations.
- Method Disclosure: show datasets, libraries, references, and prior work.

## Core Technical KPI

**Detection Coverage Retained**  
يعني: كم target بقي eco-adaptive mode قادرا على كشفه مقارنة بـ Conventional Sonar.

## Core Sustainability KPI

**Acoustic Exposure Reduction**  
يشمل:

- SEL reduction
- Duty Cycle reduction
- Energy Proxy reduction

## Main Architecture

```text
User
↓
FastAPI
↓
Computer Vision
↓
Sonar Engine
↓
SQLite
↓
Mission Overview / Map
↓
Final Evidence Report
```

## Important Files

- `main.py`: API routes and orchestration.
- `detector.py`: YOLO if available, otherwise Lightweight Detector.
- `sonar.py`: Sonar Simulation equations and KPIs.
- `database.py`: SQLite storage and stats.
- `static/index.html`: full frontend.
- `README.md`: setup and technical overview.
- `Dockerfile`: container run path.

## Computer Vision Talking Points

Say:

- "The CV module inspects visible plastic debris in images."
- "YOLO runs only if `models/best.pt` exists and Ultralytics loads."
- "If YOLO is unavailable, the app remains stable using a lightweight detector."
- "Image quality matters: clear, close, daylight images work best."

Do not say:

- "The detector is perfect."
- "The live demo is always YOLO."
- "It detects all plastic in every image."

## Research Foundation

Documented results:

- Trash-ICRA19 used for research evaluation.
- YOLOv8s, Faster R-CNN, MobileNet SSD evaluated.
- YOLOv8s: 97.77% mAP@0.5 and 122.10 FPS.
- River Floating Trash Dataset used for cross-domain testing.
- Faster R-CNN: 32.22% mAP@0.5 cross-domain result.
- Paper is under preparation/submission; public publication is not confirmed.

## Sonar Talking Points

Say:

- "The sonar part is a simulation, not hardware."
- "Conventional Sonar is the baseline."
- "Eco-Adaptive Sonar reduces Source Level by 12 dB and increases Ping Interval by 3x."
- "This reduces Duty Cycle, cumulative SEL, and energy proxy."
- "The trade-off is reduced range or missed weak/distant targets."

Do not say:

- "We tested real sonar in the ocean."
- "This proves real environmental impact."
- "Passive mode classifies plastic objects."

## Sonar Parameters

- Source Level: transmitted acoustic level.
- Frequency: operating kHz.
- Pulse Duration: ping length.
- Ping Interval: time between pings.
- Sea State: ambient noise condition.
- Depth: operating depth.
- Mission Duration: total simulated mission time.

## Evidence Report

Use it to show:

- Problem
- Core function
- Baseline
- Improved case
- Test conditions
- Technical KPI
- Sustainability KPI
- Limitations
- Repository link

Key sentence:

"The Evidence Report does not claim hardware validation; it documents the simulation assumptions and measurable trade-off."

## Method Disclosure

Must remain visible. It explains:

- AI/model methods
- Libraries
- Datasets
- Academic references
- Prior work
- Limitations

## 5-Minute Presentation Flow

### 0:00-0:40 Problem

"Marine plastic monitoring needs both visible surface inspection and underwater sensing. Manual monitoring is limited, and conventional sonar can increase acoustic exposure."

### 0:40-1:20 Solution

"Plastic Hunter combines image-based surface inspection with an eco-adaptive sonar simulation and evidence report."

### 1:20-2:00 Architecture

"FastAPI coordinates the detector, sonar engine, SQLite storage, map, dashboard, and report endpoints."

### 2:00-3:20 Sonar KPIs

"The main technical KPI is Detection Coverage Retained. The sustainability KPI is Acoustic Exposure Reduction through lower SEL and lower Duty Cycle."

### 3:20-4:10 Research Foundation

"The CV research track used Trash-ICRA19 and River Floating Trash Dataset. YOLOv8s reached 97.77% mAP@0.5 and 122.10 FPS in the documented evaluation."

### 4:10-5:00 Closing

"This is a transparent proof-of-concept for sustainable marine sensing. The next step is hardware validation and production-grade trained model deployment."

## Live Demo Flow

1. Mission Overview  
   Say: "This is the operations summary."

2. Surface Inspection  
   Click: Select Image, then Analyze Image.  
   Say: "The response shows detector mode, confidence, severity, and annotated output."

3. Monitoring Map  
   Click a marker.  
   Say: "This shows stored inspection records."

4. Sonar Simulation  
   Select a preset and click Start Sonar Simulation.  
   Say: "This compares conventional and eco-adaptive modes."

5. Final Evidence Report  
   Say: "This is the structured judge-facing brief."

6. Method Disclosure  
   Say: "This keeps resources, assumptions, and external methods transparent."

## Top Judge Q&A

**Is sonar real?**  
No. It is a mathematical Sonar Simulation, not hardware.

**Why simulation?**  
To demonstrate the trade-off before hardware trials.

**Does YOLO run?**  
Only when weights and dependencies are available.

**What is SEL?**  
Sound Exposure Level, a cumulative acoustic exposure metric.

**What is Duty Cycle?**  
The active transmission fraction of mission time.

**What is the trade-off?**  
Lower acoustic exposure can reduce range or miss weak targets.

**Is the research published?**  
Not confirmed. The repository says under preparation/submission.

**What is the biggest limitation?**  
No real sonar hardware validation yet.

## Dangerous Claims To Avoid

- "This is real sonar hardware."
- "We tested it in the ocean."
- "The live demo is always YOLO."
- "The research is published."
- "The system is production-ready."
- "The detector is perfect."

## Best Closing Sentence

"Plastic Hunter AI is not presented as a finished ocean deployment; it is a transparent, executable proof-of-concept showing how marine detection performance and sonar sustainability can be evaluated together."
