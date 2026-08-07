# EXP-MTBK-306bdb implementation notes (v2, frozen protocol)

This file documents the full-harness implementation used for the DEC-approved
extension of EXP-MTBK-306bdb after `SMOKE-FIND-003`.

## Fixed design points

- Curve set: 5 fixed toy instances with deterministic seeds `1..5`.
- Field size: 16 bits for every instance (as the `generate_instance(seed, 16, min_prime_order_bits=14)` protocol pin).
- Factor bases: each cell uses `m ∈ {3,4,5}` and `b ∈ {0.6, 0.7}` only.
- Target streams:
  - `desc`: 50 targets per `(curve, b)` for descent reporting.
  - `harv`: 50 targets per `(curve, b)` for relation-collection reporting.

## Frozen protocol

- All instance/curve/factor-base/target material is pinned in
  `frozen-instances.yaml`.
- Instance records include:
  curve tuple `p, a, b, n, P, Q, k`, verification checks, and a SHA-256 digest
  over the frozen payload.
- Factor base entries are `size=B=round(p^b)` with `seed=instance.seed` and a
  SHA-256 digest over the full x-coordinate list.
- Target batch entries include stream tag/count and a SHA-256 digest over all
  target points.

The runtime loads `frozen-instances.yaml` and re-computes every frozen component
with the pinned seed stream before starting measurements; any mismatch marks the
run as invalid with `frozen_verification` failures in `raw-result.json`.

## Full run mechanics

- Driver: `code/run_mtbk_full.py` (new, harness-writer path).
- Output writer: `harness.runner.write_run` with immutable run directory.
- Per cell run key:
  `cell_id = (seed, m, b_exp)` and all 5 × 3 × 2 = 30 cells execute in one run.
- For each `cell`:
  - load its factor base (std domain) and BKK domain (`first half`),
  - generate `harv` and `desc` targets from the frozen streams,
  - run both channels under identical code paths:
    - `std`: full `(m-1)`-tuple enumeration over full factor base,
    - `bkk`: `(m-1)`-tuple enumeration over factor-base half only,
  - enforce per-target check-cap and record `timed_out` if exceeded,
  - compute cell metrics (`K*`, checks, found counts, ratio, and theorem gate).
- Theoretical check:
  the BKK gate is the exact combinatorial theorem from
  `KN-FIND-c7d31e`:
  `Pr[at least m-1 of m indices in half] = (m+1)/2^m`.
  This is separately tested with Monte-Carlo draws in each cell (`theorem_index_test`)
  at a fixed reproducible seed.

## Control mapping

- `null_no_bkk`: implemented by toggling only domain selection, keeping target
  stream and all other logic identical.
- `non_interference`: checks share one frozen factor-base object and run stream but
  independent target batches; if a control artifact changed, the verification block
  in raw output records a failure reason.
- `rho_baseline`: baseline is run using harness Pollard-rho on every
  descent target, with matching public-key target list only (seeded from frozen
  streams); this uses the same public instance state and does not read `k`.
- `smoke`: unchanged `run_mtbk_smoke.py` gate must pass before this full run is
  dispatched.

## Non-goals / scope note

- No certificate is emitted per target decomposition in this dataset run.
  Targets are recorded and reproducible; claims are measurement-only as required by
  the experiment contract.
- No new curve families were introduced in this extension.

