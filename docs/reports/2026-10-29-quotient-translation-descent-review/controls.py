"""Finite-group controls for translation_commutes_iff_two_torsion (2026-10-29 review).

Checks, in every product Z/a x Z/b with a, b <= 12, for every S and T:
  positive:  (forall P, -(P+S)+T == -(P+T+S))  <->  2T == 0
and that three nearby statements are false somewhere:
  M1 conclusion T == 0           (2-torsion T != 0 commutes)
  M2 conclusion 2S == 0          (the dropped stub hypothesis is not the condition)
  M3 iota_S replaced by tau_S    (translations always commute: no 2-torsion content)
Also counts groups/pairs where the left side is false, so the theorem is not
vacuous (both sides take both truth values). Standard library only.
"""
from itertools import product


def group(a, b):
    elems = list(product(range(a), range(b)))
    add = lambda x, y: ((x[0] + y[0]) % a, (x[1] + y[1]) % b)
    neg = lambda x: ((-x[0]) % a, (-x[1]) % b)
    return elems, add, neg, (0, 0)


def main():
    pairs = lhs_false = 0
    m1 = m2 = m3 = 0
    for a in range(1, 13):
        for b in range(1, 13):
            E, add, neg, zero = group(a, b)
            for S in E:
                for T in E:
                    pairs += 1
                    lhs = all(add(neg(add(P, S)), T) == neg(add(add(P, T), S)) for P in E)
                    rhs = add(T, T) == zero
                    assert lhs == rhs, (a, b, S, T)
                    lhs_false += not lhs
                    m1 += lhs != (T == zero)
                    m2 += lhs != (add(S, S) == zero)
                    tau_commutes = all(add(add(P, S), T) == add(add(P, T), S) for P in E)
                    m3 += tau_commutes and not rhs
    print(f"positive: equivalence holds for all {pairs} (S, T) pairs in 144 groups")
    print(f"nonvacuity: left side false for {lhs_false} pairs, true for {pairs - lhs_false}")
    print(f"M1 (T == 0) disagrees on {m1} pairs  -> nearby statement refuted" if m1 else "M1 NOT refuted")
    print(f"M2 (2S == 0) disagrees on {m2} pairs -> nearby statement refuted" if m2 else "M2 NOT refuted")
    print(f"M3 (tau_S in place of iota_S) commutes where 2T != 0 on {m3} pairs -> the [-1] is load-bearing")


if __name__ == "__main__":
    main()
