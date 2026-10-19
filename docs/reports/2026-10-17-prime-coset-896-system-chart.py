"""Render exact input counts for the two archived prime coset candidates."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OLD = ROOT / "research/icperf_prime_coset_quadratic_20261017/system.json"
NEW = ROOT / "research/icperf_prime_coset_896_system_20261017/systems.json"
OUTPUT = Path(__file__).with_name("2026-10-17-prime-coset-896-system.svg")


def render() -> str:
    old_raw, new_raw = OLD.read_bytes(), NEW.read_bytes()
    old, new = json.loads(old_raw), json.loads(new_raw)
    older = old["arity_grid_input_counts"]
    newer = new["arities"]
    assert [r["m"] for r in older] == [r["m"] for r in newer] == list(range(2, 9))
    panels = [("Lifted variables", "variable_count", 125, 285, 115),
              ("Lifted monomial occurrences", "monomial_occurrences", 370, 530, 325)]
    colors = {"old": "#2760a8", "new": "#c05435"}
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="740" viewBox="0 0 960 740">',
        '<rect width="960" height="740" fill="white"/>',
        '<text x="55" y="42" font-family="sans-serif" font-size="23" font-weight="bold">Prime coset systems: m=2…8 exact input counts</text>',
        '<text x="55" y="68" font-family="sans-serif" font-size="14">Same 63-bit curve; d=788 has 380 columns, d=896 has 475. No solver costs measured.</text>',
    ]
    for title, key, top, bottom, ymax in panels:
        left, right = 90, 900
        parts.extend([
            f'<text x="90" y="{top-15}" font-family="sans-serif" font-size="18" font-weight="bold">{title}</text>',
            f'<path d="M{left} {top}V{bottom}H{right}" stroke="#333" fill="none"/>',
        ])
        for value in (0, round(ymax / 2), ymax):
            y = bottom - value / ymax * (bottom-top)
            parts.append(f'<path d="M{left} {y:.1f}H{right}" stroke="#e2e2e2"/>')
            parts.append(f'<text x="78" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{value}</text>')
        for kind, rows in (("old", older), ("new", newer)):
            coords = []
            for i, row in enumerate(rows):
                value = row["lifted"][key]
                x = left + i * (right-left)/6
                y = bottom - value / ymax * (bottom-top)
                coords.append((x, y))
            points = " ".join(f"{x:.1f},{y:.1f}" for x, y in coords)
            parts.append(f'<polyline points="{points}" fill="none" stroke="{colors[kind]}" stroke-width="3"/>')
            for x, y in coords:
                parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{colors[kind]}"/>')
        for i, row in enumerate(older):
            x = left + i * (right-left)/6
            parts.append(f'<text x="{x:.1f}" y="{bottom+18}" text-anchor="middle" font-family="sans-serif" font-size="12">m={row["m"]}</text>')
    parts.extend([
        '<rect x="95" y="570" width="315" height="54" rx="7" fill="#eaf1f9" stroke="#2760a8"/>',
        '<text x="252" y="602" text-anchor="middle" font-family="sans-serif" font-size="15">d=788: 380 columns, 12 gates/x</text>',
        '<path d="M413 597H505" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<rect x="510" y="570" width="350" height="54" rx="7" fill="#faeee9" stroke="#c05435"/>',
        '<text x="685" y="602" text-anchor="middle" font-family="sans-serif" font-size="15">d=896: 475 columns, 11 gates/x</text>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#333"/></marker></defs>',
        '<text x="95" y="655" font-family="sans-serif" font-size="13">All lifted systems have maximum input degree 4. Base sizes differ; counts do not predict Gröbner degree or speed.</text>',
        f'<text x="55" y="695" font-family="sans-serif" font-size="11">d=788 SHA-256: {hashlib.sha256(old_raw).hexdigest()}</text>',
        f'<text x="55" y="714" font-family="sans-serif" font-size="11">d=896 SHA-256: {hashlib.sha256(new_raw).hexdigest()}</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render())
    print(OUTPUT)
