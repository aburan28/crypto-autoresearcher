#!/bin/bash
# Waits for driver.sh to exit, then applies the PREREGISTERED guard (finish before
# stop minus 300 s reserve) to B27, which driver.sh's padded EST=200/RESERVE=330
# guard may have dropped. Records the decision and the clock reading either way.
cd "$(dirname "$0")"
STOP=1785787137
PREREG_RESERVE=300
ACTUAL_EST=170          # measured mean arm wall this session, padded up from ~166.5
while pgrep -f "driver.sh" >/dev/null; do sleep 5; done
now=$(date +%s)
name="B27-RAND-20260803727"
if [ -s runs/$name.json ]; then
  echo "B27 already completed by driver; no manual run. now=$now" >> runs/b27_decision.txt
  exit 0
fi
if [ $(( now + ACTUAL_EST + PREREG_RESERVE )) -lt $STOP ]; then
  echo "B27 DROPPED by driver padded guard but PERMITTED by the preregistered guard (finish before stop-300s). now=$now stop=$STOP est=$ACTUAL_EST reserve=$PREREG_RESERVE. Running it." >> runs/b27_decision.txt
  S=$(date +%s.%N)
  ./rc8probe_native arm "$name" rand:20260803727 5 1 1 30 631001 1 2 > runs/$name.json 2> runs/$name.err
  E=$?
  T=$(python3 -c "print(f'{$(date +%s.%N)-$S:.2f}')")
  echo "$name exit=$E wall=$T cmd=./rc8probe_native arm $name rand:20260803727 5 1 1 30 631001 1 2 [MANUAL, preregistered guard]" >> runs/arms_timing.txt
  echo "./rc8probe_native arm $name rand:20260803727 5 1 1 30 631001 1 2" >> runs/commands.txt
  echo "B27 manual run finished exit=$E wall=$T at $(date +%s)" >> runs/b27_decision.txt
else
  echo "B27 NOT RUN: the preregistered guard also refuses it. now=$now stop=$STOP" >> runs/b27_decision.txt
fi
