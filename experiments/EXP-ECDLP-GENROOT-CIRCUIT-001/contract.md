# Experiment contract: bounded-source generalized-root circuit

## Status and execution boundary

`CONJECTURE`, `HEURISTIC`, `MODEL-BOUND`, `REVIEW_REQUIRED`.

This is a paper and symbolic-census contract. It authorizes no implementation,
development run, or canonical run. Source work requires separate theory,
literature, benchmark, and red-team `GO` records, a clean frozen commit, and an
explicit development authorization. Canonical execution remains a separate
user authorization boundary.

## Candidate

Exploit bounded or composition-labeled public source variables while retaining
the exact sparse graph of five EC additions, so a dedicated generalized-root
algorithm can recover one signed five-leaf witness without constructing D2,
D3, a summation-polynomial eliminant, or a D2-indexed target vector.

The primary lane is the arbitrary-prime `x_interval` factor base. `square_map`
and `rational_union` are representation variants. A p-1-smooth or auxiliary
isogeny chain is a separately costed future family and cannot rescue a failure
of the arbitrary-prime lane by relabeling its claim.

## Attack class

This contract targets a one-instance index-calculus relation engine, not only a
fixed-curve online compiler. Write `B=|F|` and balance `B` near `n^(1/5)`.
Let `epsilon_rel=|D5|/n` for uniform targets, let
`R_req=r_star-r_0` be required rank increments, and let `eta_r` be conditional
rank yield at rank `r`. The stationary expected attempt count is

```text
E[A]=R_req/(epsilon_rel*eta).
```

The execution budget is instead the preregistered rank-dependent geometric-sum
quantile `A_(1-alpha)`, or its conservative `p_min` binomial bound, defined in
the shared accounting note. If `R_req=Theta(B^rho)`, support decays as
`B^-delta_epsilon`, and rank yield as `B^-delta_eta`, then
`A=Theta(B^(rho+delta_epsilon+delta_eta))`. A credible sub-rho path requires:

```text
factor-base plus compiler preprocessing = o(B^2.5)
actual A_(1-alpha)-attempt relation work = o(B^2.5)
per-attempt exponent tau must satisfy
  tau+rho+delta_epsilon+delta_eta < 2.5
```

The constant-yield `rho=1` specialization gives `tau<1.5`. The matrix and
descent stages must later remain below `B^2.5`. A development `0.8x` result is
only an engineering continuation signal.

## Advice boundaries

- Finite continuation: at most `0.8x` exact-comparator bytes is only a toy
  engineering screen.
- Compressed fixed-curve compiler: total advice and peak preprocessing workspace
  have upper B-slope below 3.
- One-instance candidate: advice, advice writes, construction, peak preprocessing
  workspace, actual relation batch, linear algebra, and descent each have upper
  B-slope below 2.5.

All advice includes registries, shift schedules, reduced bases, completion data,
metadata, pointers, page cache, and accelerator-resident state.

## Mathematical objects

Let `E/F_p` be an ordinary prime-order short-Weierstrass curve and let each
factor leaf be identified by:

```text
(branch b, source root t, orientation sign, public factor id).
```

Register an exact decoration relation `Reg(b,t,x,y)` returning every eligible
public identifier. Equality of coordinate solutions is not equality of factor
identifiers when fibers or identifiers collide.

For branch `b`, disclose:

- accepted squarefree root polynomial `M_b(T)`;
- source bound `T_b=1+max(t)` for the registered integer representatives;
- rational map `phi_b(T)=N_b(T)/D_b(T)`;
- exact root-to-factor fibers and non-pole policy;
- construction operations and canonical bytes.

For each multiset of five branches, construct variables for five sources,
affine leaf coordinates, and the minimum projective intermediate state needed by
an exact addition graph. The target enters only through final public coordinate
ports.

## Exact circuit obligations

The equations must enforce all of the following without divisions:

1. `M_b(t_i)=0` and the registered integer bound on every source root;
2. `D_b(t_i) x_i-N_b(t_i)=0` with an explicit saturation or inverse witness for
   every denominator;
