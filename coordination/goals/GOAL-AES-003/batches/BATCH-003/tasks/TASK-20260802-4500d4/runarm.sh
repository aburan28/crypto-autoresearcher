#!/bin/bash
# runarm.sh <tag> <r> <j0> <key> <base> <matrix> <winbits> <threads>
set -u
D=/home/user/crypto-autoresearcher/coordination/goals/GOAL-AES-003/batches/BATCH-003/tasks/TASK-20260802-4500d4
tag=$1; shift
cmd="$D/collide $*"
st=$(date -u +%s)
out=$($cmd 2>>"$D/stderr.log"); rc=$?
en=$(date -u +%s)
python3 - "$tag" "$cmd" "$rc" "$st" "$en" "$out" <<'PY' >> "$D/raw_runs.jsonl"
import json,sys
tag,cmd,rc,st,en,out=sys.argv[1:7]
rec={"tag":tag,"command":cmd,"exit_status":int(rc),"start_epoch":int(st),"end_epoch":int(en),"wall_seconds":int(en)-int(st)}
try: rec["result"]=json.loads(out)
except Exception as e: rec["result"]=None; rec["parse_error"]=str(e); rec["raw_stdout"]=out[:2000]
print(json.dumps(rec))
PY
echo "$tag rc=$rc wall=$((en-st))"
