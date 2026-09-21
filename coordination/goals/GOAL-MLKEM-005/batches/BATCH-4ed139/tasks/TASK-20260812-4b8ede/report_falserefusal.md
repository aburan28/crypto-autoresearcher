# RIDER (ii) — THE FALSE-REFUSAL CONTROL — EXECUTION REPORT

    task        TASK-20260812-4b8ede   (executor, producer)
    goal/batch  GOAL-MLKEM-005 / BATCH-4ed139
    run         RUN-20260812-4b8ede-01   (one run; maximum_runs 1)
    governed by PREREG-1, TASK-20260812-34b86c, sha256 dc04d640737e6f15c40d9afdba919e75a72e52ee6510cbbbba16678d24af4c62
                notarized by TASK-20260812-1ed548 at commit 8d72f2c03
    outcome row R2-OUT-7
    archived by TASK-20260812-b53c2f  (this producer COMMITTED NOTHING)
    claim tier  TOY, UNCONDITIONALLY

---

## HEADLINE — READ THIS BEFORE ANY NUMBER BELOW

**This is ONE CONSTRUCTED INSTANCE, n = 1.** It narrows DEC-20260812-7c4a1e
C-2(b) from *"the refusal side is untested in either direction"* to *"the refusal
side has one constructed instance of a false refusal"*. **IT DOES NOT MEASURE A
FALSE-REFUSAL RATE.** No rate is reported, estimated or implied anywhere in this
report, in `results_falserefusal.json`, or in `run_manifest.yaml`. A rate needs a
population and a sampling scheme and this batch has neither.

Nothing here bears on ML-KEM security, on any FIPS 203 parameter set, on any
attack cost, or on any cost model. **CLAIM TIER TOY.**

Observations only. No hypothesis is declared supported, rejected or closed here,
and no heuristic is declared validated or refuted; that judgement belongs to the
Validator, the Red Team and the Coordinator.

## THE LEAD'S OUTCOME ROWS COME FIRST

This rider is gated behind the lead and may not be reported ahead of it. The lead
producer TASK-20260812-56b9da (`results_gvar2.json`, sha256
`2ef8ca90a1f331584f9164f0b47d58c6ba93ef60d7d4c54c4f082693cbf61082`) records, and
these are **carried, not measured here**:

    R2-OUT-1  F0 fixture   FAIL
    R2-OUT-2  F1 fixture   FAIL
    R2-OUT-V  VOID row     DOES NOT FIRE
    branch                 T-F0FAIL-PARTIAL   (PREREG-1 7.3, -PARTIAL per 7.4)

That context is load-bearing for section F.4 below and is stated before this
rider's own row rather than after it.

---

## 0. FILES WRITTEN BY THIS TASK — EXACTLY SEVEN, NOTHING ELSE

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/measure_falserefusal.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/results_falserefusal.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/report_falserefusal.md
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/run_manifest.yaml

No eighth file. `task_card.md` in this directory was written by the Coordinator
and is not this task's output. No file outside the write scope was created or
modified; see section G.1 for the one transient side effect and its removal.

## 1. THE OBJECT, AS FROZEN AND NOT REDEFINED

    X_gso_k(B) = (1/k) * sum_{j=1..k} log ||b*_j||   over the RAW basis,
                                                     frozen row order
    declared arguments: d, k, q, raw GSO profile — AND NO BETA   (PREREG-1 2.4)
    routes: RQ  QR of B^T,                   log|R_jj|, j = 1..k
            RG  Cholesky of the Gram B B^T,  log of the diagonal, j = 1..k

Implemented exactly as written. This producer has objections to two frozen
clauses (sections F.1 and F.5); both are recorded as findings and the frozen text
was scored anyway.

Scored on all ten lattices (L1, L2, L4, L5, L7–L12), 8 frozen bases each, on
families F0 and F1 and on the fibre families at seed prefixes 2, 3 and 4 — 640
bases in total, one QR and one Cholesky each. **No reduction of any kind**, so
fpylll is not required and the d <= 40 reduction bound does not apply here.

