# SW-1 — One source switched off: run without the chat export. The gaps still appear.
import json
import pathlib
import tempfile

import pytest

from backend.app.db import read_path as db
from backend.app.pipeline.seed_demo import DEMO_DIR
from backend.app.pipeline import run as pipeline_run
from backend.app.storage import save_upload


def test_sw1_without_chat_export_gaps_still_appear(tmp_path, monkeypatch, answer_key):
    monkeypatch.setenv("TETHER_DB", str(tmp_path / "sw1.db"))
    monkeypatch.setenv("TETHER_DATA", str(tmp_path / "var"))
    db.init_db()

    manifest = json.loads((DEMO_DIR / "manifest.json").read_text())
    project = db.create_project("Aster — sans chat", "Aster")
    db.seed_users(project["id"])
    for s in manifest["sources"]:
        if s["kind"] == "chat":
            continue  # the switched-off source: never uploaded
        path = DEMO_DIR / s["path"]
        data = path.read_bytes()
        display_name = s["path"] if s["kind"] == "notes" else path.name
        src = db.create_source(project["id"], s["kind"], display_name, s["label"], "pending",
                               s.get("sha256", ""), excluded_channels=s.get("excluded_channels", []))
        save_upload(src["id"], path.name, data)
    db.set_project_state(project["id"], "labelled")
    result = pipeline_run.run_rebuild(project["id"], actor="pytest", role="reviewer")

    open_subjects = {g["subject"] for g in db.list_gaps(project["id"]) if g["state"] == "open"}
    missing = set(answer_key["gaps"]["missing"])
    assert missing <= open_subjects, f"gaps lost without chat export: {sorted(missing - open_subjects)}"
    stored = db.list_sources(project["id"])
    assert not any(s["kind"] == "chat" for s in stored)
    report_note = "run without the chat export — 11 of 61 planted facts live in chat and are absent; the report must name chat.json"
    print(report_note)
