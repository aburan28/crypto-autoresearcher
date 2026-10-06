"""J5 (rho de-duplication, P7(a)) and the rho half of the proves-too-much control.

  1. rho-row listing of every input file with its key (p, a, b, curve, bits), p_filter label
     and every recorded field -> out/j5_rho_rows.jsonl
  2. key groups across files: are key-equal rows the SAME instance (every field except the
     wall-clock `seconds` equal), or the same key with different walks?
  3. the filtered/unfiltered overlap: (bits, curve) pairs whose curve (p, a, b) is identical in
     the two labelled sets, and whether N and walk_ops agree
  4. walk exponent (frozen stats.bootstrap_slope, groups = bits, 2000 reps, seed 0) per set
     under: (a) the archived convention (first-seen over the P0 file order, cross-file key),
     (b) each labelled set keeps its own copy (dedupe within label), (c) each primary file's
     own rho rows
  5. static read of analyze_floor.py: which names the outcome block reads (does any outcome
     condition or tripwire read the rho set?)
  6. proves-too-much on the rho slice: the frozen interval against the known exponent 1/2, and
     synthetic coverage on each rho design with slope 1/2 true by construction (R1 within-rung
     residual resampling, R3 per-rung Gaussian), K = 20000, via common.FastBoot (exact).
Seeds: numpy default_rng([0x69b7c5, 5, design_index, model_index]).
"""
import json
import math
import os
import re
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

stats = C.load_stats()
K = 20000
res = {}

# 1. listing
listing = []
for f in C.FILES:
    for r in C.all_rows()[f]:
        if r["method"] == "rho":
            listing.append({"file": f, **{k: r[k] for k in r}})
with open(os.path.join(C.OUT, "j5_rho_rows.jsonl"), "w") as fh:
    for x in listing:
        fh.write(json.dumps(x, sort_keys=True) + "\n")
res["rows_per_file"] = {f: sum(1 for x in listing if x["file"] == f) for f in C.FILES}
res["labels_per_file"] = {f: sorted({x["p_filter"] for x in listing if x["file"] == f}) for f in C.FILES}

# 2. key groups
IGN = {"file", "seconds"}
groups = {}
for x in listing:
    groups.setdefault((x["p"], x["a"], x["b"], x["curve"], x["bits"]), []).append(x)
same, differ = 0, []
for k, xs in groups.items():
    base = {kk: v for kk, v in xs[0].items() if kk not in IGN}
    for y in xs[1:]:
        yy = {kk: v for kk, v in y.items() if kk not in IGN}
        if yy == base:
            same += 1
        else:
            differ.append({"key": list(k), "files": [xs[0]["file"], y["file"]],
                           "fields": sorted(kk for kk in set(base) | set(yy) if base.get(kk) != yy.get(kk))})
res["key_groups"] = {"distinct_keys": len(groups), "multiplicity_histogram": {
    str(n): sum(1 for v in groups.values() if len(v) == n) for n in sorted({len(v) for v in groups.values()})},
    "duplicate_pairs_identical_instance": same, "duplicate_pairs_differing": differ,
    "keys_spanning_two_labels": sum(1 for v in groups.values() if len({x["p_filter"] for x in v}) > 1)}

# 3. filtered/unfiltered overlap
lab_f = [l for l in {x["p_filter"] for x in listing} if l != "none"][0]
fil = {(x["bits"], x["curve"]): x for x in listing if x["p_filter"] == lab_f}
unf = {(x["bits"], x["curve"]): x for x in listing if x["p_filter"] == "none"}
ov = []
for k in sorted(set(fil) & set(unf)):
    a, b = fil[k], unf[k]
    if (a["p"], a["a"], a["b"]) == (b["p"], b["a"], b["b"]):
        ov.append({"bits": k[0], "curve": k[1], "p": a["p"], "N_equal": a["N"] == b["N"],
                   "walk_ops": [a["walk_ops"], b["walk_ops"]], "walk_ops_equal": a["walk_ops"] == b["walk_ops"],
                   "all_fields_but_label_and_seconds_equal": {kk: v for kk, v in a.items() if kk not in IGN | {"p_filter"}}
                   == {kk: v for kk, v in b.items() if kk not in IGN | {"p_filter"}}})
res["filtered_unfiltered_shared_curves"] = {"n": len(ov), "rows": ov,
                                            "by_bits": {b: sum(1 for x in ov if x["bits"] == b) for b in sorted({x["bits"] for x in ov})}}


# 4. exponents under conventions
def expo(sel):
    xs = [x["log2N"] for x in sel]
    ys = [math.log2(x["walk_ops"]) for x in sel]
    gs = [x["bits"] for x in sel]
    v = stats.bootstrap_slope(xs, ys, groups=gs, reps=C.REPS, level=C.LEVEL, seed=C.SEED)
    v["contains_half"] = v["lo"] <= 0.5 <= v["hi"]
    v["per_rung_n"] = {b: gs.count(b) for b in sorted(set(gs))}
    return v, (xs, ys, gs)


