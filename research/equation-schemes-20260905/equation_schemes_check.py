#!/usr/bin/env python3
"""Stdlib recomputation of the SafeCurves "Equations" criterion and of the
equation-scheme (curve-model) availability structure for all 20 SafeCurves
curves, from the fetched pages in retrieved-pages/ (parsed by
parse_safecurves.py into parsed_safecurves.json).

What is computed, per curve, with Python integers only (no PARI, no Sage):
  E1  the SafeCurves "elliptic?" quantity 4a^3+27b^2 | B(A^2-4) | d(1-d) mod p,
      compared with the page value and with the user-pasted table value;
  E2  the SafeCurves conversion formulas Montgomery->short Weierstrass and
      Edwards->Montgomery, checked by transporting the base point;
  E3  base point on curve; l probable prime (Miller-Rabin); h*l = #E satisfies
      Hasse; p+1-#E equals the page's trace; l*G = O on the Weierstrass model;
      twist order 2p+2-#E equals the page's l'*h'; D | t^2-4p with square cofactor;
  T1  rational 2-torsion rank of E(F_p) (roots of the Weierstrass cubic);
  T2  existence of a rational point of order 4 above each 2-torsion point;
  M1  availability over F_p of the Montgomery, twisted Edwards, Edwards,
      complete Edwards, Legendre, Jacobi-quartic, twisted Hessian models, from
      the torsion data and the cited criteria (see the note for provenance).
Nothing here is an attack, a cost measurement, or a safety conclusion.
"""
import json, os, random, re, sys
from math import isqrt

HERE = os.path.dirname(os.path.abspath(__file__))
random.seed(20260905)

# The "Result" column of the SafeCurves equation page as pasted by the user
# into this session (version 2013.10.14), used as an independent transcription.
USER_PASTE = {
 "Anomalous": 11727648024975671349546803128441217519000050500482270354686052,
 "M-221": 13700702496,
 "E-222": 6739986666787659948666753771754907668409286105635143120250270071885,
 "NIST P-224": 11286604486433664602000942456042078497941322427273965674759527357535,
 "Curve1174": 3618502788666131106986593281521497120414687020801267626233049500247283921789,
 "Curve25519": 236839902240,
 "BN(2,254)": 108,
 "brainpoolP256t1": 57658212939451454047362440458822499786448049740370722175159801125840878929880,
 "ANSSI FRP256v1": 79787647489891169820553912837105662027419783964415804103003411012672767526332,
 "NIST P-256": 76665531554481589733451106912866963084117386858640348521070896428385330110353,
 "secp256k1": 1323,
 "E-382": 9850501549098619803069760025035903451269934817616361666987073351061430442874302652853566563721228910201652474408829,
 "M-383": 4264844522496,
 "Curve383187": 52885740957,
 "brainpoolP384t1": 5181212714295366734216266753166056344803944016281454944474282600874932100420353077879019424596754753434846239416135,
 "NIST P-384": 34547176980116681824645216591738245691976440597762634059085075689656433507713054265850219419421678489421763812122908,
 "Curve41417": 42307582002575910332922579714097346549017899709713998034217522897561970639123926132812109468141778230245837569601494918393295,
 "Ed448-Goldilocks": 726838724295606890549323807888004534353641360687318060281490199180612328166730772686396383698676545930088884461843637361053496491001797,
 "M-511": 281364471840,
 "E-521": 6864797660130609714981900799081393217269435300143305409394463459185543183397656052122559640661454554977296311391480858037121987999716643812574028149728152941,
}

def parse_int(s):
    """First decimal integer in a cell such as '2695...881 = 2^224 - 2^96 + 1'."""
    m = re.search(r"-?\d+", s.replace(" ", ""))
    return int(m.group(0))

