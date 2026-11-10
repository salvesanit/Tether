# Architecture — Tether, Round 2

Single Python process (FastAPI + uvicorn) serving a static SPA and one JSON API; SQLite via a single read path; no build step; one constants module (`backend/app/config.py`); one label policy (`backend/app/policy/labels.py`).

## System

```mermaid
flowchart LR
  B[Browser SPA<br/>frontend/] -->|/api, X-Tether-Role| F[FastAPI<br/>backend/app/api/main.py]
  F --> P[pipeline/run.py<br/>Read → Cut/clean → Pull → Check → Group → Queue]
  P --> R[readers/readers.py]
  P --> C[pipeline/clean.py<br/>redact before store]
  P --> L[llm/adapter.py<br/>live / replay / rules]
  L --> FX[(fixtures/llm/)]
  F --> DB[(SQLite<br/>tether.db)]
  P --> DB
  DB -->|only via| RP[db/read_path.py]
```

*Plain text: the browser talks only to the FastAPI process. The process holds no other service; the LLM is a file (replay), a network call (live), or patterns (rules); all SQL lives in `read_path.py`.*

## Data flow, source → signed handover

```mermaid
flowchart TD
  S1[repo bundle] --> S[spans · locator + redacted text + sha256]
  S2[issues/PRs JSON] --> S
  S3[notes .md] --> S
  S4[chat JSON] --> S
  S --> Q{CK-1 quote check<br/>exact substring at locator}
  Q -- miss --> D[dropped + counted<br/>openable list]
  Q -- hit --> G{CK-2 ceilings · CK-3 group · CK-4 gaps}
  G --> CL[claims + evidence<br/>weakest label wins]
  CL --> REV[Review queue<br/>confirm · edit · reject · park]
  REV -->|all conflicts decided<br/>no uncertain unsettled<br/>citations 100%| SIGN[Gate 3 — reviewer signs<br/>sha256 freezes v1.x]
  SIGN --> SHARE[state: shared]
  SHARE --> HO[Handover filtered by role<br/>sections in risk order<br/>one plain restricted notice]
  HO --> RC[receipt row · state: received]
```

*Plain text: anything without a matching quote never becomes a claim; a person decides every conflict; the signed version is the only thing the successor can open.*

## Project state machine

```mermaid
stateDiagram-v2
  [*] --> scoped
  scoped --> labelled : Gate 1 — labels cleared
  labelled --> rebuilt : rebuild run
  rebuilt --> in_review : first review action
  in_review --> signed : Gate 2 gates green — reviewer signs
  signed --> shared : reviewer/admin shares
  shared --> received : successor confirms receipt
```

*Plain text: seven states; every skipped transition returns 409 with a `*.refused` log row (REV-1).* States are `scoped, labelled, rebuilt, in review, signed, shared, received` in `config.PROJECT_STATES`.

## Evidence model

A **claim** (`claims`) has zero or more **evidence** rows (`evidence`), each tying quote + locator + source label + capture time to a **span** (`spans`). A claim's label is the *weakest* among its evidence (HR-2): one restricted source makes the claim restricted. The handover shows a claim only if the viewer's role may read that label; the citation endpoint additionally fails closed when *every* claim citing a span is unreadable by the role. Signing hashes `payload = {version number, items: risk-ordered claims with citations, gaps, risk_rule, decided conflicts}` (see `_signed_payload` in `main.py`) — later edits create a new draft version; nothing mutates a signed one.

## Design records

See [decisions/](decisions/): 0001 SQLite over Postgres · 0002 replay fixtures provenance · 0003 fail-closed citation gate · 0004 fixture union for identical chunks · 0005 static SPA, no build step.
