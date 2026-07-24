# Research Brief: Structured-Generic Barriers, Fixed-Curve Preprocessing, and Batch Decomposition

Date: 2026-07-12

Status: RESEARCH PROGRAM / HYPOTHESIS SET / MODEL-BOUND / TOY-EVIDENCE-PENDING

This brief turns the current operator lead into AutoLab-ready research tracks.
It does not claim an ECDLP break. It separates three different goals:

- single-instance prime-field ECDLP exponent improvement;
- fixed-curve preprocessing with separate offline and online accounting;
- coordinate-specific barrier theory for point-decomposition predicates.

## Working Assessment

The most actionable classical bet is not more generic Grobner tuning. It is a
compiled, batch, non-Grobner decomposition compiler for random ordinary
prime-field curves, tested against a severe end-to-end exponent gate.

The most timely theory bet is a concrete structured-generic or
additive-combinatorial barrier for coordinate predicates such as short-x
membership, `L(x)=0`, recursive addition-law circuits, and batched
decomposition. Plain generic-group lower bounds are useful baselines, but they
hide the actual coordinate structure that the current P1399-P1403 line is
probing.

The most practical classical bet is fixed-curve preprocessing. A standard curve
reused for many public keys is not the same object as a fresh one-shot ECDLP
instance. Any claim here must report offline work, storage, memory bandwidth,
online work, target count, success probability, fixed generator status, and
special structure of the modulus/curve.

## Source Map

Primary literature signals checked for this brief:

- Dinur, Keller, Marmor, 2025, "Non-Adaptive Cryptanalytic Time-Space Lower
  Bounds via a Shearer-like Inequality for Permutations",
  https://arxiv.org/abs/2505.00894
  - Generic DLOG preprocessing is explicitly modeled with advice `S` and
    online time `T`.
  - The paper summarizes Shoup's plain GGM lower bound: DLOG success after `T`
    generic queries is bounded by about `T^2/N`.
  - It also records adaptive preprocessing algorithms with
    `S*T^2 <= polylog(N)*N`, and sharp non-adaptive barriers.

- Ahmadi and Shparlinski, 2008, "On the Sum-Product Problem on Elliptic
  Curves", https://arxiv.org/abs/0806.0640
  - This is not an ECDLP algorithm, but it is close to the needed theory style:
    lower-bound expansion statements involving x-coordinates of elliptic-curve
    multiples.
  - Useful as a template for barrier work on coordinate predicates and
    addition-law circuits.

- Semaev, 2015, "New algorithm for the discrete logarithm problem on elliptic
  curves", https://arxiv.org/abs/1504.01175
  - Summation-polynomial and first-fall-degree line remains relevant for
    decomposition experiments.
  - The strongest claims are for binary fields under heuristics, not a generic
    ordinary prime-field break.

- Euler and Petit, 2021, "New results on quasi-subfield polynomials",
  https://arxiv.org/abs/1909.11326
  - Useful negative evidence: new small-characteristic polynomial families and
    a limiting theorem did not yield speedups over previous ECDLP approaches.
  - Lesson for AutoLab: new representation structure must change relation
    supply or online decomposition cost, not merely repackage a known system.

- Dzierzkowski, 2024, "The generalized method of solving ECDLP using quantum
  annealing", https://arxiv.org/abs/2410.08725
  - Confirms QUBO conversion can be generalized to arbitrary elliptic-curve
    models, but the demonstrated scale is tiny: the table reports 1248 D-Wave
    qubits for a subgroup of size 7, and the conclusion states larger 4-bit
    examples required a hybrid solver.
  - Treat as low-priority for asymptotic cryptanalysis.

- Roetteler, Naehrig, Svore, Lauter, 2017, "Quantum resource estimates for
  computing elliptic curve discrete logarithms",
  https://arxiv.org/abs/1706.06752
  - Baseline Shor resource estimate: at most `9n + 2ceil(log2(n)) + 10`
    logical qubits and `448 n^3 log2(n) + 4090 n^3` Toffoli gates.

