# Controls report — RG-0 through RG-4

Task `TASK-20260904-1f4e2f` · Batch `BATCH-256a94` · Goal `GOAL-SSI-001`

## Citation prohibition (restated verbatim; NOT lifted by this artifact)

> The `P=512` crossover value and its `w=2^80` sign are **NOT
> citation-eligible**. This task does not lift that prohibition. Only a
> committed Coordinator decision on independently reviewed evidence can lift
> it.

## Claim boundary

Every control below is arithmetic on already-committed literals plus code and
record reading. Nothing was measured, executed as an experiment, or timed. No
security, standardized-parameter, exponent, or asymptotic-complexity claim is
made in any direction. No status changed; no ledger record was written; nothing
was committed.

Machine-readable results: `anchor_reconciliation.json` → `controls`.
Implementation: `reconcile.py`.

---

## RG-0 — source-state census

**Verdict: `fix_already_applied`.** Full evidence in `source_state_census.md`.

**Concrete input that would have made it fail.** RG-0 fails to `indeterminate`
if the five quoted lines disagree in a way the committed record set does not
explain, or if a governing artifact cannot be read. Both branches are real
here:

* *Would have gone `indeterminate`:* if `git status --porcelain experiments/`
  had been non-empty, or if `git hash-object cost_model.py` had differed from
  `git rev-parse HEAD:...cost_model.py`. Then the corrected law would have been
  a worktree fact, not a committed one, and the census could not have named a
  verdict about committed state. The comparison was run and returned equality
  on all three of worktree, `HEAD` and `origin/main`
  (`a7ec7fd1ac4a48e7025fe8e7cfee0e46f6344b47`).
* *Would have gone `indeterminate`:* if `protocol_amendment.yaml` for
  `TASK-20260809-ef3e58` had been absent or untracked, since
  `DEC-20260809-c1066f` names it as the authority for a change to a frozen
  contract. `git ls-files | grep ef3e58` returns it, and it was read.
* *Would have gone `fix_outstanding`:* if `cost_model.py:239` had held
  `"T_full / sqrt(min(w, M))"`, or if the executable expression had read
  `log2Tfull - 0.5 * min(lw, log2M) + overhead_bits`. Neither does; the
  pre-fix revision `8c5188b90` does, which is how the branch was verified to be
  distinguishable.
* The unexplained-disagreement branch was exercised in substance: quotation (3)
  (`RUN-WESOVOW-001`) *does* disagree with the other four. It did not force
  `indeterminate` only because `CORR-20260806-3ac71e`, `TASK-20260809-ef3e58`
  and `DEC-20260809-c1066f` explain it and require it to stay that way.

---

## RG-1 — predecessor reproduction gate

**Verdict: `PASS`.**

All 120 `RUN-WESOVOW-001` vOW cells (5 field sizes × 6 budgets × 4 overhead
values) were recomputed from that run's own committed anchors
(`per_field[log2p=*].optimal.log2T`, `.log2M`) under the law that run
serializes, `L_pred`.

* `cells_expected: 120`, `cells_checked: 120`, `mismatch_count: 0`
* `max_abs_diff_bits: 0.0`, tolerance `1e-9`

The maximum deviation is exactly zero, not merely within tolerance: the
recomputation reproduces the committed doubles bit-for-bit.

**Concrete input that would have made it fail.** Feeding `L_curr` instead of
`L_pred` to the same gate against the same run. That input was actually run, as
`proves_too_much` object 3: it returns `status: FAIL` with
`mismatch_count: 120` and `max_abs_diff_bits: 134.34336795088666`. The gate
also fails on any absent budget row or cell (`ValueError`-free branches record
`reason: "missing budget row"` / `"missing cell"` and force `FAIL`), and on any
deviation above `1e-9`.

---

## RG-2 — successor reproduction gate

**Verdict: `PASS`.**

All 120 `RUN-WESOVOW-201692-001` vOW cells recomputed from that run's own
committed `per_field[*].optimal` anchors under the law it serializes, `L_curr`.

* `cells_expected: 120`, `cells_checked: 120`, `mismatch_count: 0`
* `max_abs_diff_bits: 0.0`, tolerance `1e-9`

