<!-- commit a6ce51adc492 · modified worktree · 2026-11-12 · model mode: replay · measured on the synthetic project -->
# Leak-test report — every route and role tried

commit `a6ce51adc492` · 2026-11-12 · model mode: `replay` · measured on the synthetic project.

**Result: PASS** — 14 sentinel strings probed on every row below. A hit anywhere for the successor or the leaver fails the build.

| Role | Route | Status | Sentinel hits | OK |
|---|---|---|---|---|
| successor | `/` | 200 | 0 | ✓ |
| successor | `/judge` | 200 | 0 | ✓ |
| successor | `/api/projects` | 200 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17` | 200 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/sources` | 200 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/claims` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/conflicts` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/gaps` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/quarantine` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/gates` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/handover` | 200 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/export` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/log` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/runs/latest` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/dropped` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/proposals` | 403 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/versions/latest` | 200 | 0 | ✓ |
| successor | `/api/projects/p_57cc78b800b81e17/versions/v1.0` | 200 | 0 | ✓ |
| leaver | `/` | 200 | 0 | ✓ |
| leaver | `/judge` | 200 | 0 | ✓ |
| leaver | `/api/projects` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/sources` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/claims` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/conflicts` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/gaps` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/quarantine` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/gates` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/handover` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/export` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/log` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/runs/latest` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/dropped` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/proposals` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/versions/latest` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_57cc78b800b81e17/versions/v1.0` | 200 | 0 | ✓ |
| reviewer | `/` | 200 | 0 | ✓ |
| reviewer | `/judge` | 200 | 0 | ✓ |
| reviewer | `/api/projects` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/sources` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/claims` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/conflicts` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/gaps` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/quarantine` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/gates` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/handover` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/export` | 403 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/log` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/runs/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/dropped` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/proposals` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/versions/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_57cc78b800b81e17/versions/v1.0` | 200 | 0 | ✓ |
| admin | `/` | 200 | 0 | ✓ |
| admin | `/judge` | 200 | 0 | ✓ |
| admin | `/api/projects` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/sources` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/claims` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/conflicts` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/gaps` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/quarantine` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/gates` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/handover` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/export` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/log` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/runs/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/dropped` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/proposals` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/versions/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_57cc78b800b81e17/versions/v1.0` | 200 | 0 | ✓ |
| successor | `/api/spans/span_3f628a82e1c70…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_18ffc078b0962…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_34230ae10b7bb…` | 403 | 0 | ✓ |
| leaver | `/api/spans/span_3f628a82e1c70…` | 403 | 0 | ✓ |

No restricted, confidential, personal-data or honeytoken string crossed the successor or leaver boundary on any route, including direct span IDs (403) and the export and the log.
