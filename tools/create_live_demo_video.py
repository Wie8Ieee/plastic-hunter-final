"""
Create the Plastic Hunter AI live demo backup video.

Output:
  Plastic_Hunter_AI_Live_Demo_Backup.mp4

Regenerate:
  py tools/create_live_demo_video.py

Dependencies used:
  - Python: pillow, opencv-python
  - Node temporary dependency: playwright-core, installed under the OS temp dir
  - Browser: local Google Chrome
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


ROOT = Path(__file__).resolve().parents[1]
BASE_URL = "http://127.0.0.1:8000"
VIDEO_PATH = ROOT / "Plastic_Hunter_AI_Live_Demo_Backup.mp4"
WORK_DIR = ROOT / "demo" / "live_demo_video"
FRAME_DIR = WORK_DIR / "browser_frames"
RENDER_DIR = WORK_DIR / "rendered_frames"
CAPTURE_JS = WORK_DIR / "capture_demo_frames.js"
SAMPLE_IMAGE = ROOT / "sample_images" / "marine_dataset_demo" / "01_marine_plastic_bottle.jpg"

WIDTH = 1920
HEIGHT = 1080
FPS = 24
SECONDS_PER_CAPTION = 8
TRANSITION_FRAMES = 12

CAPTIONS = [
    "Plastic Hunter AI - Live Demo Backup",
    "Software proof of concept - not deployed hardware",
    "Marine plastic monitoring using Computer Vision and Eco-Adaptive Sonar Simulation",
    "Step 1: Open the monitoring dashboard",
    "The dashboard shows the monitoring workflow from detection to evidence",
    "Step 2: Upload a marine or beach image",
    "Step 3: Detect visible plastic using Computer Vision",
    "Detection result is annotated and stored as a monitoring record",
    "Step 4: View detection records on the map",
    "The map helps make inspection records spatially interpretable",
    "Step 5: Run sonar simulation",
    "Conventional vs Passive vs Eco-Adaptive sonar modes",
    "Baseline: 200 dB SL, 5 s ping interval, 2% duty cycle",
    "Eco-adaptive: 188 dB SL, 15 s ping interval, 0.67% duty cycle",
    "SEL reduction: 97.9%",
    "Duty-cycle cut: 66.7%",
    "Detection retention: 50.0% in this simulated scenario",
    "This is an intentional sustainability trade-off: lower acoustic exposure with reduced range",
    "Step 6: Open judge-ready evidence report",
    "Evidence includes baseline, improved case, test conditions, KPIs, assumptions, and limitations",
    "Future work: hardware validation and real marine deployment testing",
]

CAPTION_TO_SCREEN = [
    "dashboard.png",
    "dashboard.png",
    "dashboard.png",
    "dashboard.png",
    "workflow.png",
    "upload.png",
    "detection_result.png",
    "detection_result.png",
    "map.png",
    "map.png",
    "sonar_start.png",
    "sonar_result.png",
    "sonar_result.png",
    "sonar_result.png",
    "sonar_result.png",
    "sonar_result.png",
    "sonar_result.png",
    "sonar_result.png",
    "evidence.png",
    "evidence.png",
    "limitations.png",
]


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    subprocess.run(cmd, cwd=str(cwd or ROOT), env=env, check=True)


def health_ok() -> bool:
    try:
        with urllib.request.urlopen(f"{BASE_URL}/healthz", timeout=2) as response:
            return response.status == 200
    except (urllib.error.URLError, TimeoutError):
        return False


def start_server_if_needed() -> subprocess.Popen[str] | None:
    if health_ok():
        print("FastAPI server already running.")
        return None

    print("Starting FastAPI server...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "uvicorn", "main:app", "--host", "127.0.0.1", "--port", "8000"],
        cwd=str(ROOT),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    for _ in range(45):
        if health_ok():
            print("FastAPI server is ready.")
            return proc
        if proc.poll() is not None:
            output = proc.stdout.read() if proc.stdout else ""
            raise RuntimeError(f"FastAPI server exited early:\n{output}")
        time.sleep(1)
    raise RuntimeError("Timed out waiting for FastAPI server.")


def chrome_path() -> Path:
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google" / "Chrome" / "Application" / "chrome.exe",
    ]
    for path in candidates:
        if path.exists():
            return path
    found = shutil.which("chrome") or shutil.which("chrome.exe") or shutil.which("msedge") or shutil.which("msedge.exe")
    if found:
        return Path(found)
    raise RuntimeError("Chrome or Edge was not found.")


def ensure_playwright_core() -> Path:
    node_root = Path(tempfile.gettempdir()) / "plastic-hunter-shot-node"
    package_json = node_root / "node_modules" / "playwright-core" / "package.json"
    if package_json.exists():
        return node_root / "node_modules"

    node_root.mkdir(parents=True, exist_ok=True)
    print("Installing temporary Node dependency: playwright-core")
    run(["npm", "init", "-y"], cwd=node_root)
    run(["npm", "install", "playwright-core"], cwd=node_root)
    if not package_json.exists():
        raise RuntimeError("playwright-core installation did not complete.")
    return node_root / "node_modules"


def write_capture_script(node_modules: Path, chrome: Path) -> None:
    sample = str(SAMPLE_IMAGE).replace("\\", "\\\\")
    frame_dir = str(FRAME_DIR).replace("\\", "\\\\")
    chrome_str = str(chrome).replace("\\", "\\\\")
    js = f"""
