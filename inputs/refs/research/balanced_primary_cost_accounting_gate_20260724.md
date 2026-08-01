# Balanced-Primary Cost Accounting Gate

Date: 2026-07-24

## Handoff: balanced-primary proxy-cost gate

### Claim or task

Convert the same-instance balanced-primary versus theta-gated Kani comparison
into a receipt-level cost gate before drafting any arXiv-style breakthrough
claim.

### Status

`OBSERVATION / TOY-EVIDENCE / MODEL-BOUND / PROXY-COST / NOT-A-BREAKTHROUGH`

### Assumptions

- Ordinary prime-field fixtures at degrees `23`, `31`, and `39`.
- Existing balanced-primary and theta-gated Kani receipts are taken as fixed
  inputs; no Sage rerun is performed by the accounting script.
- Wall-clock and memory are local implementation measurements.
- Algebraic object sizes, branch counts, theta calls, and output coefficient
  lengths are proxy costs, not normalized field-operation counts.

### Evidence

The parser `experiments/ecdlp_isogeny/iso_balanced_primary_cost_accounting.py`
generated:

```text
experiments/ecdlp_isogeny/iso_balanced_primary_cost_accounting_result.json
```

Hashes:

```text
script: c3d30eb6262e06db4c3cdf3fe944bf2fb843250c22806c6e7efa046915329a6f
result: 3d7171fc09564cfa6e11850d2f05ade5b32260805bf59c6fdf14afaa7b400dfb
```

Same-instance comparison:

| degree | primary sec | Kani sec | Kani/primary | primary resultants | resultant degree each | total resultant degree / d^2 | explicit output elements | Kani theta calls |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 23 | 0.756411291 | 15.21352005 | 20.113 | 3 | 1058 | 6.0 | 59 | 384 |
| 31 | 1.362477541 | 10.461672068 | 7.678 | 3 | 1922 | 6.0 | 79 | 384 |
| 39 | 2.962653708 | 125.205960989 | 42.261 | 3 | 3042 | 6.0 | 99 | 768 |

The balanced-primary receipts separate acquisition counts from decoder costs.
For the three Kani-comparison fixtures, the decoder residual bidegrees are
`[d,d]`, and every nonzero resultant has degree exactly `2*d^2`.  Since the
decoder computes three such resultants in those fixtures, the recorded
algebraic resultant degree total is `6*d^2`.

The same dense-elimination invariant also appears in the supplemental
primary-only degree-13 and degree-17 receipts.  Across degrees
`13,17,23,31,39`, every measured residual bidegree is `[d,d]`, and every
measured nonzero resultant degree is `2*d^2`.

### Interpretation

This strengthens the implementation comparison but weakens the manuscript
claim boundary.  Balanced-primary is faster than the repository-local
theta-gated Kani baseline on these three selected toy fixtures, yet the current
decoder is dense and explicit-map oriented.  The measured `2*d^2` resultant
degree is direct evidence that the present reconstruction backend cannot by
itself support a subquadratic or compact asymptotic claim.

Theory sidecar review classifies the dense decoder obstruction as
`HYPOTHESIS / OBSERVATION / MODEL-BOUND / NOT-A-BREAKTHROUGH`: the `2*d^2`
resultant degree looks structural for the current two-parameter
`(kernel parameter, target scale)` representation, not merely an implementation
artifact.  The reason is that generic sample residuals have full bidegree
`[d,d]`; eliminating the kernel parameter between two such residuals has
generic scale-degree at most and, on the five measured receipts, exactly
`d*d + d*d = 2*d^2`.

Red-team sidecar review agrees that the strongest valid claim remains
reconstruction-stage and receipt-local.  It explicitly rejects any current
general isogeny-complexity improvement, SCALLOP attack, ECDLP consequence,
subquadratic decoder claim, or novelty claim against GGR without a full PDF
audit.

Pole/content diagnostic:

```text
experiments/ecdlp_isogeny/iso_balanced_primary_pole_factor_probe_result.json
script sha256: 6051237e2382edf05ed0b51a0776a3afba85d9bc1496a353c9e9386f2be50746
result sha256: 375ef5b12c5f610a75ea1b4b5251fcd75ee0ac899624a43b87e15c6ce99e3a69
```

On degrees `13,17,23`, primitive-part stripping in the eliminated parameter
removes no nonconstant scale content, and all primitive resultants remain
degree `2*d^2`.  Squarefree stripping does reduce repeated factors, but the
remaining degree is still quadratic: `146,258,486`, matching
`d^2 - 2d + 3` for `d=13,17,23`.

The nearest valid paper statement is:

> Balanced-primary supplies model-bound toy evidence for a direct public-row
> reconstruction backend that outperforms a local theta-gated Kani baseline on
> three selected ordinary fixtures.  The evidence is not a general isogeny
> complexity improvement, a SCALLOP attack, or an ECDLP consequence.

### Failure modes

- No normalized field-operation model is available for either route.
- The fixture family is selected and toy-scale.
- The balanced-primary decoder uses dense residual bidegrees `[d,d]`.
- Every measured nonzero resultant has degree `2*d^2`.
- Explicit output length grows linearly with `d`; no compact representation is
  supplied.
- There is no SCALLOP discriminant-family mapping.
- There is no ECDLP target-descent mechanism.

### Next concrete action

Prove or falsify the leading-term lemma for this representation: symbolically
derive the top `(T,L)` terms of one residual and the top `L^(2d^2)` term of
the two-row resultant.  In parallel, test whether squarefree-first root
extraction improves constants without changing the quadratic asymptotic
obstruction.

### Artifact paths

- `experiments/ecdlp_isogeny/iso_balanced_primary_cost_accounting.py`
- `experiments/ecdlp_isogeny/iso_balanced_primary_cost_accounting_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_pole_factor_probe.sage.py`
- `experiments/ecdlp_isogeny/iso_balanced_primary_pole_factor_probe_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree23_ramified_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree31_ramified_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_primary_degree39_ramified_recovery_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_degree23_recovery_theta_gated_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_degree31_recovery_theta_gated_result.json`
- `experiments/ecdlp_isogeny/iso_balanced_kani_degree39_recovery_result.json`
