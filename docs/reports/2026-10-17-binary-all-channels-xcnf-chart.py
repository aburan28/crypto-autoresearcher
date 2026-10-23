"""Render structural gate counts from the immutable all-channel manifest."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    rows = json.loads(args.manifest.read_text())["arms"]
    assert len(rows) == 8
    top = 150_000
    left, plot_width = 100, 820
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1040" height="450" viewBox="0 0 1040 450">',
             '<rect width="1040" height="450" fill="#f8fafc"/>',
             '<text x="42" y="35" font-family="Arial" font-size="22" fill="#102a43">Live XOR–AND gates in eight m8 input formulas</text>',
             '<text x="42" y="58" font-family="Arial" font-size="14" fill="#475569">Frozen GF(2^61) field representation; counts are structural, not solver time.</text>']
    for tick in (0, 50_000, 100_000, 150_000):
        x = left + tick * plot_width / top
        parts += [f'<line x1="{x:.1f}" y1="80" x2="{x:.1f}" y2="390" stroke="#cbd5e1"/>',
                  f'<text x="{x:.1f}" y="410" text-anchor="middle" font-family="Arial" font-size="12" fill="#475569">{tick//1000}k</text>']
    for i, row in enumerate(rows):
        y = 91 + i * 38
        count = row["live_gates"]["live_gate_total"]
        bar_width = count * plot_width / top
        color = "#2563eb" if row["kind"] == "torsion_phi" else "#d97706"
        label = ("torsion" if row["kind"] == "torsion_phi" else "raw x") + f" c{row['channel']}"
        parts += [f'<text x="92" y="{y+18}" text-anchor="end" font-family="Arial" font-size="14" fill="#102a43">{label}</text>',
                  f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="25" fill="{color}" rx="3"/>',
                  f'<text x="{left+bar_width+8:.1f}" y="{y+18}" font-family="Arial" font-size="13" fill="#102a43">{count:,}</text>']
    parts += ['<text x="510" y="438" text-anchor="middle" font-family="Arial" font-size="13" fill="#475569">Live two-input gates (AND + XOR); 1 input per channel, no uncertainty interval</text>',
              '</svg>']
    with args.out.open("x") as stream:
        stream.write("\n".join(parts) + "\n")
    print(f"{args.out}: {len(rows)} bars")


if __name__ == "__main__":
    main()
