"""
groebner.py -- from-scratch Buchberger Groebner-basis algorithm over F_p (grevlex),
with degree-of-computation tracking. No CAS dependency.

Operational definition of "groebner_solving_degree_d_reg" (frozen driver convention,
documented in MANIFEST.md, identical across every curve/class/null arm): the maximum
total degree of any S-polynomial constructed during the run of this Buchberger
implementation to compute a Groebner basis of the frozen Semaev system
{S3(x1,x2,x_R), g(x1), g(x2)} (m=2 decomposition, g = the factor-base defining
polynomial). This is a standard, well-defined proxy for the degree at which the
algorithm is forced to work (closely related to, but not claimed identical to, the
literature notion of degree of regularity), fixed once and applied uniformly.
"""
import time
from . import mvpoly


class SolverTimeout(Exception):
    pass


def s_poly(f, g, order, p, nvars):
    lm_f, lc_f = f.leading_term(order)
    lm_g, lc_g = g.leading_term(order)
    lcm = mvpoly.monomial_lcm(lm_f, lm_g)
    mono_f = mvpoly.monomial_div(lcm, lm_f)
    mono_g = mvpoly.monomial_div(lcm, lm_g)
    inv_f = pow(lc_f, p - 2, p)
    inv_g = pow(lc_g, p - 2, p)
    Sf = mvpoly.MPoly({mono_f: inv_f}, nvars, p).mul(f)
    Sg = mvpoly.MPoly({mono_g: inv_g}, nvars, p).mul(g)
    return Sf.sub(Sg)


def reduce_poly(h, G, order, p, nvars):
    remainder = mvpoly.MPoly.zero(nvars, p)
    work = h.copy()
    while not work.is_zero():
        lm = work.leading_monomial(order)
        lc = work.terms[lm]
        divided = False
        for g in G:
            if g.is_zero():
                continue
            lmg, lcg = g.leading_term(order)
            if mvpoly.monomial_divides(lmg, lm):
                factor_mono = mvpoly.monomial_div(lm, lmg)
                factor_coeff = (lc * pow(lcg, p - 2, p)) % p
                sub_poly = mvpoly.MPoly({factor_mono: factor_coeff}, nvars, p).mul(g)
                work = work.sub(sub_poly)
                divided = True
                break
        if not divided:
            remainder = remainder.add(mvpoly.MPoly({lm: lc}, nvars, p))
            new_terms = {m: c for m, c in work.terms.items() if m != lm}
            work = mvpoly.MPoly(new_terms, nvars, p)
    return remainder


def buchberger(generators, p, nvars, max_pairs=20000, max_degree=60, wall_seconds=60.0):
    """Returns (G, stats) where stats has 'max_spoly_degree' (the d_reg proxy),
    'pairs_processed', 'basis_size', 'timed_out' (bool)."""
    order = mvpoly.GrevlexOrder()
    t0 = time.time()
    G = [g.copy() for g in generators if not g.is_zero()]
    pairs = [(i, j) for i in range(len(G)) for j in range(i + 1, len(G))]
    max_deg_seen = max((g.total_degree() for g in G), default=0)
    pairs_processed = 0
    timed_out = False
    while pairs:
        if pairs_processed >= max_pairs:
            timed_out = True
            break
        if time.time() - t0 > wall_seconds:
            timed_out = True
            break
        i, j = pairs.pop(0)
        f, g = G[i], G[j]
        # Buchberger's first criterion: coprime leading monomials -> S-poly reduces to 0
        lm_f, _ = f.leading_term(order)
        lm_g, _ = g.leading_term(order)
        if all(a == 0 or b == 0 for a, b in zip(lm_f, lm_g)):
            pairs_processed += 1
            continue
        sp = s_poly(f, g, order, p, nvars)
        pairs_processed += 1
        if sp.is_zero():
            continue
        deg = sp.total_degree()
        if deg > max_deg_seen:
            max_deg_seen = deg
        if deg > max_degree:
            timed_out = True
            break
        r = reduce_poly(sp, G, order, p, nvars)
        if not r.is_zero():
            rdeg = r.total_degree()
            if rdeg > max_deg_seen:
                max_deg_seen = rdeg
            k = len(G)
            G.append(r)
            for idx in range(k):
                pairs.append((idx, k))
    stats = {
        "max_spoly_degree": max_deg_seen,
        "pairs_processed": pairs_processed,
        "basis_size": len(G),
        "timed_out": timed_out,
        "elapsed_s": time.time() - t0,
    }
    return G, stats
