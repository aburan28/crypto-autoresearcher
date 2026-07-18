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
  inference:
    requested_policy: null
    resolved_model_id: null
    reasoning_effort: null
    fallback_used: false
    adapter_version: null
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

## Baseline discipline

Every claimed improvement must compare against a clearly defined baseline under matched conditions. For ECDLP experiments, report generic Pollard-rho context where relevant, but do not treat incomparable operation types as directly equivalent without a cost model.

## Statistical discipline

- Predefine the primary metric.
- Report distributions and paired observations, not only best runs.
- Treat seed selection as part of the protocol.
- Report invalid and censored runs.
- Distinguish solver timeout from measured high cost.
- Use effect size and uncertainty, not only a binary significance label.