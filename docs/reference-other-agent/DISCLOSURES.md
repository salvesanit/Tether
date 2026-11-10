# Tether — Disclosures (D5)

## 1. APIs and External Services
| Service / API | Purpose | Usage in Build |
| :--- | :--- | :--- |
| **Google Gemini API** (`@google/genai`) | Optional live claim extraction when `LLM_MODE=live` | Hermetic offline execution default (`LLM_MODE=replay`); fallback to `rules` regex extractor when no API key provided. |
| **None other used** | N/A | No external third-party network calls are required for normal evaluation. |

## 2. Open Source Libraries & Frameworks
| Library / Package | Version | Licence | Purpose |
| :--- | :--- | :--- | :--- |
| **React** | ^19.0.1 | MIT | UI component library |
| **Vite** | ^8.3.0 | MIT | Frontend build tool and development server |
| **Tailwind CSS** | ^4.3.3 | MIT | Minimalist styling engine |
| **Express** | ^4.21.2 | MIT | Full-stack REST API server |
| **Lucide React** | ^0.546.0 | ISC | Minimal line icons |
| **Motion** | ^12.23.24 | MIT | Micro-interaction motion primitives |
| **TSX** | ^4.21.0 | MIT | TypeScript execution runner for Node.js tests |

## 3. Datasets and Fixtures
| Dataset | Source | Licence / Permission | Notes |
| :--- | :--- | :--- | :--- |
| **Beacon - Campus Hub** | NightOwls Team (Synthetic) | CC0 / Public Domain | 100% synthetic project data created for evaluation. Contains no real personal data or proprietary company information. |

## 4. Templates & Boilerplate
- Base Vite React template used for initial project directory scaffolding.
- All domain logic, readers, cleaner, pipeline, ledger, tests, and screens written specifically for Tether.
