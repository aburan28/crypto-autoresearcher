#!/usr/bin/env python3
"""Render the two recorded positive-call wall times; performs no solver work."""

import json
from pathlib import Path
from xml.sax.saxutils import escape


HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "plot-data.json").read_text())
assert len(data["values"]) == 2
assert all(value["status"] == "wall_censored" and value["n"] == 1 for value in data["values"])

width, height = 880, 370
left, right = 220, 820
scale = (right - left) / 320
ticks = (0, 100, 200, 300)
parts = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="Two positive solver calls each reached the 300-second wall cap">',
    '<rect width="880" height="370" fill="#ffffff"/>',
    '<text x="40" y="42" font-family="Arial,sans-serif" font-size="21" font-weight="bold" fill="#162536">Positive controls: solver process wall time</text>',
    '<text x="40" y="69" font-family="Arial,sans-serif" font-size="13" fill="#526171">RUN-ICPERF-712e85 · one call per base · both wall censored</text>',
]
for tick in ticks:
    x = left + scale * tick
    parts.extend([
        f'<line x1="{x:.2f}" y1="100" x2="{x:.2f}" y2="288" stroke="#d9e0e8"/>',
        f'<text x="{x:.2f}" y="311" text-anchor="middle" font-family="Arial,sans-serif" font-size="13" fill="#35485b">{tick}</text>',
    ])
for index, row in enumerate(data["values"]):
    y = 126 + index * 91
    bar_width = scale * row["seconds"]
    parts.extend([
        f'<text x="{left - 14}" y="{y + 24}" text-anchor="end" font-family="Arial,sans-serif" font-size="15" fill="#162536">{escape(row["base"])}</text>',
        f'<rect x="{left}" y="{y}" width="{bar_width:.3f}" height="38" rx="4" fill="{("#23678b", "#568c69")[index]}"/>',
        f'<text x="{left + bar_width - 8:.2f}" y="{y + 24}" text-anchor="end" font-family="Arial,sans-serif" font-size="14" font-weight="bold" fill="#ffffff">{row["seconds"]:.3f} s</text>',
        f'<text x="{left + bar_width + 12:.2f}" y="{y + 24}" font-family="Arial,sans-serif" font-size="12" fill="#526171">n=1</text>',
    ])
cap_x = left + scale * data["call_cap_seconds"]
parts.extend([
    f'<line x1="{cap_x:.2f}" y1="103" x2="{cap_x:.2f}" y2="270" stroke="#b63b42" stroke-width="2" stroke-dasharray="5 4"/>',
    f'<text x="{cap_x - 4:.2f}" y="98" text-anchor="end" font-family="Arial,sans-serif" font-size="12" fill="#9e3038">300 s cap</text>',
    '<text x="520" y="341" text-anchor="middle" font-family="Arial,sans-serif" font-size="14" fill="#35485b">Measured solver process wall time (seconds)</text>',
    '<text x="40" y="362" font-family="Arial,sans-serif" font-size="11" fill="#526171">Censoring is an observation about the cap; the bars do not imply relation absence or solver exhaustion.</text>',
    '</svg>',
])
(HERE / "diagram.svg").write_text("\n".join(parts) + "\n")
