# TASK-20260813-630414 — hkz mutation-testing (positive) control — write-up

    goal        GOAL-MLKEM-005
    batch       BATCH-8d09f5
    task        TASK-20260813-630414 (executor, lead producer)
    governed by PREREG-6 (coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/
                tasks/TASK-20260813-4aec9a/prereg.md), notarized in commit
                dcaac725f65da93c0ab27eeed970d6d10b2bcde1 (verified below to be
                an ancestor of this run's HEAD, and via `git log --all` to be
                the sole commit touching prereg.md, i.e. the notarization
                point, before trusting the text)
    claim tier  TOY, UNCONDITIONALLY
    role        executor
    requested policy   executor-implementation, effort medium
    runtime     Claude Code (Sonnet 5). model_verified: false — AGENTS.md
                rule 12 is unmet and unwaived in this goal; this session's
                own model identity is not independently verified, exactly
                as PREREG-6 section 5 requires be recorded.

**WHAT THIS TASK IS, RESTATED.** This is NOT a fourth ROUTE-P-vs-independent-
route comparison. It is a mutation-testing (positive) control on the
`D_route`/`D_route''` comparison MECHANISM itself: a deliberately injected,
precisely-described, known defect (a one-line seed-index off-by-one) in a
COPY of code the campaign's routes are licensed to share, checked against
whether the EXISTING, unchanged comparison formula (`PREREG-3` §3.3) actually
flags it. Its outcome, whichever branch fires, says nothing about `hkz`'s
admissibility, does not re-litigate `T-HKZINDEP-CONFIRMED`
(`BATCH-a6fab5`), and does not close, pause, or complete `GOAL-MLKEM-005`.

---

## Every path this task wrote

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/measure_hkz_mutation6.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/results_hkz_mutation6.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/hkz_mutation6_writeup.md   (this file)
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/run_manifest.yaml
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-8d09f5/tasks/TASK-20260813-630414/environment.json

