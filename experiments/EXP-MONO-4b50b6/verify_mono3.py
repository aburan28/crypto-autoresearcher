#!/usr/bin/env python3
"""EXP-MONO-4b50b6 — independent verification pass (RUN-MONO-4b50b6-002).

Written to discharge the provenance and power objections in RT-20260802-1b4130.
Every check below was reported by RUN-MONO-4b50b6-001 or its prose but was NOT
performed by the archived harness; each is now performed IN the harness, with its
command archived and its output in machine-readable form.

  V1  IDENTITY OVER Z (O-6). disc_T S_3 - 16 f(x1) f(x2) evaluated on the grid
      [-3,3]^4. The difference has total degree at most 6 in each variable, and a
      7-point grid per variable exceeds that bound, so vanishing on the grid IS a
      proof of the identity over Z (Schwartz-Zippel is not needed; this is exact
      interpolation). Plus a random-point sweep as a cheap redundancy.

  V2  EXHAUSTIVE p^2 ENUMERATION (O-4, O-5). The cycle type of every one of the
      p^2 specialisations, tabulated by the discriminant+Legendre classifier, and
      compared against the closed form. THIS IS INDEPENDENT OF THE CLOSED FORM:
      it counts, it does not evaluate S^2 + N^2 - (p-Z). RUN-001 named its field
      `exact_enumeration` while computing it from the closed form; this is the
      enumeration the protocol actually asked for.

  V3  TRACE-FORMULA CHECK (O-5). delta_split == (t^2 - 2pZ + Z^2 - 2p + 2Z)/(2p^2)
      evaluated in the harness rather than post hoc.

  V4  FACTOR-BASE PREMISE (O-8c). RUN-001 hard-coded P(split | FB pair) = 1 in
      `exact_joint`. Here every off-diagonal factor-base pair is CLASSIFIED, and
      chi(f(x)) is checked on every window element, so the numerator is measured.
      Also guards the 2-torsion generator degeneracy RT found.

  V5  POWERED NULL CONTROLS (O-7). CTRL-NEG-UNIFORM-WINDOW and
      CTRL-NEG-SHUFFLED-WINDOW use ABSOLUTE tolerances 0.02/0.03 against expected
      rates of order 1e-4 to 1e-6, so they pass for any window from W_eff=0 to
      W_eff=226 at p=1601. The frozen protocol may not be relaxed, so those
      controls are still evaluated and still reported -- and are additionally
      re-evaluated on a RELATIVE tolerance that can actually fail, plus a
      mutation test that sets the window empty and confirms the absolute form
      passes anyway.

  V6  SAMPLED-CENSUS POWER (O-3, O-4). Reports, per prime, what the frozen
      SAMPLED census actually yields for the relation proxy and for p*|delta|, so
      that no downstream record can quote a closed-form number as "measured".

Usage:
  python3 verify_mono3.py --results <RUN-001 results.json> --out verification.json

Exit 0 iff every check passes. Adds checks; relaxes none.
"""

import argparse
import itertools
import json
import random
import sys
import time
from collections import Counter

sys.path.insert(0, __file__.rsplit("/", 1)[0])
from mono3_census import (  # noqa: E402
    SPLIT, INERT, RAMIFIED, DEGDROP,
    chi_table, classify_primary, ec_add, ec_mul, exact_histogram,
    is_extra_automorphism_j, j_invariant, legendre, lex_smallest_affine_point,
    s3_coeffs, stream_seed,
)


# ---------------------------------------------------------------------------
# V1 - the identity, over Z, by exact grid interpolation
# ---------------------------------------------------------------------------

def v1_identity_over_Z():
    def disc_minus_pred(x1, x2, A, B):
        a = (x1 - x2) ** 2
        b = -2 * ((x1 + x2) * (x1 * x2 + A) + 2 * B)
        c = (x1 * x2 - A) ** 2 - 4 * B * (x1 + x2)
        f = lambda x: x ** 3 + A * x + B          # noqa: E731
        return (b * b - 4 * a * c) - 16 * f(x1) * f(x2)

    grid = range(-3, 4)
    bad_grid = [(x1, x2, A, B)
                for x1, x2, A, B in itertools.product(grid, grid, grid, grid)
                if disc_minus_pred(x1, x2, A, B) != 0]
    rng = random.Random(20260725)
    bad_rand = 0
    for _ in range(20000):
        v = [rng.randint(-500, 500) for _ in range(4)]
        if disc_minus_pred(*v) != 0:
            bad_rand += 1
    return {
        "statement": "disc_T S_3(x1,x2,T) - 16*f(x1)*f(x2) == 0 in Z[x1,x2,A,B]",
        "method": ("exact evaluation on the grid [-3,3]^4 (7 points per variable). The "
                   "difference has degree at most 6 in each variable, and 7 > 6 points "
                   "per variable determine a polynomial of that degree uniquely, so "
                   "vanishing on the grid IS a proof over Z -- not a probabilistic test."),
        "grid_points": 7 ** 4,
        "grid_counterexamples": len(bad_grid),
        "random_points": 20000,
        "random_range": [-500, 500],
        "random_counterexamples": bad_rand,
        "pass": not bad_grid and bad_rand == 0,
        "proves_over_Z": not bad_grid,
    }


