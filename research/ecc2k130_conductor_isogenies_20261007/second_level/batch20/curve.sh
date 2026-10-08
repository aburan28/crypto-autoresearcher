#!/bin/bash
# One level-2 curve, resumable: 82153-descent from a 45641-floor curve, then the 11-cycle and torsion level checks.
# Run i uses start representative ((i-1) mod 6)+1 of iso163_45641.txt and seed 100+i. A step is skipped when its
# output already ends with a `real` timing line, so a container restart costs only the step in progress.
set -u; i=$1; cd "$(dirname "$0")"
done_() { grep -q '^real' "$1" 2>/dev/null; }
b0=$(sed -n "$(( (i-1) % 6 + 1 ))p" /home/user/koblitz_cond/iso163_45641.txt | tr -d '[' | cut -d, -f1)
if ! done_ d$i.out; then
  printf '\\\\ run %d: 82153-descent from 45641-floor curve %s, seed setrand(%d)\nsetrand(%d);\nMOD = x^163+x^7+x^6+x^3+1; m = 163; A2 = 1; BINT = %s; lp = 82153; k = 63; twist = 1; NISO = 1; OUT = "d%d.txt";\nread("vert_down.gp");\n' $i $b0 $((100+i)) $((100+i)) $b0 $i > d$i.gp
  : > d$i.txt; (time gp -q -s 4G d$i.gp </dev/null) > d$i.out 2>&1
fi
b=$(tr -d '[' < d$i.txt | cut -d, -f1)
if ! done_ c$i.out; then
  printf 'MOD = x^163+x^7+x^6+x^3+1; IN = "d%d.txt"; S = 11; CAP = 200000;\nread("cyc_gen.gp");\n' $i > c$i.gp
  (time gp -q -s 2G c$i.gp </dev/null) > c$i.out 2>&1
fi
if ! done_ t$i.out; then
  printf 'MOD = x^163+x^7+x^6+x^3+1; m = 163;\n{CURVES = [["level-2 b=%s", 1, %s]];}\nPRIMES = [[45641, 20, 1], [82153, 63, 1]]; NGOOD = 4;\nread("lvl_check.gp");\n' $b $b > t$i.gp
  (time gp -q -s 4G t$i.gp </dev/null) > t$i.out 2>&1
fi
