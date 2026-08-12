#!/bin/bash
cd "$(dirname "$0")"
STOP=1785703621
M1=00030101010203000101000303000102
K=6fe52e2e9b3ea04085c370f9bc609245
B=e35f00e7631cdd862e59d126e72b8fc9
run(){
  lbl=$1; shift
  now=$(date -u +%s); left=$((STOP-now-60))
  if [ $left -le 60 ]; then echo "SKIP $lbl (budget ${left}s)"; return; fi
  echo "SEG3 CMD $lbl ./cnt $*" >> commands.txt
  s=$now
  out=$(timeout $left ./cnt "$@"); st=$?
  e=$(date -u +%s)
  python3 mkrow3.py "$lbl" "$st" "$s" "$e" "$out"
  echo "$lbl exit=$st $((e-s))s"
  python3 -c "
import time,json,sys
now=int(time.time())
print(json.dumps({'stamp':'C2_SECTION','segment':3,'section':'arm_'+sys.argv[1],'utc':time.strftime('%Y-%m-%dT%H:%M:%SZ',time.gmtime(now)),'epoch':now,'elapsed_s':now-1785701821,'remaining_s':1785703621-now,'marker':'arm '+sys.argv[1]+' terminal, exit '+sys.argv[2]}))" "$lbl" "$st" >> budget_stamps.jsonl
}
run M1_r5_j0 soft 5 0 $K $B $M1 16 1 4
run M1_r5_j1 soft 5 1 $K $B $M1 16 1 4
echo SEG3_DONE
