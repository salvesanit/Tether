<!-- commit 8c22a41a3d83 · 2026-11-10 · model mode: replay · measured on the synthetic project -->
# Leak-test report — every route and role tried

commit `8c22a41a3d83` · 2026-11-10 · model mode: `replay` · measured on the synthetic project.

**Result: PASS** — 14 sentinel strings probed on every row below. A hit anywhere for the successor or the leaver fails the build.

| Role | Route | Status | Sentinel hits | OK |
|---|---|---|---|---|
| successor | `/` | 200 | 0 | ✓ |
| successor | `/judge` | 200 | 0 | ✓ |
| successor | `/api/projects` | 200 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24` | 200 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/sources` | 200 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/claims` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/conflicts` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/gaps` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/quarantine` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/gates` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/handover` | 200 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/export` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/log` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/runs/latest` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/dropped` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/proposals` | 403 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/versions/latest` | 200 | 0 | ✓ |
| successor | `/api/projects/p_78ebeffc9f806a24/versions/v1.0` | 200 | 0 | ✓ |
| leaver | `/` | 200 | 0 | ✓ |
| leaver | `/judge` | 200 | 0 | ✓ |
| leaver | `/api/projects` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/sources` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/claims` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/conflicts` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/gaps` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/quarantine` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/gates` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/handover` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/export` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/log` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/runs/latest` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/dropped` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/proposals` | 403 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/versions/latest` | 200 | 0 | ✓ |
| leaver | `/api/projects/p_78ebeffc9f806a24/versions/v1.0` | 200 | 0 | ✓ |
| reviewer | `/` | 200 | 0 | ✓ |
| reviewer | `/judge` | 200 | 0 | ✓ |
| reviewer | `/api/projects` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/sources` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/claims` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/conflicts` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/gaps` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/quarantine` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/gates` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/handover` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/export` | 403 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/log` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/runs/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/dropped` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/proposals` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/versions/latest` | 200 | 0 | ✓ |
| reviewer | `/api/projects/p_78ebeffc9f806a24/versions/v1.0` | 200 | 0 | ✓ |
| admin | `/` | 200 | 0 | ✓ |
| admin | `/judge` | 200 | 0 | ✓ |
| admin | `/api/projects` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/sources` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/claims` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/conflicts` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/gaps` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/quarantine` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/gates` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/handover` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/export` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/log` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/runs/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/dropped` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/proposals` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/versions/latest` | 200 | 0 | ✓ |
| admin | `/api/projects/p_78ebeffc9f806a24/versions/v1.0` | 200 | 0 | ✓ |
| successor | `/api/spans/span_3ace9aca6fbdb…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_72b5162253770…` | 403 | 0 | ✓ |
| successor | `/api/spans/span_17e7b0c93870a…` | 403 | 0 | ✓ |
| leaver | `/api/spans/span_17e7b0c93870a…` | 403 | 0 | ✓ |

No restricted, confidential, personal-data or honeytoken string crossed the successor or leaver boundary on any route, including direct span IDs (403) and the export and the log.