- Babbush et al., 2026, "Securing Elliptic Curve Cryptocurrencies against
  Quantum Vulnerabilities: Resource Estimates and Mitigations",
  https://arxiv.org/abs/2603.28846
  - Whitepaper, not a classical algorithm. Reports `<1200` logical qubits and
    `<90M` Toffoli gates or `<1450` logical qubits and `<70M` Toffoli gates
    for 256-bit ECDLP, with undisclosed circuit details validated through a
    zero-knowledge proof.

- Schrottenloher, 2026, "Optimized Point Addition Circuits for Elliptic Curve
  Discrete Logarithms", https://arxiv.org/abs/2606.02235
  - Gives an explicit logical-circuit architecture close to Babbush et al.:
    slightly more qubits and fewer Toffoli gates for secp256k1.

- Luo, Yang, Wang, Su, Li, 2026, "Space-Efficient Quantum Algorithm for
  Elliptic Curve Discrete Logarithms with Resource Estimation",
  https://arxiv.org/abs/2604.02311
  - Independent space-efficient Shor implementation line. Reports
    `5n + 4 floor(log2 n) + O(1)` qubits and a 256-bit estimate of 1333
    logical qubits.

## Current AutoLab Boundary

The P1399-P1402 line is relevant but not yet a breakthrough:

- P1399 gave a public short-x row index and reduced candidate verifications,
  but produced no held-out verifier/RHS/rank closure.
- P1400 x-only S3 pair-chain certificates preserved relation counts but widened
  candidate buckets and stayed above the useful cost boundary.
- P1401 x-only S5-consensus did not narrow P1400.
- P1402 explicit orientation narrowed P1400/P1401 back to the P1399 boundary:
  `2864` certificate-policy verifications, ratio `1.0` versus P1399, no
  held-out closure, and `1187460` charged pair-sum constructions.

Therefore P1403 should not be "more orientation accounting." It should be one
of:

- a true symbolic S5 finite-field backend that predicts row buckets without
  reconstructing the P1399 candidate-x index; or
- a quotient/rational-map/factor-base generator that changes relation supply
  before row-index verification.

## Lead Ranking

### 1. Structured coordinate barrier for P1399-P1403 style predicates

Status: OPEN / MODEL-BOUND / THEORY-AND-EXPERIMENT

Candidate: instantiate a structured-generic model for concrete coordinate
predicates and recursive addition-law circuits, then either prove expansion or
find the loophole that a decomposition compiler can exploit.

Assumptions:

- Prime-order subgroup of an ordinary random curve over `F_p`.
- Public coordinate predicates are allowed: short-x intervals, residues,
  rational maps, low-degree `L(x)` tests, recursive S3/S5 addition circuits.
- No secret scalar, verifier label, or post-replay relation outcome may be used
  in the predicate.

Evidence type:

- Literature-backed MODEL-BOUND if proved.
- TOY-EVIDENCE if only measured over 40-96 bit random curves.

Falsification route:

- Exhibit a coordinate predicate/factor base for which `m`-term decomposition
  probability or batch amortization exceeds the random-sum model after all
  construction costs are charged.

Next experiment:

- Implement a coordinate-predicate expansion audit: for sets `F` of size
  approximately `n^(1/m)`, measure `|F +_E F|`, recursive `mF`, x-coordinate
  collision entropy, bucket concentration, and decomposition rate versus
  `|F|^m/n`.

### 2. Fixed-curve preprocessing relation compiler

Status: HYPOTHESIS / PRACTICAL-CLASSICAL / MODEL-BOUND

Candidate: build fixed-curve advice for a standard or synthetic fixed
`(E,P)` and later solve many independent targets `Q=xP` with online work below
the generic preprocessing frontier, or produce a precise negative result.

Assumptions:

- The curve and generator are fixed during preprocessing.
- Targets are drawn after advice generation.
- Success probability is measured over fresh target draws.
- Advice access cost and memory bandwidth are charged separately from arithmetic.

Evidence type:

- MODEL-BOUND for comparison against generic `S*T^2` frontier.
- TOY-EVIDENCE for 40-96 bit synthetic curves.

Falsification route:

- Online speedup disappears once memory bandwidth, cache misses, target descent,
  failed attempts, and relation matrix setup are included.

Next experiment:

