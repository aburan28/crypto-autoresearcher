# Execution report — TASK-20260831-66f15c

- experiment_id: EXP-MLKEM-980909
- approved_by: DEC-20260831-dfa5a6
- role: executor
- git commit at launch: `47110d635ea646d09efeeb5fcd1f95b0b54a3481`
- git commit at report time: `06932d11d18e10d46afe5d2c8c19dd9b51c4ab85` (unrelated
  concurrent merges landed on the shared branch during the 6-hour run; see
  `output/environment.json.note_on_commit_drift`)

## Scope and starting state

This directory already contained driver scripts and `task_card.yaml` from a
prior session that never executed the run: `rt_ctrl_1_target.py`,
`rt_ctrl_1_supervisor.py`, `verify_telemetry_receipt.py`, and
`inputs/fplll_strategies_default.json`. Before executing anything, this
session re-verified every one of those files against the frozen hashes in
`task_card.yaml` and `experiments/EXP-MLKEM-980909/specification.yaml`:

| file | expected sha256 | measured sha256 | match |
|---|---|---|---|
| `rt_ctrl_1_target.py` | `c7d6571354247e2211095deec22c69a23530c036eaaa99d6fb2699d97f78b261` | same | yes |
| `rt_ctrl_1_supervisor.py` | `a76c365943eee549fc547fdf89dd611cbbe19c38c933d11192a79326325a86f9` | same | yes |
| `verify_telemetry_receipt.py` | `52e192c64f9b38e419079e1bee422f01e71f2f80d133514a64678c5622f0b027` | same | yes |
| `inputs/fplll_strategies_default.json` | `f516b0a6f0c580cff72e1e2c3562c44dc6f17e8f99613e9e4020e35481b27a18` | same | yes |

All four content-pinned bytes matched exactly. No worker or supervisor code
was edited. The scripts were used as-is; only the runtime toolchain and
launch command were adapted to this Linux host (see deviations below), since
the `task_card.yaml` command referenced a macOS path
(`/Library/Frameworks/Python.framework/...`, `/private/tmp/...`) that does
not exist here.

## Protocol deviations (recorded per AGENTS.md / agents/executor.md)

1. **Host/toolchain path deviation.** `task_card.yaml`'s recorded command was
   written for a macOS host with Python 3.13 at
   `/Library/Frameworks/Python.framework/Versions/3.13/bin/python3` and a
   `PYTHONPATH` under `/private/tmp/crypto-mlkem-control-repair-20260831/.runtime-deps`.
   Neither exists on this Linux container. This session used
   `/usr/bin/python3.13` (the system Python 3.13.12 present on this host) with
   the exact pinned package versions installed to its user site-packages
   (`pip install --break-system-packages --user`); no `PYTHONPATH` override
   was required. No frozen scientific parameter (d, beta, mpfr_bits, seed
   formula, strategy hash, wall-clock cap) was changed by this substitution.
2. **Undeclared transitive dependency.** The frozen constraint list names
   only `fpylll==0.6.4`, `numpy==2.4.0`, `psutil==7.2.2`. Importing the
   `fpylll` 0.6.4 manylinux wheel on this host raised
   `ModuleNotFoundError: No module named 'cysignals'` until `cysignals`
   (1.12.6) was additionally installed. This is an unstated build/runtime
   dependency of the pinned wheel, not a change to any frozen value.
3. **Yanked numpy release.** PyPI reports `numpy==2.4.0` (cp313-manylinux) as
   yanked ("Backward compatibility bug"). It was installed anyway because it
   is the exact version the frozen specification pins; this is recorded, not
   silently substituted for a different numpy version.
4. **Cap overshoot of ~1.4 seconds.** `terminal_receipt.json` records
   `elapsed_seconds: 21601.41` against a `wall_clock_seconds` cap of 21600.
   This is a supervisor polling-loop artifact (30-second `--sample-seconds`
   interval; the cap check runs once per iteration, not continuously), not a
   deviation from the pre-registered cap value or a retune.
