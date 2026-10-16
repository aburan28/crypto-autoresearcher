"""Render the P-224 twist comparison from the verified factors."""

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
v = json.loads((HERE / "verification.json").read_text())
values = [
    (777, v["other_p224_slots_largest_prime_factor_bits"]["777"], "Passed over"),
    (1485, v["new_largest_prime_factor_bits"], "Passed over"),
    (5736, v["other_p224_slots_largest_prime_factor_bits"]["5736"], "Passed over"),
    (7026, v["published_largest_prime_factor_bits"], "Published P-224"),
]
width, height = 760, 345
baseline, scale = 273, 1.55
lines = [
    f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
    '<rect width="100%" height="100%" fill="#ffffff"/>',
    '<text x="34" y="31" font-family="sans-serif" font-size="18" font-weight="bold">P-224 stream: largest prime factor of twist order</text>',
    '<text x="34" y="52" font-family="sans-serif" font-size="12" fill="#455468">Four qualifying blocks; factor size in bits, not a security rating</text>',
]
for tick in (0, 40, 80, 120):
    y = baseline - tick * scale
    lines += [
        f'<line x1="73" y1="{y}" x2="718" y2="{y}" stroke="#dce3ea"/>',
        f'<text x="62" y="{y+4}" text-anchor="end" font-family="sans-serif" font-size="11" fill="#455468">{tick}</text>',
    ]
for i, (ordinal, bits, label) in enumerate(values):
    x = 105 + i * 156
    y = baseline - bits * scale
    color = "#2b6cb0" if label == "Passed over" else "#23865c"
    lines += [
        f'<rect x="{x}" y="{y}" width="92" height="{bits*scale}" fill="{color}"/>',
        f'<text x="{x+46}" y="{y-8}" text-anchor="middle" font-family="sans-serif" font-size="14" font-weight="bold">{bits}</text>',
        f'<text x="{x+46}" y="{baseline+20}" text-anchor="middle" font-family="sans-serif" font-size="12">slot {ordinal}</text>',
        f'<text x="{x+46}" y="{baseline+37}" text-anchor="middle" font-family="sans-serif" font-size="11" fill="#455468">{html.escape(label)}</text>',
    ]
lines += [
    '<text x="14" y="168" transform="rotate(-90 14 168)" font-family="sans-serif" font-size="11" fill="#455468">Largest prime factor (bits)</text>',
    '<text x="34" y="337" font-family="sans-serif" font-size="10" fill="#596579">Source: verification.json and twist_factor_probe.json; slot 1485 verified with PARI/GP 2.17.3.</text>',
    '</svg>',
]
(HERE / "p224_twist.svg").write_text("\n".join(lines) + "\n")
