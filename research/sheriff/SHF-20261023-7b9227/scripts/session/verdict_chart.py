"""Draw verdicts.svg from findings.yaml: claims per area, one box per claim, coloured by verdict.
Plots the composed verdicts only; no new computation."""
from pathlib import Path
import html
import yaml

CASE = Path(__file__).resolve().parents[2]
case = yaml.safe_load((CASE / "findings.yaml").read_text())["sheriff_case"]
AREAS = [("GOAL-MONO-001 closure", ["C1", "C2", "C3"]), ("crypto STARK fix", ["C4", "C5", "C6"]),
         ("new formal/ Lean", ["C7", "C8"]), ("cryptanalysis n=83 IC", ["C9", "C10", "C11", "C12"]),
         ("repository health", ["C13", "C14", "C15", "C16"])]
ORDER = ["upheld", "upheld_scoped", "not_covered", "overclaimed", "unsupported", "broken"]
COLOR = {"upheld": "#2e7d32", "upheld_scoped": "#81c784", "not_covered": "#5f8dd3",
         "overclaimed": "#f2c94c", "unsupported": "#e8710a", "broken": "#b3261e"}
verdict = {c["id"]: c["verdict"] for c in case["claims"]}
W, LEFT, ROW, UNIT = 900, 210, 38, 64
h = 90 + ROW * len(AREAS) + 50
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" font-family="Helvetica, Arial, sans-serif" font-size="13">',
       f'<rect width="{W}" height="{h}" fill="#ffffff"/>',
       f'<text x="16" y="28" font-size="16" font-weight="bold">{case["id"]}: verdicts on {len(case["claims"])} audited claims</text>',
       '<text x="16" y="48" fill="#444">one box per claim, grouped by area; colour = verdict; source findings.yaml</text>']
for k, (label, ids) in enumerate(AREAS):
    y = 64 + k * ROW
    out.append(f'<text x="16" y="{y + 21}">{html.escape(label)}</text>')
    for i, cid in enumerate(sorted(ids, key=lambda c: ORDER.index(verdict[c]))):
        v = verdict[cid]; x = LEFT + i * UNIT
        out.append(f'<rect x="{x}" y="{y + 4}" width="{UNIT - 4}" height="26" fill="{COLOR[v]}"><title>{cid}: {v}</title></rect>')
        tc = "#000" if v in ("upheld_scoped", "overclaimed") else "#fff"
        out.append(f'<text x="{x + (UNIT - 4) / 2}" y="{y + 22}" text-anchor="middle" fill="{tc}" font-weight="bold">{cid}</text>')
ly = 64 + ROW * len(AREAS) + 16
for k, v in enumerate(ORDER):
    n = sum(x == v for x in verdict.values())
    out.append(f'<rect x="{16 + k * 145}" y="{ly}" width="14" height="14" fill="{COLOR[v]}"/><text x="{36 + k * 145}" y="{ly + 12}">{v} ({n})</text>')
out.append("</svg>")
(CASE / "verdicts.svg").write_text("\n".join(out) + "\n")
print("verdicts.svg written")
