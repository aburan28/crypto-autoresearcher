# ECDLP-IDEA-121 — Shared bivariate common-norm reporter

## Status and claim labels

- Class: `algorithm`
- Risk band: `conservative`
- State: `deferred_ku_circuit_common_norm_reduction_required`
- Cohort: `20260717-g`
- Evidence scale: theorem and synthetic identity diagnostics only; no ECDLP run
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a compact bivariate circuit, exact norm identity,
  common planted factor, valid relation, or recovered toy source is not an ECDLP break.

## Falsifiable hypothesis

For a generic ordinary prime-field curve and factor base of size `B=N^(1/5)`, one
symbolic source-marked two-transition circuit `H(U,W)` of size `B^(2+o(1))` can be
shared across a degree-`B` public target selector and the degree-`B` factor-start
selector. A circuit-preserving finite-field algorithm computes only the common factors
of the two resulting norms, together with exact target, start, and four transition
source labels, in `N^(lambda+o(1))` time and `N^(mu+o(1))` memory for
`lambda,mu<1/2`. Repeating this operation yields `B+sigma` independent rows, verified
factor logs, and blind masked-target descent below Pollard rho and BSGS.

The claim is false for any proposed reduction if circuit-to-dense conversion, norm
reconstruction, common-factor multiplicity, source splitting, failed batches, rank, or
descent introduces an exponent at least `1/2`.

## Mechanism-new operation

The operation is **compute a source-labelled gcd of two selector norms of one shared
bivariate product circuit without specializing or expanding either norm**. In exact
notation,

```text
N_T(W)=Res_U(T(U),H(U,W)),
N_F(W)=Res_U(F(U),H(U,W)),
```

and the reporter returns `gcd(N_T,N_F)` plus a complete inverse to target/start/four
within-transition source labels.

The operation is new only if one circuit remains symbolic through the norm
intersection. Evaluating `H` at every selector root is the closed IDEA-117 grammar;
factoring a supplied circuit is the IDEA-106 solver substitution; outputting moments or
an unlabeled gcd is the IDEA-053 provenance loss; and minimizing a supplied serial
source automaton is the IDEA-120 state-quotient lane.

## Assumptions

1. `E(F_p)` has a public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target
   `Q=[x]P`, and target-independent signed factor deck of size `Theta(B)`.
2. P1509/P1510's complete addition charts and source-marker conventions extend to one
   symbolic bivariate `H(U,W)` with exactly `Theta(B^2)` constant-degree leaves.
3. Public selector polynomials `T,F` have degree `Theta(B)` and can be constructed
   without source or scalar-log advice.
4. A bounded number of finite-field modular-composition, power-projection, or related
   operations consumes the circuit directly, not a `Theta(B^3)` coefficient/evaluation
   image.
5. Every common factor recovers target, start, all four transition labels, signs,
   repetitions, multiplicity, and exceptional-chart data without a source table.
6. Bit complexity is converted to base-field and group-operation costs; lifting,
   multimodular reductions, FFTs, randomness, failures, and serialized advice are
   charged.
7. Relation density, fresh rank, factor logs, blind descent, output, verification, and
   peak memory are included.
8. All diagnostics remain toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`shared_symbolic_P1510_bivariate_circuit | two_selector_norms | circuit_preserving_common_norm | exact_target_start_source_jets | KU_bit_model_reduction | full_rank_and_blind_descent`

The removal test is the common-norm operation on a single shared circuit. Removing it
leaves either repeated P1510 specializations or a generic solver backend.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H676`, the closest requirement for a
   public arithmetic source-fiber generator transposed across `Theta(B)` related
   targets; IDEA-121 supplies a concrete shared norm identity but not yet its algorithm.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-RT-1476`, which freezes the complete
   five-term setup, query, rank, descent, and rho exponent boundary used here.
3. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-MX-1478`, where a compact exact local
   norm identity densifies under composition; IDEA-121 must avoid precisely that dense
   norm image.
4. `ledger/FINDING-PF-IC-001.md` — imported `P1477`, whose serial-S3 forward/backward
   vanishing polynomials are the nearest aggregate transition representation and source
   provenance control.
5. `ledger/FINDING-PF-IC-001.md` — imported `P1434`, which distinguishes an actual
   public source-fiber generator from a supplied membership or factorization oracle.

## Closest primary literature

- Neiger, Salvy, Schost, and Villard,
  [Faster modular composition using two relation matrices](https://arxiv.org/abs/2601.17422),
  give a generic algebraic degree-`n` composition cost
  `soft-O(n^((omega+3)/4))`; at `n=Theta(B^2)` this cannot strictly beat
  `B^(5/2)` for any `omega>=2`.
- Kedlaya and Umans,
  [Fast Polynomial Factorization and Modular Composition](https://doi.org/10.1137/08073408X),
  give quasi-optimal finite-field modular composition in a bit-complexity model; they do
  not reduce a bivariate product-circuit common norm with source jets to that problem.
- Moroz and Schost,
  [A Fast Algorithm for Computing the Truncated Resultant](https://arxiv.org/abs/1609.04259),
  compute `k` local resultant coefficients in soft-`O(kd)` operations; in this regime
  even `k=Theta(B), d=Theta(B^2)` is cubic and fixed-point truncation does not locate
  unknown common roots.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the elliptic relation equations but no shared common-norm source reporter.

No checked source supplies the complete IDEA-121 operation.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B`, all addition charts, marker codes, `H(U,W)`, selector grammar,
   finite-field algorithm, randomness, bit-cost conversion, and source normalization.
2. Construct and independently hash the one `Theta(B^2)`-leaf circuit without endpoint
   roots, source tables, or factor logs.
