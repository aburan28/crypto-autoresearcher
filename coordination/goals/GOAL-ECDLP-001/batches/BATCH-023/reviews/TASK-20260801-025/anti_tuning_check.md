# ANTI-TUNING CHECK — ATS-1 CLAUSE 6

Duty (3) of TASK-20260801-025. Named deliverable. Reviewer role served by the
red-team subagent. Independence is PROCEDURAL, not model-level (see
`attainability_check.md` header); not admissible toward the AGENTS.md rule 13
quorum.

The question ATS-1 clause 6 charges me with is not "are the numbers right" —
that is duty (2). It is: **did the calibration TUNE the experiment toward a
desired outcome on the real object?**

## VERDICT ON THIS DUTY: PASS. THE CALIBRATION SUPPLIED NUMBERS; IT DID NOT TUNE.

The STAT-KS1-E2 exclusion is a **legitimate pre-declared exclusion that removes
a variable**, not a post-calibration choice that loosens the test. My reasoning
is in §3 and I did not take it on the Coordinator's word — I re-derived it from
the frozen spec text and the frozen driver source. One correction to how the
exclusion is described is recorded at §3.5, and one material coverage objection
with a binding condition is at §3.6.

---

## 1. Clause 1 — the rule precedes the measurement. VERIFIED AGAINST GIT.

```
7792331bc  snapshot(TASK-20260801-020): hash-bind EXP-EQD-001 contract  [SPEC FREEZE]
e9e601bd8  control-plane: bind 7792331b; calibration executor ready
53e202dd2  snapshot(TASK-20260801-022): archive RUN-EQD-001-calib       [CALIBRATION]
c52cd37f3  control-plane: bind 53e202dd; validator ready
2918680a7  snapshot(TASK-20260801-024): freeze RR-EQD-1 reading rule    [FREEZE]
a50e24ebc  control-plane: bind 024; reviewer 025 ready                  [HEAD]
```

- `git merge-base --is-ancestor 7792331bc 53e202dd2` → **true**. The spec freeze
  is an ancestor of the calibration commit.
- `git merge-base --is-ancestor 53e202dd2 2918680a7` → **true**.
- The tree at 7792331bc under `experiments/EXP-EQD-001/` contains **exactly one
  file**, `specification.yaml`. **No run artifact of any kind**, no driver, no
  results directory. Verified with `git ls-tree -r --name-only`.
- That tree's specification carries THR-EQD-1 (line 582), CERT-EQD-1 (618),
  CAL-STOP-1 (632) and ATS-1 (655) **in full** — including
  `one_sided_statistics` (the 199th-order-statistic rule with its strict-greater
  comparison and its 0.00995 exact level), `two_sided_statistic` (the
  [3rd, 398th] of 400 band), the CERT-EQD-1 ladder, bar, both-cells requirement
  and tie-break, both CAL-STOP-1 legs, and all six ATS-1 clauses.
- `experiments/EXP-EQD-001/specification.yaml` is **byte-identical** at
  7792331bc and at HEAD: `git diff` between them is empty and the sha256 is
  `295d85c748cf9d1d14e2746d3067fbbbc0a7fc9ebd8b62ccbdbe021a6dc99431` at both.
  The contract was not edited after the calibration ran.

**Independent corroboration not relied on by the file:** the calibration run
manifest records `run.code.commit: e9e601bd82eab31eb9fd083f31cfd62a772beb80`,
which is the child of 7792331bc. The run itself testifies that it executed
against a tree in which the threshold rule was already frozen. It also records
`specification_sha256: 295d85c7…`, the same value.

The manifest records `dirty: true` — the calibration executed on a working tree
that was not clean, which is expected since the snapshot commit follows the
run, and it is recorded rather than hidden. The binding that matters is the
declared-path digest match at the 53e202dd receipt, not the dirty flag.

Clause 1: **satisfied**.

## 2. Clause 2 — the null arm never sees the real data. VERIFIED.

- A recursive case-insensitive grep for `OBJ-REAL`, `deterministic_factor_base`
  and `factor_base_sha256` across `experiments/EXP-EQD-001/results/calib/` and
  `experiments/EXP-EQD-001/runs/RUN-EQD-001-calib/` returns **nothing**.
- The archived representative draw is labelled `"object": "OBJ-NULL-RFB"` with
  the note "representative NULL draw archived for reproducibility; it is not
  real data", and its `x_list` is a random draw, not the sorted prefix a
  deterministic base would be. I checked: the bits-16 list begins
  9660, 27302, 33671, 17634 — not increasing, so not the deterministic policy.
- The driver carries a module-level tripwire `_REAL_DATA_TOUCHED` and
  `main()` raises `RuntimeError("ATS-1 CLAUSE 2 VIOLATION …")` before emitting
  results if it is set. Both cells record
  `ats1_clause_2_real_data_touched: false`.
