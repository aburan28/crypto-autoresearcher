"""Draw the torsion-coordinate input counts and exact two-to-one diagram."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RECORD = ROOT / "research/icperf_binary_torsion_coordinate_20261017/base.json"
OUT = Path(__file__).with_name("2026-10-17-binary-torsion-coordinate.svg")
d = json.loads(RECORD.read_text())
rows = d["candidate_scans"]
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="620" viewBox="0 0 960 620">',
    '<rect width="960" height="620" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#183040}.title{font-size:24px;font-weight:bold}.label{font-size:16px}.small{font-size:13px}</style>',
    '<text x="480" y="34" text-anchor="middle" class="title">Torsion-coordinate affine input on GF(2^61)</text>',
    '<text x="480" y="62" text-anchor="middle" class="label">Each target-blind offset scans 1,024 coordinate values</text>',
    '<line x1="105" y1="390" x2="875" y2="390" stroke="#183040" stroke-width="2"/>',
    '<line x1="105" y1="100" x2="105" y2="390" stroke="#183040" stroke-width="2"/>',
]
for tick in (0, 200, 400, 600):
    y = 390 - tick * 0.45
    parts.append(f'<line x1="105" y1="{y:.1f}" x2="875" y2="{y:.1f}" stroke="#d4dde2"/>')
    parts.append(f'<text x="88" y="{y+5:.1f}" text-anchor="end" class="label">{tick}</text>')
target_y = 390 - d["predeclared_selection"]["target_columns"] * 0.45
parts.append(f'<line x1="105" y1="{target_y:.1f}" x2="875" y2="{target_y:.1f}" stroke="#a64d30" stroke-width="2" stroke-dasharray="7 5"/>')
parts.append('<line x1="660" y1="456" x2="695" y2="456" stroke="#a64d30" stroke-width="2" stroke-dasharray="7 5"/>')
parts.append('<text x="705" y="460" class="small">m=8 default B=287 columns</text>')
for i, row in enumerate(rows):
    x = 145 + i * 180
    for dx, value, fill in ((0, row["raw_representatives"], "#6b93a9"),
                            (65, row["projected_columns"], "#078d66")):
        h = value * 0.45
        parts.append(f'<rect x="{x+dx}" y="{390-h:.1f}" width="51" height="{h:.1f}" fill="{fill}"/>')
        label_y = 390 - h - 8 if dx == 0 else 390 - h + 22
        label_style = '' if dx == 0 else ' style="fill:white;font-weight:bold"'
        parts.append(f'<text x="{x+dx+25}" y="{label_y:.1f}" text-anchor="middle" class="small"{label_style}>{value}</text>')
    parts.append(f'<text x="{x+58}" y="416" text-anchor="middle" class="label">{row["offset"]}</text>')
parts += [
    '<rect x="120" y="446" width="16" height="16" fill="#6b93a9"/><text x="145" y="459" class="small">raw liftable representatives</text>',
    '<rect x="405" y="446" width="16" height="16" fill="#078d66"/><text x="430" y="459" class="small">unique sign-folded [4] columns</text>',
    '<text x="480" y="505" text-anchor="middle" class="label">t  ── +1 ──▶  t+1     |     P  ── +T₂ (up to sign) ──▶  P′</text>',
    '<text x="480" y="540" text-anchor="middle" class="label">[4]P and [4]P′ enter the same sign-folded log column</text>',
    '<text x="480" y="585" text-anchor="middle" class="small">Source: base.json and independent Sage replay. Counts are input preparation only.</text>',
    '</svg>',
]
OUT.write_text("\n".join(parts) + "\n")
