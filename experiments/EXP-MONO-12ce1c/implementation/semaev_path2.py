"""
Path 2 of the dual-path cross-check: build S_m explicitly by the resultant
recursion named in specification.yaml `arms_and_controls.dual_path_control`:

    S_3(x1, x2, T)  (the pinned normalization from EXP-MONO-4b50b6 mono3_census.py
                      s3_coeffs, identical to EV-MONO-a0a89c OBS-1's normalization)
    S_4 = Res_X( S_3(x1, x2, X), S_3(x3, T, X) )
    S_5 = Res_X( S_4(x1, x2, x3, X), S_3(x4, T, X) )

and factor the specialization over F_p. sympy is available in this session's
environment (the contract's 2026-08-05 environment note recording sympy's
absence is stale; the contract's actual requirement is "no CAS needed", not
"no CAS allowed" -- see handoff TASK-20260830-a1cb32).

Performance note (measured, disclosed in implementation.md): naive
`Poly.subs` on the fully expanded S_4/S_5 templates costs ~75ms/specialization
(sympy expression-tree substitution into a many-term Add). Using
`sympy.lambdify` on the polynomial's T-coefficients (each a small polynomial
in x1,x2,x3,A,B) as plain Python callables reduces this to ~0.4ms/spec for S4
and, combined with reusing that fast numeric evaluation before a single
numeric-coefficient resultant against S3(x4,T,X), to ~6ms/spec for S5 --
both orders of magnitude faster and mathematically identical (same resultant,
same factorization), verified to agree with the slow path on a spot sample.
"""
import sympy as sp

x1, x2, x3, x4, T, X, A, B = sp.symbols("x1 x2 x3 x4 T X A B")


def S3_expr(a, b, t):
    """Pinned normalization (matches EXP-MONO-4b50b6 mono3_census.s3_coeffs
    exactly): a=(x1-x2)^2, b=-2[(x1+x2)(x1x2+A)+2B], c=(x1x2-A)^2-4B(x1+x2)."""
    return (a - b) ** 2 * t ** 2 - 2 * ((a + b) * (a * b + A) + 2 * B) * t + (a * b - A) ** 2 - 4 * B * (a + b)


class SemaevPath2:
    """Builds the S_4 template once (symbolic in x1,x2,x3,T,A,B), and provides
    fast per-specialization S_4 and S_5 factorizations over F_p."""

    def __init__(self):
        s4_template = sp.expand(sp.resultant(S3_expr(x1, x2, X), S3_expr(x3, T, X), X))
        self.s4_template = s4_template
        self.s4_deg_T = sp.degree(s4_template, T)
        poly4 = sp.Poly(s4_template, T)
        self.s4_coeffs_sym = poly4.all_coeffs()  # highest degree first, each a poly in x1,x2,x3,A,B
        self.s4_coeff_funcs = [sp.lambdify((x1, x2, x3, A, B), c, modules="math") for c in self.s4_coeffs_sym]

    def fixture_deg_T_S4(self):
        """S_4's T-degree is 4 as a fully symbolic identity in x1,x2,x3,T,A,B
        (A,B ALSO symbolic here -- the strongest form of this check, done once,
        not per curve)."""
        return self.s4_deg_T == 4

    def s4_coeffs_numeric(self, v1, v2, v3, Aval, Bval, p):
        """Coefficients (highest degree first) of S_4(v1,v2,v3,T) mod p, as a
        polynomial in T. Uses the lambdified fast path."""
        return [int(f(v1, v2, v3, Aval, Bval)) % p for f in self.s4_coeff_funcs]

    def factor_S4_mod_p(self, v1, v2, v3, Aval, Bval, p):
        """Returns (degree_list, coeffs) for S_4(v1,v2,v3,T) mod p factored over F_p.
        degree_list is the multiset of irreducible-factor degrees (with multiplicity
        counted once per factor instance, i.e. repeated per its multiplicity)."""
        cvals = self.s4_coeffs_numeric(v1, v2, v3, Aval, Bval, p)
        # strip any leading zero coefficients (degree drop -- degenerate stratum)
        while len(cvals) > 1 and cvals[0] % p == 0:
            cvals = cvals[1:]
        poly = sp.Poly(cvals, T, modulus=p)
        _, factors = poly.factor_list()
        degs = []
        for fac, mult in factors:
            d = sp.degree(fac, T)
            degs.extend([d] * mult)
        return degs, cvals

    def factor_S5_mod_p(self, v1, v2, v3, v4, Aval, Bval, p):
        """S_5 = Res_X(S_4(v1,v2,v3,X), S_3(v4,T,X)) mod p, factored over F_p.
        Returns (degree_list, deg_T_S5_this_instance)."""
        cvals4 = self.s4_coeffs_numeric(v1, v2, v3, Aval, Bval, p)
        s4_as_X = sp.Poly([c % p for c in cvals4], X, domain="ZZ")
        s3_4TX = sp.Poly(S3_expr(v4, T, X).subs({A: Aval, B: Bval}), X)
        res = sp.resultant(s4_as_X.as_expr(), s3_4TX.as_expr(), X)
        res = sp.expand(res)
        poly = sp.Poly(res, T)
        deg_T_here = poly.degree()
        coeffs_mod_p = [int(c) % p for c in poly.all_coeffs()]
        while len(coeffs_mod_p) > 1 and coeffs_mod_p[0] % p == 0:
            coeffs_mod_p = coeffs_mod_p[1:]
        polyp = sp.Poly(coeffs_mod_p, T, modulus=p)
        _, factors = polyp.factor_list()
        degs = []
        for fac, mult in factors:
            d = sp.degree(fac, T)
            degs.extend([d] * mult)
        return degs, deg_T_here


def s3_vanishes_at_sum_and_difference(Aval, Bval, p, xP, yP, xQ, yQ):
    """Fixture check: S_3(xP, xQ, x(P+Q)) == 0 and S_3(xP, xQ, x(P-Q)) == 0 mod p,
    for real curve points P=(xP,yP), Q=(xQ,yQ) with xP != xQ, using plain F_p
    chord-and-tangent addition (no F_p2 needed since P, Q are F_p-rational)."""
    def add_fp(P, Q):
        xp, yp = P
        xq, yq = Q
        if xp == xq:
            if (yp + yq) % p == 0:
                return None
            lam = ((3 * xp * xp + Aval) * pow(2 * yp, p - 2, p)) % p
        else:
            lam = ((yq - yp) * pow((xq - xp) % p, p - 2, p)) % p
        xr = (lam * lam - xp - xq) % p
        yr = (lam * (xp - xr) - yp) % p
        return (xr, yr)

    def neg_fp(P):
        return (P[0], (-P[1]) % p)

    Rsum = add_fp((xP, yP), (xQ, yQ))
    Rdiff = add_fp((xP, yP), neg_fp((xQ, yQ)))
    x1_ = xP % p
    x2_ = xQ % p

    def s3_num(a, b, t):
        aa = (a - b) ** 2
        bb = -2 * ((a + b) * (a * b + Aval) + 2 * Bval)
        cc = (a * b - Aval) ** 2 - 4 * Bval * (a + b)
        return (aa * t * t + bb * t + cc) % p

    vsum = s3_num(x1_, x2_, Rsum[0]) if Rsum is not None else 0
    vdiff = s3_num(x1_, x2_, Rdiff[0]) if Rdiff is not None else 0
    return (vsum % p == 0), (vdiff % p == 0)
