# Prime-field ECDLP subexponential-existence and barrier program

**Date anchor:** 2026-10-31
**Status:** planning specification only; no scientific status changes, experiment
approvals, runs, lower-bound claims, or ECDLP speedups are recorded here.

## 1. Request and delivered scope

The request is to turn five theorem targets for the existence or nonexistence of
a subexponential classical algorithm for prime-field ECDLP into detailed goals
that experiment designers, implementers, runners, validators, and reviewers can
work toward.

| Requirement | This document supplies | Evidence or remaining gate |
| --- | --- | --- |
| Preserve the mathematical question | One frozen target statement and explicit quantifiers | Section 3 |
| Expand the five theorem targets | Five goal specifications with proof and empirical work | Sections 5-9 |
| Make the work dispatchable | Proposed bounded work packages with inputs, artifacts, controls, budgets, and completion gates | Section 11 |
| Reuse rather than duplicate the portfolio | A mapping to existing `GOAL-*`, `RQ-*`, `KN-OPEN-*`, and frontier records | Section 4 |
| Use asymptotics and heuristics honestly | A common cost model and architecture-falsification rules | Sections 2 and 10 |
| Enable experimenters and runners | A lifecycle and artifact contract, without launching a trial from this planning record | Sections 11-13 |

This is deliberately not a new `GOAL-*` ledger record. The repository already
contains the umbrella campaigns and several child goals needed for this work.
A Coordinator should materialize a selected work package into a versioned
`RQ-*`/`H-*`/`EXP-*`/`TASK-*` chain only after deduplication and protocol
preapproval. Until then, the identifiers `PFSE-G*` and `PFSE-WP*` below are
document-local planning labels, not ledger IDs and not runnable experiment IDs.

## 2. Claim boundary and notation

Let `r` be the prime order of the target cyclic subgroup and

```text
n = ceil(log2 r).
```

A uniform classical randomized family algorithm is **subexponential in the
ECDLP input scale** when

```text
T(n) = 2^o(n), equivalently log2(T(n)) / n -> 0.
```

The common `L` notation is

```text
L_r[alpha,c]
  = exp((c + o(1)) (log r)^alpha (log log r)^(1-alpha)),
0 < alpha < 1.
```

The primary question is not meaningful for a single fixed curve. It is a
family question, and the following costs remain separate in every theorem,
model, experiment, and report:

- setup and instance generation;
- one-time preprocessing;
- per-target online work;
- relation collection and verification;
- linear algebra and target descent;
- recovery and final scalar-multiplication verification;
- peak memory, stored advice, processors, and communication;
- success probability and repetitions;
- single-target versus amortized multi-target work.

An observed slope, a failed search, or agreement with a random-map heuristic
does not disprove the existence of an algorithm. Experiments can falsify a
named heuristic, implementation, cost model, or algorithmic architecture.
Only a proof in an explicit computational model can establish nonexistence in
that model. A universal lower bound for unrestricted classical algorithms is
not implied by completing any finite set of experiments in this program.

## 3. Frozen target statement

The program studies the following target, unless a child protocol explicitly
narrows it.

> **PFSE Target.** Determine whether there is a uniform classical randomized
> algorithm with success probability at least `2/3` and total expected time
> and memory `2^o(n)` for ECDLP on a declared density-one or cryptographically
> sampled family of ordinary elliptic curves `E/F_p`, where `E(F_p)` contains
> a prime-order subgroup of order `r`, `log2 p = Theta(n)`, and all setup,
> preprocessing, transfer, descent, recovery, and verification costs are
> charged.

The target excludes quantum algorithms. It does not quantify over every curve
over a prime field: anomalous curves, small-embedding-degree curves, smooth
groups, and other special families are positive controls showing that a blanket
universal hardness statement is false.

The family definition must eventually choose exactly one of these quantifiers:

1. worst case over an explicitly defined family;
2. average case under a reproducible curve sampler;
3. density one under a stated measure and limiting process.

Results for one quantifier do not silently transfer to another. Random
self-reducibility on a fixed cyclic group does not by itself provide a
worst-curve-to-average-curve reduction.

## 4. Existing portfolio mapping and non-duplication

The five goals below should extend existing records instead of opening five
empty parallel campaigns.

