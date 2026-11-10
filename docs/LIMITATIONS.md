# Limitations — what Tether does not do

Read this before the demo. A short honest list scores better than a long proud one.

**Authentication is a demo switcher, not a login.** `DEMO_MODE=true` turns on the browser role switcher and treats `X-Tether-Role: <role>` as identity. Any caller can set that header — authorisation is real (server-side label filtering, gates, 409s) but authentication is not. A deployed Tether needs real SSO/OIDC in front of the same read path; that is not built. The switcher and the tokens exist only when `DEMO_MODE=true`.

**SQLite, not PostgreSQL with row-level security.** The Round 1 stack declared PostgreSQL 16 + pgvector + RLS behind one read path. This build uses SQLite with `db/read_path.py` as the only module that issues SQL (enforced by `test_perm2_perm3_perm4.py::test_perm4_one_read_path`), and row-level filtering in application code, plus a fail-closed citation rule on `/api/spans/{id}` (a span is readable only when at least one claim citing it is readable by the role). What is NOT proven here: database-enforced RLS, and Postgres concurrency behaviour. Deviation recorded in [docs/CHANGES_FROM_ROUND1.md](CHANGES_FROM_ROUND1.md) and [docs/decisions/0001-sqlite-over-postgres.md](decisions/0001-sqlite-over-postgres.md).

**Replay proves the plumbing, not the model.** `LLM_MODE=replay` returns recorded fixtures (`fixtures/llm/`, provenance `handwritten-reference`). It demonstrates that readers, the quote check, caps, grouping, gates and permissions work. It says nothing about how a hosted model would perform on fresh text. `LLM_MODE=live` is implemented in `backend/app/llm/adapter.py` (temperature 0, call cap, id stored on the run, rules fallback on failure) but has never been executed — there is no key in this environment.

**Reports carry counts, never percentages.** "60 of 61 planted facts found" is a measurement of the synthetic project. It is not a knowledge-capture rate, and no loss rate is stated anywhere (Galan (2023) shows the field cannot measure it).

**Browser coverage.** The Playwright end-to-end test (E2E-1) skips on machines without chromium system libraries — exactly this sandbox (no libnspr4). E2E-1 shows in [reports/verify.md](../reports/verify.md) as SKIPPED, not as a pass. The scripted four-minute path (`scripts/judge_walkthrough.sh`) does the same journey over HTTP and has passed twice in a row ([docs/demo/golden_path_run.md](demo/golden_path_run.md)). axe-core has **not** been run; keyboard operability and focus styles are checked statically only (UX-1). No a11y claim beyond that.

**Excluded chat channels are dropped in memory only.** The reader never stores `#hr-leave` / `#private-aarav`, they appear as `not read` in the source list, and their honeytokens never reach the database, logs, exports or API (SEC-1). But the raw `chat.json` **on disk** still contains those lines — copying the file out of `data/` would carry them. Deleting the file is the owner's responsibility; the app does not rewrite uploads on receipt.

**Role matrix deviation awaiting N1.** The spec's matrix has admin unable to read claim text by default (acting via reviewer path). This build's `ROLE_LABELS` gives admin read access to every label (mirroring reviewer) because the one-read-path enforcement is label-based. Logged as an open decision in [docs/N1_DECISIONS.md](N1_DECISIONS.md) — not silently changed.

**Receipts are minimal.** One row per (version, successor); no delivery semantics, no reminders, no UI beyond the one button.

**Retention and erasure.** Default 30 days, one-click project delete, and a logged request when a person asks for their rows. The log keeps the request, not the data. Automatic expiry sweeps are not implemented ([docs/LATER.md](LATER.md)).

**Admin has no claim text of its own in UI language.** Claim text is shown only on the reviewer/successor paths; admin screens show metadata, labels, retention and the log — but server-side label filtering does not currently withhold claim text from the `admin` role (same matrix deviation as above).

**No judge-facing hosting.** Deployed URL: [ADD]. Docker: `Dockerfile` + `docker-compose.yml` authored but untested in this sandbox (no Docker daemon); the verified start is `pip install -r requirements.txt && python3 scripts/seed.py && python3 run.py` (or `make run`).

**No real feedback yet.** The Round 2 feedback is instruments only: [docs/feedback/](feedback/) — interview guide, survey, ten questions, usability script, and a `results.md` with `[ADD: real results]` placeholders. No interviews have been run.

**Synthetic people only.** Aarav Mehta, Sanit Salve, Diya Raman, Krushna Patil are invented for Aster (synthetic). Any resemblance is accidental.

**What Tether refuses to claim.** No percentage of "knowledge captured". No loss rate. No ranking of people. No guessing who leaves next. No model-settled conflicts. No published handover that nobody signed.
