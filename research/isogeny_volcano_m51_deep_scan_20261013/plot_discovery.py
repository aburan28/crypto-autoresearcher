#!/usr/bin/env python3
"""Render the sealed m=51 scan's cumulative hit yield as deterministic SVG."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


SCAN_END = 3_600_000_000
CUTOFF = 2_531_725_702
EXPECTED_HITS = 42
EXPECTED_CUTOFF_COUNT = 32


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--hits", type=Path, default=Path("results/hits.csv"))
    parser.add_argument("--output", type=Path, default=Path("discovery-yield.svg"))
    return parser.parse_args()


def load_hits(path: Path) -> list[int]:
    with path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    indices = [int(row["global_index"]) for row in rows]
    if len(indices) != EXPECTED_HITS:
        raise ValueError(f"expected {EXPECTED_HITS} hits, found {len(indices)}")
    if indices != sorted(indices) or len(set(indices)) != len(indices):
        raise ValueError("hit indices must be unique and sorted")
    if not all(0 <= index < SCAN_END for index in indices):
        raise ValueError("hit index outside frozen scan range")
    if sum(index <= CUTOFF for index in indices) != EXPECTED_CUTOFF_COUNT:
        raise ValueError("frozen cutoff does not contain exactly 32 hits")
    return indices


def render(indices: list[int]) -> str:
    width, height = 1200, 720
    left, right, top, bottom = 105, 55, 95, 115
    plot_w, plot_h = width - left - right, height - top - bottom
    y_max = 45

    def x_pos(value: int) -> float:
        return left + plot_w * value / SCAN_END

    def y_pos(value: int) -> float:
        return top + plot_h * (1 - value / y_max)

    step_points: list[tuple[float, float]] = [(x_pos(0), y_pos(0))]
    previous_count = 0
    for count, index in enumerate(indices, start=1):
        step_points.append((x_pos(index), y_pos(previous_count)))
        step_points.append((x_pos(index), y_pos(count)))
        previous_count = count
    step_points.append((x_pos(SCAN_END), y_pos(previous_count)))
    path = " ".join(
        ("M" if number == 0 else "L") + f" {x:.3f} {y:.3f}"
        for number, (x, y) in enumerate(step_points)
    )

    out = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        '<style>text{font-family:DejaVu Sans,Arial,sans-serif;fill:#172033}.title{font-size:25px;font-weight:700}.subtitle{font-size:15px;fill:#475569}.axis{font-size:14px}.tick{font-size:12px;fill:#475569}.note{font-size:13px;fill:#334155}.grid{stroke:#dbe3ed;stroke-width:1}.frame{stroke:#334155;stroke-width:1.5;fill:none}</style>',
        '<text class="title" x="600" y="38" text-anchor="middle">Cumulative certified discovery yield</text>',
        '<text class="subtitle" x="600" y="65" text-anchor="middle">m=51 full rank scan; 42 certified hits in [0, 3.6B); n=42</text>',
    ]

    for value in range(0, y_max + 1, 5):
        y = y_pos(value)
        out.append(f'<line class="grid" x1="{left}" y1="{y:.3f}" x2="{width-right}" y2="{y:.3f}"/>')
        out.append(f'<text class="tick" x="{left-14}" y="{y+4:.3f}" text-anchor="end">{value}</text>')

    for number in range(7):
        value = number * 600_000_000
        x = x_pos(value)
        out.append(f'<line class="grid" x1="{x:.3f}" y1="{top}" x2="{x:.3f}" y2="{height-bottom}"/>')
        out.append(f'<text class="tick" x="{x:.3f}" y="{height-bottom+25}" text-anchor="middle">{value/1_000_000_000:.1f}</text>')

    quota_y = y_pos(EXPECTED_CUTOFF_COUNT)
    out.append(f'<line x1="{left}" y1="{quota_y:.3f}" x2="{width-right}" y2="{quota_y:.3f}" stroke="#7c3aed" stroke-width="1.5" stroke-dasharray="8 6"/>')
    out.append(f'<text class="note" x="{left+10}" y="{quota_y-9:.3f}" fill="#6d28d9">frozen selection quota: 32</text>')

    cutoff_x = x_pos(CUTOFF)
    out.append(f'<line x1="{cutoff_x:.3f}" y1="{top}" x2="{cutoff_x:.3f}" y2="{height-bottom}" stroke="#ea580c" stroke-width="2" stroke-dasharray="7 6"/>')
    out.append(f'<text class="note" x="{cutoff_x+8:.3f}" y="{top+22}" fill="#c2410c">32nd selected rank</text>')
    out.append(f'<text class="note" x="{cutoff_x+8:.3f}" y="{top+42}" fill="#c2410c">2,531,725,702</text>')

    out.append(f'<path d="{path}" fill="none" stroke="#0369a1" stroke-width="3" stroke-linejoin="round"/>')
    for count, index in enumerate(indices, start=1):
        out.append(f'<circle cx="{x_pos(index):.3f}" cy="{y_pos(count):.3f}" r="3.2" fill="#0284c7"/>')

    out.extend(
        [
            f'<rect class="frame" x="{left}" y="{top}" width="{plot_w}" height="{plot_h}"/>',
            f'<text class="axis" x="{left + plot_w/2:.3f}" y="{height-35}" text-anchor="middle">Global modeled-PRP rank (billions scanned)</text>',
            f'<text class="axis" x="27" y="{top + plot_h/2:.3f}" text-anchor="middle" transform="rotate(-90 27 {top + plot_h/2:.3f})">Cumulative certified hits</text>',
            f'<text class="note" x="{left}" y="{height-9}">Source: results/hits.csv; sealed run tree m51-deep-scan-run-d2dd22d7. No uncertainty interval was estimated for this descriptive curve.</text>',
            '</svg>',
            '',
        ]
    )
    return "\n".join(out)


def main() -> None:
    args = parse_args()
    args.output.write_text(render(load_hits(args.hits)), encoding="utf-8")


if __name__ == "__main__":
    main()
