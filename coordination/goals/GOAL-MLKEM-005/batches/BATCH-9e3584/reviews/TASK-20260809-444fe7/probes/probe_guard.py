#!/usr/bin/env python3
"""PROBE M (red team, TASK-20260809-444fe7) -- IS X_mp = rawtail A FAIR GUARD?

NOT PRE-REGISTERED. Rescores NO frozen verdict: every G-REL verdict in
report_relvar.md stands exactly as the producer reported it, and this probe
adds a quantity the frozen text never asked for -- the MARGIN by which each
candidate clears or misses tau_rel, in its own units, and the NORMALIZATION
REGIME each candidate is scored in. CLAIM TIER TOY.

RE-EXECUTABLE from the repository root:
    python3 <this file> --out probe_guard_output.json

Input: the producer's OWN committed per-basis entries, read from
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/tasks/
        TASK-20260809-cda2f6/results_relvar.json
at git c034ef38 (or the working tree copy, whichever the --results flag names).
Nothing is re-measured; every number below is derived from committed numbers,
so this probe cannot disagree with the producer about any measurement, only
about what the measurements support.

WHAT IT ATTACKS
---------------
AM-10(c) requires "at least one declared candidate that MUST PASS [the
criterion], so the criterion has a could-not-PASS guard of its own".
BATCH-9e3584 declares X_mp = rawtail. report_relvar.md section 7 concludes:
"G-REL could-not-PASS -- averted, and demonstrably: X_mp passed at 10/10 and
14/19, so the criterion was not pinned by its s_X = 1.0 floor into never
firing."

Two things a binary MUST-PASS guard cannot establish, and this probe measures
both:

  (Q1) THE REGIME. rho = |X_b - X_a| / max(|X_a|, s_X) has two regimes. When
       |X_a| >= s_X = 1 it is a RELATIVE test; when |X_a| < 1 the denominator
       is pinned at 1 and it is an ABSOLUTE 0.10 test in X's own units. If the
       guard passes only in the relative regime while every research candidate
       is scored in the pinned regime, the guard has not exercised the
       criterion in the regime that decides the candidates.

  (Q2) THE MARGIN. A binary pass tells you the criterion is not identically
       dead. It does not tell you what effect size it can resolve. Define, per
       candidate per cell per basis, the AMPLITUDE MULTIPLIER

           mu = tau_rel * max(|X_a|, s_X) / |X_b - X_a|

       the factor by which that candidate's own mirrored gap would have to be
       multiplied to reach tau_rel. mu < 1 means the entry passes with margin
       1/mu; mu > 1 means it misses by a factor mu. This is a ladder statistic
       of exactly the kind prereg 5.2 pre-registers for Section C2
       (delta/SE in {0.5 .. 12}); Section R pre-registered a binary guard
       instead, and the ladder is what this probe supplies.

MY OWN CHECK'S COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE RUNNING, BOTH WAYS
---------------------------------------------------------------------------
* could-not-FIRE: if the guard and the candidates lived in the same
  normalization regime with comparable mu, the probe would find nothing. That
  is a live outcome -- rawtail and hkz are the SAME functional form
  (mean_{i>=d-beta} log||b*_i|| - logdet/d) evaluated on the raw and on the
  HKZ-reduced basis respectively, so there is no a priori reason their
  magnitudes must differ. The probe fires only if the measured regimes and mu
  distributions actually separate.
* could-not-PASS: if I chose a statistic that must separate them -- e.g. one
  normalised by rawtail's own magnitude -- separation would be built in. mu is
  computed with the FROZEN denominator max(|X_a|, s_X) and the FROZEN
  tau_rel = 0.10, from the producer's own committed X_a and X_b. No threshold
  of mine enters it.

AM-10 / AM-11 ON THIS PROBE'S OWN STATISTICS
--------------------------------------------
mu is reported over all 8 frozen bases at every cell (AM-10 replication) with
its between-basis sd, min, median and max (AM-11 dispersion), never as a
single number.
"""
import argparse
import json
import os
import statistics
import subprocess
import sys
from collections import OrderedDict

import numpy as np

DEFAULT_RESULTS = ("coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/"
                   "tasks/TASK-20260809-cda2f6/results_relvar.json")
TAU_REL = 0.10
S_X = 1.0
CANDS = ["rdet", "lam1n", "hkz", "null", "rawtail"]


def load_results(path):
    if os.path.exists(path):
        return json.load(open(path)), "working tree"
    blob = subprocess.run(["git", "show", "c034ef38:%s" % path],
                          capture_output=True, check=True)
    return json.loads(blob.stdout.decode()), "git c034ef38"


