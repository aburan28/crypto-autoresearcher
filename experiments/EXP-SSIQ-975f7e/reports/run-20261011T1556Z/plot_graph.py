"""Render the recorded SSIQ prefix products as SVG and a small PDF graph."""
from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
RUN = HERE.parents[1] / "runs" / "RUN-SSIQ-be0b59"
WIDTH, HEIGHT = 760, 430
LEFT, RIGHT, TOP, BOTTOM = 64, 24, 48, 58
YMAX = 30


def load_rows() -> list[dict]:
    data = json.loads((RUN / "raw-result.json").read_text(encoding="utf-8"))
    return data["rows"]


def xy(index: int, value: int, count: int) -> tuple[float, float]:
    span_x = WIDTH - LEFT - RIGHT
    span_y = HEIGHT - TOP - BOTTOM
    x = LEFT if count == 1 else LEFT + (index / (count - 1)) * span_x
    y = HEIGHT - BOTTOM - (value / YMAX) * span_y
    return x, y


def svg(rows: list[dict]) -> str:
    count = len(rows)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}">',
        '<rect width="100%" height="100%" fill="white"/>',
        '<text x="64" y="24" font-family="Helvetica,Arial,sans-serif" font-size="16" font-weight="bold">Recorded prefix products by eligible integer</text>',
        f'<line x1="{LEFT}" y1="{HEIGHT-BOTTOM}" x2="{WIDTH-RIGHT}" y2="{HEIGHT-BOTTOM}" stroke="#222"/>',
        f'<line x1="{LEFT}" y1="{TOP}" x2="{LEFT}" y2="{HEIGHT-BOTTOM}" stroke="#222"/>',
        f'<text x="{WIDTH/2:.1f}" y="{HEIGHT-12}" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="12">eligible-row index (n={count})</text>',
        f'<text x="16" y="{HEIGHT/2:.1f}" transform="rotate(-90 16 {HEIGHT/2:.1f})" text-anchor="middle" font-family="Helvetica,Arial,sans-serif" font-size="12">recorded prefix product</text>',
    ]
    for tick in (0, 5, 10, 15, 20, 25, 30):
        y = HEIGHT - BOTTOM - (tick / YMAX) * (HEIGHT - TOP - BOTTOM)
        parts.append(f'<line x1="{LEFT}" y1="{y:.2f}" x2="{WIDTH-RIGHT}" y2="{y:.2f}" stroke="#dddddd"/>')
        parts.append(f'<text x="{LEFT-8}" y="{y+4:.2f}" text-anchor="end" font-family="Helvetica,Arial,sans-serif" font-size="10">{tick}</text>')
    for name, color, key in (("ascending", "#1261a0", "ascending_prefix"), ("descending", "#c44e52", "descending_prefix")):
        points = " ".join(f"{xy(i, row[key], count)[0]:.2f},{xy(i, row[key], count)[1]:.2f}" for i, row in enumerate(rows))
        parts.append(f'<polyline points="{points}" fill="none" stroke="{color}" stroke-width="2"/>')
        for i, row in enumerate(rows):
            x, y = xy(i, row[key], count)
            parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="2.2" fill="{color}"/>')
    parts += [
        '<line x1="560" y1="38" x2="580" y2="38" stroke="#1261a0" stroke-width="2"/><text x="586" y="42" font-family="Helvetica,Arial,sans-serif" font-size="11">ascending</text>',
        '<line x1="650" y1="38" x2="670" y2="38" stroke="#c44e52" stroke-width="2"/><text x="676" y="42" font-family="Helvetica,Arial,sans-serif" font-size="11">descending</text>',
        '</svg>',
    ]
    return "\n".join(parts) + "\n"


def pdf_escape(value: str) -> str:
    return value.replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")


def pdf(rows: list[dict]) -> bytes:
    page_w, page_h = 612, 360
    left, right, top, bottom = 52, 20, 40, 48
    ymax = 30
    count = len(rows)
    def pxy(index: int, value: int) -> tuple[float, float]:
        x = left if count == 1 else left + (index / (count - 1)) * (page_w - left - right)
        y = bottom + (value / ymax) * (page_h - top - bottom)
        return x, y
    content: list[str] = ["BT /F1 12 Tf 52 334 Td (Recorded prefix products by eligible integer) Tj ET"]
    content.append("0.85 0.85 0.85 RG 0.5 w")
    for tick in (0, 5, 10, 15, 20, 25, 30):
        y = bottom + (tick / ymax) * (page_h - top - bottom)
        content.append(f"{left} {y:.2f} m {page_w-right} {y:.2f} l S")
        content.append(f"BT /F1 8 Tf {left-22} {y-3:.2f} Td ({tick}) Tj ET")
    content += [f"0 0 0 RG {left} {bottom} m {page_w-right} {bottom} l S", f"{left} {bottom} m {left} {page_h-top} l S"]
    for color, key in (("0.071 0.380 0.627", "ascending_prefix"), ("0.769 0.306 0.322", "descending_prefix")):
        content.append(f"{color} RG 1.4 w")
        pts = [pxy(i, row[key]) for i, row in enumerate(rows)]
        if pts:
            content.append(f"{pts[0][0]:.2f} {pts[0][1]:.2f} m")
            content.extend(f"{x:.2f} {y:.2f} l" for x, y in pts[1:])
            content.append("S")
    content += [
        "0 0 0 RG 0.7 w",
        f"BT /F1 9 Tf 245 18 Td (eligible-row index; n={count}) Tj ET",
        "BT /F1 9 Tf 10 150 Td 0 1 1 0 0 0 cm (recorded prefix product) Tj ET",
        "BT /F1 9 Tf 490 334 Td 0 0 1 rg (ascending) Tj ET",
        "BT /F1 9 Tf 540 334 Td 1 0 0 rg (descending) Tj ET",
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
    rows = load_rows()
    (HERE / "prefix-plot.svg").write_text(svg(rows), encoding="utf-8")
    (HERE / "prefix-plot.pdf").write_bytes(pdf(rows))


if __name__ == "__main__":
    main()
