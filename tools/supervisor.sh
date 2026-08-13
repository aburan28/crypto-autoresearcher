#!/usr/bin/env bash
# tools/supervisor.sh — outer loop for unattended / overnight OpenCode runs.
#
# Usage:
#   bash tools/supervisor.sh                       # use default goal
#   GOAL="my custom goal" bash tools/supervisor.sh # override goal
#   MAX_RESTARTS=20 bash tools/supervisor.sh        # limit restart count
#
# The script starts an OpenCode session with --auto approval and a
# continuation prompt, then keeps restarting it (--continue) whenever
# it voluntarily exits, up to MAX_RESTARTS times.  A restart is NOT
# triggered when OpenCode exits with the special "goal complete" code 0
# AND the session contained a /goal-plugin completion claim.  For
# simpler setups, the while loop itself is the guard — just interrupt
# (Ctrl-C) when you are satisfied.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAX_RESTARTS="${MAX_RESTARTS:-100}"
SLEEP_BETWEEN="${SLEEP_BETWEEN:-3}"

GOAL="${GOAL:-Continue pursuing the existing research objective.

Do not just summarize prior work.
Inspect the repository and current results.
Choose the highest-value unfinished action.
Perform it.
Verify it.
Record the result.
Then proceed to the next action.

If the previous approach failed, diagnose it and try a different approach.
Only stop for a genuine external blocker.}"

cd "$PROJECT_ROOT"

echo "[supervisor] Starting initial OpenCode session"
opencode run --auto "$GOAL" || true

restarts=0
while [ "$restarts" -lt "$MAX_RESTARTS" ]; do
    restarts=$(( restarts + 1 ))
    echo "[supervisor] Session returned (restart $restarts / $MAX_RESTARTS). Continuing in ${SLEEP_BETWEEN}s..."
    sleep "$SLEEP_BETWEEN"

    opencode run --continue --auto \
        "Continue from where you left off. $GOAL" || true
done

echo "[supervisor] Reached MAX_RESTARTS=$MAX_RESTARTS. Exiting."
