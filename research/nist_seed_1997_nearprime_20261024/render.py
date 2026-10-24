#!/usr/bin/env python3
"""Render exact source-bound lower-bound counts as an SVG."""

import json
from pathlib import Path

HERE=Path(__file__).resolve().parent
data=json.loads((HERE/'runs/positive-20261024T022524Z/analysis.json').read_text())['streams']
order=['prime192v2','prime239v3','P-224','P-256','P-384','P-521']
names={'prime192v2':'192-bit shared','prime239v3':'239-bit shared','P-224':'P-224','P-256':'P-256','P-384':'P-384','P-521':'P-521'}
max_total=max(data[k]['nearprime_1997_positions'] for k in order)
left,width,top,step,height=180,740,78,67,30
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1050" height="610" viewBox="0 0 1050 610">',
     '<rect width="1050" height="610" fill="white"/>',
     '<text x="24" y="30" font-family="sans-serif" font-size="22" font-weight="bold">Confirmed 1997 near-prime positions in the retained positive-order set</text>',
     '<text x="24" y="53" font-family="sans-serif" font-size="13">Exact lower-bound counts; l_max = 255; corrected run positive-20261024T022524Z; 99 point certificates.</text>']
for i,k in enumerate(order):
    y=top+i*step
    full=data[k]['prime_full_order_positions']
    extra=data[k]['nearprime_1997_positions']-full
    w1=full*width/max_total;w2=extra*width/max_total
    svg.append(f'<text x="24" y="{y+21}" font-family="sans-serif" font-size="16">{names[k]}</text>')
    svg.append(f'<rect x="{left}" y="{y}" width="{w1:.2f}" height="{height}" fill="#3d7bb6"/>')
    if w2:svg.append(f'<rect x="{left+w1:.2f}" y="{y}" width="{w2:.2f}" height="{height}" fill="#e18a36"/>')
    if w1>25:svg.append(f'<text x="{left+w1/2:.2f}" y="{y+21}" font-family="sans-serif" font-size="15" text-anchor="middle" fill="white">{full}</text>')
    if w2>25:svg.append(f'<text x="{left+w1+w2/2:.2f}" y="{y+21}" font-family="sans-serif" font-size="15" text-anchor="middle" fill="white">{extra}</text>')
    svg.append(f'<text x="{left+w1+w2+8:.2f}" y="{y+21}" font-family="sans-serif" font-size="16">{full+extra}</text>')
y=top+step*len(order)+25
svg.extend([f'<rect x="32" y="{y}" width="17" height="17" fill="#3d7bb6"/>',
            f'<text x="56" y="{y+14}" font-family="sans-serif" font-size="14">69 prime full-order positions</text>',
            f'<rect x="350" y="{y}" width="17" height="17" fill="#e18a36"/>',
            f'<text x="374" y="{y+14}" font-family="sans-serif" font-size="14">30 additional smooth-cofactor positions</text>',
            f'<text x="24" y="{y+52}" font-family="sans-serif" font-size="13">10,083 seeded positions have censored exact orders on eligible roots; they are not counted as failures.</text>',
            '</svg>'])
(HERE/'nearprime_counts.svg').write_text('\n'.join(svg)+'\n')
