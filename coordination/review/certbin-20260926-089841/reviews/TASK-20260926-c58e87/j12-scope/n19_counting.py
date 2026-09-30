"""J12 (ii) n = 19 counting (TASK-20260926-c58e87). A DERIVATION, unchecked by measurement:
no n = 19 system is closed here (only degree-4 projection ranks P from quadratic parts).
Setting: n = 19, l = 10, m = 2, 20 Boolean variables, x_1 = sum_{j<10} v_j b_j,
x_2 = sum_{j<10} v_{10+j} b_j. Counts: M_4 rows 19 * (1 + 20 + 190) = 4009; dim B_{<=3} =
1 + 20 + 190 + 1140 = 1351; trivial syzygies C(19,2) + 19 = 190; ell-syzygies <= 19.
Computes P for:
  (a) the convolution forms Q_s = sum_{i+j=s} v_i v_{10+j} (s = 0..18) -- modulus-free
      (2l - 1 = n: x_1 x_2 has degree <= 18 < 19, no reduction);
  (b) S_3's quadratic part phi_{x_R}(x_1 x_2) over the polynomial basis, with a modulus CHOSEN
      HERE (the n = 19 cell's modulus was not read: it is in excluded files), 5 random x_R;
  (c) the same over 3 random bases V' (nine... ten random elements, independent, not all deg < 10).
Also the same P for n = 17 as a cross-check against j9b-counting.json (1695) and O4 (1904).
Usage: python3 n19_counting.py <out.json>
"""
import itertools
import json
import random
import sys
from math import comb


def make_field(n, poly):
    MOD = poly

    def mul(a, b):
        r = 0
        while b:
            if b & 1:
                r ^= a
            b >>= 1
            a <<= 1
            if a >> n:
                a ^= MOD
        return r
    return mul


def irreducible(n, poly):
    mul = make_field(n, poly)
    x = 2
    for _ in range(n):
        x = mul(x, x)
    # n prime here (17, 19): irreducible iff t^(2^n) = t and no root in F_2
    no_root = (poly & 1) == 1 and bin(poly).count("1") % 2 == 1
    return x == 2 and no_root


def find_modulus(n):
    for k in range(1, n):
        p = (1 << n) | (1 << k) | 1
        if irreducible(n, p):
            return p, "trinomial"
    for a, b, c in itertools.combinations(range(1, n), 3):
        p = (1 << n) | (1 << c) | (1 << b) | (1 << a) | 1
        if irreducible(n, p):
            return p, "pentanomial"
    raise RuntimeError


def P_rank(qforms, nv):
    """qforms: list of sets of pair-masks (bilinear/quadratic monomials). Degree-4 projection rank."""
    deg4 = {sum(1 << x for x in t): i for i, t in enumerate(itertools.combinations(range(nv), 4))}
    piv = {}
    rank = 0
    for t in itertools.combinations(range(nv), 2):
        mu = (1 << t[0]) | (1 << t[1])
        for q in qforms:
            x = 0
            for m in q:
                if mu & m == 0:
                    x ^= 1 << deg4[mu | m]
            while x:
                hb = x.bit_length() - 1
                if hb in piv:
                    x ^= piv[hb]
                else:
                    piv[hb] = x
                    rank += 1
                    break
    return rank


def quad_forms(n, l, basis, xr, mul, phi=True):
    """coordinate k of phi_{x_R}(x_1 x_2) (phi(y) = y^2 + x_R y), or of x_1 x_2 if phi False."""
    forms = [set() for _ in range(n)]
    for i in range(l):
        for j in range(l):
            y = mul(basis[i], basis[j])
            c = (mul(y, y) ^ mul(xr, y)) if phi else y
            m = (1 << i) | (1 << (l + j))
            for k in range(n):
                if (c >> k) & 1:
                    forms[k] ^= {m}
    return forms


def conv_forms(n, l):
    forms = [set() for _ in range(n)]
    for i in range(l):
        for j in range(l):
            forms[i + j] ^= {(1 << i) | (1 << (l + j))}
    return forms


def independent(vals):
    ech = {}
    for x in vals:
        while x:
            hb = x.bit_length() - 1
            if hb in ech:
                x ^= ech[hb]
            else:
                ech[hb] = x
                break
        if x == 0:
            return False
    return True


def arithmetic(n, l, P, ell=True):
    nv = 2 * l
    rows = n * (1 + nv + comb(nv, 2))
    b3 = 1 + nv + comb(nv, 2) + comb(nv, 3)
    triv = comb(n, 2) + n
    ellsyz = n - 2 if False else (nv - 1 if ell else 0)  # 17 at n = 17 (measured); nv - 1 by analogy
    Z = rows - P
    return {"n": n, "l": l, "rows_M4": rows, "dim_B_le3": b3, "trivial": triv, "ell_syzygies_assumed": ellsyz,
            "P": P, "dim_Z_top": Z, "Z_minus_trivial": Z - triv, "excess_over_B3": Z - triv - b3,
            "excess_over_B3_with_ell_syz": Z - triv - ellsyz - b3,
            "saturation_forced_count": Z - triv - ellsyz - b3 > 0,
            "rigorous_fallen_upper_bound_if_not_forced": Z - triv - ellsyz}


rng = random.Random(2026092689219)
res = {"seed_python_random": 2026092689219}
for n, l in ((17, 9), (19, 10)):
    p, kind = ((1 << 17) | (1 << 3) | 1, "frozen t^17+t^3+1") if n == 17 else find_modulus(n)
    assert irreducible(n, p)
    mul = make_field(n, p)
    pb = [1 << j for j in range(l)]
    rec = {"modulus": p, "modulus_kind": kind}
    Pc = P_rank(conv_forms(n, l), 2 * l)
    rec["P_convolution_forms"] = Pc
    rec["arith_convolution_no_ell"] = arithmetic(n, l, Pc, ell=False)
    Ps = []
    for _ in range(5):
        xr = rng.randrange(1 << l, 1 << n)
        Ps.append(P_rank(quad_forms(n, l, pb, xr, mul), 2 * l))
    rec["P_S3_poly_basis_5_xR"] = Ps
    rec["arith_S3_poly_basis"] = arithmetic(n, l, Ps[0], ell=True)
    Pr = []
    for _ in range(3):
        while True:
            b = [rng.randrange(1, 1 << n) for _ in range(l)]
            if independent(b) and not all(x < (1 << l) for x in b):
                break
        xr = rng.randrange(1 << l, 1 << n)
        Pr.append(P_rank(quad_forms(n, l, b, xr, mul), 2 * l))
    rec["P_S3_random_basis_3"] = Pr
    rec["arith_S3_random_basis"] = arithmetic(n, l, Pr[0], ell=True)
    res[f"n{n}"] = rec
    print(json.dumps(rec, indent=1), flush=True)
json.dump(res, open(sys.argv[1], "w"), indent=1)
