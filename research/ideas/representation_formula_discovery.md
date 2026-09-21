# ECC representation and formula discovery

Prepared 2026-09-09 for `aburan28/crypto-autoresearcher`.

**Status: proposal intake only; all six experiments are unrun.** This document
and the [machine-readable pack](../experiments/representation_formula_discovery_proposals.yaml)
import the discussion's six proposals. They do not implement solvers, create
canonical experiment records, dispatch tasks, approve protocols, or change
ledger state. Numerical improvement thresholds are proposed design choices,
not predictions or observed results.

The bibliography and source-inspection notes in the YAML are inherited from
the original design pack. This import is not a fresh literature review or a
reproduction of those papers. Blanket novelty and unrestricted ECC lower-bound
claims are explicitly excluded.

## What to optimize

Keep three objectives separate: the cost of a complete Pollard-rho transition,
the cost of finding a valid point decomposition, and the total cost of collecting
useful relations and recovering a target logarithm. Arithmetic gains are useful
without implying an improved asymptotic exponent. A smaller equation system is
not useful if its solutions fail to lift or its relations fail to increase rank.

| Draft slug | Objective | First comparison |
| --- | --- | --- |
| `addition-law-superoptimization` | Cheaper certified arithmetic circuits | Synthesized mixed addition versus applicable EFD formulas |
| `rho-coordinate-workload-codesign` | Faster complete collision search | Projective/mixed coordinates versus batched affine arithmetic |
| `relation-circuit-synthesis` | Easier equivalent decomposition encodings | Chain versus balanced tree versus hybrid elimination |
| `point-chart-factor-base-codesign` | Better charts and membership predicates | Transport a fixed base first; change the actual base second |
| `representation-mechanism-audit` | Correctly attribute any improvement | Preserved algebraic objects versus solver-facing changes |
| `restricted-lower-bounds-and-cost-audit` | Checkable model-bounded exclusions and costs | Finite-grammar certificates and exact relation-yield bounds |

The YAML retains each hypothesis, mechanism, search arms, controls, proof
obligations, primary and diagnostic metrics, promotion target, falsification
criteria, and required artifacts. Slugs are intake keys, not canonical IDs.

## 1. Addition-law superoptimization

Use counterexample-guided synthesis over a typed arithmetic DAG. Start with
`P -> P + A` for a public affine step-table point `A`; distinguish formulas
specialized to one table entry from formulas accepting any entry. Search
factoring, shared intermediates, cached coordinates, dependency schedules,
and square-versus-multiply choices. Seed from applicable EFD formulas [S1];
use the synthesis pattern described in [S8].

A verifier must establish the declared input domain and reject counterexamples.
Check infinity, inverse points, doubling, zero denominators and projective
rescaling. An incomplete formula needs an explicit, verified fallback, and its
cost is included. Tiny exhaustive tests and randomized tests are controls, not
a universal proof. Prime-field arithmetic must not silently become word overflow;
binary multiplication must use the specified irreducible-polynomial reduction.

Measure compiled complete-transition time, register use, spills, dependency
depth, conversion and exceptional-case costs, not just multiplication counts.
The proposed engineering gate is a reproducible 10% transition-time improvement
against the strongest matched baseline, with no correctness failures. Synthesis
and compilation costs belong in cold-start and explicit-reuse accounting.

## 2. Coordinates inside the actual rho walk

Compare applicable projective/mixed coordinates and verified batched affine
arithmetic. The initial batch-size panel is `1, 8, 32, 128, 512`. For binary
fields, compare polynomial, normal and certified hybrid field representations;
charge basis conversion. Historical ECC2K-130 work [S9] is precedent, not a
performance forecast for current hardware.

First preserve the mathematical walk: identical step table, partition,
distinguished-point predicate, seeds and targets. Equivalent projective
encodings of a point must give the same point-level next state and endpoint
decision, unless an extended-state walk is explicitly specified. Only then
compare changed walks as a separate experiment.

Verify `X = aG + bQ` throughout toy executions. Negation and endomorphism steps
must transport the coefficients correctly. Measure useful collisions, short
cycles, restarts, endpoint traffic and normalization. A cheaper iteration that
requires more iterations need not be a faster attack. X-only differential
addition requires its difference state; it is not an ordinary rho-addition
replacement. The proposed complete-workload improvement gate is 10% with
independent reproduction. Full-size kernel throughput is arithmetic evidence,
not a claim of full-size DLP recovery.

## 3. Equivalent relation-circuit synthesis

**First scientific experiment:** freeze the original field, curve, subgroup,
factor-base point list and targets, and change only the exact presentation of

