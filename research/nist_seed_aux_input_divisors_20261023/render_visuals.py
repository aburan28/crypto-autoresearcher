"""Draw the exact divisor screen as a comparison chart and inference diagram."""
import json
import math
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
data = json.loads((HERE / "analysis.json").read_text())
rows = data["rows"]
by_name = {r["name"]: r for r in rows}
minus = sorted((r for r in rows if r["direction"] == "minus"),
               key=lambda r: (r["field_bits"], r["seed_ordinal_one_based"], r["label"]))
W, H = 1120, 105 + 29 * len(minus)
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       f'<rect width="{W}" height="{H}" fill="white"/>',
       '<text x="25" y="30" font-family="sans-serif" font-size="21">Divisor gap below Cheon bounds: 19 exact same-field curves</text>',
       '<text x="25" y="52" font-family="sans-serif" font-size="13">Bar = log₂(bound / largest divisor at bound); shorter means a closer divisor. No auxiliary powers are observed.</text>',
       '<text x="295" y="80" font-family="sans-serif" font-size="15">d | n−1, bound √n</text>',
       '<text x="690" y="80" font-family="sans-serif" font-size="15">d | n+1, bound ∛n</text>',
       '<text x="25" y="80" font-family="sans-serif" font-size="12" fill="#d0782b">orange: omitted</text>',
       '<text x="135" y="80" font-family="sans-serif" font-size="12" fill="#2e6da4">blue: published</text>']
for i, a in enumerate(minus):
    y = 97 + 29 * i
    b = by_name[a["name"].replace("_minus", "_plus")]
    label = a["name"].replace("omitted_", "skip ").replace("published_", "pub ").replace("_minus", "")
    color = "#d0782b" if a["label"] == "omitted" else "#2e6da4"
    svg.append(f'<text x="25" y="{y+15}" font-family="monospace" font-size="14">{label}</text>')
    for x, r in ((295, a), (690, b)):
        gap = math.log2(int(r["gap_numerator"]) / int(r["gap_denominator"]))
        width = max(1.5, min(340, gap * 2.7))
        svg.append(f'<rect x="{x}" y="{y}" width="{width:.2f}" height="20" fill="{color}"/>')
        svg.append(f'<text x="{x+width+7:.2f}" y="{y+15}" font-family="sans-serif" font-size="12">{gap:.2f} bits</text>')
svg.append('</svg>')
(HERE / "gaps.svg").write_text("\n".join(svg) + "\n")

dot = '''digraph G {
  graph [rankdir=LR, bgcolor="white", fontname="Helvetica", labelloc=t,
         label="Arithmetic opportunity and the missing auxiliary input", fontsize=16];
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=11];
  exact [label="19 certified prime-order curves\\n38 complete n±1 factorizations", fillcolor="#dceaf6"];
  divisors [label="Exact divisor bounds\\nno published/skipped separator", fillcolor="#e1f2df"];
  aux [label="Required powers of secret scalar\\nnot observed in ordinary ECDLP", fillcolor="#fff0ca"];
  attack [label="Conditional Cheon route\\nnot an ordinary-curve weakness", fillcolor="#fff0ca"];
  history [label="1997 selection rule\\nnot identified", fillcolor="#fff0ca"];
  exact -> divisors [label="verified data"];
  divisors -> attack [style=dashed, label="requires auxiliary powers"];
  aux -> attack [style=dashed, label="hypothetical access"];
  divisors -> history [style=dashed, label="no source linkage"];
}
'''
(HERE / "inference.dot").write_text(dot)
subprocess.run(["dot", "-Tsvg", str(HERE / "inference.dot"), "-o", str(HERE / "inference.svg")], check=True)
