# Basis-independent EndRing trapdoor-interface funnel

Date: 2026-10-07

Goal: `GOAL-SSI-2fa82a`

Question: `RQ-SSI-1946c9`

Batch: `BATCH-cb7b9a`

## Claim boundary

This zero-run batch searches for a typed interface that could later support a
public-key-encryption design. It does not construct a secure PKE, prove
EndRing hardness, establish novelty, or justify parameters. Every output is a
candidate interface or a scoped obstruction until independent review closes
the applicable obligations in `docs/scheme-construction-contract.md`.

The object under study is

```text
Trap_E : X_E -> Y_E.
```

Public sampling and forward evaluation must use only a bare supersingular
curve `E` drawn from the exact EndRing challenge distribution. Inversion must
work from every valid complete evaluable basis of `End(E)`, not only a planted
or aligned basis. Complete-ring necessity needs either a non-factorization
theorem over a declared smaller-witness class or a reconstruction theorem from
the smaller witness to a complete evaluable rank-four basis. The security map
must have the direction

```text
selected-message attacker
    -> Trap_E inverter or distinguisher
    -> complete evaluable End(E) basis.
```

The reverse implication, `EndRing solver -> decrypt`, is an attack route and
does not establish security.

## Alternating loop

1. Two mutually blind idea generators propose materially distinct interfaces.
2. Each packet specifies exact distributions, encodings, `Sample`, `Eval`,
   `Inv`, any-basis quantifiers, costs, failures, smaller witnesses, proof map,
   prior-art delta, and O1--O6 precursor status.
3. The Coordinator snapshots both packets before review.
4. Independent owners evaluate T1--T5 from the frozen plan. They report only
   `holds`, `breaks`, or `inconclusive` on their joints.
5. The Coordinator composes without voting and emits one smallest
   decision-changing gap.
6. One fresh producer may repair or replace one mechanism using only that gap
   packet. It may not weaken quantifiers, erase failures, or assume an oracle.
7. The revision is snapshotted and evaluated under the unchanged joints.
8. The batch stops unconditionally after the second evaluation.

## Diversity and honesty constraints

- Candidates must differ in `X_E`, `Y_E`, public evaluation, and inversion,
  not merely hashes, serialization, parameters, or names.
- At most one initial candidate may be based on finite point-evaluation tuples
  or planted words. The other must use a materially different curve-,
  transcript-, ideal-, or order-level object.
- Orientation, torsion bases, connecting isogenies, planted-basis alignment,
  normalized quotient lifts, `BaseGen`, `Eval2`, and canonical selectors are
  unavailable unless an explicit polynomial algorithm, representation,
  distribution, and failure bound are supplied.
- A producer that reaches a hidden oracle returns a typed obstruction packet
  naming the earliest failed arrow.

## Cheap audits before review

1. Reproduce the CEST/RWCT finite-evaluator factorization as a regression
   fixture.
2. Search for distinct bases, basis changes, or witnesses with the same
   proposed observable; identify the smallest witness through which inversion
   factors.
3. Check the quantifier order: every sampled `E`, every valid complete basis,
   and every admitted input—not existence of a helpful planted basis.
4. State the method ceiling and run the same reasoning on a leaked-output or
   publicly invertible control.

No formalizer is launched. Each packet names the smallest lemma that could be
formalized later or the missing definition that prevents a useful proof task.

## Frozen joints

| Joint | Question |
| --- | --- |
| T1 | Can `Sample` and `Eval` be run from the bare curve on the exact challenge distribution, with no hidden secret-correlated public data? |
| T2 | Is `Inv` typed, polynomial, and correct for every valid complete evaluable basis, including after basis change? |
| T3 | Does inversion avoid a smaller witness, or does a reviewed reconstruction theorem recover the complete ring from it? |
| T4 | Does a scheme attacker yield a complete ring basis with explicit embedding, simulation, loss, runtime, and abort terms? |
| T5 | Are the full view, encodings, malformed inputs, collisions, repeated use, prior art, sources, and rendered documentation covered? |

## Inherited correction controls

These constraints preserve `BATCH-0cd12a`; they are not new votes on that
batch.

- Normalized `x(X)` arguments retain the reviewed fixed-model, simultaneous-
  normalization, `p>3`, and `ord(P)=N>4D` scope. The pair `f/-f` is not by
  itself a normalized cross-message or different-kernel collision.
- `P=O` and lower-order `P` are controls obtained by weakening both exact-order
  premises. They are not valid-input attacks when exact order is enforced.
- When `M=ord(P)>4D`, the scoped uniqueness reasoning is retained even when
  `M<N`; on the archived `b=1` slice there is no nonzero lower-order
  five-power point.
- A digit-loop return value is not inferred without full pseudocode and tie
  handling. Observation ambiguity alone does not prove “returns zero”.
- Milne's hash-matched PDF uses one-based PDF pages 74--75, 79, and 80 for the
  cited printed pages; see `legacy-correction-addendum.md`.
- Pairing, norm, quotient, and point-counting claims are limited to their exact
  source scope. Vélu formulas and exposition do not establish a full original
  categorical quotient theorem.
- Mermaid, SVG, and PDF routing must agree. Visual agreement is documentation,
  not mathematical evidence.

## Stop and promotion rule

Stop after evaluation two. A later PKE-design batch is justified only if T1
and T2 hold on the exact distribution and every valid basis, T3 has a reviewed
non-factorization or reconstruction theorem, T4 has a correctly directed
quantitative extraction route, and T5 has no break. Even then the survivor is
an interface candidate, not a secure or novel PKE. Candidate-specific breaks
do not imply a family-level impossibility.
