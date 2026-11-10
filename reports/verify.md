<!-- commit 05b0538eb6ee · 2026-11-10 · model mode: replay · measured on the synthetic project -->
# Tether — verification report

**Result: PASS** · commit `05b0538eb6ee` · 2026-11-10 · model mode: `replay` · measured on the synthetic project.

In replay mode the model call is recorded, so this report shows that the checks and the plumbing work — not that the model is good. Counts only: never a loss rate, never a percent of knowledge captured.

| Test ID | Result | Detail |
|---|---|---|
| AK-1 | PASS | ok |
| AK-2 | PASS | ok |
| CK-1 | PASS | ok |
| CK-2 | PASS | ok |
| CK-3 | PASS | ok |
| CK-4 | PASS | ok |
| E2E-1 | PASS (browser-dependent parts SKIPPED) | skipped |
| IN-1 | PASS | ok |
| KEY-1 | PASS | ok |
| PERM-1 | PASS | ok |
| PERM-2 | PASS | ok |
| PERM-3 | PASS | ok |
| PERM-4 | PASS | ok |
| RD-1 | PASS | ok |
| RD-2 | PASS | ok |
| REV-1 | PASS | ok |
| SEC-1 | PASS | ok |
| SEC-2 | PASS | ok |
| SEC-3 | PASS | ok |
| SW-1 | PASS | ok |
| UX-1 | PASS | ok |

## Rebuild counts (this run)

spans 165 · candidates 82 · kept 60 · dropped 21 ({'quote_not_found': 21}) · conflicts 6 · gaps 6 · redactions 5 · quarantine 1

## Not read

- chat.json · #hr-leave — HR channel — excluded by policy
- chat.json · #private-aarav — private channel — not ours to read

## SW-1

Run without the chat export: the CK-4 gap queue still opens (see test_sw1_*), and the missing source is chat.json — 11 of 61 planted facts live in chat. The report you are reading names it.

## E2E-1 / UX-1

Browser-dependent. Where chromium cannot launch (this machine lacks libnspr4), those tests SKIP with a stated reason; `python3 scripts/ui_smoke.py` runs the same path on a desktop and writes screenshots to reports/ui/.
