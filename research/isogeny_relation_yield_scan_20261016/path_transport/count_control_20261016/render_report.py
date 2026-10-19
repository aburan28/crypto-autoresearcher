"""Render only the recorded ordered-count outputs as a vector chart."""
from pathlib import Path
from html import escape

HERE = Path(__file__).resolve().parent
WIDTH, HEIGHT = 980, 540
LEFT, RIGHT = 78, 948


def values(path):
    rows = [line.split("\t") for line in path.read_text().splitlines()]
    return [int(row[2]) for row in rows[1:]]


def chart():
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
             '<rect width="100%" height="100%" fill="#ffffff"/>',
             '<style>text{font-family:Arial,sans-serif;fill:#202832} .title{font-size:21px;font-weight:bold} .label{font-size:15px} .tick{font-size:12px}</style>',
             '<text x="78" y="34" class="title">Exact ordered counts on transported bases</text>',
             '<text x="78" y="55" class="label">128 fixed public targets per stratum; source and transported symbols coincide exactly</text>']
    for stratum, top, maximum in (("p29", 86, 6), ("p37", 307, 12)):
        source = values(HERE / f"{stratum}-attempt1/source.count")
        moved = values(HERE / f"{stratum}-attempt1/transported.count")
        if len(source) != 128 or source != moved:
            raise ValueError("recorded count arrays differ")
        baseline, plot_top = top + 168, top + 26
        parts.append(f'<text x="78" y="{top+12}" class="label">{escape(stratum.upper())}: {sum(v>0 for v in source)}/128 nonempty; {sum(source)} ordered relations</text>')
        for tick in (0, maximum // 2, maximum):
            y = baseline - tick / maximum * (baseline - plot_top)
            parts.append(f'<line x1="{LEFT}" y1="{y:.1f}" x2="{RIGHT}" y2="{y:.1f}" stroke="#e2e6ea"/>')
            parts.append(f'<text x="43" y="{y+4:.1f}" class="tick">{tick}</text>')
        for index, value in enumerate(source):
            if value == 0:
                continue
            x = LEFT + index / 127 * (RIGHT - LEFT)
            y = baseline - value / maximum * (baseline - plot_top)
            parts.append(f'<line x1="{x:.1f}" y1="{baseline}" x2="{x:.1f}" y2="{y:.1f}" stroke="#316a87" stroke-width="1.5"/>')
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="4" fill="#ffffff" stroke="#316a87" stroke-width="2"/>')
            parts.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" fill="#c76528"/>')
        parts.append(f'<line x1="{LEFT}" y1="{baseline}" x2="{RIGHT}" y2="{baseline}" stroke="#52606c"/>')
        for tick in (0, 32, 64, 96, 127):
            x = LEFT + tick / 127 * (RIGHT - LEFT)
            parts.append(f'<text x="{x-7:.1f}" y="{baseline+18}" class="tick">{tick}</text>')
    parts.append('<text x="473" y="534" class="tick">Fixed target index</text>')
    parts.append('</svg>')
    (HERE / "counts.svg").write_text("\n".join(parts) + "\n")


if __name__ == "__main__":
    chart()
