"""Draw the recorded BINSTD toy-yield ratios from the replay receipt."""

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def main():
    receipt = json.loads((HERE / "receipt.json").read_text())
    if receipt["status"] != "pass" or len(receipt["cases"]) != 2:
        raise ValueError("expected two passed replay cases")
    cells = [cell for case in receipt["cases"] for cell in case["cells"]]
    if [(c["ell"], c["ratio_tau_over_open"]) for c in cells] != [
        (8, 0.4), (9, 1.0), (8, 0.5), (9, 1.0)
    ]:
        raise ValueError("replay ratio data changed; review the chart layout")
    width, height = 780, 425
    top, bottom = 76, 322
    scale = (bottom - top) / 1.4
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="780" height="425" fill="#ffffff"/>',
        '<text x="28" y="31" font-family="sans-serif" font-weight="bold" font-size="19">BINSTD toy relation yield, n = 17</text>',
        '<text x="28" y="52" font-family="sans-serif" font-size="12" fill="#555">Derived ratio R_tau / R_open; 40 sampled targets per cell. This is not runtime or ECDLP cost.</text>',
        f'<line x1="75" y1="{top}" x2="75" y2="{bottom}" stroke="#555"/>',
        f'<line x1="75" y1="{bottom}" x2="735" y2="{bottom}" stroke="#555"/>',
    ]
    for value in (0, 0.5, 1.0, 1.25):
        y = bottom - value * scale
        parts.append(f'<line x1="75" y1="{y:.1f}" x2="735" y2="{y:.1f}" stroke="#d8dce0"/>')
        parts.append(f'<text x="27" y="{y+4:.1f}" font-family="sans-serif" font-size="11" fill="#555">{value:g}</text>')
    threshold_y = bottom - 1.25 * scale
    parts.append(f'<line x1="75" y1="{threshold_y:.1f}" x2="735" y2="{threshold_y:.1f}" stroke="#c45831" stroke-width="2" stroke-dasharray="6,4"/>')
    parts.append(f'<text x="590" y="{threshold_y-8:.1f}" font-family="sans-serif" font-size="11" fill="#a43f21">pre-registered 1.25 band</text>')
    positions = (165, 290, 475, 600)
    colors = ("#217c96", "#217c96", "#7354a4", "#7354a4")
    for i, (cell, x, color) in enumerate(zip(cells, positions, colors)):
        ratio = cell["ratio_tau_over_open"]
        y = bottom - ratio * scale
        parts.append(f'<rect x="{x}" y="{y:.1f}" width="70" height="{bottom-y:.1f}" fill="{color}"/>')
        parts.append(f'<text x="{x+35}" y="{y-9:.1f}" text-anchor="middle" font-family="sans-serif" font-size="12" font-weight="bold">{ratio:g}</text>')
        parts.append(f'<text x="{x+35}" y="{bottom+18}" text-anchor="middle" font-family="sans-serif" font-size="11">ell={cell["ell"]}</text>')
        parts.append(f'<text x="{x+35}" y="{bottom+33}" text-anchor="middle" font-family="sans-serif" font-size="10" fill="#555">{cell["hits_tau"]}/{cell["hits_open"]} hits</text>')
    parts.extend((
        '<rect x="140" y="371" width="13" height="13" fill="#217c96"/><text x="160" y="382" font-family="sans-serif" font-size="11">RUN-BINSTD-43abd4 (ell89)</text>',
        '<rect x="415" y="371" width="13" height="13" fill="#7354a4"/><text x="435" y="382" font-family="sans-serif" font-size="11">RUN-BINSTD-a2a24c (ell89r1)</text>',
        '<text x="28" y="410" font-family="sans-serif" font-size="10" fill="#555">No uncertainty interval was recorded. Replays confirm archived output bytes, not an independent curve-arithmetic oracle.</text>',
        '</svg>',
    ))
    (HERE / "yield-ratios.svg").write_text("\n".join(parts) + "\n")
    print("rendered yield-ratios.svg from receipt.json")


if __name__ == "__main__":
    main()
