#!/usr/bin/env sage -python
import json
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

here = Path(__file__).resolve().parent
data = json.loads((here / 'summary.json').read_text())
rows = data['builds']
fig, ax = plt.subplots(figsize=(8.2, 3.7))
ok = [r['successful_commands'] for r in rows]
bad = [r['failed_commands'] for r in rows]
ax.bar(range(4), ok, color='#316f9e')
ax.bar(range(4), bad, bottom=ok, color='#bb7444')
for i, (a, b) in enumerate(zip(ok, bad)):
    ax.text(i, a + b + .6, f'{a} passed; {b} failed', ha='center', fontsize=9)
ax.set_xticks(range(4), ['v1: header case', 'v2: return declaration', 'v3: return declaration', 'v4: build completes'], fontsize=9)
ax.set_ylim(0, 58); ax.set_ylabel('Compiler / linker commands', fontsize=10)
ax.spines[['top', 'right']].set_visible(False)
ax.set_title('Compatibility build history: every attempted command retained\nCounts are build diagnostics, not runtime or speed comparisons', fontsize=11)
ax.legend(handles=[Patch(facecolor='#316f9e', label='Exit zero'), Patch(facecolor='#bb7444', label='Compiler error')], frameon=False, fontsize=9)
fig.tight_layout()
p = here / 'build_history.svg'; fig.savefig(p)
p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines()) + '\n')
