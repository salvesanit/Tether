# Tether

Tether turns an authorised project's work trail into a reviewable handover: claims are tied to exact source quotes, a human reviewer resolves uncertainty and signs a version, and the successor gets a role-filtered view. This Round 2 prototype uses a fictional project, Aster — a campus club events app.

> **Prototype notice:** sign-in is a demo role switcher, not authentication. Use synthetic data for demonstrations; do not expose this app to the public internet or treat it as a production service. See [Limitations](docs/LIMITATIONS.md).

## Contents

- [Start Tether](#start-tether)
- [Take the guided demo](#take-the-guided-demo)
- [Use every screen and action](#use-every-screen-and-action)
- [Use your own authorised sources](#use-your-own-authorised-sources)
- [Roles and visibility](#roles-and-visibility)
- [Run tests and scripted checks](#run-tests-and-scripted-checks)
- [Requirements cross-check](#requirements-cross-check)
- [Known limitations](#known-limitations)
- [Project documents](#project-documents)

## Start Tether

### Windows PowerShell

Run these commands from the repository folder:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts\seed.py
python run.py
```

Open [http://localhost:8000](http://localhost:8000). Stop the server with **Ctrl+C** in its terminal.

If PowerShell prevents virtual-environment activation, either allow the script for the current terminal with `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, or skip activation and run `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`, `.\.venv\Scripts\python.exe scripts\seed.py`, and `.\.venv\Scripts\python.exe run.py`.

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/seed.py
python run.py
```

The app listens on port `8000` by default. `PORT`, `TETHER_DB`, `TETHER_DATA`, `DEMO_MODE`, and `LLM_MODE` can be set as environment variables before starting it. Defaults are `8000`, `tether.db`, `var`, `true`, and `replay`.

The app can also load the synthetic Aster project from the start screen. Seeding and loading are safe to repeat: if an Aster project is already at the first gate, the seed script reports that project instead of adding another.

## Take the guided demo

The demo exercises the complete path without API keys or outbound model calls:

1. On the start screen, choose **Load Demo Project & Start Flow**. The project is Aster; all its people and source material are invented.
2. In **Connect**, inspect the source labels and the channels marked **not read**. As the reviewer, clear the labels to open Gate 1.
3. In **Reconstruct**, run the rebuild. Review the counts and the list of dropped claims.
4. In **Review Queue**, inspect evidence and work through claims, conflicts, gaps, quarantine, and leaver proposals.
5. In **Sign-Off**, resolve every blocking gate, sign the version, then share it with the successor.
6. Switch to **Diya Raman · Successor** and open **Successor View**. Inspect the signed handover, open citations, and log receipt when ready.

The navigation bar links to Connect, Reconstruct, Review Queue, Sign-Off, Successor View, and Admin & Log. The workflow bar shows which steps are open or complete. **Dark / Colour** switches the appearance and remembers the selection in this browser.

## Use every screen and action

### Start screen

- **Load Demo Project & Start Flow** loads the synthetic Aster sources through the normal upload/consent path and opens Connect.
- **Connect Custom Sources** creates a blank project and opens Connect so you can upload authorised source files.
- **Open Interactive Guide** opens the Judge Guide, which explains the four-minute demonstration and the evidence to check.

### Connect — scope, label, and upload sources

The source table shows each source's kind, name, label, and whether Tether read it. Excluded channels appear as **not read** with a reason; the reader drops excluded chat channels before they enter the application database.

Source labels define who can read evidence:

| Label | Intended visibility |
|---|---|
| `open` | Any project role |
| `internal` | Project members, including the successor |
| `restricted` | Named project roles; not the successor |
| `confidential` | Reviewer and admin only |

A claim backed by multiple sources inherits the most restrictive source label. The reviewer changes labels with the source dropdown and selects **Clear labels** only when they are ready for Gate 1. Tether does not start the reconstruction/read of source contents until that gate is cleared.

To add your own sources, select **Use Your Own Authorised Sources** from the start screen. On Connect:

1. Choose the files to upload.
2. Read and tick the authorisation checkbox. Consent is required and logged before the files are parsed.
3. Select **Upload & label**.
4. Check the source list and labels; clear labels when it is safe to proceed.

Accepted shapes and examples are in [Input formats](docs/INPUT_FORMATS.md). In brief: Markdown notes, a Git bundle or repository ZIP, Slack-style chat JSON, GitHub REST-shaped issue/PR JSON, and an optional manifest for labels and channel exclusions. The per-file upload limit is 25 MiB.

### Reconstruct — rebuild and inspect results

After labels are cleared, select **Run the rebuild**. Tether reads the authorised sources, cleans and checks the text, rebuilds candidate claims, and checks each proposed quote at its source locator.

The report shows spans, candidates, kept and dropped claims, conflicts, gaps, redactions, and quarantined material. These are counts, not a knowledge-capture percentage or loss rate. Open **Dropped claims** to see proposals that failed a check and why. The step-by-step section records the pipeline stages.

**Re-run the rebuild** creates a new run from the current source set. Review the latest run before making decisions.

### Review Queue — check claims and make decisions

Use the tabs to switch among **Claims**, **Conflicts**, **Gaps**, **Quarantine**, and **Proposals**. Click a citation/locator chip to inspect the underlying source excerpt; the UI highlights an exact quote match.

- **Claims:** the reviewer can **Confirm** a claim, **Edit** its sentence, **Reject** it with a written reason, or **Park** it with a reason. An edit is retained only if its citation still holds. Use the filters to narrow the claim list. The leaver can **Propose a correction** for the reviewer; proposals do not change the signed handover by themselves.
- **Conflicts:** inspect both sides and their evidence. The reviewer picks the winning value and gives a written reason, or parks the conflict with a reason. Tether never chooses a side automatically.
- **Gaps:** each gap asks who may know and what the next step is. The reviewer can assign an owner and next step, or park it with a reason. A gap stays visible in the handover rather than being filled with a guess.
- **Quarantine:** inspect flagged text. The reviewer can mark it **Dismissed — not an attack** or **Confirm injection**. Quarantined text does not silently change a gate.
- **Proposals:** read corrections submitted by the leaver. To accept one, review the claim itself and confirm or edit it; a proposal is not an automatic approval.

The successor is directed to the signed handover instead of the review queue. The admin view is read-only for review decisions.

### Sign-Off — pass gates, sign, and share

Sign-Off lists the blocking checks:

1. **Gate 1:** source labels were cleared.
2. **Gate 2:** conflicts have a decision or a reasoned park, and uncertain claims are settled.
3. **Gate 3:** confirmed claims still pass the citation check.

Fix a failing item in Connect or Review Queue. There is no override button. Only the reviewer can sign. Signing freezes a named version with the reviewer's name, timestamp, and SHA-256 hash. When ready, choose **Share with the successor**; sharing opens the handover to the successor role.

### Successor View — read the signed handover

The successor sees the latest signed and shared version, arranged into six sections in work-risk order. Claims include citations and available decision reasons; unresolved gaps remain visible with their owner and next step. Use **Print / save PDF** for a copy. The successor can select **I received this handover — log it** to record receipt.

If material is hidden by the successor's label permissions, Tether shows one plain restriction notice rather than revealing restricted titles or counts. The signed version is not changed by role filtering.

### Admin & Log — audit, retention, export, and deletion

Switch to **Krushna Patil · Admin** to use Admin & Log:

- **Audit log:** review recent actions and the hash-chain status. Select **Re-verify the chain from genesis** to check the full chain.
- **Retention:** set the configured period from 1 to 365 days (default 30). Automatic expiry sweeps are not implemented; a setting is not proof that old data is automatically deleted.
- **Export:** download a JSON export of project records. Export actions are logged; treat the file as sensitive.
- **Deletion request:** enter a request detail and log the request. This does not delete the project.
- **Delete this project:** select **Delete this project…**, then confirm the second prompt. This is irreversible and removes the project's sources, claims, versions, and log.

## Use your own authorised sources

Tether is intended to process only sources you are allowed to use. For exact JSON shapes, locators, and a manifest example, see [Input formats](docs/INPUT_FORMATS.md).

| File/source | Accepted form |
|---|---|
| Repository | Real Git `.bundle` or repository `.zip` |
| Notes | Markdown (`.md`, `.markdown`, or `.txt`) |
| Chat | `chat.json`, with channels containing messages with `ts`, `user`, and `text` |
| Issues / pull requests | `issues.json` / `prs.json`, using the documented GitHub REST list-item shape |
| Labels and exclusions | Optional `manifest.json`; labels can also be set in Connect |

Empty or malformed files, unsupported formats, and files over the size limit are rejected. Secrets and some personal details are redacted before storage. Excluded channel content is not stored in Tether's database, but the original uploaded file remains on disk under `var/uploads/`; manage that file separately. Do not upload real HR/private channels or sensitive production data to this demo.

## Roles and visibility

The role selector is a **demo-only** convenience; it does not authenticate a person. The four fictional demo users are:

| Demo user | Role | Typical actions |
|---|---|---|
| Aarav Mehta | Leaver | Review the queue and propose corrections |
| Sanit Salve | Reviewer | Label sources, decide claims/conflicts/gaps, sign and share |
| Diya Raman | Successor | Read the shared handover and log receipt |
| Krushna Patil | Admin | Verify the log, set retention, export, log deletion requests, delete projects |

The server enforces the prototype's role and label rules, but anyone who can reach the demo can choose a role. Do not deploy it as-is. The admin claim-text policy also differs from the original role matrix; that decision is explicitly open in [N1 decisions](docs/N1_DECISIONS.md).

## Run tests and scripted checks

From the repository root:

```powershell
python -m pytest backend\tests -q
python scripts\verify.py
```

`python scripts\verify.py` runs the automated suite and produces reports for the synthetic project. For the scripted end-to-end judge path, `make judge` requires GNU Make and a Bash-compatible shell (for example Git Bash on Windows). The Docker files are provided, but the Docker start path has not been validated; the direct Python start above is the supported path for this prototype.

Check `/api/health` in a browser to confirm the server is responding. For a concise feature-to-test map, see [Testing](docs/TESTING.md); for the four-minute script, see [Golden path](docs/demo/golden_path.md).

## Requirements cross-check

This README was checked against the supplied **Tether Round 2 Prototype Build Prompt**, **Tether — Sanit Salve (Leader)** Round 1 plan, and **NightOwls Tether Round 1 Team Member** plan. The detailed commitment-by-commitment audit is [Plan vs Build](docs/PLAN_VS_BUILD.md); the R2 evidence and current limitations are [Testing](docs/TESTING.md), [Limitations](docs/LIMITATIONS.md), and the verification reports.

| Requirement from the supplied plans / build prompt | Current evidence and status |
|---|---|
| End-to-end connect → rebuild → review → signed/shared handover | Implemented; scripted walkthrough is available with `make judge`. See [Golden path](docs/demo/golden_path.md). |
| Claims must be checked against exact source quotes and locators; failed claims are counted | CK-1 and RD-1 tests; see [verification report](reports/verify.md) and [answer-key report](reports/answer_key_report.md). |
| Confidence ceilings, conflicts decided by a person, visible gaps with owners/next steps | CK-2, CK-3, and CK-4 tests; reviewer actions are described above. |
| Labels, weakest-source visibility, successor filtering, and a plain restriction notice | PERM-1 through PERM-4 tests; see [leak test report](reports/leak_test_report.md). |
| Excluded channels, pre-storage redaction, and prompt-injection quarantine | SEC-1 through SEC-4 tests. The original upload remains on disk; see [Limitations](docs/LIMITATIONS.md). |
| Offline/replay mode, honest fixture provenance, and changed input changes output | Replay is the default and makes no live model call; IN-1 covers input changes. Replay verifies the pipeline, not live model quality. |
| Gate enforcement, reviewer signature, frozen version, and audit trail | REV-1 and the scripted walkthrough; admin export, retention, and deletion have less regression coverage and are not represented as fully verified. |
| Docker deployment, hosted link, live model quality, and user research | Not verified or not delivered. Docker is untested, there is no deployed URL, live extraction has not been run with a key, and the feedback documents are instruments rather than research results. |

The current reports are measurements of the **synthetic Aster project only**. Browser E2E may be skipped on machines missing browser system libraries; the report records that honestly. Do not interpret planted counts as a percentage of real-world knowledge captured. The Round 1 implementation changes, partial items, and deferrals are tracked in [Plan vs Build](docs/PLAN_VS_BUILD.md); unresolved policy choices are in [N1 decisions](docs/N1_DECISIONS.md).

## Known limitations

- Authentication is not built; the demo role switcher can be changed by any visitor.
- SQLite and application-level filtering are used instead of database-enforced PostgreSQL row-level security.
- Live hosted-model extraction is implemented but has not been exercised; replay uses recorded, `handwritten-reference` fixtures.
- Docker, public deployment, automated expiry sweeps, real user research, and complete admin regression tests are not delivered.
- Automated browser E2E may skip when Chromium system libraries are unavailable.

Read [Limitations](docs/LIMITATIONS.md) before using any real sources.

## Project documents

- [Judge Guide](docs/JUDGE_GUIDE.md) — rubric-to-evidence map and demo path
- [Architecture](docs/ARCHITECTURE.md) — data flow, gates, access model, and design decisions
- [Walkthrough](docs/WALKTHROUGH.md) — trace of a request through the implementation
- [Plan vs Build](docs/PLAN_VS_BUILD.md) — Round 1 commitments and deviations
- [Testing](docs/TESTING.md) and [Reliability](docs/RELIABILITY.md) — test coverage and failure cases
- [Input formats](docs/INPUT_FORMATS.md) — upload schemas and examples
- [Synthetic data](docs/SYNTHETIC_DATA.md) — Aster's provenance and answer-key method
- [Limitations](docs/LIMITATIONS.md) and [N1 decisions](docs/N1_DECISIONS.md) — known gaps and choices awaiting approval
- [Glossary](docs/GLOSSARY.md) — shared product terminology
