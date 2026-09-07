# ECDLP research slate: symmetry-aware factor bases and local-global representations

Status: speculative research agenda. Nothing here claims an attack, speedup, or sub-square-root ECDLP algorithm.

## Motivation

Known ECDLP improvements repeatedly exploit structure that is invisible in the generic-group model: Frobenius on binary extension curves, descent, special embeddings, or arithmetic maps. The experiments below ask a narrower question: can representation choice reduce the *total* cost of relation generation or expose independently computable information about the unknown scalar?

Every experiment must compare end-to-end cost against the appropriate Pollard-rho baseline and account for setup, decomposition, relation collection, linear algebra, and individual-log recovery.

## IDEA-FROB-0: Frobenius orbits as first-class factor-base objects

For a Koblitz curve over `F_(2^m)`, Frobenius acts by

`pi(x,y) = (x^2, y^2)`.

For a point `P`, define the orbit

`O(P) = {P, pi(P), pi^2(P), ...}`.

On the large prime-order subgroup, Frobenius acts as multiplication by an eigenvalue `lambda` modulo the subgroup order `r`, so

`pi(P) = [lambda]P`

and therefore

`log_G(pi^i(P)) = lambda^i log_G(P) mod r`.

This means a Frobenius-stable factor base should be modeled by **one logarithm unknown per orbit**, not one unknown per point. If a full orbit has size `m`, an orbit representative plus a known exponent `i` identifies the point and contributes a known coefficient `lambda^i` to the relation row.

A relation such as

`R = P_1 + pi^3(P_2) + pi^7(P_3)`

becomes

`log_G(R) = X_1 + lambda^3 X_2 + lambda^7 X_3 mod r`,

where `X_j = log_G(P_j)` for canonical orbit representatives.

### Important dependency warning

Applying Frobenius to an entire relation generally gives a scalar/Frobenius transform of the same information, not a fresh independent relation. The harness must detect and discount these dependencies. The benefit comes from quotienting redundant columns/representatives and possibly simplifying decomposition, not from counting all orbit shifts as new relations.

### Why F_(2^131) is interesting

For prime extension degree `m=131`, full-size Frobenius orbits can have size 131. This makes orbit compression potentially large at the linear-algebra layer, but the actual research question is whether relation generation and point decomposition can also exploit this structure. A large matrix shrink is not enough if decomposition remains dominant.

### EXP-FROB-ORBIT-1: three-way decomposition encoding benchmark

Compare three encodings over a ladder of toy Koblitz curves:

1. **RAW** — current raw point-coordinate decomposition encoding;
2. **CANONICAL-ORBIT** — canonicalize every candidate point to an orbit representative before decomposition/row formation;
3. **REP+INDEX** — parameterize a point as `(orbit_representative, frobenius_index)` and solve using the representative plus a small orbit-index variable.

For each field size and decomposition arity `k`, measure:

- SAT/Groebner variable and constraint counts;
- median and tail solve time;
- decomposition success probability;
- number of candidate decompositions modulo permutation and Frobenius action;
- relation rank gain after removing Frobenius/scalar dependencies;
- memory use;
- total seconds and projected operations per independent usable relation.

The comparison must use identical targets, factor-base cardinality targets, timeouts, and solver settings.

### EXP-FROB-ORBIT-2: normal-basis cyclic-constraint test

In a normal basis, squaring/Frobenius is a cyclic coordinate permutation. Test whether the decomposition system can be rewritten so repeated Frobenius constraints become shared templates, circulant blocks, or permutation-indexed clauses rather than duplicated arithmetic.

Compare:

- generated gate/clause count;
- propagation/conflict statistics for SAT;
- Macaulay matrix size / degree-of-regularity proxy for Groebner variants;
- wall-clock relation throughput.

Reject the idea if syntactic compression does not translate into solver-time improvement.

### EXP-FROB-ORBIT-3: canonical representative strategies

Benchmark canonicalization rules for an orbit representative, including:

- lexicographically minimal normal-basis coordinate vector;
- minimum Hamming weight then lexicographic tie-break;
- minimum integer encoding;
- invariant-signature bucket plus lexicographic tie-break.

Measure canonicalization cost, collision behavior, orbit coverage, and effect on downstream decomposition locality/cache behavior. Canonicalization must be much cheaper than a group operation/relation solve to be worthwhile.

### EXP-FROB-ORBIT-4: orbit-aware relation independence

Instrument the relation collector so every accepted row carries provenance:

- orbit representatives used;
- Frobenius exponents;
- target provenance;
- normalized row hash;
- whether the row is a scalar/Frobenius multiple of a prior row;
- incremental rank delta.

The objective is to determine how much nominal relation multiplicity survives as actual linear information.

