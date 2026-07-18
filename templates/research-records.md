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
  to: idea-generator | executor | reviewer
  objective: null
  uncertainty_reduced: null
  inputs: []
  constraints: []
  deliverables: []
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
