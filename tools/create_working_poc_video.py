"""
Create the Plastic Hunter AI working proof of concept video.

Output:
  Plastic_Hunter_AI_Working_Proof_of_Concept.mp4

Regenerate:
  py tools/create_working_poc_video.py

Dependencies used:
  - Python: pillow, opencv-python
  - Node temporary dependency: playwright-core, installed under the OS temp dir
  - Browser: local Google Chrome or Microsoft Edge
"""

from __future__ import annotations

from pathlib import Path

import create_live_demo_video as demo_video


ROOT = Path(__file__).resolve().parents[1]

demo_video.VIDEO_PATH = ROOT / "Plastic_Hunter_AI_Working_Proof_of_Concept.mp4"
demo_video.WORK_DIR = ROOT / "demo" / "working_poc_video"
demo_video.FRAME_DIR = demo_video.WORK_DIR / "browser_frames"
demo_video.RENDER_DIR = demo_video.WORK_DIR / "rendered_frames"
demo_video.CAPTURE_JS = demo_video.WORK_DIR / "capture_demo_frames.js"
demo_video.SECONDS_PER_CAPTION = 9

demo_video.CAPTIONS = [
    "Plastic Hunter AI - Working Proof of Concept",
    "Software proof of concept - not deployed hardware",
    "The system combines Computer Vision detection with Eco-Adaptive Sonar Simulation",
    "Step 1: Open the monitoring dashboard",
    "Step 2: Upload a marine or beach image",
    "Step 3: Detect visible plastic using Computer Vision",
    "Detection result is annotated and stored as a monitoring record",
    "Step 4: View detection records on the map",
    "Step 5: Review dashboard and monitoring records",
    "Step 6: Run sonar simulation",
    "Conventional vs Passive vs Eco-Adaptive sonar modes",
    "SEL reduction: 97.9%",
    "Duty-cycle cut: 66.7%",
    "Detection retention: 50.0% in this simulated scenario",
    "Step 7: Open judge-ready evidence report",
    "Evidence includes baseline, improved case, test conditions, KPIs, assumptions, and limitations",
    "Future work: hardware validation and real marine testing",
]

demo_video.CAPTION_TO_SCREEN = [
    "dashboard.png",
    "dashboard.png",
    "workflow.png",
    "dashboard.png",
    "upload.png",
    "detection_result.png",
    "detection_result.png",
    "map.png",
    "history.png",
    "sonar_start.png",
    "sonar_result.png",
    "sonar_result.png",
    "sonar_result.png",
    "sonar_result.png",
    "evidence.png",
    "evidence.png",
    "limitations.png",
]


if __name__ == "__main__":
    demo_video.main()