def parse_product(s):
    """'2^3', '1', '3^2 * 11 * 47 * ...' -> integer."""
    s = s.split("=")[0]
    val = 1
    for f in s.split("*"):
        f = f.strip()
        if not f:
            continue
        if "^" in f:
            b, e = f.split("^"); val *= int(b) ** int(e)
        else:
            val *= int(f)
    return val

def parse_equation(shape, eq, p):
    eq = eq.replace(" ", "")
    if shape == "short Weierstrass":
        m = re.fullmatch(r"y\^2=x\^3([+-]\d+)x([+-]\d+)", eq)
        a, b = int(m.group(1)) % p, int(m.group(2)) % p
        return {"a": a, "b": b}
    if shape == "Montgomery":
        m = re.fullmatch(r"y\^2=x\^3\+(\d+)x\^2\+x", eq)
        return {"A": int(m.group(1)) % p, "B": 1}
    if shape == "Edwards":
        m = re.fullmatch(r"x\^2\+y\^2=1([+-]\d+)x\^2y\^2", eq)
        return {"d": int(m.group(1)) % p}
    raise ValueError(shape)

def inv(x, p): return pow(x, -1, p)
def legendre(x, p):
    x %= p
    if x == 0: return 0
    return 1 if pow(x, (p - 1) // 2, p) == 1 else -1
def sqrt_mod(x, p):
    """Tonelli-Shanks; assumes x is a QR mod prime p."""
    x %= p
    if x == 0: return 0
    if p % 4 == 3:
        r = pow(x, (p + 1) // 4, p); assert r * r % p == x; return r
    q, s = p - 1, 0
    while q % 2 == 0: q //= 2; s += 1
    z = 2
    while legendre(z, p) != -1: z += 1
    m, c, t, r = s, pow(z, q, p), pow(x, q, p), pow(x, (q + 1) // 2, p)
    while t != 1:
        i, t2 = 0, t
        while t2 != 1: t2 = t2 * t2 % p; i += 1
        b = pow(c, 1 << (m - i - 1), p)
        m, c, t, r = i, b * b % p, t * b * b % p, r * b % p
    assert r * r % p == x
    return r

def is_probable_prime(n, rounds=40):
    if n < 2: return False
    for sp in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % sp == 0: return n == sp
    d, s = n - 1, 0
    while d % 2 == 0: d //= 2; s += 1
    for _ in range(rounds):
        a = random.randrange(2, n - 1)
        x = pow(a, d, n)
        if x in (1, n - 1): continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1: break
        else:
            return False
    return True

# ---- short Weierstrass affine group law -----------------------------------
def w_on_curve(P, a, b, p):
    if P is None: return True
    x, y = P
    return (y * y - (x * x * x + a * x + b)) % p == 0
def w_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3 * x1 * x1 + a) * inv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * inv((x2 - x1) % p, p) % p
    x3 = (lam * lam - x1 - x2) % p
    return (x3, (lam * (x1 - x3) - y1) % p)
def w_mul(k, P, a, p):
    R = None
    while k:
        if k & 1: R = w_add(R, P, a, p)
        P = w_add(P, P, a, p); k >>= 1
    return R

# ---- polynomial arithmetic mod (cubic, p) for root counting -----------------
def poly_mulmod(f, g, mod, p):
    # f, g, mod lists of coeffs low->high; mod monic degree 3
    res = [0] * (len(f) + len(g) - 1)
    for i, fi in enumerate(f):
        if fi == 0: continue
        for j, gj in enumerate(g):
            res[i + j] = (res[i + j] + fi * gj) % p
    # reduce
    d = len(mod) - 1
    for i in range(len(res) - 1, d - 1, -1):
        c = res[i]
        if c == 0: continue
        for j in range(d + 1):
            res[i - d + j] = (res[i - d + j] - c * mod[j]) % p
    res = res[:d]
    while len(res) < d: res.append(0)
    return res
def poly_powmod_x(e, mod, p):
    result = [1, 0, 0]; base = [0, 1, 0]
    while e:
        if e & 1: result = poly_mulmod(result, base, mod, p)
        base = poly_mulmod(base, base, mod, p); e >>= 1
    return result
def poly_gcd(f, g, p):
    def strip(h):
        while h and h[-1] == 0: h.pop()
        return h
    f, g = strip(list(f)), strip(list(g))
    while g:
        # f mod g
        while len(f) >= len(g):
            c = f[-1] * inv(g[-1], p) % p; sh = len(f) - len(g)
            for j in range(len(g)):
                f[sh + j] = (f[sh + j] - c * g[j]) % p
            f = strip(f)
            if not f: break
        f, g = g, f
    return f
def cubic_roots(a, b, p):
    """Rational roots of x^3 + a x + b over F_p: count via gcd(x^p - x, f), then
    find them by testing the gcd's factors (degree <= 3, so brute force by
    Cantor-Zassenhaus-free method: if degree 1 read off; if 3 use the fact that
    one root can be found by splitting with random (x+c)^((p-1)/2))."""
    f = [b % p, a % p, 0, 1]
    xp = poly_powmod_x(p, f, p)              # x^p mod f
    g = [(xp[0]) % p, (xp[1] - 1) % p, xp[2] % p]
    gcd = poly_gcd(g, f[:], p)
    deg = len(gcd) - 1
    roots = []
    if deg == 0:
        return []
    if deg == 1:
        roots = [(-gcd[0] * inv(gcd[1], p)) % p]
    elif deg == 3:
        # split: find one root via gcd((x+c)^((p-1)/2) - 1, f)
        for c in range(1, 200):
            base = [c % p, 1, 0]; e = (p - 1) // 2; acc = [1, 0, 0]
            while e:
                if e & 1: acc = poly_mulmod(acc, base, f, p)
                base = poly_mulmod(base, base, f, p); e >>= 1
            h = [(acc[0] - 1) % p, acc[1], acc[2]]
            gg = poly_gcd(h, f[:], p)
            if 1 <= len(gg) - 1 <= 2:
                if len(gg) - 1 == 1:
                    r = (-gg[0] * inv(gg[1], p)) % p
                else:
                    # quadratic: solve
                    A2, B2, C2 = gg[2], gg[1], gg[0]
                    disc = (B2 * B2 - 4 * A2 * C2) % p
                    r = ((-B2 + sqrt_mod(disc, p)) * inv(2 * A2, p)) % p
                # deflate f by (x - r): remaining quadratic x^2 + r x + (r^2 + a)
                A2, B2, C2 = 1, r, (r * r + a) % p
                disc = (B2 * B2 - 4 * A2 * C2) % p
                s = sqrt_mod(disc, p)
                roots = sorted({r, ((-B2 + s) * inv(2, p)) % p, ((-B2 - s) * inv(2, p)) % p})
                break
    for r in roots:
        assert (r * r * r + a * r + b) % p == 0
    return roots

def analyse(name, rec):
    p = rec["p"]; shape = rec["shape"]; eq = parse_equation(shape, rec["equation"], p)
    out = {"curve": name, "shape": shape, "p_bits": p.bit_length(), "p_mod_4": p % 4,
           "cofactor_h": rec["h"], "l_bits": rec["l"].bit_length()}
    # E1 elliptic quantity
    if shape == "short Weierstrass":
        q = (4 * pow(eq["a"], 3, p) + 27 * pow(eq["b"], 2, p)) % p
    elif shape == "Montgomery":
        q = eq["B"] * (eq["A"] * eq["A"] - 4) % p
    else:
        q = eq["d"] * (1 - eq["d"]) % p
    out["E1_elliptic_quantity_matches_page"] = (q == rec["elliptic_page"] % p)
    out["E1_elliptic_quantity_matches_user_paste"] = (q == USER_PASTE[name] % p)
    out["E1_nonzero"] = q != 0
    # E2 conversions and Weierstrass model
    G = rec["G"]
    if shape == "short Weierstrass":
        a, b = eq["a"], eq["b"]; Gw = G
        out["E2_base_on_native_curve"] = w_on_curve(G, a, b, p)
    elif shape == "Montgomery":
        A, B = eq["A"], eq["B"]
        x, y = G
        out["E2_base_on_native_curve"] = (B * y * y - (x ** 3 + A * x * x + x)) % p == 0
        a = (3 - A * A) * inv(3 * B * B, p) % p
        b = (2 * A ** 3 - 9 * A) * inv(27 * B ** 3, p) % p
        Gw = ((x + A * inv(3, p)) * inv(B, p) % p, y * inv(B, p) % p)
    else:
        d = eq["d"]
        x, y = G
        out["E2_base_on_native_curve"] = (x * x + y * y - (1 + d * x * x * y * y)) % p == 0
        A = 2 * (1 + d) * inv(1 - d, p) % p; B = 4 * inv(1 - d, p) % p
        u = (1 + y) * inv(1 - y, p) % p; v = (1 + y) * inv((1 - y) * x, p) % p
        out["E2_edwards_to_montgomery_base_on_curve"] = (B * v * v - (u ** 3 + A * u * u + u)) % p == 0
        a = (3 - A * A) * inv(3 * B * B, p) % p
        b = (2 * A ** 3 - 9 * A) * inv(27 * B ** 3, p) % p
        Gw = ((u + A * inv(3, p)) * inv(B, p) % p, v * inv(B, p) % p)
        out["edwards_d_is_nonsquare_complete"] = legendre(d, p) == -1
    out["E2_converted_base_on_weierstrass"] = w_on_curve(Gw, a, b, p)
    out["weierstrass_discriminant_nonzero"] = (4 * pow(a, 3, p) + 27 * pow(b, 2, p)) % p != 0
    # E3 orders
    l, h = rec["l"], rec["h"]
    N = h * l
    out["E3_l_probable_prime_MR40"] = is_probable_prime(l)
    out["E3_hasse_holds"] = abs(p + 1 - N) <= 2 * isqrt(p) + 1
    t = p + 1 - N
    out["E3_trace_matches_page"] = (t == rec["trace_page"])
    out["E3_lG_is_infinity_on_weierstrass"] = (w_mul(l, Gw, a, p) is None)
    out["E3_hG_not_infinity_when_h_gt_1"] = (h == 1) or (w_mul(h, Gw, a, p) is not None)
    Ntw = 2 * p + 2 - N
    out["E3_twist_order_matches_page"] = (Ntw == rec["l_twist"] * rec["h_twist"])
    D = rec["D_page"]
    disc = t * t - 4 * p
    ok = D != 0 and disc % D == 0 and (disc // D) > 0 and isqrt(disc // D) ** 2 == (disc // D)
    out["E3_D_divides_t2_minus_4p_with_square_cofactor"] = ok
    # T1 rational 2-torsion
    roots = cubic_roots(a, b, p)
    out["T1_rational_2torsion_points"] = len(roots)
    out["T1_E2_rank"] = {0: 0, 1: 1, 3: 2}[len(roots)]
    # T2 order-4 points above each 2-torsion point; Montgomery criterion per root
    mont_roots, order4 = [], []
    for al in roots:
        c = (3 * al * al + a) % p
        if legendre(c, p) == 1:
            mont_roots.append(al)
            s = sqrt_mod(c, p)
            u = 3 * al % p
            if legendre((2 * s + u) % p, p) == 1 or legendre((-2 * s + u) % p, p) == 1:
                order4.append(al)
    out["T2_2torsion_points_with_montgomery_form"] = len(mont_roots)
    out["T2_2torsion_points_halvable_order4_exists"] = len(order4)
    # consistency with group structure forced by #E = h*l
    if h in (1, 4, 8):
        r = out["T1_E2_rank"]
        structure = {1: "trivial", 4: {1: "Z/4", 2: "Z/2xZ/2"}, 8: {1: "Z/8", 2: "Z/2xZ/4"}}[h]
        if isinstance(structure, dict): structure = structure.get(r, "inconsistent")
        out["T2_torsion_structure_from_h_and_rank"] = structure
        expect4 = (h >= 4 and r == 1) or (h >= 8 and r == 2)
        out["T2_order4_consistent_with_structure"] = (expect4 == (len(order4) > 0))
    out["T3_three_divides_group_order"] = (N % 3 == 0)
    # M1 model availability over F_p
    out["M1_short_weierstrass"] = True
    out["M1_montgomery"] = len(mont_roots) > 0
    out["M1_twisted_edwards"] = len(mont_roots) > 0          # BBJLP Thm 3.2
    out["M1_edwards_a_eq_1"] = len(order4) > 0               # BBJLP Thm 3.3
    out["M1_legendre_full_2torsion"] = len(roots) == 3
    out["M1_jacobi_quartic_needs_2torsion"] = len(roots) >= 1  # criterion: recalled, see note
    out["M1_twisted_hessian_needs_3torsion"] = (N % 3 == 0)    # criterion: recalled, see note
    # deck-group orders available to a torsion-symmetrised coordinate (2 * |cyclic rational torsion|)
    cyc = {1: [1], 4: [1, 2, 4] if len(roots) == 1 else [1, 2], 8: [1, 2, 4, 8] if len(roots) == 1 else [1, 2, 4]}.get(h, [1])
    out["deck_orders_2k_for_cyclic_rational_torsion_k"] = [2 * k for k in cyc]
    return out

def main():
    d = json.load(open(os.path.join(HERE, "parsed_safecurves.json")))
    field, equation, base, twist, disc = d["field"], d["equation"], d["base"], d["twist"], d["disc"]
    results = []
    for name in USER_PASTE:
        rec = {
            "p": parse_int(field[6][name][1]),
            "shape": equation[6][name][0], "equation": equation[6][name][1],
            "elliptic_page": parse_int(equation[7][name][1]),
            "G": tuple(int(v) for v in re.findall(r"-?\d+", base[6][name][1].split("=")[0])[:2]),
            "l": parse_int(base[7][name][2]),
            "h": parse_product(twist[8][name][0]), "h_twist": parse_product(twist[8][name][1]),
            "l_twist": parse_int(twist[7][name][0]),
            "trace_page": parse_int(disc[6][name][0]), "D_page": parse_int(disc[7][name][1]),
        }
        results.append(analyse(name, rec))
    json.dump(results, open(os.path.join(HERE, "results.json"), "w"), indent=1)
    keys = [k for k in results[0] if k.startswith(("E1", "E2", "E3", "T2_order4_consistent", "weierstrass_disc"))]
    all_ok = all(all(r.get(k, True) is not False for k in keys) for r in results)
    print("ALL VERIFICATION CHECKS PASS" if all_ok else "SOME CHECK FAILED")
    for r in results:
        fails = [k for k in keys if r.get(k, True) is False]
        print(f"{r['curve']:>17} | {r['shape']:>17} | h={r['cofactor_h']:<2} | E[2]rank={r['T1_E2_rank']} "
              f"| 2tors={r['T1_rational_2torsion_points']} mont={r['T2_2torsion_points_with_montgomery_form']} "
              f"ord4={r['T2_2torsion_points_halvable_order4_exists']} | struct={r.get('T2_torsion_structure_from_h_and_rank','?'):>8} "
              f"| Edw(a=1)={r['M1_edwards_a_eq_1']!s:5} tEdw={r['M1_twisted_edwards']!s:5} Leg={r['M1_legendre_full_2torsion']!s:5} "
              f"| deck={r['deck_orders_2k_for_cyclic_rational_torsion_k']} | p%4={r['p_mod_4']} | fails={fails}")
main()
