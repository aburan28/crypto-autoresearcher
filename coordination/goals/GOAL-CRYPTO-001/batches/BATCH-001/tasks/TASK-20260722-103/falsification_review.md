# TASK-20260722-103 falsification review

## Review boundary and provenance

This is an independent, non-operational academic mathematics review. It does
not design or run key-recovery software, target a real key or deployed system,
instantiate a standardized cryptographic curve, or provide operational
cryptanalytic instructions.

The producer files are the unchanged SHA-256-bound artifacts attested by
`TASK-20260722-107` and archived at commit
`8fc27312beea75c8e35fdcfdd2e89fda1bc60262`; the committed task card records
`TASK-20260722-108` completed at verification commit
`07fdfc4b6a04d2c25b81d6500be51f69fdd0911c`. The
`TASK-20260722-108/snapshot-receipt.json` file itself is the provisional
pending-post-commit form, so the task card supplies the durable commit and
parent metadata. `TASK-20260722-102` remains invalid because its archive commit
message omitted the archive task ID. That is an evidence-integrity event only,
not evidence for or against any mathematical claim.

## Reconstructed claim

Put `N=B^5`. Five signed, coloured, occurrence-labelled decks of size
`Theta(B)` yield `B^5` candidate five-source tuples. For a fresh target `R`,
the proposed exact object is

```text
z_R(T) = gcd(g_I(T), r_R(T)),
```

where `g_I` has one root for each fifth occurrence and the asserted
complete-chart resultant `r_R` vanishes at a label exactly when that occurrence
extends to a valid pair-pair relation. A nontrivial support factor is intended
to permit adaptive dyadic restrictions that replay one exact signed labelled
source tuple.

There is no constructor in the package. The retained item is an obligation to
construct the target-dependent support predicate directly from compact
source-labelled pair data, without supplying `r_R mod g_I`, `z_R`, a source,
a scalar character, target-fitted advice, or a represented `B^3` payload. This
is internally a known interface: `FINDING-PF-IC-001` already records the P1513
common-factor locator, P1515 support/source router, and P1551/P1552
endpoint-coefficient/source-unranking frontier. The producer is therefore
right not to claim a new conjecture.

## Oracle and semantic objections

The package does not contain a self-contained definition or proof of the
load-bearing statement

```text
r_R(t_a)=0  iff  occurrence a extends to a valid signed relation.
```

The phrase “complete-chart intersection resultant” is still a macro at this
review boundary. A durable theorem candidate must name the base rings,
projective charts, saturations, occurrence maps, multiplicity policy, and
handling of infinity, identity, tangent, vertical, repeated, collision, and
nonreduced fibers. Resultants and projective closure can create extraneous
support; squarefree reduction can erase multiplicity information needed by
replay. This is a missing premise, not a counterexample to an earlier proof.

Even an exact `z_R` is only fifth-label support. It does not contain the other
four source labels. The claimed `O(log B)` replay is sound only if every
positive and negative restricted query is itself built from the same compact
input, remains biconditional after prior choices, and carries no precomputed
parent pointers or supplied restricted residues. One complete symbolic replay
transcript is a cheaper discriminator than a toy run.

## Generic-model gate

The requested setup/query rectangle already forces genuine non-genericity. In
the generic preprocessing model, advice `S` and constant-success query work
`T` obey, up to polylogarithmic factors,

```text
S*T^2 = Omega(N).
```

At the producer's caps,

```text
S = B^(9/4),  T = B^(5/4),
S*T^2 = B^(19/4) < B^5 = N.
```

Equivalently, generic advice `B^(9/4)` requires
`T=Omega_tilde(B^(11/8))`, larger than the desired `B^(5/4)`. Thus a candidate
that still works after concrete coordinates are replaced by random generic
encodings is rejected before any full theorem audit. A survivor must identify
and charge the exact finite-field coordinate operation that defeats this
simulation. Gauge invariance alone does not establish non-genericity.

## Exponent reconstruction

The time arithmetic is internally consistent as a conditional budget:

```text
Pollard rho                         B^(5/2) = N^0.50
preprocessing cap                  B^(9/4) = N^0.45
B targets times B^(5/4) per query  B^(9/4) = N^0.45
factor-log algebra, if valid       B^2     = N^0.40
one masked descent                 B^(5/4) = N^0.25
maximum conditional time           B^(9/4) = N^0.45
```

This establishes only the arithmetic of the proposed caps. It does not
establish an algorithm because the constructor, constant success, independent
rank, factor-log completion, and identical blind descent are all missing.

