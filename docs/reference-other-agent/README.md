# External reference — another agent's Tether build (archived unmodified)

**What this is.** On 2026-11-09/10 the team uploaded the output of a *different* AI agent that was asked to build the same Round 2 brief: its 12-document suite and six screenshots (`screenshots/`, plus `r1-desktop`, `r2-connect`, `r3-rebuild`, `r4-review`, `r5-citation-inspector`, `r6-successor-handover`). The trigger was a UI re-skin that looked close to, but better than, the previous left-rail layout. The team asked for that look to be ported onto this repository's working app.

**What it is not.** It is not this project, was not built by this team, and **its source code was never provided** — only documentation and screenshots. Nothing here is verified by running it. Nothing in this directory is executed by the build, the tests, or CI.

**Precedence.** Where this directory and the rest of the repository disagree, the repository wins. These files are archived as *unmodified originals* so the comparison is honest. They must never be cited as evidence about this build.

**What was adopted (with corrections):**
- The layout language — top bar + horizontal gate stepper — was re-implemented in `frontend/` (no backend change). See `docs/CHANGES_FROM_ROUND1.md` #17.
- The dark theme — charcoal & ink with green/amber/red semantics — replaced the pure B&W dark mode. Colour mode is unchanged.
- Their document structure for `docs/ARCHITECTURE.md` (three numbered figures) was ported with the stack corrected to this build (FastAPI + SQLite single read path, built-in scanners — not React/Express as written here).
- Their disclosure table column layout (component · author · verification) was adapted into `docs/AI_DISCLOSURE.md` with real module paths and test IDs.

**Defects found in the reference (honest, with evidence):**
1. `PLAN_VS_BUILD.md` claims "6 of 6 planted contradictions surfaced"; their own `r3-rebuild.png` shows **Conflicts Surfaced (CK-3): 4**. Two of six planted conflicts missing against the answer key.
2. `N1_DECISIONS.md` ships every box pre-ticked, including **MIT licence approved** and all confidence ceilings. This repository's truthful record is the opposite: licence decision is **pending/blocked (N1-8, D3 blocked)** and the extra ceilings are unapproved defaults — see `docs/N1_DECISIONS.md` here.
3. `AI_DISCLOSURE.md` attributes authorship to "Google AI Studio Agent — Gemini 2.5 Flash / **Gemini 3.8 Flash**", and `DISCLOSURES.md` claims React 19 / Vite 8 / Express / Tailwind. None of that stack exists here; the commands it prints (`npx tsx --test tests/tether.test.ts`, "21 verification tests") cannot run — there is no Node toolchain in this build and our suite is 48 passed, 1 skipped (pytest).
4. Roles in its judge guide are "**Successor Jordan Lee**" and "**Admin Morgan Chen**" — people who exist nowhere upstream. The synthetic people in this build are Aarav Mehta, Sanit Salve, Diya Raman, Krushna Patil (and the Aster demo cast, all marked synthetic).
5. Its judge guide claims incompatibility with hermetic offline runs in spirit — it assumes `localhost:3000` dev server and npm tooling; this build is one Python process and works fully offline.
6. `r5-citation-inspector.png` shows the citation highlight extending **past** the exact quote into the following `### Deployment Calendar` markdown heading — a highlight-overshoot bug (HR-1 visual contract broken). Our implementation highlights exactly `indexOf(quote)` and nothing more.
7. Their claimed theme is "minimalist charcoal/pure-white" yet every screenshot renders green/amber/red accents — their docs describe a build they didn't ship.
8. `LIMITATIONS.md`/`RELIABILITY.md` (the better parts) also list a "Gitleaks scanner" — no gitleaks binary is or was used here; secrets redaction is our built-in regex scanner (`backend/app/pipeline/clean.py`, SEC-2).
9. Root-level `AGENTS.md`/`JUDGE_GUIDE.md` there reference `/p/proj_beacon_demo/*` routes and a `/judge` path under npm auspices; this build serves the same journey at `http://localhost:8000/` with a Python server (`python3 run.py`).
10. Counts there (60 kept / 20 dropped fakes / 6 gaps) partially match luck/fixtures, not a stated shared methodology; this repository's reports are generated from the real pipeline (see `reports/`).

**Duplicates.** The two `media_*.png` files the team also uploaded are byte-identical to `r6-successor-handover.png` and `r5-citation-inspector.png` respectively (sha256 verified) and are not copied here a second time.

**Licence of this archive.** The reference documents remain the other agent's output, reproduced here solely for comparison under the event's evaluation. This repository's own licence decision remains pending N1's call (`docs/N1_DECISIONS.md`); nothing in this archive grants any rights to this repository's content.
