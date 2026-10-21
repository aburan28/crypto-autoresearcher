"""Render exact prime-coset input counts from the immutable system record."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/icperf_prime_coset_quadratic_20261017/system.json"
OUTPUT = Path(__file__).with_name("2026-10-17-prime-coset-quadratic.svg")


def render() -> str:
    raw = SOURCE.read_bytes()
    rows = json.loads(raw)["arity_grid_input_counts"]
    colors = {"direct": "#2760a8", "lifted": "#c05435"}
    panels = [
        ("Variables", "variable_count", 125, 300),
        ("Monomial occurrences", "monomial_occurrences", 385, 560),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="800" viewBox="0 0 960 800">',
        '<rect width="960" height="800" fill="#ffffff"/>',
        '<text x="55" y="43" font-family="sans-serif" font-size="23" font-weight="bold">Prime coset formulation: exact input size</text>',
        '<text x="55" y="68" font-family="sans-serif" font-size="14">63-bit field, 380-point base, m=2…8; counts are structural, not solver timings</text>',
    ]
    for title, key, top, bottom in panels:
        max_value = max(row[kind][key] for row in rows for kind in colors)
        left, right = 90, 900
        parts.extend([
            f'<text x="90" y="{top-18}" font-family="sans-serif" font-size="18" font-weight="bold">{title}</text>',
            f'<path d="M{left} {top}V{bottom}H{right}" stroke="#333" fill="none"/>',
        ])
        for frac in (0, 0.5, 1):
            y = bottom - frac * (bottom - top)
            value = round(frac * max_value)
            parts.append(f'<path d="M{left} {y:.1f}H{right}" stroke="#e2e2e2"/>')
            parts.append(f'<text x="79" y="{y+5:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{value}</text>')
        for kind, color in colors.items():
            coords = []
            for i, row in enumerate(rows):
                x = left + i * (right-left)/6
                y = bottom - row[kind][key] / max_value * (bottom-top)
                coords.append((x, y))
            points = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
            parts.append(f'<polyline points="{points}" stroke="{color}" stroke-width="3" fill="none"/>')
            for x, y in coords:
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>')
        for i, row in enumerate(rows):
            x = left + i * (right-left)/6
            parts.append(f'<text x="{x:.1f}" y="{bottom+19}" text-anchor="middle" font-family="sans-serif" font-size="12">m={row["m"]}</text>')
    parts.extend([
        '<rect x="100" y="596" width="210" height="54" rx="7" stroke="#2760a8" fill="#eaf1f9"/>',
        '<text x="205" y="628" text-anchor="middle" font-family="sans-serif" font-size="17">x^788 = c</text>',
        '<path d="M312 623H355" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<rect x="360" y="596" width="250" height="54" rx="7" stroke="#c05435" fill="#faeee9"/>',
        '<text x="485" y="617" text-anchor="middle" font-family="sans-serif" font-size="14">12 gates: q_e = q_a q_b</text>',
        '<text x="485" y="638" text-anchor="middle" font-family="sans-serif" font-size="14">and q_788 = c</text>',
        '<path d="M612 623H655" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<rect x="660" y="596" width="210" height="54" rx="7" stroke="#555" fill="#f3f3f3"/>',
        '<text x="765" y="628" text-anchor="middle" font-family="sans-serif" font-size="15">same coset predicate</text>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#333"/></marker></defs>',
        '<text x="100" y="674" font-family="sans-serif" font-size="12">S3 chain retained; curve liftability and point signs checked after root extraction.</text>',
        '<circle cx="95" cy="721" r="5" fill="#2760a8"/><text x="108" y="726" font-family="sans-serif" font-size="14">Direct degree-788 coset equations</text>',
        '<circle cx="420" cy="721" r="5" fill="#c05435"/><text x="433" y="726" font-family="sans-serif" font-size="14">Quadratic lifted coset equations</text>',
        f'<text x="55" y="770" font-family="sans-serif" font-size="11">Input record SHA-256: {hashlib.sha256(raw).hexdigest()}</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render())
    print(OUTPUT)
