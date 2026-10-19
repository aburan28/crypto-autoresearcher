"""Draw only the three recorded useful-target counts from data.json."""
import json
from pathlib import Path
from xml.sax.saxutils import escape
root = Path(__file__).resolve().parent
data = json.loads((root / "data.json").read_text())
order = ["P29-E2-native", "P29-E3-native", "P37-floor-u2-native"]
rows = {x["trial_id"]: x for x in data["trials"] if x["status"] == "output_validated"}
assert set(order) == set(rows)
width, height = 760, 380
base_y, plot_h, scale_max = 280, 205, 2500
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">', '<rect width="760" height="380" fill="white"/>', '<text x="380" y="28" text-anchor="middle" font-size="17" font-family="sans-serif" font-weight="bold">Recorded useful-target counts in validated arms</text>', '<text x="380" y="49" text-anchor="middle" font-size="12" font-family="sans-serif">32,768 distinct targets sampled in each arm</text>']
for tick in [0, 500, 1000, 1500, 2000, 2500]:
    y = base_y - tick * plot_h / scale_max
    parts += [f'<line x1="75" y1="{y:.1f}" x2="700" y2="{y:.1f}" stroke="#d7dde1"/>', f'<text x="67" y="{y+4:.1f}" text-anchor="end" font-size="11" font-family="sans-serif">{tick}</text>']
labels = ["P29 E2 native", "P29 E3 native", "P37 floor u2 native"]
colors = ["#267b9d", "#58a0bc", "#ad7c44"]
for i, key in enumerate(order):
    item = rows[key]; value = item["useful_targets"]; x = 125 + i * 190; bar_h = value * plot_h / scale_max; y = base_y - bar_h
    parts += [f'<rect x="{x}" y="{y:.1f}" width="115" height="{bar_h:.1f}" fill="{colors[i]}"/>', f'<text x="{x+57.5:.1f}" y="{y-8:.1f}" text-anchor="middle" font-size="13" font-family="sans-serif" font-weight="bold">{value}</text>', f'<text x="{x+57.5:.1f}" y="302" text-anchor="middle" font-size="11" font-family="sans-serif">{escape(labels[i])}</text>', f'<text x="{x+57.5:.1f}" y="320" text-anchor="middle" font-size="10" font-family="monospace">{escape(item["run_id"])}</text>']
parts += ['<text x="380" y="354" text-anchor="middle" font-size="11" font-family="sans-serif">Counts are descriptive; missing primary arms are omitted, not zero.</text>', '</svg>']
(root / "yield.svg").write_text("\n".join(parts) + "\n")
