#!/usr/bin/env python3
"""P3 / P4 / P-N4 (SHF-20261016-3caa6f, SHF-20261017-e4d7f6): independent
recount of the numbers in crypto:papers/structural-completeness/
structural_completeness.tex, from the statements alone (no crypto script is
imported or run).

- P4: primes p = 1 (mod 6), 7 <= p <= 5000; primes <= 5000; primes PARI's
  forprime(p=7,5000) visits; primes p = 1 (mod 6) <= 1000 (split-Jacobian sweep).
- CM-73 norm form 4p = 73 + 3k^2 (p prime, p <= 5000), Legendre (-219/p),
  the Weil-polynomial factorisation identity, class numbers by reduced forms.
- Lemma (quadratic-twist l-rank) check: curves y^2 = x^3 + b, b = 1..p-1, over
  F_p, primes 5 <= p < 500; instance (l, p, b) when l | #E and p != 0 (mod l);
  #E by exact point count; #E^t = 2p + 2 - #E; ordinary iff p = 1 (mod 3);
  l in {3,5,7} all curves, l in {11,13} ordinary curves only.
- secp256k1 p residues; p = 307 example; the Reproducibility LOC table total
  and the line counts of the 16 named PARI scripts at the pinned commit.

Usage: python3 -I structural_recount.py /home/user/crypto <rev>
"""
import collections
import math
import subprocess
import sys

repo, rev = sys.argv[1], sys.argv[2]


def sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