| Program goal | Existing owner or source | What remains distinct here |
| --- | --- | --- |
| PFSE-G1: family and exceptions | `GOAL-ECDLP-001`, `RQ-ECDLP-002`, curve-identity rules | Freeze the exact asymptotic quantifiers and a machine-checkable inclusion/exclusion certificate |
| PFSE-G2: generic/model lower bounds | `KN-LIT-011`, `KR-RHO-13bf67`, `KN-OPEN-005`, `LEAD-RHO-generic-sqrt-lower-bound` | Build a model ladder and proof obligations beyond simply restating Shoup |
| PFSE-G3: structural transfers | `SG-ECDLP-002`, `EV-IT-511f3d`, `KR-RHO-53c89f`, `KR-RHO-817bf8`, `KN-TECH-6a2ef9` | Re-express every destination cost in the source input scale and retain uncovered interfaces |
| PFSE-G4: relation-generation barrier | `GOAL-PATH-001`, `GOAL-SDEG-001`, `GOAL-RELN-001`, `GOAL-ICEX-001`, `KN-OPEN-001`, `KN-OPEN-020` | Join factor-base size, relation supply, solver cost, rank, descent, and memory in one optimized asymptotic envelope |
| PFSE-G5: representation-aware lower bound | `KN-OPEN-005`, `KN-OPEN-020`, `KN-TECH-080`, prior `GOAL-ECDLP-001` model screens | Specify a hierarchy broad enough to expose coordinates while preserving a checkable lower-bound proof |

`GOAL-ECDLP-bbc21f` is not an exponent lane: it studies constant-factor
batch/precomputation tradeoffs and explicitly says so. Automorphism and GLV
measurements likewise remain constant-factor evidence unless a separate proof
changes the exponent.

## 5. PFSE-G1 — Freeze the family, quantifiers, and exception boundary

### Decision target

Produce the exact family statement against which the words “subexponential
prime-field ECDLP algorithm” and “no such algorithm” are evaluated. Prevent a
special-family result, a quantum result, an amortized result, or a fixed-curve
measurement from answering a different question by accident.

### Theorem and specification obligations

1. Define the curve sampler or family `F_n` completely: prime generation,
   coefficient distribution, rejection rules, subgroup selection, cofactor
   bound, and what is public input.
2. Require ordinary nonsingular curves and a certified prime subgroup order
   `r`; record `p`, `#E(F_p)`, `r`, cofactor, trace, and subgroup generator.
3. State the asymptotic relation between `p` and `r`. A recommended baseline is
   `log p = Theta(log r)` with cofactor polynomial in `n`.
4. Separate, rather than merely discard, known exceptional strata:
   anomalous/trace-one, supersingular, small embedding degree, smooth subgroup
   order, special transfer, and explicitly structured endomorphism families.
5. Define the embedding-degree threshold in terms of source-scale cost. If a
   target finite-field DLP has cost `L_{p^k}[alpha,c]`, classify it using
   `n = log2 r`, not only `log(p^k)`.
6. State whether preprocessing may depend on the curve, the subgroup, the
   generator, or the target and whether advice is uniform.
7. State the success probability and whether failures are detectable.
8. State the single-target and multi-target questions separately.

### Experimental work

Build a deterministic family-classification fixture over toy and medium
instances. It is an instrument test, not evidence of asymptotic hardness.

Positive controls must include:

- an anomalous curve for which the trace-one attack applies;
- a small-embedding-degree curve for which a pairing transfer is explicit;
- a curve whose chosen subgroup order is smooth;
- an ordinary prime-order control that passes the proposed generic-family
  filter;
- a mutation that changes one family field and must change the certificate.

Every row records the complete curve identity and the reason for inclusion or
exclusion. A “generic” label means only “passes the frozen filter”; it is not a
hardness certificate.

### Completion gate

PFSE-G1 is ready for dependent theorem work when:

- the family/sampler and quantifier order are frozen in machine-readable form;
- every exclusion has a mathematical reason and a positive fixture;
- the classifier reproduces every fixture independently;
- the source input scale is used for every transfer threshold;
- worst-case, average-case, density-one, single-target, and amortized claims
  cannot be confused by the schema;
- a Reviewer confirms that the target is not already false by one of the
  admitted controls.

### Falsification and limits

A false negative on a known weak control invalidates the classifier. A curve
passing the filter and later exhibiting special structure triggers a versioned
family amendment; it does not establish that all other passing curves are weak.
No finite sample establishes density one.

