#!/bin/bash
# Kill/resume matrix for joint W7 (5). Output: $SP/work/out/resume.jsonl and resume.log. Run after 02_build_libs.sh and make_mutants.py.
. $(dirname $0)/00_env.sh
cd $SP/work
R="python3 $WS/scripts/w7_resume.py out/resume.jsonl"
T=chained_n9_m3_t3_k4_d0
for k in 1 2 3 4 5 6 7 8 9 10; do $R $T orig 0.0265228 $k; done
$R $T orig 0.0265228 3 0.0530455; $R $T orig 0.0265228 3 0.0198921; $R $T orig 0.0198921 4 0.0795683
$R $T orig 0.0265228 2,3; $R $T orig 0.0265228 3,4; $R $T orig 0.0265228 1,1,1; $R $T orig 0.0265228 2,5,3 0.0397842
T=chained_n20_m2_t2_k10_d3
for k in 1 5 20 40 50; do $R $T orig 0.0134077 $k; done
$R $T orig 0.0134077 5 0.0536308; $R $T orig 0.0134077 20 0.0536308; $R $T orig 0.0134077 5,10 0.0178769
T=null_n18_m2_t2_k9_d0
$R $T orig 0.00763047 1; $R $T orig 0.00763047 2; $R $T orig 0.00763047 1 0.0381523
T=chained_n10_m3_t3_k4_d0
$R $T orig 0.0289783 2; $R $T orig 0.0289783 3; $R $T orig 0.0289783 5; $R $T orig 0.0289783 3 0.115913
T=chained_n18_m2_t2_k11_d0
for k in 3 8 12; do $R $T orig 0.0289783 $k; done
# the harness against resume mutants
for v in ME MI; do for k in 2 3 5; do $R chained_n9_m3_t3_k4_d0 $v 0.0265228 $k; done; $R chained_n20_m2_t2_k10_d3 $v 0.0134077 5; $R chained_n20_m2_t2_k10_d3 $v 0.0134077 20; done
echo RESUME_DONE
