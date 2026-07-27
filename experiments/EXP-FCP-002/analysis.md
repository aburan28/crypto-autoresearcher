# EXP-FCP-002 Fixed-curve preprocessing at extended toy bit sizes (16-28 bit)

## Objective
Test whether fixed-curve factor-base preprocessing provides a measurable
amortized cost advantage over per-target naive rebuilding at toy prime fields
of 16-28 bits, with K=5 targets per curve, factor base B=14, m=2 (S_3
decomposition). Extends EXP-FCP-001 (8-16 bit, K=3) which found no advantage.

## Protocol
- Frozen specification: `experiments/EXP-FCP-002/specification.yaml` (approved)
- Hypothesis: H-FCP-001 (pre-registered prediction: amortized_cost_ratio < 0.95
  at bit sizes >= 20 for at least 2 of 3 seeds)
- Bit sizes: 16, 20, 24, 28
- Seeds: 1, 2, 3
- Factor base: 14 points, m=2 (S_3 decomposition)
- Targets per curve: 5
- Modes: fixed (precompute once, reuse) vs naive (rebuild per target)
- Baseline: Pollard rho per (bits, seed)
- All runs at commit 10cb3510, dirty: false, Python 3.13.1, sympy 1.14.0,
  macOS arm64
- Total runs: 144 (12 precompute + 12 rho + 60 fixed + 60 naive)

## Observation

### Run validity
- 144/144 runs completed_valid
- All runs dirty: false (code pinned at commit 10cb3510)
- All certificates: kind=none (no decompositions found at any bit size,
  as expected since B^2/N << 1 for bits >= 16), or discrete_log for rho
  baselines (all verified: true, verifier: independent-recompute)
- Control comparability: all matched fixed/naive pairs use identical
  curve_id and target points

### Precompute cost (seconds, one per curve)
| bits | seed 1 | seed 2 | seed 3 | mean |
|---:|---:|---:|---:|---:|
| 16 | 0.000204 | 0.000161 | 0.000183 | 0.000183 |
| 20 | 0.000399 | 0.000354 | 0.000377 | 0.000377 |
| 24 | 0.000589 | 0.000594 | 0.000646 | 0.000610 |
| 28 | 0.000624 | 0.000652 | 0.000632 | 0.000636 |

### Rebuild cost (seconds, per naive target, mean of 5)
| bits | seed 1 | seed 2 | seed 3 | mean |
|---:|---:|---:|---:|---:|
| 16 | 0.000361 | 0.000336 | 0.000384 | 0.000360 |
| 20 | 0.000519 | 0.000607 | 0.000524 | 0.000550 |
| 24 | 0.000849 | 0.000857 | 0.000892 | 0.000866 |
| 28 | 0.000926 | 0.000908 | 0.000863 | 0.000899 |

### Groebner solve time (seconds, mean of 5 targets)
| bits | fixed mean | naive mean |
|---:|---:|---:|
| 16 | 0.0440 | 0.0395 |
| 20 | 0.0481 | 0.0406 |
| 24 | 0.0448 | 0.0413 |
| 28 | 0.0429 | 0.0396 |

### Amortized cost ratio (fixed_total / naive_total, K=5)
| bits | seed 1 | seed 2 | seed 3 | mean | <0.95? |
|---:|---:|---:|---:|---:|---:|
| 16 | 1.113 | 1.134 | 1.130 | 1.125 | 0/3 |
| 20 | 1.195 | 1.148 | 1.166 | 1.169 | 0/3 |
| 24 | 1.053 | 0.985 | 1.165 | 1.067 | 0/3 |
| 28 | 1.057 | 1.129 | 0.999 | 1.061 | 0/3 |

### Precompute/groebner ratio trend
| bits | precomp/groeb (mean) |
|---:|---:|
| 16 | 0.0041 |
| 20 | 0.0078 |
| 24 | 0.0136 |
| 28 | 0.0149 |

The ratio increases monotonically, confirming that construction cost grows
faster than Groebner solve cost with field size. However, at 28 bits it is
still only ~1.5% of the Groebner time.

### Pollard-rho baselines
All 12 rho runs solved with verified discrete-log certificates. Group-operation
counts range from 15 (8-bit control) to 4716 (28-bit, seed 3), consistent with
~sqrt(N) scaling.

## Comparison
The amortized cost ratio is >1.0 at 10 of 12 (bits, seed) combinations,
meaning fixed-curve preprocessing is MORE expensive than naive rebuilding at
the current scale. The only sub-1.0 ratios are seed 2 at bits 24 (0.985) and
seed 3 at bits 28 (0.999) — both within noise and far from the 0.95 success
threshold. The precompute/groebner ratio increases with bit size (0.4% → 1.5%)
but is too small at K=5 to produce a measurable advantage: the theoretical
savings at 28 bits would be (K-1)/K * 0.015/1.015 ≈ 1.2%, well below the 5%
threshold and within the Groebner solve noise (~10%).

## Inference
Two explanations are compatible with the data:
1. **Construction cost is genuinely too small**: at toy scale (16-28 bits),
   factor-base construction is dominated by Groebner solving, and no
   amortization strategy can produce a measurable advantage. The precomp/groeb
   ratio may need to reach ~6% (requiring ~40+ bit fields) for the K=5
   amortization to produce >5% savings.
2. **K is too small**: with K=5 targets, the savings fraction is
   (K-1)/K * ratio ≈ 0.9 * 1.5% = 1.4% at 28 bits. At K=50, the savings
   would be 0.98 * 1.5% = 1.5% — still small. The bottleneck is the
   precomp/groeb ratio, not K.

The hypothesis's success criterion is not met. The falsification criterion
requires BOTH no advantage AND no increasing precomp/groeb trend; the trend
does increase, so the combined falsification is not triggered. The result is
inconclusive: the direction is not closed, but the advantage (if it exists)
is below the noise floor at this scale.

## Limitation
- Toy scale only (max 28 bits); the precomp/groeb ratio at crypto scale is
  unknown and may not extrapolate linearly.
- No decompositions were found at any bit size (B^2/N << 1), so all Groebner
  solves return trivial ideals. The cost for non-trivial systems may differ.
- B=14, m=2 only; larger factor bases or higher arity may change the ratio.
- Absolute timings are sympy-bound and macOS-arm64-bound; only within-machine
  ratios are comparable.
- The Groebner solve time does not increase significantly across 16-28 bits
  (0.04-0.05s), suggesting the polynomial operation count dominates over
  coefficient arithmetic cost at this range. The construction cost grows
  because modular exponentiation (quadratic residuosity test) scales with
  log(p), but the absolute cost is still <0.001s.
