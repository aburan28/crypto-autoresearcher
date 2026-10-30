"""Render the source-ledger N83 charge map; no benchmark is run here.

All numbers are copied from cryptanalysis docs/ic/BASELINES.md and baselines.json
at e7cf096b4e2f9020e1326e4ed0b5ac0e96cc99f9. The factor-base time comes
from a separate host-class replay, and is deliberately drawn on its own row.
"""

from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
RANK_MS = 2806.5
SETUP_MS = 4308.5
ONLINE_MS = 158.6
RHO_S = 0.1138
UNIT_MS = 16288.0
BASE_OTHER_HOST_MS = 427.524

assert 7000 < RANK_MS + SETUP_MS + ONLINE_MS < 7500
assert 1800 < RHO_S * UNIT_MS < 1900


def label(x: float) -> str:
    return f"{x / 1000:.3f} s"


W, H = 980, 450
left, scale = 260, 75  # pixels per second
bars = [
    ("Current IC, same run", 114, [("Rank", RANK_MS, "#336899"),
                                    ("Setup after rank", SETUP_MS, "#6b9fc2"),
                                    ("Online", ONLINE_MS, "#a9ced9")]),
    ("Matched rho, same run", 215, [("Cold rho", RHO_S * UNIT_MS, "#ad683e")]),
    ("Base construction, other host", 317,
     [("Separate replay", BASE_OTHER_HOST_MS, "#8e929a")]),
]

out = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       '<rect width="100%" height="100%" fill="#fff"/>',
       '<text x="30" y="39" font-family="sans-serif" font-size="23" font-weight="bold" fill="#183042">N83 Koblitz: what the current cost row charges</text>',
       '<text x="30" y="64" font-family="sans-serif" font-size="14" fill="#3b4d57">r = 8,569,786,107,849,059; rank-finder run 39527997793; wall time</text>']

for tick in range(0, 9, 2):
    x = left + tick * scale
    out.append(f'<line x1="{x}" y1="82" x2="{x}" y2="371" stroke="#d8e2e9"/>')
    out.append(f'<text x="{x}" y="393" text-anchor="middle" font-family="sans-serif" font-size="13" fill="#455760">{tick} s</text>')

for name, y, segments in bars:
    out.append(f'<text x="30" y="{y + 24}" font-family="sans-serif" font-size="15" fill="#183042">{escape(name)}</text>')
    x = left
    total = 0.0
    for segment_name, value, color in segments:
        width = value / 1000 * scale
        out.append(f'<rect x="{x:.2f}" y="{y}" width="{width:.2f}" height="34" fill="{color}"/>')
        if width > 70:
            out.append(f'<text x="{x + width / 2:.2f}" y="{y + 23}" text-anchor="middle" font-family="sans-serif" font-size="12" fill="#fff">{escape(segment_name)}</text>')
        x += width
        total += value
    out.append(f'<text x="{x + 10:.2f}" y="{y + 24}" font-family="sans-serif" font-size="15" fill="#183042">{label(total)}</text>')

out += [
    '<text x="30" y="420" font-family="sans-serif" font-size="12" fill="#3b4d57">The gray construction measurement is from a different host and is excluded from the current IC bar.</text>',
    '<text x="30" y="438" font-family="sans-serif" font-size="12" fill="#3b4d57">Root-index build and self-test are nested in setup. Rho time is derived from rounded S and the run unit.</text>',
    '</svg>',
]
HERE.joinpath("phase-chart.svg").write_text("\n".join(out) + "\n", encoding="utf-8")
