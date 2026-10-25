#!/usr/bin/env python3
"""Decode the data in the producer's three matplotlib SVGs and check it
against the blind re-derivation. Pixel -> data maps are fitted from the
axis tick marks and their text comments; nothing of the producer runs.

Usage: python3 -I decode_figures.py <figures_dir> <rederive_out.json>
"""
import json
import math
import re
import sys

figdir, mine_p = sys.argv[1], sys.argv[2]
mine = json.load(open(mine_p))
ORDER = ["r24", "r26", "r28", "c24", "c28", "c30"]  # summary.json row order
ARMS = ["half-base", "double-base", "full-rank", "random-targets", "rootfind"]


def groups(t, prefix):
    """Top-level text of each <g id="prefix_N"> ... up to the next sibling id."""
    out = []
    for m in re.finditer(r'<g id="(%s_\d+)">' % prefix, t):
        out.append((m.group(1), m.start()))
    res = []
    for i, (gid, st) in enumerate(out):
        en = out[i + 1][1] if i + 1 < len(out) else len(t)
        res.append((gid, t[st:en]))
    return res


def tick_map(t, axis, log=False):
    pts = []
    for gid, body in groups(t, axis + "tick"):
        u = re.search(r'<use xlink:href="#[^"]+" x="([-0-9.]+)" y="([-0-9.]+)"', body)
        c = re.search(r"<!-- (.*?) -->", body)
        if not u or not c:
            continue
        lab = c.group(1).replace("−", "-")
        mm = re.search(r"10\^\{(-?\d+)\}", lab)
        if mm:
            val = 10.0 ** int(mm.group(1))
        else:
            try:
                val = float(lab)
            except ValueError:
                continue
        pix = float(u.group(1) if axis == "x" else u.group(2))
        pts.append((pix, val))
    (p0, v0), (p1, v1) = pts[0], pts[-1]
    if log:
        a = (math.log10(v1) - math.log10(v0)) / (p1 - p0)
        return (lambda p: 10 ** (math.log10(v0) + a * (p - p0))), pts
    a = (v1 - v0) / (p1 - p0)
    return (lambda p: v0 + a * (p - p0)), pts


def path_pts(d):
    return [(float(x), float(y)) for x, y in re.findall(r"[ML] ([-0-9.]+) ([-0-9.]+)", d)]


rows = []


def rec(fig, what, decoded, mine_v, tol_rel):
    ok = abs(decoded - mine_v) <= tol_rel * abs(mine_v)
    rows.append((fig, what, round(decoded, 4), round(mine_v, 4), "match" if ok else "MISMATCH"))


# ---- Figure 1: bars (log y), 6 rows x 5 arms, with error bars ---------------
t = open(f"{figdir}/alternatives_vs_plan.svg").read()
ymap, _ = tick_map(t, "y", log=True)
bars = []
for gid, body in groups(t, "patch"):
    m = re.search(r'<path d="([^"]+)"[^>]*clip-path', body)
    if m:
        p = path_pts(m.group(1))
        if len(p) == 4:
            bars.append(p)
# error-bar collections: one per row, 5 vertical segments each
lcs = []
for gid, body in groups(t, "LineCollection"):
    segs = [path_pts(d) for d in re.findall(r'<path d="([^"]+)"', body)]
    lcs.append(segs)
assert len(bars) == 30, len(bars)
for k, s in enumerate(ORDER):
    for i, arm in enumerate(ARMS):
        b = bars[k * 5 + i]
        ytop = min(y for _, y in b)
        rec("alternatives_vs_plan", f"{s} {arm} ratio(w=0)", ymap(ytop),
            mine[s]["compare"][f"plan__{arm}"]["ratio"], 0.01)
        seg = lcs[k][i]
        ys = sorted(y for _, y in seg)
        lo, hi = ymap(ys[-1]), ymap(ys[0])
        ci = mine[s]["compare"][f"plan__{arm}"]["ci95"]
        rec("alternatives_vs_plan", f"{s} {arm} ci_lo", lo, ci[0], 0.01)
        rec("alternatives_vs_plan", f"{s} {arm} ci_hi", hi, ci[1], 0.01)