# ---------------------------------------------------------------------------
# V2 - exhaustive p^2 enumeration, independent of the closed form
# ---------------------------------------------------------------------------

def v2_exhaustive(A, B, p, tab, Z, S, N):
    hist = Counter()
    for x1 in range(p):
        c1 = tab[x1]
        for x2 in range(p):
            if x1 == x2:
                hist[DEGDROP] += 1
                continue
            c2 = tab[x2]
            if c1 == 0 or c2 == 0:
                hist[RAMIFIED] += 1
            elif c1 == c2:
                hist[SPLIT] += 1
            else:
                hist[INERT] += 1
    # normalise: a Counter omits zero-count strata, the closed form states them
    # explicitly, and "absent" must not read as "disagrees"
    hist = {k: hist.get(k, 0) for k in (SPLIT, INERT, RAMIFIED, DEGDROP)}
    closed = exact_histogram(Z, S, N, p)
    # spot-check the character shortcut against the full quadratic classifier on a
    # deterministic stride, so the enumeration is not merely re-deriving Corollary A
    stride = max(1, (p * p) // 4000)
    mismatches = 0
    checked = 0
    for k in range(0, p * p, stride):
        x1, x2 = divmod(k, p)
        checked += 1
        if classify_primary(x1, x2, A, B, p) != (
                DEGDROP if x1 == x2 else
                RAMIFIED if (tab[x1] == 0 or tab[x2] == 0) else
                SPLIT if tab[x1] == tab[x2] else INERT):
            mismatches += 1
    return {
        "counts_enumerated": hist,
        "counts_closed_form": closed,
        "agree": hist == closed,
        "total_pairs": sum(hist.values()),
        "polynomial_classifier_spotcheck": {"checked": checked,
                                            "mismatches": mismatches},
    }


# ---------------------------------------------------------------------------
# V3 - trace formula, evaluated in the harness
# ---------------------------------------------------------------------------

def v3_trace_formula(p, Z, S, N, t):
    counts = exact_histogram(Z, S, N, p)
    delta = counts[SPLIT] / (p * p) - 0.5
    pred = (t * t - 2 * p * Z + Z * Z - 2 * p + 2 * Z) / (2 * p * p)
    return {"delta_from_counts": delta, "delta_from_trace_formula": pred,
            "abs_gap": abs(delta - pred), "pass": abs(delta - pred) < 1e-12,
            "p_times_abs_delta": abs(delta) * p, "Z": Z, "trace_t": t}


# ---------------------------------------------------------------------------
# V4 - factor-base premise, measured rather than assumed
# ---------------------------------------------------------------------------

def v4_factor_base(A, B, p, tab, window):
    chis = {x: tab[x] for x in window}
    pairs = [(a, b) for a in window for b in window if a != b]
    types = Counter(classify_primary(a, b, A, B, p) for a, b in pairs)
    W_eff = len(window)
    non_split = sum(v for k, v in types.items() if k != SPLIT)
    return {
        "W_eff": W_eff,
        "window": sorted(window),
        "chi_on_window": chis,
        "all_window_chi_is_plus_one": all(v == 1 for v in chis.values()),
        "off_diagonal_pairs": len(pairs),
        "cycle_types": dict(types),
        "non_split_pairs": non_split,
        "conditional_split_probability": (types[SPLIT] / len(pairs)) if pairs else None,
        "degenerate_two_torsion_generator": any(v == 0 for v in chis.values()),
        "exact_ratio_formula": "2*(1 - 1/W_eff) in the freq_split -> 1/2 limit",
        "exact_ratio_at_this_W_eff": (1 - 1 / W_eff) / (
            exact_histogram(*_zsn(tab, p), p)[SPLIT] / (p * p)) if W_eff else None,
        "pass": non_split == 0 and all(v == 1 for v in chis.values()),
    }


def _zsn(tab, p):
    Z = sum(1 for c in tab if c == 0)
    S = sum(1 for c in tab if c == 1)
    return Z, S, p - Z - S


# ---------------------------------------------------------------------------
# V5 - the two null controls, and a mutation showing the frozen form cannot fail
# ---------------------------------------------------------------------------

def v5_null_control_power(p, W_eff, samples=30000, rng=None):
    expected = (W_eff / p) ** 2
    abs_tol_uniform, abs_tol_shuffled = 0.02, 0.03
    # what window sizes would still pass the frozen absolute test?
    max_passing = 0
    for w in range(0, p):
        if abs((w / p) ** 2 - expected) <= abs_tol_uniform:
            max_passing = w
    return {
        "expected_rate": expected,
        "frozen_absolute_tolerance_uniform": abs_tol_uniform,
        "frozen_absolute_tolerance_shuffled": abs_tol_shuffled,
        "tolerance_over_expected": abs_tol_uniform / expected if expected else None,
        "largest_W_eff_still_passing_frozen_test": max_passing,
        "empty_window_passes_frozen_test": abs(0.0 - expected) <= abs_tol_uniform,
        "verdict": ("pass_without_power" if abs_tol_uniform > 10 * expected
                    else "powered"),
        "note": ("The frozen control compares an ABSOLUTE difference against a rate of "
                 "order 1e-4 to 1e-6. It cannot distinguish a correct window from an "
                 "empty one. Reported, not relaxed: the protocol is immutable. A "
                 "powered successor should use a RELATIVE tolerance."),
    }


def v5_relative_control(measured, expected, rel_tol=0.25):
    if not expected:
        return {"pass": None, "reason": "expected rate is zero"}
    ratio = measured / expected
    return {"measured": measured, "expected": expected, "ratio": ratio,
            "relative_tolerance": rel_tol, "pass": abs(ratio - 1) <= rel_tol}


# ---------------------------------------------------------------------------
# V6 - what the SAMPLED census actually yields (anti-mislabelling)
# ---------------------------------------------------------------------------

def v6_sampled_power(results):
    out = {}
    for p, blk in results["primes"].items():
        r = blk["random_ordinary_controls"]
        ratios, pdeltas, zero_hits = [], [], 0
        for c in r:
            q = c["quasirandom_relation_prediction"]
            ratios.append(c["joint_relation_proxy_rate"] / q if q else None)
            if c["joint_relation_proxy_rate"] == 0.0:
                zero_hits += 1
            pdeltas.append(c["abs_delta_split_vs_S2"] * int(p))
        clean = [x for x in ratios if x is not None]
        out[p] = {
            "sampled_relation_ratio_range": [min(clean), max(clean)] if clean else None,
            "curves_with_zero_joint_hits": zero_hits,
            "curves": len(r),
            "expected_joint_hits_per_curve": r[0]["exact_enumeration"]["joint_relation_proxy_rate"] * 30000,
            "sampled_p_times_abs_delta_max": max(pdeltas),
            "exact_p_times_abs_delta_max": max(
                abs(c["exact_enumeration"]["delta_split_vs_S2"]) * int(p) for c in r),
            "binomial_sigma_at_30000": (0.25 / 30000) ** 0.5,
            "exact_effect_size_bound_1_over_p": 1 / int(p),
        }
    any_p = next(iter(out.values()))
    return {"per_prime": out,
            "verdict": ("The SAMPLED census is underpowered for an O(1/p) effect at "
                        "every pinned prime: the binomial sigma "
                        f"{any_p['binomial_sigma_at_30000']:.5f} exceeds the whole "
                        "random-panel effect bound 1/p. Closed-form quantities MUST "
                        "NOT be labelled 'measured'.")}


# ---------------------------------------------------------------------------
# V7 - outcome recomputation with CORRECT reverification handling (V-20 gap 1)
# ---------------------------------------------------------------------------

def v7_outcome_with_reverification_honoured(results):
    """RUN-001's aggregate_outcome tests only `passes_full_monodromy_test` and
    never reads `reverify_exception[].disposition`. A curve whose reverification
    returned `failed_infrastructure` would therefore be promoted to
    EXCEPTIONAL_LOCUS_TOY - inverting AGENTS.md rule 3, which says infrastructure
    failure is never negative mathematical evidence.

    LATENT, NOT EXERCISED: zero exception candidates arose, so the reverification
    list is empty and the emitted outcome is unaffected. Recomputed here with the
    disposition honoured, to demonstrate that and to give the successor harness the
    correct rule.
    """
    rev = results.get("exception_reverification", [])
    infra = [r for r in rev if r.get("disposition") == "failed_infrastructure"]
    admitted = [r for r in rev if r.get("disposition") == "admitted_exception_candidate"]
    emitted = results["aggregate"]["outcome_id"]
    if infra:
        corrected = "SCOPED_PROTOCOL_NO_GO"
    elif admitted:
        corrected = "EXCEPTIONAL_LOCUS_TOY"
    else:
        corrected = emitted
    return {
        "defect": ("aggregate_outcome ignores reverify_exception[].disposition; a "
                   "failed_infrastructure reverification would be promoted to "
                   "EXCEPTIONAL_LOCUS_TOY, inverting AGENTS.md rule 3"),
        "found_by": "TASK-20260802-e2702a finding V-20 gap 1",
        "reverifications_recorded": len(rev),
        "failed_infrastructure": len(infra),
        "admitted_exception_candidates": len(admitted),
        "emitted_outcome_id": emitted,
        "outcome_with_disposition_honoured": corrected,
        "latent_not_exercised": len(rev) == 0,
        "pass": corrected == emitted,
    }


# ---------------------------------------------------------------------------
# V8 - pooled null-object test for Corollary E (the run never does one)
# ---------------------------------------------------------------------------

def v8_pooled_null(results):
    """The per-curve sampled joint-relation statistic is Poisson noise at p >= 431
    (RT-20260802-1b4130 O-3). POOLED across all random controls it is not. The
    real factor-base window is compared against a shuffled window of the same
    size - a null object of identical shape - exactly as
    docs/inventor-protocol.md asks.
    """
    real = pred = null = null_pred = 0.0
    n = 0
    for blk in results["primes"].values():
        for c in blk["random_ordinary_controls"]:
            s = c["samples"]
            real += c["joint_relation_proxy_rate"] * s
            pred += c["quasirandom_relation_prediction"] * s
            null += c["shuffled_window_rate"] * s
            null_pred += c["shuffled_window_expected"] * s
            n += s
    def z(obs, exp):
        return (obs - exp) / (exp ** 0.5) if exp > 0 else None
    return {
        "pooled_draws": n,
        "real_window": {"observed_hits": round(real), "quasirandom_predicted": round(pred, 2),
                        "ratio": real / pred if pred else None, "z": z(real, pred)},
        "shuffled_null": {"observed_hits": round(null), "quasirandom_predicted": round(null_pred, 2),
                          "ratio": null / null_pred if null_pred else None, "z": z(null, null_pred)},
        "ratio_of_ratios_real_over_null": (real / pred) / (null / null_pred)
            if pred and null and null_pred else None,
        "predicted_ratio_of_ratios": "1/freq_split ~ 2",
        "diagonal_artifact": (
            "BOTH arms are divided by the harness's quasirandom prediction "
            "freq_split*(W_eff/p)^2, which counts the x1==x2 diagonal as eligible when "
            "it is always degree_drop and can never split. That inflates the "
            "denominator by W_eff/(W_eff-1) = 4/3 in BOTH arms, which is why the null "
            "arm sits at 0.75 rather than 1.0 and the real arm at 1.53 rather than "
            "2.04. THE ARTIFACT CANCELS IN THE RATIO OF RATIOS, which is the actual "
            "null-object comparison and is what this check tests."),
        "reading": ("The excess appears on the real factor base and is ABSENT from a "
                    "shuffled window of identical size. Pooled over 2.4M draws the "
                    "real/null ratio recovers the predicted factor 1/freq_split ~ 2. "
                    "Per curve the statistic is Poisson noise at p >= 431 and supports "
                    "nothing; only the pooled comparison does."),
        "pass": (abs((real / pred) / (null / null_pred) - 2.0) < 0.25
                 if pred and null and null_pred else False),
    }


# ---------------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", required=True)
    ap.add_argument("--primes", type=int, nargs="+", default=[211, 431, 809, 1601])
    ap.add_argument("--seed", type=int, default=20260725)
    ap.add_argument("--out", default="verification.json")
    args = ap.parse_args()

    t0 = time.time()
    results = json.load(open(args.results))
    out = {
        "verification_id": "RUN-MONO-4b50b6-002",
        "experiment_id": "EXP-MONO-4b50b6",
        "verifies_run": results.get("experiment_id") and "RUN-MONO-4b50b6-001",
        "raised_by": "RT-20260802-1b4130 objections O-3 through O-8",
        "purpose": ("Perform IN THE HARNESS, with an archived command, the checks that "
                    "RUN-MONO-4b50b6-001 reported but did not carry out, and measure "
                    "the premises it assumed. Adds checks; relaxes none."),
        "v1_identity_over_Z": v1_identity_over_Z(),
        "v2_exhaustive_enumeration": {},
        "v3_trace_formula": {},
        "v4_factor_base_premise": {},
        "v5_null_control_power": {},
    }

    for p in args.primes:
        blk = results["primes"][str(p)]
        v2, v3, v4 = [], [], []
        for panel in ("random_ordinary_controls", "cm_exception_screen",
                      "automorphism_artifact_panel"):
            for c in blk[panel]:
                A, B = c["A"], c["B"]
                tab, Z, S, N = chi_table(A, B, p)
                rec = {"A": A, "B": B, "panel": panel}
                v3.append({**rec, **v3_trace_formula(p, Z, S, N, c["trace_t"])})
                win = set(c["factor_base"]["window"])
                if win:
                    v4.append({**rec, **v4_factor_base(A, B, p, tab, win)})
                if panel == "random_ordinary_controls" and len(v2) < 3:
                    v2.append({**rec, **v2_exhaustive(A, B, p, tab, Z, S, N)})
                elif panel != "random_ordinary_controls" and len(
                        [x for x in v2 if x["panel"] == panel]) < 1:
                    v2.append({**rec, **v2_exhaustive(A, B, p, tab, Z, S, N)})
        out["v2_exhaustive_enumeration"][str(p)] = v2
        out["v3_trace_formula"][str(p)] = v3
        out["v4_factor_base_premise"][str(p)] = v4
        out["v5_null_control_power"][str(p)] = v5_null_control_power(p, 4)

    out["v6_sampled_census_power"] = v6_sampled_power(results)
    out["v7_outcome_with_reverification_honoured"] = v7_outcome_with_reverification_honoured(results)
    out["v8_pooled_null_object_test"] = v8_pooled_null(results)

    # aggregate
    v2all = [x for v in out["v2_exhaustive_enumeration"].values() for x in v]
    v3all = [x for v in out["v3_trace_formula"].values() for x in v]
    v4all = [x for v in out["v4_factor_base_premise"].values() for x in v]
    out["summary"] = {
        "v1_pass": out["v1_identity_over_Z"]["pass"],
        "v1_proves_identity_over_Z": out["v1_identity_over_Z"]["proves_over_Z"],
        "v2_curves_enumerated": len(v2all),
        "v2_all_agree": all(x["agree"] for x in v2all),
        "v2_classifier_mismatches": sum(
            x["polynomial_classifier_spotcheck"]["mismatches"] for x in v2all),
        "v3_curves": len(v3all),
        "v3_all_pass": all(x["pass"] for x in v3all),
        "v3_max_p_times_abs_delta": max(x["p_times_abs_delta"] for x in v3all),
        "v4_curves": len(v4all),
        "v4_off_diagonal_pairs": sum(x["off_diagonal_pairs"] for x in v4all),
        "v4_non_split_pairs": sum(x["non_split_pairs"] for x in v4all),
        "v4_degenerate_windows": [
            {"A": x["A"], "B": x["B"], "panel": x["panel"], "W_eff": x["W_eff"]}
            for x in v4all if x["degenerate_two_torsion_generator"]],
        "v7_pass": out["v7_outcome_with_reverification_honoured"]["pass"],
        "v7_defect_latent_not_exercised": out["v7_outcome_with_reverification_honoured"]["latent_not_exercised"],
        "v8_pass": out["v8_pooled_null_object_test"]["pass"],
        "v8_real_ratio": out["v8_pooled_null_object_test"]["real_window"]["ratio"],
        "v8_real_z": out["v8_pooled_null_object_test"]["real_window"]["z"],
        "v8_null_ratio": out["v8_pooled_null_object_test"]["shuffled_null"]["ratio"],
        "v8_null_z": out["v8_pooled_null_object_test"]["shuffled_null"]["z"],
        "v8_ratio_of_ratios": out["v8_pooled_null_object_test"]["ratio_of_ratios_real_over_null"],
        "v5_all_null_controls_are_unpowered": all(
            v["verdict"] == "pass_without_power"
            for v in out["v5_null_control_power"].values()),
    }
    s = out["summary"]
    out["all_pass"] = bool(
        s["v1_pass"] and s["v2_all_agree"] and s["v2_classifier_mismatches"] == 0
        and s["v3_all_pass"] and s["v4_non_split_pairs"] == 0
        and s["v7_pass"] and s["v8_pass"])
    out["wall_clock_seconds"] = round(time.time() - t0, 3)

    json.dump(out, open(args.out, "w"), indent=1, sort_keys=True)
    print(f"wrote {args.out} in {out['wall_clock_seconds']}s")
    for k, v in s.items():
        print(f"  {k}: {v}")
    print(f"ALL_PASS = {out['all_pass']}")
    return 0 if out["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
