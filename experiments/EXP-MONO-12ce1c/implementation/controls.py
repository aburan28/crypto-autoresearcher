"""
Stage 4 controls and nulls (specification.yaml arms_and_controls):
  positive_control_1  -- random monic quartics vs S_4 Chebotarev densities
  positive_control_2  -- planted 2-torsion collision on the sublocus
  measured_null_1     -- cross-curve construction (CAN FAIL; see finding below)
  measured_null_2     -- is realized directly from the tau=1 Stage-3 cells,
                          not a separate function (same code path, same
                          construction, per the contract's own text)
"""
import math
import sympy as sp
from seed import Drawer
from fields import Fp2, ec_add_fp2, ec_neg_fp2, legendre

CHEBOTAREV_S4 = {
    "1^4": sp.Rational(1, 24),
    "2+1+1": sp.Rational(1, 4),
    "2^2": sp.Rational(1, 8),
    "3+1": sp.Rational(1, 3),
    "4": sp.Rational(1, 4),
}

T_SYM = sp.symbols("T")


def _degree_multiset_to_label(degs):
    degs = tuple(sorted(degs))
    if degs == (1, 1, 1, 1):
        return "1^4"
    if degs == (1, 1, 2):
        return "2+1+1"
    if degs == (2, 2):
        return "2^2"
    if degs == (1, 3):
        return "3+1"
    if degs == (4,):
        return "4"
    return None  # degenerate (repeated-factor) stratum -- excluded, counted separately


def positive_control_1(domain, p, n_trials):
    """Random monic quartics T^4+c3T^3+c2T^2+c1T+c0 over F_p, label 'quartic',
    classified by factoring over F_p (sympy, modulus=p) -- the identical
    general-purpose classifier Path 2 uses for the treatment arms."""
    drawer = Drawer(domain, "quartic", p, 0)
    histogram = {k: 0 for k in CHEBOTAREV_S4}
    degenerate = 0
    n_admissible = 0
    for _ in range(n_trials):
        c3 = drawer.draw(p)
        c2 = drawer.draw(p)
        c1 = drawer.draw(p)
        c0 = drawer.draw(p)
        coeffs = [1, c3, c2, c1, c0]
        poly = sp.Poly(coeffs, T_SYM, modulus=p)
        _, factors = poly.factor_list()
        if any(mult > 1 for _, mult in factors):
            degenerate += 1
            continue
        degs = []
        for fac, mult in factors:
            degs.extend([sp.degree(fac, T_SYM)] * mult)
        label = _degree_multiset_to_label(degs)
        if label is None:
            degenerate += 1
            continue
        histogram[label] += 1
        n_admissible += 1
    return {
        "n_trials": n_trials, "n_admissible": n_admissible, "degenerate_excluded": degenerate,
        "histogram": histogram,
    }


def chebotarev_check(histogram, n_admissible):
    """Per-type: observed frequency, forced density, binomial SE, sigma deviation."""
    out = {}
    for label, density in CHEBOTAREV_S4.items():
        density_f = float(density)
        observed = histogram[label]
        freq = observed / n_admissible if n_admissible else float("nan")
        se = math.sqrt(density_f * (1 - density_f) / n_admissible) if n_admissible else float("nan")
        sigma = abs(freq - density_f) / se if se > 0 else float("nan")
        out[label] = {
            "observed_count": observed, "observed_freq": freq, "forced_density": density_f,
            "binomial_se": se, "sigma_deviation": sigma, "within_3_sigma": sigma <= 3.0,
        }
    return out


def positive_control_2_planted(domain, p, A, B, fb, m, n_trials):
    """Plant P_2 = P_1 + T for the nonzero 2-torsion point T (requires the
    curve to have Z >= 1, i.e. tau >= 2). label 'plant'. Every planted tuple
    MUST show a collision (D >= 1) at m = 4 (the {1,2}-branch construction the
    contract names); m = 5 planted tuples use an extra genuinely-random
    factor-base point beyond the planted pair and are reported separately."""
    F = Fp2(p)
    A_fp2 = F.from_fp(A)
    T_x = None
    for x in range(p):
        if (x * x * x + A * x + B) % p == 0:
            T_x = x
            break
    if T_x is None:
        return None  # tau == 1, no 2-torsion point -- caller must not call this on tau=1 curves
    T_pt = (F.from_fp(T_x), F.from_fp(0))
    drawer = Drawer(domain, "plant", p, m)
    n_fb = len(fb)
    detected = 0
    n_valid = 0
    for _ in range(n_trials):
        i1 = drawer.draw(n_fb)
        x1, y1 = fb[i1]
        P1 = (F.from_fp(x1), F.from_fp(y1))
        P2 = ec_add_fp2(F, P1, T_pt, A_fp2)
        if P2 is None:
            continue  # P1 == -T, degenerate draw; excluded
        x2 = P2[0][0]
        extra_xs = set()
        others = []
        needed = m - 3  # 0 for m=4, 1 for m=5
        tries = 0
        while len(others) < needed and tries < 50:
            j = drawer.draw(n_fb)
            tries += 1
            xj, yj = fb[j]
            if xj in (x1, x2) or xj in extra_xs:
                continue
            extra_xs.add(xj)
            others.append((xj, yj))
        if len(others) < needed:
            continue
        pts = [(F.from_fp(x1), F.from_fp(y1)), P2] + [
            (F.from_fp(xj), F.from_fp(yj)) for xj, yj in others
        ]
        partial = {(): pts[0]}
        for Pi in pts[1:]:
            negPi = ec_neg_fp2(F, Pi)
            new_partial = {}
            for key, pt in partial.items():
                new_partial[key + (1,)] = ec_add_fp2(F, pt, Pi, A_fp2)
                new_partial[key + (-1,)] = ec_add_fp2(F, pt, negPi, A_fp2)
            partial = new_partial
        xs = [("INF" if pt is None else pt[0][0]) for pt in partial.values()]
        n_valid += 1
        if len(set(xs)) < len(xs):
            detected += 1
    return {"n_trials": n_trials, "n_valid": n_valid, "detected": detected,
            "detection_rate": (detected / n_valid) if n_valid else float("nan")}


