#!/usr/bin/env python3
"""Check that every number quoted in a SEMBIN record matches its raw result.

WHY THIS EXISTS. Three van Oorschot-Wiener figures in COST-SEMBIN-8d123b were
first written by hand from the margins in raw-result.json and were wrong: the
margin is (baseline - attack), and they were transcribed as if it were the
other way round. Every one of them was individually plausible, none was
contradicted by anything else in the record, and the error was caught only by
noticing that 166.2 is not what 0.886*sqrt(2^163) costs. A record whose numbers
are copied by hand needs a checker, or the next such slip ships.

Scope, stated plainly: this checks TRANSCRIPTION and nothing else. It re-reads
the values the records assert and compares them to the run's own raw output. It
cannot tell whether the raw output is right -- that is what
independent_arith.py, the controls, and independent review are for -- and a
clean pass here says only that the prose agrees with the JSON it summarises.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys

import yaml

REPO = os.path.dirname(os.path.dirname(os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))))
TOL = 5e-4          # the records quote 4 decimal places


class Checks:
    def __init__(self) -> None:
        self.rows: list[tuple[bool, str]] = []

    def eq(self, label: str, claimed, actual, tol: float = TOL) -> None:
        if isinstance(claimed, (int, float)) and isinstance(actual, (int, float)):
            ok = math.isclose(float(claimed), float(actual), abs_tol=tol)
        else:
            ok = claimed == actual
        self.rows.append((ok, f"{label}: record={claimed!r} raw={actual!r}"))

    def report(self) -> int:
        bad = [m for ok, m in self.rows if not ok]
        for ok, m in self.rows:
            print(("  ok   " if ok else "  FAIL ") + m)
        print(f"\n{len(self.rows) - len(bad)}/{len(self.rows)} transcription "
              f"checks agree")
        if bad:
            print("\nTRANSCRIPTION MISMATCH -- the record disagrees with the "
                  "run it summarises. Fix the record, never the raw result.")
        return 1 if bad else 0


def load(path: str):
    with open(os.path.join(REPO, path)) as fh:
        if path.endswith(".json"):
            return json.load(fh)
        return yaml.safe_load(fh)


def check_cost_record(c: Checks) -> None:
    raw = load("experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/"
               "raw-result.json")
    rec = load("experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/"
               "COST-SEMBIN-8d123b.yaml")["concrete_cost"]
    vmap = raw["verdict_map"]
    label_to_n = {163: "163", 233: "233", 283: "283", 409: "409", 571: "571"}

    for pset in rec["parameter_sets"]:
        n = int(str(pset["security_parameter"]).split("=")[1].strip())
        key = label_to_n[n]
        tonly = vmap["time_only_zero_memory_weight"]
        prod = vmap["time_memory_product"]
        d, s = tonly["dense"][key], tonly["semaev_sparse"][key]
        pd, ps = prod["dense"][key], prod["semaev_sparse"][key]
        c.eq(f"n={n} semaev_time_log2", pset["semaev_time_log2"],
             d["semaev_log2_time"])
        c.eq(f"n={n} semaev_memory_log2_dense",
             pset["semaev_memory_log2_dense"], d["semaev_log2_memory_bits"],
             tol=5e-3)
        c.eq(f"n={n} semaev_memory_log2_sparse",
             pset["semaev_memory_log2_sparse"], s["semaev_log2_memory_bits"],
             tol=5e-3)
        c.eq(f"n={n} semaev_optimal_m", pset["semaev_optimal_m"],
             d["m_optimal"])
        c.eq(f"n={n} margin_bits_time_only", pset["margin_bits_time_only"],
             d["margin_bits"])
        c.eq(f"n={n} margin_bits_time_memory_dense",
             pset["margin_bits_time_memory_dense"], pd["margin_bits"])
        c.eq(f"n={n} margin_bits_time_memory_sparse",
             pset["margin_bits_time_memory_sparse"], ps["margin_bits"])
        # The one that was wrong. Derived two independent ways: from the run's
        # own (time, margin) pair, and from the closed form the comparator is
        # defined by. Both must agree with the record.
        c.eq(f"n={n} vow_time_log2 (from run margin)", pset["vow_time_log2"],
             d["semaev_log2_time"] + d["margin_bits"])
        c.eq(f"n={n} vow_time_log2 (from 0.886*2^(n/2))",
             pset["vow_time_log2"], math.log2(0.886) + n / 2.0)

    for metric, per_storage in rec["crossover_n_by_metric"].items():
        for storage, n_star in per_storage.items():
            c.eq(f"crossover {metric}/{storage}", n_star,
                 raw["crossovers_per_metric"][metric][storage]["crossover_n"])

    c.eq("published crossover reproduced", rec["crossover_published"],
         raw["controls"]["baseline_zero_memory_weight"]
         ["crossover_papers_own_convention"])
    c.eq("ceiling crossover unceiled",
         rec["ceiling_discrepancy"]["crossover_unceiled"],
         raw["ceiling_discrepancy"]["crossover_unceiled"])
    c.eq("ceiling crossover ceiled",
         rec["ceiling_discrepancy"]["crossover_ceiled"],
         raw["ceiling_discrepancy"]["crossover_ceiled"])
    for n_key, bits in rec["ceiling_discrepancy"][
            "per_n_stage1_discrepancy_bits"].items():
        row = next(r for r in raw["ceiling_discrepancy"]["per_n"]
                   if r["n"] == int(n_key))
        c.eq(f"ceiling discrepancy bits n={n_key}", bits,
             row["discrepancy_bits"], tol=5e-3)
    for field, degree in (("bits_added_if_the_bound_is_5", 5),
                          ("bits_added_if_the_bound_is_6", 6)):
        for n_key, bits in rec["degree_bound_sensitivity"][field].items():
            row = next(r for r in raw["degree_sensitivity"]["rows"]
                       if r["n"] == int(n_key))
            c.eq(f"degree {degree} bits added n={n_key}", bits,
                 row[f"bits_added_by_degree_{degree}"])


def check_manifest_f4a17b(c: Checks) -> None:
    raw = load("experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/"
               "raw-result.json")
    m = load("experiments/EXP-SEMBIN-f4a17b/runs/RUN-SEMBIN-121b59/"
             "manifest.yaml")["run"]["result"]["metrics"]
    for metric, per_storage in m["crossover_n_by_metric_and_storage"].items():
        for storage, n_star in per_storage.items():
            c.eq(f"manifest crossover {metric}/{storage}", n_star,
                 raw["crossovers_per_metric"][metric][storage]["crossover_n"])
    prod = raw["crossovers_per_metric"]["time_memory_product"]
    tonly = raw["crossovers_per_metric"]["time_only_zero_memory_weight"]
    for storage in ("dense", "semaev_sparse"):
        c.eq(f"manifest memory shift {storage}",
             m["crossover_shift_from_charging_memory_in_n"][storage],
             prod[storage]["crossover_n"] - tonly[storage]["crossover_n"])
    vm = raw["verdict_map"]
    c.eq("manifest 409 time_only margin",
         m["fips_409_margin_bits"]["time_only"],
         vm["time_only_zero_memory_weight"]["dense"]["409"]["margin_bits"])
    c.eq("manifest 409 product dense margin",
         m["fips_409_margin_bits"]["time_memory_product_dense"],
         vm["time_memory_product"]["dense"]["409"]["margin_bits"])
    c.eq("manifest 409 product sparse margin",
         m["fips_409_margin_bits"]["time_memory_product_sparse"],
         vm["time_memory_product"]["semaev_sparse"]["409"]["margin_bits"])
    c.eq("manifest 571 wins everywhere",
         m["fips_571_semaev_wins_under_every_metric"],
         all(vm[met][st]["571"]["semaev_wins"] for met in vm for st in vm[met]))
    c.eq("manifest 163/233/283 lose everywhere",
         m["fips_163_233_283_semaev_loses_under_every_metric"],
         not any(vm[met][st][k]["semaev_wins"]
                 for met in vm for st in vm[met]
                 for k in ("163", "233", "283")))
    c.eq("manifest ceiling unceiled", m["ceiling_discrepancy_crossover_unceiled"],
         raw["ceiling_discrepancy"]["crossover_unceiled"])
    c.eq("manifest ceiling ceiled", m["ceiling_discrepancy_crossover_ceiled"],
         raw["ceiling_discrepancy"]["crossover_ceiled"])


def check_manifest_81dc96(c: Checks) -> None:
    raw = load("experiments/EXP-SEMBIN-81dc96/runs/RUN-SEMBIN-aa5161/"
               "raw-result.json")
    m = load("experiments/EXP-SEMBIN-81dc96/runs/RUN-SEMBIN-aa5161/"
             "manifest.yaml")["run"]["result"]["metrics"]
    corr = raw["correction_1_joint_optimum"]
    by_solve = {}
    for key, block in corr.items():
        solve = key.split(",")[0].split("=")[1]
        by_solve[solve] = block
    c.eq("81dc96 n with interior optimum", m["n_with_interior_optimum"],
         sum(b["n_with_interior_optimum"] for b in by_solve.values()))
    c.eq("81dc96 any interior", m["joint_optimum_interior_at_any_n"],
         any(b["n_with_interior_optimum"] for b in by_solve.values()))
    c.eq("81dc96 t*=m* everywhere", m["t_star_equals_m_star_everywhere"],
         all(b["t_star_at_fips"] == b["m_star_at_fips"]
             for b in by_solve.values()))
    c.eq("81dc96 crossover shift", m["crossover_shift_in_n"],
         max(abs(b["crossover_shift"]) for b in by_solve.values()))
    for solve, field in (("block_n4w", "crossover_block_n4w"),
                         ("macaulay4", "crossover_macaulay4"),
                         ("f4_std", "crossover_f4_std")):
        c.eq(f"81dc96 {field}", m[field], by_solve[solve]["crossover_joint"])
    for field, solve in (("t_star_at_fips_block_n4w", "block_n4w"),
                         ("m_star_at_fips_block_n4w", "block_n4w")):
        which = "t_star_at_fips" if field.startswith("t_") else "m_star_at_fips"
        for n_key, v in m[field].items():
            c.eq(f"81dc96 {field} n={n_key}", v,
                 by_solve[solve][which][str(n_key)])
    c.eq("81dc96 exponent constant", m["exponent_constant_c_published"],
         raw["exponent_constant"]["c_published_eq17"], tol=5e-6)
    c.eq("81dc96 exponent claim", m["exponent_constant_claim"],
         raw["exponent_constant"]["claim"])
    c.eq("81dc96 heur006 agreement",
         m["heur006_readings_agree_about_interiority"],
         raw["heur006_readings"]["readings_agree_qualitatively_about_interiority"])
    c.eq("81dc96 prediction refuted",
         load("experiments/EXP-SEMBIN-81dc96/runs/RUN-SEMBIN-aa5161/"
              "manifest.yaml")["run"]["result"]
         ["preregistered_prediction_refuted"],
         raw["preregistered_outcome"]["prediction_refuted"])
    arith = load("experiments/EXP-SEMBIN-81dc96/runs/RUN-SEMBIN-aa5161/"
                 "independent-arithmetic.json")
    c.eq("81dc96 cofactor exceeds stage2 at 571",
         m["cofactor_exceeds_stage2_at_571"],
         arith["load_bearing"]["cofactor_minus_stage2_bits"]
         ["cofactor_exceeds_stage2"])
    c.eq("81dc96 cofactor minus stage2 bits",
         m["cofactor_minus_stage2_bits_at_571"],
         arith["load_bearing"]["cofactor_minus_stage2_bits"]["value"])
    c.eq("81dc96 arithmetic control passed", True,
         arith["all_checks_passed"])


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.parse_args()
    c = Checks()
    print("COST-SEMBIN-8d123b against RUN-SEMBIN-121b59/raw-result.json")
    check_cost_record(c)
    print("\nRUN-SEMBIN-121b59/manifest.yaml against its raw result")
    check_manifest_f4a17b(c)
    print("\nRUN-SEMBIN-aa5161/manifest.yaml against its raw result")
    check_manifest_81dc96(c)
    print()
    return c.report()


if __name__ == "__main__":
    sys.exit(main())
