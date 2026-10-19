"""Render editable SVG evidence views from traits.json and assessed.json."""

from __future__ import annotations

import hashlib
import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
RAW = json.loads((HERE / "traits.json").read_text())
ASSESSED = json.loads((HERE / "assessed.json").read_text())
DATA_HASH = hashlib.sha256((HERE / "assessed.json").read_bytes()).hexdigest()[:16]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def selection_diagram() -> None:
    stages = [
        ("1", "1997–98 timestamp", "Six cited streams"),
        ("2", "srand48 → 20 bytes", "One-based ordinal"),
        ("3", "ANSI SHA-1 expansion", "a = −3, c fixes b²"),
        ("4", "Two signs of b", "P-224 pairs isomorphic"),
        ("5", "Count + order checks", "11 qualifying seeds"),
        ("6", "Trait + control screens", "Distinct published orders"),
    ]
    width, height = 1200, 250
    boxes = []
    for i, (num, title, subtitle) in enumerate(stages):
        x = 22 + i * 195
        boxes.append(f'<rect x="{x}" y="59" width="172" height="128" rx="12" fill="#f6f8fb" stroke="#54708e" stroke-width="2"/>')
        boxes.append(f'<text x="{x+12}" y="85" class="num">{num}</text>')
        boxes.append(f'<text x="{x+12}" y="116" class="title">{esc(title)}</text>')
        boxes.append(f'<text x="{x+12}" y="145" class="sub">{esc(subtitle)}</text>')
        if i < len(stages) - 1:
            boxes.append(f'<path d="M {x+173} 123 L {x+192} 123" stroke="#54708e" stroke-width="2.5" marker-end="url(#arrow)"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">
<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#54708e"/></marker></defs>
<style>.num{{font:700 16px sans-serif;fill:#365a7e}} .title{{font:600 14px sans-serif;fill:#1a2a3a}} .sub{{font:12px sans-serif;fill:#4c5c68}}</style>
<rect width="{width}" height="{height}" fill="white"/>
<text x="22" y="31" style="font:700 18px sans-serif;fill:#1a2a3a">Reconstruction and assessment boundary</text>
{''.join(boxes)}
<text x="22" y="225" style="font:12px sans-serif;fill:#4c5c68">Source: Valsorda article; NIST SP 800-186 C.3.1; reproducible audit. Assessed data SHA-256: {DATA_HASH}…</text>
</svg>'''
    (HERE / "selection.svg").write_text(svg)


def trace_plot() -> None:
    published = [
        {"bits": int(row["p_hex"], 16).bit_length(), "label": name, "value": row["trace_normalized"], "kind": "published"}
        for name, row in RAW["published_controls"].items()
        if int(row["p_hex"], 16).bit_length() in (192, 224, 239, 256)
    ]
    skipped = [
        {"bits": int(row["p_hex"], 16).bit_length(), "label": str(row["seed_ordinal_one_based"]), "value": row["trace_normalized"], "kind": "skipped"}
        for row in ASSESSED["candidate_rows"]
    ]
    groups = [192, 224, 239, 256]
    xcentre = {192: 175, 224: 445, 239: 715, 256: 985}
    parts = []
    for tick in (-1, -0.5, 0, 0.5, 1):
        y = 440 - 300 * (tick + 1) / 2
        color = "#8b9baa" if tick == 0 else "#e5ebf1"
        stroke_width = 2 if tick == 0 else 1
        parts.append(f'<line x1="92" y1="{y:.1f}" x2="1095" y2="{y:.1f}" stroke="{color}" stroke-width="{stroke_width}"/>')
        parts.append(f'<text x="75" y="{y+4:.1f}" text-anchor="end" class="tick">{tick:g}</text>')
    for bits in groups:
        cx = xcentre[bits]
        parts.append(f'<text x="{cx}" y="479" text-anchor="middle" class="xtick">{bits}-bit field</text>')
        values = [r for r in published + skipped if r["bits"] == bits]
        pub = sorted([r for r in values if r["kind"] == "published"], key=lambda r: r["label"])
        unpub = sorted([r for r in values if r["kind"] == "skipped"], key=lambda r: int(r["label"]))
        for i, row in enumerate(pub):
            x = cx - 82 + i * 30
            y = 440 - 300 * (row["value"] + 1) / 2
            parts.append(f'<rect x="{x-5:.1f}" y="{y-5:.1f}" width="10" height="10" fill="#31678f"/>')
            parts.append(f'<text x="{x:.1f}" y="{y-11:.1f}" text-anchor="middle" class="label">{esc(row["label"].replace("prime", "p").replace("secp", "p"))}</text>')
        for i, row in enumerate(unpub):
            x = cx + 22 + i * 28
            y = 440 - 300 * (row["value"] + 1) / 2
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="#d16531"/>')
            parts.append(f'<text x="{x:.1f}" y="{y+20:.1f}" text-anchor="middle" class="label">#{esc(row["label"])}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="1180" height="560" viewBox="0 0 1180 560">
<style>.tick,.xtick{{font:14px sans-serif;fill:#334b60}}.label{{font:11px sans-serif;fill:#263a4c}}</style>
<rect width="1180" height="560" fill="white"/>
<text x="30" y="38" style="font:700 20px sans-serif;fill:#1a2a3a">Frobenius trace across published and skipped curves</text>
<text x="30" y="65" style="font:13px sans-serif;fill:#4c5c68">Exact derived value t/(2√p), where t = p + 1 − #E(Fp). Eleven skipped seeds; eight same-field published controls.</text>
<text x="29" y="105" style="font:13px sans-serif;fill:#334b60">t/(2√p)</text>
{''.join(parts)}
<rect x="815" y="93" width="11" height="11" fill="#31678f"/><text x="836" y="103" class="xtick">published</text>
<circle cx="974" cy="99" r="6" fill="#d16531"/><text x="986" y="103" class="xtick">skipped</text>
<text x="30" y="532" style="font:12px sans-serif;fill:#4c5c68">Data: traits.json and assessed.json (SHA-256 {DATA_HASH}…). Label # is the article’s one-based seed ordinal. No sampling uncertainty.</text>
</svg>'''
    (HERE / "trace.svg").write_text(svg)


if __name__ == "__main__":
    selection_diagram()
    trace_plot()
    print("wrote selection.svg and trace.svg")
