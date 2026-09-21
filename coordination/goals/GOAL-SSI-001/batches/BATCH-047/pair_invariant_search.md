# Pair-Invariant Search: Can We Evade Ramanujan?

**Verdict**: NO. All six candidates fail. Candidate 3 (resultant/GCD) is literally
Wesolowski's algorithm in algebraic language — it matches p^{1/3} exactly.

## The six candidates

| # | Invariant | Complexity | Why it fails |
|---|-----------|-----------|--------------|
| 1 | Neighborhood intersection |N₁(i)∩N₁(j)| | O(1) | IS the (A²)_{ij} entry — spectral, only distinguishes d≤2 |
| 2 | Modular polynomial Φ_n(j₁,j₂) | O(n²) | Binary (0 or random); no gradient information |
| 3 | Resultant R_n = GCD test | Õ(n^{1/2}) via MITM | = Wesolowski's algorithm restated: p^{1/3} exactly |
| 4 | Multi-prime evaluation | O(Σℓ_i) | Only tests degree-1; composition → Candidate 3 |
| 5 | Theta function | Requires End | Circular (Barrier 3) |
| 6 | Supersingular polynomial | O(p/12) | Encodes no pair information |

## The deep reason

Candidate 3 reveals the key identity:

> **Wesolowski's meet-in-the-middle on smooth-degree isogenies IS EQUIVALENT TO computing GCDs of specialized modular polynomial compositions.**

The "structured polynomial arithmetic" optimization of the resultant gives
EXACTLY the same Õ(n^{1/2}) = p^{1/6+o(1)} per-table-side cost that Wesolowski
achieves via ℓ-isogeny chain enumeration. They are the SAME algorithm viewed
from different angles. No polynomial-arithmetic speedup exists beyond this
because the Ramanujan property guarantees roots are pseudorandom (no
exploitable algebraic structure in the root locations).

## The unified obstruction (sharpened)

Pair-specific isogeny information lives in:
  Hom(E₁, E₂) = left O₁-ideal I with right order O₂

Testing "does I represent norm n?" (= "does degree-n isogeny exist?") is a
QUATERNION NORM REPRESENTATION problem. The Minkowski bound on the representing
lattice gives norm ≥ p^{1/3}. ANY computable test for norm representation
that doesn't access O₁ directly must enumerate at least p^{1/3} candidates.

## Conclusion

No pair-computable invariant evading Ramanujan has been found or appears
constructible with known mathematics. The p^{1/3} barrier is a convergence
of spectral (Ramanujan), lattice-geometric (Minkowski), and algebraic
(quaternion norm representation) obstructions that all point to the same bound.
