"""Scratch inspection 2 (executor, EXP-ECRANK-41775b). Not a protocol artifact."""
import json

p = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(p))
print('n:', d.get('n'), 'seed:', d.get('seed'), 'n_b:', d.get('n_b_declared'), d.get('n_b_done'))
print('n2r:', json.dumps(d.get('n2r'), indent=1)[:3000])
print('ops:', d.get('ops'))
print('feasible_tuples:', d['feasible_tuples'])
# multiplicity per b_index among found
import collections
c = collections.Counter(rec['b_index'] for rec in d['found'])
print('found per-b_index counts:', dict(c))
print('max multiplicity:', max(c.values()))

p13 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R13-construct-n6-replay/raw-result.json'
d13 = json.load(open(p13))
print('R13 near_miss_total:', d13['near_miss_total'], 'ledger:', len(d13['near_miss_ledger']), 'found:', len(d13['found']))

p3 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R3-construct-n6/raw-result.json'
d3 = json.load(open(p3))
print('R3(v1) keys:', sorted(d3.keys()))
print('R3(v1) near_miss_total:', d3.get('near_miss_total'), 'ledger:', len(d3.get('near_miss_ledger', [])), 'found:', len(d3.get('found', [])))
if d3.get('near_miss_ledger'):
    print(json.dumps(d3['near_miss_ledger'][0], indent=1)[:600])
