#!/usr/bin/env python3
"""Render the audited parse dispositions as a deterministic vector chart."""

from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "evidence.json").read_text(encoding="utf-8"))
counts = data["counts"]
segments = [
    ("Verified replacement", counts["verified_schema_replacement"], "#207c76"),
    ("Legacy baseline defect", counts["legacy_parse_baseline"], "#cb8a27"),
    ("Unresolved", counts["unresolved"], "#b34845"),
]
total = sum(value for _, value, _ in segments)
if total == 0:
    raise SystemExit("no malformed originals to chart")
left, width = 72, 720
current = left
rects = []
legend = []
for i, (label, value, color) in enumerate(segments):
    span = width * value / total
    if span:
        rects.append(f'<rect x="{current:.2f}" y="128" width="{span:.2f}" '
                     f'height="72" fill="{color}"/>')
        rects.append(f'<text x="{current + span / 2:.2f}" y="173" '
                     f'text-anchor="middle" class="inside">{value}</text>')
    current += span
    legend.append(f'<rect x="72" y="{244 + 37*i}" width="19" height="19" '
                  f'fill="{color}"/><text x="105" y="{260 + 37*i}" '
                  f'class="legend">{label}: {value}</text>')
svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="864" height="420" viewBox="0 0 864 420">
<style>text{{font-family:DejaVu Sans,Arial,sans-serif;fill:#1e293b}}
.title{{font-size:24px;font-weight:bold}}.sub{{font-size:14px;fill:#475569}}
.inside{{font-size:23px;font-weight:bold;fill:white}}.legend{{font-size:17px}}
.foot{{font-size:13px;fill:#475569}}</style>
<rect width="864" height="420" fill="white"/>
<text x="72" y="50" class="title">Malformed ledger YAML originals by disposition</text>
<text x="72" y="78" class="sub">Exact main {data['source_commit'][:12]} · n={total} · all ledger YAML parsed</text>
<text x="72" y="112" class="sub">Counts describe archive syntax, not research validity or proof coverage.</text>
{''.join(rects)}
{''.join(legend)}
<text x="72" y="380" class="foot">A baseline entry remains a defect. Replacement means SHA, parse, identity and merge-gate routing agree.</text>
</svg>
'''
(HERE / "parse-dispositions.svg").write_text(svg, encoding="utf-8")
print(HERE / "parse-dispositions.svg")
