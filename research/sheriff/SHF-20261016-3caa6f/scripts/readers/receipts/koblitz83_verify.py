#!/usr/bin/env python3
"""Independent GF(2^83) Koblitz-curve check of the n83 stacked recovered scalars.

Pure Python, shares no code with the producer or its oracle. Curve parameters
are taken from the crypto repo at the pinned revision 770f6a69
(research/sat_factor_base_review_20260908/autolab/protocol.json,
beats.koblitz.compact_orbit.n83_single_target.curve_fixture), passed in as a
JSON file. Points and scalars come from the study's inputs/cold_targets.json
and panel/runs.jsonl. Writes only to stdout.

E: y^2 + x y = x^3 + a x^2 + 1 over GF(2)[t]/(f), integers = polynomial-basis bit vectors.
"""
import hashlib
import json
import sys

fix = json.load(open(sys.argv[1]))
targets = json.load(open(sys.argv[2]))
runs = [json.loads(l) for l in open(sys.argv[3]) if l.strip()]

M = fix["degree"]
A = fix["curve_a"]
F = (1 << M) | sum(1 << e for e in fix["irreducible"]["low_terms"])
R = int(fix["subgroup_order"])
N = int(fix["group_order"])
H = int(fix["cofactor"])
G = tuple(int(v) for v in fix["generator"])


def fmul(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        b >>= 1
        a <<= 1
        if a >> M:
            a ^= F
    return r


def fsq(a):
    return fmul(a, a)


def finv(a):
    # a^(2^M - 2)
    assert a
    r, e = 1, (1 << M) - 2
    while e:
        if e & 1:
            r = fmul(r, a)
        a = fsq(a)
        e >>= 1
    return r


def trace(c):
    t, x = 0, c
    for _ in range(M):
        t ^= x
        x = fsq(x)
    assert t in (0, 1)
    return t


def halftrace(c):
    # M odd: H(c) = sum_{i=0}^{(M-1)/2} c^(2^(2i)); solves z^2 + z = c when Tr(c)=0
    z, x = 0, c
    for _ in range((M - 1) // 2 + 1):
        z ^= x
        x = fsq(fsq(x))
    return z


O = None


def on_curve(P):
    if P is O:
        return True
    x, y = P
    return fsq(y) ^ fmul(x, y) == fmul(fsq(x), x) ^ (fmul(A, fsq(x)) if A else 0) ^ 1


def neg(P):
    return O if P is O else (P[0], P[0] ^ P[1])


def add(P, Q):
    if P is O:
        return Q
    if Q is O:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2:
        if y2 == x1 ^ y1:  # Q = -P (covers P = -P when x = 0)
            return O
        assert y1 == y2
        # doubling, x1 != 0 here
        lam = x1 ^ fmul(y1, finv(x1))
        x3 = fsq(lam) ^ lam ^ A
        y3 = fsq(x1) ^ fmul(lam ^ 1, x3)
        return (x3, y3)
    lam = fmul(y1 ^ y2, finv(x1 ^ x2))
    x3 = fsq(lam) ^ lam ^ x1 ^ x2 ^ A
    y3 = fmul(lam, x1 ^ x3) ^ x3 ^ y1
    return (x3, y3)


def mul(k, P):
    Rr = O
    if k < 0:
        k, P = -k, neg(P)
    while k:
        if k & 1:
            Rr = add(Rr, P)
        P = add(P, P)
        k >>= 1
    return Rr


def is_probable_prime(n):
    if n < 2:
        return False
    small = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41]
    for p in small:
        if n % p == 0:
            return n == p
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for a in small:  # deterministic for n < 3.3e24
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(s - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


# Koblitz order: mu = (-1)^(1-a); t_0 = 2, t_1 = mu, t_{k+1} = mu t_k - 2 t_{k-1}
mu = 1 if A == 1 else -1
t0, t1 = 2, mu
for _ in range(M - 1):
    t0, t1 = t1, mu * t1 - 2 * t0
order_lucas = (1 << M) + 1 - t1

print("reduction poly f = t^%d + %s" % (M, " + ".join("t^%d" % e for e in sorted(fix["irreducible"]["low_terms"], reverse=True))))
print("curve_a", A)
print("#E via Lucas (Frobenius trace)", order_lucas, "== fixture group_order:", order_lucas == N)
print("cofactor * r == group_order:", H * R == N)
print("r probable prime (MR, 13 bases, deterministic < 3.3e24):", is_probable_prime(R))
print("r^2 does not divide #E:", N % (R * R) != 0)
print("G on curve:", on_curve(G))
print("[r]G == O:", mul(R, G) is O, " G != O:", G is not O)
print("[h]G != O (sanity)", mul(H, G) is not O)

# Targets: re-derive each cold point from the public input law, then check [k]G == Q
law_domain = targets["domain"]
law_role = targets["role"]


def derive(seed):
    counter = 0
    while True:
        dig = hashlib.sha256(("%s|%s|%d|%d" % (law_domain, law_role, seed, counter)).encode()).digest()
        x = int.from_bytes(dig[0:8], "little") % (1 << M)
        if x:
            c = x ^ A ^ fsq(finv(x))  # z^2 + z = x + a + 1/x^2, y = x z
            if trace(c) == 0:
                z = halftrace(c)
                assert fsq(z) ^ z == c
                bit = dig[8] & 1
                if (z & 1) != bit:
                    z ^= 1
                P = (x, fmul(x, z))
                assert on_curve(P)
                return mul(H, P), counter
        counter += 1


scal = {}
for r in runs:
    if r["arm"] and r["fields"].get("recovered_scalar") is not None:
        scal.setdefault(r["point_id"], set()).add(r["fields"]["recovered_scalar"])
    if r["fields"].get("verified") != "1":
        print("row not verified by producer:", r["serial"], r["arm"])

ok_all = True
for i, p in enumerate(targets["points"]):
    pid = "s%03d" % p["seed"]
    Q = tuple(int(v) for v in p["point"])
    Qd, ctr = derive(p["seed"])
    ks = scal.get(pid, set())
    k = int(next(iter(ks))) if len(ks) == 1 else None
    on = on_curve(Q)
    in_sub = mul(R, Q) is O
    kp = (mul(k, G) == Q) if k is not None else False
    der_x = Qd is not O and Qd[0] == Q[0]
    der_xy = Qd == Q
    ok_all &= on and in_sub and kp and der_x
    print(pid, "arms_with_scalar", sum(1 for r in runs if r["point_id"] == pid), "distinct_scalars", len(ks), "k", k,
          "on_curve", on, "[r]Q=O", in_sub, "[k]G==Q", kp, "law_x_match", der_x, "law_xy_match", der_xy, "counter", ctr)

# Q0 (archived identity)
q0 = [r for r in runs if r["point_id"] == "q0"]
q0pt = (2655898345537166180532960, 3881526307991673265292615)
k0 = {r["fields"]["recovered_scalar"] for r in q0}
print("q0 scalars", k0, "on_curve", on_curve(q0pt), "[k]G==Q0", mul(int(next(iter(k0))), G) == q0pt)
print("ALL 20 cold points verified:", ok_all)
