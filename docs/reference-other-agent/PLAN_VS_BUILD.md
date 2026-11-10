# Tether — Plan vs Build Matrix (D6)

Every commitment from the Round 1 plan is accounted for below, numbered R1-001 through R1-020.

| ID | Commitment from Round 1 Plan | Status | Evidence / Test ID | One-Line Reason / Note |
| :--- | :--- | :---: | :--- | :--- |
| **R1-001** | One project, one leaver, three permitted sources | **Done** | `src/engine/syntheticData.ts` | Campus hub synthetic project built with Git repo, notes, and chat export. |
| **R1-002** | Turn sources into claims across seven fixed types | **Done** | `src/engine/constants.ts` | `decision`, `owner`, `dependency`, `risk`, `repeated_problem`, `open_question`, `next_step`. |
| **R1-003** | Exact quote match check (CK-1) | **Done** | `tests/tether.test.ts` (`CK-1`) | Look up quote at locator; drops all 20 unsupported fakes. |
| **R1-004** | Source confidence ceiling caps (CK-2) | **Changed** | `tests/tether.test.ts` (`CK-2`) | 0.95 ceiling used for files/commits instead of 0.96 example per N1 review. |
| **R1-005** | Group and compare contradiction detection (CK-3) | **Done** | `tests/tether.test.ts` (`CK-3`) | 6 of 6 planted contradictions surfaced; 0 settled by machine. |
| **R1-006** | Successor-needs gap check across 12 subjects (CK-4) | **Done** | `tests/tether.test.ts` (`CK-4`) | Fixed 12 subjects evaluated; exactly 6 planted gaps returned with owner & next step. |
| **R1-007** | Four distinct roles with strict access rules | **Done** | `src/engine/ledger.ts` | Reviewer, Successor, Leaver, Admin enforced at database read path. |
| **R1-008** | Single read path (`readPath`) with RLS | **Done** | `tests/tether.test.ts` (`PERM-4`) | All data access routed through `readPath`; direct bypass prevented. |
| **R1-009** | Gate 1: Reviewer clears source labels | **Done** | `src/engine/ledger.ts` | Reviewer must clear labels before rebuild is allowed. |
| **R1-010** | Gate 2 & 3: Reviewer signs version 1.0 with hash | **Done** | `tests/tether.test.ts` (`REV-1`) | Requires all conflicts decided/parked and 100% citation pass. |
| **R1-011** | Successor view in risk order (formula estimate) | **Done** | `src/engine/constants.ts` | Risk formula combines type weight, author concentration, and open items. |
| **R1-012** | Plain restriction notice without metadata leaks | **Done** | `tests/tether.test.ts` (`PERM-1`) | Successor sees plain notice when claims withheld; zero counts or titles. |
| **R1-013** | Block successor on unsigned drafts with 403 | **Done** | `tests/tether.test.ts` (`PERM-2`) | Attempting to access draft handover returns 403 Forbidden. |
| **R1-014** | Weakest-source visibility rule (HR-2) | **Done** | `tests/tether.test.ts` (`PERM-3`) | Multi-source claims inherit the most restrictive label among evidence. |
| **R1-015** | Append-only audit log with chained hashes | **Done** | `src/engine/ledger.ts` | Every action chained with `prev_hash` and SHA-256 `hash`. |
| **R1-016** | Gitleaks secrets scanning & PII masking | **Done** | `tests/tether.test.ts` (`SEC-2`) | AWS keys, phone numbers, and emails redacted prior to storage. |
| **R1-017** | Honeytokens in excluded channels dropped in-memory | **Done** | `tests/tether.test.ts` (`SEC-1`) | Private/HR channels excluded in-memory; 0 honeytokens reach storage. |
| **R1-018** | Prompt injection quarantine | **Done** | `tests/tether.test.ts` (`SEC-3`) | Instructions like "ignore previous instructions" quarantined as reviewer item. |
| **R1-019** | Successor handover receipt confirmation | **Done** | `src/engine/ledger.ts` | Successor can confirm receipt with closing timestamp. |
| **R1-020** | Live external GitHub sync and pgvector | **Deferred** | `docs/LATER.md` | Deferred to Round 3 to keep P0 rock-solid and hermetic without external keys. |