$$P_1+\cdots+P_m=R,\qquad P_i\in F.$$

Compare direct Semaev systems where feasible, chains of third summation
polynomials, full-point addition chains, balanced trees and partially eliminated
hybrids. For four summands, a balanced encoding is

$$U=P_1+P_2,\quad V=P_3+P_4,\quad U+V=R.$$

Retaining an auxiliary variable with its defining equation can preserve lower
local degree without forcing every expression to expand. That can also add
variables or make solving harder: the experiment, not input degree, decides.
Auxiliary formulations, symmetry-sensitive systems and SAT-based binary point
decomposition have prior work [S2-S6].

Compile applicable encodings to finite-field systems and binary XOR-aware SAT.
Treat prime-field bit encodings as a separate, fully charged backend. An
independent exhaustive or MITM oracle checks tiny instances. Require both
soundness and completeness: returned assignments must lift to original-field,
original-subgroup points, and every oracle decomposition must be representable.
Local Semaev roots do not by themselves establish globally compatible signs or
intermediate points.

Use uniform targets for yield. Keep planted-SAT and certified-UNSAT controls
separate. Measure charged cost per useful independent relation and time to a
fixed rank, not just successful solves. The proposed gate is a 25% reduction on
the two largest completed held-out sizes with paired uncertainty excluding no
improvement. Censored or thin evidence is inconclusive, not negative mathematics.

## 4. Point-chart and factor-base co-design

Start with reversible charts such as `u=x+c*y, v=y`, inverse `x=u-c*v, y=v`.
Extend to bounded triangular polynomial maps and rational charts with explicit
inverses, denominator domains and exceptional-point coverage. Model changes
are separate arms: check that the original curve admits the desired model over
the original field rather than assuming every curve has an Edwards or
Montgomery model [S2, S3].

Stage A transports the exact same factor-base points and targets. A bijective
change of description cannot change decomposition existence. Stage B changes
the actual membership predicate at matched full-point cardinality and charges
base construction, sampling, conversion and predicate compilation. Do not
invent an F2-linear field-basis interpretation for a prime field.

Record sumset support, duplicates, rank growth and held-out success. Reject gains
caused by dropping difficult chart cases, hidden enumeration, free conversion,
or leaked factor-base logarithms. Arbitrary charts require transporting the
whole group-law constraint; their coordinates do not automatically inherit an
unrelated model's familiar addition law. The proposed gate is 20% lower net
relation cost, including discovery/setup under an explicitly stated reuse model.

## 5. Mechanism and symmetry audit

For every transform state exactly what is preserved: the same ideal, a graded-
isomorphic ideal, the same projected solution set, the same original point set,
or a quotient with a certified lift. These require different certificates.

An invertible homogeneous linear substitution induces a graded isomorphism
`S/I ~= S/phi(I)`, preserving the Hilbert function and intrinsic regularity.
Solver runtime and sparsity may still change. Keep input degree, first-fall
degree, observed solving degree and intrinsic regularity distinct [S6, S10].
A verified engineering improvement remains useful even when its proposed
structural explanation is wrong.

Require field-of-definition and target-transport checks for Frobenius. Squaring
coordinates on a random binary curve also squares its coefficients; it need
not preserve that curve. A fixed target moves to `pi(R)` unless it is fixed.
On `E(F_p)`, p-power Frobenius fixes rational points. For a rectangular Macaulay
map, use compatible domain/codomain actions:

$$M F_{\mathrm{domain}}=F_{\mathrm{codomain}}M.$$

Do not use an ill-typed square commutator or discard small nonzero blocks and
call the result exact.

Reuse, rather than rename, the existing proposals in
[frobenius_next_wave_experiments.yaml](../experiments/frobenius_next_wave_experiments.yaml):
`EXP-FROB-GBORDER-002`, `EXP-FROB-CHARMAC-002`, `EXP-SDEG-BASISSURR-001`,
`EXP-SDEG-ACTIVEBASIS-001` and `EXP-FROB-STABSTRATA-002`. Their source snapshot
is pinned in the YAML. Its `proposed` label is not proof that no execution or
successor record exists elsewhere; the canonical intake must check current
knowledge and ledger history.

## 6. Restricted lower bounds and full-cost accounting

Shoup's generic-group lower bound [S7] is not an unrestricted lower bound on
coordinate-aware index calculus. Every exclusion must state its oracle model,
preprocessing, quantifiers and allowed operations.

For a fixed full-point factor base `F` of size `B` in a subgroup of order `N`,
let `mF` be the attainable sums of exactly `m` points, with repetitions allowed.
For a uniform target chosen independently of `F`,

