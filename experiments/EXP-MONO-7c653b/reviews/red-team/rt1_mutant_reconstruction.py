#!/usr/bin/env python3
"""RT-20260905-340bf1, joint 2 (Stage-4a wrong-rescaling-constant mutant).

Fresh, INDEPENDENT re-implementation of ONE Stage-4a mutant trial. Deliberately
does NOT import harness/toycurve.py's EllipticCurve/_sqrt_mod, nor
experiments/EXP-MONO-7c653b/implementation/run_experiment.py's group-law or
sqrt helpers. Uses only the textbook affine short-Weierstrass addition law and
a brute-force modular square root (p=211 is small enough).

Reconstructs RUN-MONO-7c653b-1's own Stage-4a trial 0:
  m=4, p=211, a=37, b=57, j=3 (=m-1), delta=57, delta_prime=102,
  tuple_x=[5,163,155] (raw-result.json stage4a.trials[0]).

Checks:
  (i) building the twist points and E_delta with the CORRECT delta, then
      rescaling by inverse(delta) (the Stage-3-style route) reproduces the
      reported direct_route_xset for this trial exactly -- i.e. this fresh
      reconstruction is faithful to the implementation's own reported
      "correct" behaviour before touching the mutation at all;
  (ii) the SAME accumulated sum R, rescaled instead by inverse(delta_prime),
      reproduces the implementation's own reported mutant_twist_route_xset
      for this trial exactly, and does NOT intersect the direct-route set.

Run: python3 rt1_mutant_reconstruction.py
"""
import itertools

p = 211
a = 37
b = 57
delta = 57
delta_prime = 102
tuple_x = [5, 163, 155]                     # RUN-1 stage4a.trials[0].tuple_x
direct_route_xset = {5, 67, 144, 171}       # RUN-1 stage4a.trials[0].direct_route_xset
reported_mutant_xset = {6, 9, 139, 205}     # RUN-1 stage4a.trials[0].mutant_twist_route_xset


def f(x):
    return (x ** 3 + a * x + b) % p


def modinv(x, p):
    return pow(x, -1, p)


def sqrt_mod_bruteforce(v, p):
    v %= p
    return [y for y in range(p) if (y * y) % p == v]


# --- Step 1: twist points, built with the CORRECT delta throughout (matching
# Stage 3's own construction; this is what the contract requires Stage 4a to
# do before the final rescaling is mutated). ---
inv_delta = modinv(delta, p)
pts_delta = []
for x in tuple_x:
    fx = f(x)
    rhs = (fx * inv_delta) % p
    roots = sqrt_mod_bruteforce(rhs, p)
    assert roots, f"no sqrt found for x={x}, rhs={rhs}"
    yprime = roots[0]
    X = (delta * x) % p
    Y = (delta * delta * yprime) % p
    pts_delta.append((X, Y))
    print(f"x={x}: f(x)={fx}, target y'^2={rhs}, y'={yprime}, twist point=({X},{Y})")

A_delta = (a * delta * delta) % p
B_delta = (b * delta ** 3) % p
print(f"E_delta: y^2 = x^3 + {A_delta} x + {B_delta}  (mod {p})")

for (X, Y) in pts_delta:
    assert (Y * Y) % p == (X ** 3 + A_delta * X + B_delta) % p, "point not on E_delta!"
print("all twist points independently verified on E_delta.\n")


# --- independent affine short-Weierstrass group law (no import) ---
INF = None


def ec_neg(P):
    if P is INF:
        return INF
    x, y = P
    return (x, (-y) % p)


def ec_add(P, Q, A):
    if P is INF:
        return Q
    if Q is INF:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return INF
    if P == Q:
        lam = (3 * x1 * x1 + A) * modinv(2 * y1, p) % p
    else:
        lam = (y2 - y1) * modinv((x2 - x1) % p, p) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


# --- Step 2: signed sum over eps in {+1,-1}^2 with eps_0 fixed to +1 (k=3
# points -> 2^(3-1)=4 sign classes), per the spec's own construction. ---
k = len(pts_delta)
correct_route_xs = set()
mutant_route_xs = set()
inv_delta_prime = modinv(delta_prime, p)

for rest_signs in itertools.product([1, -1], repeat=k - 1):
    signs = (1,) + rest_signs
    acc = INF
    for s, pt in zip(signs, pts_delta):
        term = pt if s == 1 else ec_neg(pt)
        acc = ec_add(acc, term, A_delta)
    assert acc is not INF
    X_R = acc[0]
    x_correct = (X_R * inv_delta) % p
    x_mutant = (X_R * inv_delta_prime) % p
    correct_route_xs.add(x_correct)
    mutant_route_xs.add(x_mutant)
    print(f"signs={signs}: R=({acc[0]},{acc[1]})  x(Q)_correct={x_correct}  x(Q)_mutant={x_mutant}")

print()
print("Correct-delta twist route x-set  :", sorted(correct_route_xs))
print("Reported direct_route_xset       :", sorted(direct_route_xset))
print("correct route == reported direct :", correct_route_xs == direct_route_xset)
print()
print("Mutant (delta') twist route x-set:", sorted(mutant_route_xs))
print("Reported mutant_twist_route_xset :", sorted(reported_mutant_xset))
print("mutant route == reported mutant  :", mutant_route_xs == reported_mutant_xset)
print("mutant route == direct route     :", mutant_route_xs == direct_route_xset, "(must be False)")

assert correct_route_xs == direct_route_xset
assert mutant_route_xs == reported_mutant_xset
assert mutant_route_xs != direct_route_xset
print("\nALL CHECKS PASSED.")
