# Independent Sage re-derivation for the FrobTrace Lean modules.
# Usage: sage frob_recheck.sage <repo-root>
import re, json, sys
ROOT = sys.argv[1]
F = ROOT + "/formal/CryptoResearch/FrobTrace/"
out = {}

qm = open(F + "QuotientMatrices.lean").read()
def lean_poly(s, R):
    X = R.gen()
    s = s.replace("^", "**")
    return R(sage_eval(s, locals={"X": X}))

CELLS = {11: 2, 13: 8, 19: 3}
for q, c in CELLS.items():
    k = GF(q); R = PolynomialRing(k, "X"); X = R.gen()
    m = X^5 + c*X^4 + 1
    cell = {}
    cell["modulus_irreducible"] = bool(m.is_irreducible())
    # Lean modulus text
    mm = re.search(r"def modulus%d : \(ZMod %d\)\[X\] := (.*)\n" % (q, q), qm).group(1)
    cell["lean_modulus_matches"] = lean_poly(mm, R) == m
    # matrix: columns = X^(q j) mod m, rows = coefficient i
    cols = [list((X^(q*j)) % m) for j in range(5)]
    M = matrix(k, 5, 5, lambda i, j: (cols[j] + [0]*5)[i])
    blk = re.search(r"def frobeniusMatrix%d : Matrix \(Fin 5\) \(Fin 5\) \(ZMod %d\) :=\s*!!\[(.*?)\]" % (q, q), qm, re.S).group(1)
    rows = [[int(t) for t in r.split(",")] for r in blk.replace("\n", " ").split(";")]
    ML = matrix(k, rows)
    cell["matrix_matches_sage"] = (M == ML)
    # division certificates
    divs_ok = True
    for j in range(1, 5):
        qt = re.search(r"def quotient%d_%d : \(ZMod %d\)\[X\] := (.*)\n" % (q, j, q), qm).group(1)
        rt = re.search(r"def remainder%d_%d : \(ZMod %d\)\[X\] := (.*)\n" % (q, j, q), qm).group(1)
        Q = lean_poly(qt, R); Rm = lean_poly(rt, R)
        divs_ok &= (Rm + m*Q == X^(q*j)) and Rm.degree() < 5
    cell["division_certificates_ok"] = bool(divs_ok)
    # kernels
    I5 = identity_matrix(k, 5)
    cell["M5_is_identity"] = (ML^5 == I5)
    cell["M_is_not_identity"] = (ML != I5)
    T = I5 + ML + ML^2 + ML^3 + ML^4
    cell["T_first_row"] = [int(x) for x in T.row(0)]
    cell["T_other_rows_zero"] = all(T.row(i) == 0 for i in range(1, 5))
    cell["rank_T"] = int(T.rank())
    cell["dim_ker_T"] = int(5 - T.rank())
    # direct trace: Tr of basis element z^j (field trace of F_{q^5}/F_q) equals T[0][j]
    K = GF(q^5, "z", modulus=m); z = K.gen()
    cell["T_row0_equals_field_trace"] = [int((z^j).trace()) for j in range(5)] == cell["T_first_row"]
    facs = [f for f, e in (X^5 - 1).factor() if f.degree() > 0 and f != X - 1]
    cell["nontrivial_factors"] = [str(f) for f in facs]
    kers = [(f(ML)).right_kernel() for f in facs]
    cell["factor_kernel_dims"] = [int(V.dimension()) for V in kers]
    S = sum(kers[1:], kers[0])
    cell["sum_dim"] = int(S.dimension())
    cell["direct"] = int(S.dimension()) == sum(V.dimension() for V in kers)
    cell["sum_equals_ker_T"] = S == T.right_kernel()
    fixed = (ML - I5).right_kernel()
    cell["fixed_space_dim"] = int(fixed.dimension())
    cell["fixed_space_is_constants"] = fixed == span([vector(k, [1, 0, 0, 0, 0])])
    cell["fixed_meets_kerT_trivially"] = (fixed.intersection(T.right_kernel())).dimension() == 0
    # proves-too-much: factor-kernel identity on a WRONG matrix (identity, zero, random)
    def factor_claim(Mx):
        ks = [(f(Mx)).right_kernel() for f in facs]
        Sx = sum(ks[1:], ks[0])
        Tx = I5 + Mx + Mx^2 + Mx^3 + Mx^4
        return bool(Sx == Tx.right_kernel())
    set_random_seed(20261023)
    Mr = random_matrix(k, 5, 5)
    cell["factor_sum_claim_holds_for_identity_matrix"] = factor_claim(I5)
    cell["factor_sum_claim_holds_for_zero_matrix"] = factor_claim(zero_matrix(k, 5))
    cell["factor_sum_claim_holds_for_random_matrix"] = factor_claim(Mr)
    Tr = I5 + Mr + Mr^2 + Mr^3 + Mr^4
    cell["random_matrix_kerT_dim"] = int(5 - Tr.rank())
    out["q%d" % q] = cell

