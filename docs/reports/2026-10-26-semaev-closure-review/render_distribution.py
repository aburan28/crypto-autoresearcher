"""Render the source-bound 80-draw Boolean quotient comparison."""

import json
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "distribution-evidence.json").read_text())
ROWS = DATA["draws"]
if len(ROWS) != 80:
    raise RuntimeError("distribution must contain all 80 archived draws")


def count_changed(bound, field):
    key = str(bound)
    return sum(row["selected"][key][field] != row["closed"][key][field]
               for row in ROWS)


def count_outside(bound):
    return sum(row["closed"][str(bound)]["direct_outside_closed_dimension"] > 0
               for row in ROWS)


def bar(parts, x, y, value, width_scale, color, label, maxwidth=None):
    parts.append(f'<text x="{x}" y="{y+12}" class="label">{label}</text>')
    bx = x + 112
    width = value * width_scale
    if maxwidth is not None and width > maxwidth:
        raise RuntimeError("bar exceeds its panel")
    parts.append(f'<rect x="{bx}" y="{y}" width="{max(width, 1):.1f}" height="16" rx="3" fill="{color}"/>')
    parts.append(f'<text x="{bx+width+7:.1f}" y="{y+13}" class="number">{value}</text>')


def main():
    selected = DATA["selected_first_positive"]
    closed = DATA["closed_first_positive"]
    if selected != {"2": 68, "3": 12} or closed != selected:
        raise RuntimeError("first-positive degree counts changed")
    rank_changed = [count_changed(d, "rank") for d in (1, 2, 3)]
    new_changed = [count_changed(d, "new_falls") for d in (2, 3)]
    outside = [count_outside(d) for d in (1, 2, 3)]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="410" viewBox="0 0 1100 410" role="img" aria-labelledby="title desc">',
        '<title id="title">First positive degree agrees, but Semaev quotient dimensions differ</title>',
        '<desc id="desc">All 80 archived Semaev draws have first positive degree two in 68 cases and degree three in 12 under both selected rows and Boolean quotient closure. Ranks differ in 2, 68, and 74 draws at degrees one, two, and three. New-class counts differ in 23 and 77 draws at degrees two and three.</desc>',
        '<style>text{font-family:DejaVu Sans,sans-serif;fill:#193444}.title{font-size:20px;font-weight:700}.sub{font-size:12px;fill:#4b6472}.head{font-size:14px;font-weight:700}.label,.number{font-size:12px}.note{font-size:11px;fill:#4b6472}</style>',
        '<rect width="1100" height="410" fill="#fff"/>',
        '<text x="28" y="36" class="title">80 Semaev draws: same first degree, different quotient dimensions</text>',
        '<text x="28" y="59" class="sub">Archived source equations independently re-derived; squarefree Boolean quotient closure through degree 3.</text>',
        '<line x1="365" y1="86" x2="365" y2="343" stroke="#c8d6dd"/>',
        '<line x1="744" y1="86" x2="744" y2="343" stroke="#c8d6dd"/>',
        '<text x="28" y="104" class="head">First positive degree</text>',
        '<text x="390" y="104" class="head">Draws with changed values</text>',
        '<text x="769" y="104" class="head">Selected rows outside closure</text>',
        '<rect x="28" y="120" width="11" height="11" fill="#245a81"/><text x="45" y="130" class="note">selected direct rows</text>',
        '<rect x="184" y="120" width="11" height="11" fill="#c87539"/><text x="201" y="130" class="note">closed Boolean quotient</text>',
    ]
    for index, bound in enumerate((2, 3)):
        y = 158 + 68 * index
        parts.append(f'<text x="28" y="{y+21}" class="label">degree {bound}</text>')
        for offset, color, count in ((0, "#245a81", selected[str(bound)]),
                                     (20, "#c87539", closed[str(bound)])):
            width = count * 2.45
            parts.append(f'<rect x="125" y="{y+offset}" width="{width:.1f}" height="16" rx="3" fill="{color}"/>')
            parts.append(f'<text x="{132+width:.1f}" y="{y+offset+13}" class="number">{count}</text>')
    for index, (label, count) in enumerate(zip(
            ("rank D1", "rank D2", "rank D3", "new D2", "new D3"),
            rank_changed + new_changed)):
        bar(parts, 390, 139 + 36 * index, count, 2.65, "#43818e", label,
            maxwidth=220)
    for index, (bound, count) in enumerate(zip((1, 2, 3), outside)):
        bar(parts, 769, 153 + 54 * index, count, 25, "#a65d54",
            f"degree {bound}", maxwidth=190)
    parts += [
        '<line x1="28" y1="351" x2="1070" y2="351" stroke="#c8d6dd"/>',
        '<text x="28" y="373" class="note">“Outside” counts selected-row spaces that are not contained in the specified degree-budget quotient closure.</text>',
        '<text x="28" y="393" class="note">These finite grades are not a polynomial-ring first-fall theorem, Lean certificate, benchmark, or attack-cost result.</text>',
        '</svg>',
    ]
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    (HERE / "closure-distribution.svg").write_text(svg)


if __name__ == "__main__":
    main()
