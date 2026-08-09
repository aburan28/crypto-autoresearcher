# TASK-20260808-cece0c — Section B (AM-6): the AM-3 positive control rebuilt

`c_min` in CLOSED FORM at ALL 12 STEPS of ALL 4 CELLS, with the post-injection `Delta` printed at each.

BATCH-cbe023 / GOAL-MLKEM-005. Executor artifact — **observations only**. No status change, no evidence record, no hypothesis movement.

> ### CLAIM TIER: TOY, UNCONDITIONALLY.
> Nothing in this document, and nothing the measurement it reports can produce, bears on ML-KEM security, on any FIPS 203 parameter set, on any attack cost, or on any cost model. `d <= 140`, `beta <= 40`, `n = 8` draws, `N = 2^20`.

`certificate.kind: none` — no discrete-log solve and no factor-base relation is claimed or produced, so `docs/claims-and-verification.md` requires no solution certificate. The independent re-verifications this run carries are INSTRUMENT CHECKS and are labelled as such, never as certificates.

---

## 0. Inference record (verbatim, as the task card requires)

```
requested_policy: executor-implementation
degraded_allowed: false ; fallback_allowed: false
resolved: per CLAUDE.md, per-role model selection is process-level under the
  Claude Code runtime and subagents keep model: inherit, so the resolved
  model is the session model
fallback_used: false
model_verified: false (no `orchestration.adapter doctor --probe` receipt for
  this session)
independent_session: PROCEDURAL ONLY -- separate session, no shared scratch.
  NEVER model-level. AGENTS.md rule 12 remains UNMET and UNWAIVED in this
  goal and is recorded, not smoothed (prereg 5.10).
```

---

## 1. Notarized pre-registration — VERIFIED, and verified IN THIS WORKTREE

The governing contract is Section B (3.1–3.9) of
`coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-35efa3/prereg.md`.
It was loaded READ-ONLY and was NOT modified. No threshold was re-derived, no grid point was added, removed or re-spaced.

| check | value |
|---|---|
| recomputed sha256 | `2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8` |
| expected sha256 (task card, hard-coded in the script) | `2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8` |
| producer sidecar `prereg_sha256.txt` | `2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8` |
| notarized receipt `archive.path_sha256` | `2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8` |
| notarized receipt `prereg_sha256` field | `2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8` |
| sha256 of the BLOB INSIDE the notarizing commit | `2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8` |
| prereg bytes | 89077 |
| **all five agree** | **True** |

**Quoted digest, as the completion gate requires:**

```
sha256(prereg.md) = 2da554914e5d78146c1e6cafcdbd109aacbc1a1624ed1f8e94ae769f757fc4f8
```

### 1.1 Ancestry asserted against the NOTARIZING COMMIT ITSELF

```
git merge-base --is-ancestor 4f7c63703d50445c758fc6216ca8d4436e04ae2a HEAD
  -> is_ancestor_of_HEAD = True
```

* notarizing commit: `4f7c63703d50445c758fc6216ca8d4436e04ae2a`
* notarizing commit metadata (obtained at the shell, see deviation D-3 below): `4f7c63703d50445c758fc6216ca8d4436e04ae2a  2026-08-08 18:14:03 -0700  research: GOAL-MLKEM-005 TASK-20260808-e725b4 NOTARIZES the BATCH-cbe023 pre-registration`
* `git log --follow` commits touching the prereg: ['4f7c63703d50445c758fc6216ca8d4436e04ae2a'] (count 1) — the file has exactly one history entry, the notarizing commit
* HEAD at gate time: `ed5cc287d54991480c23629b5ed477bb194dfa4c` on branch `feat/crypto-autoresearcher-kb-adfc38`
* worktree dirty: True; dirty paths recorded in `results_g3.json`

The assertion asserts the **notarizing commit itself, not its parent** — carried correction V-7 (prereg 0.3), recorded because BATCH-f19c37's check would have passed had the notarization never happened.

### 1.2 Defect D-2 is NOT repeated — the assertion was made IN THIS WORKTREE

The sibling task AM-7 recorded defect **D-2**: its script's `REPO_ROOT` resolved five directory levels up, landing in the enclosing checkout, so its ancestry assertion was made against the WRONG `HEAD`. This run resolves `REPO_ROOT` four levels above `batches/` **and then verifies it**, and aborts if the verification fails:

| check | value |
|---|---|
| `REPO_ROOT` resolved | `/Volumes/SSD990/crypto-autoresearcher/.claude/worktrees/crypto-autoresearcher-kb-adfc38` |
| `git -C REPO_ROOT rev-parse --show-toplevel` | `/Volumes/SSD990/crypto-autoresearcher/.claude/worktrees/crypto-autoresearcher-kb-adfc38` |
| `git rev-parse --git-common-dir` | `/Volumes/SSD990/crypto-autoresearcher/.git` |
| **REPO_ROOT is this worktree** | **True** |

The two paths are identical, so the `merge-base` assertion above was evaluated against the `HEAD` of the dispatched worktree `crypto-autoresearcher-kb-adfc38` and not against any enclosing checkout. `--git-common-dir` differs from the worktree path, which is exactly the signature of a linked worktree and is why the naive parent-count was insufficient on its own.

---

## 2. NO NEW BKZ — the seed-cache reproduction, re-verified BEFORE any scoring

The graded family and the Haar null are pure `numpy` and **the seeds are the cache**. No lattice was generated, no basis was reduced, **no LLL and no BKZ was executed**, and `fpylll` was not called. All 4 × 14 × 8 = 448 per-draw values `r = q_emp(2^-10)/q_Beta(2^-10)` were regenerated from the carried seeds and compared BEFORE anything was scored.

