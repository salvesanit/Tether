# Later — parked as P2 (not in this build)

- Live GitHub read-only reader behind the same reader interface (P1 in the plan; extends `backend/app/readers/`).
- pgvector subject matching between claims; falls back to trigram similarity. (Name/ID matching first, always.)
- Deployed link (Vercel/Fly.io + Supabase free tier) — needs accounts this build does not hold. [ADD]
- Ten-claim spot-check tool for the reviewer.
- Timeline of decisions view.
- Automatic 30-day expiry sweep (retention job) — currently 30d default + one-click admin delete, but no sweeper process.
- Real authentication (SSO/OIDC) replacing the DEMO_MODE role switcher.
- Per-person row erasure automation (today: logged request + admin removes rows).
- Suggested-gap subjects executed automatically (today they show as `suggested`, never counted — by design).
- Interview/survey results (instruments are written; nothing has been run — [docs/feedback/](feedback/)).
- axe-core run on the five screens; E2E-1 unskipped in CI with chromium present.
- `make verify-live` writing a separate live-mode report (never merged into the replay reports).