All 8 file names match the task card's suggestions exactly; none were
renamed. Nothing was written outside this task's `write_scope`. No commit
was made by this task (the Coordinator's snapshot task, `TASK-20260813-cb8943`
per the task card's `archived_by` field, does that separately).

---

## 1. Infrastructure re-verification (PREREG-6 section 1) — R-MC-OUT-0

Performed fresh, in this task's own session, before any other code was
written, exactly as PREREG-6 section 1 requires (it explicitly does NOT
license assuming availability from any prior batch's own check).

- `import fpylll`, `import cysignals`, `from fpylll import IntegerMatrix,
  LLL, BKZ, GSO, Enumeration`, `from fpylll.fplll.bkz import
  BKZReduction` — all succeeded.
- `fpylll.__version__` = `0.6.4`. `cysignals.__version__` reported
  `"unknown"` from the module attribute itself, but `pip freeze` (captured
  in `environment.json`) shows `cysignals==1.12.5`, matching the version
  every prior batch of this lineage (`PREREG-5`, `BATCH-a6fab5`) recorded.
- Smoke test: LLL reduction of an 8x8 random integer matrix completed
  (seed `20260813`, matching `measure_hkz_indep.py`'s own precedent
  smoke-test seed for direct comparability of the check itself, not of any
  measured value). First row after reduction:
  `[-10, -9, 2, -15, 17, -14, 15, -7]`.

**Outcome: `fpylll`/`cysignals` are available and functional in this task's
own session. Branch A (fpylll's own public API) is used, per PREREG-6
section 1. `T-MUTCTRL-NODATA` branch (b) did NOT fire.** This is reported
plainly as infrastructure signal only (`AGENTS.md` rule 5) — it is not
evidence for or against the instrument's power, which is what the rest of
this document addresses.

---

## 2. Independent recomputation of the frozen prediction (PREREG-6 section
##    2.3 / 2.4 point 1) — R-MC-OUT-0b

PREREG-6 section 7 states plainly that its own section-2.3 arithmetic was
performed by hand, by a shell-less Coordinator session, and explicitly
requires this executor's own independent recomputation before proceeding,
with any mismatch reported as a finding about PREREG-6 itself, never
silently corrected or substituted.

This task's own recomputation (`measure_hkz_mutation6.py`'s
`recompute_frozen_prediction`, embedded in the run and its own JSON output
at `R_MC_OUT_0b_prediction_recomputation`) reads `results_relvar.json`'s own
`G_REL1.hkz.L7.per_basis[i].X_a` (i=0..7) and
`G_REL1.hkz.L11.per_basis[i].X_b` (i=0..7) arrays directly, computes the
cyclic adjacent-basis max-abs-difference, and compares to PREREG-6's stated
numbers:

| cell | this task's own recomputed max | PREREG-6 stated | match |
|---|---|---|---|
| `hkz/L7_b5`   | `0.0665893489077094`  | `0.0665893489077094`  | **YES, bit-exact** |
| `hkz/L11_b30` | `0.00948000985335451` | `0.00948000985335451` | **YES, bit-exact** |

`results_relvar.json`'s own sha256 was independently re-verified as
`c5b2918dccf1b58261eed1e9d221f1074ae6143f2a8fc5c0f42ff475646ccd6d`, matching
PREREG-6 section 2.1's declared value bit-exact (checked via `sha256sum`
before any Python arithmetic ran).

**Outcome: this task's own independent recomputation matches PREREG-6's
stated numbers exactly, at both cells. No disagreement is reported — there
is no finding about PREREG-6 itself to file here.** `s_c^fib` was also
independently read (never recomputed, per PREREG-6 section 2.1): `hkz/L7_b5`
= `0.023887966155964283` (PREREG-6 states `0.023888` to the precision it
reports — matches), `hkz/L11_b30` = `0.003818306775026579` (PREREG-6 states
`0.003818` — matches).

---

## 3. The mutant file and its mechanical diff (PREREG-6 section 2.2 / 2.4
##    point 2) — R-MC-OUT-1

`measure_hkz_mutation6.py` contains a copy of `measure_hkz_indep.py`'s four
`ROUTE-I''`-building functions (`route_ii_make_A`, `route_ii_build_basis`,
`hkz_route_ii`, `route_ii_hkz_value`), each renamed with a `_mut` suffix,
with **exactly one functional line changed**, inside the copy of
`route_ii_make_A` only:

```
- rng = np.random.default_rng([1, d, k, i])
+ rng = np.random.default_rng([1, d, k, (i + 1) % n_bases])   # MUTATED
```

`measure_hkz_indep.py` itself was never edited, and was never `import`ed —
it was read only as plain text (via Python's `ast` module, a read-only
parse of its source, inside `measure_hkz_mutation6.py`'s own
`extract_function_sources`) purely to build the diff below mechanically,
at run time, rather than by prose assertion.

**Deviation recorded, per the rule that all deviations are recorded rather
than discarded.** A first draft of the mutant file, written before this
recorded run, inadvertently dropped two inline comment blocks inside
`hkz_route_ii_mut` and reworded the `route_ii_hkz_value_mut` docstring
beyond a mechanical name change. This was NOT caught by manual review — it
was caught by the mechanical diff step itself (`build_mechanical_diff`),
which is exactly the kind of defect this whole document exists to test
whether a comparison instrument catches. That draft was never run to
completion as a measurement and produced no run artifact; it was corrected
in place before this run, restoring the two comment blocks and the
docstring verbatim from the frozen file. The diff below is the diff of the
CORRECTED file, embedded in this run's own `results_hkz_mutation6.json` at
`R_MC_OUT_1_mechanical_diff.unified_diff`, generated by
`difflib.unified_diff` inside the run itself (not hand-assembled
afterward):

```diff
--- measure_hkz_indep.py (4 named functions, frozen)
+++ measure_hkz_mutation6.py (4 _mut functions)
@@ -1,15 +1,15 @@
-def route_ii_make_A(d, k, q, i):
-    rng = np.random.default_rng([1, d, k, i])
+def route_ii_make_A_mut(d, k, q, i, n_bases=N_BASES):
+    rng = np.random.default_rng([1, d, k, (i + 1) % n_bases])   # MUTATED
     return rng.integers(0, q, size=(k, d - k), dtype=np.int64)
 
-def route_ii_build_basis(d, k, q, i):
+def route_ii_build_basis_mut(d, k, q, i):
     B = np.zeros((d, d), dtype=np.int64)
     B[:k, :k] = np.eye(k, dtype=np.int64)
-    B[:k, k:] = route_ii_make_A(d, k, q, i)
+    B[:k, k:] = route_ii_make_A_mut(d, k, q, i)
     B[k:, k:] = q * np.eye(d - k, dtype=np.int64)
     return B
 
-def hkz_route_ii(B, d, deadline_ts):
+def hkz_route_ii_mut(B, d, deadline_ts):
     """Returns a dict with status, r (post-reduction squared GS norms),
     sweep_rounds, verify_max_residual, secs. Uses fpylll's own public API:
     IntegerMatrix -> GSO.Mat (basis-based, not Gram-based) -> LLL.reduction
@@ -97,7 +97,7 @@
         "secs": time.time() - t0,
     }
 
-def route_ii_hkz_value(r, d, k, beta, q):
+def route_ii_hkz_value_mut(r, d, k, beta, q):
     """The hkz observable's own definition (reused identically -- see the
     INDEPENDENCE DECLARATION at the top of this file). r = squared GS
     norms after ROUTE-I''s own reduction/enumeration."""
```

**Mechanical accounting, computed by the script, not asserted by prose:**
`n_removed_lines = 6`, `n_added_lines = 6`. Of those 6+6 pairs: **4 are
def-line / call-site renames** (cosmetic, the `_mut` suffix, unavoidable
given every function is being copied under a new name so its call sites
must agree) and **exactly 1 pair (`n_functional_change_pairs = 1`) is the
named functional change** — the seed-formula index argument. The remaining
line pair is the blank-line context around function boundaries, which
`difflib` reports identically on both sides (not a diff line). **Confirmed
mechanically: exactly one functional line differs between the mutant file
and `measure_hkz_indep.py`, plus the cosmetic renames PREREG-6 section 2.4
point 2 explicitly permits and requires be shown as such — both conditions
are met.**

---

## 4. Per-cell measurement (PREREG-6 section 2.4 points 3-6) — R-MC-OUT-2

**The detection mapping, quoted in full so a reader does not have to
cross-reference PREREG-6 (section 2.4 point 5):** `VERDICT_mut = "DOES NOT
EXCEED"` at a cell means the injected defect pushed `D_route_mut` far
enough above `s_c^fib` that the ordinary comparison correctly signals a
route disagreement — **this is the DETECTED outcome**, demonstrating real
instrument power against this defect. `VERDICT_mut = "EXCEEDS"` at a cell
means `s_c^fib` still swamps `D_route_mut` despite the injected defect —
**this is the NOT-DETECTED outcome**: the instrument would silently pass
this specific shared-code defect through as agreement.

Both named cells were fully computed, 8/8 matched bases each, well inside
budget (total wall time 8.14 s against a 3600 s hard cap):

| cell | `D_route_mut` | `s_c^fib` | matched bases | `VERDICT_mut` | reading | matches frozen prediction |
|---|---|---|---|---|---|---|
| `hkz/L7_b5`   | `0.06658934890771118`  | `0.023887966155964283`  | 8/8 | `DOES NOT EXCEED` | **DETECTED** | yes (predicted `0.0665893489077094`) |
| `hkz/L11_b30` | `0.00948000985335451`  | `0.003818306775026579`  | 8/8 | `DOES NOT EXCEED` | **DETECTED** | yes (predicted `0.00948000985335451`) |

`D_route_mut` was computed exactly per `PREREG-3` §3.3's own formula,
reused verbatim: `max` over matched bases `i` of
`|hkz_ROUTE-P(L, b, i) - hkz_ROUTE-MUT(L, b, i)|`, against
`results_relvar.json`'s own `G_REL1.hkz` per-basis values — never
`results_l7l8.json`/`results_am4.json`. `s_c^fib` is the same
already-archived `G_VAR.per_candidate.hkz.per_cell.<L>_<b>.float_sd` value,
read, not recomputed. No new dispersion criterion, gate, or threshold was
introduced anywhere in this run.

`HEURISTIC-M1` note (PREREG-6 section 2.3): both cells' measured
`D_route_mut` agrees with the frozen prediction to within ~1e-14 (well
inside the ~2^-49 floor PREREG-6 names) — consistent with, but not proof
of, `HEURISTIC-M1`'s assumption that the mutant's shifted-seed HKZ-quality
reduction converged as reliably as `BATCH-a6fab5`'s own unmutated route.
No basis failed to converge within budget at either cell (`basis_status`:
8/8 `"ok"` at both cells).

---

## 5. Aggregate reading (PREREG-6 section 2.5) — R-MC-OUT-3

    COVERED           = {hkz/L7_b5, hkz/L11_b30}      (2/2)
    DETECTED_SET       = {hkz/L7_b5, hkz/L11_b30}
    NOT_DETECTED_SET   = {}                            (empty)

---

## 6. Termination branch (PREREG-6 section 2.6, fresh 4-branch precedence)
##    — R-MC-OUT-4

`COVERED` is non-empty (rules out `T-MUTCTRL-NODATA`). `|COVERED| = 2`, so
`T-MUTCTRL-MIXED` is checked first and does not fire (the two cells agree,
both `DOES NOT EXCEED`). Both cells agree on `DOES NOT EXCEED`, so:

**`T-MUTCTRL-DETECTED` fires, unsuffixed (`|COVERED| = 2`, no `-PARTIAL`).**

Per PREREG-6's own licensing/forbidding text for this branch: this
licenses citing this as a positive calibration result for the `D_route`
mechanism against THIS defect class (a one-line seed-index off-by-one in
the shared basis-construction helper), at THIS approximate magnitude, at
the 2 cells tested — narrowly. It forbids generalizing to any other defect
class (a sign flip, a logdet-constant error, any defect inside `fpylll`'s
own C/Cython kernel — this run explicitly does not and, reusing `fpylll`'s
library code unmodified, structurally cannot test a defect inside that
library), to any uncovered cell of the other 4 in this goal's 6-cell hkz
set, to any claim about `hkz`'s own admissibility, `T-HKZINDEP-CONFIRMED`'s
own correctness, or any `ML-KEM`/FIPS 203/attack-cost/cost-model claim; and
it does not close, pause, or complete `GOAL-MLKEM-005`.

Per PREREG-6 section 2.6's own declared forward boundary: since
`T-MUTCTRL-DETECTED` fired (unsuffixed), no further mutation-testing
control of this SAME defect class (seed-index off-by-one) at these SAME two
cells is licensed by this document alone. A genuinely different defect
class (the sign-flip or logdet-constant options PREREG-6 section 2.2
declined) would require its own, separately-commissioned Coordinator
decision.

---

## Summary, plainly and symmetrically as required

- **Infrastructure re-verification:** `fpylll` 0.6.4 / `cysignals` 1.12.5
  available and functional in this task's own session. Branch A used.
  `T-MUTCTRL-NODATA` branch (b) did not fire.
- **Independent recomputation of PREREG-6's frozen prediction:** matched
  PREREG-6's stated numbers bit-exact at both cells (`0.0665893489077094`
  at `hkz/L7_b5`, `0.00948000985335451` at `hkz/L11_b30`). No disagreement
  to report.
