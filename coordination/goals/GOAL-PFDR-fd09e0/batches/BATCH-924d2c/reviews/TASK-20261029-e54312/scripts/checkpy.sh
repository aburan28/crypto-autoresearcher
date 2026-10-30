#!/usr/bin/env bash
# J2a(4): re-run the bound checker check.py on each of the five recorded run directories, read-only, under
# the named interpreter. check.py writes nothing into a run directory; its census branch compiles the kernel
# into tempfile.mkdtemp under $TMPDIR (a scratch path). The tree digest of experiments/EXP-PFDR-bb0d26 is taken
# before and after to show that nothing changed.
# usage: checkpy.sh <interpreter> <tag>      (run from the repository root)
set -u
PY="$1"; TAG="$2"
OUT="coordination/goals/GOAL-PFDR-fd09e0/batches/BATCH-924d2c/reviews/TASK-20261029-e54312/outputs/checkpy-$TAG"
export TMPDIR=/tmp/claude-0/j2-scratch/tmp
mkdir -p "$OUT"
tree_digest() { find experiments/EXP-PFDR-bb0d26 -type f -print0 | sort -z | xargs -0 sha256sum | sha256sum | cut -d' ' -f1; }
BEFORE=$(tree_digest)
"$PY" -B -I -c 'import json,sys; print(json.dumps({"version": sys.version, "executable": sys.executable}))' > "$OUT/interpreter.json"
: > "$OUT/results.jsonl"
for spec in "RUN-PFDR-e44a19 selftest" "RUN-PFDR-4d8c71 census-toy-main" "RUN-PFDR-243425 analyze-main" \
            "RUN-PFDR-cd03e2 census-toy-rep" "RUN-PFDR-089edc analyze-final"; do
  set -- $spec
  RID="$1"; TR="$2"
  T0=$(date +%s.%N)
  "$PY" -B -I experiments/EXP-PFDR-bb0d26/implementation/check.py experiments/EXP-PFDR-bb0d26/runs/$RID \
      experiments/EXP-PFDR-bb0d26/trial-plan.json "$TR" > "$OUT/$RID.stdout.log" 2> "$OUT/$RID.stderr.log"
  RC=$?
  T1=$(date +%s.%N)
  SAME=$(cmp -s "$OUT/$RID.stdout.log" "experiments/EXP-PFDR-bb0d26/runs/$RID/check.stdout.log" && echo true || echo false)
  echo "{\"run_id\": \"$RID\", \"trial\": \"$TR\", \"exit_code\": $RC, \"stdout_identical_to_recorded_check_stdout_log\": $SAME, \"wall_seconds\": $(printf "%.3f" "$(echo "$T1 - $T0" | bc)")}" >> "$OUT/results.jsonl"
  echo "$RID $TR rc=$RC same_stdout=$SAME"
done
AFTER=$(tree_digest)
echo "{\"experiment_tree_digest_before\": \"$BEFORE\", \"experiment_tree_digest_after\": \"$AFTER\", \"unchanged\": $([ "$BEFORE" = "$AFTER" ] && echo true || echo false)}" > "$OUT/tree.json"
cat "$OUT/tree.json"
