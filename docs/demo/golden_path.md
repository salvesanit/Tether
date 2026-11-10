# Golden path — the four-minute demo, step by step

Every step states the expected result. Screenshots are [ADD — capture on a desktop with chromium]; this sandbox has no browser, and every step below was instead verified over HTTP by `scripts/judge_walkthrough.sh` (twice consecutively — see [golden_path_run.md](golden_path_run.md)).

**Preconditions.** `pip install -r requirements.txt && python3 scripts/seed.py && python3 run.py`. Open `http://localhost:8000`. DEMO_MODE=true. (Synthetic data only.)

| Step | You do | Expected |
|---|---|---|
| DM-1 Connect | Start screen → Aster demo → Connect | Source list: repo bundle, issues/PRs JSON, 15 notes, chat.json — labels preset (notes mixed open/confidential/restricted, chat internal); `chat.json · #hr-leave` and `chat.json · #private-aarav` shown **not read** with reasons. Consent box ticked and logged. Gate 1: press **Clear labels** → gate passes, state `labelled`. |
| DM-1b Rebuild | Press rebuild | Run report: spans 165 · candidates 82 · kept 60 · dropped **21** (all `quote_not_found`; openable dropped list) · conflicts **6** · gaps **6 (+1 suggested, not counted)** · quarantine **1** · redactions **5**. |
| DM-2 Prove | Open any claim → **citation** | The quote is highlighted inside its source line; the locator resolves character-for-character; opening a span of a claim you may not read (successor) returns 403. |
| DM-3 Correct | Review → Conflicts tab | Six conflicts, both sides with locators. Decide one — value + typed reason required. Confirm the uncertain claims (confidence < 0.80 — chat-sourced). Then **Sign off**: Gate 3 checklist goes green → Sign → freeze `v1.0` with SHA-256 (`signed by Sanit Salve`). |
| DM-4 Restrict | Switch role → Diya Raman (successor) → Handover | Six sections in risk order; every line with a citation chip; restricted material appears only as **one plain notice** — no title, no count. The review queue routes 403. Her **Receipt** button logs the loop-closing row. |

**Timings.** Target under 5 minutes for a cold reader (Target, not measured). The scripted path takes ~2 s machine time (rebuild + 60 confirms + 6 decisions + 6 assignments + sign + share + receipt) — `make judge`.

**If something differs.** Counts are the contract: see [reports/check_report.json](../../reports/check_report.json) for this commit. A different number means the fixture snapshot changed — `make record` regenerates `fixtures/llm/`; commit the diff.
