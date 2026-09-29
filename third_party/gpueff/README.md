# gpueff: how close does a workload run to its own roofline?

A workload-specific efficiency score for GPU (and CPU) work, computed from
DCGM exporter and Prometheus metrics. It was built for the ECC2K-130 rho walk
and applies equally to ML inference. It uses only the Python standard library
and runs on Python 3.8 or later.

Generic GPU utilisation says whether a kernel was resident. It does not say
whether the work was *useful*, or how much more there is to gain. This tool
answers the second question the way an inference engineer would. It asks
what the most is that this workload could do on this machine, and what
fraction of that it achieves.

```text
$ python3 -m gpueff score --machine rtx-pro-6000-blackwell-server \
      --workload ecc2k130-packed-walk \
      --scrape tests/data/scrape-t0.prom@1000 --scrape tests/data/scrape-t60.prom@1060
ecc2k130 packed walk on NVIDIA RTX PRO 6000 Blackwell Server Edition x2
score           87.5 / 100  (basis: roofline, coverage 100.0%)
roofline        81.6%  achieved 12.8 G/s of 15.69 G/s attainable (bound: alu:iadd3+ffma)
next roof       alu:imad.wide, 3.96x above the bound
energy          62.5 nJ per walk iteration at 800 W

component       value      raw  weight  note
roofline        0.816    0.816    0.50
sm_active       0.950    0.950    0.15  DCGM SM_ACTIVE
occupancy       0.963    0.321    0.10
bound_pipe      0.890    0.890    0.15
clock           0.975    0.975    0.10
cpu          not_applicable             0.00  CPU only feeds the GPU; see HOST_BOUND for its effect

roofline = clock_factor x sm_active x in_kernel
  clock_factor  0.975   (12% of the loss)
  sm_active     0.950   (25% of the loss)
  in_kernel     0.880   (63% of the loss)

[warning] THROTTLED: clocks were held down by a power or thermal limit in 25% of samples (clock factor 0.975)
```

(The two scrapes are synthetic test fixtures with hand-picked values, not a
measurement.)

## The model

### 1. Roofs: machine ceilings divided by workload demand

A **machine profile** lists ceilings, each the most a device can do of one
kind of work per second: integer-pipe lane-ops, tensor FLOPs, DRAM bytes, and
so on. A ceiling is either absolute (`per_second`, e.g. DRAM bandwidth) or
per SM per clock (`per_sm_per_clock`), which scales with the SM clock. CPUs
use `per_core_per_clock`.

A **workload profile** lists demand: what one unit of useful output costs on
each resource. For ecc2k130 the unit is one walk iteration, which costs
4,328 lane-instructions, 742.5 of them wide multiplies. For LLM decode the
unit is one token, which costs 2·params FLOPs plus its share of the weight
and KV-cache bytes.

Each demand gives a roof, `ceiling / demand` units per second. The lowest roof
is the **bound**, and `attainable = bound × devices`. This is the classic
roofline generalised to N resources. The next-lowest roof is also reported:
it is the most any optimisation of the bound can buy before the workload hits
the next wall.

```text
$ python3 -m gpueff roofline --machine h100-sxm-datasheet --workload llm-decode-8b-bf16
demand           resource                   per unit      ceiling/s   generated token/s
hbm_bytes        hbm_bytes                     770 M         3.35 T   4.351 k   <- bound
tensor_bf16_flops tensor_bf16_flops           16.06 G        989.4 T   61.61 k
```

### 2. Roofline efficiency: the outcome

```text
roofline_efficiency = achieved throughput / attainable throughput
```

This is the number an optimisation moves. At 1.0 nothing is left without
changing the algorithm (the demand) or the hardware (the ceilings). A value
above 1.02 raises `CEILING_EXCEEDED`: the "ceiling" is not one, or the demand
is overstated. The profile is wrong, and the tool says so rather than
clamping the value quietly.

### 3. Loss decomposition: where the missing percent went

