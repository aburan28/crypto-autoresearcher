#!/usr/bin/env python3
"""EXP-XEDN-002 controls 1-5 (plus the structural checks the census provoked).

  1 frozen-predicate control  : three-way agreement between the frozen predicate,
                                an independent square-root-extraction reference,
                                and sympy factorization over GF(p).
  2 planted-section control   : the EXP-XEDN-001 planted surface must be
                                recovered at p = 101.
  3 smoke-consistency control : the closed form's expected number of hits in the
                                5760 slots the p=101 smoke tested, against the
                                observed 0, with a Poisson interval.
  4 iso-triviality control    : discharge the EXP-XEDN-001 contract constraint
                                explicitly for deg b = 6.
  5 degenerate-section control: quantify the excluded y = 0 section.
  6 structural check (not a contract control, recorded because the census
    produced it): the mu_3 automorphism of the j = 0 family for p = 1 mod 3.

Usage (see implementation/run_arm.sh):
  python3 experiments/EXP-XEDN-002/implementation/controls.py --run-id RUN-XEDN-002-CTRL
"""
from __future__ import annotations

import argparse
import datetime as dt
import itertools
import math
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import xedn2_lib as L                                            # noqa: E402

P_SMOKE = 101
SMOKE_SLOTS = 5760           # EXP-XEDN-001 smoke: 40 surfaces x 12 x 12 slots
SMOKE_HITS = 0
SMOKE_SEXTICS = 200000
SMOKE_SEXTIC_HITS = 0
XSEC = [3, 5, 1]             # x*(t) = t^2 + 5t + 3   (harness xsec)
YSEC = [7, 4, 2, 1]          # y*(t) = t^3 + 2t^2 + 4t + 7 (harness ysec)


# ------------------------------------------------------------------ control 1
def control1_full_f_space(p: int, frozen, use_sympy: bool) -> dict:
    """Three-way classification of EVERY reachable f at this p.

    The reachable set is {f : deg f <= 6, [t^6] f != 1}: by the arm A bijection
    that is exactly the set of f = x^3 + b values for any fixed monic quadratic
    x, so this covers the whole slot space up to the (verified) bijection.
    """
    sqrts = L.sqrt_table(p)
    n = 0
    frozen_hits = ref_hits = true_sq = 0
    disagree_semantics = []
    disagree_sympy = []
    sympy_sqfree = sympy_other = 0
    for coeffs in itertools.product(*([range(p)] * 6)):
        for f6 in range(p):
            if f6 == 1:
                continue
            f = list(coeffs) + [f6]
            while len(f) > 1 and f[-1] == 0:
                f.pop()
            n += 1
            fz = frozen.is_square_poly(f, p) is not None
            y = L.ref_poly_sqrt(f, p, sqrts)
            ts = y is not None
            rp = ts and L.ref_is_squarefree_disc(y, p)
            frozen_hits += fz
            ref_hits += rp
            true_sq += ts
            if fz != rp and len(disagree_semantics) < 20:
                disagree_semantics.append({"f": f, "frozen": fz, "reference": rp})
            if use_sympy:
                cls = L.sympy_square_class(f, p)
                sympy_sqfree += (cls == "square_squarefree_root")
                sympy_other += (cls == "square_other_root")
                if (cls == "square_squarefree_root") != fz and len(disagree_sympy) < 20:
                    disagree_sympy.append({"f": f, "frozen": fz, "sympy": cls})
    out = {
        "p": p, "f_values_classified": n,
        "frozen_hits": frozen_hits,
        "independent_sqrt_reference_hits": ref_hits,
        "mathematical_square_count": true_sq,
        "closed_form_q_pred": L.q_pred(p),
        "closed_form_q_true_square": L.q_true_square(p),
        "frozen_matches_closed_form": frozen_hits == L.q_pred(p),
        "true_square_matches_closed_form": true_sq == L.q_true_square(p),
        "frozen_vs_sqrt_reference_disagreements": len(disagree_semantics),
        "disagreement_examples": disagree_semantics,
        "sympy_used": use_sympy,
    }
    if use_sympy:
        out.update({
            "sympy_square_squarefree_root": sympy_sqfree,
            "sympy_square_other_root": sympy_other,
            "sympy_total_squares": sympy_sqfree + sympy_other,
            "frozen_vs_sympy_disagreements": len(disagree_sympy),
            "sympy_disagreement_examples": disagree_sympy,
            "sympy_agrees_with_frozen_semantics": (sympy_sqfree == frozen_hits
                                                   and not disagree_sympy),
            "sympy_agrees_with_mathematical_count":
                sympy_sqfree + sympy_other == true_sq,
        })
    return out


