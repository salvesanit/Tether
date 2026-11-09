# Tether — one vocabulary, imported by code, tests and docs. Every term in the UI, API and docs comes from here.
CLAIM_TYPES = ["decision","owner","dependency","risk","repeated problem","open question","next step"]

# Confidence ceilings by source type (Round 2 prompt, CK-2). Defaults N1 approves in docs/N1_DECISIONS.md.
CEILINGS = {
    "file": 0.95,          # notes, code, ci config
    "commit": 0.95,
    "merged_pr": 0.95,
    "issue_comment": 0.85,
    "pr_comment": 0.85,
    "unmerged_pr": 0.70,
    "chat": 0.60,
}
CONFIDENCE_VERIFIED_FLOOR = 0.80

# Claim status set by the checks, then confirmed by a person.
STATUSES = ["verified","uncertain","conflicting","missing"]
REVIEW_STATES = ["pending","confirmed","edited","rejected","parked"]

LABELS = ["open","internal","restricted","confidential"]
LABEL_RANK = {"open": 0, "internal": 1, "restricted": 2, "confidential": 3}

PROJECT_STATES = ["scoped","labelled","rebuilt","in review","signed","shared","received"]

# The twelve successor-needs subjects the gap check walks (CK-4).
GAP_SUBJECTS = [
    "build and run",
    "deploy",
    "accounts and credentials",
    "third-party services and vendors",
    "data and backups",
    "open work and branches",
    "key decisions",
    "known issues and workarounds",
    "contacts",
    "deadlines",
    "access",
    "testing and CI",
]

# Risk order (successor queue). Estimate only — labeled as such in the UI.
TYPE_WEIGHT = {
    "risk": 5,
    "dependency": 4,
    "open question": 4,
    "next step": 3,
    "repeated problem": 3,
    "owner": 2,
    "decision": 1,
}
RISK_SINGLE_AUTHOR_BONUS = 3   # module where one author wrote >= 80% of commits
RISK_OPEN_LINK_BONUS = 2       # links to an open issue or PR
RISK_CONFLICT_GAP_BONUS = 2    # a conflict or a gap sits beside it

SEVEN_DAYS_STEP = "notes"
PROMPT_VERSION = "extract-claims-v3"
REVIEWER_REASON_REQUIRED = ["reject","park","decide"]
