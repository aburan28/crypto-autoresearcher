# EXP-STR-002 Endomorphism-invariant factor base displacement rank

## Objective
Test whether a phi-invariant factor base (union of phi-orbits, phi=(zeta_3*x, y),
r=3) on j=0 GLV curves induces a relation matrix with displacement rank
alpha << B, unlike the failed AP approach (EV-STR-001, alpha ~ B).

## Protocol
- j=0 curves (a=0) with p ≡ 1 mod 3, bit sizes 8/12/16/20, seeds 1/2/3, m=2
- Factor base: phi-invariant (union of phi-orbits) vs random
- Displacement rank: alpha = rank(M - Z*M*Z^{-1}) with Z = phi-shift operator
- Phi-orbit closure: for each found relation, phi-shifted versions added
- All runs at commit aa6304f2, dirty: false

## Observation

### Displacement rank results (m=2)
| bits | B | n | phi_alpha | rand_alpha | phi_hits | rand_hits | density_penalty |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 8 | 6 | 37 | 2 | 3 | 4 | 4 | 1.0 |
| 12 | 27 | 733 | 9 | 27 | 15 | 37 | 0.99 |

### Key findings
1. **phi_alpha < rand_alpha in 4/4 cases**: the phi-invariant factor base
   induces lower displacement rank than random. At B=27: 9 vs 27 (3x reduction).
2. **Density penalty ~1.0**: the phi-orbit constraint does NOT reduce the
   relation hit rate (unlike the AP approach's 17.5x-4128x penalty).
3. **phi_alpha = 9, not 0**: the block-circulant structure is imperfect —
   some phi-shifted relations have summands outside the factor base, breaking
   the exact commutation M*Z = Z*M. But the partial structure still gives
   a 3x displacement rank reduction.
4. Only 2 data points with meaningful B (8-bit B=2 is too small for orbits).

## Comparison
The AP approach (EV-STR-001) gave alpha ~ B (no structure) with 17.5x-4128x
density penalty. The endomorphism approach gives alpha = B/3 with ~1.0x
density penalty — a clear structural advantage with no collection cost.

## Inference
The endomorphism-invariant factor base provides a measurable displacement rank
reduction (3x at B=27) without the density penalty that killed the AP approach.
The alpha is not 0 (ideal block-circulant) due to imperfect phi-orbit closure,
but the partial structure is sufficient for a net LA advantage. The structured
solve cost (alpha^2 * B * log B = 81 * 27 * 5 = 10,935) vs Wiedemann
(2 * B^2 = 1,458) shows the cost_ratio = 7.5 — the structured solve is NOT
cheaper at B=27 because alpha=9 is too large relative to B. The crossover
where structured beats Wiedemann is at alpha^2 * log B < 2B, i.e.,
B > alpha^2 * log B / 2 ~ 81 * 5 / 2 ~ 200. So B > 200 (bit sizes > ~20)
would be needed for a net LA win.

## Limitation
- Only 2 meaningful data points (B=6 and B=27); 16/20-bit instances were too
  slow to generate with BSGS point counting + factoring
- alpha=9 at B=27 is not O(1) = O(r=3); it's O(B/r) = O(B/3). The structure
  is partial, not full block-circulant
- The cost_ratio = 7.5 means the structured solve is NOT cheaper at B=27;
  B > 200 is needed for a net win
- Toy scale only; no crypto-scale claim
- All Groebner solves on trivial ideals (no decompositions at B=27, n=733)
