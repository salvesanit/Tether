# Tether — System Architecture (D4)

## 1. High-Level System Architecture

```mermaid
graph TD
    subgraph Sources [Authorized Input Sources]
        G[Git Repository<br/>Commits & Files]
        M[Markdown Notes<br/>Meeting Syncs]
        C[Chat JSON<br/>Slack / Discord]
        P[Excluded Channels<br/>#private, #hr]
    end

    subgraph SecurityLayer [Trust & Sanitization Layer]
        K[Gitleaks Scanner<br/>Secrets Redaction]
        PII[PII Masking<br/>Phone & Email]
        Q[Prompt Injection<br/>Quarantine Filter]
        EX[In-Memory Exclusion<br/>Drop Honeytokens]
    end

    subgraph Pipeline [6-Stage Reconstruction Pipeline]
        S1[1. Reader & Locators]
        S2[2. Cut & Clean]
        S3[3. Pull Claims<br/>Replay / Rules / Live]
        S4[4. CK-1 Quote Match<br/>Exact Char Substring]
        S5[5. Group & Compare<br/>CK-2 Caps, CK-3 Conflicts, CK-4 Gaps]
        S6[6. Fill Queue]
    end

    subgraph Storage [Ledger & Row-Level Security]
        L[Database Ledger]
        AL[Append-Only Audit Log<br/>Chained SHA-256 Hashes]
        RP[Single Read Path<br/>readPath by Role]
    end

    subgraph Views [Role-Based Interfaces]
        V_REV[Reviewer View<br/>Queue, Conflicts, Sign-off]
        V_SUC[Successor View<br/>Risk Order, Plain Notice]
        V_ADM[Admin View<br/>Retention, Export, Delete]
    end

    P -->|Drop in memory| EX
    G & M & C --> S1
    S1 --> S2
    S2 --> K & PII & Q
    K & PII & Q --> S3
    S3 --> S4
    S4 -->|Drop unsupported| D[Dropped Claims Count]
    S4 -->|Kept| S5
    S5 --> S6
    S6 --> L
    L --> AL
    L --> RP
    RP -->|Reviewer Role| V_REV
    RP -->|Successor Role - 403 on unsigned| V_SUC
    RP -->|Admin Role| V_ADM
```

### System Architecture Description
Tether ingests three authorized sources: Git commits/files, Markdown notes, and Chat JSON. Excluded private/HR channels are stripped in-memory before reaching persistent storage. The sanitization layer applies Gitleaks patterns to redact API keys and AWS tokens, masks phone numbers and emails, and quarantines prompt injection instructions. The 6-stage reconstruction pipeline validates exact quote substrings (CK-1), applies source confidence ceilings (CK-2), groups contradictions without settling by machine (CK-3), and checks 12 successor-needs subjects for gaps (CK-4). All entities are stored in the ledger with append-only hash-chained audit logging, accessible exclusively through a single read path (`readPath`) enforcing row-level security.

---

## 2. Project State Machine & Gate Transitions

```mermaid
stateDiagram-v2
    [*] --> scoped : Project created
    scoped --> labelled : Gate 1: Reviewer clears source labels
    labelled --> rebuilt : Reconstruction pipeline completed
    rebuilt --> in_review : Reviewer begins queue triage
    in_review --> signed : Gate 2: Conflicts & gaps settled<br/>Gate 3: 100% Citation pass & hash frozen
    signed --> shared : Released to Successor
    shared --> received : Successor confirms receipt
    received --> [*]

    note right of in_review
        Attempting to jump states returns 409 Conflict
        Successor reading unsigned draft returns 403 Forbidden
    end note
```

### State Machine Description
A Tether project advances through 7 strict sequential states: `scoped` -> `labelled` -> `rebuilt` -> `in_review` -> `signed` -> `shared` -> `received`. Skipping a state returns an HTTP 409 Conflict and records an audit log row. Gate 1 requires the Reviewer to clear source labels before reading. Gate 2 requires all conflicts to be decided or parked with a reason. Gate 3 requires 100% citation pass rate, freezing Version 1.0 with a cryptographic SHA-256 seal.

---

## 3. Evidence Model & Weakest-Source Visibility

```mermaid
graph LR
    subgraph Evidence [Evidence Items]
        E1[Source 1: Open Git File]
        E2[Source 2: Restricted Budget Note]
    end

    subgraph ClaimModel [Claim Record]
        C[Claim: Infrastructure Grant Allocation]
        L[Derived Label: RESTRICTED]
    end

    subgraph Visibility [Row-Level Security]
        R1[Reviewer: Visible]
        R2[Successor: Filtered Out]
        N[Plain Notice: Some information is restricted for your role]
    end

    E1 --> C
    E2 --> C
    E1 & E2 -->|Weakest-Source Rule HR-2| L
    L --> R1
    L --> R2
    R2 --> N
```

### Evidence Model Description
Under House Rule HR-2, a claim backed by multiple sources takes the most restrictive security label among its supporting evidence (`confidential` > `restricted` > `internal` > `open`). When a restricted claim is withheld from a Successor, Tether displays ONE plain notice stating that some information is restricted for their role, with zero counts, titles, or leaked metadata.
