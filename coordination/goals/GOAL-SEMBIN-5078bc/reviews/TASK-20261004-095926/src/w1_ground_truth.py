#!/usr/bin/env python3
"""W1(2): ground truth WITHOUT any closure.  B/I = F_2^V, so I = {f : f|_V = 0} and LM(I_{<=4}) is exact linear algebra on the evaluation matrix.
For every random system (families quad/sparsequad/cubic/bilinear/toeplitz/planted, N in NMIN..NMAX, quadratic and cubic generators) compare
  verdict_closure  = N_std(LM(W)) vs |V|                      (the rule on the card)
  G1               = LM(W) == LM(I_{<=4})                     (the 'leading monomials equal that set' formulation)
  G3               = N_std(LM(I_{<=4})) == |V|                (best achievable at D=4: the ideal-level sufficiency)
and the structural facts  LM(W) subset LM(I_{<=4}),  rank <= c - eval_rank.
usage: w1_ground_truth.py NMIN NMAX NSEEDS OUT.json [families...]"""
import sys, os, json, random, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
HERE = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(HERE, 'closure')
TMP = os.environ.get('TMPDIR', '/tmp')

def write_masks(path, N, polys):
    with open(path, 'w') as f:
        f.write('%d %d\n' % (N, len(polys)))
        for p in polys:
            ms = sorted(p); f.write('%d %s\n' % (len(ms), ' '.join(map(str, ms))))

def main():
    nmin, nmax, nseeds, out = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    fams = sys.argv[5:] or ['quad', 'sparsequad', 'cubic', 'bilinear', 'toeplitz', 'planted']
    table = {}; records = []; bad = []
    for fam in fams:
        for N in range(nmin, nmax + 1):
            for seed in range(nseeds):
                rng = random.Random((hash(fam) & 0xffff) * 977 + N * 13 + seed)
                M = max(2, N + rng.choice([-4, -3, -2, -1, 0, 0, 1])) if fam != 'planted' else max(2, N - rng.choice([2, 3, 4, 5]))
                gens = system(fam, N, M, seed)
                if not gens: continue
                path = os.path.join(TMP, 'w1gt.masks'); write_masks(path, N, gens)
                o = subprocess.run([EXE, path, '-o', os.path.join(TMP, 'w1gt'), '-q', '-t', '1'], capture_output=True, text=True)
                j = json.loads(o.stdout.strip().splitlines()[-1])
                lmW = set(int(x) for x in open(os.path.join(TMP, 'w1gt.lm')).read().split())
                pts = points_of_system(N, gens); nV = len(pts)
                lmI, stdI = eval_kernel_lm(N, 4, pts)
                c = len(lmI) + len(stdI)
                ns_W = j['N_std']; ns_I = count_std(N, lmI)
                v = verdict(ns_W, nV)
                G1 = (lmW == lmI); G3 = (ns_I == nV)
                sub = lmW <= lmI; rk = j['rank'] <= c - len(stdI)
                if not (sub and rk): bad.append(dict(family=fam, N=N, M=M, seed=seed))
                key = (v, 'LM(W)==LM(I<=4)' if G1 else 'LM(W)!=LM(I<=4)', 'ideal-level suff' if G3 else 'ideal-level insuff')
                table[key] = table.get(key, 0) + 1
                records.append(dict(family=fam, N=N, M=M, seed=seed, V=nV, rank=j['rank'], c=c, eval_rank=len(stdI), N_std_W=ns_W, N_std_I=ns_I, verdict=v, G1=G1, G3=G3))
    print('systems', len(records), 'violations of LM(W) subset LM(I<=4) or rank bound:', len(bad), bad[:3])
    for k, n in sorted(table.items(), key=lambda kv: str(kv[0])): print(' ', k, n)
    # the two formulations of sufficiency
    both_diff = [r for r in records if (r['verdict'] == 'sufficient') != r['G1']]
    print('systems where (N_std==|V|) and (LM(W)==LM(I<=4)) give different answers:', len(both_diff))
    for r in both_diff[:5]: print('  ', r)
    json.dump(dict(table={str(k): v for k, v in table.items()}, records=records, violations=bad), open(out, 'w'))

main()
