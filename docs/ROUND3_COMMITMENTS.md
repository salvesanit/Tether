# Round 3 commitments — three, real, each with problem, design, files, tests, risk

The Round 2 brief's "last section" (which lists the three improvements to carry forward) was not included in this build's copy of the brief — the three below are proposed from this build's own recorded gaps, each small enough to verify. N1 signs them into existence or they do not happen ([N1_DECISIONS.md](N1_DECISIONS.md) N1-14).

## 1. Database-enforced row security (PostgreSQL + RLS)
**Problem.** The one read path is application-enforced; a bug in a filter is a leak. Round 1 declared RLS; this build documents its absence instead ([LIMITATIONS](LIMITATIONS.md), [decisions/0001](decisions/0001-sqlite-over-postgres.md)).
**Design.** Port `db/migrations/001_init.sql` to Postgres; `ENABLE` + `FORCE ROW LEVEL SECURITY` on claims, evidence, spans, sources, versions, log; policies keyed off a per-request `app.role` setting set inside `read_path` transactions; SQLite stays as the dev fallback behind the same module.
**Files.** `db/migrations/002_rls.sql` · `backend/app/db/read_path.py` · `docker-compose.yml` (adds postgres service) · `.github/workflows/ci.yml` (service container).
**Acceptance tests.** `test_perm1_leak_successor.py` runs under Postgres in CI (PERM-1 green with RLS forced, not just app filters); a new `test_perm5_rls_forced.py` asserts `current_setting('app.role')` scoping directly; PERM-4 unchanged.
**Risk.** Dual-driver drift — mitigated by keeping SQLite dev-only and CI-enforced Postgres for merges; one week of migration honesty.

## 2. Browser-proven journey in CI (E2E-1 unskipped + axe-core)
**Problem.** E2E-1 authored but SKIPPED (no libnspr4 here); a11y claims are static-only. Usability is 10 points of rubric.
**Design.** CI job installs chromium + libnspr4; runs E2E-1 twice from a clean start; adds `@axe-core/playwright` on the five main screens; fixes critical/serious only (full AA audit stays N1's call).
**Files.** `backend/tests/test_e2e1_ux1.py` · `.github/workflows/ci.yml` · `docs/TESTING.md` (Section: main journeys).
**Acceptance tests.** E2E-1 PASS in CI (not skipped); UX-1 gains an axe run with zero critical/serious violations; `make judge` still green twice consecutively.
**Risk.** Flaky timing — mitigated by deterministic seeds and network-idle waits; a red CI blocks merge, never "passes with retry".

## 3. Live-model verification, reported separately (`make verify-live`)
**Problem.** Replay proves the plumbing; whether a real hosted model keeps real facts is unknown here — and honesty requires separate reports, never merged ([TESTING](TESTING.md)).
**Design.** With an N1-approved key: record live fixtures (`make record`), then `make verify-live` rebuilds from them and writes `reports/verify_live.md` — counts only, plus a 25-claim side-by-side spot check written by N1 vs the answer key. Model id + prompt version pinned in `runs`.
**Files.** `scripts/verify_live.py` (new) · `scripts/record_fixtures.sh` (extend) · `reports/verify_live.md` · `Makefile`.
**Acceptance tests.** Live report shows kept/dropped/fakes counts vs the same answer key; any divergence >2 facts from replay is a review item, not silently accepted; reports never mix.
**Risk.** Model drift between versions invalidates yesterday's live report — mitigated by pinning `LLM_MODEL` and regenerating on every prompt change; the replay reports remain the plumbing baseline.