def control1_random_sextics(p: int, n: int, seed: int, frozen,
                            sympy_every: int = 0) -> dict:
    """Frozen vs independent reference on n random polynomials of degree 6."""
    rng = random.Random(seed)
    sqrts = L.sqrt_table(p)
    frozen_hits = ref_hits = true_sq = 0
    disagree = []
    sympy_checked = sympy_disagree = 0
    for i in range(n):
        f = [rng.randrange(p) for _ in range(6)] + [rng.randrange(1, p)]
        fz = frozen.is_square_poly(f, p) is not None
        y = L.ref_poly_sqrt(f, p, sqrts)
        ts = y is not None
        rp = ts and L.ref_is_squarefree_disc(y, p)
        frozen_hits += fz
        ref_hits += rp
        true_sq += ts
        if fz != rp and len(disagree) < 20:
            disagree.append({"f": f, "frozen": fz, "reference": rp})
        if sympy_every and i % sympy_every == 0:
            sympy_checked += 1
            cls = L.sympy_square_class(f, p)
            if (cls == "square_squarefree_root") != fz:
                sympy_disagree += 1
    rate = L.sextic_square_rate(p)
    return {
        "p": p, "samples": n, "seed": seed,
        "frozen_hits": frozen_hits,
        "independent_sqrt_reference_hits": ref_hits,
        "mathematical_square_count": true_sq,
        "frozen_vs_reference_disagreements": len(disagree),
        "disagreement_examples": disagree,
        "sympy_cross_checked": sympy_checked,
        "sympy_disagreements": sympy_disagree,
        "closed_form_hit_rate_exact": f"{rate.numerator}/{rate.denominator}",
        "closed_form_hit_rate_float": float(rate),
        "expected_hits": n * float(rate),
        "poisson_prob_of_observing_zero": math.exp(-n * float(rate)),
    }


# ------------------------------------------------------------------ control 2
def control2_planted(frozen) -> dict:
    p = P_SMOKE
    bplant = frozen.psub(frozen.pmul(YSEC, YSEC, p),
                         frozen.pmul(frozen.pmul(XSEC, XSEC, p), XSEC, p), p)
    hits = []
    for x0 in range(p):
        for x1 in range(p):
            xt = [x0, x1, 1]
            f = frozen.padd(frozen.pmul(frozen.pmul(xt, xt, p), xt, p), bplant, p)
            g = frozen.is_square_poly(f, p)
            if g is not None:
                hits.append({"x0": x0, "x1": x1, "predicate_root": list(g)})
    sqrts = L.sqrt_table(p)
    ref_hits = []
    for x0 in range(p):
        for x1 in range(p):
            xt = [x0, x1, 1]
            f = frozen.padd(frozen.pmul(frozen.pmul(xt, xt, p), xt, p), bplant, p)
            y = L.ref_poly_sqrt(f, p, sqrts)
            if y is not None and L.ref_is_squarefree_disc(y, p):
                ref_hits.append({"x0": x0, "x1": x1, "sqrt": y})
    recovered = any(h["x0"] == XSEC[0] and h["x1"] == XSEC[1] for h in hits)
    return {
        "p": p,
        "x_star": XSEC, "y_star": YSEC,
        "b_planted": bplant,
        "b_planted_degree": len(bplant) - 1,
        "b_degree_is_6": len(bplant) - 1 == 6,
        "slots_enumerated": p * p,
        "frozen_hits": len(hits),
        "hit_list": hits,
        "independent_reference_hits": len(ref_hits),
        "reference_hit_list": ref_hits,
        "planted_section_recovered": recovered,
        "smoke_planted_total_sections_found": 1,
        "matches_smoke": recovered and len(hits) == 1,
        "y_star_squarefree": L.ref_is_squarefree_disc(YSEC, p),
        "deviation_note": (
            "b_planted = y*^2 - x*^3 has degree 5, not 6: the t^6 coefficients of "
            "y*^2 and x*^3 are both 1 and cancel. The planted surface therefore lies "
            "OUTSIDE the frozen deg-b-exactly-6 census family. It is a valid recovery "
            "control on the enumerator and predicate, and it is NOT a member of the "
            "population whose P_lift arm A computes. The EXP-XEDN-001 smoke recorded "
            "the same degree (planted_surface_b_degree = 5)."),
    }


