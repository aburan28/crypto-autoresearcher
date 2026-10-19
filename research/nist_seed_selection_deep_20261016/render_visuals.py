"""Render the exact reported candidate ordinals by reconstructed stream."""

from __future__ import annotations

import html
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
DATA = json.loads((HERE / "selection_matrix.json").read_text())
WIDTH, HEIGHT = 1420, 530
X0, X1 = 260, 1310
MAX_ORDINAL = 7500


def x(ordinal: int) -> float:
    return X0 + (X1 - X0) * ordinal / MAX_ORDINAL


def main() -> None:
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" '
        f'viewBox="0 0 {WIDTH} {HEIGHT}" role="img" '
        'aria-label="Published and passed-over qualifying seeds by candidate ordinal">',
        '<rect width="100%" height="100%" fill="#fffdf9"/>',
        '<style>text{font-family:Arial,Helvetica,sans-serif;fill:#263746}'
        '.title{font-size:24px;font-weight:700}.label{font-size:16px}'
        '.small{font-size:13px;fill:#526573}.tick{font-size:13px;fill:#526573}</style>',
        '<text x="35" y="40" class="title">Which qualifying seed slots were published?</text>',
        '<circle cx="1070" cy="32" r="7" fill="#1d5d93"/>'
        '<text x="1084" y="37" class="small">published</text>',
        '<circle cx="1192" cy="32" r="7" fill="#d77b20"/>'
        '<text x="1206" y="37" class="small">passed over</text>',
    ]
    for tick in range(0, 8000, 1000):
        px = x(tick)
        parts.append(f'<line x1="{px:.2f}" y1="66" x2="{px:.2f}" y2="450" '
                     'stroke="#dce3e6" stroke-width="1"/>')
        parts.append(f'<text x="{px:.2f}" y="469" text-anchor="middle" '
                     f'class="tick">{tick}</text>')
    for i, stream in enumerate(DATA["streams"]):
        y = 94 + i * 67
        timestamp = stream["timestamp"]
        bits = stream["field_bits"]
        date = stream["utc"][:10]
        parts.append(f'<text x="35" y="{y + 6}" class="label">'
                     f'{bits}-bit · {date}</text>')
        parts.append(f'<line x1="{X0}" y1="{y}" x2="{X1}" y2="{y}" '
                     'stroke="#a9bbc7" stroke-width="2"/>')
        for slot in stream["slots"]:
            ordinal = slot["ordinal"]
            px = x(ordinal)
            fill = "#1d5d93" if slot["label"] == "published" else "#d77b20"
            title = html.escape(f"{bits}-bit stream {timestamp}: block {ordinal}, "
                                f"{slot['label']}, {slot['name']}")
            parts.append(f'<circle cx="{px:.2f}" cy="{y}" r="8" fill="{fill}" '
                         f'stroke="#fffdf9" stroke-width="2"><title>{title}</title></circle>')
    parts += [
        '<text x="785" y="498" class="label">Candidate block ordinal (20 generator draws per block)</text>',
        '<text x="35" y="518" class="small">Exact points from selection_matrix.json; reported qualifying slots are not a historical accept/reject log.</text>',
        '</svg>',
    ]
    (HERE / "seed_slots.svg").write_text("\n".join(parts) + "\n")
    print("wrote seed_slots.svg")


if __name__ == "__main__":
    main()
