<!-- commit 3a3fef9b0da9 · 2026-11-10 · model mode: replay · measured on the synthetic project -->
# Leak-test report — every route and role tried

commit `3a3fef9b0da9` · 2026-11-10 · model mode: `replay` · measured on the synthetic project.

**Result: PASS** — 14 sentinel strings probed on every row below. A hit anywhere for the successor or the leaver fails the build.

| Role | Route | Status | Sentinel hits | OK |
|---|---|---|---|---|
| successor | `/` | 200 | 0 | ✓ |
| successor | `/judge` | 200 | 0 | ✓ |
| successor | `/api/projects` | 200 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598` | 200 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/sources` | 200 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/claims` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/conflicts` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/gaps` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/quarantine` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/gates` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/handover` | 200 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/export` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/log` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/runs/latest` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/dropped` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/proposals` | 403 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/versions/latest` | 200 | 0 | ✓ |
| successor | `/api/projects/p_d5ec05780e222598/versions/v1.0` | 200 | 0 | ✓ |
| leaver | `/` | 200 | 0 | ✓ |
| leaver | `/judge` | 200 | 0 | ✓ |
| leaver | `/api/projects` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/sources` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/claims` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/conflicts` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/gaps` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/quarantine` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/gates` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/handover` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/export` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/log` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/runs/latest` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/dropped` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/proposals` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/versions/latest` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_d5ec05780e222598/versions/v1.0` | 200 | 0 | ✓ |
| reviewer | `/` | 200 | 0 | ✓ |
| reviewer | `/judge` | 200 | 0 | ✓ |
| reviewer | `/api/projects` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/sources` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/claims` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/conflicts` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/gaps` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/quarantine` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/gates` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/handover` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/export` | 403 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/log` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/runs/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/dropped` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/proposals` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/versions/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_d5ec05780e222598/versions/v1.0` | 200 | 0 | ✓ |
| admin | `/` | 200 | 0 | ✓ |
| admin | `/judge` | 200 | 0 | ✓ |
| admin | `/api/projects` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/sources` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/claims` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/conflicts` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/gaps` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/quarantine` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/gates` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/handover` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/export` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/log` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/runs/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/dropped` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/proposals` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/versions/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_d5ec05780e222598/versions/v1.0` | 200 | 0 | ✓ |
| successor | `/api/spans/span_c24a52e13d259…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_bed7dfe4b632f…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_ce641c95f9aee…` | 403 | 0 | ✓ |
| leaver | `/api/spans/span_c24a52e13d259…` | 403 | 0 | ✓ |

No restricted, confidential, personal-data or honeytoken string crossed the successor or leaver boundary on any route, including direct span IDs (403) and the export and the log.