3. `y_i^2=x_i^3+a x_i+b`;
4. an exact graph of `P_1+...+P_5=Q` using a complete system of addition laws or
   a finite branch cover with selector and saturation semantics;
5. repeated leaves, inverse pairs, doubling, identity intermediates, and target
   identity;
6. source-fiber and sign provenance sufficient to return five public ids.

The frozen primary semantics enumerate all typed addition-branch patterns. A
one-hot polynomial encoding additionally requires Boolean selectors,
exactly-one selection, and gated or saturated inactive equations. Each source
uses one registered integer lift `0 <= t_i < T_i <= p`; modular aliases are
separate charged candidates.

Before solver code, prove both directions for accepted decorated solutions:

- every accepted circuit solution maps to five registered signed factors whose
  affine sum is `Q`;
- every ordered registered five-leaf witness for `Q` induces at least one
  accepted circuit solution.

The theorem is equality of identifier projections, not a bijection of raw
coordinate solutions. Registry filtering, rejected algebraic roots, duplicate
identifier expansion, and their completeness evidence are part of solver cost.

Permutation symmetry may remove duplicate solutions only after this lemma. It
may not delete repeated leaves or orientation routes.

## Candidate solver

The positive path has two explicitly separated stages.

### Bounded-root stage

Freeze a family of lattice shifts or another dedicated bounded-root operator
using only the source bounds and target-independent circuit layout. Report:

- scaled monomials and integer representatives;
- lattice rows, columns, determinant, norms, and reduction operations;
- integer coefficient bit lengths, growth, and bit-operation totals;
- the exact or heuristic inequality predicting recovery;
- dependence on `B`, `p`, map degrees, and every full-field variable;
- every candidate root, miss, retry, and ambiguity.

The generic box is near `product_i T_i approximately p`. No Coppersmith-style
advantage may be asserted without a strictly stronger registered inequality.
Jochemsz-May-style multivariate predictions are `HEURISTIC` unless a theorem
matching this circuit is supplied.

#### Frozen first-power negative

`first-power-box-lattice-negative-v1.md` instantiates the first-power tensor-box
shifts. Their `Theta(B^5)` explicitly materialized rows and columns
unconditionally violate the preprocessing gate. Dense expanded membership
polynomials additionally give `Theta(B^6)` nonzeros. The determinant-volume
heuristic supplies no positive recovery slack, but does not prove that
exceptional short combinations are absent. This shift family is
`REJECTED_SCOPED`; tuning or implementation is forbidden. A higher-power,
support-adapted, composition-tower, implicit, or non-lattice operator is a new
family and needs a fresh symbolic gate.

### Exact completion stage

Candidate roots enter a sparse Macaulay, rational-univariate, triangular, or
other independently checkable completion method. Report rows, columns,
nonzeros, rank, degree, Krylov iterations, fill, bytes, and every field
operation. A candidate list is not a complete solve.

Each branch pattern must end with either:

- a certificate proving the complete solution set for that pattern; or
- an exact D2+D3 fallback charged in full.

Any supported target that needs fallback cannot satisfy a positive signal.
The completion bound must include all candidate roots, all registry rejections,
and duplicate decorations, not only accepted five-id outputs.

## Forbidden displacement

The positive path may not construct or retain:

- D2, D3, D4, or D5 support;
- `G_Q`, `H_Q`, `f6`, or another eliminated target polynomial with a
  `Theta(B^2)` live coefficient vector;
- one target bit, coefficient, row, pointer, or cache entry per D2 orbit;
- target-specific preprocessing or target scalar data;
- a hidden compatibility mask, supported-target table, or uncharged fallback;
- audit scalar indices in candidate advice or solver decisions.

Sage, SymPy, or a generic Groebner solver may serve as a tiny independent oracle
and cold-solver baseline. It is not the candidate mechanism.

## Controls

### Positive controls

