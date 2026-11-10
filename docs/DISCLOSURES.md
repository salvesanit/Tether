# Disclosures — APIs, models, datasets, libraries, templates, services

## APIs used
| API | Used for | Notes |
|---|---|---|
| none at runtime | — | The app makes zero outbound calls in replay/rules modes (the default). |
| Hosted LLM endpoint (name not fixed) | `LLM_MODE=live` only | temperature 0, 30s timeout, `LLM_MAX_CALLS` cap (default 200), model id stored on the run. Never called in this build — no key. |

## AI models
| Model | Where | Provenance |
|---|---|---|
| none live | — | replay fixtures are handwritten-reference; the model-id field on runs stays null |
| Arena Agent Mode (root agent; models incl. Claude-family, not otherwise identified) | authorship of this repository under N1's direction | see [AI_DISCLOSURE.md](AI_DISCLOSURE.md); must match commit history |

## Datasets
| Dataset | Kind |
|---|---|
| `data/demo_project/` (Aster) | synthetic, authored for this build; nothing derived from a real company or person |
| `answer_key.json` | planted answers, written before the sources |
| evidence base (Galan 2023; Nourry 2024; Sinequa 2022) | cited as written in the Round 1 plan; no new data collected; nothing invented |

## Libraries (pinned in requirements.txt; licences from package metadata)
| Package | Version | Licence |
|---|---|---|
| fastapi | 0.162.2 | MIT |
| uvicorn[standard] | 0.54.0 | BSD-3-Clause |
| pydantic | 2.14.2 | MIT |
| python-multipart | 0.0.33 | Apache-2.0 |
| pytest | 9.0.3 | MIT |
| httpx | 0.28.1 | BSD-3-Clause |
| PyYAML | 6.0.3 | MIT |

System prerequisite: `git` (reads the demo bundle; the only external binary).

## Templates / boilerplate
| Item | Where from |
|---|---|
| none | every file hand- or agent-authored for this repository; no UI kit, no starter repo, no generated scaffold |

## External services
| Service | Used for |
|---|---|
| none | — |

*None used* applies to: network calls at runtime, issue/PR fetching (JSON files are uploaded, not pulled), analytics, error tracking, CDN assets (all frontend assets are local; no external fonts/scripts).

## Corrections vs the external reference build

An archive of that build's disclosures lives at [reference-other-agent/](reference-other-agent/). Its disclosure claims are corrected here:

| Their claim | Correction |
|---|---|
| Authorship: Google AI Studio Agent, “Gemini 2.5 Flash / Gemini 3.8 Flash” | Arena Agent Mode (agentic coding harness); no live model API of any kind was called in this build — replay fixtures are `handwritten-reference` |
| Licence MIT marked **approved** (N1_DECISIONS.md) | Licence is **undecided** — N1-8 in [N1_DECISIONS.md](N1_DECISIONS.md); D3 blocked until chosen |
| React 19 / Vite 8 / Tailwind / Express / 21 tsx tests on `localhost:3000` | This build: static vanilla SPA + FastAPI + SQLite on `http://localhost:8000`; tests via `python3 -m pytest` — 48 passed, 1 skipped |
| Roles: Successor “Jordan Lee”, Admin “Morgan Chen” | Successor **Diya Raman**; Admin **Krushna Patil** (synthetic) |
| Gitleaks binary | built-in regex scanner (`backend/app/pipeline/clean.py`, SEC-2) — no external scanner binary is used |
