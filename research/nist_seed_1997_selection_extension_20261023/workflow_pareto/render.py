#!/usr/bin/env python3
"""Render the four frozen pair-counts from the archived analysis JSON."""
import html
import json
from pathlib import Path

here = Path(__file__).resolve().parent
data = json.loads((here/'analysis.json').read_text())
summary = data['summary']
assert summary['earlier_omission_pairs'] == 16
items = [
    ('n−1 factor bits', 'minus_largest_prime_at_crossing_bits', '#bc7136'),
    ('n−1 components', 'minus_minimum_prime_power_components', '#bc7136'),
    ('n+1 factor bits (control)', 'plus_largest_prime_at_crossing_bits', '#6e92ae'),
    ('n+1 components (control)', 'plus_minimum_prime_power_components', '#6e92ae'),
]
out = ['<svg xmlns="http://www.w3.org/2000/svg" width="860" height="340" viewBox="0 0 860 340">',
       '<rect width="860" height="340" fill="white"/>',
       '<style>text{font-family:Arial,sans-serif;fill:#26394a}.title{font-size:20px;font-weight:bold}.label{font-size:15px}.tick{font-size:13px}</style>',
       '<text class="title" x="20" y="32">Earlier omission dominates later published curve</text>',
       '<text class="tick" x="20" y="55">Same-field earlier pairs, n = 16; smaller values in both cost proxies are preferred</text>']
x0=300
scale=27
for i,(label,key,color) in enumerate(items):
    count=summary[key]['earlier_omission_dominates_published']
    y=85+i*52
    out += [f'<text class="label" x="20" y="{y+19}">{html.escape(label)}</text>',
            f'<rect x="{x0}" y="{y}" width="{count*scale}" height="27" fill="{color}"/>',
            f'<text class="label" x="{x0+count*scale+9}" y="{y+20}">{count}/16</text>']
for tick in [0,4,8,12,16]:
    x=x0+tick*scale
    out += [f'<line x1="{x}" y1="70" x2="{x}" y2="290" stroke="#d8e0e9"/>',
            f'<text class="tick" x="{x}" y="310" text-anchor="middle">{tick}</text>']
out += ['<text class="tick" x="20" y="332">Exact pair rows: analysis.json. Blue controls use n+1 and are not certificate proxies for n.</text>', '</svg>']
(here/'pair_counts.svg').write_text('\n'.join(out)+'\n')
