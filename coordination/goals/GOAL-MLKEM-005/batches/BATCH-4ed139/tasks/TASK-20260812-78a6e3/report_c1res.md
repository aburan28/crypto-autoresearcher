# RIDER (i) — the C-1 resolving tabulation

    task        TASK-20260812-78a6e3          role      executor
    goal/batch  GOAL-MLKEM-005 / BATCH-4ed139
    governed by PREREG-1 (TASK-20260812-34b86c) section 8.1, frozen and
                notarized; DEC-20260812-7c4a1e conflict C-1
    outcome row R2-OUT-6
    archived by TASK-20260812-b53c2f (rider snapshot) — THIS TASK COMMITS NOTHING
    claim tier  TOY, UNCONDITIONALLY

**This report records observations. It adjudicates nothing.** Whether either
validator's count becomes citable is a Coordinator ruling in the batch
decision. Until that ruling, **NEITHER SUB-6x COUNT IS CITABLE**, and
**"a factor of 6 to 31" is FALSE and uncitable regardless** — the citable
range is **4.87x to 31.03x**. Nothing here bears on ML-KEM security, on any
FIPS 203 parameter set, on any attack cost, or on any cost model.

---

## 1. Source, pinned and unmodified

    path    coordination/goals/GOAL-MLKEM-005/batches/BATCH-9e3584/
            tasks/TASK-20260809-cda2f6/results_relvar.json
    sha256  c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d

The same sha256 was taken before and after the read, the file's mtime was
unchanged across the run, `git status --porcelain` reports the path clean, and
`git show HEAD:<path> | sha256sum` returns the identical digest. The file was
**read only** and **never edited**. No reduction, no fpylll, no basis rebuild;
Python standard library only.

    scored objects   19 G-REL2 cells (5 mirrored pairs x their beta grids)
                     10 G-REL1 lattices
                     = 29 X_null G-REL entries, the two denominators in conflict
    tau_rel          0.10 (frozen, PREREG-1 section 2.1)

## 2. What was tabulated, and along which axes

PREREG-1 section 8.1 names **three readings** of the 8 per-basis values. The
committed file additionally stores **two normalizations** of the criterion
value at every entry, and a count of "entries below 6x" is undefined without
naming one, so both are tabulated. The normalization is **not** one of the
three declared readings and is not treated as one.

    readings         R_i0_legacy     per_basis[0]
                     R_npass_of_8    count of passing bases out of 8
                     R_mean_over_8   mean over i = 0..7 (math.fsum / 8)
    normalizations   maxfloor        value_maxfloor  (scale-floor normalization)
                     absX            value_absX      (|X| normalization)

**Boundary rule.** `6.0 * 0.10` is `0.6000000000000001` in IEEE-754 double,
**not** `0.6`, and four (maxfloor) or five (absX) G-REL2 cells sit at or within
one ulp of `0.6`. Two boundary rules are therefore reported side by side and
**neither is chosen for the reader**:

    RULE A  strict IEEE: value < 6.0*tau_rel = 0.6000000000000001, so an entry
            stored as exactly 0.6 counts as BELOW 6x
    RULE B  an entry within a relative 1e-12 of the boundary counts as AT 6x,
            not below it

They differ by exactly 2 G-REL2 cells (maxfloor) / 3 (absX).

## 3. OBSERVATION 1 — the three readings coincide, so the reading axis cannot explain the conflict

At **every one of the 29 entries, under both normalizations**, all 8 per-basis
values are **bit-identical** (`distinct_ieee754_values_over_8 = 1`, committed
`sd = 0.0`, `n_pass_of_8 = 8`). Consequently:

* `R_i0_legacy`, `R_npass_of_8` and `R_mean_over_8` return the **same IEEE-754
  double** at every entry, bitwise, and the mean agrees bitwise with the mean
  committed in the source file;
* every count below is **identical across all three declared readings**.

The two waves cannot have differed because they read the 8 bases differently.

## 4. THE MULTISET — all 29 entries, reading beside each

Because the three readings coincide bitwise (section 3), one column per
normalization carries all three. Ratios are value / tau_rel. Full per-entry
records, including `repr()` of every double and all three readings written out
separately, are in `results_c1res.json` (`entries`).

### maxfloor normalization

