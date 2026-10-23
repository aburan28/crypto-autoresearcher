"""Render the exact 19-curve conductor comparison from sealed verifications."""
import hashlib
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
RUN = HERE / "runs/census-20261023T1733Z"
FIRST = HERE.parent / "nist_seed_exact_conductor_20261023/runs/first-stage-20261023T1720Z"
assert (RUN / "complete.ok").read_text() == "verified\n"
assert (FIRST / "complete.ok").read_text() == "verified\n"
new = json.loads((RUN / "verification.json").read_text())["rows"]
first = json.loads((FIRST / "verification.json").read_text())["rows"]
rows = [x for x in new if x["label"] != "control"]
for x in first:
    if x["name"] == "omitted_p256_876":
        rows.append({**x, "label": "omitted"})
    if x["name"] == "published_p256_1842":
        rows.append({**x, "label": "published"})
assert len(rows) == 19
discriminants = [(x["name"], abs(int(x["D_K"]))) for x in rows]
assert all(int(x["D_K"]) % 4 == 1 for x in rows)
minimum_name, minimum_abs = min(discriminants, key=lambda pair: pair[1])
assert minimum_name == "omitted_192_2198"
assert minimum_abs == 8414124017300985115354808730810798330685690037040240202027
assert (minimum_abs + 1) // 4 > 2**190
(HERE / "summary.json").write_text(json.dumps({
    "new_verification_sha256": hashlib.sha256((RUN / "verification.json").read_bytes()).hexdigest(),
    "first_verification_sha256": hashlib.sha256((FIRST / "verification.json").read_bytes()).hexdigest(),
    "comparable_curve_count": 19,
    "omitted_f_pi_counts": {str(f): sum(x["label"] == "omitted" and x["f_pi"] == str(f) for x in rows) for f in (1, 3, 5)},
    "published_f_pi_counts": {str(f): sum(x["label"] == "published" and x["f_pi"] == str(f) for x in rows) for f in (1, 3, 5)},
    "minimum_abs_D_K": str(minimum_abs),
    "minimum_abs_D_K_curve": minimum_name,
    "noninteger_endomorphism_degree_lower_bound_exceeds_2_pow_190": True,
}, indent=2, sort_keys=True) + "\n")

def key(x):
    name = x["name"]
    field = 192 if "192" in name else 224 if "224" in name else 239 if "239" in name else 256
    return field, 0 if x["label"] == "omitted" else 1, name

rows.sort(key=key)
width, height = 760, 64 + 31 * len(rows) + 35
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
       f'<rect width="{width}" height="{height}" fill="white"/>',
       '<text x="20" y="28" font-family="sans-serif" font-size="20">Exact Frobenius-order conductors, 19 comparable curves</text>',
       '<text x="20" y="47" font-family="sans-serif" font-size="12">Orange = omitted; blue = published. Bar width is the exact integer f_pi.</text>']
for i, x in enumerate(rows):
    y = 67 + 31*i
    label = x["name"].replace("omitted_", "skip ").replace("published_", "pub ")
    f = int(x["f_pi"])
    color = "#d9843c" if x["label"] == "omitted" else "#5788c1"
    svg.append(f'<text x="20" y="{y+15}" font-family="monospace" font-size="13">{label}</text>')
    svg.append(f'<rect x="295" y="{y}" width="{f*65}" height="19" fill="{color}"/>')
    svg.append(f'<text x="{305+f*65}" y="{y+15}" font-family="sans-serif" font-size="13">{f}</text>')
svg.append(f'<text x="20" y="{height-12}" font-family="sans-serif" font-size="11">Sources: sealed Sage verification records; exact factors and EC1 identities are linked in report.md.</text>')
svg.append('</svg>')
(HERE / "conductors.svg").write_text("\n".join(svg)+"\n")

dot = '''digraph Census {
  graph [rankdir=LR, bgcolor="white", labelloc=t,
    label="Exact conductor census: four comparable fields", fontsize=19];
  node [shape=box, style="rounded,filled", fontname="Helvetica", fontsize=15];
  a [label="11 omitted classes\\n10 have f_pi=1; one has f_pi=5", fillcolor="#ffe6d3"];
  b [label="8 published controls\\n6 have f_pi=1; one 5; one 3", fillcolor="#e1edff"];
  c [label="No exact f_pi split\\nof the named labels", fillcolor="#e4f4e7"];
  d [label="Historical program reached\\nand rejected all eleven", style="dashed,rounded", fillcolor="white"];
  e [label="All 19: noninteger endomorphism\\ndegree > 2^190", fillcolor="#e4f4e7"];
  a -> c; b -> c; a -> e; b -> e; d -> a [style=dashed, label="working premise"];
}
'''
(HERE / "inference.dot").write_text(dot)
subprocess.run(["dot", "-Tsvg", str(HERE / "inference.dot"), "-o", str(HERE / "inference.svg")], check=True)
