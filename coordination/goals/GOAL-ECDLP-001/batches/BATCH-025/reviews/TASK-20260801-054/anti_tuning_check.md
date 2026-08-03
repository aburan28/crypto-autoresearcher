# DUTY 2 — ANTI-TUNING (ATS-LPF-1)

TASK-20260801-054. Reviewer role served by red-team. Independence **procedural, not
model-level**. Everything below was verified against Git or recomputed from the
named arrays in this session.

---

## 0. Verdict on this duty

**The mechanical anti-tuning checks all pass.** The threshold *rule* was hash-bound
before any calibration datum existed, only measured numbers were substituted, and
**no branch, statistic, rung, cut or band was added, removed, moved or reordered**.

**The strikes are a pre-declared mechanism the contract actually provides, not a
post-calibration choice** — but they are also the one place latitude existed, they do
make the favourable path easier, and §5 below scrutinises them on exactly that
ground. Two findings come out of that scrutiny: the strikes themselves are sound,
and the **per-rung** certifications attached to them are not (RTB-054-1).

---

## 1. ATS-LPF-1 clause 1 — ancestry and no run artifact at the contract freeze

Verified against Git, not from prose:

```
git merge-base --is-ancestor ba1567ee 104d32fa   → YES
git merge-base --is-ancestor 104d32fa 1026150f   → YES
```

The contract commit is an ancestor of the calibration commit, which is an ancestor of
the reading-rule freeze.

```
git ls-tree -r --name-only ba1567ee -- experiments/EXP-LPF-001
  experiments/EXP-LPF-001/specification.yaml          ← THE ONLY ENTRY
```

**At the contract commit the experiment directory contained the specification and
nothing else** — no run artifact, no results, and not even the driver. The threshold
rule THR-LPF-1, the order-statistic ranks, the `[1/8, 8]` band, both ladders, both
`Bsm` ladders, the statistic family, the certifying set, DET-LPF-1 and the whole
branch structure were fixed in a file whose hash predates every number.

Specification integrity across the whole window:

```
sha256(ba1567ee:specification.yaml) = 0d6c946f…86d1cda
sha256(working tree specification.yaml) = 0d6c946f…86d1cda   ← IDENTICAL
```

matching the `source_binding.specification_sha256` in RR-LPF-1. **The contract has
not been touched since it was frozen.** ✅ Clause 1 satisfied.

---

## 2. ATS-LPF-1 clause 3 — DRIVER_SHA256 binds one file across both stages

```
sha256(104d32fa:implementation/lpf001_driver.py) = 786aeb05…4722d65
sha256(working tree implementation/lpf001_driver.py) = 786aeb05…4722d65
RR-LPF-1 source_binding.driver_sha256                = 786aeb05…4722d65
RUN-LPF-001-calib manifest.yaml driver_sha256        = 786aeb05…4722d65
```

**One identical file across the calibration snapshot, the manifest, the reading rule
and the tree the measurement would run from.** ✅ Clause 3 satisfied on the
calibration side; the measurement-side equality is TASK-20260801-058's duty and is
not yet checkable.

---

## 3. ATS-LPF-1 clause 5 — structural blindness to the real object, at the level of objects

Checked at the object level and not by label, per the clause's own instruction (which
exists because RTB-040-1 found a calibration that truthfully recorded
`ladder_rungs_executed: []` while bit-identically constructing the top-rung object).

**Call-graph fact from source:** `deterministic_factor_base` — the function whose
docstring states "CALLING THIS FUNCTION IS SEEING THE REAL DATA" and which is the
sole writer of the module-level tripwire `_REAL_OBJECT_TOUCHED` — is called at
**exactly two sites**, driver lines **1623** (`run_measurement`) and **2085**
(`_independent_pmax_recheck`, reached only from the measurement path).
`run_calibration` spans lines 1063–1478 and calls it at neither. The tripwire is
asserted still false at line 1433, inside `run_calibration`, before the results are
written.

**Object-level fact, which is the one that matters here.** Every object the
calibration constructs is derived from `Stream`-seeded `rng.integers` draws on
`[1, p²]` or on `[0, p) × [0, p)`:

