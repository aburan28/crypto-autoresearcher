#!/usr/bin/env python3
"""Second figure (hand-rolled SVG): the new measurements of the comprehensive pass.

A. n = 16 Koblitz class, per-prime strata (v3, v31): yield/|F|^2 and reductions per call at m = 2.
B. n = 51 ordinary class (f_pi = 7^2, ell = 7): |F| per volcano level (the only curve-varying quantity).
C. m = 3 panel on the n = 16 class: reductions per call per stratum (production S4 solver).
D. Transport cost against rho across the Koblitz ladder: log2 F_q-multiplications.
"""
import json, os, math
here = os.path.dirname(os.path.abspath(__file__))
S = json.load(open(os.path.join(here, "per_ell_strata_results.json")))["classes"]["pres_16_0_l8.jsonl"]
N51 = json.load(open(os.path.join(here, "n51_level_yield_results.json")))
M3 = json.load(open(os.path.join(here, "m3_panel_results.json"))) if os.path.exists(os.path.join(here, "m3_panel_results.json")) else None
T = json.load(open(os.path.join(here, "transport_cost_table.json")))["classes"]

W, H = 1400, 900
P = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" font-family="Helvetica, Arial, sans-serif" font-size="11">', f'<rect width="{W}" height="{H}" fill="white"/>']
def esc(s): return str(s).replace("&", "&amp;").replace("<", "&lt;")
def text(x, y, s, size=11, anchor="start", weight="normal", fill="#111", rot=False):
    tr = f' transform="rotate(-90 {x} {y})"' if rot else ""
    P.append(f'<text x="{x}" y="{y}" font-size="{size}" text-anchor="{anchor}" font-weight="{weight}" fill="{fill}"{tr}>{esc(s)}</text>')
def panel(x, y, w, h, title, sub):
    text(x, y - 22, title, 13, weight="bold"); text(x, y - 8, sub, 10, fill="#444"); P.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="none" stroke="#999"/>')
def dots(x, y, w, h, groups, key, label_fmt, ylab, ref=None):
    """groups: list of (name, mean, sd, n); y-axis is ratio to ref (first group with n>1 if ref None)."""
    base = ref if ref is not None else next(m for _, m, _, n in groups if n > 1)
    vals = [(nm, m / base, (sd or 0) / base, n) for nm, m, sd, n in groups]
    lo = min(v - s for _, v, s, _ in vals + [("", 1, 0.05, 1)]) - 0.02; hi = max(v + s for _, v, s, _ in vals + [("", 1, 0.05, 1)]) + 0.02
    def Y(v): return y + h - (v - lo) / (hi - lo) * h
    for tv in (0.9, 0.95, 1.0, 1.05, 1.1):
        if lo < tv < hi:
            P.append(f'<line x1="{x}" y1="{Y(tv):.1f}" x2="{x+w}" y2="{Y(tv):.1f}" stroke="{"#333" if tv == 1 else "#ddd"}" stroke-dasharray="{"" if tv == 1 else "3,3"}"/>'); text(x - 6, Y(tv) + 4, f"{tv:.2f}", anchor="end")
    text(x - 42, y + h / 2, ylab, 10, anchor="middle", rot=True)
    for i, (nm, v, s, n) in enumerate(vals):
        cx = x + w * (i + 0.5) / len(vals); col = "#c0392b" if n == 1 else "#2c3e50"
        if s > 0: P.append(f'<line x1="{cx}" y1="{Y(v+s):.1f}" x2="{cx}" y2="{Y(v-s):.1f}" stroke="{col}" stroke-width="2"/>')
        P.append(f'<circle cx="{cx}" cy="{Y(v):.1f}" r="5" fill="{col}"/>'); text(cx, y + h + 14, label_fmt(nm, n), 10, anchor="middle")

# A
ax, ay, aw, ah = 70, 50, 380, 220
panel(ax, ay, aw, ah, "A. n = 16, f = 3*31: per-prime strata, m = 2", "ratio to the (0,1)-stratum mean; bars +/- 1 SD over curves; 165 curves x 4 subspaces")
g = [(s, v["yield_F2"]["mean"], v["yield_F2"]["sd"], v["yield_F2"]["n"]) for s, v in S["per_stratum"].items()]
ref = next(m for s, m, _, n in g if "('3', 0), ('31', 1)" in s)
def short(nm):
    import ast
    d = dict(ast.literal_eval(nm)); return f"v3={d['3']} v31={d['31']}"
dots(ax, ay, aw, ah, g, "yield", lambda nm, n: f"{short(nm)} n={n}", "yield / |F|^2", ref=ref)
t = S["tests"]["yield_F2"]; text(ax, ay + ah + 32, f"between-stratum permutation p = {t['p_perm']:.2f} (yield), {S['tests']['red']['p_perm']:.2f} (reductions/call)", 10, fill="#444")

