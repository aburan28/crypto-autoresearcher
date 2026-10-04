"""TASK-20260913-f6652f, joint B1 -- independent recomputation from the DEFINITIONS.

This file imports NOTHING from experiments/EXP-SEMBIN-db9bc3/code/.  Every quantity is
re-implemented from the statement of T1-T5 in H-SEMBIN-4a80f3 (mechanism,
heuristic_assumptions) and the metric definitions the run declares in
cost-surface.json `column_definitions` / `vow_baseline`; the producer's JSON is read
only to COMPARE against.

Outputs (all under this task's scratch/):
  b1_recompute.json      every recomputed cell at n in {409, 571}, all comparisons
  b1_tables.md           the tables pasted into report.md
"""
from __future__ import annotations

import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
RUN = "/workspace/experiments/EXP-SEMBIN-db9bc3/runs/RUN-SEMBIN-251fd3"

P = 2
D_F = 4
LOG2_0886 = math.log2(0.886)
OMEGAS = [2.376, 2.807, 3.0]
C0S = [2, 3, 4, 6, 8, 10, 12, 16]
NS = [163, 233, 283, 409, 571]
METRICS = ["time_only", "time_memory_product", "area_time_AT", "equal_rate_max"]
MEMORY_METRICS = ["time_memory_product", "area_time_AT", "equal_rate_max"]


# ----------------------------------------------------------------------------- primitives
def log2_int(v: int) -> float:
    b = v.bit_length()
    if b <= 60:
        return math.log2(v)
    return (b - 60) + math.log2(v >> (b - 60))


def log2_add(a: float, b: float) -> float:
    hi, lo = max(a, b), min(a, b)
    return hi if hi - lo > 64 else hi + math.log2(1.0 + 2.0 ** (lo - hi))


def m_of(n: int, c0: int) -> int:
    return max(2, math.ceil(n / c0))


def per_coset_deficit_bits(c0: int) -> float:
    """log2 E[2B] - E[log2 2B | B >= 1],  B ~ Bin(S, 1/2), S = 2^c0.

    Own implementation: exact pmf via lgamma in log space (the producer uses a
    cumulative-sum log-factorial table with numpy; same mathematics, different code)."""
    S = 2 ** c0
    if S > (1 << 20):
        return 1.0 / (2.0 * S * math.log(2.0))          # second-order expansion
    logS_fact = math.lgamma(S + 1)
    w = 0.0
    acc = 0.0
    for b in range(1, S + 1):
        lp = logS_fact - math.lgamma(b + 1) - math.lgamma(S - b + 1) - S * math.log(2.0)
        p = math.exp(lp)
        w += p
        acc += p * math.log2(2.0 * b)
    return math.log2(S) - acc / w                         # E[2B] = S exactly


_DEF = {}


def total_deficit_bits(n: int, c0: int) -> float:
    if c0 not in _DEF:
        _DEF[c0] = per_coset_deficit_bits(c0)
    return m_of(n, c0) * _DEF[c0]


def bound_B_min(n: int, tol: float = 1.0, c0_max: int = 40) -> int:
    prof = [total_deficit_bits(n, c) for c in range(1, c0_max + 1)]
    for i, _ in enumerate(prof):
        if all(x <= tol for x in prof[i:]):
            return i + 1
    return None


def bound_A_min(n: int, eps: float = 0.05) -> int:
    for c0 in range(1, 65):
        m = m_of(n, c0)
        lp = m * math.log1p(-0.5 ** (2 ** c0)) / math.log(2.0) if 2 ** c0 < 1000 else 0.0
        if lp >= math.log2(1 - eps):
            return c0
    return None


def t4_bits(n: int, c0: int) -> tuple[float, float]:
    m = m_of(n, c0)
    log2_lam = (m * c0 - n) - total_deficit_bits(n, c0)
    if log2_lam > 20:
        return 0.0, log2_lam
    if log2_lam < -40:
        return -log2_lam, log2_lam
    lam = 2.0 ** log2_lam
    return -math.log2(-math.expm1(-lam)), log2_lam


