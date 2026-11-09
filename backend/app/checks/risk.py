# One-line purpose: risk-order estimate for the successor queue. Labelled 'estimate'; ranks work, never people.
import re

from .. import config


def estimate(claim: dict, module_concentration: float, has_open_conflict: bool, gap_is_open: bool):
    parts = []
    score = config.TYPE_WEIGHT.get(claim["type"], 1)
    parts.append(f"type {claim['type']} +{config.TYPE_WEIGHT.get(claim['type'], 1)}")
    text = f"{claim.get('text','')} {claim.get('quote','')}".lower()
    heavy_module = next((m for m in ("payments", "notifications", "search") if m in text), None)
    if heavy_module and module_concentration >= 0.80:
        score += config.RISK_SINGLE_AUTHOR_BONUS
        parts.append(f"one author wrote ≥80% of {heavy_module} +{config.RISK_SINGLE_AUTHOR_BONUS}")
    if re.search(r"#\d+", text) or claim.get("has_issue_ref"):
        score += config.RISK_OPEN_LINK_BONUS
        parts.append(f"links to an open issue or PR +{config.RISK_OPEN_LINK_BONUS}")
    if has_open_conflict or gap_is_open:
        score += config.RISK_CONFLICT_GAP_BONUS
        why = "open conflict" if has_open_conflict else "open gap"
        parts.append(f"{why} beside it +{config.RISK_CONFLICT_GAP_BONUS}")
    return float(score), "estimate · " + " · ".join(parts)


def module_concentration_from_authors(author_counts: dict, total: int) -> float:
    if not author_counts or total == 0:
        return 0.0
    return max(author_counts.values()) / total
