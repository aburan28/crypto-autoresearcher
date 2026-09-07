# EXP-SEMAEV-002 analysis

Frozen contract: `experiments/EXP-SEMAEV-002/specification.yaml`
(`status: approved`, `claim_tier: toy`).
Dispatch authorization: `DEC-20260906-1c8b5d` (2026-09-06 Coordinator
re-approval, repairing the fabricated citation in `TASK-20260727-010`'s own
`authorized_by` field, which remains unedited and immutable).

## What was computed

Two independent, disjoint classification code paths were built and run
exhaustively over every target in F_p for every (m, p) cell:

- **Method 1 (hull-based, `implementation/newton_sections.py`)**: builds the
  full multivariate integer coefficient dictionary of
  f_{m,t}(x1,...,x_{m-1}) = S_m(x1,...,x_{m-1},t) once per curve (from
  `harness/semaev.py`'s `s3_expr`/`s4_expr`), then for each target reduces
  every monomial's coefficient exactly mod p (never by integer
  lift-and-reduce of a pre-substituted numeric specialization -- the
  reduction is exact modular arithmetic on the formal polynomial identity),
  checks the per-variable degree bound D_m, and classifies SATURATED iff
  every one of the 2^(m-1) box-corner monomials is present with nonzero
  coefficient. This uses no corner-coefficient formula at all -- only the
  elementary convex-geometry fact that a point set bounded inside a box
  whose hull contains every box vertex has hull exactly equal to the box.
- **Method 2 (corner-based, `implementation/corner_classes.py`)**: evaluates
  the m=3 literature closed forms `c_{3,0}=A^2-4Bt`, `c_{3,1}=t^2`,
  `c_{3,2}=1` directly, and for m=4 uses the recursion `c_{4,1}=c_{3,0}^2`,
  `c_{4,2}=t^4`, `c_{4,3}=1` (all three fully independent of ever
  constructing S4), plus `c_{4,0}(t) = S_4(0,0,0,t)` obtained by EARLY
  zero-substitution into the *unexpanded* resultant expression -- a
  distinct computational route from Method 1's full-expansion-then-slice,
  though it is **not** independent of the underlying S4 object itself (no
  closed form for this one class exists in the frozen specification). This
  partial (3-of-4) independence for m=4's base class is disclosed here and
  in `corner_classes.py`'s module docstring, and is not overstated.
