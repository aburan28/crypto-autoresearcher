#!/usr/bin/env python3
"""N3: reproduction gate and controls' integrity.

(1) 22 gate cells whose TARGETS I typed from the committed records myself
    (COST-SEMBIN-8d123b.yaml, CORR-20260913-53739b.yaml, EV-SEMBIN-71e5cd.yaml,
    line numbers recorded) -- not from reproduction.json's target column -- across
    all three sources and all four tolerance classes; check reproduction.json's
    target IS the committed number, then check reproduced against it, both under
    the run's declared tolerance and under the frozen contract's literal 1e-3.
(2) m!-only control: no CORRECTED-only figure among its matches.
(3) ARM K: my predicted rise at three cells (both readings) vs known-false-dF5.json.
(4) ARM P: mask two traces myself and compare.
(6) sha256 every run-directory file vs manifest.yaml and the snapshot receipt.
(7) PD-4: what is verifiable about the tolerance policy's timing.
"""
import hashlib
import json
import math
import os
import re
from math import lgamma, log, log2

import yaml

RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/"
RECEIPT = ("/workspace/coordination/goals/GOAL-SEMBIN-5078bc/batches/BATCH-9d649f/"
           "archives/TASK-20260913-a10007/snapshot-receipt.json")
out = {}

# ---------------------------------------------------------------- (1) gate cells
# (cell name in reproduction.json, committed value AS I READ IT, source, line, class)
MY_CELLS = [
    ("semaev_time_log2[n=163]", 123.7697, "COST-SEMBIN-8d123b.yaml", 62, "1e-3"),
    ("semaev_memory_log2_sparse[n=283]", 61.9374, "COST-SEMBIN-8d123b.yaml", 86, "1e-3"),
    ("vow_time_log2[n=409]", 204.3254, "COST-SEMBIN-8d123b.yaml", 99, "1e-3"),
    ("margin_bits_time_memory_dense[n=409]", -8.7946, "COST-SEMBIN-8d123b.yaml", 101, "1e-3"),
    ("margin_bits_time_memory_sparse[n=571]", 69.4889, "COST-SEMBIN-8d123b.yaml", 122, "1e-3"),
    ("semaev_optimal_m[n=571]", 12, "COST-SEMBIN-8d123b.yaml", 118, "int"),
    ("crossover[time_memory_product,dense]", 435, "COST-SEMBIN-8d123b.yaml", 131, "int"),
    ("crossover_published[stage1_vs_bare_rho,unceiled]", 302, "COST-SEMBIN-8d123b.yaml", 134, "int"),
    ("crossover_ceiled[total_vs_walk_constant]", 281, "COST-SEMBIN-8d123b.yaml", 179, "int"),
    ("per_n_stage1_discrepancy_bits[n=409]", -8.18, "COST-SEMBIN-8d123b.yaml", 180, "5e-3"),
    ("bits_added_if_bound_is_6[n=571]", 40.654, "COST-SEMBIN-8d123b.yaml", 192, "1e-3"),
    ("stage1[571,12,48,eq11,d_sat=5]", 185.5, "CORR-20260913-53739b.yaml", 114, "5e-2"),
    ("reoptimised_total[571,eq11,d_sat=6]", 192.8, "CORR-20260913-53739b.yaml", 115, "5e-2"),
    ("reoptimised_argmin_m_k[571,eq11,d_sat=6]", [21, 28], "CORR-20260913-53739b.yaml", 116, "int"),
    ("crossover[eq11,d_sat=7]", 393, "CORR-20260913-53739b.yaml", 117, "int"),
    ("log2_lambda_at_optimum[n=1000]", -36.25, "CORR-20260913-53739b.yaml", 124, "5e-3"),
    ("m_eq_21_total[omega'=2.376]", 203.36, "CORR-20260913-53739b.yaml", 129, "5e-3"),
    ("argmin_total[omega'=3.0]", 197.08, "CORR-20260913-53739b.yaml", 129, "5e-3"),
    ("omega_prime_invariant_argmin[omega'=1.0]", [18, 32], "CORR-20260913-53739b.yaml", 128, "int"),
    ("O6_dominated_charge_overcharge_bits[n=310]", 29.0, "EV-SEMBIN-71e5cd.yaml", 99, "5e-2"),
    ("O7_crossover_both_at_own_minimum[dense]", 518, "EV-SEMBIN-71e5cd.yaml", 108, "int"),
    ("O7_margin_at_409_coherent[semaev_sparse]", -17.48, "EV-SEMBIN-71e5cd.yaml", 104, "5e-3"),
    ("O7_margin_at_571_sparse_coherent", 40.49, "EV-SEMBIN-71e5cd.yaml", 109, "5e-3"),
]
TOL = {"1e-3": 1e-3, "5e-3": 5e-3, "5e-2": 5e-2, "int": 0.0}