The memory claim is undercharged. The obligation allows retained advice/state
`B^(9/4)=N^0.45`, while the conditional path claims total memory
`B^2=N^0.40`. Retained preprocessing state remains live during queries. The
honest bound is therefore at most `N^0.45` unless a successor separately proves
that all retained advice and state fit `B^(2+o(1))`.

## Density, rank, and descent

Tuple mass is not target success. Under a uniform-endpoint heuristic,
`B^5=N` tuples give expected representation count `Theta(1)`, but
`E[X]=Theta(1)` does not imply `Pr[X>0]=Theta(1)`. Structured decks can
concentrate many representations on few targets. If hit probability is
`B^(-delta)`, relation and descent work acquire a `B^delta` factor. A support
size or second-moment theorem is required.

Likewise, `Theta(B)` valid rows do not establish `Theta(B)` independent rows.
Colouring, signs, repeated points, and support concentration can create
structural nullspaces. The `B^2` sparse-linear-algebra term is a reasonable
conditional cost for a `Theta(B)`-dimensional, constant-row-weight matrix, but
only after its exact columns, rank distribution, oversampling, rejected rows,
and modulus are fixed.

Finally, relation targets with known logarithms do not imply descent on an
unknown target. The same code and retained state must work on a fresh uniformly
blinded target without a scalar character, target-trained coefficient,
successful-branch cache, or known-scalar orientation. Mask failures, ambiguity,
unmasking, and final verification must be charged. The producer lists these
assumptions, so they are not literally hidden, but the label “conditional
0.45 path” must never be shortened to an achieved exponent.

## Baseline comparison

- Pollard rho costs `B^(5/2+o(1))=N^(1/2+o(1))` work with small serial
  memory and is the correct generic baseline. Parallel wall-clock claims must
  match processor count and memory traffic.
- Baby-step/giant-step has the same `B^(5/2)` work exponent and
  `B^(5/2)` memory. It is not the strongest practical memory baseline, but it
  is a required square-root comparison.
- The closest specialized baseline is source-reporting five-sum, or `k=6`
  indexing when the `B` known targets are treated as a sixth list. Explicit
  splits have `(state, query)` equal to `(B^2,B^3)`, `(B^3,B^2)`, or
  `(B^4,B)`; the balanced full campaign costs `B^3`, above the `B^(9/4)`
  cap.
- The reviewed Dinur--Golovnev control gives
  `S=soft-O(B^(5.5-delta))`, `T=soft-O(B^delta)`, with
  `soft-O(B^5)` preprocessing. Its best recorded setup exponent is `4.5`;
  the asymmetric `B^2/B^3` form leaves setup exponent at least `4.75` when
  query exponent is capped at `1.25`.

These positive-algorithm comparisons show that checked routes miss the target
rectangle. They are not lower bounds against arbitrary nonlinear finite-field
representations.

## Novelty and source completeness

The “known” label is justified as an internal deduplication result. The package
does not justify a global literature-exhaustion claim: the knowledge index has
41 entries, most frontier statements are `reported` rather than independently
rederived from primary sources, one citation is explicitly unverified, and the
producer supplies no reproducible database, query, or inclusion protocol for
its six-item external search. The narrow safe wording is exactly “no new
conjecture in this package” and “no checked source supplies the constructor.”
Absence of construction is neither external novelty nor impossibility.

## Cheapest next gate

Before the producer's full typed theorem audit, use a zero-compute
constructor-admission gate. Require one self-contained sheet containing:

1. exact definitions and a support proof for `r_R` and `z_R`;
2. one explicit compact fresh-target update identity or recurrence;
3. dimensions and target dependence of every input, state, and output;
4. a generic-encoding-erasure analysis naming the non-generic operation; and
5. initial time and live-memory recurrences with no supplied forbidden payload.

If any item is an untyped whole-divisor, resultant, common-factor, source,
coefficient, or scalar oracle, return `NO_ADMISSIBLE_CONSTRUCTION` and stop.
Only a passing sheet warrants the larger typed theorem proof. A pass still says
nothing about density, rank, descent, or ECDLP advantage.

## Verdict

The producer's narrow conclusion survives: no new conjecture was produced, and `OBL-ZR-COMPACT-CONSTRUCTOR-001` remains an internally known open construction interface rather than an impossibility claim. The standard represented and indexing routes reviewed here miss the stated rectangle, but the exact support object is not self-containedly proved in this snapshot, no constructor exists, and the `N^0.45` path remains conditional on unproved density, rank, factor-log, replay, and scalar-blind descent premises. The time-exponent arithmetic is correct only as a budget identity; the memory exponent is undercharged and is `N^0.45`, not `N^0.40`, unless retained state is tightened. The next action is the cheaper stage-zero constructor-admission and genericity gate, with no run or toy experiment.
