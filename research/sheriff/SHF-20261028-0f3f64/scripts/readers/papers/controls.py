#!/usr/bin/env python3
"""Positive/negative (proves-too-much) controls for this reader's checks.
Self-contained; reads nothing from crypto. Usage: python3 -I controls.py

1. Lean stripper (same algorithm as lean_text_scan.py): a planted `sorry` and
   `native_decide` in code must be flagged; the same words in a line comment,
   a nested block comment and a string must not.
2. Twist-lemma recount: with a wrong twist order (#E^t := #E, i.e. no twist)
   the 'hypothesis class has 0 violations' check must FAIL (violations > 0),
   and with the excluded class (r = l-1) the lemma must fail as the paper's
   tightness remark predicts.
3. Prime counts: variants of the P4 statement (range edges, residue class,
   all primes); only the residue-class and all-primes variants discriminate.
4. GF(2): t^4+t+1 (=19, order 15) and t^5+t^2+1 (=37) must not divide t^7+1;
   t^3+t+1 (=11) and t+1 (=3) must.
5. f64: the exact overflow threshold is n ~ 2^256 - 2^201; 2^256 - 2^203
   must not overflow n^4, 2^256 - 2^199 and 2^256 - 1 must.
"""
import collections
import re
from fractions import Fraction


def strip(src):
    out, i, n, depth = [], 0, len(src), 0
    while i < n:
        if depth == 0 and src.startswith("--", i):
            j = src.find("\n", i)
            i = n if j < 0 else j
            continue
        if src.startswith("/-", i):
            depth += 1
            i += 2
            continue
        if depth and src.startswith("-/", i):
            depth -= 1
            i += 2
            continue
        if depth:
            out.append("\n" if src[i] == "\n" else " ")
            i += 1
            continue
        if src[i] == '"':
            j = i + 1
            while j < n and src[j] != '"':
                j += 2 if src[j] == "\\" else 1
            out.append('""')
            i = j + 1
            continue
        out.append(src[i])
        i += 1
    return "".join(out)


planted = '''/-! doc: sorry native_decide /- nested sorry -/ still comment -/
theorem a : 1 = 1 := by sorry
theorem b : True := by native_decide -- trailing sorry
def s := "sorry native_decide"
-- sorry
theorem c : 2 = 2 := rfl
'''
code = strip(planted)
hits = [(ln, t) for ln, line in enumerate(code.splitlines(), 1)
        for t in ("sorry", "native_decide") if re.search(r"(?<![\w.`])" + t + r"(?!\w)", line)]
print("1. stripper hits on planted text:", hits, "expected [(2, 'sorry'), (3, 'native_decide')]:",
      hits == [(2, "sorry"), (3, "native_decide")])


def sieve(n):
    s = bytearray([1]) * (n + 1)
    s[0] = s[1] = 0
    for i in range(2, int(n ** 0.5) + 1):
        if s[i]:
            s[i * i::i] = bytearray(len(s[i * i::i]))
    return [i for i in range(n + 1) if s[i]]


viol_wrong = viol_excl = 0
for p in [q for q in sieve(199) if q >= 5]:
    sq = [0] * p
    for y in range(p):
        sq[y * y % p] += 1
    cub = collections.Counter(x * x * x % p for x in range(p)).items()
    for b in range(1, p):
        nE = 1 + sum(m * sq[(c + b) % p] for c, m in cub)
        for l in (3, 5, 7):
            if nE % l or p % l == 0 or p % 3 != 1:
                continue
            r = p % l
            if r != l - 1 and nE % l == 0:  # wrong twist: #E^t := #E
                viol_wrong += 1
            if r == l - 1 and (2 * p + 2 - nE) % l == 0:
                viol_excl += 1
print(f"2. wrong-twist violations in hypothesis classes (must be > 0): {viol_wrong};"
      f" excluded-class l | #E^t cases with the true twist (must be > 0): {viol_excl}")

P = sieve(5001)
print("3. off-by-one variants:",
      {"p<5000": sum(1 for p in P if 7 <= p < 5000 and p % 6 == 1),
       "5<=p<=5000": sum(1 for p in P if 5 <= p <= 5000 and p % 6 == 1),
       "all primes<=5000 incl 2,3": sum(1 for p in P if p <= 5000),
       "p=5 mod 6": sum(1 for p in P if p <= 5000 and p % 6 == 5)},
      "(the two edge variants are NOT discriminating: 5000 is composite and 5 = 5 mod 6, so"
      " '<' vs '<=' and a start at 5 vs 7 all give 330; the discriminating variants are"
      " 'all primes' and the other residue class, which must differ from 330)")


def gf2_mod(a, m):
    dm = m.bit_length() - 1
    while a and a.bit_length() - 1 >= dm:
        a ^= m << (a.bit_length() - 1 - dm)
    return a


T7 = 0b10000001
print("4. GF(2) t^7+1 mod g == 0:", {g: gf2_mod(T7, g) == 0 for g in (19, 37, 11, 3)},
      "expected {19: False, 37: False, 11: True, 3: True}")

F64_MAX = Fraction((2 ** 53 - 1) * 2 ** 971)
print("5. n^4 > f64::MAX (threshold n ~ 2^256 - 2^201):",
      {"2^256-2^203": Fraction(2 ** 256 - 2 ** 203) ** 4 > F64_MAX,
       "2^256-2^199": Fraction(2 ** 256 - 2 ** 199) ** 4 > F64_MAX,
       "2^256-1": Fraction(2 ** 256 - 1) ** 4 > F64_MAX},
      "expected {False, True, True}")
