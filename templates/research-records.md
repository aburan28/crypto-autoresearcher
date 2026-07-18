# Research Record Templates

Copy these records into experiment-specific YAML files. IDs are immutable.

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
  observations: []
  inference: null
  boundaries: []
  unresolved_confounds: []
  reviewed_by: coordinator
```

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
  decided_by: coordinator
  decided_at: null
```

## Agent handoff

```yaml
handoff:
  id: TASK-YYYYMMDD-NNN
  from: coordinator
  to: idea-generator | executor
  objective: null
  uncertainty_reduced: null
  inputs: []
  constraints: []
  deliverables: []
  budget:
    wall_clock_seconds: null
    memory_gb: null
    maximum_runs: null
  completion_gate: []
  return_format: null
```
