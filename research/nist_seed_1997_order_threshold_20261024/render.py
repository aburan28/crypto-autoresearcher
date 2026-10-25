#!/usr/bin/env python3
"""Draw exact within-field order ranks; spacing is rank, not order magnitude."""
import html
import json
from collections import defaultdict
from pathlib import Path

here = Path(__file__).resolve().parent
data = json.loads((here / "analysis.json").read_text())
groups = defaultdict(list)
for row in data["rows"]:
    groups[row["field_bits"]].append(row)
W, H = 1520, 780
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">', '<rect width="100%" height="100%" fill="white"/>', '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#202938}.title{font-size:24px;font-weight:bold}.sub{font-size:15px}.field{font-size:20px;font-weight:bold}.label{font-size:15px}.small{font-size:13px}</style>', '<text x="28" y="38" class="title">Can a minimum subgroup order explain the omissions?</text>', '<text x="28" y="64" class="sub">Exact order rank within each field; spacing shows rank, not numeric distance. Blue = published; orange = omitted.</text>']
for i, bits in enumerate((192, 224, 239, 256)):
    rows = sorted(groups[bits], key=lambda r: r["n"])
    y = 155 + i * 150
    left, right = 300, 1400
    step = (right-left)/max(len(rows)-1,1)
    xs = [left+j*step for j in range(len(rows))]
    floor = min(r["n"] for r in rows if r["label"] == "published")
    first_pub = next(j for j,r in enumerate(rows) if r["n"] == floor)
    boundary = xs[first_pub]-step/2 if first_pub else left-35
    forced = sum(r["label"] == "omitted" and r["n"] >= floor for r in rows)
    parts += [f'<text x="28" y="{y-7}" class="field">{bits}-bit field</text>', f'<text x="28" y="{y+18}" class="small">{forced} skipped must pass</text>', f'<rect x="{boundary:.1f}" y="{y-58}" width="{right-boundary+35:.1f}" height="105" fill="#eaf3ff"/>', f'<line x1="{left-35}" y1="{y}" x2="{right+35}" y2="{y}" stroke="#66758b" stroke-width="2"/>', f'<line x1="{boundary:.1f}" y1="{y-58}" x2="{boundary:.1f}" y2="{y+47}" stroke="#335a89" stroke-width="2" stroke-dasharray="5 4"/>']
    for j,(x,r) in enumerate(zip(xs,rows)):
        pub = r["label"] == "published"
        color = "#2469a3" if pub else "#d36b24"
        marker_y = y-19 if pub else y+19
        label = r["name"] if pub else f"#{r['ordinal']}"
        label_y = y-30 if pub else y+39
        parts += [f'<circle cx="{x:.1f}" cy="{marker_y}" r="7" fill="{color}"/>', f'<text x="{x:.1f}" y="{label_y}" text-anchor="middle" class="label">{html.escape(label)}</text>']
    parts.append(f'<text x="{right+50}" y="{y+5}" class="small">n increases →</text>')
parts += ['<text x="28" y="755" class="small">Shaded region: n ≥ smallest published n, so every field-fixed r_min that accepts all published curves also accepts every orange point there.</text>', '</svg>']
(here / "order_ranks.svg").write_text("\n".join(parts)+"\n")
