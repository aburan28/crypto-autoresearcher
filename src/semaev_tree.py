"""
E1.1 — Semaev 2015 chained S_3 tree system over F_{2^n}, with Weil descent to F_2.

Per Semaev 2015 §3 (ePrint 2015/310):
  Curve: Y^2 + XY = X^3 + A*X^2 + B  over F_q = F_{2^n}
  S_3(x_1, x_2, x_3) = (x_1*x_2 + x_1*x_3 + x_2*x_3)^2 + x_1*x_2*x_3 + B

  Chained system (5) for decomposition R = P_1 + ... + P_t:
    S_3(u_1,        x_1, x_2     ) = 0
    S_3(u_i,        u_{i+1}, x_{i+2}) = 0,  1 ≤ i ≤ t-3
    S_3(u_{t-2},    x_t, R_X     ) = 0
  with x_i ∈ V (subspace) and u_i ∈ F_q.

  Weil descent (§4.5): pick basis {1, α, α^2, ..., α^{n-1}} of F_{2^n}/F_2.
    Write each u_i and x_j in coordinates over F_2.
    Equating coefficients of each α^k in each S_3 equation gives n Boolean
    equations per S_3, for a total of n*(t-1) equations in n*(t-2) + k*t
    unknowns (where k = ⌈n/m⌉ = dim V).

  This module generates the chained system, the Weil-descended Boolean system,
  and provides solver hooks.
"""

from sage.all import (
    GF, PolynomialRing, EllipticCurve, vector, Matrix, ZZ, Integer,
    BooleanPolynomialRing, gcd
)
import itertools


def build_field_and_curve(n, A=None, B=None, seed=None):
    """Return (Fq, E, alpha) where Fq = F_{2^n}, E is the curve, alpha generates Fq/F_2."""
    Fq = GF(2**n, name='alpha')
    alpha = Fq.gen()
    if A is None:
        A = Fq(1)  # Semaev 2015 uses a_2 = A as nonzero
    else:
        A = Fq(A)
    if B is None:
        # Default: B = alpha (a primitive element) so curve is non-singular
        B = alpha
    else:
        B = Fq(B)
    # Curve y^2 + xy = x^3 + A x^2 + B in char 2
    # Standard Weierstrass: a1=1, a2=A, a3=0, a4=0, a6=B
    E = EllipticCurve(Fq, [1, A, 0, 0, B])
    return Fq, E, alpha, A, B


def S3_char2(x1, x2, x3, B):
    """S_3 over F_{2^n}: (x1*x2 + x1*x3 + x2*x3)^2 + x1*x2*x3 + B."""
    return (x1*x2 + x1*x3 + x2*x3)**2 + x1*x2*x3 + B


def build_chained_system_symbolic(t, Fq, B_curve, R_X):
    """
    Build the chained S_3 system over a polynomial ring with variables u_1..u_{t-2}, x_1..x_t,
    over Fq. The R_X is treated as a constant from Fq.

    Returns (R_poly_ring, list_of_S3_polynomials, var_names).
    """
    if t < 2:
        raise ValueError("t must be ≥ 2")
    if t == 2:
        # Special case: just S_3(x_1, x_2, R_X) = 0
        R = PolynomialRing(Fq, ['x1', 'x2'], order='degrevlex')
        x1, x2 = R.gens()
        return R, [S3_char2(R(x1), R(x2), R(R_X), R(B_curve))], ['x1', 'x2']

    n_u = t - 2
    n_x = t
    var_names = [f'u{i+1}' for i in range(n_u)] + [f'x{j+1}' for j in range(n_x)]
    R = PolynomialRing(Fq, var_names, order='degrevlex')
    gens = R.gens()
    us = gens[:n_u]
    xs = gens[n_u:]

    polys = []
    # S_3(u_1, x_1, x_2) = 0
    polys.append(S3_char2(us[0], xs[0], xs[1], R(B_curve)))
    # S_3(u_i, u_{i+1}, x_{i+2}) = 0  for 1 ≤ i ≤ t-3
    for i in range(t - 3):
        polys.append(S3_char2(us[i], us[i+1], xs[i+2], R(B_curve)))
    # S_3(u_{t-2}, x_t, R_X) = 0
    polys.append(S3_char2(us[-1], xs[-1], R(R_X), R(B_curve)))

    return R, polys, var_names


