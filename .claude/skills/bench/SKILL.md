---
name: bench
description: "Assess benchmark receipts, cost models, throughput claims, rank/relation metrics, CPU/GPU comparisons and performance regressions. Use when asked whether a measured optimization is faster or comparisons are fair. Use run to collect trials and review-evidence to promote research claims."
---

# Benchmark assessment

Read `docs/bounds-and-frontiers.md` and the producing tool's measurement contract. Consult `groebner_compare/relation_metrics.py`, `harness/efficiency.py`, `harness/bench_rho_throughput.py` and `ui/comparisons.py` as applicable.

1. Match exact curve/subgroup, candidate, workload, instance selection, controls, seeds, output validity, units and timing boundaries. Incompatible rows remain incomparable.
2. Separate setup and online work; charge failed searches, timeouts, duplicates, verification, independent rank updates, conversion and recovery. Amortize only reusable setup with a stated target count.
3. Retain CPU core/NUMA pinning, OS, CPU generation, DDR type, GPU model, compiler/dependencies, resources and calibration. Distinguish field bits from subgroup bits and iterations from useful steps.
4. Separate arithmetic primitive counts, operation models, wall time, throughput and asymptotic claims. A modeled cost or kernel throughput is not a complete-problem bound.
5. Compare paired results with uncertainty at the stated scope. Report missing controls or quantities explicitly; do not invent a global winner from partial receipts.
6. Return the paired table, accounting boundary, sources, uncertainty and material limitations. Measured bounds require the existing producing harness; official frontier/claim changes remain with Coordinator review. Do not rerun or launch cloud work solely to assess supplied measurements.

Follow current `AGENTS.md` authority, provenance and immutable-record rules. This profile adds no prerequisite to `run`; preserve explicit execution requests.
