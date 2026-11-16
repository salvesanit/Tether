<!-- commit a6ce51adc492 · modified worktree · 2026-11-12 · model mode: replay · measured on the synthetic project -->
# Tether — verification report

**Result: PASS WITH SKIPS** · commit `a6ce51adc492` · 2026-11-12 · model mode: `replay` · measured on the synthetic project.

In replay mode the model call is recorded, so this report shows that the checks and the plumbing work — not that the model is good. Counts only: never a loss rate, never a percent of knowledge captured.

| Test ID | Result | Detail |
|---|---|---|
| AK-1 | PASS | ok |
| AK-2 | PASS | ok |
| CK-1 | PASS | ok |
| CK-2 | PASS | ok |
| CK-3 | PASS | ok |
| CK-4 | PASS | ok |
| E2E-1 | SKIPPED (requires CI service) | skipped |
| IN-1 | PASS | ok |
| KEY-1 | PASS | ok |
| LIVE-1 | PASS | ok |
| PERM-1 | PASS | ok |
| PERM-2 | PASS | ok |
| PERM-3 | PASS | ok |
| PERM-4 | PASS | ok |
| PERM-5 | SKIPPED (requires CI service) | skipped |
| RD-1 | PASS | ok |
| RD-2 | PASS | ok |
| REV-1 | PASS | ok |
| SEC-1 | PASS | ok |
| SEC-2 | PASS | ok |
| SEC-3 | PASS | ok |
| SEC-4 | PASS | ok |
| SW-1 | PASS | ok |
| UX-1 | PASS | ok |

## Rebuild counts (this run)

spans 165 · candidates 82 · kept 60 · dropped 21 ({'quote_not_found': 21}) · conflicts 6 · gaps 6 · redactions 5 · quarantine 1

## Not read

- chat.json · #hr-leave — HR channel — excluded by policy
- chat.json · #private-aarav — private channel — not ours to read

## SW-1

Run without the chat export: the CK-4 gap queue still opens (see test_sw1_*), and the missing source is chat.json — 11 of 61 planted facts live in chat. The report you are reading names it.

## Integration checks

E2E-1 requires Playwright Chromium; PERM-5 requires PostgreSQL. Local skips are reported as SKIPPED, not PASS. CI installs the browser and database service and requires these checks to run. The separate `scripts/ui_smoke.py` path also writes screenshots under `reports/ui/`.
