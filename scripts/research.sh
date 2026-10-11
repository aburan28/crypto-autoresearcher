#!/usr/bin/env bash
# One entry point for the research supervisor, whichever provider serves it.
#
#   scripts/research.sh <preset> [autopilot flags...]
#   scripts/research.sh --list              # every preset, what it needs
#
#   scripts/research.sh anthropic-batch                 # Claude Code + Message Batches drafts
#   scripts/research.sh openrouter --once               # OpenCode through OpenRouter
#   scripts/research.sh openrouter --model vendor/id \
#       --model-caps effort=high,context=200000,output=32000
#   scripts/research.sh abliterated                     # OpenCode against Abliteration.ai
#   scripts/research.sh abliterated-claude --dry-run    # Claude Code against its Anthropic endpoint
#   scripts/research.sh local --report
#
# Everything after the preset is passed to `autoresearch campaign autopilot`;
# `--dry-run` shows the plan and the next action without a model call, `--once`
# runs one action, no limit keeps running. Credentials come from the
# environment or `.env` (never from this script); models come from
# orchestration/model-bindings.yaml and orchestration/model-bindings.local.yaml.
set -euo pipefail

repo=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$repo"

usage() {
    sed -n '2,20p' "${BASH_SOURCE[0]}" | sed 's/^# \{0,1\}//'
}

pick_python() {
    if [ -n "${AUTORESEARCH_PYTHON:-}" ]; then
        printf '%s\n' "$AUTORESEARCH_PYTHON"
        return
    fi
    # The pinned interpreter first; a distribution python3 only when it is
    # new enough for the package (see .python-version).
    for candidate in /usr/local/bin/python3 python3; do
        if command -v "$candidate" >/dev/null 2>&1 &&
           "$candidate" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null; then
            printf '%s\n' "$candidate"
            return
        fi
    done
    echo "research.sh: no python3 >= 3.12 found; set AUTORESEARCH_PYTHON" >&2
    exit 2
}

case "${1:-}" in
    ""|-h|--help)
        usage
        exit 0
        ;;
    --list|--list-presets)
        exec "$(pick_python)" -m orchestration campaign autopilot --list-presets
        ;;
    --*)
        echo "research.sh: the first argument is a preset name (see --list)" >&2
        exit 2
        ;;
esac

preset=$1
shift
exec "$(pick_python)" -m orchestration campaign autopilot --preset "$preset" "$@"
