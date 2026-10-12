#!/bin/bash
# Nearby-object controls AT WINDOW SCALE (not a task deliverable on the twelve): drop k generators from an N=40 window instance, enumerate V
# (count_solutions mode A with dump), run closure_v with the pointwise row check, then the independent post-check (evaluation-kernel truth, Apriori N_std).
# usage: bash src/scale_controls.sh SOURCE.masks TAG k1 k2 ...      (run from out/)
cd "$(dirname "$0")/.."
src=$1; tag=$2; shift 2
mkdir -p results/scale
export OMP_NUM_THREADS=2
for k in "$@"; do
  python3 - "$src" "results/scale/${tag}_drop${k}.masks" $k <<'PY'
import sys
src,dst,k=sys.argv[1],sys.argv[2],int(sys.argv[3])
L=open(src).read().split('\n'); N,M=map(int,L[0].split()); polys=L[1:1+M]
polys=polys[k:]
open(dst,'w').write('%d %d\n'%(N,len(polys))+'\n'.join(polys)+'\n')
PY
  m=results/scale/${tag}_drop${k}.masks
  N=$(head -1 $m | cut -d' ' -f1); h=$((N/2))
  src/count_solutions A $m 0 $h results/scale/${tag}_drop${k}.sol 200000 > results/scale/${tag}_drop${k}.V.txt
  python3 src/masks_to_ms.py $m results/scale/${tag}_drop${k}.ms
  src/closure_v $m -o results/scale/${tag}_drop${k} -t 2 -q -V results/scale/${tag}_drop${k}.sol > results/scale/${tag}_drop${k}.closure.json
  python3 src/postcheck.py results/scale/${tag}_drop${k}.ms results/scale/${tag}_drop${k}.lm results/scale/${tag}_drop${k}.sol > results/scale/${tag}_drop${k}.postcheck.json
  echo "drop $k: $(head -c 300 results/scale/${tag}_drop${k}.V.txt | head -1 | grep -o 'total=[0-9]*') | $(python3 -c "
import json
j=json.load(open('results/scale/${tag}_drop${k}.closure.json')); p=json.load(open('results/scale/${tag}_drop${k}.postcheck.json'))
print('rank',j['rank'],'of',j['columns'],'N_std',j['N_std'],'violations',j['row_eval_violations'],'| eval-truth: LM(W)<=LM(I)',p['LM_W_subset_LM_I'],'W==I<=4',p['LM_W_equals_LM_I'],'| apriori Nstd',p['N_std_apriori'],p['verdict_apriori'])")"
done
