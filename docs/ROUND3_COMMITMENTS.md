# Round 3 commitments — implementation status

The Round 2 brief's "last section" (which lists the three improvements to carry forward) was not included in this build's copy of the brief — the three below were proposed from this build's own recorded gaps. Implementation is delivered, but N1's policy approval remains separate ([N1_DECISIONS.md](N1_DECISIONS.md) N1-14). Exact changes and verification boundaries are in [ROUND3_DELIVERY.md](ROUND3_DELIVERY.md).

## 1. Database-enforced row security (PostgreSQL + RLS)
**Problem.** The one read path is application-enforced; a bug in a filter is a leak. Round 1 declared RLS; this build documents its absence instead ([LIMITATIONS](LIMITATIONS.md), [decisions/0001](decisions/0001-sqlite-over-postgres.md)).
**Design delivered.** PostgreSQL migrations `002_postgres_rls.sql` and `003_postgres_version_views.sql`; transaction-local role context; forced policies on the six planned tables plus audience-filtered signed version views; SQLite remains the local fallback.
**Files.** `db/migrations/002_postgres_rls.sql` · `db/migrations/003_postgres_version_views.sql` · `backend/app/db/read_path.py` · `docker-compose.yml` · `.github/workflows/ci.yml`.
**Tests.** PERM-1 and PERM-5 are configured for PostgreSQL CI; local SQLite regression coverage passes. Operational PostgreSQL CI remains to be observed.

## 2. Browser-proven journey in CI (E2E-1 unskipped + axe-core)
**Problem.** E2E-1 authored but SKIPPED (no libnspr4 here); a11y claims are static-only. Usability is 10 points of rubric.
**Design delivered.** CI installs Chromium and system libraries, requires the browser test rather than permitting a skip, runs the journey twice from a clean database, and invokes axe-core on the five main screens for critical/serious WCAG A/AA violations.
**Files.** `backend/tests/test_e2e1_ux1.py` · `scripts/ui_smoke.py` · `.github/workflows/ci.yml` · `docs/TESTING.md`.
**Tests.** Syntax and SQLite tests pass locally. Chromium download was unavailable here, so CI must provide the browser pass evidence.

## 3. Live-model verification, reported separately (`make verify-live`)
**Problem.** Replay proves the plumbing; whether a real hosted model keeps real facts is unknown here — and honesty requires separate reports, never merged ([TESTING](TESTING.md)).
**Design delivered.** `make record-live` stores real model fixtures in their own directory and refuses incomplete recordings. `make verify-live` uses separate databases and provenance filters, writes a separate `reports/verify_live.md` with counts and a 25-item N1 spot-check, and returns nonzero when exact-text fact-count divergence exceeds two. Model id and prompt version are attached to the run.
**Files.** `scripts/verify_live.py` · `scripts/record_fixtures.py` · `backend/app/llm/adapter.py` · `Makefile` · `backend/tests/test_live_verify.py`.
**Tests.** The divergence threshold is unit-tested. A live report requires an approved key and recorded model fixtures; neither is present here, so no model result is claimed.
