# Prospective correction readiness for EXP-ECDLP-1b1b99

## Outcome

The assigned output is a complete proposed effective prospective contract, but
the experiment is not executable-ready, scientifically ready, approved, or
authorized. The correction preserves the original finite panel, seeds,
thresholds, repetition rule, and claim boundary while resolving the
mathematical class-multiplicity error and specifying the missing cost,
selection, custody, control, admission, authorization, and artifact rules.

This task performed drafting only. It created no implementation, fixture,
certificate, control result, timing result, key, signature, lock, nonce, RUN,
Executor handoff, approval, status transition, queue edit, release, commit, or
scientific conclusion.

The proposed contract keeps:

- approved_by: null
- execution_authorized: false
- evidence_eligible: false
- novelty_status: unverified

A later committed Coordinator readiness decision is required before the
correction can take precedence for prospective work.

Protocol approval and execution authorization are separate transitions. Under
the standing user authorization, the Coordinator may approve a complete frozen
protocol before its implementation exists. Such approval would still leave
execution_authorized false until the implementation, independent review,
runtime, verifier, RUN, and one-run authorization gates all hold.

## Source and read attestation

The drafting session could not use command tools and did not directly open or
hash repository files. The parent control plane read all bound sources in full,
verified the stated bytes, and relayed authoritative excerpts. This note
therefore attests to parent-relayed inputs and does not claim an independent
file read, hash computation, model probe, or experiment run.

The relayed and parent-verified bindings were:

| Source | Commit or snapshot | SHA-256 | Relayed use |
|---|---|---|---|
| ledger/handoffs/TASK-20260907-fe3f53.yaml | 8b80fff14048ce9ecc284debccda5255feb2efb4 | 804dc2665d35b04103838ae0f081d0cab2ef206e82ebeac8571b7d7110313e60 | exact drafting authority and scope |
| ledger/decisions/DEC-20260907-23c71a.yaml | 8b80fff14048ce9ecc284debccda5255feb2efb4 | 7195128ac82e68fa44bbfd78452a1783c0831b922d32cba561225c854fcf3082 | accepted correction requirements |
| experiments/EXP-ECDLP-1b1b99/specification.yaml | bound source | b331940a2f5215058d84845f953365c39dac78b4a0d4894604e90b06bc2f3fff | complete predecessor field extraction |
| experiments/EXP-ECDLP-1b1b99/approvals/DEC-20260906-f73475.yaml | snapshot 1a7917e234dd599e9fec58fe93299652a5c019ce | e4d8106508ebe5f7c89a637b72df38debd65b95cdcbd6760f89b408d5ad31fed | historical bounded-calibration approval boundary |
| coordination/experiment-reserve/BATCH-45b4d5/reviews/TASK-20260907-c96324/review.yaml | 37156a4789493224596c6e01de00d5fd6ea658b0 | 9231abde92f8493d1b61bf57cc036ccbc348b31c8094e445b9d3f6a373c75df9 | implementation and admission defects |
| coordination/experiment-reserve/BATCH-45b4d5/reviews/TASK-20260907-167cea/review.yaml | 37156a4789493224596c6e01de00d5fd6ea658b0 | 548859ff820de7c6969ec820abc8ac17112480fd2c91344a98bb85757bdf60c4 | blind mathematical correction |
| coordination/experiment-reserve/BATCH-45b4d5/reviews/TASK-20260907-167cea/derivation.md | 37156a4789493224596c6e01de00d5fd6ea658b0 | 454569e92bf34216878b618c34c4a64f4499b6b77a3ce005ac70202895e02046 | blind beta and multiplicity derivation |

Claim epoch 1 was relayed as published at
217a3108893e75deb81607da449a591d640ad7cc, owned by
coordinator-reserve-admission-20260907/session01a07d92-d309-7620-9947-a358afc60883.

The mathematical citations retain the reviewers' provenance:

