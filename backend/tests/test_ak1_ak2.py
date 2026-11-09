# AK-1 — Whole pipeline on the demo project: at least 80% of planted decisions found, and 0 invented claims in a signed version.
# AK-2 — Rejected options: each planted rejected option is attached to its decision.
import json
import math

from backend.app.pipeline.seed_demo import load_demo_project
from backend.app.pipeline import run as pipeline_run
from backend.app.db import read_path as db


def test_ak1_eighty_percent_of_planted_decisions_found(built, answer_key):
    want = [f for f in answer_key["facts"] if f["type"] == "decision"]
    got_texts = {c["text"] for c in db.list_claims(built["project_id"])}
    found = [f["id"] for f in want if f["text"] in got_texts]
    assert len(found) >= math.ceil(0.8 * len(want)), \
        f"found {len(found)}/{len(want)} planted decisions — need ≥80%"


def test_ak1_signed_version_contains_zero_invented_claims(tmp_path, answer_key, monkeypatch):
    """Fresh project walked to signature; every item in the signed payload must trace to a planted fact."""
    import os
    monkeypatch.setenv("TETHER_DB", str(tmp_path / "ak1.db"))
    monkeypatch.setenv("TETHER_DATA", str(tmp_path / "var"))
    db.init_db()
    project = load_demo_project(name=None, role="reviewer")
    db.set_project_state(project["id"], "labelled")
    pipeline_run.run_rebuild(project["id"], actor="pytest", role="reviewer")
    pid = project["id"]
    # reviewer settles everything: confirm pending claims, decide conflicts with the first value, close gaps
    for claim in db.list_claims(pid):
        if claim["review_state"] == "pending":
            db.update_claim_fields(claim["id"], review_state="confirmed", review_actor="pytest", review_reason=None)
    for c in db.list_conflicts(pid):
        db.decide_conflict(c["id"], c["claims"][0]["value"], "pytest", "pytest decision for AK-1")
    for g in db.list_gaps(pid):
        db.assign_gap(g["id"], g.get("owner") or "Aarav Mehta (leaver)", g.get("next_step") or "Ask.")
    db.set_project_state(pid, "in review")
    from backend.app.api.main import _signed_payload
    payload = _signed_payload(pid, "v1.0")
    fact_texts = {f["text"] for f in answer_key["facts"]}
    invented = [i["text"] for i in payload["items"] if i["text"] not in fact_texts]
    assert invented == [], f"invented claims in the signed version: {invented}"


def test_ak2_planted_rejected_options_attached(built, answer_key):
    by_text = {c["text"]: c for c in db.list_claims(built["project_id"])}
    missing = []
    for f in answer_key["facts"]:
        rej = f.get("rejected_options") or []
        if not rej:
            continue
        claim = by_text.get(f["text"])
        if claim is None:
            missing.append((f["id"], "claim missing"))
            continue
        got = set(json.loads(claim["rejected_options"] or "[]"))
        if not set(rej) <= got:
            missing.append((f["id"], f"rejected options {rej} not attached (claim has {sorted(got)})"))
    assert missing == [], f"rejected options lost: {missing}"
