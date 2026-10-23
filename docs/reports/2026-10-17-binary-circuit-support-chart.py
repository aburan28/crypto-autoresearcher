"""Render live XOR-AND gate counts from the archived binary m=8 circuit record."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "research/icperf_binary_circuit_support_20261017/circuit.json"
OUT = Path(__file__).with_name("2026-10-17-binary-circuit-support.svg")
rows = json.loads(DATA.read_text())["arms"]
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="680" viewBox="0 0 1080 680">',
    '<rect width="1080" height="680" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#183040}.title{font-size:25px;font-weight:bold}.head{font-size:18px;font-weight:bold}.label{font-size:16px}.small{font-size:14px}</style>',
    '<text x="540" y="42" text-anchor="middle" class="title">Binary m=8 chains: live circuit gates</text>',
    '<text x="540" y="70" text-anchor="middle" class="label">Same GF(2^61) schoolbook multiplier and polynomial basis; seven equations</text>',
    '<text x="435" y="112" text-anchor="middle" class="head">AND gates</text>',
    '<text x="820" y="112" text-anchor="middle" class="head">XOR gates</text>',
    '<line x1="20" y1="126" x2="1050" y2="126" stroke="#bacbd3"/>',
]
for i, arm in enumerate(rows):
    kind = "torsion φ" if arm["kind"] == "torsion_phi" else "raw x"
    selected = i < 2
    y = 162 + 94 * i
    gates = arm["all_equations_live"]
    color = "#12846b" if arm["kind"] == "torsion_phi" else "#4f7899"
    if not selected:
        color = "#98a6ad" if arm["kind"] == "torsion_phi" else "#b3bdc2"
    parts.append(f'<text x="25" y="{y+23}" class="label">{kind}, k={arm["base_dimension"]}</text>')
    if not selected:
        parts.append(f'<text x="25" y="{y+45}" class="small">width control</text>')
    for x, value, scale in [(285, gates["and"], 50000), (670, gates["xor"], 110000)]:
        width = round(value / scale * 270, 1)
        parts.append(f'<rect x="{x}" y="{y}" width="{width}" height="33" fill="{color}"/>')
        parts.append(f'<text x="{x+width+9}" y="{y+23}" class="small">{value:,}</text>')
    parts.append(f'<line x1="20" y1="{y+68}" x2="1050" y2="{y+68}" stroke="#e0e8eb"/>')
parts += [
    '<text x="540" y="575" text-anchor="middle" class="label">Circuit size reverses the expanded-ANF term ordering on this fixed encoding.</text>',
    '<text x="540" y="610" text-anchor="middle" class="small">Live two-input gates after common-subexpression reuse across the seven equations; primary inputs excluded.</text>',
    '<text x="540" y="641" text-anchor="middle" class="small">Neither gate count is a solver runtime, degree-of-regularity measurement, or complete ECDLP cost.</text>',
    '</svg>',
]
OUT.write_text("\n".join(parts) + "\n")
