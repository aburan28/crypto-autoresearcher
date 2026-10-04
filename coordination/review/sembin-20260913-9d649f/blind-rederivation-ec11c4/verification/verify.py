#!/usr/bin/env python3
"""Phase-two verification for joint J6-BLIND, TASK-20260913-ec11c4.

NOT part of the blind re-derivation.  Written after the producer's record was
read, and it says so.  Three things the frozen localisation did not check:

  A. Whether the producer's crossover 375 is the FIRST n at which its own model
     is cheaper, or only the first inside the window [250, 650] that
     crossover_curve() hardcodes.  My blind model has a cheaper point at n = 3,
     so the same question has to be asked of the producer's.
  B. Whether COST-SEMBIN-8d123b.yaml transcribes its own run's raw-result.json,
     rather than being retyped by hand.
  C. Whether the second implementation (independent_arith.py) re-derives the
     sparse working set or retypes the same (nm)^4/24 * n^3/m constant.  If it
     retypes it, the two implementations agreeing says nothing about that term.

Run from the parent directory of this file (needs rederivation.py importable).
"""

from __future__ import annotations

import json
import os
import re
import sys
from fractions import Fraction

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from rederivation import (  # noqa: E402
    Interval,
    Model,
    baseline_cost,
    log2_float,
    relation_store_bits,
)

REPO = "/workspace"
RUN = f"{REPO}/experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59"
IND = f"{REPO}/experiments/EXP-SEMBIN-81dc96/code/independent_arith.py"


def producer_sparse_working_set_bits(n: int, m: int) -> Fraction:
    """(nm)^4/24 columns times n^3/m nonzeros per row, one bit each.

    Retyped from memory_charged_cost.py semaev_memory_log2, storage
    "semaev_sparse", lines cols_log2 / nz_per_row_log2.
    """
    return Fraction((n * m) ** 4, 24) * Fraction(n ** 3, m)


class ProducerSparseModel(Model):
    def attack_memory(self, n: int, m: int) -> int:
        # producer sums the two terms (log2_add); at these parameters one
        # dominates, so sum and max agree to ~1e-6 bits.
        return int(Fraction(relation_store_bits(n, m))
                   + producer_sparse_working_set_bits(n, m))


def check_a_scan_window() -> dict:
    """Is 375 the first crossing, or the first crossing above 250?"""
    mdl = ProducerSparseModel(yield_mode="closed", m_objective="time",
                              storage="sparse", nvars="plan")
    region_full = mdl.cheaper_region(3, 700)
    region_window = mdl.cheaper_region(250, 650)
    return {
        "question": "is the record's 375 the smallest n, or the smallest n >= 250?",
        "producer_model_scanned_from_3": {
            "smallest_cheaper": region_full["smallest_cheaper"],
            "last_not_cheaper": region_full["last_not_cheaper"],
            "final_crossover": region_full["final_crossover"],
            "contiguous_cheaper_runs": region_full["contiguous_cheaper_runs"],
        },
        "producer_model_scanned_from_250": {
            "final_crossover": region_window["final_crossover"],
            "smallest_cheaper": region_window["smallest_cheaper"],
        },
        "record_crossover_n": 375,
    }


def check_b_record_vs_raw() -> dict:
    """Does the COST record's headline agree with its own raw-result.json?"""
    raw = json.load(open(f"{RUN}/raw-result.json"))
    cx = raw["crossovers_per_metric"]["time_memory_product"]["semaev_sparse"]
    vm = raw["verdict_map"]["time_memory_product"]["semaev_sparse"]["409"]
    return {
        "raw_crossover_n": cx["crossover_n"],
        "raw_monotone_after_crossover": cx["monotone_after_crossover"],
        "raw_margin_at_409": cx["margin_at_409"],
        "raw_verdict_map_margin_409": vm["margin_bits"],
        "raw_verdict_map_memory_409": vm["semaev_log2_memory_bits"],
        "cost_record_crossover_n": 375,
        "cost_record_margin_409": 11.5175,
        "cost_record_memory_409": 66.5250,
        "record_matches_raw": (cx["crossover_n"] == 375
                               and abs(cx["margin_at_409"] - 11.5175) < 5e-4
                               and abs(vm["semaev_log2_memory_bits"] - 66.5250) < 5e-4),
    }


def check_c_second_implementation() -> dict:
    """Does independent_arith.py re-derive the sparse term or retype it?"""
    src = open(IND).read()
    hits = {
        "mentions_24_divisor": bool(re.search(r"\b24\b", src)),
        "mentions_n_m_fourth_power": bool(re.search(r"\*\*\s*4|\^4|4\s*\*\s*log", src)),
        "mentions_semaev_sparse": "semaev_sparse" in src,
        "mentions_nonzeros_per_row": bool(re.search(r"nz_per_row|nonzero", src)),
    }
    snippets = [ln.strip() for ln in src.splitlines()
                if re.search(r"24|nz_per_row|semaev_sparse", ln)]
    return {"signals": hits, "matching_lines": snippets[:25],
            "question": ("if the same (nm)^4/24 * n^3/m appears here, the two "
                         "implementations agreeing is evidence about the "
                         "arithmetic and not about the storage model")}


