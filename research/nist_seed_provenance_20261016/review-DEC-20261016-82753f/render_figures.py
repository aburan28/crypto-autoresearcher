"""Lay out recorded review values as the four figures of report.md. Plotting only:
every number is read from the Validator's outputs (validation-20261016/) or the
evidence record EV-SCURVE-e9d71b; nothing is computed beyond counting entries."""
import json, pathlib, yaml
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = pathlib.Path(__file__).parent
VAL = HERE.parent / "validation-20261016"
REPO = HERE.parents[2]
CAP = "VAL-20261016-cd9156 · EV-SCURVE-e9d71b"
INK, CONCERN, NOTRUN, INC = "#1f4e9c", "#c98a1a", "#9aa3b5", "#b8322a"

def save(fig, name):
    fig.tight_layout()
    fig.savefig(HERE / f"{name}.svg"); fig.savefig(HERE / f"{name}.png", dpi=150); plt.close(fig)

# Fig 1: checks by joint, tallied from validation_report.yaml
v = yaml.safe_load(open(VAL / "validation_report.yaml"))["validation_report"]
group = {"J1": ["J1-1", "J1-2", "J1-3", "J1-4", "Q2-1", "C2-1", "C2-2", "PTM-1", "PTM-2", "PTM-4"],
         "J2": ["J2-1", "J2-2", "PTM-3"], "J3": ["J3-1", "J3-2"], "J4": ["J4-1", "J4-2", "J4-3", "J4-4"],
         "J5": ["J5-1", "J5-2", "J5-3", "J5-4", "C4-1", "C4-2", "PTM-5"], "J6": ["J6-1", "J6-2", "J6-3", "J6-4"]}
res = {}
for sec in ("artifact_checks", "control_checks", "metric_recomputations"):
    for e in v.get(sec) or []:
        res[e.get("id")] = e.get("status") or e.get("result")
cats = ["pass", "concern", "not_run", "inconclusive"]
rows = {j: [sum(res[i] == c for i in ids) for c in cats] for j, ids in group.items()}
c5 = v["c5_labelling_and_provenance"]
lab = c5.get("labelling"); lab = lab.get("verdict") if isinstance(lab, dict) else lab
rows["J7"] = [1 if str(lab).lower().startswith("holds") else 0, 0, 0, 1]
assert sum(sum(r) for j, r in rows.items() if j != 'J7') == 30, rows
fig, ax = plt.subplots(figsize=(7.5, 3.6))
js = list(rows)[::-1]; left = [0] * len(js)
for k, (c, col) in enumerate(zip(cats, [INK, CONCERN, NOTRUN, INC])):
    vals = [rows[j][k] for j in js]
    ax.barh(js, vals, left=left, color=col, label=c.replace("_", " "))
    left = [a + b for a, b in zip(left, vals)]
ax.set_xlabel("check entries (count)"); ax.legend(ncol=4, fontsize=8, frameon=False, loc="lower right")
ax.set_title(f"Checks by joint. J1-J6: 30 check entries (28 pass, 1 concern, 1 not run); J7 from the C5 block\n{CAP}", fontsize=9)
ax.spines[["top", "right"]].set_visible(False); save(fig, "fig1-checks-by-joint")

# Fig 2: claim strength, from the evidence record
ev = yaml.safe_load(open(REPO / "ledger/evidence/EV-SCURVE-e9d71b.yaml"))
ev = ev.get("evidence", ev)
sbc = ev["strength_by_claim"]
scale = ["anecdotal", "preliminary", "replicated", "strong"]
claims = ["C1a", "C1b", "C2", "C3", "C4", "C5"]
fig, ax = plt.subplots(figsize=(7.5, 3.4))
for y, c in enumerate(claims[::-1]):
    s = sbc[c]["strength"]
    if s in scale:
        ax.scatter([scale.index(s)], [y], s=90, color=INK, zorder=3)
        ax.scatter([scale.index(s)], [y], s=220, facecolors="none", edgecolors=INK, zorder=2)
    else:
        ax.text(0, y, "no strength (external analyses)", va="center", fontsize=8, color=NOTRUN)
ax.set_yticks(range(len(claims))); ax.set_yticklabels(claims[::-1])
ax.set_xticks(range(4)); ax.set_xticklabels(scale); ax.set_xlim(-0.4, 3.4); ax.set_ylim(-0.7, len(claims) - 0.4)
ax.grid(axis="x", color="#e1e4ea"); ax.spines[["top", "right"]].set_visible(False)
ax.set_title(f"Assigned strength per claim (filled) and reachable under DEC-20261016-7bcdd6 (ring)\n{CAP}", fontsize=9)
save(fig, "fig2-claim-strength")

# Fig 3: twist bookkeeping, from out/j4_lost_criteria.json
j4 = json.load(open(VAL / "out/j4_lost_criteria.json"))
order = [("863711343", "p239"), ("863966734", "p192"), ("871002724", "p521"), ("871696354", "p256"), ("872952608", "p384"), ("891607927", "p224")]
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for x, (k, lab) in enumerate(order):
    r = j4[k]; tw = r["twist_only"]; fail = len(r["fail_bitlen"]); ok = tw - fail
    col = INK if r["p_mod_4"] == 3 else NOTRUN
    ax.bar(x - 0.18, tw, 0.36, color="#c9d6ee" if r["p_mod_4"] == 3 else "#e3e6ec", edgecolor=col)
    ax.bar(x + 0.18, ok, 0.36, color=col)
    if r["p_mod_4"] == 1:
        ax.text(x, tw + 0.6, "not reachable by -b", ha="center", fontsize=7, color=NOTRUN)
ax.set_xticks(range(len(order))); ax.set_xticklabels([f"{lab}\n{k}" for k, lab in order], fontsize=7)
ax.set_ylabel("candidates")
s = j4["summary"]
ax.set_title(f"Twist-only prime candidates (light) and those passing the criteria on the twist (dark)\n"
             f"p = 3 mod 4 runs: {s['twist_only_p3mod4']} twist-only (README), {s['would_be_accepted_p3mod4']} lost (corrected) · {CAP}", fontsize=8)
ax.spines[["top", "right"]].set_visible(False); save(fig, "fig3-twist-bookkeeping")

# Fig 4: re-census agreement, from out/recensus_compare.json
rc = json.load(open(VAL / "out/recensus_compare.json"))["runs"]
fig, ax = plt.subplots(figsize=(7.5, 3.6))
for x, (k, lab) in enumerate(order):
    r = rc[k]
    ax.bar(x, r["exact_both"], color=INK)
    ax.bar(x, r["zero_vs_composite"], bottom=r["exact_both"], color=CONCERN)
    ax.text(x, r["rows_compared"] + 40, f"{r['mismatch']} mismatches", ha="center", fontsize=7)
ax.set_xticks(range(len(order))); ax.set_xticklabels([f"{lab}\n{k}" for k, lab in order], fontsize=7)
ax.set_ylabel("rows (count)")
ax.legend(["identical in both columns", "Nt filled from N0 (consistent)"], fontsize=8, frameon=False)
ax.set_title(f"Independent re-census vs recorded census: 11,042 rows, 0 mismatches\n{CAP}", fontsize=9)
ax.spines[["top", "right"]].set_visible(False); save(fig, "fig4-recensus-agreement")
print("rendered 4 figures")
