# One-line purpose: rule-based extractor — the fallback and default engine. Proposes claims; never decides.
import re

from .. import config

_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")
_LEADING_BULLET = re.compile(r"^\s*(?:[-*•]|\d+[.)])\s+")
_COMMENT_PREFIX = re.compile(r"^\s*(?:[#;/]+(?:\s*(?:rev|line)\s*\d+)?[-: ]*|//\s*)")
_CONVENTIONAL_PREFIX = re.compile(r"^(?:feat|fix|chore|docs|refactor|test|build|ci|perf|style|release)(\([^)]*\))?!?:\s*", re.I)

def _clean_sentence(s: str):
    """Strip list/comment/conventional prefixes. Returns (sentence, type_hint|None)."""
    s = _LEADING_BULLET.sub("", s).strip()
    s = _CONVENTIONAL_PREFIX.sub("", s).strip()
    s = _COMMENT_PREFIX.sub("", s).strip()
    hint = None
    m = re.match(r"(?i)^(risk):\s*", s)
    if m:
        s, hint = s[m.end():].strip(), "risk"
    return s, hint

# Type assignment: keyed (subject/attribute/value) patterns first — these also feed conflict detection.
KEYED = [
    (re.compile(r"deploy(?:s|ment)?\s+(?:on|every|goes out on)\s+(Friday|Thursday|Monday|Tuesday|Wednesday|Saturday|Sunday)s?", re.I),
     dict(type="decision", subject="deploy", attribute="day", value=lambda m: m.group(1).capitalize(), gap="deploy")),
    (re.compile(r"rate[ -]?limit\s*(?:is|of|to|set to|=|was)?\s*(\d+)\s*(?:requests\s*)?(?:per|/)\s*min", re.I),
     dict(type="decision", subject="rate limit", attribute="requests per minute", value=lambda m: f"{m.group(1)} per minute", gap=None)),
    (re.compile(r"session\s+timeout\s*(?:is|to|of|was)?\s*(\d+)\s*min", re.I),
     dict(type="decision", subject="session timeout", attribute="minutes", value=lambda m: f"{m.group(1)} minutes", gap=None)),
    (re.compile(r"cache\s+ttl\s*(?:is|of|=|was)?\s*(\d+)\s*min", re.I),
     dict(type="decision", subject="search cache", attribute="ttl minutes", value=lambda m: f"{m.group(1)} minutes", gap=None)),
    (re.compile(r"(?:cut releases from|releases from|ship from)\s+([A-Za-z0-9._/-]+)", re.I),
     dict(type="decision", subject="release branch", attribute="branch", value=lambda m: m.group(1).rstrip("."), gap="open work and branches")),
    (re.compile(r"([A-Za-z][a-z]+)\s+owns\s+notifications", re.I),
     dict(type="owner", subject="notifications", attribute="owner", value=lambda m: m.group(1).capitalize(), gap=None)),
    (re.compile(r"payments\s+cutover\s+(?:happens\s+)?on\s+(\d{4}-\d{2}-\d{2})", re.I),
     dict(type="next step", subject="payments", attribute="cutover date", value=lambda m: m.group(1), gap="open work and branches")),
]

# Gap coverage taggers: attach a successor-needs subject to a claim (does not change its type).
GAP_TAGGERS = [
    (re.compile(r"Node 20|npm run dev|build and run|run locally", re.I), "build and run"),
    (re.compile(r"migrate|backport|issue #\d+|release/[\d.x]+|branch(?:es)?\b", re.I), "open work and branches"),
    (re.compile(r"workaround|known issue|recurs on|time out again|double-fires again", re.I), "known issues and workarounds"),
    (re.compile(r"CI runs|CI depend|testing and CI|GitHub Actions|pytest|Playwright", re.I), "testing and CI"),
    (re.compile(r"deploy", re.I), "deploy"),
]

