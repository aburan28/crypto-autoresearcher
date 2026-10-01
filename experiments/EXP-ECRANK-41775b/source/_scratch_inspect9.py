"""Scratch inspection 9: R2 dynamic double-invocation smoke (read-only).
Not a protocol artifact."""
import json, sys
from fractions import Fraction as Fr

BOUND_V1 = 'experiments/EXP-ECRANK-73275e/source'
BOUND_V2 = 'experiments/EXP-ECRANK-73275e/source-v2'
sys.path.insert(0, BOUND_V1)
sys.path.insert(0, BOUND_V2)
import ecrank_engine as E
import construct

R12 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(R12))
E.reset_ops()
E.start_counting()
by = {}
for rec in d['found']:
    by.setdefault(rec['b_index'], rec)
for bi in (649, 1299, 4995):
    rec = by[bi]
    b = [Fr(x) for x in rec['instance']['b']]
    dpat = list(rec['instance']['d_pattern'])
    k4, n4, m4 = construct.solve_n6(E, b, dpat, 10 ** 4)
    k9, n9, m9 = construct.solve_n6(E, b, dpat, 10 ** 9)
    print(bi, 'meta equal:', m4 == m9, 'kept4', len(k4), 'kept9', len(k9),
          'near4', n4, 'near9', n9)
    print('  meta:', m4)
    print('  kept r:', [x['r'] for x in k4], '->', [x['r'] for x in k9])
print('ops:', E.ops_count())
