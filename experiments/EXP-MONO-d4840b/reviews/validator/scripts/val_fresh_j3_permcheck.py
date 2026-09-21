"""
Extra robustness check (not required by the task but useful diligence):
does h_pair_from_characters's OUTPUT for a single curve depend on the order
roots are passed in, and does the ACHIEVABLE SET (across curves) still match
even if we feed all 6 permutations of the found roots, not just sorted order?
"""
import itertools

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
    return [x for x in range(p) if (x * x * x + A * x + B) % p == 0]

def h_pair_from_characters_reimpl(roots, chi, p):
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

for p in (101, 103):
    chi = build_chi_table(p)
    order_dependent_examples = 0
    all_perm_pairs = set()
    checked = 0
    for A in range(p):
        for B in range(p):
            roots = cubic_roots_mod_p(A, B, p)
            if len(roots) != 3:
                continue
            checked += 1
            results_for_this_curve = set()
            for perm in itertools.permutations(roots):
                r = h_pair_from_characters_reimpl(list(perm), chi, p)
                results_for_this_curve.add(r)
                all_perm_pairs.add(r)
            if len(results_for_this_curve) > 1:
                order_dependent_examples += 1
    print(f"p={p}: curves checked={checked}, "
          f"curves where root order changes (hp,hm) output: {order_dependent_examples}, "
          f"achievable set over ALL 6 permutations of ALL curves: {sorted(all_perm_pairs)}")
