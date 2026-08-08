# Local entry points for the knowledge base. `make help` lists them.
#
# The default configuration is offline: a filesystem corpus under .kb-corpus
# and an embedded Qdrant. `make qdrant-up` switches to a real server.

PYTHON ?= python3
REPO_ROOT ?= ..
QUESTIONS ?= tests/retrieval_eval/questions.jsonl

.PHONY: help install install-all test test-fast lint slice ingest search status \
        doctor evaluate eval-slice eval-manifest qdrant-up qdrant-down mcp clean

help:
	@echo "setup"
	@echo "  make install       core install (no Qdrant, no AWS, no Docling)"
	@echo "  make install-all   everything except docling and transformers"
	@echo ""
	@echo "local vertical slice"
	@echo "  make qdrant-up     start Qdrant in docker"
	@echo "  make slice         stage this repo -> ingest -> report status"
	@echo "  make search Q='negative results for Semaev decomposition'"
	@echo "  make status        corpus, manifest, and index state"
	@echo "  make doctor        check the pieces are reachable and consistent"
	@echo ""
	@echo "evaluate"
	@echo "  make eval-slice    stage + ingest the frozen evaluation corpus"
	@echo "  make eval-manifest report drift between the frozen slice and the globs"
	@echo "  make evaluate      hybrid vs dense vs sparse, against the gates"
	@echo ""
	@echo "verify"
	@echo "  make test          full suite (builds a ~610 document corpus)"
	@echo "  make test-fast     unit tests only"
	@echo ""
	@echo "serve"
	@echo "  make mcp           run the FastMCP server on stdio"

install:
	$(PYTHON) -m pip install -e .

install-all:
	$(PYTHON) -m pip install -e ".[index,mcp,aws,dev]"

qdrant-up:
	docker compose up -d qdrant
	@echo "qdrant on http://localhost:6333 -- export CRYPTO_KB_QDRANT_URL=http://localhost:6333"

qdrant-down:
	docker compose down

# Stage the repository's own records into the corpus layout, then ingest.
# Both steps are idempotent: re-running changes nothing that has not changed.
slice:
	$(PYTHON) -m crypto_kb.cli stage-repo $(REPO_ROOT)
	$(PYTHON) -m crypto_kb.cli ingest
	$(PYTHON) -m crypto_kb.cli status

ingest:
	$(PYTHON) -m crypto_kb.cli ingest

search:
	@test -n "$(Q)" || (echo "usage: make search Q='your query'" && exit 1)
	$(PYTHON) -m crypto_kb.cli search "$(Q)"

status:
	$(PYTHON) -m crypto_kb.cli status

doctor:
	$(PYTHON) -m crypto_kb.cli doctor

# The question set is labelled against the fixed evaluation slice, so the
# corpus is staged from it rather than from whatever happens to be ingested.
eval-slice:
	$(PYTHON) -m crypto_kb.cli stage-repo $(REPO_ROOT) --eval-slice
	$(PYTHON) -m crypto_kb.cli ingest

evaluate:
	$(PYTHON) -m crypto_kb.cli evaluate --questions $(QUESTIONS)

# Reports what the globs match that the frozen slice does not. Exits non-zero
# only when a frozen path has been deleted, which invalidates question labels.
eval-manifest:
	$(PYTHON) -m crypto_kb.cli eval-manifest $(REPO_ROOT)

mcp:
	$(PYTHON) -m crypto_kb.mcp.server

test:
	$(PYTHON) -m pytest -q

test-fast:
	$(PYTHON) -m pytest tests/unit -q

clean:
	rm -rf .kb-corpus .pytest_cache
	find . -name __pycache__ -type d -prune -exec rm -rf {} +
