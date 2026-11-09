#!/usr/bin/env python3
# One-line purpose: load the Aster demo project (upload path, consent logged) and stop before the gates.
# The judge then walks Connect → Rebuild → Review → Sign → Handover, exactly as the four-minute path describes.
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from backend.app.db import read_path as db
from backend.app.pipeline.seed_demo import load_demo_project

if __name__ == "__main__":
    db.init_db()
    existing = [p for p in db.list_projects() if p["name"].startswith("Aster")]
    if existing:
        print(f"Aster project already loaded: {existing[0]['id']} (state {existing[0]['state']})")
        print("To start fresh: rm tether.db && make seed")
        sys.exit(0)
    project = load_demo_project(name=None, role="reviewer")
    print(f"Demo project loaded: {project['id']}")
    print(f"  name:  {project['name']}")
    print(f"  state: {project['state']}  (labels not yet cleared — that is the first gate)")
    print(f"  next:  open http://localhost:8000  as the reviewer (Sanit) and press 'Clear labels' on the Connect screen")
    print("  or run the scripted four-minute path: ./scripts/judge_walkthrough.sh")
