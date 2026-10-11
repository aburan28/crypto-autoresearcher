# Public-binding interface funnel for EndRing PKE

Date: 2026-10-08

Goal: `GOAL-SSI-2fa82a`

Question: `RQ-SSI-1946c9`

Batch: `BATCH-fc23a6`

## Purpose and claim boundary

This authorized zero-run round tests whether a public binding relation can
repair the preimage ambiguity exposed by the preceding Trap_E funnel without
introducing a hidden selector, secret-correlated public data, or a new
extraction gap. It implements an explicit propose/evaluate/propose/evaluate
loop. It does not construct or validate a secure PKE, prove EndRing hardness,
establish novelty, recommend parameters, or close the goal.

Each candidate must define a polynomial-time decidable public relation

```text
R_E(x, y) in {0,1}
```

with public `Sample` and `Eval` using a bare supersingular curve `E` from the
declared EndRing challenge distribution. For every honest output `y`, all
accepted preimages must lie in one publicly specified equivalence class, and
that equivalence must preserve the functionality needed for actual-message
recovery. A complete evaluable basis `B` of `End(E)` may be used only by one
uniform inverse `Inv(E,B,y)`, quantified over every valid such basis.

The required security direction is

```text
scheme attacker
  -> accepted preimage or public equivalence class
  -> complete evaluable basis of End(E).
```

The reverse direction, `EndRing solver -> decrypt`, is an attack route and is
not a security reduction. Interface one-wayness is not automatically IND-CPA.

## Cursor reconciliation

This batch is an additive continuation of `DEC-20261007-be6e31`. The older
goal projection still names `BATCH-9681e3`; `BATCH-0cd12a` later handled its
J4/J5 correction and `BATCH-cb7b9a` later selected this public-binding
objective. Those immutable records and their obligations remain unchanged.

The Milne locator mapping retained by the predecessor is metadata/regression
guidance, not a fresh primary-PDF verification in this lane. This lane does
not recode historical J4/J5, repair missing digit-loop tie handling, or close
the general quotient-source and custody gaps.

## Alternating loop

1. Two mutually blind idea generators propose materially distinct public
   binding interfaces.
2. Each packet supplies exact distributions, byte grammar, domains, public
   relation, `Sample`, `Eval`, `Inv`, equivalence, any-basis quantifiers,
   costs, failures, smaller witnesses, proof-search map, prior-art delta, and
   O1--O6/C1--C6 status.
3. The Coordinator freezes both packets before review.
4. Independent owners evaluate T1--T5. Each joint verdict is exactly
   `holds`, `breaks`, or `inconclusive`.
5. The Coordinator composes without voting and selects at most one smallest
   decision-changing gap.
6. One fresh producer may repair or replace one mechanism using only that gap
   packet. If no decision-changing repair is specifiable, the revision is
   skipped and the scoped obstruction is retained.
7. Any revision is frozen and reviewed under the same T1--T5 definitions.
8. The batch stops unconditionally after the second evaluation.

## Diversity and deduplication

- Initial candidates must differ in relation, domains, public evaluation,
  equivalence, and inverse mechanism—not only hashes, tags, encoding, or
  parameters.
- Candidate A may not use a walk endpoint, lexicographic path selector,
  parity mask, or finite point-evaluation tuple as its central relation.
- Candidate B may not be a relabeling of Candidate A and may use a transcript
  only if every accepted representative has the same declared functionality.
- Screen both candidates against CEST, ER-McE, UTTK, RWER, and remote ideas
  `IDEA-20261007-20f660`, `IDEA-20261007-cd446e`,
  `IDEA-20261007-81e7ef`, and `IDEA-20261007-670f01`.
- The remote ideas remain proposed/unapproved and are not fresh blind
  candidates. Primary-source novelty remains unverified until checked.

## Frozen definitions

1. Pin the exact EndRing instance distribution, field, curve encoding,
   auxiliary information, conditional assumptions, and complete evaluable
   output representation. A key-distribution replacement needs its own
   quantified bridge.
2. Pin `X_E`, `Y_E`, `R_E`, byte encodings, equality/equivalence, validation,
   failure symbols, and all randomness.
3. Public binding means that every accepted preimage of an honest output is in
   one public equivalence class that preserves actual-message recovery.
4. `Inv(E,B,y)` must be uniform, polynomial, and correct for every valid
   complete evaluable basis `B`, including valid basis changes.
5. Repeated-use semantics name adversary class, input lengths, query count,
   adaptive history, state, randomness coupling, aborts, and the complete
   public view.
6. Complete-ring necessity needs either a non-factorization result over the
   declared smaller-witness class or a reconstruction theorem from such a
   witness to a complete evaluable basis.

## Frozen joints

| Joint | Question and worked attack |
| --- | --- |
| T1 | Can all public data be generated from bare `E`, and is the relation genuinely binding? Hold `y` fixed, vary accepted witnesses, and trace every field for secret-derived tags, orientation, ideals, or selectors. |
| T2 | Does one polynomial `Inv` work from every valid complete basis, with fiber correctness? Blindly rederive typing and correctness, apply valid unimodular basis changes, and vary equivalent encodings. |
| T3 | Does inversion avoid a smaller witness? Try one endomorphism, finite torsion action, transcript table, or proper suborder; require reconstruction where complete-ring dependency factors through one. |
| T4 | Does an attacker yield a complete basis quantitatively? Start with the exact bare challenge and audit embedding, simulation, correlated calls, extraction, loss, runtime, aborts, rank, and saturation. |
| T5 | Are byte grammar, malformed inputs, repeated use, controls, sources, prior art, and documentation complete and consistent? |

## Controls and review independence

Proves-too-much controls include a leaked witness/tag, a public inverse, an
ordinary many-to-one endpoint mask, CEST/RWCT finite-witness factorization,
and oriented/torsion-aided nearby objects. Required failure signatures are
frozen in the review plan.

Every reviewer writes a canonical top-level `review_attestation` with exact
`task_id`, `joints_owned`, flat per-joint `verdicts`, actual `sources_read`,
and blindness. The raw independence checker must pass separately for each
candidate and round. No metadata projection or alias repair is accepted.

Blind rederivation includes all load-bearing numerical bounds. Expressions
such as `epsilon^q * u_I` require their independence and call assumptions.
Failure to derive a positive saturation bound is not a proof that its infimum
is zero.

## Inherited correction controls

- Preserve the reviewed fixed-model, simultaneous-normalization, `p>3`, and
  `ord(P)=N>4D` scope for normalized `x(X)` arguments.
- Obtain `P=O` and lower-order controls only by weakening both exact-order
  premises; do not present them as valid-input attacks.
- Do not infer a digit-loop return value without complete pseudocode and tie
  handling.
- Limit pairing, norm, quotient, and point-count claims to inspected source
  scope. Vélu formulas alone do not prove a general categorical quotient.
- Mermaid, SVG, PDF, and prose routing must agree; visual agreement is not
  mathematical evidence.

## Budgets, stop rule, and promotion rule

All tasks have `maximum_runs: 0`, separately covering scientific,
implementation, formalizer, experiment, benchmark, and parameter-selection
runs. Read-only source inspection and administrative validation/rendering are
allowed. Workers are bounded to 4 GiB and one hour; archive tasks are shorter.

Stop after evaluation two. A survivor is only a reviewed interface candidate.
A later PKE-design round is justified only if all T1--T5 joints hold on the
exact distribution and semantics. Candidate-specific breaks do not imply a
family-level impossibility.
