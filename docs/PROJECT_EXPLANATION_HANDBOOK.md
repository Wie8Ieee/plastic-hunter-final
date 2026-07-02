# Plastic Hunter AI - Project Explanation Handbook

هذا الدليل مكتوب للفريق الذي سيشرح المشروع أو يدافع عنه أمام لجنة IEEE. الهدف ليس حفظ كلام تسويقي، بل فهم النظام: ماذا يفعل، ماذا لا يفعل، ما هي الحسابات الموجودة، وما هي الحدود التي يجب قولها بوضوح.

## 1. Project Identity

**Project name:** Plastic Hunter AI

**Team name:** Team EcoNauts مذكور في README القديم وسياق المشروع. إن كان اسم الفريق الرسمي تغيّر، يجب تحديثه في العرض.  

**Hackathon track:** IEEE AESS Sustainability Hackathon 2026 - Challenge 3: Sustainable Sonar Systems for Marine & Climate Protection.

**Challenge goal:** تقديم proof-of-concept لنظام sensing بحري يقلل الأثر البيئي، خصوصا acoustic exposure، مع الحفاظ على قدرة كشف مفيدة.

**One-sentence summary:** Plastic Hunter AI هو prototype لمنصة مراقبة تلوث بحري تجمع بين Computer Vision لفحص الصور السطحية وSonar Simulation لشرح trade-off بين Conventional Sonar وEco-Adaptive Sonar.

## 2. The Problem

Marine plastic pollution مشكلة بيئية لأن البلاستيك يتراكم على الشواطئ، يطفو على سطح الماء، وقد يبقى تحت السطح أو يعلق في nets/ropes/debris. جزء من المشكلة مرئي بالكاميرات، لكن جزءا آخر تحت الماء لا يمكن فهمه بالصور السطحية فقط.

المراقبة اليدوية محدودة لأنها بطيئة، مكلفة، وتعتمد على وجود فرق ميدانية. كما أن التغطية الجغرافية قد تكون متقطعة، والنتائج تتأثر بوقت الزيارة، الطقس، والإضاءة.

الكاميرات وحدها ليست كافية. Computer Vision يساعد في surface inspection، لكنه لا يرى ما تحت سطح الماء، ولا يعمل جيدا إذا كانت الصورة مظلمة أو ضبابية أو الجسم صغيرا جدا أو بعيدا.

Conventional active sonar يمكن أن يساعد في underwater sensing، لكنه يرسل pings صوتية نشطة. زيادة Source Level أو كثافة pinging قد ترفع Acoustic Exposure وتؤثر على البيئة البحرية. لهذا السبب Challenge 3 يهتم بسونار أكثر استدامة، وليس فقط بكشف أقوى.

## 3. The Proposed Solution

Plastic Hunter AI يقدم workflow كامل:

- Surface Inspection: رفع صورة بحرية أو ساحلية وتحليلها عبر detector.
- Monitoring Map: تسجيل النتائج على خريطة.
- Mission Overview: عرض مؤشرات التشغيل والنتائج.
- Sonar Simulation: مقارنة Conventional Sonar وEco-Adaptive Sonar وPassive Sonar.
- Final Evidence Report: تلخيص assumptions وKPIs والحدود.
- Method Disclosure: توضيح datasets وlibraries والمراجع والموارد الخارجية.

سبب الجمع بين Computer Vision وEco-Adaptive Sonar Simulation هو أن المشروع يعالج نوعين من sensing:

- Computer Vision مناسب للأجسام المرئية على السطح أو الشاطئ.
- Sonar Simulation يشرح كيف يمكن التفكير في الكشف تحت الماء مع تقليل acoustic footprint.

الارتباط بـ Challenge 3 هو أن الجزء الأساسي ليس "AI detection" وحده، بل مقارنة sonar baseline مع eco-adaptive approach عبر KPIs مثل Detection Coverage Retained وAcoustic Exposure Reduction.

**Core innovation:** تحويل فكرة eco-adaptive sonar إلى simulation قابلة للتشغيل داخل تطبيق، مع Evidence Sheet يوضح trade-off: ماذا نحتفظ به من detection، وماذا نوفره من acoustic exposure وduty cycle وenergy proxy.

## 4. System Architecture

