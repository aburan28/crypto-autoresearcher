"""J13 O4 N-PERT19 generation, exactly as the plan fixes it (see j13-ptm/o4-reading-table.yaml
interpretations). Writes the generation log (every attempt) and the kept systems."""
import sys, json, gzip, hashlib
sys.path.insert(0, sys.argv[1])
import numpy as np
from itertools import combinations
from exhaust import solve
from rtlib19 import decode_E_hex, quad_kernel, ftr, fmul, finv
run, outdir = sys.argv[2], sys.argv[3]
SEED = 2026092670901
print('numpy', np.__version__)
inst = {}
for l in gzip.open(run + '/instances.jsonl.gz', 'rt'):
    r = json.loads(l); inst[r['key']] = r
pairs = list(combinations(range(20), 2))          # E_layout columns 21..210 in order
col_of_pair = {p: 21 + i for i, p in enumerate(pairs)}
nonbil = [p for p in pairs if (p[0] < 10 and p[1] < 10) or (p[0] >= 10 and p[1] >= 10)]
assert len(nonbil) == 90
bases = [inst['S3-U400:%d' % i] for i in range(20)]
g = np.random.Generator(np.random.PCG64(SEED))
log = open(outdir + '/o4-generation-log.jsonl', 'w')
kept = open(outdir + '/o4-kept-systems.jsonl', 'w')
summary = {'seed': SEED, 'numpy': np.__version__, 'families': {}}
def esha(E_hex):
    return hashlib.sha256(json.dumps(E_hex, separators=(',', ':')).encode()).hexdigest()
for fam in ('P-BIL', 'P-QUAD'):
    fs = {'kept': 0, 'rejected_sat': 0, 'exhausted': []}
    for i, b in enumerate(bases):
        rows = [int(h, 16) for h in b['E_hex']]
        xR = b['x_R']
        inv2 = finv(fmul(xR, xR))
        ctr = [ftr(fmul(1 << k, inv2)) for k in range(19)]
        done = False
        for a in range(64):
            k = int(g.integers(0, 19))
            if fam == 'P-BIL':
                c = int(g.integers(0, 100))
                pair = (c // 10, 10 + c % 10)
            else:
                c = int(g.integers(0, 90))
                pair = nonbil[c]
            col = col_of_pair[pair]
            new = list(rows)
            new[k] ^= 1 << col
            s, sols = solve(new)
            E_hex = [format(x, 'x') for x in new]
            rec = {'family': fam, 'slot': i, 'base': b['key'], 'attempt': a, 'k': k, 'c': c, 'pair': list(pair), 'col': col,
                   'base_coeff_before': (rows[k] >> col) & 1, 'c_k_trace': ctr[k], 's': s, 'E_sha256': esha(E_hex)}
            if s == 0:
                rec['outcome'] = 'kept'
                log.write(json.dumps(rec) + '\n')
                P = decode_E_hex(E_hex)
                K = quad_kernel(P)
                ker = [list(v) for v in K]
                krec = dict(rec)
                krec.update({'key': f'N-PERT19:{fam}:{i}', 'E_hex': E_hex, 'x_R': xR, 'kernel_dim': len(K),
                             'trace_vector_in_kernel': (ctr in [list(v) for v in K]) if K else False,
                             'ell_survives_by_rule': ctr[k] == 0})
                kept.write(json.dumps(krec) + '\n')
                fs['kept'] += 1
                done = True
                break
            else:
                rec['outcome'] = 'rejected_sat'
                log.write(json.dumps(rec) + '\n')
                fs['rejected_sat'] += 1
        if not done:
            fs['exhausted'].append(i)
    summary['families'][fam] = fs
json.dump(summary, open(outdir + '/o4-generation-summary.json', 'w'), indent=1)
print(json.dumps(summary))
