"""Render the exact binary-field multiplicative-divisor gap screen as SVG."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
data = json.loads((ROOT / "research/icperf_binary_divisor_20261017/field_fit.json").read_text())
rows = data["rows"]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="960" height="405" viewBox="0 0 960 405">',
         '<rect width="960" height="405" fill="white"/>',
         '<text x="24" y="35" font-family="sans-serif" font-size="21" font-weight="bold" fill="#18303a">Nearest divisor of 2^n−1 vs 2 × nominal base size</text>']
for j, m in enumerate(range(2, 9)):
    parts.append(f'<text x="{242+j*107}" y="84" text-anchor="middle" font-family="sans-serif" font-size="16">m={m}</text>')
for i, row in enumerate(rows):
    y = 99 + 70*i
    parts.append(f'<text x="178" y="{y+39}" text-anchor="end" font-family="sans-serif" font-size="16">GF(2^{row["bits"]})</text>')
    for j, cell in enumerate(row["cells"]):
        gap = 100 * cell["nominal_gap_numerator"] / cell["nominal_gap_denominator"]
        color = "#d2ead7" if gap <= 15 else "#f9dfae" if gap <= 25 else "#efc0b5"
        x = 190 + 107*j
        parts.append(f'<rect x="{x}" y="{y}" width="105" height="68" fill="{color}"/>')
        parts.append(f'<text x="{x+52}" y="{y+41}" text-anchor="middle" font-family="sans-serif" font-size="16" fill="#1d303a">{gap:.1f}%</text>')
parts.extend(['<text x="24" y="347" font-family="sans-serif" font-size="13" fill="#3c4c56">Green: ≤15%; amber: 15–25%; red: &gt;25%. Rounded to 0.1%.</text>',
              '<text x="24" y="368" font-family="sans-serif" font-size="13" fill="#3c4c56">Source: research/icperf_binary_divisor_20261017/field_fit.json. Field eligibility only.</text>',
              '</svg>'])
out = Path(__file__).with_name("2026-10-17-icperf-binary-divisor-fit.svg")
out.write_text("\n".join(parts) + "\n")
print(out)
