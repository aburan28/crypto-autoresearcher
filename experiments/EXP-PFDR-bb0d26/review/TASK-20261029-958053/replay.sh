#!/usr/bin/env bash
# J1 audit replay of one EXP-PFDR-bb0d26 unit (TASK-20261029-958053, REVIEW-PFDR-bb0d26-20261029).
# usage: replay.sh <interpreter> <tag> <trial_id> <run_id> <scratch_base> [<extra PYTHONPATH>]
# Builds a fresh scratch root from tree-auth.tar (implementation/, trial-plan.json, specification.yaml,
# runbook.yaml at authority commit 48bd193a) and runs-head.tar (runs/ at snapshot 1eddb474), then runs
# the recorded command (runs/<RUN>/command.txt) with the interpreter replaced and --run-dir pointed into
# scratch. inputs_from resolves via run.py RUNS_DIR = <root>/experiments/EXP-PFDR-bb0d26/runs, i.e. the
# recorded census jobs. Nothing is written inside the repository.
set -euo pipefail
PYBIN=$1; TAG=$2; TRIAL=$3; RUN=$4; S=$5; XPP=${6:-}
U=$S/j1/$TAG/$TRIAL
rm -rf "$U"; mkdir -p "$U/root" "$U/out/$RUN"
tar -xf "$S/tree-auth.tar" -C "$U/root"
tar -xf "$S/runs-head.tar" -C "$U/root"
cd "$U/root"
export PYTHONPATH="$XPP"
"$PYBIN" -c 'import sys,platform,json,os; json.dump({"sys.version":sys.version,"sys.executable":sys.executable,"platform":platform.platform(),"PYTHONPATH":os.environ.get("PYTHONPATH",""),"cwd":os.getcwd()}, open(sys.argv[1],"w"), indent=1)' "$U/interp.json"
date -u +%Y-%m-%dT%H:%M:%SZ > "$U/started"
set +e
"$PYBIN" experiments/EXP-PFDR-bb0d26/implementation/run.py trial --run-dir "$U/out/$RUN" --run-id "$RUN" \
  --trial-id "$TRIAL" --plan experiments/EXP-PFDR-bb0d26/trial-plan.json \
  > "$U/out/$RUN/stdout.log" 2> "$U/out/$RUN/stderr.log"
echo $? > "$U/run.rc"
"$PYBIN" experiments/EXP-PFDR-bb0d26/implementation/check.py "$U/out/$RUN" experiments/EXP-PFDR-bb0d26/trial-plan.json "$TRIAL" \
  > "$U/out/$RUN/check.stdout.log" 2> "$U/out/$RUN/check.stderr.log"
echo $? > "$U/check.rc"
set -e
date -u +%Y-%m-%dT%H:%M:%SZ > "$U/finished"
echo "$TAG $TRIAL $RUN run.rc=$(cat "$U/run.rc") check.rc=$(cat "$U/check.rc")"
