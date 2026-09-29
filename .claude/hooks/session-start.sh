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

# SageMath 10.9, pinned to match the version driver.py/checker.py hard-assert
# (dependencies.json's "sage": "10.9" across frozen experiments, e.g.
# EXP-FROB-d8aa37). Workspace tooling only: this does NOT satisfy a frozen
# experiment's runtime-lock admission (that stays a Coordinator-pinned,
# hash-verified sandbox; see AGENTS.md and each experiment's
# dependencies.json/linux-runtime-lock.json). What it does let an Executor or
# a human run safely is `sage -python .../driver.py --self-test` during
# implementation -- restricted to fixed, non-scientific fixtures per
# dependencies.json's "stage0 scientific constructors during implementation"
# prohibition -- plus general Sage-touching dev/lint work. Heavy (~8GiB), so
# only for the web container, and skipped rather than filling the disk.
if [ "${CLAUDE_CODE_REMOTE:-}" = "true" ]; then
    SAGE_PREFIX=/opt/conda-sage
    SAGE_ENV="$SAGE_PREFIX/envs/sage"
    if [ -x "$SAGE_ENV/bin/python3" ] \
        && "$SAGE_ENV/bin/python3" -c "
from sage.env import SAGE_VERSION
import sys
sys.exit(0 if SAGE_VERSION == '10.9' else 1)
" 2>/dev/null; then
        : # already installed and pinned correctly -- container cache did its job
    elif [ "$(df -Pk /opt 2>/dev/null | awk 'NR==2{print $4}')" -lt 10485760 ] 2>/dev/null; then
        echo "session-start: <10GiB free under /opt, skipping SageMath 10.9 install" >&2
    else
        echo "session-start: installing SageMath 10.9 (conda-forge, ~8GiB) for workspace use" >&2
        MM=/tmp/session-start-micromamba
        if [ ! -x "$MM" ]; then
            curl -fsSL --max-time 60 https://micro.mamba.pm/api/micromamba/linux-64/latest \
                | tar xj -O bin/micromamba > "$MM.tmp" \
                && mv "$MM.tmp" "$MM" && chmod +x "$MM"
        fi
        if [ -x "$MM" ]; then
            "$MM" create -y -r "$SAGE_PREFIX" -p "$SAGE_ENV" -c conda-forge "sage=10.9" \
                || echo "session-start: SageMath install failed; rerun manually if needed" >&2
        else
            echo "session-start: could not fetch micromamba; skipping SageMath install" >&2
        fi
    fi

    # A shim on PATH matching the official upstream Sage CLI's
    # `sage -python <script> [args...]` convention that frozen trial-plan
    # argv uses. conda-forge's own `sage` entry point (sage.cli.__main__) has
    # no -python subcommand; everything else delegates to it unchanged.
    if [ -x "$SAGE_ENV/bin/python3" ]; then
        mkdir -p "$SAGE_PREFIX/bin"
        cat > "$SAGE_PREFIX/bin/sage" << SAGESHIM
#!/bin/sh
if [ "\$1" = "-python" ]; then
    shift
    exec "$SAGE_ENV/bin/python3" "\$@"
fi
exec "$SAGE_ENV/bin/sage" "\$@"
SAGESHIM
        chmod +x "$SAGE_PREFIX/bin/sage"
        if [ -n "${CLAUDE_ENV_FILE:-}" ]; then
            echo "export PATH=\"$SAGE_PREFIX/bin:\$PATH\"" >> "$CLAUDE_ENV_FILE"
        fi
    fi
fi

exit 0