## 6. PFSE-G2 — Reproduce the generic barrier and build the model ladder

### Decision target

Establish exactly what the generic-group lower bound excludes and identify the
first additional coordinate operation that a candidate subexponential attack
needs. Turn “non-generic” from a label into a typed model difference.

### Known theorem baseline

For a group whose largest prime-order component has size `r`, Shoup's generic
model gives success bounded on the order of `q^2/r` after `q` oracle queries.
Constant success therefore needs `Omega(sqrt(r))` generic operations. The
bound applies to randomly encoded group elements and does not cover algorithms
that exploit their explicit elliptic-curve coordinates.

The baseline deliverable is a source-checked theorem statement containing the
model, input distribution, success probability, query bound, and the exact
uniformity/advice assumptions. Do not replace it with the slogan “rho is
optimal.” BSGS matches the exponent in the generic model; Pollard-rho behavior
depends on its walk/random-map assumptions and belongs in a separate baseline
record.

### Model ladder

Define at least the following interfaces, with syntax and operation cost:

| Model | Allowed observations | Intended result |
| --- | --- | --- |
| M0 | unique random labels, group operation, inversion, equality | reproduce the generic lower bound |
| M1 | M0 plus canonical affine/projective coordinates and base-field arithmetic | state why the M0 proof no longer applies; no lower bound is presumed |
| M2 | M1 plus rational maps represented by circuits of bounded size/degree | seek a transcript, degree-growth, or simulability bound |
| M3 | M2 plus algebraic predicates/factor-base membership and source recovery | connect to `KN-OPEN-020` and relation generation |
| M4 | unrestricted uniform classical algorithms | ultimate target; explicitly beyond current lower-bound methods |

Every model records whether preprocessing, branching on encodings, hashing,
random oracles, table lookup, and target-dependent predicates are allowed.

### Proof-search obligations

- **Baseline embedding:** M0 must reproduce Shoup's game exactly enough that a
  theorem statement can be compared line by line.
- **Observation collision:** for each added oracle, search for two group
  instances or scalars producing the same transcript but requiring different
  outputs.
- **Quantifier audit:** state whether the encoding, oracle, and preprocessing
  are adversarial, random, or chosen by the algorithm.
- **Method ceiling:** an M2/M3 theorem is never stated as an M4 theorem.
- **Proves-too-much control:** anomalous curves must either fall outside the
  assumptions or visibly break a claimed representation-aware theorem.
- **Single responsibilities:** separate transcript size, collision
  probability, correctness, runtime, and scope lemmas.

### Instrument experiment

Implement an M0 oracle simulator and run BSGS plus the repository's generic
walk controls across a deterministic size ladder. Measure oracle queries,
collisions, success, memory, and setup separately. This validates counters and
fixtures; it is not evidence for the theorem, which rests on proof.

A mutation oracle that leaks one scalar bit is the mandatory nearby-object
control. The lower-bound harness must detect that it is no longer M0 rather
than reporting the ordinary generic bound.

### Completion gate

PFSE-G2 completes its first milestone when the exact M0 theorem has a checked
primary-source derivation note and the oracle simulator passes all controls.
The research milestone is stronger: prove a nontrivial lower bound for at least
one precisely defined model strictly containing M0, or produce a scoped
obstruction record naming the exact oracle feature that defeats the proof
method. Neither outcome is a universal classical lower bound.

## 7. PFSE-G3 — Close or expose structural-transfer escape routes

### Decision target

For every admitted transfer family, determine whether a generic member of the
PFSE-G1 source family can be moved to a problem with `2^o(n)` total cost after
construction, evaluation, recovery, failure probability, memory, and target
algorithm costs are re-expressed in the original input size `n`.

### Required transfer certificate

Each candidate map or correspondence supplies:

```text
source curve/subgroup identity
domain, codomain, and working field
concrete map or construction algorithm
geometric degree and representation size
field of definition
subgroup preservation and kernel-intersection certificate
image order and scalar orientation
map construction and evaluation cost
inverse, dual, descent, or source-recovery procedure
target problem and target input size
target algorithm, success probability, memory, and preprocessing
full source-scale cost and verification step
```

A polynomial root that could be an endomorphism eigenvalue is not a subgroup
action certificate. Geometric degree is not map-evaluation cost. A small
target representation is not a cheaper source-to-target algorithm.

