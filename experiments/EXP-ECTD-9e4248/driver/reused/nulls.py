"""
nulls.py -- CTRL-OUTSIDE-CLASS and CTRL-DEGREE-PROFILE null constructions.

CTRL-OUTSIDE-CLASS: random same-p curves with prime order in the same bit range but
DIFFERENT N (i.e. a different isogeny class entirely), same meters computed on them
via meters.compute_curve_meters -- the frozen FB rule and solver budget are
identical, only the curve draw differs (drawn independently, not via the isogeny
walk).

CTRL-DEGREE-PROFILE: random systems with the SAME shape as the frozen m=2 Semaev
system {f0(x1,x2) degree<=4, f1(x1) degree=fb_size, f2(x2) degree=fb_size} but random
coefficients, each forced through a shared planted common root (ALBIN lesson: a
properly-determined system, not an artificially underdetermined one) -- see
docs referenced in specification.yaml controls.CTRL-DEGREE-PROFILE.
"""
from . import fp, curve, mvpoly, groebner, macaulay


def outside_class_curves(p, exclude_N, bit_lo, bit_hi, rng, count, max_attempts=20000):
    out = []
    attempts = 0
    while len(out) < count and attempts < max_attempts:
        attempts += 1
        a = rng.randrange(p)
        b = rng.randrange(p)
        if (4 * a ** 3 + 27 * b * b) % p == 0:
            continue
        N = curve.find_curve_order(a, b, p, rng, tries=6)
        if N is None:
            continue
        if not (bit_lo <= N.bit_length() <= bit_hi):
            continue
        if N == exclude_N:
            continue
        if not fp.is_probable_prime(N):
            continue
        out.append((a, b, N))
    return out, attempts


def _random_poly_with_root(nvars, p, root, max_deg, nterms, rng, allowed_vars=None):
    """allowed_vars: if given, only these variable indices may have nonzero exponent
    (used to build the univariate-in-x1-only / univariate-in-x2-only null pieces)."""
    allowed_vars = allowed_vars if allowed_vars is not None else list(range(nvars))
    terms = {}
    for _ in range(nterms):
        exps = [0] * nvars
        deg_budget = max_deg
        for v in allowed_vars:
            e = rng.randrange(0, deg_budget + 1)
            exps[v] = e
            deg_budget -= e
        c = rng.randrange(1, p)
        terms[tuple(exps)] = (terms.get(tuple(exps), 0) + c) % p
    # ensure the top degree is actually hit at least once (mimic the real system's
    # degree profile faithfully rather than drifting low)
    top = [0] * nvars
    v0 = allowed_vars[0]
    top[v0] = max_deg
    terms[tuple(top)] = (terms.get(tuple(top), 0) + rng.randrange(1, p)) % p
    f = mvpoly.MPoly(terms, nvars, p)
    val = f.evaluate(root)
    const_key = (0,) * nvars
    new_const = (f.terms.get(const_key, 0) - val) % p
    new_terms = dict(f.terms)
    if new_const == 0:
        new_terms.pop(const_key, None)
    else:
        new_terms[const_key] = new_const
    f2 = mvpoly.MPoly(new_terms, nvars, p)
    assert f2.evaluate(root) == 0
    return f2


def degree_profile_null_system(fb_size, p, rng, s3_degree=4):
    nvars = 2
    root = (rng.randrange(p), rng.randrange(p))
    f0 = _random_poly_with_root(nvars, p, root, s3_degree, nterms=8, rng=rng, allowed_vars=[0, 1])
    f1 = _random_poly_with_root(nvars, p, root, fb_size, nterms=4, rng=rng, allowed_vars=[0])
    f2 = _random_poly_with_root(nvars, p, root, fb_size, nterms=4, rng=rng, allowed_vars=[1])
    return [f0, f1, f2], root


def degree_profile_null_meters(fb_size, p, rng, gb_budget, macaulay_cap, s3_degree=4):
    gens, root = degree_profile_null_system(fb_size, p, rng, s3_degree=s3_degree)
    G, gb_stats = groebner.buchberger(
        gens, p, 2,
        max_pairs=gb_budget.get("max_pairs", 20000),
        max_degree=gb_budget.get("max_degree", 60),
        wall_seconds=gb_budget.get("wall_seconds", 60.0),
    )
    ff = macaulay.first_fall_scan(gens, 2, p, max_extra_degrees=macaulay_cap)
    return {
        "groebner_solving_degree_d_reg": gb_stats["max_spoly_degree"],
        "groebner_timed_out": gb_stats["timed_out"],
        "macaulay_rank_defect_at_first_fall": ff["defect"],
        "macaulay_first_fall_degree": ff["first_fall_degree"],
        "macaulay_observed": ff["observed"],
        "planted_root": root,
    }
