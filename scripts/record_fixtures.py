#!/usr/bin/env python3
# One-line purpose: build fixtures/llm/ replay recordings — either from the answer key (handwritten-reference, default)
# or by recording a live model run (provenance "model", needs LLM_API_KEY/LLM_URL/LLM_MODEL).
# Replay fixtures replace ONLY the model call. Every check, gate and plumbing path stays live either way.
import argparse
import hashlib
import json
import os
import re
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def build_reference(args):
    work = Path(tempfile.mkdtemp(prefix="tether-fixture-gen-"))
    os.environ["TETHER_DB"] = str(work / "gen.db")
    os.environ["TETHER_DATA"] = str(work / "var")
    os.environ["LLM_MODE"] = "rules"  # capture raw spans; proposals from rules are discarded here

    from backend.app.db import read_path as db
    from backend.app.pipeline.seed_demo import load_demo_project
    from backend.app.pipeline import run as pipeline_run
    from backend.app.llm import adapter

    db.init_db()
    project = load_demo_project(name=None, role="reviewer")
    db.set_project_state(project["id"], "labelled")  # fixture generation jumps the gate; the claims themselves are still check-gated

    captured = []
    orig = adapter.extract_claims

    def spy(chunk_text, ceiling_kind, ceiling, locator):
        captured.append({"text": chunk_text, "locator": locator, "ceiling_kind": ceiling_kind})
        return orig(chunk_text, ceiling_kind, ceiling, locator)

    adapter.extract_claims = spy
    pipeline_run.run_rebuild(project["id"], actor="fixture-recorder", role="reviewer")

    key = json.loads((ROOT / "data/demo_project/answer_key.json").read_text())
    facts, fakes = key["facts"], key["fakes"]
    span_by_locator = {c["locator"]: c for c in captured}

    def same_file_span(locator):
        """First span from the same file as the stated locator (invented quotes get cited from somewhere real)."""
        fname = locator.split("#", 1)[0]
        for c in captured:
            if c["locator"].split("#", 1)[0] == fname:
                return c
        return None

    per_span = {i: [] for i in range(len(captured))}
    unplaced_facts, unplaced_fakes = [], []
    placed_fact_ids, placed_fake_ids = [], []
    for f in facts:
        hit = None
        for i, c in enumerate(captured):
            if f["quote"] in c["text"]:
                hit = i
                break
        if hit is None:
            unplaced_facts.append(f["id"])
            continue
        placed_fact_ids.append(f["id"])
        per_span[hit].append({
            "type": f["type"], "text": f["text"], "quote": f["quote"],
            "subject": f.get("subject"), "attribute": f.get("attribute"), "value": f.get("value"),
            "rejected_options": f.get("rejected_options", []), "gap_subject": f.get("gap_subject"),
            "has_issue_ref": bool(re.search(r"#\d+", f["text"])),
            "confidence": 0.9,
        })
    for k_f in fakes:
        target = span_by_locator.get(k_f["locator"])
        if target is None:
            # fall back to the span that actually holds the fake's real quote (wrong_locator case),
            # then to the span from the same file (the model cited the file, invented the sentence)
            for i, c in enumerate(captured):
                if k_f["kind"] == "wrong_locator" and k_f["quote"] in c["text"]:
                    target = c
                    break
        if target is None:
            target = same_file_span(k_f["locator"])
        if target is None:
            unplaced_fakes.append(k_f["id"])
            continue
        placed_fake_ids.append(k_f["id"])
        idx = captured.index(target)
        per_span[idx].append({
            "type": k_f.get("claim_type") or "fact", "text": k_f["quote"], "quote": k_f["quote"],
            "subject": None, "attribute": None, "value": None,
            "rejected_options": [], "gap_subject": None, "has_issue_ref": False,
            "confidence": 0.9,
        })

    out_dir = ROOT / "fixtures" / "llm"
    out_dir.mkdir(parents=True, exist_ok=True)
    for old in out_dir.glob("extract-claims-v3.*.json"):
        meta = json.loads(old.read_text())
        if meta.get("provenance") == "handwritten-reference":
            old.unlink()  # regenerate only our own tier; model fixtures are never touched
    written = 0
    for i, c in enumerate(captured):
        claims = per_span[i]
        chunk_hash = hashlib.sha256(c["text"].encode("utf-8")).hexdigest()[:16]
        fixture = {
            "provenance": "handwritten-reference",
            "generated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_id": None,
            "derived_from": "data/demo_project/answer_key.json (handwritten planted reference) matched to seeded spans",
            "chunk_locator": c["locator"],
            "ceiling_kind": c["ceiling_kind"],
            "claims": claims,
        }
        (out_dir / f"extract-claims-v3.{chunk_hash}.json").write_text(json.dumps(fixture, indent=1))
        written += 1
    print(f"spans captured: {len(captured)}")
    print(f"fixtures written: {written} to {out_dir}")
    print(f"planted fact candidates placed: {len(placed_fact_ids)} of {len(facts)}")
    if unplaced_facts:
        print(f"FACTS NOT PLACED (will read as misses in the report): {', '.join(unplaced_facts)}")
    print(f"planted fake candidates placed: {len(placed_fake_ids)} of {len(fakes)}")
    if unplaced_fakes:
        print(f"FAKES NOT PLACED (no matching span locator): {', '.join(unplaced_fakes)}")


def build_live(args):
    for var in ("LLM_API_KEY", "LLM_URL", "LLM_MODEL"):
        if not os.environ.get(var):
            sys.exit(f"{var} must be set for live recording — refusing to fabricate a 'model' fixture")
    work = Path(tempfile.mkdtemp(prefix="tether-fixture-live-"))
    os.environ["TETHER_DB"] = str(work / "live.db")
    os.environ["TETHER_DATA"] = str(work / "var")
    os.environ["LLM_MODE"] = "live"

    from backend.app.db import read_path as db
    from backend.app.pipeline.seed_demo import load_demo_project
    from backend.app.pipeline import run as pipeline_run
    from backend.app.llm import adapter

    db.init_db()
    project = load_demo_project(name=None, role="reviewer")
    out_dir = ROOT / "fixtures" / "llm"
    out_dir.mkdir(parents=True, exist_ok=True)
    recorded = [0]
    orig_live = adapter._live_extract

    def spy(chunk_text, ceiling_kind, ceiling, locator):
        claims = orig_live(chunk_text, ceiling_kind, ceiling, locator)
        chunk_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()[:16]
        fixture = {
            "provenance": "model",
            "recorded_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "model_id": os.environ["LLM_MODEL"],
            "prompt_version": "extract-claims-v3",
            "chunk_locator": locator,
            "ceiling_kind": ceiling_kind,
            "claims": claims,
        }
        (out_dir / f"extract-claims-v3.{chunk_hash}.json").write_text(json.dumps(fixture, indent=1))
        recorded[0] += 1
        return claims

    adapter._live_extract = spy
    pipeline_run.run_rebuild(project["id"], actor="fixture-recorder", role="reviewer")
    print(f"recorded {recorded[0]} model chunks into {out_dir}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["reference", "live"], default="reference")
    args = ap.parse_args()
    (build_reference if args.mode == "reference" else build_live)(args)
