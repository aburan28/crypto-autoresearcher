# G-VAR2 — LEAD PRODUCER EXECUTION REPORT

    task        TASK-20260812-56b9da  (executor, LEAD PRODUCER)
    goal/batch  GOAL-MLKEM-005 / BATCH-4ed139
    run         RUN-20260812-56b9da-01   (the ONE run; budget maximum_runs = 1)
    contract    PREREG-1, tasks/TASK-20260812-34b86c/prereg.md
                sha256 dc04d640737e6f15c40d9afdba919e75a72e52ee6510cbbbba16678d24af4c62
                notarized by commit 8d72f2c038a577e216ab9d6d0e5995f65d5ff819
    commit      64aa091bff78008c862fe9016cd111900a127189
                branch claude/launch-research-harness-1ns6z3
    claim tier  TOY, UNCONDITIONALLY
    certificate kind: none — pure measurement run; no discrete-log solve and no
                factor-base relation is claimed or produced.

**THIS REPORT RECORDS OBSERVATIONS. IT INTERPRETS NOTHING.** It declares no
hypothesis supported, rejected or closed and no heuristic validated or refuted;
those are Reviewer and Coordinator acts. It changes no research status. Nothing
here bears on ML-KEM security, on any FIPS 203 parameter set, on any attack cost
or on any cost model, and no number transports to beta = 606, d = 1420 or any
other parameter set by extrapolation, analogy or any other route.

---

## 0. EVERY PATH THIS TASK WROTE INSIDE THE REPOSITORY

Exactly seven, exactly the declared `artifact_paths`, and nothing else:

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/measure_gvar2.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/results_gvar2.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/report_gvar2.md
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/run_manifest.yaml

No other repository file was created, modified, deleted or staged. No committed
artifact was edited: `results_relvar.json`, both probes, both preregs and every
ledger record are untouched and are pinned by sha256 in `run_manifest.yaml`.
`knowledge/INDEX.md` was not written, regenerated or staged. Nothing was
committed; the Coordinator snapshot TASK-20260812-b581a8 commits this package.

Development dry-runs of the script were executed **outside the repository**
under a scratch path, writing only scratch files. The recorded run is one, is
the one in `command.txt`, and produced every number below.

---

## A. WHAT WAS BUILT, AND HOW IT IS PINNED TO THE FIXTURES

`measure_gvar2.py` implements G-VAR2 exactly as PREREG-1 §3 freezes it: VAR-S
(§3.1) as between-basis sd (ddof = 1) at fixed (d, k, beta, q) divided by the
candidate's OWN between-cell range `R_{d,k}` at fixed (d, k) over that lattice's
beta grid, `tau_var = 1e-3`; the degenerate-scale rule (§3.2) with the NAIVE
reading reported beside the frozen one at every `scale_degenerate` cell; VAR-F
(§3.3) on the fibre families, replicated on seed prefixes 3 and 4; the
conjunction of §3.4. Every verdict is a PER-CELL PROFILE
(`results_gvar2.json → per_cell_profiles`); no all-cells Boolean is reported for
any candidate.

**PROVENANCE — IMPORTED, NOT TRANSCRIBED.** `probe_nullroute.py` is IMPORTED as
a module and its `fixed_unimodular`, `fixed_isometry`, `bit_identical`,
`make_A`, `build_basis` and `logdet_routes` are used directly.
`probe_gvar_family.py` is IMPORTED for its `moduli()`/`build_basis()`. Measured
agreement:

| check | result |
|---|---|
| this file's family-parametrised routes vs the committed `logdet_routes`, F0 | **480 / 480 route values BIT-IDENTICAL**, max abs difference 0.0 |
| F0 and F1 bases vs the committed `probe_gvar_family.build_basis` | identical at every lattice and basis |
| the two committed transcriptions of the notarized prereg 2.6 table | 38 / 38 entries agree exactly |