- `draw_uniform` → uniform integers on `[1, p²]`;
- `draw_synth` → `ENC-B(e₁, e₂)`, a bijection onto `[1, p²]` from uniform `(e₁, e₂)`;
- `draw_product_control` → `max(e₁,1) · max(e₂,1)` on uniform `(e₁, e₂)`;
- `apply_plant` → replacement of a γ-fraction of a `draw_uniform` base by
  `build_smooth_replacement` / `build_rough_replacement` outputs.

**None of these reads an x-coordinate of `E(F_p)`, evaluates `S₃`, or specializes
`f_ij(Z)`.** The Semaev machinery (`int1_fibre_invariants`,
`upper_triangle_indices` over the deterministic factor base) is not reachable from
`run_calibration`. I regenerated the plant bases and the plants themselves in this
session using only `MASTER_SEED`, `STREAM_OFFSETS` and `bits`, and reproduced the
archived null statistics exactly — which is direct positive evidence that the
calibration objects are functions of the seed alone and carry no real-object
information.

`LPF_real_object_touched = false` in `raw-result.json`. ✅ Clause 5 satisfied
structurally.

---

## 4. ATS-LPF-1 clause 2 — substitution only. Nothing added, dropped, moved or reordered

### 4.1 Branch structure — whitespace-normalised comparison, machine-checked

Parsed both YAML files and compared `' '.join(str(s).split())` of every branch
`condition` and `disposition` against `specification.yaml`'s `branch_structure`:

| | specification | reading rule | match |
|---|---|---|---|
| branch ids, in order | L-0, L-1, L-5, L-2, L-3, L-4 | L-0, L-1, L-5, L-2, L-3, L-4 | ✅ |
| precedence string | "L-0, then L-1, then L-5, then EXACTLY ONE of L-2, L-3, L-4." | identical | ✅ |
| L-0 condition / disposition | — | — | ✅ / ✅ |
| L-1 condition / disposition | — | — | ✅ / ✅ |
| L-5 condition / disposition | — | — | ✅ / ✅ |
| L-2 condition / disposition | — | — | ✅ / ✅ |
| L-3 condition / disposition | — | — | ✅ / ✅ |
| L-4 condition / disposition | — | — | ✅ / ✅ |

**Twelve of twelve strings byte-identical after whitespace normalisation. No branch
was added, removed, merged, reordered or reworded.** ✅

Note in the freeze's favour: L-2's disposition still says "THESE THREE STATISTICS"
even though only two families are now read. **The freeze did not edit it**, and
instead recorded the wording consequence and routed it. That is the correct
behaviour under clause 2 and it is the kind of thing a tuning-minded freeze would
have quietly fixed.

### 4.2 Bands and spreads — recomputed from the named arrays

All **28** band edges (7 statistics × 2 cells × 2 edges) equal
`sorted(LPF_null_replicate_values[sid])[1]` and `[198]` **exactly**, and all **28**
`null_spread` entries (count, min, max, median, mean, sd with `ddof = 1`) match
**exactly**. Ranks are `lower_rank_ascending = 2`, `upper_rank_ascending = 199`
throughout, as THR-LPF-1 fixes. ✅

### 4.3 Cuts, ladders, statistic family — unchanged

- `identity_binomial_cut = 4`, an integer cut computed from `4/201` and a comparison
  count; all three candidate cuts recomputed (§ attainability_check §3(ii)) and each
  is the unique smallest admissible integer for its `n`. **The cut is derived from
  the order-statistic ranks alone and from no datum.**
- `frozen_absolute_band = [0.125, 8.0]` — `constant_factor_c = 8` inherited from
  EXP-DS-001 and matching the driver's `CONSTANT_FACTOR_C`. **Has not moved.**
- Both ladders are the driver's `LADDER_SMOOTH` / `LADDER_ROUGH` =
  (0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05), seven rungs, unchanged.
- `BSM_LADDER` rungs `u_target` 2–6 unchanged; all ten `u_recomputed` values
  reproduce.
- All **seven** statistic ids appear under **both** cells in **both** `bands` and
  `null_spread`, including the two struck ids. Nothing was dropped from the file.

**No cut moved.** ✅ Clause 2 satisfied.

### 4.4 The one piece of latitude I did find — the numeric movement floor

Stated because the duty is to find latitude, not to certify its absence.

