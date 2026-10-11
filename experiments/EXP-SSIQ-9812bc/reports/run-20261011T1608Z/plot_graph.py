"""Render the recorded SSIQ histograms as SVG and a small PDF graph."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "runs" / "RUN-SSIQ-ee5cdb"
WIDTH, HEIGHT = 760, 430
LEFT, RIGHT, TOP, BOTTOM = 64, 24, 48, 58
YMAX = 50


def load_result() -> dict:
    return json.loads((RUN / "raw-result.json").read_text(encoding="utf-8"))


def xy(index: int, value: int, count: int) -> tuple[float, float]:
    span_x = WIDTH - LEFT - RIGHT
    span_y = HEIGHT - TOP - BOTTOM
    x = LEFT + ((index + 0.5) / count) * span_x
    y = HEIGHT - BOTTOM - (value / YMAX) * span_y
    return x, y


def svg(data: dict) -> str:
    a = data["histogram_a"]
    n = data["histogram_n"]
    count = len(a)
    bar_w = (WIDTH - LEFT - RIGHT) / count * 0.38
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="64" y="24" font-family="Helvetica,Arial,sans-serif" font-size="16" font-weight="bold">Recorded SSIQ histograms</text>',
        f'<line x1="{LEFT}" y1="{HEIGHT-BOTTOM}" x2="{WIDTH-RIGHT}" y2="{HEIGHT-BOTTOM}" stroke="#222"/>',
        f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{HEIGHT-BOTTOM}" stroke="#222"/>',
        f'<text x="{WIDTH/2:.1f}" y="{HEIGHT-12}" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="12">bin index (n={count})</text>',
        f'<text x="16" y="{HEIGHT/2:.1f}" transform="rotate(-90 16 {HEIGHT/2:.1f})" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="12">recorded count</text>',
    ]
    for tick in (0, 10, 20, 30, 40, 50):
        y = HEIGHT - BOTTOM - (tick / YMAX) * (HEIGHT - TOP - BOTTOM)
        parts.append(f'<line x1="{LEFT}" y1="{y:.2f}" x2="{WIDTH-RIGHT}" y2="{y:.2f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{LEFT-8}" y="{y+4:.2f}" text-anchor="end" font-family="Helvetica,Arial,sans-serif" font-size="10">{tick}</text>')
    for index, (value_a, value_n) in enumerate(zip(a, n)):
        center, _ = xy(index, 0, count)
        base = HEIGHT - BOTTOM
        height_a = (value_a / YMAX) * (HEIGHT - TOP - BOTTOM)
        height_n = (value_n / YMAX) * (HEIGHT - TOP - BOTTOM)
        parts.append(f'<rect x="{center-bar_w-1:.2f}" y="{base-height_a:.2f}" width="{bar_w:.2f}" height="{height_a:.2f}" fill="#1261a0"/>')
        parts.append(f'<rect x="{center+1:.2f}" y="{base-height_n:.2f}" width="{bar_w:.2f}" height="{height_n:.2f}" fill="#c44e52"/>')
        parts.append(f'<text x="{center:.2f}" y="{base+16:.2f}" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="8">{index}</text>')
    parts += [
        '<rect x="526" y="30" width="12" height="12" fill="#1261a0"/><text x="544" y="41" font-family="Helvetica,Arial,sans-serif" font-size="11">curve a</text>',
        '<rect x="606" y="30" width="12" height="12" fill="#c44e52"/><text x="624" y="41" font-family="Helvetica,Arial,sans-serif" font-size="11">curve n</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def pdf(data: dict) -> bytes:
    page_w, page_h = 612, 360
    left, right, top, bottom = 52, 20, 40, 48
    ymax = 50
    a = data["histogram_a"]
    n = data["histogram_n"]
    count = len(a)
    span_x = page_w - left - right
    span_y = page_h - top - bottom
    bar_w = span_x / count * 0.30

    content: list[str] = ["BT /F1 12 Tf 52 334 Td (Recorded SSIQ histograms) Tj ET", "0.85 0.85 0.85 RG 0.5 w"]
    for tick in (0, 10, 20, 30, 40, 50):
        y = bottom + (tick / ymax) * span_y
        content.append(f"{left} {y:.2f} m {page_w-right} {y:.2f} l S")
        content.append(f"BT /F1 8 Tf {left-22} {y-3:.2f} Td ({tick}) Tj ET")
    content += [f"0 0 0 RG {left} {bottom} m {page_w-right} {bottom} l S", f"{left} {bottom} m {left} {page_h-top} l S"]
    for values, color, offset in ((a, "0.071 0.380 0.627", -0.18), (n, "0.769 0.306 0.322", 0.18)):
        content.append(f"{color} rg")
        for index, value in enumerate(values):
            center = left + ((index + 0.5) / count) * span_x
            x = center + offset * span_x / count - bar_w / 2
            h = value / ymax * span_y
            content.append(f"{x:.2f} {bottom:.2f} {bar_w:.2f} {h:.2f} re f")
    content += [
        "0 0 0 RG 0.7 w",
        f"BT /F1 9 Tf 250 18 Td (bin index; n={count}) Tj ET",
        "BT /F1 9 Tf 10 150 Td 0 1 1 0 0 0 cm (recorded count) Tj ET",
        "BT /F1 9 Tf 490 334 Td 0 0 1 rg (curve a) Tj ET",
        "BT /F1 9 Tf 540 334 Td 1 0 0 rg (curve n) Tj ET",
    ]
    stream = "\n".join(content).encode("ascii")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 360] /Resources << /Font << /F1 4 0 R >> >> /Contents 5 0 R >>",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
        b"<< /Length " + str(len(stream)).encode("ascii") + b" >>\nstream\n" + stream + b"\nendstream",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = [0]
    for i, obj in enumerate(objects, 1):
        offsets.append(len(out)); out.extend(f"{i} 0 obj\n".encode()); out.extend(obj); out.extend(b"\nendobj\n")
    xref = len(out); out.extend(f"xref\n0 {len(objects)+1}\n0000000000 65535 f \n".encode())
    out.extend("".join(f"{offset:010d} 00000 n \n" for offset in offsets[1:]).encode())
    out.extend(f"trailer\n<< /Size {len(objects)+1} /Root 1 0 R >>\nstartxref\n{xref}\n%%EOF\n".encode())
    return bytes(out)


def main() -> None:
    data = load_result()
    (HERE / "histogram-plot.svg").write_text(svg(data), encoding="utf-8")
    (HERE / "histogram-plot.pdf").write_bytes(pdf(data))


if __name__ == "__main__":
    main()
