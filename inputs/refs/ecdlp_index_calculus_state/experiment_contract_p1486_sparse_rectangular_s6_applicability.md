# P1486 sparse rectangular S6 applicability contract

## Objective

Apply the black-box zero-testing and equation-solving bounds of Aichinger,
Grünbacher, and Hametner, *Zero testing and equation solving for sparse
polynomials on rectangular domains* (`arXiv:2305.19669`, 22 March 2026
revision), to the exact P1476 five-term subgroup-domain obligation.

The paper is treated as a theorem. P1486 tests whether its evaluation radius
and the unique reduced equation indicator are sparse enough to give a complete
five-term decision below `L^(3/2)`. A paper-level zero test, a nonzero finder,
or a sparse input `S6` is not a relation algorithm unless equation existence,
source recovery, and all conversion costs pass.

## Frozen lineage

- P1476 result/audit SHA-256:
  `c29426c61c687560b45e38cae1c50f18e89c2846a6d599c6f4583fc98ec70e5f` /
  `752190e01263740ed8b0db73ae4fe3d092797ff1e1991a48438a8f66d2bcc138`.
- P1478 result/audit SHA-256:
  `287a08a131ce7b56bd4e8468eb6c443d7bcba4b7fb2ba13c860866c21902b8df` /
  `d035cba39d08165c4b7dd336d4a095c1c99ff822f8db8c6cf5f3fca3b8c764f9`.
- P1485 result/audit SHA-256:
  `c8b47ff4f086726651b1d020b72cf20a3b23522c71db713533d159a2d8651ead` /
  `c93098d5a76d19fd32fe9aa2d79f767df5edab846ed4146029bb18fce356ccef`.
- Paper: `https://arxiv.org/abs/2305.19669`.

## Exact problem instance

Use the P1477/P1485 L4 and L8 ordinary prime-order fixtures. Let H be the full
order-L multiplicative subgroup of F_p, including x-values that do not lift
over F_p. Lift every x in H to its two points over F_(p^2).

Choose a deterministic nonidentity planted target R in E(F_p) as a signed sum
of five liftable subgroup-x points. On the rectangular domain H^5, define the
equation indicator

`g(x1,...,x5)=1` iff `S6(x1,...,x5,x(R))=0`, else `0`.

Compute g without a symbolic S6 expansion: enumerate all signs of the five
quadratic-closure lifts and accept exactly when their sum is R or -R. Preserve
and replay one exact signed witness, including the sixth target sign, for every
accepted tuple. This is the defining zero-set property of Semaev's sixth
summation polynomial.

## Unique reduced representation

Because H is cyclic and `L | p-1`, the functions

`x -> product_i x_i^(e_i)`, `0<=e_i<L`,

form the character basis of functions on H^5. Compute the unique representative
of g modulo `X_i^L-1` by a separable five-dimensional finite-field Fourier
transform. Record every nonzero coefficient, its hash, support M, density, and
an exact inverse-transform roundtrip to all `L^5` indicator values.

Controls:

- constant-one indicator: Fourier support exactly one and exact roundtrip;
- deterministic random indicator with the same Hamming weight as g: identical
  transform, support, density, and roundtrip accounting;
- the planted S6 indicator: every nonzero value has an EC witness.

No coefficient may be inferred from target secrets or omitted because it is
expensive. Charge the complete direct indicator and Fourier diagnostics.

## Paper bounds and query gate

The paper's general result uses

`t=(p-1)/(p-2)` and radius `floor(log_t M)`.

For equation solving it applies the nonzero test to
`1-S6^(p-1)`. Even the optimistic nonconstant lower bound M=2 must be reported;
if `floor(log_t 2)>=5`, the guaranteed Hamming sphere is already all H^5.

After reduction modulo `X_i^L-1`, the bounded-degree result gives radius
`floor(log_2 M_reduced)`, clamped to N=5. The exact sphere size around a base
tuple is

`sum_(i=0)^k binomial(5,i)*(L-1)^i`.

Report its exact log-L exponent. P1476 requires a complete decision and source
opening with query exponent strictly below `3/2`; hence an integer Hamming
radius at most one, which in this bound requires `M_reduced<4`. Merely having
`M_reduced<32` avoids the full five-coordinate sphere but still does not pass
the P1476 gate.

The paper's quasipolynomial statement fixes the field. Do not hide the growing-p
dependence of t or the equation-indicator conversion inside big-O notation.

## Accounting

Record pair/triple sign-sum preprocessing, complete tuple probes, accepted
tuples, witness replay, indicator storage, forward/inverse transform field
operations, coefficient support, and wall time. The diagnostic transform costs
`Theta(5*L^6)` field operations and is not candidate preprocessing.

The candidate paper bound is charged by the complete guaranteed sphere size,
with one black-box equation-indicator evaluation and source-opening obligation
per point until a witness is found or nonexistence is certified. A planted
early hit cannot replace the complete UNSAT bound.

## Promotion gate

`SPARSE_RECTANGULAR_S6_SIGNAL` requires on both fixtures:

- all direct indicators and every accepted source witness are exact;
- Fourier and inverse Fourier transforms roundtrip exactly;
- constant and random controls behave as specified;
- the reduced S6 indicator has `M<4`, radius at most one, and guaranteed sphere
  exponent strictly below `3/2`;
- the general t-dependent radius also gives a strict sub-`L^(3/2)` sphere;
- source opening and all conversion/preprocessing costs preserve that bound;
- the result is entered into the P1476 relation/rank/descent ledger.

One sparse polynomial, one solution, nonzero testing, a fixed-field asymptotic,
an average/early query, or an exponent below 5 but at least 3/2 does not promote.

## Outputs

- `ecdlp_index_calculus_state/p1486_sparse_rectangular_s6_applicability.json`
- `research/p1486_sparse_rectangular_s6_applicability.md`

## Interpretation boundary

If the reduced equation indicator forces the full H^5 sphere, close this
paper's direct rectangular testing-set strategy for the current S6 subgroup
representation. This does not challenge the paper and does not rule out a new
sparse encoding with fewer than four reduced characters, a variable-reducing
elimination, or P1478's compact transition norm. Any successor must exhibit
that encoding before another domain sweep.