The roofline fraction splits exactly into three factors:

```text
roofline = clock_factor × sm_active × in_kernel
```

| factor | source | loss it captures |
|---|---|---|
| `clock_factor` | `DCGM_FI_DEV_SM_CLOCK` / reference clock (only when the bound roof scales with the clock) | power and thermal throttling |
| `sm_active` | `DCGM_FI_PROF_SM_ACTIVE` | launch gaps, host stalls, synchronisation, tail waves |
| `in_kernel` | the remainder | how close the code runs to the roof *while it runs* |

Each factor's share of the loss is `ln(factor) / ln(roofline)`, so the shares
add up to 100%.

### 4. Composite score (0–100): outcome plus explanation

The composite is a weighted **geometric** mean of components in [0, 1]. With a
geometric mean, one component near zero cannot be hidden by the others being
good.

| component | default weight | definition |
|---|---:|---|
| `roofline` | 0.50 | roofline efficiency (capped at 1) |
| `bound_pipe` | 0.15 | DCGM activity of the bound pipe (`PIPE_INT_ACTIVE`, `PIPE_TENSOR_ACTIVE`, `DRAM_ACTIVE`, …) |
| `sm_active` | 0.15 | `SM_ACTIVE`; falls back to `GR_ENGINE_ACTIVE`, then `GPU_UTIL`, and the report names the basis used |
| `occupancy` | 0.10 | `(SM_OCCUPANCY / SM_ACTIVE) / target_occupancy`, capped at 1 |
| `clock` | 0.10 | observed SM clock / reference clock, capped at 1 |
| `cpu` | 0.15 | cores used / cores allocated; scored only when `cpu.role` is `compute` |

Deliberate choices:

* **Occupancy is measured against the launch's own target, never against
  100%.** More resident warps is not better per se. The ecc2k130 kernel is
  pipe-bound at 16 of 48 warps, and every occupancy experiment in its history
  failed to help. Without a `target_occupancy` the component is reported as
  not applicable. Occupancy is divided by `SM_ACTIVE` so that idle time,
  which `sm_active` already counts, is not charged twice.
* **Clock counts only when the bound scales with the clock.** A decode
  workload bound on HBM loses nothing when the SM clock drops.
* **Missing data is never filled in.** A missing component is left out, the
  weights are renormalised, and `coverage` reports the fraction of the weight
  that had data. Without a throughput metric the score is flagged
  `basis: hardware-proxy`: it still ranks hardware behaviour, but it is not a
  roofline number.
* Weights are adjustable per workload (`"weights": {...}` in the profile) or
  per run (`--weights roofline=0.6,clock=0`).

### 5. Findings

| code | fires when |
|---|---|
| `CEILING_EXCEEDED` | achieved > 1.02 × attainable |
| `HOST_BOUND` | SMs idle more than 10% of the time and a CPU core is at least 95% busy |
| `IDLE_GAPS` | SMs idle more than 10% of the time, with no pegged core |
| `THROTTLED` | a power or thermal clock event reason was set in any sample |
| `WASTED_WORK` | the bound pipe is at least 85% active, but less than 75% of that becomes useful output (spills, recomputation, or a stale demand model) |
| `BOUND_MISMATCH` | another resource is busier than the modelled bound, so the demand profile is wrong about what binds |
| `LOW_OCCUPANCY` | achieved occupancy is below 80% of the launch target |

## Inputs

Metrics are read under their DCGM exporter names. The PROF fields need DCGM
profiling metrics enabled, which DCGM exporter provides through its
`dcp-metrics-included.csv` counters file.