## IDEA-FROB-1: nonlinear Frobenius-stable factor bases

For Koblitz/subfield curves, do not restrict the search to Frobenius-invariant linear subspaces. Search families of nonlinear sets `F` with:

1. `pi(F) = F` or a small number of Frobenius-related components;
2. compact membership predicates;
3. controllable cardinality and orbit distribution;
4. decomposition equations whose degree/regularity is no worse than conventional bases.

Candidate families:

- normal-basis Hamming-weight shells and unions of shells;
- trace/norm level sets;
- zero sets of sparse linearized-plus-low-degree polynomials;
- intersections/unions of low-codimension Frobenius-stable varieties;
- orbit unions selected by cheap algebraic invariants.

### EXP-FROB-FB-1: predicate sweep

On toy Koblitz curves over `F_(2^m)`, enumerate candidate predicates at small `m`. For each candidate measure:

- `|F|` and number/orbit-size distribution under Frobenius;
- empirical decomposition probability for `k=2,3,4`;
- polynomial-system size and degree-of-regularity proxy;
- SAT/Groebner solve time per successful relation;
- relation independence rate;
- projected relation-collection + sparse-linear-algebra cost.

The objective is not smallest `|F|`. Rank by estimated **cost per independent usable relation**.

### EXP-FROB-FB-2: fixed-cardinality comparison

Choose several factor-base predicates with matched cardinality. This isolates whether geometry/predicate structure changes decomposition difficulty independent of factor-base size.

Compare conventional linear-subspace bases, Hamming-weight shells, trace/norm level sets, and best candidates from the predicate sweep.

## IDEA-FROB-2: symmetry-adapted decomposition coordinates

Treat Frobenius symmetry as part of the solver representation rather than only collapsing relation-matrix columns. Construct coordinates on decomposition tuples modulo Frobenius and permutation action, then compare them with the existing chained-S3/SAT encoding.

Questions:

- Can orbit invariants eliminate variables before SAT/Groebner solving?
- Can normal-basis cyclic structure turn repeated constraints into structured/circulant blocks?
- Can representative-plus-index coordinates reduce branching?
- Does quotienting introduce equations of higher degree that erase the benefit?

### EXP-FROB-SYM-1: quotient-vs-raw scaling ladder

For the same family of targets and factor bases, compare raw decomposition with symmetry-adapted variants over increasing `m`. Fit empirical growth rates to solver time and memory, while reporting uncertainty and timeout censoring.

### Falsification gate

Reject a representation if its measured relation throughput, after orbit multiplicity and independence corrections, is not better than the current baseline over a scaling ladder. A reduction in variable count alone is not evidence.

## IDEA-TORUS-1: representation search via algebraic groups/tori

Investigate Couveignes-Lercier-style field representations and algebraic-group constructions as a *factor-base design mechanism*. The goal is not to transfer arbitrary ECDLP to an easy torus DLP. Search for representations in which Frobenius/Galois action is simple and factor-base membership/decomposition becomes cheaper.

Automated search variables can include representation parameters, basis choice, trace/norm constraints, orbit structure, and decomposition arity. Record representation-construction cost explicitly.

For prime `m` such as 131, where simple invariant linear-subspace constructions may offer no useful intermediate dimension, prioritize nonlinear or multi-component constructions rather than repeatedly searching the same linear-subspace family.

### EXP-TORUS-1: representation generator

Build a toy-scale generator that enumerates admissible algebraic-group/torus-inspired field representations. Emit a normalized description of:

- field basis and arithmetic cost;
- Galois/Frobenius action;
- candidate smoothness/factor-base predicate;
- construction cost;
- expected orbit structure.

Feed each generated representation into the same factor-base/decomposition benchmark used by FROB-1/FROB-2.

### EXP-TORUS-2: same-curve representation A/B test

For each toy curve, hold the curve and target set fixed while changing only field/representation coordinates. Test whether any apparent win survives after accounting for conversion/setup costs and after mapping relations back to the same canonical group representation.

## IDEA-BRAUER-1: local-global signature channel

Explore the Frey / Huang-Raskind line as a separate high-risk theory track. Given a public ECDLP instance, search for arithmetic lifts and pairings/local invariants that produce efficiently computable signatures correlated with the scalar.

This is only interesting if the auxiliary arithmetic objects can themselves be constructed without solving an equivalent hard problem.

### Required accounting

For each proposed channel write down explicitly:

1. public inputs used to construct the lift;
2. construction complexity;
3. invariant/pairing evaluation complexity;
4. exactly what scalar information is revealed;
5. number of independent observations required;
6. reconstruction complexity;
7. known obstruction showing where ECDLP hardness may have merely moved.

