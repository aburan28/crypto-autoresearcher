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
  decided_by: coordinator
  decided_at: null
```

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
    policy: coordinator-ultra-code | research-sol-max | executor-terra | review-xhigh
    fallback_allowed: false
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