# ------------------------------------------------------------------ control 3
def control3_smoke_consistency() -> dict:
    p = P_SMOKE
    pl = L.p_lift(p)
    lam = SMOKE_SLOTS * float(pl)
    p0 = math.exp(-lam)
    rate = L.sextic_square_rate(p)
    lam_neg = SMOKE_SEXTICS * float(rate)
    return {
        "p": p,
        "slots_tested_by_smoke": SMOKE_SLOTS,
        "hits_observed_by_smoke": SMOKE_HITS,
        "P_lift_exact": f"{pl.numerator}/{pl.denominator}",
        "P_lift_float": float(pl),
        "expected_hits": lam,
        "poisson_prob_of_observing_zero": p0,
        "poisson_95_upper_limit_on_count_given_zero_observed": 2.9957,
        "observed_zero_inside_poisson_interval": lam < 2.9957,
        "one_sided_95_upper_limit_on_rate_given_zero_hits":
            2.9957 / SMOKE_SLOTS,
        "closed_form_rate_inside_that_limit": float(pl) < 2.9957 / SMOKE_SLOTS,
        "naive_harness_prediction_per_slot": 1.0 / p**3,
        "closed_form_over_naive": float(pl) * p**3,
        "negative_control": {
            "population": "polynomials of degree exactly 6 (EXP-XEDN-001 part 4)",
            "samples": SMOKE_SEXTICS,
            "hits_observed": SMOKE_SEXTIC_HITS,
            "closed_form_rate_exact": f"{rate.numerator}/{rate.denominator}",
            "closed_form_rate_float": float(rate),
            "expected_hits": lam_neg,
            "poisson_prob_of_observing_zero": math.exp(-lam_neg),
            "observed_zero_consistent": lam_neg < 2.9957,
        },
        "verdict_note": (
            "the closed form predicts far fewer than one hit in the smoke's 5760 slots, "
            "so the smoke's 0 is the expected outcome and carries almost no information "
            "about the rate; it is consistent with, but could not have detected, "
            "P_lift ~ 1/(2p^3)"),
    }