`raw_gso_logs` and `x_rawtail_of` are TRANSCRIBED VERBATIM from BATCH-9e3584
`measure_relvar.py` (route RD for `rawtail` needs no reduction); the
transcription is checked against the committed values below (max abs difference
0.0 in both the per-cell sd and the per-cell mean at 38 / 38 cells).

**CONTRACT VERIFIED, NOT ASSERTED.** The run re-derives, in code: working-tree
`prereg.md` sha256 = sidecar sha256 = the blob at 8d72f2c03; the file is ABSENT
at that commit's parent 18dd3819b; the commit is an ancestor of HEAD; and it
changed exactly three files (the receipt, `prereg.md`, `prereg_sha256.txt`) —
zero producer artifacts.

---

## B. THE GUARDS (PREREG-1 6.4), ASSERTED AND PRINTED

* **Block structure verified entrywise** at every family, lattice and basis, so
  `|det B_i| = prod(m)` is a verified consequence of a verified structure and
  not an assumption.
* **FIBRE GUARD HOLDS EVERYWHERE**: at every fibre family (`F0|fib_s2`,
  `F1|fib_s2`, and the seed-prefix 3 and 4 replicates) and every lattice,
  `abs(det B_i)` is BIT-IDENTICAL across all 8 bases (exact integer
  determinant; 1 distinct value out of 8 everywhere). The run is therefore not
  an instrument failure under §6.4.
* **F1 moduli strictly increase in i**: `m_i[0] = [3329..3336]`, strictly
  increasing.

---

## C. OUTCOME ROWS

### R2-OUT-1 — FIXTURE F0 VERDICT: **FAIL** (fully covered on the half that fails)

Declared target (PREREG-1 4.1): all six routes to `X_null` REFUSED, all six to
`rdet` REFUSED, `lam1n` / `hkz` / `rawtail` ADMITTED.

**Refusal half — per candidate, per route, per cell, coverage 38/38 each:**

| candidate | route | coverage | REFUSE | ADMIT | target met |
|---|---|---|---|---|---|
| `X_null` | R0_closed_form | 38/38 | 38 | 0 | YES |
| `X_null` | R1_slogdet | 38/38 | 38 | 0 | YES |
| `X_null` | R2_QR_of_BT | 38/38 | 38 | 0 | YES |
| `X_null` | R3_slogdet_of_UB | 38/38 | 38 | 0 | YES |
| `X_null` | R4_gram_half_slogdet | 38/38 | 38 | 0 | YES |
| `X_null` | R5_slogdet_of_BH | 38/38 | 38 | 0 | YES |
| `rdet` | R0_closed_form | 38/38 | 38 | 0 | YES |
| `rdet` | R1_slogdet | 38/38 | 38 | 0 | YES |
| **`rdet`** | **R2_QR_of_BT** | 38/38 | **0** | **38** | **NO** |
| `rdet` | R3_slogdet_of_UB | 38/38 | 38 | 0 | YES |
| **`rdet`** | **R4_gram_half_slogdet** | 38/38 | **0** | **38** | **NO** |
| **`rdet`** | **R5_slogdet_of_BH** | 38/38 | **0** | **38** | **NO** |

**The mechanism, as measured.** `rdet` takes no beta argument, so `R_{d,k} = 0`
exactly and VAR-S is `scale_degenerate` at all 38 cells under all six routes —
by §3.2 that is NOT a fail, and the cell is decided by VAR-F alone. On the fibre
family `F0|fib_s2` the exact determinant is bit-identical across the 8 bases
(the guard above), but the FLOAT value of `log abs(det B)` is not, under three
of the six declared routes: measured between-basis fibre sd
5.42e-13 … 4.18e-11 (R2), 5.69e-09 … 6.03e-07 (R4), 2.81e-13 … 3.35e-11 (R5).
`R^fib_{d,k} = 0` as well, so §3.3 decides non-constancy by the carried
`bit_identical()` test, which those three routes break at every one of the 38
cells (8 distinct IEEE-754 values out of 8). VAR-F therefore PASSES and §3.4
ADMITS `rdet`. **Replicated on all three fibre families** (seed prefixes 2, 3
and 4): PASS at every cell in each.

