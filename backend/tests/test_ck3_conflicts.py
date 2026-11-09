# CK-3 — Group and compare: same subject+attribute, different values ⇒ a conflict. Code never picks a winner.
def test_ck3_six_planted_conflicts_shown_both_sides(built, answer_key):
    db = built["db"]
    conflicts = db.list_conflicts(built["project_id"])
    assert len(conflicts) == 6, f"expected the 6 planted conflicts, got {len(conflicts)}"
    got = {(c["subject"], c["attribute"]) for c in conflicts}
    want = {(c["subject"], c["attribute"]) for c in answer_key["conflicts"]}
    assert got == want
    for c in conflicts:
        values = {cl["value"] for cl in c["claims"]}
        assert len(c["claims"]) >= 2, f"conflict {c['id']} has fewer than two sides"
        assert len(values) >= 2, f"conflict {c['id']} does not actually disagree"


def test_ck3_nothing_settled_by_code_after_rebuild(built):
    db = built["db"]
    conflicts = db.list_conflicts(built["project_id"])
    assert all(c["state"] == "open" for c in conflicts), "the code settled a conflict by itself"
    assert all(c.get("decided_value") in (None, "") for c in conflicts)


def test_ck3_conflict_claims_carry_evidence(built):
    db = built["db"]
    for c in db.list_conflicts(built["project_id"]):
        for cl in c["claims"]:
            ev = db.list_evidence(cl["id"])
            assert ev, f"conflict side {cl['id']} carries no evidence"
