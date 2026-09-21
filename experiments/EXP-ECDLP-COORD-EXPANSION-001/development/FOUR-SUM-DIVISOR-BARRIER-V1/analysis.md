# Four-Sum Divisor Barrier V1 Analysis

## Status

`RESTRICTED THEOREM`, `OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`.

The coordinate four-sum reduced supports are larger than `sqrt(q)` on the
tested rows, so an explicitly materialized reduced point algebra already has
more than `sqrt(q)` field dimensions. The preregistered stronger all-row
`B^2.5` gate fails at one small cell. This is a finite count comparison, not
a charged rho-cost lower bound. No lower bound for succinct arithmetic
circuits, resultants, structured quotients, or succinct scheme presentations
follows.

## Exact Run

- source commit: `5b2bb561607536355aac4451c0613c6ecf8b5fe9`;
- curves: `q in {953,3919,15583}`;
- four coordinate families plus scalar-progression positive control;
- `B in {5,8,10}`;
- exact canonical D2, D3, and D4 support;
- exact D2+D2 reconstruction of reduced D4 support;
- 15 family rows;
- zero support symmetric difference;
- wall time: 0.032 seconds;
- peak RSS: 29,982,720 bytes;
- same-code deterministic normalized rerun: exact;
- separate affine red-team reproduction: all 15 point supports, x supports,
  and reduced-support equalities exact.

## Restricted Divisor Theorem

Let `D` be a reduced effective divisor consisting of `m` distinct rational
points on a smooth projective curve.

1. The split coordinate algebra of `D` has dimension `m`.
2. If a nonzero rational function vanishes at every point of `D`, its zero
   divisor has degree at least `m`.
3. A principal divisor has degree zero, so its pole divisor also has degree
   at least `m`.

Therefore an explicit reduced coordinate algebra has dimension `m`, and a
rational function with this zero requirement has pole degree at least `m`.
A generic dense multiplication matrix has `m^2` entries, while an evaluation
basis may represent a diagonal operator with `m` entries. There is no
representation-independent coefficient count of `m+1`.

This theorem does not lower-bound arithmetic-circuit size. A degree-`m`
function may have a succinct product, resultant, or structured quotient
representation.

## Coordinate D4 Support

| q | B | random-x | source-PRF-x | x-interval | rational-union |
|---:|---:|---:|---:|---:|---:|
| 953 | 5 | 70 | 55 | 69 | 69 |
| 3919 | 8 | 326 | 313 | 328 | 329 |
| 15583 | 10 | 693 | 710 | 711 | 691 |

Canonical tuple counts are `70`, `330`, and `715`. Thus larger coordinate
rows retain nearly all canonical four-tuple support.

All 12 coordinate rows exceed `sqrt(q)`:

- ratios `1.78–2.27` at `q=953`;
- ratios `5.00–5.26` at `q=3919`;
- ratios `5.54–5.70` at `q=15583`.

Eleven of 12 exceed `B^2.5`. The exception is the smallest source-PRF-x
cell, with support 55 versus `B^2.5=55.90`. Therefore:

- preregistered all-family explicit-divisor gate: false;
- explicit coordinate-algebra payload versus rho gate: true.

The fitted D4-support slopes against `q` are:

- random-x: 0.822;
- source-PRF-x: 0.917;
- x-interval: 0.836;
- rational-union: 0.826.

These three-point slopes couple `q`, `B`, the curve, and the seed. They are
descriptive toy evidence and do not establish `Theta(B^4)` or any asymptotic
family law. A random-like finite model is regime-dependent, approximately
`min(binomial(B+3,4),q)`.

## Positive Control

Scalar progression D4 support is:

| q | B | D4 support | support / sqrt(q) |
|---:|---:|---:|---:|
| 953 | 5 | 29 | 0.939 |
| 3919 | 8 | 55 | 0.879 |
| 15583 | 10 | 75 | 0.601 |

Its fitted D4 slope is 0.341, and collision multiplicity grows to 21. This
shows that the census detects a genuinely compressed additive divisor rather
than forcing every family above rho.

The control is scalar-defined and not attack-eligible because its point logs
are structurally exposed. Its signed scalar support gives the exact upper
bound `|4R| <= 8B+1`; it is a compression control only.

## Reconstruction

For every family and curve:

- direct canonical D4 reduced support equals the reduced support obtained by
  adding every canonical pair of unique D2 points;
- point-support and multiplicity digests are deterministic;
- no representation is inferred from tuple multiplicity alone.

This is not equality of divisors or convolution measures. At
`q=953, random_x`, direct canonical D4 has total multiplicity 70 while
unique-D2 pairing has total 120, with different multiplicities at 45 of 70
points. Ordered four-draw convolution is a third multiplicity object.
Resultants and norms generally preserve multiplicity, so a successor must
track all three before squarefree reduction.

The reduced-support identity does not compress the computation: the unique
D2-pair attempt surface is already larger than the direct canonical D4 tuple
surface on these sizes.

## Strongest Valid Conclusion

> On the tested coordinate families, the explicit reduced four-sum point
> algebra has dimension above `sqrt(q)`. Any rational function regular and
> vanishing on every reduced support point needs pole degree at least that
> support size.

The strongest negative is restricted:

> Explicit reduced-point-algebra materialization exceeds the numerical
> `sqrt(q)` count on these rows. The result does not convert field storage to
> rho work and does not rule out succinct high-degree circuits, iterated
> resultants, low displacement-rank operators, target amortization, succinct
> presentations, or alternate divisors. Nonreduced thickening itself cannot
> reduce scheme length below its reduction.

## Literature Link

Stange's net-polynomial theorem supplies rational functions
`Psi_v` whose zeros correspond to a vanishing point combination, and
Corollary 5.2 states the exact zero equivalence. For a rank-two net associated
to `(D,T)`, `Psi_(n,1)=0` exactly when `nD+T=O`, subject to the paper's
appropriateness conditions.

This motivates a block norm over the four-sum divisor, but the explicit split
algebra has exactly the large dimension measured here.

## Next Concrete Action

After independently certifying the equality-pair leaves, run
`ITERATED-DIVISOR-RESULTANT-V1-SCHEME-AWARE` as a circuit experiment rather
than another dense divisor table:

1. Separate reduced support, canonical-multiset, ordered-convolution, and
   unique-D2-pair pushforward divisors.
2. Build point-based and x-eliminated D2/D4 objects through a
   product/resultant DAG.
3. Measure multiplicity handling, squarefree reduction, DAG nodes, polynomial
   degrees, coefficient growth, operator structure, target work, and exact
   witness descent.
4. Add fixed-q B sweeps, at least three seeds, scalar progression, matched
   random point sets, and matched random x sets.
5. Charge logical state, actual live bytes, traffic, build/query work, and
   separate rho and BSGS baselines.
