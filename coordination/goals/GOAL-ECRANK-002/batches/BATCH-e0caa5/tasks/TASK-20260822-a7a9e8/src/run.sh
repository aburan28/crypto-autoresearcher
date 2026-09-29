#!/usr/bin/env bash
# Run-record harness for TASK-20260822-a7a9e8.
# usage: run.sh <RUN-ID> <memory_mb> <wall_s> -- <command...>
set -u
TASKDIR="$(cd "$(dirname "$0")/.." && pwd)"
RUNID="$1"; MEMMB="$2"; WALL="$3"; shift 4
RD="$TASKDIR/runs/$RUNID"
mkdir -p "$RD"
printf '%q ' "$@" > "$RD/command.txt"; echo >> "$RD/command.txt"
python3 - "$RD" <<'PY'
import json, os, platform, subprocess, sys
rd = sys.argv[1]
import cypari
env = dict(
    python=sys.version,
    platform=platform.platform(),
    cypari_version=getattr(cypari, "__version__", "unknown"),
    pari_version=str(cypari.pari("version()")),
    numpy=__import__("numpy").__version__,
    git_commit=subprocess.run(["git","rev-parse","HEAD"],capture_output=True,text=True).stdout.strip(),
    git_dirty=bool(subprocess.run(["git","status","--porcelain"],capture_output=True,text=True).stdout.strip()),
    git_branch=subprocess.run(["git","rev-parse","--abbrev-ref","HEAD"],capture_output=True,text=True).stdout.strip(),
)
json.dump(env, open(os.path.join(rd,"environment.json"),"w"), indent=1)
PY
START=$(date -u +%FT%TZ)
T0=$(date +%s.%N)
( ulimit -v $((MEMMB*1024)); timeout "$WALL" "$@" ) \
    > "$RD/stdout.log" 2> "$RD/stderr.log"
RC=$?
T1=$(date +%s.%N)
END=$(date -u +%FT%TZ)
{
  echo "run_id: $RUNID"
  echo "task_id: TASK-20260822-a7a9e8"
  echo "started_at: $START"
  echo "ended_at: $END"
  echo "wall_clock_seconds: $(echo "$T1 - $T0" | bc)"
  echo "exit_code: $RC"
  echo "memory_cap_mb: $MEMMB"
  echo "wall_clock_cap_seconds: $WALL"
  echo "certificate:"
  echo "  kind: exhibited_points_with_height_regulator"
  echo "  verified_by: construct_highrank.verify_on_curve (exact Fractions, own code)"
} > "$RD/manifest.yaml"
echo "RUN $RUNID exit=$RC"
exit $RC