### Transfer families

1. MOV/Frey-Rueck pairing transfers, parameterized by embedding degree `k`.
2. Anomalous-curve additive or p-adic transfers, retained as positive controls.
3. Isogenies within an ordinary `F_p` isogeny class, with endomorphism-order
   levels and map construction charged.
4. Covers, Weil restriction/descent, Jacobian correspondences, and higher
   dimensional decompositions.
5. Endomorphism and automorphism actions used for scalar decomposition or rho
   quotienting.

For a finite-field target of size `N = p^k` and target cost
`L_N[alpha,c]`, the source-scale exponent is computed from

```text
log T ~ c (k n)^alpha (log(k n))^(1-alpha).
```

For `alpha = 1/3`, a necessary source-scale subexponential condition is

```text
k (log(k n))^2 = o(n^2).
```

The protocol reports this derived quantity beside the exact finite-field
parameters. A statement that the destination algorithm is subexponential in
its own input size is insufficient.

Fixed automorphism groups receive only their supported constant-factor
interpretation: an ideal order-`m` quotient changes rho iterations by
approximately `sqrt(m)` before canonicalization and cycle costs. GLV-style
scalar decompositions and map evaluation are separately priced; neither is an
ECDLP exponent result by itself.

### Controls

- positive MOV instance with a verified small embedding degree;
- positive anomalous instance;
- explicit low-degree isogeny with verified subgroup transport and recovery;
- non-injective map whose kernel intersects the target subgroup;
- singular or formula-compatible invalid companion;
- a map with small geometric degree but deliberately expensive evaluation;
- an automorphism quotient whose ideal iteration reduction disappears after
  charged canonicalization, to test stage-versus-total reporting.

### Completion gate

The first milestone is a versioned transfer registry in which every known
family has a certificate or a named missing obligation and every target cost is
source-scaled. A scoped no-cheap-transfer theorem may cover only the enumerated
interfaces and PFSE-G1 family. The registry is not a complete classification of
all possible representations, covers, or correspondences.

## 8. PFSE-G4 — Establish the relation-generation and solver-cost frontier

### Decision target

For prime-field index-calculus architectures, optimize all admissible
parameters jointly and decide which precise assumption would have to fail for
the architecture to reach `2^o(n)` total cost. This is the main empirical and
asymptotic workstream.

### Common relation model

Let a factor base have size

```text
B(n) = 2^b(n)
```

and let relations use `m(n)` factor-base points. Under a random-sum heuristic,
the expected number of decompositions of one random target is approximately

```text
B^m / r.
```

Producing on the order of `B` relations for a relation matrix requires, at
minimum in the same heuristic,

```text
B^m / r >= B,
or (m - 1) b(n) >= n.
```

This is a supply condition, not a computational lower bound. It creates the
architecture's central tension:

- `B = r^delta` with fixed `delta > 0` already costs `2^(delta n)` merely to
  enumerate/store a linear-size object;
- `B = 2^o(n)` forces `m -> infinity`, moving the burden to construction and
  solution of growing structured polynomial systems.

The desired theorem for a precisely delimited architecture is therefore not
“relations are rare.” It is a proved lower bound on the cheapest complete
method for finding, verifying, ranking, and descending those relations after
optimizing `B`, `m`, representation, solver, and memory.

### Work decomposition

#### G4-A — Primary-source and theorem audit

Read the full Yokoyama-Yasuda-Takahashi-Kogure paper and extract:

- the exact definition of “naive” Semaev index calculus;
- every statistical assumption and its quantifiers;
- the lower-bound cost unit;
- the Gröbner/extended-Euclidean reduction;
- which choices of factor base, arity, preprocessing, and solver it covers;
- what it does not cover.

Until this is done, `KR-IC-401ebf` remains an abstract-level heuristic pointer
and must not be expanded into a universal prime-field no-go.

#### G4-B — Symbolic architecture optimizer

Create a cost worksheet with independently replaceable phases:

```text
T_total(n,theta) =
  T_setup + T_relation + T_verify + T_rank + T_LA + T_descent + T_recover,

theta = (B,m,base representation,solver,large-prime policy,memory,target count,...).
```

