# Tether — AI Tool Disclosure (D5)

In accordance with event rules 6 and 7, this document discloses AI assistance during the Round 2 build.

## Tools Used
- **Google AI Studio Agent**: Used for initial code generation, test scaffolding, and TypeScript interface generation.
- **Model Used**: Gemini 2.5 Flash / Gemini 3.8 Flash.

## Division of Labor

| Component / File | Primary Author | Human Reviewer | Verification Method |
| :--- | :--- | :--- | :--- |
| **Claim Model & Vocabulary** (`src/types/`, `src/engine/constants.ts`) | Sanit Salve (N1) specification | Sanit Salve (N1) | Verified against 7 claim types and 12 successor needs |
| **Locator Grammar & Resolvers** (`src/engine/readers.ts`) | AI Agent + Krushna Patil (N2) | Krushna Patil (N2) | `RD-1` 100% locator resolution test |
| **Security Cleaner & Scanners** (`src/engine/cleaner.ts`) | AI Agent + Sanit Salve (N1) | Sanit Salve (N1) | `SEC-1`, `SEC-2`, `SEC-3` unit tests |
| **Quote Check & Caps** (`src/engine/pipeline.ts`) | AI Agent + Krushna Patil (N2) | Krushna Patil (N2) | `CK-1`, `CK-2` tests (60 kept, 20 dropped) |
| **Ledger & RLS Single Read Path** (`src/engine/ledger.ts`) | AI Agent + Sanit Salve (N1) | Sanit Salve (N1) | `PERM-1` through `PERM-4` leak tests |
| **Synthetic Dataset & Answer Key** (`src/engine/syntheticData.ts`) | AI Agent + Team NightOwls | Sanit Salve (N1) | `KEY-1` ground-truth validation |
| **UI Components & Theme** (`src/components/`, `src/App.tsx`) | AI Agent | Team NightOwls | Browser inspection & accessibility verification |

## AI Integrity Commitment
- AI is never allowed to settle a conflict or override human sign-off.
- AI never proposes claims without an exact character-matched quote verified by plain code.
- Replay mode fixtures are honestly disclosed and never disguised as live inference.
