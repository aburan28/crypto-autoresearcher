#!/usr/bin/env python3
"""W1(1) at larger N: closure.c (waves, RREF tails, compaction, product tables) vs closure2.c (literal passes, plain head reduction, hash lookup)
vs closure2 -i, and (N <= 19) the Python reference.  Compares the LM file bytes (hence rank, LM set, hash) and N_std.
usage: diff_c_vs_c2.py NMIN NMAX NSEEDS [families...]"""
import sys, os, json, random, subprocess, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from ref_closure import *
from gen_systems import system
HERE = os.path.dirname(os.path.abspath(__file__)); TMP = os.environ.get('TMPDIR', '/tmp')
CORP = os.path.join(HERE, '..', 'corpus', 'medium'); os.makedirs(CORP, exist_ok=True)

def write_masks(path, N, polys):
    with open(path, 'w') as f:
        f.write('%d %d\n' % (N, len(polys)))
        for p in polys:
            ms = sorted(p); f.write('%d %s\n' % (len(ms), ' '.join(map(str, ms))))

def run(cmd):
    o = subprocess.run(cmd, capture_output=True, text=True)
    if o.returncode: raise RuntimeError(o.stderr[:500])
    return json.loads(o.stdout.strip().splitlines()[-1])

def main():
    nmin, nmax, nseeds = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    fams = sys.argv[4:] or ['toeplitz', 'bilinear', 'quad', 'cubic']
    tests = fails = 0
    for fam in fams:
        for N in range(nmin, nmax + 1):
            for seed in range(nseeds):
                rng = random.Random((hash(fam) & 0xffff) * 31 + N * 7 + seed)
                M = max(2, N + rng.choice([-3, -2, -1, 0, 0, 1]))
                gens = system(fam, N, M, seed)
                if not gens: continue
                tag = '%s_N%d_M%d_s%d' % (fam, N, M, seed)
                path = os.path.join(CORP, tag + '.masks'); write_masks(path, N, gens)
                pre = os.path.join(TMP, 'dd_' + tag)
                j1 = run([os.path.join(HERE, 'closure'), path, '-o', pre + '_a', '-q', '-t', '1'])
                j1e = run([os.path.join(HERE, 'closure'), path, '-o', pre + '_ae', '-q', '-t', '1', '-E'])
                j2 = run([os.path.join(HERE, 'closure2'), path, '-o', pre + '_b'])
                j2i = run([os.path.join(HERE, 'closure2'), path, '-o', pre + '_bi', '-i'])
                files = [open(pre + s + '.lm', 'rb').read() for s in ['_a', '_ae', '_b', '_bi']]
                hs = [hashlib.sha256(x).hexdigest() for x in files]
                same = len(set(hs)) == 1 and len({j1['rank'], j1e['rank'], j2['rank'], j2i['rank']}) == 1 and len({j1['N_std'], j1e['N_std'], j2['N_std'], j2i['N_std']}) == 1
                if N <= 19:
                    R = Closure(gens, N, 4).run(); lm = R.lm_set()
                    same = same and (open(pre + '_a.lm').read().split() == [str(m) for m in lm]) and R.saturated()
                tests += 1
                if not same:
                    fails += 1; print('MISMATCH', tag, hs, j1['rank'], j1e['rank'], j2['rank'], j2i['rank'])
                for s in ['_a', '_ae', '_b', '_bi']: os.remove(pre + s + '.lm')
    print('tests', tests, 'fails', fails)
    sys.exit(1 if fails else 0)
main()