def disp(vals):
    a = np.asarray(vals, dtype=float)
    return {"n": int(a.size), "mean": float(a.mean()),
            "sd": float(a.std(ddof=1)) if a.size > 1 else 0.0,
            "min": float(a.min()), "median": float(np.median(a)),
            "max": float(a.max())}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=DEFAULT_RESULTS)
    ap.add_argument("--out", default="probe_guard_output.json")
    args = ap.parse_args()

    R, src = load_results(args.results)
    OUT = OrderedDict()
    OUT["probe"] = "PROBE-M"
    OUT["task_id"] = "TASK-20260809-444fe7"
    OUT["claim_tier"] = "toy"
    OUT["status_of_this_measurement"] = (
        "RED-TEAM PROBE. NOT PRE-REGISTERED. Derived entirely from the "
        "producer's committed numbers; rescores no verdict.")
    OUT["source"] = {"path": args.results, "read_from": src}

    # ---------------------------------------------------------- Q1 + Q2 on REL2
    per_cell = OrderedDict()
    for c in CANDS:
        rows = OrderedDict()
        for pair, betas in R["G_REL2"][c].items():
            for beta, ent in betas.items():
                if "per_basis" not in ent:
                    continue
                pb = ent["per_basis"]
                mus, binding, absXa, gaps, rhos = [], 0, [], [], []
                for e in pb:
                    Xa, Xb = e["X_a"], e["X_b"]
                    gap = abs(Xb - Xa)
                    den = max(abs(Xa), S_X)
                    mus.append(TAU_REL * den / gap if gap > 0 else float("inf"))
                    binding += 1 if e["scale_floor_is_binding"] else 0
                    absXa.append(abs(Xa))
                    gaps.append(gap)
                    rhos.append(e["value_maxfloor"])
                finite = [m for m in mus if np.isfinite(m)]
                rows["%s_b%s" % (pair, beta)] = {
                    "n_bases": len(pb),
                    "scale_floor_binding_in_n_of_8": binding,
                    "regime": ("PINNED (absolute 0.10 test)" if binding == len(pb)
                               else "RELATIVE" if binding == 0 else "MIXED"),
                    "abs_X_a": disp(absXa),
                    "abs_mirrored_gap": disp(gaps),
                    "rho_maxfloor": disp(rhos),
                    "mu_amplitude_multiplier_to_reach_tau_rel":
                        (disp(finite) if finite else None),
                    "n_bases_passing_of_8": int(sum(r >= TAU_REL for r in rhos)),
                }
        per_cell[c] = rows
    OUT["REL2_per_cell"] = per_cell

    # ---------------------------------------------------------- summaries
    summary = OrderedDict()
    for c in CANDS:
        rows = per_cell[c]
        if not rows:
            continue
        allbind = sum(v["scale_floor_binding_in_n_of_8"] for v in rows.values())
        alln = sum(v["n_bases"] for v in rows.values())
        mus = [v["mu_amplitude_multiplier_to_reach_tau_rel"]["median"]
               for v in rows.values()
               if v["mu_amplitude_multiplier_to_reach_tau_rel"]]
        summary[c] = {
            "n_cells": len(rows),
            "entries_in_the_PINNED_regime_of_total":
                "%d of %d" % (allbind, alln),
            "fraction_pinned": allbind / alln if alln else None,
            "median_mu_over_cells": (statistics.median(mus) if mus else None),
            "min_mu_over_cells": (min(mus) if mus else None),
            "max_mu_over_cells": (max(mus) if mus else None),
            "n_cells_passing_at_mean_over_8": sum(
                1 for v in rows.values() if v["rho_maxfloor"]["mean"] >= TAU_REL),
        }
    OUT["SUMMARY_REL2"] = summary

    # ------------------------------------- the guard vs the candidates, same cells
    # hkz and lam1n exist only on the small-d pairs. Compare the guard's mu
    # against the candidates' mu AT THE VERY SAME CELLS, so no cell-selection
    # effect can enter.
    shared = OrderedDict()
    for cell in per_cell["hkz"]:
        row = {}
        for c in ("rawtail", "hkz", "lam1n", "null"):
            v = per_cell[c].get(cell)
            if v and v["mu_amplitude_multiplier_to_reach_tau_rel"]:
                row[c] = {
                    "mu_median": v["mu_amplitude_multiplier_to_reach_tau_rel"]["median"],
                    "regime": v["regime"],
                    "abs_gap_median": v["abs_mirrored_gap"]["median"],
                    "abs_X_a_median": v["abs_X_a"]["median"],
                    "n_pass_of_8": v["n_bases_passing_of_8"],
                }
        if "rawtail" in row and "hkz" in row:
            row["ratio_mu_hkz_over_mu_rawtail"] = (
                row["hkz"]["mu_median"] / row["rawtail"]["mu_median"])
            row["ratio_gap_rawtail_over_gap_hkz"] = (
                row["rawtail"]["abs_gap_median"] / row["hkz"]["abs_gap_median"])
        shared[cell] = row
    OUT["GUARD_VS_CANDIDATES_AT_THE_SAME_CELLS"] = shared

    # ------------------------------------- internal consistency of the report
    # Recompute the producer's own aggregate from its own per-basis entries.
    consistency = OrderedDict()
    for c in CANDS:
        worst = 0.0
        for pair, betas in R["G_REL2"][c].items():
            for beta, ent in betas.items():
                if "per_basis" not in ent or "maxfloor" not in ent:
                    continue
                mine = float(np.mean([e["value_maxfloor"]
                                      for e in ent["per_basis"]]))
                worst = max(worst, abs(mine - ent["maxfloor"]["mean"]))
        consistency[c] = {"max_abs_deviation_recomputed_mean_vs_reported": worst}
    OUT["internal_consistency_of_the_committed_results"] = consistency

    guard = summary.get("rawtail", {})
    hk = summary.get("hkz", {})
    OUT["HEADLINE"] = {
        "Q1_regime": {
            "rawtail_fraction_of_entries_in_the_PINNED_regime":
                guard.get("fraction_pinned"),
            "hkz_fraction_of_entries_in_the_PINNED_regime":
                hk.get("fraction_pinned"),
            "lam1n_fraction_of_entries_in_the_PINNED_regime":
                summary.get("lam1n", {}).get("fraction_pinned"),
            "reading": (
                "If the guard's fraction is 0 and the candidates' fraction is "
                "1, the MUST-PASS guard is scored under a relative test and "
                "every reduction-dependent candidate is scored under an "
                "absolute 0.10 test. The guard then does not exercise the "
                "criterion in the regime that decides the candidates."),
        },
        "Q2_margin": {
            "rawtail_median_mu": guard.get("median_mu_over_cells"),
            "hkz_median_mu": hk.get("median_mu_over_cells"),
            "lam1n_median_mu": summary.get("lam1n", {}).get("median_mu_over_cells"),
            "reading": (
                "mu < 1 means the entry passes with margin 1/mu; mu > 1 means "
                "it misses by that factor. The guard's pass at mu << 1 does "
                "not certify that the criterion can resolve an effect at the "
                "candidates' mu."),
        },
        "what_this_does_NOT_show": (
            "It does not show that hkz or lam1n has block-attribution content. "
            "The producer's paired t and detection floors, which this probe "
            "does not touch, already report every hkz mirrored gap as below "
            "its own paired-test detection floor at 9 of 9 cells. A criterion "
            "being blind at a scale and the quantity being zero at that scale "
            "are different statements and this probe distinguishes neither."),
    }

    with open(args.out, "w") as fh:
        json.dump(OUT, fh, indent=1)

    print("=" * 78)
    print("PROBE M -- is X_mp = rawtail a fair MUST-PASS guard?")
    print("RED-TEAM PROBE, NOT PRE-REGISTERED, RESCORES NOTHING. TOY.")
    print("source: %s (%s)" % (args.results, src))
    print("=" * 78)
    print("\n%-9s %6s %-18s %10s %10s %10s %8s" % (
        "cand", "cells", "pinned-regime", "mu_med", "mu_min", "mu_max",
        "pass"))
    for c, v in summary.items():
        print("%-9s %6d %-18s %10.4g %10.4g %10.4g %4d/%-3d" % (
            c, v["n_cells"], v["entries_in_the_PINNED_regime_of_total"],
            v["median_mu_over_cells"] or float("nan"),
            v["min_mu_over_cells"] or float("nan"),
            v["max_mu_over_cells"] or float("nan"),
            v["n_cells_passing_at_mean_over_8"], v["n_cells"]))
    print("\nSame-cell comparison, guard vs candidates (median over 8 bases):")
    print("%-16s %10s %10s %10s %12s" % (
        "cell", "mu rawtail", "mu hkz", "mu lam1n", "gap ratio"))
    for cell, row in shared.items():
        print("%-16s %10.4g %10.4g %10s %12.4g" % (
            cell,
            row.get("rawtail", {}).get("mu_median", float("nan")),
            row.get("hkz", {}).get("mu_median", float("nan")),
            ("%.4g" % row["lam1n"]["mu_median"]) if "lam1n" in row else "-",
            row.get("ratio_gap_rawtail_over_gap_hkz", float("nan"))))
    print("\ninternal consistency (recomputed mean vs reported mean):")
    for c, v in consistency.items():
        print("   %-9s max abs dev %.3e"
              % (c, v["max_abs_deviation_recomputed_mean_vs_reported"]))
    print("\nwrote %s" % args.out)


if __name__ == "__main__":
    main()
