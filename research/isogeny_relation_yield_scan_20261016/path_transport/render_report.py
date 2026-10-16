"""Render the fixed check-vertex transport diagrams from saved checkpoints."""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
CONFIG = {
    "P29": ("walk-p29-2048-attempt2.jsonl", "p29-twoedge-attempt1", 8),
    "P37": ("walk-p37-256.jsonl", "p37-twoedge-attempt1", 4),
}


def load():
    output = {}
    for stratum, (walk_name, control_dir, last) in CONFIG.items():
        with (ROOT / walk_name).open() as handle:
            header = json.loads(next(handle))
        directory = HERE / "controls" / control_dir
        records = [json.loads((directory / f"edge-{i:04d}.json").read_text())
                   for i in range(last + 1)]
        output[stratum] = (header, records)
    return output


def svg_start(width, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img">',
            '<style>text{font-family:Helvetica,Arial,sans-serif;fill:#152238}'
            '.title{font-size:22px;font-weight:700}.subtitle{font-size:14px}'
            '.node{font-size:12px}.head{font-size:15px;font-weight:700}'
            '.edge{font-size:12px;fill:#35506c}</style>',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" '
            'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
            '<path d="M0 0 L10 5 L0 10 Z" fill="#55728e"/></marker></defs>']


def node(parts, x, y, index, record):
    model = record["model"]
    check = record["check_vertex"]
    color = "#e4f6ed" if check else "#eef2f8"
    stroke = "#33875f" if check else "#7389a3"
    parts.append(f'<rect x="{x}" y="{y}" width="155" height="80" rx="9" '
                 f'fill="{color}" stroke="{stroke}" stroke-width="1.5"/>')
    parts.append(f'<text x="{x+8}" y="{y+17}" class="head">E{index}'
                 f'{" • check" if check else ""}</text>')
    for offset, key in enumerate(("a", "b", "j"), 1):
        parts.append(f'<text x="{x+8}" y="{y+17+18*offset}" class="node">'
                     f'{key}={model[key]}</text>')


def arrow(parts, start_x, end_x, y, label=True):
    parts.append(f'<line x1="{start_x}" y1="{y}" x2="{end_x}" y2="{y}" '
                 'stroke="#55728e" stroke-width="2" marker-end="url(#arrow)"/>')
    if label:
        parts.append(f'<text x="{(start_x+end_x)/2}" y="{y-9}" text-anchor="middle" '
                     'class="edge">7</text>')


def chain_svg(data):
    parts = svg_start(1000, 610)
    parts.append('<text x="30" y="34" class="title">Saved degree-7 path transport</text>')
    parts.append('<text x="30" y="57" class="subtitle">'
                 'Each node is E: y²=x³+ax+b over the panel field; r is the prime subgroup order. '
                 'Green nodes are scheduled all-point checks.</text>')
    header, records = data["P29"]
    parts.append(f'<text x="30" y="91" class="head">P29: p={header["p"]}, '
                 f'r={header["r"]}, D_K={header["D_K"]}, f_π={header["f_pi"]}; '
                 f'source f_E={header["f_E"]}</text>')
    for i in range(5):
        x = 30 + i * 190
        node(parts, x, 108, i, records[i])
        if i < 4:
            arrow(parts, x + 157, x + 187, 148)
    parts.append('<path d="M 947 148 H 975 V 258 H 16 V 258 H 27" '
                 'fill="none" stroke="#55728e" stroke-width="2" marker-end="url(#arrow)"/>')
    parts.append('<text x="810" y="239" class="edge">E4 → E5, degree 7</text>')
    for i in range(5, 9):
        x = 30 + (i - 5) * 190
        node(parts, x, 218, i, records[i])
        if i < 8:
            arrow(parts, x + 157, x + 187, 258)
    header, records = data["P37"]
    parts.append(f'<text x="30" y="355" class="head">P37: p={header["p"]}, '
                 f'r={header["r"]}, D_K={header["D_K"]}, f_π={header["f_pi"]}; '
                 f'source f_E={header["f_E"]}</text>')
    for i in range(5):
        x = 30 + i * 190
        node(parts, x, 372, i, records[i])
        if i < 4:
            arrow(parts, x + 157, x + 187, 412)
    parts.append('<text x="30" y="495" class="subtitle">'
                 'All arrows: degree 7, separable, defined over Fₚ. '
                 'Non-source f_E and volcano edge direction were not independently certified here.</text>')
    parts.append('<text x="30" y="522" class="subtitle">'
                 'Evidence: T-3361 controls, graph hashes and checkpoint chains in manifest.json '
                 'and *-check1-verify.stdout.</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def timing_svg(data):
    parts = svg_start(1000, 600)
    parts.append('<text x="30" y="35" class="title">Per-edge control elapsed time</text>')
    parts.append('<text x="30" y="59" class="subtitle">'
                 'Seconds inside transport_path.py. Diagnostics from one run per edge; '
                 'not a matched performance comparison.</text>')
    for stratum, top, scale in (("P29", 100, 4.0), ("P37", 350, 20.0)):
        _, records = data[stratum]
        parts.append(f'<text x="30" y="{top}" class="head">{stratum} '
                     f'(n={len(records)-1} edges; axis 0–{scale:g} s)</text>')
        for i, record in enumerate(records[1:], 1):
            y = top + 25 + (i - 1) * 24
            value = record["elapsed_seconds"]
            width = value / scale * 660
            parts.append(f'<text x="30" y="{y+12}" class="node">E{i-1}→E{i}</text>')
            parts.append(f'<rect x="105" y="{y}" width="{width:.2f}" height="15" '
                         'fill="#4e77a4"/>')
            parts.append(f'<text x="{113+width:.2f}" y="{y+12}" class="node">'
                         f'{value:.3f} s</text>')
    parts.append('<text x="30" y="578" class="subtitle">'
                 'No CPU, RSS, hardware isolation or uncertainty estimate was recorded. '
                 'The bars are not an ECDLP cost result.</text>')
    parts.append('</svg>')
    return "\n".join(parts) + "\n"


def main():
    data = load()
    (HERE / "chain.svg").write_text(chain_svg(data))
    (HERE / "edge_times.svg").write_text(timing_svg(data))


if __name__ == "__main__":
    main()
