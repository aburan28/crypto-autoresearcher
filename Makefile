# Local entry points. `make help` lists them.
#
# Targets that spend tokens are marked. Everything else is free and offline.

PYTHON ?= python3
BACKEND ?= $(AUTORESEARCH_BACKEND)
TRIALS ?= 5

.PHONY: help install doctor status check check-harness check-ledger test loop \
        eval-dev eval-held-out baseline clean

help:
	@echo "setup"
	@echo "  make install         editable install + all dependencies"
	@echo "  make doctor          is this machine ready? (free, offline)"
	@echo "  make status          what is configured and recorded (free)"
	@echo ""
	@echo "verify (free, offline)"
	@echo "  make check           everything below"
	@echo "  make check-harness   config, role bindings, eval suites, dispatch"
	@echo "  make check-ledger    ledger, run immutability, knowledge corpus"
	@echo "                       (currently RED: some KN-LIT-* entries predating"
	@echo "                        the tags requirement are missing 'tags')"
	@echo "  make test            the full test suite"
	@echo ""
	@echo "measure (SPENDS TOKENS — set BACKEND=, TRIALS=)"
	@echo "  make loop            dev suites + comparison against pinned baselines"
	@echo "  make eval-dev        dev split only, no baseline comparison"
	@echo "  make eval-held-out   held-out split — spend this sparingly"
	@echo "  make baseline SUITE=capability FROM=evals/results/<stamp>/capability"

install:
	$(PYTHON) -m pip install -e ".[agent,dev]"
	@echo
	@$(PYTHON) -m orchestration doctor || true

doctor:
	@$(PYTHON) -m orchestration doctor

status:
	@$(PYTHON) -m orchestration status

check: check-harness check-ledger

# What this toolchain owns. Green means your setup is good.
check-harness:
	$(PYTHON) -m orchestration.adapter doctor
	$(PYTHON) tools/generate_runtime_agents.py --check
	$(PYTHON) tools/check_runtime_bindings.py
	@for suite in evals/suites/*.yaml; do \
		$(PYTHON) -m orchestration.eval validate --suite $$suite || exit 1; \
	done
	$(PYTHON) tools/research_dispatch.py coordination/dispatch_queue.json \
		--output /tmp/dispatch.json --report /tmp/dispatch.md

# Research-record integrity. Currently RED for a pre-existing reason: literature
# entries seeded before `tags` became required are missing it. Kept separate so
# a newcomer can tell "my install is broken" from "this repo has an open issue".
check-ledger:
	$(PYTHON) tools/validate_ledger.py
	$(PYTHON) tools/check_run_immutability.py

test:
	$(PYTHON) -m pytest -q

loop:
	$(PYTHON) -m orchestration loop --trials $(TRIALS) \
		$(if $(BACKEND),--backend $(BACKEND),)

eval-dev:
	$(PYTHON) -m orchestration loop --trials $(TRIALS) --split dev --no-record \
		$(if $(BACKEND),--backend $(BACKEND),)

eval-held-out:
	$(PYTHON) -m orchestration loop --trials $(TRIALS) --split held_out \
		$(if $(BACKEND),--backend $(BACKEND),)

baseline:
	@test -n "$(SUITE)" || (echo "usage: make baseline SUITE=capability FROM=evals/results/<stamp>/capability" && exit 1)
	$(PYTHON) -m orchestration.eval baseline --source $(FROM) \
		--out evals/baselines/$(SUITE).json

clean:
	rm -rf .agent-state .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
