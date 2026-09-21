#!/bin/bash
# TASK-20260802-142a4b run driver. Order fixed by PREREGISTRATION.md section 5.
cd "$(dirname "$0")"
AESMC=02030101010203010101020303010102
M0=00030101010203010101020303010102
M1=00030101010203000101000303000102
K=6fe52e2e9b3ea04085c370f9bc609245
B=e35f00e7631cdd862e59d126e72b8fc9
run(){ # label engine r j0 key base matrix cw wbits
  lbl=$1; shift
  echo "CMD $lbl ./cnt $*" >> commands.txt
  s=$(date -u +%s)
  out=$(./cnt "$@" 4)
  st=$?
  e=$(date -u +%s)
  python3 -c "
import json,sys
lbl=sys.argv[1]; st=int(sys.argv[2]); s=int(sys.argv[3]); e=int(sys.argv[4]); raw=sys.argv[5]
try: d=json.loads(raw)
except Exception: d={'parse_error':raw[:400]}
d['label']=lbl; d['exit_status']=st; d['start_epoch']=s; d['end_epoch']=e; d['wall_s']=e-s
print(json.dumps(d))
" "$lbl" "$st" "$s" "$e" "$out" >> raw.jsonl
  echo "$lbl done exit=$st $((e-s))s"
}
# ORDER v2 (after the counting-kernel change; see RESULTS.json deviation D-2)
AESMC=02030101010203010101020303010102
run N1 aesni 10 0 d6e8b0bc6cb2749dc3e4b1d5359ddf85 502ddf7c0f432fb9a866f39e33cd0965 $AESMC 8 0
run N2 aesni 10 1 3da27ad55721c729448c02daea5805f7 5e6835660e37ee3d9c07a2c25ebb7e99 $AESMC 8 0
run N3 aesni 10 0 2bb4f19dd101c9c7adc75fdb1f0655d6 a652ceedbcc31dc3d281dd8b5befb4ef $AESMC 8 0
run CTRL_AESMC_r4_j0 soft 4 0 $K $B $AESMC 8 0
run M0_r4_j0_CRIT    soft 4 0 $K $B $M0 16 1
run M0_r4_j1_NONCRIT soft 4 1 $K $B $M0 8 0
run M0_r5_j0 soft 5 0 $K $B $M0 8 0
run CTRL_AESMC_r5_j0 soft 5 0 $K $B $AESMC 8 0
run M0_r5_j1 soft 5 1 $K $B $M0 8 0
run M1_r5_j0 soft 5 0 $K $B $M1 16 1
run M1_r4_j0 soft 4 0 $K $B $M1 16 1
run N4 aesni 10 3 22f5d83f80dedd23a4b89bd1e67d9403 b7b114c0d0a169e4dc33befca84bb4cf $AESMC 8 0
run N5 aesni 10 2 4c6714249e4fcecc5f95749784142c7e 9c9ec7cd076bdcd6ca1c8646364820aa $AESMC 8 0
echo ALL_DONE
