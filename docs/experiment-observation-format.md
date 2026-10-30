# Experiment observation format, MVP v1

Use one small YAML presentation sidecar for each new report or snapshot. It
surfaces what was observed, including ordinary behavior, failures, censoring and
unresolved measurements. Interpretation, relevance and usefulness calls stay
with the owner. No anomaly, improvement or scientific verdict is required.

Start from [the template](../templates/experiment-observation.yaml); see the
[saved rotation-density example](../templates/examples/rotation-observation.yaml).
The machine contract is
[`crypto.autoresearch.experiment_observation.v1`](../schemas/experiment-observation.schema.json).
YAML contains JSON-compatible values, string mapping keys, no duplicate keys,
custom tags, merge keys, nonfinite numbers or implicit dates. Quote dates and
ambiguous string values. Keep exact large integers or rational numerators and
denominators; do not round away the underlying counts.

## Surface order

| Field | What the reader gets |
| --- | --- |
| `question`, `scope` | Observable question, instance domain and explicit exclusions |
| `method` | Actual procedure, command, parameters, seeds, sampling unit and stopping rule |
| `runs` | Existing experiment/run IDs and literal statuses with evidence selectors |
| `observations` | Measured or derived values, units, counts, dependence, uncertainty and source selectors |
| `controls` | Observed references, matching conditions and limitations |
| `patterns` | Optional deviations, exploratory patterns or suspected measurement artifacts worth inspecting |
| `limitations`, `missing` | Unresolved scope, unavailable fields and why they are unavailable |
| `next_checks` | Specific questions and proposed methods/controls |
| `artifacts` | Repository-relative paths, full commit pins and SHA-256 hashes |

Human summaries use this same order. Lead with concrete values, then the
reference and uncertainty. A flag can say “this pattern is worth inspecting”
when supported by the linked data. Include ordinary/control outcomes alongside
flags. `patterns: []` needs no apology or replacement conclusion.

## Measurement rules

1. Copy existing IDs and literal native statuses. A program exit code, checker
   outcome, archive/schema status and scientific interpretation are different
   facts; report them as separate observations when available. A finished
   program can have a native `invalid_output` receipt. Do not normalize that to
   success. Group multiple runs only when their provenance remains separable.
2. `kind: measured` means transcribed saved output; `kind: derived` means a new
   aggregation, formula or calculation. Derived observations cite their saved
   inputs and analysis code. Put vectors or outcome tables in `value`, or cite
   a full table and include a bounded summary. Do not replace the raw table.
3. State the sampling unit and actual `sample.n`. A draw count is not a count of
   independent curves, targets or seeds. Record repeats, clustering, weighting,
   failed attempts and censoring. A timeout records a limit, not a mathematical
   null result; use `sample: null` for nonsampled computations and explain why
   in `missing`. Never substitute zero for an unavailable count or duration.
4. Every observation states `uncertainty`, including “not estimated” and why
   when appropriate. A spread across cells is not a confidence interval.
   Controls state which domain, distribution and conditions match. A mismatched
   reference can still be presented with its mismatch explicit; it cannot be
   silently treated as an exact null model or a matched performance baseline.
5. Every pattern links observations and named references, states uncertainty
   and lists explanations to check. Labels are `observed_deviation`,
   `exploratory_pattern` or `suspected_measurement_artifact`. None asserts a
   cause. Record post hoc selection and multiple comparisons in limitations
   where relevant. Proposed checks are not claims that the checks ran.
6. `null` means unavailable, with a JSON Pointer and reason in `missing`;
   `[]` means an explicitly empty collection, not an unknown sample. Fields that
   do not apply also get a reason. Hash and cite actual bytes, not placeholders.
   A selector locates the evidence within an artifact; selectors are human
   readable, such as `/cells` plus an explicit cell predicate.

## Storage and compatibility

Save `observation.yaml` in a new report directory after the existing raw-record
publication step. Never add it to a sealed run, rewrite an imported report or
change a manifest to fit this shape. Revised reports use new directories and
link their predecessors as artifacts. Preserve historical status and weighting.

This sidecar complements native run manifests, receipts, `TaskResult`, existing
reports, figures and PDFs. It does not mint ledger IDs, change canonical state,
replace existing presentation requirements or grant execution/review authority.
There is no mandatory run preflight or new admission gate. Performance or other
scientific claims retain their own evidence requirements when actually made.

## Optional format check

After writing a sidecar, in an environment with PyYAML and jsonschema:

```sh
python3 tools/check_experiment_observation.py path/to/new/report/observation.yaml
python3 tools/check_experiment_observation.py path/to/new/report/observation.yaml --check-artifacts
python3 -m unittest discover -s tests -p test_experiment_observation.py
```

The checker is read-only. It checks shape, duplicate/local reference IDs and
missing-value explanations; the optional flag also hashes locally available
artifact bytes. Missing sparse-checkout files are reported as unavailable, never
fetched automatically. It does not replay experiments, evaluate selectors,
verify that a commit contains an artifact, check statistical validity, confer
independent review or change any run status. A passing check means those narrow
format checks passed. There is no automatic scientific verdict.
