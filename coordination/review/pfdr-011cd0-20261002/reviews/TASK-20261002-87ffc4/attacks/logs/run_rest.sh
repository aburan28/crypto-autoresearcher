#!/bin/bash
# Sequential runner (one computation process at a time, RT-7) for the remaining attacks.
S=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/rt-87ffc4
PY=/tmp/claude-0/-home-user/015c3767-cc03-52db-9b0c-bd2aa6c26537/scratchpad/venv-ci/bin/python
R=/home/user/crypto-autoresearcher/coordination/review/pfdr-011cd0-20261002/reviews/TASK-20261002-87ffc4
cd $R
mkdir -p attacks/ptm/out attacks/j8/out attacks/j6/out
TS=$($PY -c "import json;print(json.load(open('attacks/j4/out/tstar.json'))['variants']['per_family']['t_star'])")
echo "own t* = $TS" > $S/run_rest.log
$S/rt_run.sh $S/j4_aint.log $PY attacks/j4/j4_aint.py --out attacks/j4/out/aint.json --tstar-own $TS
echo "aint done $(date -u +%T)" >> $S/run_rest.log
$S/rt_run.sh $S/j4_pcr_iii.log $PY attacks/j4/j4_pcr_iii.py --out attacks/j4/out/pcr_iii.json
echo "pcr_iii done $(date -u +%T)" >> $S/run_rest.log
$S/rt_run.sh $S/j4_pcnull_power.log $PY attacks/j4/j4_pcnull_power.py --npz $S/null-z.npz --out attacks/j4/out/pcnull_power.json
echo "pcnull_power done $(date -u +%T)" >> $S/run_rest.log
$S/rt_run.sh $S/ptm.log $PY attacks/ptm/ptm.py --out attacks/ptm/out/ptm.json --tstar-own $TS --npz $S/null-z.npz
echo "ptm done $(date -u +%T)" >> $S/run_rest.log
$S/rt_run.sh $S/j8.log $PY attacks/j8/j8_heur.py --out attacks/j8/out/heur.json
echo "j8 done $(date -u +%T)" >> $S/run_rest.log
$S/rt_run.sh $S/j6sz.log $PY attacks/j6/replication_sizing.py --out attacks/j6/out/replication-sizing.json
$S/rt_run.sh $S/j6.log $PY attacks/j6/j6_table.py --out attacks/j6/out/cell-statements.json
echo "j6 done $(date -u +%T)" >> $S/run_rest.log
$S/rt_run.sh $S/j2rest.log $PY attacks/j2/j2_e2_and_scale.py --out attacks/j2/out/toy_enum2_rest.json
echo "ALL DONE $(date -u +%T)" >> $S/run_rest.log
