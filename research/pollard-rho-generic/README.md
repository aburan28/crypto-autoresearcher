# Generic prime-field Pollard-rho maintenance lane

This lane explores **constant-factor implementation improvements only** for
Pollard rho on ordinary, prime-order elliptic-curve groups over prime fields.
It does not claim, seek, or test a sub-square-root ECDLP algorithm. The
generic-group lower bound is a model-bound baseline, not an impossibility claim
about non-generic ECDLP algorithms elsewhere in this repository.

The admissible mechanism is a full-point-state r-adding walk whose partition
selection and distinguished-point (DP) test are co-designed to reduce charged
work per *useful, verified collision*. Every gain must retain the same
asymptotic exponent and pay for table setup, canonicalization, DP storage,
transfers, duplicate collisions, escapes, and final scalar verification.

Status: **specified; no experiment is approved or has run.**

## Memo triage

| Direction | Disposition |
|---|---|
| Better-than-rho generic algorithm | Out of scope; needs a distinct non-generic ECDLP mechanism. |
| Fixed-order automorphism fold | Known constant-factor control; excluded from generic curve cells. |
| `x`-only state | Negative control; H041 reports short cycles and low useful-collision yield for its tested construction. |
| Larger `r` / partition tuning | Baseline quality control, not a discovery claim. |
| DP storage / host transfer policy | Included only when fully charged. |
| GPU batch / energy tuning | Deferred to a hardware successor after the portable gate passes. |
| Precomputation / many-query tables | Excluded; a separate amortized model must charge setup, storage, and query count. |

## Semantic deduplication

The corpus-level screen found no standalone contract for full-state r-adding/DP
implementation quality on ordinary prime-order curves. The closest local
artifacts are controls:

- `inputs/h100_session/h039_walk_corr.json`: r=20 serial walk-correlation probe;
- `inputs/h100_session/h040_rho_const.json`: plain/negation collision constants;
- `inputs/h100_session/h041_xonly_walk.json`: x-only negative control;
- `ideas/reviews/DEDUP-20260717T124917-0700.md`: fixed-order automorphism rho
  folding is already catalogued as a known constant factor.

A positive pilot would remain **TOY-EVIDENCE**, **HEURISTIC**, and
**MODEL-BOUND** to its implementation and hardware; it would not establish a
new generic algorithm, a below-rho exponent, or a deployed-curve weakness.

## Frozen records

- `RQ-RHO-001.yaml` — research question
- `H-RHO-001.yaml` — falsifiable hypothesis
- `EXP-RHO-001-contract.yaml` — review-required protocol
- `literature.md` — checked anchors and boundaries
- `TASK-20260718-RHO-REDTEAM.yaml` — independent review handoff

## Exactly one next action

Obtain the red-team review specified in `TASK-20260718-RHO-REDTEAM.yaml`; do
not implement or run `EXP-RHO-001` until that review accepts the
accounting/correctness gates or records a versioned repair.
