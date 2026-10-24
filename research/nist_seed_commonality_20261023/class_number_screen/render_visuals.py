"""Render an exact-count SVG chart from the immutable comparison output."""
from __future__ import annotations

import json
from html import escape
from pathlib import Path

HERE = Path(__file__).resolve().parent


def main() -> None:
    source = json.loads((HERE / "analysis.json").read_text())
    rows = sorted(source["curves"], key=lambda r: (r["group"] != "omitted", r["label"]))
    assert len(rows) == 21
    width, height = 1160, 880
    left, top, bar_max = 280, 120, 690
    maximum = 14
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
             'role="img" aria-label="Low-class-number list discriminants dividing each curve discriminant">',
             '<rect width="100%" height="100%" fill="#fbfcff"/>',
             '<text x="40" y="47" font-family="Arial,sans-serif" font-size="23" font-weight="bold" fill="#172b4d">'
             'Divisibility prefilter for 21 named curves</text>',
             '<text x="40" y="76" font-family="Arial,sans-serif" font-size="15" fill="#354762">'
             'List entries with D dividing |Δ|; none gives a square quotient, so there are zero CM-field matches.</text>']
    for tick in (0, 2, 4, 6, 8, 10, 12, 14):
        x = left + bar_max * tick / maximum
        lines.append(f'<line x1="{x:.1f}" y1="104" x2="{x:.1f}" y2="755" stroke="#dce4ee"/>')
        lines.append(f'<text x="{x:.1f}" y="774" text-anchor="middle" font-family="Arial,sans-serif" '
                     f'font-size="12" fill="#52617a">{tick}</text>')
    for idx, row in enumerate(rows):
        y = top + idx * 29
        if idx == 11:
            lines.append(f'<line x1="40" y1="{y-13}" x2="1060" y2="{y-13}" stroke="#9ba9bc"/>')
        count = row["listed_discriminants_dividing_delta"]
        fill = "#d47b28" if row["group"] == "omitted" else "#2d70a5"
        bar_width = bar_max * count / maximum
        label = row["label"].replace("skip-", "skipped ")
        lines.append(f'<text x="38" y="{y+7}" font-family="Arial,sans-serif" font-size="13" '
                     f'fill="#243650">{escape(label)}</text>')
        if count:
            lines.append(f'<rect x="{left}" y="{y-10}" width="{bar_width:.1f}" height="20" rx="3" fill="{fill}"/>')
        else:
            lines.append(f'<circle cx="{left}" cy="{y}" r="3" fill="{fill}"/>')
        lines.append(f'<text x="{left + bar_width + 11:.1f}" y="{y+6}" font-family="Arial,sans-serif" '
                     f'font-size="12" fill="#26384f">{count}</text>')
    lines += [
        '<rect x="42" y="811" width="14" height="14" fill="#d47b28"/>',
        '<text x="64" y="823" font-family="Arial,sans-serif" font-size="13" fill="#26384f">'
        'Reconstructed omission (11)</text>',
        '<rect x="312" y="811" width="14" height="14" fill="#2d70a5"/>',
        '<text x="334" y="823" font-family="Arial,sans-serif" font-size="13" fill="#26384f">'
        'Published control (10)</text>',
        '<text x="40" y="851" font-family="Arial,sans-serif" font-size="12" fill="#52617a">'
        'Exact input: analysis.json; 16,453,493 external list entries. Divisibility alone is not a class-number match.</text>',
        '</svg>',
    ]
    (HERE / "divisibility.svg").write_text("\n".join(lines) + "\n")


if __name__ == "__main__":
    main()
