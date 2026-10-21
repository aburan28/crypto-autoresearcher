#!/bin/sh
# m4-sat-cost-pilot campaign: one solver process at a time, global deadline 1792257340
R=/home/user/crypto-autoresearcher/analysis/ecdlp2m-iteration-20261009/m4-sat-cost-pilot/run_cells.py
I=/tmp/claude-0/-home-user/f42055f8-3588-569d-b7d9-926d696d2468/scratchpad/m4sat/instances
run() { # cell config unsat sat timeout
  while [ ! -f $I/$1.json ]; do [ $(date +%s) -gt 1792257340 ] && exit 0; sleep 10; done
  echo "=== $1 $2 U=$3 S=$4 to=$5 $(date +%T)"
  python3 $R $1 $2 --unsat $3 --sat $4 --timeout $5 --deadline 1792257340
}
run m3-n13-k4 xg 10 3 600;      run m3-n13-k4 xg_b 10 3 600
run m3-n17-k5 xg 10 3 600;      run m3-n17-k5 xg_b 10 3 600
run m4-n13-k3 xg 10 3 600;      run m4-n13-k3 xg_symfull 10 3 600
run m4-n17-k3 xg 10 3 600;      run m4-n17-k3 xg_symfull 10 3 600
run m3-n19-k6 xg_b 10 3 600;    run m3-n19-k6 xg 10 3 600
run m4-n15-k4 xg 10 3 600;      run m4-n15-k4 xg_symfull 10 3 600
run m4-n17-k4 xg 10 3 600;      run m4-n17-k4 xg_symfull 10 3 600
run m4-n19-k5 xg_symfull 3 1 600; run m4-n19-k5 xg 3 1 600
run m3-n23-k5 xg_b 10 3 600;    run m3-n23-k5 xg 10 3 600
run m3-n23-k7 xg_b 5 2 600;     run m3-n23-k6 xg_b 8 2 600
run m4-n23-k4 xg 6 2 600;       run m4-n23-k4 xg_symfull 6 2 600
run m4-n17-k5 xg_symfull 3 1 600; run m4-n17-k5 xg 3 1 600
run m3-n23-k6 xg 5 2 600;       run m3-n23-k7 xg 2 1 600
run m4-n23-k5 xg_symfull 2 1 600; run m4-n23-k5 xg 2 1 600
echo CAMPAIGN DONE $(date +%T)
