"""Scratch inspection 12: R3 op-count breakdown (read-only). Not a protocol artifact."""
import json, sys
from fractions import Fraction as Fr

BOUND_V1 = 'experiments/EXP-ECRANK-73275e/source'
BOUND_V2 = 'experiments/EXP-ECRANK-73275e/source-v2'
sys.path.insert(0, BOUND_V1)
sys.path.insert(0, BOUND_V2)
import ecrank_engine as E
import certify76 as C
import certify_ladder as CL
import random

R12 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(R12))

E.reset_ops()
E.start_counting()
print('after reset+start:', E.ops_count())
ec, digest = E.load_exact_certify('.')
print('after load_exact_certify:', E.ops_count())
cosets = E.eligible_cosets()
print('after eligible_cosets:', E.ops_count())
rng_c = random.Random(760906)
coset = cosets[rng_c.randrange(len(cosets))]
print('after coset pick:', E.ops_count())

rows = []
for rec in d['found']:
    inst = rec['instance']
    xs = [Fr(x) for x in inst['b']]
    dpat = list(inst['d_pattern'])
    t = Fr(inst['r'][0])
    g = [t, Fr(1)]
    r = [E.peval(g, x) for x in xs]
    built, why = E.build_instance(xs, dpat, r, 6)
    rows.append((rec.get('b_index'), built is not None))
print('after 33 peval+build:', E.ops_count())

# per-certify cost on the first 3
costs = []
for i, rec in enumerate(d['found'][:3]):
    inst = rec['instance']
    xs = [Fr(x) for x in inst['b']]
    dpat = list(inst['d_pattern'])
    t = Fr(inst['r'][0])
    r = [t + x for x in xs]
    before = E.ops_count()
    cert = C.certify_instance(E.build_instance(xs, dpat, r, 6)[0], coset, ec)
    costs.append(E.ops_count() - before)
print('per-certify costs (first 3):', costs)
print('projected total for 33 certs:', E.ops_count() + sum(costs) * 33 // 3)
