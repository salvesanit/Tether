# Tether — Judge Guide

Welcome to the Tether Round 2 evaluation guide. This document maps the 100-point rubric directly to the codebase, commands, and screens.

## Rubric Navigation

| Rubric Criterion (Points) | What to Open in App | Command to Run | What to Verify |
| :--- | :--- | :--- | :--- |
| **Core Workflow Runs End-to-End (30 pts)** | `/` then `/p/proj_beacon_demo/connect` through `/handover` | `npx tsx --test tests/tether.test.ts` | 5-stage pipeline runs without mock breaks. Gate 1, 2, and 3 enforced on server. |
| **Technical Depth & Reliability (25 pts)** | `/p/proj_beacon_demo/rebuild` and `/p/proj_beacon_demo/review` | `cat reports/verify.md` | Schema-validated candidate claims, CK-1 exact quote match, CK-2 confidence caps, CK-3 conflicts, CK-4 gaps. |
| **Progress Against the Plan (20 pts)** | `docs/PLAN_VS_BUILD.md` | `cat docs/CHANGES_FROM_ROUND1.md` | R1 commitments tracked R1-001 through R1-020 with status (Done/Partial/Changed) and test ID. |
| **Three Planned Improvements (15 pts)** | `docs/ROUND3_COMMITMENTS.md` | N/A | Substantial Round 3 capabilities: Leaver Question Loop, Version Lifecycle Diffs, Live GitHub Reader Resilience. |
| **Usability So Far (10 pts)** | Top bar role switcher & step bar | `/judge` interactive guide | Minimalist charcoal/pure-white theme, tabular numerals, unboxed metadata, full keyboard navigation. |

---

## The Four Demo Roles

Tether implements 4 distinct roles. Switch between them instantly via the **Role Switcher** in the top navigation bar:

1. **Reviewer (Sanit Salve, N1)**:
   - Owns the review queue, resolves conflicts, assigns/parks gaps, clears Gate 1 labels, and signs Version 1.0.
   - Has visibility over all security labels (`open`, `internal`, `restricted`, `confidential`), the dropped claims list, and the tamper-evident audit log.
2. **Successor (Jordan Lee, Day 1)**:
   - Inherits the project cold.
   - Accesses only the latest signed version. Attempting to view an unsigned draft returns **403 Forbidden**.
   - Row-level security strictly hides `restricted` and `confidential` rows, displaying ONE plain notice: *"Some information is restricted for your role."* (No titles, no counts, no leak).
   - Confirms handover receipt.
3. **Leaver (Alex Rivera, Notice)**:
   - Departing team lead. Proposes corrections and clarifies questions the automated trail could not answer.
4. **Admin (Morgan Chen, Project Owner)**:
   - Manages retention policy (30 days default), executes one-click project deletion, exports full JSON bundles, and verifies audit log hashes. Cannot edit or approve claims.

---

## Verifying Claims & Quotes

To verify any claim in the interface:
1. Go to `/p/proj_beacon_demo/review` or `/p/proj_beacon_demo/handover`.
2. Click any **Citation Chip** (e.g. `file:notes/2026-08-12.md#P2` or `commit:a1b2c3d4`).
3. The **Citation Inspector** opens, displaying:
   - The exact character-matched quote highlighted.
   - The 3 lines of source context before and after.
   - The locator grammar string and source security label.
   - The capture timestamp and sha256 checksum.

---

## What is NOT Built (Honest Scope Boundaries)

- **Company-wide general chatbot**: Tether deliberately does not offer a free-form conversational bot over all company data. We produce verifiable, signed claims.
- **Automatic conflict winner selection**: A machine must never pick which engineer was right. Contradictions are surfaced to the reviewer with both sides intact.
- **Performance scoring or mood tracking**: We measure project work only, never people (House Rule HR-5).
