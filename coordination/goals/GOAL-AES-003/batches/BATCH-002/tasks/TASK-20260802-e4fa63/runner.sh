#!/bin/bash
# arms in the preregistered priority order: A1, A3, A2, A4, A1b
cd "$(dirname "$0")"
run(){ name=$1; shift
  echo "$(date -u +%FT%TZ) START $name: ./probe arm $*" >> runner.log
  s=$(date +%s)
  ./probe arm $* > arm_${name}.json 2> arm_${name}.err
  rc=$?
  e=$(date +%s)
  echo "$(date -u +%FT%TZ) DONE $name exit=$rc seconds=$((e-s))" >> runner.log
}
run A1  A1  5  1  1 33 424242001 5 4
run A3  A3 10  1  1 33 424242003 10 4
run A2  A2  6  1  1 32 424242006 6 4
run A4  A4  5 15  1 32 424242004 45 4
run A1b A1b 5  1  1 32 777000333 15 4
echo "$(date -u +%FT%TZ) ALL_DONE" >> runner.log
