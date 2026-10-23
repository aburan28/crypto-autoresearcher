"""Render selected and equal-width binary input-support counts as SVG."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SUPPORT = ROOT / "research/icperf_binary_boolean_support_20261017/support.json"
CONTROLS = ROOT / "research/icperf_binary_boolean_support_20261017/controls.json"
OUT = Path(__file__).with_name("2026-10-17-binary-boolean-support.svg")
a = json.loads(SUPPORT.read_text())
b = json.loads(CONTROLS.read_text())
rows = [(arm, True) for arm in a["arms"]] + [(arm, False) for arm in b["arms"]]
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="660" viewBox="0 0 1080 660">',
    '<rect width="1080" height="660" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#183040}.title{font-size:25px;font-weight:bold}.head{font-size:18px;font-weight:bold}.label{font-size:16px}.small{font-size:14px}</style>',
    '<text x="540" y="42" text-anchor="middle" class="title">Full-field m=8 chain: one middle equation</text>',
    '<text x="540" y="69" text-anchor="middle" class="label">Exact ANF support after GF(2^61) polynomial-basis Boolean descent</text>',
    '<text x="440" y="111" text-anchor="middle" class="head">Distinct field monomials</text>',
    '<text x="830" y="111" text-anchor="middle" class="head">Descended coefficient-bit terms</text>',
    '<line x1="150" y1="125" x2="1030" y2="125" stroke="#b6c7d0"/>',
]
for i, (arm, selected) in enumerate(rows):
    stat = arm["equation_stats"][1]
    kind = "torsion φ" if arm["kind"] == "torsion_phi" else "raw x"
    y = 165 + i*92
    field_count = stat["unique_field_monomials"]
    bit_count = stat["coefficient_bit_terms"]
    color = "#12846b" if arm["kind"] == "torsion_phi" else "#4f7899"
    if not selected:
        color = "#97a5ad" if arm["kind"] == "torsion_phi" else "#b2bcc2"
    parts.append(f'<text x="30" y="{y+21}" class="label">{kind}, k={arm["base_dimension"]}</text>')
    if not selected:
        parts.append(f'<text x="30" y="{y+42}" class="small">width control</text>')
    fw = round(field_count/50000*270,1)
    bw = round(bit_count/750000*270,1)
    parts.append(f'<rect x="280" y="{y}" width="{fw}" height="31" fill="{color}"/>')
    parts.append(f'<text x="{290+fw}" y="{y+22}" class="small">{field_count:,}</text>')
    parts.append(f'<rect x="670" y="{y}" width="{bw}" height="31" fill="{color}"/>')
    parts.append(f'<text x="{680+bw}" y="{y+22}" class="small">{bit_count:,}</text>')
    parts.append(f'<line x1="25" y1="{y+66}" x2="1030" y2="{y+66}" stroke="#e0e7ea"/>')
parts += [
    '<text x="540" y="566" text-anchor="middle" class="label">Compact invariant expression → dense binary coefficients → solver behavior still unmeasured</text>',
    '<text x="540" y="601" text-anchor="middle" class="small">Selected bases have 267 (φ) and 265 (raw x) projected columns; width controls are symbolic only.</text>',
    '<text x="540" y="635" text-anchor="middle" class="small">Source: support.json, controls.json and independent Sage replay; counts exclude lift and pole constraints.</text>',
    '</svg>',
]
OUT.write_text("\n".join(parts) + "\n")
