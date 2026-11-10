# Walkthrough — one request, file by file

How either student can explain a request from the browser to the signed handover.

**The request:** Diya (successor) opens `/p/{id}/handover` the morning after Sanit (reviewer) signed `v1.0`.

1. `frontend/index.html` shells the app; `frontend/app.js` boots, reads the hash route `/p/{id}/handover`, and calls `api('/api/projects/{id}/handover')`. `api()` sets `Content-Type: application/json` (FormData excepted) and attaches `X-Tether-Role: successor` — in DEMO_MODE that header *is* the identity.
2. `backend/app/api/main.py` — the SPA catch-all `/{full_path:path}` sits **last** by construction, so `/api/...` wins first. `handover()` starts by resolving the role (`identity`) and then `_visible_version()`: project must exist; successor/leaver get 403 unless state ∈ signed/shared/received and a signed version exists — the gate is enforced before any payload leaves the server.
3. It loads `versions.payload` (computed at sign time), filters with `_filter_payload`: every item's `label` must be in `role_labels('successor')` = open, internal — restricted/confidential items are removed *here*, server-side, and the response carries `restricted_notice: "Some information is restricted for your role."` (no title, no count).
4. `_sections(filtered)` orders what remains by the risk estimate (rule in `risk_rule`, labelled `estimate`) and buckets into the six sections: Own first, Open work, Decisions and why, Dependencies and accounts, Repeated problems, What nobody knows.
5. `db/read_path.py` is the only module that talks to SQLite — every screen is served through it; `test_perm2_perm3_perm4.py::test_perm4_one_read_path` walks the tree and fails the build if SQL appears elsewhere.
6. The successor presses **Receipt** → `POST .../receipt` → one row in `receipts`, state → `received`, one `receipt.confirmed` log row (hash-chained). The leaver's loop is closed.

**The rebuild request** (`POST /api/projects/{id}/runs`, reviewer), same skeleton:

1. `main.py` guards role=reviewer, loads the project, demands state ∈ labelled/rebuilt/in review, then calls `pipeline/run.py::run_rebuild`.
2. `run_rebuild` pulls sources (must be `read` + labelled), and for each: `readers/readers.py` cuts text into **spans** with locators → `pipeline/clean.py` redacts secrets/PII to `[REDACTED:type]` (scanners run before anything is stored) → injection-like chunks become **quarantine** rows → spans persist via `read_path`.
3. Claims: `llm/adapter.py` — replay returns recorded fixtures keyed by prompt version + chunk SHA-256 (`fixtures/llm/`, provenance handwritten-reference); `live` would call the hosted model (temperature 0, call cap, id on the run); on any failure or no recording, the **rules** extractor runs and the run records `extractor: rules`. Output is validated against `schemas/claim.schema.json`.
4. Checks (plain code, `pipeline/…`, `app/config.py` ceilings): **CK-1** the quote must be an exact substring of the span its locator resolves to — a miss is dropped and counted. **CK-2** confidence capped per source type (file/commit 0.95 · PR/issue comment 0.85/0.70 · one chat message 0.60; verified floor 0.80). **CK-3** same subject+attribute, different values ⇒ conflict; both sides kept; nothing picked. **CK-4** the twelve successor-needs subjects with no kept claim ⇒ gap rows with owner + next step.
5. Claims land in `claims` with the **weakest label** among their evidence; evidence rows tie quote+locator+source label+capture time; conflicts link member claims; everything writes hash-chained `log` rows.
6. The response reports counts only (`spans · candidates · kept · dropped (dropped_by_reason) · conflicts · gaps · redactions · quarantined`) and the UI renders them on the Rebuild screen.

**File map**

```
run.py                     # start uvicorn on 0.0.0.0:$PORT
backend/app/api/main.py    # every route; SPA static served last; gates live here
backend/app/pipeline/run.py# the six steps of a rebuild; counts only
backend/app/pipeline/clean.py  # secret/PII scan before storage
backend/app/pipeline/seed_demo.py # load the synthetic Aster via the upload path
backend/app/readers/readers.py    # git bundle, issues/PRs JSON, notes, chat — locators out
backend/app/llm/adapter.py       # live / replay (default) / rules — proposes, never decides
backend/app/policy/labels.py     # role matrix + weakest-source rule
backend/app/policy/…             # gate helpers
backend/app/db/read_path.py      # the ONLY SQL in the codebase (PERM-4)
schemas/claim.schema.json        # model output contract
frontend/{index.html,app.js,style.css}  # static SPA, role switcher, /judge guide
scripts/seed.py · verify.py · judge_walkthrough.sh · record_fixtures.{py,sh}
```
