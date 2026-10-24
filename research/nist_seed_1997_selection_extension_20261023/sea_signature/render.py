#!/usr/bin/env python3
"""Render exact cutoff values; no new screening metrics."""
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = HERE / 'runs/scan-20261023T1840Z/raw.json'
OUT = HERE / 'cutoffs.svg'

def main():
    rows = json.loads(RAW.read_text())['rows']
    rows.sort(key=lambda r: (r['field_bits'], r['cutoff_ell']))
    height = 190 + len(rows) * 29
    x0, scale = 210, 2.0
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="900" height="{height}" viewBox="0 0 900 {height}">',
             '<rect width="900" height="100%" fill="white"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#25394b} .name{font-size:13px}.tick{font-size:12px}.title{font-weight:bold;font-size:18px}</style>',
             '<text class="title" x="24" y="29">Elkies-only trace threshold by exact curve</text>',
             '<text x="24" y="50" font-size="12">Smallest odd prime scanned when the Elkies-prime product M satisfies M² &gt; 16p</text>']
    for tick in [100, 150, 200, 250, 300]:
        x = x0 + tick * scale
        parts += [f'<line x1="{x}" y1="70" x2="{x}" y2="{height-70}" stroke="#d9e2ea"/>',
                  f'<text class="tick" x="{x}" y="{height-54}" text-anchor="middle">{tick}</text>']
    for idx, r in enumerate(rows):
        y = 83 + idx * 29
        color = '#d68133' if r['label'] == 'omitted' else '#3a74ab'
        name = html.escape(r['name'])
        width = scale * r['cutoff_ell']
        parts += [f'<text class="name" x="24" y="{y+13}">{name}</text>',
                  f'<rect x="{x0}" y="{y}" width="{width}" height="18" fill="{color}"/>',
                  f'<text class="tick" x="{x0+width+7}" y="{y+14}">{r["cutoff_ell"]}</text>']
        if idx and rows[idx-1]['field_bits'] != r['field_bits']:
            parts += [f'<line x1="24" y1="{y-5}" x2="850" y2="{y-5}" stroke="#b5c5d2"/>']
    parts += [f'<text class="tick" x="24" y="{height-20}">Source: raw.json (SHA-256 4a0df1de…). Orange: omitted; blue: published.</text>', '</svg>']
    OUT.write_text('\n'.join(parts) + '\n')

if __name__ == '__main__':
    main()
