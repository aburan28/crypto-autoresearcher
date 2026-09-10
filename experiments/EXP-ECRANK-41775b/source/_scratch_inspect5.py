"""Scratch inspection 5: can R3 build+certify the R12 found set (read-only try)?
Not a protocol artifact. Uses bound modules read-only."""
import json, sys
from fractions import Fraction as Fr

BOUND_V1 = 'experiments/EXP-ECRANK-73275e/source'
BOUND_V2 = 'experiments/EXP-ECRANK-73275e/source-v2'
sys.path.insert(0, BOUND_V1)
sys.path.insert(0, BOUND_V2)
import ecrank_engine as E
import certify76 as C
import construct
import certify_ladder as CL

R12 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(R12))
E.reset_ops()
E.start_counting()
ec, digest = E.load_exact_certify('.')
cosets = E.eligible_cosets()
# R12 coset_V [0,1,14,15,38,39,40,41]
coset = next(c for c in cosets if sorted(c['V']) == sorted([0, 1, 14, 15, 38, 39, 40, 41]))
print('coset found, m0', coset.get('m0'))
n_rebuilt = 0
n_cert_pass = 0
mismatches = []
for rec in d['found']:
    inst = rec['instance']
    xs = [Fr(x) for x in inst['b']]
    dpat = list(inst['d_pattern'])
    t = Fr(inst['r'][0])
    g = [t, Fr(1)]
    r = [E.peval(g, x) for x in xs]
    built, why = E.build_instance(xs, dpat, r, 6)
    if built is None:
        mismatches.append((rec.get('b_index'), why))
        continue
    n_rebuilt += 1
    cert = CL.certify_instance_ladder(built, coset, ec, max_prime=1500)
    if cert.get('verdict') == 'PASS' and cert.get('aggregate_total') == rec['certificate']['aggregate_total']:
        n_cert_pass += 1
    else:
        mismatches.append((rec.get('b_index'), 'cert', cert.get('verdict'),
                           cert.get('aggregate_total'), rec['certificate']['aggregate_total']))
print('rebuilt:', n_rebuilt, 'cert match:', n_cert_pass, 'mismatches:', mismatches[:10])
print('ops:', E.ops_count())
