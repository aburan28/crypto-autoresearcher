"""Render the four recorded affine-placement counts as standalone SVG."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "research/icperf_binary_projected_base_20261017/base.json"
OUT = Path(__file__).with_name("2026-10-17-binary-projected-base.svg")
d = json.loads(RECORD.read_text())
rows = d["candidate_scans"]
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="500" viewBox="0 0 900 500">',
    '<rect width="900" height="500" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#172a36} .small{font-size:16px} .title{font-size:24px;font-weight:bold}</style>',
    '<text x="450" y="40" text-anchor="middle" class="title">Ordinary binary GF(2^61): affine placements</text>',
    '<text x="450" y="72" text-anchor="middle" class="small">Each offset scans 512 x values; bars count liftable representatives</text>',
    '<line x1="105" y1="395" x2="840" y2="395" stroke="#172a36" stroke-width="2"/>',
    '<line x1="105" y1="100" x2="105" y2="395" stroke="#172a36" stroke-width="2"/>',
    '<text x="450" y="445" text-anchor="middle" class="small">Affine offset c (field encoding)</text>',
    '<text x="450" y="482" text-anchor="middle" font-size="13">Source: projected-base base.json; independently replayed in Sage. Input counts only.</text>',
]
for tick in (0, 100, 200, 300):
    y = 395 - tick * 0.9
    parts.append(f'<text x="90" y="{y+5:.1f}" text-anchor="end" class="small">{tick}</text>')
    parts.append(f'<line x1="105" y1="{y:.1f}" x2="840" y2="{y:.1f}" stroke="#d7e0e4"/>')
target_y = 395 - d["predeclared_selection"]["target_size"] * 0.9
parts += [f'<line x1="105" y1="{target_y:.1f}" x2="840" y2="{target_y:.1f}" stroke="#a45237" stroke-dasharray="8 5" stroke-width="2"/>',
          f'<text x="830" y="{target_y-7:.1f}" text-anchor="end" fill="#a45237" font-size="14">m=8 default B=287</text>']
for i, row in enumerate(rows):
    x = 155 + i * 170
    height = row["realized_size"] * 0.9
    y = 395 - height
    fill = "#0a8f6a" if row["offset"] == d["selected_offset"] else "#4f7994"
    parts.append(f'<rect x="{x}" y="{y:.1f}" width="90" height="{height:.1f}" fill="{fill}"/>')
    parts.append(f'<text x="{x+45}" y="{y-9:.1f}" text-anchor="middle" class="small">{row["realized_size"]}</text>')
    parts.append(f'<text x="{x+45}" y="418" text-anchor="middle" class="small">{row["offset"]}</text>')
parts.append('</svg>')
OUT.write_text("\n".join(parts) + "\n")
