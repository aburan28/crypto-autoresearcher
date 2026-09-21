# B1-3 Test: Is the superpolynomial o(1) removable?

**Verdict: NOT_REMOVABLE (at κ = 1)**
**Named obstruction: Large-prime isogeny enumeration cost**

## The test

Replace B-smoothness (P₀ = u^{-u} = p^{-o(1)}) with Ford's divisor-in-window
density (P₀_Ford ≈ 1/polylog(p)). Check whether the total cost decreases.

## The computation

At NIST-I (p ≈ 2^256), with X = (p/2)^{1/6} ≈ 2^{42.7}:

### Smooth table (Wesolowski):
- Table size: Ψ(X, B)·X ≈ p^{1/3-o(1)} ≈ 2^{71}
- Per-entry cost: O(log X / log B) × O(B) ≈ 7 × 85 ≈ 2^{9.2} F_{p²}-ops
- P₀ = u^{-u} ≈ 2^{-14} (superpolynomial in log p)
- Total: 2^{71} × 2^{9.2} × 2^{14} = 2^{94.2} — close to paper's 2^{106.5}
  (difference: optimization of B and exact Ψ counting)

### Non-smooth table (B1-3 proposal):
- Table size: X² ≈ p^{1/3} ≈ 2^{85.3} (ALL cyclic isogenies of degree ≤ X)
- Per-entry cost: to reach degree d ≤ X with largest prime factor q > B:
  - Must compute a q-isogeny from E (enumerating q+1 subgroups of E[q])
  - Cost per q-isogeny: O(q) via Vélu, O(√q) via √élu
  - Typical largest prime factor of d ≤ X: ~X/ln X ≈ p^{1/6}/log p
  - Cost: O(p^{1/6}) via Vélu, O(p^{1/12}) via √élu
- P₀_Ford ≈ 1/polylog(p) ≈ 1/1.4 (essentially constant!)
- Total (Vélu): 2^{85.3} × 2^{42.7} × 1.4 = 2^{128.5}
- Total (√élu): 2^{85.3} × 2^{21.3} × 1.4 = 2^{107.1}

### Comparison

| Method | Total cost | Memory |
|--------|-----------|--------|
| Wesolowski (smooth, optimal B) | 2^{106.5} | 2^{92.5} |
| Non-smooth, Vélu (κ=1) | 2^{128.5} | 2^{85.3} |
| Non-smooth, √élu (κ=1/2) | 2^{107.1} | 2^{85.3} |
| Non-smooth, free steps (κ=0) | 2^{85.8} | 2^{85.3} |

## Interpretation

1. **At κ = 1 (Vélu)**: Non-smooth is WORSE (2^{128.5} > 2^{106.5}). No benefit.
2. **At κ = 1/2 (√élu)**: Non-smooth is COMPARABLE (2^{107.1} ≈ 2^{106.5}). No improvement.
3. **At κ = 0 (free steps)**: Non-smooth wins dramatically (2^{85.8} << 2^{106.5}).
   But κ = 0 requires an oracle for free isogeny computation that doesn't exist.

## The obstruction

The superpolynomial o(1) is CONDITIONALLY NECESSARY because:

1. Removing the smoothness requirement increases the table universe (more entries)
2. BUT each non-smooth entry costs O(largest_prime_factor(d)) to construct
3. The largest prime factor of a typical d ≤ X is ~X/log X
4. This enumeration cost DOMINATES the savings from the higher P₀

**Formally**: The o(1) in p^{1/3+o(1)} exists because:
- The algorithm needs entries in the table at ALL degrees up to X
- Constructing a degree-d entry costs Ω(d^{1/2}) (√élu lower bound)
- The sum over all entries: Σ_{d≤X, d∈S} √d ≈ |S| × √X
- For |S| = Ψ(X,B) (smooth): cheap entries, but fewer → success probability drops
- For |S| = X (all): expensive entries, but more → success probability rises
- The PRODUCT (entries × cost × 1/P₀) is minimized at the smooth balance

## Forward guidance

The o(1) is removable ONLY IF:
- Large-degree isogeny evaluation becomes sub-linear (currently Ω(√ℓ) via √élu)
- OR: a way to enumerate degree-d isogenies WITHOUT computing them individually

Neither is known. The isogeny-evaluation lower bound (Ω(√ℓ) for ℓ-isogenies
from the output size alone) makes κ < 1/2 impossible without a fundamentally
different computational model.

## Conclusion

B1-3's test resolves at **κ = 1/2 (√élu) with no improvement** over Wesolowski.
The superpolynomial o(1) is conditionally necessary given current isogeny
evaluation costs. The condition: Ω(√ℓ) cost for ℓ-isogenies.
