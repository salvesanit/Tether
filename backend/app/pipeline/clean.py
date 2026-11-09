# One-line purpose: redact secrets and personal data before storage; flag instruction-like text for quarantine.
import re

# gitleaks-style rules, kept deliberately small and readable. Each match becomes [REDACTED:<type>].
SECRET_RULES = [
    ("aws_access_key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("github_token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")),
    ("slack_token", re.compile(r"xox[bapors]-[A-Za-z0-9-]{10,}")),
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----")),
    ("generic_secret", re.compile(r"(?i)(?:password|passwd|secret|api[_-]?key)\s*[:=]\s*\S+")),
]
EMAIL_RE = re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}")
PHONE_RE = re.compile(r"\+?\d[\d\s().-]{7,}\d")
_PHONE_MIN_DIGITS = 10

INJECTION_PATTERNS = [
    re.compile(r"ignore\s+(?:all\s+)?previous\s+instructions", re.I),
    re.compile(r"system\s*:", re.I),
    re.compile(r"you\s+are\s+now\b", re.I),
    re.compile(r"disregard\s+(?:the\s+)?(?:above|previous)", re.I),
    re.compile(r"mark\s+every\s+claim\s+verified", re.I),
]


def redact(text: str):
    """Return (redacted_text, redactions list). Runs before anything is stored."""
    redactions = []
    out = text
    for name, rx in SECRET_RULES:
        out, n = rx.subn(f"[REDACTED:{name}]", out)
        if n:
            redactions.append({"type": name, "count": n})
    out, email_n = EMAIL_RE.subn("[REDACTED:email]", out)  # emails first, so phones don't touch them
    phones = 0
    def _phone_sub(m):
        nonlocal phones
        digits = sum(ch.isdigit() for ch in m.group(0))
        if digits >= _PHONE_MIN_DIGITS:
            phones += 1
            return "[REDACTED:phone]"
        return m.group(0)  # keep things like 2026-08-12 untouched
    out = PHONE_RE.sub(_phone_sub, out)
    if email_n > 0:
        redactions.append({"type": "email", "count": email_n})
    if phones:
        redactions.append({"type": "phone", "count": phones})
    return out, redactions


def injection_hits(text: str) -> list:
    return [rx.pattern for rx in INJECTION_PATTERNS if rx.search(text)]
