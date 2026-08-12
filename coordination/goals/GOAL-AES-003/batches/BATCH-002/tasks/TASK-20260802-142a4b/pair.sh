#!/bin/bash
cd "$(dirname "$0")"
lbl=$1; tmo=$2; shift 2
echo "CMD $lbl ./cnt $*" >> commands.txt
s=$(date -u +%s)
out=$(timeout $tmo ./cnt "$@"); st=$?
e=$(date -u +%s)
python3 -c "
import json,sys
lbl,st,s,e,raw=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
try: d=json.loads(raw)
except Exception: d={'parse_error':raw[:300],'status':'no_result_terminated_or_failed'}
d['label']=lbl; d['exit_status']=st; d['start_epoch']=s; d['end_epoch']=e; d['wall_s']=e-s
print(json.dumps(d))" "$lbl" "$st" "$s" "$e" "$out" >> raw.jsonl
echo "$lbl exit=$st $((e-s))s"
