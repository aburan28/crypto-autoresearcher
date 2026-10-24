#!/usr/bin/env python3
"""Render source-versus-strict threshold differences from pinned comparison."""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / 'comparison_bound.json').read_text())['rows']
rows.sort(key=lambda r: (r['field_bits'], r['name']))
height = 190 + len(rows)*29
x0 = 230
scale = 13
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="880" height="{height}" viewBox="0 0 880 {height}">',
       '<rect width="880" height="100%" fill="white"/>',
       '<style>text{font-family:Arial,sans-serif;fill:#26394a}.title{font-size:18px;font-weight:bold}.label{font-size:13px}.tick{font-size:12px}</style>',
       '<text class="title" x="20" y="29">Difference from a strict Elkies-only trace threshold</text>',
       '<text class="tick" x="20" y="52">Strict exact cutoff minus reported public-table cutoff; positive means the table reaches it earlier</text>']
for tick in [0, 8, 16, 24, 32]:
    x = x0+tick*scale
    out += [f'<line x1="{x}" y1="70" x2="{x}" y2="{height-70}" stroke="#d8e0e9"/>',
            f'<text class="tick" x="{x}" y="{height-54}" text-anchor="middle">{tick}</text>']
for i,r in enumerate(rows):
    y=83+i*29
    delta=r['strict_exact_elkies_only_cutoff']-r['source_reported_cutoff']
    color='#d08339' if delta else '#5b88aa'
    out += [f'<text class="label" x="20" y="{y+13}">{html.escape(r["name"])}</text>',
            f'<rect x="{x0}" y="{y}" width="{max(2,delta*scale)}" height="17" fill="{color}"/>',
            f'<text class="tick" x="{x0+max(2,delta*scale)+8}" y="{y+14}">{delta}</text>']
    if i and rows[i-1]['field_bits']!=r['field_bits']:
        out.append(f'<line x1="20" y1="{y-5}" x2="810" y2="{y-5}" stroke="#b6c7d6"/>')
out += [f'<text class="tick" x="20" y="{height-20}">Pinned external source SHA-256 9fd4cf9a…; checked comparison: comparison_bound.json.</text>', '</svg>']
(HERE/'cutoff_differences.svg').write_text('\n'.join(out)+'\n')
