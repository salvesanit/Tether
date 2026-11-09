<!-- commit HEAD · 2026-11-09 · model mode: replay · measured on the synthetic project -->
# Leak-test report — every route and role tried

commit `HEAD` · 2026-11-09 · model mode: `replay` · measured on the synthetic project.

**Result: PASS** — 10 sentinel strings probed on every row below. A hit anywhere for the successor or the leaver fails the build.

| Role | Route | Status | Sentinel hits | OK |
|---|---|---|---|---|
| successor | `/` | 200 | 0 | ✓ |
| successor | `/judge` | 200 | 0 | ✓ |
| successor | `/api/projects` | 200 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06` | 200 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/sources` | 200 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/claims` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/conflicts` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/gaps` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/quarantine` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/gates` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/handover` | 200 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/export` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/log` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/runs/latest` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/dropped` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/proposals` | 403 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/versions/latest` | 200 | 0 | ✓ |
| successor | `/api/projects/p_a9b214dce35e8f06/versions/v1.0` | 200 | 0 | ✓ |
| leaver | `/` | 200 | 0 | ✓ |
| leaver | `/judge` | 200 | 0 | ✓ |
| leaver | `/api/projects` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/sources` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/claims` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/conflicts` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/gaps` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/quarantine` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/gates` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/handover` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/export` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/log` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/runs/latest` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/dropped` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/proposals` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/versions/latest` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_a9b214dce35e8f06/versions/v1.0` | 200 | 0 | ✓ |
| reviewer | `/` | 200 | 0 | ✓ |
| reviewer | `/judge` | 200 | 0 | ✓ |
| reviewer | `/api/projects` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/sources` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/claims` | 200 | 2 | ✗ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/conflicts` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/gaps` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/quarantine` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/gates` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/handover` | 200 | 2 | ✗ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/export` | 403 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/log` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/runs/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/dropped` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/proposals` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/versions/latest` | 200 | 2 | ✗ |
| reviewer | `/api/projects/p_a9b214dce35e8f06/versions/v1.0` | 200 | 2 | ✗ |
| admin | `/` | 200 | 0 | ✓ |
| admin | `/judge` | 200 | 0 | ✓ |
| admin | `/api/projects` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/sources` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/claims` | 200 | 2 | ✗ |
| admin | `/api/projects/p_a9b214dce35e8f06/conflicts` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/gaps` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/quarantine` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/gates` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/handover` | 200 | 2 | ✗ |
| admin | `/api/projects/p_a9b214dce35e8f06/export` | 200 | 2 | ✗ |
| admin | `/api/projects/p_a9b214dce35e8f06/log` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/runs/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/dropped` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/proposals` | 200 | 0 | ✓ |
| admin | `/api/projects/p_a9b214dce35e8f06/versions/latest` | 200 | 2 | ✗ |
| admin | `/api/projects/p_a9b214dce35e8f06/versions/v1.0` | 200 | 2 | ✗ |
| successor | `/api/spans/span_1d422cbc10d65…` | 403 | 0 | ✓ |

No restricted, confidential, personal-data or honeytoken string crossed the successor or leaver boundary on any route, including direct span IDs (403) and the export and the log.
