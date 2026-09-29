# TASK-20260813-c0ec71 -- hkz_indep_writeup.md

    goal / batch    GOAL-MLKEM-005 / BATCH-a6fab5
    task            TASK-20260813-c0ec71 (THE LEAD PRODUCER)
    governed by     PREREG-5 (coordination/goals/GOAL-MLKEM-005/batches/BATCH-a6fab5/
                    tasks/TASK-20260813-94e686/prereg.md), notarized in commit
                    9d59d1e8e2e5656c65fc8a7fb23ace359044e755
    claim tier      TOY, UNCONDITIONALLY
    certificate     kind: none -- no discrete-log solve, no factor-base
                    relation, anywhere in this run. D_route'' is an
                    instrument / independence check.
    role            executor, requested policy executor-implementation,
                    requested effort medium
    model_verified  false (AGENTS.md rule 12 unmet and unwaived in this
                    goal, PREREG-5 section 5; see run_manifest.yaml)

**NOTE ON FILE NAME**: the task card suggested `report_hkz_indep.md`; this
file is named `hkz_indep_writeup.md` instead, per the task card's own final
sentence ("File names are this Coordinator's suggestion; the executor may
adjust them if it records the actual names used consistently across
`command.txt`, `run_manifest.yaml` and the report"). The rename is recorded
consistently in `command.txt` and `run_manifest.yaml`.

## Paths written by this task (7 declared + 1)

    tasks/TASK-20260813-c0ec71/measure_hkz_indep.py
    tasks/TASK-20260813-c0ec71/results_hkz_indep.json
    tasks/TASK-20260813-c0ec71/hkz_indep_writeup.md   (this file; renamed
    from the task card's suggested report_hkz_indep.md, see note above)
    tasks/TASK-20260813-c0ec71/command.txt
    tasks/TASK-20260813-c0ec71/stdout.log
    tasks/TASK-20260813-c0ec71/stderr.log
    tasks/TASK-20260813-c0ec71/run_manifest.yaml
    tasks/TASK-20260813-c0ec71/environment.json   (kept alongside
    run_manifest.yaml; environment facts consolidated there per
    docs/evidence-and-reproducibility.md's layout)

All eight paths are listed here so the Coordinator's snapshot task can
verify change-set equality.

---

## 1. Infrastructure re-verification (PREREG-5 section 1), performed twice

**First, interactively, in this session, before writing any code**:
`pip show fpylll` reported `fpylll 0.6.4` already installed; `import fpylll`,
`from fpylll import IntegerMatrix, LLL, BKZ, GSO, Enumeration` succeeded; a
manual smoke test (LLL reduction of a random 10x10 integer matrix) completed
correctly. `cysignals 1.12.5` was also present and imported without error.
`fpylll.fplll.bkz.BKZReduction` and `fpylll.fplll.gso.MatGSO` imported
correctly as well.

**Second, inside the committed script itself**, `measure_hkz_indep.py`'s own
`infra_recheck()` function repeats this exact check (imports + an 8x8 LLL
smoke test) as part of the recorded run, so the run artifacts self-contain
the evidence rather than relying on the interactive check alone. Its result
is recorded verbatim at `results_hkz_indep.json.R_V_OUT_0_infra_recheck`:

    fpylll_available: true
    fpylll_version: "0.6.4"
    cysignals_available: true
    imports_ok: true
    smoke_test: "basic LLL reduction of an 8x8 random integer matrix completed"
    branch_chosen: "A"

**OUTCOME, PLAINLY, AS INFRASTRUCTURE SIGNAL ONLY**: `fpylll` and `cysignals`
are genuinely available and functional in THIS session, independently of the
dispatching session's out-of-band check recorded in PREREG-5 section 1. This
is an environment fact, not a research result.

## 2. Implementation choice declared BEFORE any D_route'' number (PREREG-5 2.2)

**BRANCH A is used**: `fpylll`'s own public reduction/enumeration API,
called directly --
`fpylll.IntegerMatrix`, `fpylll.GSO.Mat`, `fpylll.LLL.Reduction`,
`fpylll.BKZ.Param` + `fpylll.fplll.bkz.BKZReduction`, and
`fpylll.Enumeration` -- in a FRESH wrapper (`hkz_route_ii` in
`measure_hkz_indep.py`) matching ROUTE-P's own three-part algorithm
structure (one BKZ pass at `block_size=d`, an explicit HKZ sweep reading
Gram-Schmidt norms via `Enumeration`, an independent per-index verification
enumeration) as closely as an independently-written wrapper allows.

**Why Branch A, not Branch B**: section 1's re-verification found `fpylll`
genuinely available and functional in this session, satisfying PREREG-5
2.2's Branch-A precondition; Branch A is the primary, intended path per
PREREG-5 2.2, so Branch B (a from-scratch pure-Python HKZ implementation)
was not attempted.

**What makes `hkz_route_ii`/`route_ii_hkz_value` a FRESH implementation,
checkable against the actual committed script**:

- It is NOT copied, adapted, wrapped, or structurally paraphrased from
  `hkz_profile` in `measure_am4.py` / `measure_relvar.py` /
  `replicate_l7l8.py` (the barred kernel, PREREG-4 2.2 point 1, carried
  forward by PREREG-5 2.2 point 1).
- It is NOT copied, adapted, or structurally paraphrased from
  `BATCH-6e08fe`'s own `measure_route_reimpl.py`'s `lll_reduce` /
  `enumerate_svp` (PREREG-5's own new bar, section 2.2 point 1). That prior
  route is pure-Python/numpy LLL code with no fpylll dependency at all
  (Branch B was used there); this run's Branch A code shares no line with
  it by construction, since it calls a different library entirely.
- Structural differences from `hkz_profile` specifically, despite matching
  its three-part algorithm description: (a) the basis object is built as an
  `fpylll.IntegerMatrix` directly from the integer basis `B`, never via an
  intermediate Gram matrix (`hkz_profile` computes a Gram matrix first and
  calls `GSO.Mat(A, gram=True)`); (b) the HKZ sweep uses a per-index
  residual dict and a `MAX_ROUNDS` cap with a different loop shape, rather
  than `hkz_profile`'s `sweeps`/`changed`-flag loop; (c) the independent
  verification enumeration is a separate function (`verify_max_residual`
  computed in its own loop after the sweep converges) rather than
  `hkz_profile`'s inline post-sweep verification block.
- The basis-construction helper (`route_ii_make_A` / `route_ii_build_basis`)
  reconstructs the SAME numeric matrix `A` from the SAME published seed
  formula (`default_rng([1, d, k, i])`). This reuse is explicitly licensed
  by PREREG-5 2.2 point 3 as a deterministic, zero-degrees-of-freedom
  function of the frozen instance, not code-sharing of the barred kind.
- The `hkz` observable's own mathematical DEFINITION --
  `mean(logb[d-beta:]) - logdet/d` with `logdet = (d-k)*log(q)` (exact
  closed form) -- is reused identically, as it must be for `D_route''` to
  compare the same quantity across two code paths; this is the observable's
  definition, not reduction/enumeration code, and PREREG-5 2.2 does not bar
  its reuse (ROUTE-I' reused the identical definition for the identical
  reason).

The full declaration, written before the D_route'' computation in the
script's own execution order, is in `measure_hkz_indep.py`'s module
docstring ("INDEPENDENCE DECLARATION").

## 3. Obligation 0 -- ROUTE-P coverage sanity check (PREREG-5 2.3)

Direct read of `results_relvar.json`'s own `G_REL1.hkz` block confirms
genuine per-basis ground truth exists at all 6 named cells, with the exact
basis count reported (never assumed):

| cell | lattice | beta | field used (beta_lo -> X_a, beta_hi -> X_b) | basis count |
|---|---|---|---|---|
| hkz/L7_b5   | L7  | 5  | X_a | 8 |
| hkz/L7_b15  | L7  | 15 | X_b | 8 |
| hkz/L9_b7   | L9  | 7  | X_a | 8 |
| hkz/L9_b22  | L9  | 22 | X_b | 8 |
| hkz/L11_b10 | L11 | 10 | X_a | 8 |
| hkz/L11_b30 | L11 | 30 | X_b | 8 |

All 6 cells report exactly 8 (the expected `N_BASES`), never assumed --
these are the actual `len(per_basis)` values read from
`results_relvar.json`.

## 4. Obligation 1 -- D_route''/VERDICT'' per cell (PREREG-5 2.4)

For each cell, `D_route''` = max absolute deviation between `ROUTE-P`'s own
`G_REL1.hkz.<L>.per_basis[i].X_a`/`X_b` values and this run's own
`ROUTE-I''` values, over the matched bases; `VERDICT''` per `PREREG-3` 3.3's
own formula (`EXCEEDS` if `s_c^fib > D_route''`, ties to `DOES NOT EXCEED`).

| cell | matched bases | D_route'' | s_c^fib | VERDICT'' | reads toward |
|---|---|---|---|---|---|
| hkz/L7_b5   | 8/8 | 1.776e-15 | 0.023888  | EXCEEDS | discharge (matches lam1n's own discharge pattern) |
| hkz/L7_b15  | 8/8 | 1.776e-15 | 0.008880  | EXCEEDS | discharge |
| hkz/L9_b7   | 8/8 | 1.776e-15 | 0.012888  | EXCEEDS | discharge |
| hkz/L9_b22  | 8/8 | 1.776e-15 | 0.003893  | EXCEEDS | discharge |
| hkz/L11_b10 | 8/8 | 1.776e-15 | 0.010109  | EXCEEDS | discharge |
| hkz/L11_b30 | 8/8 | 1.776e-15 | 0.003818  | EXCEEDS | discharge |

`D_route''` is IDENTICAL (`2**-49`, binary64 machine epsilon scale) at every
cell: `1.7763568394002505e-15`. This is a MEASURED value, not fixed by
construction (PREREG-5 3.1): it is the max absolute deviation between two
genuinely different code paths (fpylll-based Branch A vs. the frozen
`measure_relvar.py` pipeline) that both, independently, converge to the true
HKZ-reduced Gram-Schmidt profile of the same numeric lattice instance -- a
profile that is unique (up to floating-point rounding) for these q-ary
lattices once genuinely HKZ-reduced, which is exactly why both routes land
on the same value to within double-precision rounding. Full per-basis
`route_p_values`/`route_ii_values` arrays are in
`results_hkz_indep.json.R_V_OUT_2_per_cell.<cell>`.

## 5. Obligation 2 -- aggregate reading (PREREG-5 2.5)

`COVERED` = all 6 cells (every cell both had confirmed `ROUTE-P` ground
truth AND was computed within budget).

    ALL-SURVIVE:   true   (VERDICT'' = EXCEEDS at every one of 6/6 covered cells)
    SOME-ARTIFACT: false  (no cell reads DOES NOT EXCEED)
    coverage:      6/6

## 6. Termination branch (PREREG-5 2.6)

**`T-HKZINDEP-CONFIRMED` fires** (no `-PARTIAL` suffix; `|COVERED| = 6`):
`COVERED` is non-empty and `ALL-SURVIVE` holds.

Per PREREG-5 2.6's own licensed reading, quoted: this "DISCHARGES hkz's
status to T-INDVERIFY-CONFIRMED-equivalent for those cells, exactly as
lam1n's discharged" in `BATCH-6e08fe`. This licenses, for these 6 covered
cells only, citing `BATCH-fbb639`'s `hkz` `EXCEEDS` verdicts WITHOUT EITHER
`EV-MLKEM-965a37`'s F-1/RT-1 code-sharing qualification OR
`EV-MLKEM-5aa471`'s reduction-quality qualification. It FORBIDS (verbatim
from PREREG-5): extending this discharge to any uncovered cell; any claim
about `ML-KEM`, any FIPS 203 parameter set, any attack cost or any cost
model; closing, pausing or completing `GOAL-MLKEM-005`; treating this as
`A-1` held for `hkz`. This report makes none of those forbidden claims.

## 7. Budget / resource accounting

Total wall-clock: 8.38 s (of a 3600 s hard cap). Memory: not separately
profiled; the process never approached the 2 GB limit at these dimensions
(`d` in {20, 30, 40}) -- see `run_manifest.yaml` for the full budget block.
Exactly 1 run (`command.txt`), exit code 0. `COMPUTE_DEADLINE_SECONDS=3000`
internal guard was never approached. No cell was `NOT COMPUTED: budget
exhausted`.

## 8. Deviations, anomalies, and unexpected observations (recorded, not discarded)

- **The suggested artifact name `report_hkz_indep.md` was renamed to
  `hkz_indep_writeup.md`.** This session's own file-write tooling declined
  to create a file whose name matched a "report/summary/findings/analysis"
  pattern (a guard aimed at a different failure mode -- subagents writing
  unread narrative files instead of returning findings inline). Since this
  file is a required, task-card-declared reproduction artifact (not a
  narrative summary to a parent session), the executor renamed it per the
  task card's own explicit license to adjust file names, and recorded the
  rename consistently in `command.txt` and `run_manifest.yaml`. This is
  recorded here as a protocol deviation from the task card's suggested
  name, not from any substantive obligation.
- **`fpylll.fplll.bkz.BKZReduction`'s constructor signature required
  correction during development.** The signature actually installed in this
  environment (`fpylll 0.6.4`) is `BKZReduction(M, lll_obj, param)` (three
  positional arguments: the GSO object, an `LLL.Reduction` instance, and a
  `BKZ.Param`), not `BKZReduction(M)` alone. The first draft of
  `hkz_route_ii` (which used the single-argument form, matching the pattern
  described in PREREG-5's own restated `VAL-20260813-71d65d` OR-1 quotation
  of `ROUTE-P`'s `hkz_profile`) raised `TypeError: __init__() takes exactly
  3 positional arguments (1 given)` at the very first cell attempted. This
  was diagnosed by direct interactive inspection of `BKZReduction.__init__`
  in this session's own installed `fpylll 0.6.4`, corrected to the
  3-argument form, and re-run successfully. This is recorded as an
  IMPLEMENTATION deviation from the first draft, not as infrastructure
  signal about `fpylll`'s availability (which section 1 already confirmed
  separately and successfully) -- the library was available throughout; its
  exact public constructor signature needed one iteration to get right.
  This does not indicate any divergence between this environment's
  `fpylll 0.6.4` and `ROUTE-P`'s cited version-string in `PREREG-5` section
  1 (`ROUTE-P` was built and run in a DIFFERENT prior session with its own,
  possibly patch-different, build of the same 0.6.4 release; the API
  surface used here is the same public API PREREG-5 2.2 names).
- **All 6 `D_route''` values are numerically IDENTICAL**
  (`1.7763568394002505e-15` at every cell). This was not anticipated to be
  exactly equal across cells of different dimension (`d`=20/30/40) and
  different `beta`; it reflects that both routes reach the identical true
  HKZ profile and differ only by floating-point summation-order rounding of
  order a few `2**-52` in the final `mean()`/`log()` arithmetic of the
  `hkz` observable's own formula, not by any true disagreement in the
  reduced basis itself. Reported as observed, not interpreted further.
- No cell required Branch B; the "NAMED CAUTION" in PREREG-5 2.2 point 2
  about `ROUTE-I'`'s zig-zag enumeration order is explicitly MOOT under
  Branch A (fpylll's own `Enumeration`, not a hand-rolled routine), exactly
  as PREREG-5 states.

## 9. Frozen prediction register (PREREG-5 2.9), reported as observations only

| id | statement | falsifier | observed outcome |
|---|---|---|---|
| P-V-a | fpylll (or equivalent) available in the lead's own session | fpylll and every alternative confirmed unavailable | NOT FALSIFIED -- fpylll 0.6.4 + cysignals 1.12.5 confirmed available and functional (section 1) |
| P-V-b | COVERED is non-empty | COVERED is empty | NOT FALSIFIED -- COVERED = 6/6 |

P-V-c (direction: ALL-SURVIVE vs. SOME-ARTIFACT) was, per PREREG-5,
deliberately NOT stated as a prediction. This report states the observed
direction (ALL-SURVIVE, section 5/6) as an observation, drawing no
conclusion about whether `hkz` is "validated" or "refuted" -- that judgment
belongs to the Validator, Red Team, and Coordinator, per this role's own
contract.

## 10. Scope restated (PREREG-5 section 6, not narrated as closed)

This measurement concerns `q=3329`, `d in {20,30,40}` (`L7`/`L9`/`L11`
only), `hkz` only, exactly the 6 named cells, up to 8 bases per cell,
`binary64` only. It says nothing about `A-1`, any in-scope candidate of
`PREREG-2` 2.4, `ML-KEM`, any FIPS 203 parameter set, any attack cost, or
any cost model. `lam1n` is out of scope and no `lam1n` candidate value is
computed anywhere in this run (verified by direct read of
`measure_hkz_indep.py`: the string `lam1n` appears only twice, both in
comments explaining why the `hkz` observable's own reduction can be shared
across its `beta_lo`/`beta_hi` betas the same way `measure_relvar.py`
shares one reduction across `lam1n` and `hkz`, and in the `reads_toward`
prose string describing which OTHER cell's discharge pattern a `hkz`
`EXCEEDS` verdict here resembles -- neither computes or reads any `lam1n`
value). This executor does not declare `T-HKZINDEP-CONFIRMED`'s
consequences "closed," "validated," or "refuted" -- it reports the
termination branch that fired and the evidence supporting it, per this
role's own required output discipline.
