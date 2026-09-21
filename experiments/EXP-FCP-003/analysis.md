# EXP-FCP-003 Fixed-curve preprocessing at 32-36 bit toy primes

## Objective
Extend EXP-FCP-002 to 32 and 36 bit primes to test whether the precomp/groebner
ratio continues to grow and crosses the threshold for measurable amortized
savings. Requires Hasse-bound point counting (order_bsgs) for instance
generation above 28 bits.

## Protocol
- Bit sizes: 32, 36
- Seeds: 1, 2, 3
- Factor base: 14, m=2 (S_3), K=5 targets
- All runs at commit 1cb47f7b, dirty: false, Python 3.13.1, sympy 1.14.0
- Total runs: 72 (6 precompute + 6 rho + 30 fixed + 30 naive)

## Observation

### Amortized cost ratio (K=5)
| bits | seed 1 | seed 2 | seed 3 | mean |
|---:|---:|---:|---:|---:|
| 32 | 1.029 | 0.996 | 1.045 | 1.023 |
| 36 | 1.043 | 1.072 | 1.007 | 1.040 |

### Precompute/groebner ratio
| bits | precomp/groeb (mean) |
|---:|---:|
| 32 | 0.0166 |
| 36 | 0.0157 |

### Combined trend (EXP-FCP-002 + EXP-FCP-003)
| bits | precomp/groeb | mean ratio | mean savings |
|---:|---:|---:|---:|
| 16 | 0.41% | 1.125 | -12.5% |
| 20 | 0.78% | 1.169 | -16.9% |
| 24 | 1.36% | 1.067 | -6.7% |
| 28 | 1.49% | 1.061 | -6.1% |
| 32 | 1.66% | 1.023 | -2.3% |
| 36 | 1.57% | 1.040 | -4.0% |

The precomp/groebner ratio plateaus at ~1.6% at 32-36 bits and does not
continue to grow. The amortized cost ratio approaches 1.0 but does not
cross below 0.95.

## Comparison
The ratio approaches 1.0 (from 1.125 at 16 bits to 1.023 at 32 bits) as the
precompute cost grows relative to Groebner time. However, at 36 bits the
ratio rebounds slightly (1.040) and the precomp/groebner ratio decreases
(1.66% -> 1.57%), indicating saturation. The Groebner solve time remains
~0.04-0.05s across all bit sizes because the polynomial system (degree 14,
2 variables) is structurally fixed — only coefficient arithmetic changes,
and sympy handles 36-bit coefficients efficiently.

## Inference
The predicted crossover does not occur. The mechanism (construction cost
grows faster than Groebner cost) is partially correct at 16-32 bits but
saturates. The plateau is consistent with the theoretical analysis: the
Groebner cost is dominated by the polynomial operation count (O(B^2 * D)
where B=14 and D is the Semaev degree), which is independent of p. Only the
coefficient arithmetic cost grows with p, and at toy scale this is a small
fraction of the total.

## Limitation
- Toy scale only (max 36 bits); at crypto scale (128+ bits), coefficient
  arithmetic may dominate and the ratio could grow again.
- B=14, m=2 only; larger factor bases would increase construction cost but
  also make Groebner infeasible for sympy.
- All Groebner solves return trivial ideals; non-trivial systems may differ.
- The plateau at ~1.6% is specific to B=14 and sympy's Buchberger; an
  optimized F4 implementation might show different coefficient arithmetic
  scaling.