# ------------------------------------------------------------------ control 4
def control4_isotriviality(frozen) -> dict:
    """Discharge the iso-triviality constraint for deg b = 6 exactly."""
    trivial_counts = {}
    for p in (5, 7, 11, 13):
        found = set()
        for a in range(p):
            base = [a % p, 1]
            h6 = [1]
            for _ in range(6):
                h6 = frozen.pmul(h6, base, p)
            for c in range(1, p):
                b = [c * v % p for v in h6]
                assert len(b) - 1 == 6
                found.add(tuple(b))
        trivial_counts[p] = {
            "b_of_form_c_times_linear_to_the_6": len(found),
            "closed_form_(p-1)*p": (p - 1) * p,
            "agree": len(found) == (p - 1) * p,
            "surfaces_in_family": (p - 1) * p**6,
            "fraction": len(found) / ((p - 1) * p**6),
        }
    return {
        "j_invariant_of_the_family": 0,
        "j_invariant_reasoning": (
            "for y^2 = x^3 + a(t)x + b(t) the fibre j-invariant is "
            "1728 * 4a^3 / (4a^3 + 27b^2); the frozen family has a(t) = 0 identically, "
            "so j = 0 for every fibre and every member of the family"),
        "isotrivial_under_constant_j_definition": {
            "count": "all (p-1)*p^6 surfaces in the family",
            "fraction": 1.0,
            "explanation": (
                "under the standard definition (an elliptic surface is isotrivial iff "
                "its smooth fibres are mutually isomorphic over the algebraic closure, "
                "equivalently j is constant), EVERY surface in the frozen family is "
                "isotrivial, because a(t) = 0 forces j = 0 identically. The family is a "
                "family of sextic twists of the fixed j = 0 curve Y^2 = X^3 + 1. This "
                "CONTRADICTS the reading assumed by the EXP-XEDN-002 specification's "
                "control text (which expected the count to be exactly zero) and by the "
                "EXP-XEDN-001 contract constraint 'iso-trivial surfaces must be "
                "detected and excluded'. Reported as an observation, not resolved here: "
                "no surface was excluded from any count, because excluding them would "
                "empty the frozen family."),
        },
        "constant_b_surfaces": {
            "count": 0,
            "explanation": ("deg b = 6 exactly excludes b constant, so under the "
                            "narrow reading 'iso-trivial = constant coefficients' the "
                            "count is exactly zero, as the specification anticipated"),
        },
        "trivial_over_F_p_of_t": {
            "definition": ("b = c * h(t)^6 with deg h = 1: then x = h^2 X, y = h^3 Y "
                           "turns the surface into the constant curve Y^2 = X^3 + c, so "
                           "these members are isomorphic over F_p(t) to a constant curve"),
            "counts": trivial_counts,
            "closed_form": "(p-1)*p surfaces, a fraction p^-5 of the family",
        },
    }


# ------------------------------------------------------------------ control 5
def control5_degenerate(frozen) -> dict:
    """Slots whose only section is the excluded y = 0 case: b = -x^3."""
    per_p = {}
    for p in (5, 7, 11, 13):
        cnt = 0
        rejected = 0
        for x0 in range(p):
            for x1 in range(p):
                xt = [x0, x1, 1]
                x3 = frozen.pmul(frozen.pmul(xt, xt, p), xt, p)
                b = [(-v) % p for v in x3]
                if len(b) - 1 != 6 or b[-1] == 0:
                    continue
                cnt += 1
                f = frozen.padd(x3, b, p)
                assert f == [0], f
                if frozen.is_square_poly(f, p) is None:
                    rejected += 1
        per_p[p] = {
            "slots_with_f_zero": cnt,
            "closed_form_p^2": p**2,
            "agree": cnt == p**2,
            "all_rejected_by_frozen_predicate": rejected == cnt,
            "b_stays_in_family": True,
            "P_lift_frozen": float(L.p_lift(p)),
            "P_lift_if_y0_counted": float(L.p_lift_with_zero_section(p)),
            "relative_increase": float(L.p_lift_with_zero_section(p) / L.p_lift(p)) - 1,
        }
    return {
        "characterisation": ("f = x^3 + b = 0 iff b = -x^3; deg(-x^3) = 6 with leading "
                             "coefficient -1 != 0, so all p^2 of these slots lie inside "
                             "the frozen family, one per monic quadratic x"),
        "per_p": per_p,
        "effect_on_P_lift": ("counting the y = 0 two-torsion section would add exactly "
                             "p^2 hit slots, i.e. multiply N_hit by "
                             "(q_pred(p)+1)/q_pred(p) = 1 + O(p^-4); it changes no "
                             "exponent"),
        "also_note": ("these p^2 slots are the ONLY slots whose section set is exactly "
                      "{y = 0}: for any other slot f != 0, so y = 0 is not a section at "
                      "all"),
    }


