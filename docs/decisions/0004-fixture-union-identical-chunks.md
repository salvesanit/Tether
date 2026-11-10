# 0004 — byte-identical chunks share one fixture; twins' claims are unioned
Context: One 2026-11-10 refactor moved wrong-locator fake fixtures off the quote's span. The notes paragraph and chat message holding "Payments cutover happens on 2026-11-20." hash identically, and the fixture writer was last-write-wins — the recorded file kept only the fake and silently lost the two real facts (scratch rebuild: 59 kept, NS-01 missing).
Decision: group captured chunks by SHA-256 first; union claims across positions; write one fixture per unique chunk; identical claims dedupe by full dict signature.
Alternatives rejected: two fixtures per identical chunk (impossible — the reader keys by hash); per-position suffixes (breaks the hash key contract with the adapter).
Consequence: all 61 planted facts surface; the 2026-12-01 fake is proposed at both identical spans and dropped twice (dropped=21); `test_ck1_replay_run_kept_and_dropped_counts` asserts lost-facts==0.