def legendre(a, p):
    r = pow(a % p, (p - 1) // 2, p)
    return -1 if r == p - 1 else r


print(f"commit {rev}")
P = sieve(5000)
print("== P4 ==")
print(f"primes <= 5000: {len(P)}")
print(f"primes p = 1 mod 6 with 7 <= p <= 5000: {sum(1 for p in P if 7 <= p and p % 6 == 1)}  (paper: 330; original: 621)")
print(f"primes visited by forprime(p=7,5000): {sum(1 for p in P if p >= 7)}")
print(f"first/last p = 1 mod 6 in [7,5000]: {min(p for p in P if p >= 7 and p % 6 == 1)}, {max(p for p in P if p % 6 == 1)}")
print(f"primes p = 1 mod 6 with 7 <= p <= 1000: {sum(1 for p in P if 7 <= p <= 1000 and p % 6 == 1)}  (paper: 80)")

print("\n== CM-73 norm form 4p = 73 + 3k^2, p prime <= 5000 ==")
nf = []
for k in range(1, 200):
    v = 73 + 3 * k * k
    if v % 4 == 0 and v // 4 <= 5000 and (v // 4) in set(P):
        nf.append((k, v // 4))
print(f"count: {len(nf)}  (paper: 11)")
print(f"k values: {[k for k, _ in nf]}  (paper: [1,5,9,11,21,25,31,35,41,55,65])")
print(f"primes: {[p for _, p in nf]}")
for p in (19, 37, 79, 109, 349):
    print(f"  Legendre(-219/{p}) = {legendre(-219, p)}")
for k, p in nf[:4]:
    print(f"  p={p}: (2p-73)^2 + 219 k^2 == 4 p^2: {(2 * p - 73) ** 2 + 219 * k * k == 4 * p * p};"
          f" k^2 == (4p-73)/3: {k * k * 3 == 4 * p - 73}; Weil poly T^4 + {2 * p - 73} T^2 + {p * p}")


def reduced_forms(D):
    forms = []
    a = 1
    while 3 * a * a <= -D:
        for b in range(-a + 1, a + 1):
            if (b * b - D) % (4 * a) == 0:
                c = (b * b - D) // (4 * a)
                if c >= a and math.gcd(math.gcd(a, abs(b)), c) == 1 and not (b < 0 and (a == c)):
                    forms.append((a, b, c))
        a += 1
    return forms


for D in (-219, -292, -3):
    f = reduced_forms(D)
    amb = [x for x in f if x[1] == 0 or x[0] == x[1] or x[0] == x[2]]
    print(f"  h({D}) = {len(f)}; reduced forms {f}; ambiguous (order <= 2): {len(amb)}"
          + ("  => cyclic Z/4" if len(f) == 4 and len(amb) == 2 else ""))

print("\n== twist l-rank lemma recount (y^2 = x^3 + b, 5 <= p < 500) ==")
primes = [p for p in sieve(499) if p >= 5]
counts = collections.Counter()
distinct = collections.defaultdict(set)
dropped = []
class_hit = collections.defaultdict(set)
viol = 0
for p in primes:
    sq = [0] * p
    for y in range(p):
        sq[y * y % p] += 1
    cub = collections.Counter(x * x * x % p for x in range(p))
    items = list(cub.items())
    ordinary = p % 3 == 1
    for b in range(1, p):
        nE = 1 + sum(m * sq[(c + b) % p] for c, m in items)
        nT = 2 * p + 2 - nE
        for l in (3, 5, 7, 11, 13):
            if nE % l:
                continue
            if l >= 11 and not ordinary:
                continue
            r = p % l
            if r == 0:
                dropped.append((l, p, b, nE))
                continue
            grp = "357" if l <= 7 else "1113"
            cls = "hyp" if r != l - 1 else "excl"
            typ = "ord" if ordinary else "ss"
            tw = nT % l == 0
            counts[(grp, l, typ, cls, tw)] += 1
            distinct[(grp, cls if typ == "ord" else "ss-" + cls)].add((l, p, nE))
            distinct[(grp, "all")].add((l, p, nE))
            class_hit[(l, cls)].add(r)
            if cls == "hyp" and tw:
                viol += 1


def tot(pred):
    return sum(v for k, v in counts.items() if pred(*k))


for k in sorted(counts):
    print(f"  {k}: {counts[k]}")
t357 = tot(lambda g, l, t, c, w: g == "357")
print(f"l in {{3,5,7}}: total {t357} (paper 24476); ordinary {tot(lambda g, l, t, c, w: g == '357' and t == 'ord')} (8734);"
      f" supersingular {tot(lambda g, l, t, c, w: g == '357' and t == 'ss')} (15742)")
print(f"  hypothesis classes {tot(lambda g, l, t, c, w: g == '357' and c == 'hyp')} (8156), of which supersingular {tot(lambda g, l, t, c, w: g == '357' and c == 'hyp' and t == 'ss')} (0)")
print(f"  excluded class r=l-1 {tot(lambda g, l, t, c, w: g == '357' and c == 'excl')} (16320): ordinary {tot(lambda g, l, t, c, w: g == '357' and c == 'excl' and t == 'ord')} (578),"
      f" supersingular {tot(lambda g, l, t, c, w: g == '357' and c == 'excl' and t == 'ss')} (15742); with l | #E^t {tot(lambda g, l, t, c, w: g == '357' and c == 'excl' and w)}")
print(f"l in {{11,13}} (ordinary only): total {tot(lambda g, l, t, c, w: g == '1113')} (1802); l=11 {tot(lambda g, l, t, c, w: l == 11)} (198);"
      f" l=13 hyp {tot(lambda g, l, t, c, w: l == 13 and c == 'hyp')} (1510); l=13 excl {tot(lambda g, l, t, c, w: l == 13 and c == 'excl')} (94)")
print(f"all: total {tot(lambda *a: True)} (26278); ordinary {tot(lambda g, l, t, c, w: t == 'ord')} (10536);"
      f" ordinary in hypothesis {tot(lambda g, l, t, c, w: t == 'ord' and c == 'hyp')} (9864); violations {viol} (0)")
d_all = len(distinct[("357", "all")] | distinct[("1113", "all")])
d_hyp = len(distinct[("357", "hyp")] | distinct[("1113", "hyp")])
print(f"distinct (l,p,#E): all {d_all} (paper 336); ordinary-hypothesis {d_hyp} (249);"
      f" l in {{3,5,7}}: all {len(distinct[('357', 'all')])} (292), hypothesis {len(distinct[('357', 'hyp')])} (209)")
print(f"hypothesis residue classes with instances: " + ", ".join(f"l={l}: {sorted(class_hit[(l, 'hyp')])}" for l in (3, 5, 7, 11, 13)))
print(f"instances dropped by r = 0 (p = l): {dropped}  (paper: one, (7,7,5) with #E = 7)")

print("\n== secp256k1 p residues ==")
p = 2 ** 256 - 2 ** 32 - 977
print("  " + ", ".join(f"p mod {l} = {p % l}" for l in (3, 5, 7, 11, 13)) + "  (paper: 1, 3, 1, 7, 5)")
odd = [l for l in sieve(29) if l > 2]
print(f"  odd primes l <= 29 with p = l-1 mod l: {[l for l in odd if p % l == l - 1]}  (paper: none)")

print("\n== p = 307 example ==")
print(f"  4*307 = {4 * 307} = 35^2 + 3 = {35 ** 2 + 3}; 307+1-35 = {308 - 35}; 307+1+35 = {308 + 35} = 7^3: {308 + 35 == 343};"
      f" 273 = 3*7*13: {3 * 7 * 13 == 273}; 7^1.5 = {7 ** 1.5:.2f}")

print("\n== Reproducibility table (LOC) ==")
table = {"audit.gp": 235, "cl_o_horizontal.gp": 203, "structural_invariants.gp": 292,
         "vfcg_experiment.gp": 254, "vfcg_variants.gp": 284, "howe_gluing_test.gp": 260,
         "howe_explicit_cover.gp": 274, "cover_complexity.gp": 165,
         "supersingular_reductions.gp": 171, "p256_comparison.gp": 283,
         "multi_curve_audit.gp": 274, "curve_audit_template.gp": 120,
         "generate_cm_curve.gp": 80, "glv_hnp_phase1.gp": 180,
         "fp3_obstruction_secp256k1.gp": 200, "igusa_f43_howe.gp": 58}
print(f"  sum of the 16 stated LOC values: {sum(table.values())}  (paper total: approx 3533)")
actual = 0
for f, v in table.items():
    out = subprocess.run(["git", "-C", repo, "-c", "gc.auto=0", "show", f"{rev}:secp256k1_cm_audit/{f}"],
                         capture_output=True)
    n = out.stdout.count(b"\n") if out.returncode == 0 else None
    actual += n or 0
    print(f"    {f:32} stated {v:4d}  actual lines {n}")
print(f"  actual total lines of the 16 files: {actual}")
