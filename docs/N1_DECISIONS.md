# N1 decisions — defaults N1 must approve (owner: Sanit Salve)

Each line is a default the builder chose that is N1's call. Unticked = needs N1. Tick by editing this file and re-running `make verify`.

| # | Decision | Default in build | Approve |
|---|---|---|---|
| N1-1 | Label rules: `open/internal/restricted/confidential`; private+HR channels excluded entirely (never labelled, never read); a claim takes its weakest evidence label (HR-2) | as built (`policy/labels.py`) | [ ] |
| N1-2 | Ceiling: merged PR 0.95 · issue/PR comment 0.85 · unmerged PR 0.70 (0.95 file/commit and 0.60 chat are the plan's own) | `config.CEILINGS` | [ ] |
| N1-3 | Verified floor: 0.80 — a single chat message can never be verified | `CONFIDENCE_VERIFIED_FLOOR` | [ ] |
| N1-4 | Role matrix as coded: leaver = open..restricted · reviewer/admin = all · successor = open+internal | `policy/labels.py` | [ ] |
| N1-5 | **Admin reads claim text** — deviates from the spec matrix (admin: no claim text by default, acts via reviewer path). One label-based read path is simpler; the deviation is documented, not hidden. N1 either accepts it or orders the filter change (small: `_visible_claims` + admin UI paths) | admin = all labels | [ ] — DEVIATION |
| N1-6 | Risk order weights: risk 5 · dependency 4 · open question 4 · next step 3 · repeated problem 3 · owner 2 · decision 1; +3 single-author module ≥80%; +2 open issue/PR link; +2 beside a conflict/gap | `config.TYPE_WEIGHT` + bonuses; labelled `estimate` in payload | [ ] |
| N1-7 | Retention: 30 days default, 1–365 settable by admin, one-click delete, deletion requests logged | `projects.retention_days` | [ ] |
| N1-8 | Licence for D3 (public repo + this file) | **not chosen** — build refuses to presume; candidates: MIT (default for permissive student work) or Apache-2.0 | [ ] — BLOCKS D3 |
| N1-9 | Gate behaviour: every skipped state 409 + `*.refused` log row; sign refused with named failing gates | `main.py` | [ ] |
| N1-10 | Fail-closed span citations (any citing claim unreadable ⇒ 403) | [decisions/0003](decisions/0003-fail-closed-span-gate.md) | [ ] |
| N1-11 | Upload ceiling 25 MiB/file → 413 + log row (SEC-4) | `config.MAX_UPLOAD_BYTES` | [ ] |
| N1-12 | Consent wording (upload gate) | current copy in the UI — review the sentence | [ ] |
| N1-13 | `extractor: rules` fallback acceptable once labelled as such on the run | as built | [ ] |
| N1-14 | The three Round 3 commitments in [ROUND3_COMMITMENTS.md](ROUND3_COMMITMENTS.md) | proposed by the builder, adopted only if N1 signs | [ ] |

**How to approve:** tick the box, commit with message `N1-n approved — <one line>`; the build re-verifies clean regardless (these are policy knobs, not code paths).

> The sibling build archived at [reference-other-agent/N1_DECISIONS.md](reference-other-agent/N1_DECISIONS.md) ships every box pre-ticked, including the licence. Those are that build's claimed approvals, not this build's — nothing here is approved until N1 ticks it and commits with an `N1-n approved` message.
