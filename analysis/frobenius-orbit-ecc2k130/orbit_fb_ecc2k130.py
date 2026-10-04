"""Frobenius orbit-union factor base at the true ECC2K-130 parameters.

A pre-compute audit in the sense of docs/inventor-protocol.md section 8:
every number is computed here, nothing is run against the challenge.

Four parts:
  A  field + curve + exact group order, all re-derived (no recall, no SEA)
  B  the COMPLETE lattice of Frobenius-stable F_2-subspaces of F_2^131,
     which decides whether a *linear* stable factor base exists at all
  C  an orbit-union factor base built at real scale, with pi(S) = S and the
     orbit sizes verified on real field elements
  D  the one gain the union earns, verified on the real curve, and the
     charged cost sweep against the recorded rho baseline

Run:  /opt/conda-sage/bin/sage -python orbit_fb_ecc2k130.py --json results.json
"""
import argparse
import json
import math
from itertools import combinations

from sage.all import (GF, PolynomialRing, VectorSpace, EllipticCurve, Integer,
                      factor, is_prime, vector)

N_DEG = 131
RHO_LOG2 = 60.9          # KN-LIT-096: authors' ESTIMATE of required work
RHO_ACTUAL_LOG2 = 58.3   # KN-LIT-661e97: reached by the real public effort


def part_a():
    """Field, curve, exact order via the Koblitz trace recursion."""
    out = {}
    R = PolynomialRing(GF(2), 'z')
    z = R.gen()
    red = z**131 + z**13 + z**2 + z + 1
    out["reduction_polynomial"] = str(red)
    out["reduction_polynomial_irreducible"] = bool(red.is_irreducible())

    K = GF(2**131, name='a', modulus=red)
    out["field_cardinality_is_2_131"] = bool(K.cardinality() == 2**131)

    # base curve over F_2; trace recursion gives the order over F_2^131 exactly
    E2 = EllipticCurve(GF(2), [1, 0, 0, 0, 1])       # y^2 + xy = x^3 + 1
    order_F2 = E2.order()
    t1 = Integer(2) + 1 - order_F2
    out["curve"] = "y^2 + x*y = x^3 + 1"
    out["order_over_F2"] = int(order_F2)
    out["trace_t1"] = int(t1)

    t_prev2, t_prev1 = Integer(2), t1
    for _ in range(2, N_DEG + 1):
        t_prev2, t_prev1 = t_prev1, t1 * t_prev1 - 2 * t_prev2
    t_n = t_prev1
    N = Integer(2)**N_DEG + 1 - t_n
    out["trace_t131"] = int(t_n)
    out["group_order_N"] = str(N)
    out["hasse_bound_ok"] = bool(abs(t_n) <= 2 * Integer(2)**(Integer(N_DEG) / 2))

    fac = factor(N)
    out["order_factorisation"] = str(fac)
    r = max(p for (p, e) in fac)
    out["prime_subgroup_r"] = str(r)
    out["r_is_prime"] = bool(is_prime(r))
    out["r_log2"] = float(r.log(2).n())
    out["N_equals_4r"] = bool(N == 4 * r)

    # independent confirmation: the computed order must annihilate real points
    EK = EllipticCurve(K, [1, 0, 0, 0, 1])
    out["order_annihilates_random_points"] = [
        bool((N * EK.random_point()).is_zero()) for _ in range(3)]
    return out, K, EK, N, r


def part_b():
    """Every Frobenius-stable F_2-subspace of F_2^131, by submodule counting.

    F_2^131 with sigma is the F_2[X]-module F_2[X]/(X^131 - 1) (normal basis);
    its submodules correspond one-for-one to the monic divisors of X^131 - 1.
    """
    out = {}
    R = PolynomialRing(GF(2), 'z')
    X = R.gen()
    f = X**131 - 1
    fac = list(f.factor())
    out["X131_minus_1_factor_degrees"] = sorted(int(g.degree()) for g, _ in fac)
    out["X131_minus_1_num_irreducible_factors"] = len(fac)
    assert all(e == 1 for _, e in fac), "X^131-1 must be squarefree"

    ord_131_2 = next(d for d in sorted(Integer(130).divisors())
                     if pow(2, d, 131) == 1)
    out["ord_131_of_2"] = int(ord_131_2)

    dims = []
    for k in range(len(fac) + 1):
        for sub in combinations(fac, k):
            deg = sum(int(g.degree()) for g, _ in sub)
            dims.append(N_DEG - deg)
    out["num_frobenius_stable_subspaces"] = len(dims)
    out["frobenius_stable_subspace_dims"] = sorted(dims)
    band = [d for d in sorted(dims) if 2 <= d <= N_DEG - 2]
    out["stable_dims_in_index_calculus_band"] = band
    out["linear_stable_factor_base_exists"] = bool(band)
    return out


