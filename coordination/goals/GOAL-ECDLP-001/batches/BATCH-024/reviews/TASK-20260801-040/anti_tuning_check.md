# ANTI-TUNING CHECK — ATS-DEP-1

TASK-20260801-040, reviewer duty 2. Verdict carried in `contract_review.yaml`.

**Result of this duty in isolation: PASS.** The calibration supplied numbers and
did not supply a choice. The REVISE verdict rests on the attainability and
alternative-class duties, not on this one.

---

## 1. ATS-DEP-1.1 — hash-binding before calibration, verified against Git

```
36141a951  2026-08-01  snapshot(TASK-20260801-034): hash-bind EXP-DEP-001 contract …
e60f4fbec  2026-08-01  snapshot(TASK-20260801-036): archive RUN-DEP-001-calib; bind DRIVER_SHA256
f75139918  2026-08-01  snapshot(TASK-20260801-039): freeze RR-DEP-1 and ATTAIN-RR-DEP-1 …
```

* `git merge-base --is-ancestor 36141a95 e60f4fbe` → **true**. The contract
  commit **is an ancestor** of the calibration commit, as ATS-DEP-1.1 requires.
* `git merge-base --is-ancestor e60f4fbe f7513991` → **true**.
* `git diff 36141a95 e60f4fbe -- experiments/EXP-DEP-001/specification.yaml` →
  **empty**. The contract did not move between freeze and calibration.
* `git ls-tree -r 36141a95 -- experiments/EXP-DEP-001/` returns exactly one path,
  `specification.yaml`. **No run artifact existed in the tree at the contract
  freeze.**
* Working tree equals the snapshot: sha256 of `reading_rule.yaml`,
  `specification.yaml` and `dep001_driver.py` each equal `git show f7513991:<path>`.
  Recomputed values —
  `360d4f1c6df56377825d2f06f7d26f3ffcb8627b8868ce223a184bffcaf12e32`,
  `e4a977f2117b190fef2baa95e2fbb7791d601b5a42c783b82d835222d9c9e20d`,
  `c83e9e9f4c04ba52a8f4b4768d6a4eeb4ee316e0f149a1d6c9a278d819aef3d8` — the last
  two equal to the values the contract and reading rule name.

**Observation, not a defect.** The driver did **not** exist at 36141a95; it
appears with the calibration at e60f4fbe. That is exactly what ATS-DEP-1.5 says
("hash-bound by the TASK-20260801-036 receipt"), so the clause is honoured as
written. The residual exposure — that the code implementing the plants was
authored after the contract froze — is bounded by the fact that all three
constructions are specified in prose in the 034 contract's `objects` block, and
this reviewer verified line by line that the code implements that prose. See
`alternative_class_check.md` §2.

---

## 2. Every quoted archived threshold, recomputed from its named raw array

Source: `experiments/EXP-EQD-001/results/calib/null_replicate_statistics.json`.
sha256 recomputed in this session:
`284ca32143b386beefe80bae5ae05419a2b2f9286c96e3450e09c33e0fdca019` — **matches**
the value the contract, the reading rule and the run manifest all name.

Each array at `cells.<bits>.replicate_values.<STAT>` asserted to have exactly 200
elements; **verified, all eight**. The 199th ascending order statistic
(`sorted(arr)[198]`) recomputed with this reviewer's own sort:

| cell | statistic | recomputed | frozen in RR-DEP-1 | equal |
|---|---|---|---|---|
| 16 | STAT-CHI-16 | 315.4755320010126 | 315.4755320010126 | ✔ |
| 16 | STAT-CHI-64 | 4345.885305765976 | 4345.885305765976 | ✔ |
| 16 | STAT-KS1-E1 | 0.006191903131115506 | 0.006191903131115506 | ✔ |
| 16 | STAT-KS1-E2 | 0.00623012475538165 | 0.00623012475538165 | ✔ |
| 20 | STAT-CHI-16 | 326.2209621328956 | 326.2209621328956 | ✔ |
| 20 | STAT-CHI-64 | 4293.229704961268 | 4293.229704961268 | ✔ |
| 20 | STAT-KS1-E1 | 0.006841670743639949 | 0.006841670743639949 | ✔ |
| 20 | STAT-KS1-E2 | 0.00631421232876711 | 0.00631421232876711 | ✔ |

**All eight equal to the last floating-point digit.** No threshold was retuned.

The eight **secondary** DEP-CAL-A order statistics were likewise recomputed from
`cells.<bits>.replicates[*].<STAT>` (200 elements each, verified) and all eight
match the frozen values exactly: 301.2903602941641, 4364.774920729396,
0.007124510763209357, 0.006948691291585152 at bits 16 and 306.11321542075933,
4299.122230073232, 0.00655883072407043, 0.006253057729941336 at bits 20.