- Build a fixed-curve relation compiler with advice sizes
  `S in {n^0.20, n^0.25, n^0.30, n^0.33}` and report offline field ops,
  bytes stored, random/sequential reads, online field ops, success probability,
  target count, and `S*T^2/n`.

### 3. Batch non-Grobner m-term decomposition sieve

Status: HYPOTHESIS / PRIME-FIELD-ATTACK-CANDIDATE

Candidate: for `m in {5,6,8}`, compile factor-base sets of size about
`n^(1/m)` and produce enough independent decompositions in total time
`n^(1/2 - epsilon)` without generic Grobner solving or exceptional curves.

Assumptions:

- Random ordinary prime-field curves at 40, 56, 72, 88, and 96 bits when
  feasible.
- Avoid smooth `p-1`, special j-invariants, anomalous curves, and
  hand-selected auxiliary structure.
- Include positive and negative controls.

Evidence type:

- TOY-EVIDENCE until scaling across at least three sizes is measured.
- HEURISTIC if fitted exponents are extrapolated.

Falsification route:

- Observed decompositions follow `B^m/n`, relation generation cost fits
  exponent >= `0.5`, or batch amortization does not reduce total exponent once
  setup and memory are charged.

Next experiment:

- Sweep factor-base definitions: intervals, random x-sets, coordinate residues,
  rational-map images, unions of maps, and model/isogeny transforms. Report
  relation probability, rank, peelable fraction, core size, memory traffic, and
  end-to-end recovery cost.

### 4. P1403 symbolic S5 backend or generator pivot

Status: OPEN / TOY-EVIDENCE / MODEL-BOUND

Candidate: replace P1402's oriented pair-sum bucket accounting with a true
symbolic S5 predicate or a generator-level quotient/rational-map change.

Assumptions:

- Same toy target and verifier policies as P1399-P1402 for continuity.
- Controls must reproduce identity/lower-shift behavior.
- Promotion requires held-out verifier/RHS/rank closure or relation-supply
  change before row-index lookup.

Evidence type:

- TOY-EVIDENCE, verifier-backed.

Falsification route:

- The backend preserves P1399/P1402 relation counts but does not reduce
  candidate verification below P1399, does not create held-out closure, and
  only moves costs between bucket predicates.

Next experiment:

- Implement symbolic S5 resultants/filtering with explicit y-sign/orientation
  terms, then compare against P1399/P1400/P1401/P1402 under identical
  candidate, replay, relation-count, RHS, rank, and source-cost accounting.

## Deprioritized Tracks

These are not closed globally; they are lower-priority under the present
objective.

- Generic Grobner tuning: useful for records and diagnostics, weak as a primary
  exponent-break bet unless the algorithm stops behaving like generic
  elimination.
- Pollard-rho hardware and parallelism: good for records and wall-clock
  reduction, not an exponent change.
- Isogeny walk until weak curve: no convincing generic mechanism because group
  order and embedding-degree constraints remain load-bearing. Isogenies may
  still matter as representation transforms for factor bases.
- Generic p-adic/Xedni-style lifting: useful only under special anomalous or
  local-structure assumptions; ordinary prime-field curves need an explicit
  subgroup-wide homomorphism or descent object.
- QUBO/annealing: current evidence is scale diagnostic, not asymptotic.

## Experiment Contract: Structured Coordinate Expansion Audit

### Hypothesis

Coordinate-defined factor bases on random ordinary prime-field curves exhibit
measurable non-random expansion, decomposition density, or bucket concentration
that can support a non-Grobner relation compiler.

### Null Hypothesis

For all tested coordinate predicates, recursive `m`-term decomposition follows
the random-sum model `B^m/n` up to sampling error, and expansion is sufficient
to block online exponent improvement.

### Parameters

- field/curve family: random ordinary prime-field curves, prime-order or
  large-prime-order subgroup
- sizes: 40, 56, 72, 88, 96 bits when feasible
- seeds: at least 10 per size
- factor base: intervals, random x-sets, `L(x)=0`, residues, rational-map
  images, unions of maps
- relation shape: `Q = P1 + ... + Pm`, `m in {5,6,8}`
- baseline: random-sum model and optimized rho field-op model

