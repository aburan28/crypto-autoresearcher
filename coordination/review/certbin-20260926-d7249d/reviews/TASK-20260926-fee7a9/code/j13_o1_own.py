"""J13 O1 add-on: my own literal W_4 on a few satisfiable controls, to confirm codim(W_4) = s
independently of the engine (RT-8: own W_4 on O1-O4 permitted)."""
import sys, json, gzip
sys.path.insert(0, sys.argv[1])
from rtlib19 import *
run, outp = sys.argv[2], sys.argv[3]
inst = [json.loads(l) for l in gzip.open(run + '/instances.jsonl.gz', 'rt')]
sel = sorted([r for r in inst if r['arm'] == 'S3-SAT100'], key=lambda r: r['index'])[:10] + \
      sorted([r for r in inst if r['arm'] == 'N-CONV19' and r['role'] == 'sat'], key=lambda r: r['index'])[:5]
M4 = Mono(20, 4)
fo = open(outp, 'w')
for r in sel:
    P = decode_E_hex(r['E_hex'])
    rec, E = literal_W(P, M4, 4)
    # soundness: every basis element vanishes on every listed solution
    sound = all(eval_poly(set(M4.masks_of(x)), u) == 0 for x in E.piv.values() for u in r['solutions'])
    out = {'key': r['key'], 's': r['s'], 'own_W4_final_dim': rec['final_dim'], 'codim': 6196 - rec['final_dim'],
           'codim_eq_s': 6196 - rec['final_dim'] == r['s'], 'one': rec['one'], 'basis_vanishes_on_solutions': sound,
           'iterations_to_fixpoint': rec['iterations_to_fixpoint'], 'dims': rec['dims']}
    fo.write(json.dumps(out) + '\n'); fo.flush(); print(out, flush=True)
