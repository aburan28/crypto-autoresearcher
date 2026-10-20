#!/usr/bin/env bash
# Live smoke test of the task-card batch lane (docs/model-tiers.md, "Batch lane"):
# director compile through a real Message Batch, `task_card.py run`, director
# assess through a second batch, each reply checked by `task_card.py ingest`.
# Needs ANTHROPIC_API_KEY (or Anthropic WIF) and the standalone delphi binary:
#   go install github.com/aburan28/conductor/cmd/delphi@main
# Spends two Sonnet 5.5 batch requests (a few thousand tokens each).
# Usage: examples/batch-lane/smoke.sh   (from the repository root)
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
DELPHI=${DELPHI:-delphi}
MODEL=${DELPHI_DIRECTOR_MODEL:-claude-sonnet-5-5}
if [ -z "${ANTHROPIC_API_KEY:-}" ] && [ -z "${DELPHI_FAKE:-}" ]; then
  echo "IMPEDIMENT ANTHROPIC_API_KEY is not set; add it to the environment and start a new session" >&2
  exit 2
fi
OUT=.tmp/batch-smoke/$(date -u +%Y%m%dT%H%M%SZ)
mkdir -p "$OUT"
cat > "$OUT/design.md" <<DESIGN
# Decided design: batch-lane smoke test

- Experiment id: EXAMPLE-batch-smoke. Card id: CARD-EXAMPLE-batch-smoke-01.
- Command 1 (id verify): \`python3 tools/runbook.py verify examples/runbooks/toy-ecdlp-bsgs/runbook-sessions/RBS-EXAMPLE-b301f5\`, timeout 120 seconds, success exit code 0.
- Pin the commit. Bind tools/runbook.py. Receipt at \`$OUT/run/receipt.json\`.
- Write scope: \`$OUT/run/\` only. Bus address: executor-mechanical-batch-smoke. Not in the background.
- Stop condition: the run command exits with status 2.
DESIGN

ask() {  # ask NAME PROMPT_FILE -> prints the answer text
  "$DELPHI" run -model "$MODEL" -effort high -every 30s -out "$OUT/$1" -prompt "$(cat "$2")" >&2
  python3 - "$OUT/$1/results.jsonl" <<'PY'
import json, sys
result = [json.loads(line) for line in open(sys.argv[1]) if line.strip()][-1]
print(result["status"], result.get("model"), result.get("usage"), file=sys.stderr)
if result["status"] != "succeeded":
    sys.exit(1)
print(result["text"])
PY
}

python3 tools/task_card.py request compile --design "$OUT/design.md" --bind tools/runbook.py \
  --out "$OUT/card.yaml" > "$OUT/compile.md"
ask compile "$OUT/compile.md" > "$OUT/compile.reply.md"
python3 tools/task_card.py ingest "$OUT/compile.reply.md" --expect card --out "$OUT/card.yaml"
python3 tools/task_card.py run "$OUT/card.yaml"
python3 tools/task_card.py request assess "$OUT/card.yaml" > "$OUT/assess.md"
ask assess "$OUT/assess.md" > "$OUT/assess.reply.md"
python3 tools/task_card.py ingest "$OUT/assess.reply.md" --expect assessment \
  --card "$OUT/card.yaml" --out "$OUT/run/assessment.yaml"
echo "SMOKE OK $OUT"
