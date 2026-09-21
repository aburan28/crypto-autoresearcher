# Automated index-calculus pipeline search

Status: proposed research plan; no attack or speedup claim.

## Objective

Search over complete elliptic-curve index-calculus relation-generation pipelines rather than optimizing one Gröbner configuration in isolation. The evaluator should answer:

> Which combination of factor base, point/field representation, decomposition formulation, symmetry handling, and solver minimizes the cost of producing enough verified independent relations to complete a discrete-log solve?

The main target is relation generation. A candidate receives a curve/subgroup, a factor-base specification, a target relation point, and a resource budget, and must return either a verified point decomposition or a solver outcome. The candidate does not get access to hidden evaluator discrete logs.

## Mathematical contract

For subgroup generator `G`, target `Q = [x]G`, and random relation point

`R = [a]G + [b]Q`,

a candidate attempts to find

`R = sum_j [c_j] B_j`

for factor-base points `B_j`. Once independently verified, this contributes

`sum_j c_j log_G(B_j) - b x = a mod r`.

The nonlinear decomposition step and the later linear algebra must be measured separately. Polynomial roots receive no credit unless they lift to valid subgroup points and satisfy the original group equation.

## Search dimensions

1. Factor base
   - algebraically described subsets
   - orbit-closed bases where applicable
   - matched random controls
   - stabilizer/orbit-stratified variants
2. Representation
   - polynomial basis
   - normal/self-dual normal basis where available
   - tower basis where available
   - admissible curve-coordinate/model choices
3. Decomposition formulation
   - direct summation-polynomial formulation
   - chains of lower-arity summation constraints with auxiliaries
   - direct point-addition polynomial constraints
   - representative-plus-orbit-index formulations where mathematically valid
4. Symmetry handling
   - permutation symmetry breaking
   - established Frobenius quotient/canonicalization baselines
   - orbit-aware variable/block orderings
5. Solver
   - Gröbner basis
   - SAT/XOR-aware SAT
   - bounded enumeration / meet-in-the-middle controls on tiny instances
   - hybrid algebraic/SAT preprocessing
6. Search policy
   - elimination and variable order
   - selective guessing
   - learned timeout/cost prediction
   - budgeted bandit/Bayesian search over already-correct candidate families

## Evaluator invariants

The proposer/executor may change candidate code, but may not change:

- hidden test instances
- independent group-law verifier
- accounting rules
- promotion thresholds after results are visible
- evaluator-only discrete-log tables

Every run records code revision, environment, curve/subgroup, factor-base definition and cardinality, target seed, solver configuration, wall time, peak memory, solver-specific diagnostics, raw output, independently verified decomposition, and relation-matrix effect.

A timeout means only `not solved within budget`, never `unsatisfiable`.

## Metrics

Primary screening metric within matched systems:

- seconds per newly independent verified relation

Also record:

- decomposition success probability
- duplicate relation fraction
- rank deficit after fixed wall time
- solver seconds and total seconds including encoding/conversion/verification
- maximum Gröbner degree / actual solving degree where available
- Macaulay rows, columns, nonzeros, and peak degree
- SAT decisions, conflicts, propagations, XOR statistics where available
- peak memory

Promotion metric across configurations that change factor-base size or unknown count:

`T_total = T_setup + T_relation_collection + T_linear_algebra + T_target_recovery`.

No cross-configuration asymptotic claim is made from raw rank-per-second alone.

## Correctness and benchmark ladder

### Stage 0: exhaustive tiny-instance verification

Exhaustively enumerate all decompositions for tiny groups. Compare candidate solution sets to ground truth to detect both false positives and false negatives. Planted decompositions are allowed only for correctness testing, not as the sole performance distribution.

### Stage 1: frozen random discovery corpus

Use matched random targets, seeds, factor-base cardinalities, and resource limits. Keep cohorts separate:

- generic prime-field curves
- structured prime-field curves
- generic nonsupersingular binary curves
- binary Koblitz curves

Begin with toy subgroup sizes around 12-24 bits and arities 2-4, then calibrate upward based on measured runtime.

### Stage 2: held-out validation

Promising candidates are rerun on unseen curves/fields and fresh seeds at larger sizes. A held-out corpus is retired after repeated adaptive exposure and replaced with fresh evaluator-only instances.

### Stage 3: complete solve

For survivors, measure the full relation matrix, linear algebra, and target recovery, and compare against the strongest available index-calculus baseline plus an appropriate Pollard-rho implementation.

## First priority: representation x Frobenius x solver

For binary Koblitz instances, test whether exposing Frobenius structure inside the decomposition formulation yields benefit beyond established Frobenius-aware factor-base and symmetry-reduction baselines.

Matched arms:

A. established factor base + conventional encoding + established symmetry baseline
B. same mathematical problem in a normal basis
C. B + orbit representative and explicit orbit-index encoding
D. C + orbit/block-aware Gröbner or SAT ordering

Run applicable arms with both Gröbner and XOR-aware SAT backends.

Correctness invariant: applying Frobenius to summands also transforms the target. No arm may independently rotate summands while leaving the relation target fixed unless the retained variables/constraints prove equivalence. Stage-0 exhaustive comparison is mandatory before performance runs.

## Second priority: factor-base/formulation co-design

A factor base must not be judged independently from its equation formulation. Search paired variants while holding effective factor-base size and targets fixed. Promote only pairs that improve independent-relation cost and preserve or improve final matrix quality.

## Automated search policy

Use cheap deterministic search for solver parameters and representation choices. Use the research model for materially different formulations and for interpreting verified outliers. Once enough data exists, train a cost/timeout predictor, but compare it against random search and simple hand-written heuristics on fresh instances.

Keep explicit exploration budget so the loop cannot converge permanently on the current incumbent. Suggested allocation after an incumbent exists:

- 50% incumbent refinements
- 25% orthogonal candidate families
- 15% replications / held-out validation
- 10% high-risk new formulations

## Promotion rules

A candidate is promoted only if:

- there are zero unexplained correctness failures
- all overhead is included
- the improvement is paired on identical instances
- the gain persists on the largest measured sizes and fresh seeds
- held-out instances show the same direction
- complete-solve accounting does not reverse the gain when applicable

A candidate is killed or demoted when its gain disappears after deduplication/rank accounting, only appears on tiny sizes, depends on leaked evaluator data, or requires an uncharged precomputation.

## Claim discipline

Maintain three separate claim classes:

1. `implementation improvement`: faster on measured instances
2. `scaling signal`: fitted growth is better over the measured ladder
3. `complexity claim`: requires a mathematical argument that all relevant costs and success probabilities scale accordingly

Only the first two can be emitted automatically from experiments. The third requires theory review.
