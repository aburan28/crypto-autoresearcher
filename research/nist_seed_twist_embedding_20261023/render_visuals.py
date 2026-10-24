#!/usr/bin/env python3
"""Render the retained chart and inference diagram from analysis.json."""
import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "analysis.json").read_text())
rows = data["rows"]
colors = {"published": "#2458a6", "skipped": "#d27018"}
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="800" viewBox="0 0 1100 800">',
         '<rect width="1100" height="800" fill="white"/>',
         '<text x="30" y="35" font-family="sans-serif" font-size="20" font-weight="bold">Twist subgroup embedding degree: all 21 curves have k &gt; 1000</text>',
         '<text x="30" y="60" font-family="sans-serif" font-size="13">Each bar is the largest certified prime factor of the exact quadratic-twist order; 25 factors ≥ 80 bits were screened.</text>']
for x in (0, 100, 200, 300, 400, 500):
    sx = 260 + x * 1.3
    parts += [f'<line x1="{sx}" y1="80" x2="{sx}" y2="733" stroke="#dddddd"/>',
              f'<text x="{sx}" y="755" text-anchor="middle" font-family="sans-serif" font-size="11">{x}</text>']
for i, row in enumerate(rows):
    y = 91 + i * 30
    w = row["largest_factor_bits"] * 1.3
    parts += [f'<text x="250" y="{y+14}" text-anchor="end" font-family="sans-serif" font-size="12">{escape(row["name"])}</text>',
              f'<rect x="260" y="{y}" width="{w}" height="20" fill="{colors[row["label"]]}"/>',
              f'<text x="{268+w}" y="{y+14}" font-family="sans-serif" font-size="11">{row["largest_factor_bits"]} bits; k &gt; 1000</text>']
parts += ['<text x="585" y="782" text-anchor="middle" font-family="sans-serif" font-size="13">Largest twist prime factor (bits)</text>',
          '<rect x="900" y="45" width="14" height="12" fill="#2458a6"/><text x="919" y="56" font-family="sans-serif" font-size="12">published</text>',
          '<rect x="900" y="64" width="14" height="12" fill="#d27018"/><text x="919" y="75" font-family="sans-serif" font-size="12">skipped</text>',
          '</svg>']
(HERE / "twist_embedding.svg").write_text("\n".join(parts) + "\n")

dot = '''digraph inference {
  graph [rankdir=LR, bgcolor="white", fontname="Helvetica", label="Quadratic-twist pairing screen: exact arithmetic vs unproved history"];
  node [shape=box, style="rounded,filled", fillcolor="#eef4fb", fontname="Helvetica"];
  archive [label="21 exact curve records\\n11 omitted + 10 published"];
  factors [label="25 certified twist primes ≥ 2^80"];
  screen [label="Direct modular test\\nno k ≤ 1000 hits"];
  premise [label="Original program evaluated all 11\\nand rejected them for a weakness", fillcolor="#fff2df"];
  history [label="Original rejection criterion\\nunknown", fillcolor="#fff2df"];
  attack [label="Twist-input attack requires\\nprotocol and oracle details", fillcolor="#fff2df"];
  archive -> factors -> screen;
  premise -> history [style=dashed, label="stipulated"];
  screen -> history [style=dashed, label="does not identify"];
  screen -> attack [style=dashed, label="does not establish"];
}'''
(HERE / "inference.dot").write_text(dot + "\n")