def cell(n: int, c0: int, omega: float, reading: str, d_f: int = D_F) -> dict:
    m = m_of(n, c0)
    N = n * (m - 1)
    monos_bin = log2_int(math.comb(N + d_f, d_f))
    t1 = monos_bin if reading == "binomial" else d_f * math.log2(N)
    t2 = (omega - 1.0) * t1
    t3 = log2_int(m * P ** c0 + 1)
    t4, log2_lam = t4_bits(n, c0)
    t5_frozen = monos_bin
    t5_dense = 2.0 * monos_bin
    # additional memory readings this review adds (see report B1(1)):
    rows_first_step = N * (N + 1)                          # N cubics x (N+1) multipliers
    t5_rows_x_cols = log2_int(rows_first_step) + monos_bin  # dense first-step Macaulay
    # sparse storage of the first-step Macaulay matrix: nnz/row <= n^2 (C_0+1) + 2nC_0 + n + 1
    nnz_row = n * n * (c0 + 1) + 2 * n * c0 + n + 1
    t5_sparse_first_step_bits = log2_int(rows_first_step) + math.log2(nnz_row) + math.log2(monos_bin + 1)
    time_dec = t1 + t2 + t3 + t4
    t6 = omega * t3
    time = log2_add(time_dec, t6)
    return {"n": n, "C_0": c0, "omega": omega, "reading": reading, "m": m, "N": N,
            "T1": t1, "T2": t2, "T3": t3, "T4": t4, "log2_lambda": log2_lam,
            "T5_frozen": t5_frozen, "T5_dense": t5_dense,
            "T5_rows_x_cols_first_step": t5_rows_x_cols,
            "T5_sparse_first_step_bits": t5_sparse_first_step_bits,
            "log2_rows_first_step": log2_int(rows_first_step),
            "log2_nnz_per_row_upper": math.log2(nnz_row),
            "T6": t6, "time": time, "time_decompose": time_dec}


def vow(n: int, metric: str, extra_time_bits: float = 0.0) -> float:
    """W = 0.886 2^{n/2} group ops (+ extra_time_bits when converting the unit);
    Mem = 3n max(w, M) bits; T = W(1/M + 1/w)."""
    w = LOG2_0886 + n / 2.0 + extra_time_bits
    prod = math.log2(6.0 * n) + w
    if metric == "time_only":
        return w
    if metric in ("time_memory_product", "area_time_AT"):
        return prod
    if metric == "equal_rate_max":
        return prod / 2.0
    raise ValueError(metric)


def nagao_metric(c: dict, metric: str, mem_key: str) -> float:
    if metric == "time_only":
        return c["time"]
    if metric in ("time_memory_product", "area_time_AT"):
        return c["time"] + c[mem_key]
    if metric == "equal_rate_max":
        return max(c["time"], c[mem_key])
    raise ValueError(metric)


