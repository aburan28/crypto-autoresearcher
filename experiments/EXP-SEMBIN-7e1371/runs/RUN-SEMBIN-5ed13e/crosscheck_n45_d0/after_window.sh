#!/bin/bash
# Waits for the window scheduler to exit, then cross-checks n=45 draw 0.
S=/tmp/claude-0/-home-user/e1ee877e-40c0-526f-8ca6-a6aa5f9bf38e/scratchpad/xcheck45d0
R=/home/user/crypto-autoresearcher/experiments/EXP-SEMBIN-7e1371/runs/RUN-SEMBIN-5ed13e
I=$R/closure_m2_n45/cells/instances/ch_n45_m2_t2_k23_low_B_ran_s20260913101_d0.json
while ps -eo args | awk '$1 ~ /python3$/ && $2=="-u" && $3 ~ /window_sched\.py$/ {f=1} END {exit !f}'; do sleep 60; done
grep -q "window schedule done" $R/schedulers/window_sched.log || { echo "[after_window $(date -u +%FT%TZ)] scheduler exited WITHOUT finishing; not starting"; exit 1; }
cd $S && echo "[after_window $(date -u +%FT%TZ)] scheduler gone; starting xcheck method 0 cap 11.5" && python3 -u xcheck.py 0 11.5 $I 2 > xcheck_default_cap11.5.log 2>&1; echo "[after_window $(date -u +%FT%TZ)] xcheck exit $?"
