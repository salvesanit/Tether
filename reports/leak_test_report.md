<!-- commit 05b0538eb6ee · 2026-11-10 · model mode: replay · measured on the synthetic project -->
# Leak-test report — every route and role tried

commit `05b0538eb6ee` · 2026-11-10 · model mode: `replay` · measured on the synthetic project.

**Result: PASS** — 14 sentinel strings probed on every row below. A hit anywhere for the successor or the leaver fails the build.

| Role | Route | Status | Sentinel hits | OK |
|---|---|---|---|---|
| successor | `/` | 200 | 0 | ✓ |
| successor | `/judge` | 200 | 0 | ✓ |
| successor | `/api/projects` | 200 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1` | 200 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/sources` | 200 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/claims` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/conflicts` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/gaps` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/quarantine` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/gates` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/handover` | 200 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/export` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/log` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/runs/latest` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/dropped` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/proposals` | 403 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/versions/latest` | 200 | 0 | ✓ |
| successor | `/api/projects/p_38ae901c25df74e1/versions/v1.0` | 200 | 0 | ✓ |
| leaver | `/` | 200 | 0 | ✓ |
| leaver | `/judge` | 200 | 0 | ✓ |
| leaver | `/api/projects` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/sources` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/claims` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/conflicts` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/gaps` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/quarantine` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/gates` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/handover` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/export` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/log` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/runs/latest` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/dropped` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/proposals` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/versions/latest` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_38ae901c25df74e1/versions/v1.0` | 200 | 0 | ✓ |
| reviewer | `/` | 200 | 0 | ✓ |
| reviewer | `/judge` | 200 | 0 | ✓ |
| reviewer | `/api/projects` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/sources` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/claims` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/conflicts` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/gaps` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/quarantine` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/gates` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/handover` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/export` | 403 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/log` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/runs/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/dropped` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/proposals` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/versions/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_38ae901c25df74e1/versions/v1.0` | 200 | 0 | ✓ |
| admin | `/` | 200 | 0 | ✓ |
| admin | `/judge` | 200 | 0 | ✓ |
| admin | `/api/projects` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/sources` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/claims` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/conflicts` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/gaps` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/quarantine` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/gates` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/handover` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/export` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/log` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/runs/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/dropped` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/proposals` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/versions/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_38ae901c25df74e1/versions/v1.0` | 200 | 0 | ✓ |
| successor | `/api/spans/span_9244862534410…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_bac4262719341…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_51cdf477585f8…` | 403 | 0 | ✓ |
| leaver | `/api/spans/span_51cdf477585f8…` | 403 | 0 | ✓ |

No restricted, confidential, personal-data or honeytoken string crossed the successor or leaver boundary on any route, including direct span IDs (403) and the export and the log.
