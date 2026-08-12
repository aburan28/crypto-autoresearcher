# TASK-20260729-044 — Implement the EXP-STR-004 driver and Sage verifier and execute all fourteen named cells on both arms

**MIRROR ONLY.** The authoritative card is the `tasks[]` entry with this id in
the BATCH-014 `dispatch_queue.json`. Where they disagree, the queue governs.

- **Role:** executor
- **Depends on:** TASK-20260729-042, TASK-20260729-043
- **Archived by:** TASK-20260729-045
- **Budget:** 7200 s wall clock, 8 GB, `maximum_runs: 28`
- **Inference policy:** `executor-implementation`. The adapter's resolution and
  the session's self-reported model have disagreed before in this campaign —
  **record both honestly and substitute neither.**

## Objective — observe only, interpret nothing

Produce **exactly 28 run records** (arm A-prime and arm E-prime at each of the
fourteen named cells), each carrying the measured alpha, the measured
misalignment set, the predicted set, their symmetric difference, the
suppression count, the base-row count, the sha256 of the factor base and of the
final row list, and the decomposition certificates of every base row; then
verify every certificate in **one** Sage invocation through the `sage` binary.

**The contract governs.** Where this card and
`experiments/EXP-STR-004/specification.yaml` differ, the contract governs and
the difference is **reported**, not resolved by preference. The
TASK-20260729-043 receipt's numbered pre-dispatch conditions bind this
execution; record how each was met.

## Absolute prohibitions

- **Never modify anything under `harness/`.** The committed harness is the
  object of measurement. If a harness defect blocks a cell, record it and stop
  that cell — a repair needs a protocol amendment and this card has none.
- **Never call `harness.endomorphism_la.main()`**, in process or as a
  subprocess. It raises `IndexError` at `endomorphism_la.py:451` whenever
  `B mod 3 != 0` with relations present — true of **seven of the fourteen**
  declared cells — and it cannot express either arm.
- **Call the committed measurement functions rather than reimplementing them.**
  Implement only the two closures and the misalignment-set computation.
  Reimplementing `_measure_displacement_rank` would measure a different object.
- **Compute every instance parameter; transcribe none.** A mismatch against a
  prior record is a **finding to report**, never grounds for overriding the
  computed value.

## The controls that make this a replication

- **Matched base-row budget:** both arms collect exactly `R_base(cell)` base
  rows before any closure. A shortfall is recorded **naming the cell and the
  arm**, and that cell is excluded from the comparative criteria. Do **not** top
  up one arm alone.
- **Both closures unconditional** — no dedup, no zero filter. Record the
  suppression count anyway; a **nonzero** value is a finding to report.
- **Report sets, not counts.** Emit predicted set, measured set, symmetric
  difference and both sorted member lists per cell and arm. Where you report a
  count, say it is a count and name its members. A cardinality match with a
  different member set is `cardinality_only_agreement` and **must not** be
  reported as agreement.

## Sage

- Capture `sage --version` **exactly once, before the first computation**, and
  record the exact string verbatim in all 28 manifests and in
  `results/certificate_verification.json`, with the statement that it is **one
  capture reused verbatim**.
- If the string does not name **SageMath 10.9, release date 2026-05-04**, or the
  binary is absent, fails to start, or exits nonzero: **STOP AND REPORT. That is
  infrastructure signal and never a mathematical result in either direction.**
- **Invoke through the `sage` binary, never as a Python import** — `import sage`
  from the system python3 fails on this host. One batched invocation over all
  cells; record the exact command in `command.txt`.
- The verifier reconstructs each curve as `EllipticCurve(GF(p),[a,b])` and
  re-verifies with **Sage's own arithmetic** — it must not import, call or
  replicate `harness/toycurve.py`.
- A failed certificate makes that run `completed_invalid` with
  `invalid_reason: certificate_failed` — an **invalid_measurement**, not a
  negative observation, and not evidence against anything.
- **Appended rows are not claimed as relations by either arm.** They carry
  certificate kind `none` with the reason recorded.

## Budgets and what a breach means

- **Pre-flight disk check before the first write.** Record the exact free-space
  figure. **Below 5 GiB: stop and report, write no run records.** The volume is
  at 99% with about 30 GiB free and `git fsck` has already timed out on it.
- **2 MiB per run directory:** on breach, write the two sha256 values, omit the
  full dumps, record `DEV-SIZE-1` naming the exact cells, continue. **Never
  write a truncated JSON document.**
- **64 MiB tree:** on breach, stop; every unreached cell is
  `cancelled_by_budget` with its full six-file set; report which named cells
  were not reached.
- **900 s per run / 7200 s total / 900 s Sage.** A breach terminates that unit
  and is recorded as **infrastructure signal** with the terminal status in the
  manifest — never a measurement, never a zero, never a negative result.

## Artifact policy

All six files in every run directory **even for a cancelled, failed or invalid
run**. Distinct non-overlapping per-run timing windows (reusing one window is
the EXP-STR-002 defect D6 and is forbidden). `numpy.__version__` explicitly in
every `raw-result.json`. The sha256 of all four harness sources in every
`raw-result.json`; all 28 must agree. Abort if the tracked tree is dirty with
respect to `harness/`.

**Write an executor task receipt and populate it.** UC-4 of EV-STR-003 records
that no executor receipt exists for TASK-20260727-021, so five disclosed
deviations live in no durable artifact. Every deviation, ambiguity and judgement
call goes in `results/run_index.json` under a **named identifier**, with a what,
an effect and a conservative reading. Declaring an ambiguity and naming its
blast radius is the required behaviour; applying a reading silently is not.

## Make no commit

TASK-20260729-045 commits this package. Write nothing under `ledger/`,
`knowledge/`, `coordination/`, `harness/` or `tools/`. Make no claim about
H-STR-002's mechanism, no cost claim, no scaling law, no statement about
`B > 193` or `field_bits > 16`, and no rho or BSGS comparison.