The committed code paths are **imported, not transcribed**:
`rho_both`, `bit_identical`, `summarize`, `TAU_REL`, `REL1_PAIR` from
BATCH-9e3584 `measure_relvar.py`; `build_basis_fam`, `moduli`,
`structural_check_and_exact_absdet`, `sd_mean`, `var_s_from_cells`,
`var_f_from_cells`, `gvar2`, `FAMILIES`, `FIBRE_OF`, `LATTICES`, `BETA_GRID`,
`TAU_VAR`, `Q`, `N_BASES`, `S_X` from the lead's `measure_gvar2.py`. Neither
module's `main()` was executed; neither file was modified.

## 2. RUN FACTS

    exit code                 0
    stderr                    0 bytes
    measurement wall clock    0.762 s   (declared cap 600 s — NOT exceeded)
    total script wall clock   1.702 s   (session budget 3600 s)
    memory                    4 GB address-space cap enforced via `ulimit -v`;
                              not hit. Peak RSS NOT INSTRUMENTED — GNU time is
                              absent on this host (see G.2). No RSS number is
                              invented.
    runs executed             1 of 1 allowed
    git revision              a790aa0ee82e92fdbaa0e5ec4fa754e962ee4717
    dirty tree                untracked task artifacts only (this task's and
                              rider (i)'s); NO tracked file modified
    python 3.11.15, numpy 2.4.6, Linux-6.18.5-fc-v20-x86_64, 4 cores
    fpylll                    ABSENT — recorded as an environment fact; this
                              rider runs no reduction and depends on it nowhere

---

## A. COULD-NOT-FAIL ARRANGEMENTS, NAMED BEFORE THE RUN AND DECIDED BY MEASUREMENT

Both are printed at the top of `stdout.log`, before any number, and both are
decided by the numbers in sections B and C rather than by the paragraph naming
them.

**could-not-FIRE** — a construction that could never be refused. Would hold if
the candidate satisfied every clause of the gate by construction, so that no
refusal was reachable. **Excluded by measurement**: the gate does return a
refusal for this candidate — G-REL1's rho is 0 < tau_rel = 0.10 at every one of
the 10 lattices, at every one of the 8 bases, on both routes, at both
normalizations, giving 0/8 passing bases everywhere (section C).

**could-not-PASS** — a construction that could never be informative, making
"informative by construction" vacuous. Would hold if `X_gso_k` were constant
across the 8 bases. **Excluded by measurement**: the between-basis sd is strictly
positive at every lattice and both routes, with 8/8 distinct IEEE-754 values,
while `|det B_i|` is bit-identical across those same 8 bases (section B).

## B. THE INFORMATIVENESS HALF — DEMONSTRATED, NOT ASSERTED

Family F0, 8 frozen bases per lattice, route RQ (RG agrees to the precision
reported in F.2):

| lattice | (d,k) | mean X_gso_k | sd over 8 bases | distinct IEEE-754 / 8 | abs(det B_i) bit-identical over 8 |
|---|---|---|---|---|---|
| L1 | (100,30) | +8.943713228 | 1.0056e-02 | 8/8 | yes |
| L2 | (100,70) | +3.831474573 | 3.8613e-03 | 8/8 | yes |
| L4 | (140,40) | +9.120197092 | 6.5404e-03 | 8/8 | yes |
| L5 | (140,100) | +3.647449661 | 4.0006e-03 | 8/8 | yes |
| L7 | (20,6) | +8.268057416 | 7.8385e-02 | 8/8 | yes |
| L8 | (20,14) | +3.569842176 | 3.2624e-02 | 8/8 | yes |
| L9 | (30,9) | +8.415950290 | 3.9209e-02 | 8/8 | yes |
| L10 | (30,21) | +3.619352366 | 2.4153e-02 | 8/8 | yes |
| L11 | (40,12) | +8.559675089 | 3.1982e-02 | 8/8 | yes |
| L12 | (40,28) | +3.663572235 | 1.7079e-02 | 8/8 | yes |

Between-basis sd ranges over **3.86e-03 … 7.84e-02**. Within F0 the only thing
that varies with the basis index `i` is `A_i`; `abs(det B_i) = q^(d-k)` is
bit-identical across the 8 bases at every lattice (exact integer comparison on
the verified block structure, not a float read). So the dispersion is not a
determinant effect.

**Second demonstration, at fixed (d, k, q and abs(det B))** — F0 against
F0|fib_s2, a *new A draw* (seed prefix 2) with the identical determinant: the
per-index absolute difference reaches 8.30e-03 (L5) to 1.81e-01 (L7), at every
lattice, and the determinant is identical across the two families at all ten. The
observable moves when and only when `A` moves.

**Bound on this half.** This shows `X_gso_k` *varies with the entries of A* on
the tested families and lattices. Per PREREG-1 3.5 it carries **no** claim that
the observable carries lattice information, and none is made.

## C. THE REFUSAL HALF — THROUGH THE GATE'S OWN COMMITTED CODE PATH

`rho_both()` and `bit_identical()` from the committed `measure_relvar.py` were
called directly, with `s_X = 1.0` and `tau_rel = 0.10` as PREREG-1 2.1 freezes
them, on the REL1 endpoint pairs of PREREG-1 2.2. Because `X_gso_k` takes no beta
argument, its value at `beta_lo` and at `beta_hi` is the same number; that is the
frozen definition applied literally.

Measured, at **every** lattice, **both** routes, **all 8** bases:

* `rho` at the max-floor normalization = **0.0 exactly** (mean, min, max all 0);
* `rho` at the abs(X) normalization = **0.0 exactly**;
* `s_X/abs(X)` beside each entry: **0.1096 … 0.2801** across the ten lattices
  (0.1096 at L4, 0.2801 at L8) — the scale floor is not binding at any lattice
  (`scale_floor_binding_in_n_of_8 = 0` everywhere), so both normalizations agree
  and neither rescues the candidate;
* passing bases: **0 of 8** at every lattice, both routes;
* `FORCED_ZERO_BY_ALGEBRA`: **true at 10 of 10 lattices, both routes**;
* under the committed aggregation of `measure_relvar.py` section 6
  (`rel1_ok = n_pass_at_mean_over_8 > 0 and not UNTESTED_BY_ALGEBRA`),
  `rel1_ok = False` for both routes, so the candidate does not pass G-REL.

**Confirmed: `rho = 0` exactly, and REL-1 fails by algebra**, exactly as PREREG-1
8.2 states it does for `rdet` and `lam1n`.

**Reported with it, not adjudicated (F.3):** the committed code labels a forced
zero **UNTESTED**, not a failure — its own note reads *"this candidate takes no
beta argument, so REL-1 is identically 0 BY ALGEBRA. Reported as UNTESTED, NOT as
a failure. This is not a test that could have failed."* Both readings are
reported; under either, the candidate does not pass.

## D. G-VAR2, THROUGH THE LEAD PRODUCER'S OWN COMMITTED CODE

`var_s_from_cells()`, `var_f_from_cells()` and `gvar2()` were imported from the
lead's `measure_gvar2.py` and called on `X_gso_k`'s cell statistics, so this is
the same instrument the lead scored and not a re-reading of it.

**Fibre guard (PREREG-1 6.4), measured first:** `abs(det B_i)` is bit-identical
across all 8 bases and matches its declared closed form (`q^(d-k)` for F0|fib,
`(q+3) q^(d-k-1)` for F1|fib) at **all 10 lattices in all 6 fibre families**
(seed prefixes 2, 3, 4). The guard holds everywhere; the run is not an instrument
failure on that count.

**Per-cell profile — 38 cells per (route, family), and it is uniform:**

| route | family | cells | VAR-S degenerate | VAR-S ADMIT | VAR-S REFUSE | VAR-F PASS | G-VAR2 ADMIT |
|---|---|---|---|---|---|---|---|
| RQ | F0 | 38 | 38 | 0 | 0 | 38 | 38 |
| RQ | F1 | 38 | 38 | 0 | 0 | 38 | 38 |
| RG | F0 | 38 | 38 | 0 | 0 | 38 | 38 |
| RG | F1 | 38 | 38 | 0 | 0 | 38 | 38 |

* **VAR-S = `scale_degenerate` at 38/38 cells**, both routes, both families:
  `R_{d,k} = 0` exactly, because `X_gso_k` is beta-free. This is the frozen
  reading of PREREG-1 3.2 — not a pass and not a fail.
* **Naive reading recorded beside it at every one of those cells**, as 3.2
  requires: `s_c > 0` everywhere, so `D_c = s/0 = +inf` and the naive reading
  **ADMITS** at 38/38. Frozen and naive readings agree in outcome here (they
  disagree for `rdet` under R0/R1/R3, where `s_c = 0` — carried from the lead).
* **VAR-F = PASS at 38/38**, decided by
  `bit_identity_at_scale_degenerate_fibre_cell`, with 8 distinct IEEE-754 values
  over the 8 fibre bases at every cell. Fibre sd ranges 2.08e-03 (L5) …
  9.02e-02 (L7).
* **AM-10 replication:** the same PASS at 38/38 on the two further fibre families
  at seed prefixes 3 and 4, for both routes and both scored families
  (`replicate_agreement` = 38 everywhere).
* **G-VAR2 = ADMIT at 38/38 cells**, both routes, both families.

The lead's own numbers (carried, sha-pinned above) put this in its intended
contrast: `rdet` under routes R0/R1/R3 has `s_c = 0.0`, `bit_identical = true`,
**VAR-F FAIL**, **G-VAR2 REFUSE**. So on those routes the discriminating case
PREREG-1 3.2 named in advance does behave as 3.2 predicted: two beta-free
candidates, both `scale_degenerate`, one refused (`rdet`) and one admitted
(`X_gso_k`). See F.1 for the part of that contrast that does **not** hold.

## E. P-FR1 — THE FROZEN PREDICTION, SCORED EXACTLY AS WRITTEN

    P-FR1 (PREREG-1 8.2 and the section-9 register, OPEN at notarization):
      "X_gso_k is REFUSED by G-REL1 and ADMITTED by G-VAR2
       (scale_degenerate on VAR-S, PASS on VAR-F)."
    FALSIFIER: either half failing.

    half 1 — refused by G-REL1 ............................. TRUE
    half 2 — VAR-S scale_degenerate at all F0 cells ........ TRUE (38/38 x 2 routes)
             VAR-F PASS at all F0 cells .................... TRUE (38/38 x 2 routes)
             G-VAR2 ADMIT at all F0 cells .................. TRUE (38/38 x 2 routes)

    P-FR1: HOLDS  — as one constructed instance, n = 1.

**R2-OUT-7:** rider (ii), P-FR1 HOLDS; one constructed instance of an observable
that varies with `A` on the tested families and that the gate's G-REL1 clause
does not pass. **No rate.**

**The louder alternative did NOT fire.** The completion gate required that, if
G-VAR2 also refused `X_gso_k`, it be said loudly, because PREREG-1 3.2 declares
in advance that this would mean the degenerate-scale rule was doing the refusing
and the fibre clause was decorative. **G-VAR2 did not refuse it**
(`instrument_defect_flag: false`). The defect named in 3.2 is therefore not
exhibited by this measurement — but see F.1, which is a different and unnamed
weakness in the same clause and which this run did exhibit.

---

## F. OBJECTIONS, CAVEATS AND UNEXPECTED OBSERVATIONS — RECORDED, NOT REPAIRED

### F.1 The VAR-F clause at a scale-degenerate cell cannot tell 4e-11 from 9e-02

At `scale_degenerate` fibre cells, PREREG-1 3.3 decides non-constancy by the
**bit-identity** test alone. That test is scale-free. Measured here: `X_gso_k`'s
fibre dispersion is `s_c_fib` ~ 9.02e-02 at L7 beta 5 with 8 distinct values →
PASS. The lead's committed numbers record `rdet` under route `R2_QR_of_BT` at the
same cell with `s_c_fib` ~ 4.18e-11, also 8 distinct values, also **PASS**, also
**G-VAR2 ADMIT** — and `rdet` reads zero entries of `A`. The two are separated by
about **nine orders of magnitude** and the clause treats them identically.

Consequence for this rider's own claim, stated plainly: **`X_gso_k`'s VAR-F PASS
is obtained through the same test that float noise passes.** The PASS is
therefore weak evidence of the *fibre* property, even though section B's
dispersion measurement is strong evidence of `A`-dependence. The two are
independent measurements and only the first goes through the instrument.

This is an **objection to a frozen clause**. The clause was implemented as
written and scored as written; no threshold was invented and nothing was
rescored. Repair, if any, is a Coordinator act in a successor record.

### F.2 RQ and RG agree to 1.8e-15 at narrow k and to 3.0e-09 at wide k

No tolerance for RQ-vs-RG agreement is pre-registered and none is invented here.
Measured on F0: max abs(RQ − RG) is 1.78e-15 at L1/L4/L7/L11 (7 of 8 bases
bit-identical), 0.0 at L9 (8/8 bit-identical), and 3.42e-10 … 3.00e-09 at the
wide-k lattices L2, L8, L10, L12, L5 (**0 of 8** bit-identical), worst 3.002e-09
at L5 (d = 140, k = 100). The Cholesky route loses roughly half the significant
digits of the Gram, as expected of a squared condition number; that is reported
as measured, not as a defect.

For proportion: at L5 the route disagreement (3.0e-09) is about six orders of
magnitude **below** the between-basis signal (sd 4.0e-03) it is used to measure.
Both routes give identical G-REL1 and G-VAR2 verdicts at every cell.

### F.3 "Refused" versus "untested" is a live reading difference in the committed code

Section C measures that `rho = 0 < tau_rel` everywhere and that `rel1_ok` is
False. Whether that is properly called a **refusal** — the word this rider's
objective uses — or an **UNTESTED** outcome is exactly what the committed code's
own note disputes. This producer records both and adjudicates neither. A reader
who needs "the gate refused an informative observable" should note that under the
code's own labelling the narrowest supported statement is: *the G-REL1 clause
returns rho = 0, does not pass the candidate, and annotates that as untested by
algebra rather than as a failed test.*

### F.4 The instrument this rider's second half is scored on failed its own fixture

The lead records **R2-OUT-1 F0 = FAIL**, branch **T-F0FAIL-PARTIAL**. PREREG-1
7.3 forbids "treating the F1 result as informative" and states that if the
instrument fails at its own reference point, *its behaviour elsewhere is
uninterpretable*. `X_gso_k` is elsewhere. The G-VAR2 half of P-FR1 is therefore
recorded here as a measurement of what the instrument did, and its interpretive
weight is for the Coordinator to rule on under 7.3. The G-REL1 half is
unaffected: it goes through a different, committed clause and is decided by an
exact algebraic zero, not by the G-VAR2 instrument.

### F.5 An objection to the frozen definition, recorded and then run as written

`X_gso_k` averages the leading `k` GSO log-norms of the **raw** basis in the
frozen row order. For `B = [[I_k, A],[0, q I_{d-k}]]` those first `k` rows are
`[e_j | A_j]`, so `X_gso_k` is close to `mean_j log norm(A_j)` up to the
Gram–Schmidt correction — a statistic of the *entries of A as written down*,
which is a presentation property of the basis rather than an invariant of the
lattice. That is not a defect for this rider's purpose (the point is exactly that
it is informative about `A` and beta-free), but a reader must not read
`X_gso_k`'s dispersion as lattice information. Recorded as an objection under the
task's instruction to record and run anyway; the definition was not altered.

