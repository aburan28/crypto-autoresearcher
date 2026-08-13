# TASK-20260812-0e930c — RIDER (iii): the fpylll-equipped L7/L8 replication

    goal / batch      GOAL-MLKEM-005 / BATCH-4ed139
    role              executor — OBSERVATIONS ONLY, no conclusion is drawn here
    governed by       PREREG-1 section 8.3 (routes RC/RD of 2.5), frozen and
                      notarized at commit 8d72f2c03 by TASK-20260812-1ed548
    depends on        TASK-20260812-b581a8 (the lead's snapshot, commit 3aac83fd8)
    archived by       TASK-20260812-b53c2f
    claim tier        TOY, UNCONDITIONALLY
    outcome row       R2-OUT-8

## 0. WHAT THIS IS, AND WHAT IT IS NOT — THE FROZEN FRAMING, FIRST

**This RESTORES THE COVERAGE WAVE 2 LOST. It RESOLVES NO DOUBT, THERE BEING NONE
TO RESOLVE.** fpylll was absent in both wave-2 review sessions and in this
batch's lead producer. That absence is **INFRASTRUCTURE SIGNAL** (AGENTS.md rule
5) and was **NEVER** evidence against `lam1n`, `hkz`, the 48 reductions, or their
reported max `hkz_violation` of 0.0.

The values below reproduce. **That vindicates nothing and impugns nothing.** It
is a replication of quantities nobody doubted, and it is exactly what was already
expected. The honest position it improves on, from DEC-20260812-7c4a1e, is a
coverage position and not a credence one: the reduction-dependent quantities had
**one re-execution** (wave 1, through the producer's own code on the producer's
own machine, which cannot catch a specification error) and **zero independent
re-implementations** in either wave. This run adds one re-implementation —
textually distinct code, the same frozen pipeline — on **the L7/L8 arm only**.

## 1. WHAT WAS RUN

fpylll pinned at **0.6.4** was installed into a virtualenv **outside the
repository**; the 8 frozen bases of family F0 were rebuilt at **L7 (d = 20,
k = 6)** and **L8 (d = 20, k = 14)** and verified against the notarized text
before any reduction; the frozen HKZ pipeline (route RD) was run once per basis;
`hkz` was taken at the frozen beta grid **{5, 10, 15}** and `lam1n` once per
basis; each value was compared to the **committed per-basis value** of
`results_relvar.json` (route RC), which was read only and never edited.

PREREG-1 was re-verified in both directions before any measurement: working tree,
committed sidecar and the blob inside notarizing commit
`8d72f2c038a577e216ab9d6d0e5995f65d5ff819` all hash to
`dc04d640737e6f15c40d9afdba919e75a72e52ee6510cbbbba16678d24af4c62`; the text is
absent at that commit's parent; the commit is an ancestor of HEAD.

## 2. THE RESULT — MEASURED

| quantity | measured |
|---|---|
| comparisons made | **96** (2 candidates x 2 lattices x 3 betas x 8 bases) |
| **MAX ABSOLUTE DEVIATION** | **0.0** |
| bit-identical (IEEE-754 hex) | **96 of 96** |
| **P-L1** (falsifier: max abs deviation > 1e-6) | **HOLDS** |
| reductions run | 16, all `status: ok`, `gram_int_dev` 0.0 at every one |
| **max `hkz_violation` measured here (L7/L8 arm)** | **0.0** |
| rows handed to fpylll, per basis | **20** |
| reduction wall clock | 0.054 s total; script total 0.359 s |
| peak RSS | 62,197,760 bytes (0.058 GiB) against a 4 GB budget |

The committed figure `max_hkz_violation_overall = 0.0` in `results_relvar.json`
is a maximum over **all** of that run's reductions (L7, L8, L9, L10, L11, L12).
The 0.0 above is over the **L7/L8 arm only**. They are reported side by side and
are **not the same quantity**.

## 3. THE COMPARISON, PER CELL AND PER BASIS

Every cell: max |deviation| = 0.0, bit-identical 8 of 8. The committed value is
printed; the re-measured value is bit-identical to it in every entry, so one
column carries both.

`hkz` — committed = re-measured, per basis i = 0..7:

| cell | i0 | i1 | i2 | i3 | i4 | i5 | i6 | i7 |
|---|---|---|---|---|---|---|---|---|
| L7 beta 5 | -0.172674255604 | -0.192957996853 | -0.238829770096 | -0.172240421188 | -0.186492268906 | -0.224257946997 | -0.202621848231 | -0.211938969567 |
| L7 beta 10 | -0.127351161805 | -0.127769979944 | -0.149898629473 | -0.116556096606 | -0.132967973158 | -0.129236848158 | -0.116258705245 | -0.133314351951 |
| L7 beta 15 | -0.066050827267 | -0.066559175631 | -0.072426747492 | -0.049740067772 | -0.061866326675 | -0.060898070346 | -0.045586048401 | -0.058947037474 |
| L8 beta 5 | -0.242366239089 | -0.228310668668 | -0.185659051181 | -0.142364515997 | -0.209447718207 | -0.251473316728 | -0.194105660157 | -0.156502932847 |
| L8 beta 10 | -0.144102081592 | -0.139178085936 | -0.119684375637 | -0.097483484368 | -0.143367289162 | -0.155446717287 | -0.120019406123 | -0.108863164408 |
| L8 beta 15 | -0.068708830968 | -0.077550990011 | -0.056403131952 | -0.051083161349 | -0.067718442442 | -0.067337130222 | -0.058271268529 | -0.055280277328 |

`lam1n` — committed = re-measured, per basis i = 0..7:

| cell | i0 | i1 | i2 | i3 | i4 | i5 | i6 | i7 |
|---|---|---|---|---|---|---|---|---|
| L7 | 1.201575050842 | 1.255623139126 | 1.275452332762 | 1.128965887870 | 1.197678436332 | 1.215471484798 | 1.215129264781 | 1.207406096857 |
| L8 | 1.295788461067 | 1.286841598295 | 1.113573274613 | 1.183972337115 | 1.130732579268 | 1.209713875126 | 1.034697170786 | 1.157658555204 |

`lam1n` takes no beta argument, so its value is measured once per basis and
compared at all three beta cells; the re-measured value was checked to be
identical across beta 5, 10 and 15 and it is. Those 48 comparisons are therefore
**48 comparisons over 16 distinct measured values**, and that is stated rather
than left for a reader to infer from a count. The 48 `hkz` comparisons are over
48 distinct measured values.

Per-basis reduction metadata (`status`, `hkz_violation`, sweeps, `gram_int_dev`,
seconds, rows passed to fpylll) is in `results_l7l8.json` under `reduction`. All
16 report `status: ok`, `hkz_violation` 0.0 and `gram_int_dev` 0.0; the explicit
HKZ sweep loop terminated after 0 additional sweeps at 12 of 16 bases and 1 at
four (L7/i2, L8/i1, L8/i5, L8/i7).

## 4. AM-9, APPLIED AND STATED

**fpylll's `k` counts the q-scaled rows, NOT the identity block.** Here
`k = |K_I|` = the identity block throughout: L7 `k = 6`, L8 `k = 14`; fpylll's
`k` would be `k_fpylll = d - k`, i.e. 14 and 6.

**The row count passed to fpylll is 20, for every basis, at both lattices**, and
the reason is structural rather than nominal: what is handed to fpylll is the
**full d x d integer Gram matrix** `G = B B^T` with `d = 20` rows — all of them,
never `k` rows and never `d - k` rows. No fpylll basis generator is called
anywhere; each basis is built explicitly as `[[I_k, A], [0, q I_{d-k}]]` in exact
integer arithmetic. fpylll is therefore never asked to interpret a `k` at all,
and the convention cannot drift on a label. `rows_passed_to_fpylll: 20` is
recorded per basis in `results_l7l8.json`.

The basis construction was verified block by block against PREREG-1 section 2.3
(family F0) **before** any reduction: shape, int64 dtype, `I_k` top-left, `A_i`
top-right equal to `default_rng([1,d,k,i]).integers(0,q,(k,d-k))`, zero
bottom-left, `q I_{d-k}` bottom-right, `A` entries in `[0, q-1]`, and
`log|det B|` equal to the closed form `(d-k) log q`. All 16 pass.

## 5. ENVIRONMENT — RECORDED IN FULL, AND THE CROSS-PLATFORM QUESTION SETTLED AS MEASURED

| field | this run | producer (committed, BATCH-9e3584) | same? |
|---|---|---|---|
| operating system | Linux-6.18.5-fc-v20-x86_64-with-glibc2.39 | Linux-6.18.5-fc-v20-x86_64-with-glibc2.39 | yes |
| architecture | x86_64 | x86_64 | yes |
| python | 3.11.15 | 3.11.15 | yes |
| numpy | 2.4.6 | 2.4.6 | yes |
| scipy | 1.17.1 | 1.17.1 | yes |
| fpylll | 0.6.4 | 0.6.4 | yes |
| BLAS thread caps | all five set to 1 | all five set to 1 | yes |

