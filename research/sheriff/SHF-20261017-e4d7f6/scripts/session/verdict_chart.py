"""Draw verdicts.svg from findings.yaml: the 26 findings of SHF-20261016-3caa6f,
one box each, grouped by original severity, coloured by this re-audit's verdict.
Plots the composed verdicts only; no new computation."""
from pathlib import Path
import html
import yaml

CASE = Path(__file__).resolve().parents[2]
case = yaml.safe_load((CASE / "findings.yaml").read_text())["sheriff_case"]
rows = case["original_finding_verdicts"]
ORDER = ["fixed", "partially_fixed", "not_covered", "not_fixed", "regressed"]
COLOR = {"fixed": "#2e7d32", "partially_fixed": "#f2c94c", "not_covered": "#5f8dd3",
         "not_fixed": "#b3261e", "regressed": "#6a1b9a"}
W, LEFT, ROW, UNIT = 1140, 130, 40, 64
groups = [(s, [r for r in rows if r["severity"] == s]) for s in ("blocker", "major", "minor")]
h = 90 + ROW * len(groups) + 60
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" font-family="Helvetica, Arial, sans-serif" font-size="13">',
       f'<rect width="{W}" height="{h}" fill="#ffffff"/>',
       f'<text x="16" y="28" font-size="16" font-weight="bold">{case["id"]}: re-audit of the {len(rows)} findings of SHF-20261016-3caa6f</text>',
       '<text x="16" y="48" fill="#444">one box per original finding, by original severity; colour = verdict on origin/main 2026-10-17; source findings.yaml</text>']
for k, (sev, rs) in enumerate(groups):
    y = 64 + k * ROW
    out.append(f'<text x="16" y="{y + 22}">{sev} ({len(rs)})</text>')
    rs = sorted(rs, key=lambda r: ORDER.index(r["verdict"]))
    for i, r in enumerate(rs):
        x, yy = LEFT + i * UNIT, y + 4
        out.append(f'<rect x="{x}" y="{yy}" width="{UNIT - 4}" height="26" fill="{COLOR[r["verdict"]]}"><title>{r["id"]}: {r["verdict"]}</title></rect>')
        tc = "#000" if r["verdict"] in ("partially_fixed",) else "#fff"
        out.append(f'<text x="{x + (UNIT - 4) / 2}" y="{yy + 18}" text-anchor="middle" fill="{tc}" font-weight="bold">{html.escape(r["id"])}</text>')
ly = 64 + ROW * len(groups) + 20
for k, v in enumerate(ORDER):
    n = sum(r["verdict"] == v for r in rows)
    out.append(f'<rect x="{16 + k * 170}" y="{ly}" width="14" height="14" fill="{COLOR[v]}"/><text x="{36 + k * 170}" y="{ly + 12}">{v} ({n})</text>')
out.append("</svg>")
(CASE / "verdicts.svg").write_text("\n".join(out) + "\n")
print("verdicts.svg written")
