#!/usr/bin/env python3
"""Independent check of TreeSplit.Leak's two propositions (SHF-20261016-3caa6f re-audit, L3).

Polynomials over GF(2) are encoded as integers (bit i = coeff of t^i), as in the Lean.
Two independent remainder routines: (1) textbook long division written here;
(2) a literal port of Leak.lean's polyMod loop semantics (130 iterations, highest-bit
alignment), to show the bounded loop is not what makes the theorem true.
Also: a proves-too-much control (mutated statements must be false).
"""

GS = [23, 35, 101, 159, 421, 29, 49, 127, 249, 331]  # Leak.lean:28


def deg(a):
    return a.bit_length() - 1


def gf2_mod(a, b):
    assert b != 0
    db = deg(b)
    while a and deg(a) >= db:
        a ^= b << (deg(a) - db)
    return a


def polymod_lean_port(a, b):
    db = b.bit_length() - 1 if b else 0  # Nat.log2 0 = 0
    for _ in range(130):
        if a != 0 and (a.bit_length() - 1) >= db:
            a ^= b << ((a.bit_length() - 1) - db)
    return a


def poly_str(a):
    terms = [("1" if i == 0 else ("t" if i == 1 else f"t^{i}")) for i in range(deg(a), -1, -1) if a >> i & 1]
    return "+".join(terms)


T7_1, T3_1 = (1 << 7) | 1, (1 << 3) | 1  # 129, 9
print("g, poly, deg, (t^7+1) mod g, (t^3+1) mod g, port agrees")
for g in GS:
    r7, r3 = gf2_mod(T7_1, g), gf2_mod(T3_1, g)
    agree = (r7 == polymod_lean_port(T7_1, g)) and (r3 == polymod_lean_port(T3_1, g))
    print(f"{g}, {poly_str(g)}, {deg(g)}, {r7}, {r3}, {agree}")

in7 = [g for g in GS if gf2_mod(T7_1, g) == 0]
not3 = all(gf2_mod(T3_1, g) != 0 for g in GS)
print("in_gf2_7 filter =", in7, "| Lean claims [23, 29, 127] ->", in7 == [23, 29, 127])
print("not_in_gf2_3 =", not3, "| trivially by degree (min deg g =", min(deg(g) for g in GS), "> 3):", min(deg(g) for g in GS) > 3)

# irreducible factorisation of t^7+1 over GF(2): (t+1)(t^3+t+1)(t^3+t^2+1)
f = [3, 11, 13]
prod = 0
acc = 1
for p in f:
    # carry-less multiply
    r = 0
    x, y = acc, p
    while y:
        if y & 1:
            r ^= x
        x <<= 1; y >>= 1
    acc = r
print("(t+1)(t^3+t+1)(t^3+t^2+1) == t^7+1:", acc == T7_1)
divisors7 = sorted(d for d in range(2, 256) if gf2_mod(T7_1, d) == 0)
print("all divisors of t^7+1 of degree>=1:", divisors7)

# proves-too-much controls: each mutated proposition must be FALSE
muts = {
    "filter = [23, 29]": in7 == [23, 29],
    "filter = [23, 29, 127, 249]": in7 == [23, 29, 127, 249],
    "filter (t^7+1 -> t^6+1 = 65) = [23,29,127]": [g for g in GS if gf2_mod(65, g) == 0] == [23, 29, 127],
    "gs.all (polyMod 129 g != 0)": all(gf2_mod(T7_1, g) != 0 for g in GS),
}
for k, v in muts.items():
    print(f"mutation '{k}' holds? {v}  (expected False)")
