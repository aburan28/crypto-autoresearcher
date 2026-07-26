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
  next_action: null
  owner: coordinator
  created_at: null
  updated_at: null
```

The goal record is an operational anchor, not evidence. Create and commit it
with its initial question and handoff before dispatch. Update it only through a
Coordinator ledger archive commit.

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
  replication:
    seeds: []
    independent_instances: 0
  budget:
    wall_clock_seconds_per_run: null
    total_cpu_hours: null
    maximum_memory_gb: null
    maximum_runs: null
  stopping_rules: []
  invalidation_rules: []
  success_criterion: null
  falsification_criterion: null
  required_artifacts: []
  assigned_to: executor
  approved_by: null
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
  claim_tier: toy | medium | crypto      # ceiling on what this record may assert
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
`docs/claims-and-verification.md`. The tier may never exceed what the
supporting runs' parameters allow, and any claimed solve must reference a
`verified: true` certificate.

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
            review-adversarial
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
