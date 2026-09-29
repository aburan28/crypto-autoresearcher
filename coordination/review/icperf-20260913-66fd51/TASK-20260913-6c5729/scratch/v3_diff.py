"""V3: diff my_summary.json (own reduction) against the producer's summary.json."""
import json
import os

RUN = "/workspace/experiments/EXP-ICPERF-66fd51/runs/RUN-ICPERF-305ca3"
mine = json.load(open(os.path.join(os.path.dirname(__file__), "my_summary.json")))
theirs = json.load(open(f"{RUN}/summary.json"))

KEYMAP = {  # summary.json key prefix -> (engine, config)
    "wdsat_default": ("wdsat", "default"), "wdsat_core_order": ("wdsat", "core_order"),
    "wdsat_noncore_first": ("wdsat", "noncore_first"), "wdsat_symmetry": ("wdsat", "symmetry"),
    "wdsat_gauss_elim": ("wdsat", "gauss_elim"), "wdsat_default_on_null_object": ("wdsat", "default_on_null_object"),
    "cms_xor": ("cryptominisat5", "cnf_xor"), "cryptominisat5_pure_cnf": ("cryptominisat5", "pure_cnf"),
    "cadical_pure_cnf": ("cadical", "pure_cnf"), "minisat_pure_cnf": ("minisat", "pure_cnf"),
    "m2_f4": ("macaulay2_F4_ZZ2_fieldeqs", "grevlex"), "singular": ("singular_std_GF2_fieldeqs", "dp"),
}


def close(a, b, tol=1e-9):
    if a is None or b is None:
        return a is None and b is None
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


n_cmp = n_bad = 0
bad = []
for cell, labs in theirs["cells"].items():
    for lab, d in labs.items():
        for pref, (eng, cfg) in KEYMAP.items():
            t = mine["table"].get(f"{cell}/{lab}/{eng}/{cfg}")
            for suffix, mykey in (("_wall_s", "median_wall_s"), ("_n", "n_finished"), ("_conflicts", "median_conflicts"), ("_cpu_s", "median_cpu_s")):
                k = pref + suffix
                if k not in d:
                    continue
                n_cmp += 1
                mv = t[mykey] if t else (0 if mykey == "n_finished" else None)
                if not close(d[k], mv):
                    n_bad += 1
                    bad.append((f"{cell}/{lab}", k, d[k], mv))
print(f"per-cell table: {n_cmp} values compared, {n_bad} differ")
for b in bad:
    print("  DIFF", b)

print("\n-- P3b comparator check (summary default_wall_s vs my same-5 / all-10 default medians) --")
for k, v in theirs["predictions"]["P3"]["cells"].items():
    if k.endswith("noncore_first_over_default_wall_censored"):
        cl = k.split("/noncore")[0]
        m = mine["P3"]["b"][cl]
        print(f"  {cl}: theirs default_wall_s={v['default_wall_s']} ratio={v['ratio_lower_bound']:.4f} | mine same5={m['default_same5_median_wall_s']:.4f} all10={m['default_all10_median_wall_s']:.4f} ratio(same5)={m['ratio_lower_bound_same5']:.4f} -> matched-subset? {close(round(m['default_same5_median_wall_s'],4), v['default_wall_s'], 1e-6)}")

print("\n-- P3c check --")
for k, v in theirs["predictions"]["P3"]["cells"].items():
    if k.endswith("cms_pure_cnf_over_wdsat"):
        cl = k.split("/cms")[0]
        m = mine["P3"]["c"][cl]
        print(f"  {cl}: theirs ratio={v['ratio']} | mine vs all10={m['ratio_vs_all10']:.4f} vs same5={m['ratio_vs_same5']:.4f} | theirs full entry: {v}")

print("\n-- P5 --")
for k, v in theirs["predictions"]["P5"]["cells"].items():
    cell, what = k.split("/")
    eng = "wdsat/default" if what.startswith("wdsat") else "cryptominisat5/cnf_xor"
    m = mine["P5"]["sat"][f"{cell}/{eng}"]
    print(f"  {k}: theirs {v['ratio']:.6f} mine {m['U_over_S']:.6f} equal={close(v['ratio'], m['U_over_S'])}")

print("\n-- P6 --")
for cell, v in theirs["predictions"]["P6"]["cells"].items():
    m = mine["P6"]["cells"][cell]
    print(f"  {cell}: theirs null_median={v['null_median_conflicts']} ratio={v['ratio']} | mine median over all finished nulls={m['null_median_conflicts_finished']} (n={m['n_null_finished']}) ratio={m['ratio_null_over_U']} | finished null conflicts sorted={m['null_finished_conflicts_sorted']}")
    sN = theirs["cells"][cell]["S"]["wdsat_default_on_null_object_conflicts"]
    uN = theirs["cells"][cell]["U"]["wdsat_default_on_null_object_conflicts"]
    if sN is not None and uN is not None:
        print(f"      mean of (S-null median {sN}, U-null median {uN}) = {(sN+uN)/2}  -> equals theirs? {close((sN+uN)/2, v['null_median_conflicts'])}")
print("  theirs P6 holds:", theirs["predictions"]["P6"]["holds"], "| mine strict every-cell:", mine["P6"]["holds_every_cell_strict"], "| mine ignoring-null:", mine["P6"]["holds_ignoring_null_cells"])

print("\n-- P4 --")
for k, v in theirs["predictions"]["P4"]["cells"].items():
    m = mine["P4"]["cells"][k]
    print(f"  {k}: theirs gauss={v['gauss_elim']} default={v['default']} holds={v['holds']} | mine {m['gauss_elim_median_wall_s']} {m['default_median_wall_s']} {m['verdict']} equal={close(v['gauss_elim'], m['gauss_elim_median_wall_s']) and close(v['default'], m['default_median_wall_s'])}")

print("\n-- P1 --")
print("  theirs unverified:", theirs["predictions"]["P1"]["unverified_sat_answers"])
print("  mine unverified:", [(d['instance'], d['engine'], d['config']) for d in mine["P1"]["my_unverified"]])
print("\n-- top-level verdicts -- theirs:", {k: v["holds"] for k, v in theirs["predictions"].items()}, "| mine:", mine["verdicts"])