**Admitted half — reported at its ACTUAL coverage:**

| block | cells with a VAR-S value | cells with a FULL G-VAR2 verdict | ADMIT | REFUSE | UNCOVERED | target met |
|---|---|---|---|---|---|---|
| `rawtail` / RC (committed) | 38 | 0 | 0 | 0 | 38 | — (uncovered) |
| `rawtail` / RD_rawgso | 38 | 38 | 37 | 1 | 0 | **NO** (1 miss) |
| `lam1n` / RC (committed) | 18 | 0 | 0 | 0 | 38 | — (uncovered) |
| `lam1n` / RD_frozen_HKZ | 0 | 0 | 0 | 0 | 38 | — (uncovered) |
| `hkz` / RC (committed) | 18 | 0 | 0 | 0 | 38 | — (uncovered) |
| `hkz` / RD_frozen_HKZ | 0 | 0 | 0 | 0 | 38 | — (uncovered) |

* `hkz` through RC: VAR-S ADMIT at 18 / 18 committed cells, `D_c` in
  [6.65e-3, 2.833e-1]; VAR-F is UNCOVERED (no fibre values exist for a
  reduction-dependent candidate on this host), so the FULL G-VAR2 verdict is
  uncovered.
* `lam1n` through RC: the committed values are constant across the beta grid at
  fixed (d, k), so `R_{d,k} = 0` and VAR-S is `scale_degenerate` at 18 / 18
  cells; VAR-F is likewise UNCOVERED. `lam1n`'s beta-freeness in the committed
  file is a MEASURED outcome here, not an assumption.
* `rawtail` through RD_rawgso: the single miss is **L4 beta 95**, `D_c` =
  4.876e-4 < `tau_var` = 1e-3 (VAR-S REFUSE) with `D^fib_c` = 6.240e-4 (VAR-F
  FAIL). Every other cell ADMITs; `D_c` over the 38 cells spans
  [4.876e-4, 8.751e-2].
* The 20 cells at d in {100, 140} for `lam1n` and `hkz` were NOT COMPUTED in the
  committed file (declared d <= 40 reduction bound) and are neither a zero, nor
  a pass, nor a fail.

**R2-OUT-1 = FAIL.** The failure lies entirely in the **determinant-only half**,
which PREREG-1 7.4 states "requires no reduction at all and is fully scorable on
any host; its verdict is binding regardless". It is covered 38/38 at all six
routes, replicated on three fibre families, and **is not caused by a missing
dependency, a timeout or a crash**. The `rawtail` miss at L4 beta 95 is a
second, independent miss; F0 would FAIL from `rdet` alone even if `rawtail`,
`lam1n` and `hkz` were struck out entirely.

### R2-OUT-2 — FIXTURE F1 VERDICT: **FAIL**

Declared target (PREREG-1 4.2 / AM-17(b)): `X_null` REFUSED and `rdet` REFUSED
at all 38 cells, every declared route.

| candidate | route | coverage | REFUSE | ADMIT | target met |
|---|---|---|---|---|---|
| `X_null` | all six R0…R5 | 38/38 each | 38 each | 0 each | YES (6/6 routes) |
| `rdet` | R0_closed_form | 38/38 | 38 | 0 | YES |
| `rdet` | R1_slogdet | 38/38 | 38 | 0 | YES |
| **`rdet`** | **R2_QR_of_BT** | 38/38 | **0** | **38** | **NO** |
| `rdet` | R3_slogdet_of_UB | 38/38 | 38 | 0 | YES |
| **`rdet`** | **R4_gram_half_slogdet** | 38/38 | **0** | **38** | **NO** |
| **`rdet`** | **R5_slogdet_of_BH** | 38/38 | **0** | **38** | **NO** |