### Metrics

- group operations
- field operations
- memory traffic
- relation probability
- x-bucket entropy and max bucket mass
- expansion ratios for recursive sums
- rank and dependency profile
- wall-clock

### Positive Control

Use a deliberately structured toy curve or factor base where decomposition is
known to be biased or artificially planted.

### Negative Control

Use random point subsets of the same size and the same curve.

### Success Criterion

At least one public coordinate predicate produces a reproducible decomposition
or batch-amortization exponent below `0.5` after setup and memory are charged,
or a mathematically clean expansion counterexample suitable for theory work.

### Falsification Criterion

All predicates match random-sum density and fitted total exponent is `>= 0.5`
after accounting for failed attempts, setup, memory, rank, and individual logs.

### Reproduction Command

```bash
python3 tasks/ecdlp_index_calculus/structured_coordinate_expansion_audit.py \
  --bits 40,56,72,88,96 \
  --m-values 5,6,8 \
  --factor-bases interval,random_x,lx_zero,residue,rational_map,map_union \
  --seeds 10 \
  --out ecdlp_index_calculus_state/structured_coordinate_expansion_audit.json
```

## Experiment Contract: Fixed-Curve Preprocessing Compiler

### Hypothesis

A fixed-curve coordinate-specific advice compiler can reduce online work for
fresh targets below the generic preprocessing frontier in a way that survives
offline/storage/bandwidth accounting.

### Null Hypothesis

Any online gain is explained by generic preprocessing or disappears once advice
size, memory bandwidth, failed target descents, and matrix/rank costs are
included.

### Parameters

- field/curve family: one random curve per size, plus optional standard-like
  sparse-prime analogues
- sizes: 40, 56, 72, 88, 96 bits when feasible
- seeds: fixed curve seed plus fresh target seeds
- factor base: short-x/rational-map/union predicates
- relation shape: `m in {5,6,8}`
- baseline: generic preprocessing frontier `S*T^2/n`, BSGS, rho

### Metrics

- offline field operations
- advice bytes
- sequential and random memory reads
- memory bandwidth
- online field operations
- online group operations
- relation probability
- rank and target-descent success
- number of supported targets
- success probability

### Positive Control

Synthetic planted advice where the compiler is known to answer a bounded set of
targets faster than rho.

### Negative Control

Random advice of the same size and generic BSGS/rho preprocessing.

### Success Criterion

For fresh targets, measured online exponent beats the generic preprocessing
frontier at matched `S` and success probability, with all advice access and
target descent charged.

### Falsification Criterion

`S*T^2/n` does not improve over generic preprocessing, or online gains require
exceptional modulus/curve/generator structure not present in random controls.

### Reproduction Command

```bash
python3 tasks/ecdlp_index_calculus/fixed_curve_preprocessing_compiler.py \
  --bits 40,56,72,88,96 \
  --advice-exponents 0.20,0.25,0.30,0.33 \
  --targets 256 \
  --m-values 5,6,8 \
  --out ecdlp_index_calculus_state/fixed_curve_preprocessing_compiler.json
```

## Experiment Contract: Random-Curve Batch Decomposition Sieve

### Hypothesis

Batched processing of many targets through a compiled non-Grobner
point-decomposition sieve reduces amortized total exponent below rho on random
ordinary prime-field curves.

### Null Hypothesis

Batching only amortizes constants or setup; the total exponent remains `>= 0.5`.

### Parameters

- field/curve family: random ordinary prime-field curves
- sizes: 40, 56, 72, 88, 96 bits when feasible
- seeds: at least 10 per size
- batch sizes: 1, 8, 32, 128, 512 targets
- factor base: intervals, random x-sets, rational maps, map unions
- relation shape: `m in {5,6,8}`
- baseline: optimized rho with the same field-operation cost model

### Metrics

- decomposition attempts and successes
- total field multiplications
- memory traffic
- rank deficiency
- peelable fraction
- core size
- block-Wiedemann cost estimate
- target descent cost
- per-target amortized exponent

### Positive Control

Planted decomposition instances and a small weak curve/factor-base pair where
batching is known to help.

### Negative Control

Independent random target processing without shared advice.

### Success Criterion