For each phase record rigorous lower/upper bounds, heuristic estimates, measured
fits, and unknowns in separate fields. Compute the lower envelope over all
admissible `theta(n)`; never optimize only fixed `m` or fixed `delta`.

The architecture is rigorously excluded from subexponential time only if an
unavoidable phase satisfies `T_i >= 2^(c n)` for some fixed `c > 0` over every
admissible parameter schedule. A fitted positive exponent is not that proof.

#### G4-C — Exact relation-supply census

Extend the existing prime-field implementation's exact small-instance census.
For each curve/base/arity cell retain:

- all attempted targets and tuples;
- decompositions and multiplicities;
- misses, duplicates, invalid and dependent relations;
- independent rank progression;
- relation and target-recovery probability;
- setup, table, solver, verification, and memory counters;
- complete small-instance DLP verification when feasible.

Use matched random bases, algebraic/structured bases, isomorphic model controls,
and planted-relation positive controls. Compare the empirical distribution of
preimage counts with the frozen random-map prediction, including zero and tail
counts; a mean alone cannot validate the relation model.

#### G4-D — Solver and arity ladder

Measure exhaustive, meet-in-the-middle, Gröbner, SAT, and any admitted solver
on identical certified systems. Vary `m` rather than extrapolating from only
`m=2,3`. Record observed solving degree only under its correct definition;
Macaulay degree, maximum row degree, timeout, and memory are separate metrics.
Timeouts are censored observations, not “no relation” and not mathematical
lower bounds.

#### G4-E — Full-pipeline comparison

Join admissible relation-supply, solver, rank, linear-algebra, descent, recovery,
and verification records into the `GOAL-ICEX-001` charged comparison. Preserve
each cost unit and supply a conversion model before any total is formed. Report
time, memory, preprocessing, online work, and target count together.

### Completion gates

PFSE-G4 has three increasingly strong deliverables:

1. **Measured frontier:** reproducible exact and censored data with no
   asymptotic conclusion beyond the tested range.
2. **Conditional architecture theorem:** a single-responsibility derivation of
   total cost under numbered relation and solver heuristics, with each heuristic
   receiving a validation/falsification protocol.
3. **Scoped no-go theorem:** an unconditional lower bound for a precisely
   specified architecture. It must state the interfaces it excludes and the
   routes it leaves open.

Only the third is a mathematical nonexistence result, and only inside its
architecture. The first two remain valuable even if their observations point
in no preferred direction.

## 9. PFSE-G5 — Prove a representation-aware lower bound or name the obstruction

### Decision target

Move one step beyond the generic-group model: prove a lower bound for a model
that admits an explicitly useful portion of elliptic-curve representation, or
identify exactly why the lower-bound method fails when that portion is added.

### Candidate theorem shape

For a frozen model `M_j`, curve distribution `F_n`, allowed preprocessing `P`,
and success probability `epsilon`, prove a statement of the form

```text
Pr[A solves ECDLP] <= Bound(T,P,n)
```

where `Bound` is negligible for every `T = 2^o(n)` and admissible `P`; or prove
the weaker but still decisive lower bound `T >= r^c` for some fixed `c > 0`.

The theorem statement must expose:

- the encoding and curve distribution;
- all oracle operations and their bit costs;
- whether the algorithm branches on coordinate bits;
- preprocessing/advice dependence;
- degree and circuit-size growth of rational maps;
- equality, zero, membership, source-recovery, and factorization tests;
- success probability, memory, and uniformity;
- excluded exceptional curves.

### Proof obligations

1. **Transcript normal form:** represent every value and branch condition the
   model can construct.
2. **Growth lemma:** bound degree, circuit size, number of exceptional loci, or
   another complexity measure after `T` operations.
3. **Collision/identifiability lemma:** bound the probability that two hidden
   scalars become distinguishable through the transcript.
4. **Correctness lemma:** show why success implies one of the bounded events.
5. **Runtime and memory lemma:** charge every allowed operation in bit or field
   complexity, not only oracle calls.
6. **Scope lemma:** prove that the PFSE-G1 family satisfies the assumptions.
7. **Assembly theorem:** combine the lemmas without introducing a new
   heuristic or uncharged oracle.

### Cheap falsification before proof search

- Run the observation-collision test from `KN-TECH-080` on the proposed
  transcript invariant.
- Test the theorem on an anomalous curve and a small-embedding-degree curve. A
  theorem that also rules out their known attacks is missing a hypothesis or
  an allowed operation.
