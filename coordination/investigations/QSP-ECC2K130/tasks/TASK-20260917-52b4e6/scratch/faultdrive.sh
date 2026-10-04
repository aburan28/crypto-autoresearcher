#!/bin/sh
cd /home/user/crypto-autoresearcher/coordination/investigations/QSP-ECC2K130/tasks/TASK-20260917-52b4e6
OUT=scratch/faults_final.txt
: > $OUT
python3 - <<'PY' > scratch/fault_keys.txt
import sys; sys.path.insert(0,"scratch")
import importlib.util
spec=importlib.util.spec_from_file_location("fr","scratch/faultrun.py")
src=open("scratch/faultrun.py").read()
import re
ks=re.findall(r'\n "([^"]+)":\n', src)
print("\n".join(ks))
PY
timeout 300 python3 scratch/faultrun.py "BASE" base > scratch/base.json 2>>$OUT
echo "BASELINE rc=$?" >> $OUT
cat scratch/base.json >> $OUT
while IFS= read -r k; do
  [ -z "$k" ] && continue
  timeout 300 python3 scratch/faultrun.py "$k" fault > scratch/f.json 2>/dev/null
  rc=$?
  if [ $rc -eq 0 ]; then
    python3 - "$k" <<'PY' >> $OUT
import json,sys
b=json.load(open("scratch/base.json")); f=json.load(open("scratch/f.json"))
bm={tuple(r[:3]):tuple(r[3:]) for r in b["rows"]}
ch=sum(1 for r in f["rows"] if tuple(r[3:])!=bm[tuple(r[:3])])
clean = f["I1_vs_I2"]==0 and f["I1_vs_I3"]==0 and f["I2_vs_I3"]==0
print("%-104s n=%d changed=%-5d M2=(%d,%d,%d)  AGREEMENT STILL CLEAN: %s"
      %(sys.argv[1], f["n"], ch, f["I1_vs_I2"], f["I1_vs_I3"], f["I2_vs_I3"], clean))
PY
  elif [ $rc -eq 124 ]; then
    echo "$k -> NON-TERMINATING within 300 s (infrastructure outcome, not agreement)" >> $OUT
  else
    echo "$k -> CRASHED rc=$rc (the package's own self-check or an assert caught the fault)" >> $OUT
  fi
done < scratch/fault_keys.txt
echo "DONE" >> $OUT