3. For a public batch `T` of known-scalar targets, compute only the common norm factors
   against `F`; invert every factor to complete signed five-source rows and verify each
   elliptic sum.
4. Preserve misses, duplicate factors, multiplicities, dependent rows, and all failed
   source inversions; continue until exactly `B+sigma` retained rows have rank `B`.
5. Solve every factor-base logarithm and independently verify each point/log pair.
6. Freeze all state and apply the unchanged circuit operation to fresh masked targets
   `Q+[t]P`, retaining every common factor and source ambiguity.
7. Substitute verified factor logs, subtract masks, enumerate every retained candidate,
   and accept only `x` satisfying `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` expected group operations with constant-state memory;
BSGS costs `N^(1/2+o(1))` time and memory. Let `B=N^beta`, with the primary arm
`beta=1/5`. Let shared circuit and selector construction cost `N^a` time and `N^a_m`
memory; one complete known-target batch common-norm/source operation cost `N^c` time and
`N^c_m` memory; reciprocal probability that a batch supplies `Theta(B)` usable rows be
`N^delta`; written source output have exponent `o`; source ambiguity have exponent `u`;
verification cost `N^v`; factor-log linear algebra cost `N^ell` time and `N^ell_m`
memory; and one blind masked-target operation have exponent `c_t` with reciprocal success
`N^delta_t`.

The complete time exponent is

`lambda=max(a,delta+c+o+v,ell,delta_t+c_t+o+u+v)`

and peak-memory exponent is

`mu=max(a_m,c_m,ell_m,beta+o,o+u)`.

The shared leaf input alone gives `a>=2beta`; absent extra rank structure,
`ell>=2beta`. Explicit norms or specializations give `c>=3beta`. At `beta=1/5`, the
latter is `0.6`, above rho. A passing circuit reduction must instead prove
`lambda,mu<1/2`, including field-bit conversion, coefficient traffic, all failed
batches, exactly `B+sigma` rows, factor logs, and blind descent.

## Likely fatal obstruction

The compact circuit may compress only its description, not the common-norm operation.
Every standard route either emits `Theta(B^3)` specialized leaves or norm coefficients,
or creates a `Theta(B^4)` dense fiber-product module. Kedlaya-Umans consumes ordinary
dense univariate composition inputs; converting the bivariate source-marked product
circuit to those inputs may restore the cubic image. Even an unlabeled common factor can
aggregate target/start/source tuples, forcing the missing source splitter to redo the
five-sum search.

## Proof track

Give a circuit-level reduction from `(T,F,H)` to a bounded number of explicitly sized
Kedlaya-Umans-compatible operations, prove common-factor multiplicity and complete source
jets, convert bit complexity to the full `lambda,mu` model, and carry the operation
through relation rank and blind descent.

## Disproof track

Show that every valid reduction materializes an `Omega(B^(5/2))` coefficient,
evaluation, quotient, or source object; prove one common factor mixes distinct source
rows without a sub-rho splitter; or derive `lambda>=1/2` or `mu>=1/2` after exact field-
bit conversion and relation/descent accounting.

## Positive and negative controls

- Positive identity control: one `B^2`-leaf bivariate product circuit whose two selector
  norms have exactly `B` planted common roots and complete source rows.
- Positive backend control: published dense modular-composition fixtures in the exact
  finite-field bit model.
- Negative route controls: repeated specialization, explicit norms, dense fiber-product
  gcd, truncated resultants, and relation-matrix modular composition.
- Source controls: target/start permutations, repeated factors, label deletion,
  nonreduced roots, vertical pairs, infinity, and return paths.
- Geometry control: matched random bivariate circuits with identical degrees and leaf
  counts.
- Pipeline controls: shuffled relation rows, matched Pollard rho, and memory-matched
  BSGS.

## Quantitative promotion and falsification gates

No elliptic scaling run is admissible before the circuit-to-common-norm theorem gives a
complete base-field and bit recurrence, exact source inverse, and symbolic
`lambda,mu<=0.45`. A future toy preflight must have zero common-factor, source, sum,
rank, factor-log, or blind-descent errors on at least 20 ordinary curves at four sizes,
at least 1,000 independently verified rows and 100 blind descents at each of the two
largest sizes, rank at least `B`, and upper 95% bounds `lambda,mu<=0.45`. Falsify a
tested family on one persistent source collision or a proved or lower-95% bound at least
`0.50`.

## Artifact plan

- Assignment receipt: `ideas/artifacts/ECDLP-IDEA-121/assignment_receipt.md`
- KU/common-norm theorem gate: `ideas/artifacts/ECDLP-IDEA-121/ku_common_norm_reduction_gate.md`
- Remaining KU circuit reduction gate: `ideas/artifacts/ECDLP-IDEA-121/ku_circuit_reduction_v2.md`
- Frozen circuit schema: `ideas/artifacts/ECDLP-IDEA-121/shared_norm_circuit.yaml`
- Prospective exact reducer: `ideas/artifacts/ECDLP-IDEA-121/common_norm_reduce.py`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-121/verify_common_norm_sources.py`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-121/analysis.md`

## Interpretation boundary

This deferred record is toy, heuristic, model-bound, and novelty-unverified. The exact
shared norm identities, quadratic circuit description, planted common factors, standard-
route negatives, valid source rows, or toy scalar are not evidence of relation
collection, blind descent, a better-than-rho algorithm, or a breakthrough. Promotion
requires the missing circuit-level operation and every end-to-end exponent.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-121/ku_circuit_reduction_v2.md` deriving a source-preserving reduction from the shared bivariate product circuit to a bounded number of degree-`Theta(B^2)` Kedlaya–Umans operations with `lambda,mu<=0.45`, or a scoped obstruction for that remaining circuit route.
