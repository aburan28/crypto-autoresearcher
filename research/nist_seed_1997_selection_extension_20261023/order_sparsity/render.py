#!/usr/bin/env python3
"""Editable, data-derived stacked comparison chart."""

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "analysis.json").read_text())
labels = [
    ("n_binary_weight", "Binary weight of n"),
    ("n_naf_weight", "Signed-digit weight of n"),
    ("gap_binary_weight", "Binary weight of 2^m−n"),
    ("gap_naf_weight", "Signed-digit weight of 2^m−n"),
]
colors = {"published": "#2b6d9a", "tie": "#b9c2ca", "omitted": "#d2773f"}
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="390" viewBox="0 0 1000 390">',
    '<rect width="1000" height="390" fill="white"/>',
    '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#223245}.title{font-size:21px;font-weight:700}.label{font-size:15px}.count{font-size:15px;fill:white;font-weight:700}.legend{font-size:14px}.note{font-size:13px;fill:#536577}</style>',
    '<text class="title" x="32" y="38">Earlier omitted curve versus later published curve</text>',
    '<text class="note" x="32" y="64">16 exact same-field pairs per metric; smaller weight is the proposed preference</text>',
]
bar_x, unit = 380, 31
for index, (metric, label) in enumerate(labels):
    y = 99 + index * 60
    s = data["summary"][metric]
    better = s["published_better_earlier_omission_pairs"]
    tie = s["ties_earlier_omission_pairs"]
    worse = 16 - better - tie
    parts.append(f'<text class="label" x="32" y="{y+22}">{html.escape(label)}</text>')
    cursor = bar_x
    for count, key in ((better, "published"), (tie, "tie"), (worse, "omitted")):
        if count:
            width = count * unit
            parts.append(f'<rect x="{cursor}" y="{y}" width="{width}" height="35" fill="{colors[key]}"/>')
            if width >= 28:
                text_color = '#223245' if key == 'tie' else 'white'
                parts.append(f'<text x="{cursor+width/2}" y="{y+24}" text-anchor="middle" style="font:700 15px Arial;fill:{text_color}">{count}</text>')
            cursor += width
    assert cursor == bar_x + 16 * unit
parts.extend([
    '<rect x="35" y="350" width="15" height="15" fill="#2b6d9a"/><text class="legend" x="58" y="363">published lighter</text>',
    '<rect x="265" y="350" width="15" height="15" fill="#b9c2ca"/><text class="legend" x="288" y="363">tie</text>',
    '<rect x="365" y="350" width="15" height="15" fill="#d2773f"/><text class="legend" x="388" y="363">omitted lighter</text>',
    '<text class="note" x="665" y="363">The two signed-digit rows agree identically.</text>',
    '</svg>',
])
(HERE / "pair_counts.svg").write_text("\n".join(parts) + "\n")
print("rendered pair_counts.svg from 16 exact earlier-omission pairs")
