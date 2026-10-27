"""Render source-reported chained m=3 degree-four closure counts.

Values are transcribed from crypto commit d51b908a, research/
dreg_closure_scale_20261016/RESULTS.md, table "The measurement".
This script runs no solver and makes no interpolation.
"""

from pathlib import Path

CELLS = [(16, 6, 4, 4), (18, 6, 4, 4), (19, 7, 0, 4), (21, 7, 0, 4)]
OUT = Path(__file__).with_name("figure.svg")

parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="340" viewBox="0 0 900 340">',
    '<rect width="900" height="340" fill="#fff"/>',
    '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#17243a} .small{font-size:15px} .label{font-size:18px} .title{font-size:22px;font-weight:700}</style>',
    '<text x="40" y="37" class="title">Chained S3, random subspaces: degree-4 refutations</text>',
    '<text x="40" y="65" class="small">m=3; four source-checked unsatisfiable draws per cell</text>',
    '<line x1="210" y1="94" x2="650" y2="94" stroke="#9aa9bb"/>',
    '<line x1="210" y1="94" x2="210" y2="287" stroke="#9aa9bb"/>',
    '<line x1="650" y1="94" x2="650" y2="287" stroke="#9aa9bb"/>',
    '<text x="201" y="84" class="small">0</text>',
    '<text x="637" y="84" class="small">4</text>',
]
for i, (n, ell, refuted, total) in enumerate(CELLS):
    y = 120 + i * 46
    width = 110 * refuted
    parts.extend(
        [
            f'<text x="40" y="{y + 23}" class="label">GF(2^{n}), ℓ={ell}</text>',
            f'<rect x="210" y="{y}" width="440" height="30" fill="#e9eef5"/>',
            f'<rect x="210" y="{y}" width="{width}" height="30" fill="#276b8d"/>',
            f'<text x="675" y="{y + 23}" class="label">{refuted}/{total}</text>',
        ]
    )
parts.extend(
    [
        '<text x="40" y="315" class="small">Source: crypto d51b908a, run-20261016T1705Z; n and ℓ change together.</text>',
        '</svg>',
    ]
)
OUT.write_text("\n".join(parts) + "\n", encoding="utf-8")
