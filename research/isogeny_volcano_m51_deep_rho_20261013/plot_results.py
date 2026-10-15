#!/usr/bin/env python3
"""Render the additive diagnostic interval figure as deterministic SVG."""

from __future__ import annotations

import argparse
import csv
import hashlib
from pathlib import Path
from xml.sax.saxutils import escape


WIDTH = 1550
HEIGHT = 1200
LEFT = 265
RIGHT = 1360


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def line(x1: float, y1: float, x2: float, y2: float, **attrs: object) -> str:
    values = {"x1": x1, "y1": y1, "x2": x2, "y2": y2, **attrs}
    return "<line " + " ".join(f'{key.replace("_", "-")}="{value}"' for key, value in values.items()) + "/>"


def text(x: float, y: float, value: str, **attrs: object) -> str:
    values = {"x": x, "y": y, **attrs}
    return (
        "<text "
        + " ".join(f'{key.replace("_", "-")}="{entry}"' for key, entry in values.items())
        + f">{escape(value)}</text>"
    )


def scale(value: float, low: float, high: float) -> float:
    return LEFT + (value - low) * (RIGHT - LEFT) / (high - low)


def axis(parts: list[str], y1: int, y2: int, low: float, high: float, ticks: list[float]) -> None:
    for tick in ticks:
        x = scale(tick, low, high)
        parts.append(line(x, y1, x, y2, stroke="#d8dee9", stroke_width="1"))
        parts.append(text(x, y2 + 28, f"{tick:+.2f}", text_anchor="middle", font_size="17", fill="#263238"))
    zero = scale(0.0, low, high)
    parts.append(line(zero, y1, zero, y2, stroke="#1f2937", stroke_width="2"))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contrasts", type=Path, required=True)
    parser.add_argument("--aa", type=Path, required=True)
    parser.add_argument("--analysis", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    contrast_rows = rows(args.contrasts)
    aa_rows = rows(args.aa)
    if len(contrast_rows) != 10 or len(aa_rows) != 4:
        raise ValueError("unexpected summary row count")
    analysis_sha = hashlib.sha256(args.analysis.read_bytes()).hexdigest()

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="#ffffff"/>',
        text(45, 52, "m=51 four-level native-rho diagnostics", font_size="30", font_weight="700", fill="#111827"),
        '<rect x="40" y="72" width="1470" height="58" rx="8" fill="#fff1f2" stroke="#be123c" stroke-width="2"/>',
        text(WIDTH / 2, 108, "DIAGNOSTIC ONLY — A/A gate failed; all inferential and equivalence labels are withheld", text_anchor="middle", font_size="22", font_weight="700", fill="#9f1239"),
        text(45, 165, "Primary contrast family: computed simultaneous 95% intervals (n=32 pair clusters)", font_size="21", font_weight="700", fill="#111827"),
        text(45, 193, "2I is derived from I and is not a tenth family member; only B−P is exactly calibrated-weight paired.", font_size="16", fill="#475569"),
    ]

    top_y1 = 220
    top_step = 47
    top_y2 = top_y1 + top_step * len(contrast_rows)
    low, high = -0.17, 0.17
    axis(parts, top_y1 - 13, top_y2 - 17, low, high, [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15])
    for index, row in enumerate(contrast_rows):
        y = top_y1 + index * top_step
        estimate = float(row["estimate_bits"])
        lower = float(row["diagnostic_simultaneous_lower_bits"])
        upper = float(row["diagnostic_simultaneous_upper_bits"])
        family = row["included_in_nine_contrast_family"] == "true"
        colour = "#2563eb" if family else "#7c3aed"
        parts.append(text(235, y + 6, row["contrast_id"], text_anchor="end", font_size="18", font_weight="700" if family else "400", fill="#111827"))
        parts.append(line(scale(lower, low, high), y, scale(upper, low, high), y, stroke=colour, stroke_width="4"))
        parts.append(line(scale(lower, low, high), y - 8, scale(lower, low, high), y + 8, stroke=colour, stroke_width="3"))
        parts.append(line(scale(upper, low, high), y - 8, scale(upper, low, high), y + 8, stroke=colour, stroke_width="3"))
        parts.append(f'<circle cx="{scale(estimate, low, high):.3f}" cy="{y}" r="7" fill="{colour}"/>')
        parts.append(text(RIGHT + 12, y + 6, f"{estimate:+.5f} bit", font_size="16", fill="#334155"))
    parts.append(text((LEFT + RIGHT) / 2, top_y2 + 25, "log2 calibrated mean-walk-work contrast (bits)", text_anchor="middle", font_size="18", fill="#111827"))

    aa_title_y = top_y2 + 76
    parts.append(text(45, aa_title_y, "Held-out A/A control: computed simultaneous 99% intervals (n=32 pair clusters)", font_size="21", font_weight="700", fill="#111827"))
    parts.append(text(45, aa_title_y + 27, "Frozen practical-equivalence margin: ±0.15 bit. A and B cross the margin; therefore the family gate fails.", font_size="16", fill="#475569"))
    aa_y1 = aa_title_y + 68
    aa_step = 48
    aa_y2 = aa_y1 + aa_step * len(aa_rows)
    aa_low, aa_high = -0.18, 0.18
    band_left = scale(-0.15, aa_low, aa_high)
    band_right = scale(0.15, aa_low, aa_high)
    parts.append(f'<rect x="{band_left:.3f}" y="{aa_y1 - 21}" width="{band_right - band_left:.3f}" height="{aa_y2 - aa_y1 + 21}" fill="#ecfdf5"/>')
    axis(parts, aa_y1 - 21, aa_y2 - 15, aa_low, aa_high, [-0.15, -0.10, -0.05, 0.0, 0.05, 0.10, 0.15])
    for boundary in (-0.15, 0.15):
        x = scale(boundary, aa_low, aa_high)
        parts.append(line(x, aa_y1 - 21, x, aa_y2 - 15, stroke="#059669", stroke_width="2", stroke_dasharray="8 6"))
    for index, row in enumerate(aa_rows):
        y = aa_y1 + index * aa_step
        estimate = float(row["estimate_bits"])
        lower = float(row["diagnostic_simultaneous_lower_bits"])
        upper = float(row["diagnostic_simultaneous_upper_bits"])
        passed = row["within_equivalence_margin"] == "true"
        colour = "#047857" if passed else "#be123c"
        parts.append(text(235, y + 6, row["arm"], text_anchor="end", font_size="18", font_weight="700", fill=colour))
        parts.append(line(scale(lower, aa_low, aa_high), y, scale(upper, aa_low, aa_high), y, stroke=colour, stroke_width="4"))
        parts.append(line(scale(lower, aa_low, aa_high), y - 8, scale(lower, aa_low, aa_high), y + 8, stroke=colour, stroke_width="3"))
        parts.append(line(scale(upper, aa_low, aa_high), y - 8, scale(upper, aa_low, aa_high), y + 8, stroke=colour, stroke_width="3"))
        parts.append(f'<circle cx="{scale(estimate, aa_low, aa_high):.3f}" cy="{y}" r="7" fill="{colour}"/>')
        result = "inside" if passed else "CROSSES"
        parts.append(text(RIGHT + 12, y + 6, f"{result} ±0.15", font_size="16", font_weight="700" if not passed else "400", fill=colour))
    parts.append(text((LEFT + RIGHT) / 2, aa_y2 + 24, "A/A stream difference (bits)", text_anchor="middle", font_size="18", fill="#111827"))
    parts.append(text(45, HEIGHT - 52, f"Source: analysis.json SHA-256 {analysis_sha}", font_size="13", fill="#64748b"))
    parts.append(text(45, HEIGHT - 24, "No causal conductor, transfer, weak-curve, end-to-end, or security-bit claim is permitted.", font_size="15", font_weight="700", fill="#9f1239"))
    parts.append("</svg>")
    args.out.write_text("\n".join(parts) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
