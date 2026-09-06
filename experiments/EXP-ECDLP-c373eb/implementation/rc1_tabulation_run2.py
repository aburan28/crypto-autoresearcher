#!/usr/bin/env python3
"""
RC-1 tabulation, RUN-2 (replication instance).

Adapted from rc1_tabulation.py (RUN-1), same algorithm and protocol,
applied to a SECOND, independently chosen toy instance:
  p=1013 (RUN-1 used p=1009), curve y^2 = x^3 + 2x + 2 (RUN-1: x^3+x+1),
  n=41 (RUN-1: n=47).

No change to the mathematical method: Jacobian-coordinate scalar
multiplication, canonical order-n lift via Hensel/Newton lifting on the
order-n condition, discriminating null lift, Vandermonde/non-rigid probe,
independent spot-check.
"""
import json, sympy

p = 1013
A, B = 2, 2
r = 8
MOD = p ** r

assert sympy.isprime(p)
disc = -16 * (4*A**3 + 27*B**2)
assert disc % p != 0

# ---------------- affine F_p arithmetic: find S and check curve ----------------
def fp_add(P, Q, p, A):
    if P is None: return Q
    if Q is None: return P
    (x1, y1), (x2, y2) = P, Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P == Q:
        lam = (3*x1*x1 + A) * pow(2*y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1-x3) - y1) % p
    return (x3, y3)

def fp_mul(k, P, p, A):
    R = None; Q = P
    while k > 0:
        if k & 1: R = fp_add(R, Q, p, A)
        Q = fp_add(Q, Q, p, A)
        k >>= 1
    return R

