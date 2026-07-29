# Experiment Contract: EXP-ECDLP-COORD-EXPANSION-001

## Hypothesis

`HYPOTHESIS`: On generated ordinary prime-order toy curves, a frozen
coordinate factor-base family may retain random-like *new* five-term support
while compressing both `D2` and `D3` enough to justify a recursive
point-advice and batch-query successor.

For exact support sets `Dk=kF`, define

- `D5_nonidentity = D5 \ {O}`;
- `D5_new = D5 \ (D1 union D3)`;
- `h(Q) = #{(U,V) in D2 x D3 : U+V=Q}`;
- `T_perm(Q)=(|D2|+1)/(h(Q)+1)` on supported targets and `|D2|`
  otherwise;
- `Phi=(|D2|+|D3|)*mean_Q(T_perm(Q))^2/|D5|`.

`Phi` is an explicitly uncalibrated support-mass diagnostic. It is not the
generic preprocessing quantity `S*T^2`, because support states are not yet a
packed advice representation.

## Null hypothesis

The tested coordinate families obtain intermediate compression only by
losing total or genuinely new five-term support, or their apparent gain is
reproduced by coordinate-matched public nulls.

A miss narrows only the frozen families, sign policies, curve schedule, and
toy sizes. It is not an additive-combinatorial barrier theorem.

## Two-plane architecture

### Candidate compiler plane

The candidate plane receives only:

- public curve and generator;
- public factor-base construction seed and source records;
- elliptic-curve points in the factor base;
- target elliptic-curve points.

It builds exact point-keyed `D2` and `D3` supports with lexicographically
canonical witnesses and performs point subtraction plus point-table lookup.
It never receives subgroup scalars, `D4`, `D5`, or split-hit census state.

### Audit plane

After every factor base is built and hashed, the audit plane may create:

- a full subgroup point-to-scalar census;
- independent point-keyed `D1` through `D5`;
- canonical reduced coefficient classes;
- ordered multiplicities;
- the exhaustive `D2 x D3` split census.

All audit construction and memory are reported separately and are never
attack advice. Factor-base digests must be identical before and after audit.

## Parameters

- curves: seeded nonsingular prime-order short-Weierstrass curves
- exclusions: trace `0` or `1`, `j in {0,1728}`, composite order, or
  nontrivial cofactor
- development field sizes: 10, 12, and 14 bits
- expanded field sizes: 10, 12, 14, and 16 bits
- current field restriction: `p mod 4 = 3`, selected before and independently
  of the disclosed `p-1` factorization
- curve seeds: one for a development falsifier; at least two for promotion
- relation depth: five
- occupancy target: `lambda=0.5`
- sign-canonical size: smallest even `B` with
  `binomial(B+4,5)/q >= lambda`
- sign-complete size `B=2b`: smallest even `B` with
  `N_5^pm(b)/q >= lambda`, using cancellation-canonical signed classes
- candidates: x interval, square-map image, balanced square/Mobius union
- coordinate nulls: random valid x and SHA-256-ranked public-source x
- secondary null: random subgroup points
- compression-positive control: scalar progression
- development null count: at least 31 draws per stochastic null family
- confirmatory null count: at least 63 draws per stochastic null family
- primary targets: shared uniform nonzero subgroup points
- scan mutations: canonical, reverse, public-hash, and public shuffle

The current curve generator remains restricted to `p mod 4 = 3`. A later
chart-sensitivity successor must add general Tonelli-Shanks and `p mod 4 = 1`
curves before any generic-prime claim.

## Canonical representation accounting

For sign-canonical `F`, the formal class count at depth `k` is
`binomial(B+k-1,k)`.

For sign-complete `F={+/-P_1,...,+/-P_b}`, cancellation-equivalent ordered
tuples reduce to coefficient vectors

`C_k^pm(b)={c in Z^b: ||c||_1 <= k and ||c||_1 = k mod 2}`.

Their exact count is

`1_(2 divides k) + sum_j sum_s 2^s binomial(b,s) binomial(j-1,s-1)`,

