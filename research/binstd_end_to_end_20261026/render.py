#!/usr/bin/env python3
"""Render checked hit and miss counts for the four frozen BINSTD toy cells."""

import json
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "evidence.json").read_text())
rows = data["panels"]
parts = []
for i, row in enumerate(rows):
    y = 143 + i * 86
    label = escape(row["panel"].replace("-ell", " / ell="))
    tau, open_ = (row["independent_exhaustive_hits"][arm] for arm in ("tau", "open"))
    tau_miss, open_miss = (row["independent_exhaustive_misses"][arm]
                           for arm in ("tau", "open"))
    if tau + tau_miss != 40 or open_ + open_miss != 40:
        raise ValueError(f"incomplete target outcomes in {row['panel']}")
    parts.extend([
        f'<text x="40" y="{y+20}" class="label">{label}</text>',
        f'<rect x="230" y="{y}" width="480" height="25" fill="#d9e2e8"/>',
        f'<rect x="230" y="{y}" width="{tau*12}" height="25" fill="#207c76"/>',
        f'<text x="725" y="{y+19}" class="count">tau: {tau} hit / {tau_miss} miss</text>',
        f'<rect x="230" y="{y+29}" width="480" height="25" fill="#d9e2e8"/>',
        f'<rect x="230" y="{y+29}" width="{open_*12}" height="25" fill="#cb8a27"/>',
        f'<text x="725" y="{y+48}" class="count">open: {open_} hit / {open_miss} miss</text>',
    ])
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="570" viewBox="0 0 1000 570">
<style>text{{font-family:DejaVu Sans,Arial,sans-serif;fill:#1e293b}}
.title{{font-size:24px;font-weight:bold}}.sub{{font-size:14px;fill:#475569}}
.label{{font-size:16px;font-weight:bold}}.count{{font-size:14px}}.foot{{font-size:13px;fill:#475569}}</style>
<rect width="1000" height="570" fill="white"/>
<text x="40" y="48" class="title">BINSTD toy outcomes: independent replay check</text>
<text x="40" y="76" class="sub">Exact main {data['source_main'][:12]} · four 40-target cells · 160 targets</text>
<text x="40" y="100" class="sub">Colour shows hits; grey shows misses. Bars are counts, not runtime or attack advantage.</text>
{''.join(parts)}
<text x="40" y="524" class="foot">Independent arithmetic checks 276 hits and 44 misses over the source-generated bases and targets.</text>
<text x="40" y="545" class="foot">Original host input selection, execution and timing remain unverified.</text>
</svg>
'''
(HERE / "hits.svg").write_text(svg)
print(HERE / "hits.svg")
