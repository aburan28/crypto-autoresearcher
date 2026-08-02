# Coordinate Decomposition Theories: Cycle 2

## Evidence entering this cycle

`OBSERVATION`, `TOY-EVIDENCE`: In `EXP-ECDLP-ENERGY-001`, random five-term target coverage tracked

```text
1 - exp(-binomial(B + 4, 5) / q)
```

rather than `1 - exp(-B^5/q)`. The scalar-progression control compressed intermediate sumsets and increased pair energy, but usually destroyed final target coverage. The next objective is therefore **high final expansion with cheap or compressed intermediate joins**, not pair concentration alone.

## Theory 1: Symmetry-corrected split compiler

### Candidate

Exploit permutation-aware occupancy and sign-canonical factor bases to size `B` correctly and reduce redundant split-table work without reducing `mF` coverage.

### Status

HYPOTHESIS

### Core mechanism

Choose the smallest even `B` satisfying `binomial(B+m-1,m)/q >= lambda`, compile `floor(m/2)F` and `ceil(m/2)F`, and query targets by iterating the smaller support. Compare sign-canonical and sign-complete sets at equal point cardinality.

### Why it might evade the current barrier

It removes factorial overcount and explicit sign duplication from the cost model. This cannot change the `q^(1/m)` factor-base exponent by itself, but it may materially change which `m` and split are viable in a batched fixed-curve compiler.

### Minimal test

Sweep `m in {5,6,8}`, three monotone prime subgroup sizes, two seeds, and random/coordinate/AP controls. Measure support growth, advice entries, online additions/lookups, storage, and target success.

### Likely failure

Canonicalization may save only a constant factor, while coordinate sets remain indistinguishable from random sets at every split level.

### Learning if it fails

It establishes a trustworthy symmetry-corrected baseline for all later recursive-circuit experiments.

## Theory 2: Expanding compositional-map union

### Candidate

Use a union of several shallow rational-map images whose components have compact source circuits but whose cross-component sums expand nearly randomly.

### Status

CONJECTURE

### Core mechanism

Each component is source-compressible, such as `x=t^2+c`, a Mobius image, or a two-level composition. The union is selected to preserve high `mF` support while allowing intermediate sums to be indexed by source tags and component pairs rather than a flat point table.

### Why it might evade the current barrier

The first experiment tested only the aggregate point set. A source-tagged union may expose a compressed recursive circuit even when its aggregate pair energy is random-like.

### Minimal test

Compare flat advice with component-tagged advice for two-, three-, and four-way joins. Require identical recovered witnesses and at least `0.8x` random final coverage with at most `0.8x` flat advice or online work.

### Likely failure

Cross-component source tags may not predict EC sums, so the tagged representation degenerates to the flat table.

### Learning if it fails

It distinguishes lack of source composability from lack of additive expansion.

## Theory 3: Coordinate-signature batch routing

### Candidate

Use a small vector of coordinate predicates or characters as a learned-but-audited routing signature for partial sums, then batch many targets through only compatible join buckets.

### Status

CONJECTURE

### Core mechanism

Compile partial sums into buckets indexed by exact low-cost signatures such as low coordinate bits, Legendre characters of shifted coordinates, or rational-map source tags. For a target batch, learn only the routing order on training curves; witness acceptance remains exact EC arithmetic.

### Why it might evade the current barrier

The signature need not be a homomorphism. It only needs conditional entropy low enough to reduce bucket probes across many fixed-curve targets while preserving exact verification.

### Minimal test

Measure mutual information between target-compatible complements and signatures, bucket imbalance, false-candidate work, exact witness recovery, memory traffic, and amortized operations for batch sizes `1, 16, 256`.

### Likely failure

Coordinate signatures may be pseudorandom under EC addition, yielding no routing information beyond chance or creating adversarially imbalanced buckets.

### Learning if it fails

It supplies a concrete structured-generic barrier datum for coordinate predicates rather than an intuition-only dismissal.

## Proof track

- Formalize the unordered multiset occupancy approximation and its error terms for random subsets of a cyclic prime-order group.
- Derive necessary support-size conditions for a split compiler with success probability `epsilon`.
- Express the fixed-curve advice/query diagnostic in entries, bytes, field operations, and memory traffic.

## Disproof track

- Construct high-energy sets with small `mF` to show why pair concentration is insufficient.
- Test whether every source-tagged map union loses its compression once cross-component sums are included.
- Compare signature routing against shuffled signatures and matched random point sets.
