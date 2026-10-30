import datetime
import json
import os
from pathlib import Path
os.environ.setdefault('MPLCONFIGDIR', '/tmp/ecdlp-execution-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent
summary = json.loads((root / 'summary.json').read_text())
rows = sorted(summary['command_receipts'], key=lambda r: r['started_utc'])
zero = min(datetime.datetime.fromisoformat(r['started_utc']) for r in rows)
fig, ax = plt.subplots(figsize=(8.2, 3.0), layout='constrained')
for i, row in enumerate(rows):
    start = (datetime.datetime.fromisoformat(row['started_utc'])-zero).total_seconds()
    ax.barh(i, row['wall_seconds'], left=start, height=.55, color='#27649b' if row['name'].startswith('reference') else '#8b6424')
    ax.text(start + row['wall_seconds'] + .08, i, f"{row['wall_seconds']:.2f} s", va='center', fontsize=8)
ax.set_yticks(range(len(rows)), [r['name'] for r in rows])
ax.invert_yaxis()
ax.set_xlabel('Seconds after '+zero.strftime('%H:%M:%S UTC')+'; includes compilation')
ax.set_xlim(0,max((datetime.datetime.fromisoformat(r['started_utc'])-zero).total_seconds()+r['wall_seconds'] for r in rows)+1)
ax.set_title('Recorded command overlap — development replay only', fontsize=11)
ax.grid(axis='x', alpha=.2)
ax.set_axisbelow(True)
for ext in ('svg','pdf'):
    fig.savefig(root / ('timeline.'+ext))
