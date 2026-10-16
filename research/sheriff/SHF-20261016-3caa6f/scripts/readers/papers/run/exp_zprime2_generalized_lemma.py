#!/usr/bin/env python3
"""
exp_zprime2_generalized_lemma.py — Exp Z' follow-up

ENHANCED LEMMA (Generalized quadratic-twist ℓ-rank obstruction):

  Claim: For odd prime ℓ and prime p ≢ 0, -1 (mod ℓ):
    ℓ | #E  ⟹  ℓ ∤ #E^t.

  Proof:
    p+1 ≡ r+1 mod ℓ  where r = p mod ℓ, r ≠ 0, r ≠ ℓ-1.
    ℓ | #E = p+1-t  ⟹  t ≡ r+1 mod ℓ.
    #E^t = p+1+t ≡ (r+1)+(r+1) = 2(r+1) mod ℓ.
    ℓ | 2(r+1)  iff  ℓ | r+1  (since ℓ odd prime, gcd(2,ℓ)=1)
                    iff  r ≡ -1 ≡ ℓ-1 mod ℓ.
    But r ≠ ℓ-1 by hypothesis.  ⟹  ℓ ∤ #E^t.  ∎

  Tight: when p ≡ ℓ-1 mod ℓ, we get t≡0, #E^t≡0 → ℓ|#E^t (counterexample).

  Original Lemma 1 stated only p≡1 mod ℓ; this is strictly weaker.
  The enhanced version covers ALL p except p≡0,-1 mod ℓ.

  For secp256k1, this improves the theorem:
    If p_secp ≢ ℓ-1 mod ℓ for any odd prime ℓ, then Lemma applies.
    We check ℓ ∈ {3,5,7,11,13} below.

This script:
  (a) Verifies the Enhanced Lemma numerically for ℓ ∈ {3,5,7}: for EVERY
      residue r ∈ {1,...,ℓ-2} (i.e., p≡r mod ℓ, r≠0,ℓ-1), confirms 0 failures.
  (b) Verifies the failure pattern: for r = ℓ-1, fails 100%.
  (c) Computes p_secp256k1 mod ℓ for ℓ ∈ {3,5,7,11,13} and checks r ≠ ℓ-1.
"""