rep = json.load(open(RUN + "reproduction.json"))
by_name = {c["cell"]: c for c in rep["cells"]}
assert len(by_name) == 107 == rep["gate_cells_total"]
rows = []
for name, mine, src, line, cls in MY_CELLS:
    c = by_name[name]
    tgt_is_committed = (c["target"] == mine)
    if cls == "int":
        err = None
        ok_declared = (c["reproduced"] == mine)
        ok_literal = ok_declared
    else:
        err = abs(c["reproduced"] - mine)
        ok_declared = err <= TOL[cls]
        ok_literal = err <= 1e-3
    rows.append(dict(cell=name, source=src, line=line, my_committed_reading=mine,
                     json_target=c["target"], target_is_committed_number=tgt_is_committed,
                     json_declared_tolerance=c["tolerance"], my_tolerance_class=cls,
                     reproduced=c["reproduced"], abs_err_vs_my_reading=err,
                     passes_declared=ok_declared, passes_literal_1e_3=ok_literal))
out["gate_cells_mine"] = rows
print("(1) 22 gate cells, targets typed from the committed records:")
print(f"{'cell':<48} {'src':<26} {'mine':>10} {'json_tgt':>10} tgt=committed  {'repro':>12} {'err':>10} decl lit")
for r in rows:
    e = "int" if r["abs_err_vs_my_reading"] is None else f"{r['abs_err_vs_my_reading']:.2e}"
    print(f"{r['cell']:<48} {r['source'][:26]:<26} {str(r['my_committed_reading']):>10} "
          f"{str(r['json_target']):>10} {str(r['target_is_committed_number']):<13} "
          f"{str(r['reproduced'])[:12]:>12} {e:>10} {'Y' if r['passes_declared'] else 'N'}    "
          f"{'Y' if r['passes_literal_1e_3'] else 'N'}")
print(f"  targets that ARE the committed number: {sum(r['target_is_committed_number'] for r in rows)}/{len(rows)}")
print(f"  pass under declared tolerance:         {sum(r['passes_declared'] for r in rows)}/{len(rows)}")
print(f"  pass under the contract's literal 1e-3: {sum(r['passes_literal_1e_3'] for r in rows)}/{len(rows)}")

# the whole gate under the frozen contract's LITERAL 1e-3 (spec ARM R: "tolerance: 1e-3 bits per cell")
lit_fail = []
round_ok = []
for c in rep["cells"]:
    if c["abs_error_bits"] is None:
        continue
    if c["abs_error_bits"] > 1e-3:
        # how many decimals is the target printed to?
        s = repr(c["target"])
        dec = len(s.split(".")[1]) if "." in s else 0
        rounds_to_target = round(c["reproduced"], dec) == c["target"]
        within_half_ulp = c["abs_error_bits"] <= 0.5 * 10 ** (-dec) + 1e-12
        lit_fail.append(dict(cell=c["cell"], target=c["target"], reproduced=c["reproduced"],
                             abs_error_bits=c["abs_error_bits"], target_decimals=dec,
                             declared_tolerance=c["tolerance"],
                             reproduced_rounds_to_target=rounds_to_target,
                             within_half_unit_of_printed_precision=within_half_ulp))
out["gate_under_literal_1e_3"] = dict(
    cells_failing_literal_1e_3=len(lit_fail),
    all_of_them_round_to_printed_target=all(x["reproduced_rounds_to_target"] for x in lit_fail),
    all_within_half_unit_of_printed_precision=all(x["within_half_unit_of_printed_precision"] for x in lit_fail),
    by_decimals={d: sum(1 for x in lit_fail if x["target_decimals"] == d) for d in (1, 2)},
    cells=lit_fail)