- No statistic in the package is computed from a real sample: CAL-1 compares
  two OBJ-NULL-RFB arms, CAL-2 an OBJ-PLANT arm against an OBJ-NULL-RFB arm,
  CAL-3 an OBJ-NULL-IND arm against an OBJ-NULL-RFB arm, CAL-4 measures curve
  facts and one OBJ-NULL-UNIF2 support fraction.

Clause 2: **satisfied**.

## 3. Clause 4 — substitution only. THE CRUX.

### 3.1 Every substituted number is the number the calibration measured

Recomputed by me as code from the raw archived arrays, not from the archived
summaries and not from the Validator's report. All six one-sided thresholds and
both dup bands match EXACTLY; all 40 CAL-2 detection-rate cells (four
statistics × five deltas × two cells) match EXACTLY when recomputed with my own
199th order statistics; `n_replaced = 6541 = int(round(0.05 × 130816))`
confirmed on every delta-0.05 row; every quoted mean-shift figure reproduced to
two decimals. Full tables in `attainability_check.md` §§1–2 and §5.

### 3.2 No selection among alternatives where only substitution was permitted

Four places where a selection could have hidden, checked one by one:

1. **The certified delta.** CERT-EQD-1 is a predicate, not a choice: smallest
   delta on the frozen ladder with detection ≥ 0.95 at BOTH cells for at least
   one of the two admitted chi-squares. I evaluated it myself and got
   delta 0.05 / STAT-CHI-16. The tie-break did not arise. No latitude used.
2. **STAT-KS1-E1 at delta 0.02.** It reaches 20/20 at both cells at a delta two
   rungs lower than the certified one. Acting on it would have produced a
   better-sounding certified delta. **The Coordinator declined**, recorded the
   fact, and named the reason correctly: CERT-EQD-1, frozen at TASK-019, admits
   only the two chi-squares as certifiers, and acting on it "would be selection
   where the contract permits only substitution." **This is the strongest single
   piece of evidence in the package that the freeze bound its author against
   convenience**, because the available latitude ran in the flattering
   direction and was not taken.
3. **STAT-CHI-64.** Low power and a non-monotone bits-16 detection sequence
   supplied a ready-made pretext to drop it, which would have removed two more
   tests and pushed family-wise attainability from 0.9418 to 0.9604 — again in
   the flattering direction. It was **retained**, and I confirm none of the
   three second_stop_leg grounds is met (non-zero null variance, not
   identically zero, largest-delta plant exceeds 20/20 at both cells), so
   retention was the only permitted answer and the file gives the right one,
   with the low-power limitation declared and bound.
4. **STAT-DUP.** Not excluded. The stated reason is textual as well as
   structural — CAL-STOP-1 second_stop_leg is written over "the four two-sample
   statistics" and STAT-DUP is a one-arm statistic, so the pre-declared
   exclusion mechanism does not reach it, and "inventing a reach for it would be
   exactly the post-calibration latitude ATS-1 clause 4 forbids." I checked the
   frozen text at 7792331bc: the leg does read "any of the four two-sample
   statistics". The reading is correct, and STAT-DUP is the variable whose
   exclusion would have been most convenient (it is the one that is degenerate
   at bits 20 and whose declared level is not attained at either cell).
   **The Coordinator declined the convenient reading here too.**

Three of the four available latitudes ran toward a more favourable or tidier
package and none was taken. That pattern is itself evidence about the process.

### 3.3 The one substantive judgement — STAT-KS1-E2. RULING: SUBSTITUTION.

I did not accept the Coordinator's deductive argument as stated. I checked it.

**The plant construction really does leave e_2 untouched, and it did so in the
tree that predates the calibration.** `specification.yaml` at 7792331bc,
`objects` / `OBJ-PLANT-delta` (lines 345–350): "An OBJ-NULL-RFB draw in which a
declared fraction delta of the 130816 pairs has its e_1 coordinate REPLACED by
a uniform draw from [0, floor(p/2)) and **its e_2 coordinate left unchanged**".
The driver's implementation matches:

```python
out1 = e1.copy()
out1[idx] = rng.integers(0, self.p // 2, size=n_replace).astype(np.int64)
return out1, e2.copy(), n_replace
```

**The deduction, which I performed rather than read.** STAT-KS1-E2 is the
two-sample KS on the e_2 marginal between the plant arm and a fresh independent
OBJ-NULL-RFB draw. The plant arm's e_2 *is* its base OBJ-NULL-RFB draw's e_2,
unmodified. So the pair (plant-arm e_2, comparison-arm e_2) is exactly a pair of
e_2 marginals from two independent OBJ-NULL-RFB draws — which is precisely the
CAL-1 null comparison. Its law is therefore **identically the null law, at
every delta on the ladder, at both cells**. Its reported "detection rates" ARE
its false-rejection rates. **Not one calibration number is load-bearing for this
conclusion**; it follows from the frozen contract alone and was fully derivable
at TASK-20260801-019.

