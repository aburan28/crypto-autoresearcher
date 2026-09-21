# Cyclic Pareto V2 Analysis

## Status

`OBSERVATION`, `TOY-EVIDENCE`, `MODEL-BOUND`,
`NOVELTY-UNVERIFIED`.

The exact occupancy sweep confirms that the joint `D2/D3/D5_new` target is
occasionally feasible, but the nominal-occupancy witness is a single
finite-size affine mechanism rather than evidence of a scaling family.

## Scope and integrity

- source commit: `08bfcd8745437f89d4ae68f69a4ba86a780b45ad`
- source SHA-256:
  `957e15408b8acac1777e705c9aa4b3da1768a6618f522b512d16dc1cbccdb497`
- raw-result SHA-256:
  `1b0beb7260e57e0526a97cf55e82a6ff6dc8e925cec1515de07b4f656fa96bca`
- exact cells: 24
- cell enumerations: 6,057,836
- wall time: 153.85 seconds
- maximum resident set: 24,936,448 bytes

`Cell enumerations` includes repeated populations when two occupancy targets
round to the same factor-base size. It is not a unique-set count.

## Occupancy summary

No cell qualifies at target occupancy `0.2`.

At target occupancy `0.5`, only two cells qualify:

- `q=19`, sign-complete, `B=4`: 9 of 36 sets;
- `q=43`, sign-canonical, `B=4`: 294 of 111,930 sets.

At target occupancy `1.5`, qualifying sets occur for every group, usually
after the formal occupancy rounds well above one. These high-occupancy cells
are strongly affected by modular saturation and are not evidence for the
`B=Theta(q^(1/5))` scaling target.

## Affine classification

The 294 nominal `q=43` witnesses form seven multiplicative-scaling orbits:

- `{1,4,7,38}`;
- `{1,4,10,41}`;
- `{1,5,18,35}`;
- `{1,6,17,28}`;
- `{1,7,13,32}`;
- `{1,7,38,41}`;
- `{1,12,28,33}`.

All seven collapse to one full affine class with normal form

`{0,1,2,4}`.

Thus the positive V1 witness is a translated and scaled near progression. The
translation matters: `D1`, `D3`, and `D5` shift by different multiples, so
`D5_new` is not translation invariant. A search over translations is
chargeable fixed-curve preprocessing and must be selected without target
adaptation.

## Higher-occupancy structure

Qualifying normal forms at `q=59`, `B=5` often look like:

- a progression plus an outlier, such as `{1,4,7,10,32}`;
- a sparse progression union, such as `{1,2,11,21,31}`.

Sign-complete `B=6` witnesses are often inverse-symmetric progressions such as
`{+/-1,+/-2,+/-5}` or `{+/-1,+/-4,+/-7}`.

These patterns support a layered hypothesis: one low-complexity additive layer
can compress early sums, while a transverse outlier or second progression can
restore later coverage. The homogeneous one-dimensional coordinate
constructors tested in V3 did not instantiate that mechanism.

## Restricted conclusion

The Stage-A thresholds are feasible in finite cyclic groups. At nominal
occupancy, the observed feasibility is rare and explained by one affine
near-progression class at `q=43`; it does not persist to `q=59`. At high
occupancy, progression-plus-outlier and inverse-symmetric layered shapes
reappear, but saturation prevents an asymptotic inference.

## Next positive experiment

Freeze two layered families before testing:

1. progression plus one transverse outlier;
2. union of two short progressions with independently frozen step sizes.

Sweep group sizes and translations, charge selection as fixed-curve
preprocessing, and compare against occupancy-matched unrestricted and
coordinate nulls. Promote only if `D2` compression and `D5_new` retention
persist as `q` grows.

## Next proof direction

Combine Vosper/Freiman structure for small doubling with a translation-aware
bound on `|5F \ (F union 3F)|`. The key open regime is moderate, not minimal,
doubling: enough structure to reduce `D2` by a constant factor while retaining
constant-fraction fivefold coverage.
