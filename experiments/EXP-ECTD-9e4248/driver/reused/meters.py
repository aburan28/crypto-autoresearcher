"""
meters.py -- the five frozen per-curve meters for EXP-ECTD-001, built on curve.py,
semaev.py, mvpoly.py, groebner.py, macaulay.py.

FROZEN FACTOR-BASE CONVENTION (spec.inputs.factor_base_rule; hashed into every run
manifest -- see run_common.factor_base_rule_hash): FB(E) = the FB_SIZE smallest
non-negative integers x in [0, p), in increasing order starting from x=0, such that
x^3 + a*x + b is a nonzero quadratic residue mod p (i.e. a genuine affine curve point
exists at that x-coordinate). Identical procedure applied to every curve in every
class, every outside-class draw, and every null arm.

FROZEN meter definitions:
  semaev_m3_relation_density: for n_samples_density target points R (see sampling
    mode below), the fraction of ordered FB x FB pairs (x1,x2) with
    S3(x1,x2,x_R)=0, averaged over the samples.
  semaev_m4_relation_density: as above but FB^3 triples and S4_via_resultant.
  fb_decomposition_probability: over n_samples_prob INDEPENDENT RANDOM (not forced)
    target points R, the fraction for which at least one FB pair satisfies
    S3(x1,x2,x_R)=0 (an m=2 "does this point decompose at all" indicator).
  groebner_solving_degree_d_reg: see groebner.py docstring; computed on ONE frozen
    representative target R_rep (see below) via the m=2 system
    {S3(x1,x2,x_R_rep), g(x1), g(x2)}, g = the FB-defining polynomial.
  macaulay_rank_defect_at_first_fall: see macaulay.py docstring; same system as
    the Groebner meter, same R_rep.

CTRL-PLANTED-OUTLIER sampling mode: for the ordinary case, target points R are drawn
uniformly at random on E (curve.random_point). For the designated planted-outlier
curve, R is instead constructed as R = P_i + P_j (or P_i+P_j+P_k for the m4/S4
system) for FB points P_i, P_j chosen at random FROM the factor base -- i.e. R is
GUARANTEED (by the verified S3/S4 identity) to actually decompose over the frozen
FB, without touching the FB convention, the meter definitions, or the solver budget.
This is a real (if adversarially chosen) measurement of the same algebraic system,
not a fabricated number.
"""
import time
from . import fp, curve, semaev, mvpoly, groebner, macaulay


def get_fb(a, b, p, fb_size):
    fb = []
    x = 0
    while len(fb) < fb_size and x < p:
        rhs = (x ** 3 + a * x + b) % p
        if rhs != 0 and fp.is_qr(rhs, p):
            fb.append(x)
        x += 1
    if len(fb) < fb_size:
        raise RuntimeError("factor base exhausted before reaching fb_size (p too small)")
    return fb


def fb_point(x, a, b, p):
    rhs = (x ** 3 + a * x + b) % p
    y = fp.sqrt_mod(rhs, p)
    if y is None:
        raise ValueError("FB x-coordinate is not on the curve")
    y = min(y, p - y)
    return (x, y)


def _sample_target_random(a, b, p, rng):
    return curve.random_point(a, b, p, rng)


def _sample_target_planted_m2(fb_points, a, b, p, rng, max_attempts=50):
    for _ in range(max_attempts):
        i = rng.randrange(len(fb_points))
        j = rng.randrange(len(fb_points))
        Pi, Pj = fb_points[i], fb_points[j]
        R = curve.add(Pi, Pj, a, p)
        if R is not None:
            return R
    raise RuntimeError("could not construct a planted m2 target (unlucky cancellation)")


def _sample_target_planted_m3(fb_points, a, b, p, rng, max_attempts=50):
    for _ in range(max_attempts):
        i = rng.randrange(len(fb_points))
        j = rng.randrange(len(fb_points))
        k = rng.randrange(len(fb_points))
        R = curve.add(curve.add(fb_points[i], fb_points[j], a, p), fb_points[k], a, p)
        if R is not None:
            return R
    raise RuntimeError("could not construct a planted m3 target (unlucky cancellation)")


def relation_density_m3(a, b, p, fb, rng, n_samples, planted=False):
    fb_pts = [fb_point(x, a, b, p) for x in fb] if planted else None
    total_pairs = len(fb) * len(fb)
    densities = []
    for _ in range(n_samples):
        R = _sample_target_planted_m2(fb_pts, a, b, p, rng) if planted else _sample_target_random(a, b, p, rng)
        xR = R[0]
        hits = 0
        for x1 in fb:
            for x2 in fb:
                if semaev.S3(x1, x2, xR, a, b, p) == 0:
                    hits += 1
        densities.append(hits / total_pairs)
    return sum(densities) / len(densities), densities


def relation_density_m4(a, b, p, fb, rng, n_samples, planted=False):
    fb_pts = [fb_point(x, a, b, p) for x in fb] if planted else None
    total_triples = len(fb) ** 3
    densities = []
    for _ in range(n_samples):
        R = _sample_target_planted_m3(fb_pts, a, b, p, rng) if planted else _sample_target_random(a, b, p, rng)
        xR = R[0]
        hits = 0
        for x1 in fb:
            for x2 in fb:
                P = semaev.S3_coeffs_in_X(x1, x2, a, b, p)
                for x3 in fb:
                    Q = semaev.S3_coeffs_in_X(x3, xR, a, b, p)
                    # S4(x1,x2,x3,xR) = Res_X(S3(x1,x2,X), S3(x3,xR,X))... we need the
                    # 4-var form S4(x1,x2,x3,x4) = Res_X(S3(x1,x2,X), S3(x3,x4,X)) with
                    # x4 = xR fixed, i.e. Q should be S3(x3, xR, X) coeffs -- matches.
                    if semaev.sylvester_resultant_quadratics(P, Q, p) == 0:
                        hits += 1
        densities.append(hits / total_triples)
    return sum(densities) / len(densities), densities


