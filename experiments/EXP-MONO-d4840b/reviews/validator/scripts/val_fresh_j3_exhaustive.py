"""
Validator J3 -- fresh, independent exhaustive empirical cross-check.
All curve arithmetic, root-finding, and chi-table construction written from
scratch here; h_pair_from_characters reimplemented verbatim (same logic,
own code) -- not imported or copied from any existing file in this repo
or scratchpad.
"""

def build_chi_table(p):
    chi = [0] * p
    e = (p - 1) // 2
    for x in range(p):
        if x == 0:
            continue
        v = pow(x, e, p)
        chi[x] = 1 if v == 1 else -1
    return chi

def cubic_roots_mod_p(A, B, p):
    """Brute-force: find all distinct x in F_p with x^3 + A x + B == 0 mod p."""
    roots = []
    for x in range(p):
        if (x * x * x + A * x + B) % p == 0:
            roots.append(x)
    return roots

def h_pair_from_characters_reimpl(roots, chi, p):
    """Verbatim reimplementation of the exact algorithm under analysis,
    written independently by the validator (own variable names, own loop),
    logically identical to the handoff's quoted code."""
    hp = hm = 0
    for i in range(3):
        others = [q for q in range(3) if q != i]
        j, k = others[0], others[1]
        a = chi[(roots[i] - roots[j]) % p]
        b = chi[(roots[i] - roots[k]) % p]
        if a == 1 and b == 1:
            hp += 1
        elif a == -1 and b == -1:
            hm += 1
    return hp, hm

def exhaustive_scan(p):
    chi = build_chi_table(p)
    observed = {}
    n_curves_z3 = 0
    n_total_AB = 0
    for A in range(p):
        for B in range(p):
            n_total_AB += 1
            roots = cubic_roots_mod_p(A, B, p)
            if len(roots) != 3:
                continue  # not Z=3 (need exactly 3 distinct roots)
            n_curves_z3 += 1
            roots_sorted = sorted(roots)
            hp, hm = h_pair_from_characters_reimpl(roots_sorted, chi, p)
            observed.setdefault((hp, hm), 0)
            observed[(hp, hm)] += 1
    return observed, n_curves_z3, n_total_AB

for p in (101, 103):
    print(f"=== EXHAUSTIVE SCAN p={p} (p mod 4 = {p % 4}) ===")
    observed, n_z3, n_total = exhaustive_scan(p)
    print(f"  total (A,B) pairs scanned: {n_total}, of which Z=3 (3 distinct roots): {n_z3}")
    print(f"  observed (h_+,h_-) set: {sorted(observed.keys())}")
    for pair, cnt in sorted(observed.items()):
        print(f"    {pair}: {cnt} curves")
    print()
