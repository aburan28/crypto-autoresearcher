"""Render only the retained-diagnostics values; no scientific computation."""
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
data = json.loads((HERE/'retained-diagnostics.json').read_text())
fig, axes = plt.subplots(1, 2, figsize=(11, 4.4), constrained_layout=True)
ax = axes[0]
for offset, key, label, color in [(-0.24,'rows','Retained witnesses','#436c9b'),
                                 (0,'unique_affine_equations','Distinct affine equations','#57a290'),
                                 (0.24,'rank','Rank','#c98b48')]:
    values = [c['summary'][key] for c in data['prym']]
    bars = ax.bar([i+offset for i in range(2)], values, width=0.24, label=label, color=color)
    ax.bar_label(bars, padding=3)
ax.set_xticks([0,1],['p=4099, b=13','p=4099, b=16'])
ax.set_ylabel('Counts (exact retained-matrix recomputation)')
ax.set_ylim(0,115)
ax.legend(fontsize=8)
ax.set_title('RUN-ECDLP-967315: repeated witnesses')
ax = axes[1]
values = data['outside_cancellation']
before = [v['base_rank_before'] for v in values]
gain = [v['rank_gain'] for v in values]
ax.bar(range(4), before, label='Existing full-base rank', color='#436c9b')
bars = ax.bar(range(4), gain, bottom=before, label='Added after cancellation', color='#57a290')
ax.bar_label(bars, labels=[f'+{v}' for v in gain], padding=3)
ax.set_xticks(range(4), ['One outside','Two outside','Signed triangle','Combined'], rotation=20)
ax.set_ylim(0,11)
ax.set_ylabel('Rank over the subgroup field')
ax.legend(fontsize=8)
ax.set_title('F4 check-04: constructed fixtures only')
fig.suptitle('Post-data algebraic diagnostics — no new scientific trials', fontsize=13)
fig.savefig(HERE/'retained-diagnostics.svg')
# Matplotlib emits spaces at SVG path line endings; normalize text for Git.
svg = HERE/'retained-diagnostics.svg'
svg.write_text('\n'.join(line.rstrip() for line in svg.read_text().splitlines())+'\n')
# Lightweight preview; the vector rendering and report retain full detail.
fig.savefig(HERE/'retained-diagnostics.png', dpi=90)
plt.close(fig)