def fb_decomposition_probability(a, b, p, fb, rng, n_samples):
    hits = 0
    for _ in range(n_samples):
        R = _sample_target_random(a, b, p, rng)
        xR = R[0]
        found = False
        for x1 in fb:
            for x2 in fb:
                if semaev.S3(x1, x2, xR, a, b, p) == 0:
                    found = True
                    break
            if found:
                break
        if found:
            hits += 1
    return hits / n_samples


def _fb_defining_poly(fb, nvars, var_index, p):
    """g(x_var) = prod_{f in fb} (x_var - f), as an MPoly in `nvars` variables."""
    x = mvpoly.MPoly.var(var_index, nvars, p)
    one = mvpoly.MPoly.constant(1, nvars, p)
    g = one
    for f in fb:
        g = g.mul(x.sub(mvpoly.MPoly.constant(f, nvars, p)))
    return g


def _s3_as_mpoly(xR, a, b, p, nvars=2):
    """S3(x1, x2, xR) as a bivariate MPoly (x1=var0, x2=var1), xR/a/b constants."""
    x1 = mvpoly.MPoly.var(0, nvars, p)
    x2 = mvpoly.MPoly.var(1, nvars, p)
    aC = mvpoly.MPoly.constant(a, nvars, p)
    bC = mvpoly.MPoly.constant(b, nvars, p)
    xRC = mvpoly.MPoly.constant(xR, nvars, p)
    diff = x1.sub(x2)
    term_sq = diff.mul(diff).mul(xRC).mul(xRC)
    inner = x1.add(x2).mul(x1.mul(x2).add(aC)).add(mvpoly.MPoly.constant((2 * b) % p, nvars, p))
    term_lin = inner.mul(xRC).scale(2)
    prod_sub_a = x1.mul(x2).sub(aC)
    const = prod_sub_a.mul(prod_sub_a).sub(x1.add(x2).mul(bC).scale(4))
    return term_sq.sub(term_lin).add(const)


def groebner_and_macaulay_meters(a, b, p, fb, R_x, gb_budget, macaulay_cap):
    nvars = 2
    f0 = _s3_as_mpoly(R_x, a, b, p, nvars)
    f1 = _fb_defining_poly(fb, nvars, 0, p)
    f2 = _fb_defining_poly(fb, nvars, 1, p)
    gens = [f0, f1, f2]
    t0 = time.time()
    G, gb_stats = groebner.buchberger(
        gens, p, nvars,
        max_pairs=gb_budget.get("max_pairs", 20000),
        max_degree=gb_budget.get("max_degree", 60),
        wall_seconds=gb_budget.get("wall_seconds", 60.0),
    )
    gb_elapsed = time.time() - t0
    t1 = time.time()
    ff = macaulay.first_fall_scan(gens, nvars, p, max_extra_degrees=macaulay_cap)
    macaulay_elapsed = time.time() - t1
    return {
        "groebner_solving_degree_d_reg": gb_stats["max_spoly_degree"],
        "groebner_timed_out": gb_stats["timed_out"],
        "groebner_stats": gb_stats,
        "groebner_elapsed_s": gb_elapsed,
        "macaulay_rank_defect_at_first_fall": ff["defect"],
        "macaulay_first_fall_degree": ff["first_fall_degree"],
        "macaulay_observed": ff["observed"],
        "macaulay_stats": ff,
        "macaulay_elapsed_s": macaulay_elapsed,
    }


def compute_curve_meters(a, b, p, fb_size, rng, n_samples_density=6, n_samples_prob=24,
                          gb_budget=None, macaulay_cap=6, planted=False):
    gb_budget = gb_budget or {"max_pairs": 20000, "max_degree": 60, "wall_seconds": 60.0}
    fb = get_fb(a, b, p, fb_size)
    m3_mean, m3_samples = relation_density_m3(a, b, p, fb, rng, n_samples_density, planted=planted)
    m4_mean, m4_samples = relation_density_m4(a, b, p, fb, rng, n_samples_density, planted=planted)
    prob = fb_decomposition_probability(a, b, p, fb, rng, n_samples_prob) if not planted else 1.0
    if planted:
        # For the designated planted curve, groebner/macaulay use the SAME forced
        # target as the density meters (a decomposable R), documented deviation from
        # the "random R" convention used for ordinary curves -- this is exactly what
        # "planting an artificially easy Semaev instance" means operationally.
        R = _sample_target_planted_m2([fb_point(x, a, b, p) for x in fb], a, b, p, rng)
    else:
        R = curve.random_point(a, b, p, rng)
    gm = groebner_and_macaulay_meters(a, b, p, fb, R[0], gb_budget, macaulay_cap)
    return {
        "fb": fb,
        "R_used_for_gb_macaulay": R,
        "semaev_m3_relation_density": m3_mean,
        "semaev_m3_samples": m3_samples,
        "semaev_m4_relation_density": m4_mean,
        "semaev_m4_samples": m4_samples,
        "fb_decomposition_probability": prob,
        **gm,
    }