---

## G. DEVIATIONS FROM THE PROTOCOL AND INFRASTRUCTURE EVENTS

### G.1 Bytecode caches created outside the write scope, and removed

Loading the two committed producer modules by path caused CPython to write
`__pycache__/` directories inside their task directories
(`.../TASK-20260812-56b9da/` and `.../TASK-20260809-cda2f6/`) during a pre-run
import check, and one inside this task's directory from `py_compile`.
`__pycache__/` is gitignored at repository root, so none of them could ever have
entered a change set. All three were **deleted**, restoring the tree to its prior
state, and the recorded run was executed with `python3 -B` so that none is
created. Verified after the run: no `__pycache__` exists in either producer
directory or in this task's directory. Recorded rather than omitted.

### G.2 GNU `time` is absent on this host, so peak RSS was not instrumented

`/usr/bin/time` does not exist here; a first invocation exited 127 before any
measurement ran, so that attempt executed no measurement and consumed no run.
Peak RSS is therefore **not measured** and no value is stated for it. The 4 GB
memory budget was instead enforced as a hard `ulimit -v` address-space cap, which
was not hit. The lead's comparable workload recorded 50 MB peak RSS; that number
is the lead's, is carried, and is not this run's measurement.

### G.3 Nothing else

No frozen clause was modified. No prediction was adjusted. One run was executed,
as budgeted; there were no retries, no crashes, no timeouts, and no candidate,
cell, route or family declared for this rider is uncovered — the rider runs no
reduction, so fpylll's absence costs it nothing. `knowledge/INDEX.md` was not
written, regenerated or staged. Nothing was committed.

