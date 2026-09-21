#!/usr/bin/env python3
"""EXP-QSP-33b442 RUN 4 -- Stage 3: the n = 131 census with root-list
certificates.

K = F_2[z]/(z^131 + z^13 + z^2 + z + 1) (the ECC2K-130 field polynomial; no
curve, no point, no group is constructed anywhere).  n' in {33, 44, 66}.
Candidates: every NON-LINEARIZED lambda in F_2[X] of exact degree 3..7 (248
minus the 4 linearized degree-4 ones = 244 per cell, 732 in total); affine
lambda are included and marked.  Instrument: I3 only, with the per-orbit
closing test.  Every candidate with N > 0 emits an explicit root list grouped
into Frobenius orbits, which the run wrapper then re-verifies INDEPENDENTLY by
evaluating x^{2^{n'}} - lambda(x) in K.

Usage:  python3 stage3.py RUN-QSP-33b442-S3
"""
from __future__ import annotations

import json
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qspcore import (KField, FIELD_POLY, field_poly_str, deg, poly_str, polys_of_degree,
                     is_linearized, is_affine, i3_injection_f2, difference_poly_f2,
                     verify_roots_f2)
import runlib

NPRS = [33, 44, 66]
N = 131


def candidates() -> list[int]:
    return [lam for d in range(3, 8) for lam in polys_of_degree(d) if not is_linearized(lam)]


