"""Scratch inspection 11: pre-verify R12 class-key union, armB streams, n2r maxima, R14.
Not a protocol artifact."""
import json
import collections

R12 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(R12))
keys = set()
for rec in d['found']:
    keys.update(rec['certificate']['class_keys'])
print('R12 class-key union:', sorted(keys, key=lambda x: int(x)))
print('R12 coset_V:', d['coset_V'])
ct = d['n2r']['reconciliation']['cross_tabulation']
print('n rows:', len(ct))
print('max h_A:', max(r['h_A'] for r in ct), 'max h_B:', max(r['h_B'] for r in ct))
print('h_A list:', sorted(r['h_A'] for r in ct))
print('h_B list:', sorted(r['h_B'] for r in ct))
print('membership levels A:', collections.Counter(r['membership_level_A'] for r in ct))
print('membership levels B:', collections.Counter(r['membership_level_B'] for r in ct))
print('N A:', d['n2r']['reconciliation']['N_per_H_convention_A'])
print('N B:', d['n2r']['reconciliation']['N_per_H_convention_B'])
print('out_of_box_B:', d['n2r']['reconciliation']['out_of_box_B_observations'])
agg = collections.Counter(rec['certificate']['aggregate_total'] for rec in d['found'])
print('aggregate totals hist:', dict(agg))
verdicts = collections.Counter(rec['certificate']['verdict'] for rec in d['found'])
print('verdicts:', dict(verdicts))

B = 'experiments/EXP-ECRANK-76a70d/runs/RUN-ECRANK-76a70d-R3-armB/raw-result.json'
b = json.load(open(B))
print('\narmB keys:', sorted(b.keys()))
print('streams b_done:', [s['b_done'] for s in b['streams']], 'sum:', sum(s['b_done'] for s in b['streams']))
print('streams b_total:', [s['b_total'] for s in b['streams']])
print('streams solves_ok:', [s.get('solves_ok') for s in b['streams']])
print('streams square_ok:', [s.get('square_ok') for s in b['streams']])
print('params:', json.dumps(b['parameters'], indent=1))
print('found_instances:', len(b['found_instances']), 'cumulative:', b['cumulative_counts_per_H'])
print('level_counts:', b['level_counts_per_H'])
print('ops:', b['ops_counted_total'], 'exhaustion:', b['exhaustion'], 'events:', b['events'])

R14 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R14-construct-n8-rescoped/raw-result.json'
r14 = json.load(open(R14))
print('\nR14 found:', len(r14['found']), 'near_miss_total:', r14['near_miss_total'],
      'ledger len:', len(r14['near_miss_ledger']), 'exhaustion:', r14['exhaustion'])
print('R14 keys:', sorted(r14.keys()))
print('R14 counts_per_H:', r14.get('counts_per_H'), 'feasible:', r14.get('feasible_tuples'))