- Shumow, *Isogenies of Elliptic Curves: A Computational Approach* (2009),
  Theorem 2.23, Remark 2.24, and Section 3,
  https://eprint.iacr.org/2009/522.pdf; provenance: retrieved by
  TASK-20260907-167cea.
- Kohel, *Endomorphism rings of elliptic curves over finite fields* (1996),
  Section 4.2, Propositions 21 and 23,
  https://www.i2m.univ-amu.fr/perso/david.kohel/pub/thesis.pdf; provenance:
  retrieved by TASK-20260907-167cea.

This drafting session did not retrieve those sources independently.

## Corrections incorporated

The proposed effective contract now distinguishes four canonically labeled
order-three kernels and quotient-map endpoints from the two
Fp-isomorphism classes they represent. Each class has exactly two labels. The
class IDs are assigned only after explicit isomorphism certificates, with C0
defined as the class containing the smallest canonical kernel label. Every
nonrepresentative endpoint requires a within-pair isomorphism and inverse.

The map convention is explicit. If v is a raw Velu map and alpha normalizes its
codomain, then phi = alpha o v and psi = dual(v) o alpha^-1. Under coordinate
transport rho_u, the required maps are phi_u = rho_u o phi and
psi_u = psi o rho_u^-1. The auxiliary map beta = phi o iota o psi acts as
[3 lambda] and satisfies beta^2 = [-9].

The cost tensor now materializes source fixture, kernel endpoint, derived target
class, coordinate, seed, q, arm, timing block, repetition, component, and stage.
Every raw charged item has exactly one rational allocation record in each
applicable strategy view. Integer-nanosecond remainders are distributed by
canonical target order. Shared source, fixture, kernel, class, coordinate,
selection, setup, warmup, evaluation, verification, control, and publication
costs have explicit treatment. Actual campaign cost, normalized fixed-q batch
cost, and modeled amortization are separate reports.

The primary ratio is scalar charged total divided by transport charged total.
Within each target class, the two endpoint totals have equal weight and are
summed before division. A mean of endpoint ratios is secondary only. Each fixed
q report is a separate cold-total view; q reports cannot be summed. Because all
six q=256 selection trials are charged, the q=1 report is a
protocol-defined cold-total scenario rather than ordinary one-query latency.

The baseline selection rule is now fixed before data:

- Nine strata are the Cartesian product of three declared prime intervals and
  three coordinate values.
- Each stratum pools both accepted fixtures and all four labeled endpoints,
  giving eight endpoints.
- All six scalar candidates are scored at seed 606101 and q=256.
- The score is the sum of equally weighted charged scalar endpoint costs in
  integer CPU nanoseconds over all eight endpoints, including every candidate
  setup, table, warmup resource charge, block, repeat, and verification.
  Dividing each candidate score by the same transport total would give the
  same argmin; endpoint-wise ratios are never averaged.
- Exact ties choose the lowest numeric arm ID.
- The selected arm is persisted before any seed-606103 work and is frozen
  across all q values, both seeds, and every endpoint in the stratum.
- Seed 606103 uses the frozen arm even if its separately reported oracle
  minimum is lower.

The runner is specified as a concrete fixed pipeline. Arbitrary
prepare/audit/measure callbacks cannot determine validity. The hard reducer
treats empty collections, missing booleans, explicit false controls, missing
rows, failed replay, failed allocations, or missing artifacts as nonvalid.

The evaluator receives a closed public-only type. Fixture, generator, scalar,
kernel, class, expected-answer, certificate, RNG-state, and join labels remain
with the verifier. Raw evaluator output is committed before the private join.
The label-permutation control changes the private join and reaggregates the same
raw costs; it must leave class summaries bit-for-bit invariant.

The RNG is a persistent SHA-256 state machine keyed by the complete serialized
tuple. Every digest, including rejected samples, advances the counter. Query
helpers cannot reset state or accept caller-supplied coefficients. Coordinate
variants transport the same samples from the original unscaled floor, and the
4096 generator-search cap counts x values rather than affine points.