def measured_null_1_cross_curve(domain, p, A, B, Ap, Bp, n_trials):
    """Cross-curve null (specification.yaml measured_null_1), m = 4.
    P1=(x1,y1) with y1^2=f_E(x1); P2=(x2,y2) with y2^2=f_E(x2) (both from E,
    label 'crosscurve' draws x1,x2); P3'=(x3,y3') with y3'^2=f_{E'}(x3) (from
    the DIFFERENT curve E', same field p). All three combined via the SAME
    chord-tangent addition formula used everywhere else in this experiment
    (E's own A is only used in the doubling branch, which x1!=x2!=x3 admissible
    draws essentially never hit).

    FINDING (recorded here because it was produced by running this exact
    construction, not asserted): the observed cycle type distribution over
    n_trials draws contains ONLY the two Kummer-allowed types (identity and
    pure-2-cycle), never a 4-cycle or a 3+1 split -- contradicting this
    control's own declared forced value. See implementation.md
    "measured_null_1 finding" for the accompanying algebraic argument
    (Frobenius commutes with the chord-tangent addition formula's rational
    functions regardless of whether the summed points lie on a common curve,
    since each individual generator's Frobenius image is +-itself purely from
    being a square root of an F_p element -- a fact that does not require
    curve membership at all). Per the contract's own text this control's
    failure would render Stage 2 VOID; that disposition is reported literally
    in execution_report.yaml as a Stage-4 finding, not decided here."""
    F = Fp2(p)
    A_fp2 = F.from_fp(A)
    drawer = Drawer(domain, "crosscurve", p, 4)
    histogram = {}
    n_valid = 0
    for _ in range(n_trials):
        x1 = drawer.draw(p)
        x2 = drawer.draw(p)
        x3 = drawer.draw(p)
        if len({x1, x2, x3}) < 3:
            continue
        f1 = (x1 ** 3 + A * x1 + B) % p
        f2 = (x2 ** 3 + A * x2 + B) % p
        f3p = (x3 ** 3 + Ap * x3 + Bp) % p
        if f1 == 0 or f2 == 0 or f3p == 0:
            continue
        y1, _ = F.sqrt_of_fp_element(f1)
        y2, _ = F.sqrt_of_fp_element(f2)
        y3, _ = F.sqrt_of_fp_element(f3p)
        P1, P2, P3 = (F.from_fp(x1), y1), (F.from_fp(x2), y2), (F.from_fp(x3), y3)
        partial = {(): P1}
        for Pi in (P2, P3):
            negPi = ec_neg_fp2(F, Pi)
            new_partial = {}
            for key, pt in partial.items():
                new_partial[key + (1,)] = ec_add_fp2(F, pt, Pi, A_fp2)
                new_partial[key + (-1,)] = ec_add_fp2(F, pt, negPi, A_fp2)
            partial = new_partial
        if any(pt is None for pt in partial.values()):
            continue
        xvals = {}
        dup = False
        for key, pt in partial.items():
            xv = (pt[0][0] % p, pt[0][1] % p)
            if xv in xvals:
                dup = True
                break
            xvals[xv] = key
        if dup:
            continue
        perm = {}
        ok = True
        for key, pt in partial.items():
            fX = F.conj(pt[0])
            if fX not in xvals:
                ok = False
                break
            perm[key] = xvals[fX]
        if not ok:
            continue
        n_valid += 1
        # cycle type
        keys = list(partial.keys())
        seen = set()
        lengths = []
        for k in keys:
            if k in seen:
                continue
            length = 0
            cur = k
            while cur not in seen:
                seen.add(cur)
                cur = perm[cur]
                length += 1
            lengths.append(length)
        ct = tuple(sorted(lengths))
        histogram[ct] = histogram.get(ct, 0) + 1
    return {"n_trials": n_trials, "n_valid": n_valid, "histogram": {str(k): v for k, v in histogram.items()},
            "four_cycles_or_3plus1_observed": any(
                ct not in ((1, 1, 1, 1), (2, 2)) for ct in histogram),
            }
