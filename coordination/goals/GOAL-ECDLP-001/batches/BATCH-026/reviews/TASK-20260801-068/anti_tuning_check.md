# TASK-20260801-068 — DUTY: ANTI-TUNING

RTB-068. The failure mode hunted here is the one the handoff names: **a repair
authored after an independent review that quietly improves its own position.**
Both the strikes and the regeneration make the favourable path easier, so this
is the direction that demands scrutiny.

## 1. Ancestry and immutability, verified against Git

| check | result |
|---|---|
| `ba1567ee` is an ancestor of `104d32fa` | **YES** |
| `104d32fa` is an ancestor of `aaf7672c` | **YES** |
| `aaf7672c` is an ancestor of `9515f6a1` (the TASK-20260801-067 commit) | **YES** |
| `1026150f` is an ancestor of `9515f6a1` | **YES** |
| `9515f6a1` is an ancestor of `HEAD` (`837c14e2b`) | **YES** |
| `specification.yaml` sha256 = `0d6c946fb84073feae47865da9b787b7d7ba459617834644680a06bf886d1cda` | **YES** |
| `reading_rule.yaml` BIT-IDENTICAL to `1026150f`, sha256 `8bcb196fa620503c736da307281325d17bb3dc8b0299407b24b584067c979f1d` | **YES — no edit. Not an evidence-integrity failure.** |
| `lpf001_driver.py` sha256 = `786aeb0550d75fa3d0785aefbe50b121a24cacae584a4cadd79902c464722d65` | **YES** |
| `9515f6a1` changed exactly two paths, 2235 insertions, 0 deletions | **YES** |
| `reading_rule_v2.yaml` at `9515f6a1` == worktree, sha256 `b633eaf1837ec876ffb7a52bdc6450baba8b1bb4d253dce3d8f3e6e13a7de328` | **YES** |

No rebase over pushed run records. No history rewrite. RR-LPF-1 was superseded,
not overwritten, exactly as AGENTS.md rule 4 requires.

## 2. Was the regeneration genuinely mechanical, or selective?

This is the central anti-tuning test, and I answered it by **re-running the
generating operation myself against the 210 archived flags** rather than reading
`raw_flag_sets_all_28`.

- 210 rows; my own recomputation of the criterion `|shift| >= 1` agrees with the
  archived flag column at **210/210**.
- All 28 raw flag sets regenerated from scratch, addressed by field and not by
  position: **28/28 match the published audit block exactly.**
- All 28 certification lists: **28/28 equal (raw set if certified, `[]` if
  STRUCK)**; all 28 statuses equal (`certified` iff the top-rung flag is true).
- **0 unsupported entries** in the certified lists.

**The decisive tell is the direction of the three corrections.** A selective
repairer corrects only what hurts. Two of the three corrections go **against**
the experiment (DIFF-1 removes ROUGH per-rung power at γ=0.005 bits 16, shift
−0.882122, flag false; DIFF-2 removes it at γ=0.01 bits 16, shift −0.937958, flag
false) and **one goes in its favour** (DIFF-3 adds SMOOTH γ=0.001 at bits 20,
shift +1.5724157930250209, flag true). DIFF-3 is the one a tuner would have
omitted — RTB-054-3 explicitly flagged it as "not a REVISE ground on its own"
and RR-LPF-1's error there erred *against* the experiment, so there was no
external pressure to fix it. **It was fixed.** A mechanical operation applied
only where it hurts would not be a mechanical operation, and the file says so
and then behaves accordingly.

## 3. Did only permitted numbers move?

Verified by whitespace-normalised machine comparison of every condition,
disposition, band, spread, cut, probability and ruling — full table in
`supersession_diff_check.md`. Summary:

- **No statistic added, dropped, moved or reordered.** Retained set, struck set,
  and the seven-id `statistic_ids(bits)` ordering are identical.
- **No rung added, dropped, moved or reordered.** Both γ ladders are
  `(0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05)`, identical to
  `specification.yaml` `LPF-LADDER-SMOOTH` / `LPF-LADDER-ROUGH`. Both Bsm ladders
  are identical to the driver's own `BSM_LADDER`.
- **No cut moved.** `identity_binomial_cut: 4`; the three-reading table is
  identical.
- **No band moved.** All 28 `bands` entries and all 28 `null_spread` entries are
  identical; `[0.125, 8.0]` is identical; every one of the 10
  `limb_b_decidability_map` rows is identical.
- **No branch moved.** All six conditions and dispositions are whitespace-
  normalised **identical to `specification.yaml`** and to RR-LPF-1, in the
  specification's own order `L-0, L-1, L-5, L-2, L-3, L-4`.
- **No probability moved.** 0.800995 / 0.817910 / 0.980100 / 0.818 /
  `[0.789, 0.980]` / L_3 ≈0.001 / L_4 ≈0.18 all identical.

## 4. Does the plant-Z package contain an OBJ-REAL sample?

Checked at the level of objects, not labels.