def main(run_id: str) -> int:
    rng = random.Random(0xC0FFEE)
    cand = candidates()
    excluded = [lam for d in range(3, 8) for lam in polys_of_degree(d) if is_linearized(lam)]
    inputs = {
        "stage": "stage_3 (the n = 131 census with root-list certificates)",
        "field": field_poly_str(N),
        "field_polynomial_bits": hex(FIELD_POLY[N]),
        "field_note": "the ECC2K-130 field polynomial of RQ-QSP-f9bbdb. NO CURVE, "
                      "NO POINT, NO GROUP is constructed by this experiment.",
        "cells": [{"n": N, "n_prime": npr, "q": N // npr, "r": N % npr,
                   "bound_form": "max(d^%d, 2)" % (N // npr + 1)} for npr in NPRS],
        "candidate_set": "every NON-LINEARIZED lambda in F_2[X] of exact degree 3..7: "
                         "248 of exact degree 3..7 minus the %d linearized ones = %d "
                         "per cell, %d in total; exhaustive and seed-free"
                         % (len(excluded), len(cand), len(cand) * len(NPRS)),
        "excluded_linearized": [poly_str(l) for l in excluded],
        "excluded_linearized_note": "linearized lambda are EXCLUDED from the census "
                                    "per specification stage_3.candidates and are "
                                    "decided by control C6 (Proposition 2 of "
                                    "KN-LIT-4fe9d2) in the Stage 1 and Stage 2 runs",
        "instrument": "I3 only (I1 and I2 are infeasible at deg L = 2^{n'}): the "
                      "injection count with the PER-ORBIT closing test",
        "certificate": "per candidate with N > 0, an explicit root list as "
                       "coefficient vectors over F_2[z]/(z^131 + z^13 + z^2 + z + 1), "
                       "grouped into Frobenius orbits, re-verified by the wrapper",
        "seeds": {"base_seed": runlib.BASE_SEED, "stage_3_is_seed_free": True,
                  "note": "exhaustive candidate set; the only random.Random "
                          "(seed 0xC0FFEE) drives equal-degree splitting, whose "
                          "factor set is unique"},
    }
    run = runlib.Run(run_id, "stage_3",
                     "python3 experiments/EXP-QSP-33b442/implementation/stage3.py " + run_id,
                     inputs, certificate_kind="root_list")
    raw: dict = {"stage": "stage_3", "specification_version": 1}
    K = KField(N)
    cells_out = {}
    violations = []
    cert_failures = []
    n_certs = 0
    run.log("== Stage 3: n = %d over %s, %d candidates per cell"
            % (N, field_poly_str(N), len(cand)))
    for npr in NPRS:
        q, r = divmod(N, npr)
        rows = []
        hist: dict[int, int] = {}
        best = (-1.0, None)
        slack_max = 0
        slack_sum = 0
        orbit_carrying = 0
        degen = 0
        for lam in cand:
            d = deg(lam)
            bound = max(d ** (q + 1), 1 << (npr - r))
            res = i3_injection_f2(K, lam, npr, rng, want_roots=True)
            if res["degenerate"]:
                degen += 1
                rows.append({"lambda_bits": lam, "lambda_printed": poly_str(lam),
                             "n": N, "n_prime": npr, "d": d, "q": q, "r": r,
                             "degenerate_D_zero": True, "N": None, "bound": bound,
                             "note": "D = 0; excluded from the M1 ratio"})
                continue
            Nv = res["N"]
            orbits = res["root_orbits"]
            roots = [x for orb in orbits for x in orb]
            assert len(roots) == Nv, (len(roots), Nv)
            row = {
                "lambda_bits": lam, "lambda_hex": hex(lam), "lambda_printed": poly_str(lam),
                "n": N, "n_prime": npr, "d": d, "q": q, "r": r,
                "field_polynomial": field_poly_str(N),
                "instruments_run": ["I3"],
                "I1": None, "I1_skip_reason": "2^131 elements: infeasible",
                "I2": None, "I2_skip_reason": "deg L = 2^%d: infeasible" % npr,
                "I3": Nv, "N": Nv, "bound": bound, "ratio": Nv / bound,
                "deg_D": res["deg_D"], "D_roots_in_K": res["D_roots_in_K"],
                "slack": res["slack"],
                "orbit_sizes": sorted(len(o) for o in orbits),
                "n_orbits": len(orbits),
                "orbit_carrying_size_n": any(len(o) == N for o in orbits),
                "degenerate_D_zero": False,
                "linearized": False, "affine": is_affine(lam),
                "square_lambda_prime_zero": all(((lam >> i) & 1) == 0
                                                for i in range(1, d + 1, 2)),
                "certificate_path": None,
            }
            if Nv > 0:
                ver = verify_roots_f2(K, lam, npr, roots)
                cert = {
                    "experiment_id": "EXP-QSP-33b442", "run_id": run_id,
                    "stage": "stage_3", "n": N, "n_prime": npr, "q": q, "r": r,
                    "field_polynomial": field_poly_str(N),
                    "field_polynomial_bits": hex(FIELD_POLY[N]),
                    "lambda_printed": poly_str(lam), "lambda_bits": lam, "d": d,
                    "L": "X^{2^%d} + (%s)" % (npr, poly_str(lam)),
                    "N_distinct_K_roots": Nv,
                    "bound_max_d_qplus1_2_nprime_minus_r": bound,
                    "ratio": Nv / bound,
                    "D_roots_in_K": res["D_roots_in_K"],
                    "slack_D_roots_discarded_by_closing_test": res["slack"],
                    "frobenius_orbits": [
                        {"size": len(o),
                         "roots": [{"coefficient_vector_over_F2": K.to_vector(x),
                                    "printed": K.elt_str(x), "hex": hex(x)} for x in o]}
                        for o in orbits],
                    "independent_reverification": ver | {
                        "method": "the wrapper evaluates x^{2^{n'}} and lambda(x) in K "
                                  "directly (qspcore.verify_roots_f2) and asserts "
                                  "x^{2^{n'}} - lambda(x) = 0, and asserts the listed "
                                  "roots are pairwise distinct. It shares no code path "
                                  "with the injection count that produced the list."},
                }
                name = "np%d_lam%s.json" % (npr, hex(lam))
                path = run.path("certificates", name)
                with open(path, "w") as fh:
                    json.dump(cert, fh, indent=1, sort_keys=False)
                row["certificate_path"] = "certificates/" + name
                row["root_verification"] = ver
                n_certs += 1
                if not ver["all_roots_verified"]:
                    cert_failures.append(row)
            if Nv > bound:
                violations.append(row)
            hist[Nv] = hist.get(Nv, 0) + 1
            slack_max = max(slack_max, res["slack"])
            slack_sum += res["slack"]
            if row["orbit_carrying_size_n"]:
                orbit_carrying += 1
            if Nv / bound > best[0]:
                best = (Nv / bound, row)
            rows.append(row)
        nd = len(rows) - degen
        lam_p = nd / N
        tail = 1.0 - sum(math.exp(-lam_p) * lam_p ** k / math.factorial(k)
                         for k in range(orbit_carrying))
        label = "n131_np%d" % npr
        cells_out[label] = {
            "n": N, "n_prime": npr, "q": q, "r": r,
            "field_polynomial": field_poly_str(N),
            "candidates": len(rows), "degenerate_candidates": degen,
            "M1_max_ratio": best[0],
            "M1_attaining_lambda": best[1]["lambda_printed"] if best[1] else None,
            "max_N": max((r_["N"] for r_ in rows if r_["N"] is not None), default=None),
            "N_histogram": dict(sorted(hist.items())),
            "candidates_with_N_gt_0": sum(1 for r_ in rows if r_["N"]),
            "orbit_carrying_candidates": orbit_carrying,
            "orbit_carrying_lambdas": [r_["lambda_printed"] for r_ in rows
                                       if r_.get("orbit_carrying_size_n")],
            "M8_slack_max": slack_max, "M8_slack_mean": slack_sum / nd if nd else None,
            "M9_orbit_tail": {
                "observed_orbit_carrying": orbit_carrying,
                "poisson_mean_under_H2": lam_p,
                "upper_tail_probability_P_at_least_observed": tail,
                "refutes_H2_at_0_01": tail < 0.01,
                "model_note": "H2's Poisson(C/n) reference is MODELED, not measured. "
                              "It bears on the null model only, never on the bound.",
            },
            "certificates": sum(1 for r_ in rows if r_.get("certificate_path")),
            "rows": rows,
        }
        with open(run.path("cells", label + ".json"), "w") as fh:
            json.dump(cells_out[label], fh, indent=1, sort_keys=False)
        run.log("   n' = %2d (q=%d, r=%2d): %d candidates, max N = %d, M1 = %.6f at %s, "
                "hist %s, orbit-carrying = %d (Poisson mean %.3f, upper tail %.4f), "
                "slack max = %d, certificates = %d"
                % (npr, q, r, len(rows), cells_out[label]["max_N"], best[0],
                   best[1]["lambda_printed"], cells_out[label]["N_histogram"],
                   orbit_carrying, lam_p, tail, slack_max, cells_out[label]["certificates"]))
    raw["stage_3_cells"] = cells_out
    raw["per_cell_json_files"] = ["cells/%s.json" % k for k in cells_out]
    raw["certificates_written"] = n_certs
    raw["certificate_reverification_failures"] = cert_failures
    raw["violations_of_the_bound"] = violations
    raw["tail_checks"] = {
        "largest_N_at_n_131": max(v["max_N"] for v in cells_out.values()),
        "largest_N_row": max((r_ for v in cells_out.values() for r_ in v["rows"]
                              if r_["N"] is not None), key=lambda r_: r_["N"]),
        "largest_ratio_at_n_131": max(v["M1_max_ratio"] for v in cells_out.values()),
        "orbit_tail": {k: v["M9_orbit_tail"] for k, v in cells_out.items()},
        "slack": {k: {"max": v["M8_slack_max"], "mean": v["M8_slack_mean"]}
                  for k, v in cells_out.items()},
    }
    if cert_failures or violations:
        reason = ("%d root lists failed independent re-verification" % len(cert_failures)) \
            if cert_failures else "%d candidates above the bound (F1)" % len(violations)
        run.warn("STOP:", reason)
        run.finish(raw, "invalid_measurement" if cert_failures else "completed_valid", reason,
                   certificate={"kind": "root_list", "verified": not cert_failures,
                                "verifier": "qspcore.verify_roots_f2"},
                   anomalies=[{"branch": "F1" if violations else "invalid_measurement",
                               "detail": reason}])
        return 1
    run.log("\n== Summary: %d candidates over 3 cells; %d certificates written, all "
            "independently re-verified; 0 candidates above the bound"
            % (len(cand) * len(NPRS), n_certs))
    run.finish(raw, "completed_valid",
               "732 exact counts at n = 131; every candidate with N > 0 carries an "
               "explicit Frobenius-orbit root list that the wrapper re-verified "
               "independently; no candidate exceeded max(d^{q+1}, 2^{n'-r})",
               certificate={"kind": "root_list", "verified": True,
                            "verifier": "qspcore.verify_roots_f2 (evaluates "
                                        "x^{2^{n'}} - lambda(x) in K directly)",
                            "certified_candidates": n_certs})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
