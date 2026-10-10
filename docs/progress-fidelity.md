# Cryptanalytic Progress and Fidelity Framework (CPFF) v1

## Normative policy

Every new numeric claim of a cryptanalytic speedup, ECDLP work-factor reduction,
or attack-level improvement MUST include a machine-readable record under
`claims/*.json`, passing the `progress-fidelity` CI job. Historical immutable
run records are never rewritten; backfill by adding separate claim records.

The validator checks provenance, matched instance/seed pairs, reconciled
attempted/verified/failed/timeout/invalid outcomes, positive finite observations,
consistent units and cost-model components. A local speedup is **not** an
attack-level improvement. The baseline and candidate must share the same
workload, hardware and measurement protocol; reviewers must inspect the
referenced immutable run artifacts.

The gate rejects censored or invalid runs as evidence of a qualified improvement;
the runs themselves must remain archived, including failed attempts. A separately
reviewed survival-analysis cost model is needed for timeout-heavy experiments.
`qualified_schema` means structurally admissible, **not independently verified**.
The Coordinator and independent reviewer must still check certificates,
statistical power, confidence intervals, environment comparability, and scaling.

## Full-cost metrics

Index calculus: setup + relation generation including misses + rank/linear
algebra + individual log + verification. Rho: walk generation + distinguished
point transport + collision processing + verification. Isogeny: discovery +
transfer + target solve + inverse recovery. Record CPU/GPU time, energy, and
dollars separately; never add unlike units. For cryptographic-scale
extrapolation use `level=attack_projection` with assumptions and uncertainty.
Do not multiply overlapping local speedups.

## Usage

`python3 -m tools.progress_fidelity validate claims/example.json`
`python3 -m tools.progress_fidelity compare claims/example.json`
`python3 -m tools.progress_fidelity portfolio claims/`

## Enforcement limitations

The workflow validates submitted records; it cannot automatically detect
speedup prose that has no claim record. Reviewers must enforce the policy for
new claims, and repository administrators must require the `progress-fidelity`
check in branch protection. A workflow alone is not mandatory merge protection.

The portfolio command exports JSON for future UI integration; it is not yet a
deployed dashboard. Backfill, statistical intervals, censored observations,
cost-frontier histories, and UI integration remain follow-up implementation.
