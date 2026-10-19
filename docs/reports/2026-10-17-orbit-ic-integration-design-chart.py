"""Render the scope and complete-cost gate for orbit-base IC integration."""

from pathlib import Path


OUT = Path(__file__).with_name("2026-10-17-orbit-ic-integration-design.svg")


def rect(x, y, w, h, fill, stroke, radius=16):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="2"/>')


def line(x1, y1, x2, y2, color="#597187"):
    return (f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" '
            f'stroke="{color}" stroke-width="3" marker-end="url(#arrow)"/>')


def label(x, y, content, size=19, weight=400, color="#1c3448", anchor="start"):
    return (f'<text x="{x}" y="{y}" font-family="Arial, Helvetica, sans-serif" '
            f'font-size="{size}" font-weight="{weight}" fill="{color}" '
            f'text-anchor="{anchor}">{content}</text>')


parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="630" viewBox="0 0 1200 630">',
    '<defs><marker id="arrow" markerWidth="10" markerHeight="10" refX="8" refY="5" '
    'orient="auto"><path d="M0 0 L10 5 L0 10" fill="#597187"/></marker></defs>',
    '<rect width="1200" height="630" fill="#fbfcfe"/>',
    label(55, 55, "Orbit-base evidence to full index-calculus cost", 31, 700),
    label(55, 91, "Accepted finite receipts feed a new same-point, cold-job gate; their ratios are not combined.", 18, 400, "#4c657a"),
    rect(55, 132, 505, 142, "#edf3f8", "#85a6bf"),
    label(78, 167, "N53 complete IC comparator", 22, 700),
    label(78, 199, "Cold IC median: 3.081 s", 18),
    label(78, 225, "Paired IC / strengthened rho: 3.295", 18),
    label(78, 251, "75-column signed Frobenius-orbit base", 16, 400, "#526c80"),
    rect(640, 132, 505, 142, "#eaf6f1", "#75ad99"),
    label(663, 167, "N23 point-decomposition receipt", 22, 700),
    label(663, 199, "Canonical / expanded, 512 queries: 0.647", 18),
    label(663, 225, "Table saved time; queries cost slightly more", 18),
    label(663, 251, "Different curve, base, and target panel", 16, 400, "#527366"),
    line(310, 276, 440, 321),
    line(890, 276, 760, 321),
    rect(310, 323, 580, 115, "#fff4dc", "#d6a44a"),
    label(600, 359, "Proposed N53 same-base integration", 23, 700, anchor="middle"),
    label(600, 387, "A  Exact support + inverse witness replay", 17, anchor="middle"),
    label(600, 414, "B  Paired complete IC + matched rho on unseen points", 17, anchor="middle"),
    line(600, 440, 600, 477),
    rect(145, 478, 910, 91, "#f3f0fb", "#9b89bf"),
    label(600, 511, "Full cost: base selection + build + table + relations + rank/LA", 18, 700, anchor="middle"),
    label(600, 540, "+ target extraction + certificates + verification + I/O; CPU, wall, RSS", 17, anchor="middle"),
    label(55, 606, "Next: freeze target-blind elite-base selection separately; 50–63-bit prime/binary and m=2..8 remain open.", 16, 400, "#455f72"),
    '</svg>',
]

OUT.write_text("\n".join(parts) + "\n")
