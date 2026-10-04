#!/bin/bash
set -e
cd "$(dirname "$0")"
KEY=6fe52e2e9b3ea04085c370f9bc609245
BASE=e35f00e7631cdd862e59d126e72b8fc9
AESMC=02030101010203010101020303010102
RK=$(./anchor keysched $KEY)
STAMP(){ python3 -c "
import time,json,sys
now=int(time.time())
print(json.dumps({'stamp':'C2_SECTION','section':sys.argv[1],'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(now)),'epoch':now}))
" "$1" >> budget_stamps.jsonl; }
run(){
  lbl=$1; shift
  STAMP "arm_${lbl}_start"
  s=$(date +%s)
  out=$("$@"); st=$?
  e=$(date +%s)
  python3 -c "
import json,sys
lbl,st,s,e,raw=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
try: d=json.loads(raw)
except Exception: d={'parse_error':raw[:300],'status':'no_result_terminated_or_failed'}
d['label']=lbl; d['exit_status']=st; d['start_epoch']=s; d['end_epoch']=e; d['wall_s_measured']=e-s
print(json.dumps(d))" "$lbl" "$st" "$s" "$e" "$out" >> raw.jsonl
  STAMP "arm_${lbl}_end"
  echo "$lbl exit=$st $((e-s))s"
}
run CASE_Z_count5   ./count5 4 0 $RK $BASE id coset
run CASE_NZ_count5  ./count5 5 0 $RK $BASE id coset
run CASE_Z_cnt_soft  ./cnt soft 4 0 $KEY $BASE $AESMC 8 0 4
run CASE_NZ_cnt_soft ./cnt soft 5 0 $KEY $BASE $AESMC 16 0 4
echo ALL_ARMS_DONE
