# One-line purpose: CK-1 — the quote must be an exact substring of the span at its locator, character for character.
def check_quote(span_text: str, quote: str) -> bool:
    if not span_text or not quote:
        return False
    return quote in span_text


def check_locator_format(locator: str) -> bool:
    import re
    return bool(re.match(
        r"^(file:.+#(P[0-9]+|L[0-9]+-[0-9]+)|commit:[0-9a-f]{7,40}|issue:[0-9]+#(body|c[0-9]+)|pr:[0-9]+#(body|c[0-9]+)|chat:[^@]+@.+)$",
        locator or "",
    ))
