# Research Record Templates

Copy these records into experiment-specific YAML files. IDs are immutable.

## Persistent research goal

```yaml
research_goal:
  id: GOAL-AREA-NNN
  title: null
  objective: null
  question_ids: []
  active_hypothesis_ids: []
  status: draft | active | paused | blocked | completed | cancelled
                                 | closed_at_budget
  runtime:
    provider: codex | none
    goal_id: null
  campaign_budget:
    maximum_batches: null
    total_wall_clock_seconds: null
    max_concurrent: 3
  current_batch_id: null
  dispatch_queue_path: null
  latest_verified_commit: null
  completion_criteria: []
  pause_conditions: []
  # OPTIONAL. The three-model quorum that once gated status -> completed is
  # suspended (AGENTS.md rule 13), so closure needs only a committed
  # Coordinator decision naming the criterion met. Omit this block entirely
  # unless you actually gathered attestations; if present, every field below
  # is validated and must describe a review that really happened.
  completion_quorum:
    quorum_satisfied: false      # true only in the same archive that sets
                                 # status: completed
    attestations:
      - role: reviewer | validator | red-team | coordinator
        requested_policy: null   # policy alias asked for
        resolved_model_id: null  # the model that ACTUALLY ran; distinctness is
                                 # judged on this field, not the alias
        reasoning_effort: null
        fallback_used: null
        independent_session: true
        reviewed_record_ids: []  # exact EV-/DEC-/GOAL- ids this vote rests on
        verdict: CONCUR | DISSENT
        rationale: null
        attested_at: null
  next_action: null
  owner: coordinator
  created_at: null
  updated_at: null
```

The goal record is an operational anchor, not evidence. Create and commit it
with its initial question and handoff before dispatch. Update it only through a
Coordinator ledger archive commit.

`completion_quorum` **no longer gates** `status: completed` — the three-model
quorum is suspended (AGENTS.md rule 13, restored via
`GOAL_CLOSURE_QUORUM_REQUIRED` in `tools/validate_ledger.py`). Closure now rests
on a committed Coordinator decision naming the criterion met and citing its
evidence.

The block stays optional and supported. When present it is still validated in
full: attestation shape, `independent_session: true`, cited record IDs that
resolve, and `quorum_satisfied: true` only on a goal that is actually
`completed`. A single `DISSENT` still blocks closure rather than being outvoted
— that is self-consistency, not the quorum. Never record an attestation you did
not obtain. Under the restored rule, three attestations resolving to the same
model are not a quorum however many distinct policy aliases they requested; the
validator compares `resolved_model_id`. Statuses that assert no success
(`paused`, `blocked`, `closed_at_budget`) never needed a quorum.

## Research question

```yaml
research_question:
  id: RQ-AREA-NNN
  title: null
  scope:
    curve_families: []
    field_types: []
    bit_sizes: []
    methods: []
  motivation: null
  decision_target: null
  constraints: []
  status: active
  owner: coordinator
```

## Hypothesis

