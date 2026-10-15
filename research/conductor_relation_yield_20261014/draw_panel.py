"""Editable source for the prospective curve-panel diagram (no data plotted)."""
from pathlib import Path

OUT = Path(__file__).with_name("panel.svg")
svg = '''<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="410" viewBox="0 0 1000 410">
<rect width="1000" height="410" fill="white"/>
<style>text{font-family:Arial,Helvetica,sans-serif;fill:#17202a}.h{font-size:20px;font-weight:700}.t{font-size:15px}.s{font-size:13px}.box{fill:#f4f8fc;stroke:#557491;stroke-width:2}.edge{stroke:#176aa5;stroke-width:3}.dash{stroke-dasharray:7 5;stroke:#a75b21;stroke-width:2}</style>
<text x="30" y="32" class="h">Prospective arity-3 native relation-yield panel</text>
<text x="30" y="62" class="t">P29: F₃₂₀₀₉₂₀₃₇, r=320091991, D_K=-19, fπ=8209</text>
<rect x="50" y="88" width="300" height="80" rx="9" class="box"/><text x="68" y="116" class="t">Crater fE=1</text><text x="68" y="141" class="s">a=254576120, b=276414759</text>
<rect x="650" y="88" width="300" height="80" rx="9" class="box"/><text x="668" y="116" class="t">Floor fE=8209</text><text x="668" y="141" class="s">a=101186781, b=57596093</text>
<line x1="350" y1="128" x2="650" y2="128" class="edge"/><text x="406" y="111" class="s">certified isogeny class; degree 8209</text>
<text x="50" y="192" class="s">Secondary P29 floors: E2 (a=64570613, b=54195252); E3 (a=234001141, b=79995391)</text>
<text x="30" y="236" class="t">P37: F₈₁₆₄₀₅₁₂₁₃₇, r=81640511861, D_K=-19, fπ=131101</text>
<rect x="50" y="258" width="300" height="80" rx="9" class="box"/><text x="68" y="286" class="t">Crater fE=1</text><text x="68" y="311" class="s">a=6206588639, b=31351229805</text>
<rect x="650" y="258" width="300" height="80" rx="9" class="box"/><text x="668" y="286" class="t">Floor fE=131101</text><text x="668" y="311" class="s">a=6064550680, b=68678790390</text>
<line x1="350" y1="298" x2="650" y2="298" class="edge"/><text x="398" y="281" class="s">certified isogeny class; degree 131101</text>
<text x="30" y="385" class="s">Native-base contrasts; u=2 coordinate sensitivity. Point-map evaluation/dual not supplied.</text>
</svg>'''
OUT.write_text(svg, encoding="utf-8")
