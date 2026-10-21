"""Render exact input monomial occurrences from common-target systems."""

import gzip
import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "research/icperf_prime_475_target_systems_20261017/systems.json.gz"
OUTPUT = Path(__file__).with_name("2026-10-17-prime-475-target-systems.svg")


def render() -> str:
    record = json.load(gzip.open(SOURCE, "rt"))
    assert record["schema"] == "icperf-prime-475-target-systems-v1"
    series = [
        ("random direct", "random", "direct", "#2876a8"),
        ("small-x direct", "small_x", "direct", "#748891"),
        ("coset quadratic lift", "coset", "quadratic_lift", "#dc8c3e"),
        ("coset direct", "coset", "direct", "#b14930"),
    ]
    by_key = {(row["m"], row["arm"]): row for row in record["systems"]}
    left, top, right, bottom = 110, 115, 865, 555
    xcoord = lambda m: left + (m - 2) * (right-left) / 6
    ycoord = lambda value: bottom - (math.log10(value)-1) * (bottom-top) / 3
    parts = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="960" height="720" viewBox="0 0 960 720">',
        '<rect width="960" height="720" fill="white"/>',
        '<text x="55" y="44" font-family="sans-serif" font-size="23" font-weight="bold">Common-target 475-point prime input support</text>',
        '<text x="55" y="71" font-family="sans-serif" font-size="14">Seven public known-answer targets, m=2…8; 21 exact arm-by-arity systems</text>',
        f'<path d="M{left} {top}V{bottom}H{right}" stroke="#333" fill="none"/>',
    ]
    for value in (10, 100, 1000, 10000):
        y = ycoord(value)
        parts += [f'<path d="M{left} {y:.1f}H{right}" stroke="#e1e5e7"/>',
                  f'<text x="98" y="{y+4:.1f}" text-anchor="end" font-family="sans-serif" font-size="13">{value:,}</text>']
    for m in range(2,9):
        x = xcoord(m)
        parts += [f'<text x="{x:.1f}" y="{bottom+24}" text-anchor="middle" font-family="sans-serif" font-size="13">{m}</text>']
    for index, (label, arm, encoding, color) in enumerate(series):
        points = [(xcoord(m), ycoord(by_key[(m,arm)]["encodings"][encoding]["monomial_occurrences"]))
                  for m in range(2,9)]
        path = " ".join(("M" if i==0 else "L")+f"{x:.1f},{y:.1f}" for i,(x,y) in enumerate(points))
        parts.append(f'<path d="{path}" fill="none" stroke="{color}" stroke-width="3"/>')
        parts += [f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="{color}"/>' for x,y in points]
        ly = 603 + index*24
        parts += [f'<path d="M160 {ly}H192" stroke="{color}" stroke-width="3"/>',
                  f'<text x="202" y="{ly+4}" font-family="sans-serif" font-size="13">{label}</text>']
    parts += [
        f'<text x="{(left+right)/2:.1f}" y="{bottom+47}" text-anchor="middle" font-family="sans-serif" font-size="14">Summands m</text>',
        '<text transform="translate(28,340) rotate(-90)" text-anchor="middle" font-family="sans-serif" font-size="14">Input monomial occurrences (log scale)</text>',
        '<text x="55" y="690" font-family="sans-serif" font-size="11">Exact algebraic input counts; not solver matrix size or observed cost.</text>',
        f'<text x="55" y="707" font-family="sans-serif" font-size="10">Source SHA-256: {hashlib.sha256(SOURCE.read_bytes()).hexdigest()}</text>',
        '</svg>',
    ]
    return "\n".join(parts)+"\n"


if __name__ == "__main__":
    OUTPUT.write_text(render())
    print(OUTPUT)