print(f"\n  whole gate under the CONTRACT's literal 1e-3: {len(lit_fail)} of 107 cells exceed it "
      f"(1-decimal targets: {out['gate_under_literal_1e_3']['by_decimals'][1]}, "
      f"2-decimal targets: {out['gate_under_literal_1e_3']['by_decimals'][2]})")
print(f"  every one of those reproduces to a value that ROUNDS to the printed target: "
      f"{out['gate_under_literal_1e_3']['all_of_them_round_to_printed_target']}")
print(f"  every one within half a unit of the target's printed precision: "
      f"{out['gate_under_literal_1e_3']['all_within_half_unit_of_printed_precision']}")
# 3-decimal cells that pass 1e-3 but do not round-match
three = [c for c in rep["cells"] if c["abs_error_bits"] is not None and c["tolerance"] == 1e-3
         and round(c["reproduced"], len(repr(c["target"]).split(".")[1])) != c["target"]]
out["one_em_three_cells_not_round_matching"] = [(c["cell"], c["target"], c["reproduced"], c["abs_error_bits"]) for c in three]
print(f"  1e-3-class cells that pass 1e-3 but do NOT round to the printed target: {[(c['cell'], c['target'], round(c['reproduced'],5)) for c in three]}")

# ---------------------------------------------------------------- (2) m!-only control
CORRECTED_ONLY = {181.7, 185.5, 175.1, 176.9, 192.8, 281, 295, 337, 393}  # differ from uncorrected
CORRECTED_ARGMINS = [[15, 39], [21, 28]]
SHARED = {212.8, 240.3}  # identical under both charges at d_sat >= 6
ctrl = rep["uncorrected_figures_control"]
m_only_targets = [c["target"] for c in ctrl["m_only_pipeline_reproduces_m_only_targets"]]
m_only_repro = [c["reproduced"] for c in ctrl["m_only_pipeline_reproduces_m_only_targets"]]
hits_t = [t for t in m_only_targets if (not isinstance(t, list)) and t in CORRECTED_ONLY]
hits_r = [r for r in m_only_repro if isinstance(r, (int, float)) and any(abs(r - v) <= 0.05 for v in CORRECTED_ONLY)]
hits_a = [t for t in m_only_targets if isinstance(t, list) and t in CORRECTED_ARGMINS]
eq11_hits = [e for e in ctrl["eq11_pipeline_against_uncorrected_targets"]
             if e["uncorrected_differs_from_corrected"] and abs(e["eq11_pipeline_value"] - e["uncorrected_target"]) <= 0.05]
out["m_only_control"] = dict(m_only_targets=m_only_targets,
                             corrected_only_figures_among_m_only_targets=hits_t,
                             corrected_only_figures_within_0p05_of_m_only_reproduced=hits_r,
                             corrected_argmins_among_m_only=hits_a,
                             eq11_pipeline_matching_an_uncorrected_figure_where_it_differs=eq11_hits,
                             shared_figures_present=sorted(SHARED & set(t for t in m_only_targets if not isinstance(t, list))))
print(f"\n(2) m!-only control targets: {m_only_targets}")
print(f"  corrected-only figures among them: {hits_t}  (reproduced within 0.05 of a corrected-only figure: {hits_r}; argmins: {hits_a})")
print(f"  eq11 pipeline matching an UNcorrected figure where it differs: {eq11_hits}")
print(f"  shared (charge-independent, d_sat>=6) figures present, expected: {out['m_only_control']['shared_figures_present']}")

# ---------------------------------------------------------------- (3) ARM K
def lchoose(a, b):
    return (lgamma(a + 1) - lgamma(b + 1) - lgamma(a - b + 1)) / log(2)

kf = json.load(open(RUN + "known-false-dF5.json"))
kcells = {(c["n"], round(c["omega"], 3), c["C_0"], c["reading"]): c for c in kf["cells"]}
pick = [(163, 2.376, 2, "nagao_loose_N_to_the_d"),
        (571, 2.807, 8, "binomial_C_N_plus_d_choose_d"),
        (409, 3.0, 16, "binomial_C_N_plus_d_choose_d"),
        (283, 2.376, 4, "nagao_loose_N_to_the_d")]