- Embed M0 exactly and recover its known lower bound as a boundary case.
- Give the algorithm a one-bit leakage oracle and confirm that the proof marks
  the new information rather than silently simulating it.
- Search for high-degree maps with small arithmetic circuits; a degree-only
  argument that rejects them without pricing circuit evaluation has exceeded
  its method ceiling.

### Completion gate

The first publishable milestone is either:

- a checked theorem for a named model strictly containing M0; or
- a checked counterexample/obstruction showing that the proposed measure is
  non-identifying, with the smallest additional operation that breaks the
  proof and a successor model/proof obligation.

Failure to prove the theorem within a budget is neither deliverable. A scoped
counterexample to the proof method is.

## 10. Common asymptotic and heuristic falsification protocol

Every candidate architecture supplies phase costs `T_i(n,theta)` and the
optimized normalized exponent

```text
tau(n) = inf_theta max_i log2(T_i(n,theta)) / n.
```

The use of `max` gives the bottleneck exponent; reports may also retain the
exact sum for concrete costs. Interpretations are:

- a rigorous `liminf tau(n) > 0` excludes subexponential time for the frozen
  architecture;
- `tau(n) -> 0` is only a necessary asymptotic pass, not an algorithm;
- a measured positive local slope is evidence about the measured regime, not
  the limit;
- optimizing fixed parameters is invalid when `theta` may depend on `n`.

Runner reports include the effective slope

```text
a_eff(n1,n2) =
  (log2 T(n2) - log2 T(n1)) / (n2 - n1)
```

for descriptive diagnosis. Under a clean `r^c` law it approaches `c`; under a
true `2^o(n)` law it should tend toward zero. At practical sizes, different
power, `L`, and mixed-overhead models can be statistically indistinguishable.
Model comparison therefore reports holdout prediction, uncertainty, residuals,
and the largest tested scale rather than selecting a preferred asymptotic by
in-sample fit alone.

Heuristics are numbered and individually falsifiable. Recommended initial
heuristics are:

- **HEUR-PFSE-REL-1:** after conditioning on the frozen curve/base stratum,
  `m`-term sums behave like a stated random-map occupancy model.
- **HEUR-PFSE-SOL-1:** a specified algebraic-system ensemble follows a stated
  solving-degree or cost distribution uniformly over a declared parameter
  range.
- **HEUR-PFSE-TRF-1:** a stated transfer parameter, such as embedding degree or
  smoothness, follows a named distribution under the PFSE-G1 sampler.

Each heuristic records quantifiers, uniformity range, random-model
justification, supporting rigorous facts, a direct validation experiment, a
tail check, and a falsification condition. Rejection of one heuristic changes
only the theorem branches that cite it.

## 11. Proposed work packages

These are dispatch designs, not committed handoffs. When selected, the
Coordinator allocates real IDs, writes the frozen protocol, checks
preapproval, and publishes the queue before an Executor or runner begins.

### PFSE-WP0 — Literature and prior-art adjudication

- **Owner role:** Idea Generator / deep research; independent Reviewer.
- **Inputs:** Section 14 sources, frontier map, existing ECDLP goals and open
  problems.
- **Deliverables:** theorem-assumption table; exact coverage/noncoverage map;
  source-provenance log; proposed corrections as new records, never edits to
  immutable literature records.
- **Required focus:** full Yokoyama et al. text; exact Shoup theorem; JMV level
  restriction; prime-field versus extension-field index-calculus boundary.
- **Completion gate:** every load-bearing claim is primary-source read or
  explicitly marked inaccessible/unverified; contradictions retained.
- **Budget:** reading task, no scientific compute; one producer session and one
  independent source audit.

### PFSE-WP1 — Family specification and classifier fixtures

- **Owner role:** Experiment Director, then Executor implementation.
- **Write scope when materialized:** a new task-owned directory under
  `research/prime_field_subexponential/family/` plus its frozen protocol.
- **Deliverables:** machine-readable family schema, deterministic fixture
  generator, positive/negative fixtures, independent classifier, report.
- **Completion gate:** all Section 5 controls pass; all identities and subgroup
  orders independently verified.
- **Resource envelope:** one CPU worker, at most 4 GiB, exact toy/medium
  arithmetic only; no cryptographic-scale search.

