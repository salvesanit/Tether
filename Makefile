# Tether — the handover that holds. Canonical commands.
.PHONY: setup run seed verify test judge stop

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
