# Self-audit — what this build got wrong, and how it was found

Honesty first: every entry below was found by tests, probes or a person, and is fixed or recorded. Nothing was found by "polish review" alone.

| # | What was wrong | Found by | Fix / status |
|---|---|---|---|
| 1 | SPA catch-all shadowed the API routes (static block registered before /api/* routes) — every /api call 404/500 | PERM-1 failing after first chromium-less run | static block moved to EOF in `main.py`; PERM-1 green |
| 2 | Route /api/spans was unreachable (404 instead of 403) — a permission check that never ran | test_perm1_leak_successor (expected 403, got 404) | same fix as #1 |
| 3 | 165 recorded fixtures collided to 164 files — last-write-wins silently erased the two real "Payments cutover" facts (kept 60→59, NS-01/NS-01b absent) | answer_key_report showing an absent fact; candidate scan | `scripts/record_fixtures.py` now unions twin positions; `test_ck1…` asserts lost-facts == 0 |
| 4 | Wrong-locator fake fixtures were placed on the quote's span, making them un-droppable (contradiction with CK-1) | dropped-count probe in a scratch rebuild | `attach_wrong_locator()` attaches off the quote's span; report now shows 20/20 fakes dropped |
| 5 | Restricted claim readable via its open-source citation (span gate checked source label only) — successor could read the restricted sentence | strengthening PERM-1 after fixture union fix surfaced the claim | fail-closed citation rule (decisions/0003); PERM-1 + leak probe span rows green |
| 6 | verify.py leak probe failed the *leaver* for restricted content the matrix says the leaver may read | first verify run against the new fixtures | role-aware probe; reviewer/admin unprobed by design; report table shows every row |
| 7 | verify.py verdict printed FAIL with 0 failing groups after #6 (probe failures invisible to the verdict string) | reading the report output | verdict counts probe failures; now honest: FAIL iff leaks found or tests fail |
| 8 | Unguarded labels gate: re-POSTing /gates/labels on a signed project re-logged a fake gate clear | code read during pending-work sweep | scoped-only + 409 + `gate.refused` log row (both refusal paths) |
| 9 | Sign/share refusals were 403/409 without log rows | REV-1 expectation vs behavior | `sign.refused` / `share.refused` rows on every refusal path |
| 10 | Upload ceiling absent — unbounded reads into `raw` dict | RELIABILITY audit while writing the failure-mode table | 25 MiB/file cap → 413 + `upload.refused` log; SEC-4 test |
| 11 | Live adapter had a 30s timeout but no call cap (spec: 200/run) | same audit | `LLM_MAX_CALLS` default 200, rules fallback past the cap |
| 12 | Stale comment in adapter claimed no handwritten fixtures existed (they are the majority) | doc-vs-code sweep | comment corrected |
| 13 | E2E-1 never runs here (chromium/libnspr4 missing) — reported as SKIPPED, with a static UX substitute, not hidden | repeated attempts, no apt rights | scripts/ui_smoke.py stays; limitations doc says so plainly |
| 14 | Reports briefly embedded "HEAD" as commit SHA (not a hash) and mis-credited test IDs by filename | first verify run | `git rev-parse --verify HEAD` with hex check; per-ID match on function name; reports re-issued |
| 15 | PERM-4 regex flagged decorators/method calls as stray SQL | first PERM-4 run | regex rewritten to full clause shapes only; 0 false positives in 5 consecutive runs |

**Known-open at submission:** licence (N1, D3); deployed link ([ADD]); admin claim-text deviation (N1-5); oversized-upload backpressure beyond per-file cap (streaming); SQLite durability under power loss (WAL mitigates, not proven); raw excluded channels remain on disk ([SYNTHETIC_DATA.md](SYNTHETIC_DATA.md)).