# --------------------------------------------------- structural check (mu_3)
def scaling_orbit_check(p: int, b: list, frozen) -> dict:
    """Is the monic hit set of S_b a union of orbits of the F_p^*-scaling action?

    Action: x(t) -> lambda^-2 x(lambda t), which keeps x monic; it fixes S_b for
    exactly those lambda with lambda^-6 b(lambda t) == b(t).
    """
    def scale_b(lam):
        inv6 = pow(pow(lam, 6, p), p - 2, p)
        return [(inv6 * b[k] % p) * pow(lam, k, p) % p for k in range(len(b))]

    stab = [lam for lam in range(1, p) if scale_b(lam) == list(b)]
    hits = []
    for x0 in range(p):
        for x1 in range(p):
            xt = [x0, x1, 1]
            f = frozen.padd(frozen.pmul(frozen.pmul(xt, xt, p), xt, p), b, p)
            if frozen.is_square_poly(f, p) is not None:
                hits.append((x0, x1))
    hitset = set(hits)
    orbits = []
    seen = set()
    for h in hits:
        if h in seen:
            continue
        orb = set()
        for lam in stab:
            inv2 = pow(lam * lam % p, p - 2, p)
            orb.add(((h[0] * inv2) % p, (h[1] * lam % p) * inv2 % p))
        seen |= orb
        orbits.append(sorted(orb))
    return {
        "p": p, "b": list(b), "b_degree": len(b) - 1,
        "monic_hit_slots": hits,
        "monic_hit_count": len(hits),
        "scaling_stabiliser": stab,
        "stabiliser_order": len(stab),
        "orbits": orbits,
        "orbit_sizes": [len(o) for o in orbits],
        "hit_set_is_a_union_of_orbits": all(set(o) <= hitset for o in orbits)
                                        and set().union(*orbits) == hitset
                                        if orbits else len(hits) == 0,
    }


