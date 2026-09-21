#!/usr/bin/env python3
"""Post-blind localisation: which single step accounts for the disagreement?

Run AFTER figures-before-reading.json was written and hashed.  This script is
the localisation deliverable of joint J6-BLIND, not part of the blind
re-derivation: it substitutes the producer's own sparse-storage formula into my
independent implementation, one term at a time, and reports which substitution
closes the gap.

It imports nothing from the producer's code.  The producer's formula is
retyped here from the two lines that define it so the substitution is explicit.
"""

from __future__ import annotations

import json
from decimal import Decimal
from fractions import Fraction

from rederivation import (
    Interval,
    Model,
    baseline_cost,
    baseline_memory_bits,
    baseline_time,
    boolean_monomials_upto,
    log2_float,
    macaulay_variables_paper,
    macaulay_variables_plan,
    relation_store_bits,
)

# The record's own figures, transcribed from
# experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/COST-SEMBIN-8d123b.yaml
RECORD = {
    163: {"time": 123.7697, "mem_dense": 70.3526, "mem_sparse": 55.2782, "m": 7,
          "vow_time": 81.3254, "margin_sparse": -58.7888, "margin_dense": -73.8632},
    233: {"time": 138.7283, "mem_dense": 77.7467, "mem_sparse": 59.9741, "m": 9,
          "vow_time": 116.3254, "margin_sparse": -42.9278, "margin_dense": -60.7004},
    283: {"time": 147.6495, "mem_dense": 80.0103, "mem_sparse": 61.9374, "m": 9,
          "vow_time": 141.3254, "margin_sparse": -28.5319, "margin_dense": -46.6047},
    409: {"time": 166.5438, "mem_dense": 86.8371, "mem_sparse": 66.5250, "m": 11,
          "vow_time": 204.3254, "margin_sparse": 11.5175, "margin_dense": -8.7946},
    571: {"time": 186.3070, "mem_dense": 91.7726, "mem_sparse": 70.2718, "m": 12,
          "vow_time": 285.3254, "margin_sparse": 69.4889, "margin_dense": 47.9882},
}
RECORD_CROSSOVER = {"time_memory_product_sparse": 375,
                    "time_memory_product_dense": 435,
                    "time_only": 303}


# --------------------------------------------------------------------------
# the producer's sparse formula, retyped from its two defining lines
# --------------------------------------------------------------------------

def producer_sparse_working_set_bits(n: int, m: int) -> Fraction:
    """(n*m)^4 / 24 columns times n^3 / m nonzeros per row, one bit per nonzero.

    Retyped from memory_charged_cost.py semaev_memory_log2, storage
    "semaev_sparse".  Attributed there to Semaev's reply in the ellipticnews
    thread recorded as KN-LIT-e77232, NOT derived from the frozen paper.
    Evaluated as an exact rational so the comparison carries no float error.
    """
    cols = Fraction((n * m) ** 4, 24)
    nz_per_row = Fraction(n ** 3, m)
    return cols * nz_per_row


def plan_sparse_working_set_bits(n: int, m: int, nvars: str = "plan") -> int:
    """The review plan's sparse reading: "charges the width itself (one field
    element per nonzero)", i.e. the degree-<=4 monomial count."""
    nv = macaulay_variables_plan(n, m) if nvars == "plan" else macaulay_variables_paper(n, m)
    return boolean_monomials_upto(nv)


def l2(x) -> float:
    return log2_float(Interval.exact(Fraction(x)))


# --------------------------------------------------------------------------
# term-by-term reconciliation at each of the record's parameter sets
# --------------------------------------------------------------------------

