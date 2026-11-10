<!-- commit a261b138a879 · 2026-11-09 · model mode: replay · measured on the synthetic project -->
# Leak-test report — every route and role tried

commit `a261b138a879` · 2026-11-09 · model mode: `replay` · measured on the synthetic project.

**Result: PASS** — 10 sentinel strings probed on every row below. A hit anywhere for the successor or the leaver fails the build.

| Role | Route | Status | Sentinel hits | OK |
|---|---|---|---|---|
| successor | `/` | 200 | 0 | ✓ |
| successor | `/judge` | 200 | 0 | ✓ |
| successor | `/api/projects` | 200 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6` | 200 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/sources` | 200 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/claims` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/conflicts` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/gaps` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/quarantine` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/gates` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/handover` | 200 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/export` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/log` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/runs/latest` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/dropped` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/proposals` | 403 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/versions/latest` | 200 | 0 | ✓ |
| successor | `/api/projects/p_49c9f7a9603856d6/versions/v1.0` | 200 | 0 | ✓ |
| leaver | `/` | 200 | 0 | ✓ |
| leaver | `/judge` | 200 | 0 | ✓ |
| leaver | `/api/projects` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/sources` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/claims` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/conflicts` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/gaps` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/quarantine` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/gates` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/handover` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/export` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/log` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/runs/latest` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/dropped` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/proposals` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/versions/latest` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_49c9f7a9603856d6/versions/v1.0` | 200 | 0 | ✓ |
| reviewer | `/` | 200 | 0 | ✓ |
| reviewer | `/judge` | 200 | 0 | ✓ |
| reviewer | `/api/projects` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/sources` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/claims` | 200 | 2 | ✗ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/conflicts` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/gaps` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/quarantine` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/gates` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/handover` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/export` | 403 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/log` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/runs/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/dropped` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/proposals` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/versions/latest` | 200 | 2 | ✗ |
| reviewer | `/api/projects/p_49c9f7a9603856d6/versions/v1.0` | 200 | 2 | ✗ |
| admin | `/` | 200 | 0 | ✓ |
| admin | `/judge` | 200 | 0 | ✓ |
| admin | `/api/projects` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/sources` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/claims` | 200 | 2 | ✗ |
| admin | `/api/projects/p_49c9f7a9603856d6/conflicts` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/gaps` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/quarantine` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/gates` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/handover` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/export` | 200 | 2 | ✗ |
| admin | `/api/projects/p_49c9f7a9603856d6/log` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/runs/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/dropped` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/proposals` | 200 | 0 | ✓ |
| admin | `/api/projects/p_49c9f7a9603856d6/versions/latest` | 200 | 2 | ✗ |
| admin | `/api/projects/p_49c9f7a9603856d6/versions/v1.0` | 200 | 2 | ✗ |
| successor | `/api/spans/span_799fb188de601…` | 403 | 0 | ✓ |

No restricted, confidential, personal-data or honeytoken string crossed the successor or leaver boundary on any route, including direct span IDs (403) and the export and the log.
