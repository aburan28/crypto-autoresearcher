"""Render target-blind binary affine-subspace base and control sizes."""

from __future__ import annotations

import json
from pathlib import Path

root = Path(__file__).resolve().parents[2]
data = json.loads((root / "research/icperf_binary_subspace_base_20261017/base.json").read_text())
scans = data["candidate_scans"]
target = data["predeclared_selection"]["target_size"]
selected = data["selected_offset"]
rows = [(f"offset {scan['offset']}", scan["realized_size"], scan["offset"] == selected)
        for scan in scans]
rows.append(("random control", data["random_control"]["realized_size"], False))
x0, xmax = 230, 965
scale = (xmax - x0) / 330
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="420" viewBox="0 0 1050 420">',
         '<rect width="1050" height="420" fill="white"/>',
         '<text x="30" y="34" font-family="sans-serif" font-size="21" font-weight="bold" fill="#18303a">Target-blind affine F₂ subspace: realized order-r base size</text>',
         f'<line x1="{x0 + target*scale:.1f}" y1="64" x2="{x0 + target*scale:.1f}" y2="350" stroke="#b14f22" stroke-width="2" stroke-dasharray="6 4"/>',
         f'<text x="{x0 + target*scale-5:.1f}" y="60" text-anchor="end" font-family="sans-serif" font-size="13" fill="#a34a20">m=8 default B={target}</text>']
for i, (label, size, chosen) in enumerate(rows):
    y = 95 + i * 54
    color = '#16644c' if chosen else ('#6c86b8' if label == 'random control' else '#315aaf')
    parts.append(f'<text x="{x0-15}" y="{y+19}" text-anchor="end" font-family="sans-serif" font-size="15">{label}</text>')
    parts.append(f'<rect x="{x0}" y="{y}" width="{size*scale:.1f}" height="29" rx="4" fill="{color}"/>')
    parts.append(f'<text x="{x0 + size*scale + 8:.1f}" y="{y+20}" font-family="sans-serif" font-size="14" fill="#18303a">{size}</text>')
parts.extend(['<text x="358" y="393" font-family="sans-serif" font-size="14">valid subgroup abscissae; both signs are implicit</text>',
              '</svg>'])
output = Path(__file__).with_name('2026-10-17-binary-subspace-base.svg')
output.write_text('\n'.join(parts) + '\n')
print(output)