designs = {}
seen, first = set(), []
for x in listing:  # listing is already in the P0 file order
    k = (x["p"], x["a"], x["b"], x["curve"], x["bits"])
    if k not in seen:
        seen.add(k)
        first.append(x)
conv = {}
for lab in sorted({x["p_filter"] for x in listing}):
    v, d = expo([x for x in first if x["p_filter"] == lab])
    conv[f"archived_first_seen|{lab}"] = v
    designs[f"archived_first_seen|{lab}"] = d
    own = {}
    for x in listing:
        if x["p_filter"] == lab:
            own.setdefault((x["p"], x["a"], x["b"], x["curve"], x["bits"]), x)
    v, d = expo(list(own.values()))
    conv[f"within_label_dedupe|{lab}"] = v
    designs[f"within_label_dedupe|{lab}"] = d
for f in C.FILES[:3]:
    v, d = expo([x for x in listing if x["file"] == f])
    conv[f"per_file|{f}"] = v
    designs[f"per_file|{f}"] = d
res["walk_exponent"] = conv
fits = json.load(open(os.path.join(C.RUN_DIR, "fits.json")))
res["archived_fits_rho"] = {k: v["walk_exponent"] for k, v in fits["rho"].items()}

# 5. static read: what does the outcome block read?
src = open(os.path.join(C.WT, "experiments", "EXP-PFDR-7c8bf2", "analyze_floor.py")).read().splitlines()
start = next(i for i, l in enumerate(src) if "# outcome ---" in l)
block = src[start:start + 30]
res["outcome_block_static_read"] = {
    "lines": f"{start + 1}-{start + len(block)}",
    "mentions_rho": [l.strip() for l in block if re.search(r"rho", l)],
    "names_read": sorted(set(re.findall(r"\b(p5|fits|pairs|rho_sets|rho_rows|p7|h1|h2)\b", "\n".join(block))))}
spec = open(os.path.join(C.WT, "experiments", "EXP-PFDR-7c8bf2", "specification.yaml")).read()
ao = spec[spec.index("analysis_outcomes:"):spec.index("success_criterion:")]
res["spec_analysis_outcomes_mentions_rho"] = bool(re.search(r"rho", ao))

# 6. proves-too-much: synthetic coverage on rho designs
cov = {}
for di, (name, (xs, ys, gs)) in enumerate(designs.items()):
    xs, ys = np.array(xs), np.array(ys)
    b, a = C.ols(xs, ys)
    resid = ys - (a + b * xs)
    fbt = C.FastBoot(xs, gs)
    base = a + 0.5 * xs
    G = np.array(gs)
    cell = {}
    for mi, mname in enumerate(("R1_within_rung_residual_resample", "R3_per_rung_gaussian")):
        rng = np.random.default_rng([0x69b7c5, 5, di, mi])
        E = np.empty((K, len(xs)))
        for g in np.unique(G):
            pos = np.where(G == g)[0]
            if mi == 0:
                E[:, pos] = resid[pos][rng.integers(0, len(pos), size=(K, len(pos)))]
            else:
                E[:, pos] = rng.normal(0, ys[pos].std(ddof=1), size=(K, len(pos)))
        s, lo, hi = fbt.interval(base[None, :] + E)
        c_ = float(np.mean((lo <= 0.5) & (0.5 <= hi)))
        cell[mname] = {"K": K, "coverage": c_, "mc_se": math.sqrt(c_ * (1 - c_) / K),
                       "p_lo_above_half": float(np.mean(lo > 0.5)), "p_hi_below_half": float(np.mean(hi < 0.5)),
                       "mean_width_over_2x1.96x_true_sd": float(np.mean(hi - lo) / (2 * 1.96 * np.std(s, ddof=1)))}
    cov[name] = cell
res["proves_too_much_rho_synthetic_coverage"] = cov

print(C.dump("j5_rho.json", res))
print(json.dumps({k: res[k] for k in ("rows_per_file", "labels_per_file", "key_groups")}, indent=1)[:3000])
print("shared curves:", res["filtered_unfiltered_shared_curves"]["n"], res["filtered_unfiltered_shared_curves"]["by_bits"],
      "walk equal:", sum(x["walk_ops_equal"] for x in ov), "all fields equal:", sum(x["all_fields_but_label_and_seconds_equal"] for x in ov))
for k, v in conv.items():
    print("%-70s n=%3d %.4f [%.4f, %.4f] contains 1/2: %s" % (k, v["n"], v["slope"], v["lo"], v["hi"], v["contains_half"]))
print("archived:", res["archived_fits_rho"])
print("outcome block:", res["outcome_block_static_read"], "spec outcomes mention rho:", res["spec_analysis_outcomes_mentions_rho"])
for k, v in cov.items():
    print(k, {m: "cov=%.3f lo>.5=%.3f hi<.5=%.3f w/w*=%.2f" % (x["coverage"], x["p_lo_above_half"], x["p_hi_below_half"],
                                                               x["mean_width_over_2x1.96x_true_sd"]) for m, x in v.items()})
