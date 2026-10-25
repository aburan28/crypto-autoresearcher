"""Render checkpoint-recorded per-edge P37 transport time, no new measurements."""
import json
import math
from pathlib import Path
import sys

checkpoints, output = map(Path, sys.argv[1:3])
rows = [json.loads((checkpoints / f"edge-{i:04d}.json").read_text()) for i in range(1, 257)]
limit = max(1, math.ceil(max(row["elapsed_seconds"] for row in rows) / 5) * 5)
x = lambda i: 80 + 850 * (i - 1) / 255
y = lambda value: 410 - 325 * value / limit
parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1000" height="500" viewBox="0 0 1000 500">',
    '<rect width="1000" height="500" fill="white"/>',
    '<style>text{font-family:Arial,sans-serif;fill:#243447;font-size:13px}'
    '.axis{stroke:#44566c;stroke-width:1.5}.grid{stroke:#dbe4ed}'
    '.prior{fill:#3d6b91}.new{fill:#c33e42}</style>',
    '<text x="80" y="30" font-size="18" font-weight="bold">P37 source-base transport through edge 256</text>',
    '<text x="80" y="52">Saved per-edge elapsed seconds; 3,200 signed source-base points per edge; T-4626 valid attempt 2</text>',
]
for tick in range(0, limit + 1, 5):
    parts.extend((f'<line class="grid" x1="80" y1="{y(tick):.1f}" x2="930" y2="{y(tick):.1f}"/>',
                  f'<text x="69" y="{y(tick)+4:.1f}" text-anchor="end">{tick}</text>'))
parts.extend(('<line class="axis" x1="80" y1="85" x2="80" y2="410"/>',
              '<line class="axis" x1="80" y1="410" x2="930" y2="410"/>'))
for tick in (1, 32, 64, 96, 128, 160, 192, 224, 256):
    parts.append(f'<text x="{x(tick):.1f}" y="432" text-anchor="middle">{tick}</text>')
parts.extend(('<text x="505" y="460" text-anchor="middle">Edge index</text>',
              '<text x="21" y="250" transform="rotate(-90 21 250)" text-anchor="middle">Producer edge time (s)</text>'))
for i, row in enumerate(rows, 1):
    parts.append(f'<circle class="{"prior" if i <= 28 else "new"}" cx="{x(i):.1f}" '
                 f'cy="{y(row["elapsed_seconds"]):.1f}" r="2.6"><title>Edge {i}: '
                 f'{row["elapsed_seconds"]:.3f} s</title></circle>')
parts.append('<text x="80" y="486">Blue: archived edges 1–28. Red: valid restarted run, edges 29–256. No relation targets.</text>')
parts.append('</svg>')
output.write_text("\n".join(parts) + "\n")
