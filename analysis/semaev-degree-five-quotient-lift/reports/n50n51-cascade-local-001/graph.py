"""Render recorded D3 codimension lower bounds for the 18 fixed inputs."""
import json
from pathlib import Path

root = Path(__file__).parent
rows = json.loads((root / 'rows.json').read_text())
width, height = 1540, 630
left, top, bottom = 90, 76, 505
bar_w, gap = 46, 34
scale = (bottom - top) / 18000
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<style>text{font-family:Arial,sans-serif;fill:#223046}.title{font-size:22px;font-weight:bold}.tick{font-size:15px}.label{font-size:12px}.note{font-size:14px}</style>',
         '<text x="90" y="35" class="title">Checked D3 codimension lower bounds, original n50/n51 inputs</text>']
for tick in (0, 5000, 10000, 15000):
    y = bottom - tick * scale
    parts += [f'<line x1="{left}" y1="{y:.1f}" x2="{width-20}" y2="{y:.1f}" stroke="#d8dde7"/>',
              f'<text x="{left-12}" y="{y+5:.1f}" text-anchor="end" class="tick">{tick:,}</text>']
for i, row in enumerate(rows):
    x = left + 19 + i * (bar_w + gap)
    value = row['checked_d3_codimension']
    color = '#4e79a7' if row['n'] == 50 else '#e08736'
    if value is None:
        parts += [f'<rect x="{x}" y="{bottom-17}" width="{bar_w}" height="17" fill="#adb5c2"/>',
                  f'<text x="{x+bar_w/2}" y="{bottom-24}" text-anchor="middle" class="label">no cert</text>']
    else:
        y = bottom - value * scale
        parts += [f'<rect x="{x}" y="{y:.1f}" width="{bar_w}" height="{bottom-y:.1f}" fill="{color}"/>',
                  f'<text x="{x+bar_w/2}" y="{y-7:.1f}" text-anchor="middle" class="label">{value:,}</text>']
    short = row['id'].replace('fresh-', '').replace('-D5-cascade01', '')
    parts += [f'<text x="{x+bar_w/2}" y="{bottom+17}" text-anchor="middle" class="label" transform="rotate(55 {x+bar_w/2} {bottom+17})">{short}</text>']
parts += ['<text x="90" y="610" class="note">Blue: n50; orange: n51; grey: D3 producer reported W3_one = 1. Exact named inputs; no uncertainty interval.</text>',
          '</svg>']
(root / 'checked-d3.svg').write_text('\n'.join(parts) + '\n')