const {{ chromium }} = require('playwright-core');
const fs = require('fs');
const path = require('path');

const base = {json.dumps(BASE_URL)};
const sample = "{sample}";
const frameDir = "{frame_dir}";
const chromePath = "{chrome_str}";

async function tab(page, id) {{
  await page.evaluate((sectionId) => {{
    const btn = [...document.querySelectorAll('.nav-tab')]
      .find((b) => b.getAttribute('onclick')?.includes(`'${{sectionId}}'`));
    btn?.click();
  }}, id);
  await page.waitForTimeout(1200);
}}

async function shot(page, name) {{
  await page.screenshot({{ path: path.join(frameDir, name), fullPage: false }});
  console.log('captured', name);
}}

(async () => {{
  fs.mkdirSync(frameDir, {{ recursive: true }});
  const browser = await chromium.launch({{ executablePath: chromePath, headless: true }});
  const page = await browser.newPage({{ viewport: {{ width: 1920, height: 1080 }}, deviceScaleFactor: 1 }});
  page.setDefaultTimeout(20000);
  await page.goto(base, {{ waitUntil: 'domcontentloaded' }});
  await page.waitForTimeout(1500);

  await tab(page, 'dashboard');
  await shot(page, 'dashboard.png');

  await page.evaluate(() => window.scrollTo(0, 0));
  await shot(page, 'workflow.png');

  await tab(page, 'detect');
  await shot(page, 'upload.png');
  await page.setInputFiles('#fileInput', sample);
  await page.waitForTimeout(1200);
  await page.click('#detectBtn');
  await page.waitForFunction(() => {{
    const el = document.querySelector('#resultContent');
    return el && getComputedStyle(el).display !== 'none';
  }}, null, {{ timeout: 30000 }});
  await page.waitForTimeout(1200);
  await shot(page, 'detection_result.png');

  await tab(page, 'map');
  await page.waitForTimeout(2200);
  await shot(page, 'map.png');

  await tab(page, 'history');
  await page.waitForTimeout(1000);
  await shot(page, 'history.png');

  await tab(page, 'sonar');
  await page.waitForTimeout(1000);
  await shot(page, 'sonar_start.png');
  await page.click('#sonarRunBtn');
  await page.waitForTimeout(3500);
  await shot(page, 'sonar_result.png');

  await tab(page, 'dashboard');
  await page.evaluate(() => window.showEvidenceModal && window.showEvidenceModal());
  await page.waitForTimeout(2200);
  await shot(page, 'evidence.png');

  await page.evaluate(() => {{
    const modal = document.querySelector('#evidenceModal .modal-box');
    if (modal) modal.scrollTop = modal.scrollHeight;
  }});
  await page.waitForTimeout(800);
  await shot(page, 'limitations.png');

  await browser.close();
}})().catch((error) => {{
  console.error(error);
  process.exit(1);
}});
"""
    WORK_DIR.mkdir(parents=True, exist_ok=True)
    CAPTURE_JS.write_text(js, encoding="utf-8")


def capture_browser_frames() -> None:
    if not SAMPLE_IMAGE.exists():
        raise RuntimeError(f"Sample image not found: {SAMPLE_IMAGE}")
    FRAME_DIR.mkdir(parents=True, exist_ok=True)
    node_modules = ensure_playwright_core()
    write_capture_script(node_modules, chrome_path())
    env = os.environ.copy()
    env["NODE_PATH"] = str(node_modules)
    run(["node", str(CAPTURE_JS)], cwd=ROOT, env=env)


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("arialbd.ttf" if bold else "arial.ttf"),
        Path(os.environ.get("WINDIR", "C:/Windows")) / "Fonts" / ("segoeuib.ttf" if bold else "segoeui.ttf"),
    ]
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def wrap_text(text: str, draw: ImageDraw.ImageDraw, fnt: ImageFont.ImageFont, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        test = f"{current} {word}".strip()
        if draw.textbbox((0, 0), test, font=fnt)[2] <= max_width:
            current = test
        else:
            if current:
                lines.append(current)
            current = word
    if current:
        lines.append(current)
    return lines


def fit_image_to_canvas(source: Image.Image) -> Image.Image:
    canvas = Image.new("RGB", (WIDTH, HEIGHT), "#f4f1ea")
    max_w = WIDTH
    max_h = HEIGHT - 170
    scale = min(max_w / source.width, max_h / source.height)
    new_size = (int(source.width * scale), int(source.height * scale))
    resized = source.resize(new_size, Image.Resampling.LANCZOS)
    x = (WIDTH - new_size[0]) // 2
    y = 28
    canvas.paste(resized, (x, y))
    return canvas


def add_caption(frame: Image.Image, caption: str, step_index: int, total_steps: int) -> Image.Image:
    frame = frame.convert("RGBA")
    overlay = Image.new("RGBA", frame.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    title_font = font(34, bold=True)
    body_font = font(39, bold=True)
    small_font = font(22)

    lines = wrap_text(caption, draw, body_font, WIDTH - 300)
    line_h = 48
    box_h = 58 + len(lines) * line_h
    box_y = HEIGHT - box_h - 34
    box_x = 120
    box_w = WIDTH - 240

    draw.rounded_rectangle((box_x, box_y, box_x + box_w, box_y + box_h), radius=24, fill=(10, 24, 38, 218))
    draw.text((box_x + 34, box_y + 18), "Plastic Hunter AI live demo", font=title_font, fill=(200, 245, 244, 255))
    draw.text((box_x + box_w - 145, box_y + 24), f"{step_index}/{total_steps}", font=small_font, fill=(210, 220, 226, 255))
    y = box_y + 64
    for line in lines:
        draw.text((box_x + 34, y), line, font=body_font, fill=(255, 255, 255, 255))
        y += line_h

    return Image.alpha_composite(frame, overlay).convert("RGB")


def render_caption_frames() -> list[Path]:
    RENDER_DIR.mkdir(parents=True, exist_ok=True)
    rendered: list[Path] = []
    total = len(CAPTIONS)
    for idx, (caption, source_name) in enumerate(zip(CAPTIONS, CAPTION_TO_SCREEN), start=1):
        source_path = FRAME_DIR / source_name
        if not source_path.exists():
            raise RuntimeError(f"Missing captured frame: {source_path}")
        source = Image.open(source_path).convert("RGB")
        frame = fit_image_to_canvas(source)
        frame = add_caption(frame, caption, idx, total)
        out = RENDER_DIR / f"caption_{idx:02d}.png"
        frame.save(out)
        rendered.append(out)
    return rendered


def write_video(rendered_frames: list[Path]) -> None:
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(str(VIDEO_PATH), fourcc, FPS, (WIDTH, HEIGHT))
    if not writer.isOpened():
        raise RuntimeError("Could not open MP4 writer.")

    previous = None
    frames_per_caption = SECONDS_PER_CAPTION * FPS
    hold_frames = frames_per_caption - TRANSITION_FRAMES

    for path in rendered_frames:
        image_rgb = Image.open(path).convert("RGB")
        image = cv2.cvtColor(np.array(image_rgb), cv2.COLOR_RGB2BGR)
        if previous is not None:
            for t in range(TRANSITION_FRAMES):
                alpha = (t + 1) / TRANSITION_FRAMES
                mixed = cv2.addWeighted(previous, 1 - alpha, image, alpha, 0)
                writer.write(mixed)
        for _ in range(hold_frames):
            writer.write(image)
        previous = image

    writer.release()
    if not VIDEO_PATH.exists() or VIDEO_PATH.stat().st_size == 0:
        raise RuntimeError("MP4 was not created.")


def main() -> None:
    server_proc = None
    try:
        server_proc = start_server_if_needed()
        capture_browser_frames()
        rendered = render_caption_frames()
        write_video(rendered)
        duration = len(CAPTIONS) * SECONDS_PER_CAPTION
        print(f"Created: {VIDEO_PATH.name}")
        print(f"Duration: {duration} seconds")
        print("Method: browser screenshot compilation with OpenCV MP4 rendering")
    finally:
        if server_proc is not None:
            server_proc.terminate()
            try:
                server_proc.wait(timeout=8)
            except subprocess.TimeoutExpired:
                server_proc.kill()


if __name__ == "__main__":
    main()