```yaml
hypothesis:
  id: H-AREA-NNN
  question_id: RQ-AREA-NNN
  statement: null
  mechanism: null
  assumptions: []
  proof_search_map:              # required for proof-oriented hypotheses;
                                 # docs/inventor-protocol.md section 8
    bottleneck: null             # exact step whose removal changes theorem/cost
    baseline_embedding:
      parameter_slice: null      # exact old-method boundary, or not_applicable
      reproduction_check: null   # symbolic proof or frozen regression fixture
    observation_collision:
      observable: null           # invariant/certificate/quotient carrying claim
      distinct_preimage_search: null
    constructive_transforms:
      - transform: null          # boundary_lift | stronger_invariant |
                                 # telescoping_potential | specialization_pack |
                                 # representation_reduction | observable_fiber
        proposed_object: null
        predicted_gain: null
    quantifier_order: null       # explicit forall/exists statement and dependencies
    method_ceiling:
      strongest_certifiable_claim: null
      nearby_object_control: null
    proof_obligations:
      - claim: null
        responsibility: null     # baseline | feasibility | strictness | size |
                                 # runtime | memory | correctness |
                                 # success_probability | interface | scope
    not_applicable_reason: null
  rerandomization: null         # worst-to-average-case device, if any: the
                                # re-randomizing walk, its mixing-time
                                # justification (with citation), and how the
                                # solution is pulled back to the input instance
  asymptotic_claim:             # required when claiming a complexity improvement;
                                # see docs/target-result-profile.md
    problem: null               # central hard problem whose cost is improved
    prior_best: null            # e.g. p^{1/2} * (log p)^{O(1)}
    time_exponent: null         # claimed exponent in the security parameter
    memory_exponent: null       # claimed memory exponent
    hidden_cofactor: null       # overhead hiding in lower-order terms, e.g. a
                                # superpolynomial o(1) term vs a (log p)^{O(1)}
                                # cofactor
    claim_kind: exponent_improvement | cofactor_improvement | constant_factor
  heuristic_assumptions:        # numbered, formally stated; one entry per heuristic
    - id: HEUR-NNN
      formal_statement: null    # precise quantifiers and uniformity conditions
      random_model_justification: null
                                # why the quantity should behave like a uniform
                                # random object of its size
      supporting_results: []    # rigorous bound + classical distribution theorem
                                # combined in the justification, with citations
      validation_experiment_ids: []   # EXP-* ids testing this heuristic
      falsification_condition: null   # observation that would refute the heuristic
  structural_ingredients:       # external mathematics the mechanism converts
                                # into an algorithm; never fabricate citations
    - description: null
      citation: null
      role: null                # e.g. degree bound, distribution law, mixing time
  reduction_chain:
    core_problem: null          # problem the core result solves directly
    corollaries:
      - problem: null           # downstream problem reached immediately
        reduction_ref: null     # published polynomial-time reduction cited
        asymptotics_preserved: null
  predictions:
    - metric: null
      direction: higher | lower | different
      minimum_effect: null
  test_boundary:
    instances: []
    parameters: {}
    implementation: null
    budget: {}
  falsification_conditions: []
  interpretation_limits: []
  status: proposed
  proposed_by: idea-generator
```

The exemplar for these fields is the p^{1/3+o(1)} supersingular-isogeny
record in `inputs/P13-WESOLOWSKI-2026/`; `docs/target-result-profile.md`
describes the pattern they encode. A hypothesis with no complexity claim
leaves `asymptotic_claim` null. Each `HEUR-NNN` is part of the hypothesis
and is refuted only through its own `falsification_condition` — an
infrastructure failure or timeout is never evidence against it (AGENTS.md
rule 5).

`proof_search_map` operationalizes `KN-TECH-080`. A hypothesis that is purely
empirical may set `not_applicable_reason` and leave the other subfields null.
For proof-oriented work, nulling the whole map is incomplete: baseline
reproduction, observation collisions, quantifier order, and method ceilings
are deliberately cheap pre-compute audits.

## Experiment

```yaml
experiment:
  id: EXP-AREA-NNN
  hypothesis_id: H-AREA-NNN
  version: 1
  title: null
  status: draft
  objective: null
  inputs: {}
  controls: []
  independent_variables: []
  metrics:
    primary: []
    secondary: []
  heuristic_under_test: null    # HEUR-NNN id when this experiment validates an
                                # assumed heuristic rather than the main claim
  preregistered_prediction:     # fixed before execution; never tuned to the data
    quantity: null              # what is predicted, e.g. a smoothness CDF
    formula: null               # e.g. rho(u) ~ u^{-u(1+o(1))}, with u defined
    source: null                # theorem the prediction derives from, cited
  scale_relevance:
    tier: toy | medium | crypto | null # descriptive tested scale label
    justification: null         # tested parameters and any transfer or
                                # extrapolation assumptions
    correspondence: null        # sampling correspondence used to reach scale,
                                # if any (e.g. Deuring correspondence): the
                                # isometry claim and its citation; null means
                                # direct sampling
  tail_checks: []               # consistency checks beyond the bulk fit, e.g.
                                # comparing the smoothest observed sample against
                                # its predicted extreme-value probability
  replication:
    seeds: []
    independent_instances: 0
  # Budget floors. Historical contracts carry budgets far below anything the
  # hardware required -- 90 s cells and 255 s scripts (EXP-ICI-001), sized to a
  # ~280 s tool timeout rather than to the computation. Those caps censored
  # cells and forced checkpoint engines to be written around them
  # (src/h012c_block_m4ri.py). The tool cap is now 600 s
  # (.claude/settings.json), so size a budget to the WORK and let the stopping
  # rules end the run. Below these floors, state in the objective why:
  #   wall_clock_seconds_per_run >= 600     (one full tool window)
  #   maximum_memory_gb          >= 8       (DREG peaked at 7.16 GB)
  # Existing frozen contracts keep their budgets: they are immutable, and a
  # re-budgeted protocol is a NEW contract, not an edit to an approved one.
  budget:
    wall_clock_seconds_per_run: null
    total_cpu_hours: null
    maximum_memory_gb: null
    maximum_runs: null
    maximum_workers: null   # optional; omitted == 1 == the run process alone.
                            # Declaring N > 1 lets a LOCKED run create N-1
                            # descendants (RLIMIT_NPROC is raised from zero to a
                            # bound that is recorded in the approval lock and the
                            # manifest). Declare it only for work that has passed
                            # parallel.verify_determinism, and never above the
                            # core count: the run is charged for its whole
                            # process group's CPU against total_cpu_hours.
  stopping_rules: []
  invalidation_rules: []
  success_criterion: null
  falsification_criterion: null
  required_artifacts: []
  assigned_to: executor
  approved_by: null
```