# FactorKernel constants
k19 = GF(19); R19 = PolynomialRing(k19, "X"); X = R19.gen()
p19 = X^2 + 5*X + 1; q19 = X^2 + 15*X + 1; h19 = X^4 + X^3 + X^2 + X + 1
out["factor19"] = (p19*q19 == h19)
out["bezout19"] = ((11 + 2*X)*p19 + (9 + 17*X)*q19 == 1)
out["p19_q19_irreducible"] = [bool(p19.is_irreducible()), bool(q19.is_irreducible())]
k11 = GF(11); R11 = PolynomialRing(k11, "X"); X = R11.gen()
out["factor11"] = ((X + 2)*(X + 6)*(X + 7)*(X + 8) == X^4 + X^3 + X^2 + X + 1)
k13 = GF(13); R13 = PolynomialRing(k13, "X"); X = R13.gen()
out["h13_irreducible"] = bool((X^4 + X^3 + X^2 + X + 1).is_irreducible())
out["order_13_mod_5"] = int(Mod(13, 5).multiplicative_order())
out["order_19_mod_5"] = int(Mod(19, 5).multiplicative_order())
# CharacteristicFive
k5 = GF(5); R5 = PolynomialRing(k5, "X"); X = R5.gen()
out["char5_pow5"] = ((X - 1)^5 == X^5 - 1)
out["char5_pow4"] = ((X - 1)^4 == X^4 + X^3 + X^2 + X + 1)
out["char5_squarefree"] = bool((X^5 - 1).is_squarefree())

# NullCurveOrder: interval arithmetic and actual curve orders
cases = [("q11_accepted", 11, 160250, 161854, 40161, 160644, 0, 0),
         ("q13_rejected", 13, 370076, 372512, 370778, 370778, 0, 0),
         ("q13_accepted", 13, 370076, 372512, 92605, 370420, 0, 1),
         ("q19_rejected", 19, 2472953, 2479247, 1237500, 2475000, 0, 0),
         ("q19_accepted", 19, 2472953, 2479247, 619165, 2476660, 0, 1)]
nco = {}
for name, q, lo, hi, d, order, a, b in cases:
    Q = q^5
    hasse_lo = ceil(Q + 1 - 2*sqrt(RealField(200)(Q)))
    hasse_hi = floor(Q + 1 + 2*sqrt(RealField(200)(Q)))
    mults = [x for x in range(lo, hi + 1) if x % d == 0]
    K = GF(q^5, "z", modulus=PolynomialRing(GF(q), "X")([1, 0, 0, 0, CELLS[q], 1]))
    z = K.gen()
    E = EllipticCurve(K, [z + a, z + b])
    N = E.order()
    # proves-too-much: shrink the divisor to a proper divisor and show uniqueness fails
    pdiv = [x for x in divisors(d) if x < d]
    weaker = max(x for x in pdiv if len([y for y in range(lo, hi + 1) if y % x == 0]) > 1)
    nco[name] = dict(hasse_interval_recomputed=[int(hasse_lo), int(hasse_hi)],
                     hasse_matches_lean=(int(hasse_lo), int(hasse_hi)) == (lo, hi),
                     multiples_in_interval=mults, unique_and_equals_order=(mults == [order]),
                     curve="y^2 = x^3 + (z+%d)x + (z+%d) over GF(%d^5), modulus X^5+%dX^4+1" % (a, b, q, CELLS[q]),
                     sage_curve_order=int(N), sage_order_equals_lean=(int(N) == order),
                     divisor_divides_sage_order=(int(N) % d == 0),
                     largest_proper_divisor_breaking_uniqueness=int(weaker))
out["null_curve_order"] = nco
print(json.dumps(out, indent=1, default=str))