krows = []
for key in pick:
    c = kcells[key]
    n, om, c0, rd = key
    m = math.ceil(n / c0)
    N = n * (m - 1)
    if rd == "nagao_loose_N_to_the_d":
        t1_rise = log2(N)                     # d log2 N -> (d+1) log2 N
    else:
        t1_rise = lchoose(N + 5, 5) - lchoose(N + 4, 4)   # = log2((N+5)/5)
        closed = log2((N + 5) / 5)
        assert abs(t1_rise - closed) < 1e-9
    pred_time = om * t1_rise
    pred_mem = t1_rise   # frozen-width memory column = T1 (binomial); K reports one memory rise
    krows.append(dict(cell=key, my_N=N, json_N=c["N"], N_match=(N == c["N"]),
                      my_pred_time_rise=pred_time, json_pred_time_rise=c["predicted_time_rise_bits"],
                      json_obs_time_rise=c["observed_time_rise_bits"],
                      my_pred_minus_json_obs=pred_time - c["observed_time_rise_bits"],
                      my_pred_mem_rise=pred_mem, json_pred_mem_rise=c["predicted_memory_rise_bits"],
                      json_obs_mem_rise=c["observed_memory_rise_bits"],
                      my_pred_mem_minus_json_obs=pred_mem - c["observed_memory_rise_bits"]))
out["arm_k"] = dict(cells=krows, json_summary={k: kf[k] for k in
                    ["all_cells_rose", "max_abs_time_rise_minus_predicted_bits",
                     "max_abs_memory_rise_minus_predicted_bits", "min_observed_time_rise_bits",
                     "max_observed_time_rise_bits"]}, n_cells=len(kf["cells"]))
print("\n(3) ARM K, my predicted rise vs the JSON's OBSERVED rise:")
for r in krows:
    print(f"  {str(r['cell']):<52} N={r['my_N']}({'ok' if r['N_match'] else 'MISMATCH'})  "
          f"time: mine {r['my_pred_time_rise']:.6f} obs {r['json_obs_time_rise']:.6f} "
          f"resid {r['my_pred_minus_json_obs']:+.2e} | mem: mine {r['my_pred_mem_rise']:.6f} "
          f"obs {r['json_obs_mem_rise']:.6f} resid {r['my_pred_mem_minus_json_obs']:+.2e}")
# why the residual can be ~0 despite T6 being log-added: T6 is unchanged by d_F, so the
# residual is log2(1+2^(T6-time_dF5)) - log2(1+2^(T6-time_dF4)) ~ 2^(T6-time), far below double eps.
cs = json.load(open(RUN + "cost-surface.json"))
gap = min(c["time_log2_total"] - c["T6_index_calculus_linear_algebra_log2"] for c in cs["cells"]
          if "T6_index_calculus_linear_algebra_log2" in c) if cs["cells"] and "T6_index_calculus_linear_algebra_log2" in cs["cells"][0] else None
out["arm_k"]["min_time_minus_T6_over_surface_bits"] = gap
print(f"  min over the surface of (time - T6) = {gap} bits -> log-addition residual ~ 2^-{gap:.0f}, below double precision" if gap else
      "  (T6 key not found by that name; see N4)")

# ---------------------------------------------------------------- (4) ARM P traces
po = json.load(open(RUN + "nearby-object-oddchar.json"))
cp = po["code_path_diff"]
def mask_p(t):
    return re.sub(r"p=\d+", "p=*", t)
def mask_p_dF(t):
    return re.sub(r"d_F=\d+", "d_F=*", mask_p(t))