`X_null` in F1: between-basis sd 7.50e-7 … 2.76e-5 against its own between-cell
range, giving `D_c` in [2.42e-7, 2.27e-5], far below `tau_var`; VAR-S REFUSES,
and VAR-F FAILS as well (the fibre family holds the determinant fixed, so
`D^fib_c` = 0.0 under R0/R1/R3 and ~1e-15…5e-14 under R2/R4/R5). The scaled
criterion does refuse in F1 what bit-identity alone admitted there. `rdet` in F1
fails through the same three float routes as in F0, by the same mechanism.

`lam1n`, `hkz` and `rawtail` are NOT SCORED in F1 and no target behaviour is
declared for them there; that absence is a **declared scope limit and is never
reported as a failure**. (`rawtail`'s F1 row was computed and appears in the
JSON for information only — 37 ADMIT, 1 REFUSE — and enters no F1 verdict.)

**PRECEDENCE NOTE, BINDING.** The branch below is T-F0FAIL, and PREREG-1 7.3
FORBIDS treating the F1 result as informative: "If the instrument fails at its
own reference point, its behaviour elsewhere is uninterpretable." The F1 numbers
are reported because the completion gate requires them to be reported. They are
not to be read as evidence in either direction.

### R2-OUT-3 — P-V1: VAR-S ALONE on `V_evade` over F0: **HOLDS**

Adjudicated on **VAR-S ALONE**, at every one of the 38 scored F0 cells, through
**all six** declared routes (the gate asks for at least two).

| route | REFUSE | ADMIT | max `D_c` | max between-basis sd |
|---|---|---|---|---|
| R0_closed_form | 38 | 0 | 3.215e-10 | 3.912e-10 |
| R1_slogdet | 38 | 0 | 3.215e-10 | 3.912e-10 |
| R2_QR_of_BT | 38 | 0 | 3.215e-10 | 3.912e-10 |
| R3_slogdet_of_UB | 38 | 0 | 3.215e-10 | 3.912e-10 |
| R4_gram_half_slogdet | 38 | 0 | 1.238e-09 | 1.625e-09 |
| R5_slogdet_of_BH | 38 | 0 | 3.215e-10 | 3.912e-10 |

The falsifier (VAR-S admits `V_evade` at any scored cell) did not occur at any
cell on any route. **P-V1 HOLDS.** Its class is fixed in advance by PREREG-1 §5:
**CONSISTENCY CHECK (AM-15(a))** — reported, and NOT counted toward this
batch's empirical content. The measured max between-basis sd of 3.912e-10
reproduces the reviewer's committed 3.91e-10 that PREREG-1 attributes rather
than measures.

**Reported SEPARATELY, and it is NOT P-V1:** the FULL G-VAR2 verdict on
`V_evade` in F0 is REFUSE at 38 / 38 cells under all six routes (VAR-S REFUSE
dominates the conjunction; VAR-F PASSes there because `A'[0,0]` varies on the
fibre).

### R2-OUT-4 — the graded guard's crossing amplitude (PREREG-1 6.1)

`X_lambda = X_null + lambda * A[0,0]/q` over the frozen grid
{0, 1e-12, 1e-10, 1e-9, 1e-8, 1e-6, 1e-4, 1e-2, 1e-1, 1}, F0, all six routes.

| route | cells crossing | `lambda*` values observed |
|---|---|---|
| R0_closed_form | 38 / 38 | {1e-2, 1e-1} |
| R1_slogdet | 38 / 38 | {1e-2, 1e-1} |
| R2_QR_of_BT | 38 / 38 | {1e-2, 1e-1} |
| R3_slogdet_of_UB | 38 / 38 | {1e-2, 1e-1} |
| R4_gram_half_slogdet | 38 / 38 | {1e-2, 1e-1} |
| R5_slogdet_of_BH | 38 / 38 | {1e-2, 1e-1} |

The per-cell `lambda*` and the full 10-point profile are in
`results_gvar2.json → GRADED_GUARD.per_route[*].per_cell`. **P-G1 (MUST-PASS
GUARD): the guard crosses within the grid at 38 of 38 cells on every route**,
which is a majority at every route.

### R2-OUT-V — **DOES NOT FIRE**