Recorded as an observation: the successor run's `per_field[*].optimal.log2T`
and `.log2M` are **numerically identical** to the predecessor run's, for all
five field sizes (`anchor_reconciliation.json` →
`predecessor_and_successor_optimal_anchors_identical: true`). That is expected
— the fix changed the vOW charging step and the crossover, not the `B`
optimizer or the Dickman machinery — and it is what makes the `fitted_opt`
anchor well defined across both runs.

**Concrete input that would have made it fail.** Feeding `L_pred` to this gate
against the successor run: the constant `0.5*log2M` offset makes every one of
the 120 cells miss by 46.6 to 134.3 bits. Same missing-cell and tolerance
branches as RG-1.

---

## RG-3 — null-discrimination control

**Verdict: `PASS`.**

The control evaluates `L_pred` and `L_curr` at identical inputs and requires the
reconciliation procedure to *report a difference where one exists*, and — on a
deliberately non-discriminating object — to report *no* difference rather than
manufacture one.

* Real anchors: 240 rows (both anchors × full grid); `all_real_rows_discriminate:
  true`; `min_abs_separation_bits: 46.25`.
* Synthetic object `log2M = 0`: 30 rows;
  `synthetic_log2M_0_reports_no_difference: true` — both laws collapse to
  `log2T_full` and the procedure reports exactly that.

Because the separation is a constant `0.5*log2M` (see `law_equivalence.md`,
Result 4), the smallest real-anchor separation is 46.25 bits, which is 13.6
orders of magnitude above the `1e-12` discrimination threshold. The control is
therefore not near its threshold anywhere, which is a limitation as much as a
result: it says the procedure can see a large difference, not that it could see
a small one.

**Concrete input that would have made it fail.** Two, and both were run:

1. Any real-anchor cell with `|L_curr - L_pred| <= 1e-12` — a configuration in
   which the procedure would be blind to a difference that exists. Reached by
   setting `log2M = 0`, which is exactly the synthetic object; on it the real-
   anchor branch of the control would report `FAIL`.
2. The synthetic `log2M = 0` object being reported as *different* — the
   procedure manufacturing a difference that does not exist. Also checked, and
   it is not.

The control is discarded-and-reported rather than silently passed if either
branch trips; both branches are reachable and one of them was exercised on a
known-false object.

---

## RG-4 — cap and monotonicity control, per anchor

**Verdict: `PASS` for both anchors** — with the entailment disclosure below,
which qualifies what that pass means.

Run separately for `fitted_opt` and for `PAPER_PAIRS`; 20 cap rows and 20
monotonicity rows per anchor (5 fields × 4 `c`).

* `current_law_cap_identity_holds: true` — `L_curr` at `log2w = log2M` and at
  `log2w = log2M + 1` equals `log2T_full + overhead_bits` to within `1e-12`.
* `current_law_non_increasing_in_w: true` — over the sequence `log2w = 30, 40,
  50, 60, 70, 80, log2M, log2M+1`, `log2T(w)` never increases.
* `predecessor_law_violates_cap_everywhere: true` — `L_pred` at `log2w = log2M`
  misses `log2T_full + overhead_bits` at every one of the 20 rows per anchor.

### Entailment disclosure (required, and stated rather than glossed)

**The cap identity is algebraically built into the law being tested.** For
`log2T(w) = log2T_full + 0.5*max(0, log2M - log2w) + overhead_bits`, at
`log2w = log2M` the penalty term is `0.5*max(0, 0) = 0` by the definition of
`max`, for every anchor, every field size and every `c`. So the cap arm of RG-4
**cannot fail for `L_curr`** and its pass is a restatement of the law, **not
independent confirmation** of it.

