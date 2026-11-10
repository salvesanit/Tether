# AGENTS.md — for coding agents working in this repository
Rules: one constants module (backend/app/config.py); one read path (backend/app/db/read_path.py) — never query the database elsewhere (PERM-4 test enforces it); no claim without a character-for-character quote at its locator; the model proposes and never decides — N1 signs; fixtures carry provenance and handwritten-reference is never called model output; reports carry counts, never loss rates or percentages; synthetic data everywhere and it says so.
Verify before you claim: python3 scripts/verify.py must exit 0; tests live in backend/tests/; put the test ID in every new test's name.
Do not add: dead buttons, untested endpoints, text addressing the examiner, TODO/FIXME in shipped code.
