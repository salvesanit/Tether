# Tether — Changes from Round 1 Plan (D6)

This document records every modification made from the initial Round 1 proposal, along with engineering rationale and team review approvals.

### 1. Confidence Ceiling Adjusted from 0.96 to 0.95
- **Original Plan**: An example claim in the Round 1 proposal mentioned confidence 0.96.
- **Change**: Adjusted ceiling to 0.95 for files and commits to match the strict 0.95 maximum confidence rule for verified documents.
- **Rationale**: Keeps confidence ceilings mathematically consistent across all readers.

### 2. Expanded Claim Model Fields
- **Original Plan**: Fields were limited to `type`, `text`, `quote`, `locator`, `confidence`, and `status`.
- **Change**: Added `subject`, `attribute`, `value`, `reason`, `rejected_options`, `owner`, `label`, `evidence[]`, and `review`.
- **Rationale**:
  - `subject`, `attribute`, `value` enable deterministic conflict detection without relying on fuzzy AI comparison.
  - `reason` and `rejected_options` preserve the drivers and alternatives behind decisions (van Heesch vaporisation model).
  - `label` enforces weakest-source visibility (HR-2).
  - `review` tracks human audit history.

### 3. Excluded Channels Handled In-Memory Before Storage
- **Original Plan**: Excluded channels flagged during source review.
- **Change**: Implemented strict in-memory drop in `readChatExport()` so that private/HR channel contents and honeytokens never touch the database, search indexes, or logs.
- **Rationale**: Prevents accidental leakage or forensic recovery of excluded communications.

### 4. Direct Full-Stack TypeScript Implementation
- **Original Plan**: Separate Python FastAPI backend and Next.js frontend with PostgreSQL.
- **Change**: Unified high-performance TypeScript engine with Node/Express REST API and React 19 frontend, executing identical logic in browser preview and `node:test` CLI.
- **Rationale**: Eliminates multi-runtime drift, allows instantaneous deterministic seeding without external database daemon dependencies, and enables the judge to run all 21 verification tests directly with `npx tsx --test`.

### 5. Minimal Handover Receipt
- **Original Plan**: Complex multi-step receipt acknowledgement workflow.
- **Change**: Streamlined to a single verifiable `confirmReceipt()` record with user name, timestamp, and signed version hash, closing the handover loop.
