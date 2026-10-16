#!/usr/bin/env python3
"""
exp_zdoubleprime_lemma_extended.py — Exp Z'' (Thread 6 follow-up)

Extends Enhanced Lemma numerical verification to ell in {11, 13}.

ENHANCED LEMMA (recap):
  For odd prime ell and prime p ≢ 0, -1 (mod ell), and E/F_p ordinary:
    ell | #E  =>  ell ∤ #E^t.
  Proof: r = p mod ell in {1,...,ell-2}.
    t ≡ r+1 mod ell.  #E^t ≡ 2(r+1) mod ell.
    ell | 2(r+1) iff r = ell-1.  Excluded.  QED.
  Tight: r = ell-1 is a genuine counterexample.

This script:
  (a) Verifies for ell in {11, 13}: residue r in {1,...,ell-2} → 0 failures.
  (b) Verifies failure pattern: r = ell-1 → 100% failures.
  (c) Extends secp256k1 residue safety check to ell up to 29.

Note: for j=0 curves (y^2 = x^3 + b) over F_p with p ≡ 2 mod 3,
the curve is supersingular (t=0) and both E, E^t have #E = p+1.
These are EXCLUDED from the Lemma (which requires "ordinary").
The script skips p ≡ 2 mod 3 to avoid spurious supersingular cases.
"""

import sys
from collections import defaultdict

P_SECP256K1 = (
    0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
)


def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    i = 3
    while i * i <= n:
        if n % i == 0: return False
        i += 2
    return True


def count_points_j0(b, p):
    """Count #E for y^2 = x^3 + b over F_p (j=0 curve)."""
    count = 1  # point at infinity
    for x in range(p):
        rhs = (pow(x, 3, p) + b) % p
        if rhs == 0:
            count += 1
        else:
            leg = pow(rhs, (p - 1) // 2, p)
            if leg == 1:
                count += 2
    return count


def residue_breakdown(ell, max_p=500):
    """
    For ell and all primes p < max_p with p ≡ 1 mod 3 (ordinary j=0),
    p ≠ ell, enumerate j=0 curves with ell | #E.
    Split by residue r = p mod ell and whether ell | #E^t.
    Returns dict: r -> {'lemma_holds': int, 'lemma_fails': int}
    """
    counts = defaultdict(lambda: {'lemma_fails': 0, 'lemma_holds': 0})
    for p in range(5, max_p):
        if not is_prime(p): continue
        if p == ell: continue
        if p % 3 != 1: continue  # skip supersingular (p≡2 mod 3)
        r = p % ell
        if r == 0: continue
        for b in range(1, p):
            n_E = count_points_j0(b, p)
            if n_E % ell != 0: continue
            # t = p+1 - #E  => #E^t = p+1+t = 2(p+1) - #E
            n_Et = 2 * (p + 1) - n_E
            if n_Et % ell == 0:
                counts[r]['lemma_fails'] += 1
            else:
                counts[r]['lemma_holds'] += 1
    return dict(counts)


def print_table(ell, bd):
    total_instances = 0
    all_pass = True
    print(f"  ell = {ell}:")
    print(f"    {'r=p mod ell':>12}  {'Pred':>10}  {'Total':>6}  "
          f"{'Lemma holds':>12}  {'Lemma fails':>12}  Status")
    print("    " + "-" * 72)
    for r in sorted(bd.keys()):
        d = bd[r]
        total = d['lemma_holds'] + d['lemma_fails']
        total_instances += total
        pred = "fails" if r == ell - 1 else "holds"
        if pred == "holds":
            ok = (d['lemma_fails'] == 0)
        else:
            ok = (d['lemma_holds'] == 0)
        status = "PASS" if ok else "FAIL !!!"
        if not ok:
            all_pass = False
        print(f"    {r:>12}  {pred:>10}  {total:>6}  "
              f"{d['lemma_holds']:>12}  {d['lemma_fails']:>12}  {status}")
    print(f"    Total instances: {total_instances}")
    print()
    return all_pass, total_instances


def main():
    print("=" * 76)
    print("Exp Z'': Enhanced Lemma extended verification — ell in {11, 13}")
    print("=" * 76)
    print()
    print("Scope: j=0 ordinary curves (p ≡ 1 mod 3) over F_p, p < 500.")
    print("For each (ell, p, b), check: ell|#E => ell∤#E^t (Lemma holds)")
    print("or ell|#E^t (Lemma fails, expected only for r = ell-1).")
    print()

    all_pass = True
    grand_total = 0

    for ell in [11, 13]:
        print(f"Computing residue breakdown for ell = {ell}... ", end="", flush=True)
        bd = residue_breakdown(ell, max_p=500)
        print("done.")
        ok, n = print_table(ell, bd)
        all_pass = all_pass and ok
        grand_total += n

    print("=" * 76)
    print(f"Grand total instances checked: {grand_total}")
    print()

    # secp256k1 extended residue safety check
    print("=" * 76)
    print("secp256k1 EXTENDED RESIDUE SAFETY (ell up to 29)")
    print("=" * 76)
    print()
    p = P_SECP256K1
    print(f"  p_secp256k1 = 0x...{hex(p)[-12:]}")
    print()
    print(f"  {'ell':>4}  {'r = p mod ell':>14}  {'ell-1':>6}  "
          f"{'r = ell-1?':>11}  {'Lemma applies?':>15}")
    print("  " + "-" * 56)

    # Primes up to 29
    primes_to_check = [ell for ell in range(3, 30) if is_prime(ell)]
    all_safe = True
    for ell in primes_to_check:
        r = p % ell
        is_bad = (r == ell - 1)
        if is_bad:
            all_safe = False
        applies = not is_bad
        bad_str = "YES (bad!)" if is_bad else "no"
        applies_str = "YES" if applies else "NO (fails)"
        print(f"  {ell:>4}  {r:>14}  {ell-1:>6}  {bad_str:>11}  {applies_str:>15}")

    print()
    if all_safe:
        print("  -> secp256k1 is SAFE for all ell in {3,5,7,11,13,17,19,23,29}.")
        print("  -> No F_p-rational split (ell,ell)-kernel for any of these ell.")
    else:
        safe = [ell for ell in primes_to_check if (p % ell) != ell - 1]
        unsafe = [ell for ell in primes_to_check if (p % ell) == ell - 1]
        print(f"  -> SAFE ell: {safe}")
        print(f"  -> Lemma fails for ell: {unsafe}")
        print("  -> B5 Corollary still holds unconditionally (Honda-Tate).")

    print()
    print("=" * 76)
    print("COVERAGE SUMMARY")
    print("=" * 76)
    print()
    print("  Enhanced Lemma verified numerically for ell in {3,5,7} (Exp Z')")
    print(f"  and now for ell in {{11,13}} (Exp Z'').  Grand total: "
          f"16562 + {grand_total:,} = {16562 + grand_total:,} instances.")
    print()
    print("  Residue coverage per ell:")
    print(f"  {'ell':>4}  {'Valid residues (not 0,ell-1)':>30}  "
          f"{'Coverage':>10}")
    print("  " + "-" * 48)
    for ell in [3, 5, 7, 11, 13]:
        valid = ell - 2
        total_nz = ell - 1
        print(f"  {ell:>4}  {valid:>30}  "
              f"  {valid}/{total_nz} = {valid/total_nz*100:.1f}%")

    print()
    if all_pass:
        print("ALL VERIFICATIONS PASSED. Enhanced Lemma confirmed for ell in {3,5,7,11,13}.")
    else:
        print("SOME VERIFICATIONS FAILED.")
        sys.exit(1)
    print()


if __name__ == "__main__":
    main()
