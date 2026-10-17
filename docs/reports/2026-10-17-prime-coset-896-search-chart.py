"""Editable SVG of all target-blind d=896 coset preparation attempts."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/icperf_prime_coset_896_20261017/scan.json"
OUTPUT = Path(__file__).with_name("2026-10-17-prime-coset-896-search.svg")


def render() -> str:
    raw = SOURCE.read_bytes()
    data = json.loads(raw)
    assert data["schema"] == "icperf-prime-coset-896-search-v1"
    attempts = data["attempts"]
    rows = [(a["base_parameters"]["seed"], a["realized_size"]) for a in attempts]
    assert len(rows) == 16
    selected = data["selected_seed"]
    left, right, top, bottom = 90, 930, 130, 430
    lo, hi = 400, 480
    y = lambda value: bottom - (value - lo) * (bottom - top) / (hi - lo)
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="1020" height="700" viewBox="0 0 1020 700">',
        '<rect width="1020" height="700" fill="white"/>',
        '<text x="55" y="42" font-family="sans-serif" font-size="23" font-weight="bold">63-bit prime cosets: all 16 frozen seeds</text>',
        '<text x="55" y="68" font-family="sans-serif" font-size="14">Exact liftable point counts, d=896; target-blind selection by largest realized base</text>',
        f'<path d="M{left} {top}V{bottom}H{right}" stroke="#333" fill="none"/>',
    ]
    for tick in (400, 420, 440, 460, 480):
        yy = y(tick)
        parts.append(f'<path d="M{left} {yy:.1f}H{right}" stroke="#e1e1e1"/>')
        parts.append(f'<text x="78" y="{yy+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{tick}</text>')
    threshold = y(441)
    parts.append(f'<path d="M{left} {threshold:.1f}H{right}" stroke="#995d1a" stroke-width="2" stroke-dasharray="7 5"/>')
    parts.append(f'<text x="925" y="{threshold-8:.1f}" text-anchor="end" font-family="sans-serif" font-size="12" fill="#995d1a">441 count threshold</text>')
    gap = (right - left) / len(rows)
    for i, (seed, size) in enumerate(rows):
        x = left + i * gap + 8
        width = gap - 15
        yy = y(size)
        color = "#ba4d2c" if seed == selected else ("#26779e" if size >= 441 else "#9daeb6")
        parts.append(f'<rect x="{x:.1f}" y="{yy:.1f}" width="{width:.1f}" height="{bottom-yy:.1f}" fill="{color}"/>')
        parts.append(f'<text x="{x+width/2:.1f}" y="{yy-6:.1f}" text-anchor="middle" font-family="sans-serif" font-size="11">{size}</text>')
        parts.append(f'<text x="{x+width/2:.1f}" y="{bottom+18}" text-anchor="middle" font-family="sans-serif" font-size="11">{str(seed)[-2:]}</text>')
    parts.extend([
        '<text x="510" y="478" text-anchor="middle" font-family="sans-serif" font-size="13">Seed suffix (20261017…20261032); 9 of 16 reach the optimistic count threshold</text>',
        '<rect x="80" y="515" width="245" height="58" rx="7" fill="#eaf2f6" stroke="#26779e"/>',
        '<text x="202" y="549" text-anchor="middle" font-family="sans-serif" font-size="14">16 fixed seeds, full cosets</text>',
        '<path d="M328 544H375" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<rect x="380" y="515" width="245" height="58" rx="7" fill="#f5f5f5" stroke="#777"/>',
        '<text x="502" y="549" text-anchor="middle" font-family="sans-serif" font-size="14">lift every x, retain misses</text>',
        '<path d="M628 544H675" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<rect x="680" y="515" width="245" height="58" rx="7" fill="#f9ece8" stroke="#ba4d2c"/>',
        '<text x="802" y="549" text-anchor="middle" font-family="sans-serif" font-size="14">seed 20261027: 475 points</text>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#333"/></marker></defs>',
        '<text x="55" y="610" font-family="sans-serif" font-size="13">Dashed threshold is necessary for count capacity; it does not establish coverage, relation yield, or solver speed.</text>',
        f'<text x="55" y="655" font-family="sans-serif" font-size="11">Scan SHA-256: {hashlib.sha256(raw).hexdigest()}</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render())
    print(OUTPUT)
