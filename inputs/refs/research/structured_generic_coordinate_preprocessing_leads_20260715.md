# Structured-generic coordinate and fixed-curve preprocessing leads

Date: 2026-07-15

## Executive classification

- Overall status: `OPEN / LITERATURE-MAPPED / MODEL-BOUND`.
- Positive target: a coordinate-specific relation compiler or decomposition
  join whose charged fixed-curve online tradeoff beats the generic
  preprocessing frontier.
- Negative target: a concrete expansion or structured-group theorem for
  coordinate-defined factor bases and recursive addition circuits.
- Evidence in this note: literature-derived theorems and explicit complexity
  algebra only. There is no ECDLP run or performance result here.
- Deployment relevance: none. All proposed experiments use generated toy
  curves and held-out random targets.

## Primary sources checked

1. Henry Corrigan-Gibbs, Alexandra Henzinger, and David J. Wu,
   [The Structured Generic-Group Model](https://www.cs.utexas.edu/~dwu4/papers/SGGM.pdf),
   EUROCRYPT 2026 / IACR ePrint 2026/384.
2. Henry Corrigan-Gibbs and Dmitry Kogan,
   [The Discrete-Logarithm Problem with Preprocessing](https://people.eecs.berkeley.edu/~henrycg/pubs/eurocrypt18discrete/),
   EUROCRYPT 2018 / IACR ePrint 2017/1113.
3. Lior Rotem and Gil Segev,
   [A Fully-Constructive Discrete-Logarithm Preprocessing Algorithm with an Optimal Time-Space Tradeoff](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.ITC.2022.12),
   ITC 2022.
4. Omran Ahmadi and Igor Shparlinski,
   [On the Sum-Product Problem on Elliptic Curves](https://arxiv.org/abs/0806.0640),
   2008.
5. Igor Shparlinski,
   [On the elliptic curve analogue of the sum-product problem](https://doi.org/10.1016/j.ffa.2007.12.002),
   Finite Fields and Their Applications 14(3), 2008.
6. Christophe Petit, Michiel Kosters, and Ange Messeng,
   [Algebraic approaches for the Elliptic Curve Discrete Logarithm Problem over prime fields](https://www.iacr.org/archive/pkc2016/96140156/96140156.pdf),
   PKC 2016.

Novelty is not claimed. The literature search did not locate a published batch
point-decomposition algorithm for random prime-field curves that gives a
charged exponent below `1/2`.

## Finding 1: the structured theorem is stronger, but its EC instantiation is open

### Status

`RESTRICTED THEOREM / LITERATURE-DERIVED`

The structured generic-group model gives an algorithm free access to a partial
binary operation `star` on labels. Wherever `star` is defined, it agrees with
the hidden group operation. A label is constrained if it occurs as an input or
output of a defined `star` relation. In the paper's base definition, the
structured label space is a commutative monoid with unique factorization.

For a prime-order group of order `q`, if a `delta` fraction of labels is
constrained, Theorem 3.2 bounds non-preprocessed advantage by terms of order

```text
T^2/q + delta*T.
```

More importantly for a fixed curve, Appendix B, Theorem B.1, allows arbitrary
offline group-oracle queries that are compressed to `S` bits of advice and
bounds advantage by

```text
soft-O(S*T^2/q + delta*T).
```

The theorem is existential over a hard distribution of structured labeling
functions. It is not a lower bound for a named concrete elliptic curve.

Section 5.3 explicitly lists special-case elliptic-curve discrete-log algorithms
among applications that the authors have not yet attempted to model. The paper
does not instantiate its interface with an `x`-coordinate predicate, a Semaev
summation relation, a recursive addition circuit, or a batch witness-recovery
oracle. This is the immediate theory gap.

### Why coordinate decompositions do not drop directly into `star`

A prime-field factor base such as

```text
F = {P in E(F_p): L(x(P)) = 0}
```

offers cheap membership, not a unique factorization operation. A point may
have zero, one, or many `m`-term decompositions over `F`. A useful attack must
also recover witnesses, and a recursive `S3`/`S5` circuit exposes intermediate
points whose labels need not lie in `F`. These properties violate or go beyond
the simplest unique-factorization, partial-binary interface.

Therefore neither of the following substitutions is currently justified:

- setting `delta = |F|/q` and declaring the model applicable;
- treating a summation-polynomial decision oracle as a free `star` operation.

Both require a new model and a proof that its oracle captures the actual cost
and information exposed by coordinate arithmetic.

## Finding 2: additive energy is the clean concrete bridge

### Status

`HYPOTHESIS / OPEN`

Let `F` be a coordinate-defined subset of a prime-order elliptic-curve group,
with `B = |F| approximately q^(1/5)`. Define its group-additive energy

```text
E2(F) = #{(a,b,c,d) in F^4: a+b=c+d}.
```

Cauchy-Schwarz gives

```text
|F+F| >= B^4/E2(F).
```

A random set below the square-root density has energy dominated by diagonal
solutions, so the benchmark behavior is `E2(F) = B^(2+o(1))` and
`|F+F| = B^(2-o(1))`. At `B=q^(1/5)`, this means an intermediate two-sum set of
about `q^(2/5)` elements.

If a proposed compiler exposes every pair addition in `F x F` for free and
`F+F` has that size, at least about a `q^(-3/5)` fraction of group labels become
constrained. The structured density term alone then does not yield a
sub-square-root algorithm. This is only an exponent sanity check: the current
theorem's unique-factorization and hard-labeling hypotheses still have to be
proved for the concrete construction.

The useful concrete theorem target is one of:

1. Expansion: prove near-minimal energy, and analogous higher energy bounds,
   for intervals, rational-map images, unions of maps, or recursive coordinate
   predicates on random ordinary curves.
2. Loophole: exhibit a succinct witness-recovering representation of `F+F` or
   a higher recursive join that avoids enumerating its near-maximal cardinality.

The second outcome would be the cryptanalytic signal. Merely observing a small
sumset is insufficient unless membership and source recovery are also cheap.

## Finding 3: existing EC sum-product results miss the critical scale

### Status

`RESTRICTED THEOREM / NEGATIVE APPLICABILITY RESULT`

The 2008 elliptic sum-product papers prove genuine coordinate expansion
statements, but not the critical claim needed here.

- Shparlinski studies the tension between the field-coordinate sumset
  `{x(R)+x(S)}` and the coordinate image of the group sum
  `{x(R+S)}`. At least one expands in the covered regimes; this does not force
  the group-sum side alone to expand for a chosen coordinate factor base.
- Ahmadi-Shparlinski study sets built from scalar coefficients, including
  `{x(aP)+x(bP)}` and `{x(abP)}`. Their nontrivial corollaries require sets far
  larger than `q^(1/5)` when the point order is comparable to `q`.
- These results do not analyze five-term witness recovery, balanced recursive
  `S3` circuits, or amortized decomposition of many random targets.

This is a scoped applicability result, not evidence that coordinate expansion
cannot be proved at `q^(1/5)`. The next proof attempt should work directly with
the group energy of the coordinate-defined set, rather than scalar-product
sets whose known bounds start in a much denser regime.

## Finding 4: fixed-curve preprocessing has exact exponent targets

### Status

`RESTRICTED THEOREM / EXPERIMENT DESIGN`

For a generic fixed group, the 2018 lower bound is, up to logarithmic factors,

```text
S*T^2 >= epsilon*q,
```

where `S` is advice bits, `T` is online time, and `epsilon` is success
probability. Rotem-Segev give a fully constructive generic algorithm matching
the tradeoff in their stated parameter range. In exponent notation, for
constant success, `S=q^sigma` and `T=q^tau` must satisfy

```text
sigma + 2*tau >= 1.
```

The resulting online targets are:

| Advice exponent `sigma` | Generic online floor `tau` |
|---:|---:|
| `0` | `1/2` |
| `1/5` | `2/5` |
| `3/10` | `7/20` |
| `1/3` | `1/3` |
| `2/5` | `3/10` |
| `1/2` | `1/4` |

A coordinate-specific fixed-curve compiler is interesting only if its measured
held-out tradeoff has `sigma+2*tau<1` at matched success, or if it improves a
separately declared resource such as memory bandwidth. Unlimited offline work
does not disappear: it must be reported even though the generic theorem allows
arbitrary offline queries before compressing them into advice.

Required accounting for every claim:

- offline field multiplications and wall-clock time;
- advice bits, resident memory, and memory traffic;
- online field and group operations;
- random held-out targets supported, not just curated targets;
- success probability and failure distribution;
- fixed generator, fixed curve, field modulus, and curve special structure;
- batch size and amortized versus per-target cost.

For nonconstant success `epsilon=q^(-kappa)`, the comparison line becomes
`sigma+2*tau >= 1-kappa`. Reporting a fast online exponent without `kappa`
would be misleading.

## Candidate theorem: coordinate-circuit expansion

### Claim or task

For random ordinary prime-field curves and specified factor-base families,
bound the additive energy and source multiplicity of every intermediate set in
a balanced five-term addition circuit.

### Status

`CONJECTURE`

### Assumptions

- `E(F_p)` contains a prime-order subgroup of order `q approximately p`.
- Curves and seeds are sampled before factor-base parameters are fit.
- `|F| = q^(1/5+o(1))`.
- Exceptional denominators and sign symmetry are accounted for explicitly.

### Evidence so far

- Generic random-set heuristics predict `|2F| approximately B^2` and one
  five-term representation per random target on average.
- Existing sum-product theorems establish related expansion phenomena only in
  different or denser regimes.
- The structured generic-group theorem identifies constrained-label density as
  a barrier but does not prove this concrete coordinate statement.

### Failure modes

- A coordinate family has large additive energy due to an unnoticed subgroup,
  isogeny, automorphism, or sign artifact.
- `2F` expands but has a succinct source-recovering representation.
- Pairwise expansion does not control the collision pattern of a recursive
  five-term circuit.
- The empirical range is too small for exponent inference.

### Next concrete action

Implement a verifier-first energy and occupancy sweep for one frozen P1436 cell,
then extend only after independent arithmetic replay passes.

### Artifact paths

- `research/structured_generic_coordinate_preprocessing_leads_20260715.md`
- `ecdlp_index_calculus_state/experiment_contract_p1466_verification_first_untrusted_one_cell.md`

## Experiment Contract: P1469 coordinate energy and recursive occupancy

## Hypothesis

At least one nonrandom coordinate family has a reproducible deviation in
energy, occupancy, or source-recovery cost that survives matched random controls
and suggests a compressed recursive join.

## Null hypothesis

All tested families have random-set-scale additive energy and recursive
occupancy once sign, curve, and cardinality controls are matched, or any
compression loses source witnesses and offers no charged work reduction.

## Parameters

- field/curve family: generated ordinary prime-field curves;
- sizes: at least three feasible bit sizes after the one-cell preflight;
- seeds: preregistered and held out from implementation;
- factor base: interval, random coordinate set, rational-map image, union of
  maps, and model/isogeny-transformed image;
- relation shape: balanced five-term circuit, with two- and three-input
  intermediate sets;
- baseline: matched random set, explicit hash join, BSGS/MITM, and rho in a
  common field-operation model.

## Metrics

- group and field operations;
- `E2`, sampled higher energies, and sumset occupancy;
- source multiplicity and witness-recovery work;
- bucket entropy, maximum load, and peelable/core fractions;
- memory, bytes read/written, and random-access count;
- five-term representation probability per held-out target;
- batch amortization and end-to-end fitted exponent.

## Positive control

A deliberately subgroup-like or low-dimensional toy set with known excess
energy and a recoverable compressed description.

## Negative control

A cardinality- and sign-matched random point set on the same curve.

## Success criterion

A preregistered coordinate family must show both:

1. a replicated exponent-level reduction in charged join or witness-recovery
   work relative to the matched random/hash join; and
2. a concrete path to an end-to-end fixed-curve tradeoff below
   `sigma+2*tau=1`, or a single-instance fitted total exponent below `1/2`.

## Falsification criterion

No family survives held-out replication, or every occupancy deviation is paid
back by source recovery, memory traffic, relation rank, or target descent.

## Reproduction command

```bash
# To be filled only after P1466 independent arithmetic verification authorizes
# expansion beyond one frozen cell.
```

## Three candidate theories

### Conservative extension

Measure exact/sampled additive energies and recursive source multiplicities for
existing factor bases. It may expose a usable nonrandom bucket law; it likely
fails because pair sums expand like a random set. Either result calibrates the
structured density parameter with concrete coordinates.

### Representation change

Compile each recursive addition node to a coordinate sketch that supports both
membership and source recovery, then compare intervals, rational maps, unions,
and isogenous/model-transformed coordinates. It may evade explicit `B^2`
materialization; it likely fails because sketch collisions or openings restore
the missing work. The useful output is an exact source-cover/opening bound.

### High-risk fixed-curve theory

Build a reusable, memory-bounded tensor or algebraic-sketch index for five-term
decomposition and query many held-out targets. It may exploit fixed-curve reuse
that single-instance analysis discards; it likely lands on or above
`S*T^2=q`. The useful output is the first coordinate-specific measurement of
distance from that frontier with offline work and bandwidth fully charged.

## Handoff: model the concrete loophole, not just density

### Claim or task

Decide whether coordinate-defined recursive decomposition offers a succinct,
source-recovering operation outside the current structured-generic interface.

### Status

`OPEN`

### Assumptions

- Only generated toy curves and held-out random targets are used.
- Correctness is established by a verifier independent of the generator.
- No one-cell observation is promoted to an exponent claim.

### Evidence so far

- The structured preprocessing theorem gives the right high-level comparison
  line but does not instantiate coordinate predicates or multi-witness circuits.
- Existing elliptic sum-product results do not reach the critical
  `B=q^(1/5)` decomposition regime.
- Generic fixed-curve preprocessing gives exact storage/online targets to beat.

### Failure modes

- Rebranding explicit enumeration as a compiler.
- Omitting witness recovery, memory traffic, failed targets, or offline work.
- Using a special curve or field and claiming a generic-prime-field result.
- Treating a barrier in one restricted interface as a general impossibility.

### Next concrete action

Complete and independently audit P1466's verifier-first one-cell experiment;
if it passes, instantiate the P1469 energy/occupancy contract on the same frozen
cell before any sweep.

### Artifact paths

- `research/structured_generic_coordinate_preprocessing_leads_20260715.md`
- `tasks/ecdlp_index_calculus/p1466_untrusted_one_cell_generator.py`
- `tasks/ecdlp_index_calculus/p1466_independent_arithmetic_verifier.py`
