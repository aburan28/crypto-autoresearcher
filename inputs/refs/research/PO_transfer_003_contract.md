# Experiment Contract: PO-transfer-003 Bielliptic Norm-Interpolation Transfer

## Candidate

Candidate: use a split genus-2 correspondence to replace raw divisor-list
meet-in-the-middle with low-degree interpolation and factorization.  For

```text
C: y^2 = x^6 + A*x^2 + B
E1: Y^2 = U^3 + A*U + B
```

the degree-2 quotient `pi1(x,y) = (x^2,y)` maps `C` to the target elliptic
curve.  The second involution gives the auxiliary quotient

```text
E2: V^2 = W^3 + A*W^2 + B^2
pi2(x,y) = (B/x^2, B*y/x^3).
```

For a cubic `v(x)`, the principal divisor of `y-v(x)` has affine support at
the roots of

```text
v(x)^2 - (x^6 + A*x^2 + B).
```

Pushing this divisor through `pi1` gives a relation on `E1`.  Interpolating
`v` through a lift of `-lambda*Q` and three factor-base lifts makes the
relation target-coupled before the residual quadratic is factored.

Status before execution: `HYPOTHESIS / UNTESTED / MODEL-BOUND`.

## Hypothesis

The bielliptic quotient exposes target-coupled relations by one cubic
interpolation and one quadratic split test per attempt, with materially less
memory and better rank gained per charged operation than the raw sparse-divisor
MITM in `PO-transfer-002`.

The stronger algorithmic hypothesis is that a structured enumeration or sieve
over the interpolation tuples can make full target recovery cheaper than
Pollard rho.

## Null hypothesis

The quotient-pushed principal divisors are mechanically valid but the need to
choose three factor-base points makes relation collection cubic in the factor
base size, or residual split probability/rank/target descent forces total cost
above rho.  In that case the result narrows the search to batch interpolation,
large-prime elimination, or a lower-dimensional native function family.

## Parameters

- field/curve family: generated prime-order `E1/F_p` with smooth genus-2 cover
  `C`, for toy primes `101`, `211`, and `431`;
- sizes: factor-base sizes chosen near `sqrt(p)` and recorded in the JSON;
- seeds: `20260713`, `20260714`, and `20260715`;
- target: `Q=kG`, with `k` fixed per cell and used only for verifier checks;
- factor base: deterministic public subset of `E1(F_p)` points whose
  `U`-coordinate has a square root and hence lifts to `C(F_p)`;
- relation shape: pushforward of `div(y-v(x))`, with either four factor-base
  interpolation points or one lift of `-lambda*Q` plus three factor-base
  interpolation points;
- baseline: Pollard rho with negation-map estimate `0.886*sqrt(#E1)`;
- comparison: `PO-transfer-002` raw signed-divisor MITM.

## Model Of Computation

- Relation generation may use public curve arithmetic, field arithmetic,
  polynomial interpolation, degree-2 factorization, and known multiples of
  `Q`.
- It may not use factor-base discrete logs or the target scalar.
- Hidden logs and the target scalar may be used only after relation collection
  to verify correctness.
- The primary charged lower bound counts every interpolation/residual test as
  at least one group-operation equivalent, plus public relation verification.
  Raw field-operation proxies and wall-clock time are recorded separately.
- Memory counts factor-base, lift, and retained relation entries; no uncharged
  divisor table is allowed.

## Metrics

- group operations: target-multiple construction and relation verification;
- relation-kernel attempts: cubic interpolations plus residual split tests;
- field operations: explicit proxy count for interpolation/evaluation/factor
  work, reported separately from group operations;
- charged lower-bound operations and ratio to rho;
- memory entries and ratio to `sqrt(#E1)`;
- zero and target relation counts;
- relation-matrix rank and augmented rank;
- target recovery;
- residual split/accept probability;
- wall-clock time;
- fitted log-log exponent for attempts required per rank gained when at least
  three nonzero cells are available.

## Positive Control

Find a public cubic `v` for which `v(x)^2-F(x)` splits into six distinct linear
factors, then verify that the six pushed points sum to the identity on `E1`.

## Negative Control

Flip the sign of exactly one pushed point in the positive-control relation.
The resulting sum must be nonzero.

## Success Criterion

Algorithmic success requires all of:

- at least one genuine relation involving the original public target `Q`;
- full relation-matrix rank and verifier-confirmed target recovery;
- no secret-dependent factor-base, tuple filter, or rank oracle;
- charged lower-bound cost below `1.0x` rho on at least one size and a fitted
  trend not increasing beyond exponent `0.5`, or a greater than `16x`
  improvement over the corresponding recovering `PO-transfer-002` cost with a
  credible decreasing trend across all three sizes;
- evidence from the second quotient that the relation source is native to the
  split correspondence rather than a scalar `E1` pullback or raw divisor MITM.

## Falsification Criterion

The current mechanism is narrowed if any of the following persists across the
three-size sweep:

- no target relations;
- target relations but rank deficiency or failed target recovery;
- recovery only after a cubic-size tuple enumeration whose charged lower bound
  is above rho;
- memory or linear algebra erases the interpolation advantage;
- all accepted relations reduce to symmetric-pair cancellations or another
  scalar pullback.

This falsifies only the tested interpolation family and enumeration model, not
all cover, Prym, Jacobian, or correspondence transfers.

## Proof Track

- Prove the two quotient maps and the induced split-Jacobian correspondence.
- Prove that pushing `div(y-v(x))` through `pi1` gives the recorded `E1`
  relation, including the points at infinity.
- Determine whether the residual quadratic coefficients admit a batch sieve or
  a norm equation that avoids enumerating all factor-base triples.

## Disproof Track

- Derive the expected residual acceptance probability for a public factor base
  of size `B` in a field of size `p`.
- Lower-bound tuple enumeration needed for `B` independent rows.
- Test whether relation rows have structural dependencies beyond random sparse
  matrices.
- Compare the strongest recovering cell against rho and `PO-transfer-002` after
  charging target descent and memory.

## Reproduction Command

```bash
mkdir -p /private/tmp/codex-sage-home
HOME=/private/tmp/codex-sage-home sage experiments/ecdlp_isogeny/po_transfer_003_bielliptic_norm_interpolation.sage \
  --out experiments/ecdlp_isogeny/po_transfer_003_result.json
```

