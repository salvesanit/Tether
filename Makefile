# Tether — the handover that holds. Canonical commands.
.PHONY: setup run seed verify test judge stop demo-tokens

setup:
	pip install -r requirements.txt

run:					## start the app on :8000 (TETHER_DB=tether.db, DEMO_MODE=true)
	python3 run.py

seed:					## load the Aster demo through the upload path (leaves the label gate for the judge)
	python3 scripts/seed.py

verify:				## full test suite + reports/verify.md (measured on the synthetic project)
	python3 scripts/verify.py

test:
	pytest backend/tests -q

judge:				## scripted four-minute path against a fresh throwaway DB
	./scripts/judge_walkthrough.sh

stop:
	-pkill -f "run.py" || true

demo-tokens:				## print the four role headers for API calls (only meaningful with DEMO_MODE=true)
	@echo "Tether demo (synthetic) — no secrets. Send one header per request:"; \
	for r in leaver reviewer successor admin; do \
	  echo "  $$r:    curl -H 'X-Tether-Role: $$r' http://localhost:8000/api/health"; \
	done; \
	echo "The browser role switcher exists only when DEMO_MODE=true."
