"""Draw recorded P37 checkpoint time values through edge 20."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
CHAIN = HERE.parent / "controls" / "p37-twoedge-attempt1"


def render():
    rows = [json.loads(p.read_text()) for p in sorted(CHAIN.glob("edge-????.json"))[1:]]
    if [row["index"] for row in rows] != list(range(1, 21)):
        raise ValueError("P37 edge-20 checkpoint range differs")
    lines = ['<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="430" viewBox="0 0 1000 430">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#27323d}.title{font-size:21px;font-weight:bold}.label{font-size:13px}</style>',
             '<text x="72" y="32" class="title">P37 source-base transport through fixed check vertex 20</text>',
             '<text x="72" y="54" class="label">Recorded per-edge internal elapsed seconds; process wall time is separate</text>']
    left, right, bottom, top = 80, 962, 345, 85
    for tick in (0, 10, 20, 30):
        y = bottom - tick / 35 * (bottom - top)
        lines += [f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#e1e6eb"/>',
                  f'<text x="47" y="{y+4:.1f}" class="label">{tick}</text>']
    for row in rows:
        index, elapsed = row["index"], row["elapsed_seconds"]
        x = left + (index - 1) / 19 * (right - left)
        y = bottom - elapsed / 35 * (bottom - top)
        color = "#7e9eaa" if index <= 4 else "#2f6d88"
        lines += [f'<line x1="{x:.1f}" y1="{bottom}" x2="{x:.1f}" y2="{y:.1f}" stroke="{color}" stroke-width="3"/>',
                  f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>',
                  f'<text x="{x-7:.1f}" y="{bottom+22}" class="label">{index}</text>']
    lines += ['<text x="422" y="410" class="label">Archived degree-7 edge index</text>',
              '<text x="680" y="78" class="label">Gray: earlier control; blue: this continuation</text>', '</svg>']
    (HERE / "edge_times.svg").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    render()
