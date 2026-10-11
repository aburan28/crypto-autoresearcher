# SNFS-E3 prescribed-fibre section-solver design audit

```yaml
generated_at: 2026-10-10
task_id: T-959
fencing_epoch: 1
idea_id: IDEA-20261009-581f5d
hypothesis_id: H-ECDLP-bd1572
goal_id: GOAL-ECDLP-001
idea_status: proposed
idea_approval: false
goal_status_change: none
scientific_result: none
disposition: keep proposed; do not approve or dispatch
```

## Evidence and mechanism

The idea proposes measuring the cost of finding a bounded-height section
`sigma=(x(t),y(t))` on an elliptic surface `S/F_p(t)` whose specialization at a
fixed `t_0` is a prescribed point of a fibre `E/F_p`. Relation sections and one
target section are intended to reduce the section-finding problem to a finite
coefficient system; the Mordell--Weil union of solution sets is the proposed
structural distinction from a dense random system. The load-bearing
observables are solver cost, degree of regularity, first-fall degree, and
certificate-checked recovery at the frozen degree selected from E4.

The novelty boundary is narrow: a finite complexity measurement for this
prescribed-fibre coefficient system, with structured-versus-random controls.
It is not a new surface-through-fibre construction, not a proof that the
Mordell--Weil structure helps, not a general section-incidence result, and not
an attack claim. The parent hypothesis places this in the function-field F5
lifting face and treats it as a heuristic test, not a theorem. `KN-TECH-06bb4e`
requires the proposal to state which F5 obstruction it addresses; this audit
records the tested question as whether bounded degree and prescribed
specialization make the section solver cheaper than its matched random null.

Repository evidence read: `ledger/proposals/IDEA-20261009-581f5d.yaml`,
`ledger/hypotheses/H-ECDLP-bd1572.yaml`,
`experiments/EXP-ECDLP-3e8403/specification.yaml`, its `implementation/run.py`
and `implementation/primeset.py`, `knowledge/techniques/KN-TECH-06bb4e.md`,
and `ledger/proposals/IDEA-20260906-7304fe.yaml`. The idea itself says that
E1 and E4 are prerequisites, that its current p range is a small-p finite
measurement, and that no asymptotic statement is permitted.

## Overlap and required reuse

`EXP-ECDLP-3e8403` is a different experiment. Its object is a lift of a
curve into `K_d = Q[x]/(x^d-c)` or a matched base-m field, with a Q-lift arm,
square tests, residue membership, and the `D(W)`, `Y(W)`, and `gamma`
coverage statistics. Its implementation does not construct or solve a
prescribed-fibre section system. Therefore:

- Reuse only the byte-identical special-prime and matched-random-prime
  conventions from `implementation/primeset.py`, the seed domain-separation
  convention, manifest/hash practice, and the general replay and invalidation
  discipline.
- Remove from this proposal the K-point square test, degree-one-prime field
  arithmetic, Q-lift arm, residue-coverage statistics, `gamma`, `Y_max`, and
  the degree ladder. Those measure the existing field-lift contract and must
  not be relabelled as section-solver evidence.
- The section protocol needs its own solver implementation, specification,
  trial plan, and run artifacts. The existing EXP launcher is not a runnable
  implementation of IDEA-20261009-581f5d.

`IDEA-20260906-7304fe` is adjacent and partially overlapping. It starts from
jointly target-labelled sections and eliminates shared surface coefficients
to measure an interpolation-defect representation and the cost per
Q-informative relation. Reuse its requirements for labelled specialization,
certified back-substitution, group-law verification, charged failed attempts,
matched random labels, and the rule that section abundance is not a useful
relation. Remove from this proposal its joint surface-incidence objective,
factor-two informative-relation target, multiplicity-weighting claim, and
Q-coefficient yield analysis. A future combined protocol would need a new
successor contract; it must not merge the two mechanisms by prose.

## Readiness verdict

As filed, IDEA-20261009-581f5d is **not runnable and not approvable**. The
following fields are missing or not frozen:

1. An exact E1 surface-through-fibre constructor, its source identity, and a
   certificate for every accepted surface and independent section set. The
   fallback to unconstrained surfaces changes the realization question and
   cannot silently substitute for the prescribed-fibre arm.
2. The exact fibre equation, `t_0`, point encoding, subgroup/order, and the
   relation and target labels. The filing does not resolve how a section
   through the point at infinity is represented; affine `x,y` polynomials
   cannot encode that case without a separate projective contract.
