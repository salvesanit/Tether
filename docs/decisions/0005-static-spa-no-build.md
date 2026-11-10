# 0005 — static SPA (no build step) instead of Next.js
Context: Round 1 declared Next.js + TypeScript. Build constraint: one Python process, no node in the sandbox, inspectable output. The judge counts verified behaviour, not framework names.
Decision: vanilla HTML/CSS/JS served by the API (`frontend/`), semantic landmarks, `:focus-visible`, reduced-motion support, data-testid hooks, stable routes (/p/{id}/…, /judge).
Alternatives rejected: Next.js (build chain unverifiable offline; large surface for a single-flow app); SSR framework of any kind (nothing to render but JSON + one page).
Consequence: no TS type safety in the frontend (mitigated by small surface + smoke checks in UX-1); the stack change is recorded in CHANGES_FROM_ROUND1.
