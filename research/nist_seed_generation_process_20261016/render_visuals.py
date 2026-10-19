#!/usr/bin/env python3
"""Render editable-source SVGs for the NIST seed process assessment."""

from __future__ import annotations

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "process_checks.json").read_text())


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def text(x, y, label, size=17, color="#152536", weight="normal", anchor="start"):
    return (f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}" '
            f'font-weight="{weight}" text-anchor="{anchor}" '
            f'font-family="Arial, Helvetica, sans-serif">{esc(label)}</text>')


def rect(x, y, w, h, fill, stroke="#31485b", radius=12):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" '
            f'rx="{radius}" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>')


def line(x1, y1, x2, y2, color="#31485b", width=2, dash=""):
    d = f' stroke-dasharray="{dash}"' if dash else ""
    return (f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" '
            f'stroke="{color}" stroke-width="{width}"{d}/>')


def svg(body, width, height):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
            f'viewBox="0 0 {width} {height}">'
            f'<rect width="100%" height="100%" fill="#f7fafc"/>{body}</svg>\n')


def process_diagram():
    parts = [text(32, 40, "What the published seeds constrain", 26, weight="bold")]
    stages = [
        (30, "Clock input t", "Six recovered values", "#dfefff"),
        (237, "48-bit lrand48", "Exact output recurrence", "#dfefff"),
        (444, "20-byte blocks", "All ten published seeds match", "#dfefff"),
        (651, "Curve tests", "Call path unknown", "#fff0d8"),
        (858, "Publication", "10 chosen / 11 passed", "#fff0d8"),
    ]
    for x, title, sub, fill in stages:
        parts.append(rect(x, 82, 184, 90, fill))
        parts.append(text(x + 92, 117, title, 18, weight="bold", anchor="middle"))
        parts.append(text(x + 92, 147, sub, 12, anchor="middle"))
    for x in (214, 421, 628, 835):
        parts.append(line(x, 127, x + 23, 127))
    parts.extend([
        text(32, 231, "Strict consecutive blocks", 21, weight="bold"),
        text(32, 263, "At most 2^46 candidate-start states, even with arbitrary timestamp retries and block ordinal."),
        text(32, 306, "Extra calls to the same RNG", 21, weight="bold"),
        text(32, 338, "At most 2^48 possible start states if candidate windows may begin at any offset."),
        text(32, 387, "Neither ceiling measures actual historical attempts or identifies the missing acceptance rule.", 17),
        line(735, 174, 735, 214, "#b46b0c", 2, "6 5"),
        text(746, 206, "Unknown decision", 14, "#9a5600"),
        text(32, 427, "Derived from POSIX LCG period and the 21 archived candidate records; process model remains conjectural.", 13, "#526477"),
    ])
    (HERE / "process_space.svg").write_text(svg("".join(parts), 1070, 452))


def stream_chart():
    streams = DATA["streams"]
    parts = [text(32, 41, "Reported qualifying blocks by reconstructed stream", 25, weight="bold")]
    for i, s in enumerate(streams):
        y = 96 + 61 * i
        name = f'{s["field_bits"]} bit / {s["timestamp"]}'
        parts.append(text(35, y + 22, name, 16))
        x0 = 310
        pub = len(s["published_slots"])
        skip = len(s["passed_over_slots"])
        ordered = [r for r in DATA["candidate_checks"] if r["timestamp"] == s["timestamp"]]
        for j, r in enumerate(ordered):
            if r["label"] == "published":
                fill, stroke = "#3f83c5", "#2b5b87"
            else:
                fill, stroke = "#e4a755", "#a56922"
            parts.append(rect(x0 + 53 * j, y, 43, 35, fill, stroke, 5))
        parts.append(text(760, y + 23, f'{skip} passed over  /  {pub} published', 15))
    parts.extend([
        rect(34, 475, 20, 20, "#e4a755", "#a56922", 3), text(64, 491, "Passed over", 14),
        rect(194, 475, 20, 20, "#3f83c5", "#2b5b87", 3), text(224, 491, "Published", 14),
        text(35, 532, "Squares follow ordinal order, not ordinal spacing; 21 reported blocks do not count historical attempts.", 14, "#526477"),
    ])
    (HERE / "stream_counts.svg").write_text(svg("".join(parts), 1080, 560))


if __name__ == "__main__":
    process_diagram()
    stream_chart()
    print("wrote process_space.svg and stream_counts.svg")
