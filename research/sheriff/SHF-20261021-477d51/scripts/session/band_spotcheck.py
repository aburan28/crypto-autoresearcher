"""Session spot-check: plan/rho-neg and double-base/plan at w = 0, 0.1, 1 from the producer's band json.
Reads crypto band-*.json (data only); run: python3 -I band_spotcheck.py /home/user/crypto/research/ic_planner_validation_20261020/analysis"""
import json, sys
from pathlib import Path
root = Path(sys.argv[1])
for s in ['c24', 'c28', 'c30', 'r24', 'r26', 'r28']:
    m = {r['arm']: r['mean_s'] for r in json.loads((root / f'band-{s}.json').read_text())['rows']}
    print(s, 'plan/rho', [round(m['plan'][i] / m['rho-neg'][i], 2) for i in range(3)],
          'double/plan', [round(m['double-base'][i] / m['plan'][i], 3) for i in range(3)],
          'S(plan) w1', round(m['plan'][2], 1), 'S(double) w1', round(m['double-base'][2], 1))
