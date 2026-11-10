<!-- commit 93be1ea87f54 · 2026-11-10 · model mode: replay · measured on the synthetic project -->
# Leak-test report — every route and role tried

commit `93be1ea87f54` · 2026-11-10 · model mode: `replay` · measured on the synthetic project.

**Result: PASS** — 14 sentinel strings probed on every row below. A hit anywhere for the successor or the leaver fails the build.

| Role | Route | Status | Sentinel hits | OK |
|---|---|---|---|---|
| successor | `/` | 200 | 0 | ✓ |
| successor | `/judge` | 200 | 0 | ✓ |
| successor | `/api/projects` | 200 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c` | 200 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/sources` | 200 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/claims` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/conflicts` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/gaps` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/quarantine` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/gates` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/handover` | 200 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/export` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/log` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/runs/latest` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/dropped` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/proposals` | 403 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/versions/latest` | 200 | 0 | ✓ |
| successor | `/api/projects/p_4ef555da01bf647c/versions/v1.0` | 200 | 0 | ✓ |
| leaver | `/` | 200 | 0 | ✓ |
| leaver | `/judge` | 200 | 0 | ✓ |
| leaver | `/api/projects` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/sources` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/claims` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/conflicts` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/gaps` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/quarantine` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/gates` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/handover` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/export` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/log` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/runs/latest` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/dropped` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/proposals` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/versions/latest` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_4ef555da01bf647c/versions/v1.0` | 200 | 0 | ✓ |
| reviewer | `/` | 200 | 0 | ✓ |
| reviewer | `/judge` | 200 | 0 | ✓ |
| reviewer | `/api/projects` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/sources` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/claims` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/conflicts` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/gaps` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/quarantine` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/gates` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/handover` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/export` | 403 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/log` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/runs/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/dropped` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/proposals` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/versions/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_4ef555da01bf647c/versions/v1.0` | 200 | 0 | ✓ |
| admin | `/` | 200 | 0 | ✓ |
| admin | `/judge` | 200 | 0 | ✓ |
| admin | `/api/projects` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/sources` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/claims` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/conflicts` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/gaps` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/quarantine` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/gates` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/handover` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/export` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/log` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/runs/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/dropped` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/proposals` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/versions/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_4ef555da01bf647c/versions/v1.0` | 200 | 0 | ✓ |
| successor | `/api/spans/span_7e34898771db6…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_0853249e7fcd7…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_c0359e6848057…` | 403 | 0 | ✓ |
| leaver | `/api/spans/span_7e34898771db6…` | 403 | 0 | ✓ |

No restricted, confidential, personal-data or honeytoken string crossed the successor or leaver boundary on any route, including direct span IDs (403) and the export and the log.
