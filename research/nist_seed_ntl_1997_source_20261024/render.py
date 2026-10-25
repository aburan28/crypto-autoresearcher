#!/usr/bin/env sage -python
"""Plot source-derived call lower bounds, not measured running times."""
import hashlib
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

here = Path(__file__).resolve().parent
raw = (here / 'analysis.json').read_bytes()
data = json.loads(raw)
verification = json.loads((here / 'verification.json').read_text())
assert verification['status'] == 'passed'
assert verification['analysis_sha256'] == hashlib.sha256(raw).hexdigest()
rows = [r for r in data['rows'] if r['argument'] == 'p']
assert all(next(x for x in data['rows'] if x['name'] == r['name'] and x['argument'] == 'n')['minimum_rng_advances'] == r['minimum_rng_advances'] for r in rows)
fig, ax = plt.subplots(figsize=(9, 3.7))
values = [r['minimum_rng_advances'] for r in rows]
bars = ax.bar(range(len(rows)), values, width=.6, color='#316f9e')
ax.axhline(7, color='#a45e2a', linestyle='--', label='Previously reproduced FreeLIP prefix: 7')
ax.bar_label(bars, labels=[f'≥ {v}' for v in values], padding=4, fontsize=10)
ax.set_ylim(0, 132)
ax.set_ylabel('RNG recurrence advances (lower bound)', fontsize=10)
ax.set_xticks(range(len(rows)), [r['name'] for r in rows], fontsize=9)
ax.spines[['top', 'right']].set_visible(False)
ax.legend(frameon=False, loc='upper left', fontsize=9)
ax.set_title('Default NTL ProbPrime: one small base plus ten full-size bases\n26-bit limbs; p and n give identical bounds for each curve; 12 source-derived inputs', fontsize=10)
fig.tight_layout()
path = here / 'call_bounds.svg'
fig.savefig(path)
path.write_text('\n'.join(line.rstrip() for line in path.read_text().splitlines()) + '\n')
