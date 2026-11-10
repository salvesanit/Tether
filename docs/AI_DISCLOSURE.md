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

**Not done:** no model was trained or fine-tuned; no user data exists; no interviews or surveys have been run — see [feedback/results.md](feedback/results.md), whose fields read [ADD: real results].