- `plant_z_regen.py` uses only `Stream/draw_seed`, `CalibrationCell.draw_uniform`,
  `Factorizer.factor`; its header states it imports nothing from the driver's
  section 8 (`deterministic_factor_base`, `int1_fibre_invariants`,
  `upper_triangle_indices`), no `run_measurement`. I grepped the file: the only
  draw call is `cell.draw_uniform(s_unif, k)` at line 202. **No call to
  `deterministic_factor_base` anywhere.**
- `runs/RUN-LPF-001-plantz/raw-result.json` records
  `LPF_real_object_touched: false` and `LPF_tripwire_asserted_false_at_exit: true`,
  status `completed_valid`.
- The report's anchor block shows the 20 base replicates reproduce **bit for
  bit** against the archived uniform series at both cells, i.e. the objects are
  the calibration's own uniform draws.

**No OBJ-REAL sample in the plant-Z package.**

## 5. Which way does the repair move the experiment's position?

I scored every substantive delta by whether it helps or hurts the experiment.

**Against the experiment (4):**
1. Two certified per-rung power entries removed (DIFF-1, DIFF-2).
2. V12 records those two rungs on the **uncertified** side, binding.
3. D1-v2 withdraws a universal impossibility claim, replacing "neither family
   CAN place mass in the deep tail" with a measured negligible rate, and
   **newly forbids** ever saying a family cannot.
4. LIMBB-DECL-RR066 part 2 states that LIMB B is **not** a symmetric 8× test and
   is a **1.75× test** at bits-16 u=5 — a direct reduction in the magnitude any
   reader may attribute to a LIMB B exit.

**In favour of the experiment (2):**
5. One certified per-rung entry added (DIFF-3), which the archive supports.
6. LIMBB-DECL-RR066 part 1 finds the sole non-decidable rung to be largely a
   definitional artifact.

Item 6 is the one that needed the hardest look, because it makes the apparatus
look better. It does **not** improve the file's position: the flag is expressly
**not** changed (`it_changes_no_disposition`), every map row is unchanged, the
`[0.125, 8.0]` band and the `u_star_formula` are unchanged, and the rung in
question is already the rung POW-LPF-1 excluded before any datum and whose LIMB A
statistic is struck, so no branch reads it either way. Moreover the same
declaration's part 2 is squarely unfavourable. **Net: the repair moves against
the experiment's position.**

The one thing the repair does protect is the ability to execute at all — L-1's
second leg staying FALSE. I did not take that on the file's word: I read all 17
certified ladders' γ=0.05 flags out of the archive and confirmed the leg is
FALSE (`attainability_check.md` §1).

## 6. The favourable-direction reading of the strikes, restated adversarially

A strike removes a statistic that would otherwise be able to fire L-1 and force a
non-execution. That is structurally the direction a tuner would push. Three
things stop the concern here, and each is a measurement rather than an argument:

1. **The strikes are pre-datum in form.** CERT-LPF-1 and PERTURB-MOVE-1 fixed
   before any datum that a member which does not move on any rung of either
   ladder is struck. The freeze applies the rule; it does not choose it.
2. **Both strikes rest on 0-of-28 measurements I recomputed.** STAT-TAIL-DEEP:
   0 of 28 flagged, max |shift| 0.3379820826156079. STAT-RATE-u@u=6: 0 of 28
   flagged, max |shift| 0.48091103648792977. Neither is close to the criterion.
3. **The struck statistics are barred in BOTH directions.** Under CERT-LPF-1 the
   non-firing of a struck statistic may never be reported as evidence about the
   intermediates, and under AP-4 neither may its firing be reported as power. A
   strike that only removed inconvenient evidence would not carry the second
   half; this one does.

I also checked the inverse tuning risk — that a statistic capable of moving was
struck to reduce the number of comparisons. It was not: the two struck ids are
the only two of seven with **zero** flagged rows in 28, and all five retained ids
move at the top rung at **both** cells.

## 7. The one anti-tuning-adjacent finding I record

`change_register.what_is_not_a_fifth_change` exists so the cap "can be audited
mechanically rather than by argument", and enumerates four classes of permitted
addition. It is **incomplete**: it does not cover V12 / the AP-3 renumber, the
RTB-054 routing→ruled status transitions, the appended RTB-054 annotations, or
the `provenance` clarification. In practice each of those is separately justified
in an ad-hoc field elsewhere in the file, so nothing is concealed — but a
register that does not enumerate the file's own additions cannot be audited
mechanically, which is what it is for. Recorded as **DEF-068-A**, non-blocking,
with the repair owed being a complete register in any future superseding record.

## 8. Duty verdict

**PASS.** Ancestry clean; RR-LPF-1, the specification and the driver unmodified
and hash-confirmed; the regeneration reproduces at 28/28 from the archive and
corrects in both directions including the direction nobody demanded; only
permitted numbers moved; no OBJ-REAL sample in the plant-Z package; and the net
direction of the repair is **against** the experiment's own position.
