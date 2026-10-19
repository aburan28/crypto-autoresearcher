# Prym-assisted prime-field relation generation

**Status: owner-requested intake and design follow-up; no new scientific run,
approved protocol, novelty claim, or measured advantage.**

Tracker: [GitHub issue #2414](https://github.com/aburan28/crypto-autoresearcher/issues/2414).
The machine-readable companion is [tracking.json](tracking.json); it is not a
canonical ledger record or an execution queue. The named missing operation is
tracked in [the problem record](../../problems/prym-assisted-source-labelled-router.md).
The [diagram](diagram.svg) and [PDF](report.pdf) are derived communication;
[render_report.py](render_report.py) rebuilds them from this report and tracking.json.

## Question and hypothesis

Can a public Prym constraint, extra correspondence, or compact adaptive router
improve source-labelled relation generation for prime-field ECDLP over a
matched, verified index-calculus pipeline?

The proposed hypothesis is that one explicit representation/operation pair can
reduce complete charged work S while retaining independent projected rank and
blind target descent. The mechanism is **not yet supplied**. A cover, a
genus-two realization, a split Prym, or cancellation alone is not that mechanism.
This is a refinement of existing work, with novelty unverified, not a new
independently specified hypothesis. No historical contract is reopened here.

The intended quantifier order is: freeze a public construction and admissible
source family first; then draw matched instances, seeds and blind targets;
apply the same algorithm to every admitted target. Any claimed applicability
fraction must be measured or proved, with failed constructions charged. The
construction cannot depend on a target secret or on observed success.

## Existing work and semantic deduplication

The intake base is main commit
`d0f70c0a0905a5d4d2fc7c082b6dd85e43094026`.

- [IDEA-20260909-4c5ee9](../../ledger/proposals/IDEA-20260909-4c5ee9.yaml)
  already proposes residual/nonlinear objects and Prym companion cancellation
  for RQ-ECDLP-002, GOAL-ECDLP-001 and GOAL-ICEX-001. Its status is unchanged.
- [ECDLP-IDEA-002](../../ideas/ECDLP-IDEA-002_split_jacobian_projected_smoothness_hypothesis.md)
  is the existing projected-smoothness proposal, not a fresh idea to duplicate.
- [P1546](../../ideas/artifacts/ECDLP-IDEA-002/p1546_projected_smoothness_counting_gate.md)
  records a scoped counting argument for fixed bounded-degree algebraic
  reduction branches, bounded cover multiplicity and explicitly enumerated
  kernel dithers. It also records the tuple-first unknown-log trap and the
  post-hoc kernel-residual tautology. Its stated successor needs a compact
  growing-degree or adaptive target-local router and a source inverse. This
  intake cites that record; it does not independently re-review its theorem
  claims, broaden its scope, or authorize its frozen contract.
- [PO-transfer-003](../../inputs/refs/experiments/ecdlp_isogeny/po_transfer_003_result.md)
  records native bielliptic principal-divisor relations and historical toy
  recovery with unfavorable costs. Those are imported observations, not a
  measured baseline for a new experiment. Its stated exclusions leave other
  function families and Prym-assisted filters open within their own gates.
- [ECDLP-IDEA-061](../../ideas/rejected/ECDLP-IDEA-061_recillas_saturated_prym_realization_hypothesis.md)
  records a semantic merge of Recillas/principal-polarization realization with
  the earlier saturated-Prym lane. A new geometric name alone is insufficient.

The generated proposal/hypothesis indexes and the index-calculus frontier map
were inspected at the intake base. Relevant frontier rows include
KR-IC-a4dd54 (full-Jacobian complexity), KR-IC-5ea2f8 (cover descent), and
KR-IC-5931ee (prime-field relation costs). The KB MCP search tool was not
available in this session; source-file retrieval and generated indexes were
used instead. Retrieval absence is not evidence of novelty or nonexistence.

## Separate routes and obligations

Work over F_p with p odd, ordinary E, G=<P> of prime order r, and Q=[k]P.
Every future fixture must bind p, E, r, cofactor, P, Q, full curve UID, field
encoding and factor-base identity before execution. None is admitted here.

For a degree-d cover pi:D->E, let i=pi^* and n=pi_*. The familiar identity
n i=[d] makes i injective on G when gcd(d,r)=1. For a double cover with deck
involution sigma, (1-sigma^*)i=0, and sigma^* acts as negation on the Prym.
These algebraic facts delimit the proposed interfaces; they are not a new
reviewed result, implementation certificate, or performance observation.

**Route A: direct homomorphic transfer into the Prym A.** Coprime rational
Frobenius characteristic polynomials F_E and F_A exclude an algebraic group
homomorphism E->A over the stated field. Shared factors establish compatibility
of isogeny classes, not an efficient evaluator or subgroup certificate. Any
extension changes the working field and must be explicitly charged. The
natural anti-invariant projection of i(G) is zero regardless of this screen.

**Route B: auxiliary Prym constraints in the full Jacobian.** Keep the elliptic
component. Auxiliary cancellation can be used in a relation-construction
algorithm even when Route A fails. A Frobenius mismatch does not reject this
route. A combination with zero Prym component still has an elliptic component
whose logarithm need not be known. The missing operation must return public
source labels or a valid target equation, not merely an elliptic point.

Potential geometric tools remain tracked separately: explicit genus-two
Jacobians isogenous to a Prym, extra endomorphisms beyond deck negation, and
split auxiliary factors. For each, require an actual construction on the
admitted field/instance, map degree and exceptions, action on G, recovery,
and charged evaluation. Fast scalar multiplication is not unknown-scalar
recovery; a solver for an unrelated auxiliary factor is not a target solver.

## Public witness interface

A proposed known-source relation constructor receives public curve/cover data,
the frozen atoms D_j and their distinct norm images F_j, a public scalar a,
and R=[a]P. It returns coefficients e_j and an independently checkable divisor
witness for i(R)=sum(e_j D_j)+K with n(K)=0, hence
[d*a]P=sum(e_j F_j). No factor-base logarithm or target secret may be an input.
The blind-descent interface receives Q+[t]P and uses the identical frozen base
and branch policy; recovery verifies [k]P=Q on E independently.

Count useful rank modulo r after removing zero columns, duplicate norm images,
sign-equivalent columns and tautological rows. A post-hoc definition of K is
not a constructor. Enumerating smooth tuples whose norm sum has an unknown
source scalar fails the known-source interface. Additional endomorphisms must
preserve source labels and have all orbit/canonicalization costs included.

## Next discriminating design step

Write one explicit router or batched relation-constructor candidate with a
public input/output interface, source-return algorithm and circuit/branch
complexity. Before implementation, compare it to the exact P1546 hypotheses:
fixed algebraic branches, enumerated dithers, implicit output expansion,
degree/genus growth and target-local advice. Exhibit the operation outside
that scope, or record its absence. This is the next design task, not an
instruction to launch the historical IDEA-002 protocol.

Four cheap proof-search audits apply before a scientific trial:

1. Baseline reproduction: bind the exact current verified IC implementation,
   protocol, S and immutable artifacts; presently unbound and unmeasured.
2. Observation collision: auxiliary cancellation also occurs in a split-product
   control with an unchanged elliptic DLP; require discrimination beyond that
   observable. This is a conceptual control, not an admitted fixture.
3. Quantifier order: construction/base/selection precede sampled targets;
   identify every instance-, seed- and target-dependent choice.
4. Method ceiling: show the proposed operation is not deck negation, scalar
   push-pull, a branch scan, duplicate norm columns, or a verifier posing as a
   locator. P1546 is a scoped reference, not universal impossibility.

Outcomes: a concrete distinct operation proceeds to runnable design; a scope
collision records a bounded duplicate and the missing operation; an unresolved
proof remains open; missing software/access is an implementation/access gap.
None changes a hypothesis status or establishes security.

## Prospective controlled comparison

No sample count, seed grid, admitted fixture, executable collector or timing
protocol is frozen here. Before approval, a successor must bind fixed samples,
seeds, complete workloads, invalidation rules, machine limits, stopping rules,
hashes, archive ownership and native admission. The run skill is the scientific
execution entry point. This tracking record supplies no execution authority.

Controls to freeze together: A/A; the exact current IC baseline; direct E
relations; same-field coordinate-isomorphism; transported rather than reselected
factor bases; matched random companions; split-product; planted correctness;
wrong-sign/malformed witnesses; and a known-false source-label control. Keep
target secrets in a separate verifier. Null/control gates precede interpretation.

Record all attempts, valid rows, distinct projected support, rank modulo r,
rank gained per charged operation, blind-descent success, and independent
source-equation checks. Charge cover search/construction, isogeny evaluation,
base setup, failures and rejected tuples, relation generation, normalization,
norm/witness checks, rank tests, sparse linear algebra, individual descent,
recovery and verification. Record peak bytes, raw operation units, hardware,
success probability and uncertainty. Report cold-start and genuinely amortized
costs separately, binding the actual number of targets that reuse setup.

Under the current owner rule, a verified measured reduction in complete S
against the matched current IC baseline is progress. Delta S and S_base/S_new
are prospective metrics, not values measured here. Report the gap to matched
rho, and to Bernstein-Lange where setup is excluded, as distance remaining.
Sub-rho recovery is not an incremental pass/fail requirement. New quantitative
claims require progress-fidelity records and independent verification.

## Evidence, literature and scope

Internal citations above have provenance internal, retrieved at the intake
base by the Codex authoring session. Historical result labels are attributed
to their records, not independently promoted. Literature pointers retrieved
in the preceding conversation by this session are:

- Enolski-Fedorov, https://arxiv.org/abs/1411.6143 : certain Prym/genus-two
  isogeny constructions, not a generic prime-field ECDLP improvement.
- Dupuy-Kedlaya-Roe-Vincent, https://math.mit.edu/~roed/writings/research/avfq.pdf :
  finite-field Frobenius/isogeny theory, not an efficient-map certificate.
- Duursma-Gaudry-Morain, https://researchportal.ip-paris.fr/en/publications/speeding-up-the-discrete-log-computation-on-curves-with-automorph/ :
  automorphism-assisted DLP computation, not an automatically effective Prym action.

These pointers are not new repository literature certifications. The quote
"32 Prym covers" has no identified source/catalog here and is not evidence.
The previous chat's F_43 diagnostic is not a native admitted run and is not
imported as canonical evidence or a benchmark. No new scientific run occurred.

dominated_by: n/a (no algorithmic result claimed).
sota_delta: no measured attack or stage improvement; design/tracking only.
All quantitative outcomes remain unmeasured. No ordinary prime-field ECDLP
speedup, weak deployed curve, asymptotic exponent or impossibility is asserted.

## Graph and record maintenance

The new local graph distinguishes the known transfer identities, the blocked
natural Prym projection and the proposed relation-router edge. Its labels are
design/derived-interface labels, not verified empirical edges. The
index-calculus frontier rows and tracked IDEA-002/P1546 paths were checked;
the IDEA-002 artifact directory contains the P1546 Markdown gate and no existing
graph to refresh for this intake. No canonical graph finding changes because
this intake adds no reviewed evidence. Existing evidence, statuses and queues
are retained.

The next scientific owner is the Coordinator. Issue #2414 and tracking.json
record dependencies and acceptance conditions; completing the intake or merging
its PR does not resolve the router problem or promote any scientific state.
