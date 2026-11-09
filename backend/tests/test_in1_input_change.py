# IN-1 — Change the input: a planted sentence that matches a rules pattern is edited; the claim shows the new text,
# the quote resolves against the new bytes, and the run says extractor: rules for that chunk.
import json
import pathlib

from backend.app.db import read_path as db
from backend.app.pipeline import run as pipeline_run
from backend.app.storage import save_upload


def test_in1_edited_rules_sentence_is_picked_up(tmp_path, monkeypatch):
    monkeypatch.setenv("TETHER_DB", str(tmp_path / "in1.db"))
    monkeypatch.setenv("TETHER_DATA", str(tmp_path / "var"))
    db.init_db()

    root = pathlib.Path(__file__).resolve().parents[2]
    original = (root / "data/demo_project/notes/2026-08-12.md").read_text()
    assert "We deploy on Fridays after 6pm." in original
    edited = original.replace("We deploy on Fridays after 6pm.", "We deploy on Mondays after 6pm.")

    project = db.create_project("IN-1 — edited deploy note", "Aster")
    db.seed_users(project["id"])
    src = db.create_source(project["id"], "notes", "notes/2026-08-12.md", "internal", "pending", "")
    save_upload(src["id"], "2026-08-12.md", edited.encode())
    db.set_project_state(project["id"], "labelled")
    result = pipeline_run.run_rebuild(project["id"], actor="pytest", role="reviewer")

    deploy = [c for c in db.list_claims(project["id"])
              if (c.get("subject") or "").lower() == "deploy" and (c.get("attribute") or "").lower() == "day"]
    assert deploy, "the deploy-day claim vanished after a one-word edit"
    assert all("Monday" in str(c.get("value")) for c in deploy), [c["value"] for c in deploy]
    assert result["counts"]["extractor_chunks"]["rules"] >= 1, "changed chunk should fall back to the rules extractor"
    for c in deploy:
        for e in db.list_evidence(c["id"]):
            span = db.get_span(e["span_id"])
            assert span is not None and e["quote"] in span["text"], "quote does not resolve after the edit"
    assert any("Monday" in str(c.get("value")) for c in deploy)
