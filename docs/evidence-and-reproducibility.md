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
- a scale-relevance label — `toy-scale`, `feasibility-scale`, or `cryptographic-scale` — with its justification (direct computation at the stated size, or an exact correspondence/embedding at the stated size);
- the largest claim justified by the data.

A result on a small prime field establishes a measured result on the tested
distribution. It may also support a broader conclusion when the record states
the transfer argument, assumptions, and remaining uncertainty explicitly.

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

## Heuristic-validation experiments

When a theorem is stated conditional on a formally numbered heuristic (see `docs/target-result-profile.md`), that heuristic requires its own experiment, kept separate from the theorem's other evidence. The canonical pattern is a pre-registered theoretical prediction compared against a measured empirical distribution — for example, a claimed smoothness probability `u^{-u(1+o(1))}` (the Dickman–de Bruijn function `ρ(u)`) tested against the empirical CDF of the largest prime factor of the quantity whose smoothness is assumed.

Required protocol elements:

- **Pre-registered prediction.** Before data collection, the specification records the exact predicted distribution and its parameters, the parameter sets, the planned sample size per set, the primary comparison (e.g., empirical CDF vs predicted CDF), the tail checks, and the stopping rule. Later changes are recorded as amendments, never silent edits.
- **Exact prediction source.** The prediction must combine only rigorous or classical ingredients: a proved bound (e.g., degree ≤ `(p/2)^{1/3}`) plus a citable distribution theorem (e.g., Canfield–Erdős–Pomerance: `Ψ(X, B) = X·u^{-u(1+o(1))}`). The record states in one sentence exactly what the heuristic assumes beyond these ingredients.
- **Correspondence or embedding justification.** When direct sampling at cryptographically relevant sizes is infeasible, sampling may route through an exact correspondence — for example, the Deuring correspondence: sampling random maximal orders in the quaternion algebra `B_{p,∞}`, where the two-sided ideal of reduced norm `p` with quadratic form `Nrd/p` is isometric to `Hom(E, E^{(p)})` with `deg`. The record must name the correspondence, argue that the sampled distribution is exactly the distribution of interest (including uniformity of sampling on both sides), and state on which side of the correspondence the computation ran.

Required reporting:

- exact parameter sets (e.g., `p = 5·2^248 − 1`, `p = 27·2^500 − 1`), the scheme or security level each corresponds to, and the sample size at each set;
- the sampling method, its uniformity argument, and all seeds;
- the empirical-vs-predicted comparison over the full range, plus a zoomed view of the smooth tail (e.g., the 500 smoothest samples);
- tail consistency checks: the smoothest observed sample against the predicted probability of that smoothness level (e.g., a 12589-smooth minimum among 100,000 samples vs predicted `ρ(u) ≈ 1/69232`; an `e^23`-smooth minimum among 10,000 samples vs predicted `ρ(u) ≈ 1/3312`);
- every deviation from prediction, recorded as an unexpected observation — never silently discarded.

Scale labeling and strength:

- Each record carries a scale-relevance label and names the parameters actually
  tested. Evidence transferred beyond the directly tested range names the
  correspondence, model, or extrapolation and its unresolved assumptions.
- Agreement between data and prediction supports the heuristic; it does not prove it. The main theorem remains conditional, and no ledger transition may relabel a heuristic-conditional claim as unconditional.

## Concrete-cost estimation artifacts

A result that changes an asymptotic exponent must retain a concrete-cost artifact alongside the proof. A cost estimate is an analysis artifact, not a run receipt: it is labeled `estimate`, never `measured`, and its inputs are machine-readable so the table can be regenerated.

Required content:

- **Standardized parameter sets.** Estimates at standardized security levels (e.g., `log2 p ≈ 256 / 384 / 512` for the NIST-I/III/V-relevant sizes, plus at least one larger size), each in explicitly declared operation units (e.g., `F_{p^2}`-operations), with the previous best method reported in the same units for comparison.
- **Time, memory, and parallelism.** Each level reports time, memory, and the effect of parallel processors; memory is a first-class number, not an afterthought.
- **Flagged optimistic assumptions.** Every optimistic simplification (e.g., costing one field operation per table entry, or assuming tightness of a success-probability bound) is listed individually, and for each the record states the direction of bias it induces — under-estimate or over-estimate of the true cost. The artifact states plainly that such numbers are not accurate predictions.
- **Hidden-overhead disclosure.** Any superpolynomial factor absorbed into an `o(1)` term, and any `(log p)^{O(1)}`-type cofactor absorbed into an exponent, is disclosed next to the headline complexity.
- **Time–memory tradeoff.** Where a meet-in-the-middle or claw-finding structure permits it, the artifact includes the tradeoff curve — e.g., van Oorschot–Wiener: a claw problem of size `N` solved in time `√(N³/w)` with memory `w`, and in time `√(N³/w)/n` with `n` parallel processors — covering the interpolation between the high-memory and polynomial-memory regimes.
- **Affected-vs-unaffected scope statement.** An explicit list of which systems and parameter sets the estimate applies to, and which remain out of range, with the reason (e.g., a different attack already dominates their security analysis). This scope statement travels with the claim wherever the claim is cited.
