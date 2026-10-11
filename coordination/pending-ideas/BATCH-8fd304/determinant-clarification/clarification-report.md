# Determinant-object clarification preparation

Task `TASK-20260910-6d2724` is complete as a zero-run Coordinator preparation
artifact. The parent handoff grants custody of exactly five staged outputs;
the canonical repository paths are intentionally untouched.

## Decision gate carried forward

The predecessor decision `DEC-20260909-40f3ad` records `revise` because the
following sentence is preserved literally and does not identify its determinant
object:

> A cycle with coefficients whose determinant vanishes mod N must not yield an independent base relation.

The sentence is retained verbatim in the proposal, question, hypothesis, and
experiment records. This preparation does not replace it with a projected-rank
rule, infer the original authors' intention, or turn a manual argument into a
validated counterexample.

## Exact mathematical ambiguity

For an exact modular row system `M = [A | B]` over `F_N`, with auxiliary block
`A` and base/known block `B`, the ambient map is
`Phi(u,v) = A u + B v`. A cancellation multiplier is a vector in
`K_A = ker(A^T)`, and the induced auxiliary-free map is
`lambda -> lambda^T B`. The determinant sentence does not say whether its
determinant is:

1. `det(A)` for a named square auxiliary block;
2. a selected square minor of `A`;
3. a square minor of the full or bordered coefficient matrix `[A | B]`; or
4. a square minor of a matrix representing the induced projected map `K_A -> F_N^b`.

These objects have different domains and implications. In particular, when `A`
is square, `det(A)=0` can certify a nonzero left-cancellation space, but it does
not by itself say whether the projected rows are zero, redundant, or rank
increasing. A direct independence statement needs the complete projected image,
consistency and certificate checks, followed by rank increment against the
prior accepted rowspace. A selected minor is even weaker unless its maximality
and companion minors are named. A full/bordered minor concerns the combined map
unless an explicit quotient/projection is supplied. A nonzero minor of the
induced projected map can certify positive image rank for that exact map, but it
still needs the prior-rowspace and certificate premise and cannot be silently
declared the source determinant.

The protocol amendment therefore records four alternatives, their ambient maps,
their valid implications, and their missing premises. None is adopted here.

## Affected fields and proposed wording

The amendment file lists the exact literal/control fields in:

- `ledger/proposals/IDEA-20260906-f9f8c8.yaml`: the known-false control,
  first falsification condition, and nearby-object control;
- `ledger/questions/RQ-RELN-b70054.yaml`: the source-definition literal;
- `ledger/hypotheses/H-RELN-dee9ec.yaml`: the source-definition literal;
- `experiments/EXP-RELN-f3a133/specification.yaml`: the input gate, nested
  source-definition gate, and source falsification condition.

Each entry carries the exact old wording and an additive proposed wording. The
proposed wording names an object and its premise, but is marked
`pending_independent_review`; it is not a canonical edit. Parent must preserve
all current records and decide adoption only after the review chain.

## Manual F_11 material

The four existing `F_11` matrices from the predecessor decision are included in
`blind-matrix-packet.json` without group labels, producer derivations, expected
rank values, source interpretation, or cryptanalytic procedure. Their origin is
the predecessor's manual design work. They have not been executed or
independently validated in this task.

The packet asks a fresh reviewer to derive, from matrices alone, the left
kernel, projected rows, candidate determinant/minor facts, and incremental rank
against the supplied prior rows. It includes a known-false control for the
proposition that singularity of an auxiliary block alone forces no new base
information. The packet does not prefill the result.

## Frozen scope preserved

No scientific parameter or obligation is changed. The preparation preserves:

- nine integer rungs `12` through `20`;
- two auxiliary settings and fill thresholds `8`, `16`, and `32`;
- twenty streams per cell and the `9 x 2 x 3 x 20` ladder;
- `360` planned run units, `1080` paired observations, and `4320` scientific
  artifact paths;
- all acquisition, discarded-work, certificate, checker, memory, cost,
  stopping, baseline, matched-null, identity, known-false, collision, and
  corruption obligations;
- twenty-one selected future cards and two unused workflow reservations.

This task executed none of those units. The experiment remains unapproved and
the existing source, hypothesis, question, specification, queue, goal head,
claims, and sibling bytes remain outside this write scope.

## Independent review plan

The Coordinator prior is that the literal sentence is under-specified and that
a determinant-only rule is insufficient; the review may overturn that prior.
Two joints are separately owned:

- `TASK-20260910-e44f58` owns literal-definition and frozen-scope review. It
  checks every substitution, assumption, and preserved field.
- `TASK-20260910-5c08ef` owns blind matrix-only re-derivation. It may read only
  the packet and its stated field/matrices, and must not read the producer
  amendment/report, source decision, previous worked derivations, proposed
  review queue, or peer reports.

The known-false controls are the singular auxiliary block with a nonzero
projection, the same block with a zero projection, the same projection already
in prior rowspace, and the equal-support/different-coefficient case. A rule
that gives them one determinant-only conclusion proves too much. The two review
reports remain mutually blind; disagreement routes to the separate scoped
Coordinator disposition card and does not auto-adopt the amendment.

The six prospective cards are exactly the two review cards, their two snapshot
cards, the scoped disposition card, and its snapshot card. All remain blocked
until parent custody, source access, fresh sessions, canonical adoption, and
live claims are real. No existing science, implementation, formal, QA, launch,
or primary-source card is activated.

## Provenance and limitations

The records named in the amendment's provenance section were read as internal
records in this turn. No external reference was retrieved. The unrelated
67-error diagnostic in eight `EXP-ECDLP-e962f6` manifests is preserved as a
diagnostic impediment; this preparation makes no global ledger-pass claim and
does not read the excluded experiment tree.

No experiment, implementation, formal proof, test, shell-based scientific
operation, delegation, queue edit, goal-head edit, claim mutation, commit, or
publication was performed. Future sessions, outcomes, hashes, commits, and
publication remain unknown. The parent alone verifies and copies the staged
bytes.
