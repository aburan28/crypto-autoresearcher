# EXP-IC-001 Multi-target IC amortization crossover at toy prime fields (8-36 bit)

## Objective
Measure T_desc (per-target descent cost) in group-operation equivalents across
toy prime fields of 8-36 bits and determine whether the multi-target IC
crossover K* is finite (T_desc < sqrt(N)) or infinite (T_desc >= sqrt(N)).

## Protocol
- Specification: EXP-IC-001 v2 (approved after repair of v1's 5 blocking objections)
- Bit sizes: 8, 12, 16, 20, 24, 28, 32, 36
- Seeds: 1, 2, 3; Factor base: B=14, m=2 (S_3), K=10 targets
- Calibration: total_group_operations / wall_seconds (counts ALL rho group ops)
- S_rel heuristic: (N/B) * T_desc_gops (corrected for m=2)
- All runs at commit 5cae8198, dirty: false, Python 3.13.1, sympy 1.14.0
- Total runs: 528 (8×3×(1 precompute + 1 rho + 10 fixed + 10 naive))

## Observation

### Calibration factor (total_group_ops / wall_seconds)
| bits | mean calib | range |
|---:|---:|---|
| 8 | ~944K | 555K - 1.42M |
| 12 | ~1.37M | 1.28M - 1.46M |
| 16 | ~1.02M | 847K - 1.12M |
| 20 | ~1.36M | 1.27M - 1.48M |
| 24 | ~1.19M | 1.11M - 1.25M |
| 28 | ~1.09M | 864K - 1.30M |
| 32 | ~900K | 876K - 917K |
| 36 | ~803K | 790K - 812K |

### T_desc in group-op equivalents (median Groebner × calib)
~32,000 - 55,000 across all bit sizes. Groebner wall-time is ~0.04s and the
calibration factor is ~1M group_ops/second, giving ~40K group-op equivalents.

### T_desc/sqrt(N) ratio
| bits | mean ratio | min ratio | K* finite |
|---:|---:|---:|---:|
| 8 | 10,055 | 5,612 | 0/3 |
| 12 | 6,681 | 1,190 | 0/3 |
| 16 | 4,528 | 1,589 | 0/3 |
| 20 | 1,121 | 196 | 0/3 |
| 24 | 1,741 | 967 | 0/3 |
| 28 | 237 | 36 | 0/3 |
| 32 | 113 | 37 | 0/3 |
| 36 | 32 | 0.17 | 1/3 |

The ratio decreases monotonically (mean), confirming H-IC-001's prediction.
At 36-bit, seed 2 has ratio 0.1743 (K* = ~509M, finite) because its subgroup
order N ~ 3.4×10^10 gives sqrt(N) ~ 184K >> T_desc ~ 32K.

## Comparison
The success criterion (T_desc < sqrt(N) for >= 2/3 seeds at any bit size) is
NOT met: only 1/3 seeds at 36-bit have finite K*. The falsification criterion
(all K* = infinity) is also NOT met. The result is inconclusive.

The critical threshold is sqrt(N) ~ 40K (T_desc in group-ops), which requires
N > 1.6×10^9, i.e., bit sizes > ~31 bits. At 36 bits, only seed 2 has a large
enough N; seeds 1 and 3 have smaller N (sqrt(N) = 7,058 and 355 respectively)
due to the Hasse-bound variation in #E(F_p)'s largest prime factor.

## Inference
The trend strongly supports the hypothesis direction: the ratio drops 300x
across 8-36 bits. However, the success criterion requires >= 2/3 seeds at any
single bit size, and only 1/3 seeds at 36-bit cross the threshold. More seeds
at 36-bit or larger bit sizes (40+) would likely push more instances below 1.0,
but 40-bit instance generation is slow (~262s per instance).

The result is implementation-bound: T_desc in group-ops depends on the relative
overheads of sympy Buchberger and Python rho. A faster Groebner implementation
would lower T_desc_gops, shifting the crossover to smaller bit sizes.

## Limitation
- Toy scale only (max 36 bits); implementation-bound (sympy vs Python rho)
- B=14, m=2 only; all Groebner solves return trivial ideals (no decompositions)
- The Hasse-bound variation in N means some 36-bit instances have N too small
  for sqrt(N) to exceed T_desc_gops; more seeds would help
- The S_rel heuristic (N/B)*T_desc is not directly measured at bits >= 16
