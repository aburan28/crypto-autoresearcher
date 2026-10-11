#!/bin/bash
# four independent 82153-descents from four different 45641-floor curves, then both level checks on each image
cd "$(dirname "$0")"
for i in 1 2 3 4; do (time gp -q -s 4G down163_s$i.gp </dev/null) > down163_s$i.out 2>&1 & done; wait
for i in 1 2 3 4; do
  b=$(tr -d '[' < down163_s$i.txt | cut -d, -f1)
  printf 'MOD = x^163+x^7+x^6+x^3+1; IN = "down163_s%d.txt"; S = 11; CAP = 200000;\nread("cyc_gen.gp");\n' $i > cyc163_s$i.gp
  printf 'MOD = x^163+x^7+x^6+x^3+1; m = 163;\n{CURVES = [["level-2 b=%s", 1, %s]];}\nPRIMES = [[45641, 20, 1], [82153, 63, 1]]; NGOOD = 4;\nread("lvl_check.gp");\n' $b $b > lvl163_s$i.gp
done
for i in 1 2 3 4; do (time gp -q -s 2G cyc163_s$i.gp </dev/null) > cyc163_s$i.out 2>&1 & done; wait
for i in 1 2 3 4; do (time gp -q -s 4G lvl163_s$i.gp </dev/null) > lvl163_s$i.out 2>&1 & done; wait
echo ALLDONE > run_four.done
