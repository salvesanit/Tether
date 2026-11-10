# Reliability — every failure mode, what you see, what proves it

| Failure mode | What the user sees | Covered by |
|---|---|---|
| Empty source uploaded | A plain error naming the file; nothing partial ingested | RD-2 (`backend/tests/test_rd.py`) |
| Malformed JSON (issues/PRs/chat) | 400 with a sentence, never a stack trace | RD-2 |
| One source missing (chat.json off) | Gap queue still opens; the report names the missing source | SW-1 (`backend/tests/test_sw1_source_off.py`) |
| Model timeout / unreachable / bad JSON (live mode) | Rules extractor picks up that chunk; the run records `extractor: rules`; chunk says so | adapter timeout 30s + catch-all → rules (`backend/app/llm/adapter.py`); IN-1 (`backend/tests/test_in1_input_change.py`) |
| No fixture recorded for a chunk (replay) | Rules extractor for that chunk; run records `extractor: rules` per chunk | `backend/app/llm/adapter.py` |
| Over the live-call cap (`LLM_MAX_CALLS`, default 200) | Rules extractor for the rest; cap counted on the run | `backend/app/llm/adapter.py` |
| Quote miss (any fake) | Claim dropped, counted (`quote_not_found`), openable dropped list; never shown as claim | CK-1 (`backend/tests/test_ck1_quote.py`); all 20 planted fakes drop — [reports/answer_key_report.md](../reports/answer_key_report.md) |
| Locator unresolvable | The candidate is dropped with `quote_not_found`; RD-1 pins every stored locator to exact text | RD-1 (`backend/tests/test_rd.py`) |
| Injection-like source text ("ignore previous instructions") | Chunk quarantined; reviewer item; no status/label/role/gate changes | SEC-3 (`backend/tests/test_sec.py`) |
| Honeytokens in excluded channels | Never stored, never in logs/exports/API/screens | SEC-1 (`backend/tests/test_sec.py`) |
| Secrets / PII in any source | `[REDACTED:type]` before storage; phone/email masked | SEC-2 (`backend/tests/test_sec.py`) |
| Sign with undecided conflict / unsettled uncertain items | 409 with the failing gates and the reason; a `sign.refused` log row | REV-1 (`backend/tests/test_rev1_gates.py`) |
| Skipped project state (e.g. share before sign) | 409 + `*.refused` log row | REV-1; sign/share refusal rows in `backend/app/api/main.py` |
| Successor reads restricted/confidential text (incl. direct span IDs) | 403; fail-closed citation rule — a span is readable only if at least one citing claim is readable by the role | PERM-1/2/3/4, [reports/leak_test_report.md](../reports/leak_test_report.md) (span rows) |
| Database unreachable | `/api/selftest` reports `database_reachable: false` with HTTP 500; `/api/health` stays a static ok | `backend/app/api/main.py` `selftest()` — **no dedicated automated test yet** |
| Oversized upload (> 25 MiB/file) | Refused with 413 and an `upload.refused` log row; nothing is stored | SEC-4 (`backend/tests/test_sec.py::test_sec4_oversized_upload_is_refused`) |
| Browser cannot launch (no chromium/libnspr4) | E2E-1 SKIPS with the reason in [reports/verify.md](../reports/verify.md); scripted path instead: `make judge` | E2E-1 (`backend/tests/test_e2e1_ux1.py`) |
| Concurrency on SQLite | WAL mode; single-process app; not load-tested | `db/migrations/001_init.sql` |

Two rules hold across the table: **fail closed** (when in doubt, 403/409, never through) and **say so on the record** (refusals and drops write log rows with reasons; reports count, never rate).
