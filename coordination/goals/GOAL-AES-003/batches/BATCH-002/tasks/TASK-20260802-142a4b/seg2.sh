#!/bin/bash
cd "$(dirname "$0")"
STOP=1785698617
M0=00030101010203010101020303010102
M1=00030101010203000101000303000102
AESMC=02030101010203010101020303010102
K=6fe52e2e9b3ea04085c370f9bc609245
B=e35f00e7631cdd862e59d126e72b8fc9
run(){
  lbl=$1; shift
  now=$(date -u +%s); left=$((STOP-now-90))
  if [ $left -le 60 ]; then echo "SKIP $lbl (budget: ${left}s left)"; return; fi
  echo "SEG2 CMD $lbl ./cnt $*" >> commands.txt
  s=$now
  out=$(timeout $left ./cnt "$@"); st=$?
  e=$(date -u +%s)
  python3 -c "
import json,sys
lbl,st,s,e,raw=sys.argv[1],int(sys.argv[2]),int(sys.argv[3]),int(sys.argv[4]),sys.argv[5]
try: d=json.loads(raw)
except Exception: d={'parse_error':raw[:300],'status':'no_result_terminated_or_failed'}
d['label']=lbl; d['exit_status']=st; d['start_epoch']=s; d['end_epoch']=e; d['wall_s']=e-s
d['segment']=2; d['machine_conditions']='uncontended: 4 cores, no other producers (coordinator-confirmed load 0.29 at segment start)'
print(json.dumps(d))" "$lbl" "$st" "$s" "$e" "$out" >> raw.jsonl
  echo "$lbl exit=$st ${$((e-s))}s" 2>/dev/null || echo "$lbl exit=$st $((e-s))s"
  python3 -c "
import time,json,sys
now=int(time.time())
print(json.dumps({'stamp':'C2_SECTION','segment':2,'section':'arm_'+sys.argv[1],'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(now)),'epoch':now,'elapsed_s':now-1785695617,'remaining_s':1785698617-now,'marker':'arm '+sys.argv[1]+' terminal, exit '+sys.argv[2]}))" "$lbl" "$st" >> budget_stamps.jsonl
}
run M0_r5_j0         soft 5 0 $K $B $M0 8 0 4
run M0_r4_j0_CRIT    soft 4 0 $K $B $M0 16 1 4
run M0_r4_j1_NONCRIT soft 4 1 $K $B $M0 8 0 4
run CTRL_AESMC_r4_j0 soft 4 0 $K $B $AESMC 8 0 4
run CTRL_AESMC_r5_j0 soft 5 0 $K $B $AESMC 8 0 4
run M0_r5_j1         soft 5 1 $K $B $M0 8 0 4
run M1_r5_j0         soft 5 0 $K $B $M1 16 1 4
run N1 aesni 10 0 d6e8b0bc6cb2749dc3e4b1d5359ddf85 502ddf7c0f432fb9a866f39e33cd0965 $AESMC 8 0 4
run N2 aesni 10 1 3da27ad55721c729448c02daea5805f7 5e6835660e37ee3d9c07a2c25ebb7e99 $AESMC 8 0 4
run N3 aesni 10 0 2bb4f19dd101c9c7adc75fdb1f0655d6 a652ceedbcc31dc3d281dd8b5befb4ef $AESMC 8 0 4
run N4 aesni 10 3 22f5d83f80dedd23a4b89bd1e67d9403 b7b114c0d0a169e4dc33befca84bb4cf $AESMC 8 0 4
run N5 aesni 10 2 4c6714249e4fcecc5f95749784142c7e 9c9ec7cd076bdcd6ca1c8646364820aa $AESMC 8 0 4
echo SEG2_ALL_DONE
