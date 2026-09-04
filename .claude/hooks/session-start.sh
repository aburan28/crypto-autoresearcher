#!/bin/bash
# SessionStart hook: make a fresh container able to run this repo's checks.
#
# Two things are wrong with a default clone here, and both cost a whole session
# to rediscover:
#
#   1. `sympy` and `pytest` are declared (pyproject.toml, requirements-dev.txt)
#      but absent, so `make check-harness` and `make test` fail on import
#      before running anything real.
#   2. The clone is SHALLOW. tools/research_dispatch.py verifies archive
#      receipts against commit reachability, and history the clone never
#      fetched reads as an unreachable commit -- which the portfolio sweep
#      reports as `needs_repair`. That is not a research result and not
#      repository corruption; it is a missing object. It once put 26 of 46
#      active goals in that bucket, leaving the harness nothing to dispatch.
#
# Idempotent, non-interactive, and never fatal: a session that starts with a
# degraded environment is better than one that does not start.
set -uo pipefail

cd "${CLAUDE_PROJECT_DIR:-$(git rev-parse --show-toplevel)}" || exit 0

# The declared toolchain. Small and slow-moving on purpose -- a run record has
# to stay reproducible years from now (see requirements-agent.txt).
python3 -m pip install -q --disable-pip-version-check -r requirements-dev.txt \
    || echo "session-start: dependency install failed; run 'pip install -r requirements-dev.txt'" >&2

# Deepen the clone so archive verification sees real history. Only adds
# objects: it rewrites nothing and touches no working tree.
if [ "$(git rev-parse --is-shallow-repository 2>/dev/null)" = "true" ]; then
    echo "session-start: shallow clone, fetching full history for archive verification" >&2
    git fetch --unshallow origin \
        || echo "session-start: --unshallow failed; goal_portfolio_health.py retries it, and warns while it is shallow" >&2
fi

# The merge-hygiene pre-commit hook. CI is the backstop, not the gate: a new
# contributor's workflows sit in "awaiting approval" and did not run at all on
# the two PRs that corrupted nine records (Makefile `hooks`).
# PR-scoped vs origin/main: absolute, it refuses every commit in the repo while
# any record anywhere is unparseable, including ones this commit never touched.
if mkdir -p .git/hooks 2>/dev/null; then
    printf '#!/bin/sh\nif git rev-parse --verify -q origin/main >/dev/null; then\n  exec python3 tools/check_merge_hygiene.py --base origin/main\nfi\nexec python3 tools/check_merge_hygiene.py\n' > .git/hooks/pre-commit \
        && chmod +x .git/hooks/pre-commit
fi

exit 0
