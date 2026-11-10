# Ten fixed questions about Aster — with answers from the answer key

Marking: N1 and N2 time themselves answering from the raw sources, then (if time allows) again with the signed handover. Results: [ADD: real results] with timings. All content below is synthetic; answers cite locators.

| # | Question | Answer (from `answer_key.json`) |
|---|---|---|
| 1 | Why is the database PostgreSQL? | Chosen over MongoDB to keep table joins. Decision D-01 — `notes/2026-08-12.md#P2`. |
| 2 | Which day are we deploying? | Sources conflict: notes say Fridays after 6pm (`notes/2026-08-12.md#P3`); chat says Thursdays now (`chat:#dev@1757846400.101`). The machine does not settle it — the reviewer does. (conflict X-01) |
| 3 | What is the production rate limit? | 100 req/min in code (`config/ratelimit.yml#L1-2`) vs 60 req/min in a note (`notes/2026-09-03.md#P1`) — conflict X-02; person decides, both sides visible. |
| 4 | Who owns notifications? | Conflict X-06: Priya ("she has the keys", `chat:#dev@1759776000.104`) vs Rohan ("Owner update: Rohan owns notifications.", `issue:15#c2`) — the reviewer picks and signs. |
| 5 | What does Aster need to build and run? | Node 20 LTS (`README.md#L3-3`) · Postgres 16 primary store (`src/db.js#L1-23`) · Redis 7 job queue (`src/queue.js#L1-7`) — dependency claims, each with its locator. |
| 6 | Which risks involve payments? | Payment webhook has no idempotency keys (chat, `#dev@1760385600.105`) · staging DB might drift from prod schema (`notes/2026-09-03.md#P3`). Ranked by the estimate rule only — never by gut. |
| 7 | Where are the production credentials? | Nowhere in the sources — that is the gap. The gap row for accounts and credentials carries owner **Aarav Mehta** (leaver) and next step **ask in week 1**. Never a guessed answer. |
| 8 | Which successor-needs subjects have NO evidence at all? | Accounts and credentials · third-party services and vendors · data and backups · contacts · deadlines · access — the six planted gaps (CK-4). The other six are covered. |
| 9 | What did we reject, and why? | MongoDB (joins, D-01) · sha256 (bcrypt, D-12) · Heroku (cost, Fly.io, D-13) · WebSockets (SSE, D-14) · auto-increment integer keys (UUIDs, D-15) · Elasticsearch (footprint, Meilisearch, D-16). |
| 10 | What should a cold successor do first? | Open the handover, read **Own first** (risk-ordered with the rule shown), then **Dependencies and accounts**, then the unknowns list — each item has an owner to ask next. |

Honesty rule for scoring: N1 and N2 record their own times; nothing here is a result until it happens.
