# Glossary — the same words everywhere

The one-line source is `backend/app/config.py` (imported by code, tests and docs) plus this file.

- **Claim** — one sentence, one of seven types, tied to a quote at a locator; the atom of the handover.
- **Source** — an authorised artifact: the repo bundle, an issues/PRs export, Markdown notes, a chat export.
- **Span** — a clean, redacted chunk of a source, stored with a locator, its text and its SHA-256.
- **Locator** — one format per source kind: `file:{path}#L{start}-{end}` (code), `file:{path}#P{n}` (notes), `issue:{n}#c{k}`, `pr:{n}#c{k}`, `chat:#{channel}@{ts}`, `commit:{sha}`. Resolves to exact characters.
- **Label** — one of `open | internal | restricted | confidential`; a claim takes the weakest label among its evidence (HR-2).
- **Status** — set by the checks, then a person: `verified | uncertain | conflicting | missing`.
- **Review state** — the person's action on a claim: `pending | confirmed | edited | rejected | parked`.
- **Conflict** — same subject + attribute, different values; both sides visible until a person picks; code never decides (HR-3).
- **Gap** — a successor-needs subject with no kept claim anywhere; stays on the page with an owner and a next step (HR-4).
- **Version** — a frozen, hashed snapshot of the handover, signed by a named reviewer; later edits make a new draft.
- **Receipt** — the successor's "I got it" row; closes the loop, one per (version, successor).
- **Extractor** — `live | replay | rules`; what produced the candidate, stored on the run.
- **Handover** — the successor's signed, role-filtered view; sections in risk order; every line carries a citation chip.
- **Gate** — Gate 1 labels cleared · Gate 2 queue settled (conflicts decided/parked, uncertainties settled/parked) · Gate 3 citation test 100% + reviewer sign.
