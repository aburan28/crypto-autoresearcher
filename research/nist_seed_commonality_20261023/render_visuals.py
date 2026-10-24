#!/usr/bin/env python3
"""Render the bounded 21-curve comparison and its inference boundary as SVG."""

import html
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "analysis.json").read_text())


def text(x, y, value, *, size=16, color="#263445", weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="{weight}" text-anchor="{anchor}" '
            f'font-family="Arial, Helvetica, sans-serif">{html.escape(str(value))}</text>')


def trait_chart():
    rows = DATA["rows"]
    left, right = 390, 1010
    xmin, xmax = 40, 56
    top, step = 138, 26
    height = top + step * len(rows) + 85
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="1340" height="{height}" '
             'viewBox="0 0 1340 ' + str(height) + '">',
             '<rect width="1340" height="100%" fill="#ffffff"/>',
             text(34, 39, "NIST/ANSI seed-block comparison", size=27, weight="bold"),
             text(34, 67, "21 exact seed-level classes · 10 published, 11 passed over", size=17),
             text(34, 105, "Curve / block", size=15, weight="bold"),
             text((left + right) / 2, 105, "Coefficient b bit weight / field bit length", size=15,
                  weight="bold", anchor="middle"),
             text(1110, 105, "Small squared Δ prime", size=15, weight="bold")]
    for tick in (40, 44, 48, 52, 56):
        x = left + (tick - xmin) * (right - left) / (xmax - xmin)
        parts.append(f'<line x1="{x}" y1="120" x2="{x}" y2="{top + step * (len(rows) - 1) + 10}" '
                     'stroke="#e4e8ee" stroke-width="1"/>')
        parts.append(text(x, 122, f"{tick}%", size=13, color="#526073", anchor="middle"))
    prev_field = None
    for i, row in enumerate(rows):
        y = top + i * step
        field = row["field_bits"]
        if field != prev_field and prev_field is not None:
            parts.append(f'<line x1="30" y1="{y-17}" x2="1300" y2="{y-17}" '
                         'stroke="#c9d3dd" stroke-width="1"/>')
        prev_field = field
        color = "#2465aa" if row["label"] == "published" else "#d66a29"
        pct = 100 * row["features"]["b_bit_weight"] / field
        x = left + (pct - xmin) * (right - left) / (xmax - xmin)
        label = (row["name"] if row["label"] == "published"
                 else f"{field}-bit / omitted block {row['ordinal']}")
        parts.append(text(34, y + 5, label, size=14, color=color,
                          weight="bold" if row["label"] == "published" else "normal"))
        parts.append(f'<circle cx="{x:.2f}" cy="{y}" r="6" fill="{color}"/>')
        parts.append(text(x + 11, y + 5, f"{pct:.1f}%", size=13, color=color))
        square = row["delta_small_square_primes_with_local_conductor_valuation"]
        parts.append(text(1184, y + 5, ", ".join(str(v[0]) for v in square) if square else "—",
                          size=14, color="#704b9a" if square else "#8895a3", anchor="middle"))
    foot = top + step * len(rows) + 27
    parts.extend([
        text(34, foot, "Blue: published   Orange: omitted   Δ = t² − 4p; listed primes ℓ ≤ 10,000 have ℓ² | Δ.",
             size=15),
        text(34, foot + 23, "Coefficient weight is an exploratory association; the P-224 omissions include lower weights than published P-224.",
             size=14, color="#526073"),
        '</svg>',
    ])
    (HERE / "traits.svg").write_text("\n".join(parts) + "\n")


def inference_diagram():
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="420" viewBox="0 0 1200 420">',
             '<rect width="1200" height="420" fill="#fff"/>',
             text(38, 46, "What a common hidden weakness would have to explain", size=25, weight="bold")]
    boxes = [
        (45, 92, 260, 94, "Recovered streams", "21 qualifying seed blocks"),
        (363, 92, 230, 94, "Observed labels", "10 published / 11 omitted"),
        (652, 92, 260, 94, "Fixed feature family", "21 features; no exact split"),
        (652, 264, 260, 94, "Unknown weakness W", "mechanism and cost missing"),
    ]
    for x, y, w, h, title, subtitle in boxes:
        fill = "#eef4fa" if title != "Unknown weakness W" else "#fff5e8"
        stroke = "#8ca6c2" if title != "Unknown weakness W" else "#cf8a45"
        parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" '
                     f'fill="{fill}" stroke="{stroke}" stroke-width="2"/>')
        parts.append(text(x + w/2, y + 38, title, size=18, weight="bold", anchor="middle"))
        parts.append(text(x + w/2, y + 66, subtitle, size=15, anchor="middle"))
    parts.extend([
        '<path d="M305 139 L353 139" stroke="#66788b" stroke-width="3" marker-end="url(#arrow)"/>',
        '<path d="M593 139 L642 139" stroke="#66788b" stroke-width="3" marker-end="url(#arrow)"/>',
        '<path d="M782 188 L782 254" stroke="#cf8a45" stroke-width="3" stroke-dasharray="7 5" '
        'marker-end="url(#arrow-orange)"/>',
        '<defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
        '<path d="M0 0 L9 4.5 L0 9 Z" fill="#66788b"/></marker>'
        '<marker id="arrow-orange" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
        '<path d="M0 0 L9 4.5 L0 9 Z" fill="#cf8a45"/></marker></defs>',
        text(782, 225, "search remains open", size=14, color="#a46124", anchor="middle"),
        text(44, 241, "Stipulated historical step:", size=16, weight="bold"),
        text(44, 269, "program evaluated all 11", size=16),
        text(44, 295, "and rejected them for W", size=16),
        text(44, 389, "Dashed link is conjectural. A label split alone would not establish a cryptanalytic weakness or historical use.",
             size=15, color="#526073"),
        '</svg>',
    ])
    (HERE / "inference.svg").write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    trait_chart()
    inference_diagram()
    print("wrote traits.svg and inference.svg")
