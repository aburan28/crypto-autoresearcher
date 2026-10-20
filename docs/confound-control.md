# Confound control in experiment contracts

`design-experiment` step 3 requires these blocks in every experiment contract
it drafts:

- a **variable ledger**, which says how each factor that could move a
  primary metric is controlled, and which includes an A/A comparison;
- **prediction provenance**, which says what data had been seen when each
  prediction was written;
- **transfer obligations**, when a claim moves the problem across a map such
  as an isogeny, cover, descent or change of coordinates.

`review-evidence` then grades each comparison in a `confound_assessment`.
Together they answer the questions a reader asks of any result here: did the
arms differ only in the factor under test, how large is the noise floor, was
the prediction made before the data that tests it, and does the map preserve
what the claim needs?

Scope: contracts designed from 2026-10-18 on must carry the ledger and the
provenance; two drafts of 2026-10-17 carry them as the first use. A frozen
contract is not edited to add them; it gains them only through the amendment
path, like any other protocol change.

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
    - name: variable_order
      treatment: fixed
      how: one frozen order per instance; the A/A arm permutes it
    - name: host_load
      treatment: measured
      how: recorded per row; affects wall time only, never a primary metric
  comparisons:
    - id: C-arity
      arms: [m3, m4]
      differs_in: [arity_m]
      design: one_factor        # one_factor | factorial | absolute | aa | confounded
    - id: C-aa-order
      arms: [m4, m4-reordered]
      differs_in: [variable_order]
      design: aa
  crosses_map: false            # true requires transfer_obligations (section 4)
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
  `fixed` or `randomized` across those arms. An `absolute` comparison is one
  arm read against a stated threshold, with every factor fixed or randomized.
  An `aa` comparison differs only in a nuisance factor (section 3). When two
  factors cannot be separated (a solver configuration that exists for only
  one presentation), declare `factorial` and run every combination, or
  declare `confounded` with a `reason`.
- **Only `one_factor`, `factorial` and `absolute` comparisons may carry a
  success or falsification criterion.** An `aa` comparison sets the noise
  floor, which criteria may cite as the threshold a difference must exceed. A
  `confounded` comparison may be reported as an observation and decides
  nothing. Criteria cite comparison ids.
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

## 3. A/A comparison

Every ledger carries at least one comparison with `design: aa`: two arms that
differ only in a nuisance factor, such as seed, variable order, a re-encoding
of the same system, or a second independent build of the same input. Its
spread is the noise floor against which every decisive comparison is read: a
difference between arms that is not larger than the A/A spread is not a
difference. A contract whose metric has no noise, such as an exact census,
says so in `aa_not_applicable` instead.

Example. The normal-basis-window contract re-encodes the polynomial-basis
system in a random field basis. The two systems describe the same subspace,
so any change in solver cost between them is representation noise, and the
basis comparison is read against that spread.

## 4. Transfer obligations

When any claim moves the problem across a map, the ledger says
`crosses_map: true` and the contract lists each map:

```yaml
transfer_obligations:
  - map: change of coordinates, polynomial basis to normal basis of F_(2^n)
    kind: coordinate_change   # isogeny | cover | descent | lift | field_extension |
                              # restriction_of_scalars | isomorphism | coordinate_change | other
    source: descended system for V in polynomial-basis coordinates
    destination: the same subspace written in normal-basis coordinates
    preserves: [field, curve, group order, subgroup, the subspace V as a set]
    changes: [support of the Boolean system, Frobenius becomes a cyclic shift]
    controls:
      - kind: coordinate_isomorphism   # methodology controls item 3
        comparison: C-aa-basis
      - kind: matched_random           # methodology controls item 4
        comparison: C-nb-rand
    assessment: experiments/EXP-.../transfer-assessment.json
```

Rules:

- **Type the map.** Name what it preserves and what it changes. A property
  the claim needs that is not under `preserves` is an open obligation, not an
  assumption.
- **Two controls are required.** A `coordinate_isomorphism` or
  `identity_map` control separates the effect of the representation from the
  effect of the map. A `matched_random` control, with the same field, size
  and dimension, separates the map's structure from chance. Each control
  names the ledger comparison that runs it. The other controls in the
  methodology, such as the source baseline and transported versus reselected
  data, are listed when they apply.
- **Attach the transfer assessment.** `assessment` points to a draft built
  from the `transfer` skill's template, with every obligation classified.
  Its weakest open obligation bounds what the experiment can claim.

## 5. Review gate

`review-evidence` writes, for every ledger comparison of the reviewed
experiment, one row of the evidence record's `confound_assessment`:

```yaml
confound_assessment:
  - comparison: C-arity
    verdict: isolated         # isolated | randomized | not_isolated
    basis: arms ran with the same build, curves drawn by the frozen rule
```

The verdict says what happened in the runs, not what the contract planned: a
factor that the plan fixed but the runs did not hold is `not_isolated`. Any
`not_isolated` comparison caps the record's strength at `preliminary`, and it
cannot carry support or refutation. In-sample predictions are reported as
calibration only.

## Where it is enforced

- `design-experiment` step 3: the Coordinator writes the blocks and refuses
  approval while one is missing or a criterion rests on a non-decisive
  comparison or an `in_sample` prediction. The contract stays
  `review_required`.
- `tools/validate_ledger.py` checks the shape of every block on any contract
  that carries one, and requires the ledger and the provenance on contracts
  designed from 2026-10-18 on: an error once approved, an advisory while a
  draft. It refuses a success or falsification criterion that cites a
  confounded comparison or an in-sample prediction, a missing A/A arm,
  a map without its two controls, and evidence on a ledgered experiment that
  does not grade every comparison or that claims more than `preliminary`
  strength over a `not_isolated` one. It matches identifiers in criterion
  text, so criteria must cite comparisons and predictions by id.