The guard crosses in the grid (above), so VAR-S is not dead at this scale and no
G-VAR2 verdict in this batch is voided by §6.1. Because R2-OUT-V does not fire,
the fixture verdicts above stand as reported rather than being voided.

### R2-OUT-5 — the scale-degenerate disclosure (PREREG-1 3.2)

Frozen reading BINDING: `R_{d,k} == 0` gives `scale_degenerate`, which is **not
a pass and not a fail**; VAR-F alone then decides the cell. The NAIVE reading
(`s/0 = +inf -> ADMIT`) is recorded beside it at **every** such cell in the JSON.

Which candidates were `scale_degenerate`, and where:

| block | `scale_degenerate` cells | naive reading ADMIT | naive REFUSE / undefined (s = 0) | frozen-reading G-VAR2 ADMIT | frozen REFUSE |
|---|---|---|---|---|---|
| `rdet` R0, F0 | 38 (all cells, all (d,k)) | 0 | 38 | 0 | 38 |
| `rdet` R1, F0 | 38 | 0 | 38 | 0 | 38 |
| `rdet` R2, F0 | 38 | 38 | 0 | 38 | 0 |
| `rdet` R3, F0 | 38 | 0 | 38 | 0 | 38 |
| `rdet` R4, F0 | 38 | 38 | 0 | 38 | 0 |
| `rdet` R5, F0 | 38 | 38 | 0 | 38 | 0 |
| `rdet` R0, F1 | 38 | 38 | 0 | 0 | 38 |
| `rdet` R1, F1 | 38 | 38 | 0 | 0 | 38 |
| `rdet` R2, F1 | 38 | 38 | 0 | 38 | 0 |
| `rdet` R3, F1 | 38 | 38 | 0 | 0 | 38 |
| `rdet` R4, F1 | 38 | 38 | 0 | 38 | 0 |
| `rdet` R5, F1 | 38 | 38 | 0 | 38 | 0 |
| `lam1n` RC, F0 | 18 (all committed cells) | 18 | 0 | 0 (VAR-F uncovered) | 0 |

`rdet`'s beta-freeness is definitional and was expected. `lam1n`'s
`scale_degenerate` status at all 18 committed cells is a **measured** outcome,
not an assumption. No other candidate was `scale_degenerate`.

**What the two readings do and do not buy, as measured.** In F1 the frozen rule
changes the verdict on `rdet` at 3 of 6 routes (R0, R1, R3: naive ADMIT ->
frozen REFUSE, 38 cells each) and changes nothing at the other 3 (R2, R4, R5:
ADMIT either way). So the frozen rule does exactly the work §3.2 said it would
for the routes whose fibre values are bit-identical, and does none of it for the
three routes where float noise breaks bit-identity on the fibre.

### R2-OUT-6 — NOT PRODUCED BY THIS TASK

R2-OUT-6 is rider (i)'s three-reading tabulation, owned by TASK-20260812-78a6e3,
which `depends_on` this lead's snapshot archive. It is not produced here and no
count of it is reported here. Neither sub-6x count is citable pending that
rider's adjudication; the corrected range **4.87x to 31.03x** is the citable one
and is unaffected.

---

## D. INFRASTRUCTURE SIGNAL AND COVERAGE (PREREG-1 7.4)

**fpylll is ABSENT on this host** (`ModuleNotFoundError`). Consequences,
reported as coverage and never as evidence:

* route **RD** (recomputation through the frozen HKZ pipeline) could not be run
  at any cell for `lam1n` or `hkz`: 38 / 38 cells uncovered for each. Nothing
  was estimated, substituted or inferred for them.
* VAR-F for `lam1n` and `hkz` is therefore uncomputable on this host, and route
  RC cannot supply it either — BATCH-9e3584 computed no fibre family — so the
  FULL G-VAR2 verdict for both is UNCOVERED at every cell.
* the 20 d in {100, 140} cells for `lam1n`/`hkz` were already NOT COMPUTED in
  the committed file under the declared d <= 40 reduction bound.

