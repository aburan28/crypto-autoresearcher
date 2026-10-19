"""Draw verdicts.svg from findings.yaml: claims per area, stacked by verdict.
Plots the composed verdicts only; no new computation."""
from collections import Counter
from pathlib import Path
import html
import yaml

CASE = Path(__file__).resolve().parents[2]
case = yaml.safe_load((CASE / "findings.yaml").read_text())["sheriff_case"]
AREAS = [("crypto STARK (B2)", {"C1", "C2", "C3"}), ("Lean (B3)", {"C4", "C5", "C6", "C7", "C8", "C9", "C10", "C11"}),
         ("papers (B8)", {"C12", "C13", "C14", "C15", "C16"}), ("cryptanalysis #938", {"C17", "C18", "C19", "C20"}),
         ("repository integrity (B7)", {"C21", "C22", "C23"})]
ORDER = ["upheld", "upheld_scoped", "not_covered", "overclaimed", "unsupported", "broken"]
COLOR = {"upheld": "#2e7d32", "upheld_scoped": "#81c784", "not_covered": "#5f8dd3",
         "overclaimed": "#f2c94c", "unsupported": "#e8710a", "broken": "#b3261e"}
W, LEFT, ROW, UNIT = 860, 230, 34, 60
rows = []
for label, ids in AREAS:
    rows.append((label, Counter(c["verdict"] for c in case["claims"] if c["id"] in ids)))
h = 90 + ROW * len(rows) + 50
out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" font-family="Helvetica, Arial, sans-serif" font-size="13">',
       f'<rect width="{W}" height="{h}" fill="#ffffff"/>',
       f'<text x="16" y="28" font-size="16" font-weight="bold">{case["id"]}: verdicts on {len(case["claims"])} audited claims</text>',
       '<text x="16" y="48" fill="#444">one box per claim, grouped by area; source findings.yaml</text>']
for k, (label, c) in enumerate(rows):
    y = 64 + k * ROW
    out.append(f'<text x="16" y="{y + 20}">{html.escape(label)}</text>')
    x = LEFT
    for v in ORDER:
        for _ in range(c.get(v, 0)):
            out.append(f'<rect x="{x}" y="{y + 4}" width="{UNIT - 4}" height="22" fill="{COLOR[v]}"><title>{v}</title></rect>')
            x += UNIT
ly = 64 + ROW * len(rows) + 16
for k, v in enumerate(ORDER):
    out.append(f'<rect x="{16 + k * 140}" y="{ly}" width="14" height="14" fill="{COLOR[v]}"/><text x="{36 + k * 140}" y="{ly + 12}">{v}</text>')
out.append("</svg>")
(CASE / "verdicts.svg").write_text("\n".join(out) + "\n")
print("verdicts.svg written")