| input | metrics |
|---|---|
| GPU | `DCGM_FI_PROF_SM_ACTIVE`, `_SM_OCCUPANCY`, `_GR_ENGINE_ACTIVE`, `_PIPE_{INT,FP32,FP16,FP64,TENSOR}_ACTIVE`, `_DRAM_ACTIVE`, `DCGM_FI_DEV_SM_CLOCK`, `_POWER_USAGE`, `_TOTAL_ENERGY_CONSUMPTION`, `_CLOCKS_EVENT_REASONS` (or the older `_CLOCK_THROTTLE_REASONS`) |
| throughput | the metric named in the workload profile. A counter is turned into a rate with reset handling; a gauge is averaged |
| CPU | `node_cpu_seconds_total` from node_exporter, and optionally a per-process CPU counter |

Three ways to supply them, all reduced by the same code:

```sh
# saved scrapes (curl the exporters twice; counters need two points)
python3 -m gpueff score --machine M --workload W --scrape t0.prom@T0 --scrape t1.prom@T1
# a live Prometheus server, over a window
python3 -m gpueff score --machine M --workload W --prometheus http://prom:9090 --window 15m
# a benchmark that printed its own rate (hardware components then come from --scrape/--prometheus)
python3 -m gpueff score --machine M --workload W --throughput 6.905e9 --devices 1
```

`--json` prints the full report. `--prom-out FILE` writes the score in
Prometheus text format for node_exporter's textfile collector, so Grafana can
plot it next to DCGM.

### Continuous scoring inside Prometheus

```sh
python3 -m gpueff rules --machine rtx-pro-6000-blackwell-server \
    --workload ecc2k130-packed-walk --window 5m > gpueff-ecc2k130.rules.yml
```

This emits recording rules (`gpueff:score`, `gpueff:roofline_efficiency:ratio`,
`gpueff:sm_active:ratio`, …) with the roofline built in as constants. The
tests run `promtool test rules` to check that the rules produce the same score
as the Python code. One difference: when an input series is absent, the rule
records no sample instead of renormalising, so a live score goes missing
rather than silently changing its basis. Set `gpu_selector` in the workload
profile so that `devices:count` counts only the GPUs running the workload.

## Tie-in to the ECC work

* `profiles/rtx-pro-6000-blackwell-server.json` is **generated** from the
  measured probe in `ecc2k130/runner/benchmarks/hardware-limits/result.json`
  with `python3 -m gpueff machine-from-probe`. CI checks that it is current.
  These are ceilings that host-verified instructions actually reached, not
  datasheet peaks.
* `profiles/ecc2k130-packed-walk.json` carries the audited demand from
  `ecc2k130/runner/THROUGHPUT-CEILING.md`: 4,328.125 lane-instructions and
  742.5 `IMAD.WIDE` per update. The wide-multiply roof reproduces that note's
  "31 B/s if the walk did nothing else". The audited 6.905 B/s scores 88% of
  the issue roof at the reference clock. Charging the same demand to the
  LOP3+IMAD probe (69.3 per SM-clock) raises `CEILING_EXCEEDED`. That is why
  the profile uses the IADD3+FFMA dual-issue rate (78.3), and a test checks
  it.
* `ecc2k130/runner/aws/worker.py` exports `ecc2k130_walk_iterations_total`
  and `ecc2k130_walk_rate` on each heartbeat when `ECC_METRICS_DIR` names a
  textfile-collector directory. Nothing changes when it is unset.

**Keep demand current.** Each instruction-count change to the kernel changes
the demand per update. A stale profile makes the score drift without any
warning. `WASTED_WORK` and `CEILING_EXCEEDED` catch only large errors.

## Adding a workload

1. Choose the unit of useful output: an iteration, a relation, a token, a
   request.
2. Count what one unit costs on each resource. SASS instruction counts,
   bytes moved and FLOPs are all fine; say where each number came from in
   `why`.
3. Charge each demand to a machine ceiling. Prefer measured ceilings; a
   datasheet profile (like `h100-sxm-datasheet.json`) makes every score
   pessimistic by the same unexplained margin.
4. Name the throughput metric, and set `target_occupancy` if the launch fixes
   one.

## Tests

```sh
cd gpueff && python3 -m unittest discover -s tests -v   # PROMTOOL=/path/to/promtool to include the rules test
```
