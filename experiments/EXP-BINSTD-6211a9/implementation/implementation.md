# Implementation notes — EXP-BINSTD-6211a9 / TASK-20261001-a76432

## Provenance

- Field / curve / schoolbook paths adapted from
  `experiments/EXP-CERTBIN-e94b27/impl/{gf2n,curve,macaulay}.py`.
- FIPS 186-4 Appendix D.1.3.1 read from frozen corpus copy
  `inputs/FIPS186-4-BINARY-CURVES/NIST.FIPS.186-4.pdf`
  (`verified_by: executor:TASK-20261001-a76432`). Live NIST URL returned HTTP 403.

## Protocol deviations (recorded, not silent)

1. **M4/WDSat** not run (not authorized; HOLD-J).
2. **Stage 1 M3** uses dense GF(2) Macaulay ranks at `dmax=3` (not a full
   Gröbner basis). First-fall reported from that instrument.
3. **Stage 2 n=29 order**: Hasse-bound + BSGS (`hasse_trace_bsgs`) instead of
   full-field trace enumeration (2^29 inversions infeasible). Method labeled
   per cell in `order_method`.
4. **Stage 2 M3** instance count reduced to 8 (vs Stage-1 ≥20) and labeled;
   `m_a=3` recorded as `instrument_ceiling`.
5. **N1 noise floor** for exact GE ranks is identically 0 (deterministic
   arithmetic); reported as such.
6. **Stage 2 M2 G-membership**: exhaustive census uses class-bit-0 proxy
   (`G_membership_mode: class_bit_proxy`) because strict `[r]P=O` at n=29 with
   `r~2^{28}` is not feasible for a full pair table; certificates verify
   on-curve arithmetic of sampled sums.

## Measured vs modeled

- MEASURED: FIPS parameters (retrieved), P1/M1, Trimoska #E/r/|Fb_E|, M2
  |Fb_E∩V| and lambda_x, M3 ranks, M5 orbit sizes / Fb.
- MODELED: matched rho rows (`sqrt(pi r/(4n))` on C-KK; `0.886 sqrt(r)` else).
- Dual-cite `RQ-NISTBIN-06157b` on every measured M2/M3/M5 yield/cost artifact.

## No deployed-curve break claim

Stages 0–2 are toy / identification only. sect163k1/r2 appear solely as Stage 0
FIPS identity cells.