- **Mechanical diff:** confirmed, by `difflib.unified_diff` run inside the
  script itself (not asserted by prose), that exactly one functional line
  differs between the mutant file and `measure_hkz_indep.py` (the
  seed-index formula in `route_ii_make_A`/`route_ii_make_A_mut`), plus 4
  cosmetic rename lines, all shown above.
- **Per-cell reading:** `hkz/L7_b5` — `D_route_mut = 0.06658934890771118`
  vs `s_c^fib = 0.023887966155964283`, `VERDICT_mut = "DOES NOT EXCEED"`,
  **DETECTED**. `hkz/L11_b30` — `D_route_mut = 0.00948000985335451` vs
  `s_c^fib = 0.003818306775026579`, `VERDICT_mut = "DOES NOT EXCEED"`,
  **DETECTED**.
- **Termination branch: `T-MUTCTRL-DETECTED`** (unsuffixed, `|COVERED| =
  2/2`). This is the outcome PREREG-6 section 2.3 predicted, and it is a
  narrow, positive finding about the `D_route` comparison mechanism's power
  against exactly this one, deliberately injected defect class, at exactly
  these two cells — nothing about any other defect class, any other cell,
  `hkz`'s own admissibility, or `GOAL-MLKEM-005`'s closure is licensed by
  it, per PREREG-6 section 2.6's own forbids list, restated in full above.

This executor makes no claim about whether this outcome "validates" or
"confirms" the instrument in general — that judgment, and any judgment
about what (if anything) follows from it, belongs to the Validator, Red
Team, and Coordinator reviewing this run.