### PFSE-WP2 — Generic oracle and model-boundary harness

- **Owner role:** Executor implementation; Validator; proof Reviewer.
- **Deliverables:** M0 oracle simulator, BSGS/walk controls, query/memory/setup
  counters, leakage mutation, theorem extraction note, model-ladder schema.
- **Completion gate:** counters agree with independent replay; leakage control
  is rejected from M0; theorem text matches the checked source.
- **Resource envelope:** deterministic ladder through sizes that finish within
  30 minutes per cell and 8 GiB; sizes are fixed in the eventual protocol.

### PFSE-WP3 — Transfer registry and source-scale cost calculator

- **Owner role:** Transfer/endomorphism assessor; Executor only for approved
  synthetic fixtures; independent subgroup/cost Reviewer.
- **Deliverables:** transfer-certificate schema, positive/negative fixture
  certificates, symbolic `L`-cost converter, obligation matrix, report.
- **Completion gate:** every fixture verifies subgroup action and recovery;
  every target cost is expressed in `n`; unimplemented maps remain explicitly
  unresolved.
- **Resource envelope:** exact synthetic fixtures and symbolic calculation;
  no search for a path to a production target.

### PFSE-WP4 — Relation-supply census and asymptotic optimizer

- **Owner role:** Index-calculus Experiment Director; Executor; Validator; Red
  Team for model and extrapolation.
- **Inputs:** existing prime-field implementation and archived exact rows;
  frozen factor bases and curve identities.
- **Deliverables:** phase-separated symbolic optimizer, exact relation census,
  solver/arity ladder, export bundle, stage report, full-cost join proposal.
- **Completion gate:** all attempts and failures retained; independent relation
  rank verified; random-map controls and planted controls pass; fits use
  holdouts and expose censoring; no cross-unit total appears without a stated
  conversion.
- **Resource envelope:** start with the existing 4-core/16-GiB toy ladder;
  larger cells require a protocol amendment with explicit timeout, memory, and
  checkpoint rules. Resource exhaustion is preserved, not converted to a
  mathematical negative.

### PFSE-WP5 — Representation-aware proof-search packet

- **Owner role:** proof-oriented Idea Generator; formal Executor for the
  smallest lemma; independent breakthrough-tier Reviewer only if the claimed
  bound exceeds established evidence.
- **Deliverables:** formal model syntax, proof-search map, M0 boundary fixture,
  observation-collision search, quantifier audit, nearby-object controls,
  single-responsibility lemma statements, smallest formalization target.
- **Completion gate:** the proposed observable survives the cheap audits or a
  machine-checkable collision is preserved; the theorem's method ceiling is
  explicit; anomalous and leakage controls do not produce a false universal.
- **Resource envelope:** cheap audits first; no large search or formalization
  until the baseline, quantifiers, and observation test pass.

### PFSE-WP6 — Independent synthesis and decision packet

- **Owner role:** Coordinator after producer snapshots and independent reviews.
- **Inputs:** only archived outputs of WP0-WP5.
- **Deliverables:** evidence-bounded synthesis, theorem dependency DAG, exact
  open obligations, concrete-cost table where an asymptotic claim exists, and
  one next action.
- **Completion gate:** observations, conditional derivations, proved scoped
  bounds, and open universal claims are visibly distinct. No finite experiment
  is used to close the M4 question.

## 12. Dependency graph and recommended order

```text
PFSE-WP0 literature adjudication
          |
          v
PFSE-WP1 family/quantifier freeze
     |           |             |
     v           v             v
PFSE-WP2      PFSE-WP3      PFSE-WP4
generic       transfers     relations/solver
     \           |            /
      \          |           /
       +------ PFSE-WP5 -----+
             model theorem
                  |
                  v
             PFSE-WP6
              synthesis
```

Recommended first bounded batch:

1. WP0 extracts Yokoyama et al.'s exact theorem and reconciles the frontier
   records.
2. WP1 freezes the family and cost quantifiers.
3. In parallel only after their inputs are committed, WP4 builds the symbolic
   optimizer from existing measurements and WP2 builds the M0 instrumentation
   fixture.

WP3 can reuse the family statement once WP1 is stable. WP5 should not begin a
large proof search until WP2-WP4 identify the exact representation operation
and bottleneck to model.

## 13. Runner and evidence contract

