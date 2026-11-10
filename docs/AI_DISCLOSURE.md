# AI disclosure — which tool wrote which part, and what a person checked

Required by the event rules (6 and 7) and the Round 2 brief. This file must match the commit history: every commit after the initial one is listed below or it does not exist.

**Tool.** The build was produced with Arena Agent Mode (an agentic coding harness), by models inside it — including Claude-family models; the harness does not expose a single model string. The two humans are Sanit Salve (N1, leader, reviewer — owns approvals and the sign-off) and Krushna Patil (N2, builder).

**Authored with agent assistance, reviewed by the team:**
- All of `backend/`, `frontend/`, `scripts/`, `db/`, `schemas/`
- All of `docs/`, all of `reports/`, README, AGENTS.md, llms.txt, Makefile, Dockerfile, docker-compose.yml, .github/workflows/ci.yml
- The synthetic demo project (`data/demo_project/`) and the handwritten replay fixtures (`fixtures/llm/`, provenance `handwritten-reference`)
- The answer key (`data/demo_project/answer_key.json`)

**Person-by-person:**
- Krushna (N2) directed the build conversation, ran the commands, made the scope calls (FastAPI + SQLite single process, no Docker daemon in the sandbox), and is accountable for the code. [ADD: list any file N2 retyped by hand]
- Sanit (N1) owned: the claim model boundary (model proposes, never decides), the label matrix and its open deviation ([N1_DECISIONS.md](N1_DECISIONS.md)), the leak-test sentinels, the sign-the-version gate, and this disclosure. [ADD: N1's review notes for the final checkpoint]

**What was written by a person without agent assistance:** nothing in-repo claims to be — all files descend from agent-assisted drafts; the decision of record (keep vs revert the wrong-locator fixture placement; the union fix; the fail-closed span gate; the leaver-boundary correction in the leak probe) was made in-review and is visible in `git log`.

**Component × author × verification** (table format adapted from the external reference build, filled with this repository's real modules and test IDs — never its claims):

| Component / file | Primary author | Human reviewer | Verification method |
| :--- | :--- | :--- | :--- |
| Claim model & constants (`backend/app/config.py`) | Arena Agent Mode (agent) | Krushna Patil (N2) | 7 claim types; CK-1/CK-2 suites |
| Locators & readers (`backend/app/readers/readers.py`) | agent | N2 | `RD-1` locator resolution; `RD-2` malformed/empty |
| Cleaner & scanners (`backend/app/pipeline/clean.py`) | agent | Sanit Salve (N1) | `SEC-1` honeytokens; `SEC-2` redactions; `SEC-3` injection quarantine; `SEC-4` upload ceiling |
| Quote check & caps (`backend/app/checks/`) | agent | N2 | `CK-1` (60 kept / 20 fakes dropped); `CK-2` ceilings; `CK-3` 6/6 conflicts, 0 machine-settled; `CK-4` 6/6 gaps |
| Ledger & single read path (`backend/app/db/read_path.py`, hash-chained log) | agent | N1 | `PERM-1..4` leak tests + [reports/leak_test_report.md](../reports/leak_test_report.md) |
| Synthetic dataset & answer key (`data/demo_project/`) | agent + NightOwls | N1 | `KEY-1`; `AK-1` answer-key walk (61 planted, 16 decisions) |
| UI & themes (`frontend/`) | agent | N2 | `UX-1` (landmarks, focus, reduced-motion); no automated visual test — screens verified by hand in the preview |

**Not done:** no model was trained or fine-tuned; no external model API was called at any point in this build (no key existed; replay fixtures are handwritten-reference); no interviews or surveys have been run — see [feedback/results.md](feedback/results.md), whose fields read [ADD: real results].