The eight **THR-DEP-REPRO** counts were recounted by applying the
strictly-greater rule directly to the raw fresh replicate values against the
archived thresholds: **0, 2, 3, 2** (bits 16) and **0, 2, 1, 0** (bits 20),
matching both the archived `archived_threshold_exceedances` fields and the frozen
file. All eight lie inside the frozen band [0, 8]; **the band was copied, not
fitted** — it appears in the 034 contract before any datum.

Every DEP-CAL-C, D, E and F count was recounted the same way from the raw
replicate arrays in `raw-result.json`. All match: C = 2,1,5,2 / 1,6,0,2 of 200;
D = 20,20,3,0 / 20,20,0,0 of 20; E = 0,0,0,0 / 0,0,0,1 of 20; F = 2 of 200. Every
DIAG-DEP-RHO summary (means, ranges, both cells, both arms) recomputed and
matches. The four anchor threshold ratios recompute to 703.479, 56.831, 690.930,
57.705 against the file's "about 704 / 56.8 / 691 / 57.7".

---

## 3. Nothing added, dropped, moved or reordered after calibration

Machine comparison of the frozen contract against the reading rule, whitespace
normalised:

* **Branch conditions** — all six **identical**.
* **Branch dispositions** — all six **identical**.
* **Order** — D-0, D-1, D-5, D-2, D-3, D-4 in both; precedence string identical;
  machine field `branch_precedence: [D-0, D-1, D-5, 'exactly one of D-2, D-3, D-4']`.
* **`forbidden_in_every_branch`** — identical.
* **Ladders** — RHO (9 rungs), CELL (6), BLOCK (3) equal element by element.
* **Cuts** — rho\* = 0.05, eps\* = 0.02, equal.
* **Statistic family** — STAT-DEP-1's four members, equal; certifying set equal to
  CERT-DEP-1's three; `excluded_statistics: []`.
* **Detection bar** — 0.95 rate and 0.90 one-sided floor, both present and
  unmoved.

**No exclusion was taken, and none was available.** EXP-DEP-001 declares no
degenerate-statistic exclusion mechanism — no CAL-STOP-1 analogue, no
`second_stop_leg`, and `stopping_rules` / `invalidation_rules` govern run
cancellation and validity only. This reviewer confirms the absence directly.
STAT-KS1-E2's non-certifying status is CERT-DEP-1's, frozen at 034, so restating
it is a copy and not an exclusion. The reading rule's leg-3 reasoning is correct.

### The metrics block, checked against DDV-1..5 specifically

`DEP_detect_rate_rho` / `_cell` / `_block` map one-to-one onto DDV-1 / 2 / 3;
`DEP_rho_det` onto DDV-4 and `DEP_eps_det` onto DDV-5, with the same definitions
and the same certifying restriction. `DEP_detect_ci_two_sided`,
`DEP_detect_ci_lower_one_sided` and `DEP_detects_flag` restate DET-DEP-1's two
clauses. `DEP_reject_per_replicate` and `DEP_statistic_values` are raw records.
**No statistic, decision variable, threshold, ladder rung or branch is added.**

The only decimals anywhere in the block are `0.90` and `0.95` — DET-DEP-1's own
two constants, copied. The only multi-digit integers are 16, 20, 64, 95, 200 and
130816 — grid resolutions, a confidence level, a replicate count and the arm
size. The block's claim that no threshold number appears is true in its evident
sense (rejection thresholds), which is the sense that matters.

---

## 4. The DET-DEP-1 constant — recomputed, with a correction to the correction

The reading rule corrects the contract's prose figure 0.9145 to
**0.9166648489336275**, calls it "the exact one-sided 95 percent lower
Clopper-Pearson bound at 190 of 200", and says it was "confirmed three
independent ways … All three agree".

Recomputed here by 300-step bisection on an exact `mpmath` binomial tail at 60
digits:

```
exact root                = 0.916664848933628025523679399229...
correctly rounded double  = 0.916664848933628
scipy.stats.beta.ppf(0.05, 190, 11) = 0.916664848933628
file's value              = 0.9166648489336275     (4 ulps low, ≈5.0e-16)
tail at file's value      = 0.049999999999997389   (should be 0.05)
```

**So the corrected constant is itself very slightly wrong, and the three-way
confirmation is not reproducible as stated** — the scipy leg returns a different
double from the driver's value. The likely cause is the driver's 200-iteration
float bisection, whose recorded residual (2.08e-17) understates the true error.

**Materiality: none.** The constant is used only to establish that the bound
clears the 0.90 floor, a margin of 1.67e-2 against an error of 5e-16. This
reviewer independently confirms the operational equivalence the file derives:
DET-DEP-1 at R_REPS = 200 ⟺ count ≥ 190 of 200, because the first clause is
exactly count ≥ 190 and the one-sided bound is monotone in the count and clears
0.90 there. Recorded as **non-blocking defect RTN-040-1**.