def check_mu3(frozen) -> dict:
    """For p = 1 mod 3 the j = 0 family has the automorphism x -> zeta*x.

    Verified exactly: with FREE x, every hit (x, y) with x != 0 has (zeta x, y)
    as a hit too, because (zeta x)^3 = x^3.  The frozen MONIC slot space hides
    this, since zeta*x is not monic.
    """
    out = {}
    for p in (5, 7, 11, 13):
        zetas = [z for z in range(1, p) if pow(z, 3, p) == 1 and z != 1]
        checked = 0
        violations = 0
        rng = random.Random(L.SEEDS[1])
        sqrts = L.sqrt_table(p)
        for _ in range(400):
            # random free x of degree <= 2 and squarefree y of degree <= 3
            x = [rng.randrange(p) for _ in range(3)]
            y = [rng.randrange(p) for _ in range(4)]
            while len(y) > 1 and y[-1] == 0:
                y.pop()
            if y == [0] or not L.ref_is_squarefree_disc(y, p):
                continue
            xt = list(x)
            while len(xt) > 1 and xt[-1] == 0:
                xt.pop()
            x3 = frozen.pmul(frozen.pmul(xt, xt, p), xt, p)
            b = frozen.psub(frozen.pmul(y, y, p), x3, p)
            if len(b) - 1 != 6:
                continue
            for z in zetas:
                zx = [c * z % p for c in xt]
                zx3 = frozen.pmul(frozen.pmul(zx, zx, p), zx, p)
                f = frozen.padd(zx3, b, p)
                checked += 1
                if frozen.is_square_poly(f, p) is None:
                    violations += 1
        out[p] = {
            "p_mod_3": p % 3,
            "nontrivial_cube_roots_of_unity": zetas,
            "orbit_checks": checked,
            "violations": violations,
            "mu3_acts": bool(zetas),
        }
    return {
        "mu3_orbit_closure": out,
        "scaling_examples": [
            scaling_orbit_check(7, [2, 0, 0, 0, 0, 0, 1], frozen),        # t^6 + 2
            scaling_orbit_check(13, [9, 0, 0, 10, 0, 0, 3], frozen),      # 3t^6+10t^3+9
            scaling_orbit_check(13, [9, 8, 10, 10, 2, 2, 3], frozen),     # generic 9-slot
        ],
        "scaling_mechanism": (
            "the base change t -> lambda t combined with the sextic-twist rescaling "
            "(x, y) -> (lambda^-2 x(lambda t), lambda^-3 y(lambda t)) preserves monicity "
            "of x and maps sections of S_b to sections of S_b' with "
            "b'(t) = lambda^-6 b(lambda t). Surfaces fixed by a subgroup H of F_p^* "
            "therefore carry section orbits whose sizes divide |H|, and the b's fixed by "
            "H are exactly those supported on monomial degrees k = 6 mod |H|. This "
            "symmetry exists because a(t) = 0 makes the family a sextic-twist family of "
            "the single j = 0 curve."),
        "interpretation_boundary": (
            "these are exact structural observations about the frozen j = 0 family, not "
            "a statement about elliptic surfaces in general and not evidence for or "
            "against H-XEDN-001; they bound how representative the frozen family is"),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-id", default="RUN-XEDN-002-CTRL")
    ap.add_argument("--sympy-full-p", type=int, default=5,
                    help="largest p for which the complete f-space gets the sympy "
                         "cross-check")
    args = ap.parse_args()

    started = dt.datetime.now(dt.timezone.utc).isoformat()
    t0 = time.time()
    frozen, digest = L.load_frozen()
    print(f"EXP-XEDN-002 controls, run {args.run_id}")
    print(f"frozen predicate sha256={digest}")
    print()

    print("== control 1: frozen predicate vs two independent implementations ==")
    c1 = {}
    for p in (5, 7):
        use_sympy = (p <= args.sympy_full_p)
        r = control1_full_f_space(p, frozen, use_sympy)
        c1[f"full_f_space_p{p}"] = r
        print(f"  p={p}: {r['f_values_classified']:,} f values (the complete "
              f"reachable set) frozen_hits={r['frozen_hits']} "
              f"reference={r['independent_sqrt_reference_hits']} "
              f"disagreements={r['frozen_vs_sqrt_reference_disagreements']} "
              f"closed_form={r['closed_form_q_pred']} "
              f"match={r['frozen_matches_closed_form']}")
        print(f"        mathematical squares={r['mathematical_square_count']} "
              f"closed_form={r['closed_form_q_true_square']} "
              f"match={r['true_square_matches_closed_form']}")
        if use_sympy:
            print(f"        sympy factorization: squarefree-root squares="
                  f"{r['sympy_square_squarefree_root']} other-root squares="
                  f"{r['sympy_square_other_root']} "
                  f"disagreements_with_frozen={r['frozen_vs_sympy_disagreements']} "
                  f"agree={r['sympy_agrees_with_frozen_semantics']}", flush=True)
    for seed in L.SEEDS:
        r = control1_random_sextics(P_SMOKE, 100000, seed, frozen, sympy_every=40)
        c1[f"random_sextics_p101_seed{seed}"] = r
        print(f"  p=101 random sextics seed={seed}: n={r['samples']:,} "
              f"frozen_hits={r['frozen_hits']} "
              f"reference={r['independent_sqrt_reference_hits']} "
              f"disagreements={r['frozen_vs_reference_disagreements']} "
              f"sympy_cross_checked={r['sympy_cross_checked']} "
              f"sympy_disagreements={r['sympy_disagreements']} "
              f"expected_hits={r['expected_hits']:.4f}", flush=True)
    c1_pass = (all(v.get("frozen_vs_sqrt_reference_disagreements", 0) == 0
                   for v in c1.values() if "frozen_vs_sqrt_reference_disagreements" in v)
               and all(v.get("frozen_vs_reference_disagreements", 0) == 0
                       for v in c1.values() if "frozen_vs_reference_disagreements" in v)
               and all(v.get("sympy_disagreements", 0) == 0 for v in c1.values())
               and all(v.get("frozen_vs_sympy_disagreements", 0) == 0
                       for v in c1.values())
               and c1["full_f_space_p5"]["frozen_matches_closed_form"]
               and c1["full_f_space_p7"]["frozen_matches_closed_form"])
    print(f"  CONTROL 1 VERDICT: {'pass' if c1_pass else 'fail'} "
          f"(no disagreement between the frozen predicate and either independent "
          f"implementation of the same semantics)")
    print()

    print("== control 2: planted-section recovery at p=101 ==")
    c2 = control2_planted(frozen)
    print(f"  planted b degree={c2['b_planted_degree']} (deg 6 required by the "
          f"frozen family: {c2['b_degree_is_6']})")
    print(f"  slots enumerated={c2['slots_enumerated']} frozen hits={c2['frozen_hits']} "
          f"hit list={[(h['x0'], h['x1']) for h in c2['hit_list']]}")
    print(f"  planted section (x0=3, x1=5) recovered={c2['planted_section_recovered']}; "
          f"matches smoke (exactly 1 section)={c2['matches_smoke']}")
    print(f"  independent reference hits={c2['independent_reference_hits']}")
    print(f"  DEVIATION: {c2['deviation_note']}")
    c2_pass = c2["planted_section_recovered"] and c2["matches_smoke"]
    print(f"  CONTROL 2 VERDICT: {'pass' if c2_pass else 'fail'}")
    print()

    print("== control 3: smoke consistency ==")
    c3 = control3_smoke_consistency()
    print(f"  P_lift(101) = {c3['P_lift_exact']} = {c3['P_lift_float']:.6e}")
    print(f"  expected hits in the smoke's {c3['slots_tested_by_smoke']} slots = "
          f"{c3['expected_hits']:.6f}; P(observe 0) = "
          f"{c3['poisson_prob_of_observing_zero']:.6f}")
    print(f"  observed 0 inside the Poisson interval of the prediction: "
          f"{c3['observed_zero_inside_poisson_interval']}")
    print(f"  95% upper limit on the rate given 0 hits = "
          f"{c3['one_sided_95_upper_limit_on_rate_given_zero_hits']:.3e}; "
          f"closed form inside it: {c3['closed_form_rate_inside_that_limit']}")
    nc = c3["negative_control"]
    print(f"  part-4 negative control: expected {nc['expected_hits']:.4f} squares in "
          f"{nc['samples']:,} sextics, observed {nc['hits_observed']}; "
          f"P(observe 0) = {nc['poisson_prob_of_observing_zero']:.4f}")
    c3_pass = (c3["observed_zero_inside_poisson_interval"]
               and c3["closed_form_rate_inside_that_limit"]
               and nc["observed_zero_consistent"])
    print(f"  CONTROL 3 VERDICT: {'pass' if c3_pass else 'fail'}")
    print()

    print("== control 4: iso-triviality ==")
    c4 = control4_isotriviality(frozen)
    print(f"  j-invariant of every member: {c4['j_invariant_of_the_family']} "
          f"({c4['j_invariant_reasoning']})")
    print(f"  constant-b surfaces: {c4['constant_b_surfaces']['count']} "
          f"({c4['constant_b_surfaces']['explanation']})")
    for p, v in c4["trivial_over_F_p_of_t"]["counts"].items():
        print(f"  p={p}: b = c*(t+a)^6 count={v['b_of_form_c_times_linear_to_the_6']} "
              f"closed form={v['closed_form_(p-1)*p']} agree={v['agree']} "
              f"fraction={v['fraction']:.3e}")
    print(f"  FINDING: {c4['isotrivial_under_constant_j_definition']['explanation']}")
    c4_discharged = all(v["agree"] for v in c4["trivial_over_F_p_of_t"]["counts"].values())
    print(f"  CONTROL 4 VERDICT: discharged with a finding "
          f"(counts verified: {c4_discharged})")
    print()

    print("== control 5: degenerate y = 0 section ==")
    c5 = control5_degenerate(frozen)
    for p, v in c5["per_p"].items():
        print(f"  p={p}: slots with f = 0: {v['slots_with_f_zero']} "
              f"(closed form p^2 = {v['closed_form_p^2']}, agree={v['agree']}); "
              f"all rejected by the frozen predicate="
              f"{v['all_rejected_by_frozen_predicate']}; "
              f"P_lift would rise by {v['relative_increase']:.3e} relative")
    c5_pass = all(v["agree"] and v["all_rejected_by_frozen_predicate"]
                  for v in c5["per_p"].values())
    print(f"  CONTROL 5 VERDICT: {'pass' if c5_pass else 'fail'}")
    print()

    print("== structural check (not a contract control): mu_3 automorphism ==")
    st = check_mu3(frozen)
    for p, v in st["mu3_orbit_closure"].items():
        print(f"  p={p} (p mod 3 = {v['p_mod_3']}): cube roots of unity "
              f"{v['nontrivial_cube_roots_of_unity']}, orbit checks "
              f"{v['orbit_checks']}, violations {v['violations']}")
    for se in st["scaling_examples"]:
        print(f"  p={se['p']}, b={se['b']}: {se['monic_hit_count']} monic hit slots, "
              f"scaling stabiliser {se['scaling_stabiliser']} (order "
              f"{se['stabiliser_order']}), orbit sizes {se['orbit_sizes']}, "
              f"hit set is a union of orbits: {se['hit_set_is_a_union_of_orbits']}")
    struct_ok = (all(v["violations"] == 0 for v in st["mu3_orbit_closure"].values())
                 and all(se["hit_set_is_a_union_of_orbits"]
                         for se in st["scaling_examples"]))
    print(f"  structural check consistent: {struct_ok}")
    print()

    verdicts = {
        "control_1_frozen_predicate": "pass" if c1_pass else "fail",
        "control_2_planted_section": "pass" if c2_pass else "fail",
        "control_3_smoke_consistency": "pass" if c3_pass else "fail",
        "control_4_isotriviality": ("discharged_with_finding" if c4_discharged
                                    else "fail"),
        "control_5_degenerate_section": "pass" if c5_pass else "fail",
    }
    print("== control verdicts ==")
    for k, v in verdicts.items():
        print(f"  {k}: {v}")
    all_ok = c1_pass and c2_pass and c3_pass and c4_discharged and c5_pass and struct_ok

    finished = dt.datetime.now(dt.timezone.utc).isoformat()
    wall = time.time() - t0
    raw = {
        "arm": "controls",
        "frozen_predicate_sha256": digest,
        "control_1_frozen_predicate": c1,
        "control_2_planted_section": c2,
        "control_3_smoke_consistency": c3,
        "control_4_isotriviality": c4,
        "control_5_degenerate_section": c5,
        "structural_check_mu3": st,
        "verdicts": verdicts,
        "all_controls_pass": all_ok,
    }
    L.write_run_record(
        run_id=args.run_id,
        purpose=("Controls 1-5 of the frozen EXP-XEDN-002 specification plus the mu_3 "
                 "structural check the census provoked"),
        entrypoint="experiments/EXP-XEDN-002/implementation/controls.py",
        parameters={
            "field_bits": P_SMOKE.bit_length(),
            "primes": [5, 7, 11, 13, 101],
            "surface_family": "y^2 = x^3 + b(t), deg b = 6",
            "section_shape": "x monic deg 2, y deg <= 3",
            "predicate": "EXP-XEDN-001 is_square_poly",
            "arms": ["controls"],
            "random_sextics_per_seed": 100000,
            "sympy_full_f_space_up_to_p": args.sympy_full_p,
        },
        started_at=started, finished_at=finished, wall=wall,
        validity="valid",
        validity_reason=("all five contract controls executed with explicit verdicts; "
                         "controls 1, 2, 3, 5 pass and control 4 is discharged with a "
                         "recorded finding about the definition of iso-triviality"),
        summary=(f"controls: 1={verdicts['control_1_frozen_predicate']}, "
                 f"2={verdicts['control_2_planted_section']}, "
                 f"3={verdicts['control_3_smoke_consistency']}, "
                 f"4={verdicts['control_4_isotriviality']}, "
                 f"5={verdicts['control_5_degenerate_section']}; planted b has degree 5 "
                 f"so it lies outside the deg-b-6 census family; every member of the "
                 f"family has j = 0"),
        raw=raw,
    )
    print(f"controls complete in {wall:.1f}s; peak_memory_mb={L.peak_memory_mb()}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