TYPE_PATTERNS = [
    ("decision", re.compile(r"\b(decided|decision|chose\b.*\bover\b|chosen over|settled on|going with|we deploy on|we ship from)\b", re.I)),
    ("owner", re.compile(r"\b(owns|owned by|owner[: ]|takes ownership)\b", re.I)),
    ("dependency", re.compile(r"\b(depends? on|blocked by|requires|depends upon)\b", re.I)),
    ("repeated problem", re.compile(r"\b(again|recurring|keeps happening|keep happening|recurs|same 429 retry loop|retry storms?|time out again)\b", re.I)),
    ("risk", re.compile(r"\b(risk|might break|might lose|might drift|might force|might overload|might double|no idempotency|no backoff|could fail|might switch|might move|might be stale|might drift)\b", re.I)),
    ("next step", re.compile(r"\b(TODO|next step|backport|cut release|cutover|close out|migrate|rotate the|write the|we will|publish results)\b", re.I)),
]

ISSUE_REF = re.compile(r"(?:issue|pr)\s*#?\s*(\d+)|#(\d+)", re.I)
VALUE_NORM = re.compile(r"[^a-z0-9]+")


def _sentences(text: str):
    for raw in _SENTENCE_SPLIT.split(text.strip()):
        s, hint = _clean_sentence(raw)
        if s:
            yield s, hint


def _normalize_value(v):
    if v is None:
        return None
    return VALUE_NORM.sub(" ", str(v).lower()).strip()


def extract_from_span(span_text: str, ceiling_kind: str, ceiling: float) -> list:
    """Return candidate claims for one span. The quote is always an exact substring of the span."""
    out = []
    for sentence, hint in _sentences(span_text):
        if len(sentence) < 12 or len(sentence) > 240:
            continue  # too short to be a claim / too long for one line
        keyed = None
        for rx, spec in KEYED:
            m = rx.search(sentence)
            if m:
                keyed = (m, spec)
                break
        ctype = None
        subject = attribute = value = None
        gap_subject = None
        if keyed:
            m, spec = keyed
            ctype = spec["type"]
            subject, attribute = spec["subject"], spec["attribute"]
            value = spec["value"](m)
            gap_subject = spec["gap"]
        elif hint:
            ctype = hint
        else:
            s = sentence.strip()
            if s.endswith("?"):
                ctype = "open question"
            else:
                for t, rx in TYPE_PATTERNS:
                    if rx.search(s):
                        ctype = t
                        break
        if ctype is None:
            continue  # not a claim candidate
        if gap_subject is None:
            for rx, gap in GAP_TAGGERS:
                if rx.search(sentence):
                    gap_subject = gap
                    break
        if ctype == "decision" and gap_subject is None:
            gap_subject = "key decisions"
        rejected = []
        if ctype == "decision":
            m = re.search(r"\bover\s+([^.;,]+)", sentence)
            if m:
                opt = m.group(1).strip()
                low = opt.lower()
                for stop in (" to ", " for ", " because", " and ", " with ", " so ", " after ", " instead"):
                    i = low.find(stop)
                    if i != -1:
                        opt = opt[:i]
                        low = opt.lower()
                opt = opt.strip(" .")
                if opt and len(opt) <= 48:
                    rejected = [opt]
        raw = 0.90
        capped = round(min(raw, ceiling), 2)
        rule = f"rules-v1 raw {raw:.2f}, capped by {ceiling_kind}@{ceiling:.2f}"
        if capped == raw:
            rule = f"rules-v1 raw {raw:.2f}, within {ceiling_kind}@{ceiling:.2f}"
        out.append({
            "type": ctype,
            "text": sentence.strip(),
            "quote": sentence,
            "subject": subject.lower() if subject else None,
            "attribute": attribute.lower() if attribute else None,
            "value": value,
            "value_norm": _normalize_value(value),
            "rejected_options": rejected,
            "confidence": capped,
            "confidence_rule": rule,
            "ceiling_kind": ceiling_kind,
            "gap_subject": gap_subject,
            "has_issue_ref": bool(ISSUE_REF.search(sentence)),
        })
    return out


def ceiling_for(ceiling_kind: str) -> float:
    return {
        "file": config.CEILINGS["file"],
        "commit": config.CEILINGS["commit"],
        "merged_pr": config.CEILINGS["merged_pr"],
        "issue_comment": config.CEILINGS["issue_comment"],
        "pr_comment": config.CEILINGS["pr_comment"],
        "unmerged_pr": config.CEILINGS["unmerged_pr"],
        "chat": config.CEILINGS["chat"],
    }.get(ceiling_kind, 0.60)
