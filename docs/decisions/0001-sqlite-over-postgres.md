# 0001 — SQLite (+ one read path) instead of PostgreSQL + pgvector + RLS
Context: Round 1 declared Postgres 16, pgvector, gitleaks binary, Next.js. Build constraint from the team: one Python process, FastAPI + SQLite, no build step, verifiable in a Docker-less sandbox.
Decision: SQLite, WAL mode; `db/read_path.py` is the only module issuing SQL; PERM-4 test walks the tree and fails the build if SQL appears elsewhere; row-filtering in application code against the label matrix; span citations fail closed.
Alternatives rejected: Postgres+RLS now (no daemon, unverifiable here — a security control you cannot run is decoration); dual drivers (two code paths, no proof either works).
Consequence: database-enforced row security is NOT proven in this build; concurrency is single-writer; a data-volume or multi-user need forces the Postgres migration ([LATER](../LATER.md), [ROUND3_COMMITMENTS](../ROUND3_COMMITMENTS.md)). Recorded in CHANGES_FROM_ROUND1.