where `j<=k`, `j=k mod 2`, and `1<=s<=min(b,j)`.

Canonical multiplicity and formal defect are primary. Ordered multiplicity is
reported only as a diagnostic artifact.

## Metrics

- factor-base field/group operations and accepted-source diagnostics
- immutable factor-base digest before and after audit
- exact `|D1|,...,|D5|`, `|D5_nonidentity|`, and `|D5_new|`
- canonical formal classes, defect, collision energy, maximum multiplicity
- ordered representations, collision energy, and maximum multiplicity
- exact split-hit distribution, split redundancy, and maximum `h(Q)`
- random-permutation first-hit expectation in both one-sided directions
- point-only sampled query mean, median, p95, maximum, and EC operations
- scan-order spread under four public order mutations
- separate `D2`, `D3`, support-mass, serialized JSON bytes, builder deep bytes
- exact compiler EC operations by level
- separately charged `D4`/`D5`, split census, and subgroup-log audit state
- toy Pollard-rho group operations and analytic `sqrt(q)`
- exploratory fitted slopes over at least three sizes

Rank, filtering, sparse linear algebra, individual logarithms, genuine batch
inversion, and compressed recursive codecs are not measured in Stage A.

## Controls

### Positive control

Scalar progression should create visible canonical collisions or intermediate
support compression, normally with a compensating loss in `D5_new`.

### Negative controls

Random-x and SHA-256-ranked source-x use the same public coordinate surface,
fiber stopping rule, and sign policy as candidates. Random subgroup points are
a secondary control and may not replace coordinate nulls.

## Stage-A success criterion

A candidate/sign cell passes on an instance only if, against both coordinate
null medians:

1. `D5_nonidentity` retention is at least `0.9`;
2. `D5_new` retention is at least `0.9`;
3. `|D2|` ratio is at most `0.8`;
4. `|D3|` ratio is at most `0.8`;
5. a preregistered scalar effect score lies in the lower 5 percent tail of
   each coordinate null separately;
6. sampled point-only witnesses verify;
7. scan-order mean spread is at most `1.05`;
8. factor-base hashes are unchanged after audit.

Promotion requires a joint pass on at least 75 percent of expanded instances,
covering all four sizes and at least two seeds. Passing authorizes a Stage-B
packed recursive point DAG, actual batched EC subtraction, matrix-rank, and
target-descent experiment. It does not establish an exponent improvement.

If total `D5` retention passes while `D5_new` fails, classify the observation
as an inverse-cancellation artifact.

The V3 development artifact predates the scalar tail statistic. Its pooled
partial-order dominance count is an uncalibrated score and must not be called
a p-value. V3's scoped negative conclusion rests on the large `D2` effect-size
failure, not that score. Any confirmatory run additionally requires
family-wise correction across candidates, sign modes, occupancies, and charts.

## Falsification criterion

Narrow a candidate if it misses any joint gate. If no frozen family passes,
report:

> No useful intermediate compression was found for these representations and
> curve schedules under this Stage-A contract.

Do not report a coordinate barrier, structured-generic theorem, or generic
ECDLP negative result.

## Reproduction command

Development runs use:

```bash
python3 -B experiments/EXP-ECDLP-COORD-EXPANSION-001/src/coordinate_expansion.py \
  --bit-sizes 10 12 14 \
  --seeds 271828 \
  --null-draws 31 \
  --targets 128 \
  --rho-trials 2 \
  --occupancy-lambda 0.5
```

An immutable expanded run requires a separately reviewed exact command,
resource budget, source hash, independent verifier, and at least 63 null
draws.

## Claim boundary

`TOY-EVIDENCE`, `MODEL-BOUND`, `HEURISTIC`, and `NOVELTY-UNVERIFIED`.
Stage A measures concrete additive geometry and an exact point-only MITM
baseline. It does not produce independent logarithmic relations, solve a
relation matrix, descend an arbitrary target, beat rho, or threaten deployed
keys.