## Concrete cost estimate

A rough, explicitly flagged costing of an asymptotic claim at standardized
parameter sets. One record per algorithm per hypothesis. These records
describe concrete cost and scope only: they are not evidence for or against
a heuristic, and optimistic numbers must never be presented as accurate
predictions.

```yaml
concrete_cost:
  id: COST-AREA-NNN
  hypothesis_id: H-AREA-NNN
  algorithm_ref: null           # construction being costed
  cost_unit: null               # e.g. F_{p^2}-operations
  bound_kind: lower_bound | upper_bound | heuristic_estimate
  parameter_sets:
    - name: null                # standardized set, e.g. SQIsign NIST-I
      security_parameter: null  # e.g. log2(p) ~ 256
      time_log2: null
      memory_log2: null
      prior_time_log2: null     # previous best method at the same set
      prior_memory_log2: null
  optimistic_assumptions: []    # every underestimating assumption, each flagged;
                                # a cost table without this list is invalid
  overestimating_factors: []    # e.g. a success-probability bound assumed tight
  parallelism: null             # scaling law with processor count
  time_memory_tradeoff: null    # interpolation between the high-memory and
                                # low-memory endpoint algorithms, with citation
                                # (e.g. van Oorschot-Wiener), incl. parallel form
  affected_scope: []            # constructions whose parameters this pressures
  safe_scope: []                # constructions out of range, with the reason
  implementation_ref: null      # referenced proof-of-concept, if any
  status: draft | reviewed | archived
```

## Evidence

```yaml
evidence:
  id: EV-AREA-NNN
  hypothesis_id: H-AREA-NNN
  experiment_ids: []
  run_ids: []
  type: empirical | theoretical | literature
  direction: supports | weakens | contradicts | neutral
  strength: anecdotal | preliminary | replicated | strong | inconclusive | contradictory
  claim_tier: toy | medium | crypto      # descriptive evidence-scale label
  certificate_refs: []                   # run certificates backing any claimed solve/relation
  proof_status: certificate | derivation | empirical_only | not_applicable
                                         # strongest checkable basis for the stated
                                         # direction (docs/claims-and-verification.md,
                                         # "Refutation artifacts")
  proof_refs: []                         # counterexample certificates / derivation-note
                                         # paths backing proof_status
  observations: []
  inference: null
  boundaries: []
  unresolved_confounds: []
  reviewed_by: coordinator
```

`claim_tier` and certificate semantics are defined in
`docs/claims-and-verification.md`. The tier describes the tested evidence;
records must state their parameters, scope, and transfer assumptions, and any
claimed solve must reference a `verified: true` certificate.

## Focused campaign claim

Use one record per conclusion boundary. A local identity, global construction,
relation collector, descent, and end-to-end complexity claim are separate
records.

```yaml
claim:
  id: CLM-AREA-NNN
  statement: null
  scope: null
  target_result: null
  observed_result: null
  verdict: reproduced | partially_reproduced | not_reproduced | not_attempted | open | invalidated
  independently_verified: false
  evidence_artifacts: []
  evidence_runs: []
  linked_experiments: []
  scope_deviations: []
  blockers: []
```

## Focused attention and stage budget

Queue v3 requires this record on every active or queued candidate. Stages are
ordered critical-path phases: wall-clock and CPU totals must reconcile with the
top-level estimate, and the maximum stage memory must fit its cap.

