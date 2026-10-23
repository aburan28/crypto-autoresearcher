"""Render exact membership support and x-candidate counts for three 475-point bases."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/icperf_prime_475_controls_20261017/controls.json"
OUTPUT = Path(__file__).with_name("2026-10-17-prime-475-controls.svg")


def render() -> str:
    raw = SOURCE.read_bytes()
    record = json.loads(raw)
    assert record["schema"] == "icperf-prime-475-controls-v1"
    by_kind = {a["kind"]: a for a in record["controls"]}
    rows = [
        ("d=896 coset", 2, 896, "#bb5933"),
        ("random", by_kind["random"]["membership_nonzero_terms"],
         by_kind["random"]["draw_count"], "#317aa6"),
        ("small x", by_kind["small_x"]["membership_nonzero_terms"],
         by_kind["small_x"]["draw_count"], "#71858c"),
    ]
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="720" viewBox="0 0 960 720">',
        '<rect width="960" height="720" fill="white"/>',
        '<text x="55" y="42" font-family="sans-serif" font-size="23" font-weight="bold">Matched 475-point prime bases: exact input counts</text>',
        '<text x="55" y="68" font-family="sans-serif" font-size="14">Same certified 63-bit curve; one target-blind coset and two deterministic controls</text>',
    ]
    for title, column, maximum, top, bottom in (("Membership polynomial nonzero terms", 1, 500, 125, 310),
                                                 ("Candidate x-values examined", 2, 1000, 380, 565)):
        left, right = 115, 885
        parts.append(f'<text x="115" y="{top-18}" font-family="sans-serif" font-size="18" font-weight="bold">{title}</text>')
        parts.append(f'<path d="M{left} {top}V{bottom}H{right}" stroke="#333" fill="none"/>')
        for tick in (0, maximum // 2, maximum):
            y = bottom - tick / maximum * (bottom-top)
            parts.append(f'<path d="M{left} {y:.1f}H{right}" stroke="#e2e2e2"/>')
            parts.append(f'<text x="104" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="12">{tick}</text>')
        for i, (label, support, draws, color) in enumerate(rows):
            value = support if column == 1 else draws
            x = left + 110 + i * 250
            y = bottom - value / maximum * (bottom-top)
            parts.append(f'<rect x="{x}" y="{y:.1f}" width="75" height="{bottom-y:.1f}" fill="{color}"/>')
            parts.append(f'<text x="{x+37.5:.1f}" y="{y-7:.1f}" text-anchor="middle" font-family="sans-serif" font-size="13">{value}</text>')
            parts.append(f'<text x="{x+37.5:.1f}" y="{bottom+20}" text-anchor="middle" font-family="sans-serif" font-size="12">{label}</text>')
    parts.extend([
        '<rect x="75" y="610" width="200" height="49" rx="7" fill="#f0f4f6" stroke="#71858c"/>',
        '<text x="175" y="640" text-anchor="middle" font-family="sans-serif" font-size="14">475 curve points each</text>',
        '<path d="M278 635H340" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<rect x="345" y="610" width="255" height="49" rx="7" fill="#eaf1f9" stroke="#317aa6"/>',
        '<text x="472" y="640" text-anchor="middle" font-family="sans-serif" font-size="14">different exact x predicates</text>',
        '<path d="M603 635H665" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>',
        '<rect x="670" y="610" width="210" height="49" rx="7" fill="#faeee9" stroke="#bb5933"/>',
        '<text x="775" y="640" text-anchor="middle" font-family="sans-serif" font-size="14">solver cost unknown</text>',
        '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0 0L10 5L0 10Z" fill="#333"/></marker></defs>',
        f'<text x="55" y="690" font-family="sans-serif" font-size="11">Control record SHA-256: {hashlib.sha256(raw).hexdigest()}</text>',
        '</svg>',
    ])
    return "\n".join(parts) + "\n"


if __name__ == "__main__":
    OUTPUT.write_text(render())
    print(OUTPUT)
