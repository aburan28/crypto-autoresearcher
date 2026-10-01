# harness — executable spine

Minimal, correct ECDLP experiment substrate. The included implementations are
deterministic and independently verifiable; each run records the parameters
and evidence scope needed to interpret results at the scale actually tested.

| module | role |
|---|---|
| `toycurve.py` | F_p short-Weierstrass arithmetic, exact point counting, deterministic ECDLP instance generation. Also the **independent verifier** for certificates. |
| `rho.py` | Pollard rho (Teske r-adding walk) — the matched generic baseline (KN-TECH-001). Recovers k using public data only. |
| `walk.py` | The rho walk as a first-class object: Teske r-adding steps with coefficient bookkeeping, orbit tracing (tail/cycle), distinguished-point walks, and the van Oorschot--Wiener DP collision search. |
| `kangaroo.py` | Pollard kangaroo over an interval: tame/wild herds meeting at distinguished points, trajectories retained. |
| `walkviz.py` | Draws what those two produce -- functional graph with one rho highlighted, DP forest with the golden collision, kangaroo herds -- as dependency-free SVG. |
| `run_walkviz.py` | `python -m harness.run_walkviz --seed 7 --field-bits 16 --out-dir out/`: walk records (JSON) plus figures (SVG) for one instance. |
| `semaev.py` | Semaev summation polynomials S_2/S_3/S_4 and the S_3 point-decomposition Groebner measurement (KN-TECH-002/003/004). |
| `runner.py` | Run wrapper: captures commit/env/timing/resources, re-verifies every certificate independently, and writes the immutable run record. Refuses to overwrite a run id. |
| `run.py` | Experiment entry point (EXP-SEMAEV-001). `python -m harness.run --experiment EXP-SEMAEV-001`. |
| `bench_rho_throughput.py` | Rho **step throughput** on this machine, CPU and CUDA from one walk definition: three implementations cross-checked limb-for-limb before any rate is reported. Kernel and dual-target field arithmetic in `gpu/` (see `gpu/README.md`). |

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

## Compute efficiency (optional, opt-in)

`harness/efficiency.py` adds a wrapper-measured `result.metrics.efficiency`
block to a run record. It measures how the run used the machine; it is a cost
observation scoped to this machine and run, never mathematical evidence.

```python
from harness.efficiency import run_wrapped_measured

run_wrapped_measured(
    "EXP-...", "AREA", run_fn, status="completed_valid", command=cmd,
    efficiency={                                   # optional: roofline score
        "machine": "rtx-pro-6000-blackwell-server",   # third_party/gpueff/profiles
        "workload": "ecc2k130-packed-walk",
        "work_units_metric": "iterations",         # key in the run's own metrics
        "dcgm_url": "http://host:9400/metrics",    # optional, scraped at start and end
        # "prometheus_url": "http://prom:9090",    # optional, range-queried over the run
    })
```

- `cpu` (always): process-tree CPU seconds (own plus waited-for children)
  over the wrapper's wall seconds, as `parallelism` in cores and
  `utilization` of the cores this process may use.
- `roofline` (with a spec): the gpueff score from `third_party/gpueff`, which
  is vendored from `aburan28/cryptanalysis` at the commit in its
  `UPSTREAM.json`. It records the achieved/attainable throughput, the
  `clock x sm_active x in_kernel` loss decomposition, the components, the
  findings, and the sha256 of both profiles. Throughput is work units over
  the wrapper's wall clock, never caller-reported.
- Missing inputs are listed under `missing` with the reason. A scoring
  failure is recorded as `status: error` in the block and the run is still
  written. An experiment metric already named `efficiency` is refused, not
  overwritten.

It is a separate entry point on purpose. `harness/runner.py` and
`schemas/run-manifest.schema.json` are hash-pinned by locked execution plans,
so they are unchanged, and runs that do not call this function record exactly
what they recorded before. Using it in a frozen protocol is an additive
amendment to that protocol, as for any change of entry point.
