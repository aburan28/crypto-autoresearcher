#!/usr/bin/env python3
"""Render the recorded Part A and Part B values as a self-contained SVG."""

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parent
DATA = json.loads((ROOT / "plot_data.json").read_text())
OUT = ROOT / "graph.svg"

W, H = 1100, 760
BG = "#fbfaf7"
INK = "#17212b"
GRID = "#d7dde2"
BLUE = "#2b6cb0"
ORANGE = "#c05621"
GREEN = "#2f855a"


def esc(value):
    return (str(value).replace("&", "&amp;").replace("<", "&lt;")
            .replace(">", "&gt;").replace('"', "&quot;"))


def text(x, y, value, size=16, weight="400", anchor="start", fill=INK):
    return (f'<text x="{x}" y="{y}" font-family="Arial, sans-serif" '
            f'font-size="{size}px" font-weight="{weight}" text-anchor="{anchor}" '
            f'fill="{fill}">{esc(value)}</text>')


def line(x1, y1, x2, y2, stroke=GRID, width=1, dash=""):
    extra = f' stroke-dasharray="{dash}"' if dash else ""
    return f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{stroke}" stroke-width="{width}"{extra}/>'


def rect(x, y, w, h, fill, stroke="none", width=1, rx=0):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{width}" rx="{rx}"/>'


def circle(cx, cy, r, fill, stroke="white", width=1):
    return f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{width}"/>'


def bar_panel(parts):
    x0, y0, pw, ph = 85, 95, 435, 240
    out = [text(x0, 55, "Part A: recorded arm statistics", 22, "700"),
           text(x0, 78, "fraction k ≤ 20 and mean log₂(t); n shown below", 14)]
    maxy = 1.35
    for tick in [0, .25, .5, .75, 1, 1.25]:
        y = y0 + ph - tick / maxy * ph
        out += [line(x0, y, x0 + pw, y), text(x0 - 10, y + 5, f"{tick:g}", 12, anchor="end")]
    out += [line(x0, y0, x0, y0 + ph, INK, 2), line(x0, y0 + ph, x0 + pw, y0 + ph, INK, 2)]
    groups = [("special", BLUE), ("random", ORANGE)]
    centers = [x0 + 130, x0 + 310]
    for center, (arm, color), idx in zip(centers, groups, range(2)):
        frac = parts["small_k_fraction"][idx]
        mean = parts["mean_log2_t"][idx]
        bw = 48
        for off, value, label in [(-30, frac, "k≤20"), (30, mean, "mean log₂t")]:
            h = value / maxy * ph
            out += [rect(center + off - bw / 2, y0 + ph - h, bw, h, color, rx=5),
                    text(center + off, y0 + ph - h - 8, f"{value:.3f}", 12, anchor="middle"),
                    text(center + off, y0 + ph + 23, label, 12, anchor="middle")]
        out += [text(center, y0 + ph + 48, f"{arm} (n={parts['n_curves'][idx]})", 15, "700", anchor="middle", fill=color)]
    out += [text(x0 + pw / 2, y0 + ph + 76, "Arm", 13, anchor="middle")]
    return out


def threshold_panel(parts):
    x0, y0, pw, ph = 625, 95, 410, 240
    out = [text(x0, 55, "Part B: recorded k* thresholds", 22, "700"),
           text(x0, 78, "threshold k* by public parameter set and model", 14)]
    maxy = 52
    for tick in [0, 10, 20, 30, 40, 50]:
        y = y0 + ph - tick / maxy * ph
        out += [line(x0, y, x0 + pw, y), text(x0 - 10, y + 5, str(tick), 12, anchor="end")]
    out += [line(x0, y0, x0, y0 + ph, INK, 2), line(x0, y0 + ph, x0 + pw, y0 + ph, INK, 2)]
    curves = parts["curves"]
    models = [("GNFS_1.923", BLUE), ("exTNFS_1.747", ORANGE), ("SNFS_or_STNFS_1.526", GREEN)]
    groupw = pw / len(curves)
    for i, curve in enumerate(curves):
        center = x0 + groupw * (i + .5)
        for j, (model, color) in enumerate(models):
            value = curve["k_star"][model]
            bx = center + (j - 1) * 19
            h = value / maxy * ph
            out += [rect(bx - 7, y0 + ph - h, 14, h, color, rx=3), text(bx, y0 + ph - h - 6, str(value), 10, anchor="middle")]
        label = curve["name"].replace("brainpoolP256r1", "brainpool").replace("secp256k1", "secp256k1")
        out += [text(center, y0 + ph + 28, label, 10, anchor="middle")]
    legend_y = y0 + ph + 64
    for i, (model, color) in enumerate(models):
        lx = x0 + i * 132
        out += [rect(lx, legend_y - 12, 12, 12, color, rx=2), text(lx + 17, legend_y - 1, model.split("_")[0], 11)]
    return out


def histogram_panel(parts):
    x0, y0, pw, ph = 85, 435, 950, 220
    out = [text(x0, 400, "Part A: recorded cofactor histogram", 22, "700"),
           text(x0, 423, "counts per arm; bins are the pre-registered t ranges", 14)]
    counts = parts["t_histogram_counts_special"], parts["t_histogram_counts_random"]
    maxy = max(max(x) for x in counts)
    for tick in [0, 200, 400, 600, 800]:
        y = y0 + ph - tick / maxy * ph
        out += [line(x0, y, x0 + pw, y), text(x0 - 10, y + 5, str(tick), 12, anchor="end")]
    out += [line(x0, y0, x0, y0 + ph, INK, 2), line(x0, y0 + ph, x0 + pw, y0 + ph, INK, 2)]
    n = len(parts["t_histogram_bins"])
    groupw = pw / n
    for i, label in enumerate(parts["t_histogram_bins"]):
        center = x0 + groupw * (i + .5)
        for j, (vals, color) in enumerate(zip(counts, [BLUE, ORANGE])):
            value = vals[i]
            bx = center + (j - .5) * 25
            h = value / maxy * ph
            out += [rect(bx - 10, y0 + ph - h, 20, h, color, rx=3), text(bx, y0 + ph - h - 6, str(value), 11, anchor="middle")]
        out += [text(center, y0 + ph + 24, label, 13, anchor="middle")]
    legend_y = y0 + ph + 53
    for i, (label, color) in enumerate([("special", BLUE), ("random", ORANGE)]):
        lx = x0 + i * 120
        out += [rect(lx, legend_y - 12, 12, 12, color, rx=2), text(lx + 17, legend_y - 1, label, 12)]
    return out


parts_a = DATA["part_a"]
parts_b = DATA["part_b"]
svg = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
       rect(0, 0, W, H, BG),
       text(55, 32, "EXP-ECDLP-6dacdb — recorded run quantities", 24, "700"),
       text(55, 55 + H - 70, "RUN-ECDLP-36b2a5 (Part A), RUN-ECDLP-994eb9 (Part B); values are recorded, not recomputed", 13),
       *bar_panel(parts_a), *threshold_panel(parts_b), *histogram_panel(parts_a), "</svg>"]
OUT.write_text("\n".join(svg) + "\n")
print(f"wrote {OUT}")