- A planted five-root target for every feasible typed branch route, or a proved
  infeasibility sentinel. With finite leaves and left association, gate 1 is
  `ORD`, `DBL`, or `INV`; a later `LID` occurs exactly after an `INV`; `RID` is
  unreachable; every other finite-input gate is `ORD`, `DBL`, or `INV`.
- A tiny univariate bounded-root instance whose registered lattice theorem is
  known to apply.
- Exhaustive 5- to 7-bit circuit enumeration including every exceptional
  addition branch.

### Negative and mutation controls

- Alter one source root, one multiplicity, one map denominator, one target port,
  and one projective branch equation; independent replay must reject each.
- A generic sparse polynomial circuit matched for variables, equation degrees,
  nonzeros, target ports, and source bounds.
- A source-label permutation against fixed accepted x-values, audit only.

### Same-map controls

For each candidate map, sample accepted non-pole source roots uniformly without
replacement, preserve map parameters, branch cardinality, x-collision policy,
factor-base size, every integer source-bound shape, target schedule, circuit,
shifts, and completion method. If the bounded domain admits no nontrivial
randomization, this null is ineligible for the continuation gate and the
degree-, nonzero-, and bound-matched generic circuit is the structural control.
A map-confounded or bound-confounded comparison cannot satisfy a coordinate gate.

### Target schedule

- Uniform targets come from preregistered scalar seeds independent of source
  data, candidate advice, and audit witnesses.
- Planted targets use blinded leaf indices and are reported separately.
- Hit and no-hit cardinalities are exact and aggregated conjunctively.
- Fallback is forbidden on every attempted target, not only postselected
  supported targets.

## Baselines and kill screens

- complete exact D2+D3 lookup with full operation and traffic vector;
- cold direct `f6` or polynomial-system solve as an oracle, not a target;
- explicit outer translator as a known negative implementation control;
- equal-advice fixed-base BSGS;
- constructive generic preprocessing, with offline work and advice separated;
- normalized rho with the same curve formulas and valid automorphisms.

Only D2+D3 is output-equivalent. BSGS, generic preprocessing, and rho solve a
stronger problem and are end-to-end kill screens.

For equal-byte BSGS, treat candidate advice as a byte cap and minimize total
work over every table size `1<=m<=M_B`; do not force the comparator to consume
the cap. For constructive generic preprocessing, use its separate complete
record size, restrict `m` to the cited construction's valid range, and minimize
total work over that range. At each fixed valid `m`, charge

```text
T_G=soft-Theta(sqrt(epsilon_DLP*n/m))
P_G=soft-Theta(sqrt(epsilon_DLP*n*m)).
```

Field operations and traffic remain separate from generic-group oracle queries.
Full formulas and theorem boundaries are frozen in
`notes/ecdlp_relation_preprocessing_accounting_20260718.md`.

## Metrics

Report by curve, family, branch pattern, target kind, and control:

- exact `N_j` supports, formal multiset ceilings, uniform `epsilon_rel`,
  `R_req`, rank-dependent `eta_r`, and confidence level `alpha`;
- source bounds, box volume, variables, equations, degrees, and circuit nodes;
- lattice dimensions, determinant proxy, integer coefficient sizes, reduction
  swaps, field arithmetic, and bit operations;
- Macaulay dimensions, nonzeros, rank, degree, Krylov work, and fill;
- advice bytes, target live bytes, RSS, reads, writes, and bandwidth;
- field additions, multiplications, inversions, zero tests, and group checks;
- candidate-list bound, enumerated roots, registry rejections, duplicate
  decorations, exact solutions, certificate bytes, retries, and fallback;
- five-id witness bytes and independent affine verification;
- one-attempt, actual `A_(1-alpha)`, `K=B`, and `K=16B` costs, without
  projecting a one-target average as batch sharing.

## Zero-run feasibility gate

Implementation remains unauthorized unless all pass on paper or by a symbolic
census that does not attempt target solving:

1. the decorated identifier-projection lemma is complete for every typed branch
   pattern and selector policy;
