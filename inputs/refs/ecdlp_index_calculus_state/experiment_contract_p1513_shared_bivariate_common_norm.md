# P1513 Shared Bivariate Common-Norm Contract

Status: `preregistered_theorem_gate`. No scaling run is approved until Phase 0
derives and independently checks the exact common-norm recurrence.

## Objective

Test the nonlinear target-specialized exception preserved by P1512. Keep one
symbolic P1510 two-transition circuit `H(U,W)` with `Theta(r^2)` source-marked
leaves, then intersect its norms over a public target polynomial `T(U)` and the
factor-start polynomial `F(U)` without emitting `Theta(r^3)` specializations,
norm coefficients, quotient state, or source rows.

The complete relation-campaign work and state must have exponent strictly below
`5/2` in `r` on `q=Theta(r^5)`.

This is a theorem gate, not relation collection, blind descent, an ECDLP
algorithm, or a Shoup-bound break.

## Frozen Inputs

- P1513 shared bivariate norm identity and its exact hash;
- P1509 local Hasse source section and audit;
- P1510 global marked-resultant compiler, transcript, and audit;
- both P1511 scoped negatives and independent audits;
- P1512 cycle-length theorem, result, and independent audit;
- immutable P1513-active focus queue, plan, and report, hash-frozen before
  execution.

Any changed input requires a versioned successor contract.

Frozen SHA-256 values:

- shared bivariate norm identity:
  `f3207d0634e04e61e7768548f03014989c65f6319330645cbd1b165f9c00fa73`;
- P1512 cycle-length derivation:
  `7b76a37f27cb137d7ef31d95a235984eda0f266171ef8ded6c6680538704202c`;
- P1512 producer, result, and independent audit result:
  `2c63157fb42afe70777a8d0eeaf02aa2b04b95a62ea7e9c4b27e19d4803ec383`,
  `80d8c7d5424910a37ecd8c4dad829c2cc96bda08b2763cbe21da9623acf54a2d`,
  and `a3eed3439bb22f4068551410c4d3edc931aa9e3fe88cdd3a2cf50a18e647c7ed`;
- P1513-active focus queue, plan, and readable report:
  `9bea8e182ca0a1f7f980cb783dd78b33d3f2b834e9fc100c96c2673561d4775b`,
  `7f6ba860cb11b9469e4772ad399f12ebf740c6bf9ae1c300703be0540a4cebae`,
  and `b56b7e4607e48e3e86175c68ec13a873264b94b3320ca7cbcd4afb2997cf96ea`.

## Admitted Input

The only admitted large algebraic input is one circuit

```text
H(U,W) = product_(i,j) Res_V(
    S3(U,V,x_i),
    S3(V,W,x_j)
),
```

with exactly `r^2` constant-degree bivariate leaves and complete P1510 marker
components. `T(U)` and `F(U)` each have degree `Theta(r)` and public source
labels.

The producer may not instantiate `H` separately at every root of `T` or `F`,
expand a degree-`Theta(r^3)` norm, import endpoint roots, or annotate sources
after common factors are known.

## Required Output

Compute the squarefree common factors of

```text
N_T(W)=Res_U(T(U),H(U,W)),
N_F(W)=Res_U(F(U),H(U,W)),
```

and, for every common root, recover its public target label, A2 pair, A3 start,
and remaining A3 pair. Each row must replay as an exact signed five-factor
elliptic relation, including repeated, vertical, return, infinity, and
nonreduced charts.

A membership bit, determinant zero, unlabeled gcd, component factor, or
post-hoc source table is insufficient.

## Phase 0 Theorem Gate

Before implementation, freeze:

1. the exact bidegrees and coefficient circuits of every leaf and marker;
2. one common-norm algorithm, including every quotient ring and transposed map;
3. a recurrence for base-field operations, coefficient traffic, serialized
   state, peak workspace, and output;
4. the common-factor and target/start/four-source biconditional;
5. multiplicity, exceptional-chart, and normalization rules;
6. complete relation, unsuccessful-batch, rank, factor-log, blind-descent, and
   verification exponents;
7. a trust manifest proving that no `r^3` evaluation grid, norm, matrix, module,
   leaf family, or source dictionary entered the computation.

Calling generic resultant, modular composition, power projection, structured
linear algebra, or circuit factorization is not a recurrence.

## Cost Gate

The shared input circuit has `Theta(r^2)` leaves, while each explicit norm has
degree `Theta(r^3)`. A passing algorithm must be output-sensitive in the common
factor of expected degree `Theta(r)`.

Charge all arithmetic in coefficient extensions and quotient algebras back to
base-field operations. In particular, `r` evaluations of an `r^2`-leaf circuit,
an `r^3` dense coefficient vector, and an `r^3`-dimensional quotient module are
cubic controls even if produced by a named fast backend.

The total exponent must be strictly below `5/2`; equality, fitted toy wall time,
or an uncharged preprocessing phase fails.

## Exact Controls

- P1511 planted products at `r in {4,6,8,12,16,24,32}`;
- deterministic planted bivariate `H` circuits with exactly `r` common norm
  roots and complete target/start/source labels;
- matched random circuits with the same bidegrees and leaf count;
- expanded norms and evaluate/interpolate baselines;
- Sylvester, Bezout, subresultant, quotient-module, modular-composition, and
  power-projection controls with full base-field accounting;
- source-label permutation, deletion, multiplicity, and exceptional-chart
  mutations;
- exhaustive generated ordinary elliptic fixtures after the theorem passes.

## Decision Rule

Record a scoped positive theorem only if one explicit common-norm recurrence
returns every common factor and complete source row with all total time and state
exponents below `5/2`.

Record a scoped negative for the tested algorithm family if any mandatory
object or operation is `Omega(r^(5/2))`. Record `REVISE` if the identities are
exact but the recurrence, source inverse, or exceptional charts remain open.

Even a positive theorem authorizes only a separately frozen tiny exact
implementation. Relation collection, factor-log rank, blind descent, and the
generic sub-rho claim remain separate experiments.

## Independent Audit

The audit must not import candidate helpers. It must independently reconstruct
the shared circuit identity, base-field recurrence, common factors, and every
source row; replay all exceptional charts; and reject mutations to a leaf,
target, start, source code, multiplicity, quotient dimension, recurrence term,
trust input, and claimed exponent.

## Budget

Phase 0 is limited to 7,200 wall-clock seconds, 8 aggregate CPU-hours, 8 GiB
peak memory, and 12 runs. No matrix, norm, or curve scaling is approved by this
contract.
