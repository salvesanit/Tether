# Tether

Tether keeps what a leaver knows tied to the team: one signed handover in which every line can be checked against its source, and a named person has signed. It is for a two-person team handing one project over — a lead on two weeks' notice, a successor joining cold — and this repository is the Round 2 prototype of it. It proves the central workflow end to end on a synthetic project: sources connect, claims are rebuilt and checked against exact quotes, a named reviewer decides and signs, and the successor opens a role-filtered handover.

**Judge:** open [docs/JUDGE_GUIDE.md](docs/JUDGE_GUIDE.md) first. In a hurry? The next block is the whole loop.

## 60-second quickstart

```bash
pip install -r requirements.txt
python3 scripts/seed.py          # loads the synthetic Aster project through the upload path
python3 run.py                   # serves http://localhost:8000
```

(The Round 2 brief's start is `docker compose up --build` then `make seed` — see Rule 2 under [Limitations](docs/LIMITATIONS.md): no Docker daemon exists in the build sandbox, so the Dockerfile/compose are provided but untested here. `make run` is the verified path.)

Then, in the browser at `http://localhost:8000`:

1. Sign in as **Sanit Salve** (reviewer) — the role switcher is top-right (DEMO_MODE only).
2. **Connect** → the manifest labels are preset; two channels are shown as never read. Press **Clear labels** (Gate 1).
3. **Rebuild** → the run prints claims kept, dropped, conflicts, gaps.
4. **Review** → confirm claims, decide the six conflicts, assign the six gaps.
5. **Sign off** → the three gates go green; **Sign** freezes `v1.0` with a SHA-256.
6. Switch role to **Diya Raman** (successor) → **Handover** → six sections, citations, one plain restriction notice.

Scripted equivalent, end to end on a throwaway database:

```bash
make judge      # scripts/judge_walkthrough.sh — DM-1 to DM-4, ~2 seconds, never touches tether.db
make verify     # full suite + reports/verify.md (counts only)
```

## What this build proves

| Capability | Status | Evidence |
|---|---|---|
| Claims rebuilt from three source types with character-for-character quote check (CK-1) | Verified by test | `backend/tests/test_ck1_quote.py` · [reports/verify.md](reports/verify.md) (CK-1 PASS) |
| Every one of the 20 planted fakes dropped and counted | Verified by test | [reports/answer_key_report.md](reports/answer_key_report.md) · `test_ck1_*` |
| All 61 planted facts found (16 of 16 decisions) | Verified by measurement | [reports/answer_key_report.md](reports/answer_key_report.md) |
| Confidence ceilings by source type (CK-2) | Verified by test | `backend/tests/test_ck2_caps.py` · `backend/app/config.py` |
| Conflicts shown both-sides, never settled by code (CK-3) | Verified by test | `backend/tests/test_ck3_conflicts.py` |
| Exactly the 6 planted gaps listed, each with owner + next step (CK-4) | Verified by test | `backend/tests/test_ck4_gaps.py` |
| Signing freezes the version; gates enforced server-side with 409 + log row | Verified by test | `backend/tests/test_rev1_gates.py` · walkthrough output |
| Successor cannot read restricted/confidential text on any route or export (PERM) | Verified by test | [reports/leak_test_report.md](reports/leak_test_report.md) · `test_perm1_leak_successor.py`, `test_perm2_perm3_perm4.py` |
| Honeytokens never leave the excluded channels; secrets redacted pre-storage (SEC-1/2) | Verified by test | `backend/tests/test_sec.py` (SEC-1, SEC-2, SEC-3) |
| Planted prompt injection is quarantined, changes no gate (SEC-3) | Verified by test | `backend/tests/test_sec.py` (SEC-3) |
| Changed input changes output (rules fallback extractor; IN-1) | Verified by test | `backend/tests/test_in1_input_change.py` |
| Four-minute path end to end | Partial — scripted equivalent runs twice in a row; Playwright E2E skips honestly (no libnspr4) | `scripts/judge_walkthrough.sh` · [docs/demo/golden_path_run.md](docs/demo/golden_path_run.md) · [docs/TESTING.md](docs/TESTING.md) |
| Live hosted-model extraction (`LLM_MODE=live`) | Partial — adapter + call-site implemented, never executed (no key in the sandbox); replay proves the plumbing, not model quality | `backend/app/llm/adapter.py` |
| Admin: export, log, delete | Partial — implemented; no regression test yet; no percentage or score claims anywhere | `backend/app/api/main.py` |
| Delete/retention request rows | Partial — 30-day default enforced at project level; per-person erasure is a logged request, admin removes the rows | `docs/LIMITATIONS.md` |
| Docker one-command start | Planned for the judge environment — authored, untested here ([deviation recorded](docs/LIMITATIONS.md)) | `Dockerfile`, `docker-compose.yml` |
| Deployed URL | Planned | [ADD — once the public repo and host exist] |
| Interview/survey/ten-question timings | Planned — instruments written, results not invented | [docs/feedback/](docs/feedback/) |

Counts only — never a loss rate, never a percent of knowledge captured. In replay mode the model call is recorded, so the reports show that the checks and the plumbing work — not that the model is good.

## One vocabulary

Claim · source · span · locator · label · status · conflict · gap · version · receipt — one line each in [docs/GLOSSARY.md](docs/GLOSSARY.md). Terms come from `backend/app/config.py`, the one constants module.

## Judge-facing documents

- [docs/JUDGE_GUIDE.md](docs/JUDGE_GUIDE.md) — the entry point: rubric rows mapped to commands
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) + [docs/decisions/](docs/decisions/) — system, data flow, state machine, evidence model, decision records
- [docs/WALKTHROUGH.md](docs/WALKTHROUGH.md) — one request travels through the code, file by file
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — what does not work; read this before the demo
- [docs/SYNTHETIC_DATA.md](docs/SYNTHETIC_DATA.md) — the method behind Aster and its answer key
- [docs/TESTING.md](docs/TESTING.md) — what each test proves and the latest result
- [docs/demo/golden_path.md](docs/demo/golden_path.md) — the four-minute path with expected results
- [docs/demo/golden_path_run.md](docs/demo/golden_path_run.md) — recorded passing run (SHA, date, duration)
- [reports/verify.md](reports/verify.md) · [answer_key_report.md](reports/answer_key_report.md) · [leak_test_report.md](reports/leak_test_report.md) · [check_report.json](reports/check_report.json)

## Status

Iteration round 2 of 3. Everything is built inside the Round 2 build window; history shows one working codebase, `git log --oneline`. Licence: **pending N1's choice** — see [docs/N1_DECISIONS.md](docs/N1_DECISIONS.md). Demo data is synthetic: nothing here describes a real company.

*CI:* `.github/workflows/ci.yml` runs the suite and `scripts/verify.py`. Badge: [ADD — add the shields URL once the repo is public].