---

## H. SCOPE, BINDING CARRIES AND WHAT THIS CANNOT DO

**Tested scope.** q = 3329; d in {20, 30, 40, 100, 140}; the frozen k grid; the
frozen beta grids (entering only as cell labels, since the candidate is
beta-free); 8 bases per lattice per family; families F0 and F1 and their fibre
sub-families at seed prefixes 2, 3, 4; routes RQ and RG; numpy 2.4.6 float64 on
one 4-core host; **no reduction at all**. Every observation is scoped to exactly
that. **Transfer assumptions: none are made, and nothing here transports to any
other dimension, modulus, basis presentation, arithmetic route or family.**

**Binding carries in force.** AM-10..AM-14 (DEC-20260808-05b684); AM-15, AM-16
(DEC-20260809-afe29b) as extended by AM-17 (DEC-20260812-7c4a1e); PREREG-1
sections 11 and 11.1 in full. **AM-3 is NOT retired**; its 0.096 family-wise
false-failure bound stands. **BATCH-a44d08 is NOT rescored in any respect.**
AM-9: fpylll's k counts the q-scaled rows, not the identity block. **The G-VAR
refusal is cited only as conditional on the frozen family F0.** AM4-OBS-1 is
cited only through `knowledge/findings/KN-FIND-f38a89.md`. CLAIM TIER STAYS TOY.