That is my discriminant for tuning, and it is decisive: a decision that no
datum informs cannot be a decision tuned by data. The calibration confirmed the
deduction rather than producing it — 4 exceedances in 100 comparisons at bits 16
against 0.995 expected at the 0.00995 per-test level, 0 in 100 at bits 20; the
plant-arm mean shift never exceeds 0.66 null sd; and the SIGN of the shift is
not monotone in delta (recomputed: +0.03, +0.16, −0.25, +0.58, +0.06 at bits 16;
−0.66, +0.11, +0.02, +0.05, −0.50 at bits 20).

**Inventor-protocol §3 applied.** I asked what the reported quantity should have
done as the parameter meant to destroy it (delta) increases. For a statistic
with power, the shift should grow monotonically with delta — STAT-CHI-16 does,
+0.03 → +1.06 → +6.22 → +27.11 at bits 16, and STAT-KS1-E1 does. STAT-KS1-E2
does not grow and does not even keep its sign. **That is the canonical
artifact/degeneracy tell, and here it is correctly read as a controlled null
rather than as a finding.** It is the BATCH-021 degeneracy class — a variable
whose value does not depend on the thing it is supposed to measure — arriving
through a different door, and the pre-declared mechanism exists to remove
exactly that.

### 3.4 The exclusion removes a variable and adds none. VERIFIED.

I diffed the branch structure of the reading rule against the frozen contract's
form. The branch set, the precedence order N-0 > N-5 > N-1 > {N-2, N-4, N-6},
the statistic forms, K ∈ {16, 64}, the replicate counts (200 CAL-1, 20 CAL-2),
the quantile (199th of 200; 3rd and 398th of 400), the plant construction and
the delta ladder are all unchanged. Exactly one decision variable is removed.
**No variable, no branch, no rung, no threshold and no statistic is added
anywhere in the file.** The N-5 leg (c) margins are not an addition: the
contract requires the reading rule to declare them, and both endpoints are
named order statistics of a named CAL-1 array (the 1st and 200th of the
STAT-CHI-16 array), which I verified equal the array min and max.

### 3.5 A correction: the word "cannot" was interpreted, not applied

I will not let this pass unsaid, because it is the load-bearing word.
**Neither reading of "a threshold that the CAL-2 plant at the largest delta
cannot exceed" is literal.** Under the construction reading the plant *can*
exceed the threshold and did — 1 of 20 at delta 0.10 at bits 16 — so "cannot
exceed" is false as written. What is true is "has no power to exceed it more
often than a correct null does." The Coordinator took a **purposive** reading,
and it should have said so in those words rather than presenting the
construction reading as a plain reading.

I nonetheless judge the purposive reading **correct**, for three reasons the
Coordinator gives or that follow from its disclosure:

1. The leg's own stated purpose governs the ambiguity: exclusion is permitted
   "ONLY toward removing a variable that cannot discriminate." A statistic whose
   law is exactly the null law under every alternative on the frozen ladder is
   the paradigm case of a variable that cannot discriminate.
2. The sampling reading is not a property of the statistic and yields a
   **per-cell** answer (exclude at bits 20, retain at bits 16) that the branch
   structure cannot express. Choosing which cell to follow would itself be a
   post-calibration choice, and a worse one, because it *would* be data-driven.
3. The Coordinator disclosed the ambiguity, named both readings, named which it
   took, and named the direction of the resulting bias **first and loudest**
   rather than burying it. Disclosure is what makes the choice auditable, and it
   is why I could adjudicate it at all. Undisclosed, this would have been the
   defect of the batch.

**On the direction of the bias.** The exclusion moves family-wise attainability
from 0.9231 (not 0.9234 — see `attainability_check.md` §9, defect A-1) to
0.9418 and the misread probability from 0.0769 to 0.0582, a shift of 1.87
points, not 1.84, in the direction a Coordinator would be tempted to want. The
file states this plainly and states it first. The bias is real; what makes it
admissible is not that it is small but that **no datum determined it**, which I
verified independently in §3.3. The alternative — retaining two tests whose
power against the declared alternative class is zero by construction and whose
rejections would be pure false alarms at 0.00995 each — buys apparent
stringency with no detection capability, which is not conservatism but noise.

### 3.6 What the exclusion costs, and the condition it forces (RT025-O3)