# ----------------------------------------------------------------------------- main
def main() -> None:
    surf = json.load(open(os.path.join(RUN, "cost-surface.json")))
    kf = json.load(open(os.path.join(RUN, "known-false-dF5.json")))
    out = {"comparison": [], "flags": {}, "survivors": {}, "erasing": [], "unit": [],
           "omitted_terms_n571_C0_8": {}, "bounds": {}}

    # ---- (0) recompute every producer cell at committed omega, compare to 0.05 bits
    worst = 0.0
    worst_where = None
    n_compared = 0
    for pc in surf["cells"]:
        if pc["omega"] not in OMEGAS:
            continue
        rd = "binomial" if pc["monomial_count_reading"].startswith("binomial") else "loose"
        c = cell(pc["n"], pc["C_0"], pc["omega"], rd)
        diffs = {
            "T1": c["T1"] - pc["T1_monomial_count_log2"],
            "T2": c["T2"] - pc["T2_linear_algebra_exponent_log2"],
            "T3": c["T3"] - pc["T3_coset_constant_log2"],
            "T4": c["T4"] - pc["T4_inverse_yield_log2"],
            "T5f": c["T5_frozen"] - pc["T5_memory_log2_frozen_width"],
            "T5d": c["T5_dense"] - pc["T5_memory_log2_dense_width_squared"],
            "T6": c["T6"] - pc["T6_index_calculus_linalg_log2"],
            "time": c["time"] - pc["time_log2_total"],
        }
        for key, mg in pc["margins"].items():
            metric, memr = key.split("|")
            mem_key = "T5_frozen" if memr.startswith("frozen") else "T5_dense"
            mine = nagao_metric(c, metric, mem_key) - vow(pc["n"], metric)
            diffs["margin:" + key] = mine - mg["margin_bits_nagao_minus_vow"]
        for k, v in diffs.items():
            n_compared += 1
            if abs(v) > worst:
                worst, worst_where = abs(v), (pc["n"], pc["C_0"], pc["omega"], rd, k)
    out["comparison"] = {"values_compared": n_compared, "worst_abs_diff_bits": worst,
                         "worst_where": worst_where}

    # ---- (1) flags: own filter over the producer's cells, then own recomputation
    def own_flags(source: str):
        flags = []
        for n in NS:
            for omega in OMEGAS + [2.7]:
                for c0 in C0S:
                    for rd in ("binomial", "loose"):
                        c = cell(n, c0, omega, rd)
                        for metric in MEMORY_METRICS:
                            for mem_key, memr in (("T5_frozen", "frozen"), ("T5_dense", "dense")):
                                mg = nagao_metric(c, metric, mem_key) - vow(n, metric)
                                if mg < 0:
                                    flags.append({"n": n, "omega": omega, "C_0": c0, "reading": rd,
                                                  "metric": metric, "memory": memr, "margin": mg,
                                                  "bound_B_ok": c0 >= bound_B_min(n),
                                                  "bound_A_ok": c0 >= bound_A_min(n),
                                                  "T6_minus_time": c["T6"] - c["time"],
                                                  "T1": c["T1"], "N": c["N"], "m": c["m"]})
        return flags

    flags = own_flags("own")
    committed = [f for f in flags if f["omega"] in OMEGAS]
    committed_B = [f for f in committed if f["bound_B_ok"]]
    out["flags"] = {
        "all_memory_charging_metric_flags": len(flags),
        "committed_omega": len(committed),
        "committed_omega_and_bound_B": len(committed_B),
        "producer_reported": [242, 180, 120],
        "producer_json_list_length": len(surf["escalation_flags_memory_charging_metric_nagao_ahead"]),
    }
    out["bounds"] = {n: {"A": bound_A_min(n), "B": bound_B_min(n)} for n in NS}

    # ---- survivors under each memory reading (120-cell set, then re-listed)
    def survivors(fl, memr):
        return [f for f in fl if f["memory"] == memr]

    def by_cell(fl):
        d = {}
        for f in fl:
            d.setdefault((f["n"], f["omega"], f["C_0"], f["reading"], f["metric"]), f)
        return d

    frozen120 = survivors(committed_B, "frozen")
    dense120 = survivors(committed_B, "dense")
    out["survivors"] = {
        "frozen_width": {"count": len(frozen120),
                         "cells": sorted(set((f["n"], f["omega"], f["C_0"], f["reading"], f["metric"]) for f in frozen120))},
        "dense_width_squared": {"count": len(dense120),
                                "cells": sorted(set((f["n"], f["omega"], f["C_0"], f["reading"], f["metric"]) for f in dense120))},
    }
    # the additional readings: rows x cols (dense first step) and sparse first step
    extra = {"rows_x_cols_first_step": [], "sparse_first_step_bits": []}
    for n in [409, 571]:
        for omega in OMEGAS:
            for c0 in C0S:
                if c0 < bound_B_min(n):
                    continue
                for rd in ("binomial", "loose"):
                    c = cell(n, c0, omega, rd)
                    for metric in MEMORY_METRICS:
                        for key, name in (("T5_rows_x_cols_first_step", "rows_x_cols_first_step"),
                                          ("T5_sparse_first_step_bits", "sparse_first_step_bits")):
                            mg = nagao_metric(c, metric, key) - vow(n, metric)
                            if mg < 0:
                                extra[name].append({"n": n, "omega": omega, "C_0": c0, "reading": rd,
                                                    "metric": metric, "margin": mg})
    out["survivors"]["rows_x_cols_first_step"] = {"count": len(extra["rows_x_cols_first_step"]),
                                                  "flags": extra["rows_x_cols_first_step"]}
    out["survivors"]["sparse_first_step_bits"] = {"count": len(extra["sparse_first_step_bits"]),
                                                  "flags": extra["sparse_first_step_bits"]}

    # ---- (2) erasing constants beside ARM K's d_F 4 -> 5 rise, dense reading, n = 571
    #      (and frozen for comparison).  Rise computed from the definitions and checked
    #      against known-false-dF5.json at the same cells.
    kf_index = {}
    kf_cells = kf.get("cells", kf if isinstance(kf, list) else [])
    for kc in kf_cells:
        # known-false-dF5.json names the monomial-count reading `reading` (cost-surface.json
        # names it `monomial_count_reading`); index by whichever is present.
        rd_key = kc.get("reading", kc.get("monomial_count_reading"))
        kf_index[(kc["n"], kc["C_0"], kc["omega"], rd_key)] = kc
    eras = []
    for f in sorted(dense120 + frozen120, key=lambda x: (x["n"], x["omega"], x["C_0"], x["reading"], x["metric"], x["memory"])):
        if f["metric"] != "time_memory_product":
            continue                      # AT is charged identically; equal-rate handled below
        n, c0, omega, rd = f["n"], f["C_0"], f["omega"], f["reading"]
        c4 = cell(n, c0, omega, rd, 4)
        c5 = cell(n, c0, omega, rd, 5)
        mem_key = "T5_frozen" if f["memory"] == "frozen" else "T5_dense"
        time_rise = c5["time"] - c4["time"]
        mem_rise = c5[mem_key] - c4[mem_key]
        kfc = kf_index.get((n, c0, omega, "binomial_C_N_plus_d_choose_d" if rd == "binomial" else "nagao_loose_N_to_the_d"))
        eras.append({"n": n, "omega": omega, "C_0": c0, "reading": rd, "memory": f["memory"],
                     "margin_TxM": f["margin"], "erasing_constant_bits": -f["margin"],
                     "dF5_time_rise": time_rise, "dF5_memory_rise": mem_rise,
                     "dF5_TxM_rise": time_rise + mem_rise,
                     "inside_dF5_range": -f["margin"] <= time_rise + mem_rise,
                     "erasing_constant_as_fraction_of_one_degree": -f["margin"] / (time_rise + mem_rise),
                     "known_false_json_time_rise": (kfc or {}).get("observed_time_rise_bits") if kfc else None})
    out["erasing"] = eras
    # equal-rate survivors (omega = 2.376, C_0 >= 10 per producer)
    er = [f for f in committed_B if f["metric"] == "equal_rate_max"]
    out["equal_rate_survivors"] = [{k: f[k] for k in ("n", "omega", "C_0", "reading", "memory", "margin")} for f in er]

    # ---- (5) unit conversion at the surviving dense flags (and frozen), n = 571
    conv = {"n_log_n": math.log2(571) + math.log2(math.log2(571)), "n_squared": 2.0 * math.log2(571)}
    unit = []
    for f in sorted(dense120, key=lambda x: (x["omega"], x["C_0"], x["reading"], x["metric"])):
        if f["reading"] != "binomial" or f["metric"] == "area_time_AT":
            continue
        n, c0, omega = f["n"], f["C_0"], f["omega"]
        c = cell(n, c0, omega, "binomial")
        row = {"n": n, "omega": omega, "C_0": c0, "metric": f["metric"], "memory": "dense",
               "margin_unconverted": f["margin"]}
        for name, bits in conv.items():
            row["margin_" + name] = nagao_metric(c, f["metric"], "T5_dense") - vow(n, f["metric"], bits)
        unit.append(row)
    out["unit"] = {"conversion_bits_added_to_vow_time_at_571": conv, "rows": unit,
                   "direction_note": "Nagao's unit is one F_2 Macaulay operation; vOW's is one E(F_2^n) group operation "
                                     "(>= one field inversion + 2 multiplications ~ n^2 bit ops schoolbook, ~ n log n with fast "
                                     "arithmetic). Putting both in bit operations multiplies vOW's count, so every conversion "
                                     "RAISES vOW and makes margin = Nagao - vOW MORE negative: it cannot erase a flag."}

    # ---- (4) omitted terms at n = 571, C_0 = 8 (m = 72, N = 40541), bits
    n, c0 = 571, 8
    c = cell(n, c0, 2.807, "binomial")
    m, N = c["m"], c["N"]
    lg = math.log2
    fb_bits = c["T3"]
    trials_bits = fb_bits + c["T4"]
    group_op_bits = 2 * lg(n)                     # schoolbook n^2 bit ops per group op (pessimistic)
    om = {
        "reference_charged_time_bits_omega_2p807": c["time"],
        "reference_charged_TxM_dense_bits": c["time"] + c["T5_dense"],
        "reference_T5_frozen_bits": c["T5_frozen"],
        "O1_weil_descent_per_R_only_last_equation_depends_on_R_bits":
            lg(n) + lg(n * n * (c0 + 1)) + trials_bits,
        "O1b_weil_descent_whole_system_once_bits": lg(m - 1) + lg(n) + lg(n * n * (c0 + 1)),
        "O2_compute_R_two_scalar_mults_per_trial_bits": lg(2 * 1.5 * n) + group_op_bits + trials_bits,
        "O3_relation_verification_per_relation_bits": lg(m) + lg(2) + max(3 * lg(n), group_op_bits) + fb_bits,
        "O4_final_linalg_T6_omega_2p807_bits": c["T6"],
        "O4b_final_linalg_sparse_wiedemann_time_bits": 2 * fb_bits + lg(m),
        "O4c_relation_matrix_memory_dense_bits": 2 * fb_bits,
        "O4d_relation_matrix_memory_sparse_bits": fb_bits + lg(m) + lg(fb_bits),
        "O5_descent_of_P_and_Q": "none: Algorithm 2 decomposes R = n1 P + n2 Q, so P and Q never need a separate descent",
        "O6_communication": "uncharged on both sides; no machine model in the contract; symmetric omission, unboundable here",
        "O7_baseline_side_negation_map_bits_vow_cheaper": 0.5,
        "O7b_baseline_side_cofactor_h_in_{2,4}_bits_vow_cheaper": [0.5, 1.0],
        "O8_over_collection_extra_relations_bits": lg(1 + 2 ** (-fb_bits + lg(64))),
        "O9_randomness_bits_per_trial_log2": lg(2 * n),
        "O12_field_equation_monomial_count_difference_bits": monomial_fe_diff(N),
    }
    om["largest_attack_side_omission_vs_charged_time_bits"] = max(
        om["O1_weil_descent_per_R_only_last_equation_depends_on_R_bits"],
        om["O2_compute_R_two_scalar_mults_per_trial_bits"],
        om["O3_relation_verification_per_relation_bits"],
        om["O4b_final_linalg_sparse_wiedemann_time_bits"]) - c["time"]
    out["omitted_terms_n571_C0_8"] = om

    # ---- dense omega = 3.0, n = 571 margins by C_0 (the +0.3 / negative-from-10 statement)
    out["dense_omega3_n571_TxM_by_C0"] = {
        c0: nagao_metric(cell(571, c0, 3.0, "binomial"), "time_memory_product", "T5_dense") - vow(571, "time_memory_product")
        for c0 in C0S}
    out["dense_n571_TxM_by_omega_C0_binomial"] = {
        f"{omega}|{c0}": nagao_metric(cell(571, c0, omega, "binomial"), "time_memory_product", "T5_dense") - vow(571, "time_memory_product")
        for omega in OMEGAS for c0 in C0S}
    out["frozen_n571_TxM_by_omega_C0_binomial"] = {
        f"{omega}|{c0}": nagao_metric(cell(571, c0, omega, "binomial"), "time_memory_product", "T5_frozen") - vow(571, "time_memory_product")
        for omega in OMEGAS for c0 in C0S}
    out["dense_n409_TxM_by_omega_C0_binomial"] = {
        f"{omega}|{c0}": nagao_metric(cell(409, c0, omega, "binomial"), "time_memory_product", "T5_dense") - vow(409, "time_memory_product")
        for omega in OMEGAS for c0 in C0S}

    json.dump(out, open(os.path.join(HERE, "b1_recompute.json"), "w"), indent=1, default=str)
    write_tables(out)
    print(json.dumps(out["comparison"], indent=1))
    print(json.dumps(out["flags"], indent=1))
    print("bounds", out["bounds"])
    print("survivors frozen", out["survivors"]["frozen_width"]["count"],
          "dense", out["survivors"]["dense_width_squared"]["count"],
          "rows_x_cols", out["survivors"]["rows_x_cols_first_step"]["count"],
          "sparse_first_step", out["survivors"]["sparse_first_step_bits"]["count"])
    print("largest attack-side omission vs charged time (bits):",
          om["largest_attack_side_omission_vs_charged_time_bits"])


