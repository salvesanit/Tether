# Tether — Reliability and Failure Modes

Every failure mode, the exact behaviour the user sees, and the test ID that proves it.

| Failure Mode | System Behaviour Seen by User | Proving Test ID |
| :--- | :--- | :---: |
| **Empty Source File** | Reader returns 0 spans and registers clean informational notice; does not crash or throw unhandled exceptions. | `RD-2` |
| **Malformed File Syntax** | Reader catches parse error, logs warning to source report, and continues processing remaining valid files. | `RD-2` |
| **One Source Missing / Switched Off** | Pipeline runs with available sources; report explicitly flags the missing source; gaps appear for subjects formerly covered. | `SW-1` |
| **Model API Timeout / Failure** | Automatically falls back to local rules-based regex extractor; run report displays `extractor: rules`. | `IN-1` |
| **Invalid Model Output / Schema Mismatch** | Schema validator discards invalid JSON; drops candidate claims failing type or sentence rules. | `CK-1` |
| **Quote Miss (Hallucinated Citation)** | Character-by-character substring comparison fails; claim is set aside into Dropped list with locator miss reason; never displayed to successor. | `CK-1` |
| **No API Key Provided** | Operates automatically in replay mode or rules mode with zero network dependency. | `KEY-1` |
| **Successor Accesses Unsigned Draft** | API responds with HTTP 403 Forbidden; UI displays notice that handover is awaiting reviewer sign-off. | `PERM-2` |
| **Reviewer Attempts State Jump** | State machine blocks transition with HTTP 409 Conflict; records incident in tamper-evident audit log. | `REV-1` |
| **Reviewer Attempts Sign-Off with Open Conflict** | Sign-off modal blocks submission; displays count of unresolved contradictions that must be decided or parked first. | `REV-1` |
| **Prompt Injection in Source Text** | Chunk is quarantined with reviewer flag; instructions cannot mutate status, labels, roles, or gates. | `SEC-3` |
| **Honeytoken in Excluded Channel** | Excluded channel is stripped in-memory before reaching database; token never appears on screens or logs. | `SEC-1` |
| **Credentials in Codebase** | Gitleaks scanner replaces secret with `[REDACTED:aws_key]`; logs redaction count on source span. | `SEC-2` |
