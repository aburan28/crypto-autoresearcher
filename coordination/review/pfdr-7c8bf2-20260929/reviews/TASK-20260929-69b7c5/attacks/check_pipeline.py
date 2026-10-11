"""Pipeline check for the red-team attacks (not a validation of J1-J3, which the validator owns).

Confirms that the series these attacks simulate on are exactly the archived series:
  1. my P3 membership equals the archived floor-rows.jsonl.gz membership per series;
  2. stats.bootstrap_slope (frozen settings) on my series reproduces fits.json exactly;
  3. FastBoot (linear-algebra form) equals stats.bootstrap_slope on every series and range;
  4. the curve sets: (bits, curve) keys shared across series carry identical p, a, b, N;
  5. descriptive facts used later: rank vs relations, fb_size design, rows per rung.
Seed: bootstrap seed 0, 2000 reps (frozen).  No randomness of its own.
"""
import gzip
import json
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common as C  # noqa: E402

stats = C.load_stats()
fits = json.load(open(os.path.join(C.RUN_DIR, "fits.json")))
with gzip.open(os.path.join(C.RUN_DIR, "floor-rows.jsonl.gz"), "rt") as fh:
    floor = [json.loads(l) for l in fh if l.strip()]

out = {"series": {}, "curve_sets": {}, "fastboot_equal": {}}
for name, (f, m, fb) in C.SERIES.items():
    mine = C.series_rows(name)
    arch = [x for x in floor if x.get("kind") != "rho" and x["file"] == f and x["m"] == m
            and x["fb"] == fb and x["engine"] == "mitm"]
    same_members = [(r["bits"], r["curve"]) for r in mine] == [(x["bits"], x["curve"]) for x in arch]
    same_ratio = max(abs(C.ratio(r) - x["ratio"]) for r, x in zip(mine, arch)) if same_members else None
    rec = {"n": len(mine), "membership_equals_archived_floor_rows": same_members,
           "max_abs_ratio_diff_vs_archived": same_ratio}
    for label, lo in (("primary_12_32", 12), ("sensitivity_20_32", 20)):
        rows = C.series_rows(name, lo)
        xs, ys, gs = C.xs_ys(rows)
        lit = stats.bootstrap_slope(xs, ys, groups=gs, reps=C.REPS, level=C.LEVEL, seed=C.SEED)
        a = fits["series"][name][label]
        fb_ = C.FastBoot(xs, gs)
        s, lo_, hi_ = fb_.interval([ys])
        rec[label] = {"literal": lit, "archived": a,
                      "literal_equals_archived": all(abs(lit[k] - a[k]) < 1e-15 for k in ("slope", "lo", "hi")),
                      "fastboot": [float(s[0]), float(lo_[0]), float(hi_[0])],
                      "fastboot_max_abs_diff_vs_literal": max(abs(float(s[0]) - lit["slope"]),
                                                              abs(float(lo_[0]) - lit["lo"]),
                                                              abs(float(hi_[0]) - lit["hi"]))}
    # design facts
    rows = C.series_rows(name)
    rungs = sorted({r["bits"] for r in rows})
    rec["rows_per_rung"] = {b: sum(1 for r in rows if r["bits"] == b) for b in rungs}
    rec["rank_equals_relations_minus_1"] = sum(1 for r in rows if r["rank"] == r["relations"] - 1)
    rec["relations_minus_fb_size_range"] = [min(r["relations"] - r["fb_size"] for r in rows),
                                            max(r["relations"] - r["fb_size"] for r in rows)]
    rec["fb_size_by_rung"] = {b: sorted(r["fb_size"] for r in rows if r["bits"] == b) for b in rungs}
    rec["fb_size_formula_check"] = all(
        r["fb_size"] == max(4, math.ceil((math.factorial(m) * r["N"] / 2) ** (1 / m) / 2)) for r in rows)
    out["series"][name] = rec

# curve sets: same (bits, curve) -> same instance?
for setname in ("filtered", "unfiltered"):
    members = [n for n, s in C.CURVE_SET.items() if s == setname]
    keyinfo = {}
    mismatch = []
    for n in members:
        for r in C.series_rows(n):
            k = (r["bits"], r["curve"])
            v = (r["p"], r["a"], r["b"], r["N"])
            if k in keyinfo and keyinfo[k] != v:
                mismatch.append([n, list(k)])
            keyinfo.setdefault(k, v)
    out["curve_sets"][setname] = {"series": members, "distinct_keys": len(keyinfo),
                                  "instance_mismatches": mismatch}

path = C.dump("check_pipeline.json", out)
print(path)
for n, r in out["series"].items():
    print(n, r["n"], r["membership_equals_archived_floor_rows"], r["primary_12_32"]["literal_equals_archived"],
          r["sensitivity_20_32"]["literal_equals_archived"],
          "fastdiff %.2e %.2e" % (r["primary_12_32"]["fastboot_max_abs_diff_vs_literal"],
                                  r["sensitivity_20_32"]["fastboot_max_abs_diff_vs_literal"]),
          "rank=rel-1:", r["rank_equals_relations_minus_1"], "rel-fb:", r["relations_minus_fb_size_range"],
          "fbformula:", r["fb_size_formula_check"])
print(json.dumps(out["curve_sets"], indent=1))