| ratio | n | reading(s) | location(s) |
|---|---|---|---|
| 4.8663x | 1 | i0 = npass = mean8 | G-REL2 L1/L2 beta 15 |
| 4.9656x | 1 | i0 = npass = mean8 | G-REL2 L4/L5 beta 20 |
| 5.7143x | 13 | i0 = npass = mean8 | G-REL2 L1/L2 beta 30, 35, 50, 65; L7/L8 beta 5, 10, 15; L9/L10 beta 7, 15, 22; L11/L12 beta 10, 20, 30 |
| 6.0000x | 4 | i0 = npass = mean8 | G-REL2 L4/L5 beta 40, 45, 70, 95 |
| 12.1656x | 4 | i0 = npass = mean8 | G-REL1 L2, L8, L10, L12 |
| 12.4139x | 1 | i0 = npass = mean8 | G-REL1 L5 |
| 20.0000x | 2 | i0 = npass = mean8 | G-REL1 L7, L11 |
| 21.4286x | 1 | i0 = npass = mean8 | G-REL1 L9 |
| 28.3865x | 1 | i0 = npass = mean8 | G-REL1 L1 |
| 31.0348x | 1 | i0 = npass = mean8 | G-REL1 L4 |

### absX normalization

| ratio | n | reading(s) | location(s) |
|---|---|---|---|
| 5.7143x | 14 | i0 = npass = mean8 | G-REL2 L1/L2 beta 15, 30, 35, 50, 65; L7/L8 beta 5, 10, 15; L9/L10 beta 7, 15, 22; L11/L12 beta 10, 20, 30 |
| 6.0000x | 5 | i0 = npass = mean8 | G-REL2 L4/L5 beta 20, 40, 45, 70, 95 |
| 20.0000x | 4 | i0 = npass = mean8 | G-REL1 L7, L8, L11, L12 |
| 21.4286x | 2 | i0 = npass = mean8 | G-REL1 L9, L10 |
| 33.3333x | 2 | i0 = npass = mean8 | G-REL1 L1, L2 |
| 37.5000x | 2 | i0 = npass = mean8 | G-REL1 L4, L5 |

## 5. Per reading: min, max, and the counts below 6x over all three denominators

Identical under `R_i0_legacy`, `R_npass_of_8` and `R_mean_over_8` — the three
rows of each block below are the same numbers, printed per reading in
`stdout.log` and stored per reading in `results_c1res.json`.

### maxfloor (all three readings)

    min    0.486625634255 = 4.8663x   at G-REL2 L1/L2 beta 15
    max    3.103479810297 = 31.0348x  at G-REL1 L4
    below 6x, RULE A:  17 of 19 G-REL2    0 of 10 G-REL1    17 of all 29
    below 6x, RULE B:  15 of 19 G-REL2    0 of 10 G-REL1    15 of all 29
    at 6x within 1e-12: 4 of 19 G-REL2 (L4/L5 beta 40, 45, 70, 95)
    at 5.71x within 1e-12: 13 of 19 G-REL2, 0 of 10 G-REL1, 13 of all 29
    at 5.71x bitwise equal to 4/7: 10 of 19 G-REL2
    strictly below 5.71x: 2 of all 29 (4.8663x and 4.9656x)

### absX (all three readings)

    min    0.571428571429 = 5.7143x   at G-REL2 L1/L2 beta 15
    max    3.750000000000 = 37.5000x  at G-REL1 L4 (L5 ties bitwise-adjacently)
    below 6x, RULE A:  17 of 19 G-REL2    0 of 10 G-REL1    17 of all 29
    below 6x, RULE B:  14 of 19 G-REL2    0 of 10 G-REL1    14 of all 29
    at 6x within 1e-12: 5 of 19 G-REL2 (L4/L5 beta 20, 40, 45, 70, 95)
    at 5.71x within 1e-12: 14 of 19 G-REL2, 0 of 10 G-REL1, 14 of all 29
    at 5.71x bitwise equal to 4/7: 11 of 19 G-REL2
    strictly below 5.71x: 0 of all 29

**Zero G-REL1 entries fall below 6x under any reading, normalization or
boundary rule.** The three denominators therefore agree by construction here:
the count over all 29 equals the count over the 19 G-REL2 cells.

## 6. OBSERVATION 2 — the 5.71x plateau, and the note made before looking

The task card recorded in advance that `1 - k/(d-k) = 4/7 = 0.5714285714285714`
for `(d,k) = (100,30)`, so 5.71x is **structurally available** in this family
and wave 1's figure is not obviously a typo.

