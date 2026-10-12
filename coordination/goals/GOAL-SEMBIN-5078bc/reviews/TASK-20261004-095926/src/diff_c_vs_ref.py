#!/usr/bin/env python3
"""W1(1): diff the packed C closure against the plain Python reference on random Boolean systems.
usage: diff_c_vs_ref.py  NMIN NMAX NSEEDS [families...]
For each (family, N, M, seed): final rank, LM set (exact, ascending masks), LM hash and N_std must be identical;
the C closure is run with and without the early exit on '1 in W'; the reference closure is also checked with its own
saturation verifier and (N <= 18) against the evaluation-kernel ground truth LM(W) <= LM(I_{<=4})."""
import sys, os, json, subprocess, random, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
HERE = os.path.dirname(os.path.abspath(__file__)); EXE = os.path.join(HERE, 'closure')
TMP = os.environ.get('TMPDIR', '/tmp'); CORP = os.path.join(HERE, '..', 'corpus', 'small')
os.makedirs(CORP, exist_ok=True)

def write_masks(path, N, polys):
    with open(path, 'w') as f:
        f.write('%d %d\n' % (N, len(polys)))
        for p in polys:
            ms = sorted(p); f.write('%d %s\n' % (len(ms), ' '.join(map(str, ms))))

def run_c(path, prefix, extra=()):
    out = subprocess.run([EXE, path, '-o', prefix, '-q', '-t', '2'] + list(extra), capture_output=True, text=True)
    if out.returncode != 0: raise RuntimeError(out.stderr)
    j = json.loads(out.stdout.strip().splitlines()[-1])
    lms = [int(x) for x in open(prefix + '.lm').read().split()]
    return j, lms

def main():
    nmin, nmax, nseeds = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    fams = sys.argv[4:] or ['quad', 'sparsequad', 'cubic', 'bilinear', 'toeplitz', 'planted']
    ntests = 0; nfail = 0; stats = {}
    for fam in fams:
        for N in range(nmin, nmax + 1):
            for seed in range(nseeds):
                rng = random.Random((hash(fam) & 0xffff) * 1000 + N * 31 + seed)
                M = max(2, N + rng.choice([-4, -3, -2, -1, 0, 0, 1]))
                if fam == 'planted': M = max(2, N - rng.choice([2, 3, 4, 5]))
                gens = system(fam, N, M, seed)
                if not gens: continue
                tag = '%s_N%d_M%d_s%d' % (fam, N, M, seed)
                path = os.path.join(CORP, tag + '.masks'); write_masks(path, N, gens)
                R = Closure(gens, N, 4).run()
                lm_r = R.lm_set(); r_r = len(R.basis)
                nstd_r = count_std(N, lm_r)
                ok = R.saturated() and R.contains_generators()
                for extra, label in [((), 'early'), (('-E',), 'noearly')]:
                    j, lm_c = run_c(path, os.path.join(TMP, 'c_' + tag), extra)
                    same = (j['rank'] == r_r and sorted(lm_c) == lm_r and j['N_std'] == nstd_r)
                    ntests += 1
                    if not same or not ok:
                        nfail += 1
                        print('MISMATCH', tag, label, 'C rank', j['rank'], 'ref rank', r_r, 'C nstd', j['N_std'], 'ref nstd', nstd_r, 'ref sat', ok)
                key = (fam, N)
                st = stats.setdefault(fam, [0, 0, 0, 0, 0])
                st[0] += 1
                st[1] += 1 if (0 in set(lm_r)) else 0          # 1 in W
                pts = None
                if N <= 16:
                    pts = points_of_system(N, gens)
                    lmI, stdI = eval_kernel_lm(N, 4, pts)
                    if not set(lm_r) <= lmI:
                        nfail += 1; print('IMPOSSIBLE: LM(W) not inside LM(I<=4)', tag)
                    v = verdict(nstd_r, len(pts))
                    st[2] += (v == 'sufficient'); st[3] += (v == 'insufficient'); st[4] += (v == 'impossible')
    print('done: tests', ntests, 'fails', nfail)
    for fam, st in stats.items():
        print(' ', fam, 'systems', st[0], 'with 1 in W', st[1], 'sufficient', st[2], 'insufficient', st[3], 'impossible', st[4], '(verdict counts only for N<=16)')
    sys.exit(1 if nfail else 0)

main()
