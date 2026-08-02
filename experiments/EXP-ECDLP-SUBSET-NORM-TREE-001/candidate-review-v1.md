# Candidate review v1: generalized roots and subset norms

## Handoff: successor ranking after root preflights

### Claim or task

Synthesize the two paper candidates, preserve their narrow negatives, and choose
the next mathematically distinct root-only question.

### Status

`OPEN`, `NOVELTY-UNVERIFIED`, paper-only. No implementation or execution is
authorized.

### Assumptions

- Curves are generated ordinary prime-field curves, not selected for anomalous
  order, smooth `p-1`, special j-invariant, or favorable auxiliary isogenies.
- `B approximately n^(1/5)` and all full-pipeline costs use the shared accounting
  note.
- Exact output is five signed public identifiers with independent replay.

### Evidence so far

#### What survived

- The registered five-leaf addition circuit is an exact constant-width
  correctness surface. This is useful for testing dedicated generalized-root
  algorithms, but is not itself a complexity improvement.
- The subset resultant gives an exact D2-leaf self-reduction in logarithmically
  many oracle calls, with an exact `Theta(B)` Tier B terminal lift.
- The identity-complete translated-D3 polynomial and its resultant norm are exact
  over the oriented quadratic encoding.
- The accounting layer now charges rank-dependent relation yield, confidence,
  advice caps, optimized BSGS, constructive generic preprocessing, traffic,
  linear algebra, and descent.

#### What was closed narrowly

- The explicitly materialized first-power tensor-box lattice has
  `Theta(B^5)` columns and raw generators. It fails before reduction; its
  determinant-volume calculation is only a supporting heuristic screen.
- The empty-generator companion commutator has rank zero but an
  `N2`-dimensional kernel. Its dense power-basis boundary and the direct
  translated-factor approximant interfaces fail the root gate. This does not
  lower-bound alternate target-parametric representations.

### Ranked successor theories

#### 1. Conservative: nested source-level resultant

**Mechanism.** Avoid constructing distinct D3 entirely. Express the finite-
finite root scalar as a nested norm over three registered source variables:

```text
Norm_(t1 in F) Norm_(t2 in F) Norm_(t3 in F)
  M_I(enc(Q-(P(t1)+P(t2)+P(t3)))).
```

Ordered triples and multiplicities are acceptable for a zero predicate; source
registries recover exact witnesses after D2 descent.

**Why it might evade the barrier.** It asks for one scalar and retains the
constant-width addition circuit instead of emitting D3 factors or an N2
remainder.

**Minimal test.** Derive one exact denominator-cleared resultant order at the
root and census every intermediate degree, coefficient module, matrix dimension,
target-dependent coefficient, and child-modulus substitution.

**Likely failure.** The first or second elimination may create an N2-sized
target polynomial or a B2/B3-degree intermediate, reproducing the forbidden
boundary under a different name.

**Learning if it fails.** It would identify whether the obstruction is D3
enumeration specifically or degree growth intrinsic to source-level norming.

#### 2. Representation change: composition-tower fiber norm

**Mechanism.** Use a factor-base source polynomial represented by a constant-
degree composition tower of depth `Theta(log B)`, carry exact inverse-edge
labels, and take norms one tower layer at a time through the addition circuit.

**Why it might evade the barrier.** The source set is never expanded as a
degree-B coefficient vector; an active frontier smaller than `B^1.5` per attempt
would fit the constant-yield one-instance relation gate.

**Minimal test.** For one registered tower, derive the exact active-fiber width
recurrence and witness-label payload before any EC solving.

**Likely failure.** Arbitrary-prime `x_interval` has no known compact tower;
known PKM-style constructions rely on smooth `p-1` or auxiliary-isogeny
structure, and the frontier may still grow to D2 scale.

**Learning if it fails.** It separates a representation-family restriction from
a generic prime-field obstruction.

#### 3. High risk: batched target-translation norm recurrence

**Mechanism.** For preregistered targets `Q_i=Q_0+iH`, use the rational EC
translation map to update an implicit scalar node norm across targets, aiming to
share target specialization without storing the full remainder for any target.

**Why it might evade the barrier.** Fixed translation is a constant-degree
rational map, so a transposed or baby-step/giant-step recurrence might compute
many scalar predicates more cheaply than independent specialization.

**Minimal test.** Write the exact pushforward relation between `c_Q` and
`c_(Q+H)` and dimension only the state that crosses one update. Compare the
actual `A_(1-alpha)` batch, not a projected per-target average.

**Likely failure.** Updating the root set may require an N2 remainder or N3
factor stream, and scalar node bits alone may not support hereditary witness
descent.

**Learning if it fails.** It gives a concrete batch-specific barrier instead of
assuming single-target output size controls amortized computation.

### Priority decision

The nested source-level resultant is first because it directly attacks both
closed interfaces while remaining meaningful for ordinary arbitrary-prime
curves. The composition tower is second because it is structurally cleaner but
may define a restricted curve or field family. The batch recurrence is third
because its state and witness-descent semantics are least developed.

No candidate currently passes a zero-run feasibility gate, so launching a
solver would measure a known displaced object rather than the proposed
mechanism.

### Failure modes

- Calling exact correctness, a zero resultant, or logarithmic oracle calls a
  cryptanalytic improvement.
- Reconstructing D3, an N2 remainder, or one target value per D2 leaf inside a
  "compact" norm or approximant input.
- Treating a restricted smooth-`p-1` or auxiliary-isogeny tower as evidence for
  generic ordinary curves.
- Reporting a batch average without constructing the confidence-sized batch and
  charging rank, certificates, linear algebra, and descent.

### Next concrete action

Write a root-only object-dimension ledger for the exact nested source-level
resultant, including one elimination order and every intermediate degree; stop
before source code if any target-dependent intermediate reaches `Omega(B^2)`.

### Artifact paths

- `../EXP-ECDLP-GENROOT-CIRCUIT-001/first-power-box-lattice-negative-v1.md`
- `root-operator-preflight-v1.md`
- `pre-implementation-literature-review-v1.md`
- `../../notes/ecdlp_relation_preprocessing_accounting_20260718.md`
