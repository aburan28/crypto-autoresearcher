# ECDLP-IDEA-108 — Skein quantum-trace source factorization

## Status and claim labels

- Class: `representation`
- Risk band: `high-risk`
- State: `rejected_merged_trace_aggregation`
- Evidence scale: no run; any future state-sum preflight is `toy`
- Cost claims: `heuristic` and `model-bound`
- Novelty: `novelty-unverified`
- Breakthrough claim: **none**; a valid skein identity, triangulation-independent quantum
  trace, correct relation, or toy scalar is not an ECDLP break.

## Falsifiable hypothesis

There is a target-independent marked surface and skein encoding of the elliptic
`m`-source addition correspondence such that each factor-base point is a source-labelled
skein atom and elliptic addition becomes skein multiplication/gluing. A Bonahon-Wong
quantum trace into a triangulation algebra then factors the target element into local
triangle states. The hypothesis is that a bounded state word has an exact inverse to the
signed factor-base atoms, allowing `B+sigma` full-rank rows, all factor logs, and masked
blind target descent with fully charged time and peak-memory exponents below `1/2`.

## Mechanism-new operation

The proposed operation is **encode elliptic source atoms as skeins, apply a triangulation-independent
quantum trace, factor the resulting local state sum, and invert accepted states to exact
factor-base points**. A character trace, additive Fourier filter, spin-network count,
formal skein identity, or explicit state table is a control. The candidate is rejected
and merged into the recorded trace-aggregation boundary: the Bonahon-Wong map returns an
aggregate character/state expression, not source-labelled elliptic atoms. Supplying a
scalar-blind point-to-skein functor and exact local-state-to-source inverse would be the
new mathematical operation required to reopen it; source decorations or an explicit
state dictionary merely restore the full incidence table.

## Assumptions

1. `E(F_p)` has public prime-order subgroup `<P>` of order `N=p^(1+o(1))`, target
   `Q=[x]P`, fixed arity `m`, and target-independent factor base
   `F={F_1,...,F_B}` with `B=N^beta`.
2. A fixed punctured surface, ideal triangulation class, skein algebra, quantum parameter,
   and finite-field specialization encode all curve points, signs, sums, and exceptional
   branches without source-indexed advice.
3. Skein multiplication/gluing projects exactly to elliptic addition for the marked
   objects, not merely to an `SL_2` character or aggregate trace.
4. Quantum-trace states invert to exact factor-base indices, signs, and multiplicities;
   distinct source tuples are not collapsed to one trace element.
5. Triangulation changes, coefficient extensions, state sums, cancellations, source
   output, misses, rank, factor logs, descent, verification, and memory are fully charged.
6. Any future evidence remains toy, heuristic, model-bound, and novelty-unverified.

## Semantic fingerprint

`marked_elliptic_source_skeins | skein_gluing_addition | Bonahon_Wong_quantum_trace | local_triangle_state_factorization | exact_state_to_point_source_inverse | blind_descent`

The load-bearing novelty is the exact state-to-point inverse. A short quantum trace whose
states only count intersections or character data is an aggregate certificate.

## Five closest ledger entries

1. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1422-ADDITIVE-CHARACTER-NO-PROMOTION`,
   where deterministic character kernels have full rank and weak source selectivity.
2. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1421-TRANSPOSED-FULL-RANK-NO-PROMOTION`,
   where exact transformed value matrices and fixed tensor representations fail to
   expose a compact source operation.
3. `ledger/FINDING-PF-IC-001.md` — imported `P1478`, whose compact exact transition norm
   still lacks source-resolving composition.
4. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-H664`, the nearest attempt to derive
   character phases from the exact elliptic subtraction circuit.
5. `ledger/FINDING-PF-IC-001.md` — imported `ECFG-NR-1479`, where tested compact public
   feature spaces do not contain factor-log orientation.

## Closest primary literature

- Bonahon and Wong,
  [Quantum traces for representations of surface groups in `SL_2(C)`](https://arxiv.org/abs/1003.5250),
  construct a quantum-trace homomorphism from a skein algebra to a square-root quantum
  Teichmüller algebra and prove independence from ideal triangulation; they do not encode
  arbitrary finite-field elliptic point sources or invert local states to them.
- Semaev,
  [Summation polynomials and the discrete logarithm problem](https://eprint.iacr.org/2004/031),
  supplies the comparison elliptic addition relation and source obligation.
- Muller,
  [Skein and cluster algebras of marked surfaces](https://arxiv.org/abs/1204.0020),
  relates Kauffman-bracket skein algebras of marked surfaces to quantum cluster algebras;
  it does not provide a finite-field elliptic point-to-skein functor or a local-state
  source inverse.

No checked source supplies the marked elliptic source functor, addition/gluing
biconditional, or sub-rho state-to-point inverse. Novelty remains unverified.

## Complete factor-base-to-target-descent path

1. Freeze `E,P,N,F,B,m`, marked surface, triangulation class, quantum parameter,
   coefficient specialization, point-to-skein atom map, gluing order, state convention,
   and exhaustive tiny source truth.
2. Prove and independently verify that gluing source atoms and projecting their quantum
   trace equals the signed elliptic sum on all ordinary and exceptional charts.
3. For known random outputs `R_j=[r_j]P`, construct target skein data without source
   advice, evaluate/factor the complete local state sum, invert accepted states to exact
   points in `F`, and verify every sum.
4. Preserve zero/cancelled states, failed inverses, duplicate tuples, ambiguities, and
   dependencies; collect exactly `B+sigma` verified rows of rank `B`.
5. Solve every factor-base logarithm and independently verify each point equation on `E`.
6. Freeze all surface and triangulation data and apply the identical trace factorization
   to masked blind targets `Q+[t]P`, retaining the complete local-state ambiguity.
7. Substitute factor logs, unmask all scalar candidates, and accept only after verifying
   `[x]P=Q`.

## Full rho/BSGS cost model

Pollard rho costs `N^(1/2+o(1))` time with constant state; BSGS costs
`N^(1/2+o(1))` time and memory. Let `B=N^beta`. Let surface/functor setup take
`N^(a+o(1))` time and `N^(a_m+o(1))` peak memory. Let triangulation construction and
coefficient-field representation take `N^(h+o(1))` time and `N^(h_m+o(1))` memory. Let
trace evaluation and algebraic factorization outside explicit state enumeration take
`N^(q+o(1))` time and `N^(q_m+o(1))` working memory. Let the number of local admissible
states have exponent `s`, and let storing the complete state-sum coefficients and
cancellation data have exponent `s_m`. Let exact inversion of one state to source atoms
take `N^(r+o(1))` time and `N^(r_m+o(1))` memory. Let source tuples emitted per state
have exponent `o`, and let residual scalar ambiguity per emitted target source have
exponent `u`; writing all states, sources, and candidates costs their full time and
storage. Let reciprocal accepted-relation and target densities be `N^delta` and
`N^delta_t`. Let sparse linear algebra take `N^(ell+o(1))` time and
`N^(ell_m+o(1))` memory, with `ell>=2beta` absent proved structure. Let verification of
one emitted source or scalar candidate take `N^(v+o(1))` time and `N^(v_m+o(1))`
working memory.

The complete time exponent is

`lambda=max(a,h,beta+delta+q+s+r+o+v,ell,delta_t+q+s+r+o+u+v)`,

and the complete peak-memory exponent is

`mu=max(a_m,h_m,q_m,s_m,r_m,ell_m,beta,s+o+u,v_m)`.

Every triangulation edge, quantum coefficient, admissible state, cancellation, source
inverse, failed target, ambiguity branch, emitted point, and verification is explicit.
An explicit state dictionary or `2^k` state sum contributes its full time and memory
exponents even if the final trace expression is short.

## Likely fatal obstruction

Quantum traces are algebra homomorphisms for surface-group character data, not
factorizations of arbitrary labelled elliptic points. Many skeins can have the same trace,
and the local state sum aggregates intersection states rather than identifying point
atoms. Decorating states with source labels can restore an inverse only by recreating the
full source table. The necessary surface complexity, quantum coefficient extension, or
number of admissible states may also grow to the rho boundary or beyond.

## Proof track

Construct the scalar-blind point-to-skein functor, prove the addition/gluing biconditional
and triangulation-independent exact source inverse, bound all state branching and
coefficient arithmetic below rho, and then prove the seven-step rank, factor-log, and
blind-descent path with `lambda,mu<1/2`.

## Disproof track

Exhibit distinct source tuples with the same quantum trace/state data, show that local
states lack point labels, prove that source decoration is the explicit incidence table,
or establish complete setup, state-output, time, or memory exponent at least `1/2`.

## Positive and negative controls

- Positive quantum-trace control: published punctured-surface examples with independently
  verified triangulation-independent traces.
- Positive source control: a planted labelled skein category whose local states have a
  known exact atom inverse.
- Negative trace control: distinct skeins or source tuples with identical character trace.
- Mechanism controls: additive-character kernels, spinor/matchgate IDEA-050, explicit
  tensor/state tables, and unlabelled skein state sums.
- Leakage control: permute factor-base labels while preserving all skein/trace data.
- Baseline control: matched Pollard-rho and memory-matched BSGS.

## Quantitative promotion and falsification gates

No run is admissible before a theorem proves the point-to-skein functor,
addition/gluing biconditional, exact state/source inverse, and symbolic
`lambda,mu<=0.45`. A future toy preflight would require exhaustive agreement through 18
bits, 20 ordinary curves at each of four increasing sizes, zero trace/source errors,
`1,000` verified rows and `100` blind descents at each of the two largest sizes, fresh
rank at least `0.8B`, and upper 95% bounds `lambda,mu<=0.45` under the complete formulas
above. Falsify on one
source collision, label-permutation invariance, source-state lower 95% exponent at least
`0.50`, or every complete path having `lambda>=0.50`.

## Artifact plan

- Theorem gate: `ideas/artifacts/ECDLP-IDEA-108/skein_source_inverse_gate.md`
- Surface/functor specification: `ideas/artifacts/ECDLP-IDEA-108/skein_functor.yaml`
- Prospective trace evaluator: `ideas/artifacts/ECDLP-IDEA-108/quantum_trace.sage`
- Independent source verifier: `ideas/artifacts/ECDLP-IDEA-108/verify_skein_sources.py`
- Prospective receipts: `ideas/artifacts/ECDLP-IDEA-108/runs/<run-id>/`
- Complete analysis: `ideas/artifacts/ECDLP-IDEA-108/analysis.md`

## Interpretation boundary

This rejected merged trace-aggregation record is toy, heuristic, model-bound, and
novelty-unverified. A correct skein relation, quantum trace, triangulation identity, local
state sum, valid relation, or toy scalar does not show a better-than-rho algorithm or a
breakthrough. Exact point-source inversion and the full descent path remain absent; only
a new source-invertible operation smaller than the incidence table could reopen it.

## Exactly one next executable action

1. Write `ideas/artifacts/ECDLP-IDEA-108/skein_source_inverse_gate.md` constructing and testing on paper the required point-to-skein addition functor and proving either an exact local-state source inverse with symbolic sub-rho bounds or a trace-collision obstruction.
