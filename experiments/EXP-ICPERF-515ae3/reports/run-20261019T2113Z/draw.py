"""Render sampled RSS peaks from the immutable diagnostic receipt only."""
import json
from html import escape
from pathlib import Path

here = Path(__file__).resolve().parent
receipt_path = here.parents[1] / "runs/RUN-ICPERF-eb0d88/diagnostic/receipt.json"
receipt = json.loads(receipt_path.read_text())
rows = [row for row in receipt["cells"] if row["kind"] == "positive"]
assert [row["cell"] for row in rows] == ["coset-m2", "random-m2", "small_x-m2"]
assert all(row["peak_tree_rss_bytes_sampled"] is not None for row in rows)
values = [row["peak_tree_rss_bytes_sampled"] / 2**30 for row in rows]
# The 8 GiB cap is a frozen protocol parameter; the bars use receipt values.
cap = 8.0
W, H = 900, 460
left, top, plot_w, plot_h = 92, 65, 740, 280
baseline = top + plot_h
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#172b4d}.title{font-size:21px;font-weight:bold}.axis{font-size:14px}.label{font-size:16px;font-weight:bold}.note{font-size:13px;fill:#42526e}</style>',
         '<text x="92" y="31" class="title">Peak sampled process-tree RSS by fixed arm</text>']
for tick in (0, 2, 4, 6, 8):
    y = baseline - tick / cap * plot_h
    parts += [f'<line x1="{left}" y1="{y:.1f}" x2="{left+plot_w}" y2="{y:.1f}" stroke="#dfe5eb"/>',
              f'<text x="{left-14}" y="{y+5:.1f}" text-anchor="end" class="axis">{tick}</text>']
parts.append(f'<text x="20" y="{top+plot_h/2}" transform="rotate(-90 20 {top+plot_h/2})" class="axis">GiB</text>')
for i, (row, value) in enumerate(zip(rows, values)):
    x = left + 85 + i*245
    height = value / cap * plot_h
    y = baseline - height
    parts += [f'<rect x="{x}" y="{y:.1f}" width="125" height="{height:.1f}" fill="#2867a8"/>',
              f'<text x="{x+62.5:.1f}" y="{y-10:.1f}" text-anchor="middle" class="label">{value:.3f}</text>',
              f'<text x="{x+62.5:.1f}" y="{baseline+26}" text-anchor="middle" class="axis">{escape(row["cell"])}</text>',
              f'<text x="{x+62.5:.1f}" y="{baseline+46}" text-anchor="middle" class="note">timeout censored</text>']
parts += [f'<line x1="{left}" y1="{top}" x2="{left+plot_w}" y2="{top}" stroke="#b54c26" stroke-width="2" stroke-dasharray="6 4"/>',
          f'<text x="{left+plot_w-4}" y="{top-9}" text-anchor="end" class="note">8 GiB protocol cap</text>',
          '<text x="92" y="435" class="note">RUN-ICPERF-eb0d88 | one run per arm; peaks from supervisor samples; no uncertainty recorded</text>',
          '</svg>']
(here / "graph.svg").write_text("\n".join(parts) + "\n")