| leg | n values | max abs deviation | by `d` |
|---|---|---|---|
| vs committed `BATCH-a44d08/.../results_g3.json` (prereg 3.5's own comparison) | 448 | `0.0` | `{'100': 0.0, '140': 0.0}` |
| vs `BATCH-f19c37/.../results.json` (the source of the declared non-zero deviation) | 448 | `2.220446049250313e-16` | `{'100': 0.0, '140': 2.220446049250313e-16}` |

> ### THE MAX DEVIATION IS REPORTED UNROUNDED.
> Against `BATCH-f19c37` it is **`2.220446049250313e-16`**, confined to `d = 140` (`d = 100` is exactly `0.0`), which is EXACTLY the value prereg 3.5 declared in advance: one ULP, traced to a one-ULP difference in the deterministic reference divisor `betaincinv(beta/2,(d-beta)/2,2^-10)` under `scipy 1.15.3`. **It is not rounded to `0.0`, and the carried `0.0` is not reported in its place.**
> Against the committed `results_g3.json` the 448 values are bitwise identical (`0.0`), which is the expected relation: that record is itself the output of the same seeds in the same environment with BLAS threads pinned to 1.

**`c_min` reproduction.** `c_min` was not computed by BATCH-a44d08 (Section B introduces it), so `c_min(committed)` is evaluated here from the committed record's own frozen per-step quantities via the identical closed form, in two independent legs. This is NOT a rescoring of BATCH-a44d08's verdict, which stands untouched.

| leg | n compared | max abs dev (c units) |
|---|---|---|
| (a) from the committed `AM3.steps` fields `delta` / `se_step_paired` / `se_diff_at_t_lo` | 48 | `0.0` |
| (b) recomputed from the committed per-draw `r_values` | 48 | `0.0` |

**Admissibility (prereg 3.5), frozen thresholds:**

```
max |dev| on r        = 2.220446049250313e-16   <= 1e-09      -> True
max |d c_min| in c    = 0.0                <= 0.01     -> True
ADMISSIBLE            = True
```

Had either been exceeded, the arm would be INSTRUMENT-LIMITED, that would be reported as the result, and no power statement would be made.

---

## 3. The step-selection rule, and that it does not maximise the injection's own denominator

> ### THE STEP-SELECTION RULE IS: **THERE IS NONE.**

Every one of the 12 steps of every one of the 4 cells is reported. AM-6 clause (b) is satisfied by **removing** the object that carried the defect rather than by replacing it (prereg 3.3).

**Why this is the thing that had to change.** The injection is denominated in `SE_diff(A, t_i)`. BATCH-a44d08's positive control selected

```
i_hard = argmax_{i in 0..11} SE_diff(A, t_i)
```

— i.e. it selected the step that **maximises exactly the denominator the injection is measured in**. `SE_diff` is largest at the head of the descent, where `|Delta_i|` is 11× to 26× the injection unit, so the injection was spent where the curve is falling fastest. This run applies **no argmax, no argmin, and no data-dependent or grid-dependent selection to the frozen headline**: all 48 steps are scored and reported, and PRED-B1 is a count over all 12 steps of each cell. A reader can check this mechanically — `measure_g3.py` contains no `argmax` over any `SE` quantity.

Two SUMMARIES are reported beside the full table, both labelled and neither the headline:

| summary | selection basis | d100_b30 | d100_b40 | d140_b30 | d140_b40 |
|---|---|---|---|---|---|
| **S1** median `c_min`, steps `i in {5..11}` | frozen grid position only — **DATA-INDEPENDENT** | 3.9769 | 2.7152 | 3.7647 | 4.1746 |
| S1 range | | [2.0308, 7.2644] | [2.2573, 5.2813] | [2.8553, 4.6781] | [1.8608, 5.5711] |
| **S2** median `c_min`, steps with `|Delta_i| <= 1.0*SE_diff(t_i)` | uses the data — **DATA-DEPENDENT, DESCRIPTIVE ONLY** | 3.2433 (n=4) | 2.6906 (n=5) | 2.8669 (n=3) | 4.1746 (n=5) |

For reference only, and labelled as a REVIEW MEASUREMENT that AM-6 forbids citing as a rescoring: the Red Team reported plateau medians `3.98 / 2.72 / 3.76 / 4.17` [quoted: red_team_report.md 2.2]. This run's independent S1 medians are 3.98 / 2.72 / 3.76 / 4.17. The agreement is reported as an observation; it is not a reproduction of that review and confers nothing on it.

---

## 4. `c_min` in closed form at ALL 12 STEPS of ALL 4 CELLS

Closed forms, quoted from prereg 3.2 and implemented exactly as written:

```
stat_i(c) = ( Delta_i + (c - 1) * SE_diff(t_i) ) / SE_step(i)
c_min(i)  = 1 + ( t_crit * SE_step(i) - Delta_i ) / SE_diff(t_i)        t_crit = 4.2071245566046755 = t_{7,0.998}
c_pos(i)  = max( 0 , - Delta_i / SE_diff(t_i) )
post-injection Delta_i(c) = Delta_i + c * SE_diff(t_i)
```

`SE_diff(A,t) = sqrt(sd_A^2/8 + sd_haar^2/8)`; `epsilon_i = 1.0 * SE_diff(A,t_i)`; `SE_step(i) = sd_j(r_j(t_{i+1}) - r_j(t_i))/sqrt(8)`, paired, `ddof=1`. **`4.0` is a NOMINAL FACTOR, NOT a p-value; its realized one-sided false-positive rate was measured at `0.0015`–`0.0025` against a nominal `3e-5`** [quoted: BATCH-f19c37 validation_report.yaml item 4 / V-5] — prereg 1 requires every report citing the gate to state this.

**Degenerate steps: 0 of 48.** No step had `SE_diff = 0` or `SE_step = 0`, so no step was excluded from the counts and no division by zero was performed.

### 4.1 Cell `d100_b30` (`d = 100`, `beta = 30`, `q = 3329`) — Haar null `r_mean = 0.998649194`, `r_sd = 2.5442e-03`

| i | t_lo | t_hi | Delta_i | SE_step(i) | SE_diff(t_i) = eps_i | c_pos(i) | **c_min(i)** | c_min/4 | Delta>0? | near-flat? |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0000 | 0.0025 | -3.782943e-02 | 1.7934e-03 | 2.0246e-03 | 18.6851 | **23.4119** | 5.8530 | . | . |
| 1 | 0.0025 | 0.0050 | -2.053653e-02 | 4.1041e-04 | 1.7592e-03 | 11.6740 | **13.6555** | 3.4139 | . | . |
| 2 | 0.0050 | 0.0075 | -1.229569e-02 | 9.6091e-04 | 1.7109e-03 | 7.1867 | **10.5496** | 2.6374 | . | . |
| 3 | 0.0075 | 0.0100 | -7.101057e-03 | 2.7500e-04 | 1.2578e-03 | 5.6454 | **7.5652** | 1.8913 | . | . |
| 4 | 0.0100 | 0.0150 | -9.214951e-03 | 4.5361e-04 | 1.2395e-03 | 7.4343 | **9.9739** | 2.4935 | . | . |
| 5 | 0.0150 | 0.0200 | -4.839381e-03 | 6.7641e-04 | 1.2268e-03 | 3.9448 | **7.2644** | 1.8161 | . | . |
| 6 | 0.0200 | 0.0300 | -2.141897e-03 | 6.9055e-04 | 1.3050e-03 | 1.6413 | **4.8674** | 1.2169 | . | . |
| 7 | 0.0300 | 0.0500 | -1.596598e-03 | 7.7716e-04 | 1.4468e-03 | 1.1036 | **4.3635** | 1.0909 | . | . |
| 8 | 0.0500 | 0.1000 | +6.080236e-04 | 4.5275e-04 | 1.2581e-03 | 0.0000 | **2.0308** | 0.5077 | **Y** | Y |
| 9 | 0.1000 | 0.2500 | +7.379340e-04 | 1.0769e-03 | 1.4430e-03 | 0.0000 | **3.6284** | 0.9071 | **Y** | Y |
| 10 | 0.2500 | 0.5000 | +1.008432e-04 | 5.4966e-04 | 1.1902e-03 | 0.0000 | **2.8582** | 0.7145 | **Y** | Y |
| 11 | 0.5000 | 1.0000 | -1.552508e-04 | 8.7717e-04 | 1.2918e-03 | 0.1202 | **3.9769** | 0.9942 | . | Y |

**Post-injection `Delta_i(c) = Delta_i + c*SE_diff(t_i)` at every `c` of the frozen grid** (`FIRE` marks `stat_i(c) > t_crit`, equivalently `c_min(i) <= c`):

| i | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | -3.7829e-02 | -3.5805e-02 | -3.3780e-02 | -3.1756e-02 | -2.9731e-02 | -2.5682e-02 | -2.1633e-02 | -1.3535e-02 | -5.4362e-03 | +1.0760e-02 **FIRE** | +2.6957e-02 **FIRE** |
| 1 | -2.0537e-02 | -1.8777e-02 | -1.7018e-02 | -1.5259e-02 | -1.3500e-02 | -9.9815e-03 | -6.4631e-03 | +5.7358e-04 | +7.6103e-03 **FIRE** | +2.1684e-02 **FIRE** | +3.5757e-02 **FIRE** |
| 2 | -1.2296e-02 | -1.0585e-02 | -8.8739e-03 | -7.1630e-03 | -5.4521e-03 | -2.0303e-03 | +1.3915e-03 | +8.2351e-03 **FIRE** | +1.5079e-02 **FIRE** | +2.8766e-02 **FIRE** | +4.2453e-02 **FIRE** |
| 3 | -7.1011e-03 | -5.8432e-03 | -4.5854e-03 | -3.3275e-03 | -2.0697e-03 | +4.4599e-04 | +2.9617e-03 **FIRE** | +7.9930e-03 **FIRE** | +1.3024e-02 **FIRE** | +2.3087e-02 **FIRE** | +3.3150e-02 **FIRE** |
| 4 | -9.2150e-03 | -7.9754e-03 | -6.7359e-03 | -5.4964e-03 | -4.2569e-03 | -1.7779e-03 | +7.0118e-04 | +5.6592e-03 **FIRE** | +1.0617e-02 **FIRE** | +2.0533e-02 **FIRE** | +3.0450e-02 **FIRE** |
| 5 | -4.8394e-03 | -3.6126e-03 | -2.3858e-03 | -1.1590e-03 | +6.7749e-05 | +2.5213e-03 | +4.9749e-03 **FIRE** | +9.8820e-03 **FIRE** | +1.4789e-02 **FIRE** | +2.4603e-02 **FIRE** | +3.4418e-02 **FIRE** |
| 6 | -2.1419e-03 | -8.3687e-04 | +4.6816e-04 | +1.7732e-03 | +3.0782e-03 | +5.6883e-03 **FIRE** | +8.2983e-03 **FIRE** | +1.3518e-02 **FIRE** | +1.8739e-02 **FIRE** | +2.9179e-02 **FIRE** | +3.9619e-02 **FIRE** |
| 7 | -1.5966e-03 | -1.4983e-04 | +1.2969e-03 | +2.7437e-03 | +4.1905e-03 | +7.0840e-03 **FIRE** | +9.9775e-03 **FIRE** | +1.5765e-02 **FIRE** | +2.1552e-02 **FIRE** | +3.3126e-02 **FIRE** | +4.4700e-02 **FIRE** |
| 8 | +6.0802e-04 | +1.8661e-03 | +3.1241e-03 | +4.3822e-03 **FIRE** | +5.6403e-03 **FIRE** | +8.1564e-03 **FIRE** | +1.0673e-02 **FIRE** | +1.5705e-02 **FIRE** | +2.0737e-02 **FIRE** | +3.0802e-02 **FIRE** | +4.0866e-02 **FIRE** |
| 9 | +7.3793e-04 | +2.1810e-03 | +3.6240e-03 | +5.0670e-03 | +6.5101e-03 **FIRE** | +9.3961e-03 **FIRE** | +1.2282e-02 **FIRE** | +1.8054e-02 **FIRE** | +2.3826e-02 **FIRE** | +3.5371e-02 **FIRE** | +4.6915e-02 **FIRE** |
| 10 | +1.0084e-04 | +1.2911e-03 | +2.4813e-03 | +3.6715e-03 **FIRE** | +4.8617e-03 **FIRE** | +7.2421e-03 **FIRE** | +9.6225e-03 **FIRE** | +1.4383e-02 **FIRE** | +1.9144e-02 **FIRE** | +2.8666e-02 **FIRE** | +3.8188e-02 **FIRE** |
| 11 | -1.5525e-04 | +1.1366e-03 | +2.4284e-03 | +3.7202e-03 | +5.0120e-03 **FIRE** | +7.5956e-03 **FIRE** | +1.0179e-02 **FIRE** | +1.5346e-02 **FIRE** | +2.0514e-02 **FIRE** | +3.0848e-02 **FIRE** | +4.1183e-02 **FIRE** |

| n_fire(c) | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **all 12 steps** | 0 | 0 | 0 | 2 | 4 | 6 | 8 | 10 | 11 | 12 | 12 |
| excluding already-increasing steps | 0 | 0 | 0 | 0 | 1 | 3 | 5 | 7 | 8 | 9 | 9 |

* steps with `Delta_i > 0` in the raw data (NC-B3): **3 of 12**, at indices `[8, 9, 10]`
* `c_min(i) > c_pos(i)` at every step of this cell: **True**
* `c_min` min / median / max: 2.0308 / 6.0659 / 23.4119 — in gate-width units `c_min/4`: 0.5077 / 1.5165 / 5.8530
* the two `n_fire` definitions (`#{i : c_min(i) <= c}` and `stat_i(c) > t_crit`) agree at every `c`: **True**

### 4.2 Cell `d100_b40` (`d = 100`, `beta = 40`, `q = 3329`) — Haar null `r_mean = 0.998981370`, `r_sd = 2.5245e-03`

| i | t_lo | t_hi | Delta_i | SE_step(i) | SE_diff(t_i) = eps_i | c_pos(i) | **c_min(i)** | c_min/4 | Delta>0? | near-flat? |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0000 | 0.0025 | -3.433407e-02 | 1.5920e-03 | 1.3187e-03 | 26.0360 | **32.1148** | 8.0287 | . | . |
| 1 | 0.0025 | 0.0050 | -1.840990e-02 | 4.4574e-04 | 1.3211e-03 | 13.9348 | **16.3542** | 4.0885 | . | . |
| 2 | 0.0050 | 0.0075 | -1.073051e-02 | 8.4944e-04 | 1.2606e-03 | 8.5123 | **12.3472** | 3.0868 | . | . |
| 3 | 0.0075 | 0.0100 | -6.582916e-03 | 3.3106e-04 | 1.4013e-03 | 4.6978 | **6.6918** | 1.6729 | . | . |
| 4 | 0.0100 | 0.0150 | -7.086088e-03 | 3.6146e-04 | 1.4249e-03 | 4.9731 | **7.0403** | 1.7601 | . | . |
| 5 | 0.0150 | 0.0200 | -3.236980e-03 | 6.3302e-04 | 1.3781e-03 | 2.3488 | **5.2813** | 1.3203 | . | . |
| 6 | 0.0200 | 0.0300 | -2.983254e-03 | 5.0058e-04 | 1.2552e-03 | 2.3767 | **5.0545** | 1.2636 | . | . |
| 7 | 0.0300 | 0.0500 | -8.487212e-04 | 3.8837e-04 | 1.4813e-03 | 0.5730 | **2.6760** | 0.6690 | . | Y |
| 8 | 0.0500 | 0.1000 | -8.723117e-04 | 3.4976e-04 | 1.3665e-03 | 0.6384 | **2.7152** | 0.6788 | . | Y |
| 9 | 0.1000 | 0.2500 | -2.947764e-04 | 6.1457e-04 | 1.2519e-03 | 0.2355 | **3.3008** | 0.8252 | . | Y |
| 10 | 0.2500 | 0.5000 | +1.553741e-04 | 3.9567e-04 | 1.2004e-03 | 0.0000 | **2.2573** | 0.5643 | **Y** | Y |
| 11 | 0.5000 | 1.0000 | +5.088137e-04 | 6.6408e-04 | 1.3516e-03 | 0.0000 | **2.6906** | 0.6727 | **Y** | Y |

**Post-injection `Delta_i(c) = Delta_i + c*SE_diff(t_i)` at every `c` of the frozen grid** (`FIRE` marks `stat_i(c) > t_crit`, equivalently `c_min(i) <= c`):

| i | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | -3.4334e-02 | -3.3015e-02 | -3.1697e-02 | -3.0378e-02 | -2.9059e-02 | -2.6422e-02 | -2.3784e-02 | -1.8509e-02 | -1.3235e-02 | -2.6849e-03 | +7.8649e-03 |
| 1 | -1.8410e-02 | -1.7089e-02 | -1.5768e-02 | -1.4446e-02 | -1.3125e-02 | -1.0483e-02 | -7.8407e-03 | -2.5561e-03 | +2.7285e-03 | +1.3298e-02 **FIRE** | +2.3867e-02 **FIRE** |
| 2 | -1.0731e-02 | -9.4699e-03 | -8.2093e-03 | -6.9487e-03 | -5.6881e-03 | -3.1669e-03 | -6.4576e-04 | +4.3966e-03 | +9.4390e-03 **FIRE** | +1.9524e-02 **FIRE** | +2.9609e-02 **FIRE** |
| 3 | -6.5829e-03 | -5.1816e-03 | -3.7804e-03 | -2.3791e-03 | -9.7781e-04 | +1.8247e-03 | +4.6273e-03 **FIRE** | +1.0232e-02 **FIRE** | +1.5837e-02 **FIRE** | +2.7048e-02 **FIRE** | +3.8258e-02 **FIRE** |
| 4 | -7.0861e-03 | -5.6612e-03 | -4.2363e-03 | -2.8114e-03 | -1.3865e-03 | +1.4632e-03 | +4.3130e-03 **FIRE** | +1.0013e-02 **FIRE** | +1.5712e-02 **FIRE** | +2.7111e-02 **FIRE** | +3.8510e-02 **FIRE** |
| 5 | -3.2370e-03 | -1.8588e-03 | -4.8070e-04 | +8.9743e-04 | +2.2756e-03 | +5.0318e-03 **FIRE** | +7.7881e-03 **FIRE** | +1.3301e-02 **FIRE** | +1.8813e-02 **FIRE** | +2.9838e-02 **FIRE** | +4.0863e-02 **FIRE** |
| 6 | -2.9833e-03 | -1.7281e-03 | -4.7285e-04 | +7.8236e-04 | +2.0376e-03 | +4.5480e-03 **FIRE** | +7.0584e-03 **FIRE** | +1.2079e-02 **FIRE** | +1.7100e-02 **FIRE** | +2.7142e-02 **FIRE** | +3.7183e-02 **FIRE** |
| 7 | -8.4872e-04 | +6.3259e-04 | +2.1139e-03 | +3.5952e-03 **FIRE** | +5.0765e-03 **FIRE** | +8.0391e-03 **FIRE** | +1.1002e-02 **FIRE** | +1.6927e-02 **FIRE** | +2.2852e-02 **FIRE** | +3.4703e-02 **FIRE** | +4.6553e-02 **FIRE** |
| 8 | -8.7231e-04 | +4.9419e-04 | +1.8607e-03 | +3.2272e-03 **FIRE** | +4.5937e-03 **FIRE** | +7.3267e-03 **FIRE** | +1.0060e-02 **FIRE** | +1.5526e-02 **FIRE** | +2.0992e-02 **FIRE** | +3.1924e-02 **FIRE** | +4.2856e-02 **FIRE** |
| 9 | -2.9478e-04 | +9.5712e-04 | +2.2090e-03 | +3.4609e-03 | +4.7128e-03 **FIRE** | +7.2166e-03 **FIRE** | +9.7204e-03 **FIRE** | +1.4728e-02 **FIRE** | +1.9736e-02 **FIRE** | +2.9751e-02 **FIRE** | +3.9766e-02 **FIRE** |
| 10 | +1.5537e-04 | +1.3558e-03 | +2.5562e-03 | +3.7566e-03 **FIRE** | +4.9571e-03 **FIRE** | +7.3579e-03 **FIRE** | +9.7587e-03 **FIRE** | +1.4560e-02 **FIRE** | +1.9362e-02 **FIRE** | +2.8965e-02 **FIRE** | +3.8569e-02 **FIRE** |
| 11 | +5.0881e-04 | +1.8604e-03 | +3.2120e-03 | +4.5636e-03 **FIRE** | +5.9152e-03 **FIRE** | +8.6185e-03 **FIRE** | +1.1322e-02 **FIRE** | +1.6728e-02 **FIRE** | +2.2135e-02 **FIRE** | +3.2947e-02 **FIRE** | +4.3760e-02 **FIRE** |

| n_fire(c) | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **all 12 steps** | 0 | 0 | 0 | 4 | 5 | 7 | 9 | 9 | 10 | 11 | 11 |
| excluding already-increasing steps | 0 | 0 | 0 | 2 | 3 | 5 | 7 | 7 | 8 | 9 | 9 |

* steps with `Delta_i > 0` in the raw data (NC-B3): **2 of 12**, at indices `[10, 11]`
* `c_min(i) > c_pos(i)` at every step of this cell: **True**
* `c_min` min / median / max: 2.2573 / 5.1679 / 32.1148 — in gate-width units `c_min/4`: 0.5643 / 1.2920 / 8.0287
* the two `n_fire` definitions (`#{i : c_min(i) <= c}` and `stat_i(c) > t_crit`) agree at every `c`: **True**

### 4.3 Cell `d140_b30` (`d = 140`, `beta = 30`, `q = 3329`) — Haar null `r_mean = 1.000760986`, `r_sd = 3.0927e-03`

| i | t_lo | t_hi | Delta_i | SE_step(i) | SE_diff(t_i) = eps_i | c_pos(i) | **c_min(i)** | c_min/4 | Delta>0? | near-flat? |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0000 | 0.0025 | -4.535418e-02 | 1.4936e-03 | 1.7650e-03 | 25.6970 | **30.2572** | 7.5643 | . | . |
| 1 | 0.0025 | 0.0050 | -2.061705e-02 | 1.1110e-03 | 1.6725e-03 | 12.3272 | **16.1219** | 4.0305 | . | . |
| 2 | 0.0050 | 0.0075 | -9.285890e-03 | 6.1685e-04 | 1.7162e-03 | 5.4107 | **7.9228** | 1.9807 | . | . |
| 3 | 0.0075 | 0.0100 | -5.391160e-03 | 5.3381e-04 | 1.5300e-03 | 3.5236 | **5.9914** | 1.4978 | . | . |
| 4 | 0.0100 | 0.0150 | -5.298208e-03 | 6.1297e-04 | 1.7081e-03 | 3.1018 | **5.6116** | 1.4029 | . | . |
| 5 | 0.0150 | 0.0200 | -2.721744e-03 | 4.9103e-04 | 1.7317e-03 | 1.5717 | **3.7647** | 0.9412 | . | . |
| 6 | 0.0200 | 0.0300 | -2.961070e-03 | 7.6624e-04 | 1.6815e-03 | 1.7610 | **4.6781** | 1.1695 | . | . |
| 7 | 0.0300 | 0.0500 | -2.023916e-03 | 7.0934e-04 | 1.5188e-03 | 1.3326 | **4.2975** | 1.0744 | . | . |
| 8 | 0.0500 | 0.1000 | -1.368527e-03 | 6.0244e-04 | 1.2583e-03 | 1.0876 | **4.1020** | 1.0255 | . | . |
| 9 | 0.1000 | 0.2500 | +4.971552e-04 | 6.9899e-04 | 1.2969e-03 | 0.0000 | **2.8842** | 0.7210 | **Y** | Y |
| 10 | 0.2500 | 0.5000 | +3.053897e-04 | 6.1677e-04 | 1.2340e-03 | 0.0000 | **2.8553** | 0.7138 | **Y** | Y |
| 11 | 0.5000 | 1.0000 | -5.680999e-04 | 4.6042e-04 | 1.3419e-03 | 0.4234 | **2.8669** | 0.7167 | . | Y |

**Post-injection `Delta_i(c) = Delta_i + c*SE_diff(t_i)` at every `c` of the frozen grid** (`FIRE` marks `stat_i(c) > t_crit`, equivalently `c_min(i) <= c`):

| i | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | -4.5354e-02 | -4.3589e-02 | -4.1824e-02 | -4.0059e-02 | -3.8294e-02 | -3.4764e-02 | -3.1234e-02 | -2.4175e-02 | -1.7115e-02 | -2.9951e-03 | +1.1125e-02 **FIRE** |
| 1 | -2.0617e-02 | -1.8945e-02 | -1.7272e-02 | -1.5600e-02 | -1.3927e-02 | -1.0582e-02 | -7.2372e-03 | -5.4729e-04 | +6.1426e-03 | +1.9522e-02 **FIRE** | +3.2902e-02 **FIRE** |
| 2 | -9.2859e-03 | -7.5697e-03 | -5.8535e-03 | -4.1373e-03 | -2.4210e-03 | +1.0114e-03 | +4.4438e-03 **FIRE** | +1.1309e-02 **FIRE** | +1.8174e-02 **FIRE** | +3.1903e-02 **FIRE** | +4.5633e-02 **FIRE** |
| 3 | -5.3912e-03 | -3.8611e-03 | -2.3311e-03 | -8.0108e-04 | +7.2895e-04 | +3.7890e-03 **FIRE** | +6.8491e-03 **FIRE** | +1.2969e-02 **FIRE** | +1.9089e-02 **FIRE** | +3.1329e-02 **FIRE** | +4.3570e-02 **FIRE** |
| 4 | -5.2982e-03 | -3.5901e-03 | -1.8820e-03 | -1.7395e-04 | +1.5341e-03 | +4.9503e-03 **FIRE** | +8.3665e-03 **FIRE** | +1.5199e-02 **FIRE** | +2.2031e-02 **FIRE** | +3.5696e-02 **FIRE** | +4.9361e-02 **FIRE** |
| 5 | -2.7217e-03 | -9.9004e-04 | +7.4166e-04 | +2.4734e-03 | +4.2051e-03 **FIRE** | +7.6685e-03 **FIRE** | +1.1132e-02 **FIRE** | +1.8059e-02 **FIRE** | +2.4986e-02 **FIRE** | +3.8839e-02 **FIRE** | +5.2693e-02 **FIRE** |
| 6 | -2.9611e-03 | -1.2796e-03 | +4.0192e-04 | +2.0834e-03 | +3.7649e-03 | +7.1279e-03 **FIRE** | +1.0491e-02 **FIRE** | +1.7217e-02 **FIRE** | +2.3943e-02 **FIRE** | +3.7395e-02 **FIRE** | +5.0847e-02 **FIRE** |
| 7 | -2.0239e-03 | -5.0513e-04 | +1.0137e-03 | +2.5324e-03 | +4.0512e-03 | +7.0888e-03 **FIRE** | +1.0126e-02 **FIRE** | +1.6202e-02 **FIRE** | +2.2277e-02 **FIRE** | +3.4427e-02 **FIRE** | +4.6577e-02 **FIRE** |
| 8 | -1.3685e-03 | -1.1028e-04 | +1.1480e-03 | +2.4062e-03 | +3.6645e-03 | +6.1810e-03 **FIRE** | +8.6975e-03 **FIRE** | +1.3730e-02 **FIRE** | +1.8763e-02 **FIRE** | +2.8829e-02 **FIRE** | +3.8895e-02 **FIRE** |
| 9 | +4.9716e-04 | +1.7940e-03 | +3.0909e-03 | +4.3878e-03 **FIRE** | +5.6847e-03 **FIRE** | +8.2785e-03 **FIRE** | +1.0872e-02 **FIRE** | +1.6060e-02 **FIRE** | +2.1247e-02 **FIRE** | +3.1622e-02 **FIRE** | +4.1997e-02 **FIRE** |
| 10 | +3.0539e-04 | +1.5394e-03 | +2.7733e-03 | +4.0073e-03 **FIRE** | +5.2413e-03 **FIRE** | +7.7093e-03 **FIRE** | +1.0177e-02 **FIRE** | +1.5113e-02 **FIRE** | +2.0049e-02 **FIRE** | +2.9921e-02 **FIRE** | +3.9793e-02 **FIRE** |
| 11 | -5.6810e-04 | +7.7381e-04 | +2.1157e-03 | +3.4576e-03 **FIRE** | +4.7996e-03 **FIRE** | +7.4834e-03 **FIRE** | +1.0167e-02 **FIRE** | +1.5535e-02 **FIRE** | +2.0903e-02 **FIRE** | +3.1638e-02 **FIRE** | +4.2373e-02 **FIRE** |

| n_fire(c) | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **all 12 steps** | 0 | 0 | 0 | 3 | 4 | 9 | 10 | 10 | 10 | 11 | 12 |
| excluding already-increasing steps | 0 | 0 | 0 | 1 | 2 | 7 | 8 | 8 | 8 | 9 | 10 |

* steps with `Delta_i > 0` in the raw data (NC-B3): **2 of 12**, at indices `[9, 10]`
* `c_min(i) > c_pos(i)` at every step of this cell: **True**
* `c_min` min / median / max: 2.8553 / 4.4878 / 30.2572 — in gate-width units `c_min/4`: 0.7138 / 1.1220 / 7.5643
* the two `n_fire` definitions (`#{i : c_min(i) <= c}` and `stat_i(c) > t_crit`) agree at every `c`: **True**

### 4.4 Cell `d140_b40` (`d = 140`, `beta = 40`, `q = 3329`) — Haar null `r_mean = 0.999841698`, `r_sd = 1.9376e-03`

| i | t_lo | t_hi | Delta_i | SE_step(i) | SE_diff(t_i) = eps_i | c_pos(i) | **c_min(i)** | c_min/4 | Delta>0? | near-flat? |
|---|---|---|---|---|---|---|---|---|---|---|
| 0 | 0.0000 | 0.0025 | -3.939667e-02 | 1.1716e-03 | 1.0770e-03 | 36.5812 | **42.1581** | 10.5395 | . | . |
| 1 | 0.0025 | 0.0050 | -1.724890e-02 | 6.2754e-04 | 1.5547e-03 | 11.0949 | **13.7931** | 3.4483 | . | . |
| 2 | 0.0050 | 0.0075 | -8.799123e-03 | 3.8148e-04 | 1.1410e-03 | 7.7120 | **10.1186** | 2.5297 | . | . |
| 3 | 0.0075 | 0.0100 | -5.633880e-03 | 6.9603e-04 | 1.0143e-03 | 5.5546 | **9.4417** | 2.3604 | . | . |
| 4 | 0.0100 | 0.0150 | -5.990999e-03 | 7.8665e-04 | 1.1385e-03 | 5.2622 | **9.1692** | 2.2923 | . | . |
| 5 | 0.0150 | 0.0200 | -2.284679e-03 | 3.1546e-04 | 1.2233e-03 | 1.8676 | **3.9526** | 0.9881 | . | . |
| 6 | 0.0200 | 0.0300 | -1.958899e-03 | 7.9207e-04 | 1.1575e-03 | 1.6923 | **5.5711** | 1.3928 | . | . |
| 7 | 0.0300 | 0.0500 | -7.310213e-04 | 5.8763e-04 | 9.5154e-04 | 0.7682 | **4.3664** | 1.0916 | . | Y |
| 8 | 0.0500 | 0.1000 | -7.136934e-04 | 4.3284e-04 | 7.9842e-04 | 0.8939 | **4.1746** | 1.0437 | . | Y |
| 9 | 0.1000 | 0.2500 | -4.691926e-04 | 8.3715e-04 | 9.1500e-04 | 0.5128 | **5.3619** | 1.3405 | . | Y |
| 10 | 0.2500 | 0.5000 | +2.375219e-04 | 5.3670e-04 | 1.0854e-03 | 0.0000 | **2.8615** | 0.7154 | **Y** | Y |
| 11 | 0.5000 | 1.0000 | +1.245590e-03 | 5.7361e-04 | 1.3565e-03 | 0.0000 | **1.8608** | 0.4652 | **Y** | Y |

**Post-injection `Delta_i(c) = Delta_i + c*SE_diff(t_i)` at every `c` of the frozen grid** (`FIRE` marks `stat_i(c) > t_crit`, equivalently `c_min(i) <= c`):

| i | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 0 | -3.9397e-02 | -3.8320e-02 | -3.7243e-02 | -3.6166e-02 | -3.5089e-02 | -3.2935e-02 | -3.0781e-02 | -2.6473e-02 | -2.2165e-02 | -1.3550e-02 | -4.9338e-03 |
| 1 | -1.7249e-02 | -1.5694e-02 | -1.4140e-02 | -1.2585e-02 | -1.1030e-02 | -7.9209e-03 | -4.8116e-03 | +1.4071e-03 | +7.6258e-03 **FIRE** | +2.0063e-02 **FIRE** | +3.2500e-02 **FIRE** |
| 2 | -8.7991e-03 | -7.6582e-03 | -6.5172e-03 | -5.3762e-03 | -4.2353e-03 | -1.9533e-03 | +3.2862e-04 | +4.8925e-03 **FIRE** | +9.4564e-03 **FIRE** | +1.8584e-02 **FIRE** | +2.7712e-02 **FIRE** |
| 3 | -5.6339e-03 | -4.6196e-03 | -3.6054e-03 | -2.5911e-03 | -1.5768e-03 | +4.5170e-04 | +2.4802e-03 | +6.5373e-03 **FIRE** | +1.0594e-02 **FIRE** | +1.8708e-02 **FIRE** | +2.6823e-02 **FIRE** |
| 4 | -5.9910e-03 | -4.8525e-03 | -3.7140e-03 | -2.5755e-03 | -1.4370e-03 | +8.3994e-04 | +3.1169e-03 | +7.6709e-03 **FIRE** | +1.2225e-02 **FIRE** | +2.1333e-02 **FIRE** | +3.0441e-02 **FIRE** |
| 5 | -2.2847e-03 | -1.0614e-03 | +1.6192e-04 | +1.3852e-03 | +2.6085e-03 **FIRE** | +5.0551e-03 **FIRE** | +7.5017e-03 **FIRE** | +1.2395e-02 **FIRE** | +1.7288e-02 **FIRE** | +2.7075e-02 **FIRE** | +3.6861e-02 **FIRE** |
| 6 | -1.9589e-03 | -8.0135e-04 | +3.5620e-04 | +1.5137e-03 | +2.6713e-03 | +4.9864e-03 **FIRE** | +7.3015e-03 **FIRE** | +1.1932e-02 **FIRE** | +1.6562e-02 **FIRE** | +2.5822e-02 **FIRE** | +3.5083e-02 **FIRE** |
| 7 | -7.3102e-04 | +2.2052e-04 | +1.1721e-03 | +2.1236e-03 | +3.0751e-03 | +4.9782e-03 **FIRE** | +6.8813e-03 **FIRE** | +1.0687e-02 **FIRE** | +1.4494e-02 **FIRE** | +2.2106e-02 **FIRE** | +2.9718e-02 **FIRE** |
| 8 | -7.1369e-04 | +8.4730e-05 | +8.8315e-04 | +1.6816e-03 | +2.4800e-03 | +4.0768e-03 **FIRE** | +5.6737e-03 **FIRE** | +8.8674e-03 **FIRE** | +1.2061e-02 **FIRE** | +1.8448e-02 **FIRE** | +2.4836e-02 **FIRE** |
| 9 | -4.6919e-04 | +4.4581e-04 | +1.3608e-03 | +2.2758e-03 | +3.1908e-03 | +5.0208e-03 **FIRE** | +6.8508e-03 **FIRE** | +1.0511e-02 **FIRE** | +1.4171e-02 **FIRE** | +2.1491e-02 **FIRE** | +2.8811e-02 **FIRE** |
| 10 | +2.3752e-04 | +1.3229e-03 | +2.4083e-03 | +3.4937e-03 **FIRE** | +4.5791e-03 **FIRE** | +6.7499e-03 **FIRE** | +8.9207e-03 **FIRE** | +1.3262e-02 **FIRE** | +1.7604e-02 **FIRE** | +2.6287e-02 **FIRE** | +3.4970e-02 **FIRE** |
| 11 | +1.2456e-03 | +2.6021e-03 | +3.9587e-03 **FIRE** | +5.3152e-03 **FIRE** | +6.6717e-03 **FIRE** | +9.3848e-03 **FIRE** | +1.2098e-02 **FIRE** | +1.7524e-02 **FIRE** | +2.2950e-02 **FIRE** | +3.3803e-02 **FIRE** | +4.4655e-02 **FIRE** |

| n_fire(c) | c=0 | c=1 | c=2 | c=3 | c=4 | c=6 | c=8 | c=12 | c=16 | c=24 | c=32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **all 12 steps** | 0 | 0 | 1 | 2 | 3 | 7 | 7 | 10 | 11 | 11 | 11 |
| excluding already-increasing steps | 0 | 0 | 0 | 0 | 1 | 5 | 5 | 8 | 9 | 9 | 9 |

* steps with `Delta_i > 0` in the raw data (NC-B3): **2 of 12**, at indices `[10, 11]`
* `c_min(i) > c_pos(i)` at every step of this cell: **True**
* `c_min` min / median / max: 1.8608 / 5.4665 / 42.1581 — in gate-width units `c_min/4`: 0.4652 / 1.3666 / 10.5395
* the two `n_fire` definitions (`#{i : c_min(i) <= c}` and `stat_i(c) > t_crit`) agree at every `c`: **True**

---

## 5. The closed-form guarantee `c_min(i) > c_pos(i)`, verified at all 48 steps

At `c = c_min(i)` the post-injection `Delta` equals `epsilon_i + t_crit*SE_step(i)`, strictly positive whenever `SE_diff(t_i) > 0` and `SE_step(i) > 0`. Hence every firing the AM-3 gate can produce sits on a **genuinely positive post-injection `Delta`**: the gate cannot be made to fire on a step that is still decreasing. This is the exact converse of the BATCH-a44d08 defect, and it is repaired by removing the selection, not by weakening the gate.

```
steps total                                    : 48
degenerate, excluded                           : 0
steps checked                                  : 48
steps satisfying c_min(i) > c_pos(i)           : 48
HOLDS AT ALL CHECKED STEPS                     : True
violations                                     : []
min margin  c_min - c_pos  over the 48         : 1.8607641914511006
min post-injection Delta at c = c_min over 48  : 0.0024147884953880493
all post-injection Deltas at c_min positive    : True
identity |Delta(c_min) - (eps + t_crit*SE_step)| max : 5.204170427930421e-18
```

A violation here would be an **implementation error, not a finding** (prereg 3.2). There was none.

**Implementation check of the closed forms** (NOT a control, NOT a result, NOT an alternative rule — it computes the same frozen quantities two ways):

```
max |stat_closed_form - stat_direct_injection|   = 6.892264536872972e-13
max |Delta_closed_form - Delta_direct|           = 3.3306690738754696e-16
step first fires exactly at c_min at every step  = True
t_crit literal vs scipy t.ppf(0.998, 7) agree    = True  (4.2071245566046755)
alpha per step recomputed (sf)                   = 0.0019999999999982102  declared 0.002
union bound recomputed                           = 0.096  declared 0.096
```

---

## 6. PRED-B1, scored at a FIXED `c = 6`

> ### PRED-B1 (frozen): `n_fire(cell, c=6) >= 4` in EVERY one of the four cells.
> Threshold unit: a COUNT OF STEPS out of 12. Falsifier: any cell with `n_fire(c=6) <= 3`.

| cell | n_fire(c=6), all 12 steps | vs threshold 4 | n_fire(c=6) EXCLUDING already-increasing steps |
|---|---|---|---|
| `d100_b30` | **6** | MET | 3 |
| `d100_b40` | **7** | MET | 5 |
| `d140_b30` | **9** | MET | 7 |
| `d140_b40` | **7** | MET | 5 |

**Outcome: PRED-B1 MET.**

This is the scoring of a frozen prediction against this run's own recomputation. It is an OBSERVATION. It is **not** a conclusion that AM-3 is adequate, validated, or refuted, and it does not retire AM-3. That judgement belongs to the Reviewer and the Coordinator.

**Provenance of the threshold, stated so it cannot be mistaken for a carried result.** The Red Team's REVIEW MEASUREMENT reports the identical injection firing at `c <= 6` at `6, 7, 9, 7` of the 12 steps in the four cells [quoted: red_team_report.md 2.2]. AM-6 forbids citing that as a rescoring; it set a prior only, and `4` was chosen strictly below all four quoted values so PRED-B1 is a genuine two-sided claim about THIS run's own recomputation. **Observation, recorded because it is unexpected in its exactness:** this run's independent recomputation returned 6, 7, 9, 7 — the same four counts. This is reported as an observation about this run and confers nothing on the review measurement.

### 6.1 Power curve — pooled over the 48 steps, and per cell

| c | 0 | 1 | 2 | 3 | 4 | 6 | 8 | 12 | 16 | 24 | 32 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| **pooled n_fire, all 48 steps** | 0 | 0 | 1 | 11 | 16 | 29 | 34 | 39 | 42 | 45 | 46 |
| pooled n_fire, excluding already-increasing steps | 0 | 0 | 0 | 3 | 7 | 20 | 25 | 30 | 33 | 36 | 37 |
| `d100_b30`, all 12 | 0 | 0 | 0 | 2 | 4 | 6 | 8 | 10 | 11 | 12 | 12 |
| `d100_b40`, all 12 | 0 | 0 | 0 | 4 | 5 | 7 | 9 | 9 | 10 | 11 | 11 |
| `d140_b30`, all 12 | 0 | 0 | 0 | 3 | 4 | 9 | 10 | 10 | 10 | 11 | 12 |
| `d140_b40`, all 12 | 0 | 0 | 1 | 2 | 3 | 7 | 7 | 10 | 11 | 11 | 11 |

### 6.2 `c_min/4` — the firing amplitude in the design's OWN gate-width units

`c_min(i)` is FINITE at every non-degenerate step by construction, so "the gate fires at SOME `c`" is VACUOUS and is not the headline. `c_min(i)/4` states the firing amplitude in units of the design's own `4.0 * SE_diff` gate width, so a reader can see directly whether the firing amplitude is inside or outside the range the design calls detectable.

| cell | min c_min/4 | median c_min/4 | max c_min/4 |
|---|---|---|---|
| `d100_b30` | 0.5077 | 1.5165 | 5.8530 |
| `d100_b40` | 0.5643 | 1.2920 | 8.0287 |
| `d140_b30` | 0.7138 | 1.1220 | 7.5643 |
| `d140_b40` | 0.4652 | 1.3666 | 10.5395 |

---

## 7. Can the AM-3 gate fire — stated PLAINLY, and SEPARATELY from whether it DID fire in BATCH-a44d08

> ### CAN IT FIRE?
> The AM-3 gate CAN fire: at the fixed injection c = 6 it fires at 29 of the 48 non-degenerate steps pooled over the four cells, and every one of those firings sits on a strictly positive post-injection Delta by the verified closed-form guarantee c_min(i) > c_pos(i).

> ### DID IT FIRE IN BATCH-a44d08? — A DIFFERENT QUESTION.
> SEPARATELY, and this is a different statement: in BATCH-a44d08 the gate DID NOT fire. Its positive control selected steps by argmax SE_diff(A, t_i) -- the injection's own denominator -- and at c = 6 the post-injection Delta was still NEGATIVE, so no monotonicity violation of any size was ever presented to it. Its frozen INADMISSIBLE verdict stands as the output of its frozen rule on its frozen data and is NOT rescored here.

**These are two different statements.** Whether the gate CAN fire is a property of the gate. Whether it DID fire in BATCH-a44d08 is a property of that run's step selection. The first does not reinstate the second's readings, and BATCH-a44d08's four PARTIAL cell readings stay WITHHELD.

Answered by the frozen criterion `n_fire(pooled, c=6) > 0` (prereg 3.5): `n_fire(pooled, c=6) = 29` of 48 non-degenerate steps.

---

## 8. Negative controls (mandatory, prereg 3.6)

### NC-B1 — `c = 0`, the un-injected family

A gate that fires without an injection is broken.

```
violations of 48                          : 0   (required: 0)
max AM-3 statistic over the family        : -0.19342160540508713
committed value [quoted: MR-B1]           : -0.19342160540508713
abs deviation from the committed value    : 0.0
PASSES                                    : True
```

Per-cell max un-injected AM-3 statistic: `{'d100_b30': -0.6547233602577552, 'd100_b40': -1.269112253920602, 'd140_b30': -1.1441268888776548, 'd140_b40': -0.19342160540508713}`. The family maximum reproduces the committed `AM3-TIE` maximum EXACTLY (deviation `0.0`), in the cell `d140_b40` the committed record names.

### NC-B2 — `c = -6`, a NEGATIVE injection

A gate that fires on a reinforced decrease is broken.

```
violations of 48                          : 0   (required: 0)
max AM-3 statistic over the family        : -8.211428539209706
PASSES                                    : True
```

### NC-B3 — steps already increasing in the raw data, FLAGGED

At a step with `Delta_i > 0` a small `c` fires partly on a PRE-EXISTING INCREASE rather than on the injection. Every such step is flagged in the 48-step tables above (`Delta>0?` column) and `n_fire` is reported BOTH ways.

```
steps with Delta_i > 0, this run           : 9 of 48
committed [quoted: MR-B1]                  : 9
agrees                                     : True
n_fire(pooled, c=6) WITH them              : 29
n_fire(pooled, c=6) WITHOUT them           : 20
```

Per cell: `{'d100_b30': [8, 9, 10], 'd100_b40': [10, 11], 'd140_b30': [9, 10], 'd140_b40': [10, 11]}`.

> ### AN OBSERVATION THAT DOES NOT FLATTER THE PREDICTION, RECORDED AS REQUIRED.
> PRED-B1 is FROZEN and is scored on the FULL table (prereg 3.6), and on the full table it is met in all four cells. **With the already-increasing steps excluded, cell `d100_b30` falls to 3, which is below PRED-B1's threshold of 4.** The other three cells stay at 5, 7, 5. This is reported, not smoothed. It is NOT a rescoring of PRED-B1 against a different rule — the frozen prediction is not adjusted after the fact and completed runs are not re-scored — and it is exactly the number prereg 3.6 requires to be printed beside the headline so a reader can weigh it.

**Instrument-limited: False.** Neither NC-B1 nor NC-B2 failed, so the power statements above are not withheld on that ground.

---

## 9. Realized false-failure behaviour against the rate the pre-registration declared

**Declared before any datum existed:**

```
per-step alpha                                        : 0.002
family                                                : 12 steps x 4 cells = 48 comparisons
family-wise false-failure rate, flawless instrument   : 0.096
basis                                                 : union bound 48 x 0.002 = 0.096, valid under ANY dependence; steps sharing an endpoint are dependent
Sidak reference (NOT the declared rate)               : 0.0916233087376801
```

**Realized on this run:**

```
comparisons scored                                    : 48
degenerate, excluded                                  : 0
step VIOLATIONS, un-injected (c = 0)                  : 0
steps with Delta_i > 0                                : 9
max AM-3 statistic over the family, un-injected       : -0.19342160540508713
```

**Reading discipline (carried, and binding on this report).** The declared 0.096 is an UPPER BOUND on P(at least one VIOLATION | flawless instrument). The realized count above is what the 48 frozen comparisons returned on this run's un-injected data. A REALIZED COUNT IS NOT AN ESTIMATE OF A RATE: one run yields one Bernoulli draw of the family-wise event, and the observed count bounds nothing about the instrument unless the instrument is flawless in the sense above. Reported, not interpreted. Whether the instrument is flawless is not something this run can establish and is not claimed.

**Separately — the `4.0 * SE_diff` gate is a DIFFERENT object** from the AM-3 `t_crit` criterion. The 4.0 * SE_diff gate that defines SE_diff is a DIFFERENT object from the AM-3 t_crit criterion. Its realized one-sided false-positive rate was measured at 0.0015-0.0025 against a nominal 3e-5 [quoted: BATCH-f19c37 validation_report.yaml item 4 / V-5]. That is a quoted review measurement, not a result of this run.

---

## 10. Uncertainty on `c_min` — quantification, NOT selection (prereg 3.7)

Bootstrap: resample the 8 DRAW INDICES **jointly** across every `t` and the Haar null, `B = 20000`, `default_rng([9, d, beta, 0])`. **This is UNCERTAINTY QUANTIFICATION on a reported quantity. It is not a selection rule and no verdict is taken from it** — that distinction is exactly what BATCH-a44d08's argmax lottery got wrong, and repeating the bootstrap while keeping a selection would repeat it. The frozen headline PRED-B1 is scored on the POINT ESTIMATES of the full 48-step table.

### `d100_b30`

| i | c_min (point) | fraction of B with c_min <= 6 | 2.5% | 50% | 97.5% |
|---|---|---|---|---|---|
| 0 | 23.4119 | 0.0000 | 21.0309 | 23.8906 | 51.1077 |
| 1 | 13.6555 | 0.0000 | 12.4340 | 14.2963 | 20.8933 |
| 2 | 10.5496 | 0.0000 | 8.9628 | 10.9729 | 15.3913 |
| 3 | 7.5652 | 0.0008 | 6.5133 | 7.9300 | 10.2088 |
| 4 | 9.9739 | 0.0000 | 8.9407 | 10.3279 | 14.3911 |
| 5 | 7.2644 | 0.0300 | 5.9563 | 7.5428 | 9.6854 |
| 6 | 4.8674 | 0.8077 | 3.0350 | 4.9928 | 8.6135 |
| 7 | 4.3635 | 0.8477 | 2.4978 | 4.4270 | 8.2667 |
| 8 | 2.0308 | 0.9998 | 0.3738 | 2.0350 | 3.2386 |
| 9 | 3.6284 | 0.9982 | 2.1989 | 3.5632 | 4.6932 |
| 10 | 2.8582 | 0.9890 | 1.6902 | 2.7929 | 5.1647 |
| 11 | 3.9769 | 0.9954 | 1.9821 | 3.9601 | 5.4704 |

(no bootstrap replicate was degenerate: 0 of 240000 step-replicates)

### `d100_b40`

| i | c_min (point) | fraction of B with c_min <= 6 | 2.5% | 50% | 97.5% |
|---|---|---|---|---|---|
| 0 | 32.1148 | 0.0000 | 26.4307 | 33.7276 | 53.6823 |
| 1 | 16.3542 | 0.0000 | 14.9955 | 17.2057 | 22.9265 |
| 2 | 12.3472 | 0.0000 | 10.4058 | 12.7859 | 17.3503 |
| 3 | 6.6918 | 0.0437 | 5.8776 | 6.9435 | 10.5256 |
| 4 | 7.0403 | 0.0873 | 5.4772 | 7.4287 | 11.8531 |
| 5 | 5.2813 | 0.7605 | 4.3972 | 5.3926 | 7.4570 |
| 6 | 5.0545 | 0.7594 | 4.0006 | 5.2363 | 7.3892 |
| 7 | 2.6760 | 0.9998 | 2.0343 | 2.7187 | 3.8149 |
| 8 | 2.7152 | 0.9999 | 1.8724 | 2.7758 | 4.2710 |
| 9 | 3.3008 | 0.9920 | 1.7887 | 3.3799 | 5.2748 |
| 10 | 2.2573 | 1.0000 | 1.2188 | 2.2629 | 3.1067 |
| 11 | 2.6906 | 0.9996 | 1.1379 | 2.6599 | 4.3094 |

(no bootstrap replicate was degenerate: 0 of 240000 step-replicates)

### `d140_b30`

| i | c_min (point) | fraction of B with c_min <= 6 | 2.5% | 50% | 97.5% |
|---|---|---|---|---|---|
| 0 | 30.2572 | 0.0000 | 25.3969 | 31.7668 | 47.7832 |
| 1 | 16.1219 | 0.0000 | 13.6542 | 16.9671 | 24.1184 |
| 2 | 7.9228 | 0.0095 | 6.2726 | 8.2398 | 13.4759 |
| 3 | 5.9914 | 0.4263 | 4.4269 | 6.2226 | 11.0331 |
| 4 | 5.6116 | 0.5844 | 4.1204 | 5.7259 | 11.7100 |
| 5 | 3.7647 | 0.8823 | 3.0634 | 3.8316 | 8.9577 |
| 6 | 4.6781 | 0.8780 | 3.9028 | 4.7770 | 8.0222 |
| 7 | 4.2975 | 0.9212 | 3.3367 | 4.3818 | 7.3671 |
| 8 | 4.1020 | 0.8777 | 2.8062 | 4.1724 | 8.5965 |
| 9 | 2.8842 | 0.9997 | 1.8206 | 2.8958 | 3.7183 |
| 10 | 2.8553 | 1.0000 | 1.9007 | 2.8114 | 3.8737 |
| 11 | 2.8669 | 0.9952 | 1.9042 | 2.8774 | 4.8293 |

(no bootstrap replicate was degenerate: 0 of 240000 step-replicates)

### `d140_b40`

| i | c_min (point) | fraction of B with c_min <= 6 | 2.5% | 50% | 97.5% |
|---|---|---|---|---|---|
| 0 | 42.1581 | 0.0000 | 35.4499 | 44.6935 | 65.5850 |
| 1 | 13.7931 | 0.0000 | 12.3372 | 14.3867 | 23.5161 |
| 2 | 10.1186 | 0.0000 | 9.2556 | 10.5168 | 14.1174 |
| 3 | 9.4417 | 0.0001 | 7.5022 | 9.7382 | 14.1218 |
| 4 | 9.1692 | 0.0000 | 7.3079 | 9.4678 | 16.3232 |
| 5 | 3.9526 | 0.9897 | 2.9894 | 4.0881 | 5.6480 |
| 6 | 5.5711 | 0.6747 | 4.3149 | 5.6914 | 7.6227 |
| 7 | 4.3664 | 0.9859 | 3.3609 | 4.3882 | 5.6578 |
| 8 | 4.1746 | 0.9069 | 2.5795 | 4.2455 | 7.6956 |
| 9 | 5.3619 | 0.6764 | 3.2109 | 5.3970 | 7.9769 |
| 10 | 2.8615 | 0.9996 | 1.8829 | 2.8129 | 3.7806 |
| 11 | 1.8608 | 0.9999 | 0.4365 | 1.8333 | 3.2252 |

(no bootstrap replicate was degenerate: 0 of 240000 step-replicates)

---

## 11. The could-not-fail arrangement, named in BOTH directions

BATCH-a44d08's pre-registration named two could-not-fail forms, BOTH of the shape 'a gate too lenient to fire', and did NOT name the mirror, 'a positive control that cannot pass' -- which is the one it ran in. Both directions are named here. THE SECOND IS THE ONE THAT ACTUALLY HAPPENED.

### Direction 1 — A GATE TOO LENIENT TO FIRE (the gate could not fail)

A gate so lenient, or a headline so loose, that it fires regardless. Reporting c_min with an unbounded c axis makes 'the gate fires at SOME c' TRUE AT EVERY NON-DEGENERATE STEP BY CONSTRUCTION, since c_min(i) is finite whenever SE_diff(t_i) > 0. A headline of that shape is VACUOUS.

*Guards, declared in advance, with their realized values:*

* **The frozen headline is a COUNT at a FIXED `c`**, not "fires at some `c`": `PRED-B1: n_fire(cell, c=6) >= 4 of 12 in EVERY cell`. Realized per cell: `{'d100_b30': 6, 'd100_b40': 7, 'd140_b30': 9, 'd140_b40': 7}`. A cell where every `c_min` exceeded 6 would have falsified it.
* **`c_min/4` in gate-width units** is reported at every step (§6.2), so the firing amplitude is legible against the design's own detectability range.
* **NC-B1 and NC-B2**: a gate that fires with no injection, or on a reinforced decrease, is broken. Realized: 0 and 0 violations of 48 respectively.

### Direction 2 — A CONTROL THAT CANNOT PASS

> ### **THIS IS THE ONE THAT ACTUALLY HAPPENED.**

A positive control whose step selection places the injection where the injection cannot create the condition the gate tests. Then 'the gate is INADMISSIBLE' is a property of the selection rule, not a finding about the gate.

BATCH-a44d08 ran in exactly this arrangement. Its rule chose i = argmax_i SE_diff(A, t_i) over the 12 lower endpoints -- the injection's OWN denominator -- which is largest at the head of the descent where |Delta_i| is 11x to 26x the injection unit. At c = 6 the post-injection Delta was still NEGATIVE in three of four cells, so NO monotonicity violation of any size was ever presented to the gate, and a monotonicity gate declining to flag a net DECREASE is behaving CORRECTLY [quoted: validation_report.yaml item d; red_team_report.md section 2.3]. The INADMISSIBLE verdict was procedurally correct and says NOTHING about whether the gate CAN fire.

BATCH-a44d08's pre-registration named two could-not-fail forms, **both of the shape "a gate too lenient to fire"**, and did not name this mirror. That omission is why the defect was invisible to its own contract: every guard it carried pointed the other way.

*Guards against Direction 2, declared in advance, with their realized values:*

* **(a) `c_pos(i)` printed at every step** — the step's own REALITY threshold sits on the page beside its firing threshold. Realized: printed at all 48 steps; per-cell max `c_pos` = `{'d100_b30': 18.685118342693983, 'd100_b40': 26.035969043967146, 'd140_b30': 25.696970807353118, 'd140_b40': 36.58119440167787}`.
* **(b) the closed-form relation `c_min(i) > c_pos(i)` verified numerically at all 48** — every firing PROVABLY sits on a positive post-injection `Delta`. Realized: holds at 48/48, min margin `1.8607641914511006`, min post-injection `Delta` at `c_min` `0.0024147884953880493` (strictly positive).
* **(c) there is NO step selection at all** — no rule can place the control where the injection cannot create the condition. Realized: all 12 steps of all 4 cells scored and reported; no `argmax` over any `SE` quantity exists in the script.

### Direction 3 — the control could pass TRIVIALLY (the step was already increasing)

At a step with Delta_i > 0 the gate can fire on the PRE-EXISTING INCREASE rather than on the injection. *Guard:* NC-B3 flags every such step and n_fire is reported BOTH with and without them; PRED-B1 is scored on the full table with the flagged count printed beside it.

Realized: 9 already-increasing steps of 48; `n_fire(pooled, c=6)` = 29 WITH them and 20 WITHOUT them. Per cell with: `{'d100_b30': 6, 'd100_b40': 7, 'd140_b30': 9, 'd140_b40': 7}`; without: `{'d100_b30': 3, 'd100_b40': 5, 'd140_b30': 7, 'd140_b40': 5}`. See the recorded observation in §8 (NC-B3).

### Direction 4 — the reproduction could hide a defect

If the regenerated family silently differs from the committed one, c_min is computed on a DIFFERENT OBJECT than the one BATCH-a44d08 scored. *Guard:* prereg 3.5's reproduction floor, re-verified BEFORE any scoring, with the expected one-ULP d = 140 deviation declared in advance and explicitly forbidden from being rounded to 0.0.

Realized: max `|dev|` on `r` = `0.0` against the committed `results_g3.json` and `2.220446049250313e-16` against BATCH-f19c37; max `|d c_min|` = `0.0` c units; admissible = True.

### The residue I cannot close

This run measures the POWER of one positive control on one recorded graded family at four cells, n = 8 draws, N = 2^20. A demonstration that a gate CAN fire at an INJECTED violation is NOT a demonstration that it fires at a REAL one. Nothing here establishes that AM-3 is adequate.

---

## 12. Binding carries — repeated here as each section's report must

* **`AM3_is_not_retired`** — AM-3 IS NOT RETIRED and is NOT on trial for its life here. Its 0.096 family-wise false-failure bound is correctly derived, was declared before any datum existed, and is mechanically free of every run-supplied quantity. Its POWER is UNDEMONSTRATED, not disproved [carried: prereg 1.3 item 1 / 3.1 item 1].
* **`a_firing_finding_does_not_reinstate_BATCH_a44d08`** — A FINDING THAT THE GATE CAN FIRE DOES NOT REINSTATE BATCH-a44d08'S READINGS. Its frozen INADMISSIBLE verdict stands as the output of its frozen rule on its frozen data and is NOT rescored here. Its four PARTIAL cell readings stay WITHHELD and are not lifted out [carried: prereg 3.1 item 2].
* **`section_C_proposition_open_both_directions`** — Section C's proposition -- whether D depends on the frame only through V at the 2^-10 quantile -- stays OPEN IN BOTH DIRECTIONS. Nothing from BATCH-a44d08's Section C is cited here, as a baseline, as a prior, or at all [carried: prereg 1.3 item 2].
* **`claim_tier`** — TOY, unconditionally. No number here is transported to beta = 606, d = 1420, to any FIPS 203 parameter set, to any attack cost, or to any other parameter set, by extrapolation or by analogy.
* **`infrastructure_rule`** — Budget exhaustion, timeout, crash or a missing dependency is INFRASTRUCTURE SIGNAL and is NEVER negative mathematical evidence (AGENTS.md rule 3). gmpy2 is ABSENT in this environment and nothing here depends on it.

---

## 13. Protocol deviations, anomalies, and infrastructure events

Recorded in full; none is discarded.

| id | class | what happened | consequence |
|---|---|---|---|
| **D-3** | `implementation_error`, cosmetic, non-load-bearing | The script obtained the notarizing commit's metadata with `subprocess.run(..., shell=True)` on a format string containing `%H|%ci|%s`. The shell interpreted `|` as a pipe, so the recorded `notarizing_commit_metadata` field in `results_g3.json` is the EMPTY STRING. | **No verification depended on this field.** The sha256, the blob comparison and the `merge-base` ancestry assertion are all separate calls and all returned correctly. The metadata was obtained independently at the shell and is quoted in §1.1. Recorded rather than repaired, because the run record is immutable and the budget is one run. |
| **A-1** | `infrastructure`, benign | The shared worktree's `HEAD` advanced between the start of this task and the run, from `c32b4b5d` to `ed5cc287d54991480c23629b5ed477bb194dfa4c`, by a concurrent Coordinator working GOAL-MCE-001 (BATCH-a68f79) — a different goal. | The notarizing commit `4f7c63703d50445c758fc6216ca8d4436e04ae2a` remained an ancestor of `HEAD` throughout, re-checked after the run. No artifact of this task was touched. Recorded because a moving `HEAD` is exactly the condition under which an ancestry assertion can silently become stale. |
| **A-2** | `observation`, unexpected in its exactness | This run's independent recomputation of `n_fire(c=6)` returned 6, 7, 9, 7, identical to the Red Team's quoted `6, 7, 9, 7`; and the S1 medians 3.98 / 2.72 / 3.76 / 4.17 match the quoted plateau medians `3.98 / 2.72 / 3.76 / 4.17` to rounding. | Reported as an observation about THIS run. It is not a reproduction of the review measurement, not a rescoring, and confers nothing on BATCH-a44d08. |
| **A-3** | `observation`, does not flatter the prediction | Excluding the already-increasing steps, `d100_b30` falls to 3 at `c = 6`, below PRED-B1's threshold of 4. | Reported in §8 beside the headline exactly as prereg 3.6 requires. PRED-B1 is frozen and is scored on the full table; it is NOT re-scored against this number. |

**No other deviation.** No threshold was re-derived, no grid point was added, removed or re-spaced, no alternative rule was computed and presented beside a frozen verdict, and the frozen prediction was not adjusted. The wording ban was observed: no arm is described as "absent", "no departure", "vanishes" or "consistent with zero"; every zero count is reported as an UPPER BOUND at its declared floor.

---

## 14. Budget and environment

```
wall clock     : 66.59 s of 5400.0 s budget
cpu core-sec   : 29.74
peak RSS       : 1.322 GB of 4.0 GB budget
runs           : 1 of 1 (maximum_runs = 1); no rerun, no discarded attempt
```

Per-stage wall seconds: `{'arms_d100_b30_wall_seconds': 6.47, 'arms_d100_b40_wall_seconds': 15.26, 'arms_d140_b30_wall_seconds': 24.03, 'arms_d140_b40_wall_seconds': 14.5, 'stage1_arms_wall_seconds': 62.59, 'stage2_reproduction_wall_seconds': 0.03, 'stage4_closed_forms_wall_seconds': 0.0, 'stage9_cmin_repro_wall_seconds': 0.0, 'stage10_bootstrap_wall_seconds': 0.16}`

```
python  : 3.13.1 (v3.13.1:06714517797, Dec  3 2024, 14:00:22) [Clang 15.0.0 (clang-1500.3.9.4)]
platform: macOS-26.6-arm64-arm-64bit-Mach-O  (arm64)
numpy   : 2.4.0
scipy   : 1.15.3
fpylll  : PRESENT but NOT USED by this run (no BKZ, no LLL)
gmpy2   : ABSENT (declared; nothing here depends on it)
BLAS threads pinned to 1: {'OMP_NUM_THREADS': '1', 'OPENBLAS_NUM_THREADS': '1', 'MKL_NUM_THREADS': '1', 'VECLIB_MAXIMUM_THREADS': '1', 'NUMEXPR_NUM_THREADS': '1', 'ACCELERATE_MAX_THREADS': None}
```

Budget exhaustion, timeout, crash or a missing dependency would be INFRASTRUCTURE SIGNAL and NEVER negative mathematical evidence (`AGENTS.md` rule 3). None occurred: the run terminated normally, well inside both caps.

---

## 15. What this measurement does NOT reach

**Scope of what was measured:** the POWER of one positive control on one recorded graded family at four cells (d in {100,140}, beta in {30,40}), n = 8 draws, N = 2^20, q = 3329, CBD_{eta=2}.

It does not:

* license anything about lattices in either direction
* rescore BATCH-a44d08, whose frozen INADMISSIBLE verdict stands
* reinstate any withheld BATCH-a44d08 reading; the four PARTIAL cell readings stay WITHHELD
* retire AM-3, which is NOT retired and NOT on trial for its life here
* establish that the AM-3 gate is adequate -- a demonstration that a gate CAN fire at an injected violation is not a demonstration that it fires at a real one
* offer any verdict as an AM-4 adjudication of a claim about a lattice
* cite anything from BATCH-a44d08's Section C, whose proposition stays OPEN IN BOTH DIRECTIONS
* bear on ML-KEM security, any FIPS 203 parameter set, any attack cost, or any cost model

INADMISSIBLE, INVALID and PARTIAL are INSTRUMENT outcomes [carried]. Every '0 violations' remains an UPPER BOUND at the declared floor, never an absence.

**A demonstration that a gate CAN fire at an INJECTED violation is not a demonstration that it fires at a REAL one.** Nothing here establishes that AM-3 is adequate, and nothing here retires it.

---

## 16. Artifacts

All four inside the task's write scope `coordination/goals/GOAL-MLKEM-005/batches/BATCH-cbe023/tasks/TASK-20260808-cece0c/`:

| artifact | role |
|---|---|
| `measure_g3.py` | the measurement, gated on the notarized pre-registration |
| `results_g3.json` | raw machine-readable results, every step, every `c` |
| `report_g3.md` | this report |
| `run_manifest.yaml` | the run record, `AGENTS.md` artifact policy fields |
| `command.txt` | the exact command, with BLAS pinning |
| `stdout.log` / `stderr.log` | captured streams; `stderr` holds only `/usr/bin/time -l` resource accounting |

No git write, no commit, and no push was performed by this task. The run package becomes durable only after the Coordinator's snapshot archive is pushed to a branch with an open PR.
