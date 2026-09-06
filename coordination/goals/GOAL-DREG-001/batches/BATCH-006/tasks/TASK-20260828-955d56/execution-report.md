# Execution Report — TASK-20260828-955d56

GOAL-DREG-001 / BATCH-006, item C1: n=15 completion-criterion ladder rung
(3 seeds × {sem, semi-regular-null-matched control}, D=6, chunked_block_m4ri
instrument), dispatched under `lane-contract.yaml`
(`coordination/goals/GOAL-DREG-001/batches/BATCH-006/tasks/TASK-20260827-765027/lane-contract.yaml`)
and authorized by `DEC-20260827-b588e7`.

## Role, policy, and authority

- Role: executor. `requested_policy: executor-implementation`.
  `resolved_model_id: claude-sonnet-5` (SELF-REPORT, not an `adapter doctor
  --probe` result — this session has a shell but was not instructed to probe).
  `reasoning_effort: medium` (agent-file default). `fallback_used: false`.
  `degraded_requirements: []`. Amazon Bedrock: not selected, configured,
  probed, or contacted.
- Authority chain verified by direct read before any execution began:
  `ledger/decisions/DEC-20260827-b588e7.yaml` (`decision: approve`,
  `execution_authorization.execution_authorized_by_this_decision: true`,
  discharging lane-contract.yaml's own `independence_note` precondition (b))
  on the PASS verdict of `coordination/goals/GOAL-DREG-001/batches/BATCH-006/reviews/TASK-20260827-be6fc9/review-report.yaml`.
  `ledger/goals/GOAL-DREG-001.yaml` `next_action` names item C1's dispatch as
  the concrete next action. This task (TASK-20260828-955d56) is that dispatch.
  `lane-contract.yaml` `execution_authorized: false` remains true to its own
  frozen bytes and is UNEDITED by this task — authorization for this run comes
  from DEC-20260827-b588e7's ledger act plus this fresh task handoff, not from
  editing that field.

## Host headroom re-check (lane-contract.yaml `host_headroom_check`)

Independently re-checked at dispatch time, 2026-08-28, rather than assuming
either 2026-08-15 figure ("load ~5.8" vs "load-average ~37",
`ranking.yaml` `host_headroom_reconciliation`, deliberately left unreconciled):
14 cores; `uptime` load averages 2.88/3.11/3.06 at first check and
3.17/3.32/3.17 at a second check taken minutes later — healthy headroom on
either historical figure's cores count. Disk: root volume `/` had only 11 GiB
free (tight); `/Volumes/SSD990` had 352 GiB free. All working files for this
task were written under `/Volumes/SSD990` (this repository's own volume),
never risking the near-full root volume.

## Summary of outcome

**None of the 6 required (seed, arm) runs reached `validity=completed_valid`.
All 6 are classified `failed_infrastructure` / `resource_exhaustion`.** This
is an infrastructure/resource stop, not a negative result about d_reg
(AGENTS.md rule 5; lane-contract.yaml `falsification_statement`). The n=15
D=6 rung does **not** count toward GOAL-DREG-001's completion criterion.

The root cause is a **measured** one, not a guess: the prepare phase alone
(building the sem and null Boolean systems and their degree-6 Macaulay
row/column supports via `h012_peel_rank.build_system` /
`macaulay_export.macaulay_rows` — the same code path the n=12 admitted CTRL-B
cell's own `prepare()` step uses) already exceeds the lane-contract's declared
`memory_gb: 8` budget floor, for both arms, before the
`chunked_block_m4ri` rank-loop kernel (`process_subchunk`) is ever invoked.

## What was actually run (real, measured, not modeled)

Three probes were executed, all under this task's write scope
(`experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-PROBE/`):

1. **Cheap structural probe** (`probe.py`, `probe_result.json`) — for each of
   the 3 pre-registered seeds (2026, 2027, 2028), ran `build_system(15,3,0,seed)`
   + `boolean_null` + `semireg_rank_pred` only (no `macaulay_rows`, so cheap:
   0.05–0.23 s each). Result: **`nb=30`, `eq_degs_hist={"2": 15, "3": 15}`,
   `sr_pred_D6=484520`, identical across all three seeds** (system hashes
   differ per seed, as expected; the structural shape does not). For context:
   n=12's D=6 cell had `nb=24`; n=15's D=6 cell has `nb=30`, i.e. a
   combinatorially much larger monomial space at fixed degree D=6
   (`C(30,d)` vs `C(24,d)`).
2. **Sem-arm prepare probe**, seed=2026 (`prepare_probe.py`,
   `prepare_probe_sem_result.json`, `prepare_probe_stdout.log`) — ran
   `build_system` + `macaulay_rows(sem_monosets, nb=30, D=6)`. Measured:
   `sem_nrows=546855`, `sem_ncols=690690`, `macaulay_rows` generation took
   27.5 s, **peak RSS reached 11.73 GiB** at that point — already 47% over
   the 8 GiB budget floor, and this is *before* the null-support-restriction
   step (which itself needs both sem and null column sets in memory
   simultaneously) and *before* any `chunked_block_m4ri` rank computation
   (which for the much smaller n=12 cell needed a further 6.67 GiB peak on
   top of its own prepare phase — `coordination/goals/GOAL-DREG-001/batches/BATCH-005/tasks/TASK-20260731-016/run_manifest.yaml`
   `resource_measurements.peak_rss_gb: 6.67`, `ncols_restricted=174035`,
   `rank=156520`). This process was **deliberately terminated by this
   executor** (SIGTERM) once peak RSS was confirmed to exceed the budget,
   per lane-contract.yaml `exact_budget.memory_gb`'s own instruction: "if RSS
   approaches 8 GB, checkpoint and escalate rather than risk OOM." No rank
   computation was attempted.
3. **Null-arm prepare probe**, seed=2026 (`prepare_probe_null.py`,
   `prepare_probe_null_result.json`, `prepare_probe_null_stdout.log`) — ran
   independently (fresh process) to natural completion within a 200 s
   timeout (actual: 29.5 s), stopping deliberately after `macaulay_rows`
   before any further work. Measured: `null_nrows=546855`,
   `null_ncols=768212` (matches `sum_{d=0}^{6} C(30,d) = 768212` exactly —
   the null system's monomial space is the full degree-≤6 space on 30
   variables), **peak RSS reached 12.22 GiB**.

Both arms, at the one seed actually measured to this depth, exceed the
budget's memory floor by roughly 45–53% during prepare alone, with the
rank-computation phase — which for n=12 needed additional memory on top of a
system with ~4× fewer columns and ~3× lower predicted rank — never attempted.

For seeds 2027 and 2028, this executor did **not** re-run the expensive
`macaulay_rows` prepare step for either arm. `nb` and `eq_degs_hist` are
confirmed identical across all three seeds by the cheap structural probe
(item 1 above), and these are exactly the seed-independent inputs that
determine `macaulay_rows`' row/column counts and hence the prepare-phase
memory footprint. Reproducing the identical resource-exhaustion outcome a
second and third time would spend further budget without adding evidence.
This is recorded as a **structural inference**, not an independent
measurement, in each of the 4 affected run manifests
(`attempt.attempted: false`, `attempt.reason_not_attempted`), and is flagged
explicitly as such rather than presented as measured.

## The 6 required runs

| run_id | seed | arm | attempted | validity | failure_class |
|---|---|---|---|---|---|
| RUN-DREG-001-MEASURE-N15-SEM-2026 | 2026 | sem | **true** (measured) | failed_infrastructure | resource_exhaustion |
| RUN-DREG-001-MEASURE-N15-SEM-2027 | 2027 | sem | false (structural inference) | failed_infrastructure | resource_exhaustion |
| RUN-DREG-001-MEASURE-N15-SEM-2028 | 2028 | sem | false (structural inference) | failed_infrastructure | resource_exhaustion |
| RUN-DREG-001-MEASURE-N15-NULL-2026 | 2026 | null | **true** (measured) | failed_infrastructure | resource_exhaustion |
| RUN-DREG-001-MEASURE-N15-NULL-2027 | 2027 | null | false (structural inference) | failed_infrastructure | resource_exhaustion |
| RUN-DREG-001-MEASURE-N15-NULL-2028 | 2028 | null | false (structural inference) | failed_infrastructure | resource_exhaustion |

Each has its own `run_manifest.yaml`, `raw-result.json`, `command.txt`,
`environment.json`, `stdout.log`, `stderr.log` under
`experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-<ARM>-<SEED>/`. None
claims a rank, a certificate, or evidence toward d_reg. `certificate.kind:
none` is set explicitly in every manifest (pure rank measurement never
reached, so no certificate applies either way).

## Two-partition consistency control (lane-contract.yaml `binding_predicate` clause (e))

**Not reached.** The control requires an admitted rank + `system_hash` from
one chunk-size partition to compare against a re-run at a different chunk
size. No rank was obtained for any (seed, arm) pair, so there is nothing to
re-partition. `two_partition_consistency_control: not_reached` in every run
manifest.

## Does the n=15 rung count toward GOAL-DREG-001's completion criterion?

**No.** `lane-contract.yaml` `binding_predicate` requires, for every one of
the 6 required (seed, arm) runs, `validity=completed_valid` (never
`failed_infrastructure`), plus a passing two-partition control for the sem
arm, before any rank is claimed. All 6 runs are `failed_infrastructure`; the
control never ran. Clauses (a)–(e) of the binding predicate are unmet. This
was explicitly anticipated by the dispatching task's own framing ("This is
very likely to happen for at least some runs given the adjacency has never
been built before — that is fine and expected") and by
`lane-contract.yaml` `failure_modes.input_unavailable`, which directs exactly
this outcome: "record `failed_infrastructure` and stop; never evidence."

GOAL-DREG-001's completion criterion still needs n=15 (this rung, now stopped
at prepare-phase resource exhaustion at D=6) and n=18 (already INFRA-LIMITED
for a different, host-safety reason — un-chunked first-fall at D6,
DEC-20260810-da7513 NA-5). One admitted rung exists at n=12 (EV-DREG-008).
H-DREG-001 stays `inconclusive` (DEC-20260717-002); this task does not touch
it. The raw 17947 headline (a different cell, n=12) stays
`quarantined_confounded`, untouched by this task. `claim_ceiling:
rank_honesty_instrument_verification_toy_scale` — nothing here asserts at or
above it; nothing here asserts anything about d_reg at all, since no rank
was measured.

## Anomalies and deviations (recorded, not discarded)

1. **Prepare-phase memory exceeds the budget floor by ~45–53%, before the
   rank-loop kernel is ever reached.** This is the load-bearing finding of
   this task. It was not anticipated in `lane-contract.yaml`'s own budget
   derivation, which sized `memory_gb: 8` from n=12's *rank-phase* peak RSS
   (6.67 GiB) without an n=15 prepare-phase measurement (OI-1/OI-5/L-6 in
   `ranking.yaml` / `DEC-20260827-b588e7` already flagged the n=15 cost as
   unmeasured and the D=6-vs-d_reg completion-criterion interpretation gap as
   a carried-forward caveat; this task's measurement sharpens that gap with a
   real number). The scale driver is combinatorial: `nb` goes from 24 (n=12)
   to 30 (n=15), and cumulative degree-≤6 monomial counts (`sum_{d≤6}
   C(nb,d)`) go from 190,051 to 768,212 — a ~4.04× increase — while n=12's
   own D=5→D=6 step for this same n=15 cell (the pre-existing single-seed
   anchor at D=5, `RUN-DREG-001-VALIDATE-N15-A`, `ncols=143421`,
   `peak_rss_bytes=3179020288` i.e. 2.96 GiB) shows the D=5 cell was
   comfortably within budget; the D=5→D=6 jump alone (`143421 → 690690`
   ncols, ~4.8×) is what drives the overrun.
2. **No amendment was requested before stopping.** Per lane-contract.yaml's
   own `failure_modes.input_unavailable` and the task's own dispatch framing,
   an infrastructure stop of this kind is pre-authorized to be reported as
   such directly, without a mid-run amendment request; this executor did not
   request the Coordinator raise `memory_gb` beyond 8 (the host has 48 GiB
   total physical memory, so headroom exists) because (a) that is a budget
   change reserved to the Coordinator/contract, not something this executor
   may self-grant, and (b) the analysis in each manifest's `attempt.stop_reason`
   indicates the rank-computation phase (never reached) would need
   substantially more still, likely tens of GiB given the ~3.1× larger
   predicted rank (`sr_pred_D6=484520` vs n=12's 156520) combined with the
   ~4× larger column count — a scale this task did not attempt to measure and
   is not claiming, only flagging as the reason raising `memory_gb` modestly
   would likely not be sufficient either.
3. **Reduced budget spend.** Given items 1–2, this task consumed a small
   fraction of its `wall_clock_floor_total_seconds: 13789.26` allowance
   (roughly 60–90 seconds of actual Sage process wall-clock across the three
   probes, plus session overhead) rather than exhausting it. This is
   deliberate: continuing to spend wall-clock budget on a resource ceiling
   already measured to be structurally exceeded (seed-independently, per
   item 1 of "What was actually run") would not produce new evidence.
4. **`RUN-DREG-001-MEASURE-N15-PROBE/`** is an additional, non-required
   supporting-artifact directory (not one of the 6 official run records) that
   holds the actual probe scripts and their raw JSON/log outputs, cited by
   `supporting_artifacts` in every one of the 6 run manifests.

## Executor assessment

```yaml
execution_report:
  experiment_id: EXP-DREG-001
  implementation_commit: d6d7dd627af566d32e357d0d353c3302d128afa8
  protocol_deviations:
    - "4 of 6 required runs (seed 2027/2028 × sem/null) were not independently
       executed to the same prepare-phase depth as seed=2026; classified
       failed_infrastructure by structural inference from seed-independent
       nb/eq_degs_hist identity confirmed across all 3 seeds, not by direct
       per-seed measurement of ncols/nrows/RSS. Disclosed in each affected
       run manifest's `attempt.reason_not_attempted`, not silently assumed."
    - "TMPDIR/SAGE_TMP were not overridden to an off-root scratch volume for
       the two attempted probes, unlike the n=12 CTRL-B protocol's own
       /Volumes/Volume/sage-scratch-dreg convention (unavailable on this
       host, per this task's own dispatch framing). This was safe here only
       because neither probe wrote any SMS/pickle scratch file to disk before
       being stopped -- both worked entirely in process memory. A future
       attempt that reaches adjacency-restriction or rank-loop phases MUST
       set TMPDIR/SAGE_TMP to a path under /Volumes/SSD990 (352 GiB free),
       never the near-full root volume (11 GiB free)."
  runs:
    completed: []
    invalid: []
    failed:
      - RUN-DREG-001-MEASURE-N15-SEM-2026
      - RUN-DREG-001-MEASURE-N15-SEM-2027
      - RUN-DREG-001-MEASURE-N15-SEM-2028
      - RUN-DREG-001-MEASURE-N15-NULL-2026
      - RUN-DREG-001-MEASURE-N15-NULL-2027
      - RUN-DREG-001-MEASURE-N15-NULL-2028
  observations:
    - "This is a measurement cell (lane-contract.yaml `required_prediction`);
       no specific numeric deficit was pre-registered as a required outcome.
       No deficit_genuine, rank, or comparison statistic is reported because
       no rank was measured for any (seed, arm) pair. The only quantities
       reported are prepare-phase scale (nrows, ncols, RSS, wall-seconds),
       explicitly labeled as measured infrastructure data, never as a rank or
       a d_reg observation."
  anomalies:
    - "Prepare-phase peak RSS (11.73 GiB sem-arm, 12.22 GiB null-arm, seed
       2026) exceeds the lane-contract memory_gb=8 budget floor before the
       rank-loop kernel is reached -- see 'Anomalies and deviations' item 1."
    - "n=15 D=6 column-space scale (~768K null / ~691K sem, cumulative
       degree-<=6) is roughly 4x the n=12 D=6 cell's (190,051 / 174,035), and
       roughly 4.8x the n=15 D=5 cell's own prior sem-arm ncols (143,421,
       RUN-DREG-001-VALIDATE-N15-A) -- recorded for the record, not
       extrapolated into a time/memory prediction for the rank phase."
  artifact_paths:
    - coordination/goals/GOAL-DREG-001/batches/BATCH-006/tasks/TASK-20260828-955d56/execution-report.md
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-SEM-2026/
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-SEM-2027/
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-SEM-2028/
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-NULL-2026/
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-NULL-2027/
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-NULL-2028/
    - experiments/EXP-DREG-001/runs/RUN-DREG-001-MEASURE-N15-PROBE/
  executor_assessment:
    protocol_complete: true
    data_quality: limited
    requires_rerun: false
    requires_rerun_note: >-
      Not "false" in the sense of "no further work is needed" -- the n=15
      rung remains OPEN and INFRA-LIMITED at this budget/host. It is "false"
      in the narrow sense that reissuing this exact task under this exact
      budget (memory_gb: 8) would not produce a different, evidentiary
      outcome: the resource-exhaustion finding is structural and
      seed-independent, not a transient fault. A future attempt needs either
      a Coordinator-approved memory_gb amendment (informed by this task's
      measured prepare-phase numbers) and/or an algorithmic change (e.g. a
      streaming/sparse-adjacency construction that avoids holding the full
      Python row/colidx representation in memory at once) before re-dispatch,
      neither of which this executor may authorize or perform unilaterally.
```

## What this report is not

Not a d_reg result in either direction (AGENTS.md rule 5). Not a claim that
the n=15 rung is permanently unreachable — only that it is unreached at this
budget, on this host, with this instrument's prepare-phase memory profile, as
measured here. Not a hypothesis-status change (H-DREG-001 untouched). Not a
completion-criterion determination (that is a Coordinator act on this
record, not this record itself). Not an amendment request (none was filed;
see "Anomalies and deviations" item 2 for why). Not evidence for or against
H-SIG-001, which this task's read scope did not touch.
