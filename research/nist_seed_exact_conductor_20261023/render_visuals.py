"""Render the frozen first-stage conductor result from verified raw records."""
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/first-stage-20261023T1720Z"
assert (RUN / "complete.ok").read_text() == "verified\n"
rows = {x["name"]: x for x in json.loads((RUN / "results.json").read_text())}
verification = {x["name"]: x for x in json.loads((RUN / "verification.json").read_text())["rows"]}
names = ["omitted_p256_876", "published_p256_1842"]
assert all(rows[n]["value"]["f_pi"] == verification[n]["f_pi"] == "1" for n in names)

dot = '''digraph Conductor {
  graph [rankdir=LR, bgcolor="white", labelloc=t,
    label="Exact P-256 first pair: Frobenius-order conductor", fontsize=20];
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=16];
  a [label="omitted block 876\\nDelta fully factored\\nf_pi = 1", fillcolor="#ffe6d3"];
  b [label="published block 1842\\nDelta fully factored\\nf_pi = 1", fillcolor="#e1edff"];
  c [label="For each isogeny class:\\nZ[pi] = End(E) = O_K\\nno conductor-changing edge", fillcolor="#e4f4e7"];
  d [label="Proposed rule: all omitted\\nhave f_pi > 1", fillcolor="#f9dddd"];
  a -> c; b -> c; a -> d [style=dashed, label="counterexample"];
}
'''
(HERE / "inference.dot").write_text(dot)
subprocess.run(["dot", "-Tsvg", str(HERE / "inference.dot"), "-o", str(HERE / "inference.svg")], check=True)

svg = ['<svg xmlns="http://www.w3.org/2000/svg" width="760" height="270" viewBox="0 0 760 270">',
       '<rect width="760" height="270" fill="white"/>',
       '<text x="24" y="28" font-family="sans-serif" font-size="20">Exact Frobenius-order conductors</text>',
       '<text x="24" y="49" font-family="sans-serif" font-size="13">P-256 first-stage pair; full discriminant factorizations, n=2</text>']
for y, name, label, color in [(85, names[0], "omitted 876", "#d9843c"),
                               (155, names[1], "published 1842", "#5788c1")]:
    f = int(rows[name]["value"]["f_pi"])
    svg.append(f'<text x="24" y="{y+21}" font-family="sans-serif" font-size="16">{label}</text>')
    svg.append(f'<rect x="185" y="{y}" width="{f*300}" height="30" fill="{color}"/>')
    svg.append(f'<text x="{195+f*300}" y="{y+22}" font-family="sans-serif" font-size="16">f_pi = {f}</text>')
svg.append('<text x="24" y="239" font-family="sans-serif" font-size="13">Exact integer values; no sampling uncertainty. Source: runs/first-stage-20261023T1720Z/verification.json.</text>')
svg.append('</svg>')
(HERE / "comparison.svg").write_text("\n".join(svg) + "\n")
