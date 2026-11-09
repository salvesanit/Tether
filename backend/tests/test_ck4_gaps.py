# CK-4 — Gap questions: a fixed successor-needs list. No kept claim ⇒ a gap row with question, owner, next step.
def test_ck4_six_planted_gaps_listed(built, answer_key):
    db = built["db"]
    gaps = db.list_gaps(built["project_id"])  # suggested excluded by definition
    open_gaps = [g for g in gaps if g["state"] == "open"]
    got = {g["subject"] for g in open_gaps}
    want = set(answer_key["gaps"]["missing"])
    assert want <= got, f"planted gaps missing from the queue: {sorted(want - got)}"


def test_ck4_every_gap_has_question_owner_next_step(built):
    db = built["db"]
    for g in db.list_gaps(built["project_id"]):
        assert g["question"].strip(), g
        assert g["owner"] and g["owner"].strip(), g
        assert g["next_step"] and g["next_step"].strip(), g


def test_ck4_suggested_subjects_not_counted_as_planted(built, answer_key):
    db = built["db"]
    suggested = db.list_suggested_gaps(built["project_id"])
    assert suggested, "the suggested subject should be visible but suggested"
    assert all(g["state"] == "suggested" for g in suggested)
    open_subjects = {g["subject"] for g in db.list_gaps(built["project_id"]) if g["state"] == "open"}
    assert not ({g["subject"] for g in suggested} & open_subjects)