PERTURB-MOVE-1 requires "a shift beyond noise" and the metrics list defines
`LPF_movement_beyond_noise_flag` as "whether the recorded shift **exceeds the
measured null spread**". **That phrase is ambiguous between one null standard
deviation and the `[min, max]` range of the 200 replicates, and the frozen contract
fixes no number.** The number 1.0 lives in the **driver** (line 1508–1509,
`abs(shift) >= 1.0`), which did **not** exist at the contract commit ba1567ee.

Three things keep this from being a violation:

1. The driver was authored complete and hash-bound **before** the calibration ran, so
   the floor is pre-datum even though it is post-contract — which is exactly what
   ATS-LPF-1 clause 3 contemplates.
2. **The driver records both readings** (`LPF_movement_beyond_noise_flag` and
   `movement_beyond_null_range_auxiliary_record`) on every one of the 210 rows and
   freezes neither as a cut, and routes the choice to this review.
3. **Both readings agree on everything the strikes turn on.** I checked all 210 rows:
   they disagree on 22, **every one of which is a `True` under the sd reading and
   `False` under the range reading at an intermediate or top rung of a ladder that is
   certified anyway**. For the two struck ids the readings agree completely — 0 of 28
   rows flagged for `STAT-TAIL-DEEP` and 0 of 28 for `STAT-RATE-u@u_target=6` under
   **both** readings.

**Ruling:** the sd reading is the admissible one, because the metric definition
states the unit ("in units of the measured null standard deviation") and the range
reading has no fixed confidence level attached to it. **The choice is non-decisional
for every strike.** I record the ambiguity as latitude that existed and was not
exploited, and I note for the roadmap that a future contract of this shape should fix
the movement floor numerically in the hash-bound file.

---

## 5. THE STRIKES — scrutinised as the place latitude existed

This is the substance of the duty. **The strikes remove obstacles from the
favourable path**, which is the direction that demands scrutiny: with
`STAT-TAIL-DEEP` and `STAT-RATE-u@u_target=6` retained there would be **fourteen**
comparisons instead of ten, so `P(L-2 | correct null)` would fall by roughly
`(1 − 4/201)⁴ ≈ 7.7 %` relative. **A strike makes the consistent branch easier.**

### 5.1 Is the strike a mechanism the contract provides? — YES, pre-declared, twice

Two independent hash-bound provisions, both fixed at ba1567ee before any datum:

- **CERT-LPF-1** (spec lines 527–536): *"Membership of CERT-LPF-1 is **PROVISIONAL**
  until the calibration demonstrates, per statistic, per family and per rung, that
  the statistic moves… A member that does not move on any rung of either ladder **is
  STRUCK FROM THE CERTIFYING SET BY RR-LPF-1 at freeze time**, with the strike
  recorded and justified."*
- **PERTURB-MOVE-1** (spec lines 855–867): *"A FAMILY WHOSE TOP RUNG SHOWS NO
  MOVEMENT **IS STRUCK** FROM THE CERTIFIED LIST BY THE READING RULE **RATHER THAN
  REPORTED AS LOW POWER**."*

Both are **mandatory in form** — "is STRUCK", not "may be struck". The freezing
Coordinator had **no discretion to retain** a member with zero movement rows. **The
strike is not a choice the freeze made; it is an obligation the contract imposed,
and the freeze would have violated the contract by declining it.**

Further, the contract *anticipated this exact outcome* and named it as the reason
PERTURB-MOVE-1 exists: *"RTB-040-2 FOUND TWO OF THREE DECLARED CERTIFYING STATISTICS
STRUCTURALLY INCAPABLE OF MOVING, AND THEIR IMMOBILITY WAS THEN CITED AS EVIDENCE.
THAT MUST NOT RECUR."* The mechanism fired on its third instance, which is what it
was built for.

### 5.2 Is the *criterion* post-hoc? — NO

The criterion is `|shift| ≥ 1` measured null sd, applied uniformly to all 210 rows by
the hash-bound driver. **It was not chosen after seeing which statistics failed it**:
the same criterion certifies 20 ladders and strikes 8, and it is applied identically
to retained and struck ids. There is no statistic-specific threshold anywhere in the
file.

Under the auxiliary range reading the strikes are **also** unanimous (0 of 28 rows
each). **The strikes survive both readings**, so no reading was selected to produce
them.

### 5.3 Is the *measured basis* real? — YES, recomputed

