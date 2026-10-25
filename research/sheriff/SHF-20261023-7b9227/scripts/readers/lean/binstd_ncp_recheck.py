#!/usr/bin/env python3
"""Independent checks for Binstd/{Factorization,YieldCeiling} and NCP/*.

Binstd: GF(2)[X] product of bitmask factors 3*313*471 and irreducibility of
the degree-8 factors (by brute-force trial division); archived hit counts.
NCP: brute-force enumeration of words over {t_1..t_B, v} up to length d,
computing signed counts and sign independently (scan from the right),
checking the affine normal form on ZMod n and the reachability iff.

Usage: python3 -I binstd_ncp_recheck.py <repo-root>
"""
import itertools, json, random, sys
ROOT = sys.argv[1]
out = {}

# ---------------- Binstd ----------------
def pmul2(a, b):
    r = 0
    while b:
        if b & 1:
            r ^= a
        a <<= 1; b >>= 1
    return r
def pmod2(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a
prod = pmul2(pmul2(3, 313), 471)
out["binstd_product_bitmask"] = prod
out["binstd_product_is_x17_plus_1"] = prod == (1 << 17) | 1
out["binstd_bitmask_313_poly"] = [i for i in range(9) if (313 >> i) & 1]
out["binstd_bitmask_471_poly"] = [i for i in range(9) if (471 >> i) & 1]
def irreducible2(m):
    d = m.bit_length() - 1
    for g in range(2, 1 << (d // 2 + 1)):
        if g.bit_length() - 1 >= 1 and g.bit_length() - 1 <= d // 2 and pmod2(m, g) == 0:
            return False
    return True
out["binstd_313_irreducible"] = irreducible2(313)
out["binstd_471_irreducible"] = irreducible2(471)
# YieldCeiling
yc = []
for t in range(1, 60):
    for o in range(0, 60):
        for h in range(0, 60):
            hyp = (0 < t) and (o == t) and (h <= t)
            if hyp and not (4 * h < 5 * o):
                yc.append((t, o, h))
out["yield_ceiling_counterexamples_bruteforce_le59"] = yc
# proves-too-much: drop open_saturated -> counterexample exists
out["yield_ceiling_without_saturation_counterexample"] = next(
    ((t, o, h) for t in range(1, 10) for o in range(0, t + 1) for h in range(0, t + 1)
     if not (4 * h < 5 * o)), None)
ym = {}
for panel in ("stage1-ell89", "stage1-ell89r1"):
    d = json.load(open(f"{ROOT}/experiments/EXP-BINSTD-8bdf86/{panel}/yield-matrix.json"))
    ym[panel] = [(c["ell"], c["hits_tau"], c["hits_open"], c["target_count"]) for c in d["cells"]]
out["binstd_archived_counts"] = ym
out["binstd_lean_pairs_match_json"] = [(h, o) for p in ("stage1-ell89", "stage1-ell89r1") for (_, h, o, _) in ym[p]] == [(16, 40), (40, 40), (20, 40), (40, 40)]

# ---------------- NCP ----------------
def signed_counts(word, B):
    a = [0] * B; negs_right = 0
    for letter in reversed(word):
        if letter == "v":
            negs_right += 1
        else:
            a[letter] += (-1) ** negs_right
    e = (-1) ** sum(1 for l in word if l == "v")
    return e, tuple(a)
def act(word, s, x, n):
    for l in word:          # leftmost first
        x = (-x) % n if l == "v" else (x + s[l]) % n
    return x
rng = random.Random(20261023)
nf_ok = True; trials = 0
for _ in range(3000):
    B = rng.randint(0, 3); n = rng.randint(1, 30)
    s = [rng.randrange(n) for _ in range(B)]
    L = rng.randint(0, 9)
    alphabet = list(range(B)) + ["v"]
    w = [rng.choice(alphabet) for _ in range(L)]
    x = rng.randrange(n)
    e, a = signed_counts(w, B)
    nf_ok &= act(w, s, x, n) == (e * x + sum(ai * si for ai, si in zip(a, s))) % n
    trials += 1
out["ncp_affine_normal_form_random_trials"] = trials
out["ncp_affine_normal_form_ok"] = nf_ok
# proves-too-much: the LEFT-negation convention must fail somewhere
def signed_counts_left(word, B):
    a = [0] * B; negs_left = 0
    for letter in word:
        if letter == "v":
            negs_left += 1
        else:
            a[letter] += (-1) ** negs_left
    return tuple(a)
left_fail = None
for w in itertools.product([0, "v"], repeat=3):
    e, a = signed_counts(list(w), 1)
    if signed_counts_left(list(w), 1) != a:
        left_fail = list(w); break
out["ncp_left_convention_differs_witness"] = left_fail

def penalty(e, a):
    if e == 1:
        return 0 if all(x >= 0 for x in a) else 2
    return 1
reach_ok = True; cases = 0
for B in range(0, 4):
    maxd = {0: 7, 1: 7, 2: 6, 3: 5}[B]
    alphabet = list(range(B)) + ["v"]
    seen = {}
    for L in range(0, maxd + 1):
        for w in itertools.product(alphabet, repeat=L):
            sh = signed_counts(list(w), B)
            seen.setdefault(sh, L)
    for d in range(0, maxd + 1):
        reachable = {sh for sh, L in seen.items() if L <= d}
        # all (e,a) with formula <= d
        R = range(-d, d + 1)
        formula = {(e, a) for e in (1, -1) for a in itertools.product(R, repeat=B)
                   if sum(abs(x) for x in a) + penalty(e, a) <= d}
        reach_ok &= reachable == formula
        cases += 1
out["ncp_reachability_iff_bruteforce_cases"] = cases
out["ncp_reachability_iff_ok"] = reach_ok
# proves-too-much: penalty 1 instead of 2 for e=+1 with a negative coordinate is false
wrong = None
for d in range(0, 5):
    for a in itertools.product(range(-2, 3), repeat=1):
        e = 1
        if any(x < 0 for x in a) and sum(map(abs, a)) + 1 <= d and sum(map(abs, a)) + 2 > d:
            wrong = dict(e=e, a=a, d=d); break
    if wrong: break
out["ncp_penalty_2_needed_witness"] = wrong
print(json.dumps(out, indent=1))
