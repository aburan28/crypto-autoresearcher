"""Render grade changes in the 200 archived support-matched null controls."""

import json
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "null-distribution-evidence.json").read_text())
if len(DATA["draws"]) != 200:
    raise RuntimeError("expected 200 frozen matched nulls")


def main():
    selected = DATA["selected_first_positive"]
    closed = DATA["closed_first_positive"]
    transitions = {(entry["selected"], entry["closed"]): entry["count"]
                   for entry in DATA["transitions"]}
    if selected != {"2": 13, "3": 111, "4": 76} or \
            closed != {"2": 1, "3": 117, "4": 82}:
        raise RuntimeError("matched-null grade counts changed")
    if transitions != {(2, 2): 1, (2, 3): 12, (3, 3): 105,
                       (3, 4): 6, (4, 4): 76}:
        raise RuntimeError("matched-null grade transitions changed")
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="920" height="370" viewBox="0 0 920 370" role="img" aria-labelledby="title desc">',
        '<title id="title">Matched-null Boolean quotient grade changes</title>',
        '<desc id="desc">Among 200 frozen support-matched nulls, selected direct rows give first-positive degree counts 13, 111, 76 at degrees two, three, four. The defined Boolean quotient closure gives 1, 117, 82. Twelve nulls shift from degree two to three and six from three to four.</desc>',
        '<style>text{font-family:DejaVu Sans,sans-serif;fill:#193444}.title{font-size:18px;font-weight:700}.head{font-size:13px;font-weight:700}.label,.number{font-size:11px}.note{font-size:10px;fill:#4b6472}</style>',
        '<rect width="920" height="370" fill="#fff"/>',
        '<text x="25" y="34" class="title">200 matched nulls: quotient closure changes first-positive degrees</text>',
        '<text x="25" y="56" class="note">Archived support profiles and equation hashes verified; these are the original controls, not new draws.</text>',
        '<text x="25" y="91" class="head">First positive degree</text>',
        '<rect x="25" y="105" width="11" height="11" fill="#245a81"/><text x="41" y="115" class="note">selected direct rows</text>',
        '<rect x="164" y="105" width="11" height="11" fill="#c87539"/><text x="180" y="115" class="note">closed Boolean quotient</text>',
        '<line x1="485" y1="82" x2="485" y2="297" stroke="#c8d6dd"/>',
        '<text x="512" y="91" class="head">Draw-by-draw transitions</text>',
    ]
    for index, degree in enumerate((2, 3, 4)):
        y = 135 + 55 * index
        parts.append(f'<text x="25" y="{y+18}" class="label">degree {degree}</text>')
        for offset, color, value in ((0, "#245a81", selected[str(degree)]),
                                     (19, "#c87539", closed[str(degree)])):
            width = value * 2.5
            parts.append(f'<rect x="104" y="{y+offset}" width="{width:.1f}" height="15" rx="3" fill="{color}"/>')
            parts.append(f'<text x="{110+width:.1f}" y="{y+offset+12}" class="number">{value}</text>')
    for index, (label, value, color) in enumerate((
            ("2 → 3", transitions[(2, 3)], "#a65d54"),
            ("3 → 4", transitions[(3, 4)], "#a65d54"),
            ("unchanged", transitions[(2, 2)] + transitions[(3, 3)] +
             transitions[(4, 4)], "#43818e"))):
        y = 128 + 53 * index
        width = value * 1.3
        parts.append(f'<text x="512" y="{y+13}" class="label">{label}</text>')
        parts.append(f'<rect x="603" y="{y}" width="{width:.1f}" height="17" rx="3" fill="{color}"/>')
        parts.append(f'<text x="{610+width:.1f}" y="{y+13}" class="number">{value}</text>')
    parts += [
        '<line x1="25" y1="301" x2="893" y2="301" stroke="#c8d6dd"/>',
        '<text x="25" y="324" class="note">Selected rows are outside the specified quotient closure in 69 nulls at D2 and 23 at D3.</text>',
        '<text x="25" y="343" class="note">Finite toy controls only; no polynomial-ring first-fall theorem, security conclusion, or performance inference.</text>',
        '</svg>',
    ]
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    (HERE / "null-closure-distribution.svg").write_text(svg)


if __name__ == "__main__":
    main()
