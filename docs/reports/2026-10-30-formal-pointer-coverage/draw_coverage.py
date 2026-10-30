#!/usr/bin/env python3
"""Render the two syntactic pointer counts in inventory.json as SVG and TikZ."""
import json
from pathlib import Path

root = Path(__file__).resolve().parent
x = json.loads((root / "inventory.json").read_text())
rows = [("Experiment directories", x["experiment_ids_with_exact_pointer"], x["experiment_directories"]),
        ("Registered formal targets", x["targets_with_exact_pointer"], x["formal_targets"])]
parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="880" height="280" viewBox="0 0 880 280">',
         '<rect width="880" height="280" fill="white"/>',
         '<text x="32" y="35" font-family="sans-serif" font-size="20">Exact EXP-ID pointer coverage</text>',
         '<text x="32" y="58" font-family="sans-serif" font-size="12">Syntactic links only; this is not proof or experiment validation.</text>']
tikz = [r'\begin{tikzpicture}[x=0.01cm,y=0.01cm]',
        r'\node[anchor=west,font=\bfseries] at (0,380) {Exact EXP-ID pointer coverage};',
        r'\node[anchor=west,font=\small] at (0,320) {Syntactic links only; no proof or run validation.};']
for i, (label, linked, total) in enumerate(rows):
    y = 104 + i * 100
    width = 650 * linked / total
    pct = 100 * linked / total
    parts += [f'<text x="32" y="{y}" font-family="sans-serif" font-size="15">{label}: {linked} / {total} ({pct:.2f}%)</text>',
              f'<rect x="32" y="{y+13}" width="650" height="22" fill="#e5e7eb"/>',
              f'<rect x="32" y="{y+13}" width="{width:.3f}" height="22" fill="#165d8a"/>',
              f'<text x="695" y="{y+30}" font-family="sans-serif" font-size="12">{total-linked} without pointer</text>']
    ty = 165 - i * 115
    tikz += [rf'\node[anchor=west] at (0,{ty+50}) {{{label}: {linked} / {total} ({pct:.2f}\%)}};',
             rf'\fill[gray!20] (0,{ty}) rectangle (650,{ty+22});',
             rf'\fill[blue!65!black] (0,{ty}) rectangle ({width:.3f},{ty+22});',
             rf'\node[anchor=west,font=\scriptsize] at (665,{ty+11}) {{{total-linked} without pointer}};']
parts.append('</svg>')
tikz.append(r'\end{tikzpicture}')
(root / "coverage.svg").write_text("\n".join(parts) + "\n")
(root / "coverage.tikz").write_text("\n".join(tikz) + "\n")