t2, t3, t5 = cp["trace_p2"], cp["trace_p3"], cp["trace_p5"]
diff_p_only_23 = [(a, b) for a, b in zip(map(mask_p, t2), map(mask_p, t3)) if a != b]
diff_p_only_25 = [(a, b) for a, b in zip(map(mask_p, t2), map(mask_p, t5)) if a != b]
same_23 = list(map(mask_p_dF, t2)) == list(map(mask_p_dF, t3))
same_25 = list(map(mask_p_dF, t2)) == list(map(mask_p_dF, t5))
fn_seq = [re.match(r"(\w+)\(", t).group(1) for t in t2]
out["arm_p"] = dict(len_p2=len(t2), len_p3=len(t3), len_p5=len(t5),
                    function_sequence=fn_seq,
                    p_only_masked_diffs_p2_vs_p3=diff_p_only_23, p_only_masked_diffs_p2_vs_p5=diff_p_only_25,
                    identical_after_masking_p_and_dF_p2_vs_p3=same_23, identical_after_masking_p_and_dF_p2_vs_p5=same_25,
                    json_flags={k: cp[k] for k in cp if not k.startswith("trace") and k != "note"},
                    d_F_in_trace={"p2": sorted(set(re.findall(r"d_F=(\d+)", " ".join(t2)))),
                                  "p3": sorted(set(re.findall(r"d_F=(\d+)", " ".join(t3)))),
                                  "p5": sorted(set(re.findall(r"d_F=(\d+)", " ".join(t5))))})
print(f"\n(4) ARM P traces, my own masking: lengths {len(t2)}/{len(t3)}/{len(t5)}, function sequence {fn_seq}")
print(f"  masking p only, p2 vs p3 differs at: {diff_p_only_23}")
print(f"  masking p only, p2 vs p5 differs at: {diff_p_only_25}")
print(f"  masking p AND d_F: p2==p3 {same_23}, p2==p5 {same_25}; d_F values seen: {out['arm_p']['d_F_in_trace']}")
print(f"  JSON flags: {out['arm_p']['json_flags']}")
# 3p+1 check by my own arithmetic
out["arm_p"]["dF_3p_plus_1"] = {p: 3 * p + 1 for p in (3, 5)}
out["arm_p"]["exponent_6p_plus_2_omega_plus_1_at_p3_omega_2p807"] = (6 * 3 + 2) * 2.807 + 1

# ---------------------------------------------------------------- (5) ARM M identity check
mn = json.load(open(RUN + "matched-nulls.json"))
csmap = {(c["n"], round(c["omega"], 3), c["C_0"], c["monomial_count_reading"]): c for c in cs["cells"]}
worst_fy, worst_zm, nchk = 0.0, 0.0, 0
for c in mn["cells"]:
    s = csmap[(c["n"], round(c["omega"], 3), c["C_0"], c["reading"])]
    for key, mg in c["margins"].items():
        metric, memr = key.split("|")
        t5 = s["T5_memory_log2_frozen_width"] if memr == "frozen_width_C_N_plus_4_4" else s["T5_memory_log2_dense_width_squared"]
        worst_fy = max(worst_fy, abs(mg["real_minus_free_yield"] - s["T4_inverse_yield_log2"]))
        if metric in ("time_memory_product", "area_time_AT"):
            worst_zm = max(worst_zm, abs(mg["real_minus_zero_memory"] - t5))
        elif metric == "time_only":
            worst_zm = max(worst_zm, abs(mg["real_minus_zero_memory"]))
        nchk += 1
out["arm_m"] = dict(checks=nchk, max_abs_free_yield_share_minus_T4=worst_fy,
                    max_abs_zero_memory_share_minus_T5_or_0=worst_zm,
                    json_shares={"free_yield": mn["free_yield_share_of_margin_bits"],
                                 "zero_memory": mn["zero_memory_share_of_margin_bits_memory_metrics"]})
print(f"\n(5) ARM M: over {nchk} (cell, margin) pairs, |free-yield share - T4| max {worst_fy:.2e}; "
      f"|zero-memory share - T5 (or 0 for time-only)| max {worst_zm:.2e}  -> identities hold BY CONSTRUCTION")

# ---------------------------------------------------------------- (6) hashes
def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()
man = yaml.safe_load(open(RUN + "manifest.yaml"))
arts = man["run"]["artifacts"] if "run" in man and "artifacts" in man["run"] else man.get("artifacts")
man_map = {}
for a in arts:
    if isinstance(a, dict):
        p = a.get("path") or a.get("file") or a.get("name")
        man_map[os.path.basename(p)] = a.get("sha256")
    else:
        man_map[str(a)] = None
