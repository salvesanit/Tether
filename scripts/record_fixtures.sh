#!/bin/sh
# Record replay fixtures. Default: handwritten-reference from the answer key (no model involved).
# With LLM_API_KEY/LLM_URL/LLM_MODEL set and --live: records the real model (provenance "model").
set -e
cd "$(dirname "$0")/.."
if [ "$1" = "--live" ]; then
  exec python3 scripts/record_fixtures.py --mode live
fi
exec python3 scripts/record_fixtures.py --mode reference
