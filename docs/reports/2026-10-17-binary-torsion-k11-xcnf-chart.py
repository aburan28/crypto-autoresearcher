"""Render live-gate counts for the frozen k10 and k11 torsion XCNF inputs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--k10", type=Path, required=True)
    parser.add_argument("--k11", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    old, new = [json.loads(path.read_text()) for path in (args.k10, args.k11)]
    old_rows = {a["channel"]: a for a in old["arms"] if a["kind"] == "torsion_phi"}
    new_rows = {a["channel"]: a for a in new["arms"]}
    assert set(old_rows) == set(new_rows) == set(range(4))
    left, scale = 140, 750 / 100000
    parts = ['<svg xmlns="http://www.w3.org/2000/svg" width="1070" height="420" viewBox="0 0 1070 420">',
             '<rect width="1070" height="420" fill="#f8fafc"/>',
             '<text x="35" y="36" font-family="Arial" font-size="23" fill="#102a43">Four-channel torsion circuit input sizes</text>',
             '<text x="35" y="60" font-family="Arial" font-size="14" fill="#475569">Same GF(2^61) schoolbook circuit; k10 has 267 columns, k11 has 316.</text>']
    for tick in (0, 25000, 50000, 75000, 100000):
        x = left + tick * scale
        parts += [f'<line x1="{x:.1f}" y1="79" x2="{x:.1f}" y2="349" stroke="#cbd5e1"/>',
                  f'<text x="{x:.1f}" y="370" text-anchor="middle" font-family="Arial" font-size="12" fill="#475569">{tick//1000}k</text>']
    for channel in range(4):
        y = 86 + channel * 65
        old_count = old_rows[channel]["live_gates"]["live_gate_total"]
        new_count = new_rows[channel]["live_gates"]["live_gate_total"]
        parts += [f'<text x="130" y="{y+28}" text-anchor="end" font-family="Arial" font-size="15" fill="#102a43">channel {channel}</text>',
                  f'<rect x="{left}" y="{y}" width="{old_count*scale:.1f}" height="22" rx="3" fill="#16a34a"/>',
                  f'<text x="{left+old_count*scale+8:.1f}" y="{y+17}" font-family="Arial" font-size="12" fill="#102a43">{old_count:,}</text>',
                  f'<rect x="{left}" y="{y+27}" width="{new_count*scale:.1f}" height="22" rx="3" fill="#2563eb"/>',
                  f'<text x="{left+new_count*scale+8:.1f}" y="{y+44}" font-family="Arial" font-size="12" fill="#102a43">{new_count:,}</text>']
    parts += ['<rect x="145" y="392" width="16" height="10" fill="#16a34a"/>',
              '<text x="168" y="402" font-family="Arial" font-size="13" fill="#475569">k10 B=267</text>',
              '<rect x="290" y="392" width="16" height="10" fill="#2563eb"/>',
              '<text x="313" y="402" font-family="Arial" font-size="13" fill="#475569">weighted k11 B=316</text>',
              '<text x="770" y="402" font-family="Arial" font-size="13" fill="#475569">Live two-input gates; no solver time</text>',
              '</svg>']
    with args.out.open("x") as stream:
        stream.write("\n".join(parts) + "\n")
    print(f"{args.out}: 4 matched channel constants")


if __name__ == "__main__":
    main()
