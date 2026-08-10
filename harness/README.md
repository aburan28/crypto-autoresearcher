# harness — executable spine

Minimal, correct ECDLP experiment substrate. The included implementations are
deterministic and independently verifiable; each run records the parameters
and evidence scope needed to interpret results at the scale actually tested.

| module | role |
|---|---|
| `toycurve.py` | F_p short-Weierstrass arithmetic, exact point counting, deterministic ECDLP instance generation. Also the **independent verifier** for certificates. |
| `rho.py` | Pollard rho (Teske r-adding walk) — the matched generic baseline (KN-TECH-001). Recovers k using public data only. |
| `semaev.py` | Semaev summation polynomials S_2/S_3/S_4 and the S_3 point-decomposition Groebner measurement (KN-TECH-002/003/004). |
| `runner.py` | Run wrapper: captures commit/env/timing/resources, re-verifies every certificate independently, and writes the immutable run record. Refuses to overwrite a run id. |
| `run.py` | Experiment entry point (EXP-SEMAEV-001). `python -m harness.run --experiment EXP-SEMAEV-001`. |

Run tests with `python -m pytest -q`. Metrics honesty: the Groebner
`*_max_degree_proxy` is the reduced-basis max degree, an implementation-bound
proxy, **not** the theoretical degree of regularity (see KN-TECH-004). Trends
and absolute timings are interpreted only with their tested parameters, cost
model, and any stated transfer assumptions.

## Exemplar-aligned experiment classes (optional manifest metadata)

Two experiment classes in the spirit of the canonical exemplar
(`inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`; see also
`docs/target-result-profile.md`) need manifest metadata beyond `metrics`:

- **Heuristic validation** — samples a quantity whose distribution a numbered,
  formally stated heuristic predicts, and compares the empirical distribution
  against the pre-registered prediction (exemplar §4.2: the empirical CDF of
  the largest prime factor of the smallest isogeny degree vs. the
  Dickman–de Bruijn prediction ρ(u), at cryptographically sized p, with
  explicit sample sizes and a tail check on the smoothest sample).
- **Cost measurement** — measures concrete cost under an explicit cost model
  (exemplar §4.1: F_{p^2}-operation and memory bounds at standardized
  parameter sets, with optimistic assumptions flagged). The operation unit and
  assumptions are recorded so costs from different models are never compared
  without conversion (baseline discipline, docs/evidence-and-reproducibility).

`RunResult` accepts two optional dicts, recorded verbatim in the manifest when
provided and omitted entirely otherwise — existing runs and manifests are
unaffected. Like `parameters` and `metrics`, these blocks are recorded, not
interpreted: the runner enforces no schema beyond "dict or absent".

```yaml
run:
  ...
  heuristic_validation:            # optional; key absent => not this class
    heuristic_id: null             # e.g. "H1"
    statement_ref: null            # where the heuristic is formally stated
    prediction: null               # pre-registered before the run
    theoretical_distribution: null # e.g. "dickman_de_bruijn rho(u)"
    sample_size: null
    scale_relevance: null          # tested parameters and transfer assumptions
  cost_model:                      # optional; key absent => not this class
    operation_unit: null           # e.g. "group_operation", "Fp2_operation"
    assumptions: []                # optimistic assumptions flagged explicitly
    notes: null
```

Results recorded under these fields may be used for direct or conditional
claims when the tested parameters, evidence scope, and transfer assumptions
are stated explicitly (AGENTS.md rule 7).