def check_d_margin_curve_shape() -> dict:
    """The plan asks for 'the smallest integer n at which the attack is
    cheaper'. Report the sign pattern under MY plan-literal model so the
    ambiguity is visible as data rather than as an assertion."""
    mdl = Model(yield_mode="closed", m_objective="time", storage="sparse",
                nvars="plan")
    signs = []
    for n in list(range(3, 30)) + [100, 200, 250, 300, 303, 304, 305, 306, 307]:
        _, _, _, cost = mdl.best_m(n)
        signs.append({"n": n,
                      "attack_cheaper": cost.strictly_below(baseline_cost(n))})
    return {"sign_samples": signs,
            "note": ("cheaper at n = 3 then dearer from 4 to 305 then cheaper "
                     "from 306: 'the smallest integer n' has two answers under "
                     "the plan's own parameters")}


def check_e_term_decomposition() -> dict:
    """Decompose the 18.25-bit gap at n = 409 into named terms.

    The plan's sparse reading charges the Macaulay COLUMN COUNT and nothing
    else ("one field element per nonzero"); the producer charges that same
    column count TIMES n^3/m nonzeros per row.  Check that the two column
    counts really are the same object before blaming the row factor, so the
    localisation is not a coincidence of two unrelated numbers.
    """
    import math
    n, m = 409, 11
    from rederivation import (boolean_monomials_upto, macaulay_variables_paper,
                              macaulay_variables_plan)

    cols_producer = Fraction((n * m) ** 4, 24)
    nz_per_row = Fraction(n ** 3, m)
    width_paper = boolean_monomials_upto(macaulay_variables_paper(n, m))
    width_plan = boolean_monomials_upto(macaulay_variables_plan(n, m))
    rel = relation_store_bits(n, m)

    def l2(x):
        return round(log2_float(Interval.exact(Fraction(x))), 4)

    plan_mem = max(rel, width_plan)
    prod_mem = int(Fraction(rel) + cols_producer * nz_per_row)
    return {
        "n": n, "m": m,
        "macaulay_column_count_log2": {
            "producer_(nm)^4/24": l2(cols_producer),
            "degree4_monomials_in_paper_N_4099": l2(width_paper),
            "degree4_monomials_in_plan_N_1236": l2(width_plan),
            "producer_vs_paper_N_gap_bits": round(
                l2(cols_producer) - l2(width_paper), 4),
            "finding": ("the producer's (nm)^4/24 and the paper-N degree-4 "
                        "monomial count agree to about half a bit, so dense and "
                        "sparse really are two storage conventions on the same "
                        "matrix, not two different matrices"),
        },
        "nonzeros_per_row_log2_n^3/m": l2(nz_per_row),
        "relation_store_log2": l2(rel),
        "attack_memory_log2": {
            "plan_as_written": l2(plan_mem),
            "producer": l2(prod_mem),
            "gap_bits": round(l2(prod_mem) - l2(plan_mem), 4),
        },
        "margin_gap_bits": {
            "my_blind_margin_409": 29.7710,
            "record_margin_409": 11.5175,
            "difference": round(29.7710 - 11.5175, 4),
        },
        "binding_term": {
            "plan_as_written": ("relation_store 2^48.27, which exceeds the "
                                "column count 2^36.50 (plan N) / 2^43.42 "
                                "(paper N)"),
            "producer": "sparse working set 2^66.53",
        },
        "conclusion": ("the memory gap equals the margin gap to 4 dp, and it is "
                       "exactly the n^3/m nonzeros-per-row factor that the "
                       "plan's 'one field element per nonzero' wording drops"),
    }


def main() -> None:
    out = {
        "schema": "crypto.autoresearch.blind_rederivation_verification.v1",
        "task_id": "TASK-20260913-ec11c4",
        "phase": ("phase two: written AFTER the producer's record was read; "
                  "this file is not blind and does not claim to be"),
        "A_scan_window_sensitivity": check_a_scan_window(),
        "B_cost_record_vs_own_raw_result": check_b_record_vs_raw(),
        "C_second_implementation_independence": check_c_second_implementation(),
        "D_crossover_definition_ambiguity": check_d_margin_curve_shape(),
        "E_term_decomposition_of_the_gap": check_e_term_decomposition(),
    }
    print(json.dumps(out, indent=2))
    with open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "verification.json"), "w") as fh:
        json.dump(out, fh, indent=2)
        fh.write("\n")


if __name__ == "__main__":
    main()
