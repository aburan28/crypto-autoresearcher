"""Render exact observed class counts from check.json as an SVG."""
import collections
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
d = json.loads((HERE / "check.json").read_text())
counts = collections.Counter((r["field_bits"], r["class"]) for r in d["rows"])
fields = sorted({r["field_bits"] for r in d["rows"]})
out = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="340" viewBox="0 0 760 340">',
       '<rect width="760" height="340" fill="white"/>',
       '<text x="24" y="28" font-family="sans-serif" font-size="20">Archived qualifying curve classes by field size</text>',
       '<text x="24" y="50" font-family="sans-serif" font-size="13">11 reconstructed omissions; 10 published controls. Every row passes the checked gates.</text>']
colors = {"omitted": "#de8c48", "published": "#5689c5"}
for i, bits in enumerate(fields):
    y = 75 + 42*i
    out.append(f'<text x="26" y="{y+16}" font-family="sans-serif" font-size="14">{bits} bit</text>')
    for label, yoff in [("published", 0), ("omitted", 18)]:
        n = counts[(bits, label)]
        out.append(f'<rect x="100" y="{y+yoff}" width="{n*78}" height="14" fill="{colors[label]}"/>')
        out.append(f'<text x="{108+n*78}" y="{y+yoff+12}" font-family="sans-serif" font-size="12">{n}</text>')
out.append('<rect x="530" y="76" width="14" height="14" fill="#5689c5"/>')
out.append('<text x="551" y="89" font-family="sans-serif" font-size="13">published</text>')
out.append('<rect x="530" y="99" width="14" height="14" fill="#de8c48"/>')
out.append('<text x="551" y="112" font-family="sans-serif" font-size="13">omitted</text>')
out.append('<text x="24" y="329" font-family="sans-serif" font-size="12">Counts, not a historical sampling rate; streams stop at published blocks. Source: check.json.</text>')
out.append('</svg>')
(HERE / "field_counts.svg").write_text("\n".join(out) + "\n")
