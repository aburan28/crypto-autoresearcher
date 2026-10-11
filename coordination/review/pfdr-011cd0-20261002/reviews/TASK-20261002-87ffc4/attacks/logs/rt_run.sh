#!/bin/bash
# Usage: rt_run.sh <logfile> <cmd...> ; runs under nice 19 with 1 thread, polls RSS, kills child above 3.0e9 bytes.
LOG="$1"; shift
export PYTHONDONTWRITEBYTECODE=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1
export PYTHONPATH=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e/src
export RT_WT=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/wt-pfdr011cd0-5753edf2e
cd /home/user/crypto-autoresearcher/coordination/review/pfdr-011cd0-20261002/reviews/TASK-20261002-87ffc4
nice -n 19 "$@" > "$LOG" 2>&1 &
PID=$!
PEAK=0
while kill -0 $PID 2>/dev/null; do
  RSS=$(awk '/VmRSS/{print $2*1024}' /proc/$PID/status 2>/dev/null)
  if [ -n "$RSS" ]; then
    [ "$RSS" -gt "$PEAK" ] && PEAK=$RSS
    if [ "$RSS" -gt 3000000000 ]; then echo "RT-7 STOP: RSS $RSS > 3.0e9, killing $PID" >> "$LOG"; kill $PID; fi
  fi
  sleep 2
done
wait $PID; RC=$?
echo "EXIT $RC PEAK_RSS_BYTES $PEAK" >> "$LOG"