| struck id | plant rung-cell rows | rows flagged (sd reading) | rows flagged (range reading) | max abs shift |
|---|---|---|---|---|
| `STAT-TAIL-DEEP` | 28 | **0** | **0** | 0.3379820826156079 (ROUGH, bits 20, γ = 0.05) |
| `STAT-RATE-u@u_target=6` | 28 | **0** | **0** | 0.4809110364879298 (ROUGH, bits 20, γ = 0.05) |

Both maxima are far below the floor of 1.0 and both hold at **every** rung of **both**
ladders at **both** cells. ✅

### 5.4 Is the *justification* sound? — ONE YES, ONE NO

- **STRIKE-2 (`u_target=6`): sound, and I strengthened it.** Independently measured
  the "accident" rate its argument rests on — 10 of 130 820 top-rung smooth plants
  are 40-smooth at bits 16 and 1 of 130 820 are 102-smooth at bits 20, i.e. 0.5 and
  0.05 added smooth samples per replicate against a null sd of 5.06 and 3.65 counts.
  Predicted net shift ≈ −0.18 sd; measured −0.290 and −0.454. **Construction
  mismatch, correctly characterised, not low power.**
- **STRIKE-1 (`STAT-TAIL-DEEP`): the strike is right, the justification is wrong.**
  D1's quoted maxima are not reproducible and its universal claim is falsified by the
  frozen pipeline's own output. Full re-derivation in `attainability_check.md` §1;
  recorded as blocking defect **RTB-054-2**. **This does not make the strike
  post-hoc** — the measured basis is independently sufficient and both readings agree
  — but CERT-LPF-1 requires a strike to be *"recorded **and justified**"*, and the
  justification as written does not survive execution.

### 5.5 The place where the strikes DID produce an unsupported claim — RTB-054-1

The strikes are correct at the **ladder** level. They are **not** correct at the
**per-rung** level, and that is where the favourable-direction error actually landed.
`certification.certified_ladders` freezes a `moving_rungs_*` list per ladder, and the
file's own note makes that list the per-rung power certificate. Recomputing all 28
lists from `LPF_movement_beyond_noise_flag`:

| ladder | cell | frozen `moving_rungs` | recomputed | direction |
|---|---|---|---|---|
| ROUGH / `STAT-RATE-u@u_target=2` | 16 | [**0.005**, 0.01, 0.02, 0.05] | [0.01, 0.02, 0.05] | **OVERSTATES** |
| ROUGH / `STAT-KS-DICK` | 16 | [**0.01**, 0.02, 0.05] | [0.02, 0.05] | **OVERSTATES** |
| SMOOTH / `STAT-RATE-u@u_target=3` | 20 | [0.002, 0.005, 0.01, 0.02, 0.05] | [**0.001**, 0.002, …] | understates |
| all other 25 | — | — | identical | ✅ |

The two overstated rungs carry shifts **−0.882122** and **−0.937958** null sd, both
below the floor, both `False` under **both** readings, and both `1/20` rejections
with `detected_under_DET_LPF_1 = false`. **They are uncertified on every criterion
the calibration archives.**

**PERTURB-MOVE-1's named reviewer duty makes this a REVISE in terms:** *"a rung with
no recorded movement that the reading rule nevertheless certifies, is a REVISE."*
The direction is the unfavourable one — it claims rough-direction power at a γ an
octave below where any movement was recorded — and it propagates, because
ALT-CLASS-RR052 declares itself binding on every statement citing this experiment.

### 5.6 Overall ruling on the strikes

**The two strikes are a pre-declared, contract-mandated mechanism correctly
triggered by a uniformly-applied pre-datum criterion, and they are not a
post-calibration choice.** They make the favourable branch easier, that effect is
real (~7.7 % relative), and it is the price of a contract clause written before the
data existed to prevent a worse failure. I would not have accepted them had the
criterion been statistic-specific, had the two readings disagreed, or had the strike
been discretionary in the contract's wording. None of those is the case.

**What is not sound is the per-rung certification attached to them (RTB-054-1) and
STRIKE-1's justification text (RTB-054-2).** Both are repairable in a superseding
record without re-running anything.

---

## 6. Pre-disclosures — ATS-LPF-1 clause 6

The clause lists exactly two admissible pre-disclosures and says *"NO OTHER
PRE-DISCLOSURE EXISTS; if the reviewer finds one, that is a REVISE."*

- **(a) OBJ-CTRL-PRODUCT** measured in calibration, detection derivable in advance —
  declared, and used only as an apparatus control.