**A missing dependency is never negative mathematical evidence and no branch of
PREREG-1 §7 may be reached through one** (AGENTS.md rule 5). The F0 failure
recorded above was NOT reached through one: it is in the reduction-free
determinant-only half, at full 38/38 coverage on six routes.

No timeout, crash, retry or resource exhaustion occurred. Measurement wall clock
**2.037 s** against a 600 s cap; peak RSS **50.0 MB** against a 4 GB cap
(`ulimit -v 4194304` applied); one run, as budgeted.

---

## E. COULD-NOT-FAIL ARRANGEMENTS — MEASURED IN BOTH DIRECTIONS, NOT CITED

* **6.2 could-not-FIRE** (the criterion could never refuse anything). MEASURED:
  `X_null` in F0 has between-basis sd exactly 0.0 at 38 / 38 cells under R0 and
  under R1 (n_exactly_zero = 38 in both), so `D_c = 0 < tau_var`. This run
  emitted **1142 REFUSE verdicts**. WE ARE NOT IN THIS ARRANGEMENT.
* **6.3 could-not-PASS** (the criterion could never admit anything). MEASURED:
  `hkz` RC max `D_c` = 2.833e-1 with max between-basis sd 3.924e-2; `rawtail`
  RD max `D_c` = 8.751e-2. This run emitted **302 ADMIT verdicts** and 129
  VAR-S ADMIT cells. WE ARE NOT IN THIS ARRANGEMENT.
* **6.4 could-not-FAIL on the fibre clause** (VAR-F might refuse everything).
  MEASURED: VAR-F PASSES at 38 cells in each of `rdet`|R2, `rdet`|R4,
  `rdet`|R5 (F0 and F1) and at 37 cells for `rawtail`|RD in each family, plus
  `V_evade` throughout. The clause is not a constant. (`X_gso_k` is rider (ii)'s
  object and is NOT scored here.)
* **6.4 could-not-PASS on the fibre clause** (a fibre family that failed to hold
  the nuisance argument fixed would pass everything). GUARDED AND MEASURED: the
  fibre determinant guard holds at every fibre family and every lattice (§B).
  WE ARE NOT IN THIS ARRANGEMENT.
* **6.5 AM-16(f)**: N/A with its reason — this batch estimates no standard error
  and applies no variance decomposition.

---

## F. THE CONSISTENCY CHECK OF PREREG-1 4.3 — P-R26: **HOLDS**

Definitional, through-the-matrix `X_null` (route R1_slogdet) reproduces the
notarized BATCH-9e3584 prereg 2.6 table to 6 decimals at **38 of 38 F0 cells, at
all 8 bases** (304 / 304 cell-basis values; max abs deviation after rounding
0.0). Labelled a **CONSISTENCY CHECK under AM-15(a)**; it is reported and does
not count as a prediction. The per-route counts are in
`results_gvar2.json → P_R26.per_route_cellsxbases`.

Additional consistency check (AM-15(a), not a prediction): `rawtail` through the
transcribed RD raw-GSO path reproduces the committed RC per-cell between-basis
sd and per-cell mean at 38 / 38 cells, max abs difference **0.0** in both.

---

## G. PREDICTION REGISTER ROWS THIS TASK OWNS (PREREG-1 §9)

All eight items of §9 were **OPEN at notarization**; none had been evaluated by
anyone when the text was frozen.

| id | class | open at notarization | outcome measured here |
|---|---|---|---|
| P-F0 | PREDICTION | OPEN (1 of 8) | **NOT MET**: `rdet` is ADMITTED at 38/38 cells through R2, R4 and R5; `rawtail` through RD misses at 1 of 38 cells; the `lam1n`/`hkz` half is UNCOVERED |
| P-F1 | PREDICTION | OPEN | **NOT MET** as measured (`rdet` ADMITTED through R2, R4, R5) — reported, and NOT to be treated as informative under §7.3 |
| P-G1 | MUST-PASS GUARD | OPEN | **PASSES**: crossing at 38/38 cells on every route |
| P-V1 | CONSISTENCY CHECK (AM-15(a)) | OPEN | **HOLDS** |
| P-R26 | CONSISTENCY CHECK (AM-15(a)) | OPEN | **HOLDS** |