The public runner executes only a real frozen `EXP-*`, `TASK-*`, or `GOAL-*`
materialized from this plan. It does not execute `PFSE-WP*` labels directly.
For every run, preserve:

- exact command, commit, dirty-tree status, dependency versions, environment,
  hardware, seed, inputs, and timeout;
- stdout, stderr, raw machine-readable data, exit status, checkpoints, and
  peak resources;
- setup, online, verification, and excluded costs separately;
- failed controls, invalid rows, timeouts, duplicates, and missing metrics;
- an independent correctness certificate or an explicit `certificate: none`
  for descriptive measurements;
- the frozen protocol and one `experiment.export/v1` bundle;
- a visual report and PDF when required by the repository contract.

No runner changes a hypothesis or goal status. A passing run is an observation.
A timeout or implementation failure is operational evidence only. A smaller
diagnostic does not discharge a larger requested cell.

## 14. Sources checked and evidence gaps

### Primary sources read for this planning task

1. Victor Shoup, *Lower Bounds for Discrete Logarithms and Related Problems*,
   EUROCRYPT 1997, DOI
   [10.1007/3-540-69053-0_18](https://doi.org/10.1007/3-540-69053-0_18).
   Full text read on 2026-10-31. Theorem 1 gives the random-encoding/random-input
   success bound of order `m^2/r` for `m` generic queries and identifies
   representation exploitation as the route outside the theorem.
2. David Jao, Stephen Miller, and Ramarathnam Venkatesan, *Do All Elliptic
   Curves of the Same Order Have the Same Difficulty of Discrete Log?*,
   arXiv:[math/0411378](https://arxiv.org/abs/math/0411378), version 3.
   Full text read on 2026-10-31. The reduction is GRH-conditional, operates
   within fixed endomorphism-ring levels, and requires separate handling of
   conductor gaps; it does not establish an unconditional equivalence across
   every curve of the same order.

### Repository sources checked

- `docs/ecdlp-literature-review-20260926.md`;
- `knowledge/frontiers/ecdlp/generic-rho/` and
  `knowledge/frontiers/ecdlp/index-calculus/`;
- `KN-LIT-011`, `KN-LIT-006`, `KN-LIT-d8e1b9`, `KN-LIT-084`,
  `KN-LIT-085`, `KN-LIT-087`, `KN-LIT-088`, `KN-LIT-089`, and
  `KN-LIT-171`;
- `KN-OPEN-001`, `KN-OPEN-005`, and `KN-OPEN-020`;
- `GOAL-ECDLP-001`, `GOAL-PATH-001`, `GOAL-SDEG-001`,
  `GOAL-RELN-001`, `GOAL-ICEX-001`, and `SG-ECDLP-002`;
- `src/crypto_autoresearcher/index_calculus/README.md` and the existing
  prime-field exact-cost results recorded there.

### Evidence gaps that bind future work

- The full Yokoyama-Yasuda-Takahashi-Kogure article was not retrievable in
  this session; the publisher and DOAJ abstract were read. Its exact
  statistical assumptions and architecture boundary are therefore not yet
  verified and are WP0's first gate.
- The IACR PDF for Semaev 2004 returned HTTP 403, but its PostScript endpoint
  was accessible and the full six-page source was read during the WP0/WP1
  continuation recorded in
  `docs/research/pfse-wp0-wp1-gate-20261031.md`. The Galbraith-Gaudry survey's
  exact HAL record and PDF path were found, but its file endpoint returned HTTP
  403. No section-level survey claim is upgraded here.
- Existing toy measurements calibrate specified algorithms and instruments;
  they are not evidence of a universal asymptotic lower bound.
- No source or internal record reviewed here proves a lower bound for
  unrestricted classical algorithms on explicitly encoded ordinary
  prime-field curves.

## 15. What success means

This program can make real progress without resolving the universal question.
Valid target outcomes include:

- a verified family and quantifier specification;
- a lower bound in a model strictly broader than the generic group model;
- a complete source-scaled obstruction for an enumerated transfer class;
- a conditional total-cost theorem with individually tested heuristics;
- a counterexample showing that a proposed lower-bound observable is
  non-identifying;
- a measured frontier that exposes exactly which unproved solver or relation
  assumption carries a subexponential claim.

None is renamed “proof that no subexponential algorithm exists” unless its
theorem actually quantifies over the full intended computation model.
