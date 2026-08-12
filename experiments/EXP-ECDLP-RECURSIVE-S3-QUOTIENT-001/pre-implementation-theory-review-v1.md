# Pre-implementation theory review v1

## Handoff: draft recursive S3 quotient theory review

### Claim or task

Determine whether the draft defines a meaningful exact quotient experiment
rather than forcing singleton states through an injective encoding.

### Status

`OPEN`: `REVIEW / REVISE`.

The research question is worthwhile, but the reviewed contract is not
mathematically specified enough for implementation. No implementation or
execution is authorized.

### Assumptions

- `F` is an indexed, sign-complete factor base on an odd prime-order
  short-Weierstrass curve.
- Repetition means repeated leaf use, not duplicate factor-base entries.
- Quotient equality is intended to preserve complete root support and at least
  one replayable signed witness per returned root.
- Any negative result is model-bound to the exact partition semantics; implicit
  modules, multipoint operators, and other non-partition representations remain
  outside it.

### Evidence so far

The strongest defect is that the proposed initial symbolic observation is
generically injective.

Write the `Z^2` coefficient of `f3(u,phi_b(t),Z)` as
`A_u(t)=(u-phi_b(t))^2`. If two finite x-orbits `u != u'` have equal
observations modulo the squarefree accepted-root polynomial, then at every
accepted root `r`,

```text
(u-u')(u+u'-2 phi_b(r)) = 0.
```

Thus equality with `u != u'` forces every accepted root in that branch to map
to the same x-value `(u+u')/2`. Whenever a branch contains at least two distinct
mapped factor x-values, `A_u=A_u'` already implies `u=u'`. The remaining `f3`
coefficients only strengthen this separation.

Therefore the reviewed initial coloring usually makes every finite S2 state
singleton before transition refinement. A coordinate/random comparison would
measure an injective observation selected by construction, not recursive
compression or expansion. This is a restricted algebraic obstruction to this
observation, not to weaker exact representations.

### Exact ambiguities and theorem obligations

1. Define the indexed factor involution, repeated-witness semantics,
   source-root multiplicities, quotient ring, denominator clearing, canonical
   reduction, scalar normalization, poles, S3 observations, and identity.
2. Define terminal equivalence. Arbitrary-target oriented behavior is itself
   injective for any proper nonempty complement set in a prime-order group;
   classify x-orbit/sign-symmetrized exceptions.
3. Define a two-sorted labeled transition relation. One S2-to-S3 layer with
   fixed terminal colors is not yet a recursive bisimulation.
4. Use class-relative witness transport maps rather than literal canonical
   witness equality; identity requires separate rules.
5. Specify whether query output is complete D2 roots plus one witness per root
   or every signed witness, and forbid hidden member-discrimination tables.
6. A `0.8|D2_x|` object is still asymptotically linear. Separate a toy
   constant-factor gate from an asymptotic direct-address prohibition.
7. Define exact same-map random-root sampling laws, mapped-x multiplicities,
   branch collisions, sign fibers, and one family-independent target schedule.
8. Make every 0.8 predicate conjunctive and dimensionally typed; define
   crossover equations, slope fits, aggregation, and fail-closed undefined
   values.

### Failure modes

- Singleton refinement may be a tautology caused by the initial tuple.
- Weakening the observation may move a full member-discrimination vector into
  quotient advice.
- Exact witness transport may erase apparent compression.
- Dense exact output may impose linear output cost despite sublinear resident
  workspace.
- Any negative applies only to the literal partition model, not implicit
  algebraic operators or ECDLP.

### Next concrete action

Prove or refute this lemma before revising any other section:

> For every branch with squarefree accepted-root polynomial and at least two
> distinct mapped x-values, the denominator-cleared leading-in-Z coefficient
> map from a finite state x-coordinate to `f3(u,phi_b(t),Z) mod m_b(t)` is
> injective; classify one-image, pole, identity, and characteristic exceptions.

If proved, the full coefficient tuple must become an explicit injective
negative control and leave the candidate quotient's initial coloring.

### Artifact paths

- `contract.md`
- `research-question.json`
- `hypothesis.json`

## Coordinator response

The v1 `REVISE` decision is preserved. The leading-coefficient lemma and the
complete x-orbit-profile classification are proved in `theory.md`, the
injective observation is demoted to a negative control, and implementation
remains unauthorized pending a mathematically distinct implicit
representation.