**It is present, and it is the modal value.** 13 G-REL2 cells (maxfloor) / 14
(absX) sit at 4/7 to within a relative 1e-12. Of those, 10 (maxfloor) / 11
(absX) are **bitwise equal** to the double `0.5714285714285714`; the remainder
are the adjacent double `0.5714285714285715` (L7/L8 beta 15, L11/L12 beta 30,
and L1/L2 beta 15 under absX). The plateau spans several distinct `(d,k)`, so
its value is not specific to `(100,30)`.

## 7. OBSERVATION 3 — which reported count reproduces, and which does not

**Wave 1** (TASK-20260809-3f1dc4 F-1): "15 of the 19 G-REL2 cells fall BELOW
the stated lower bound of 6x", thirteen at exactly 5.71x and one at 4.97x.

> **REPRODUCED IN FULL** — under the **maxfloor** normalization with **RULE B**,
> under **all three declared readings**: 15 of 19 G-REL2 cells below 6x,
> **13** at 5.71x, one at 4.97x (0.496557, G-REL2 L4/L5 beta 20), minimum
> 4.87x. Wave 1's accompanying sub-ranges also reproduce exactly: the G-REL2
> range is 4.87x to 6.00x and the G-REL1 range is 12.17x to 31.03x.
> It does **not** reproduce under `absX` (14 of 19), and under RULE A the count
> is 17 of 19 because `6.0*tau_rel` exceeds `0.6` by one ulp.

**Wave 2** (TASK-20260812-da8c3b F-1): "TWO entries fall below 6x" out of 29,
at 0.486626 (4.87x) and 0.496557 (4.97x), "at the mean-over-8 reading".

> **NOT REPRODUCED as a count below 6x** — under no reading, no normalization
> and neither boundary rule does the number of entries below 6x equal 2. The
> smallest such count anywhere in the tabulation is 14.
>
> **Both named values are correct and correctly located**: 0.486626 at G-REL2
> L1/L2 beta 15 and 0.496557 at G-REL2 L4/L5 beta 20, under maxfloor, under all
> three readings. They are furthermore **exactly the two entries of 29 that lie
> strictly below the 4/7 = 5.71x plateau**. A count of 2 over the 29 entries is
> what a **5.71x** threshold yields; a 6x threshold yields 15 (maxfloor,
> RULE B). This report records which threshold the count of 2 corresponds to.
> It does **not** find that wave 2 applied that threshold — this tabulation
> cannot see what a validator did — and it does not declare wave 2 wrong beyond
> the count as written.

**The reading axis is not the explanation** (section 3). The axes on which the
two reported counts differ from each other, and from this tabulation, are the
**normalization**, the **boundary rule at 0.6**, and the **threshold value
itself**.

**P-C1** (PREREG-1 section 8.1, frozen): *at least one declared reading
reproduces exactly one of the two conflicting counts.* **Falsifier: no reading
reproduces either.** Observation: wave 1's count reproduces under all three
declared readings (maxfloor, RULE B); wave 2's count does not reproduce under
any. The falsifier did not fire. **The evaluation of P-C1, and any decision to
make a count citable, belong to the Coordinator and the Reviewer, not to this
report.**

## 8. The agreed range and minimum, re-derived

Instructed to re-derive and to confirm or contradict plainly:

    4.87x to 31.03x            CONFIRMED — over all 29 entries under the
                               maxfloor normalization, identical under all
                               three readings; min 0.4866256342545015
                               (4.87x), max 3.1034798102965655 (31.03x)
    minimum 0.486626 at
    G-REL2 L1/L2 beta 15       CONFIRMED — value and location both

Neither is contradicted. One measured qualifier, recorded rather than
suppressed: under the **absX** normalization the same 29 entries span **5.71x
to 37.50x**. That is a different normalization of the same committed criterion,
not a contradiction of the agreed range, which is the maxfloor one — but any
future quotation of a span should name its normalization.

## 9. Deviations, infrastructure events, and anomalies — all recorded

1. **`/usr/bin/time` is absent on this host.** A first invocation wrapped in
   `/usr/bin/time -v` exited 127 from the shell; **the tabulation script never
   started and no measurement was produced**. INFRASTRUCTURE SIGNAL, never
   mathematical evidence. Peak RSS is therefore **not instrumented and is
   reported as not measured**, not estimated. The 2 GB memory budget was
   instead applied as a hard cap via `ulimit -v 2097152`, which `command.txt`
   records; no cap was hit.
