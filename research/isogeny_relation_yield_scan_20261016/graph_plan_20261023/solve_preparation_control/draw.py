"""Render the recorded prepared-input byte sizes from result.json as SVG."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "result.json").read_text())
rows = data["arms"]
maximum = max(row["payload_bytes"] for row in rows)
base_y, bar_h, gap = 44, 34, 58
width, height = 760, 250
left, plot_width = 160, 500
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
         '<rect width="100%" height="100%" fill="white"/>',
         '<text x="380" y="23" text-anchor="middle" font-family="sans-serif" font-size="16">Prepared input bytes by factor-base treatment</text>',
         '<text x="380" y="238" text-anchor="middle" font-family="sans-serif" font-size="12">Payload size (bytes), one deterministic P37 vertex-0 preparation per arm</text>']
for i, row in enumerate(rows):
    y = base_y + i * gap
    bar_width = plot_width * row["payload_bytes"] / maximum
    parts.extend([f'<text x="{left-12}" y="{y+23}" text-anchor="end" font-family="sans-serif" font-size="14">{row["arm"]}</text>',
                  f'<rect x="{left}" y="{y}" width="{bar_width:.1f}" height="{bar_h}" fill="#2864a5"/>',
                  f'<text x="{left+bar_width+8:.1f}" y="{y+23}" font-family="sans-serif" font-size="13">{row["payload_bytes"]:,}</text>'])
parts.extend(['<line x1="160" y1="216" x2="660" y2="216" stroke="#444"/>', '</svg>'])
(HERE / "payload-size.svg").write_text("\n".join(parts) + "\n")
