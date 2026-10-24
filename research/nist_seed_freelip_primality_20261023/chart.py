#!/usr/bin/env python3
"""Render observed FreeLIP replay classifications as a small editable SVG."""
import collections
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/freelip-20261023T2014Z/results.json"
rows = json.loads(RUN.read_text())["cases"]
groups = [
    ("Omitted orders", [r for r in rows if r["kind"] == "omitted"]),
    ("Published orders", [r for r in rows if r["kind"] == "published"]),
    ("Controls", [r for r in rows if r["kind"] == "control"]),
]
palette = {"Omitted orders": "#395b8c", "Published orders": "#27836d", "Controls": "#9b713e"}
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="310" viewBox="0 0 760 310">',
         '<rect width="760" height="310" fill="white"/>',
         '<text x="26" y="35" font-family="sans-serif" font-size="20" font-weight="bold">FreeLIP 1.0 replay: expected classifications</text>',
         '<text x="26" y="57" font-family="sans-serif" font-size="12">25 exact inputs, three primality calls each; run freelip-20261023T2014Z</text>']
for i, (label, items) in enumerate(groups):
    y = 92 + i * 61
    count = sum(all(value == r["expected"] for value in r["returns"]) for r in items)
    width = 470 * len(items) / 11
    fill = 470 * count / 11
    parts.extend([
        f'<text x="26" y="{y+16}" font-family="sans-serif" font-size="15">{html.escape(label)}</text>',
        f'<rect x="210" y="{y}" width="{width:.1f}" height="24" fill="#e6e9ed"/>',
        f'<rect x="210" y="{y}" width="{fill:.1f}" height="24" fill="{palette[label]}"/>',
        f'<text x="{220+width:.1f}" y="{y+17}" font-family="sans-serif" font-size="14">{count}/{len(items)}</text>',
    ])
parts.append('<text x="26" y="290" font-family="sans-serif" font-size="12">Bar length = number of inputs; filled part = all three calls matched independent expected classification.</text>')
parts.append('</svg>')
(HERE / "classifications.svg").write_text("\n".join(parts) + "\n")
