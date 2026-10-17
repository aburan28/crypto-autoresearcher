"""Render selected-column counts from the frozen weighted k11 base record."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--parent", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    data, parent = [json.loads(p.read_text()) for p in (args.base, args.parent)]
    old = next(row["projected_columns"] for row in parent["candidate_scans"]
               if row["offset"] == parent["selected_offset"])
    threshold = data["predeclared_selection"]["target_columns"]
    rows = data["candidate_scans"]
    assert len(rows) == 4 and old == 267 and threshold == 311
    left, width = 155, 720
    scale = width / 350
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1060" height="405" viewBox="0 0 1060 405">',
             '<rect width="1060" height="405" fill="#f8fafc"/>',
             '<text x="35" y="37" font-family="Arial" font-size="23" fill="#102a43">Target-blind weighted k11 torsion-base scans</text>',
             '<text x="35" y="60" font-family="Arial" font-size="14" fill="#475569">Projected sign-folded columns; four frozen offsets, same 1,276 Hamming-cut candidates each.</text>']
    for count in (0, 100, 200, 300):
        x = left + count * scale
        parts += [f'<line x1="{x:.1f}" y1="83" x2="{x:.1f}" y2="339" stroke="#cbd5e1"/>',
                  f'<text x="{x:.1f}" y="362" text-anchor="middle" font-family="Arial" font-size="12" fill="#475569">{count}</text>']
    for i, row in enumerate(rows):
        y = 90 + i * 53
        n = row["projected_columns"]
        color = "#2563eb" if row["offset"] == data["selected_offset"] else "#94a3b8"
        label_x = left + n * scale - 9 if 0 <= threshold - n < 12 else left + n * scale + 8
        anchor = "end" if 0 <= threshold - n < 12 else "start"
        label_color = "#ffffff" if anchor == "end" else "#102a43"
        parts += [f'<text x="145" y="{y+23}" text-anchor="end" font-family="Arial" font-size="15" fill="#102a43">offset {row["offset"]}</text>',
                  f'<rect x="{left}" y="{y}" width="{n*scale:.1f}" height="31" rx="4" fill="{color}"/>',
                  f'<text x="{label_x:.1f}" y="{y+23}" text-anchor="{anchor}" font-family="Arial" font-size="15" fill="{label_color}">{n}</text>']
    ty = 90 + 4 * 53
    parts += [f'<text x="145" y="{ty+23}" text-anchor="end" font-family="Arial" font-size="15" fill="#102a43">prior k10</text>',
              f'<rect x="{left}" y="{ty}" width="{old*scale:.1f}" height="31" rx="4" fill="#16a34a"/>',
              f'<text x="{left+old*scale+8:.1f}" y="{ty+23}" font-family="Arial" font-size="15" fill="#102a43">{old}</text>']
    tx = left + threshold * scale
    parts += [f'<line x1="{tx:.1f}" y1="80" x2="{tx:.1f}" y2="340" stroke="#d97706" stroke-width="2" stroke-dasharray="6 5"/>',
              f'<text x="{tx+8:.1f}" y="80" font-family="Arial" font-size="12" fill="#a16207">count threshold 311</text>',
              '<text x="520" y="391" text-anchor="middle" font-family="Arial" font-size="14" fill="#475569">Projected columns B; source: base.json, not solver yield or time</text>',
              '</svg>']
    with args.out.open("x") as stream:
        stream.write("\n".join(parts) + "\n")
    print(f"{args.out}: {len(rows)} offsets plus prior k10")


if __name__ == "__main__":
    main()