def weil_descend_to_F2(polys, n, k, alpha, R_high):
    """
    Apply Weil descent: each Fq variable v becomes a sum sum_{j} v_j * alpha^j over F_2,
    where v ranges over its allowed support.
      - For u-variables: full F_q (j ∈ {0, ..., n-1})
      - For x-variables: restricted to V = span_F2(1, alpha, ..., alpha^{k-1})
        so j ∈ {0, ..., k-1}

    Returns (R_boolean, descended_polys) where R_boolean is a BooleanPolynomialRing
    in the F_2 unknowns and descended_polys is the list of n*len(polys) F_2 polynomials
    obtained by equating coefficients of each alpha^l for l = 0..n-1.
    """
    n_u_vars = sum(1 for v in R_high.variable_names() if v.startswith('u'))
    n_x_vars = sum(1 for v in R_high.variable_names() if v.startswith('x'))

    # Boolean ring with n*n_u + k*n_x unknowns
    bvar_names = []
    for i in range(n_u_vars):
        for j in range(n):
            bvar_names.append(f'u{i+1}_{j}')
    for i in range(n_x_vars):
        for j in range(k):
            bvar_names.append(f'x{i+1}_{j}')
    Bring = BooleanPolynomialRing(names=bvar_names, order='degrevlex')
    bvars = Bring.gens()

    # Substitution map: each Fq var → sum_j b_{var,j} * alpha^j
    # Build a polynomial ring over Fq containing the Boolean vars as Fq-variables
    # (we'll evaluate after substitution)
    Fq = R_high.base_ring()
    alpha_fq = Fq.gen()

    # Symbolic poly ring with all the boolean unknowns as variables over Fq
    Rsubs = PolynomialRing(Fq, bvar_names, order='degrevlex')
    Rsubs_gens = Rsubs.gens()

    # Map: each u_i → sum_j u_{i,j} * alpha^j, x_i → sum_{j<k} x_{i,j} * alpha^j
    sub_map = {}
    idx = 0
    for i in range(n_u_vars):
        s = Rsubs.zero()
        for j in range(n):
            s = s + Rsubs_gens[idx] * Rsubs(alpha_fq**j)
            idx += 1
        sub_map[R_high.gens()[i]] = s
    for i in range(n_x_vars):
        s = Rsubs.zero()
        for j in range(k):
            s = s + Rsubs_gens[idx] * Rsubs(alpha_fq**j)
            idx += 1
        sub_map[R_high.gens()[n_u_vars + i]] = s

    # Substitute into each polynomial
    descended = []
    for p in polys:
        # Convert p to Rsubs by substituting each variable
        p_sub = _substitute_poly(p, sub_map, Rsubs)
        # Now p_sub ∈ Rsubs is a polynomial in bvar_names with coefficients in Fq.
        # Extract coefficient of each alpha^l (for l = 0..n-1) — these are F_2 polynomials.
        # To do this: collect all coefficients (in Fq) of each monomial in bvars, and
        # express each Fq coefficient as a polynomial in alpha.
        coeff_dict = p_sub.dict()  # exponent tuple → Fq element
        # For each l = 0..n-1, build the F_2 polynomial whose monomials are the bvar monomials
        # weighted by the alpha^l coefficient of each Fq coefficient.
        for l in range(n):
            bpoly = Bring.zero()
            for expo, c in coeff_dict.items():
                # c ∈ Fq, get coefficient of alpha^l in c
                c_vec = c._vector_()  # Fq → F_2^n
                c_l = c_vec[l]
                if c_l == 0:
                    continue
                # Build the bvar monomial. But we're in F_2[bvars]/(bvar^2 - bvar) so any
                # b^k with k ≥ 1 becomes b.
                bmon = Bring.one()
                for vi, ei in enumerate(expo):
                    if ei > 0:
                        bmon = bmon * bvars[vi]  # x^k = x in F_2
                bpoly = bpoly + bmon
            if bpoly != 0:
                descended.append(bpoly)
    return Bring, descended


