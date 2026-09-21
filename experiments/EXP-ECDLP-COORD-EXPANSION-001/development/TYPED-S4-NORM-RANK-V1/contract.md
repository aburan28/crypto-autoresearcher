# Experiment Contract: Typed S4 Norm-Rank V1

## Hypothesis

For the exact complete five-input RCB addition circuit on heterogeneous source
axes `[A,R,R,R,R]`, the public group progression A causes the first
norm-locator tensor and its early Hadamard powers to have materially smaller
central unfolding ranks than a public random unknown-log A of the same size.

Such a reduction would be a precondition, not a proof, for a typed recursive
S4 compiler with shared work across the orbit `Q-P0-iD`.

## Null Hypothesis

After matching curve, R, source cardinalities, target construction, field, and
addition circuit, progression A does not reduce both central ranks by at least
20 percent relative to random A, or the relevant ranks saturate their ambient
dimensions.

## Parameters

- input: immutable `TYPED-FIVE-EC-V1/raw-result.json`;
- curves: its 10/12/14-bit generated ordinary prime-order curves;
- R families: random-x, source-PRF-x, x-interval, rational-union;
- A variants:
  - public progression from the typed relation experiment;
  - public hash-to-curve random unknown-log set of equal cardinality;
- source shape: `|A| x |R| x |R| x |R| x |R|`;
- target: a deterministic planted sum with one index from each source axis;
- circuit: four left-associated complete RCB additions;
- locator residual:
  - `eX = X*ZQ-XQ*Z`;
  - `eY = Y*ZQ-YQ*Z`;
  - `hQ = eX^2-nu*eY^2`, where `nu` is a nonsquare in `F_p`;
- tensors: `h`, `h^2`, `h^8`, and exact zero indicator
  `1-h^(p-1)`;
- rank field: `F_p`;
- cuts: all four for `h` and the indicator; central cuts two and three for
  `h^2` and `h^8`.

## Metrics

- exact source tuple count and RCB calls;
- source replay mismatches and invalid projective outputs;
- exact zero-set mismatches and witness count;
- unfolding dimensions, rank, ambient rank, and rank/ambient ratio;
- finite-field elimination operations and traffic proxy;
- progression/random-A rank ratios at matched cells;
- source construction, tensor construction, peak RSS, serialized bytes, and
  wall time;
- source/result/command/Git hashes.

## Positive Controls

- a rank-one separable tensor;
- a single-spike tensor;
- a deterministic dense hash tensor;
- every planted target has at least one exact witness;
- norm zero status must equal independent affine point equality for every
  enumerated source tuple.

## Negative Control

Public random A is matched in cardinality and excludes R. It removes the group
progression while retaining unknown logs and public point construction.

## Success Criterion

A provisional positive signal requires, on all three curves and at least
three of four R families:

- progression/random-A rank ratio at most 0.8 at both central cuts for `h^8`;
- no source, zero-set, or planted-witness mismatch;
- no ambient saturation at the promoted cuts;
- the same direction at `h^2`.

This authorizes only a constructive core-generation successor.

## Falsification Criterion

The hypothesis is narrowed if the matched rank ratio exceeds 0.8, changes
direction across cuts/sizes, or both variants saturate. A negative result
applies only to dense exact unfolding rank for this bound circuit and power
schedule. It does not rule out sparse cores, nonlinear selectors, alternate
addition trees, resultants, or other compressed S4 methods.

## Cost Boundary

The run enumerates every source tuple and is diagnostic only. Its enumeration
cost is explicitly charged and is never treated as a compiler.

For the typed ECDLP route, with `B=q^(1/5)`, a promoted successor must still
show:

- complete fixed-curve build `P=q^p` with `p<1/2`, including source
  construction, writes, and retained-state generation;
- retained advice `S=q^s` and peak workspace `M=q^m` with `s,m<1/2`,
  including representation overhead and traffic;
- relation collection
  `q^(c+u+r+max(t,w)+o(1))` with exponent `<1/2`, where `c=1/5`,
  `t` is total target-specialization cost, `w` is witness-lift cost,
  support is `q^(-u)`, and independent-row yield is `q^(-r)`;
- an executed sparse quotient solver with exponent `<1/2`; the dense
  diagnostic elimination used here is not that solver;
- arbitrary-target randomized descent with
  `u+max(t,w,c)<1/2`, including failure amplification and randomizer
  subtraction;
- processor, aggregate-work, per-worker-memory, and communication accounting
  against automorphism-aware parallel rho.

At the intended `c=t=w=1/5`, relation collection additionally requires the
strict condition `u+r<1/10`.

The generic fixed-generator `ST^2` frontier is a model-bound comparator. It
does not replace the stricter `s<1/2` requirement for a one-instance
sub-rho claim using named elliptic coordinates.

Low output rank alone is circular unless cores can be constructed without
enumerating the unknown zero set.

## Reproduction Command

```bash
python3 src/typed_s4_norm_rank.py \
  development/TYPED-FIVE-EC-V1/raw-result.json \
  --families random_x source_prf_x x_interval rational_union \
  --a-variants progression random \
  --powers 1 2 8
```
