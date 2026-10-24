#!/usr/bin/env python3
"""Render the exact generic-j counts from the immutable audit."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = json.loads((HERE / "runs/20261023T2102Z/results.json").read_text())["rows"]
groups = [("Omitted", "omitted", "#b5653b"), ("Published", "published", "#326f91")]
svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="700" height="240" viewBox="0 0 700 240">',
       '<rect width="700" height="240" fill="white"/>',
       '<text x="20" y="34" font-family="sans-serif" font-size="19" font-weight="bold">Rational twist classes of 21 exact curves</text>',
       '<text x="20" y="55" font-family="sans-serif" font-size="12">Generic j: exactly one nontrivial quadratic twist per curve</text>']
for index, (name, key, color) in enumerate(groups):
    subset = [r for r in rows if r["kind"] == key]
    passed = sum(r["j_is_generic"] for r in subset)
    y = 83 + index * 58
    svg += [f'<text x="20" y="{y+20}" font-family="sans-serif" font-size="15">{name}</text>',
            f'<rect x="155" y="{y}" width="440" height="27" fill="#e7e9ec"/>',
            f'<rect x="155" y="{y}" width="{440*passed/11:.1f}" height="27" fill="{color}"/>',
            f'<text x="{165+440*len(subset)/11:.1f}" y="{y+20}" font-family="sans-serif" font-size="15">{passed}/{len(subset)}</text>']
svg += ['<text x="20" y="218" font-family="sans-serif" font-size="12">Source: runs/20261023T2102Z; independent Sage: verification/20261023T2110Z</text>', '</svg>']
(HERE / "counts.svg").write_text("\n".join(svg) + "\n")