```yaml
attention_contract:
  decisive_evidence: null
  inconclusive_decision: null
  local_ambiguity_rule: null
  peripheral_exclusions: []
  rerank_trigger: null
resource_estimate:
  wall_clock_seconds: null
  cpu_hours: null
  maximum_memory_gb: null
  maximum_runs: null
  dominant_cost: null
  complexity_hypothesis: null
  sharding_plan: null
  stop_rule: null
  dominant_stage_id: null
  stages:
    - id: preparation
      purpose: null
      wall_clock_seconds: null
      cpu_hours: null
      maximum_memory_gb: null
      parallel_shards: 1
      dominant_operation: null
      stop_rule: null
```

## Focused run index

This is a compact campaign index, not a substitute for the immutable run
receipt with command, revision, environment, logs, and measurements.

```yaml
run:
  id: RUN-AREA-NNN
  experiment_id: EXP-AREA-NNN
  purpose: null
  status: planned | running | completed | failed | cancelled | invalid
  depends_on_runs: []
  artifacts: []
  failure_reason: null
```

## Correction

Corrections append both values. They do not mutate or delete the prior record.

```yaml
correction:
  id: CORR-YYYYMMDD-NNN
  recorded_at: null
  record_type: candidate | claim | run
  record_id: null
  field: null
  prior_value: null
  corrected_value: null
  reason: null
  evidence_artifacts: []
```

## Coordinator decision

```yaml
coordinator_decision:
  id: DEC-YYYYMMDD-NNN
  context: null
  decision: approve | revise | replicate | expand | support | weaken | reject_scoped | pause | supersede
  target_ids: []
  rationale: []
  evidence_refs: []
  limitations: []
  next_actions: []
  knowledge_promotion:          # required on every evidence-review decision
    promoted: []                # KN-* IDs created from this decision, or empty
    not_warranted: null         # if promoted is empty: why (e.g. strength below
                                # replicated, already covered by KN-*, no durable claim)
  decided_by: coordinator
  decided_at: null
```

`knowledge_promotion` makes corpus curation a checked step, not an
afterthought: a `support` or `reject_scoped` decision backed by evidence of
strength `replicated` or `strong` MUST either promote a finding
(`knowledge/findings/KN-FIND-NNN.md`, see `/curate-knowledge`) or state in
`not_warranted` why no durable entry results. Other decisions fill the field
too — usually `not_warranted` with a one-line reason.

## Agent handoff

```yaml
handoff:
  id: TASK-YYYYMMDD-NNN
  from: coordinator
  to: coordinator | idea-generator | executor | reviewer | validator | red-team
  objective: null
  uncertainty_reduced: null
  inputs: []
  constraints: []
  deliverables: []
  artifact_paths: []
  archived_by: TASK-YYYYMMDD-NNN
  inference:
    # Canonical policy ids; the pre-2.0 aliases still resolve for records
    # already committed. See docs/inference-backends.md.
    policy: coordinator-orchestration-code | coordinator-orchestration |
            research-deep | executor-implementation | executor-mechanical |
            review-adversarial | review-breakthrough
            # review-breakthrough only for a claimed break, a closure result,
            # or a contradiction between validated evidence records. It cannot
            # be degraded and refuses a backend that cannot reach `max`.
    reasoning_effort: null         # per-task calibration; null = the policy
                                   # default. Lower it for mechanical work;
                                   # a review policy may never go below its
                                   # floor, and the dispatcher enforces that.
    fallback_allowed: false        # permit the declared fallback / another backend
    degraded_allowed: false        # permit a RECORDED downgrade; needs an
                                   # inference_amendment naming the gap
    independent_session_required: false
  budget:
    wall_clock_seconds: null
    memory_gb: null
    maximum_runs: null
  completion_gate: []
  return_format: null
```

## Coordinator archive receipt

Use this only for a Coordinator task in the dynamic dispatch queue. A snapshot
archives producer artifacts before review; a ledger archive records review
reports and the official ledger transition after review.

```yaml
archive:
  kind: snapshot | ledger
  source_task_ids: []
  commit_sha: null
  parent_sha: null
  path_sha256: {}
  record_ids: []
```

`commit_sha` and `parent_sha` are filled only after the Coordinator has made
the isolated commit. Do not put a commit's own SHA into an artifact within that
same commit; the dispatch verifier binds the receipt to Git after the commit.
For a `ledger` archive, include the `EV-*` and `DEC-*` IDs in `record_ids` and
in the corresponding evidence and decision filenames.
