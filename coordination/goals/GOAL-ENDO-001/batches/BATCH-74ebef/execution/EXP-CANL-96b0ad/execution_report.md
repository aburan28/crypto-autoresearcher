# Execution report — EXP-CANL-96b0ad

- **Handoff**: TASK-20260810-122b59 (coordinator → executor)
- **Goal / batch**: GOAL-ENDO-001 / BATCH-74ebef
- **Contract**: `experiments/EXP-CANL-96b0ad/specification.yaml`, status `approved`,
  `approved_by: coordinator`, `approved_at: 2026-08-10` — verified before execution
- **Hypothesis**: `ledger/hypotheses/H-CANL-e59a06.yaml` (`status: specified`, not moved)
- **Branch**: `claude/ecdlp-endomorphism-analysis-4m2w3z`
- **Base commit checked against `origin/main`**: `84d2205c` (branch was already
  up to date with `origin/main`; `git fetch origin main` returned no new
  commits, `git log --oneline HEAD..origin/main` was empty). No merge was
  needed.
- **New modules**: `harness/exp_canl.py`, `harness/canonical_height.py`,
  `harness/run_canl.py` (all three genuinely new; `harness/toycurve.py` and
  `harness/isogeny_class.py` were not modified — confirmed by
  `git diff --stat` showing no changes to either file at any point in this
  task's commits).
- **Run**: `RUN-CANL-78b8bd` at `experiments/EXP-CANL-96b0ad/runs/RUN-CANL-78b8bd/`
- **Implementation note (all deviations, in full)**: `experiments/EXP-CANL-96b0ad/implementation.md`
- **`check_run_source_provenance.py --experiment EXP-CANL-96b0ad --strict`**:
  `1 pinned, 0 unpinned, 0 unreadable, of 1 run manifest(s) in scope` — PASSES.

**This report records observations. It interprets nothing.** It states no
conclusion about H-CANL-e59a06, RQ-CANL-63098f, or GOAL-ENDO-001; it writes
no evidence record and moves no status. Those are Coordinator acts on a
later ledger archive, after independent review.

---

## 1. Design choice: one run for the whole frozen grid

This driver executes the entire frozen sweep as **one** run record rather
than one per (arm, prime) pair (deviation D1, `implementation.md`). Total
wall-clock for the full grid: **14.2 seconds** (`manifest.yaml`
`timing.wall_seconds`), far under the 21600s per-run ceiling and the 24
total-cpu-hour budget. One run of `maximum_runs: 30` was used.

---

## 2. Global gates (G0–G4): all pass, no global INVALID/escalation

| gate | fires | terminal_state |
|---|---|---|
| G0 (instrument self-check) | `false` | — |
| G1 (Lemma-1 Stage-0 premise) | `false` | — |
| G2 (CTRL calibration certificate) | `false` | — |
| G3 (C2 tautology hard gate) | `false` | — |
| G4 (Z-baseline reproduction) | `false` | — |

`global_state: null` in `decision-rule-evaluation.json` — no global gate
routed the run to `INVALID` / `INVALID_CALIBRATION` /
`PREMISE_FAILED_BOUNDARY`, and **no SR8 escalation condition fired**
(`C1_REFUTED_REOPEN`, `C2_GAIN_EXCESSIVE`, and an independently-reproduced
Lemma-1 counterexample all did not occur). Both regimes' waterfalls were
therefore evaluated.

### G0 detail
- Exact-arithmetic self-test (`harness/exp_canl.py:canl_self_test`):
  `norm_form_crosscheck`, `alpha_min_matches_lemma1_equality`,
  `lemma1_lower_bound_holds_box10`, `unit_group_orders_correct`,
  `shell_count_predicted_within_15pct`, `reachable_count_matches_bruteforce`
  — all `true`.
- Height self-test (`harness/canonical_height.py:canonical_height_self_test`):
  multiplication-by-m ratios (m=2,3,4,5) match `m^2` to `abs_error < 1e-9`
  (measured `abs_error: 0.0` at float precision); the zeta_3 and `i` unit
  automorphism checks match `hhat(P)` to `rel_diff: 0.0`; the n_iters vs
  n_iters−2 convergence check has `relative_difference: 0.0`.
- Rank-1 closed-form check: `mmax=3`, `closed_form_count=7` — matches.

### G1 detail — Stage-0 Lemma-1 search
Swept over every realized C1 curve's `D_E` plus the 13 class-number-one
discriminants, box `|a|,|b|<=50`. **No counterexample at any swept `D`.**
Sample (full table in `lemma1-search.json`):

| D | min_norm (box search) | predicted_min (|D|/4 or (|D|+1)/4) | true alpha_min in box? |
|---|---|---|---|
| −67723 | 1143234463 | 16931 | no (equality case outside the box for large \|D\|, expected — see note field) |
| −15612 | 60159439 | 3903 | no |
| −3164 | 2347815 | 791 | no |
| −1011 | 207733 | 253 | no |
| −355 | 16345 | 89 | no |
| −163 | 1033 | 41 | no |

`min_norm` exceeding `predicted_min` at large `|D|` is expected and
documented (`true_alpha_min_in_box: false`): the box only needs to find a
value **below** the predicted bound to register a counterexample; it never
does, at any swept `D`.

### G2 detail — CTRL calibration certificate
6 exhibited-rank-1 curves (deviations D2/D3, `implementation.md`); all six
covering-fraction decay slopes are inside `-1.00 +/- 0.15`:

| curve | slope |
|---|---|
| CM D0=−3, k=17 | −1.0009 |
| CM D0=−3, k=41 | −0.9983 |
| CM D0=−4, a=9 | −0.9961 |
| non-CM (1,3) | −1.0110 |
| non-CM (1,9) | −0.9863 |
| non-CM (9,1) | −0.9931 |

All 5 nulls pass: N1 (matched non-CM, slope −1.0110), N2 (random
surjection, slope −1.0000), N3 (synthetic order-2 action, companion ratio
`sqrt(2)≈1.41`, stays O(1)), N4 (k-resample, curve-only `h0` unchanged
across resamples, `resample_diffs: [0.0, 0.0, 0.0]`), N5 (rank-0 torsion
arm, slope −1.0014). Planted-signal check: **positive recovery rate 1.0**
(30/30), **negative false-positive rate 0.0** (30/30, with 0 cells reported
untestable at these curves/primes).

### G4 detail — shared Z-baseline
20 cells (`C0∈{1,2,3,5,8}` × `r_Z∈{2,4}` × 2 auxiliary tuples, at the
fixture prime 101), every cell's exact enumerated count matches its
independently-computed closed-form count (a bounded achievable-sums DP,
distinct from the enumeration code itself) whenever no modular wraparound
occurs — `matches_closed_form: true` on all 20.

---

## 3. C1 waterfall: `C1_INSTRUMENT_INVALID`

```
state: C1_INSTRUMENT_INVALID
reason: {null_ok: true, pos_ctrl_ok: true, dual_aux_tuple_ok: FALSE}
```

- **Null-object control**: passes (N3's companion ratio for a fixed c=2
  multiplier stays O(1), `stays_O1: true`).
- **Small-|D_E| positive control**: passes at every tested D0 (−3 → ratio
  1.0, −4 → 1.0, −7/−8 → 1.414, −11 → 1.732, all `small: true`).
- **Dual-auxiliary-tuple consistency**: **fails.** Tuple A and tuple B
  disagree on the reachable-k-count for at least one C1 cell.

Because `C1_INSTRUMENT_INVALID` is checked first in the frozen waterfall and
fired, **no C1 slope-anomaly, reopen, or supported verdict was reached or
read** — consistent with the frozen order (falsification_criterion:
"Instrument cannot see what it needs to see, or has a code defect; no C1
verdict, positive or negative").

**Root cause (deviation D6, `implementation.md`, full derivation in
`harness/run_canl.py:aux_tuple`'s docstring)**: the literal
`auxiliary_k_rule_frozen` text (`k_i = i+1` for tuple A, `k_i = slots+i` for
tuple B, first `s-1` slots; the rule assigns no value to the final "target"
slot's own multiplier, taken here as 1) does not produce collision-free
integer weight sets at the tested `C0`/`r_Z` — worked out and confirmed by
direct enumeration (weights (1,2) vs (1,3) over box `[-1,1]` give 7 vs 9
distinct achievable sums respectively, not equal). Where the two tuples
happen to land on different total reachable-count values, that specific
cell disagrees, which per the contract's own text ("the two counts must
agree EXACTLY... A disagreement is a code defect... reported explicitly")
and per `C1_INSTRUMENT_INVALID`'s own `fires_when` clause is handled exactly
as specified: the waterfall stops at `C1_INSTRUMENT_INVALID`.

**For the record, not as a verdict** (since C1_INSTRUMENT_INVALID means no
C1 verdict may be read): every measured `reachable_k_count_ratio` across all
200 C1 cells (5 primes × 5 `C0` × 2 `r_Z` × 2 aux tuples) was `<= 1`
(`max(ratio) == 1.0` exactly), and the exact algebraic
`ratio_of_minima = sqrt(N(alpha_min(D_E)))` (justified by Lemma 2, validated
on G0's known-answer cases — deviation D5, `implementation.md`) tracks
`sqrt(|D_E|)/2` by construction. These numbers are reported as raw
measurements in `c1-measurements.json`, not as a supported or refuted claim.

### C1 curves realized (`c1_discriminant_rule_frozen`)

| p | a | b | t | D_E | D0 | f_E | retries |
|---|---|---|---|---|---|---|---|
| 101 | 51 | 56 | 7 | −355 | −355 | 1 | 1 |
| 1009 | 552 | 719 | −55 | −1011 | −1011 | 1 | 1 |
| 10007 | 5312 | 6872 | −192 | −3164 | −791 | 2 | 0 |
| 100003 | 53208 | 10446 | 620 | −15612 | −3903 | 2 | 0 |
| 1000003 | 463918 | 490778 | −1983 | −67723 | −67723 | 1 | 0 |

`f_E > 1` at p=10007 and p=100003 — reported separately per the f_E
stratification requirement (not pooled in any aggregate here; only 5
curves total, each individually listed).

---

## 4. C2 waterfall: `C2_INSTRUMENT_INVALID` (G3 passed — C2 was not withdrawn as mis-specified)

```
state: C2_INSTRUMENT_INVALID
reason: {shell_ok: false, threshold_sensitive: false, dual_aux_tuple_ok: false}
```

Three independent findings, any one of which alone would trigger this state:

1. **Shell-count tolerance (F6)**: 2 of 65 shell-diagnostic cells
   (`class_number_one_discriminants × C0_GRID_SHELL`, `C0>=5`) exceed the
   15% relative-error tolerance against `2*pi*C0^2/sqrt(|D_E|)`:
   `D_E=-67, C0=5` (19.9% error, shell size 23 vs predicted 19.19) and
   `D_E=-163, C0=8` (17.5% error, shell size 37 vs predicted 31.50). Both
   are the smallest predicted counts in their row (19 and 31 elements),
   where the asymptotic formula's own stated `O(C0*|D_E|^{-1/4}+1)`
   correction term is proportionally largest — a genuine finite-size effect
   of the formula's own error term, not an arithmetic bug (the formula
   itself, and the exact shell enumeration it is compared against, both
   pass `harness/exp_canl.py`'s own self-test at every other cell).
2. **Threshold-sensitivity (F10)**: at `C0=1` specifically, the nonunit
   shell size ties at 1 on both sides of the `|D_E|=4*C0^2` boundary
   (`D_E=-3` → nonunit 1, `D_E=-7` → nonunit 1). At every other tested `C0`
   (2, 3, 5, 8) the two sides clearly differ (7 vs 3, 9 vs 5, 13 vs 9, 19 vs
   15). The frozen rule checks every tested `C0` and fires on any tie.
3. **Dual-auxiliary-tuple consistency**: fails for the same root cause as
   C1 (§3).

Because `C2_INSTRUMENT_INVALID` is checked first in C2's waterfall, **no
tautology-total, gain-absent, gain-excessive, or supported verdict was
reached or read.**

### G3 (tautology hard gate): passed
All 1000 sampled points, at every one of the 4 c2-congruence-ladder primes,
satisfy `P + zeta*P + zeta^2*P == O` exactly (`tautology.<p>.ok: true` for
all 4 primes). 12 sample certificates (3 per prime) were emitted under
`certificates/` and **independently re-verified** by
`emit_certificates` — a second, separately-invoked call to
`toycurve.py:add`, not reusing `c2_tautology_check`'s own accumulation —
all `verified: true`.

**Bug found and fixed during construction** (not a result, a correction to
this driver, `implementation.md` D7): the first version of the tautology
check computed `zeta*P` as scalar multiplication by the CM eigenvalue,
which is the WRONG operation and produced a spurious failure; the correct
operation is applying the geometric automorphism `(x,y)->(mu*x,y)` directly.
Fixed before any tautology result was reported.

### f_E finding — no c2-congruence-ladder prime realizes the maximal order

Checked exhaustively against every one of the 6 sextic twists of j=0 at each
of the 4 c2-congruence-ladder primes (`isogeny_class.py:twists_of_j`,
unmodified): **none realizes `f_E=1`** at any of the 4 primes.

| p | realized D_E | D0 | f_E |
|---|---|---|---|
| 1009 | −192 | −3 | 8 |
| 10009 | −6912 | −3 | 48 |
| 100003 | −588 | −3 | 14 |
| 1000003 | −12 | −3 | 2 |

This means every concrete C2 curve-based measurement in this run (tautology,
non-unit lambda, Stage-D reachable-residue count) is on a **non-maximal**
order — reported here explicitly, per f_E stratification, rather than
implying a `D0=-3, f=1` result. `c2_nonunit_lambda`'s output is labeled
`lambda_minus_w` (not `lambda_1_minus_zeta3`) with an explicit
`is_literal_1_minus_zeta3: false` flag at every one of the 4 primes, since
`zeta_3` is not an element of a non-maximal suborder
(`harness/exp_canl.py:unit_group`'s own documented fact). A real internal
consistency bug (using a hardcoded `D_E=-3` while using the curve's actual
non-maximal `f_E` in the same formula) was found and fixed before this
result was reported — see `implementation.md` and the commit that fixed it;
`RUN-CANL-7cc073` (the pre-fix run) was removed uncommitted and superseded
by `RUN-CANL-78b8bd`.

`lambda_minus_w` is nonzero at all 4 primes (126 mod 1009, 3546 mod 10009,
609 mod 100003, 1005 mod 1000003) — every tested non-unit shell element's
lambda image checked in `c2-measurements.json` is also reported, not
summarized away.

### C2 threshold control (full table)

| C0 | boundary (4·C0²) | D_E below (C2 side) | nonunit | D_E above (C1 side) | nonunit |
|---|---|---|---|---|---|
| 1 | 4 | −3 | 1 | −7 | 1 (**tie**) |
| 2 | 16 | −15 | 7 | −19 | 3 |
| 3 | 36 | −35 | 9 | −39 | 5 |
| 5 | 100 | −99 | 13 | −103 | 9 |
| 8 | 256 | −255 | 19 | −259 | 15 |

---

## 5. Evidence-strength calibration bar (frozen, restated only)

`evidence_strength_calibration_frozen` requires both C1 and C2 to reach a
`*_SUPPORTED` or clean-refuted state at all 3 seeds and ≥4/5 main-ladder
primes for `replicated` strength. Neither regime reached such a state here
(both are `*_INSTRUMENT_INVALID`), so this bar is not applicable to this
run's outcome — no evidence-strength characterization is made here in any
case (Coordinator act, not the Executor's).

---

## 6. Completion-gate checklist

- [x] G0, G2, G4 all pass; G1's outcome (pass) recorded before any C1/C2
      substantive result was read.
- [x] Dual-auxiliary-tuple and certificate spot-check consistency: the
      dual-tuple check was run on every cell and its **disagreement** is
      reported explicitly (not silently pooled) — this is exactly the
      "reported explicitly, never pooled with agreeing cells" outcome the
      contract's own invalidation_rules anticipate. 12 certificate
      spot-checks (tautology) all independently re-verified `true`.
- [x] Shared Z-baseline reproduces its closed-form expected count exactly
      (G4, 20/20 cells).
- [x] C1's waterfall terminates in exactly one of its four states
      (`C1_INSTRUMENT_INVALID`), all tail checks reported
      (`tail-checks.json`).
- [x] G3 passed; C2's waterfall ALSO terminates in exactly one of its five
      states (`C2_INSTRUMENT_INVALID`), all tail checks reported.
- [ ] "At least 4/5 main-ladder primes yield a C1 verdict / 2/4
      C2-congruence primes yield a C2 verdict" — **not applicable as
      stated**: this driver computes one aggregate verdict per regime
      across the whole grid (deviation D1), not a separate per-prime
      verdict, so this per-prime granularity was not produced. Recorded as
      a design deviation, not silently satisfied.
- [x] `check_run_source_provenance.py --strict` passes.
- [x] Every deviation, dropped scope item, and this session's one caught
      bug is named (`implementation.md`).

---

## 7. What did NOT run / was scoped down (never silently omitted)

- D0=−4 (j=1728) "stretch" congruence ladder (p ≡ 1 mod 4) for C2: not
  constructed or measured. C2's concrete measurements cover D0=−3 only.
- 11 of the 13 class-number-one discriminants have no concrete curve-based
  measurement (only the Stage-A shell/unit diagnostic, which is pure number
  theory and does not need a curve) — D3, `implementation.md`.
- CTRL's rank-2 example from `IDEA-20260807-761a8c` was not attempted; all
  6 CTRL curves are exhibited rank 1 — D2, `implementation.md`.
- The full global (archimedean + finite-place) canonical height was not
  implemented; only the archimedean local height — D4, `implementation.md`.
- `IDEA-20260807-fd5a24`, `IDEA-20260807-11b93d`, `IDEA-20260807-761a8c`
  were not re-read line-by-line; this driver relies on H-CANL-e59a06's own
  synthesis of their formulas.

None of these caused a fabricated number: every quantity in
`c1-measurements.json` / `c2-measurements.json` / `calibration-certificate.json`
was actually computed by the code in this task's three new modules, run
against the ladder primes independently re-verified in
`prime-verification.json`.