- **(b) uniform-arm `R(u)`** measured in calibration, partially foreshadowing LIMB B
  decidability — declared, and the reading rule flags it explicitly as clause 6(b).

**I searched for a third and did not find one.** Specifically I checked that:

- no band, spread, cut or branch derives from `OBJ-REAL`, `OBJ-NULL-SYNTH`,
  `OBJ-CTRL-PRODUCT` or any plant arm — every band comes from the `LPF-CAL-A`
  `OBJ-NULL-UNIF` arrays, verified by recomputation;
- the calibration contains **no real-object sample** at the level of objects (§3);
- `STAT-KS2-CAL` is uncomputed in calibration, so nothing about the real arm's
  two-sample behaviour is foreshadowed;
- the D9 anomaly and the two strikes are calibration-internal and say nothing about
  the real arm in either direction.

⚠️ **One quantity sits close to the line and I record it rather than let it pass.**
The `limb_b_decidability_map` discloses that the uniform arm's `R(u)` is far from 1
and rises with `u`, reaching 11.59 at bits 16 u = 6. Because L-3's second leg fires
on the **real** arm's `R(u)` leaving `[1/8, 8]` **while the uniform arm's stays
inside**, this pre-disclosure tells a reader in advance how much headroom that leg
has — at bits 16 u = 5 the uniform arm sits at 4.571 of an 8.0 ceiling, so ~1.75×
rather than 8×. That is squarely within clause 6(b)'s admitted disclosure ("partially
foreshadow LIMB B's decidability at each rung") and is **not** a third
pre-disclosure. But the **asymmetry** it implies is not declared anywhere, and it
should be (RTB-054-6).

✅ Clause 6 satisfied.

---

## 7. Clause 4 — no latitude on ambiguities discovered after a number existed

Six items were routed rather than resolved: OPEN-LPF049-A, OPEN-RR052-B,
OPEN-RR052-D, DREAD-LPF-1, ANOM-LPF052-1 and (with its choice applied and its full
consequence stated) OPEN-RR052-A. **The freeze resolved none of them silently**, and
on OPEN-RR052-A it explicitly recorded that if the reviewer prefers the other reading
"the correct outcome is NOT an edit of this file but a REVISE returning a recorded
non-execution". **That is clause-4-compliant behaviour and I record it as such.** My
rulings are in `contract_review.yaml`.

One deviation to record under this clause: `identity_binomial_cut = 4` is **not** the
cut the contract's literal `n = 80` implies (which is 5). The freeze states this and
argues the low cut is the conservative direction — correctly, since firing L-5
**suspends** the rule and yields no disposition. **Accepted as conservative and
non-decisional at this calibration; binding for the future**: if any record ever
needs this leg's firing or non-firing, `n` becomes decisional and the choice is a
Coordinator amendment, never a freezer's or a reviewer's interpretation.

---

## 8. Summary table

| check | result |
|---|---|
| ba1567ee ancestor of 104d32fa ancestor of 1026150f | ✅ |
| no run artifact (and no driver) in tree at ba1567ee | ✅ |
| specification sha256 unchanged since freeze | ✅ |
| DRIVER_SHA256 binds one identical file across snapshot, manifest, RR, tree | ✅ |
| 28/28 band edges recompute exactly from named arrays | ✅ |
| 28/28 null_spread entries recompute exactly | ✅ |
| 12/12 branch condition+disposition strings identical (whitespace-normalised) | ✅ |
| branch ids and order unchanged; precedence unchanged | ✅ |
| no statistic, rung, ladder, cut or band added, dropped, moved or reordered | ✅ |
| calibration contains no real-object sample, at object level | ✅ |
| exactly two pre-disclosures, both declared | ✅ |
| strikes are a pre-declared, mandatory, uniformly-applied mechanism | ✅ |
| strike criterion is not statistic-specific and survives both readings | ✅ |
| STRIKE-2 justification sound (independently strengthened) | ✅ |
| STRIKE-1 justification sound | ❌ **RTB-054-2** |
| per-rung certifications match the movement flags | ❌ **RTB-054-1** (2 rungs overstated, 1 understated) |
| movement floor numerically fixed in the hash-bound contract | ⚠️ fixed in driver only; non-decisional |

**Duty 2 passes on the anti-tuning question proper. The defects it surfaces are
recorded against duties 3 and 4.**
