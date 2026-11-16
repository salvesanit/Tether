# Testing — what each group proves, how to run it, latest result

Latest committed baseline: **48 passed, 1 skipped**. The latest local Round 3 report is [reports/verify.md](../reports/verify.md): **50 passed, 2 skipped**, with the base commit and modified-worktree state recorded. The skips are browser E2E-1 (Chromium could not be downloaded in this Windows environment) and PERM-5 (requires the PostgreSQL CI service). The Playwright E2E is required (not skippable) in CI.

Run everything: `npm ci` then `python3 -m pytest backend/tests -q` · or the full rebuild+tests+reports: `python3 scripts/verify.py`. Chromium binaries are installed with `python3 -m playwright install chromium` for local browser runs.

## Main journeys

| Command | Proves |
|---|---|
| `pytest backend/tests/test_key1_answer_key.py` | KEY-1 — the key matches the files: every planted quote exists at its locator; no fake quote exists; honeytokens only in their excluded channels; no planted fact belongs to a gap subject |
| `pytest backend/tests/test_rd.py` | RD-1 — every locator on every claim resolves to exact text. RD-2 — 3 readers return spans on the demo; plain error on empty/malformed input |
| `pytest backend/tests/test_ck1_quote.py` | CK-1 — 60 real facts kept, 20 fakes dropped+counted; all planted fact texts surface as claims (no silent loss) |
| `pytest backend/tests/test_ck2_caps.py` | CK-2 — one test per source type; no claim above its ceiling |
| `pytest backend/tests/test_ck3_conflicts.py` | CK-3 — 6 of 6 conflicts, both sides, none settled by code |
| `pytest backend/tests/test_ck4_gaps.py` | CK-4 — 6 of 6 planted gaps with question/owner/next step; suggested subjects not counted |
| `pytest backend/tests/test_ak1_ak2.py` | AK-1 — ≥80% of planted decisions found; 0 invented claims in a signed version. AK-2 — rejected options attach to their decision |
| `pytest backend/tests/test_e2e1_ux1.py` | E2E-1 (SKIPPED honestly) · UX-1 — semantic landmarks, keyboard operability, focus-visible, reduced-motion (static checks) |
| `make judge` | scripts/judge_walkthrough.sh — the four-minute path twice in a row (see [docs/demo/golden_path_run.md](demo/golden_path_run.md)) |

## Failure cases

| Command | Proves |
|---|---|
| `pytest backend/tests/test_sec.py` | SEC-1 honeytokens never leave the excluded channels · SEC-2 secrets/PII only as [REDACTED:type] · SEC-3 injection → reviewer item, no gate moves · SEC-4 oversized upload → 413 + log row |
| `pytest backend/tests/test_sw1_source_off.py` | SW-1 — run without chat.json: the six gaps still appear; report names the missing source (11 of 61 planted facts live in chat) |
| `pytest backend/tests/test_in1_input_change.py` | IN-1 — change a planted sentence; the claim shows the new text; its quote resolves; `extractor: rules` for that chunk |
| `pytest backend/tests/test_rev1_gates.py` | REV-1 — each skipped state 409s and logs; sign with undecided conflict refused with the reason |

## Permissions

| Command | Proves |
|---|---|
| `pytest backend/tests/test_perm1_leak_successor.py` | PERM-1 — no restricted/confidential text for the successor on any route, direct ID, export; spans fail closed |
| `pytest backend/tests/test_perm2_perm3_perm4.py` | PERM-2 unsigned versions 403 · PERM-3 weakest-source label · PERM-4 no SQL outside `db/read_path.py` |
| `TETHER_DATABASE_URL=... pytest backend/tests/test_perm5_rls_forced.py` | PERM-5 — PostgreSQL `FORCE ROW LEVEL SECURITY`, non-bypass application role, request-local identity, filtered signed-version rows |

## Reliability

See [docs/RELIABILITY.md](RELIABILITY.md) — failure-mode table with the test ID beside each row, including the two honest gaps (no automated test for a dead database; SQLite not load-tested).

## Required CI jobs

The `verify` job installs Chromium and system libraries, sets `REQUIRE_E2E=1`, and runs `scripts/verify.py`; this runs the clean-start browser path twice and audits Connect, Reconstruct, Review Queue, Sign-Off, and Successor View with axe-core. The `postgres-rls` job creates a `NOSUPERUSER NOBYPASSRLS` app role and runs PERM-1/PERM-5 against PostgreSQL 16. Both are required integration evidence; SQLite-only local runs do not substitute for them.

## Live-model comparison

With an approved provider key and endpoint configured as `LLM_API_KEY`, `LLM_URL`, and `LLM_MODEL`, run `make record-live`, then `make verify-live`. This writes a separate `reports/verify_live.md`; it never overwrites replay reports. A difference of more than two exact-text planted facts returns exit code 2 and requires review. N1 should assess the 25-row sample manually. No report can be created without actual model fixtures.

## Reports

`python3 scripts/verify.py` rebuilds the demo on a throwaway DB, settles it, signs v1.0 via the API, runs the suite, probes every GET route and direct span ID as successor and leaver against role-aware sentinels, and writes [reports/verify.md](../reports/verify.md), [answer_key_report.md](../reports/answer_key_report.md), [check_report.json](../reports/check_report.json), [leak_test_report.md](../reports/leak_test_report.md) — each carrying the commit SHA, the date, the model mode and the words "measured on the synthetic project". Counts only.

## Round 3 — where the new tests will go

Section scaffolding for Round 3 notes: main journeys (E2E-1 unskipped with chromium in CI), failure cases (database-down chaos), permissions (RLS under Postgres), reliability (load profile). Keep IDs incremental (SEC-5, E2E-2…).
