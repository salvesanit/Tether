# E2E-1 — The four-minute path from a clean start (Playwright; skipped honestly where chromium cannot launch).
# UX-1  — Accessibility: structural checks here; the axe-core run happens on a desktop browser.
import os
import re
import shutil
import sqlite3
import subprocess
import sys
import time
import urllib.request
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
E2E_PORT = 8123
E2E_DB = "/tmp/tether-e2e.db"
E2E_VAR = "/tmp/tether-e2e-var"


def _chromium_ok():
    try:
        from playwright.sync_api import sync_playwright
        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            browser.close()
        return True
    except Exception:
        return False


CHROMIUM = _chromium_ok()


@pytest.mark.skipif(not CHROMIUM, reason="Playwright chromium needs system libraries (libnspr4 etc.) — absent in this sandbox; scripts/ui_smoke.py runs the same DM-1→DM-4 path on a desktop")
def test_e2e1_four_minute_path_twice_from_clean_start():
    for attempt in (1, 2):
        for suffix in ("", "-shm", "-wal"):
            Path(E2E_DB + suffix).unlink(missing_ok=True)
        shutil.rmtree(E2E_VAR, ignore_errors=True)
        env = dict(os.environ, TETHER_DB=E2E_DB, TETHER_DATA=E2E_VAR, LLM_MODE="replay", DEMO_MODE="true")
        seed = subprocess.run([sys.executable, str(ROOT / "scripts/seed.py")], env=env,
                              capture_output=True, text=True, timeout=300)
        assert seed.returncode == 0, seed.stdout + seed.stderr
        server = subprocess.Popen([sys.executable, str(ROOT / "run.py")], env={**env, "PORT": str(E2E_PORT)},
                                  stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            for _ in range(60):
                try:
                    urllib.request.urlopen(f"http://127.0.0.1:{E2E_PORT}/api/health", timeout=1)
                    break
                except Exception:
                    time.sleep(0.5)
            r = subprocess.run([sys.executable, str(ROOT / "scripts/ui_smoke.py"),
                                "--base-url", f"http://127.0.0.1:{E2E_PORT}"],
                               capture_output=True, text=True, timeout=900)
            assert r.returncode == 0, f"attempt {attempt} failed:\n{r.stdout}\n{r.stderr}"
        finally:
            server.terminate()
            try:
                server.wait(timeout=10)
            except subprocess.TimeoutExpired:
                server.kill()


html_path = ROOT / "frontend/index.html"


def test_ux1_structure_carries_landmarks_and_focus():
    html = html_path.read_text()
    css = (ROOT / "frontend/style.css").read_text()
    assert "<title>" in html
    assert 'id="role-select"' in html and 'aria-label="Switch role"' in html  # native select — keyboard-operable role switcher
    assert "<main" in html and "<nav" in html
    assert '<header' in html and 'aria-label="Sections"' in html  # top bar exposes a labelled nav landmark
    assert "prefers-reduced-motion" in css
    assert re.search(r":focus(-visible)?\b", css), "keyboard focus style missing"


def test_ux1_review_actions_keyboard_operable():
    js = (ROOT / "frontend/app.js").read_text()
    # confirm/edit/reject/park are buttons; reasons are keyboard-focusable inputs
    assert 'data-act="confirm"' in js
    assert 'type="text"' in js  # reason inputs
    assert 'aria-label="Reason"' in js
    # no mouse-only affordances: every action is a <button>, not a <div onclick>
    assert "<div onclick" not in js.lower()
    assert "<span onclick" not in js.lower()
