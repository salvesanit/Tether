# KEY-1 — The key matches the files: every planted quote exists at its locator,
# no invented/altered fake exists anywhere, each honeytoken appears only in its excluded channel,
# no planted fact belongs to a missing gap subject.
import json


def test_key1_facts_resolve_at_locator(built, spans_by_locator, answer_key):
    missing = [f["id"] for f in answer_key["facts"]
               if f["locator"] not in spans_by_locator
               or f["quote"] not in spans_by_locator[f["locator"]]["text"]]
    assert missing == [], f"planted facts whose quote is not at the stated locator: {missing}"


def test_key1_invented_and_altered_fakes_exist_nowhere(built, answer_key):
    db = built["db"]
    all_text = "\n".join(s["text"] for s in db.list_spans(built["project_id"]))
    present = [f["id"] for f in answer_key["fakes"]
               if f["kind"] in ("invented", "altered") and f["quote"] in all_text]
    assert present == [], f"fake quotes found in stored spans: {present}"


def test_key1_wrong_locator_fakes_not_at_stated_locator(built, spans_by_locator, answer_key):
    bad = []
    for f in answer_key["fakes"]:
        if f["kind"] != "wrong_locator":
            continue
        span = spans_by_locator.get(f["locator"])
        if span is not None and f["quote"] in span["text"]:
            bad.append(f["id"])  # quote IS at the stated locator — then it would be a real fact, not a fake
    assert bad == [], f"wrong-locator fakes resolvable at their stated locator: {bad}"


def test_key1_honeytokens_never_in_stored_spans(built, answer_key):
    db = built["db"]
    all_text = "\n".join(s["text"] for s in db.list_spans(built["project_id"]))
    for token in answer_key["honeytokens"]:
        assert token not in all_text, f"honeytoken {token} leaked into stored spans"


def test_key1_honeytokens_present_in_excluded_channels_only(answer_key):
    """Vacuity guard: the tokens must really exist in the demo's chat export, inside the excluded channels."""
    import pathlib
    raw = json.loads((pathlib.Path(__file__).resolve().parents[2] / "data/demo_project/chat.json").read_text())
    channels = raw.get("channels", raw)
    excluded = {c.lower().lstrip("#") for c in answer_key["excluded_channels"]}
    tokens = list(answer_key["honeytokens"])
    seen_excluded = 0
    for ch in channels:
        name = str(ch.get("name", "")).lstrip("#").lower()
        body = json.dumps(ch)
        if name in excluded:
            assert any(t in body for t in tokens), f"excluded channel #{name} carries no honeytoken"
            seen_excluded += 1
        else:
            assert not any(t in body for t in tokens), f"honeytoken in readable channel #{name}"
    assert seen_excluded == len(excluded)


def test_key1_no_fact_belongs_to_a_missing_gap_subject(answer_key):
    missing = set(answer_key["gaps"]["missing"])
    bad = [f["id"] for f in answer_key["facts"] if (f.get("gap_subject") or None) in missing]
    assert bad == [], f"planted facts filed under a missing gap subject: {bad}"
