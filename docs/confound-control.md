# Confound control in experiment contracts

`design-experiment` step 3 requires two blocks in every experiment contract
it drafts: a **variable ledger**, which says how each factor that could move a
primary metric is controlled, and **prediction provenance**, which says what
data had been seen when each prediction was written. Together they answer the
two questions a reader asks of any result here: did the arms differ only in
the factor under test, and was the prediction made before the data that tests
it?

Scope: contracts drafted from 2026-10-17 on, and any `review_required` draft
before its approval. A frozen contract is not edited to add them; it gains
them only through the amendment path, like any other protocol change.

## 1. Variable ledger

```yaml
variable_ledger:
  independent:
    - name: arity_m
      levels: [3, 4, 5]
  factors:
    - name: presentation
      treatment: fixed          # fixed | randomized | crossed | measured
      value: chained_S3
      how: every arm builds the chained S_3 system with the same builder
    - name: solver_build
      treatment: fixed
      value: wdsat 987b7f5ef9 + symfull patch (sha256 bound)
      how: one vendored build for every arm
    - name: curve
      treatment: randomized
      how: three curves per n by the frozen selection rule, independent of arm
    - name: host_load
      treatment: measured
      how: recorded per row; affects wall time only, never a primary metric
  comparisons:
    - id: C-arity
      arms: [m3, m4]
      differs_in: [arity_m]
      design: one_factor        # one_factor | factorial | confounded
```

Rules:

- **List every factor that could change a primary metric**, not only the ones
  the design varies. In this program the usual list is: field size `n`; field
  basis; factor-base subspace and its construction; arity and the system's
  presentation (chained or direct, symmetrized or not); solver, build, patches
  and flags; eliminator and library version; curve family and selection rule;
  target sampling; seeds; censoring limits; symmetry breaking; and, for
  wall-time metrics only, host and load.
- **Treatment meanings.** `fixed`: the same value in every arm. `randomized`:
  drawn by a frozen rule that does not depend on the arm. `crossed`: varied
  in a factorial design in which every combination of levels is run.
  `measured`: allowed to vary, recorded per row and analysed as a covariate;
  only for a factor that cannot be fixed.
- **Each comparison names its arms and `differs_in`.** A `one_factor`
  comparison differs in exactly one factor, and every other listed factor is
  `fixed` or `randomized` across those arms. When two factors cannot be
  separated (a solver configuration that exists for only one presentation),
  declare `factorial` and run every combination, or declare `confounded` with
  the reason.
- **Only `one_factor` and `factorial` comparisons may carry a success or
  falsification criterion.** A `confounded` comparison may be reported as an
  observation; it decides nothing. Criteria cite comparison ids.
- **A factor missing from the ledger** that is later found to vary between
  arms voids that comparison, not the run: the evidence record lists it under
  `unresolved_confounds` and the comparison decides nothing.

Example. The `m4-sat-cost-pilot` compared the chained and direct
presentations while also changing the solver configuration, because stock
`-b` symmetry pruning is incomplete on the chained system at m >= 4. Under this ledger
that comparison is `confounded` unless presentation and configuration are
crossed.

## 2. Prediction provenance

```yaml
prediction_provenance:
  - prediction: P1
    first_recorded_in: ledger/proposals/IDEA-20261017-4b1672.yaml
    written_at: '2026-10-17'
    data_seen:
      - path: analysis/ecdlp2m-iteration-20261009/m4-sat-cost-pilot/
        measured: alpha at m=4, l in {3,4,5}, chained S_3, same solver build
    sample_status: in_sample    # out_of_sample | partially_in_sample | in_sample
    overlap: same quantity, same cells, same instrument
```

Rules:

- **`data_seen` lists every result consulted** that measures the predicted
  quantity or a close proxy, including exploratory pilots, other lanes'
  results and published tables. When nothing was consulted it says `[]`
  explicitly, and the Coordinator checks that claim against the commit dates
  of the cited idea and of any pilot on the same quantity.
- **`sample_status`.** `in_sample` when any listed result measured the
  predicted quantity on the same or overlapping cells with substantially the
  same instrument. `partially_in_sample` when only some cells overlap.
  `out_of_sample` otherwise.
- **Only out-of-sample predictions carry success or falsification criteria.**
  An in-sample prediction stays in the contract as a calibration check: it is
  reported and can invalidate an instrument, never support a hypothesis. A
  partially in-sample prediction carries criteria only on its non-overlapping
  cells.
- **No re-dating.** A prediction revised after seeing data gets a new id and
  its own provenance; the original keeps its record.

Example. `IDEA-20261017-4b1672` predicted an m=4 exponent band after the
pilot had already measured that exponent with the same build. That prediction
is `in_sample`: under this rule only its m=5 and direct-presentation cells can
carry the criterion.

## Where it is enforced

- `design-experiment` step 3: the Coordinator writes both blocks and refuses
  approval while either is missing or a criterion rests on a `confounded`
  comparison or an `in_sample` prediction. The contract stays
  `review_required`.
- Not yet machine-checked: `tools/validate_ledger.py` does not read these
  blocks, and `review-evidence` does not yet grade comparisons against the
  ledger.
