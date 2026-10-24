#!/bin/bash
cd /home/user/crypto-autoresearcher
export PYTHONDONTWRITEBYTECODE=1
SCR=/tmp/claude-0/-home-user/f3553d8c-d92f-57ed-aee6-36992723a751/scratchpad
for pair in t1-inventory:RUN-CMFB-2373be t2-gate-instrument:RUN-CMFB-5905c0 t3-gate-sensitivity:RUN-CMFB-66b0fe t4-measure-c16-c20:RUN-CMFB-3dc120 t5-measure-c24-fam:RUN-CMFB-42a578 t6-measure-c24-na:RUN-CMFB-e13f0e t7-measure-c24-nb:RUN-CMFB-c71d35 t8-analysis:RUN-CMFB-2010d3; do
  t=${pair%%:*}; r=${pair##*:}
  s=$(date +%s)
  python3 experiments/EXP-CMFB-cea1d2/implementation/driver.py --trial $t --run-dir $SCR/rerun/$r > $SCR/rerun/$r.stdout 2> $SCR/rerun/$r.stderr
  rc=$?
  e=$(date +%s)
  echo "$t $r rc=$rc secs=$((e-s))" >> $SCR/rerun/progress.log
  if [ $rc -ne 0 ]; then echo "STOP on failure" >> $SCR/rerun/progress.log; exit $rc; fi
done
echo DONE >> $SCR/rerun/progress.log
