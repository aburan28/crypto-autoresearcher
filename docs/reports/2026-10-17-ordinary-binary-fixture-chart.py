"""Render the exact 30-curve ordinary-binary subgroup-size screen."""

from __future__ import annotations

import json
import math
from pathlib import Path

root = Path(__file__).resolve().parents[2]
rows = json.loads((root / "research/icperf_ordinary_binary_fixture_20261017/screen.json").read_text())["rows"]
x0, x1, y0, y1 = 76, 1000, 320, 50


def x(b: int) -> float:
    return x0 + (b - 2) * (x1 - x0) / 29


def y(bits: float) -> float:
    return y0 - bits * (y0 - y1) / 64


parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1080" height="400" viewBox="0 0 1080 400">',
         '<rect width="1080" height="400" fill="white"/>',
         '<text x="30" y="29" font-family="sans-serif" font-size="20" font-weight="bold" fill="#18303a">Ordinary binary GF(2^61): exact prime-subgroup screen</text>',
         f'<rect x="{x0}" y="{y(64):.1f}" width="{x1-x0}" height="{y(50)-y(64):.1f}" fill="#fff0df"/>',
         '<text x="82" y="82" font-family="sans-serif" font-size="13" fill="#9b501b">prime subgroup order ≥ 2^50</text>']
for bits in (0, 10, 20, 30, 40, 50, 60):
    yy = y(bits)
    parts.append(f'<line x1="{x0}" y1="{yy:.1f}" x2="{x1}" y2="{yy:.1f}" stroke="#d5dfe5"/>')
    parts.append(f'<text x="67" y="{yy+5:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{bits}</text>')
for b in range(2, 32, 2):
    parts.append(f'<text x="{x(b):.1f}" y="342" text-anchor="middle" font-family="sans-serif" font-size="12">{b}</text>')
points = []
for row in rows:
    b = row["b_polynomial_bits"]
    p = max(item["factor"] for item in row["exact_prime_factorization"])
    yy = y(math.log2(p))
    points.append(f'{x(b):.1f},{yy:.1f}')
    color = '#c45b24' if b == 31 else '#315aaf'
    radius = 6 if b == 31 else 3.5
    parts.append(f'<circle cx="{x(b):.1f}" cy="{yy:.1f}" r="{radius}" fill="{color}"/>')
parts.append(f'<polyline points="{" ".join(points)}" fill="none" stroke="#315aaf" stroke-width="2" opacity="0.6"/>')
row = rows[-1]
p = row["certified_prime_candidates"][0]
parts.append(f'<text x="{x(31)-6:.1f}" y="{y(math.log2(p))-13:.1f}" text-anchor="end" font-family="sans-serif" font-size="13" fill="#9b501b">b=31; log₂ r≈{math.log2(p):.2f}</text>')
parts.extend(['<text x="345" y="378" font-family="sans-serif" font-size="14">b as polynomial-basis integer; fixed field and curve model</text>',
              '<text x="16" y="219" transform="rotate(-90 16 219)" font-family="sans-serif" font-size="13">log₂ largest prime factor</text>',
              '</svg>'])
output = Path(__file__).with_name('2026-10-17-ordinary-binary-fixture.svg')
output.write_text('\n'.join(parts) + '\n')
print(output)