**Non-citable, carried at the point of quotation.** *"A factor of 6 to 31"* is
**FALSE**; the citable range is **4.87x–31.03x**. Both sub-6x counts remain
non-citable pending rider (i). Any use of the committed real count **29 of 48**
carries the exact-null benchmark **47 of 48** in the same sentence. *"G-VAR
cannot be tuned into or out of firing"* is FALSE. *"CONSISTENT"* is non-citable
in either direction.

**Independence.** Procedural only, never model-level. AGENTS.md rule 12 is
**UNMET AND UNWAIVED** in this goal and is not waived here; `model_verified` is
`false` with its reason in `run_manifest.yaml`.

**What this cannot do.** It says nothing about ML-KEM, any FIPS 203 parameter
set, any attack cost or any cost model. **It measures no false-refusal rate.** It
establishes no lattice information content for any observable. It does not
revalidate BATCH-9e3584 or BATCH-cbe023, does not retro-validate any verdict, and
cannot close, pause or complete GOAL-MLKEM-005. It does not decide which
termination branch of PREREG-1 section 7 fires; that is read off R2-OUT-1 and
R2-OUT-2 under R2-OUT-V's precedence, and nowhere else.

---

## I. ARTIFACT PATHS — EVERY PATH THIS TASK WROTE

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/measure_falserefusal.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/results_falserefusal.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/report_falserefusal.md
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-4b8ede/run_manifest.yaml

Seven paths, all pre-declared by the handoff, all present. No other path inside
the repository was written by this task.
