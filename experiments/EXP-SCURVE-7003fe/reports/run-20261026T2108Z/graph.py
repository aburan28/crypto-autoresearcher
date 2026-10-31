"""Draw only the three recorded curve orders from data.json."""

import json
from pathlib import Path

here = Path(__file__).resolve().parent
data = json.loads((here / "data.json").read_text())
rows = data["rows"]
assert [(r["role"], r["order"]) for r in rows] == [
    ("positive_anomalous", 5),
    ("positive_embedding", 6),
    ("negative", 23),
]

parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="680" height="330" viewBox="0 0 680 330">',
    '<rect width="680" height="330" fill="white"/>',
    '<text x="340" y="24" text-anchor="middle" font-family="sans-serif" font-size="16">Recorded curve orders · RUN-SCURVE-acab50</text>',
    '<text x="17" y="55" font-family="sans-serif" font-size="12">points (n=3 curves)</text>',
]
left, baseline, scale = 170, 263, 9
for i, row in enumerate(rows):
    x = left + i * 160
    height = row["order"] * scale
    parts += [
        f'<rect x="{x}" y="{baseline-height}" width="72" height="{height}" fill="#416aa3"/>',
        f'<text x="{x+36}" y="{baseline-height-7}" text-anchor="middle" font-family="sans-serif" font-size="13">{row["order"]}</text>',
        f'<text x="{x+36}" y="{baseline+19}" text-anchor="middle" font-family="sans-serif" font-size="12">{row["role"].replace("positive_", "")}</text>',
        f'<text x="{x+36}" y="{baseline+34}" text-anchor="middle" font-family="sans-serif" font-size="11">p={row["p"]}</text>',
    ]
parts += [
    f'<line x1="145" y1="{baseline}" x2="625" y2="{baseline}" stroke="#333"/>',
    '<text x="340" y="320" text-anchor="middle" font-family="sans-serif" font-size="11">No uncertainty interval was recorded. Source: raw-result.json.</text>',
    '</svg>',
]
(here / "graph.svg").write_text("\n".join(parts) + "\n")
