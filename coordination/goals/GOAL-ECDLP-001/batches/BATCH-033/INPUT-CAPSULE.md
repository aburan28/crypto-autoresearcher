# INPUT CAPSULE — TASK-20260802-213

Relay this file verbatim. It is the complete authorized repository input for an
Idea Generator without filesystem access.

## Objective

Starting only from ordinary prime-order ECDLP input G, alpha*G, either:

1. derive a typed, certificate-bearing method to obtain alpha^d*G or an
   equivalent nonlinear scalar generator in expected N^{beta+o(1)} time with
   beta below 1/2; or
2. prove a scoped generic-group barrier for such acquisition and name the
   precise non-generic interfaces that remain open.

No experiment, implementation, status change, closure, or breakthrough claim.

## Durable provenance

- BATCH-032 synthesis:
  1cf6ad5e115728416e977e56d715511490ef3700.
- TASK-206 snapshot:
  dbd03c4b26e48a5a093e6740588044c4f666aa4a.
- TASK-208 independent review snapshot:
  636f3975e3a66c4d76c5e2115ac0f835069a7459.
- Binding decisions: DEC-20260802-204 and DEC-20260802-205.

## Known Cheon baseline

Primary source:
https://www.iacr.org/archive/pkc2012/72930594/72930594.pdf

It describes Cheon's DLP with auxiliary input:

    input: G, alpha*G, alpha^d*G, where d divides r-1
    time: O(sqrt((r-1)/d) + sqrt(d))
    balanced d: N^{1/2+o(1)}
    balanced solve time: N^{1/4+o(1)}

It includes the same scalar-generator/two-stage structure and a
rho/distinguished-point low-memory implementation, citing Cheon's 2006 and
2010 work.

This is known prior art. APR-206 and its augmented-input variants are
rediscoveries. Do not generate, polish, implement, or claim novelty for the
augmented route. Use it only as an attributed downstream baseline.

## Reviewed acquisition boundary

Ordinary input supplies G and Q=alpha*G, not alpha^d*G.

Under ordinary generic-group operations, every constructed point has a formal
scalar label of the form a+b*alpha until equality of two encodings yields an
informative collision. BATCH-032 did not prove a complete lower bound, but it
established no sub-rho way to create a nonlinear label such as alpha^d.

The earlier quotient shortcut also failed: its quotient cardinality was N, not
N/M; searching only N/M projected states left about M compatible lifts and
success about 1/M. Apparent compression must include inverse-success cost.

Ordinary-ECDLP baseline:

    Pollard rho/kangaroo time exponent: 1/2
    memory exponent: 0
    current composed sota_delta_time: 0
    current composed sota_delta_memory: 0

The auxiliary relation is an extra assumption, so Cheon's 1/4 downstream
exponent does not change ordinary-ECDLP SOTA.

## Exact computational model

Define before proving anything:

- prime subgroup order and scalar field;
- opaque encodings and equality behavior;
- group addition, inversion, known-scalar multiplication, randomness, and
  preprocessing;
- whether advice, endomorphisms, pairings, extension fields, correspondences,
  or other oracles exist;
- cost and certificate semantics of every non-generic interface.

Use one orientation consistently: Q=alpha*G.

## Required proof route

### Ordinary generic-group branch

Decompose into single-purpose lemmas:

1. formal-label span;
2. distribution of unseen encodings;
3. informative-collision probability;
4. information obtained per collision;
5. time, memory, and success lower bound;
6. certificate correctness;
7. exact scope and excluded interfaces.

The affine-label observation is not itself the desired theorem. Prove every
step or mark the exact unresolved obligation.

### Escape branch

Any proposed escape must:

- name the precise operation breaking affine closure;
- type its source, target, and scalar action;
- produce and verify the nonlinear auxiliary relation;
- charge oracle construction, queries, preprocessing, memory, data,
  verification, and inverse-success cost;
- explain why it does not assume the target discrete log;
- yield a composed ordinary-input expected-time exponent below 1/2.

Candidate escape interfaces may include bilinear/non-generic maps,
order-changing correspondences, field-changing operations, or certified side
information. Listing an interface is not evidence that it works.

## Cost and Pareto rules

For general d=N^{delta+o(1)}, compose:

    ordinary total cost
      = acquisition cost
      + known Cheon auxiliary-input solve cost
      + certificate and verification cost.

Normalize primitive units and disclose soft-O terms, success probability,
parallelism, preprocessing, amortization, memory, and data/query requirements.

Every row records dominated_by and quantitative sota_delta. Unless a complete
sub-rho acquisition is derived, the ordinary row remains dominated by Pollard
rho/kangaroo with exponent deltas time=0 and memory=0 and a worse input-
assumption axis.

## Proof controls

Include:

1. a symbolic affine-label simulator;
2. an identical-shape random-label null;
3. an oracle-removal control for every non-generic interface;
4. a fiber-multiplicity/inverse-success accounting control;
5. a type and scalar-orientation audit;
6. a composition check restoring acquisition cost before any ordinary gain.

Run no experiment.

## Required artifacts

Return exactly five UTF-8 payloads and no commentary outside these markers:

    ---BEGIN ARTIFACT: ordinary-acquisition-analysis.md---
    [payload]
    ---END ARTIFACT: ordinary-acquisition-analysis.md---
    ---BEGIN ARTIFACT: proof-obligations.yaml---
    [payload]
    ---END ARTIFACT: proof-obligations.yaml---
    ---BEGIN ARTIFACT: escape-interfaces.yaml---
    [payload]
    ---END ARTIFACT: escape-interfaces.yaml---
    ---BEGIN ARTIFACT: pareto-frontier.yaml---
    [payload]
    ---END ARTIFACT: pareto-frontier.yaml---
    ---BEGIN ARTIFACT: provenance.yaml---
    [payload]
    ---END ARTIFACT: provenance.yaml---

The Coordinator writes them verbatim beneath
BATCH-033/tasks/TASK-20260802-213/.

## Completion outcomes

- Positive: a typed, certified sub-rho ordinary-input acquisition with complete
  composed Pareto accounting.
- Negative: a proof-grade scoped barrier plus named escape interfaces; not
  closure.
- Inconclusive: the exact missing lemma, model assumption, or cost inequality
  and cheapest bounded proof repair.

Every outcome is snapshotted and independently red-teamed before synthesis.

## Inference provenance

    requested_policy: research-deep
    runtime: codex_cli
    resolution_source: explicit_codex_role_session
    resolved_model_id: gpt-5.6-sol
    reasoning_effort: xhigh
    model_verified: false
    adapter_probe_status: not_run_backend_unavailable
    runtime_binding_verified: true
    fallback_allowed: false
    fallback_used: false
    degraded_allowed: false
    degraded_requirements: []
    independent_session_required: false
    experiment_run_budget: 0

Record actual session/backend/timestamps verbatim if supplied; otherwise use
not_reported. Any model, effort, or capability mismatch invalidates the attempt.