# ---- Figure 2: band ratios, lines (linear y, symlog x) ----------------------
t = open(f"{figdir}/base_size_band.svg").read()
ymap, _ = tick_map(t, "y", log=False)
series = []
for gid, body in groups(t, "line2d"):
    m = re.search(r'<path d="([^"]+)"', body)
    if m:
        p = path_pts(m.group(1))
        if len(p) == 3 and len({round(x, 3) for x, _ in p}) == 3:
            series.append(p)
series = series[:12]  # legend lines come after the 12 data series
for k, s in enumerate(ORDER):
    for j, arm in enumerate(["half-base", "double-base"]):
        p = series[k * 2 + j]
        for wi, (_, y) in enumerate(p):
            rec("base_size_band", f"{s} {arm} band_ratio w#{wi}", ymap(y),
                mine[s]["band_ratios"][arm]["per_weight"][wi]["ratio_of_band_means"], 0.005)

# ---- Figure 3: predicted vs measured gap to rho -----------------------------
t = open(f"{figdir}/rho_gap_predicted_vs_measured.svg").read()
ymap, _ = tick_map(t, "y")
xmap, _ = tick_map(t, "x")
PRED = {"c24": 11.461210709103137, "r24": 12.233956652458087, "r26": 14.453197377819107,
        "c28": 19.325980413591978, "r28": 20.078173411100984, "c30": 24.54954651510073}
srt = sorted(ORDER, key=lambda s: mine[s]["curve"]["log2_r"])
pred_line = None
for gid, body in groups(t, "line2d"):
    m = re.search(r'<path d="([^"]+)"', body)
    if m:
        p = path_pts(m.group(1))
        if len(p) == 6:
            pred_line = p
            break
for s, (x, y) in zip(srt, pred_line):
    rec("rho_gap", f"{s} log2_r (x)", xmap(x), mine[s]["curve"]["log2_r"], 0.002)
    rec("rho_gap", f"{s} predicted", ymap(y), PRED[s], 0.01)
segs = []
for gid, body in groups(t, "LineCollection"):
    for d in re.findall(r'<path d="([^"]+)"', body):
        p = path_pts(d)
        if len(p) == 2 and abs(p[0][0] - p[1][0]) < 1e-6:
            segs.append(p)
for s in ORDER:
    x = mine[s]["curve"]["log2_r"]
    cand = [sg for sg in segs if abs(xmap(sg[0][0]) - x) < 0.02]
    if not cand:
        rows.append(("rho_gap", f"{s} error bar", None, None, "NOT FOUND"))
        continue
    ys = sorted(y for _, y in cand[0])
    ci = mine[s]["compare"]["rho-neg__plan"]["ci95"]
    rec("rho_gap", f"{s} plan/rho ci_lo", ymap(ys[-1]), ci[0], 0.01)
    rec("rho_gap", f"{s} plan/rho ci_hi", ymap(ys[0]), ci[1], 0.01)
# measured markers
marks = re.findall(r'<use xlink:href="#[^"]+" x="([-0-9.]+)" y="([-0-9.]+)" style="fill: #(4f81bd|c0504d)', t)
for s in ORDER:
    x = mine[s]["curve"]["log2_r"]
    # caps and the point marker share x; the point is the middle one
    c = sorted({round(float(b), 6) for a, b, _ in marks if abs(xmap(float(a)) - x) < 0.02})
    if c:
        mid = c[len(c) // 2]
        rec("rho_gap", f"{s} plan/rho point (middle of {len(c)} markers)", ymap(mid),
            mine[s]["compare"]["rho-neg__plan"]["ratio"], 0.01)
    else:
        rows.append(("rho_gap", f"{s} plan/rho point", None, None, "NOT FOUND"))

bad = [r for r in rows if r[-1] != "match"]
for r in rows:
    print(*r, sep="\t")
print(f"decoded {len(rows)} figure values; non-matching {len(bad)}")
