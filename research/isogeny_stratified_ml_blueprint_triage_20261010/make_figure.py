#!/usr/bin/env python3
"""Hand-rolled SVG (no plotting library in this container) for the two
re-analyses in this directory.  Reads the two results JSON files next to it.

Panel A: binary index calculus, relation yield / |F|^2 per volcano-position
group, each group normalised to the depth-1 (first floor level) curve mean of
its sample, with +/- 1 curve-level SD where the group has more than one curve.
Panel B: prime-field rho, out-of-fold R^2 gain from the conductor/volcano
feature block against its within-prime permutation null.
"""
import json, os
here = os.path.dirname(os.path.abspath(__file__))
L = json.load(open(os.path.join(here, "level_stratified_results.json")))
P = json.load(open(os.path.join(here, "prime_field_nested_results.json")))

W, H = 1400, 640
parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="12">',
         f'<rect width="{W}" height="{H}" fill="white"/>']
def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")
def text(x, y, s, size=12, anchor="start", weight="normal", fill="#111", rotate=None):
    tr = f' transform="rotate(-90 {x} {y})"' if rotate else ""
    parts.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{tr}>{esc(s)}</text>')

# ---- Panel A ----
ax, ay, aw, ah = 100, 70, 720, 400
text(ax, 28, "A. Binary index calculus: relation yield / |F|^2 by volcano position", 14, weight="bold")
text(ax, 46, "m = 2, S3 Groebner solver, 4 random subspaces per curve, 400 probes per cell; each group / mean of the depth-1 curves of its class.", 11, fill="#444")
text(ax, 60, "Bars: +/- 1 SD across curves. Rows: crypto/experiments/koblitz_presentation/pres_*.jsonl (2026-10-04).", 11, fill="#444")
ymin, ymax = 0.85, 1.15
def Y(v): return ay + ah - (v - ymin) / (ymax - ymin) * ah
parts.append(f'<rect x="{ax}" y="{ay}" width="{aw}" height="{ah}" fill="none" stroke="#999"/>')
for tv in (0.9, 0.95, 1.0, 1.05, 1.1):
    parts.append(f'<line x1="{ax}" y1="{Y(tv):.1f}" x2="{ax+aw}" y2="{Y(tv):.1f}" stroke="{"#333" if tv == 1.0 else "#ddd"}" stroke-dasharray="{"" if tv == 1.0 else "3,3"}"/>')
    text(ax - 8, Y(tv) + 4, f"{tv:.2f}", anchor="end")
text(ax - 60, ay + ah / 2, "yield ratio to depth-1 mean", 11, anchor="middle", rotate=True)
files = list(L["files"].items())
colors = {"0": "#c0392b", "1": "#2c3e50", "2": "#2980b9"}
slot = aw / len(files)
for i, (fname, o) in enumerate(files):
    cx = ax + slot * (i + 0.5)
    base = o["per_depth"]["1"]["yield_F2"]["mean"]
    groups = sorted(o["per_depth"].items())
    for k, (d, v) in enumerate(groups):
        x = cx + (k - (len(groups) - 1) / 2) * 30
        m = v["yield_F2"]["mean"] / base
        sd = (v["yield_F2"]["sd"] or 0) / base
        n = v["yield_F2"]["n"]
        col = colors.get(d, "#000")
        if sd > 0:
            top, bot = m + sd, m - sd
            clipped = top > ymax or bot < ymin
            parts.append(f'<line x1="{x}" y1="{Y(min(ymax, top)):.1f}" x2="{x}" y2="{Y(max(ymin, bot)):.1f}" stroke="{col}" stroke-width="2"/>')
            if clipped:
                text(x + 8, Y(m) + 4, f"SD {sd:.2f} (clipped)", 9, fill=col)
        parts.append(f'<circle cx="{x}" cy="{Y(m):.1f}" r="5" fill="{col}"/>')
        text(x, Y(m) - 9 if d != "0" else Y(m) + 18, f"d{d} n={n}", 9, anchor="middle", fill=col)
    text(cx, ay + ah + 16, f"n={o['meta']['n']}  f={o['class_conductor']}  l={o['meta']['l']}", 10, anchor="middle")
    text(cx, ay + ah + 29, fname.replace("pres_", "").replace(".jsonl", ""), 9, anchor="middle", fill="#666")

