# Implementation Notes — EXP-ECDLP-1ed445

## Approach

Single Python script (`run_character_sum_ladder.py`) implementing all three
stages sequentially. Each stage gates the next via terminating conditions.

## Key implementation decisions

1. **Curve order computation**: Vectorized via numpy Legendre-symbol lookup table.
   For prime p, precompute `leg[x^2 mod p] = +1` for x=1..(p-1)/2, then
   `#E = p + 1 + sum(leg[x^3+ax+b mod p])` as a single numpy operation.
   This is ~100x faster than the naive Python loop with `pow(rhs,(p-1)/2,p)`.

2. **DL table**: Pure Python iteration Q ← Q + G using affine coordinates
   with modular inverse per step. This is the dominant cost (~63% of wall time).
   No batch inversion or projective coordinates — kept simple for auditability.

3. **FFT**: `numpy.fft.rfft` of length N on the indicator vector. Exploits
   conjugate symmetry: `max_{k=1..N-1} |F[k]| = max_{k=1..N//2} |rfft[k]|`.

4. **Seed derivation**: Exact ASCII SHA-256 as specified. Every random draw
   (null positions, AP parameters, theta replacements) derives from the
   documented seed formula and is reproducible from (domain, master_seed, bits).

5. **Ordering control**: The script structurally computes Stage 1 (null + controls)
   before Stage 2 (EC arm). The null_arm_digest is computed and printed before
   any EC curve's DL table is built. In a deterministic single-threaded script
   this is sufficient for the ordering guarantee.

## Deviations from spec environment

- Python 3.12.8 (spec: 3.11.15) — no behavioral impact
- numpy 2.4.4 (spec: 2.4.6) — patch-level difference only

## Performance

- bits=20: ~10s (DL tables for 20 curves)
- bits=22: ~65s
- bits=24: ~600s (null FFTs dominate at larger N)
- bits=26: ~1600s
- B-sweep: ~86s
- Total: 3290s (~55 min), well within 6-hour budget
- Peak memory: estimated <4 GB (largest FFT: rfft of 15.5M-point vector)