3. A finite cell set for p, `chi`, and the selected section rank `r`, plus a
   deterministic prime and surface selection rule. “`r` as achieved” is not
   a frozen design.
4. The coefficient parameterization and the exact height-to-degree map. The
   degree must be selected from the E4 receipt before solver selection and
   cannot be tuned after seeing solver behavior.
5. Canonical field arithmetic, solver names, exact versions or commits,
   command lines, output certificates, and independent checking rules. The
   current record names Magma, msolve, CryptoMiniSat, WDSat, a hybrid, and
   interpolation, but pins none of them.
6. A random-system null with the same variable count, equation count,
   degrees, coefficient distribution, planted-solution policy, and seed
   stream. “Dense system of identical shape” is not enough to reproduce it.
7. Separate planted-section, known-answer, and soundness/completeness
   controls, including a check that the recovered specialization is the
   prescribed point and that any relation coefficient claimed useful is
   nonzero in the declared subgroup.
8. Definitions for Groebner degree of regularity, first-fall degree, solver
   work, field-operation and bit-operation counts, peak memory, retained
   bytes, and all setup, failed-attempt, relation-collection, and linear
   algebra costs.
9. Per-cell time and memory censoring, total resource limits, seed derivation,
   matched rho procedure, replay receipts, and exact raw-artifact paths.

## Bounded repair specification (design only; not approval)

The following is a finite repair boundary. It becomes a runnable contract
only after E1, E4, and SNFS-A3 supply the missing immutable inputs and solver
pins; it is deliberately not an authorization to execute.

- **Surface and fibre.** Use short Weierstrass surfaces over `F_p(t)` with
  `t_0=0`, `E_0: y^2=x^3+a_0x+b_0`, and
  `A(t)=a_0+sum(i=1..4chi) A_i t^i`,
  `B(t)=b_0+sum(i=1..6chi) B_i t^i`. Coefficients are canonical residues in
  `[0,p)`, ordered low-to-high, and the discriminant and good-specialization
  checks are mandatory. E1 must construct the surface by finite enumeration
  of these coefficients while imposing the section identities and prescribed
  specializations; its constructor receipt must bind the exact accepted
  `(A,B)` and section witnesses. No unconstrained-surface fallback is part of
  this first contract.
- **Section labels and representation.** Use four, five, or six selected
  independent affine sections (`r in {4,5,6}`) with fixed non-identity fibre
  labels from the certified subgroup, plus one target label. Parameterize
  `x(t)=sum(i=0..d) x_i t^i` and
  `y(t)=sum(j=0..ceil(3d/2)) y_j t^j`, impose
  `y(t)^2=x(t)^3+A(t)x(t)+B(t)` over `F_p[t]`, and impose the exact value at
  `t=0`. The identity section is excluded from this affine pilot; an O-arm
  requires a separately frozen homogeneous Weierstrass triple and must not be
  smuggled into the affine system.
- **p, `chi`, and degree.** Use special primes generated by the shared
  `p=m^e-c` family with `e in {2,3,4,5}`, the existing squarefree `c` list,
  and bit lengths `{12,16,20,24,28}`; use one seeded matched random prime at
  each bit length. Use `chi in {1,2,3}` and `r in {4,5,6}` as fixed cells,
  omitting only cells for which the predeclared E1 constructor has no
  certificate. Set `d` before solver choice as the least integer satisfying
  the E4 frozen count rule `N_E4(p,chi,r,H(d)) >= p`, with the exact E4
  `H<->d` convention and receipt recorded. If E4 has no such integer rule or
  its measured fit changes by the declared twofold trigger, stop and repair
  the degree contract before any solver cell.
- **Arithmetic and solver pins.** All polynomial arithmetic is exact
  schoolbook arithmetic over canonical `F_p` residues with coefficients
  low-to-high, deterministic lexicographic variable order, and no floating
  point in the system or degree measurements. The protocol must bind the
  exact Python interpreter used for orchestration and exact release/commit
  identifiers for Magma, msolve, CryptoMiniSat, WDSat, the hybrid, and the
  interpolation solver. Those pins are currently absent and are hard blockers;
  a solver name without a version is not a runnable field.
