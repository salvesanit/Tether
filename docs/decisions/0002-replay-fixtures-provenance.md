# 0002 — replay fixtures carry provenance; handwritten-reference is never called model output
Context: The demo must run offline with no key. The model call is one seam among many.
Decision: `fixtures/llm/extract-claims-v3.<sha>.json`, one file per unique chunk (byte-identical chunks union their twins' claims). Each file records `provenance` (`handwritten-reference` today; `model` reserved for a live recording), date, prompt version, input hash. A chunk with no recording falls back to the rules extractor and the run says `extractor: rules`.
Alternatives rejected: fabricating "recorded model" outputs; silently degrading to rules without saying so; generating fixtures at test time (unrepeatable).
Consequence: reports show the checks and the plumbing work, not that a model is good; `make record` (scripts/record_fixtures.py) regenerates fixtures when a key is present; fixtures are reviewed as code in diffs.
