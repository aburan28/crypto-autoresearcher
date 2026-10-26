"""Draw source-reported, within-run N83 K600/K899 ratios only."""

from pathlib import Path

OUT = Path(__file__).with_name("figure.svg")

rows = [
    ("Cold total, base build excluded", 1.1873, 1.1247, 1.2523, 82),
    ("Rank stage", 1.5176, 1.4149, 1.6235, 138),
]


def x(value: float) -> float:
    return 360 + (value - 0.9) * 500


parts = [
    '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="260" viewBox="0 0 900 260">',
    '<rect width="900" height="260" fill="white"/>',
    '<text x="28" y="30" font-family="sans-serif" font-size="18" font-weight="bold">N83 K899 versus K600, older rank-probe producer</text>',
    '<text x="28" y="50" font-family="sans-serif" font-size="12" fill="#4b5563">Run 39306394645 · 20 targets, four rank blocks · K600 / K899 · source-reported intervals</text>',
    f'<line x1="{x(1):.1f}" y1="64" x2="{x(1):.1f}" y2="184" stroke="#999" stroke-dasharray="4 4"/>',
]
for label, value, lo, hi, y in rows:
    parts.extend([
        f'<text x="28" y="{y+5}" font-family="sans-serif" font-size="13">{label}</text>',
        f'<line x1="{x(lo):.1f}" y1="{y}" x2="{x(hi):.1f}" y2="{y}" stroke="#174a7e" stroke-width="4"/>',
        f'<line x1="{x(lo):.1f}" y1="{y-7}" x2="{x(lo):.1f}" y2="{y+7}" stroke="#174a7e" stroke-width="2"/>',
        f'<line x1="{x(hi):.1f}" y1="{y-7}" x2="{x(hi):.1f}" y2="{y+7}" stroke="#174a7e" stroke-width="2"/>',
        f'<circle cx="{x(value):.1f}" cy="{y}" r="6" fill="#174a7e"/>',
        f'<text x="{x(hi)+14:.1f}" y="{y+5}" font-family="sans-serif" font-size="12">{value:.4f} [{lo:.4f}, {hi:.4f}]</text>',
    ])
for tick in (1.0, 1.2, 1.4, 1.6):
    parts.extend([
        f'<line x1="{x(tick):.1f}" y1="190" x2="{x(tick):.1f}" y2="196" stroke="#333"/>',
        f'<text x="{x(tick)-12:.1f}" y="213" font-family="sans-serif" font-size="12">{tick:.1f}</text>',
    ])
parts.extend([
    '<text x="28" y="242" font-family="sans-serif" font-size="11" fill="#6b7280">Intervals belong to the old producer; no current-rank-finder K899 observation is plotted.</text>',
    '</svg>',
])
OUT.write_text("\n".join(parts) + "\n")
