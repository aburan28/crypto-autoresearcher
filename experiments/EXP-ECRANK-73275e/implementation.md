# Implementation note — EXP-ECRANK-73275e / TASK-20260907-2a3331

Executor implementation of the frozen approved contract
`experiments/EXP-ECRANK-73275e/specification.yaml` version 1
(approved by DEC-20260907-12086e). Observations only; no status
language; no HEUR-1 verdict.

## Provenance

- `source/ecrank_engine.py` and `source/certify76.py` are copies of the
  predecessor files under `experiments/EXP-ECRANK-76a70d/source/`. The
  predecessor is not edited. The audit loads the predecessor engine from
  its committed path via `importlib` (never via `sys.path` shadowing).
- Construction and audit drivers are new modules beside those copies.
- The R6 null family is frozen in `source/null_family.py` before any R6
  step. The infeasibility proof is: keep A, B from the d=1 n=6
  ellipticity quadratic and replace C by a sign-forced C_null so
  A C_null > 0 and B² − 4 A C_null < 0 (no real root).

## Implementation choices (not protocol changes)

- IC-732-1. Audit AT-0/1/2 are the first three records of
  `blind_rederivation_inputs_C3` in the snapshot-bound R3-armB
  `raw-result.json` (stream 0, b_index 0,1,2). Reconstruction replays
  `run_arm.py` IC-15/IC-16/IC-3 with seed 760708.
- IC-732-2. Planted-meet |S| is the synthetic 2-D integer box
  ([-H,H]\{0})² at H=20, N_a = 5|S|, matching R1's known-answer 2-D
  case. Distinct plants (7,8), (11,12), (13,14) for AT-0/1/2 (IV-9).
- IC-732-3. n=8 Bézout enumeration is exhaustive on the integer (a,b)
  coefficient box [-min(H,20), min(H,20)]² with c solved exactly by the
  remaining quadratic. Non-integer (a,b) are outside the enumerated
  scope and are not claimed empty. Recorded in every R5 raw result.
- IC-732-4. Counted-ops convention is the predecessor's IC-1 (Fraction
  arithmetic + isqrt + modular pow). `ops_cap_respected` is the exact
  boolean `counted_ops < 1.0e8` [SR-9].
- IC-732-5. IC-1 exclusions itemized [SR-11]: RNG calls, wall-clock
  reads, JSON/YAML serialization, and filesystem I/O are not counted.

## Deviations

None from the frozen protocol fields. Sample sizes, seeds, H boxes,
controls IV-1..IV-9, and the eight enumerated runs are as specified.
The n=8 coefficient-box restriction (IC-732-3) is a disclosed
implementation scope inside the frozen H box, not an amendment.
