"""Render direct versus closed Boolean-quotient ranks for one frozen draw."""

from html import escape
import json
from pathlib import Path
import xml.etree.ElementTree as ET


HERE = Path(__file__).resolve().parent
DIRECT = json.loads((HERE / "evidence.json").read_text())
CLOSED = json.loads((HERE / "closure-evidence.json").read_text())
if DIRECT["equations_sha256"] != CLOSED["equations_sha256"]:
    raise RuntimeError("the two rank series have different source equations")


def chart():
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="820" height="290" viewBox="0 0 820 290" role="img" aria-labelledby="title desc">',
        '<title id="title">Direct and closed Boolean row dimensions for one Semaev draw</title>',
        '<desc id="desc">At degrees one and two, both spaces have ranks one and eleven. At degree three, direct rank is 53 and closed quotient rank is 79. Low-degree dimensions at degree three are 12 and 23.</desc>',
        '<rect width="820" height="290" fill="#ffffff"/>',
        '<text x="24" y="30" font-family="DejaVu Sans, sans-serif" font-size="17" font-weight="700" fill="#193444">One Semaev draw: selected rows versus quotient closure</text>',
        '<text x="24" y="51" font-family="DejaVu Sans, sans-serif" font-size="11" fill="#4b6472">n=4, n′=4, s=1, xR=1; exact F₂ dimensions, not a polynomial-ring first-fall proof.</text>',
        '<rect x="25" y="65" width="13" height="13" fill="#245a81"/><text x="43" y="76" font-family="DejaVu Sans, sans-serif" font-size="10" fill="#193444">selected direct rows</text>',
        '<rect x="184" y="65" width="13" height="13" fill="#c87539"/><text x="202" y="76" font-family="DejaVu Sans, sans-serif" font-size="10" fill="#193444">closed Boolean quotient</text>',
        '<text x="24" y="101" font-family="DejaVu Sans, sans-serif" font-size="12" font-weight="700" fill="#193444">Full span rank</text>',
        '<text x="421" y="101" font-family="DejaVu Sans, sans-serif" font-size="12" font-weight="700" fill="#193444">Low-degree intersection</text>',
    ]
    for degree in (1, 2, 3):
        y = 118 + (degree - 1) * 48
        dr = DIRECT["profiles"]["product_degree"][str(degree)]
        cl = CLOSED["profiles"][str(degree)]["variable_steps"]
        full_values = (dr["rank"], cl["rank"])
        low_values = (dr["rank"] - dr["projected_rank"],
                      cl["low_degree_dimension"])
        for x0, scale, values in ((45, 3.5, full_values),
                                  (458, 10.0, low_values)):
            parts.append(f'<text x="{x0-25}" y="{y+20}" font-family="DejaVu Sans, sans-serif" font-size="11" fill="#193444">D{degree}</text>')
            for offset, color, value in ((0, "#245a81", values[0]),
                                         (17, "#c87539", values[1])):
                width = max(1, value * scale)
                parts.append(f'<rect x="{x0}" y="{y+offset}" width="{width:.1f}" height="12" rx="2" fill="{color}"/>')
                parts.append(f'<text x="{x0+width+5:.1f}" y="{y+offset+10}" font-family="DejaVu Sans, sans-serif" font-size="10" fill="#193444">{value}</text>')
    parts += [
        '<line x1="24" y1="267" x2="796" y2="267" stroke="#c8d6dd"/>',
        '<text x="24" y="284" font-family="DejaVu Sans, sans-serif" font-size="10" fill="#4b6472">Source equation SHA-256: ' + escape(DIRECT["equations_sha256"][:16]) + '…; no sampling or cost inference.</text>',
        '</svg>',
    ]
    svg = "\n".join(parts) + "\n"
    ET.fromstring(svg)
    return svg


if __name__ == "__main__":
    (HERE / "closure-ranks.svg").write_text(chart())
