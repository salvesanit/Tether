# One-line purpose: CK-4 — the twelve successor-needs subjects; no kept claim ⇒ a gap row with owner and next step.
from .. import config

# Fixed question + who usually knows + the next step. The model may only phrase; it never decides what is missing.
GAP_TEMPLATE = {
    "build and run": ("How does someone build and run Aster locally?", "Aarav Mehta (leaver)", "Ask Aarav to record the run steps before he leaves."),
    "deploy": ("How do deploys happen, and on what cadence?", "Aarav Mehta (leaver)", "Ask Aarav to walk Diya through one deploy."),
    "accounts and credentials": ("Which accounts exist, and where do the credentials live?", "Aarav Mehta (leaver)", "List accounts with the owner and the store location; rotate after handover."),
    "third-party services and vendors": ("Which outside services do we pay for or depend on, and whose email holds them?", "Aarav Mehta (leaver)", "Export the vendor list and move ownership to a team account."),
    "data and backups": ("What data exists, where is it backed up, and how do we restore it?", "Aarav Mehta (leaver)", "Confirm backup schedule and one test restore before the handover meeting."),
    "open work and branches": ("What work is open right now, and which branches carry it?", "Priya Nair / Rohan Iyer", "List open issues and branches; Diya picks up the queue."),
    "key decisions": ("Which decisions shaped this project, and why?", "Aarav Mehta (leaver)", "Walk the decision list in the handover meeting."),
    "known issues and workarounds": ("What breaks, and what is the workaround?", "Meera Krishnan", "Collect the workarounds into the runbook."),
    "contacts": ("Who do we ask when X breaks?", "Aarav Mehta (leaver)", "Write the who-to-ask list; Diya keeps it."),
    "deadlines": ("Which dates must we hit, and who sets them?", "Sanit Salve (reviewer)", "Confirm the next two milestones and their owners."),
    "access": ("Who has access to what, and how does Diya get hers?", "Sanit Salve (reviewer)", "Grant Diya the minimum set before day one."),
    "testing and CI": ("What does CI run, and what does it not cover?", "Rohan Iyer", "Diya watches one CI run end to end."),
}


def missing_subjects(covered_gap_subjects: set) -> list:
    return [s for s in config.GAP_SUBJECTS if s not in covered_gap_subjects]


def gap_row(subject: str):
    q, owner, step = GAP_TEMPLATE[subject]
    return {"subject": subject, "question": q, "owner": owner, "next_step": step}
