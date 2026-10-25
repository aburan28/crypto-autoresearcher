#!/usr/bin/env python3
"""Render the finite row-space dimensions from the checked source receipt."""

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
receipt = json.loads((HERE / "evidence/source-binding.json").read_text())
v2 = receipt["degree_two_rank"]
with_witness = receipt["rank_degree_two_plus_witness"]
assert (v2, with_witness) == (11, 12)

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="760" height="310" viewBox="0 0 760 310">
<rect width="760" height="310" fill="#fffdf9"/>
<style>text {{font-family: DejaVu Sans, sans-serif; fill: #17242d}} .muted {{fill: #4e626d; font-size: 15px}} .label {{font-size: 19px}} .num {{font-size: 20px; font-weight: bold}}</style>
<text x="30" y="35" font-size="23" font-weight="bold">One new low-degree direction at degree three</text>
<text x="30" y="61" class="muted">Finite n=4, n'=4, seed 32201, xR=1 Boolean draw</text>
<text x="30" y="119" class="label">Degree-two row space V₂</text>
<rect x="300" y="93" width="{v2 * 30}" height="38" rx="5" fill="#487fa6"/>
<text x="{310 + v2 * 30}" y="120" class="num">{v2}</text>
<text x="30" y="187" class="label">V₂ plus explicit witness</text>
<rect x="300" y="161" width="{v2 * 30}" height="38" rx="5" fill="#487fa6"/>
<rect x="{300 + v2 * 30}" y="161" width="30" height="38" rx="2" fill="#c67b30"/>
<text x="{340 + v2 * 30}" y="188" class="num">{with_witness}</text>
<rect x="300" y="229" width="18" height="18" fill="#487fa6"/><text x="326" y="244" class="muted">existing span</text>
<rect x="470" y="229" width="18" height="18" fill="#c67b30"/><text x="496" y="244" class="muted">new direction</text>
<text x="30" y="283" class="muted">Separator c₈₀ + c₁₉₂: zero on every V₂ row, one on the witness.</text>
</svg>
'''
(HERE / "row-space.svg").write_text(svg)
print(HERE / "row-space.svg")
