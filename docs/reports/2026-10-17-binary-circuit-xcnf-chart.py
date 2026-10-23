"""Render exact serialized XCNF input counts from the frozen manifest."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "research/icperf_binary_circuit_xcnf_20261017/manifest.json"
OUT = Path(__file__).with_name("2026-10-17-binary-circuit-xcnf.svg")
rows = json.loads(DATA.read_text())["arms"]
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="590" viewBox="0 0 1080 590">',
    '<rect width="1080" height="590" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#183040}.title{font-size:25px;font-weight:bold}.head{font-size:18px;font-weight:bold}.label{font-size:16px}.small{font-size:14px}</style>',
    '<text x="540" y="42" text-anchor="middle" class="title">Selected binary m=8 solver inputs</text>',
    '<text x="540" y="70" text-anchor="middle" class="label">Seven three-point equations plus exact precomputed base-coordinate membership</text>',
    '<text x="430" y="118" text-anchor="middle" class="head">CNF clauses</text>',
    '<text x="812" y="118" text-anchor="middle" class="head">Native XOR rows</text>',
    '<line x1="30" y1="132" x2="1040" y2="132" stroke="#b9cbd3"/>',
]
for i, arm in enumerate(rows):
    y = 173 + i * 125
    kind = "torsion φ" if arm["kind"] == "torsion_phi" else "raw x"
    color = "#12846b" if i == 0 else "#4f7899"
    parts.append(f'<text x="26" y="{y+22}" class="label">{kind}</text>')
    parts.append(f'<text x="26" y="{y+45}" class="small">{arm["allowed_coordinate_values"]} allowed values</text>')
    for x, value, scale in [(285, arm["cnf_clauses"], 150000),
                            (665, arm["native_xor_rows"], 110000)]:
        width = round(value / scale * 275, 1)
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="35" fill="{color}"/>')
        parts.append(f'<text x="{x+width+9}" y="{y+24}" class="small">{value:,}</text>')
    parts.append(f'<line x1="30" y1="{y+85}" x2="1040" y2="{y+85}" stroke="#e0e8eb"/>')
parts += [
    '<rect x="40" y="433" width="1000" height="75" rx="8" fill="#eff4f5"/>',
    '<text x="540" y="460" text-anchor="middle" class="label">Torsion planted assignment: every 79,626 CNF clause and 61,020 XOR row checks.</text>',
    '<text x="540" y="488" text-anchor="middle" class="small">Raw-x reachability, curve lifts, sign consistency, poles, other target channels and solver cost remain open.</text>',
    '<text x="540" y="555" text-anchor="middle" class="small">Source: frozen XCNF manifest and independent serialized-formula verification; no solver trial was run.</text>',
    '</svg>',
]
OUT.write_text("\n".join(parts) + "\n")
