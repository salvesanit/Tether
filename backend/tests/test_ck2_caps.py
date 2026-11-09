# CK-2 — Confidence caps: confidence is the lower of the raw score and a ceiling by source type. One test per source type.
from backend.app import config
from backend.app.checks import ck2_caps


def test_ck2_file_and_commit_ceiling():
    for kind in ("file", "commit", "merged_pr"):
        capped, rule = ck2_caps.cap(0.99, kind, config.CEILINGS[kind])
        assert capped == 0.95, (kind, capped)
        assert "0.95" in rule


def test_ck2_issue_and_pr_comment_ceiling():
    for kind in ("issue_comment", "pr_comment"):
        capped, rule = ck2_caps.cap(0.99, kind, config.CEILINGS[kind])
        assert capped == 0.85, (kind, capped)


def test_ck2_unmerged_pr_ceiling():
    capped, _ = ck2_caps.cap(0.99, "unmerged_pr", config.CEILINGS["unmerged_pr"])
    assert capped == 0.70


def test_ck2_single_chat_message_ceiling():
    capped, rule = ck2_caps.cap(0.99, "chat", config.CEILINGS["chat"])
    assert capped == 0.60
    assert "chat@0.60" in rule


def test_ck2_raw_below_ceiling_is_kept_and_rules_backed():
    capped, rule = ck2_caps.cap(0.55, "file", config.CEILINGS["file"])
    assert capped == 0.55
    assert rule.startswith("raw:0.55")
