"""Render six recorded positive-cell sampled RSS values as a dependency-free SVG."""
from pathlib import Path
from html import escape
import json

ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "experiments/EXP-ICPERF-891f7f/runs/RUN-ICPERF-7ed866/raw-result.json"
OUT = Path(__file__).with_name("peak-rss.svg")
raw = json.loads(RUN.read_text())
cells = [cell for cell in raw["cells"] if cell.get("attempted") and cell.get("kind") == "positive"]
assert len(cells) == 6 and all(cell["status"] == "timeout_censored" for cell in cells)
values = [cell["peak_tree_rss_bytes_sampled"] / (1024 ** 3) for cell in cells]
labels = [cell["cell"].replace("small_x", "small x") for cell in cells]
max_y = 2.5
x0, y0, width, height = 93, 70, 660, 220
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="800" height="380" viewBox="0 0 800 380">',
    '<rect width="800" height="380" fill="white"/>',
    '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#263238} .title{font-size:19px;font-weight:bold} .axis{font-size:12px} .value{font-size:13px;font-weight:bold} .note{font-size:11px;fill:#52606d}</style>',
    '<text class="title" x="400" y="31" text-anchor="middle">Planted controls: sampled peak process-tree RSS</text>',
]
for tick in [0, 0.5, 1, 1.5, 2, 2.5]:
    y = y0 + height - tick / max_y * height
    parts.append(f'<line x1="{x0}" y1="{y:.1f}" x2="{x0+width}" y2="{y:.1f}" stroke="#dbe3e8" stroke-width="1"/>')
    parts.append(f'<text class="axis" x="{x0-12}" y="{y+4:.1f}" text-anchor="end">{tick:g}</text>')
parts.append(f'<line x1="{x0}" y1="{y0}" x2="{x0}" y2="{y0+height}" stroke="#41515b"/>')
parts.append('<text class="axis" x="25" y="180" transform="rotate(-90 25 180)" text-anchor="middle">Sampled peak RSS (GiB)</text>')
for idx, (label, value) in enumerate(zip(labels, values)):
    center = x0 + 55 + idx * 107
    bar_height = value / max_y * height
    y = y0 + height - bar_height
    color = "#2877a7" if label.startswith("coset") else "#718394"
    parts.append(f'<rect x="{center-29}" y="{y:.2f}" width="58" height="{bar_height:.2f}" fill="{color}"/>')
    parts.append(f'<text class="value" x="{center}" y="{y-7:.2f}" text-anchor="middle">{value:.3f}</text>')
    parts.append(f'<text class="axis" x="{center}" y="{y0+height+19}" text-anchor="middle">{escape(label)}</text>')
parts.append('<text class="note" x="400" y="346" text-anchor="middle">RUN-ICPERF-7ed866 · n=1 per cell · all six timed out at 300 s without a response</text>')
parts.append('<text class="note" x="400" y="363" text-anchor="middle">GiB = recorded bytes / 2³⁰; sampled maximum is not a guaranteed absolute peak</text>')
parts.append('</svg>')
OUT.write_text("\n".join(parts) + "\n")
