#!/usr/bin/env python3
"""Draw exact counts from the write-once source-bound analysis."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE/'analysis.json').read_text())['streams']
order = ['prime192v2', 'prime239v3', 'P-224', 'P-256', 'P-384', 'P-521']
names = {'prime192v2':'192-bit stream', 'prime239v3':'239-bit stream',
         'P-224':'P-224', 'P-256':'P-256', 'P-384':'P-384', 'P-521':'P-521'}
categories = [('published', '#3d7bb6', 'published'),
              ('retrospective_omissions', '#e18a36', 'named 11'),
              ('order_too_wide_only', '#9b73b7', 'order width'),
              ('opposite_root_only', '#6c9d6f', 'other root')]
max_total = max(data[name]['all_1997_numerically_eligible'] for name in order)
left, width, top, step, bar_h = 175, 780, 75, 68, 27
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="1030" height="620" viewBox="0 0 1030 620">',
       '<rect width="1030" height="620" fill="white"/>',
       '<text x="24" y="30" font-family="sans-serif" font-size="21" font-weight="bold">Prime-order seed positions satisfying the November 1997 numerical checks</text>',
       '<text x="24" y="51" font-family="sans-serif" font-size="13">Six reconstructed streams; exact counts, no sampling uncertainty. Sources: analysis.json and cited 1997 X9.62 draft.</text>']
for i,name in enumerate(order):
    y = top+i*step
    svg.append(f'<text x="24" y="{y+20}" font-family="sans-serif" font-size="16">{names[name]}</text>')
    x=left
    for field,color,_ in categories:
        n=data[name][field]
        w=width*n/max_total
        if n:
            svg.append(f'<rect x="{x:.2f}" y="{y}" width="{w:.2f}" height="{bar_h}" fill="{color}"/>')
            if w>24:svg.append(f'<text x="{x+w/2:.2f}" y="{y+19}" font-family="sans-serif" font-size="15" text-anchor="middle" fill="white">{n}</text>')
        x+=w
    svg.append(f'<text x="{x+8:.2f}" y="{y+20}" font-family="sans-serif" font-size="15">{data[name]["all_1997_numerically_eligible"]}</text>')
y=top+step*len(order)+20
svg.append(f'<text x="24" y="{y}" font-family="sans-serif" font-size="14">Total: 69 positions = 10 published + 11 named omissions + 17 wider orders + 31 other-root-only.</text>')
ly=y+45
x=40
for _,color,label in categories:
    svg.append(f'<rect x="{x}" y="{ly}" width="17" height="17" fill="{color}"/>')
    svg.append(f'<text x="{x+24}" y="{ly+14}" font-family="sans-serif" font-size="14">{label}</text>')
    x+=215
svg.append(f'<text x="24" y="{ly+48}" font-family="sans-serif" font-size="12">Historical visitation and discretionary choices are unknown. Categories depend on the reconstructed stream and certified census.</text>')
svg.append('</svg>')
(HERE/'acceptance_counts.svg').write_text('\n'.join(svg)+'\n')