# B
bx, by, bw, bh = 540, 50, 380, 220
panel(bx, by, bw, bh, f"B. n = 51 ordinary class, f_pi = {N51['f_pi']}, ell = {N51['ell']}: |F| per level", f"{N51['rows']} vertices; cofactor {N51['cofactor']}; 2-sum yield / |F|^2 is constant to 5 digits")
g = [(f"level {k}", v["F_mean"], v["F_sd"], v["curves"]) for k, v in N51["per_level"].items()]
dots(bx, by, bw, bh, g, "F", lambda nm, n: f"{nm} n={n}", "|F| ratio to level-1 mean", ref=N51["per_level"]["1"]["F_mean"])
text(bx, by + bh + 32, f"between-level permutation p = {N51['tests']['F']['p_perm']:.2f} (|F|), {N51['tests']['log_yield2']['p_perm']:.2f} (log yield)", 10, fill="#444")

# C
cx0, cy, cw, ch = 1010, 50, 340, 220
if M3 and M3["per_stratum"]:
    panel(cx0, cy, cw, ch, "C. n = 16, m = 3 panel: reductions per call", f"production S4 solver, 6 probes per curve, monomial V; {len(M3['completed'])}/{len(M3['planned'])} cells")
    g = [(s, v["red"]["mean"], v["red"]["sd"], v["red"]["n"]) for s, v in M3["per_stratum"].items()]
    ref = next((m for s, m, _, n in g if n > 1), g[0][1])
    dots(cx0, cy, cw, ch, g, "red", lambda nm, n: f"{nm} n={n}", "reductions/call ratio", ref=ref)
    if "red" in M3["tests"]:
        text(cx0, cy + ch + 32, f"between-stratum permutation p = {M3['tests']['red']['p_perm']:.2f} (reductions), crater z = {M3['tests'].get('crater_z_red', float('nan')):+.2f}", 10, fill="#444")
else:
    panel(cx0, cy, cw, ch, "C. n = 16, m = 3 panel", "pending"); text(cx0 + 20, cy + 100, "no cells yet", 12)

# D
dx, dy, dw, dh = 70, 380, 1280, 330
panel(dx, dy, dw, dh, "D. Transport cost vs rho across the Koblitz ladder (log2 F_q multiplications, cost model in transport_cost_table.py)",
      "bars: transport (kernel route construction + two evaluations); red marks: rho on a floor curve (negation only); blue marks: rho on the crater (signed Frobenius); grey: kernel field degree too large to construct")
rows = []
for c in T:
    if "error" in c: continue
    for e in c["per_ell"]:
        rows.append((f"{c['label'].replace('Koblitz ','')} ell={e['ell']}", e.get("log2_transfer_total"), e.get("log2_rho_floor_Fq_mults"), e.get("log2_rho_crater_Fq_mults"), e.get("feasible")))
vmax = 72
def YD(v): return dy + dh - v / vmax * dh
for tv in range(0, 71, 10):
    P.append(f'<line x1="{dx}" y1="{YD(tv):.1f}" x2="{dx+dw}" y2="{YD(tv):.1f}" stroke="#ddd" stroke-dasharray="3,3"/>'); text(dx - 6, YD(tv) + 4, str(tv), anchor="end")
text(dx - 42, dy + dh / 2, "log2 F_q multiplications", 10, anchor="middle", rot=True)
slot = dw / len(rows)
for i, (lab, tr, rf, rc, feas) in enumerate(rows):
    x = dx + slot * i + 4
    if tr is not None:
        P.append(f'<rect x="{x}" y="{YD(tr):.1f}" width="{slot-8:.1f}" height="{dy+dh-YD(tr):.1f}" fill="{"#2c3e50" if feas else "#bbb"}"/>')
    else:
        P.append(f'<rect x="{x}" y="{YD(70):.1f}" width="{slot-8:.1f}" height="{dy+dh-YD(70):.1f}" fill="#eee" stroke="#bbb" stroke-dasharray="2,2"/>')
    if rf is not None:
        P.append(f'<line x1="{x}" y1="{YD(rf):.1f}" x2="{x+slot-8:.1f}" y2="{YD(rf):.1f}" stroke="#c0392b" stroke-width="3"/>')
        P.append(f'<line x1="{x}" y1="{YD(rc):.1f}" x2="{x+slot-8:.1f}" y2="{YD(rc):.1f}" stroke="#2980b9" stroke-width="3"/>')
    text(x + (slot - 8) / 2 + 3, dy + dh + 6, lab.replace("K_0 ", "").replace("ordinary random-b n=51 (binary_level_yield)", "ord n=51"), 8, anchor="end", rot=True)
text(dx, H - 18, "Reading: wherever the descending isogeny is constructible, transport costs far less than rho on either curve, so a floor-curve method must beat the crater's rho to matter (H3); where the kernel field is huge (grey / dashed), neither direction is reachable and the levels are not known to be DLP-equivalent (JMV's open case).", 10, fill="#444")
text(dx, H - 4, "research/isogeny_stratified_ml_blueprint_triage_20261010 -- figure 2; toy scale; no ECDLP claim.", 10, fill="#666")
P.append("</svg>")
os.makedirs(os.path.join(here, "figures"), exist_ok=True)
open(os.path.join(here, "figures", "comprehensive_pass.svg"), "w").write("\n".join(P)); print("wrote figures/comprehensive_pass.svg")
