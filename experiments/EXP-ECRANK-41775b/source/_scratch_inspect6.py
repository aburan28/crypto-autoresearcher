"""Scratch inspection 6: certify with v1 certify76 directly (read-only try).
Not a protocol artifact."""
import json, sys
from fractions import Fraction as Fr

BOUND_V1 = 'experiments/EXP-ECRANK-73275e/source'
BOUND_V2 = 'experiments/EXP-ECRANK-73275e/source-v2'
sys.path.insert(0, BOUND_V1)
sys.path.insert(0, BOUND_V2)
import ecrank_engine as E
import certify76 as C

R12 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(R12))
E.reset_ops()
E.start_counting()
ec, digest = E.load_exact_certify('.')
cosets = E.eligible_cosets()
coset = next(c for c in cosets if sorted(c['V']) == sorted([0, 1, 14, 15, 38, 39, 40, 41]))
n_ok = 0
bad = []
for rec in d['found']:
    inst = rec['instance']
    xs = [Fr(x) for x in inst['b']]
    dpat = list(inst['d_pattern'])
    t = Fr(inst['r'][0])
    g = [t, Fr(1)]
    r = [E.peval(g, x) for x in xs]
    built, why = E.build_instance(xs, dpat, r, 6)
    if built is None:
        bad.append((rec.get('b_index'), 'build', why))
        continue
    cert = C.certify_instance(built, coset, ec)
    if cert.get('verdict') == 'PASS' and cert.get('aggregate_total') == rec['certificate']['aggregate_total']:
        n_ok += 1
    else:
        bad.append((rec.get('b_index'), cert.get('verdict'), cert.get('aggregate_total'),
                    rec['certificate']['aggregate_total'], cert.get('errors_strict')))
print('cert match:', n_ok, '/', len(d['found']))
print('bad (first 3):', bad[:3])
print('ops:', E.ops_count())