This is the same caveat the `BATCH-eb0a7e` Validator recorded against that
batch's RG-2
(`coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/reviews/TASK-20260824-5b150a/validation_report.md:161-163`:
"the corrected identity is algebraically constructed … it does not
independently validate the provenance"). RG-4 here **repeats it**, and this
paragraph is the disclosure rather than a claim of a robustness result.
`DEC-20260824-384e78` preserves the same qualification.

What in RG-4 is *not* entailed by `L_curr`, and therefore does carry
information:

1. **The predecessor-law arm.** `L_pred` at `w = M` gives
   `log2T_full - 0.5*log2M + overhead_bits`; the control must, and does, flag a
   violation at all 40 rows. A control that reported `L_pred` as satisfying the
   cap would be broken, and this arm can detect that.
2. **Monotonicity across the memory grid.** Non-increase over the eight-point
   sequence is a property of the whole grid, not of the single cap point, and is
   not a tautology of the `max(0, ·)` clamp at one argument. It would fail if the
   penalty were, e.g., `0.5*max(0, log2w - log2M)`.
3. **The `log2w = log2M + 1` row**, which tests that the clamp is flat *above*
   the cap rather than only at it.

**Concrete input that would have made RG-4 fail.** Substituting `L_pred` for
`L_curr` in the cap arm: it returns a 46.6–134.3 bit deficit at every row and the
`corrected_cap_identity` flag goes false. Substituting a penalty of
`-0.5*max(0, log2M - log2w)` makes the monotonicity arm fail on every row.
Removing the `predecessor_law_violates_cap` requirement is what would turn RG-4
into a pure tautology; it is retained precisely so RG-4 is not one.

---

## proves-too-much set (three known-false objects)

**Verdict: `PASS`** — meaning the procedure **reported the negative outcome on
all three**. A `PASS` here is not a robustness result; a `FAIL` would have meant
the procedure proves too much and its agreements elsewhere carry no information.

| Object | Conclusion under test (KNOWN FALSE) | What the procedure reported |
| --- | --- | --- |
| `RUN-WESOVOW-001`'s serialized law | "satisfies the C4 cap requirement at `w = M`" | cap violation at all 5 fields; deficits −46.639, −68.744, −90.718, −101.654, −134.343 bits |
| synthetic anchor `log2M = 0` | "corrected and predecessor laws are distinguishable at the probe" | no discrimination at any of 6 budgets; both laws give `log2T_full` |
| predecessor run's committed vOW rows checked under `L_curr` | "these values agree with the corrected law" | disagreement on 120 of 120 cells; `max_abs_diff_bits = 134.34336795088666` |

---

## Operational observations (never mathematical evidence)

* **Run 1 of 4 failed with an implementation error and is recorded rather than
  discarded.** `reconcile.py`'s repository-root computation used six `..`
  segments instead of seven, producing
  `FileNotFoundError: .../coordination/experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json`.
  Classification: `implementation_error`. Fixed by correcting the path depth; no
  input, law, tolerance or control was changed.
* **Run 2 of 4** produced the full 240-row table and all five control verdicts
  as reported here.
* **Run 3 of 4** re-ran the identical computation after adding a
  `citation_prohibited` flag and note to the `log2p = 512` rows of the JSON
  (output-labelling only; no numeric, law, anchor or control change). All
  control verdicts and all deviations were unchanged.
* Budget: 3 of at most 4 runs used; wall clock far inside 5400 s (each run
  completes in under a second); memory far inside 2 GB (the script holds 240
  dictionaries and imports no numeric library).
* No timeout, crash, missing dependency, or resource exhaustion occurred beyond
  the implementation error above.

## Limitations of this control set

* Nothing here validates the *provenance* of `RUN-WESOVOW-201692-001` — that it
  was produced by the command its `command.txt` records, on the tree its
  manifest names. Both run manifests record `dirty_tree: true`
  (`RUN-WESOVOW-001/manifest.yaml:19`,
  `RUN-WESOVOW-201692-001/manifest.yaml:24`). RG-1 and RG-2 show internal
  arithmetic consistency of each run with the law it serializes; they do not
  re-execute `cost_model.py` and cannot.
* RG-1 and RG-2 check only the `van_oorschot_wiener` cells. The `optimal`
  anchors, the Dickman validation block, the `crossover` block and the byte
  conversions are read as inputs, not reproduced. Reproducing the `optimal`
  anchors would require re-running the `B` optimizer, which is an experiment
  execution this task is not authorized to perform.
* RG-3's discrimination margin is 46 bits or more everywhere; the control
  demonstrates sensitivity to a large difference only.
* The RG-4 cap arm for `L_curr` is entailed, as disclosed above.