Certificate admission now cross-binds the exact trace, order, Frobenius
discriminant, conductor valuation, subgroup factor, full rational 3-torsion,
four kernels, maps, exact duals, rational edge counts, two multiplicity-two
classes, explicit isomorphisms, generators, eigenvalue sign, and m. Accepted
and rejected candidates and partial search work are always retained.

The full main timing matrix, top-level control matrix, identity-transport
matrix, typed source/target composition controls, coordinate commutation,
level comparison, wrong-factor, wrong-sign, malformed-certificate, replay, and
real label-permutation controls are specified. Missing or below-resolution
primary data is inconclusive.

The authorization design uses one canonical payload and a detached signature.
The payload binds source, plan, amendment, review, implementation, runner,
verifier, runtime, dependency, Executor handoff, RUN, output path, resources,
seeds, matrix, replay implementation, and a one-run nonce. The signature and
lock hash are outside the payload, so there is no mutual hash cycle. Malformed
authorization produces a typed refusal rather than an unhandled key error.

Progressive custody begins only after signature verification and exclusive
nonce claim. Stage receipts, accepted and rejected fixture work, controls,
costs, block rows, stdout, and stderr are persisted during execution. Final
publication requires file fsync, parent-directory fsync, and an atomic rename.
A failure preserves the partial directory.

## Fixed arithmetic and cardinality audit

These are static design checks, not experimental observations. Fourteen fixed
cases were reasoned through once; there were no reruns and no scientific
fixtures, controls, or timings.

| Check | Arithmetic or predicate | Result |
|---|---|---|
| A1 | 3 intervals times 2 accepted fixtures | 6 source fixtures |
| A2 | 6 fixtures times 4 kernel labels | 24 labeled endpoints |
| A3 | 6 fixtures times 2 target classes | 12 target-class instances |
| A4 | 6 times 2 classes times 3 coordinates | 36 primary confirmation cells |
| A5 | 36 primary cells times 4 q values | 144 class-coordinate-q panel cells |
| A6 | 6 times 4 times 3 times 2 times 4 times 7 | 4032 main endpoint-arm workloads |
| A7 | 4032 workloads times 7 blocks | 28224 main timing block rows |
| A8 | 3 intervals times 3 coordinates | 9 baseline strata |
| A9 | 9 strata times 8 endpoints times 6 scalar arms | 432 selection workloads |
| A10 | 432 selection workloads times 7 blocks | 3024 selection block rows |
| A11 | 6 times 3 times 2 times 4 times 2 times 7 | 2016 top-control block rows and 2016 identity-control block rows |
| A12 | 6 times 4 times 3 times 2 endpoints times 129 samples | 18576 dual-composition assertions |
| A13 | (3 - (-1)) / (4 / 2) | 2 target isomorphism classes |
| A14 | scalar [1,1,9,9], transport [1,1,3,3] | ratio of totals 20/8 = 2.5; mean of ratios = 2.0 |

The required timed-row total after adding the two separately charged control
matrices is 28224 + 2016 + 2016 = 32256. This is a prospective cardinality,
not executed work.

The fixed beta illustration also checks:

- 3 times 44 modulo 149 is 132.
- 132 squared modulo 149 is 140, equal to -9 modulo 149.
- 44 squared modulo 149 is 148, so the missing factor of 3 fails the
  beta-squared identity.
- 17 squared modulo 149 is also 140, but 17 is not 132 modulo 149; on a
  nonzero point of prime order 149, [17] and [132] therefore differ.
- Postcomposing the forward map with coordinate isomorphism rho_7 requires
  postcomposing the dual in the opposite direction with rho_7^-1.

Allocation denominators also reconcile structurally: twelve equal
endpoint-coordinate shares sum to one for a fixture-level cost; six equal
endpoint-coordinate shares sum to one for a class-level cost; and eight equal
endpoint shares sum to one for a stratum-global selection overhead. The
contract gives canonical one-nanosecond remainder handling so integer totals
also reconcile exactly.

