"""EXP-SMON-e5cbe6 -- falsification battery for the Semaev summation cover.

Every check below is written so that it can FAIL. The predictions it tests are
frozen in ../contract.md; this file computes, it does not interpret.

Usage:  python3 verify.py [--out raw-result.json]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import random
import sys
import time
from itertools import product

from semaev_cover import (
    Curve,
    ZPoly,
    eval_poly_fp2,
    factor_pattern,
    is_squarefree,
    semaev_T_poly,
    signed_sum_xs,
)

SEED = 20260807


# ---------------------------------------------------------------------------
# C1 -- the m = 3 discriminant identity, as an identity in Z[x1, x2, A, B]
# ---------------------------------------------------------------------------


def check_disc_identity() -> dict:
    n = 4
    x1 = ZPoly.var(n, 0)
    x2 = ZPoly.var(n, 1)
    A = ZPoly.var(n, 2)
    B = ZPoly.var(n, 3)
    k = lambda v: ZPoly.const(n, v)  # noqa: E731

    c2 = (x1 - x2) ** 2
    c1 = k(-2) * ((x1 + x2) * (x1 * x2 + A) + k(2) * B)
    c0 = (x1 * x2 - A) ** 2 - k(4) * B * (x1 + x2)
    disc = c1 * c1 - k(4) * c2 * c0

    f1 = x1**3 + A * x1 + B
    f2 = x2**3 + A * x2 + B
    target = k(16) * f1 * f2

    return {
        "identity": "disc_T S_3(x1,x2,T) == 16 f(x1) f(x2) in Z[x1,x2,A,B]",
        "holds": (disc - target).is_zero(),
        "monomials_in_disc": len(disc.c),
        "ring": "Z[x1,x2,A,B] (exact integer coefficients, not a modular check)",
    }


# ---------------------------------------------------------------------------
# curve battery, including the special j-invariants
# ---------------------------------------------------------------------------


def curve_battery(rng: random.Random) -> list[dict]:
    out = []

    def add(p, A, B, label):
        try:
            c = Curve(p, A, B)
        except AssertionError:
            return
        out.append({"p": p, "A": c.A, "B": c.B, "label": label, "curve": c})

    # generic j, several primes on both sides of p mod 4 and p mod 3
    for p in (101, 103, 211, 307, 401, 1009):
        for _ in range(2):
            while True:
                A, B = rng.randrange(p), rng.randrange(p)
                if (4 * A**3 + 27 * B**2) % p:
                    break
            add(p, A, B, "generic-j")

    # j = 0  (A = 0): extra automorphisms rational iff p = 1 mod 3
    add(103, 0, 7, "j=0, p=1 mod 3")
    add(101, 0, 5, "j=0, p=2 mod 3")
    # j = 1728 (B = 0): extra automorphisms rational iff p = 1 mod 4
    add(101, 3, 0, "j=1728, p=1 mod 4")
    add(103, 3, 0, "j=1728, p=3 mod 4 (supersingular)")
    # full rational 2-torsion: f(x) = x(x-1)(x-c) shifted to A,B form
    for p in (101, 211):
        for c in (2, 5):
            # f = (x-r1)(x-r2)(x-r3) with sum of roots 0
            r = [0, 1, c]
            s = sum(r) % p
            r = [(ri - s * pow(3, p - 2, p)) % p for ri in r]
            if len({x % p for x in r}) < 3:
                continue
            A = (r[0] * r[1] + r[0] * r[2] + r[1] * r[2]) % p
            B = (-r[0] * r[1] * r[2]) % p
            add(p, A, B, "full rational 2-torsion")
    return out


# ---------------------------------------------------------------------------
# C2..C5 -- the fibre law at one specialisation
# ---------------------------------------------------------------------------


def probe(curve: Curve, xs: list[int]) -> dict:
    """Everything measurable about the fibre of S_m over (x_1,...,x_{m-1})."""
    p = curve.p
    m = len(xs) + 1
    expected_deg = 2 ** (m - 2)
    poly = semaev_T_poly(curve, xs)
    deg = len(poly) - 1
    sums = signed_sum_xs(curve, xs)
    finite = [s for s in sums if s is not None]
    distinct = len({s for s in finite})

    rec = {
        "m": m,
        "xs": xs,
        "chi": [curve.chi(x) for x in xs],
        "deg_T": deg,
        "expected_deg_T": expected_deg,
        "n_signed_sums": len(sums),
        "n_at_infinity": len(sums) - len(finite),
        "n_distinct_sums": distinct,
    }

    good = (
        deg == expected_deg
        and len(finite) == expected_deg
        and distinct == expected_deg
        and is_squarefree(poly, p)
    )
    rec["good"] = good
    if not good:
        return rec

    # C3: the signed sums are exactly the roots (checked over F_{p^2})
    F = curve.F2
    rec["all_sums_are_roots"] = all(
        F.is_zero(eval_poly_fp2(poly, s, F)) for s in finite
    )
    # C4/C5: factorisation pattern over F_p and the character prediction
    pat = factor_pattern(poly, p)
    rec["pattern"] = {str(k): v for k, v in sorted(pat.items())}
    chis = rec["chi"]
    all_equal = len(set(chis)) == 1 and chis[0] != 0
    rec["predicted_split"] = all_equal
    rec["observed_split"] = pat == {1: expected_deg}
    rec["pattern_matches_prediction"] = (
        pat == ({1: expected_deg} if all_equal else {2: expected_deg // 2})
    )
    rec["max_factor_degree"] = max(pat) if pat else 0
    rec["mixed_pattern"] = len(pat) > 1
    # roots in F_p must be exactly the F_p-rational signed sums
    rec["n_roots_in_Fp"] = sum(1 for s in finite if F.in_base_field(s))
    # C8: the Frobenius class, i.e. the chi-vector modulo the global sign flip
    cls = tuple(chis) if chis[0] == 1 else tuple(-c for c in chis)
    rec["frobenius_class"] = "".join("+" if c == 1 else "-" for c in cls)
    # C9: square class of disc_T S_m -- non-square at m = 3, square at m >= 4
    d = disc_of(poly, p)
    rec["disc_chi"] = 0 if d == 0 else (1 if pow(d, (p - 1) // 2, p) == 1 else -1)
    if m == 3:
        pred = (16 * curve.f(xs[0]) * curve.f(xs[1])) % p
        rec["disc_equals_16_f_f"] = d % p == pred
    return rec


def disc_of(poly: list[int], p: int) -> int:
    """disc(f) = (-1)^{d(d-1)/2} Res(f, f') / lc(f) for a univariate f over F_p."""
    from semaev_cover import _poly_derivative, _sylvester_det

    d = len(poly) - 1
    der = _poly_derivative(poly, p)
    r = _sylvester_det(poly, der, p)
    sign = -1 if (d * (d - 1) // 2) % 2 else 1
    return sign * r * pow(poly[-1], p - 2, p) % p


# ---------------------------------------------------------------------------
# null controls -- the same instrument on objects with no elliptic structure
# ---------------------------------------------------------------------------


def null_controls(rng: random.Random, trials: int = 400) -> dict:
    """Two nulls, both degree-4 covers, neither a summation polynomial.

    NULL-A: a uniformly random degree-4 polynomial in T.
    NULL-B: Res_X(h(X), S_3(x_3, T, X)) with h a random degree-2 polynomial --
            the S_4 construction with the inner summation polynomial replaced
            by a generic quadratic, i.e. the elliptic structure removed and
            everything else held fixed.

    If the pattern law of C4 held for these too, C4 would be vacuous.
    """
    from semaev_cover import _s3_coeffs_in_X_at_T, _interpolate, _sylvester_det

    p = 401
    curve = Curve(p, 5, 7)
    stats = {"NULL-A": {}, "NULL-B": {}}

    for name in ("NULL-A", "NULL-B"):
        seen: dict[str, int] = {}
        law_holds = 0
        n = 0
        for _ in range(trials):
            if name == "NULL-A":
                poly = [rng.randrange(p) for _ in range(4)] + [rng.randrange(1, p)]
            else:
                h = [rng.randrange(p) for _ in range(2)] + [rng.randrange(1, p)]
                x3 = rng.randrange(p)
                pts = []
                t = 0
                while len(pts) <= 4:
                    g = _s3_coeffs_in_X_at_T(curve, x3, t)
                    pts.append((t, _sylvester_det(h, g, p)))
                    t += 1
                poly = _interpolate(pts, p)
            if len(poly) - 1 != 4 or not is_squarefree(poly, p):
                continue
            n += 1
            pat = factor_pattern(poly, p)
            key = "+".join(f"{d}^{c}" for d, c in sorted(pat.items()))
            seen[key] = seen.get(key, 0) + 1
            if pat in ({1: 4}, {2: 2}):
                law_holds += 1
        stats[name] = {
            "separable_degree_4_samples": n,
            "patterns": seen,
            "fraction_obeying_the_C4_dichotomy": round(law_holds / n, 4) if n else None,
        }
    return stats


# ---------------------------------------------------------------------------
# drivers
# ---------------------------------------------------------------------------


def run_sampled(battery, m: int, per_curve: int, rng: random.Random) -> dict:
    tally = {
        "m": m,
        "samples": 0,
        "good": 0,
        "bad": 0,
        "bad_reasons": {},
        "roots_identified": 0,
        "pattern_matches": 0,
        "pattern_mismatch_examples": [],
        "max_factor_degree_seen": 0,
        "mixed_patterns": 0,
        "split_good": 0,
        "frobenius_classes": {},
        "pattern_by_class": {},
        "disc_chi_counts": {},
        "disc_identity_m3_holds": 0,
        "per_curve": [],
    }
    for entry in battery:
        curve = entry["curve"]
        p = curve.p
        if p <= 2 ** (m - 2) + 1:
            continue
        c_tally = {"p": p, "label": entry["label"], "good": 0, "bad": 0, "split": 0}
        for _ in range(per_curve):
            xs = [rng.randrange(p) for _ in range(m - 1)]
            rec = probe(curve, xs)
            tally["samples"] += 1
            if not rec["good"]:
                tally["bad"] += 1
                c_tally["bad"] += 1
                why = (
                    "degree_drop"
                    if rec["deg_T"] != rec["expected_deg_T"]
                    else "sum_at_infinity"
                    if rec["n_at_infinity"]
                    else "repeated_root"
                )
                tally["bad_reasons"][why] = tally["bad_reasons"].get(why, 0) + 1
                continue
            tally["good"] += 1
            c_tally["good"] += 1
            tally["roots_identified"] += int(rec["all_sums_are_roots"])
            tally["pattern_matches"] += int(rec["pattern_matches_prediction"])
            tally["mixed_patterns"] += int(rec["mixed_pattern"])
            tally["max_factor_degree_seen"] = max(
                tally["max_factor_degree_seen"], rec["max_factor_degree"]
            )
            cls = rec["frobenius_class"]
            tally["frobenius_classes"][cls] = tally["frobenius_classes"].get(cls, 0) + 1
            pat_key = "+".join(f"{d}^{c}" for d, c in sorted(
                (int(k), v) for k, v in rec["pattern"].items()))
            tally["pattern_by_class"].setdefault(cls, {})
            tally["pattern_by_class"][cls][pat_key] = (
                tally["pattern_by_class"][cls].get(pat_key, 0) + 1)
            dk = str(rec["disc_chi"])
            tally["disc_chi_counts"][dk] = tally["disc_chi_counts"].get(dk, 0) + 1
            if m == 3:
                tally["disc_identity_m3_holds"] += int(rec["disc_equals_16_f_f"])
            if rec["observed_split"]:
                tally["split_good"] += 1
                c_tally["split"] += 1
            if not rec["pattern_matches_prediction"] and len(
                tally["pattern_mismatch_examples"]
            ) < 10:
                tally["pattern_mismatch_examples"].append(
                    {"p": p, "A": curve.A, "B": curve.B, **rec}
                )
        tally["per_curve"].append(c_tally)

    n_classes = 2 ** (m - 2)
    seen = tally["frobenius_classes"]
    tally["n_frobenius_classes_seen"] = len(seen)
    tally["all_classes_realised"] = len(seen) == n_classes
    tally["one_pattern_per_class"] = all(
        len(v) == 1 for v in tally["pattern_by_class"].values()
    )
    if tally["good"]:
        all_classes = ["+" + "".join(s) for s in product("+-", repeat=m - 2)]
        exp = tally["good"] / n_classes
        tally["class_chi2"] = round(
            sum((seen.get(c, 0) - exp) ** 2 / exp for c in all_classes), 3
        )
        tally["class_chi2_dof"] = n_classes - 1
    return tally


def run_factor_base(battery, m: int, per_curve: int, rng: random.Random) -> dict:
    """C5 -- the specialisation index calculus actually uses.

    Every x_i is the x-coordinate of an F_p-rational point. The claim under
    test is complete splitting at EVERY m, with the root set exactly the
    signed sums, all of them in F_p.
    """
    tally = {
        "m": m,
        "samples": 0,
        "good": 0,
        "degenerate": 0,
        "split_completely": 0,
        "roots_all_in_Fp": 0,
        "roots_are_signed_sums": 0,
        "counterexamples": [],
    }
    for entry in battery:
        curve = entry["curve"]
        p = curve.p
        if p <= 2 ** (m - 2) + 1:
            continue
        fb = [x for x in range(p) if curve.chi(x) == 1]
        if len(fb) < m:
            continue
        for _ in range(per_curve):
            xs = [rng.choice(fb) for _ in range(m - 1)]
            rec = probe(curve, xs)
            tally["samples"] += 1
            if not rec["good"]:
                tally["degenerate"] += 1
                continue
            tally["good"] += 1
            split = rec["observed_split"]
            tally["split_completely"] += int(split)
            tally["roots_all_in_Fp"] += int(rec["n_roots_in_Fp"] == 2 ** (m - 2))
            tally["roots_are_signed_sums"] += int(rec["all_sums_are_roots"])
            if not split and len(tally["counterexamples"]) < 10:
                tally["counterexamples"].append(
                    {"p": p, "A": curve.A, "B": curve.B, **rec}
                )
    return tally


def run_exhaustive(p: int, A: int, B: int, m: int) -> dict:
    """Every specialisation in F_p^{m-1}, no sampling. Small p only."""
    curve = Curve(p, A, B)
    S = sum(1 for x in range(p) if curve.chi(x) == 1)
    N = sum(1 for x in range(p) if curve.chi(x) == -1)
    Z = sum(1 for x in range(p) if curve.chi(x) == 0)
    good = bad = split = mismatch = 0
    maxdeg = 0
    cls_good: dict[str, int] = {}
    cls_bad: dict[str, int] = {}
    chi = [curve.chi(x) for x in range(p)]

    def class_of(xs):
        c = [chi[x] for x in xs]
        if 0 in c:
            return None  # ramified: no Frobenius class
        return "".join("+" if v == 1 else "-" for v in (c if c[0] == 1 else [-v for v in c]))

    for xs in product(range(p), repeat=m - 1):
        rec = probe(curve, list(xs))
        k = class_of(xs)
        if not rec["good"]:
            bad += 1
            if k:
                cls_bad[k] = cls_bad.get(k, 0) + 1
            continue
        good += 1
        cls_good[k] = cls_good.get(k, 0) + 1
        split += int(rec["observed_split"])
        mismatch += int(not rec["pattern_matches_prediction"])
        maxdeg = max(maxdeg, rec["max_factor_degree"])

    # exact closed form: |class of eps| = S^k N^{n-k} + N^k S^{n-k}, n = m-1
    n = m - 1
    closed: dict[str, int] = {}
    for tail in product("+-", repeat=n - 1):
        key = "+" + "".join(tail)
        kk = key.count("+")
        closed[key] = S**kk * N ** (n - kk) + N**kk * S ** (n - kk)
    residuals = {
        key: closed[key] - cls_good.get(key, 0) - cls_bad.get(key, 0) for key in closed
    }
    return {
        "per_class_closed_form": closed,
        "per_class_good": cls_good,
        "per_class_degenerate": cls_bad,
        "per_class_residual_closed_minus_observed": residuals,
        "per_class_identity_exact": all(v == 0 for v in residuals.values()),
        "p": p,
        "A": A,
        "B": B,
        "m": m,
        "trace_t": p + 1 - (2 * S + Z + 1),
        "S": S,
        "N": N,
        "Z": Z,
        "total_specialisations": p ** (m - 1),
        "good": good,
        "bad": bad,
        "bad_fraction": round(bad / p ** (m - 1), 6),
        "bad_fraction_times_p": round(bad / p ** (m - 1) * p, 4),
        "split_on_good_locus": split,
        "closed_form_S_pow_plus_N_pow": S ** (m - 1) + N ** (m - 1),
        "closed_form_minus_observed": S ** (m - 1) + N ** (m - 1) - split,
        "pattern_mismatches": mismatch,
        "max_factor_degree": maxdeg,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="raw-result.json")
    ap.add_argument("--quick", action="store_true")
    args = ap.parse_args()

    t0 = time.time()
    rng = random.Random(SEED)
    battery = curve_battery(rng)

    # Nothing environment-dependent goes into `results`: timing, interpreter and
    # platform belong to the run manifest, and putting them here would make the
    # artifact differ between byte-identical computations.
    results = {
        "experiment_id": "EXP-SMON-e5cbe6",
        "seed": SEED,
        "curves": [
            {k: v for k, v in e.items() if k != "curve"} for e in battery
        ],
        "C1_discriminant_identity": check_disc_identity(),
    }

    per = 60 if args.quick else 400
    results["C2_C4_generic_fibre"] = {
        f"m={m}": run_sampled(battery, m, per // (1 if m < 5 else 4), rng)
        for m in (3, 4, 5)
    }
    results["C5_factor_base_locus"] = {
        f"m={m}": run_factor_base(battery, m, per // (1 if m < 5 else 4), rng)
        for m in (3, 4, 5)
    }
    results["C6_exhaustive"] = {
        "m=3": [run_exhaustive(p, 5, 7, 3) for p in ([53] if args.quick else [53, 101, 211])],
        "m=4": [run_exhaustive(p, 5, 7, 4) for p in ([37] if args.quick else [37, 53])],
    }
    results["C7_null_controls"] = null_controls(rng, 120 if args.quick else 600)

    blob = json.dumps(results, indent=2, sort_keys=True)
    with open(args.out, "w") as fh:
        fh.write(blob + "\n")
    print(blob)
    for line in (
        f"elapsed_seconds: {round(time.time() - t0, 2)}",
        f"python: {sys.version.split()[0]}",
        f"platform: {platform.platform()}",
        f"sha256({args.out}): {hashlib.sha256((blob + chr(10)).encode()).hexdigest()}",
    ):
        print(line, file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