on_disk = {f: sha(RUN + f) for f in sorted(os.listdir(RUN)) if os.path.isfile(RUN + f)}
man_cmp = {f: (man_map.get(f), on_disk[f], man_map.get(f) == on_disk[f]) for f in on_disk}
rc = json.load(open(RECEIPT))
rmap = rc["path_sha256"]
rec_cmp = {}
for p, h in rmap.items():
    rec_cmp[p] = (h, sha("/workspace/" + p), h == sha("/workspace/" + p))
out["hashes"] = dict(
    manifest_files_listed=len(man_map), run_dir_files=len(on_disk),
    manifest_match={f: v[2] for f, v in man_cmp.items()},
    files_in_run_dir_not_in_manifest=[f for f in on_disk if f not in man_map],
    files_in_manifest_not_on_disk=[f for f in man_map if f not in on_disk],
    receipt_paths=len(rmap), receipt_all_match=all(v[2] for v in rec_cmp.values()),
    receipt_mismatches=[p for p, v in rec_cmp.items() if not v[2]],
    receipt_covers_code_dir=sum(1 for p in rmap if "/code/" in p),
    receipt_covers_run_dir=sum(1 for p in rmap if "/runs/" in p),
    manifest_sha256_in_receipt=rmap.get("experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3/manifest.yaml"),
    manifest_sha256_on_disk=on_disk["manifest.yaml"],
    manifest_git_commit=man.get("run", {}).get("git", man.get("git")),
)
print(f"\n(6) manifest lists {len(man_map)} artifacts; run dir has {len(on_disk)} files; "
      f"matches: {sum(v[2] for v in man_cmp.values())}; not in manifest: {out['hashes']['files_in_run_dir_not_in_manifest']}; "
      f"in manifest not on disk: {out['hashes']['files_in_manifest_not_on_disk']}")
print(f"  receipt: {len(rmap)} paths ({out['hashes']['receipt_covers_code_dir']} code, {out['hashes']['receipt_covers_run_dir']} run), "
      f"all match on-disk sha256: {out['hashes']['receipt_all_match']}; mismatches: {out['hashes']['receipt_mismatches']}")
print(f"  manifest git block: {out['hashes']['manifest_git_commit']}")

# ---------------------------------------------------------------- (7) PD-4 verifiability
rep1 = json.load(open(RUN + "reproduction.driver-exec-1.json"))
tol1 = {c["cell"]: c["tolerance"] for c in rep1["cells"]}
tol2 = {c["cell"]: c["tolerance"] for c in rep["cells"]}
same_tol = tol1 == tol2
same_policy_text = rep1.get("tolerance_policy") == rep.get("tolerance_policy")
code_hits = {}
for f in os.listdir("/workspace/experiments/EXP-SEMBIN-db9bc3/code/"):
    if f.endswith(".py"):
        s = open("/workspace/experiments/EXP-SEMBIN-db9bc3/code/" + f).read()
        if "5e-2" in s or "0.05" in s and "decimal" in s:
            code_hits[f] = [i + 1 for i, l in enumerate(s.splitlines()) if "5e-2" in l or ("decimal" in l and "tol" in l.lower())][:8]
out["pd4"] = dict(exec1_and_exec2_per_cell_tolerances_identical=same_tol,
                  exec1_and_exec2_policy_text_identical=same_policy_text,
                  exec1_started=rep1.get("started_at") or None,
                  spec_ARM_R_tolerance_text="tolerance: 1e-3 bits per cell. (specification.yaml line 142); line 267: 'ARM R failing beyond 1e-3 bits at any cell invalidates ARMS N, K, P, M and I.'",
                  code_files_carrying_the_policy=code_hits,
                  commits_touching_code_dir="git log: only a2cdafc67 (snapshot AFTER the run); no pre-run commit of code/")
print(f"\n(7) PD-4: exec-1 vs exec-2 per-cell tolerances identical: {same_tol}; policy text identical: {same_policy_text}")
print(f"  code files carrying the 5e-2/decimal policy: {code_hits}")

json.dump(out, open("own_n3.json", "w"), indent=1, default=str)
print("\nwrote own_n3.json")