No timing was attached to these reasoning cases because this Coordinator tool
surface exposes no permitted command or process timer. The observed activity
within the bounded drafting task was 14 static cases, 0 reruns, 0 command
executions, 0 scientific fixtures, 0 scientific controls, 0 scientific timing
work, and one worker. It stayed below the 40-case bound; no claim is made for an
unobserved CPU or wall measurement.

## New neutral choices disclosed before measurement

The predecessor and decision left several implementation-neutral choices for
this correction. This draft chooses and freezes them as follows:

1. Baseline strata are prime interval by coordinate, pooling eight endpoints.
   This avoids choosing a baseline separately for either target class or any
   single kernel label.
2. Candidate scores use exact recorded integer process-group CPU nanoseconds;
   exact ties use lowest numeric arm ID.
3. The private control-scalar stream uses existing seed 606103, with 128
   scalars per endpoint. Coordinate variants transport this same base set.
4. Class IDs are derived from explicit Fp-isomorphism certificates; C0 contains
   the smallest kernel label.
5. Stability uses the existing 1.00 and 1.20 boundaries with seven
   leave-one-block-out reductions. It adds no numeric threshold.
6. The top and identity controls use the same three coordinates, two seeds,
   four q values, and seven blocks as the finite panel, with two arms each.
7. Shared integer costs use canonical-order remainder distribution rather than
   floating allocation.
8. A fixed-q normalized report charges setup once and reconciles independently;
   the four q views are alternatives and are never added together.
9. The manifest omits a self-hash; the later immutable archive receipt hashes
   the finalized manifest and run-directory binding.

These choices must be reviewed before activation. They cannot be changed after
measurement without an additive amendment.

## Unresolved admission conditions

The design contract is complete enough to tell an implementation exactly when
to refuse, but current execution readiness is false for four concrete reasons.

First, arm 7 has no real pinned external library definition. The missing
dependency is DEP-CM-PINNED-SCALAR-001: package or repository identity, exact
version or commit, source or distribution hash, callable and scalar semantics,
build flags and backend, dependency-lock entry, and evidence that its call path
is distinct from local Curve.mul. The reviewed alias currently duplicates the
local affine routine. Renaming or wrapping it does not create a second
implementation.

Second, DEP-CM-TRUSTED-VERIFIER-001 is unresolved. A later Coordinator decision
must bind the detached-signature algorithm, public key or certificate bytes,
repository path, immutable commit, SHA-256, owner, and rotation policy. The
caller cannot supply the verifier.

Third, the concrete fixed runner, hard reducer, persistent RNG, typed custody
boundary, full matrix, CostLedger path, process-group monitor, progressive
artifact writer, and detached authorization verifier have not been implemented
or archived. The existing arbitrary-callback path is not admissible.

Fourth, no future Executor runtime, corrected implementation archive,
independent implementation review, amendment if needed, RUN, one-run nonce,
signature, lock, or frozen Executor handoff exists. The future runtime remains
null because this drafting task did not bind one. Any future runtime must obey
the non-Bedrock rule.

Each condition is operational. None is mathematical or scientific evidence.

## Exact next action and archive handoff

The parent control plane should now:

1. Parse the YAML and inspect the Markdown without executing any scientific
   code.
2. Verify that only the two assigned correction files changed.
3. Compute SHA-256 hashes for both final files and bind them in
   TASK-20260907-0639f3.
4. Review the field-precedence map, nine-stratum baseline choice, allocation
   equations, matrix cardinalities, hard reducer, and unresolved dependencies.
5. If the draft is accepted, create a separate committed Coordinator readiness
   decision. Under standing authorization that decision may approve the
   complete frozen protocol before implementation exists. It must keep
   execution_authorized false until the implementation, independent review,
   runtime, verifier, RUN, and one-run authorization gates actually hold.

Final file hashes are intentionally returned by the parent control plane after
readback. A file cannot carry its own final SHA-256 without creating a
self-reference, and this drafting session cannot use the command tool needed
for an independent filesystem hash.