Two-sided value recomputed as 0.9099724622986486, matching the file. The
statement that 0.9145 matches neither bound is correct.

**The 0.90 floor is present and unmoved** (`detection_bar_one_sided_lower_floor: 0.90`),
and the file's refusal to move it on account of a prose error is correct
ATS-DEP-1.4 discipline.

**On "0.9145 appears nowhere".** It appears three times, at lines 435, 446 and
447, all inside `det_dep_1_constant_correction` and all in the negating role. It
is nowhere applied or carried as a value. The file's own narrower claim, "It is
not copied forward anywhere in this file", is accurate; the TASK-20260801-039
commit message's absolute phrasing is not. Recorded as **RTN-040-2**, no defect
in the reading rule.

---

## 5. Structural checks on the calibration package

Read from `raw-result.json` and cross-read against driver source:

* `calibration_saw_real_object: false`; `real_object_touched: false` at both cells.
* `ladder_rungs_executed: []` at both cells.
* `duplicate_decomposition_emitted: false`.
* Source-level confirmation: `run_calibration` contains **no** reference to
  `LADDER_RHO`, `LADDER_CELL`, `LADDER_BLOCK`, `plant_cell`, `plant_block`,
  `dep_deterministic_factor_base`, `duplicate_decomposition` or
  `run_duplicate_decomposition`. The forbidden objects are absent
  **structurally**, not by instruction, as the contract claims.
* 880 arms per cell, `pairs_recorded_per_arm_distinct = [130816]`,
  `degenerate_draw_count = 0`, `CTRL_DEP_MARG_all_ok = true`,
  `marg_mismatch_locations = []`.
* `eqd_tree_unmodified: true`, both CTRL-DEP-EQDHASH hashes equal their contract
  values, `all_reproduced_exactly: true`.

**One qualification, and it is substantive.** The calibration executed no ladder
*loop*, but it did construct the *object* that is the rho = 1.00 rung: at
rho = 1.0 the copula reordering is bit-identically the comonotone anchor (see
`attainability_check.md` §3.1, verified by execution). So "no ladder rung appears
in the calibration package" holds at the level of labels and fails at the level
of objects. This is not a tuning event — the anchor's use is pre-declared under
ATS-DEP-1.6, and the top rung's outcome could not have influenced any frozen
choice because every choice was frozen at 034. But **the pre-disclosure is larger
than it was declared to be**, and the amendment recommended in
`contract_review.yaml` should say so.

---

## 6. ATS-DEP-1.6 — was the declared pre-disclosure honoured as written?

The declaration says the anchor is measured in the calibration stage, that its
outcome partially foreshadows the substantive result, that this is admissible
because the entire branch structure, cut, bar, ladders and statistic family are
hash-bound before any datum, and that the anchor is not a ladder rung, is read by
no substantive branch and certifies nothing.

* Hash-binding before any datum: **verified against Git** (§1).
* Read by no substantive branch: **verified** — no branch condition mentions
  DEP-CAL-D; it is used only in ATTAIN-RR-DEP-1, which is the declared use.
* Certifies nothing: **verified** — the certified class list and rung set are
  both empty and the file says so repeatedly.
* Not a ladder rung: **FAILS as an object-level claim** (§5). Honoured in spirit
  and in every operational respect; inaccurate as stated.

**Verdict on ATS-DEP-1.6: honoured, with the object-identity correction recorded.**

---

## 7. Did the calibration TUNE or SUPPLY?

**It supplied.** Every branch, cut, rung, bar and statistic pre-dates the
calibration in a commit that is a verified Git ancestor of it, with no run
artifact in the tree. Every number the reading rule adds traces to a named
archived array and reproduces exactly under independent recomputation. Nothing
was excluded, and no mechanism to exclude anything exists. The one place where
post-calibration latitude was available — OPEN-RR-DEP-1-A — is the one place the
freezing Coordinator explicitly declined to exercise it, in both directions, and
routed to this review instead. That is the correct handling and it is the reason
the underlying defect surfaced before the measurement budget was spent.

**ATS-DEP-1 held. This duty returns PASS.**

---

## 8. Note on independence

Author, executor, validator and reviewer all resolve to the same model under this
harness; `model_verified` is false everywhere. Independence here is **procedural
only**. Accordingly every number in this document was recomputed from raw arrays
rather than read from the artifact under review, every Git fact was obtained by
running Git, and the driver's loader and threshold guard were *executed* against
the frozen file (result: `reading_rule_states_thresholds: true`, `agrees: true`,
exactly 8 comparison rows, all `equal: true`, no `RuntimeError`) rather than
inspected. Nothing in this batch is admissible toward the AGENTS.md rule 13
three-model closure quorum.