def _substitute_poly(p, sub_map, target_ring):
    """Substitute generators of source ring with target-ring polynomials per sub_map."""
    result = target_ring.zero()
    for coeff, mon in zip(p.coefficients(), p.monomials()):
        # mon is a monomial in p's ring; expand using sub_map
        expanded = target_ring.one()
        for var, ei in zip(p.parent().gens(), mon.exponents()[0]):
            if ei > 0:
                expanded = expanded * (sub_map[var]**ei)
        result = result + target_ring(coeff) * expanded
    return result


def gen_random_R(E, P=None):
    """Pick a random point R = a*P + b*Q for some scalars a, b. For simplicity here just
    return a random point on E."""
    import random
    while True:
        try:
            R = E.random_point()
            if R != E(0, 1, 0):
                return R
        except Exception:
            continue


def gen_decomposable_R(E, t, V_subspace, max_attempts=200, rng=None):
    """Generate R that decomposes as sum of t points whose x-coords lie in V_subspace.
    V_subspace is a list of F_q elements forming an F_2-subspace of F_q.
    Returns (R, P_list) where P_list = [P_1, ..., P_t] with x(P_i) ∈ V_subspace
    and R = sum(P_list).

    rng: an optional random.Random instance. If None, uses the global random module.
    Pass a seeded rng for bit-identical reproducibility across runs.
    """
    if rng is None:
        import random
        rng = random
    Fq = E.base_field()
    # Find points on E with x-coord in V_subspace
    candidates = []
    for v in V_subspace:
        try:
            pts = E.lift_x(v, all=True)
            for P in pts:
                if P != E(0, 1, 0):
                    candidates.append(P)
        except (ValueError, ArithmeticError, Exception):
            continue
    if len(candidates) < t:
        raise ValueError(f"Only {len(candidates)} factor-base points found; need {t}")
    P_list = rng.sample(candidates, t)
    R = sum(P_list, E(0, 1, 0))
    return R, P_list


def make_V_subspace(Fq, alpha, k):
    """Return the F_2-subspace of F_q spanned by {1, alpha, alpha^2, ..., alpha^{k-1}}."""
    elements = []
    for bits in range(2**k):
        v = Fq.zero()
        for j in range(k):
            if (bits >> j) & 1:
                v += alpha**j
        elements.append(v)
    return elements


if __name__ == "__main__":
    print("=== Building Semaev tree, n=8, t=3 ===")
    n = 8
    t = 3
    k = (n + t - 1) // t  # ⌈n/t⌉
    Fq, E, alpha, A, B = build_field_and_curve(n)
    print(f"  Fq = F_{{2^{n}}}, |E(Fq)| = {E.cardinality()}")
    print(f"  Curve: Y^2 + XY = X^3 + {A}*X^2 + {B}")
    print(f"  m=t={t}, k=⌈n/m⌉={k}, dim V = {k}")

    R = gen_random_R(E)
    R_X = R[0]
    print(f"  Random R = {R}")
    print(f"  R_X = {R_X}")

    R_high, polys, vnames = build_chained_system_symbolic(t, Fq, B, R_X)
    print(f"\n  Chained system vars: {vnames}")
    print(f"  Number of S_3 polys: {len(polys)}")
    for i, p in enumerate(polys):
        print(f"    poly {i}: degree {p.degree()}, {len(p.monomials())} monomials")

    print(f"\n=== Weil-descending to F_2 ===")
    Bring, dpolys = weil_descend_to_F2(polys, n, k, alpha, R_high)
    print(f"  Boolean ring: {Bring.ngens()} variables")
    print(f"  Descended polys: {len(dpolys)} equations")
    print(f"  Degrees: {sorted({p.degree() for p in dpolys})}")
    print(f"  First few:")
    for p in dpolys[:3]:
        print(f"    {p}")
