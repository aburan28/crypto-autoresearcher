#!/usr/bin/env python3
"""Render the four frozen BINSTD toy cells from the independent audit evidence."""

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
    tau, open_ = row["archived_hits"]["tau"], row["archived_hits"]["open"]
    parts.extend([
        f'<text x="40" y="{y+20}" class="label">{label}</text>',
        f'<rect x="230" y="{y}" width="{tau*12}" height="25" fill="#207c76"/>',
        f'<text x="{238+tau*12}" y="{y+19}" class="count">{tau}/40 tau</text>',
        f'<rect x="230" y="{y+29}" width="{open_*12}" height="25" fill="#cb8a27"/>',
        f'<text x="{238+open_*12}" y="{y+48}" class="count">{open_}/40 open</text>',
    ])
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="850" height="570" viewBox="0 0 850 570">
<style>text{{font-family:DejaVu Sans,Arial,sans-serif;fill:#1e293b}}
.title{{font-size:24px;font-weight:bold}}.sub{{font-size:14px;fill:#475569}}
.label{{font-size:16px;font-weight:bold}}.count{{font-size:14px}}.foot{{font-size:13px;fill:#475569}}</style>
<rect width="850" height="570" fill="white"/>
<text x="40" y="48" class="title">BINSTD archived toy hits: independent witness check</text>
<text x="40" y="76" class="sub">Exact main {data['source_main'][:12]} · four 40-target cells · 160 targets</text>
<text x="40" y="100" class="sub">Bars are hit counts, not runtime or attack advantage.</text>
{''.join(parts)}
<text x="40" y="524" class="foot">276 reported hit witnesses reconstruct their targets under an independent field implementation.</text>
<text x="40" y="545" class="foot">False hits and the original host's execution or timing are not established by this check.</text>
</svg>
'''
(HERE / "hits.svg").write_text(svg)
print(HERE / "hits.svg")
