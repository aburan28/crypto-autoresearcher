"""Plots recorded rows/intervals only; no cryptographic experiments or fits."""
from pathlib import Path
import datetime as dt
import json
import os
os.environ.setdefault('MPLCONFIGDIR', '/tmp/classical-ecdlp-pilot-mpl')
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / 'runs' / 'RUN-ECDLP-d7f049'
parts = json.loads((RUN / 'parts-manifest.json').read_text())
raw = json.loads((RUN / 'raw-result.json').read_text())
rows = []
for module in parts['modules']:
    for part in module['parts']:
        rows.extend(json.loads(line) for line in (RUN / part['path']).read_text().splitlines())

def save(fig, name):
    for ext in ('svg', 'pdf'):
        fig.savefig(HERE / (name+'.'+ext))
    plt.close(fig)

jobs = raw['module_execution']
zero = min(dt.datetime.fromisoformat(j['measurement']['started_utc']) for j in jobs)
fig, ax = plt.subplots(figsize=(8.2, 2.8), layout='constrained')
for i, j in enumerate(jobs):
    r = j['measurement']
    start = (dt.datetime.fromisoformat(r['started_utc'])-zero).total_seconds()
    ax.barh(i, r['wall_seconds'], left=start, height=.6, color='#2c6692')
    ax.text(start+r['wall_seconds']+.05, i, f"{r['wall_seconds']:.3f} s", va='center', fontsize=8)
ax.set_yticks(range(len(jobs)), [j['name'] for j in jobs]); ax.invert_yaxis()
ax.set_xlim(0, max((dt.datetime.fromisoformat(j['measurement']['started_utc'])-zero).total_seconds()+j['measurement']['wall_seconds'] for j in jobs)+.7)
ax.set_xlabel('Seconds after '+zero.strftime('%H:%M:%S UTC')+'; measurement phase only')
ax.set_title('Five module processes in a pool of three workers', fontsize=11)
ax.grid(axis='x', alpha=.2); ax.set_axisbelow(True)
save(fig, 'execution')

drows = [r for r in rows if r['track']=='D']
fig, ax = plt.subplots(figsize=(8.2, 3.3), layout='constrained')
ax.bar(range(len(drows)), [r['gate_nodes'] for r in drows], color=['#2c6692' if 'main' in r['fixture'] else '#a77122' for r in drows])
ax.set_xticks(range(len(drows)), [f"p={r['p']}\nr={r['r']}" for r in drows])
ax.set_ylabel('Scalar circuit gate nodes (count)')
ax.set_title('Constructed forward Boolean circuits; no inversion speed claim', fontsize=11)
ax.grid(axis='y', alpha=.2); ax.set_axisbelow(True)
save(fig, 'circuits')

krows = sorted([r for r in rows if r['track']=='L9' and r.get('projection')=='kummer_x'], key=lambda r:r['r'])
assert len(krows)==8, 'Kummer projection name/coverage mismatch'
fig, ax = plt.subplots(figsize=(8.2, 3.8), layout='constrained')
x = [r['r'] for r in krows]
ax.errorbar(x, [r['null_mean_bits'] for r in krows], yerr=[r['null_sample_sd_bits'] for r in krows], fmt='s', ms=5, capsize=3, label='Unconditional null mean ± draw SD (99 draws)', color='#a77122')
ax.plot(x, [r['entropy_bits'] for r in krows], 'o', ms=7, label='Exact full-pair observed entropy', color='#2c6692')
ax.plot(x, [r['matched_null_mean_bits'] for r in krows], 'x', ms=8, label='Sign-pair matched null mean (99 draws)', color='#202020')
ax.set_xlabel('Prime subgroup order r'); ax.set_ylabel('Conditional entropy (bits)')
ax.set_title('Kummer control: sign matching removes the unconditional gap', fontsize=11)
ax.grid(alpha=.2); ax.legend(fontsize=8, loc='best')
save(fig, 'kummer-controls')

lrows = [r for r in rows if r['track']=='L9']
fixtures = list(dict.fromkeys(r['fixture'] for r in lrows))
projections = list(dict.fromkeys(r['projection'] for r in lrows))
matrix = np.full((len(projections),len(fixtures)), np.nan)
for r in lrows:
    if r['outcome']=='complete_valid':
        matrix[projections.index(r['projection']),fixtures.index(r['fixture'])] = r['primary_observed_minus_reference_mean_bits']
fig, ax = plt.subplots(figsize=(8.2, 6.8), layout='constrained')
extent=max(abs(float(np.nanmin(matrix))),abs(float(np.nanmax(matrix))),.001)
palette=plt.get_cmap('RdBu_r').copy(); palette.set_bad('#b8b8b8')
im=ax.imshow(np.ma.masked_invalid(matrix), cmap=palette, vmin=-extent, vmax=extent, aspect='auto')
ax.set_xticks(range(len(fixtures)), [f.replace('pilot-','').replace('endo_j0','j0') for f in fixtures], rotation=55, ha='right', fontsize=8)
ax.set_yticks(range(len(projections)),projections,fontsize=8)
ax.set_title('Exact finite projection observations minus primary null means',fontsize=11)
fig.colorbar(im, ax=ax, label='Observed − reference mean (bits)', shrink=.8)
save(fig, 'projection-panel')
