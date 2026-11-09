# Pytest scaffold: one scratch TETHER_DB built once per session, seeded through the upload path.
import os
import sys
import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

_WORK = Path(tempfile.mkdtemp(prefix="tether-tests-"))
os.environ["TETHER_DB"] = str(_WORK / "test.db")
os.environ["TETHER_DATA"] = str(_WORK / "var")
os.environ["LLM_MODE"] = "replay"

import pytest


@pytest.fixture(scope="session")
def answer_key():
    return json.loads((ROOT / "data/demo_project/answer_key.json").read_text())


@pytest.fixture(scope="session")
def built():
    """The demo project, seeded, label gate cleared, rebuilt — the shared fixture behind most checks."""
    from backend.app.db import read_path as db
    from backend.app.pipeline.seed_demo import load_demo_project
    from backend.app.pipeline import run as pipeline_run

    db.init_db()
    project = load_demo_project(name=None, role="reviewer")
    db.set_project_state(project["id"], "labelled")
    result = pipeline_run.run_rebuild(project["id"], actor="pytest", role="reviewer")
    return {"db": db, "project_id": project["id"], "result": result,
            "counts": result["counts"]}


@pytest.fixture(scope="session")
def spans_by_locator(built):
    db = built["db"]
    return {s["locator"]: s for s in db.list_spans(built["project_id"])}


@pytest.fixture()
def client():
    from fastapi.testclient import TestClient
    from backend.app.api.main import app
    return TestClient(app, raise_server_exceptions=False)
