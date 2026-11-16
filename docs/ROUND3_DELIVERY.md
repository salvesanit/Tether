# Round 3 delivery — implementation and verification

This delivery implements the three improvements proposed in [ROUND3_COMMITMENTS.md](ROUND3_COMMITMENTS.md). N1's policy approval is still separate: code delivery does not silently approve any item in [N1_DECISIONS.md](N1_DECISIONS.md).

## 1. PostgreSQL row-level security

- SQLite remains the zero-setup local default; set `TETHER_DATABASE_URL` to select PostgreSQL through the existing `db/read_path.py` boundary.
- PostgreSQL migrations create the existing schema, force RLS on sources, spans, claims, evidence, versions, and the audit log, and scope each database connection to the HTTP request's role using a transaction-local setting.
- The successor and leaver receive pre-filtered, immutable version views; the base signed payload is blanked in PostgreSQL so direct access to the versions table cannot bypass the audience filter.
- Docker Compose provisions PostgreSQL and a non-superuser, `NOBYPASSRLS` application account. Migrations run as that account; the application does not use a superuser.
- CI runs PERM-1 and PERM-5 against PostgreSQL, including checks of the session role, database principal, forced policies, and the signed-version disclosure boundary.

The role is still the prototype's `X-Tether-Role` demo value, not a verified identity. RLS enforces the role supplied by the app; it does not turn the demo switcher into authentication. Add real authentication before deployment.

## 2. Browser journey and accessibility checks

- CI installs Playwright Chromium and its Linux dependencies, sets `REQUIRE_E2E=1`, and runs the clean-start browser journey twice. In this required CI mode, inability to launch Chromium fails the test instead of silently skipping it.
- The journey checks the five primary screens (Connect, Reconstruct, Review Queue, Sign-Off, Successor View) with axe-core and fails for any critical or serious WCAG 2 A/AA or WCAG 2.1 A/AA violations.
- The documented scripted judge path remains available as a separate deterministic check.
- Frontend source checks explicitly read UTF-8 so accessibility tests also work on Windows installations using legacy default encodings.

## 3. Live-model verification, isolated from replay

- `make record-live` records actual model responses under `fixtures/llm/model/`; it refuses to label rules fallbacks as live recordings and leaves handwritten reference fixtures untouched.
- `make verify-live` uses separate throwaway databases to compare model fixtures and handwritten-reference fixtures against the same synthetic answer key. It reports counts and a 25-item answer-key spot-check for a person to assess.
- A difference of more than two exact-text answer-key facts exits non-zero and marks the report **REVIEW REQUIRED**. This report is never merged into the replay verification report.
- Run metadata records the configured model id and prompt version. The report is not generated until real model fixtures exist; no credentials or hosted-model quality are fabricated.

## Plan changes and verification boundary

The original Round 3 plan proposed a single SQLite fallback and specified only six RLS tables. Implementing forced policies exposed an additional path: the signed JSON payload itself contained claims for every audience. PostgreSQL now stores a non-disclosing base version plus audience-specific filtered views, and applies the same forced policy to those views. The build remains demo-authenticated; real SSO, license approval, live-model assessment by N1, and production hosting remain outside this prototype.

This Windows environment does not have Docker, PostgreSQL, or a downloadable Playwright browser. The SQLite regression suite passes locally; PostgreSQL PERM-1/PERM-5 and required browser/axe tests are configured as CI gates but must pass on GitHub Actions before the database/browser commitments can be called operationally verified. See [CI workflow](../.github/workflows/ci.yml) and [Testing](TESTING.md).