المسار العام:

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
Dashboard / Mission Overview
↓
Evidence Sheet
```

شرح الملفات:

| File | Role |
|---|---|
| `main.py` | نقطة دخول FastAPI. يحتوي routes مثل `/detect`, `/sonar/ping`, `/evidence`, `/disclosure`, `/stats`, `/results`. يدير upload validation ويستدعي detector وsonar وdatabase. |
| `detector.py` | محرك Computer Vision. يدعم YOLO إذا وجد `models/best.pt` وكانت `ultralytics` متاحة. إذا لم يعمل YOLO، يرجع إلى Lightweight Detector. ينتج bounding boxes وconfidence وannotated image. |
| `sonar.py` | محرك Sonar Simulation. يحسب sound speed, transmission loss, ambient noise, SNR, Detection Probability, SEL, Duty Cycle, Energy Proxy, detection retention. |
| `database.py` | يدير SQLite database `detections.db`: إنشاء الجدول، seed demo data، حفظ detections، حساب statistics. |
| `static/index.html` | الواجهة الأمامية Single Page App: Mission Overview, Surface Inspection, Monitoring Map, Sonar Simulation, Survey Log, modals للتقرير والإفصاح. |
| `README.md` | وثيقة تشغيل وشرح عام للمشروع، API، sonar equations، YOLO training، limitations. |
| `Dockerfile` | يبني image من `python:3.11-slim` ويشغل Uvicorn على port 8000. |
| `requirements.txt` | dependencies: FastAPI, Uvicorn, Pillow, NumPy, python-multipart, ultralytics, torch, torchvision. |
| `docs/assets` | يحتوي architecture SVG وscreenshots للواجهة. |

## 5. Full User Workflow

### عندما يفتح المستخدم التطبيق

المستخدم يفتح `/` في المتصفح. FastAPI يرجع `static/index.html`. الواجهة تبدأ من Mission Overview وتعرض مؤشرات من `/stats`.

### عندما يرفع صورة

في Surface Inspection، يختار المستخدم صورة. الواجهة تعرض preview وتفعل زر Analyze Image.

### عندما يشغل detection

الواجهة ترسل POST إلى `/detect` مع الملف. `main.py` يتحقق من نوع وحجم الصورة، ثم يستدعي `run_detection` في `detector.py`. النتيجة تحفظ في SQLite مع موقع ساحلي seeded إذا لم يرسل المستخدم latitude/longitude. الواجهة تعرض annotated image وinspection report.

### عندما يفتح Monitoring Map

الواجهة تستدعي `/results` وتعرض detections كـ markers على Leaflet map. عند اختيار marker تظهر التفاصيل في side panel.

### عندما يفتح Mission Overview

الواجهة تستدعي `/stats` وتعرض عدد inspections، عدد observed items، confidence bands، severity breakdown، charts، وsonar sustainability summary من `/sonar/ping`.

### عندما يشغل Sonar Simulation

المستخدم يختار preset أو يعدل parameters، ثم يضغط Start Sonar Simulation. الواجهة ترسل POST إلى `/sonar/ping`. `sonar.py` يرجع نتائج Conventional, Eco-Adaptive, Passive، targets، SNR، P(detect)، SEL، duty cycle، وtrade-off.

### عندما يفتح Final Evidence Report

الواجهة تستدعي `/evidence`. هذا endpoint يبني report من stats وsonar default scenario ويعرض problem, baseline, improved case, KPIs, limitations, assumptions.

### عندما يفتح Method Disclosure

الواجهة تستدعي `/disclosure`. هذا يوضح AI/model methods، libraries، academic references، datasets، prior work، وحدود النظام.

## 6. Computer Vision Module

### هدف CV module

Computer Vision module مخصص لفحص صور سطحية أو ساحلية والبحث عن visible plastic debris مثل bottles, bags, nets, ropes, foam, caps, wrappers.

### كيف يعمل live demo

`detector.py` يعمل بطريقتين:

1. **YOLO mode:** إذا وجد `models/best.pt` وكانت مكتبة `ultralytics` مثبتة، يتم تحميل YOLO مرة واحدة عند startup وتشغيل inference على الصورة.
2. **Lightweight Detector mode:** إذا لم تتوفر weights أو فشل YOLO، يستخدم detector خفيف مبني على Pillow/NumPy وconnected components وscoring heuristics.

### الفرق بين Lightweight Detector وYOLO

YOLOv8 model-based detector يتعلم patterns من training data ويعطي bounding boxes مبنية على model inference. هذا هو المسار الأفضل للإنتاج عندما تكون weights مدربة جيدا.

Lightweight Detector ليس بديلا عن trained model. هو deployment demo محافظ يحلل edges, contrast, saturation, texture, object size, foreground location, reflection patterns. فائدته أنه يعمل في بيئات محدودة بدون GPU، لكنه قد يخطئ أكثر.

### إذا كان YOLO active

الاستجابة تحتوي `detector_mode: "yolo"`. يتم إرجاع boxes وlabels وconfidence من YOLO. يوجد أيضا COCO assist في الكود عند الحاجة للكشف عن bottle/cup إذا model المخصص لم يجد plastic، لكن يجب شرحه بحذر: هو مساعد عام وليس دليل أن model المخصص قوي في كل الحالات.

### إذا fallback mode مستخدم

الاستجابة تحتوي `detector_mode: "lightweight-cv-demo"` أو warning. يجب القول إن النظام يعمل في lightweight field/demo mode وأن النتائج تقريبية ومحافظة.

### معنى bounding boxes

Bounding box هو مستطيل حول منطقة يعتقد detector أنها تحتوي على debris. هو ليس قياسا فيزيائيا دقيقا لحجم الجسم، بل localization تقريبي داخل الصورة.

### معنى confidence

Confidence هو تقدير جودة detection. في YOLO يأتي من model confidence. في lightweight mode يأتي من scoring مبني على خصائص الصورة. لا يعني confidence أن النظام "متأكد علميا" 100%.

### لماذا image quality يؤثر

الصورة الضعيفة قد تحتوي على motion blur، darkness، low resolution، object too small، أو background clutter. هذه العوامل تجعل الفرق بين plastic وsand/rocks/waves أصعب.

### صور مناسبة للعرض

استخدم:

- زجاجة بلاستيك واضحة على الرمل.
- كيس بلاستيك واضح.
- net أو rope على الشاطئ.
- foam/plastic debris واضح.
- clean beach negative sample.

تجنب:

- صور مظلمة جدا.
- صور فيها objects صغيرة جدا أو بعيدة.
- صور بحر فقط بدون debris.
- صور مليئة بالضوضاء البصرية.

### ما لا يجب ادعاؤه

لا تقل إن live detector دائما YOLO. لا تقل إن النتائج production-grade. لا تقل إن bounding boxes مثالية. لا تقل إن النظام يستطيع كشف كل البلاستيك في كل الظروف.

## 7. Research Foundation

README و`main.py` يذكران research validation داخلي:

- Dataset: Trash-ICRA19.
- Models: YOLOv8s, Faster R-CNN, MobileNet SSD.
- Cross-domain test: River Floating Trash Dataset.
- YOLOv8s achieved 97.77% mAP@0.5 and 122.10 FPS على Trash-ICRA19.
- Faster R-CNN achieved 32.22% mAP@0.5 في River Floating Trash cross-domain test.

الدراسة تدعم فكرة أن CV detection قابل للبحث والتدريب على datasets حقيقية. لكنها منفصلة عن live lightweight demo إذا لم يكن YOLO active.

publication status: README يوضح أن paper under preparation/submission وليس منشورا publicly. لذلك لا يجوز القول "published paper".

## 8. Sonar Module

### ما هو sonar

Sonar هو sensing acoustic تحت الماء. يستخدم الصوت لأن الضوء والكاميرات لا تعمل دائما تحت الماء بسبب turbidity, depth, lighting, and visibility.

### Active Sonar

Active Sonar يرسل ping صوتي ثم يستقبل echo. من زمن رجوع الصدى يمكن تقدير range. ميزته أنه يعطي معلومات عن targets، لكن عيبه أنه يضيف acoustic energy للبيئة.

### Passive Sonar

Passive Sonar لا يرسل ping. هو listens فقط. في المشروع passive mode يحسب acoustic anomaly estimate بشكل محافظ. لا يصنف semantic target بدقة.

### Hybrid / Eco-Adaptive Sonar

Eco-Adaptive Sonar في هذا المشروع يقلل Source Level بمقدار 12 dB ويزيد Ping Interval إلى 3x. هذا يقلل Duty Cycle وSEL وEnergy Proxy، لكنه قد يقلل range أو يفوت targets ضعيفة/بعيدة.

### لماذا sonar مطلوب تحت الماء

لأن underwater debris قد لا يكون visible في صور السطح. Sonar يمكن أن يكون جزءا من sensing stack إذا تم تطوير hardware حقيقي مستقبلا.

### ماذا تفعل صفحة sonar فعليا

هي simulation executable، ليست hardware. تأخذ parameters مثل source level, frequency, pulse duration, ping interval, sea state, depth, mission duration. ثم تحسب targets افتراضية ونتائج detection لكل mode.

### معنى parameters

| Parameter | Meaning |
|---|---|
| Source Level | قوة الإرسال الصوتي، dB re 1 uPa @ 1 m. |
| Frequency | تردد السونار بالكيلو هرتز. يؤثر على absorption/noise. |
| Pulse Duration | مدة النبضة بالمللي ثانية. تدخل في SEL. |
| Ping Interval | الزمن بين pings. يؤثر على Duty Cycle وعدد pings. |
| Sea State | حالة البحر والضوضاء الناتجة عن wind/waves. |
| Depth | عمق التشغيل، يدخل في sound speed. |
| Mission Duration | مدة المهمة، تؤثر على عدد pings وcumulative SEL. |

### كيف يحسب `sonar.py`

**Sound speed:** يستخدم Mackenzie equation تقريبية عبر `sound_speed_ms`.

**Transmission Loss:** `transmission_loss_dB` يحسب two-way loss:

```text
TL = 40*log10(R) + 2*alpha*R/1000
```

حيث alpha من Thorp absorption simplified.

**Ambient Noise:** `ambient_noise_dB` يستخدم Knudsen-Wenz approximation:

```text
wind_noise = 50 - 17*log10(freq_kHz) + 5*sea_state
```

**SNR:** `snr_dB`:

```text
SNR = SL - TL + TS - NL + AG
```

**Detection Probability:** sigmoid:

```text
P(detect) = 1 / (1 + exp(-0.55*(SNR - 5)))
```

threshold في validation notes: P(detect) >= 0.50.

**Cumulative SEL:** `sel_per_ping_dB` ثم `cumulative_sel_dB`:

```text
SEL_ping = SL + 10*log10(pulse_s)
SEL_cum = SEL_ping + 10*log10(N_pings)
```

**Duty Cycle:**

```text
Duty Cycle = pulse_duration / ping_interval
```

**Energy Proxy:**

```text
Energy ∝ 10^(SL/10) * duty_cycle
```

**Detection Retention:**

```text
eco_detected / conventional_detected * 100
```

### ما تعرضه شاشة sonar

- Mission view: تمثيل بصري للsonar position وtargets.
- Target table: target type, range, depth, target strength, SNR, P(detect), echo time, estimated range, detected/missed, explanation.
- Baseline vs Eco-Adaptive: ماذا conventional detects، ماذا eco detects، وما تم توفيره.
- Trade-off: range/detection قد يقل مقابل acoustic exposure reduction.

## 9. Sustainability Explanation

تقليل active transmission مهم لأن active sonar يضيف sound energy في البيئة البحرية. كلما زادت pings أو زاد Source Level، زادت Acoustic Exposure.

تقليل Duty Cycle يعني أن النظام يرسل وقتا أقل خلال mission. هذا يقلل cumulative exposure.

تقليل SEL مهم لأنه Sound Exposure Level metric يلخص exposure عبر time وعدد pings.

Energy Proxy Reduction مفيد كمؤشر تقريبي لأن acoustic energy تتناسب مع power وduty cycle. هو ليس measurement hardware، لكنه comparison واضح بين baseline وeco mode.

Trade-off الأساسي: Eco-Adaptive mode يقلل acoustic impact، لكنه قد يقلل max range أو يفوت targets ضعيفة أو بعيدة.

هذا يحقق Challenge 3 لأنه يركز على sustainable sonar design: ليس فقط أن نكشف، بل أن نكشف بطريقة أقل disturbance.

## 10. Evidence Sheet

Evidence Sheet هو report من `/evidence`. مهم لأنه يجمع claims المدعومة في مكان واحد.

أجزاءه:

- **Problem:** لماذا marine plastic + conventional sonar issue مهم.
- **Core Function:** كيف يجمع النظام بين eco-sonar simulation وsurface detection.
- **Baseline:** Conventional active sonar parameters.
- **Improved Case:** Eco-adaptive parameters.
- **Test Conditions:** frequency, sea state, depth, mission duration, propagation/noise model.
- **Technical KPI:** Detection retention وCV research metric.
- **Sustainability KPI:** SEL reduction, duty cycle reduction, energy proxy reduction.
- **Limitation:** simulation-only وhardware validation required.
- **Repository Link:** رابط المشروع.

## 11. AI / External Resource Disclosure

Disclosure مطلوب لأن المشروع يستخدم libraries، datasets، references، وAI/model methods. يجب أن يكون واضحا ما هو من عمل الفريق وما هو external.

يجب الإفصاح عن:

- Datasets: Trash-ICRA19, River Floating Trash Dataset, synthetic demo detections.
- Libraries: FastAPI, Uvicorn, Pillow, NumPy, SQLite, Leaflet.js, Chart.js, python-multipart.
- AI/model assistance أو model methods: YOLOv8s/Faster R-CNN/MobileNet SSD research validation، sonar simulation.
- Prior work: Phase 1 concept.
- Academic references: Mackenzie, Thorp, Wenz, Urick, NOAA.

ما لا يجب إخفاؤه:

- sonar ليس hardware.
- live demo قد يكون lightweight.
- paper ليس publicly published.
- بعض dashboard values estimated.

## 12. API Explanation

### GET `/`

Purpose: يعرض الواجهة `static/index.html`.  
Input: لا يوجد.  
Output: HTML page.  
Demo value: بداية التطبيق.

### GET `/healthz`

Purpose: health check.  
Input: لا يوجد.  
Output: `{"status":"ok","service":"plastic-hunter-ai"}`.  
Demo value: إثبات أن backend يعمل.

### POST `/detect`

Purpose: رفع صورة وتشغيل detector.  
Input: image file، واختياريا latitude/longitude.  
Output: plastic_count, avg_confidence, severity, detections, annotated_image, detector_mode, warning, location.  
Demo value: Surface Inspection.

### GET `/results`

Purpose: عرض detections المخزنة.  
Input: لا يوجد.  
Output: list من سجلات SQLite.  
Demo value: Survey Log وMonitoring Map.

### GET `/stats`

Purpose: حساب dashboard/mission metrics.  
Input: لا يوجد.  
Output: total scans, total plastics, active sites, confidence distribution, severity breakdown, estimated type mix.  
Demo value: Mission Overview.

### POST `/demo`

Purpose: حذف السجلات وإعادة seed demo data.  
Input: لا يوجد.  
Output: message وعدد records.  
Demo value: إعادة الحالة الأساسية للعرض.

### GET `/results/{filename}`

Purpose: عرض annotated image من results folder.  
Input: filename فقط.  
Output: JPEG file.  
Demo value: عرض نتيجة detection.

### GET `/evidence`

Purpose: توليد Final Evidence Report data.  
Input: لا يوجد.  
Output: problem, baseline, improved case, KPIs, limitations, assumptions.  
Demo value: إثبات claims أمام الحكام.

### GET `/disclosure`

Purpose: عرض Method Disclosure.  
Input: لا يوجد.  
Output: AI/model methods, libraries, references, datasets, prior work.  
Demo value: transparency.

### POST `/sonar/ping`

Purpose: تشغيل Sonar Simulation.  
Input: source_level, frequency_kHz, pulse_ms, ping_interval_s, mission_min, sea_state, depth_m, seed.  
Output: conventional, eco_adaptive, passive, metrics, targets, range_sweep, dc_sweep, assumptions.  
Demo value: شرح Challenge 3 KPIs.

## 13. Database Explanation

SQLite مستخدم لأنه خفيف ومناسب لprototype محلي. لا يحتاج server منفصل.

`detections.db` يخزن:

- timestamp
- image_name
- plastic_count
- avg_confidence
- latitude/longitude
- severity
- processing_time_ms
- sonar_mode
- energy_reduction_pct
- acoustic_exposure_dB

الملف يتولد runtime عند تشغيل `init_db()`. إذا لم توجد سجلات، يتم seed demo data.

`results/` يخزن annotated images الناتجة عن `/detect`.

Seeded demo data تعني سجلات جاهزة للتجربة على مواقع ساحلية/مدن. هذه ليست قياسات ميدانية حقيقية، بل بيانات عرض.

## 14. Deployment and Running

### Install dependencies

```bash
pip install -r requirements.txt
```

أو minimal حسب README:

```bash
pip install fastapi uvicorn pillow numpy python-multipart
```

### Run locally

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

افتح:

```text
http://localhost:8000
```

### Run with Docker

```bash
docker build -t plastic-hunter .
docker run -p 8000:8000 plastic-hunter
```

### Check health

```bash
curl http://localhost:8000/healthz
```

### Reset demo data

```bash
curl -X POST http://localhost:8000/demo
```

### Confirm app is working

- افتح Mission Overview.
- شغل `/healthz`.
- ارفع صورة في Surface Inspection.
- افتح Monitoring Map.
- شغل Sonar Simulation.
- افتح Final Evidence Report وMethod Disclosure.

## 15. What We Completed

المكتمل حسب repository:

- Repository structure.
- README.
- Architecture description and assets.
- Screenshots in `docs/assets/screenshots`.
- FastAPI app.
- Surface inspection / image detection.
- Optional YOLO integration.
- Lightweight detector fallback.
- SQLite database.
- Monitoring map using Leaflet.
- Mission overview charts using Chart.js.
- Sonar Simulation.
- Evidence Sheet / Final Evidence Report.
- AI / External Resource Disclosure.
- Dockerfile.
- Cleanup from generic scaffold implied by project files. Exact cleanup history not confirmed in the repository.
- Research foundation documented.
- Smoke tests and validation scripts exist for YOLO/dataset; exact full CI pipeline not confirmed in the repository.

## 16. Current Limitations

- Sonar هو simulation، وليس hardware.
- لا توجد real underwater acoustic hardware data في repository.
- CV live demo قد يستخدم Lightweight Detector إذا YOLO غير active.
- لا يوجد ray tracing أو bathymetry أو multipath.
- Passive mode هو acoustic anomaly estimate وليس semantic classification.
- Demo GPS قد يكون seeded إذا لم يرسل المستخدم coordinates.
- بعض dashboard distributions estimated وليست ground-truth per-object history.
- Production يتطلب hardware validation، trained model deployment، calibration، field testing، وإجراءات regulatory/environmental.

## 17. What the Presenter Must Focus On

ركز على:

- marine sensing وليس مجرد AI dashboard.
- sonar sustainability.
- baseline vs eco-adaptive comparison.
- trade-off بين detection coverage وacoustic exposure.
- Evidence Report كطريقة لتثبيت claims.
- limitations بوضوح.

لا تركز فقط على image detection. لا تفتح الكود إلا إذا سئلت. لا تقل إن النظام production-ready. لا تقل إن sonar hardware موجود.

## 18. 5-Minute Presentation Script

### 0:00-0:40 Problem

Speaker notes:

"Marine plastic pollution is not only a surface problem. Some debris is visible on beaches and water surfaces, but some is underwater or visually hidden. Manual monitoring is slow, and cameras alone cannot cover underwater debris. Conventional active sonar can help underwater sensing, but frequent high-power pinging increases acoustic exposure. Our project focuses on a more sustainable sensing workflow."

### 0:40-1:20 Solution

Speaker notes:

"Plastic Hunter AI combines surface inspection using Computer Vision with an executable Eco-Adaptive Sonar Simulation. The image module logs visible debris, while the sonar module compares conventional, passive, and reduced-duty active modes. The goal is not to claim hardware deployment, but to demonstrate a measurable proof-of-concept for Challenge 3."

### 1:20-2:00 Architecture

Speaker notes:

"The user interacts with a browser interface. FastAPI handles the routes. The detector processes uploaded images and stores results in SQLite. The sonar engine calculates SNR, detection probability, duty cycle, SEL, and energy proxy. The interface shows map, mission overview, sonar results, and a final evidence report."

### 2:00-3:20 Sonar KPIs and sustainability

Speaker notes:

"The baseline is Conventional Active Sonar. The improved case lowers Source Level by 12 dB and increases ping interval by 3x. That reduces duty cycle and cumulative Sound Exposure Level. The technical KPI is Detection Coverage Retained. The sustainability KPI is Acoustic Exposure Reduction. The trade-off is that eco mode may reduce range or miss weak distant targets."

### 3:20-4:10 Research foundation

Speaker notes:

"The Computer Vision track is supported by internal research using real datasets. We evaluated YOLOv8s, Faster R-CNN, and MobileNet SSD on Trash-ICRA19, and used River Floating Trash Dataset for cross-domain testing. YOLOv8s reached 97.77% mAP@0.5 and 122.10 FPS in our research evaluation. The paper is under preparation or submission, not publicly published."

### 4:10-5:00 Closing

Speaker notes:

"The important point is the integrated workflow: observe visible debris, log it, map it, simulate underwater sensing trade-offs, and produce an evidence report. We are honest that sonar is simulation and production would require hardware validation. But as a Challenge 3 proof-of-concept, it demonstrates how detection and sustainability can be evaluated together."

## 19. 5-Minute Live Demo Script

### Step 1: Mission Overview

Click: Open app, stay on Mission Overview.  
Say: "This is the operations summary. It shows inspections, observed items, confidence, high-severity events, monitored sites, and sonar sustainability status."  
Do not say: "This is a fully deployed monitoring network."  
Expected result: KPI cards and charts load from `/stats`.

### Step 2: Surface Inspection

Click: Surface Inspection, choose a clear beach/plastic image, click Analyze Image.  
Say: "This runs the available detector mode and logs the result. If YOLO weights are active, the API reports YOLO. Otherwise it uses the lightweight detector."  
Do not say: "The detector is perfect" or "YOLO is always running."  
Expected result: annotated image, severity, confidence, detector mode, detections.

### Step 3: Monitoring Map

Click: Monitoring Map. Select a marker.  
Say: "The map visualizes logged inspection events. The side panel shows severity, count, confidence, coordinates, and image name."  
Do not say: "These are all real field GPS measurements."  
Expected result: markers and selected detection panel.

### Step 4: Sonar Simulation

Click: Sonar Simulation, choose preset, click Start Sonar Simulation.  
Say: "This is an engineering simulation. It compares Conventional, Eco-Adaptive, and Passive modes using assumptions shown in the report."  
Do not say: "This is real sonar hardware."  
Expected result: target table, mission view, KPIs, trade-off.

### Step 5: Final Evidence Report

Click: Final Evidence Report.  
Say: "This is the judge-facing summary: baseline, improved case, test conditions, KPIs, limitations, and assumptions."  
Do not say: "This proves field performance."  
Expected result: modal with structured evidence.

### Step 6: Method Disclosure

Click: Method Disclosure.  
Say: "This shows libraries, datasets, references, prior work, and the fact that sonar is simulation."  
Do not say: "We hide external tools."  
Expected result: disclosure modal.

## 20. Expected Judge Questions and Answers

1. **Is the sonar real?**  
No. It is an executable Sonar Simulation based on mathematical assumptions, not hardware.

2. **Why use simulation?**  
Because the hackathon proof-of-concept can show equations, KPIs, and trade-offs before expensive sea trials.

3. **Why not hardware?**  
Hardware requires calibrated sonar devices, permits, field testing, and acoustic validation. Not confirmed in the repository.

4. **Does YOLO run in the live demo?**  
Only if `models/best.pt` exists and `ultralytics` loads successfully. Otherwise the app uses Lightweight Detector.

5. **What is the difference between CV and sonar?**  
CV analyzes visible images. Sonar estimates underwater acoustic detection behavior.

6. **Why hybrid sonar?**  
To balance detection with lower acoustic exposure.

7. **What is SEL?**  
Sound Exposure Level. It summarizes acoustic exposure over pulse duration and number of pings.

8. **What is Duty Cycle?**  
The fraction of mission time spent actively transmitting.

9. **How is reduction calculated?**  
By comparing conventional cumulative SEL and duty cycle against eco-adaptive settings.

10. **What is the trade-off?**  
Eco mode reduces acoustic exposure but may reduce range or miss weak/distant targets.

11. **What dataset did you use?**  
Documentation cites Trash-ICRA19 and River Floating Trash Dataset.

12. **Is the research published?**  
No public publication is confirmed. README says under preparation/submission.

13. **What are main limitations?**  
Simulation-only sonar, no hardware validation, lightweight detector possible, no ray tracing/bathymetry/multipath.

14. **How would this become real hardware?**  
Integrate calibrated sonar, collect measured target strengths, run sea trials, validate model assumptions, add compliance review.

15. **Why is it sustainable?**  
It explicitly reduces active transmission, duty cycle, SEL, and energy proxy.

16. **What happens in high noise?**  
Ambient noise rises, SNR decreases, detection probability may drop.

17. **What if image is unclear?**  
Confidence may drop or detection may fail. The app can return low-confidence warnings.

18. **How reliable is the detector?**  
YOLO reliability depends on trained weights. Lightweight mode is conservative and not production-grade.

19. **What is SQLite for?**  
It stores inspection records for map, history, and stats.

20. **What does Evidence Sheet prove?**  
It organizes assumptions, calculations, baseline/improved case, and limitations. It does not prove field hardware performance.

21. **Why use FastAPI?**  
It provides simple, documented HTTP endpoints for upload, sonar simulation, stats, evidence, and disclosure.

22. **Why use Leaflet?**  
For interactive geospatial display of stored detections.

23. **Why use Chart.js?**  
For dashboard charts in the browser.

24. **What is Source Level?**  
The transmitted acoustic level at 1 m.

25. **What is SNR?**  
Signal-to-Noise Ratio after accounting for source level, transmission loss, target strength, and noise.

26. **What is Detection Probability?**  
A sigmoid approximation from SNR to probability of detection.

27. **What is Target Strength?**  
An assumed reflectivity of target classes such as ghost net or plastic drum.

28. **Are target strengths measured?**  
Repository says representative engineering assumptions, not measured object-specific values.

29. **Does passive mode classify debris?**  
No. It is a conservative acoustic-anomaly estimate.

30. **Why no ray tracing?**  
This is a simplified proof-of-concept. Ray tracing requires bathymetry/environmental data.

31. **Are GPS points real field measurements?**  
Some demo coordinates are seeded. Uploaded detections may use supplied coordinates or random coastal locations.

32. **What is `results/`?**  
Folder for annotated images generated by detections.

33. **What is `detections.db`?**  
Runtime SQLite database storing detection records.

34. **Can the system run without YOLO?**  
Yes. It falls back to lightweight detector.

35. **Can it run with YOLO?**  
Yes, if weights and dependencies are available.

36. **Why use COCO assist?**  
The code can map generic bottle/cup detections as an assist when custom plastic YOLO finds no plastic. It should be explained as support, not as perfect marine model.

37. **What is the primary technical KPI?**  
Detection Coverage Retained.

38. **What is the primary sustainability KPI?**  
Acoustic Exposure Reduction.

39. **Is the app production-ready?**  
No. It is a hackathon prototype/proof-of-concept.

40. **What should judges take away?**  
The project shows a measurable sustainable sensing workflow, not just a visual dashboard.

41. **Why include disclosure?**  
For transparency about datasets, libraries, methods, references, and limitations.

42. **Can the model detect all plastic?**  
No. Performance depends on data, visibility, object size, lighting, and detector mode.

43. **What does confidence mean?**  
A detection quality estimate, not a guarantee.

44. **Why keep limitations visible?**  
Because honest engineering scope is stronger than overclaiming.

## 21. Dangerous Things Not to Say

| Do not say | Correct wording |
|---|---|
| "This is real sonar hardware." | "This is an executable sonar simulation based on mathematical assumptions." |
| "We tested it in the ocean." | "No real sea trial is confirmed in the repository." |
| "The live demo is always YOLO." | "YOLO runs only when weights and dependencies are available; otherwise fallback is used." |
| "The research is published." | "The paper is under preparation/submission; public publication is not confirmed." |
| "The system is production-ready." | "This is a proof-of-concept requiring hardware validation and deployment hardening." |
| "The model is perfect." | "Detection depends on image quality, training data, and detector mode." |
| "Passive sonar identifies plastic types." | "Passive mode is a conservative acoustic-anomaly estimate." |
| "The map shows verified field measurements." | "The map shows stored inspection records; demo data may be seeded." |
| "SEL reduction proves environmental impact reduction in the ocean." | "SEL reduction is a simulation KPI; real environmental impact requires field validation." |
| "Dashboard type mix is ground truth." | "Historical type mix is estimated for rows that store only counts." |

## 22. One-Page Cheat Sheet

**One-sentence summary:** Plastic Hunter AI is a marine monitoring proof-of-concept combining surface Computer Vision inspection with Eco-Adaptive Sonar Simulation to compare detection coverage and acoustic sustainability.

**Main problem:** Marine plastic exists on the surface and underwater; manual monitoring is limited, cameras cannot see everything, and conventional active sonar can increase acoustic exposure.

**Main solution:** A FastAPI web application that logs image detections, maps them, simulates sonar trade-offs, and generates a final evidence report.

**Core technical KPI:** Detection Coverage Retained.

**Core sustainability KPI:** Acoustic Exposure Reduction, including SEL reduction and duty cycle reduction.

**Main limitation:** Sonar is simulation only, not hardware; CV live mode may be lightweight unless YOLO is active.

**Best closing sentence:** "Our contribution is not claiming a finished ocean deployment; it is a transparent, executable proof-of-concept showing how marine detection performance and sonar sustainability can be evaluated together."
