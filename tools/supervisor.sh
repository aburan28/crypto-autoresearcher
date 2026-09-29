#!/usr/bin/env bash
# tools/supervisor.sh — outer loop for unattended / overnight OpenCode runs.
#
# Usage:
#   bash tools/supervisor.sh                       # use default goal
#   GOAL="my custom goal" bash tools/supervisor.sh # override goal
#   MAX_RESTARTS=20 bash tools/supervisor.sh        # limit restart count
#   PREFLIGHT_ONLY=1 bash tools/supervisor.sh       # check inference, then exit
#
# The script starts an OpenCode session with --auto approval and a
# continuation prompt, then keeps restarting it (--continue) whenever
# it voluntarily exits, up to MAX_RESTARTS times.  Interrupt (Ctrl-C)
# when you are satisfied.
#
# Inference path (see ~/.config/opencode/opencode.jsonc and opencode.json):
#     opencode -> 127.0.0.1:8787 (vllm-lazy-proxy) -> vllm-alb -> g6e GPU box
# The proxy is what launches a stopped instance; an ALB with no healthy
# target cannot.  So the preflight below probes the PROXY, not the ALB.
# Note that /v1/models deliberately does NOT boot a GPU -- a green
# preflight means "the path is wired", not "a GPU is already warm".  The
# first real request pays the cold-start wait (up to ~20 min).

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MAX_RESTARTS="${MAX_RESTARTS:-100}"
SLEEP_BETWEEN="${SLEEP_BETWEEN:-3}"

# Fail-fast guard.  Without this, a broken model or a dead provider makes
# every session return instantly and the loop burns all MAX_RESTARTS in a
# couple of minutes while doing no research at all.  A session shorter than
# MIN_SESSION_SECS counts as a failure; MAX_CONSECUTIVE_FAST of them in a
# row aborts the run.
MIN_SESSION_SECS="${MIN_SESSION_SECS:-60}"
MAX_CONSECUTIVE_FAST="${MAX_CONSECUTIVE_FAST:-3}"

PROXY_URL="${PROXY_URL:-http://127.0.0.1:8787/v1}"
EXPECT_MODEL="${EXPECT_MODEL:-qwen3.8-27b}"
LOG_DIR="${LOG_DIR:-$PROJECT_ROOT/.supervisor-logs}"

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

log() { echo "[supervisor] $*"; }

preflight() {
    log "Preflight: checking inference path"

    if ! command -v opencode >/dev/null 2>&1; then
        log "FATAL: opencode is not on PATH."
        return 1
    fi

    # Is the lazy-launch proxy up?  It is a launchd job
    # (com.adamburan.vllm-lazy-proxy); if it died, nothing will start a GPU.
    local models
    if ! models="$(curl -sf -m 10 "$PROXY_URL/models" 2>/dev/null)"; then
        log "FATAL: no answer from the lazy proxy at $PROXY_URL"
        log "  Start it with:  launchctl kickstart -k gui/\$(id -u)/com.adamburan.vllm-lazy-proxy"
        return 1
    fi

    if ! printf '%s' "$models" | grep -q "$EXPECT_MODEL"; then
        log "FATAL: proxy is up but does not serve '$EXPECT_MODEL'."
        log "  It reported: $models"
        return 1
    fi
    log "  proxy OK, serving $EXPECT_MODEL"

    # Catch the actual failure this script hit before: a project-level
    # opencode.json pointing the model at a provider with no credits.
    if [ -f "$PROJECT_ROOT/opencode.json" ] \
       && grep -q '"model"[[:space:]]*:[[:space:]]*"openai/' "$PROJECT_ROOT/opencode.json"; then
        log "WARNING: opencode.json still routes 'model' to the openai provider."
        log "  If that account has no credits, every session will fail instantly."
    fi

    log "Preflight passed."
    return 0
}

if ! preflight; then
    log "Aborting: inference path is not usable.  Nothing was run."
    exit 1
fi

if [ -n "${PREFLIGHT_ONLY:-}" ]; then
    log "PREFLIGHT_ONLY set — exiting without starting a session."
    exit 0
fi

mkdir -p "$LOG_DIR"
RUN_LOG="$LOG_DIR/supervisor-$(date +%Y%m%d-%H%M%S).log"
log "Logging sessions to $RUN_LOG"

consecutive_fast=0
restarts=0

run_session() {
    # $1: human label, remaining args: opencode arguments
    local label="$1"; shift
    local started ended elapsed
    started="$(date +%s)"

    log "$label"
    opencode "$@" 2>&1 | tee -a "$RUN_LOG" || true

    ended="$(date +%s)"
    elapsed=$(( ended - started ))

    if [ "$elapsed" -lt "$MIN_SESSION_SECS" ]; then
        consecutive_fast=$(( consecutive_fast + 1 ))
        log "Session returned after ${elapsed}s (< ${MIN_SESSION_SECS}s) — \
suspected failure ${consecutive_fast}/${MAX_CONSECUTIVE_FAST}."
    else
        consecutive_fast=0
        log "Session ran ${elapsed}s."
    fi

    if [ "$consecutive_fast" -ge "$MAX_CONSECUTIVE_FAST" ]; then
        log "FATAL: ${MAX_CONSECUTIVE_FAST} consecutive fast exits. Something is"
        log "  broken (model, credits, proxy). Not looping further."
        log "  Last output is in $RUN_LOG"
        exit 1
    fi
}

run_session "Starting initial OpenCode session" run --auto "$GOAL"

while [ "$restarts" -lt "$MAX_RESTARTS" ]; do
    restarts=$(( restarts + 1 ))
    log "Continuing in ${SLEEP_BETWEEN}s (restart $restarts / $MAX_RESTARTS)..."
    sleep "$SLEEP_BETWEEN"

    run_session "Resuming session (restart $restarts)" \
        run --continue --auto "Continue from where you left off. $GOAL"
done

log "Reached MAX_RESTARTS=$MAX_RESTARTS. Exiting."