- **Exceptional-set prediction (`implementation/exception_sets.py`)**:
  x([r]P0) for 1 <= r <= m-1 via pure elliptic-curve group arithmetic
  (`harness/toycurve.py`'s exact double-and-add), with zero reference to any
  polynomial code path -- fully independent of both classification methods.
- **Curve selection**: deterministic search in increasing max(|A|,|B|)
  under the balanced-representative convention `|v| = min(v, p-v)` (there is
  no native absolute value in F_p; this convention is documented in
  `exception_sets.py` and applied identically at every cell). All 8 cells
  (m in {3,4} x p in {101,103,107,211}) found a curve on the first
  attempted (A,B)=(1,1) satisfying nonsingularity, B a QR, and
  ord(P0) >= 2m-1.

## Results (RUN-SEMAEV-002-a/b/c/d)

| m | p | ord(P0) | predicted Exc | observed Exc (hull) | observed Exc (corner) | identity | nonexc. full-box fraction | cross-method agreement |
|---|---|---|---|---|---|---|---|---|
| 3 | 101 | 21 | {0,76} | {0,76} | {0,76} | true | 1.0 | 1.0 |
| 3 | 103 | 87 | {0,26} | {0,26} | {0,26} | true | 1.0 | 1.0 |
| 3 | 107 | 21 | {0,27} | {0,27} | {0,27} | true | 1.0 | 1.0 |
| 3 | 211 | 223 | {0,53} | {0,53} | {0,53} | true | 1.0 | 1.0 |
| 4 | 101 | 21 | {0,72,76} | {0,72,76} | {0,72,76} | true | 1.0 | 1.0 |
| 4 | 103 | 87 | {0,26,72} | {0,26,72} | {0,26,72} | true | 1.0 | 1.0 |
| 4 | 107 | 21 | {0,27,72} | {0,27,72} | {0,27,72} | true | 1.0 | 1.0 |
| 4 | 211 | 223 | {0,53,72} | {0,53,72} | {0,53,72} | true | 1.0 | 1.0 |

- `m3_calibration_identity_match`: true on every one of the 4 tested m=3
  curves, verified against the FULL EXPANSION (Method 1's coefficient
  dictionary), not against the hardcoded Method-2 formula (which would be
  circular). Exact match: `c_{3,0}=A^2-4Bt`, `c_{3,1}=t^2` (checked at both
  weight-1 corners (D,0) and (0,D) separately), `c_{3,2}=1`.
- `exceptional_set_cardinality`: exactly m-1 at every cell (2 for m=3, 3 for
  m=4), matching the frozen selection rule's exact bound, not merely
  `<= m-1`.
- `cross_method_classification_agreement`: 1.0 at every cell, on the
  required sample (every 10th target plus every predicted-exceptional
  target) -- verified in `raw-result.json`'s `cross_method_sample` field per
  cell. Zero `method_disagreements` were found anywhere (i.e. this held on
  the FULL exhaustive sweep too, not only the sampled subset).
- Interior (non-corner) support fill was in [0.556, 1.0] for m=3 and
  [0.704, 1.0] for m=4 across cells -- recorded descriptively per
  `interior_support_fill_stats`; these interior losses never touch a box
  corner and are explicitly not counted as exceptions, per
  specification.yaml's invalidation_rules.
- Degree-bound violations: 0 at every cell (the per-variable degree bound
  D_m held everywhere it was checked, on the full multivariate expansion).

## CTRL-SEM-CONSISTENCY-BKK001

EV-BKK-001 recorded, at m=3 (among other m), "per-instance support fill 1.0"
on its own sampled targets -- **2 targets per instance**, not an exhaustive
sweep of F_p. This run's exhaustive p=101 result finds exactly 2 exceptional
targets out of 101 (fraction 0.0198). These are not in tension: a 2-target
sample drawn without deliberately targeting the (unknown, until this run)
exceptional set would very likely land on two of the 99 saturated targets.
**This is a plausibility consistency check, not a literal
target-for-target replay** -- this Executor did not re-extract EV-BKK-001's
specific sampled target values from its raw run artifacts
(`experiments/EXP-BKK-001/runs/RUN-BKK-001-*`) to confirm they are literally
disjoint from {0, 76}; that would strengthen the check but was out of this
dispatch's scope. No contradiction is found under either reading. Per rule
12 / the specification's stopping rule, a genuine contradiction would have
been escalated to review-breakthrough rather than resolved here; none arose.

## Falsification-condition scan (RUN-SEMAEV-002-d)

Every falsification condition in specification.yaml was checked
mechanically against the raw data at every cell:

- non-exceptional target losing a box vertex: **none found** (0/8 cells).
- exceptional set exceeding the m-1 bound: **none found** (0/8 cells).
- exceptional set containing an unpredicted target, or a predicted multiple
  saturated: **none found** (set equality held exactly at all 8 cells for
  both methods).
- m=3 calibration identity failure: **none found** (4/4 curves matched
  exactly).
- contradiction with EV-CRYPTO-009 or EV-BKK-001: **none found** (see
  consistency-check note above; this finding is a plausibility check, not a
  formal disproof of any contradiction that a stricter replay might reveal).

`overall_success_criterion_met: true` in `RUN-SEMAEV-002-d/raw-result.json`.

## Scope and limits (claim_tier: toy)

This is a toy-tier, exhaustive computational base-case check at m in {3,4}
over four small primes each, with one curve per (m,p) selected by a frozen
deterministic rule. It is **not** a proof of the all-m corner-coefficient
induction, says nothing about m >= 5 or cryptographic-scale fields, and
claims no sub-rho algorithm regardless of outcome (per
H-SEMAEV-002.interpretation_limits and AGENTS.md rule 7). It computationally
replicates the induction's stated base cases and strengthens the scoped
negative gate recorded as EV-CRYPTO-009 toward "replicated toy-tier"; it is
not an independent proof and does not itself change any hypothesis or
evidence status (that is the Coordinator's act, on review).

Every observation above is reported as a measurement of the tested cells,
parameters, and code; no conclusion beyond claim_tier toy is drawn.
