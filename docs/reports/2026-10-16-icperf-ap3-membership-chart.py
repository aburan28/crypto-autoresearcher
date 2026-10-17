"""Render the AP-3 implementation check and twist admission diagram as SVG."""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "experiments/EXP-ICPERF-42ef30/tests/ap3_validation_20261016_v2"
OUTPUT = Path(__file__).with_name("2026-10-16-icperf-ap3-membership.svg")


def main():
    summary = json.loads((DATA / "summary.json").read_text())
    rows = [json.loads((DATA / item["file"]).read_text()) for item in summary["rows"]]
    plot_left, plot_top, plot_width, plot_height = 115, 110, 715, 240
    labels = [f"n={row['n']}, b={row['b']}" for row in rows]
    fractions = [row["inside_by_order"] / row["samples_checked"] for row in rows]
    # The narrow range is for showing the deterministic prefix values clearly.
    lower, upper = 0.48, 0.52
    baseline_y = plot_top + plot_height * (upper - 0.5) / (upper - lower)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="650" viewBox="0 0 960 650">',
        '<rect width="960" height="650" fill="#fbfcfe"/>',
        '<text x="54" y="48" font-family="Arial" font-size="27" font-weight="700" fill="#152b3c">AP-3: independent 2E membership check</text>',
        '<text x="54" y="78" font-family="Arial" font-size="16" fill="#3d5568">50,000 deterministic affine points; order test vs x-trace: 0 disagreements</text>',
        f'<line x1="{plot_left}" y1="{baseline_y:.1f}" x2="{plot_left + plot_width}" y2="{baseline_y:.1f}" stroke="#8798a7" stroke-dasharray="5 5"/>',
        f'<text x="45" y="{baseline_y + 5:.1f}" font-family="Arial" font-size="13" fill="#526779">50%</text>',
        '<text x="115" y="101" font-family="Arial" font-size="14" fill="#243d51">Share in 2E among first 10,000 lifted affine points on each curve</text>',
    ]
    for index, (label, fraction, row) in enumerate(zip(labels, fractions, rows)):
        x = plot_left + 35 + index * 145
        y = plot_top + plot_height * (upper - fraction) / (upper - lower)
        top = min(y, baseline_y)
        height = max(2, abs(y - baseline_y))
        color = "#1f77a4" if row["b"] == 1 else "#37a182"
        parts.extend([
            f'<rect x="{x}" y="{top:.1f}" width="74" height="{height:.1f}" fill="{color}"/>',
            f'<circle cx="{x + 37}" cy="{y:.1f}" r="5" fill="{color}"/>',
            f'<text x="{x + 37}" y="{min(y, baseline_y) - 10:.1f}" text-anchor="middle" font-family="Arial" font-size="15" font-weight="700" fill="#173a4e">{100*fraction:.2f}%</text>',
            f'<text x="{x + 37}" y="375" text-anchor="middle" font-family="Arial" font-size="13" fill="#344d60">{label}</text>',
        ])
    parts.extend([
        '<text x="54" y="414" font-family="Arial" font-size="15" fill="#526779">The 50% line is a visual reference, not an inferential test; the sample is an ordered prefix.</text>',
        '<text x="54" y="462" font-family="Arial" font-size="21" font-weight="700" fill="#152b3c">Frozen twist control and AR-3 cannot both apply</text>',
        '<rect x="70" y="485" width="340" height="95" rx="9" fill="#e2f2ea" stroke="#339970"/>',
        '<text x="90" y="516" font-family="Arial" font-size="16" font-weight="700" fill="#164f39">Admitted binary curve E</text>',
        '<text x="90" y="543" font-family="Arial" font-size="15" fill="#244f3d">#E = 2r, r odd  ⇒  #E ≡ 2 (mod 4)</text>',
        '<path d="M 415 531 L 525 531" stroke="#546a7b" stroke-width="3" marker-end="url(#arrow)"/>',
        '<text x="426" y="516" font-family="Arial" font-size="13" fill="#465e70">quadratic twist</text>',
        '<rect x="530" y="485" width="360" height="95" rx="9" fill="#fce9e6" stroke="#cc6a5e"/>',
        '<text x="550" y="516" font-family="Arial" font-size="16" font-weight="700" fill="#8a372f">Twist E′ refused by AR-3</text>',
        '<text x="550" y="543" font-family="Arial" font-size="15" fill="#80423c">#E′ = 2(q+1) − #E ≡ 0 (mod 4)</text>',
        '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="3" orient="auto"><path d="M0,0 L0,6 L9,3 z" fill="#546a7b"/></marker></defs>',
        '<text x="54" y="623" font-family="Arial" font-size="12" fill="#607587">Source: EXP-ICPERF-42ef30/tests/ap3_validation_20261016_v2/summary.json and manifest.json; implementation check, no cost claim.</text>',
        '</svg>',
    ])
    OUTPUT.write_text("\n".join(parts) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
