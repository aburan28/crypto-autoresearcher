# Initial ECDLP Autoresearch Roadmap

## Phase 1 — Orchestration foundation

- Define agent contracts and state transitions.
- Establish immutable run manifests and evidence records.
- Add schema validation and experiment directory conventions.
- Build a local coordinator that dispatches structured tasks.

## Phase 2 — Baseline harness

- Implement deterministic toy prime-field curve generation.
- Implement matched Pollard-rho baselines and normalized cost reporting.
- Add Semaev-system generation and Gröbner-basis measurements.
- Capture arithmetic operations, wall time, degree profile, memory, and solver outcomes.

## Phase 3 — Automated hypothesis loop

- Idea Generator emits structured proposals.
- Coordinator deduplicates proposals against the ledger.
- Coordinator selects minimal discriminating experiments.
- Executor runs bounded batches and writes immutable records.
- Coordinator synthesizes results and chooses replicate, expand, refine, or pause.

## Phase 4 — Initial research programs

1. **Isogeny-neighborhood audit**
   - Walk small-degree neighbors.
   - Compare matched Semaev and Gröbner behavior.
   - Separate isogeny effects from random coefficient variance.

2. **Representation search**
   - Compare coordinate models, factor bases, eliminations, and symmetrizations.
   - Measure sparsity, degree of regularity, elimination degree, and relation density.

3. **Pair-selection learning**
   - Establish deterministic Buchberger baselines.
   - Compare heuristic, imitation-learning, and reinforcement-learning policies.
   - Separate step-count gains from arithmetic-operation gains.

4. **Predicate and decomposition channel tests**
   - Specify candidate separability or low-complexity predicates.
   - Build adversarial controls.
   - Record exact scope of negative results.

## Phase 5 — Scale and red-team gates

Before escalating a result:

- reproduce on fresh seeds and independent instances;
- compare against matched controls;
- test scaling trends rather than isolated wins;
- have an independent agent inspect implementation and analysis;
- state whether the evidence is toy-scale, medium-scale, or cryptographic-scale;
- compare projected cost against generic rho using an explicit cost model.

## Research direction criterion

Exemplar-pattern alignment is a standing criterion for direction
prioritization, per `docs/target-result-profile.md` (canonical exemplar:
Wesolowski's p^{1/3+o(1)} supersingular-isogeny result, full text at
`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`). When selecting or expanding
research programs — including the Phase 4 programs above — prefer directions
that target the asymptotic exponent of a central problem, state conditional
results against explicit numbered heuristics, plan cryptographic-scale
validation experiments for those heuristics, and report concrete costs,
memory, and affected-vs-safe scope honestly. This criterion ranks directions;
it does not lower the Phase 5 evidence gates.

## Immediate next engineering tasks

- Add YAML/JSON schemas corresponding to `templates/research-records.md`.
- Add a CLI for creating IDs and validating records.
- Add a run wrapper that captures environment, command, logs, and metrics.
- Add a ledger index generated from experiment directories.
- Add a coordinator queue and agent adapter interface.
- Add CI checks for schema validity, broken evidence references, and overwritten run IDs.