$$p_{\mathrm{dec}}=\frac{|mF|}{N}\leq
\min\left(1,\frac{\binom{B+m-1}{m}}{N}\right).$$

Every attainable sum comes from an m-element multiset. Counting those multisets
gives the bound without assuming sums are uniformly distributed or distinct.
For distinct summands use `binom(B,m)`. Count actual signed points, not just
x-coordinate entries. Adaptive bases, shared batches, multi-output attempts,
and symmetry quotients require separately declared counting models.

Under the restricted independent-uniform repeated-trial model, at most one
useful output per attempt, cost at least `c` per attempt, and success probability
at most `p_max`, expected work for `R_needed` useful outputs is at least
`R_needed*c/p_max`. Do not apply this automatically to other algorithm models.

A finite-grammar synthesis UNSAT certificate excludes only the encoded field,
domain, grammar and cost region. It needs an independent certificate checker
and encoding review. A timeout or an unchecked UNSAT message is not a proof.
The first proposed Lean target is the finite multiset-image bound, after freezing
its exact statement and dependencies; no Lean proof is delivered by this PR.

For measurements use

```text
charged_relation_cost =
  (generation + construction + solving + lifting + verification + rank_tracking)
  / useful_rank_increase

total_IC_time = search + setup + relation_collection + linear_algebra + target_recovery
```

Zero rank increase is not zero cost. Rank is computed modulo subgroup order,
not modulo the coordinate-field characteristic. Preserve full relation rows.
Compare cold-start and explicitly amortized cost against matched optimized rho
and applicable MITM baselines, with memory and valid automorphisms accounted for.

## Harness intake and delivery order

Use the existing public `crypto-autoresearcher-harness` ideas/design path; do not
add a second dispatcher. Begin with representation contracts, an independent
oracle, mechanism auditing and cost accounting. Then compare exact relation
circuits on fixed bases. Run arithmetic synthesis and complete-rho benchmarks
as a parallel practical lane. Only compose survivors or change factor bases
after the isolated comparisons.

The proposed initial ladder is 11, 13, 17, 19 and 23 field bits/degrees, arities
3 and 4, and 256 uniform target seeds per cell. Let `B0` be the smallest integer
with `B0^m >= N`; compare valid sizes `ceil(B0/2), B0, 2*B0`. Keep prime-field,
ordinary binary and Koblitz panels separate. Do not count isomorphic models as
independent curves. Freeze actual manifests, rejection sampling and curve-level
splits; never leak generator-known logarithms to the search or solver.

Before dispatch, the Coordinator must resolve the following technical intake
requirements under the repository's standing user authorization:

1. Refresh KB, ledger and literature deduplication; record the frontier comparison
   and preserve existing scoped negative results and immutable records.
2. Allocate/check canonical random-suffix IDs with `tools/allocate_id.py` and
   freeze exact specifications using `templates/research-records.md`.
3. Freeze solver/compiler versions, commands, seeds, artifacts, dependencies,
   comparison counts, memory/concurrency protections and review handoffs.
   Proof-oriented tasks also require the proof-search-map audits and Lean target.
4. Complete the committed approval, dispatcher preflight, snapshot, independent
   review and Coordinator ledger-archive gates at the appropriate lifecycle stages.

No extra user approval is requested. Merging this intake pack alone does not
make its descriptive slugs executable or satisfy those gates. Routine campaign
spending caps remain null; scientific sample counts and machine protection are
separate controls. All runtime results and proof certificates listed in the
YAML are future deliverables, not files claimed to exist in this PR.

## Sources

Source keys refer to the inherited bibliography and inspection scope in the YAML.
[S1](https://www.hyperelliptic.org/EFD/) EFD;
[S2](https://eprint.iacr.org/2012/199) symmetry-sensitive index calculus;
[S3](https://link.springer.com/chapter/10.1007/978-3-642-55220-5_3) symmetrized summation polynomials;
[S4](https://link.springer.com/chapter/10.1007/978-3-030-51938-4_11) SAT-based binary index calculus;
[S5](https://arxiv.org/html/1504.02347v2) binary point decomposition;
[S6](https://arxiv.org/html/1503.08001v3) notes on summation polynomials;
[S7](https://www.shoup.net/papers/dlbounds1.pdf) generic-group lower bounds;
[S8](https://people.csail.mit.edu/asolar/SynthesisCourse2020/Lecture10.htm) counterexample-guided synthesis;
[S9](https://homepage.iis.sinica.edu.tw/papers/byyang/11528-F.pdf) ECC2K-130 GPU arithmetic;
[S10](https://arxiv.org/abs/1706.06319) solving degree and commutative-algebra invariants.
