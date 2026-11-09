# RD-1 — Every locator on every claim resolves to the exact text in its source.
# RD-2 — Each reader returns spans on the demo project and a plain error on empty or malformed input.
import pytest

from backend.app.readers import readers


def test_rd1_every_evidence_quote_matches_its_span(built):
    db = built["db"]
    bad = []
    n = 0
    for c in db.list_claims(built["project_id"]):
        for e in db.list_evidence(c["id"]):
            n += 1
            span = db.get_span(e["span_id"])
            if span is None or e["quote"] not in span["text"]:
                bad.append(e["locator"])
    assert bad == [], f"evidence quotes not found at their span: {bad[:5]}"
    assert n > 0


def test_rd2_readers_on_demo_sources(tmp_path):
    import json
    import pathlib
    root = pathlib.Path(__file__).resolve().parents[2]
    demo = root / "data/demo_project"
    notes = next((demo / "notes").glob("*.md"))
    spans = readers.read_notes(f"notes/{notes.name}", notes.read_text())
    assert spans and all("#P" in s["locator"] for s in spans)
    chat_excl = json.loads((demo / "manifest.json").read_text())["excluded_channels"]
    chat_spans = readers.read_chat_export("chat.json", (demo / "chat.json").read_bytes(), chat_excl)
    assert chat_spans
    assert not any(ch.split("@")[0].lstrip("chat:#") in ("hr-leave", "private-aarav")
                   for ch in (s["locator"] for s in chat_spans))
    issue_spans = readers.read_issues("issues.json", (demo / "issues.json").read_bytes())
    assert issue_spans and all(s["locator"].startswith(("issue:",) ) for s in issue_spans)
    pr_spans = readers.read_prs("prs.json", (demo / "prs.json").read_bytes())
    assert pr_spans and all(s["locator"].startswith("pr:") for s in pr_spans)
    bundle_spans = readers.read_git_bundle(str(demo / "repo.bundle"))
    assert bundle_spans


def test_rd2_empty_and_malformed_inputs_raise_plain_errors():
    with pytest.raises(readers.SourceError):
        readers.read_notes("x.md", "")
    with pytest.raises(readers.SourceError):
        readers.read_chat_export("c.json", b"{not json", [])
    with pytest.raises(readers.SourceError):
        readers.read_chat_export("c.json", b'{"channels": []}', [])
    with pytest.raises(readers.SourceError):
        readers.read_issues("i.json", b"")
    with pytest.raises(readers.SourceError):
        readers.read_prs("p.json", b'[{"no_number": true}]')