Not owned here: **P-FR1** (rider ii, TASK-20260812-4b8ede), **P-C1** (rider i,
TASK-20260812-78a6e3), **P-L1** (rider iii, TASK-20260812-0e930c). PREREG-1 §9's
frozen accounting stands: five predictions, two consistency checks (not
counted), one must-pass guard.

---

## H. THE TERMINATION BRANCH

Read off **R2-OUT-1 and R2-OUT-2 under R2-OUT-V's precedence, and nowhere else**
(PREREG-1 §10). R2-OUT-V does not fire. R2-OUT-1 = FAIL. Under the frozen
precedence — "F0's verdict is evaluated before F1's. If F0 fails, T-F0FAIL fires
whatever F1 does" — the branch is:

### **T-F0FAIL** (reported with the §7.4 suffix as **T-F0FAIL-PARTIAL**)

**Clause it fires under, quoted from PREREG-1 7.3:** "**FIRES WHEN:** F0 FAILS at
one or more covered cells or routes — whatever F1 does."

The `-PARTIAL` suffix is carried per PREREG-1 7.4 ("the branch that fires is
reported with the suffix `-PARTIAL`") because declared coverage is missing:
route RD for `lam1n` and `hkz` (fpylll absent) and the full G-VAR2 verdict on
the ADMITTED half. The suffix changes nothing about which branch fired: T-F0FAIL
fires from the fully-covered, reduction-free determinant-only half.

**MEANS (PREREG-1 7.3):** AM-16(a) itself needs replacing, and that is reported
as such.

**LICENSES:** a decision recording that the AM-16(a) operationalization does not
reproduce its own declared target behaviour on the fixture it was written
against. Specifying a replacement is a Coordinator act in the successor
decision, not a producer act here — and none is specified here.

**FORBIDS:**
* proceeding to C3 behind G-VAR2;
* treating the F1 result as informative;
* presenting this F0 failure as evidence about any lattice, any observable's
  admissibility, or any proposition in this goal — it is an instrument outcome;
* reading a failure caused by a missing dependency, a timeout or a crash as an
  F0 failure at all (none was: see §D);
* closing, pausing or completing GOAL-MLKEM-005.

I do not argue for a different branch, do not re-read the clause, and report no
branch the numbers do not fire.

---

## I. OBJECTIONS TO THE FROZEN TEXT — RECORDED, AND THE TEXT WAS RUN AS WRITTEN

Recorded as findings under the handoff's instruction, having implemented every
clause exactly as frozen. **Nothing below was applied to any verdict above.**

1. **The fibre clause's bit-identity fallback re-imports the route dependence
   the fixtures were built to expose.** PREREG-1 3.3 decides non-constancy at a
   `scale_degenerate` fibre cell by `bit_identical()`. That statistic is a
   property of the arithmetic route, which is precisely what PROBE-N
   established. For a beta-free candidate BOTH `R_{d,k}` and `R^fib_{d,k}` are
   0, so the whole G-VAR2 verdict rests on bit-identity of float values that
   differ by 1e-13 to 1e-7 between bases whose exact determinants are equal.
   That is what admitted `rdet` here.
2. **PREREG-1 3.2's own aside is contradicted by the measurement.** It states
   that under the frozen rule "`rdet` is refused at scale_degenerate cells
   (constant on the fibre)". `rdet` is constant on the fibre in EXACT arithmetic
   and under routes R0, R1 and R3; it is NOT constant under R2, R4 and R5. The
   aside is not a registered prediction and was not scored as one; it is
   recorded because a successor re-deciding §3.2 should see it.
3. **Route RD is ambiguous for `rawtail`.** PREREG-1 2.5 declares routes RC and
   RD for `rawtail`, writing RD as "recomputation through the FROZEN HKZ
   pipeline ... fpylll pinned at 0.6.4"; but `rawtail` is computed inside that
   frozen pipeline from the RAW, UNREDUCED basis and needs no reduction and no
   fpylll. I ran that recomputation, labelled it `RD_rawgso_no_reduction`,
   reported RC unchanged beside it, and flagged in the JSON that a reviewer who
   reads RD as strictly requiring fpylll should read that row as UNCOVERED. F0's
   verdict does not depend on the choice: it FAILS from `rdet` alone.
4. **The two-route requirement is unsatisfiable on this host for `lam1n` and
   `hkz`** (RC only, RD needs fpylll). Reported as coverage, not worked around.

---

## J. SCOPE, BINDING CARRIES AND WHAT THIS RUN CANNOT DO

**SCOPE.** q = 3329; d in {20, 30, 40, 100, 140}; the frozen k and beta grids; 8
bases per lattice per family; families F0, F1, F0|fib and F1|fib with fibre seed
prefixes 2, 3 and 4; six declared arithmetic routes for determinant-only
candidates; RC (and, for `rawtail`, the reduction-free recomputation) for the
rest; no reduction was run at all. Every observation is scoped to exactly that
and transports nowhere.

**BINDING CARRIES, in force and not re-litigated** (PREREG-1 §§11, 11.1):
AM-10 through AM-14 (DEC-20260808-05b684); AM-15 and AM-16 (DEC-20260809-afe29b)
as extended by AM-17 (DEC-20260812-7c4a1e); **AM-3 IS NOT RETIRED** and its
0.096 family-wise false-failure bound stands; **BATCH-a44d08 IS NOT RESCORED IN
ANY RESPECT** and its Section C verdict and detection floors remain VOID IN BOTH
DIRECTIONS; AM4-OBS-1 is cited ONLY through `knowledge/findings/KN-FIND-f38a89.md`;
**AM-9**: fpylll's k counts the q-scaled rows, NOT the identity block; **the
G-VAR refusal is cited ONLY as conditional on the frozen family F0**;
`knowledge/INDEX.md` is not written, regenerated or staged; **CLAIM TIER STAYS
TOY**.

**NOT CITABLE ANYWHERE IN THIS BATCH** (carried in full): "a factor of 6 to 31"
— the citable range is **4.87x to 31.03x**; "no admissibility claim is reportable
in either direction" — replaced by DEC-20260812-7c4a1e C-2's three-part
decomposition; the "genuinely cross-platform" reading of the L7/L8 agreement —
the citable form is PORTABILITY across three textually distinct implementations
with fpylll pinned at 0.6.4; both sub-6x counts, pending rider (i); "the null
fires more often than the real arm" as a general statement; "G-VAR cannot be
tuned into or out of firing" — FALSE; "three predictions of actual empirical
content" — the official count for BATCH-9e3584 Section R remains ONE; the
blanket "Residuals are 0 identically" — cite per transform (0.0 for `X_null`
under all transforms and for `rdet` under T2 and T3; 3.865e-12 for `rdet` under
T1); "the obstruction is relocated"; "CONSISTENT" in either direction; **"29 of
48" without the exact-null benchmark of 47 of 48 in the same sentence**; the
3.91% floor without its NEGATIVE-VARIANCE-COMPONENT qualifier (the
non-degenerate figure is 10.83%).

**WHAT THIS RUN CANNOT DO.** It cannot say anything about ML-KEM, any FIPS 203
parameter set, any attack cost or any cost model. It cannot measure a
false-refusal rate. It cannot establish that any observable carries lattice
information — PREREG-1 3.5: passing G-VAR2 carries no such claim, and neither
does failing it. It cannot revalidate BATCH-9e3584 or BATCH-cbe023. It cannot
close, pause or complete GOAL-MLKEM-005.

**INDEPENDENCE IS PROCEDURAL AND NEVER MODEL-LEVEL.** AGENTS.md rule 12 is UNMET
AND UNWAIVED in this goal and is not waived here; this producer records
`model_verified: false` with its reason in `run_manifest.yaml`.
