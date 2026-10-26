"""Draw verdicts.svg (claims by verdict, findings by severity) from findings.yaml.

Hand-written SVG; reads only this case's findings.yaml. Run from the repository root:
python3 research/sheriff/SHF-20261021-477d51/scripts/session/verdict_chart.py
"""
from pathlib import Path

import yaml

CASE = Path(__file__).resolve().parents[2]
body = yaml.safe_load((CASE / "findings.yaml").read_text())["sheriff_case"]
COLORS = {"upheld": "#2e7d32", "upheld_scoped": "#7cb342", "overclaimed": "#f9a825",
          "unsupported": "#8d6e63", "broken": "#c62828", "not_covered": "#9e9e9e",
          "blocker": "#c62828", "major": "#ef6c00", "minor": "#fbc02d"}

rows = []
for c in body["claims"]:
    rows.append((c["id"], c["verdict"], c["text"][:78] + ("…" if len(c["text"]) > 78 else "")))
sev = {}
for f in body["findings"]:
    sev[f["severity"]] = sev.get(f["severity"], 0) + 1

W, ROW = 860, 22
H = 70 + ROW * len(rows) + 60
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" font-family="sans-serif" font-size="12">',
       f'<rect width="{W}" height="{H}" fill="#ffffff"/>',
       f'<text x="16" y="24" font-size="15" font-weight="bold">{body["id"]}: verdict per claim (crypto PR #2343)</text>',
       '<text x="16" y="44" fill="#444">colour = verdict; findings by severity at the foot</text>']
y = 64
for cid, verdict, text in rows:
    out.append(f'<rect x="16" y="{y}" width="120" height="{ROW - 4}" fill="{COLORS[verdict]}"/>')
    out.append(f'<text x="22" y="{y + 13}" fill="#000">{cid} {verdict}</text>')
    t = text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    out.append(f'<text x="146" y="{y + 13}" fill="#222">{t}</text>')
    y += ROW
y += 16
x = 16
for s in ("blocker", "major", "minor"):
    n = sev.get(s, 0)
    out.append(f'<rect x="{x}" y="{y}" width="14" height="14" fill="{COLORS[s]}"/>')
    out.append(f'<text x="{x + 20}" y="{y + 12}">{s}: {n}</text>')
    x += 130
out.append("</svg>")
(CASE / "verdicts.svg").write_text("\n".join(out) + "\n")
print("wrote", CASE / "verdicts.svg", {r[1] for r in rows}, sev)
