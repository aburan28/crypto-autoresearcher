"""Render only the archived per-edge diagnostic elapsed times."""
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
CHECKPOINTS = HERE.parent / "controls" / "p29-twoedge-attempt1"
WIDTH, HEIGHT = 1100, 410


def render():
    rows = [json.loads(path.read_text()) for path in sorted(CHECKPOINTS.glob("edge-????.json"))[1:]]
    if [row["index"] for row in rows] != list(range(1, 2049)):
        raise ValueError("P29 full path is incomplete")
    times = [row["elapsed_seconds"] for row in rows]
    xmax, ymax = 2048, 4.0
    x0, x1, y0, y1 = 72, 1060, 340, 72
    items = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
             '<rect width="100%" height="100%" fill="white"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#24313d} .title{font-size:20px;font-weight:bold} .lab{font-size:13px}</style>',
             '<text x="72" y="29" class="title">P29 checkpoint transport: all 2,048 saved edges</text>',
             '<text x="72" y="49" class="lab">Per-edge internal elapsed seconds; diagnostic only, not complete wall time</text>']
    for value in range(5):
        y = y0 - value / ymax * (y0 - y1)
        items.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x1}" y2="{y:.1f}" stroke="#e1e6eb"/>')
        items.append(f'<text x="48" y="{y+4:.1f}" class="lab">{value}</text>')
    for value in (0, 512, 1024, 1536, 1907, 2048):
        x = x0 + value / xmax * (x1 - x0)
        items.append(f'<text x="{x-15:.1f}" y="{y0+21}" class="lab">{value}</text>')
    boundary = x0 + 1907 / xmax * (x1 - x0)
    items.append(f'<line x1="{boundary:.1f}" y1="{y1}" x2="{boundary:.1f}" y2="{y0}" stroke="#b56334" stroke-dasharray="5 4"/>')
    for row in rows:
        x = x0 + row["index"] / xmax * (x1 - x0)
        y = y0 - min(ymax, row["elapsed_seconds"]) / ymax * (y0 - y1)
        color = "#2b6e8d" if row["index"] <= 1907 else "#b56334"
        items.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="1.15" fill="{color}"/>')
    items.append('<text x="479" y="401" class="lab">Archived edge index</text>')
    items.append('<text x="752" y="65" class="lab">Blue: first bounded attempt; orange: resumed attempt</text>')
    items.append('</svg>')
    (HERE / "edge_times.svg").write_text("\n".join(items) + "\n")


if __name__ == "__main__":
    render()