2. **Repository-root resolution defect (implementation_error).** The second
   invocation crashed with `FileNotFoundError` — the script walked six parent
   directories instead of seven. Fixed by resolving seven levels and asserting
   `.git` is present. No measurement was produced by that invocation.
3. **Naive-mean ulp noise (implementation_error).** The third invocation ran to
   completion but computed the mean-over-8 with a left-to-right sum, which
   moved entries by 1 ulp and made the mean-over-8 reading disagree bitwise
   with the other two and with the committed mean. Its output is superseded and
   is **not** reported here. Fixed with `math.fsum`, after which the mean agrees
   bitwise with the committed mean at all 29 entries under both normalizations.
   Recorded rather than discarded, per AGENTS.md rule 8.
4. **Two boundary rules rather than one.** The strict comparison against
   `6.0*tau_rel = 0.6000000000000001` and the 1e-12 tolerance rule disagree at
   2 G-REL2 cells (maxfloor). Both are published; the Executor does not pick
   one, and the choice is exposed for the Coordinator and the Validator.
5. **Normalization axis published beyond the three named readings.** PREREG-1
   section 8.1 names three readings; the committed file carries two
   normalizations. Publishing only one would have silently decided the conflict.
   Declared as an addition of reporting detail, not a change to the frozen
   protocol; the three declared readings are tabulated exactly as named.
6. **Invocation count vs `maximum_runs: 1`.** The declared measurement is ONE
   run — the final invocation, whose logs and results are the artifacts here.
   Four earlier invocations occurred: one that never started the script
   (item 1), one that crashed (item 2), one superseded implementation
   (item 3), and one identical to the final run except for added disclosure
   printing of the boundary constant. All five are enumerated in
   `run_manifest.yaml` (`invocation_log`). No invocation was a re-roll seeking
   a favourable number: the run is deterministic on a pinned file and every
   invocation after item 2 produced the same underlying values. Flagged for the
   Coordinator as a budget-accounting item.
7. **`__pycache__` from a `py_compile` syntax check** was created inside the
   task directory and **deleted immediately**; the run itself sets
   `PYTHONDONTWRITEBYTECODE=1`. The task directory contains exactly the seven
   declared artifacts plus the pre-existing committed `task_card.md`.
8. **AGENTS.md rule 12 is UNMET AND UNWAIVED** in this goal. One backend
   resolves, so `model_verified: false` with its reason, per PREREG-1
   section 12.

Nothing was omitted, no run was discarded, and no value here is estimated.

## 10. Binding carries restated

* **AM-10..AM-14** (DEC-20260808-05b684), **AM-15**, **AM-16**
  (DEC-20260809-afe29b), **AM-17** (DEC-20260812-7c4a1e) are in force.
* **AM-3 IS NOT RETIRED**; its 0.096 family-wise false-failure bound stands.
* **BATCH-a44d08 IS NOT RESCORED IN ANY RESPECT.**
* **"A factor of 6 to 31" is FALSE and is not citable anywhere**; the citable
  range is **4.87x to 31.03x**.
* **Both sub-6x counts remain NOT CITABLE** pending the Coordinator's ruling on
  this tabulation.
* Any use of the committed real count of **29 of 48** carries the exact-null
  benchmark of **47 of 48** in the same sentence. This report makes no use of
  either; the pairing is restated because the carry binds at the point of
  quotation.
* **CLAIM TIER STAYS TOY.** Nothing here bears on ML-KEM security, any FIPS 203
  parameter set, any attack cost, or any cost model. Scope: q = 3329, the
  frozen lattices, k and beta grids, 8 bases, `X_null` only, one committed
  results file. It transports nowhere.
* `knowledge/INDEX.md` was **not** written, regenerated or staged.
* This task **committed nothing**; the snapshot is TASK-20260812-b53c2f.

## 11. Every path written by this task

Exactly seven, all pre-declared by the archive, all present:

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-78a6e3/tabulate_c1res.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-78a6e3/results_c1res.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-78a6e3/report_c1res.md
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-78a6e3/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-78a6e3/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-78a6e3/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-78a6e3/run_manifest.yaml

No eighth file was written. `task_card.md` in the same directory is
pre-existing and committed and was not modified. No file outside the task's
`write_scope` was created, modified or deleted.
