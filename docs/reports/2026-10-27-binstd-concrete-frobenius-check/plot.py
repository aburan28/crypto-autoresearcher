#!/usr/bin/env python3
"""Render the finite BINSTD factor-kernel dimensions from certificate.json."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
c = json.loads((HERE / 'certificate.json').read_text())
d = c['factor_kernel_dimensions']
if [d[str(p)] for p in (3, 313, 471)] != [1, 8, 8]:
    raise ValueError('kernel dimensions differ')
if c['normal_basis_orbit_rank'] != 17:
    raise ValueError('normal orbit rank differs')
if c['factor_degree_subset_sums'] != [0, 1, 8, 9, 16, 17]:
    raise ValueError('subset sums differ')
widths = [40 * d[str(p)] for p in (3, 313, 471)]
x0 = 76
parts = []
for w, color, label in zip(widths, ('#116b77', '#357eb0', '#934aa3'), ('1', 'factor8a  (8)', 'factor8b  (8)')):
    parts.append(f'<rect x="{x0}" y="112" width="{w}" height="70" rx="8" fill="{color}"/>')
    parts.append(f'<text x="{x0+w/2}" y="153" text-anchor="middle" fill="white" font-size="17" font-family="sans-serif">{label}</text>')
    x0 += w
badges = []
for i, value in enumerate(c['factor_degree_subset_sums']):
    x = 190 + i * 95
    badges.append(f'<rect x="{x}" y="238" width="64" height="38" rx="11" fill="#edf1f4" stroke="#54717a"/>')
    badges.append(f'<text x="{x+32}" y="263" text-anchor="middle" fill="#203b46" font-size="19" font-family="sans-serif">{value}</text>')
svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="870" height="350" viewBox="0 0 870 350">
<rect width="870" height="350" fill="white"/>
<text x="435" y="39" text-anchor="middle" font-size="23" font-weight="bold" font-family="sans-serif" fill="#173744">Archived BINSTD field: finite Frobenius certificate</text>
<text x="435" y="69" text-anchor="middle" font-size="15" font-family="sans-serif" fill="#385663">Normal orbit rank 17, Frobenius order 17; kernel dimensions sum to 17</text>
<text x="76" y="101" font-size="14" font-family="sans-serif" fill="#385663">Factor kernels in the 17-dimensional bitmask field</text>
''' + '\n'.join(parts) + '''
<text x="96" y="206" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#385663">X+1</text>
<text x="755" y="206" text-anchor="end" font-size="14" font-family="sans-serif" fill="#385663">1 + 8 + 8 = 17</text>
<text x="435" y="225" text-anchor="middle" font-size="14" font-family="sans-serif" fill="#385663">Degree subset sums</text>
''' + '\n'.join(badges) + '''
<text x="435" y="318" text-anchor="middle" font-size="12" font-family="sans-serif" fill="#647781">131,072 values compared with the archived squaring code. Lean classification and yields remain open.</text>
</svg>
'''
(HERE / 'factor-kernels.svg').write_text(svg)
