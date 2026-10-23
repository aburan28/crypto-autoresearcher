"""Render the frozen same-width torsion-base control preparation counts."""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
weighted = json.loads((ROOT / "research/icperf_binary_torsion_k11_weighted_20261017/base.json").read_text())
control = json.loads((ROOT / "research/icperf_binary_torsion_k11_local_control_20261017/base.json").read_text())
scan = next(row for row in weighted["candidate_scans"] if row["offset"] == weighted["selected_offset"])
local = control["candidate_scans"][0]
assert scan["projected_columns"] == local["projected_columns"] == 316
assert scan["raw_representatives"] == local["raw_representatives"] == 632
assert scan["hamming_cut_attempts"] == 1276
assert 2 * control["full_block"]["pairs_attempted"] == 2048
candidate = {row[0] for row in scan["selected_representatives"]}
random = {row[0] for row in local["selected_representatives"]}
assert len(candidate & random) == 194

bars = [("Weighted cut", 1276, "#14965a"), ("Local random", 2048, "#2563eb")]
lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="920" height="375" viewBox="0 0 920 375">',
         '<rect width="920" height="375" fill="white"/>',
         '<style>text{font-family:Arial,sans-serif;fill:#172033}.title{font-size:25px;font-weight:700}.label{font-size:17px}.small{font-size:14px;fill:#475569}</style>',
         '<text class="title" x="55" y="45">Same-width binary factor-base control</text>',
         '<text class="small" x="55" y="73">One GF(2^61) curve; both bases use 11-bit coordinates and 316 projected columns.</text>']
for i, (label, attempts, color) in enumerate(bars):
    y = 122 + i * 92
    width = round(470 * attempts / 2048)
    lines += [f'<text class="label" x="55" y="{y + 24}">{label}</text>',
              f'<rect x="242" y="{y}" width="{width}" height="37" rx="4" fill="{color}"/>',
              f'<text class="label" x="{255 + width}" y="{y + 25}">{attempts:,} attempts</text>']
lines += ['<text class="small" x="55" y="320">632 accepted raw coordinates each; 194 of 316 projected columns overlap.</text>',
          '<text class="small" x="55" y="346">Input preparation counts only; no relation, solver, degree, rank or ECDLP timing.</text>',
          '</svg>']
(Path(__file__).with_name("2026-10-17-binary-torsion-k11-local-control.svg")).write_text("\n".join(lines) + "\n")
