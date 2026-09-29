# Execution report: RUN-MLKEM-980909-001

Experiment: EXP-MLKEM-980909 (approved_by DEC-20260831-dfa5a6)
Handoff: TASK-20260831-66f15c

## What ran

One authorized target under `experiments/EXP-MLKEM-980909/specification.yaml`
(`maximum_runs: 1`, run exactly once): a single BKZ tour attempt at
`d=512, beta=55, q=3329, mpfr_bits=100`, seed `452658293` from the frozen
formula `default_rng([715923,0,512,55,0,0]).integers(0,2**31-1)`, under a
21600-second hard wall-clock cap owned by an external supervisor, preceded by
a required controlled-SIGTERM self-test (no BKZ).

- Self-test: PASSED (`verify_telemetry_receipt.py --expect-cause controlled_sigterm`).
- Target run started `2026-09-06T04:46:22Z`, terminated `2026-09-06T10:46:23Z`.
- Terminal cause: `hard_cap` (SIGTERM delivered by the supervisor at the
  21600-second cap; worker exit code 143).
- Independent verification of the target run's terminal receipt: PASSED
  (`verify_telemetry_receipt.py --expect-cause hard_cap`).

## Observation

The single authorized BKZ-55 tour at d=512 did **not** complete within the
21600-second (6 CPU-hour) budget on this host. At signal delivery the worker
had completed the outer LLL pass (359.17s) and was inside the `bkz` stage
(GSO/MPFR-100 established, `BKZReduction` call in progress); no
`worker_result.json` was produced because the worker did not return —
consistent with `DEC-20260831-dfa5a6`'s pre-registered `hard_cap_or_signal`
branch ("snapshot as failed_infrastructure/resource outcome; no mathematical
inference"). This is recorded exactly as an infrastructure/resource-budget
outcome, per AGENTS.md rule 3: a timeout is never negative mathematical
evidence, and the experiment's own `falsification_criterion` states a timeout
or process termination falsifies no mathematical hypothesis.

The RT-CTRL-1 telemetry mechanism itself — the actual subject of this
control-repair experiment per its `objective` ("retaining a durable terminal
lifecycle record under the unchanged 21600-second cap") — worked as designed:
manifest, hash-chained event log, worker state, and terminal receipt were all
produced and independently re-verified by code that imports none of the
producer's own modules.

## Resource usage (measured, not modeled)

- Peak RSS: ~162.3 MB (721 psutil samples at ~30s intervals; min 1.36 MB at
  process start, max 162.28 MB, essentially flat once BKZ began). Far under
  both the 16 GB contract ceiling and the host's actual ~15 GB total memory.
  No OOM occurred and no host-infeasibility finding applies.
- CPU time: 21600.16 user seconds + 0.29 system seconds ≈ 6.00004 CPU-hours,
  which is 0.16 seconds (~0.0044%) over the pre-registered 6.0 CPU-hour
  budget — an artifact of a single continuously-running process whose
  wall-clock cap and CPU time coincide almost exactly, recorded here rather
  than rounded away. Not material to interpretation.

## Deviations from the approved protocol (recorded, not discarded)

1. **Interpreter/dependency provenance.** The repository's default `python3`
   (3.11.15) has no `fpylll` installed. A fresh isolated venv was built using
   the system's `python3.13` package (apt-upgraded from 3.13.12 to 3.13.15
   while installing `libfplll-dev`/`libgmp-dev`/`libmpfr-dev`/`python3.13-dev`
   as build dependencies), and `fpylll==0.6.4` was compiled from source
   against it. `numpy==2.4.0` and `psutil==7.2.2` were installed exactly as
   pinned in the handoff.
2. **Yanked dependency.** PyPI reports `numpy==2.4.0` as yanked
   ("Backward compatibility bug"). It was installed anyway, per the frozen
   pin, and imports/operates correctly throughout the run. Not silently
   substituted with a different version.
3. **`tours` field unmeasured.** The worker only records `bkz.tours` inside a
   COMPLETED/ERROR `worker_result.json`, neither of which exists on the
   `hard_cap` branch. Reported as `NOT MEASURED`, never defaulted to `0` or
   any other value.
4. **CPU-hour budget exceeded by 0.16 seconds** (see Resource usage above).

## Certificate

`certificate.kind: none` — this run claims no discrete-log solve, relation,
or key recovery; it is a pure lifecycle/telemetry measurement, exactly as the
experiment's `success_criterion` frames it ("A completed BKZ return is an
observation, not experiment success in a cryptanalytic sense").

## Scope

Toy-scale (`scale_relevance.tier: toy`), one random q-ary basis at d=512,
beta=55 under fpylll 0.6.4 on one host. This run makes no claim about FIPS
203, ML-KEM parameters, attack costs, or key recovery, and does not itself
bear on the truth of any conjunct of H-MLKEM-7d9bcc (that measurement is
EXP-MLKEM-42ea04's scope; this experiment is an operational
telemetry/lifecycle control, per `heuristic_under_test: null` and
`preregistered_prediction.quantity: run lifecycle outcome` in the frozen
specification).

## Artifacts (all under experiments/EXP-MLKEM-980909/runs/RUN-MLKEM-980909-001/)

- `manifest.yaml`, `command.txt`, `environment.json`, `raw-result.json`,
  `stdout.log`, `stderr.log` (supervisor-level; empty — neither the
  supervisor nor the worker print to stdout/stderr under any observed branch)
- `selftest_output/{target_manifest.json,events.jsonl,worker_state.json,terminal_receipt.json,stdout.log,stderr.log}`
- `output/{target_manifest.json,events.jsonl,worker_state.json,terminal_receipt.json,stdout.log,stderr.log}`
  (`output/worker_result.json` absent — worker did not return; see Deviations #3)