Toy experiments should include positive and null controls. Do not label a computable local invariant as progress unless it distinguishes scalar classes or reduces a preregistered search space.

### EXP-BRAUER-1: toy scalar-class distinguisher

On very small curves where discrete logs are known by enumeration, construct candidate local invariants/signatures from public `(G,Q)` and evaluate whether they distinguish any preregistered scalar partition better than chance.

Required controls:

- randomized scalar labels;
- coordinate/isomorphic curve changes;
- matched random curves;
- planted observable with known information content.

Any positive observation must survive held-out curves and be rewritten as an explicit deterministic relation before promotion.

### EXP-BRAUER-2: hardness relocation audit

For every candidate with nonzero signal, independently cost the construction of the arithmetic lift and auxiliary objects. Mark the candidate `hardness_relocated` if any required construction invokes an operation empirically/theoretically equivalent to solving the original DLP.

## IDEA-REP-1: search for non-index-calculus scalar observables

Broaden the harness beyond factor bases. Define a `scalar_observable` candidate as a public computable map `I(P,Q)` whose output has measurable dependence on `d` in `Q=[d]P`.

Search on toy curves across coordinate, divisor, local, cohomological, representation-theoretic, and endomorphism-derived features. ML may rank candidate features or find empirical anomalies, but promotion requires an exact reproducible mathematical relation and an algorithmic cost model.

### EXP-REP-1: observable discovery sweep

Generate feature families over toy curves and score them against preregistered scalar targets such as parity, residue classes, interval buckets, or low-dimensional characters. Use held-out field sizes and curves.

Measure mutual information only as a discovery statistic. A candidate cannot advance unless a deterministic verifier reproduces the dependency without fitting.

### EXP-REP-2: invariance stress test

For every apparent observable, apply random isomorphisms, coordinate changes, generator changes, and matched-group random curves. Classify whether the observable is:

- coordinate artifact;
- generator artifact;
- curve-family artifact;
- genuine group/arithmetic invariant candidate.

## Harness changes suggested

Add an ECDLP `representation_search` campaign with a common record format:

```yaml
candidate:
  representation: ...
  factor_base_predicate: ...
  symmetry_group: ...
  orbit_parameterization: ...
metrics:
  factor_base_size: ...
  orbit_count: ...
  orbit_size_histogram: ...
  decomposition_success_rate: ...
  relation_independence_rate: ...
  solver_seconds_per_relation: ...
  setup_seconds: ...
  canonicalization_seconds: ...
  incremental_rank_per_relation: ...
  projected_total_log2_ops: ...
controls:
  null_passed: ...
  positive_passed: ...
  isomorphism_stress_passed: ...
claim_boundary:
  beats_current_factor_base: false
  beats_rho: false
```

Require ranking to use total projected work, not isolated solver timing, nominal relation count, variable count, or matrix shrinkage.

## Suggested campaign sequence

1. **Orbit instrumentation first** — add canonical orbit IDs, Frobenius exponent provenance, dependency detection, and incremental-rank metrics to the existing Koblitz relation path.
2. **Run EXP-FROB-ORBIT-1/2/4** — determine whether orbit-aware representation helps the decomposition bottleneck or only linear algebra.
3. **Run FROB-FB-1/2** — search nonlinear Frobenius-stable factor bases with matched-cardinality controls.
4. **Feed winners into FROB-SYM-1** — test scaling, not just toy-point wins.
5. **Run TORUS representation generation** only through the same benchmark harness.
6. **Keep BRAUER and REP lanes isolated** from attack claims until their information-flow and construction-cost gates hold.

## Priority

1. **FROB-0 + FROB-1 + FROB-2**: best near-term experimental track because the repo already has Koblitz/Frobenius and decomposition machinery.
2. **TORUS-1**: representation generator feeding the same benchmark harness.
3. **BRAUER-1**: theory-first; require explicit construction and information-flow accounting before expensive experiments.
4. **REP-1**: broad anomaly search; highest novelty potential and highest false-positive risk.

## Kill criteria

A candidate should be archived rather than endlessly tuned when one of these persists across the preregistered scaling ladder:

- decomposition probability falls faster than the matrix/orbit saving improves;
- degree of regularity or SAT complexity dominates total cost;
- relations collapse to Frobenius/scalar multiples and add no rank;
- representative/index parameterization increases solver branching enough to erase the orbit saving;
- canonicalization or representation conversion costs become material relative to relation generation;
- constructing the auxiliary representation requires work equivalent to the original DLP;
- an apparent scalar observable disappears under held-out curves or coordinate changes;
- projected asymptotics remain above the rho baseline with no identified mechanism capable of changing the exponent.

Negative results should remain first-class outputs: the useful product is a map of which structures fail and *why*.