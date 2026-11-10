# Recorded passing run — `make judge` (scripts/judge_walkthrough.sh)

Measured on the synthetic project · LLM_MODE=replay · DEMO_MODE=true · throwaway database (the demo db is never touched). Artifact: this file is generated from real console output, not composed.

- **Commit (app code):** 8c22a41 · reports committed at d026615 (docs-kind commit; the app is identical)
- **Date:** 2026-11-10 · **Model mode:** replay · **Tool:** judge_walkthrough.sh twice consecutively, exits 0/0
- **Script machine time:** ~1.7–2.0 s per pass (plus uvicorn startup inside the script)

## Run A (exit 0)

```
DM-1 connect — project p_821caebf05251133 loaded through the upload path (consent logged, manifest labels applied)
== reviewer: clear the labels gate (Gate 1), then rebuild ==
  labels cleared → state=labelled
  rebuilt: spans 165 · candidates 82 · kept 60 · dropped 21 · conflicts 6 · gaps 6
== DM-2 prove — open one citation, quote must appear at its locator ==
  citation resolves · quote found in span: True
== work the queue the review screen way (confirm claims · decide conflicts · assign gaps) ==
  claims confirmed: 60
  conflicts decided: 6
  gaps assigned: 7
== DM-3 correct — sign the version (Gate 3) ==
  signed v1.0 items 60 sha256 2c4def20f6c8a1e8… by Sanit Salve
  shared with the project
== DM-4 restrict — the successor opens the handover; restricted stays hidden ==
  sections: Own first | Open work | Decisions and why | Dependencies and accounts | Repeated problems | What nobody knows — and who to ask
  restricted notice shown to successor: True
  successor reading the review queue is refused with HTTP 403 (role-filtered)
  receipt confirmed → project state=received
```

## Run B (exit 0)

```
DM-1 connect — project p_ba19756287e57657 loaded through the upload path (consent logged, manifest labels applied)
  signed v1.0 items 60 sha256 1ef8836108d6e8d7… by Sanit Salve
  sections: Own first | Open work | Decisions and why | Dependencies and accounts | Repeated problems | What nobody knows — and who to ask
  restricted notice shown to successor: True
  successor reading the review queue is refused with HTTP 403 (role-filtered)
  receipt confirmed → project state=received
```

(Gaps assigned prints 7 because the gap queue includes one explicitly-suggested extra subject, assigned like any gap but never counted among the planted six — see CK-4.)

## Notes

- The two runs above are the consecutive green pair required by the Round 2 brief. An earlier wiring bug (PORT not exported to the child server → 30 s of health-check polling against the live preview's port) failed fast, was fixed before this recording, and changed no application code.
- Screenshots per step: [ADD — desktop capture]; the steps are DOM-verifiable today in the live preview at `http://localhost:8000`.
- `gaps assigned: 7` = 6 planted gaps + 1 suggested; the suggested one is labelled `suggested` and is excluded from the planted six in every report.
