#!/usr/bin/env python3
"""Render the source-bound 80-draw first-fall classification as vector art."""

from collections import Counter
from html import escape
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / 'evidence/draws.json').read_text())

CATEGORIES = [
    ('stable_two', '#245a81', '#ffffff', '2 → 2: both models', 68),
    ('changed_to_three', '#e5a758', '#172b35', '2 → 3: parity correction', 2),
    ('stable_three_nonzero', '#8064a2', '#ffffff', '3 → 3: xR nonzero', 5),
    ('stable_three_zero', '#c45959', '#ffffff', '3 → 3: xR zero', 5),
]


def category(row):
    grades = (row['first_fall'], row['boolean_parity_first_fall'])
    if grades == (2, 2):
        return 'stable_two'
    if grades == (2, 3):
        return 'changed_to_three'
    assert grades == (3, 3)
    return 'stable_three_zero' if row['xR'] == 0 else 'stable_three_nonzero'


def main():
    rows = DATA['draws']
    assert len(rows) == 80
    index = {(r['n'], r['nprime'], r['draw']): r for r in rows}
    assert len(index) == 80
    counts = Counter(category(r) for r in rows)
    assert counts == {item[0]: item[4] for item in CATEGORIES}
    palette = {item[0]: item for item in CATEGORIES}

    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="820" height="480" viewBox="0 0 820 480" role="img" aria-labelledby="title desc">',
        '<title id="title">Archived and Boolean-parity first-fall grades by draw</title>',
        '<desc id="desc">Eight cells of ten deterministic toy draws. Two archived degree-two grades become degree three when duplicate monomials cancel over F2.</desc>',
        '<rect width="820" height="480" fill="#ffffff"/>',
        '<text x="30" y="36" font-family="DejaVu Sans, sans-serif" font-size="18" font-weight="700" fill="#193444">Toy Semaev first fall: archive → Boolean parity</text>',
        '<text x="30" y="58" font-family="DejaVu Sans, sans-serif" font-size="12" fill="#4b6472">Each tile is one seed; grades show archived set union → corrected F₂ multiplication.</text>',
    ]
    x0, y0, w, h, gap = 120, 102, 43, 29, 5
    for draw in range(10):
        x = x0 + draw * (w + gap) + w / 2
        parts.append(f'<text x="{x}" y="88" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="11" fill="#4b6472">s={draw}</text>')
    for row_index, (n, nprime) in enumerate((n, p) for n in (4, 5, 6, 7) for p in (3, 4)):
        y = y0 + row_index * (h + gap)
        parts.append(f'<text x="105" y="{y+19}" text-anchor="end" font-family="DejaVu Sans, sans-serif" font-size="12" fill="#193444">n={n}, n′={nprime}</text>')
        for draw in range(10):
            item = index[(n, nprime, draw)]
            key = category(item)
            _, color, ink, _, _ = palette[key]
            x = x0 + draw * (w + gap)
            tooltip = escape(f'n={n}, nprime={nprime}, s={draw}, xR={item["xR"]}, archived={item["first_fall"]}, Boolean parity={item["boolean_parity_first_fall"]}')
            label = (str(item['first_fall']) if item['first_fall'] == item['boolean_parity_first_fall']
                     else f'{item["first_fall"]}→{item["boolean_parity_first_fall"]}')
            size = 12 if key == 'changed_to_three' else 15
            parts.append(f'<g><title>{tooltip}</title><rect x="{x}" y="{y}" width="{w}" height="{h}" rx="4" fill="{color}"/><text x="{x+w/2}" y="{y+20}" text-anchor="middle" font-family="DejaVu Sans, sans-serif" font-size="{size}" font-weight="700" fill="{ink}">{label}</text></g>')
    parts.extend([
        '<text x="610" y="95" font-family="DejaVu Sans, sans-serif" font-size="13" font-weight="700" fill="#193444">Verified transitions</text>',
    ])
    for i, (_, color, _, label, count) in enumerate(CATEGORIES):
        y = 111 + i * 50
        parts.extend([
            f'<rect x="610" y="{y}" width="20" height="20" rx="3" fill="{color}"/>',
            f'<text x="639" y="{y+15}" font-family="DejaVu Sans, sans-serif" font-size="11" fill="#193444">{escape(label)}</text>',
            f'<text x="639" y="{y+31}" font-family="DejaVu Sans, sans-serif" font-size="11" fill="#4b6472">{count} draws</text>',
        ])
    parts.extend([
        '<line x1="30" y1="401" x2="790" y2="401" stroke="#c8d6dd"/>',
        '<text x="30" y="423" font-family="DejaVu Sans, sans-serif" font-size="12" fill="#193444">Corrected first fall: 68 at degree two, 12 at degree three; seven degree-three targets are nonzero.</text>',
        '<text x="30" y="445" font-family="DejaVu Sans, sans-serif" font-size="10" fill="#4b6472">Source: evidence/draws.json; n=4..7, n′=3,4, ten seeds per cell. Validation data, not a timing or attack-cost plot.</text>',
        '</svg>',
    ])
    svg = '\n'.join(parts) + '\n'
    (HERE / 'draws.svg').write_text(svg)

    import pymupdf
    figure = pymupdf.open(stream=svg.encode(), filetype='svg')
    (HERE / 'draws.pdf').write_bytes(figure.convert_to_pdf())
    print('rendered draws.svg and draws.pdf; counts:', dict(counts))


if __name__ == '__main__':
    main()
