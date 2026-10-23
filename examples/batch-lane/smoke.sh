#!/usr/bin/env bash
# Live smoke test of the task-card batch lane (docs/model-tiers.md, "Batch lane"):
# `tools/task_card.py lane` end to end on a toy card -- director compile through a
# real Message Batch, `run` with no model, director assess through a second batch,
# each reply checked by `ingest`. Spends two Sonnet 5.5 batch requests.
#
# Backend (VIA, default auto):
#   conductor  Conductor-hosted Delphi; the key is in the control plane's vault.
#              Needs `conductor` connected (`conductor delphi profiles` lists director).
#   delphi     standalone delphi; needs ANTHROPIC_API_KEY (or Anthropic WIF) and
#              `go install github.com/aburan28/conductor/cmd/delphi@main`.
# TASK=T-42 links both delegations to a Conductor task.
# Usage: [VIA=conductor|delphi] [TASK=T-42] examples/batch-lane/smoke.sh
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"
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
exec python3 tools/task_card.py lane --via "${VIA:-auto}" ${TASK:+--task "$TASK"} \
  --design "$OUT/design.md" --bind tools/runbook.py \
  --card "$OUT/card.yaml" --assessment "$OUT/run/assessment.yaml"