**`ENVIRONMENTS_DIFFER = False`, measured.** Every recorded field agrees.
Therefore **no cross-platform claim is made or is available from this run**, and
the bit-identity of 96 of 96 values is unsurprising on an identical stack and is
reported as such. PREREG-1 11.1 stands: the **"genuinely cross-platform"** reading
of the L7/L8 agreement is **NOT CITABLE**; the citable form is a **PORTABILITY**
result across three textually distinct implementations with fpylll pinned at
0.6.4. What this run adds is the third textually distinct implementation, not a
second platform.

One environment fact is measured here that no earlier record contains, and it is
reported because it bears on what "fpylll 0.6.4" pins: pip resolved a prebuilt
manylinux wheel that **vendors its own** `libfplll-7d3e1bd4.so.9.0.0`, `libgmp`
and `libmpfr` under `site-packages/fpylll.libs`, and `fpylll.config` reports
**fplll 5.5.0**, `have_qd False`. The system `libfplll-dev 5.4.5-1.1build1`
installed by apt in the same step is consequently **not** the fplll this run used.
The producer's committed environment block records `fpylll: 0.6.4` and **records
no fplll version at all**, so whether the two runs used the same fplll is
**UNKNOWN** and is not asserted in either direction.

## 6. FAILURE CLASSIFICATION AND DEVIATIONS

No `specification_error`, no `implementation_error`, no `resource_exhaustion`, no
`invalid_measurement`, and no `negative_observation`. Recorded anyway, in full:

* **INV-4, a failed invocation.** The measurement command was first issued
  wrapped in `/usr/bin/time -v`, which does not exist on this host: exit 127,
  `"/bin/bash: line 1: /usr/bin/time: No such file or directory"`. It ran no
  Python and produced no measurement; it did truncate `stdout.log` and
  `stderr.log` to empty, which INV-5 then rewrote. It is enumerated in
  `command.txt` and `run_manifest.yaml` rather than reconciled away. Peak RSS is
  taken from the script's own `getrusage` instead.
* **INV-2, an unplanned install step.** After fpylll was installed, `numpy` and
  `scipy` were pinned in the venv to the producer's committed versions (2.4.6 /
  1.17.1) so the environment comparison of section 5 is like for like. Declared
  because it changes what "the environment" means in that table.
* **Invocation count vs. declared run count.** `maximum_runs` is 1 and there was
  exactly **one measurement invocation** (INV-5). Six invocations total were made
  — install, pin, syntax check, the failed INV-4, the run, and read-only
  post-run probes — and all six are enumerated in `run_manifest.yaml`.
* **Budget.** Not exceeded. The 1200 s cap covers the install plus the run: 24 s
  of install (INV-1, from its own timestamps) plus about 1 s of shell wall clock
  for INV-5. Memory peak 0.058 GiB against 4 GB.
* No protocol deviation from PREREG-1 section 8.3 is recorded. The frozen
  prediction P-L1 and its 1e-6 falsifier were not touched.

## 7. WHAT THIS DOES NOT SHOW

* It resolves no doubt; there was none to resolve. It restores coverage.
* It vindicates no earlier number and impugns none.
* It is **not** a cross-platform result — the environments are identical as
  measured (section 5).
* It covers **L7 and L8 only**, `beta` in {5, 10, 15}, 8 bases, `hkz` and
  `lam1n`. L1/L2, L4/L5, L9–L12 are out of scope and remain uncovered by any
  re-implementation.
* It makes no admissibility claim about any observable, does not rescore
  BATCH-a44d08 in any respect, and does not retire AM-3.
* **CLAIM TIER TOY**: nothing here bears on ML-KEM security, on any FIPS 203
  parameter set, on any attack cost, or on any cost model.
* The citable range is **4.87x to 31.03x**; "a factor of 6 to 31" is **FALSE**
  and is not cited here.
* No conclusion about G-VAR2, about either fixture, or about the termination
  branch of PREREG-1 section 7 is drawn here. That is not an executor's act.

## 8. PATHS WRITTEN BY THIS TASK — EXACTLY SEVEN, ALL INSIDE THE WRITE SCOPE

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/replicate_l7l8.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/results_l7l8.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/report_l7l8.md
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-0e930c/run_manifest.yaml

Nothing else in the repository was created, modified or deleted. No commit was
made. `knowledge/INDEX.md` was not written, regenerated or staged. The fpylll
install lives entirely outside the repository, under the session scratch path
recorded in `command.txt` and `run_manifest.yaml`. `PYTHONDONTWRITEBYTECODE=1`
was set for every Python invocation and no `__pycache__` exists in the task
directory.

`stderr.log` is empty; that is its measured content, not an omission.
