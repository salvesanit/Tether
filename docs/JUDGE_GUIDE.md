# Judge guide — Tether, Round 2

Start here. Every entry below is a command or a file — nothing to take on trust.

## Sign in

The browser has a role switcher (DEMO_MODE only): **Aarav Mehta** (leaver), **Sanit Salve** (reviewer), **Diya Raman** (successor), **Krushna Patil** (admin). All four are synthetic people; the demo project is Aster, a campus club events app.

For API calls, send one header instead (`make demo-tokens` prints these):

```bash
curl -H "X-Tether-Role: reviewer" http://localhost:8000/api/health
```

## Rubric rows → what to open

| # | Criterion | Open / run |
|---|---|---|
| Core workflow (30) | End to end, connect → handover | `make judge` → [docs/demo/golden_path_run.md](demo/golden_path_run.md). Or the UI: README "60-second quickstart". Expected counts: spans 165 · candidates 82 · kept 60 · dropped 21 |
| Technical depth & reliability (25) | Real parsing, validation, access control, error handling | `make verify` → [reports/verify.md](../reports/verify.md) (per-ID PASS/FAIL), [reports/leak_test_report.md](../reports/leak_test_report.md), [docs/RELIABILITY.md](RELIABILITY.md), `backend/tests/` (47 tests, 1 honest skip) |
| Progress vs the plan (20) | Each Round 1 commitment marked Done/Partial/Changed/Deferred | [docs/PLAN_VS_BUILD.md](PLAN_VS_BUILD.md) with evidence paths · [docs/CHANGES_FROM_ROUND1.md](CHANGES_FROM_ROUND1.md) |
| Three improvements proposed (15) | Round 3 commitments | [docs/ROUND3_COMMITMENTS.md](ROUND3_COMMITMENTS.md) |
| Usability (10) | Next step is obvious to a cold reader | The live preview at :8000, or run locally; `UX-1` checks in `backend/tests/test_e2e1_ux1.py`; [docs/demo/golden_path.md](demo/golden_path.md) |
| D2 — reachable demonstration | Docker package; deployed link | Docker: authored, untested here ([deviation](LIMITATIONS.md)). Deployed URL: [ADD]. Scripted path: `make judge` |
| D3 — public repo | Clean history, licence | Licence: **pending N1's decision** — see [docs/N1_DECISIONS.md](N1_DECISIONS.md). History: `git log --oneline` |
| D4 — updated project document | Architecture, data flow, decisions | [docs/ARCHITECTURE.md](ARCHITECTURE.md) + [docs/decisions/](decisions/) |
| D5 — APIs, models, datasets, libraries, services | Disclosure files | [docs/DISCLOSURES.md](DISCLOSURES.md), [docs/AI_DISCLOSURE.md](AI_DISCLOSURE.md) |
| D6 — features + testing evidence | Reports and feedback instruments | [docs/PLAN_VS_BUILD.md](PLAN_VS_BUILD.md), [docs/TESTING.md](TESTING.md), [docs/feedback/](feedback/) |
| D7 — three Round 3 improvements | Problem/design/tests/risk | [docs/ROUND3_COMMITMENTS.md](ROUND3_COMMITMENTS.md) |

## Walk the central workflow yourself (~4 minutes)

1. **Connect.** `http://localhost:8000` → Connect. The Aster sources are listed with labels; `#hr-leave` and `#private-aarav` show `not read` with the reason. Press **Clear labels**.
2. **Rebuild.** Press rebuild. Expect: 165 spans · 82 candidates · 60 kept · 21 dropped (all `quote_not_found`, listed in the dropped list) · 6 conflicts · 6 gaps · 1 quarantined chunk · 5 redactions.
3. **Prove.** Open any kept claim → **citation**. The quote is highlighted inside its source line; the locator resolves character-for-character (RD-1).
4. **Review & sign.** Review → work the queue: 60 confirmations, 6 conflict decisions (both sides visible — you pick), 6 gaps (owner + next step each). Then Sign off — the gates require all conflicts decided and no uncertain item left unsettled. Gate 3 signs `v1.0` with a SHA-256.
5. **Handover.** Switch to Diya Raman (successor) → Handover. Six sections in risk order; every line carries a citation chip; restricted material is filtered server-side and appears only as one plain notice; **Receipt** logs that she got it.

## Verify any claim, the Tether way

Open the claim → click **citation** → the quote must be an exact substring of the span. Or at scale:

```bash
python3 -m pytest backend/tests/test_rd.py -q    # every locator on every claim resolves (RD-1)
python3 scripts/verify.py                         # everything, with per-ID results
```

## Upload your own authorised files

A judge can click **Use your own authorised sources** on the start screen. Accepted: a git bundle or a zip of a repository, `issues.json`, `prs.json`, Markdown notes, `chat.json`, plus a `manifest.json` with per-source labels and excluded channels. Consent is one untickable-until-ticked box (GDPR-style wording is in the UI); the tick is logged. Formats: [docs/INPUT_FORMATS.md](INPUT_FORMATS.md). Empty or malformed files are rejected with a plain error, never a stack trace (RD-2).

## What is not built

Two source readers exist (notes, chat) plus issues/PRs from JSON; a live GitHub reader is P1 and not in this build. Playwright E2E skips honestly on this machine (no chromium system lib); axe-core has not been run (the static a11y checks pass, that is all that is claimed). Details: [docs/LIMITATIONS.md](LIMITATIONS.md).
