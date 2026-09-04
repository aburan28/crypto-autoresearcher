# Local entry points. `make help` lists them.
#
# Targets that spend tokens are marked. Everything else is free and offline.

PYTHON ?= python3
BACKEND ?= $(AUTORESEARCH_BACKEND)
TRIALS ?= 5

.PHONY: help install doctor status check check-harness check-ledger test loop \
        eval-dev eval-held-out baseline sources clean

help:
	@echo "setup"
	@echo "  make install         editable install + all dependencies"
	@echo "  make doctor          is this machine ready? (free, offline)"
	@echo "  make status          what is configured and recorded (free)"
	@echo "  make ledger-status   ledger census + active goal heads (free)"
	@echo ""
	@echo "verify (free, offline)"
	@echo "  make check           everything below"
	@echo "  make check-harness   config, role bindings, eval suites, dispatch"
	@echo "  make check-ledger    ledger, run immutability, knowledge corpus"
	@echo "                       (currently RED: some KN-LIT-* entries predating"
	@echo "                        the tags requirement are missing 'tags')"
	@echo "  make test            the full test suite"
	@echo ""
	@echo "curate (free, offline)"
	@echo "  make sources         rebuild knowledge/SOURCES.md + sources.json"
	@echo ""
	@echo "measure (SPENDS TOKENS — set BACKEND=, TRIALS=)"
	@echo "  make loop            dev suites + comparison against pinned baselines"
	@echo "  make eval-dev        dev split only, no baseline comparison"
	@echo "  make eval-held-out   held-out split — spend this sparingly"
	@echo "  make baseline SUITE=capability FROM=evals/results/<stamp>/capability"

install: hooks
	TMPDIR=$$(mktemp -d /tmp/autoresearch-build.XXXXXX) \
		$(PYTHON) -m pip install -e ".[agent,dev]"
	@echo
	@$(PYTHON) -m orchestration doctor || true

# CI is the backstop, not the gate: workflows from a new contributor sit in
# "awaiting approval" and did not run at all on the two PRs that corrupted
# nine records. The local hook is what actually catches a half-finished merge,
# so it is installed by default rather than opted into.
# PR-SCOPED, deliberately. check_merge_hygiene.py is absolute without --base,
# and an absolute pre-commit hook refuses EVERY commit in the repository while
# any record anywhere is unparseable -- including records the commit does not
# touch and whose owning campaign is the only one that can repair them. That
# is the coupling the tool's own header calls the dominant failure at 115 open
# branches, and it blocked this repo outright: 7 records broken on main meant
# no commit could be made at all. Scoping preserves the check that matters --
# break a record and you changed it, so you are still caught -- while
# .github/workflows/main-health.yml keeps the absolute sweep on main.
hooks:
	@mkdir -p .git/hooks
	@printf '#!/bin/sh\nif git rev-parse --verify -q origin/main >/dev/null; then\n  exec python3 tools/check_merge_hygiene.py --base origin/main\nfi\nexec python3 tools/check_merge_hygiene.py\n' \
		> .git/hooks/pre-commit
	@chmod +x .git/hooks/pre-commit
	@echo "installed .git/hooks/pre-commit (merge hygiene, PR-scoped vs origin/main)"

doctor:
	@$(PYTHON) -m orchestration doctor

status:
	@$(PYTHON) -m orchestration status

# The read-only view of research state. Both are projections: reading the
# records themselves is ~18M tokens for the ledger and ~904k for the goal
# heads (CLAUDE.md, "Reading state: project, never `cat`").
ledger-status:
	@$(PYTHON) tools/ledger_summary.py
	@$(PYTHON) tools/goal_head.py list --status active

check: check-harness check-ledger

# What this toolchain owns. Green means your setup is good.
check-harness:
	$(PYTHON) -m orchestration.adapter doctor
	$(PYTHON) tools/check_inference_cost_policy.py
	$(PYTHON) tools/generate_runtime_agents.py --check
	$(PYTHON) tools/check_runtime_bindings.py
	@for suite in evals/suites/*.yaml; do \
		case "$$suite" in */._*) continue ;; esac; \
		$(PYTHON) -m orchestration.eval validate --suite $$suite || exit 1; \
	done
	$(PYTHON) tools/research_dispatch.py coordination/dispatch_queue.json \
		--output /tmp/dispatch.json --report /tmp/dispatch.md

# Research-record integrity. Currently RED for a pre-existing reason: literature
# entries seeded before `tags` became required are missing it. Kept separate so
# a newcomer can tell "my install is broken" from "this repo has an open issue".
check-ledger: check-merge
	$(PYTHON) tools/validate_ledger.py
	$(PYTHON) tools/check_run_immutability.py
	$(PYTHON) tools/port_autolab_experiments.py --verify
	$(PYTHON) tools/build_source_index.py --check

# Derived, like knowledge/INDEX.md: entries and inputs/ are the source of truth.
# Regenerate after adding a KN-LIT entry or vendoring a source, and commit the
# result -- `make check-ledger` fails while it is stale.
sources:
	$(PYTHON) tools/build_source_index.py

# Absolute gate, and deliberately ordered first: conflict markers and
# unparseable records make every check after this one meaningless. A record
# that does not parse cannot be schema-checked, so breaking it REMOVES
# validator errors -- which a relative gate reads as an improvement.
check-merge:
	$(PYTHON) tools/check_merge_hygiene.py --base origin/main

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