# ---- Panel B ----
bx, by, bw, bh = 940, 70, 400, 400
text(bx - 20, 28, "B. Prime-field rho: gain from conductor / volcano features", 14, weight="bold")
text(bx - 20, 46, "ml-cryptanalysis data/curves.jsonl: 1,548 curves, 25 primes, 1,269 isogeny classes.", 11, fill="#444")
text(bx - 20, 60, "Ridge, out-of-fold R^2 with class-grouped folds; 28 standardised features added to controls.", 11, fill="#444")
parts.append(f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" fill="none" stroke="#999"/>')
gmin, gmax = -1.5e-4, 1.5e-4
def YB(v): return by + bh - (v - gmin) / (gmax - gmin) * bh
for tv in (-1e-4, -5e-5, 0, 5e-5, 1e-4):
    parts.append(f'<line x1="{bx}" y1="{YB(tv):.1f}" x2="{bx+bw}" y2="{YB(tv):.1f}" stroke="{"#333" if tv == 0 else "#ddd"}" stroke-dasharray="{"" if tv == 0 else "3,3"}"/>')
    text(bx - 8, YB(tv) + 4, f"{tv:+.0e}", anchor="end")
text(bx - 70, by + bh / 2, "out-of-fold R^2 gain", 11, anchor="middle", rotate=True)
targets = list(P["targets"].items())
for i, (name, t) in enumerate(targets):
    cx = bx + bw * (i + 0.5) / len(targets)
    parts.append(f'<rect x="{cx-45}" y="{YB(t["null_gain_max"]):.1f}" width="90" height="{abs(YB(t["null_gain_mean"]) - YB(t["null_gain_max"])):.1f}" fill="#dfe6ee" stroke="none"/>')
    parts.append(f'<line x1="{cx-45}" y1="{YB(t["null_gain_95pct"]):.1f}" x2="{cx+45}" y2="{YB(t["null_gain_95pct"]):.1f}" stroke="#7f8c8d" stroke-dasharray="4,2"/>')
    parts.append(f'<line x1="{cx-45}" y1="{YB(t["null_gain_max"]):.1f}" x2="{cx+45}" y2="{YB(t["null_gain_max"]):.1f}" stroke="#7f8c8d"/>')
    parts.append(f'<circle cx="{cx}" cy="{YB(t["gain"]):.1f}" r="6" fill="#c0392b"/>')
    text(cx, by + bh + 16, name.replace("log_", "").replace("_S_total", " arm"), 10, anchor="middle")
    text(cx, by + bh + 29, f"gain {t['gain']:+.1e}; null max {t['null_gain_max']:+.1e}", 9, anchor="middle", fill="#666")
    text(cx, by + bh + 42, f"R^2 controls {t['oof_R2_controls']:.4f}", 9, anchor="middle", fill="#666")
    text(cx, by + bh + 55, f"resid SD / noise floor {t['residual_sd_over_noise_floor']:.2f}", 9, anchor="middle", fill="#666")

# ---- footnotes, full width ----
fy = H - 70
text(ax, fy, "A: d0 = Koblitz crater (one curve per class); d1, d2 = breadth-first distance from the crater along the recorded ell-walk (descending edges, ell | conductor f). "
     "n=16 is the only class with two floor levels (f = 3*31): depth-2 vs depth-1 Spearman rho = +0.025 (perm. p = 0.84);", 10, fill="#444")
text(ax, fy + 14, "incremental R^2 of depth beyond |F|, |F|^2 for the relation rate = 0.0014 (perm. p = 0.36). "
     "B: grey = within-prime permutation null (mean to max; dashed = 95th percentile), 1,000 draws; controls: log2 r, log2 p, log2 cofactor, |Aut|, family;", 10, fill="#444")
text(ax, fy + 28, "the gain of +2e-5 in R^2 on the automorphism arm is under 1 % of the post-control residual variance; the plain arm's gain is negative. "
     "Noise floor = mean per-curve SEM / mean over 24 rho seeds.", 10, fill="#444")
text(ax, fy + 48, "research/isogeny_stratified_ml_blueprint_triage_20261010 -- re-analysis of frozen rows; no new measurement; claim_tier toy; no ECDLP claim in either direction.", 10, fill="#666")
parts.append("</svg>")
os.makedirs(os.path.join(here, "figures"), exist_ok=True)
open(os.path.join(here, "figures", "level_stratified_null.svg"), "w").write("\n".join(parts))
print("wrote figures/level_stratified_null.svg")
