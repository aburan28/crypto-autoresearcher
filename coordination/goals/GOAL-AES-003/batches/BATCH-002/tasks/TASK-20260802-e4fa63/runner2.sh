#!/bin/bash
cd "$(dirname "$0")"
run(){ name=$1; shift
  echo "$(date -u +%FT%TZ) START $name: ./probe arm $*" >> runner.log
  s=$(date +%s); ./probe arm $* > arm_${name}.json 2> arm_${name}.err; rc=$?; e=$(date +%s)
  echo "$(date -u +%FT%TZ) DONE $name exit=$rc seconds=$((e-s))" >> runner.log
}
run A3b A3b 10 1 1 33 515151007 20 4
run A2b A2b  6 1 1 33 616161008 26 4
echo "$(date -u +%FT%TZ) EXTRA_DONE" >> runner.log
