#!/usr/bin/env python3
"""Compare recorded live-model fixtures with the handwritten-reference baseline."""
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def fact_count_requires_review(reference_count: int, model_count: int) -> bool:
    return abs(model_count - reference_count) > 2


def _sha():
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "HEAD"], cwd=ROOT, capture_output=True, text=True, timeout=10)
    return result.stdout.strip()[:12] if result.returncode == 0 else "(no git metadata)"


def _fixture_metadata():
    from backend.app import config

    paths = sorted((ROOT / "fixtures" / "llm" / "model").glob(f"{config.PROMPT_VERSION}.*.json"))
    if not paths:
        raise RuntimeError("no recorded model fixtures; configure LLM_API_KEY, LLM_URL, and LLM_MODEL, then run make record-live")
    models, versions = set(), set()
    for path in paths:
        fixture = json.loads(path.read_text(encoding="utf-8"))
        if fixture.get("provenance") != "model":
            raise RuntimeError(f"non-model fixture in model folder: {path.name}")
        if not isinstance(fixture.get("claims"), list):
            raise RuntimeError(f"invalid claims payload in model fixture: {path.name}")
        models.add(fixture.get("model_id"))
        versions.add(fixture.get("prompt_version"))
    if None in models or len(models) != 1:
        raise RuntimeError(f"model fixtures must use exactly one non-empty model id; found {sorted(str(v) for v in models)}")
    if versions != {config.PROMPT_VERSION}:
        raise RuntimeError(f"fixtures must use prompt {config.PROMPT_VERSION}; found {sorted(str(v) for v in versions)}")
    configured = os.environ.get("LLM_MODEL")
    model_id = next(iter(models))
    if configured and configured != model_id:
        raise RuntimeError(f"LLM_MODEL={configured!r} does not match recorded fixture model {model_id!r}")
    return model_id, config.PROMPT_VERSION, len(paths)


def _run_fixture_set_scoped(provenance, label):
    with tempfile.TemporaryDirectory(prefix=f"tether-verify-{label}-") as tmp:
        os.environ["TETHER_DB"] = str(Path(tmp) / "verify.db")
        os.environ["TETHER_DATA"] = str(Path(tmp) / "var")
        os.environ["LLM_MODE"] = "replay"
        os.environ["LLM_FIXTURE_PROVENANCE"] = provenance

        from backend.app.db import read_path as db
        from backend.app.pipeline.seed_demo import load_demo_project
        from backend.app.pipeline import run as pipeline_run

        db.init_db()
        project = load_demo_project(name=None, role="reviewer")
        db.set_project_state(project["id"], "labelled")
        result = pipeline_run.run_rebuild(project["id"], actor="verify-live", role="reviewer")
        claims = db.list_claims(project["id"])
        claim_texts = {claim["text"] for claim in claims}
        key = json.loads((ROOT / "data" / "demo_project" / "answer_key.json").read_text(encoding="utf-8"))
        facts_found = sum(1 for fact in key["facts"] if fact["text"] in claim_texts)
        dropped_quotes = set()
        for candidate in db.list_candidates(result["run"]["id"]):
            if candidate.get("drop_reason"):
                payload = json.loads(candidate.get("payload") or "{}")
                if payload.get("quote"):
                    dropped_quotes.add(payload["quote"])
        fake_dropped = sum(1 for fake in key["fakes"] if fake.get("quote") in dropped_quotes)
        quote_claims = {}
        for claim in claims:
            for evidence in db.list_evidence(claim["id"]):
                quote_claims.setdefault(evidence["quote"], []).append(claim["text"])
        return {
            "counts": result["counts"],
            "facts_found": facts_found,
            "facts_total": len(key["facts"]),
            "fake_dropped": fake_dropped,
            "fakes_total": len(key["fakes"]),
            "quote_claims": quote_claims,
            "key_facts": key["facts"],
        }


def _run_fixture_set(provenance, label):
    from backend.app.db import read_path as db
    with db.role_context("reviewer"):
        return _run_fixture_set_scoped(provenance, label)


def _md_cell(value):
    return " ".join(str(value).replace("|", "\\|").split())


