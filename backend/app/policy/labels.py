# One-line purpose: label model, role matrix and the weakest-source rule (HR-2). Pure functions, no SQL.
from .. import config

# Role matrix — defaults Sanit (N1) approves in docs/N1_DECISIONS.md
ROLE_LABELS = {
    "leaver": ["open", "internal", "restricted"],   # claims about own work, never confidential
    "reviewer": ["open", "internal", "restricted", "confidential"],
    "successor": ["open", "internal"],
    "admin": ["open", "internal", "restricted", "confidential"],  # admin reads metadata; text via reviewer path
}


def role_labels(role: str) -> list:
    return ROLE_LABELS.get(role, [])


def can_read_label(role: str, label: str) -> bool:
    return label in ROLE_LABELS.get(role, [])


def weakest_label(labels: list) -> str:
    """HR-2: a claim is only as visible as its weakest source."""
    if not labels:
        return "confidential"
    return max(labels, key=lambda l: config.LABEL_RANK[l])


def can_read_claim(role: str, claim_label: str) -> bool:
    return can_read_label(role, claim_label)


def label_for_source(source_kind: str, name: str) -> str:
    """Default label a person would set in the connect step; the demo manifest carries explicit ones."""
    return "internal"
