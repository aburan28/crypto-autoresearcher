"""Scratch inspection only (executor, EXP-ECRANK-41775b). Not a protocol artifact."""
import json, collections

p = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(p))
print('keys:', sorted(d.keys()))
print('found:', len(d['found']))
print('near_miss_total:', d['near_miss_total'])
print('ledger len:', len(d['near_miss_ledger']))
reasons = collections.Counter()
missing = 0
n_entries = 0
for e in d['near_miss_ledger']:
    for f in e.get('failing', []):
        n_entries += 1
        r = f['reason']
        key = '_'.join(r.split('_')[:2])
        reasons[key] += 1
        if 't' not in f:
            missing += 1
print('failing sub-entries:', n_entries)
print('reason prefixes:', reasons)
print('failing without t:', missing)
print(json.dumps(d['near_miss_ledger'][0], indent=1)[:900])
# R14
p14 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R14-construct-n8-rescoped/raw-result.json'
d14 = json.load(open(p14))
print('R14 keys:', sorted(d14.keys()))
print('R14 found:', len(d14['found']), 'near_miss_total:', d14['near_miss_total'])
