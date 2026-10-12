#!/usr/bin/env python3
"""W1(1) at N = 23, 24: closure.c vs closure2.c -i (and literal passes closure2 at N=23), quadratic and cubic families; compares LM bytes and N_std."""
import sys, os, json, random, subprocess, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_systems import system
HERE = os.path.dirname(os.path.abspath(__file__)); TMP = os.environ.get('TMPDIR', '/tmp'); CORP = os.path.join(HERE, '..', 'corpus', 'medium')
def write_masks(path, N, polys):
    with open(path, 'w') as f:
        f.write('%d %d\n' % (N, len(polys)))
        for p in polys:
            ms = sorted(p); f.write('%d %s\n' % (len(ms), ' '.join(map(str, ms))))
def run(cmd):
    o = subprocess.run(cmd, capture_output=True, text=True)
    if o.returncode: raise RuntimeError(o.stderr[:300])
    return json.loads(o.stdout.strip().splitlines()[-1])
tests = fails = 0
for fam, N, M, seed in [('quad', 23, 22, 0), ('quad', 24, 23, 1), ('cubic', 23, 22, 0), ('cubic', 24, 24, 1), ('toeplitz', 24, 24, 2), ('bilinear', 24, 23, 3), ('sparsequad', 24, 22, 4), ('planted', 24, 20, 5)]:
    gens = system(fam, N, M, seed); tag = '%s_N%d_M%d_s%d' % (fam, N, M, seed)
    path = os.path.join(CORP, tag + '.masks'); write_masks(path, N, gens); pre = os.path.join(TMP, 'dd2_' + tag)
    j1 = run([os.path.join(HERE, 'closure'), path, '-o', pre + '_a', '-q', '-t', '1', '-E'])
    j2 = run([os.path.join(HERE, 'closure2'), path, '-o', pre + '_bi', '-i'])
    h1 = hashlib.sha256(open(pre + '_a.lm', 'rb').read()).hexdigest(); h2 = hashlib.sha256(open(pre + '_bi.lm', 'rb').read()).hexdigest()
    same = (h1 == h2 and j1['rank'] == j2['rank'] and j1['N_std'] == j2['N_std']); tests += 1
    print(tag, 'rank', j1['rank'], 'of', j1['columns'], 'N_std', j1['N_std'], 'same' if same else 'MISMATCH', flush=True)
    if not same: fails += 1
print('tests', tests, 'fails', fails)