2. every resident and persistent object has a dimension in `B` and `log p`;
3. every source has a unique registered integer lift and modular aliases are
   excluded or charged;
4. the bounded-root stage states a concrete recovery inequality and the source
   box gives nonzero asymptotic slack beyond generic enumeration;
5. lattice coefficient growth and bit complexity fit the claimed bound;
6. full-field variables, target specialization, and registry filtering do not
   require a D2-sized elimination object;
7. the completion theorem bounds the complete candidate list, rejected roots,
   and duplicate decorations, with a plausible operation bound below `B^2` for
   continuation and per-attempt exponent
   `tau<2.5-rho-delta_epsilon-delta_eta` for a breakthrough;
8. preprocessing and the actual `A_(1-alpha)` relation batch, using uniform
   support and rank-dependent yield, each have a symbolic path below `B^2.5`;
9. no forbidden displaced state appears.

If item 4 fails, record a scoped negative for the frozen lattice shift family
and search a different dedicated generalized-root algorithm. Do not tune lattice
parameters indefinitely.

## Development functional gate

1. Candidate and independent oracle agree on exact hit/no-hit and the complete
   decorated solution set on exhaustive tiny controls and registered targets;
   the task-matched output is the first deterministic five-id witness when hit.
2. Every five-leaf witness independently sums to the target.
3. All mutation controls fail and all positive controls pass.
4. Target-independent advice is byte-identical across target schedules.
5. Requested uniform, planted, hit, and no-hit target cardinalities are realized
   exactly, with zero fallback on every attempted target.

Failure invalidates the implementation, not the mathematical frontier.

## Development continuation gate

One family may continue only if both seeds at every size pass all of:

1. the functional gate;
2. zero fallback on every attempted target and fail-closed positive and negative
   certificates;
3. candidate online operations, reads, writes, and bytes each at most `0.8` of
   exact D2+D3 for inversion weights `10,50,100`;
4. target live state below `0.8|D2_x|` field words with no packed linear mask;
5. total advice and peak workspace at most `0.8` of compressed D3;
6. at least one primary operation or size measure at most `0.8` of the same-map
   randomized source control without support loss;
7. preprocessing plus actual `K=B`, `K=16B`, and `K=A_(1-alpha)` work, retries,
   certificate generation and checking, output, support, and rank yield beat the
   output-equivalent comparator conjunctively;
8. measured crossover `K_star` against the output-equivalent comparator is at
   most `A_(1-alpha)`;
9. slopes do not worsen toward the exact comparator.

This authorizes only a larger noncanonical census.

## Eventual ECDLP gate

Use at least five geometrically spaced group orders, three fresh clean curves per
order, held-out curves, exact support/rank yields, and upper 95 percent slope
bounds. A classical exponent signal requires:

```text
factor-base and compiler preprocessing B-slope < 2.5
actual A_(1-alpha) relation batch B-slope           < 2.5
independent attempt tau+rho+delta_epsilon+delta_eta < 2.5
sparse linear algebra, descent, and total n-slope   < 0.5
absolute normalized total below rho at largest sizes
```

No component-only or many-target amortized result satisfies this gate.

## Proof and disproof tracks

### Proof track

- Prove exact circuit/witness equivalence under every addition branch.
- Derive a lattice or dedicated-root theorem using the actual source bounds and
  sparse graph, not a generic solver analogy.
- Prove completeness and complexity of the sparse completion certificate.
- Extend a passing relation engine through rank, sparse linear algebra, and
  individual descent.

### Disproof track

- Show the lattice determinant inequality has no slack at `B^5 approximately p`.
- Show full-field variables or completion recreate a `B^2` eliminant.
- Construct source-map instances that pass the lattice filter but lose solutions
  or require full fallback.
- Compare against same-map random roots and stronger generic preprocessing.

## Next concrete action

Write and independently review the exact addition-graph equivalence lemma plus
the object-dimension and lattice-feasibility ledger. Do not implement a solver.