def reconcile() -> dict:
    rows = []
    for n, rec in RECORD.items():
        m = rec["m"]
        mine_m, mine_time, _, _ = Model(m_objective="time").best_m(n)
        rel = relation_store_bits(n, m)
        dense_plan = boolean_monomials_upto(macaulay_variables_plan(n, m)) ** 2
        dense_paper = boolean_monomials_upto(macaulay_variables_paper(n, m)) ** 2
        rows.append({
            "n": n,
            "optimal_m": {"record": m, "mine": mine_m, "agree": m == mine_m},
            "attack_time_log2": {
                "record": rec["time"],
                "mine": round(log2_float(mine_time), 4),
                "delta": round(log2_float(mine_time) - rec["time"], 4)},
            "baseline_time_log2": {
                "record": rec["vow_time"],
                "mine": round(log2_float(baseline_time(n)), 4),
                "delta": round(log2_float(baseline_time(n)) - rec["vow_time"], 4)},
            "baseline_memory_log2": {
                "record_implied": round(
                    rec["margin_sparse"] + rec["time"] + rec["mem_sparse"]
                    - rec["vow_time"], 4),
                "mine": round(l2(baseline_memory_bits(n)), 4)},
            "attack_memory_dense_log2": {
                "record": rec["mem_dense"],
                "mine_nvars_paper": round(l2(dense_paper), 4),
                "mine_nvars_plan": round(l2(dense_plan), 4),
                "delta_vs_paper": round(l2(dense_paper) - rec["mem_dense"], 4)},
            "attack_memory_sparse_log2": {
                "record": rec["mem_sparse"],
                "plan_as_written_width_only_nvars_plan": round(
                    l2(max(rel, plan_sparse_working_set_bits(n, m, "plan"))), 4),
                "plan_as_written_width_only_nvars_paper": round(
                    l2(max(rel, plan_sparse_working_set_bits(n, m, "paper"))), 4),
                "producer_formula_retyped": round(
                    l2(max(Fraction(rel), producer_sparse_working_set_bits(n, m))), 4),
                "producer_formula_retyped_summed_not_maxed": round(
                    l2(Fraction(rel) + producer_sparse_working_set_bits(n, m)), 4)},
            "relation_store_log2": round(l2(rel), 4),
            "which_term_binds_under_producer_formula": (
                "producer_sparse_working_set"
                if producer_sparse_working_set_bits(n, m) > rel else "relation_store"),
        })
    return {"per_parameter_set": rows}


# --------------------------------------------------------------------------
# substitute the producer's formula into MY model and re-run the crossover
# --------------------------------------------------------------------------

class ProducerSparseModel(Model):
    """My model with exactly one term replaced: the sparse working set."""

    def attack_memory(self, n: int, m: int) -> int:
        rel = Fraction(relation_store_bits(n, m))
        ws = producer_sparse_working_set_bits(n, m)
        # the record's code sums the two in log2 space (log2_add); at these
        # parameters one term dominates by >18 bits so sum and max agree to
        # ~2e-6 bits.  Summed here to match the producer exactly.
        return int(rel + ws)


def substitution_test() -> dict:
    mdl = ProducerSparseModel(yield_mode="closed", m_objective="time",
                              storage="sparse", nvars="plan")
    margin, detail = mdl.margin_bits(409)
    region = mdl.cheaper_region(250, 650)
    return {
        "description": (
            "my implementation, unchanged except that the sparse working set is "
            "the producer's (nm)^4/24 * n^3/m instead of the plan's "
            "'width itself'"),
        "crossover_n_scan_250_650": region["final_crossover"],
        "record_crossover_n": RECORD_CROSSOVER["time_memory_product_sparse"],
        "crossover_agrees": (region["final_crossover"]
                             == RECORD_CROSSOVER["time_memory_product_sparse"]),
        "margin_bits_at_409": round(margin, 4),
        "record_margin_bits_at_409": RECORD["409"] if False else 11.5175,
        "margin_agrees_to_2dp": abs(round(margin, 2) - 11.52) < 0.005,
        "m_star_at_409": detail["m_star"],
        "attack_memory_bits_log2_at_409": detail["attack_memory_bits_log2"],
    }


def dense_agreement_test() -> dict:
    """The dense branch should already agree with no substitution at all, since
    the plan's description of the DENSE reading (width^2) matches the producer's
    -- provided N is the paper's variable count and not the plan's."""
    out = {}
    for nvars in ("paper", "plan"):
        mdl = Model(yield_mode="closed", m_objective="time", storage="dense",
                    nvars=nvars)
        margin, detail = mdl.margin_bits(409)
        region = mdl.cheaper_region(250, 650)
        out[f"nvars_{nvars}"] = {
            "crossover_n_scan_250_650": region["final_crossover"],
            "margin_bits_at_409": round(margin, 4),
            "attack_memory_bits_log2_at_409": detail["attack_memory_bits_log2"],
            "matches_record_crossover_435": (
                region["final_crossover"] == RECORD_CROSSOVER["time_memory_product_dense"]),
            "matches_record_margin_minus_8_79": abs(round(margin, 2) + 8.79) < 0.006,
        }
    return out


def main() -> None:
    out = {
        "schema": "crypto.autoresearch.blind_rederivation_localisation.v1",
        "task_id": "TASK-20260913-ec11c4",
        "note": (
            "produced AFTER figures-before-reading.json "
            "(sha256 301cbd861809dd3f2bb997621541c59be487743d1e320bc2280f61dfe8e67596)"),
        "my_blind_figures": {"crossover_n": 306, "margin_bits_at_n_409": 29.77},
        "record_figures": {"crossover_n": 375, "margin_bits_at_n_409": 11.5175},
        "reconciliation": reconcile(),
        "substitution_test_producer_sparse_formula": substitution_test(),
        "dense_branch_agreement_without_substitution": dense_agreement_test(),
    }
    print(json.dumps(out, indent=2))
    with open("localisation.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
