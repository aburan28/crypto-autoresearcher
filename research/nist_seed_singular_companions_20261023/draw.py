"""Render exact field counts from the sealed singular-companion record."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "runs/20261023T2114Z/results.json").read_text())
assert DATA["curve_count"] == 19

width, height = 900, 365
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}">',
         '<rect width="900" height="365" fill="white"/>',
         '<style>text{font-family:Arial,sans-serif;fill:#183048}.title{font-size:19px;font-weight:bold}.label{font-size:14px}.small{font-size:12px}</style>',
         '<text x="42" y="34" class="title">Identical singular input surface within each field</text>',
         '<text x="42" y="59" class="small">Archived run 20261023T2114Z · 19 exact curves · bar unit: curves</text>']
for i, bits in enumerate((192, 224, 239, 256)):
    field = DATA["fields"][str(bits)]
    y = 102 + 62*i
    omitted, published = field["omitted_count"], field["published_count"]
    orders = ["p−1" if int(f["smooth_locus_order"]) == int(field["p"])-1 else "p+1" for f in field["forms"]]
    parts.extend([
        f'<text x="42" y="{y+20}" class="label">{bits}-bit field</text>',
        f'<rect x="170" y="{y}" width="{omitted*55}" height="26" fill="#db7a24"/>',
        f'<rect x="{170+omitted*55}" y="{y}" width="{published*55}" height="26" fill="#3078b7"/>',
        f'<text x="{180+omitted*55+published*55}" y="{y+19}" class="label">b′=+2: {orders[0]} · b′=−2: {orders[1]}</text>',
        f'<text x="{170+omitted*55/2}" y="{y+19}" class="label" text-anchor="middle" fill="white" style="fill:white">{omitted}</text>',
        f'<text x="{170+omitted*55+published*55/2}" y="{y+19}" class="label" text-anchor="middle" fill="white" style="fill:white">{published}</text>',
    ])
parts += ['<rect x="42" y="330" width="14" height="14" fill="#db7a24"/>',
          '<text x="62" y="342" class="small">omitted</text>',
          '<rect x="150" y="330" width="14" height="14" fill="#3078b7"/>',
          '<text x="170" y="342" class="small">published</text>',
          '<text x="270" y="342" class="small">The orders are properties of p, not of the selected b.</text>',
          '</svg>']
(HERE / "field_surface.svg").write_text("\n".join(parts) + "\n")
