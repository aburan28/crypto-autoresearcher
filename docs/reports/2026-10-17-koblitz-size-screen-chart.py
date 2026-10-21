"""Render largest prime subgroup bits for the two binary Koblitz curves."""
from __future__ import annotations
import json
from pathlib import Path

root=Path(__file__).resolve().parents[2]
data=json.loads((root/'research/icperf_koblitz_size_screen_20261017/orders.json').read_text())
x0,x1,y0,y1=80,970,360,55
def X(n): return x0+(n-50)*(x1-x0)/13
def Y(b): return y0-(b/64)*(y0-y1)
parts=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="430" viewBox="0 0 1050 430">',
       '<rect width="1050" height="430" fill="white"/>',
       '<text x="30" y="30" font-family="sans-serif" font-size="21" font-weight="bold" fill="#18303a">Binary Koblitz: field degree vs largest prime subgroup</text>',
       f'<rect x="{x0}" y="{Y(64):.1f}" width="{x1-x0}" height="{Y(51)-Y(64):.1f}" fill="#fff0df"/>',
       '<text x="86" y="108" font-family="sans-serif" font-size="13" fill="#9b501b">subgroup order ≥ 2^50 (bit length ≥ 51)</text>']
for b in (0,10,20,30,40,50,60):
    y=Y(b)
    parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#d5dfe5"/>')
    parts.append(f'<text x="67" y="{y+5:.1f}" text-anchor="end" font-family="sans-serif" font-size="13">{b}</text>')
for n in range(50,64):
    x=X(n)
    parts.append(f'<text x="{x:.1f}" y="384" text-anchor="middle" font-family="sans-serif" font-size="12">{n}</text>')
for curve,color in zip(data['curves'],('#16644c','#315aaf')):
    points=' '.join(f'{X(r["field_degree"]):.1f},{Y(r["largest_prime_subgroup_bits"]):.1f}' for r in curve['rows'])
    parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
    for r in curve['rows']:
        parts.append(f'<circle cx="{X(r["field_degree"]):.1f}" cy="{Y(r["largest_prime_subgroup_bits"]):.1f}" r="4" fill="{color}"/>')
parts.extend(['<text x="370" y="416" font-family="sans-serif" font-size="14">ambient field degree n (GF(2^n))</text>',
              '<text x="15" y="215" transform="rotate(-90 15 215)" font-family="sans-serif" font-size="14">largest prime subgroup bit length</text>',
              '<text x="730" y="42" font-family="sans-serif" font-size="14" fill="#16644c">● a=0</text>',
              '<text x="810" y="42" font-family="sans-serif" font-size="14" fill="#315aaf">● a=1</text>',
              '</svg>'])
out=Path(__file__).with_name('2026-10-17-koblitz-size-screen.svg')
out.write_text('\n'.join(parts)+'\n')
print(out)
