# ECDLP research slate: symmetry-aware factor bases and local-global representations

Status: speculative research agenda. Nothing here claims an attack, speedup, or sub-square-root ECDLP algorithm.

## Motivation

Known ECDLP improvements repeatedly exploit structure that is invisible in the generic-group model: Frobenius on binary extension curves, descent, special embeddings, or arithmetic maps. The experiments below ask a narrower question: can representation choice reduce the *total* cost of relation generation or expose independently computable information about the unknown scalar?

Every experiment must compare end-to-end cost against the appropriate Pollard-rho baseline and account for setup, decomposition, relation collection, linear algebra, and individual-log recovery.

## IDEA-FROB-1: nonlinear Frobenius-stable factor bases

For Koblitz/subfield curves, do not restrict the search to Frobenius-invariant linear subspaces. Search families of nonlinear sets F with:

1. pi(F) = F or a small number of Frobenius-related components;
2. compact membership predicates;
3. controllable cardinality and orbit distribution;
4. decomposition equations whose degree/regularity is no worse than conventional bases.

Candidate families:

- normal-basis Hamming-weight shells and unions of shells;
- trace/norm level sets;
- zero sets of sparse linearized-plus-low-degree polynomials;
- intersections/unions of low-codimension Frobenius-stable varieties;
- orbit unions selected by cheap algebraic invariants.

### First experiment

On toy Koblitz curves over F_(2^m), enumerate candidate predicates at small m. For each candidate measure:

- |F| and number/orbit-size distribution under Frobenius;
- empirical decomposition probability for k=2,3,4;
- polynomial-system size and degree-of-regularity proxy;
- SAT/Groebner solve time per successful relation;
- projected relation-collection + sparse-linear-algebra cost.

The objective is not smallest |F|. Rank by estimated *cost per independent usable relation*.

## IDEA-FROB-2: symmetry-adapted decomposition coordinates

Treat Frobenius symmetry as part of the solver representation rather than only collapsing relation-matrix columns. Construct coordinates on decomposition tuples modulo Frobenius and permutation action, then compare them with the existing chained-S3/SAT encoding.

Questions:

- Can orbit invariants eliminate variables before SAT/Groebner solving?
- Can normal-basis cyclic structure turn repeated constraints into structured/circulant blocks?
- Does quotienting introduce equations of higher degree that erase the benefit?

### Falsification gate

Reject a representation if its measured relation throughput, after orbit multiplicity and independence corrections, is not better than the current baseline over a scaling ladder. A reduction in variable count alone is not evidence.

## IDEA-TORUS-1: representation search via algebraic groups/tori

Investigate Couveignes-Lercier-style field representations and algebraic-group constructions as a *factor-base design mechanism*. The goal is not to transfer arbitrary ECDLP to an easy torus DLP. Search for representations in which Frobenius/Galois action is simple and factor-base membership/decomposition becomes cheaper.

Automated search variables can include representation parameters, basis choice, trace/norm constraints, orbit structure, and decomposition arity. Record representation-construction cost explicitly.

For prime m such as 131, where simple invariant linear-subspace constructions may offer no useful intermediate dimension, prioritize nonlinear or multi-component constructions rather than repeatedly searching the same linear-subspace family.

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

## IDEA-REP-1: search for non-index-calculus scalar observables

Broaden the harness beyond factor bases. Define a `scalar_observable` candidate as a public computable map I(P,Q) whose output has measurable dependence on d in Q=[d]P.

Search on toy curves across coordinate, divisor, local, cohomological, representation-theoretic, and endomorphism-derived features. ML may rank candidate features or find empirical anomalies, but promotion requires an exact reproducible mathematical relation and an algorithmic cost model.

### Controls

- random relabeling of scalar labels;
- random curves with matched group size;
- coordinate/isomorphism changes;
- held-out field sizes;
- planted observables whose information content is known.

Measure mutual information only as a discovery statistic. Any promoted candidate must be converted into an explicit theorem/conjecture plus deterministic verifier.

## Harness changes suggested

Add an ECDLP `representation_search` campaign with a common record format:

```yaml
candidate:
  representation: ...
  factor_base_predicate: ...
  symmetry_group: ...
metrics:
  factor_base_size: ...
  orbit_count: ...
  decomposition_success_rate: ...
  relation_independence_rate: ...
  solver_seconds_per_relation: ...
  setup_seconds: ...
  projected_total_log2_ops: ...
controls:
  null_passed: ...
  positive_passed: ...
claim_boundary:
  beats_current_factor_base: false
  beats_rho: false
```

Require ranking to use total projected work, not isolated solver timing or matrix shrinkage.

## Priority

1. **FROB-1 + FROB-2 together**: best near-term experimental track because the repo already has Koblitz/Frobenius and decomposition machinery.
2. **TORUS-1**: representation generator feeding the same benchmark harness.
3. **BRAUER-1**: theory-first; require explicit construction and information-flow accounting before expensive experiments.
4. **REP-1**: broad anomaly search; highest novelty potential and highest false-positive risk.

## Kill criteria

A candidate should be archived rather than endlessly tuned when one of these persists across the preregistered scaling ladder:

- decomposition probability falls faster than the matrix/orbit saving improves;
- degree of regularity or SAT complexity dominates total cost;
- relations collapse to Frobenius/scalar multiples and add no rank;
- constructing the auxiliary representation requires work equivalent to the original DLP;
- an apparent scalar observable disappears under held-out curves or coordinate changes;
- projected asymptotics remain above the rho baseline with no identified mechanism capable of changing the exponent.

Negative results should remain first-class outputs: the useful product is a map of which structures fail and *why*.