#!/bin/sh
# INVOCATION 1 (TASK-20260923-2d8db0): J1 certificate re-verification, J2 arithmetic, J3 lightweight checks.
# Run from this scratch directory as:
#   flock /tmp/claude-0/-home-user/1d07255b-9852-59b9-9a33-de55220a4332/scratchpad/gfpn-solver.lock \
#     prlimit --as=$((8*1024**3)) sh run_inv1.sh
set -e
cd "$(dirname "$0")"
date -u +"start %Y-%m-%dT%H:%M:%SZ"
python3 inv1_certs.py
/opt/conda-sage/envs/sage/bin/sage inv1_sage.sage
date -u +"end %Y-%m-%dT%H:%M:%SZ"