def count_points(A, B, p):
    cnt = 1
    for x in range(p):
        rhs = (x**3 + A*x + B) % p
        if rhs == 0: cnt += 1
        else:
            if pow(rhs, (p-1)//2, p) == 1: cnt += 2
    return cnt

N = count_points(A, B, p)
a_p = p + 1 - N
assert a_p != 0, "supersingular curve (a_p == 0); pick a different (A, B)"
factorization = sympy.factorint(N)
n = 41
assert N % n == 0 and sympy.isprime(n)

def find_point_of_order_n(A, B, p, N, n):
    cofactor = N // n
    for x in range(p):
        rhs = (x**3 + A*x + B) % p
        if rhs == 0: continue
        if pow(rhs, (p-1)//2, p) != 1: continue
        from sympy.ntheory.residue_ntheory import sqrt_mod
        y = sqrt_mod(rhs, p)
        S = fp_mul(cofactor, (x, y), p, A)
        if S is None: continue
        if fp_mul(n, S, p, A) is None:
            return S
    return None

S = find_point_of_order_n(A, B, p, N, n)
assert S is not None and fp_mul(n, S, p, A) is None and S[1] % p != 0, \
    "S must have order exactly n, gcd(n,p)=1, and not be 2-torsion"
assert p % n != 0, "gcd(n,p) must be 1"

# ---------------- Z/p^k Jacobian-coordinate EC arithmetic (division-free) ----------------
def jac_dbl(P, mod):
    X1, Y1, Z1 = P
    Ssq = (4*X1*Y1*Y1) % mod
    M = (3*X1*X1 + A*Z1**4) % mod
    X3 = (M*M - 2*Ssq) % mod
    Y3 = (M*(Ssq - X3) - 8*Y1**4) % mod
    Z3 = (2*Y1*Z1) % mod
    return (X3, Y3, Z3)

def jac_add(P, Q, mod):
    X1, Y1, Z1 = P; X2, Y2, Z2 = Q
    if Z1 % mod == 0: return Q
    if Z2 % mod == 0: return P
    Z1Z1 = (Z1*Z1) % mod; Z2Z2 = (Z2*Z2) % mod
    U1 = (X1*Z2Z2) % mod; U2 = (X2*Z1Z1) % mod
    S1 = (Y1*Z2*Z2Z2) % mod; S2 = (Y2*Z1*Z1Z1) % mod
    H = (U2 - U1) % mod
    if H == 0:
        if (S2 - S1) % mod == 0: return jac_dbl(P, mod)
        else: return (0, 1, 0)
    I = (4*H*H) % mod
    J = (H*I) % mod
    rr = (2*(S2 - S1)) % mod
    V = (U1*I) % mod
    X3 = (rr*rr - J - 2*V) % mod
    Y3 = (rr*(V - X3) - 2*S1*J) % mod
    Z3 = (((Z1+Z2)**2 - Z1Z1 - Z2Z2) * H) % mod
    return (X3 % mod, Y3 % mod, Z3 % mod)

def scalar_mult(k, P, mod):
    """Double-and-add scalar multiplication."""
    Rp = (0, 1, 0); Q = P
    while k > 0:
        if k & 1: Rp = jac_add(Rp, Q, mod)
        Q = jac_dbl(Q, mod)
        k >>= 1
    return Rp

def scalar_mult_naive(k, P, mod):
    """Independent recomputation path: k repeated additions (no doubling)."""
    Rp = (0, 1, 0)
    for _ in range(k):
        Rp = jac_add(Rp, P, mod)
    return Rp

def curve_ok(P, mod):
    X, Y, Z = P
    return (Y*Y) % mod == (X**3 + A*X*Z**4 + B*Z**6) % mod

def valuation(x, cap, mod):
    x %= mod
    if x == 0: return cap
    e = 0
    while x % p == 0 and e < cap:
        x //= p; e += 1
    return e

def affine_x(P, mod):
    """Jacobian affine x = X / Z^2."""
    X, Y, Z = P
    assert valuation(Z, r, mod) == 0, "point reduces to O mod p; not affine"
    zi = pow(Z, -1, mod)
    return (X * zi * zi) % mod

def hensel_lift_y(x0, y0_modp, mod):
    """Newton/Hensel-lift a y-coordinate root of Y^2 = x0^3+A x0+B, doubling
    precision each step, starting from y0_modp mod p (requires y0_modp != 0
    mod p, i.e. S not 2-torsion)."""
    c = (x0**3 + A*x0 + B) % mod
    y = y0_modp % p
    prec = 1
    bound = mod.bit_length() + 8
    while prec < bound:
        newprec = min(2*prec, prec + 64)
        m = min(p**newprec, mod)
        yy = y % m
        fval = (yy*yy - c) % m
        fpinv = pow(2*yy, -1, m)
        yy = (yy - fval*fpinv) % m
        y = yy
        prec = newprec
        if m >= mod:
            break
    return y % mod

# ---------------- Canonical order-n lift S-hat ----------------
GUARD = 4  # extra working-precision digits carried through intermediate steps
WORK_MOD = p ** (r + GUARD)

def f_of_x0(x0, mod):
    y0 = hensel_lift_y(x0 % mod, S[1], mod)
    Q0 = (x0 % mod, y0, 1)
    Rn = scalar_mult(n, Q0, mod)
    return Rn[2] % mod

x0_start = S[0]
f0 = f_of_x0(x0_start, WORK_MOD)
f0_shift = f_of_x0(x0_start + p, WORK_MOD)
assert valuation(f0, r, WORK_MOD) == 1, \
    "expected a simple (order-1) root of the order-n condition at S.x mod p"
deriv_mod_p = ((f0_shift - f0) // p) % p
assert deriv_mod_p != 0, "derivative not a unit mod p; cannot Hensel-lift"
d_inv = pow(deriv_mod_p, -1, p)

xcur = x0_start
for step in range(1, r + 2):
    m = min(p**(step + 1), WORK_MOD)
    fval = f_of_x0(xcur, WORK_MOD)
    correction = (fval * d_inv) % m
    xcur = (xcur - correction) % m

x_hat = xcur % MOD
y_hat = hensel_lift_y(x_hat, S[1], MOD)
S_hat = (x_hat, y_hat, 1)
assert curve_ok(S_hat, MOD)
assert S_hat[0] % p == S[0] and S_hat[1] % p == S[1]

nS_hat = scalar_mult(n, S_hat, MOD)
canonical_lift_verified_exact = (nS_hat == (0, 1, 0))
canonical_lift_depth = valuation(nS_hat[2], r, MOD)

# ---------------- Null lift: a Hensel lift of S NOT enforcing the order-n
# condition (x perturbed at the p^1 digit relative to S.x; still a valid
# curve point reducing to S mod p) ----------------
x0_null = (S[0] + p) % MOD
y0_null = hensel_lift_y(x0_null, S[1], MOD)
Lift_null = (x0_null, y0_null, 1)
assert curve_ok(Lift_null, MOD)
assert Lift_null[0] % p == S[0] and Lift_null[1] % p == S[1]
n_Lift_null = scalar_mult(n, Lift_null, MOD)
null_lift_order_n_depth = valuation(n_Lift_null[2], r, MOD)

def vp_diff_x(lift, j, k):
    xk = affine_x(scalar_mult(k, lift, MOD), MOD)
    xj = affine_x(scalar_mult(j, lift, MOD), MOD)
    return valuation((xk - xj) % MOD, r, MOD)

# ---------------- Part 1: D1 on the canonical lift, all 1 <= j < k < n ----------------
part1 = {}
part1_notes = []
for j in range(1, n):
    for k in range(j+1, n):
        v = vp_diff_x(S_hat, j, k)
        part1[f"{j},{k}"] = v
        on_fibre = (k % n == j % n) or (k % n == (-j) % n)
        if on_fibre and v < r:
            part1_notes.append({"pair": [j, k], "kind": "on-fibre-short-of-cap", "v": v})
        if (not on_fibre) and (1 <= v <= r - 1):
            part1_notes.append({"pair": [j, k], "kind": "off-fibre-intermediate-VIOLATION", "v": v})

part1_image = sorted(set(part1.values()))

# ---------------- Part 2: identical tabulation on the null lift ----------------
part2 = {}
for j in range(1, n):
    for k in range(j+1, n):
        part2[f"{j},{k}"] = vp_diff_x(Lift_null, j, k)
part2_image = sorted(set(part2.values()))

# ---------------- Part 3: rigid (Vandermonde) vs non-rigid functional, canonical lift ----------------
# Triples chosen fresh for n=41 (RUN-1 used n=47); one degenerate/near-collision
# sanity case included, analogous to RUN-1's (3, 44, 41) with 44 = -3 mod 47.
triples = [(1, 2, 3), (2, 5, 9), (7, 13, 33), (4, 33, 37), (1, 40, 20), (3, 38, 35)]
# (3, 38, 35): 38 = n - 3 = -3 mod 41 -> coincident/degenerate sanity case
xs_cache = {}
def xk(k):
    if k not in xs_cache:
        xs_cache[k] = affine_x(scalar_mult(k, S_hat, MOD), MOD)
    return xs_cache[k]

part3 = []
for (k1, k2, k3) in triples:
    x1v, x2v, x3v = xk(k1), xk(k2), xk(k3)
    vander = ((x1v-x2v) * (x2v-x3v) * (x1v-x3v)) % MOD
    nonrigid = (x1v*x2v - x3v) % MOD
    part3.append({
        "k1": k1, "k2": k2, "k3": k3,
        "vandermonde_vp": valuation(vander, r, MOD),
        "nonrigid_vp": valuation(nonrigid, r, MOD),
    })

vander_image = sorted(set(t["vandermonde_vp"] for t in part3))
nonrigid_image = sorted(set(t["nonrigid_vp"] for t in part3))

# ---------------- Spot check: independent recomputation path ----------------
j_spot, k_spot = 5, 12
fast_k = scalar_mult(k_spot, S_hat, MOD)
naive_k = scalar_mult_naive(k_spot, S_hat, MOD)
fast_j = scalar_mult(j_spot, S_hat, MOD)
naive_j = scalar_mult_naive(j_spot, S_hat, MOD)
spot_check = {
    "j": j_spot, "k": k_spot,
    "x_k_via_double_and_add": affine_x(fast_k, MOD),
    "x_k_via_repeated_addition": affine_x(naive_k, MOD),
    "x_k_paths_agree": affine_x(fast_k, MOD) == affine_x(naive_k, MOD),
    "x_j_via_double_and_add": affine_x(fast_j, MOD),
    "x_j_via_repeated_addition": affine_x(naive_j, MOD),
    "x_j_paths_agree": affine_x(fast_j, MOD) == affine_x(naive_j, MOD),
    "recomputed_D1_from_independent_path": valuation(
        (affine_x(naive_k, MOD) - affine_x(naive_j, MOD)) % MOD, r, MOD),
    "tabulated_D1": part1[f"{j_spot},{k_spot}"],
    "curve_equation_holds_exactly_for_S_hat_mod_p_r": curve_ok(S_hat, MOD),
    "curve_equation_holds_exactly_for_null_lift_mod_p_r": curve_ok(Lift_null, MOD),
}

result = {
    "curve": {
        "p": p, "A": A, "B": B,
        "discriminant_mod_p_nonzero": True,
        "a_p": a_p, "ordinary": True,
        "N_points_over_Fp": N,
        "N_factorization": {str(k): v for k, v in factorization.items()},
    },
    "point_S": {"x": S[0], "y": S[1], "order_n": n},
    "precision_r": r,
    "canonical_lift_S_hat": {
        "x_mod_p_r": x_hat, "y_mod_p_r": y_hat,
        "construction": (
            "Newton/Hensel lift of the SIMPLE root x0=S.x of "
            "f(x0) = Z-coordinate of [n](x0, HenselLift_y(x0)); linear "
            "(one p-adic digit per step) Hensel iteration using a "
            "finite-difference approximation of df/dx0 mod p."
        ),
        "verified_n_times_S_hat_equals_O_exactly_mod_p_r": canonical_lift_verified_exact,
        "v_p_of_Z_of_n_times_S_hat": canonical_lift_depth,
    },
    "null_lift": {
        "x_mod_p_r": x0_null, "y_mod_p_r": y0_null,
        "construction": "Hensel lift of S with x perturbed by +p at the p^1 digit (does not enforce the order-n condition).",
        "v_p_of_Z_of_n_times_null_lift": null_lift_order_n_depth,
    },
    "part1_D1_image_canonical_lift": part1_image,
    "part1_notes": part1_notes,
    "part1_full_table": part1,
    "part2_D1_image_null_lift": part2_image,
    "part2_full_table": part2,
    "part3_triples": part3,
    "part3_vandermonde_image": vander_image,
    "part3_nonrigid_image": nonrigid_image,
    "spot_check": spot_check,
}

if __name__ == "__main__":
    print(json.dumps(
        {k: v for k, v in result.items() if k not in ("part1_full_table", "part2_full_table")},
        indent=2, default=str))
    print("num part1 pairs:", len(part1), " num part2 pairs:", len(part2))
