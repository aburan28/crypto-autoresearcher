# Pure Mathematical Core API Amendment V7

## Status and precedence

Status: `review_required`.

This file narrowly amends `pure-core-api-v6.md` and takes precedence on every
item below. It does not authorize source writing or any execution action.

## Canonical chart scalar

Let `u0 = u mod p` be the one charged field reduction. On success:

```text
CandidateCore.fixture.u = u0
```

The raw input `u` is not retained anywhere in the output. Therefore raw inputs
congruent modulo `p` produce equal mathematical outputs and equal counters.

## Fixed literals and reductions

The source uses ordinary integer literals `2`, `3`, `4`, and `27` as inputs to
the abstract field multiplication wrapper. The wrapper itself returns the
canonical residue. There is no preceding `% p` expression and no
`field_reductions` charge for a fixed literal.

`field_reductions` counts exactly one event on every call that reaches chart
scalar validation: canonicalizing input `u` to `u0`. It is zero on every
failure before that phase and exactly one thereafter. In particular,
`CurveInput(5,0,0)` fails singularity with `field_reductions=0`.

For every successful call, the complete counters are exactly:

```text
integer_remainder_tests=R(p)
field_reductions=1
field_additions=58
field_subtractions=156
field_multiplications=151
field_squarings=76
field_negations=24
field_inversions=18
point_membership_checks=24
chart_curve_transforms=1
chart_point_transforms=6
unordered_pairs_enumerated=21
ec_additions=21
secant_branches=12
tangent_branches=6
vertical_pairs_excluded=3
fiber_witnesses_inserted=18
sort_keys_emitted=6+F
representative_keys_compared=18-F
slope_collision_checks=sum_R binom(|W_R|,2)
```

Here `R(p)` is the exact trial-division remainder count, and `F` is the returned
number of fibers.

## Returned chart labels

Let `sorted_chart_points` be the exact tuple obtained by sorting the six
transformed affine points by `(x,y)`.

The same tuple is used without copying or reordering for all three roles:

```text
CandidateCore.fixture.factor_base.points = sorted_chart_points
pair-enumeration source labels index sorted_chart_points
every Witness(i,j,...) indexes sorted_chart_points
```

No transform-order tuple is retained in the output.

On every success:

```text
sum_R len(W_R) = 18
representative_keys_compared = 18-F
sort_keys_emitted = 6+F
slope_collision_checks = sum_R binom(len(W_R),2)
```

## Error-index precedence

The exact error-index list in `pure-core-api-v6.md` controls type failures.

The broader factor-base sentence is narrowed as follows:

- wrong point object type uses `TYPE_MISMATCH` and `(3,i)`;
- wrong `x` or `y` exact type uses `TYPE_MISMATCH` and `(3,i,0)` or `(3,i,1)`;
- canonical integer coordinates outside `[0,p)` use `NONCANONICAL_POINT` and
  `(i,)`;
- duplicate, ordering, membership, two-torsion, and sign-completeness failures
  use their own code and `(i,)`.

No point type failure uses `(i,)`.

## Unchanged locks

The prospective singleton source remains absent and unauthorized. Imports,
compilation, tests, execution, campaign wrappers, controls, mutations,
registered seeds, children, and experiment runs remain forbidden.
