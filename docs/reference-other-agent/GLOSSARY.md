# Tether — Glossary of Terms

One unified vocabulary used identically across code, UI, API, tests, and documentation.

- **Claim**: A single, verifiable statement of project state in present tense, classified into one of seven fixed types.
- **Source**: An authorized external origin of knowledge (Git repository, meeting notes Markdown, or chat JSON export).
- **Span**: A discrete raw text segment extracted from a source, indexed by locator and scanned for secrets.
- **Locator**: A standardized pointer string resolving directly to a source line, paragraph, commit, comment, or chat timestamp.
- **Label**: The security classification assigned to a source or claim (`open`, `internal`, `restricted`, or `confidential`).
- **Status**: The verification state of a claim determined by checks and reviewer confirmation (`verified`, `uncertain`, `conflicting`, or `missing`).
- **Conflict**: A pair of claims with identical subject and attribute but incompatible values, requiring human resolution.
- **Gap**: An uncovered topic from the twelve successor-needs subjects, carrying an inquiry, a designated owner, and a next step.
- **Version**: An immutable, signed snapshot of verified claims and settled conflicts sealed with a cryptographic hash.
- **Receipt**: An auditable acknowledgement confirmed by the successor upon receiving the signed handover.
