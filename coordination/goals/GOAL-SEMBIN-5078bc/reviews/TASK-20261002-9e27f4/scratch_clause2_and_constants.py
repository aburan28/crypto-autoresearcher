"""SCRATCH (TASK-20261002-9e27f4, validator). Pure arithmetic: no group operation,
no curve, no F_V statistic. Every number printed is a closed-form evaluation of a
STATEMENT's own formula, labelled scratch, not a measurement.

  A1 (JR-3 clause 2). Line L(K,M) = (1/8) K sqrt(l/min(M,K)) against
     (i)  ENUM with the unit-cost membership test x(Q) in V (an A_FV harvester and a
          V4 arm): ~2 units per test, success |F|/l per test, memory O(1);
          coupon-collector factor H(|F|/2) bounds the full-rank tail;
     (ii) PCS batching 4 K' sqrt(l/w) with K' = |F|/2 + 2 (relations needed once the
          |F|/2 formal identities F + (-F) = 0 are counted free);
     (iii) Koblitz orbit-quotient PCS against the Koblitz form (l -> l/2n, K kept
          |F|+2): ratio 16 (1 + c_can) / n.
  A2 (JR-3 V1 feasibility). ord_n(2) and sigma-stable dimensions at the toy degrees;
     D needed for lambda_2 in [2^-2, 2^6]; whether a sigma-stable D falls there.
  A3 (JR-1 K14). Expected-cost lower bound implied by the explicit tail
     Pr[success within T] <= (T+3)^2/(2l) (Hhan 2402.11269, Thm 3.3 proof,
     type-safe model, transferred to faithful Shoup-model algorithms by Thm C.1):
     E[T] >= sum_t (1 - (t+3)^2/(2l))_+  ~ (2/3) sqrt(2l) = 0.943 sqrt(l),
     and the same with one free negation per charged step (2 handles per op).

Usage: python3 scratch_clause2_and_constants.py > scratch_clause2_and_constants_output.txt
"""
import math


def line(K, M, l):
    return K * math.sqrt(l / min(M, K)) / 8


def A1():
    print("A1  clause-2 line vs known A_FV harvesters (log2 units; scratch arithmetic)")
    for n, h in [(31, 2), (41, 4), (47, 2), (131, 4)]:
        lg = n - math.log2(h)
        l = 2.0 ** lg
        print(f"  n={n} h={h} log2 l={lg:.1f}; 16 sqrt(l) = 2^{4 + lg/2:.1f}")
        for D in sorted({10, 14, 20, int(n / 2) + 2, int(n / 2) + 6, int(n / 2) + 10} - {0}):
            if D >= n:
                continue
            F = 2.0 ** D / h
            K = F + 2
            Kneed = F / 2 + 2
            enum = 2 * l / F * Kneed * (math.log(F / 2) + 0.5772)  # coupon-collector, m=1 worst
            enum_m = 2 * l / F * K                                      # m>=4 mixing, ~full rank
            for M in (1, 2 ** 4, 2 ** 10):
                Ln = line(K, M, l)
                print(f"    D={D:3d} |F|=2^{math.log2(F):.1f} M=2^{math.log2(M):.0f}: line=2^{math.log2(Ln):.1f}; "
                      f"ENUM+membership (m>=4)=2^{math.log2(enum_m):.1f} [{'BELOW line' if enum_m < Ln else 'above'}]; "
                      f"coupon-bound m=1=2^{math.log2(enum):.1f} [{'BELOW' if enum < Ln else 'above'}]; "
                      f"PCS 4K'sqrt(l/w) at w=min(M,K)=2^{math.log2(4*Kneed*math.sqrt(l/min(M,K))):.1f} "
                      f"(ratio to line {4*Kneed*math.sqrt(l/min(M,K))/Ln:.1f})")
    print("  Koblitz form (l -> l/2n, K = |F|+2 as worded) vs orbit-quotient PCS needing |F|/2n + 2 relations:")
    for n in (37, 41, 43, 47, 131, 163):
        for c_can in (1, 2, n):
            ratio = 16 * (1 + c_can) / n
            print(f"    n={n:3d} c_can={c_can:3d}: PCS_orbit / line = 16(1+c_can)/n = {ratio:.2f} "
                  f"[{'ALREADY BELOW the line' if ratio < 1 else 'above'}]")


def ord2(n):
    k, x = 1, 2 % n
    while x != 1:
        x = 2 * x % n
        k += 1
    return k


def A2():
    print("A2  V1 feasibility of the Koblitz (sigma-stable V) sub-clause of clause 1")
    kob_prime = {7: [(0, 4), (1, 2)], 11: [(1, 2)], 13: [(0, 4)], 17: [(1, 2)], 19: [(0, 4), (1, 2)],
                 23: [(0, 4), (1, 2)], 41: [(0, 4)]}  # from scratch_koblitz_identities_output.txt
    for n in (31, 37, 41, 43, 47):
        o = ord2(n)
        stable = sorted({e + o * j for e in (0, 1) for j in range((n - 1) // o + 1) if e + o * j <= n})
        print(f"  n={n}: ord_n(2)={o}; sigma-stable dims={stable}; Koblitz curve with #E/h prime: "
              f"{kob_prime.get(n, 'none')}")
        for a, h in kob_prime.get(n, []):
            lg = n - math.log2(h)
            Dlo = (lg + 3 - 2 + 4 * math.log2(h)) / 4
            Dhi = (lg + 3 + 6 + 4 * math.log2(h)) / 4
            hit = [D for D in stable if Dlo <= D <= Dhi]
            print(f"    a={a} h={h}: lambda_2=|F|^4/(8l) in [2^-2,2^6] needs D in [{Dlo:.2f},{Dhi:.2f}]; "
                  f"sigma-stable D in range: {hit or 'NONE'}; at D=20,21: lambda_2 = 2^{4*20-4*math.log2(h)-3-lg:.0f}, "
                  f"2^{4*21-4*math.log2(h)-3-lg:.0f}")


def A3():
    print("A3  explicit generic constant from Hhan Thm 3.3 proof (eps <= (T+3)^2/(2l)); scratch integral")
    for lg in (40, 64, 129):
        l = 2.0 ** lg
        s = math.sqrt(2 * l)
        ET = (2 / 3) * s - 3
        ET_free_neg = ET / 2
        print(f"  log2 l={lg}: E[T] >= ~(2/3)sqrt(2l) = {ET/math.sqrt(l):.4f} sqrt(l) (every oracle call charged); "
              f"with negation free (2 handles per charged op) >= {ET_free_neg/math.sqrt(l):.4f} sqrt(l); "
              f"VOW column = 0.8862 sqrt(l) [sqrt(pi l)/2, negation map, additions only]")


if __name__ == "__main__":
    A1()
    print()
    A2()
    print()
    A3()