def main():
    os.environ.pop("TETHER_DATABASE_URL", None)
    try:
        model_id, prompt_version, fixture_count = _fixture_metadata()
        reference = _run_fixture_set("handwritten-reference", "reference")
        model = _run_fixture_set("model", "model")
    except Exception as exc:
        print(f"verify-live could not run: {exc}", file=sys.stderr)
        return 1

    divergence = abs(model["facts_found"] - reference["facts_found"])
    requires_review = fact_count_requires_review(reference["facts_found"], model["facts_found"])
    date = time.strftime("%Y-%m-%d", time.gmtime())
    sha = _sha()
    lines = [
        f"<!-- commit {sha} · {date} · model mode: recorded-live-fixtures · measured on the synthetic project -->\n",
        "# Live-model verification — synthetic Aster\n\n",
        f"Commit `{sha}` · {date} · model `{model_id}` · prompt `{prompt_version}` · "
        f"{fixture_count} model fixture(s) · measured on the synthetic project.\n\n",
        "This report replays recorded model output; it makes no network calls. It is separate from "
        "`verify.md` and the handwritten-reference baseline. Counts are not quality scores or capture rates.\n\n",
        f"**Result: {'REVIEW REQUIRED' if requires_review else 'COMPARISON READY'}** — "
        f"the fact-count difference is {divergence} (review bar: more than 2).\n\n",
        "| Measure | Handwritten reference | Recorded model | Difference |\n|---|---:|---:|---:|\n",
    ]
    measures = (
        ("Facts found (answer-key exact text)", "facts_found"),
        ("Facts in answer key", "facts_total"),
        ("Candidates kept", "kept"),
        ("Candidates dropped", "dropped"),
        ("Planted fakes dropped by quote check", "fake_dropped"),
        ("Planted fakes in answer key", "fakes_total"),
        ("Spans using rules fallback", "rules"),
        ("Spans using replay fixtures", "replay"),
    )
    for label, key in measures:
        ref_value = reference["counts"].get("extractor_chunks", {}).get(key, 0) if key in ("rules", "replay") else reference.get(key, reference["counts"].get(key, 0))
        model_value = model["counts"].get("extractor_chunks", {}).get(key, 0) if key in ("rules", "replay") else model.get(key, model["counts"].get(key, 0))
        lines.append(f"| {label} | {ref_value} | {model_value} | {model_value - ref_value:+d} |\n")
    lines.extend([
        "\nModel chunks recorded: " + str(model["counts"].get("extractor_chunks", {}).get("replay", 0)) +
        f" of {model['counts'].get('spans', 0)}; model id and prompt version are recorded on the run.\n\n",
        "## N1 review — 25 answer-key claims beside model output\n\n",
        "For each row, compare the expected fact with the claim supported by the same source quote. "
        "N1 must complete the assessment; blank boxes are not approvals.\n\n",
        "| # | Expected answer-key fact | Model claim for same quote | N1 assessment / notes |\n|---:|---|---|---|\n",
    ])
    for index, fact in enumerate(model["key_facts"][:25], 1):
        found = model["quote_claims"].get(fact.get("quote"), [])
        output = " / ".join(found) if found else "No claim cited the expected quote"
        lines.append(f"| {index} | {_md_cell(fact['text'])} | {_md_cell(output)} | [ ] accurate [ ] partial [ ] wrong; |\n")
    if len(model["key_facts"]) < 25:
        lines.append(f"\nOnly {len(model['key_facts'])} answer-key facts are available; the requested 25-row sample could not be filled.\n")
    lines.append("\nReview status: pending N1's manual assessment. A difference above 2 facts is explicitly flagged for review and must not be accepted silently.\n")
    report_path = ROOT / "reports" / "verify_live.md"
    report_path.write_text("".join(lines), encoding="utf-8")
    print(f"Live-model comparison written to {report_path.relative_to(ROOT)}")
    print(f"model={model_id}; prompt={prompt_version}; facts={model['facts_found']}/{model['facts_total']}; "
          f"reference={reference['facts_found']}/{reference['facts_total']}; divergence={divergence}; "
          f"{'REVIEW REQUIRED' if requires_review else 'manual N1 review pending'}")
    return 2 if requires_review else 0


if __name__ == "__main__":
    sys.exit(main())
