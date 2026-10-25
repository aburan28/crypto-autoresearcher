#!/usr/bin/env sage -python
import hashlib
import json
from collections import Counter
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

here = Path(__file__).resolve().parent
raw = (here / 'source_audit.json').read_bytes()
data = json.loads(raw)
verified = json.loads((here / 'verification.json').read_text())
assert verified['status'] == 'passed'
assert verified['source_audit_sha256'] == hashlib.sha256(raw).hexdigest()
counts = Counter(abs(r['signed_h_entry']) for r in data['catalog_rows'])
keys = sorted(counts)
fig, ax = plt.subplots(figsize=(8.5, 3.6))
bars = ax.bar(range(len(keys)), [counts[k] for k in keys], color=['#a76a36' if k == 0 else '#316f9e' for k in keys])
ax.bar_label(bars, padding=2, fontsize=8)
ax.set_xticks(range(len(keys)), [str(k) for k in keys], fontsize=9)
ax.set_xlabel('Absolute value of stored h entry (not independently recomputed)', fontsize=9)
ax.set_ylabel('Catalog rows', fontsize=10)
ax.set_ylim(0, max(counts.values()) * 1.15)
ax.spines[['top', 'right']].set_visible(False)
ax.set_title('Recovered ECPP 3.4.1 catalog: 1,684 records\nD = 0 is the N ± 1 route; remaining records offer CM search choices', fontsize=11)
fig.tight_layout()
p = here / 'catalog.svg'
fig.savefig(p)
p.write_text('\n'.join(s.rstrip() for s in p.read_text().splitlines()) + '\n')
