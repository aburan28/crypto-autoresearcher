#!/usr/bin/env python3
# EXP-GPS-001 RUN-d — GPS-1 scoring: burst window structure, per-class region
# splits, whole-class pivot-rate bounds, P1/P2 verdict computation.
# Pure python on RUN-b/RUN-c products + state.json unit log.
import json, pickle
from pathlib import Path
from array import array

ROOT = Path('/Volumes/Volume/crypto-autoresearcher')
W = ROOT / 'experiments/EXP-GPS-001/work'
with open(W / 'shell_order.pkl', 'rb') as f:
    sh = pickle.load(f)
shell, cid, SHELL0 = sh['shell'], sh['cid'], sh['shell_start']
class_ids = {v: k for k, v in sh['class_ids'].items()}
bpc = json.load(open(W / 'burst_pivot_cols.json'))['pivot_cols']
units = json.load(open(W / 'pivots_rows_all.json'))['state_units']

N = len(shell)
def region(j):
    a = SHELL0 + j
    if a < 364000: return 'live'
    if a < 449000: return 'plateau'
    if a < 454000: return 'burst'
    return 'tail'

# per-class region split + u-degree stats
splits = {}
for j in range(N):
    c = class_ids[cid[j]]
    s = splits.setdefault(c, {'live': 0, 'plateau': 0, 'burst': 0, 'tail': 0})
    s[region(j)] += 1
# known pivots per class (burst profile, from RUN-c)
known = {}
for jc in bpc:
    c = class_ids[cid[jc - SHELL0]]
    known[c] = known.get(c, 0) + 1

# burst window contiguity + window composition
w0, w1 = min(bpc), max(bpc)
contiguous = (len(bpc) == w1 - w0 + 1)
win_classes = {}
for a in range(w0, w1 + 1):
    c = class_ids[cid[a - SHELL0]]
    win_classes[c] = win_classes.get(c, 0) + 1
win_udeg = {int(k.split(',')[0][1:]) for k in win_classes}
piv_udeg = {int(k.split(',')[0][1:]) for k in known}
# classes present in the burst unit but with ZERO pivots
unit_classes = {}
for a in range(449000, 454000):
    c = class_ids[cid[a - SHELL0]]
    unit_classes[c] = unit_classes.get(c, 0) + 1
zero_pivot_in_unit = {k: v for k, v in unit_classes.items() if k not in known}

# whole-class pivot-rate bounds
table = []
plateau_total = 0
plateau_in_proven_low = 0   # upper bound rate < 2%
plateau_in_possible_low = 0 # lower bound rate < 2% <= upper
for c, s in splits.items():
    Nc = sum(s.values())
    kp = known.get(c, 0)
    lo = kp / Nc
    hi = (kp + s['live']) / Nc   # every live-region column a pivot (extreme)
    table.append({'class': c, 'N': Nc, 'live': s['live'], 'plateau': s['plateau'],
                  'burst': s['burst'], 'tail': s['tail'], 'known_pivots': kp,
                  'rate_lo': round(lo, 5), 'rate_hi': round(hi, 5)})
    plateau_total += s['plateau']
    if hi < 0.02:
        plateau_in_proven_low += s['plateau']
    if lo < 0.02:
        plateau_in_possible_low += s['plateau']
table.sort(key=lambda r: -r['plateau'])

# plateau composition totals
plateau_by_class = {r['class']: r['plateau'] for r in table if r['plateau'] > 0}
res = {
    'run': 'RUN-EXP-GPS-001-d',
    'shell_start': SHELL0, 'n_shell': N, 'n_classes': len(splits),
    'burst_window': {'min': w0, 'max': w1, 'n_pivots': len(bpc),
                     'contiguous_all_pivot': contiguous,
                     'window_classes': win_classes,
                     'window_u_degrees': sorted(win_udeg),
                     'pivot_u_degrees': sorted(piv_udeg),
                     'unit_classes_zero_pivot': zero_pivot_in_unit},
    'class_region_table': table,
    'plateau_total_cols': plateau_total,
    'plateau_classes': plateau_by_class,
    'P2_bounds': {
        'plateau_cols_in_classes_rateHI_lt_2pct': plateau_in_proven_low,
        'plateau_cols_in_classes_rateLO_lt_2pct': plateau_in_possible_low,
        'share_proven': round(plateau_in_proven_low / plateau_total, 4),
        'share_possible': round(plateau_in_possible_low / plateau_total, 4),
    },
}
json.dump(res, open(W / 'gps1_scores.json', 'w'), indent=1)
out = ROOT / 'experiments/EXP-GPS-001/runs/RUN-EXP-GPS-001-d/raw.json'
out.parent.mkdir(parents=True, exist_ok=True)
json.dump(res, open(out, 'w'), indent=1)
print(json.dumps(res['burst_window'], indent=1)[:900])
print('plateau_total', plateau_total, 'P2 bounds', res['P2_bounds'])
print('top plateau classes:', dict(list(plateau_by_class.items())[:8]))