def part_c(K, l_prime=36):
    """Build S = union_j sigma^j(V') at real scale; verify pi(S) = S."""
    out = {"l_prime": l_prime}
    V = VectorSpace(GF(2), N_DEG)

    def to_vec(x):
        return vector(GF(2), x._vector_())

    def from_vec(v):
        return K(list(v))

    def frob(x):
        return x * x

    basis = []
    while len(basis) < l_prime:
        cand = K.random_element()
        W = V.subspace([to_vec(b) for b in basis] + [to_vec(cand)])
        if W.dimension() == len(basis) + 1:
            basis.append(cand)
    Vp = V.subspace([to_vec(b) for b in basis])
    out["dim_Vprime"] = int(Vp.dimension())

    def shift(S_sub, j):
        bs = []
        for b in S_sub.basis():
            x = from_vec(b)
            for _ in range(j):
                x = frob(x)
            bs.append(to_vec(x))
        return V.subspace(bs)

    # sigma^131 = identity on F_2^131
    ok = []
    for _ in range(5):
        x = K.random_element()
        y = x
        for _ in range(N_DEG):
            y = frob(y)
        ok.append(bool(y == x))
    out["sigma_131_is_identity"] = ok

    img = V.subspace([to_vec(frob(from_vec(b))) for b in Vp.basis()])
    out["sigma_of_Vprime_equals_shift_1"] = bool(img == shift(Vp, 1))
    out["sigma_131_of_Vprime_equals_Vprime"] = bool(shift(Vp, N_DEG) == Vp)

    # 131 prime => every element outside F_2 has orbit of size exactly 131
    sizes = []
    for _ in range(5):
        x = K.random_element()
        seen, y = set(), x
        for _ in range(N_DEG):
            seen.add(y)
            y = frob(y)
        sizes.append(len(seen))
    out["sampled_orbit_sizes"] = sizes

    inters = []
    for j in range(1, 6):
        inters.append({"j": j,
                       "intersection_dim": int(Vp.intersection(shift(Vp, j)).dimension())})
    out["pairwise_intersection_dims"] = inters
    if max(i["intersection_dim"] for i in inters) == 0:
        out["log2_S_size"] = round(math.log2(N_DEG) + l_prime, 2)
    else:
        out["log2_S_size"] = None
    return out


def part_d(EK, r):
    """The orbit gain on the real curve, then the charged cost sweep."""
    out = {}
    P = EK.random_point() * 4
    while P.is_zero() or not (r * P).is_zero():
        P = EK.random_point() * 4
    out["P_has_exact_order_r"] = True

    def frob_pt(Q):
        return Q if Q.is_zero() else EK(Q[0]**2, Q[1]**2)

    orbit, Q = [], P
    for _ in range(N_DEG):
        orbit.append(Q)
        Q = frob_pt(Q)
    out["frobenius_orbit_size_on_curve"] = len(set(orbit))
    out["sigma_131_fixes_P"] = bool(Q == P)

    # sigma acts on <P> as a scalar mu with mu^2 + mu + 2 = 0 (mod r)
    Rz = PolynomialRing(GF(r), 'u')
    u = Rz.gen()
    mu = None
    for rt, _ in (u**2 + u + 2).roots():
        if Integer(rt) * P == frob_pt(P):
            mu = Integer(rt)
            break
    out["mu"] = str(mu) if mu is not None else None
    if mu is not None:
        out["ord_r_mu"] = int(GF(r)(mu).multiplicative_order())
        out["ord_r_mu_equals_131"] = out["ord_r_mu"] == N_DEG
        out["distinct_scalar_powers"] = len(
            {pow(int(mu), j, int(r)) for j in range(N_DEG)})
    out["orbit_gain_log2"] = round(math.log2(N_DEG), 2)

    # ---- charged cost sweep -------------------------------------------
    # Generous to the attack at every step: balanced factor base, the full
    # factor-n orbit collapse on relations AND n^2 on linear algebra, and
    # ONE operation charged per decomposition solve.
    sweep = []
    for m in range(2, 7):
        log2_FB = N_DEG / m
        lp = log2_FB - math.log2(N_DEG)
        if lp < 1:
            continue
        log2_mfact = math.log2(math.factorial(m))
        # P[random point splits into m elements of S] = |S|^m / (m! N)
        log2_attempts_per_rel = -(m * log2_FB - N_DEG - log2_mfact)
        log2_rels = log2_FB - math.log2(N_DEG)   # one relation -> its orbit
        log2_solves = log2_rels + log2_attempts_per_rel
        log2_linalg = 2 * log2_rels              # sparse, orbit-reduced
        floor = math.log2(2**log2_solves + 2**log2_linalg)
        sweep.append({
            "m": m,
            "l_prime": round(lp, 2),
            "log2_FB": round(log2_FB, 2),
            "weil_descent_F2_vars": round(m * lp, 1),
            "semaev_polynomial": "S_%d" % (m + 1),
            "log2_attempts_per_relation": round(log2_attempts_per_rel, 2),
            "log2_relations_needed": round(log2_rels, 2),
            "log2_total_solves": round(log2_solves, 2),
            "log2_linear_algebra": round(log2_linalg, 2),
            "log2_floor_one_op_per_solve": round(floor, 2),
            "floor_under_rho": bool(floor < RHO_LOG2),
            "log2_budget_per_solve_for_rho_parity": round(RHO_LOG2 - log2_solves, 2),
        })
    out["rho_baseline_log2_estimated"] = RHO_LOG2
    out["rho_reached_by_public_effort_log2"] = RHO_ACTUAL_LOG2
    out["cost_sweep"] = sweep
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    ap.add_argument("--l-prime", type=int, default=36)
    args = ap.parse_args()

    a, K, EK, N, r = part_a()
    results = {
        "target": "ECC2K-130 (public Certicom challenge curve)",
        "note": "Pre-compute audit. Every number computed here; nothing run "
                "against the challenge. Not evidence; no RUN-* exists.",
        "A_field_and_curve": a,
        "B_frobenius_stable_subspaces": part_b(),
        "C_orbit_union_factor_base": part_c(K, args.l_prime),
        "D_orbit_gain_and_cost": part_d(EK, r),
    }
    text = json.dumps(results, indent=2)
    print(text)
    if args.json:
        with open(args.json, "w") as fh:
            fh.write(text + "\n")


if __name__ == "__main__":
    main()