- **Null and controls.** For every structured cell, generate a dense random
  system with identical variable/equation counts, degrees, coefficient law,
  variable order, and one planted solution from a domain-separated seed.
  Require (a) planted structured recovery, (b) planted-null recovery, (c) an
  independently generated known-answer section whose coefficient vector and
  fibre label are checked, (d) exhaustive soundness/completeness at the
  smallest cells, and (e) a group-law check for every reported relation.
  A control failure invalidates the cell; it is not negative evidence.
- **Metrics.** Record per solver and per structured/null cell: success,
  `d_reg` where defined, first-fall degree, equations and variables, Macaulay
  dimensions and field/bit operations, setup and construction time, solve
  time, verification and relation-collection time, total charged time, peak
  resident memory, stored bytes, and certificate size. For solvers without a
  Groebner degree, record `not_applicable` and retain their first-fall or
  equivalent search statistic; never substitute a guessed `d_reg`.
- **Censoring and seeds.** Fix a 12-hour per solver-line limit, 32 GiB peak
  memory limit, and 500 CPU-hour campaign ceiling. A timeout, OOM, crash, or
  missing artifact is a censored infrastructure outcome and is excluded from
  completed-cell comparisons. Use the existing base seeds
  `1311181015`, `1311181016`, and `1311181017`, expanded by the domain string
  `SNFS-E3-section:T-959:<bits>:<e>:<c>:<chi>:<r>:<cell>:<solver>:<arm>`;
  no stream may be reused across structured, null, planted, or rho arms.
- **Matched rho.** On each certified fibre and the same declared subgroup,
  run the existing Pollard-rho baseline with the same public point panel,
  exact group-operation accounting, and an independent rho seed stream. Rho
  is a finite baseline only; it does not turn section recovery into an ECDLP
  result.
- **Stopping, replay, and artifacts.** Stop after the fixed cell grid,
  controls, and receipts are complete, or at the stated resource ceiling;
  there is no optional extension after inspecting outcomes. Future artifacts
  must be written under
  `coordination/goals/GOAL-ECDLP-001/proposals/SNFS-E3-SECTION-SOLVER-20261010/repair-protocol.yaml`,
  `.../implementation/`, and
  `.../runs/<RUN-ID>/` containing `manifest.yaml`, `raw-result.json`,
  `stdout.log`, `stderr.log`, source hashes, input/surface certificates,
  seed registry, per-cell metrics, and `replay-receipt.yaml`. The replay
  must recompute all hashes, controls, degrees, and reported metrics from the
  frozen inputs.

## Dependency order

1. E1 supplies and independently checks the exact prescribed-fibre surface
   constructor, fibre, labels, subgroup, and section certificates.
2. E4 supplies the frozen height count and the deterministic `d` selection
   for each `(p,chi,r)` cell. No solver tuning or run planning precedes this.
3. SNFS-A3 supplies the solver versions, wrappers, output certificates, and
   field-arithmetic bindings.
4. The Coordinator reviews the repaired contract, including the matched null,
   planted and known-answer controls, limits, seeds, replay paths, and claim
   ceiling; only then can a new runnable experiment record be considered.

## Claim ceiling, disposition, and priority

The ceiling is finite structured-versus-random solver measurements on the
declared public surfaces, fibres, degrees, controls, and resource limits. The
result may report scoped differences in `d_reg`, first-fall behavior, success,
time, and memory. It supports no asymptotic statement, no cryptographic ECDLP
statement, no claim about deployed curves or keys, and no universal conclusion
from censored cells.

Disposition: keep `IDEA-20261009-581f5d` proposed with approval false. Do not
approve or dispatch until the repair is recorded as a separate successor
specification, E1/E4 dependencies are complete, solver pins and artifact
paths are bound, and the experiment readiness check reports `execution_state:
ready`. Relative priority is explicit: SNFS-G1 and SNFS-G4 remain ahead of
this section-solver lane; E3 must not displace either while either has a
ready, better-ranked bounded task. E3 can be reconsidered only after its
construction and degree dependencies are repaired.

**next_action:** Idea Generator/research-deep must write the repaired successor
protocol to `coordination/goals/GOAL-ECDLP-001/proposals/SNFS-E3-SECTION-SOLVER-20261010/repair-protocol.yaml`
and bind the constructor, E4 degree rule, solver pins, and controls; then the
Coordinator must run `python3 tools/newest_experiments.py --experiment <EXP-ID> --json`
and approve only if it reports `execution_state: ready`.
