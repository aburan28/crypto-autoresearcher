# No certificate produced for RUN-ECDLP-bbb42f-4

`required_artifacts` names `runs/RUN-ECDLP-bbb42f-4/certificates/` as
required for this run (the planted-path positive control, the one control
where a claimed solve certificate is expected). This directory is created,
as required, but contains **no certificate file**, and that absence is the
reportable fact rather than an oversight.

## What succeeded

At all three tested bit sizes (20, 24, 28), this run genuinely:

- constructed a real anomalous curve (`N == p`, exact point counting via
  `point_counting.exact_group_order`, independently re-certified via
  `ec_affine.fast_order_certificate`);
- walked a real forward chain of `STEP_PRIMES`-degree ordinary isogenies to
  produce `E_rand` (`kernel_polynomial` / `isogenous_curve_from_kernel`,
  `division_poly.py` + `velu.py`);
- independently re-certified that `E_rand` has the same order `N0 == p` as
  the start curve (again via `fast_order_certificate`, a genuinely separate
  computation from the forward-walk bookkeeping);
- genuinely recovered, via a real bounded BFS from `E_rand` (not by
  assumption), the SPECIFIC reverse path back to the original vertex,
  within the forward path's own degree budget, at all three bit sizes (see
  `runs/RUN-ECDLP-bbb42f-4/results.json`,
  `specific_reverse_path_recovered_within_forward_degree_budget: true`).

## What did not succeed

The contract's control definition additionally requires: "the corresponding
special-curve algorithm is run on the target, the discrete log is pulled
back, and the `[k]P=Q` certificate on the original planted instance
re-verifies." The special-curve algorithm for the E1 (anomalous) route is
Smart-Araki-Satoh-Semaev. A genuine, timed implementation attempt
(`driver/smart_ass.py`) reproduced a specific, well-defined mathematical
obstruction (a coordinate singularity in the final double-and-add
combination step of the naive affine mod-`p^2` lift) identically at 16, 20,
24, and 28 bits. See `implementation.md`, section "Smart-ASS
infeasibility," for the full debug trace and the two known correct fixes
(projective coordinates through a `p`-divisible `Z`-coordinate, or a
formal-group-law power-series logarithm), neither of which could be
implemented and independently verified correct within this run's budget.

**Consequently no `[k]P=Q` certificate exists for this control at any bit
size**, and per the contract's `INV-PLANTED-VOID` rule this makes the
harness VOID for the corresponding unplanted-census reading in
`RUN-ECDLP-bbb42f-1/2/3` until this specific defect is fixed and the
control is re-run. This is recorded here, in `results.json`, in
`implementation.md`, and in the run manifest's `result.valid: false` /
`invalid_reason` field -- consistently, not selectively.
