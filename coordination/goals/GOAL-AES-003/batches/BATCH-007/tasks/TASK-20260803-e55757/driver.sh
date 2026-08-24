#!/bin/bash
# TASK-20260803-e55757 driver. Runs the 27 RC-8 arms in fixed order B01..B27,
# 2^30 trials, 2 threads, sequentially. Never STARTS an arm that cannot finish
# before the binding stop minus RESERVE. Skipped arms are NAMED in runs/dropped.txt.
cd "$(dirname "$0")"
STOP=1785787137          # computed binding stop = start 1785781737 + 5400
RESERVE=330              # analysis + RESULTS.json + json.load check
EST=200                  # measured ~171 s/arm at 2 threads; padded

for i in $(seq -w 1 27); do
  s=202608037$i
  name="B$i-RAND-$s"
  now=$(date +%s)
  if [ $(( now + EST + RESERVE )) -ge $STOP ]; then
    echo "$name DROPPED_ON_BUDGET est=${EST}s now=$now stop=$STOP cmd=./rc8probe_native arm $name rand:$s 5 1 1 30 631001 1 2" >> runs/dropped.txt
    continue
  fi
  S=$(date +%s.%N)
  ./rc8probe_native arm "$name" "rand:$s" 5 1 1 30 631001 1 2 > runs/$name.json 2> runs/$name.err
  E=$?
  T=$(python3 -c "print(f'{$(date +%s.%N)-$S:.2f}')")
  echo "$name exit=$E wall=$T cmd=./rc8probe_native arm $name rand:$s 5 1 1 30 631001 1 2" >> runs/arms_timing.txt
  echo "./rc8probe_native arm $name rand:$s 5 1 1 30 631001 1 2" >> runs/commands.txt
done
echo "DRIVER_EXIT $(date -u +%Y-%m-%dT%H:%M:%SZ) epoch=$(date +%s) stop=$STOP" >> runs/arms_timing.txt
