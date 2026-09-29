"""Scratch inspection 4 (executor, EXP-ECRANK-41775b). Not a protocol artifact."""
import json

p = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R12-construct-n6-replication/raw-result.json'
d = json.load(open(p))
print('R12 near_miss_ledger:', d['near_miss_ledger'], 'total:', d['near_miss_total'])
p13 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R13-construct-n6-replay/raw-result.json'
d13 = json.load(open(p13))
print('R13 near_miss_total:', d13['near_miss_total'], 'ledger:', d13['near_miss_ledger'])
p3 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R3-construct-n6/raw-result.json'
d3 = json.load(open(p3))
print('R3 near_miss_total:', d3['near_miss_total'], 'ledger:', d3['near_miss_ledger'])
p4 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R4-construct-n6-replay/raw-result.json'
d4 = json.load(open(p4))
print('R4 near_miss_total:', d4['near_miss_total'], 'ledger:', d4['near_miss_ledger'])
p5 = 'experiments/EXP-ECRANK-73275e/runs/RUN-ECRANK-73275e-R5-construct-n8/raw-result.json'
d5 = json.load(open(p5))
print('R5 near_miss_total:', d5['near_miss_total'], 'ledger_len:', len(d5['near_miss_ledger']))
print('R5 found:', len(d5['found']), 'n_b_done:', d5.get('n_b_done'))
