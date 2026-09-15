"""TASK-20260913-f6652f, joint B1 extras -- own code, imports b1_recompute (own) only.

(a) dense-width^2 T x M margins at n = 409 for every committed omega and bound-B C_0
    (expected all positive: no 409 flag survives the coherent reading);
(b) the COHERENT r-row family: a Lemma-2 elimination on an r x D matrix costs time
    r^{omega-1} D and memory r D, so T x M = r^omega D^2 is monotone in r; the producer's
    time charge D^omega is r = D (memory D^2).  The one-step rectangular reading
    r = N(N+1) is evaluated only to show that any CHEAPER coherent reading deepens the
    flags (and would restore n = 409) -- it asserts an F4 shape this review may not
    assert and is NOT adopted;
(c) Koblitz Frobenius discount to the vOW baseline (sqrt(n) beyond the negation map
    already in 0.886): 0.5 log2 n bits off W, K-curves only; margins after it;
(d) T6 headroom (T6 - time) at every recomputed flag; the expected-solutions-per-solve
    figure log2 lambda = m C_0 - n - Delta at the grid C_0 (Nagao-favourable harvest).
Writes b1_extras.json."""
from __future__ import annotations

import json
import math
import os

import b1_recompute as B

HERE = os.path.dirname(os.path.abspath(__file__))


def main() -> None:
    out = {}
    # (a)
    out["dense_TxM_margins_n409"] = {
        f"{om}|{c0}|{rd}": B.nagao_metric(B.cell(409, c0, om, rd), "time_memory_product", "T5_dense") - B.vow(409, "time_memory_product")
        for om in B.OMEGAS for c0 in B.C0S if c0 >= B.bound_B_min(409) for rd in ("binomial", "loose")}
    out["min_dense_TxM_margin_n409"] = min(out["dense_TxM_margins_n409"].values())

    # (b) coherent family at the headline cell and at 409
    def coherent(n, c0, om, rd, log2_r):
        c = B.cell(n, c0, om, rd)
        D = c["T1"] if rd == "binomial" else c["T1"]           # log2 D under the reading
        t_dec = (om - 1.0) * log2_r + D + c["T3"] + c["T4"]
        time = B.log2_add(t_dec, c["T6"])
        mem = log2_r + D
        return {"log2_r": log2_r, "time": time, "mem": mem, "TxM": time + mem,
                "TxM_margin": time + mem - B.vow(n, "time_memory_product"),
                "time_margin": time - B.vow(n, "time_only")}

    fam = {}
    for n in (409, 571):
        c = B.cell(n, 8, 2.807, "binomial")
        N = c["N"]
        D = c["T1"]
        fam[n] = {
            "N": N, "log2_D_binomial": D,
            "r_eq_D_dense_producer_time_charge": coherent(n, 8, 2.807, "binomial", D),
            "r_eq_N(N+1)_one_step_rectangular_NOT_ADOPTED": coherent(n, 8, 2.807, "binomial", B.log2_int(N * (N + 1))),
            "r_eq_1_frozen_pairing_time_would_be_D_not_D^omega": coherent(n, 8, 2.807, "binomial", 0.0),
            "producer_frozen_pairing_TxM_margin_incoherent": B.nagao_metric(c, "time_memory_product", "T5_frozen") - B.vow(n, "time_memory_product"),
        }
    out["coherent_r_family_omega_2p807_C0_8"] = fam

    # (c) Koblitz: W -> W / sqrt(n) beyond negation; margins after, at the dense survivors
    kob = 0.5 * math.log2(571)
    rows = []
    for om in B.OMEGAS:
        for c0 in B.C0S:
            if c0 < B.bound_B_min(571):
                continue
            for rd in ("binomial", "loose"):
                c = B.cell(571, c0, om, rd)
                for metric in B.MEMORY_METRICS:
                    m0 = B.nagao_metric(c, metric, "T5_dense") - B.vow(571, metric)
                    if m0 >= 0:
                        continue
                    m1 = B.nagao_metric(c, metric, "T5_dense") - B.vow(571, metric, -kob)
                    rows.append({"omega": om, "C_0": c0, "reading": rd, "metric": metric,
                                 "margin_generic_baseline": m0, "margin_koblitz_baseline": m1,
                                 "erased_for_K_curve": m1 >= 0})
    out["koblitz_discount_bits_on_W"] = kob
    out["dense_survivors_after_koblitz"] = rows
    out["koblitz_erases_count"] = sum(r["erased_for_K_curve"] for r in rows)
    out["koblitz_survivor_count"] = sum(not r["erased_for_K_curve"] for r in rows)

    # (d) T6 headroom and harvest
    t6 = []
    for om in B.OMEGAS:
        for c0 in B.C0S:
            if c0 < B.bound_B_min(571):
                continue
            c = B.cell(571, c0, om, "binomial")
            t6.append({"omega": om, "C_0": c0, "T6_minus_time": c["T6"] - c["time"],
                       "log2_lambda_expected_solutions_per_solve": c["log2_lambda"]})
    out["T6_headroom_and_lambda_n571_binomial"] = t6
    out["max_T6_minus_time_at_bound_B_cells_n571"] = max(r["T6_minus_time"] for r in t6)

    json.dump(out, open(os.path.join(HERE, "b1_extras.json"), "w"), indent=1, default=str)
    print("min dense TxM margin at 409:", round(out["min_dense_TxM_margin_n409"], 2))
    for n, f in fam.items():
        print(n, {k: ({kk: round(vv, 1) for kk, vv in v.items()} if isinstance(v, dict) else (round(v, 2) if isinstance(v, float) else v)) for k, v in f.items()})
    print("koblitz bits:", round(kob, 2), "erases", out["koblitz_erases_count"], "of", len(rows))
    for r in rows:
        if r["erased_for_K_curve"]:
            print("   erased:", r)
    print("max T6 - time at bound-B cells (571, binomial):", round(out["max_T6_minus_time_at_bound_B_cells_n571"], 1))
    print("lambda:", [(r["C_0"], round(r["log2_lambda_expected_solutions_per_solve"], 2)) for r in t6 if r["omega"] == 2.807])


if __name__ == "__main__":
    main()