def monomial_fe_diff(N: int) -> float:
    a = log2_int(math.comb(N + 4, 4))
    b = log2_int(sum(math.comb(N, d) for d in range(5)))
    return a - b


def write_tables(out: dict) -> None:
    L = []
    L.append("### Survivors of the 120-cell set under each memory reading (own recomputation)\n")
    for name in ("frozen_width", "dense_width_squared"):
        s = out["survivors"][name]
        L.append(f"**{name}**: {s['count']} flag entries; distinct (n, omega, C_0, reading, metric) cells: {len(s['cells'])}\n")
        for cnt in s["cells"]:
            L.append(f"- {cnt}")
        L.append("")
    L.append("### Erasing-constant table (T x M; AT identical), beside ARM K's d_F 4 -> 5 rise\n")
    L.append("| n | omega | C_0 | reading | memory | margin (bits) | erasing constant (bits) | d_F 4->5 time rise | d_F 4->5 memory rise | d_F 4->5 TxM rise | inside? | fraction of one degree |")
    L.append("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for e in out["erasing"]:
        L.append(f"| {e['n']} | {e['omega']} | {e['C_0']} | {e['reading']} | {e['memory']} | {e['margin_TxM']:+.1f} | {e['erasing_constant_bits']:.1f} | {e['dF5_time_rise']:.1f} | {e['dF5_memory_rise']:.1f} | {e['dF5_TxM_rise']:.1f} | {'yes' if e['inside_dF5_range'] else 'NO'} | {e['erasing_constant_as_fraction_of_one_degree']:.2f} |")
    L.append("")
    L.append("### Unit-converted margins at the surviving dense flags, n = 571, binomial reading\n")
    cv = out["unit"]["conversion_bits_added_to_vow_time_at_571"]
    L.append(f"conversion added to vOW's time: n log n -> {cv['n_log_n']:.2f} bits; n^2 -> {cv['n_squared']:.2f} bits (equal-rate takes half).\n")
    L.append("| omega | C_0 | metric | unconverted | n log n | n^2 |")
    L.append("|---|---|---|---|---|---|")
    for r in out["unit"]["rows"]:
        L.append(f"| {r['omega']} | {r['C_0']} | {r['metric']} | {r['margin_unconverted']:+.1f} | {r['margin_n_log_n']:+.1f} | {r['margin_n_squared']:+.1f} |")
    L.append("")
    L.append("### Omitted terms at n = 571, C_0 = 8 (bits)\n")
    for k, v in out["omitted_terms_n571_C0_8"].items():
        L.append(f"- `{k}`: {v if not isinstance(v, float) else round(v, 2)}")
    L.append("")
    open(os.path.join(HERE, "b1_tables.md"), "w").write("\n".join(L))


if __name__ == "__main__":
    main()
