# CK-1 — Quote match: the system, not the model, resolves the locator to a stored span.
# Fed the planted facts and the twenty fakes, the check keeps the real ones and drops every fake — counted.
from backend.app.checks import ck1_quote


def _candidate(quote, locator):
    return {"type": "decision", "text": quote, "quote": quote, "locator": locator,
            "subject": None, "attribute": None, "value": None}


def test_ck1_all_planted_facts_kept(built, spans_by_locator, answer_key):
    dropped = []
    for f in answer_key["facts"]:
        span = spans_by_locator.get(f["locator"])
        if span is None or not ck1_quote.check_quote(span["text"], f["quote"]):
            dropped.append(f["id"])
    assert dropped == [], f"real facts dropped by CK-1: {dropped}"


def test_ck1_all_twenty_fakes_dropped(built, spans_by_locator, answer_key):
    survivors = []
    for f in answer_key["fakes"]:
        span = spans_by_locator.get(f["locator"])
        quote_ok = span is not None and ck1_quote.check_quote(span["text"], f["quote"])
        if quote_ok:
            survivors.append(f["id"])
    assert survivors == [], f"fakes that would survive CK-1: {survivors}"


def test_ck1_replay_run_kept_and_dropped_counts(built, answer_key):
    c = built["counts"]
    # candidates = kept proposals + dropped; kept (claim rows) trails kept proposals by the dedupe count
    assert c["candidates"] >= c["kept"] + c["dropped"]
    # 20 fakes, one of them proposed at two byte-identical chunks and dropped in both — hence 21 drop candidates
    assert c["dropped"] == 21 and c["dropped_by_reason"].get("quote_not_found") == 21
    assert c["kept"] >= 59
    # no planted fact may silently vanish: every fact text must surface as a kept claim
    claim_texts = {cl["text"] for cl in built["db"].list_claims(built["project_id"])}
    missing = [f["id"] for f in answer_key["facts"] if f["text"] not in claim_texts]
    assert missing == [], f"planted facts lost by the pipeline: {missing}"


def test_ck1_check_quote_requires_exact_substring():
    assert ck1_quote.check_quote("The cache ttl is 10 min.", "The cache ttl is 10 min.")
    assert not ck1_quote.check_quote("The cache ttl is 10 min.", "cache TTL is 10 minutes")
    assert not ck1_quote.check_quote("", "anything")
    assert ck1_quote.check_locator_format("file:notes/2026-08-12.md#P2")
    assert ck1_quote.check_locator_format("commit:48b856fc1f92408b45d595e15c146b1906f4e0dc")
    assert ck1_quote.check_locator_format("issue:9#body")
    assert ck1_quote.check_locator_format("pr:21#c4")
    assert ck1_quote.check_locator_format("chat:#dev@1757846432")
    assert not ck1_quote.check_locator_format("the database")
