"""Draw the exact combinatorial upper fractions from bound.json."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data = json.loads(args.record.read_text())
    series = [
        ("subgroup affine B=249", data["bases"]["subgroup_affine"]["rows"], "#16a34a", False),
        ("raw x B=265", data["bases"]["raw_x_projected"]["rows"], "#d97706", False),
        ("torsion φ B=267", data["bases"]["torsion_phi_projected"]["rows"], "#2563eb", False),
        ("hypothetical B=287", data["hypothetical_default_size"]["rows"], "#64748b", True),
    ]
    left, top, width, height = 100, 84, 690, 370
    def x(m): return left + (m - 2) * width / 6
    def y(value): return top + (0 - math.log10(value)) * height / 13
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="560" viewBox="0 0 1100 560">',
             '<rect width="1100" height="560" fill="#f8fafc"/>',
             '<text x="42" y="36" font-family="Arial" font-size="23" fill="#102a43">Exact upper bound on m-term target coverage</text>',
             '<text x="42" y="59" font-family="Arial" font-size="14" fill="#475569">GF(2^61), prime subgroup r = 576,460,752,557,211,763; no relation-yield data.</text>']
    for power in (0, -3, -6, -9, -12):
        yy = top + (0 - power) * height / 13
        parts += [f'<line x1="{left}" y1="{yy:.1f}" x2="{left+width}" y2="{yy:.1f}" stroke="#cbd5e1"/>',
                  f'<text x="{left-12}" y="{yy+4:.1f}" text-anchor="end" font-family="Arial" font-size="13" fill="#475569">10^{power}</text>']
    for m in range(2, 9):
        parts.append(f'<text x="{x(m):.1f}" y="{top+height+24}" text-anchor="middle" font-family="Arial" font-size="13" fill="#475569">{m}</text>')
    for idx, (label, rows, color, dashed) in enumerate(series):
        coords = [(x(row["m"]), y(float(row["maximum_distinct_target_fraction_decimal"]))) for row in rows]
        points = " ".join(f"{xx:.1f},{yy:.1f}" for xx, yy in coords)
        dash = ' stroke-dasharray="7 5"' if dashed else ""
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"{dash}/>')
        for xx, yy in coords:
            parts.append(f'<circle cx="{xx:.1f}" cy="{yy:.1f}" r="4" fill="{color}"/>')
        ly = 110 + idx * 43
        parts += [f'<line x1="830" y1="{ly}" x2="866" y2="{ly}" stroke="{color}" stroke-width="3"{dash}/>',
                  f'<text x="876" y="{ly+5}" font-family="Arial" font-size="15" fill="#102a43">{label}</text>']
    parts += ['<text x="445" y="520" text-anchor="middle" font-family="Arial" font-size="14" fill="#475569">Exact number of summands m</text>',
              '<text x="25" y="282" transform="rotate(-90 25 282)" text-anchor="middle" font-family="Arial" font-size="14" fill="#475569">Upper fraction of subgroup targets, log scale</text>',
              '<text x="830" y="330" font-family="Arial" font-size="13" fill="#475569">Bound: C(2B+m−1,m) / r.</text>',
              '<text x="830" y="355" font-family="Arial" font-size="13" fill="#475569">Four raw channels share one</text>',
              '<text x="830" y="376" font-family="Arial" font-size="13" fill="#475569">projected subgroup target.</text>',
              '</svg>']
    with args.out.open("x") as stream:
        stream.write("\n".join(parts) + "\n")
    print(f"{args.out}: four series")


if __name__ == "__main__":
    main()
