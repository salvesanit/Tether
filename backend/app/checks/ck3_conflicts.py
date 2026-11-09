# One-line purpose: CK-3 — same subject+attribute, different values ⇒ a conflict. The code never picks a winner.
def norm(v):
    return " ".join(str(v or "").lower().split())


def group_claims(kept_claims: list) -> dict:
    """Group kept claims by (subject, attribute). Returns groups with >= 2 distinct non-empty values."""
    groups = {}
    for c in kept_claims:
        subj, attr = c.get("subject"), c.get("attribute")
        value = c.get("value")
        if not subj or not attr or not value:
            continue
        groups.setdefault((norm(subj), norm(attr)), []).append(c)
    out = {}
    for key, claims in groups.items():
        values = {norm(c["value"]) for c in claims}
        if len(values) > 1:
            out[key] = claims
    return out
