# One-line purpose: CK-2 — confidence is the lower of the raw score and the ceiling for the source type.
from .. import config


def cap(raw: float, ceiling_kind: str, ceiling: float):
    capped = round(min(raw, ceiling), 2)
    rule = f"cap:{ceiling_kind}@{ceiling:.2f} (raw {raw:.2f})" if capped == ceiling < raw else f"raw:{raw:.2f} within {ceiling_kind}@{ceiling:.2f}"
    return capped, rule