The strongest objection available against the exclusion is not about tuning, and
I record it as the material one: **the alternative class on the ladder is a
proxy, not the object.** STAT-KS1-E2 has provably zero power against the *plant*,
but the real arm tests OBJ-REAL, whose deviation from the matched null — if any
— is not the plant. A deterministic-factor-base deviation that moved the e_2
marginal while leaving the K = 16 and K = 64 grid counts near null would now be
missed. The exclusion removes the only dedicated test of the e_2 marginal from
the branch condition, and the calibration certifies nothing about such an
alternative in either direction because none is on the ladder.

Two things bound this, one of which the file does not claim and which I
establish here:

- The file **discloses the cost accurately**, at
  `what_the_exclusion_costs_in_coverage` and `what_is_NOT_claimed`, and forces
  it into the N-2 disposition via
  `additional_scope_note_forced_by_the_exclusion`: "A NON-REJECTION HERE IS
  SILENT ABOUT THE e_2 MARGINAL BEYOND WHAT THE TWO GRID CHI-SQUARES SEE …
  Any deliverable reading N-2 must say so." That is the right binding.
- **The value is not lost, only the branch role is.** I read the driver:
  `flat_two_sample_values()` returns all four two-sample statistics and
  `run_real_arm` records the whole dict as `EQD_statistics`. The real-arm
  STAT-KS1-E2 value WILL be recorded, and its calibrated 199th-order-statistic
  thresholds exist in the archive (0.00623012475538165 at bits 16,
  0.00631421232876711 at bits 20). The e_2 information survives as a descriptive
  record.

That second point creates its own hazard, and it forces a condition:
**the recorded STAT-KS1-E2 value may be reported descriptively but may NEVER be
converted into a rejection after the real value is seen.** Doing so would be
precisely the post-hoc latitude ATS-1 clause 4 forbids, and it would be worse
than the exclusion because it would be data-driven. This is condition C-1 in
`contract_review.yaml`.

## 4. Clause 5 — the driver is frozen by the calibration snapshot

`shasum -a 256` of `experiments/EXP-EQD-001/implementation/eqd001_driver.py` at
HEAD is `bdb2601b195f314a4430fa80fcf8ab15ec0b605335a8386a93c2b9b3c7d7b02f`,
equal to the value recorded in the calibration manifest's
`code.driver_sha256` and to the value N-0 binds in the reading rule. The driver
was not edited between the calibration and the freeze. The reading rule
correctly declines to edit the driver to repair D-3 and D-4, and instead
absorbs the whole D-4 constraint into its own key typing — which I verified
works by executing the driver's own loader (§6 of `attainability_check.md`).

I confirm the file's honest handling of D-3: the `--mode real` gate checks only
that some readable JSON carries `APPROVAL_DETERMINATION: APPROVED` and that a
YAML with five fields exists; it binds no task id, commit or digest. The file
states "THE GATE IS AN ACCIDENT GUARD AND MUST NOT BE DESCRIBED DOWNSTREAM AS
AN AUTHORIZATION CONTROL." That is the correct characterisation and it binds.

## 5. Clause 3 — the calibration is non-evidential

Carried correctly and repeatedly: `no_hypothesis_disposition`,
`not_evidence`, `this_file_authorizes_nothing`, and the disclaimers at the head
of every archived JSON. Every number in the reading rule is labelled an
instrument constant. `the_owed_measurement_is_still_owed` keeps OPEN-BATCH023-A
alive and states that no outcome of this experiment discharges it.
`dominated_by` is "Not applicable and NOT set to null" with a reason — an
instrument calibration record states no mechanism, cost or frontier position.
That is the correct handling under the inventor protocol §5; an unchecked
`null` would have been a fabrication under AGENTS.md rule 5.

## 6. Summary of the anti-tuning duty

| ATS-1 clause | status | how checked |
|---|---|---|
| 1, rule precedes measurement | SATISFIED | git ancestry, tree listing, byte-identical spec, run manifest commit |
| 2, null arm never sees real data | SATISFIED | grep of the whole package, tripwire flag false, representative draw inspected |
| 3, calibration non-evidential | SATISFIED | textual, and no branch cites a calibration number as a result |
| 4, substitution only | SATISFIED | all numbers recomputed; four latitude sites audited; the one exclusion re-derived from frozen artifacts |
| 5, driver frozen | SATISFIED | sha256 recomputed and matched against the manifest |
| 6, reviewer duty | DISCHARGED HERE | this file |

**The calibration supplied numbers. It did not tune the experiment.** The one
substantive judgement the freeze made is a legitimate pre-declared exclusion of
a variable that cannot discriminate against the frozen alternative class,
derivable from artifacts that predate the calibration, disclosed with its
direction of bias stated first, and it adds nothing. It is substitution, not a
choice dressed as substitution.