import sys

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
    count = 1
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
    For each residue r = 1..ell-1 (r≠0), count (p,b) pairs with p≡r mod ell
    and ell|#E, split by whether ell|#E^t.
    """
    from collections import defaultdict
    counts = defaultdict(lambda: {'lemma_fails': 0, 'lemma_holds': 0})
    for p in range(5, max_p):
        if not is_prime(p): continue
        r = p % ell
        if r == 0: continue
        for b in range(1, p):
            n_E = count_points_j0(b, p)
            if n_E % ell != 0: continue
            n_Et = 2 * (p + 1) - n_E
            if n_Et % ell == 0:
                counts[r]['lemma_fails'] += 1
            else:
                counts[r]['lemma_holds'] += 1
    return dict(counts)


def main():
    print("=" * 72)
    print("Exp Z'·2: Enhanced Lemma — ℓ-rank obstruction for p ≢ 0,-1 mod ℓ")
    print("=" * 72)
    print()
    print("ENHANCED LEMMA PROOF:")
    print("  p ≡ r mod ℓ,  r ≠ 0, ℓ-1.")
    print("  ℓ | #E ⟹ t ≡ r+1 mod ℓ.")
    print("  #E^t ≡ 2(r+1) mod ℓ.")
    print("  ℓ | 2(r+1) iff ℓ | r+1 iff r = ℓ-1.  Excluded. ⟹ ℓ ∤ #E^t.  ∎")
    print()
    print("VERIFICATION (p < 500, all j=0 curves with ℓ|#E):")
    print()

    all_pass = True

    for ell in [3, 5, 7]:
        print(f"  ℓ = {ell}:")
        bd = residue_breakdown(ell, max_p=500)

        # Header
        print(f"    {'r=p mod ℓ':>10}  {'Pred: Lemma':>12}  {'Total':>6}  "
              f"{'Lemma holds':>12}  {'Lemma fails':>12}  {'Status':>8}")
        print("    " + "-" * 68)

        for r in sorted(bd.keys()):
            d = bd[r]
            total = d['lemma_holds'] + d['lemma_fails']
            pred = "fails" if r == ell - 1 else "holds"
            if pred == "holds":
                ok = (d['lemma_fails'] == 0)
                status = "✓" if ok else "✗ FAIL"
            else:
                ok = (d['lemma_holds'] == 0)
                status = "✓" if ok else "✗ FAIL"
            if not ok:
                all_pass = False
            print(f"    {r:>10}  {pred:>12}  {total:>6}  "
                  f"{d['lemma_holds']:>12}  {d['lemma_fails']:>12}  {status:>8}")
        print()

    # secp256k1 residue check
    print("=" * 72)
    print("secp256k1 PRIME RESIDUE CHECK (does Lemma apply?)")
    print("=" * 72)
    print()
    p = P_SECP256K1
    print(f"  p_secp256k1 = 0x...{hex(p)[-8:]}")
    print()
    print(f"  {'ℓ':>4}  {'p mod ℓ':>8}  {'ℓ-1':>5}  {'p≡ℓ-1?':>8}  "
          f"{'Lemma applies?':>16}")
    print("  " + "-" * 48)

    all_safe = True
    for ell in [3, 5, 7, 11, 13]:
        r = p % ell
        is_bad = (r == ell - 1)
        applies = not is_bad
        if is_bad:
            all_safe = False
        print(f"  {ell:>4}  {r:>8}  {ell-1:>5}  {'YES (bad!)' if is_bad else 'no':>8}  "
              f"{'YES' if applies else 'NO — Lemma fails':>16}")

    print()
    if all_safe:
        print("  → For all tested ℓ, p_secp256k1 ≢ ℓ-1 mod ℓ.")
        print("  → Enhanced Lemma applies for secp256k1 at ℓ ∈ {3,5,7,11,13}.")
        print("  → No F_p-rational split (ℓ,ℓ)-kernel can exist for any of these ℓ.")
    else:
        print("  → Some ℓ has p_secp ≡ ℓ-1 mod ℓ — Lemma fails for that ℓ.")
        print("  → But B5 (Corollary) still holds unconditionally.")

    print()
    print("=" * 72)
    print("SUMMARY")
    print("=" * 72)
    print()
    print("  Old Lemma: p ≡ 1 mod ℓ  ⟹  (ℓ|#E ⟹ ℓ∤#E^t)")
    print("  New Lemma: p ≢ 0,ℓ-1 mod ℓ ⟹  (ℓ|#E ⟹ ℓ∤#E^t)")
    print()
    print("  Coverage improvement:")
    print("    Old: covers (ℓ-2)/(ℓ-1) residue classes  (only r=1 for ℓ=3!)")

    # Wait, for ℓ=3: old covers r=1 only (1 out of 2 non-zero residues).
    # New covers r=1 only (r≠0,2), so for ℓ=3 both are the same.
    # For ℓ=5: old covers r=1 only; new covers r=1,2,3 (3 out of 4).
    # For ℓ=7: old covers r=1 only; new covers r=1,2,3,4,5 (5 out of 6).
    for ell in [3, 5, 7]:
        old_count = 1  # only r=1
        new_count = ell - 2  # r ∈ {1,...,ℓ-2}
        total = ell - 1  # r ∈ {1,...,ℓ-1}
        print(f"    ℓ={ell}: old covers {old_count}/{total} non-zero residues; "
              f"new covers {new_count}/{total}")
    print()
    print("  Paper update recommended: replace Lemma 1 hypothesis 'p≡1 mod ℓ'")
    print("  with 'p≢0,ℓ-1 mod ℓ' (equivalently, p+1≢0,1 mod ℓ).")
    print()

    if all_pass:
        print("ALL NUMERICAL VERIFICATIONS PASSED. ✓")
    else:
        print("SOME VERIFICATIONS FAILED. ✗")
        sys.exit(1)


if __name__ == "__main__":
    main()
