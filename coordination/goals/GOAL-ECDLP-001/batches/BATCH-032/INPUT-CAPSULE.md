# INPUT CAPSULE — TASK-20260802-206

Relay this file verbatim to the Idea Generator. It is the complete authorized
repository input for a session without filesystem access.

## Objective

Produce a proof-grade boundary for certificate-bearing ECDLP reductions based
on fixed-field isogenies or lossy quotienting. Then identify one concrete
exponent-first escape mechanism that violates a named premise and still beats
matched Pollard rho after fiber multiplicity, inverse success probability,
certificates, preprocessing, memory, and data/query costs are charged.

Do not execute an experiment, implement code, change status, or claim closure.

## Durable provenance

- TASK-201 producer snapshot:
  `801524409339d0b4a49faed09f6c5dd2e83e4769`.
- Independent TASK-202 Red Team snapshot:
  `e4d7f710ea24570ac4e17193f95a9da32206d59a`.
- BATCH-031 synthesis commit:
  `bd9552672`, parent `e4d7f710e`.
- Binding synthesis decision: `DEC-20260802-202`.
- Batch-opening decision: `DEC-20260802-203`.

BATCH-031 performed no experiment and changed no official status.

## Reviewed fixed-field obstruction

Within the frozen boundary:

- `E/F_p` has a fixed prime-order subgroup of order `N`;
- maps are prime-to-`N` isogenies over the fixed field;
- target families are anomalous, lower-embedding-degree MOV/Frey–Ruck, or
  prime-field subfield-descent-friendly.

The independently surviving constraint is:

1. Isogenous elliptic curves over `F_p` have the same trace and therefore the
   same number of `F_p`-rational points.
2. A prime-to-`N` isogeny is an isomorphism on the relevant order-`N`
   subgroup; it does not manufacture a different subgroup order.
3. The embedding degree is `k=ord_N(p)`. Holding `p` and `N` fixed holds `k`
   fixed, so movement inside the isogeny class cannot lower it.
4. A prime field has no proper subfield. Movement among curves over that same
   prime field does not create prime-field subfield structure.
5. Consequently, merely moving inside this fixed class cannot manufacture the
   named weakness.

This is a bounded admission barrier, not closure of isogeny transfer or ECDLP.
It does not cover order-changing correspondences, field-changing reductions,
extension-field constructions, or maps carrying independently recoverable side
information.

## Exact quotient correction

`IDEA-20260802-201-01` is falsified as written.

For its stated construction, the ambient set has `N*M` pairs and each stated
equivalence class contains `M` representatives. Therefore:

```text
|(G × [M]) / ~| = (N*M)/M = N,
```

not `N/M`.

If a projected search nevertheless explores only `N/M` effective states while
the omitted fiber has multiplicity `M`, a random target has success probability
about:

```text
p_success ≈ 1/M.
```

Thus an apparent per-attempt search cost near `sqrt(N/M)` must be multiplied by
about `M` attempts unless a proof-backed, independently recoverable fiber label
or structural bias removes that loss:

```text
total expected cost = per-attempt cost / p_success.
```

The Red Team expressed the corrected exponent in the proposal's notation as:

```text
gamma + (1 + delta)/2.
```

Do not assume this formula. Reconstruct it, define `gamma`, `delta`, `M`, and
the asymptotic regime, and check every algebraic step.

Also repair:

- scalar orientation: use one convention consistently, e.g. `Q=[x]P`;
- type correctness of every map, quotient, pullback, and certificate;
- comparable cost units;
- complete time, memory, and data/query Pareto accounting.

## Required proof architecture

Decompose the analysis into single-purpose statements:

1. fixed-field trace/order invariance;
2. embedding-degree invariance;
3. prime-field subfield limitation;
4. quotient cardinality or state-count lemma;
5. fiber multiplicity and success-probability lemma;
6. per-attempt cost lemma;
7. total expected-cost assembly;
8. certificate correctness and scalar recovery;
9. exact scope and escape-premise statement.

The final theorem or proposition may only assemble these statements. Keep
`per-attempt cost × inverse success probability` explicit.

Every heuristic must be numbered, formally stated, and given a falsification
condition. Do not present a heuristic as a theorem.

## Exponent-first escape requirement

Search for one mechanism that violates a named barrier premise, such as:

- changing the relevant subgroup order through a justified correspondence;
- changing the field while accounting for extension/restriction costs;
- providing independently recoverable fiber information without paying its
  full multiplicity;
- another explicitly stated structural premise change.

Naming a premise violation is not evidence that the mechanism works.

A candidate survives only if it supplies:

- typed source and target objects;
- a certificate-bearing reduction and scalar recovery;
- exact state cardinalities and fiber sizes;
- success probability and stopping rule;
- total expected time exponent below `1/2`;
- memory and data/query exponents;
- preprocessing and amortization boundaries;
- comparison with matched Pollard rho;
- `dominated_by` after checking every Pareto row;
- quantitative `sota_delta`;
- mechanism, predictions, test boundary, and falsification criteria.

If none survives, return the scoped barrier and explicit open premise-changing
routes. Do not call the lane closed.

## Controls

For each apparent compression or speedup, include:

1. a cardinality-preserving null construction of identical shape;
2. a fiber-label permutation or destruction control;
3. a limit test as `M` grows;
4. an accounting control that restores inverse-success cost;
5. a scalar-orientation/type-check control.

A signal that survives only because multiplicity, failure probability, or unit
conversion is omitted is an artifact.

## Required artifacts

Return exactly five complete UTF-8 payloads with no commentary outside markers:

```text
---BEGIN ARTIFACT: barrier-and-escape-analysis.md---
[payload]
---END ARTIFACT: barrier-and-escape-analysis.md---
---BEGIN ARTIFACT: proof-obligations.yaml---
[payload]
---END ARTIFACT: proof-obligations.yaml---
---BEGIN ARTIFACT: pareto-frontier.yaml---
[payload]
---END ARTIFACT: pareto-frontier.yaml---
---BEGIN ARTIFACT: successor-proposal.yaml---
[payload, or explicit no_surviving_candidate record]
---END ARTIFACT: successor-proposal.yaml---
---BEGIN ARTIFACT: provenance.yaml---
[payload]
---END ARTIFACT: provenance.yaml---
```

The Coordinator writes them verbatim beneath:

`coordination/goals/GOAL-ECDLP-001/batches/BATCH-032/tasks/TASK-20260802-206/`

## Inference provenance

```yaml
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
```

Record actual session/backend/timestamps verbatim if supplied; otherwise use
`not_reported`. Any model, effort, or role-capability mismatch invalidates the
attempt.