Fitted total exponent `< 0.5` over at least three sizes on random curves with
preprocessing and memory included.

### Falsification Criterion

Fitted exponent `>= 0.5`, success depends on smooth `p-1` or special curves, or
linear algebra/target descent dominates.

### Reproduction Command

```bash
python3 tasks/ecdlp_index_calculus/random_curve_batch_decomposition_sieve.py \
  --bits 40,56,72,88,96 \
  --batch-sizes 1,8,32,128,512 \
  --m-values 5,6,8 \
  --out ecdlp_index_calculus_state/random_curve_batch_decomposition_sieve.json
```

## Experiment Contract: P1403 Symbolic S5 Or Generator Pivot

### Hypothesis

A true symbolic S5 finite-field backend or a lower-level quotient/rational-map
generator can beat P1402's P1399-equivalent oriented-pair indexing and create
held-out verifier/RHS/rank closure or relation-supply change.

### Null Hypothesis

The new backend only reproduces P1399/P1402 candidate indexing, preserves no
new closure, and adds source/certificate cost without changing relation supply.

### Parameters

- field/curve family: existing P1399-P1402 toy target and controls
- sizes: current modulus `9521` continuity run, then one fresh random toy curve
- seeds: existing held-out transfer split plus fresh held-out split
- factor base: P1398/P1399 quotient-basis policies plus generator pivot
- relation shape: S5 symbolic predicate and quotient/rational-map generator
- baseline: P1399, P1400, P1401, P1402, rho

### Metrics

- candidate constructions
- candidate verifications
- pair-sum or symbolic-filter source cost
- relation counts by policy
- held-out verifier closure
- RHS closure
- rank closure
- candidate ops/rho
- relation-supply delta before row-index lookup

### Positive Control

Identity/lower-shift controls reproduce transfer-0 closure where expected.

### Negative Control

P1402 oriented-pair bucket narrowing at exactly the P1399 verification boundary.

### Success Criterion

Either held-out verifier/RHS/rank closure appears under public pre-replay
criteria, or relation supply changes before row-index verification with cost
below the rho and P1399/P1402 baselines.

### Falsification Criterion

All held-out closures remain zero, relation counts are only preserved rather
than improved, and total cost is no better than P1399/P1402 once source/symbolic
cost is charged.

### Reproduction Command

```bash
python3 tasks/ecdlp_index_calculus/low_term_total2_p1403_symbolic_s5_or_generator_pivot_after_p1402.py \
  --out ecdlp_index_calculus_state/p1403_symbolic_s5_or_generator_pivot_after_p1402_probe.json
```

## Handoff: next research action

### Claim or task

Promote P1403 as the local AutoLab continuation while opening two parallel
research tracks: fixed-curve preprocessing and structured-coordinate barrier
theory.

### Status

OPEN

### Assumptions

- The current P1402 result is cost/selectivity evidence only.
- Fixed-curve preprocessing is a separate model from one-shot ECDLP.
- Coordinate predicates require structured models, not only plain GGM.

### Evidence so far

- P1402 narrows P1400/P1401 buckets to the P1399 boundary but gives no held-out
  closure.
- Generic preprocessing literature gives a real `S*T^2` frontier to compare
  against.
- Elliptic-curve x-coordinate expansion literature exists but does not yet
  close the concrete `L(x)=0` / recursive S5 / batch-decomposition gap.

### Failure modes

- Hidden post-verifier selection.
- Ignoring memory bandwidth and advice access.
- Counting only solved systems, not failed decomposition attempts.
- Comparing online-only fixed-curve performance to one-shot rho without
  reporting preprocessing.
- Mistaking bucket indexing for relation supply.

### Next concrete action

Implement `tasks/ecdlp_index_calculus/low_term_total2_p1403_symbolic_s5_or_generator_pivot_after_p1402.py` or, if prioritizing theory, implement `structured_coordinate_expansion_audit.py` with the random-curve controls above.

### Artifact paths

- `ecdlp_index_calculus_state/research_briefs/structured_generic_preprocessing_batch_decomposition_20260712.md`
- `research_ledger.md`
- `ecdlp_index_calculus_state/work_orders.json`
