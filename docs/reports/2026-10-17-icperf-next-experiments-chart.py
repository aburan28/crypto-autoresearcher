"""Render exact signed-multiset count ceilings for two prepared ICPERF bases.

The ordinate is a tuple-count / subgroup-order ratio, not measured relation
yield and not a probability when it exceeds one.  No solver is called.
"""

from __future__ import annotations

import math
from pathlib import Path


HERE = Path(__file__).resolve().parent
OUT = HERE / "2026-10-17-icperf-next-experiments.svg"
ARITIES = range(2, 9)
SERIES = (
    ("ordinary binary: B=316, r=576460752557211763", 316, 576460752557211763, "#1678a3"),
    ("prime: B=475, r=9223372018953067627", 475, 9223372018953067627, "#b35a25"),
)
LEFT, RIGHT, TOP, BOTTOM = 100, 785, 46, 415
LOG_MIN, LOG_MAX = -14, 1


def x(m: int) -> float:
    return LEFT + (m - 2) * (RIGHT - LEFT) / 6


def y(value: float) -> float:
    return BOTTOM - (math.log10(value) - LOG_MIN) * (BOTTOM - TOP) / (LOG_MAX - LOG_MIN)


def render() -> str:
    lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" width="900" height="510" viewBox="0 0 900 510">',
        '<rect width="900" height="510" fill="white"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#253342} .small{font-size:13px} .axis{stroke:#536476;stroke-width:1.4} .grid{stroke:#dfe5eb;stroke-width:1}</style>',
        '<text x="100" y="24" font-size="18" font-weight="bold">Exact tuple-count ceilings across arity</text>',
        '<text x="100" y="44" class="small">C(2B+m-1,m) / r; derived upper count, never observed relation yield</text>',
    ]
    for exponent in (-14, -11, -8, -5, -2, 0):
        yy = y(10**exponent)
        lines.append(f'<line x1="{LEFT}" y1="{yy:.1f}" x2="{RIGHT}" y2="{yy:.1f}" class="grid"/>')
        lines.append(f'<text x="{LEFT-12}" y="{yy+4:.1f}" class="small" text-anchor="end">10^{exponent}</text>')
    lines += [
        f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{BOTTOM}" class="axis"/>',
        f'<line x1="{LEFT}" y1="{BOTTOM}" x2="{RIGHT}" y2="{BOTTOM}" class="axis"/>',
    ]
    for m in ARITIES:
        xx = x(m)
        lines.append(f'<line x1="{xx:.1f}" y1="{BOTTOM}" x2="{xx:.1f}" y2="{BOTTOM+6}" class="axis"/>')
        lines.append(f'<text x="{xx:.1f}" y="{BOTTOM+24}" class="small" text-anchor="middle">{m}</text>')
    lines.append(f'<text x="{(LEFT+RIGHT)/2:.1f}" y="{BOTTOM+49}" class="small" text-anchor="middle">summands m</text>')
    for label, base_size, order, color in SERIES:
        values = [math.comb(2 * base_size + m - 1, m) / order for m in ARITIES]
        points = " ".join(f"{x(m):.1f},{y(value):.1f}" for m, value in zip(ARITIES, values))
        lines.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="3"/>')
        for m, value in zip(ARITIES, values):
            lines.append(f'<circle cx="{x(m):.1f}" cy="{y(value):.1f}" r="4.5" fill="{color}"/>')
    lines += [
        '<line x1="100" y1="487" x2="135" y2="487" stroke="#1678a3" stroke-width="3"/>',
        '<text x="142" y="492" class="small">ordinary binary B=316</text>',
        '<line x1="385" y1="487" x2="420" y2="487" stroke="#b35a25" stroke-width="3"/>',
        '<text x="427" y="492" class="small">prime B=475</text>',
        '<text x="612" y="492" class="small">Above 1 is still only a count ceiling</text>',
        '</svg>',
    ]
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    OUT.write_text(render())
    print(OUT)
