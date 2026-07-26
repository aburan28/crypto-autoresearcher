# Evidence and Reproducibility

## Evidence hierarchy

Evidence strength is assigned by the Coordinator.

| Level | Meaning |
|---|---|
| `anecdotal` | One observation or debugging trace; useful only for generating hypotheses. |
| `preliminary` | Valid experiment with limited instances, seeds, controls, or scale. |
| `replicated` | The effect was reproduced from a clean run, preferably independently. |
| `strong` | Predefined protocol, adequate controls, multiple instances, retained artifacts, and stable effect. |
| `inconclusive` | Data do not distinguish the relevant explanations. |
| `contradictory` | Valid experiments materially disagree and require reconciliation. |

## Claim boundaries

Every evidence record must state:

- curve family and field type;
- bit sizes tested;
- instance-generation method;
- solver and implementation version;
- parameter range;
- number of seeds and independent instances;
- controls and baselines;
- resource limits;
- known confounders;
- the largest claim justified by the data.

A result on toy prime fields establishes behavior only on the tested toy distribution. It may motivate a scaling study but does not establish a P-256 result.

## Negative-result semantics

A valid negative result may reject only a scoped prediction. It does not prove that:

- all parameterizations fail;
- all related representations fail;
- all isogenous curves behave identically;
- no undiscovered structure exists;
- no future algorithm can exploit the mechanism.

Use language such as:

> No improvement meeting the predefined threshold was observed over the tested instances, parameters, solver, and resource budget.

## Reproduction package

Each experiment must retain:

```text
experiments/<experiment-id>/
  specification.yaml
  amendments/
  implementation.md
  analysis.md
  runs/<run-id>/
    manifest.yaml
    command.txt
    environment.json
    stdout.log
    stderr.log
    raw-result.json
```

## Minimum run manifest

```yaml
run:
  id: RUN-...
  experiment_id: EXP-...
  status: completed_valid
  code:
    commit: git-sha
    dirty: false
    command: exact command
  inference:                       # written by orchestration/adapter/manifest.py
    requested_policy: null         # exactly as the handoff wrote it
    canonical_policy: null
    backend: null                  # null = no model was in this run's loop
    provider: null
    resolved_model_id: null
    model_provenance: null         # runtime-verified | operator-supplied |
                                   # unbound | not-applicable
    model_verified: false          # probe-confirmed that the backend serves it
    requested_reasoning_effort: null
    reasoning_effort: null
    fallback_used: false
    fallback_reason: null
    degraded_requirements: []      # requirements the resolved model does not meet
    independent_session: false
    adapter_version: null
    config_digest: null            # binds the run to exact policy/binding config
  environment:
    operating_system: null
    architecture: null
    sage_version: null
    python_version: null
    dependencies: {}
  inputs:
    curve_id: null
    seed: null
    parameters: {}
  timing:
    started_at: null
    finished_at: null
    wall_seconds: null
  resources:
    peak_rss_bytes: null
    cpu_seconds: null
  result:
    metrics: {}
    valid: true
    invalid_reason: null
    certificate:              # see docs/claims-and-verification.md
      kind: discrete_log | decomposition | none
      verified: null          # true once independently re-checked; a failed
                              # check invalidates the run (invalid_measurement)
      verifier: null
  artifacts: {}
```

## Data integrity

- Never overwrite a raw result.
- Never delete failed runs from the ledger.
- Never hand-edit generated metrics without preserving the original and transformation code.
- Use stable IDs rather than filenames as identity.
- Record checksums for large external datasets and artifacts.
- Separate exploratory notebooks from canonical analysis scripts.
- Prefer machine-readable outputs over parsing human-oriented logs.

## Git archival gate

A run manifest's `code.commit` identifies the code revision used for that run;
it does not by itself prove that the run package, theory, review, or ledger
record was committed. The dispatch lifecycle therefore uses Coordinator-only
archive tasks:

- a snapshot archive commits exact producer artifacts before review;
- a ledger archive commits review reports, evidence, decisions, and any status
  or knowledge updates before an official transition.

Archive tasks run alone in a shared worktree. Their receipts bind the Git
commit and parent, exact changed paths, record IDs, and SHA-256 values. The
dispatcher verifies those facts from Git; a working-tree-only artifact remains
incomplete evidence.

## Baseline discipline

Every claimed improvement must compare against a clearly defined baseline under matched conditions. For ECDLP experiments, report generic Pollard-rho context where relevant, but do not treat incomparable operation types as directly equivalent without a cost model.

## Statistical discipline

- Predefine the primary metric.
- Report distributions and paired observations, not only best runs.
- Treat seed selection as part of the protocol.
- Report invalid and censored runs.
- Distinguish solver timeout from measured high cost.
- Use effect size and uncertainty, not only a binary significance label.