5. **Unrelated concurrent branch activity.** `git rev-parse HEAD` moved from
   `47110d6...` at launch to `06932d1...` at report time because other
   sessions merged unrelated PRs into the shared branch environment during
   the ~6-hour run. All four content-pinned files for this task were
   re-hashed after the run and are byte-identical to their frozen values
   (table above / this run's own re-check). No pinned input was affected.

None of these deviations touch the frozen target parameters (d=512, beta=55,
mpfr_bits=100, seed formula, strategy hash, or the 21600-second cap), the
worker/supervisor/verifier code, or the strategy file bytes.

## Pre-target control: no-BKZ controlled-SIGTERM self-test

Run once, in a scratch directory outside `write_scope`
(`/tmp/rtctrl1_selftest`, not retained as a research artifact — it is a
pre-flight infrastructure check, not part of the one authorized target run):

```
/usr/bin/python3.13 rt_ctrl_1_supervisor.py \
  --worker rt_ctrl_1_target.py \
  --strategies inputs/fplll_strategies_default.json \
  --out /tmp/rtctrl1_selftest \
  --wall-clock 21600 --sample-seconds 2 --self-test-sigterm-after 8
```

Result: `terminal_cause: controlled_sigterm`, `exit_code: 143`,
`worker_state.json` stage `signal_received`, `terminal: true`. Independent
verifier (`verify_telemetry_receipt.py --expect-cause controlled_sigterm`)
returned `PASS: telemetry receipt, manifest, and hash chain verify` (exit
code 0). This satisfies completion-gate item 1 ("The no-BKZ controlled
SIGTERM self-test independently verifies before target launch").

## The one authorized target run

Launched 2026-09-08T02:01:19Z, exactly once, into the declared write_scope
output directory:

```
/usr/bin/python3.13 rt_ctrl_1_supervisor.py \
  --worker rt_ctrl_1_target.py \
  --strategies inputs/fplll_strategies_default.json \
  --out output \
  --wall-clock 21600 --sample-seconds 30
```

`target_manifest.json` (written by the supervisor before launch) pins
`d=512, beta=55, mpfr_bits=100, seed_formula: default_rng([715923,0,d,beta,0,0])`,
`strategies_sha256: f516b0a6f0c580c...`, `wall_clock_seconds: 21600`,
`worker_sha256: c7d657135424...` — all matching the frozen specification and
`task_card.yaml` exactly. `worker_state.json`'s `seed_used` field recorded
`452658293`, matching `experiments/EXP-MLKEM-980909/specification.yaml`
`replication.seeds: [452658293]`.

### Observed lifecycle

- `stage: started` → `environment_ready` → `basis_generation` (`seed_used:
  452658293`) → `outer_lll` → `gso` (`outer_lll_elapsed_seconds: 399.45`) →
  `bkz` (`gso_float_type_used: mpfr`).
- The worker remained in `stage: bkz` for the remainder of the run. No
  `worker_result.json` was ever written — the worker's single call to
  `bkz(params)` (`BKZReduction(...)` with `flags=BKZ.AUTO_ABORT`, block size
  55) had not returned by the cap.
- At `elapsed_seconds ≈ 21600`, the supervisor sent `SIGTERM` to the worker's
  process group (`terminal_cause: hard_cap`). The worker's own SIGTERM
  handler wrote a final `worker_state.json` (`stage: signal_received`,
  `signal: SIGTERM`, `terminal: true`) and raised `SystemExit(143)`; the
  supervisor observed `exit_code: 143` and no leftover process (verified via
  `ps -ef` after the run: no matching PIDs).
- 721 `sample` events were recorded at ~30-second intervals plus
  `child_started`, `signal_sent`, and `terminal_receipt_written` events (724
  lines total in `events.jsonl`).
- Final sample before termination: `cpu_user_seconds: 21599.33`,
  `cpu_system_seconds: 0.67`, `rss_bytes: 151351296` (~144 MiB) — consistent
  with a single-threaded process using nearly all of its wall-clock time as
  CPU time, with no runaway memory growth over the run.

### Terminal receipt

```json
{
  "elapsed_seconds": 21601.408611689003,
  "exit_code": 143,
  "terminal_cause": "hard_cap",
  "target_manifest_sha256": "80891ff8448627ffe53d7f83f7219922b969a1ab080c96efed597ed8db329168",
  "worker_result_exists": false,
  "worker_state_exists": true,
  "terminal": true
}
```

### Independent verification

`verify_telemetry_receipt.py --out output --expect-cause hard_cap` (a
separate process, imports no writer code) returned:

```
PASS: telemetry receipt, manifest, and hash chain verify
```

exit code 0 — the manifest digest, the terminal cause, and the full 724-event
hash chain all verified independently. This satisfies completion-gate item 2
("Exactly one terminal receipt exists and its manifest preserves every frozen
target-defining value").

## Classification (per agents/executor.md failure taxonomy)

This run is **not** classified as a failure of any kind. It is a
`negative_observation`-adjacent lifecycle observation exactly as anticipated
by `DEC-20260831-dfa5a6`'s `decision_branches.hard_cap_or_signal`: "snapshot
as failed_infrastructure/resource outcome; no mathematical inference." The
BKZ-55 tour at d=512 did not return within the 21600-second cap under this
single-threaded `fpylll` 0.6.4/MPFR-100 implementation on this host. This is
an implementation/resource-budget observation about the tested configuration,
not evidence for or against any mathematical hypothesis, and it makes no
claim about ML-KEM, FIPS 203 parameters, or attack cost — exactly the scope
`EXP-MLKEM-980909.falsification_criterion` and `scale_relevance` already
state. No certificate is claimed (`certificate.kind: none` — this run never
reached a discrete-log/relation solve; it is a pure lifecycle/telemetry
measurement) and none is required.

## Completion gate check

- [x] No-BKZ controlled SIGTERM self-test independently verified before
      target launch.
- [x] Exactly one target run was started, under the fixed cap (21600 s),
      exactly once (`maximum_runs: 1`).
- [x] All terminal artifacts are retained: `target_manifest.json`,
      `events.jsonl`, `worker_state.json`, `terminal_receipt.json`,
      `stdout.log`, `stderr.log`, `environment.json`. `worker_result.json`
      does not exist because the worker never returned before the cap
      (expected and explicitly allowed by
      `experiments/EXP-MLKEM-980909/specification.yaml`:
      "`worker_result.json` when worker returns").
- [x] Raw event stream, worker_state.json, and terminal_receipt.json agree
      (independently re-verified above).
- [x] Reproducible from the recorded command, pinned code/strategy hashes,
      and the recorded git commits, modulo the two Linux-host tool-path
      adaptations recorded above as deviations (no scientific parameter
      changed).

## Not done here (explicitly out of scope)

- No second target was run.
- No worker, supervisor, or strategy byte was edited after the self-test.
- No ledger record was edited and no commit was made to the shared worktree.
- No conclusion is drawn about BKZ-55/d=512 feasibility, ML-KEM security, or
  any cost model — see Classification above.
