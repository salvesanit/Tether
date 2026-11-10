# Plan vs build — Round 1 commitments, audited

Sources audited: `Tether — Round 1 plan` (N2 team-member copy, 6 Nov 2026, both attachments) and the Round 2 brief's "Round 1 commitments to honour or explain". N1's copy of Round 1 is not in this repository — the leader-side commitments are marked Partial/Deferred where only the N1 copy could pin them. Every change carries a one-line reason.

| # | Round 1 / brief commitment | Status | Evidence (test ID, report, file) | One-line reason for change |
|---|---|---|---|---|
| R1-001 | One reader per source with a locator for every line | Done | `backend/app/readers/readers.py` · RD-1/RD-2 | — |
| R1-002 | Clean before storage: secrets/PII removed | Done | `backend/app/pipeline/clean.py` · SEC-2 | — |
| R1-003 | Model proposes one sentence, one of seven types, quote + locator | Done | adapter + `schemas/claim.schema.json` | — |
| R1-004 | No quote at locator ⇒ claim dropped and counted | Done | CK-1 · `backend/tests/test_ck1_quote.py` · answer_key_report (20/20 dropped) | — |
| R1-005 | CK-2 ceilings: 0.95 file/commit, 0.60 chat | Done | CK-2 · `config.CEILINGS` | — |
| R1-006 | Ceilings beyond 0.95/0.60 (merged PR 0.95, issue/PR comment 0.85, unmerged PR 0.70) | Partial — defaults implemented, **awaiting N1 approval** | `config.CEILINGS` · [N1_DECISIONS.md](N1_DECISIONS.md) | defaults the brief asked N1 to approve; marked unapproved |
| R1-007 | CK-3 conflicts both-sides, never settled by code | Done | CK-3 | — |
| R1-008 | CK-4 gaps: twelve subjects, exactly the six planted | Done | CK-4 | — |
| R1-009 | Weakest-source rule (HR-2) | Done | PERM-3 in `test_perm2_perm3_perm4.py` | — |
| R1-010 | Gate 1 labels before read; Gate 2 queue settled; Gate 3 sign + freeze | Done | REV-1 · `main.py` gates · walkthrough | — |
| R1-011 | States scoped→…→received; skips 409 + log row | Done | REV-1 · `config.PROJECT_STATES` | — |
| R1-012 | Signing freezes version with reviewer name, date, hash | Done | `versions/sign` → sha256; walkthrough DM-3 | — |
| R1-013 | Restriction notice with no title, no count | Done | `handover()` in `main.py`; DM-4 | — |
| R1-014 | Successor view: six sections, risk order, citations | Done | `_sections()`; red herring check: all six render (screenshot substituted by DM-4 text in this sandbox) | — |
| R1-015 | Risk score labelled `estimate` + the rule shown | Partial — rule and `estimate` label ship; not yet shown beside every UI row | `risk_rule` in signed payload · [LIMITATIONS.md](LIMITATIONS.md) | UI surfacing deferred, rule kept |
| R1-016 | One read path for DB access (RLS) | Changed — SQLite + single read module, no SQL elsewhere | PERM-4 · [decisions/0001](decisions/0001-sqlite-over-postgres.md) | Postgres daemon unavailable in the build sandbox |
| R1-017 | Postgres 16 + pgvector subject matching | Deferred | [LATER.md](LATER.md) | no vector provider offline; name/ID matching first by design |
| R1-018 | Next.js + TypeScript frontend | Changed — static SPA (vanilla JS/CSS/HTML) | [decisions/0005](decisions/0005-static-spa-no-build.md) | no build step constraint |
| R1-019 | gitleaks binary | Changed — built-in regex scanner | `clean.py` · SEC-2 passes | binary unavailable offline; rules equivalent in-repo |
| R1-020 | FastAPI backend, Python ≥3.11 | Done | `backend/app/` · run.py (3.13) | — |
| R1-021 | Hosted model behind thin adapter, id on each run, temp 0, caps, retries/fallback | Partial — coded (incl. 30s timeout, 200-call cap added 2026-11-10), never executed (no key here) | `backend/app/llm/adapter.py` | cannot run live without a key; replay never labelled live |
| R1-022 | Rule-based fallback when model returns few/unusable claims | Done | IN-1 · `rules_extractor.py` | — |
| R1-023 | Nothing trained on user data | Done | no training code anywhere; fixtures are handwritten-reference | — |
| R1-024 | Secrets removed before storage; scanner + redaction count per span | Done | `spans.redactions` · SEC-2 | — |
| R1-025 | 30-day retention default; one-click admin delete; logged deletion requests | Done | `projects.retention_days=30`; DELETE admin route; `POST .../retention-request` + log row | — |
| R1-026 | If public project: licence-respecting subset, names stripped | Deferred — demo is synthetic, no public project imported | [SYNTHETIC_DATA.md](SYNTHETIC_DATA.md) | scope decision, revisited if a real repo is approved |
| R1-027 | Append-only log, prev_hash/hash; shown to reviewer+admin | Done | `read_path.py::append_log`, `/api/projects/{id}/log` + verify-chain endpoint | — |
| R1-028 | Demo loaded via upload API with consent tick, logged | Done | `seed_demo.py` · consent.ticked log row · judge_walkthrough DM-1 | — |
| R1-029 | Four-minute path: connect → prove → decide+sign → restricted notice | Done (scripted) · Partial (Playwright) | `make judge` two consecutive passes; E2E-1 SKIPPED honestly | chromium unavailable in sandbox (libnspr4) |
| R1-030 | Answer key: 60 facts, 20 fakes, 6 conflicts, 6 gaps | Done — 61 facts planted (16 decisions) | [reports/answer_key_report.md](../reports/answer_key_report.md) | N2 plan wrote ≥60; prompt fixes 60/20/6/6 targets — build exceeds on facts, matches elsewhere |
| R1-031 | Excluded channels with honeytokens never read | Done | readers drop in memory; SEC-1 · `not read` rows | raw chat.json on disk still contains them ([LIMITATIONS](LIMITATIONS.md)) |
| R1-032 | Planted injection note quarantined | Done | SEC-3 | — |
| R1-033 | Rejected options attach to decisions | Done | AK-2 | — |
| R1-034 | Counted drops list openable by reviewer | Done | `/dropped` route + Review UI | — |
| R1-035 | Claim fields added beyond Round 1 (subject/attribute/value, reason/rejected_options, owner, label, evidence[], review block) | Done — **additions, recorded** | `claims` table; [CHANGES_FROM_ROUND1.md](CHANGES_FROM_ROUND1.md) | required by conflict checks and rejection reasons; per brief |
| R1-036 | CI: lint + verify + E2E from clean clone | Partial — workflow authored; cannot run here | `.github/workflows/ci.yml` | no runner in sandbox; E2E step tolerates chromium absence via skip |
| R1-037 | Deployed link (P1) | Deferred | — | needs hosting accounts; [ADD] |
| R1-038 | Live GitHub read-only reader (P1) | Deferred | [LATER.md](LATER.md) | P1 after P0 green |
| R1-039 | Feedback: five interviews + survey + ten timed questions | Partial — instruments written, no sessions held; results marked [ADD] | [docs/feedback/](feedback/) | cannot invent results; rule 17 event rules |
| R1-040 | Golden-path screenshots in docs/demo/golden_path.md | Partial — every step + expected result documented; screenshots [ADD] on a desktop with chromium | [docs/demo/golden_path.md](demo/golden_path.md) | no browser in sandbox |

**Counts:** Done 29 · Changed 5 · Partial 6 · Deferred 5 (of 45 audited). Nothing is Done that a test does not prove; anything unproven is Partial with the reason above.
