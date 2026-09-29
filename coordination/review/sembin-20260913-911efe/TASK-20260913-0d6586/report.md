# TASK-20260913-0d6586 — joints K1 and K2

Validator report for review round `REVIEW-SEMBIN-20260913-911efe`.
Joints owned: **K1**, **K2**. Not a verdict on H-SEMBIN-83a856, on any
degree, or on any curve's security.

Snapshot reviewed: producer package `RUN-SEMBIN-8be036` as archived by
`TASK-20260913-e39bfe` in commit `e7a7f6ddb` (ancestor of `HEAD`). Source
counts: `RUN-SEMBIN-1b9afe/per-R-counts.json` (180 configurations, committed).

K1 sequencing was respected: both N1 integers and the offending pairs below
were computed from `binary_field.modulus_for`, this task's own trace loop, and
`per-R-counts.json` **before** any path under `experiments/EXP-SEMBIN-911efe/runs/`
or `experiments/EXP-SEMBIN-911efe/code/` was opened.

---

## K1 — THE INTEGER (computed first)

**N1 (i)** = **16**  
Definition: low_degree_polynomial, even n, both sides, each side with its own
`a`, `pi(R) = Tr(x_R) + Tr(a) != m·Tr(a) (mod 2)`, and a nonzero count in
`single_x_multiset` **or** `chained_x_multiset`.

**N1 (ii)** = **0**  
Definition: the same (configuration, side, target) set, `usable_point_multiset`
nonzero.

Empty-class targets scanned: 79751. Reachable-class targets: 80249.
Even-n low_degree configurations: 40. Trace cross-check vs `GF2m.trace` on 28
probe elements: agree.

### Offending pairs for (i) — all sixteen; (ii) has none

Each row is `(configuration, side, target-index)`. All sixteen have
`usable_point_multiset = 0`. All are twist side, `a = 512`, `Tr(a) = 1`,
`m = 6` so `m·Tr(a) = 0`, `pi = 1` (the predicted-empty class), `Tr(x_R) = 0`.

| # | configuration | side | idx | R_x | single | chained | usable | outside |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913201 | T | 578 | 1120 | 1 | 1 | 0 | 2 |
| 2 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913201 | T | 643 | 1120 | 1 | 1 | 0 | 2 |
| 3 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913201 | T | 1733 | 2301 | 1 | 1 | 0 | 2 |
| 4 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913202 | T | 1195 | 2301 | 1 | 1 | 0 | 2 |
| 5 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913202 | T | 1359 | 3334 | 4 | 4 | 0 | 8 |
| 6 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913202 | T | 1975 | 3334 | 4 | 4 | 0 | 8 |
| 7 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913203 | T | 126 | 3334 | 4 | 4 | 0 | 8 |
| 8 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913203 | T | 424 | 3334 | 4 | 4 | 0 | 8 |
| 9 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913203 | T | 919 | 3334 | 4 | 4 | 0 | 8 |
| 10 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913203 | T | 1180 | 1120 | 1 | 1 | 0 | 2 |
| 11 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913203 | T | 1558 | 3334 | 4 | 4 | 0 | 8 |
| 12 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913203 | T | 1874 | 2301 | 1 | 1 | 0 | 2 |
| 13 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913204 | T | 550 | 3334 | 4 | 4 | 0 | 8 |
| 14 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913204 | T | 583 | 1120 | 1 | 1 | 0 | 2 |
| 15 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913204 | T | 1289 | 3334 | 4 | 4 | 0 | 8 |
| 16 | n12-m6-t6-k2-low_degree_polynomial-B_eq_1-s20260913205 | T | 1540 | 1120 | 1 | 1 | 0 | 2 |

N1 (i) at every even-n low_degree `t = 2` cell: **0**. N1 (ii) everywhere in
the even-n low_degree slice: **0**.

### Twist-side `a` (from source construction, not the producer)

`yield_run.py` fixes `a = 0` on E. `CellContext` builds the twist with
`twist_a(field, a) = a xor delta`, `delta` = smallest element of absolute
trace 1 (`fastfield.twist_a`, same delta as `QuadraticExtension`). This
task's own trace under `modulus_for(n)`:

| n | modulus | delta = a_T | Tr(a_E) | Tr(a_T) |
| --- | --- | --- | --- | --- |
| 12 | 0x1009 | **512** | 0 | 1 |
| 20 | 0x100009 | 131072 | 0 | 1 |
| 22 | 0x400003 | 2097152 | 0 | 1 |
| 24 | 0x100001b | 2097152 | 0 | 1 |

At n = 12, m = 6 (even): confined parity `m·Tr(a_T) = 0`, so the predicted-empty
class is `pi = 1`. The sixteen pairs are exactly that class. `a = 512` is the
twist's `a`, not E's.

### Pair-for-pair with the producer (opened after the integers above)

Producer `parity-split.json` / `raw-result.json`: N1 = 16, the same sixteen
`(label, side, target_index)` keys, same `R_x`, `a = 512`, `Tr(a) = 1`,
`pi = 1`, `m·Tr(a) = 0`, `count` matching `single_x_multiset`. All sixteen
usable counts are 0. No extra pair, no missing pair.

**The sixteen pairs the producer reports are a contract-wording defect:** the
frozen N1 counts a nonzero x-multiset in either presentation, and those columns
include algebraic solutions whose y-coordinates lie in F_{q^2} \ F_q, while
the theorem is about usable F_q-rational decompositions, of which these sixteen
have none.

Not a theorem defect (usable is identically 0 on the predicted-empty class).
Not a run defect (the pairs recompute from the committed source columns and the
source field).

**K1: holds.** Deciding artifact: this task's `scratch/k1_n1_pass1.json`
(N1 (i) = 16 with the sixteen pairs above; N1 (ii) = 0) together with
`parity-split.json` `offending_pairs` agreeing pair-for-pair, and twist
`a_T = 512`, `Tr(a_T) = 1`.

---

## K2 — THE SHAPE AND THE CONTROLS

Presentation scored: E-side `usable_point_multiset` (the column of the original
deficit table). T-side usable is identically 0 at every t = 2 cell in this
archive, for both subspace variants; K2's Poisson-shape claims are therefore
scored on E. Bootstrap: 2500 replicates, seed 20260913, percentile 95%
intervals, `var` with `ddof=1`. Cell-grain (n pooled over B) intervals used
8000 replicates.

A printed-table excerpt of
`coordination/review/sembin-20260913-run2/TASK-20260913-31d530/report.md`
(the 12-box reconstruction table only) was read for the reconstruction control.
Independently recomputed E usable pooled-over-5-seeds mean, hit fraction and
f_dispersion match that table at printed precision for all 12 boxes.

### Per-configuration (low_degree, E, t = 2): reachable-class D and mean vs 2×pooled

Reachable class on E is `pi = 0` (`a = 0`, m even). Predicted-empty class
`pi = 1` has **zero** usable hits on every one of these 30 configurations.

| configuration | n_reach | mean | D | D 95% CI | CI contains 1 | mean / (2 pooled) CI contains 1 |
| --- | --- | --- | --- | --- | --- | --- |
| n20 B=1 s201 | 1002 | 0.900 | 1.063 | [0.974, 1.155] | yes | yes |
| n20 B=1 s202 | 1005 | 0.931 | 0.982 | [0.899, 1.069] | yes | yes |
| n20 B=1 s203 | 1004 | 0.880 | 0.899 | [0.821, 0.975] | **no** | yes |
| n20 B=1 s204 | 961 | 0.888 | 1.026 | [0.935, 1.116] | yes | yes |
| n20 B=1 s205 | 1024 | 0.912 | 0.969 | [0.894, 1.045] | yes | yes |
| n20 randB s201 | 993 | 1.010 | 0.990 | [0.911, 1.074] | yes | yes |
| n20 randB s202 | 1019 | 1.027 | 0.984 | [0.913, 1.053] | yes | yes |
| n20 randB s203 | 984 | 1.029 | 0.982 | [0.909, 1.061] | yes | yes |
| n20 randB s204 | 973 | 0.958 | 0.979 | [0.896, 1.067] | yes | yes |
| n20 randB s205 | 1024 | 0.984 | 0.947 | [0.874, 1.016] | yes | yes |
| n22 B=1 s201 | 1001 | 1.014 | 1.120 | [1.018, 1.216] | **no** | yes |
| n22 B=1 s202 | 1027 | 1.043 | 0.993 | [0.907, 1.087] | yes | yes |
| n22 B=1 s203 | 996 | 1.006 | 1.003 | [0.925, 1.082] | yes | yes |
| n22 B=1 s204 | 997 | 0.945 | 1.001 | [0.924, 1.076] | yes | yes |
| n22 B=1 s205 | 992 | 1.033 | 1.090 | [0.989, 1.189] | yes | yes |
| n22 randB s201 | 1037 | 1.079 | 0.982 | [0.901, 1.065] | yes | yes |
| n22 randB s202 | 998 | 1.003 | 0.997 | [0.913, 1.082] | yes | yes |
| n22 randB s203 | 1029 | 0.992 | 0.914 | [0.843, 0.983] | **no** | yes |
| n22 randB s204 | 1019 | 0.935 | 0.958 | [0.884, 1.038] | yes | yes |
| n22 randB s205 | 1032 | 1.036 | 0.975 | [0.880, 1.078] | yes | yes |
| n24 B=1 s201 | 993 | 1.003 | 0.998 | [0.914, 1.083] | yes | yes |
| n24 B=1 s202 | 977 | 1.002 | 1.037 | [0.945, 1.129] | yes | yes |
| n24 B=1 s203 | 997 | 1.002 | 1.022 | [0.928, 1.126] | yes | yes |
| n24 B=1 s204 | 988 | 0.964 | 0.960 | [0.876, 1.051] | yes | yes |
| n24 B=1 s205 | 1029 | 0.934 | 1.085 | [0.976, 1.204] | yes | yes |
| n24 randB s201 | 995 | 1.030 | 1.028 | [0.938, 1.121] | yes | yes |
| n24 randB s202 | 1000 | 0.970 | 1.143 | [1.045, 1.248] | **no** | yes |
| n24 randB s203 | 1001 | 0.983 | 0.981 | [0.903, 1.070] | yes | yes |
| n24 randB s204 | 1005 | 1.044 | 1.017 | [0.927, 1.110] | yes | yes |
| n24 randB s205 | 988 | 0.937 | 0.960 | [0.883, 1.030] | yes | yes |

Four of 30 configuration CIs exclude 1. Under exact 95% coverage that is not
an extreme count (binomial tail on 30 × 0.05). Every configuration's reachable
mean / (2 × pooled mean) interval contains 1. Predicted-empty usable is 0 on
all 30.

### Per-(n, B) boxes (5 seeds pooled) and the three cells (B pooled)

E usable, low_degree, t = 2.

| n | B | n_reach | mean_reach | 2×pooled | D_reach | D 95% CI | contains 1 | D_pooled | 1+λ | D−(1+λ) CI contains 0 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | B=1 | 4996 | 0.90252 | 0.9018 | 0.987 | [0.950, 1.025] | yes | 1.439 | 1.451 | yes |
| 20 | rand | 4993 | 1.00200 | 1.0006 | 0.976 | [0.944, 1.010] | yes | 1.478 | 1.500 | yes |
| 22 | B=1 | 5013 | 1.00838 | 1.0110 | 1.042 | [1.001, 1.083] | **no** | 1.545 | 1.506 | yes |
| 22 | rand | 5115 | 1.00938 | 1.0326 | 0.967 | [0.930, 1.005] | yes | 1.460 | 1.516 | **no** (below) |
| 24 | B=1 | 4984 | 0.98054 | 0.9774 | 1.020 | [0.978, 1.064] | yes | 1.512 | 1.489 | yes |
| 24 | rand | 4989 | 0.99298 | 0.9908 | 1.027 | [0.988, 1.066] | yes | 1.525 | 1.495 | yes |

The named grain in the specification and in the breaking artifact is the
**cell** `(n, m, t, k)`, with B an independent variable inside it. Pooling both
B modes (8000-replicate bootstrap):

| n | n_reach | D_reach | D 95% CI | contains 1 | D_pooled | 1+λ | D−(1+λ) CI contains 0 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20 | 9989 | 0.984 | [0.958, 1.010] | yes | 1.461 | 1.476 | yes |
| 22 | 10128 | 1.004 | [0.977, 1.033] | yes | 1.502 | 1.511 | yes |
| 24 | 9973 | 1.024 | [0.995, 1.053] | yes | 1.518 | 1.492 | yes |

At cell grain, every Tr = 0 class D interval contains 1, and every pooled
D − (1+λ) interval contains 0. The (n = 22, B = 1) box's 95% interval
[1.001, 1.083] excludes 1 (Poisson-SE z = 2.10 against D = 1). That is
disclosed; it is not a miss at the three cells. Pooled D is not outside its
interval around 1+λ at all three cells in the same direction (the n = 22
random_B box is *below* 1+λ; the n = 22 B = 1 box is slightly above; cell-grain
all contain 0).

Tr = 0 mean vs 2 × pooled mean: all six (n, B) ratio CIs contain 1; the
largest mean offset is n = 22 random_B (1.009 vs 1.033), still inside the
ratio interval.

### Proves-too-much: random_k_dimensional at the same three cells

On **E**, both pi classes are populated at every (n, B) box. Class means are of
the same order (example: n = 20 B = 1, pi0 mean 0.507 vs pi1 mean 0.521;
n_nonzero 2050 vs 1995). Per-class D is in [0.980, 1.016] with CIs containing 1.
Pooled D is 0.986–1.012, against 1+λ ≈ 1.49–1.52 — i.e. the mixture signature
is **absent**, as required of a V not confined. No empty or depleted pi class
on E.

On **T**, usable is identically 0 at t = 2 for *both* random V and low-degree V.
That is not a pi-split artifact: both classes are empty of usable
decompositions. The failure signature is an empty or depleted pi class produced
by the split; a uniformly zero usable column on the twist at these cells does
not distinguish pi.

### Known-false splits (rerun here)

LSB of `R_x`, and `Tr` under the second irreducible of the same degree (same
search order as `binary_field._find_modulus`, skipping `modulus_for(n)`).
Primary vs alt at n = 20: 1048585 vs 1048609, matching the producer's example.

Neither split produced an empty class (no split class with zero targets) on any
t = 2 configuration, either subspace, either side. Producer
`known_false_empty_class: false` agrees.

Example, n = 20 B = 1 seed 20260913201 E usable: LSB class means 0.452 / 0.450
(n = 991 / 1009); alt-mod class means 0.450 / 0.452. Both classes nonempty.
Pooled over-dispersion persists inside each known-false class (D ≈ 1.44–1.59),
as required.

### Odd-n cells (P4)

From the run's own logs and counts, not from a sampling flag:

- stdout: `|V|^t = 4194304` (n = 21, k = 11, t = 2 = 2^22) and
  `|V|^t = 16777216` (n = 23, k = 12, t = 2 = 2^24).
- `partial/p4.json`: `reached_exhaustively: true` on both cells; `unreached: []`.
- `odd-n-per-R-counts.json`: 8 configurations, 2000 targets per side; usable
  counts are integers; V basis length = k (low_degree `{1,2,4,...,2^{k-1}}`).
- Code path: `yield_run.run_config(..., draws=2000)` → `solve_for_target` at
  t = 2, which walks every factor-base 1-prefix and looks up the completing
  point (exhaustive over the factor-base pairs, i.e. over V^2 as used by
  the source machinery). R is drawn (2000), which is the declared 354a75
  procedure; V^2 is not sampled. Wall 2.1–4.4 s per config is consistent with
  exhaustive t = 2 lookup, not with walking all of E(F_{2^n}).

E-side f_dispersion, recomputed here: 0.98500–1.01545 across the eight
configs (producer table 0.985–1.015). Both pi classes are hit on E. `Tr(1) = 1`
at both odd n, so 1 ∈ V is not in ker(Tr). T-side usable is 0 on all eight
(same t = 2 twist pattern as the source cells).

### K2 verdict

**K2: holds.** Deciding artifacts: the per-configuration and per-cell tables
in `independent-figures.json` (reachable D interval contains 1 at each of
the three even-n cells; reachable mean / (2 × pooled) intervals contain 1;
pooled D − (1+λ) intervals contain 0 at cell grain; random-V E both classes
populated; LSB and second-irreducible splits rerun with no empty class;
odd-n `|V|^t` logs plus 2000-row integer per-R counts showing exhaustive t = 2
enumeration).

Limitation, not a break of the named cell grain: the (n = 22, B = 1) box
reachable-class D 95% interval [1.001, 1.083] excludes 1 (z = 2.10). The
Coordinator's mind-changing condition named "any cell"; at (n, m, t, k) that
interval contains 1. T-side usable is zero at t = 2 in this archive, so twist
shape is untestable here.

---

## Receipt integrity (not a joint)

- Required artifacts present under `runs/RUN-SEMBIN-8be036/`. Declared
  sha256 in `artifact-digests.json` match the files (25/25).
- Copied `binary_field.py`, `yield_core.py`, `yield_run.py` sha256-equal the
  EXP-SEMBIN-354a75 sources.
- Command, seeds, environment, wall 234.1 s, peak RSS 0.310 GB recorded.
  Manifest `status: completed_valid`. `dirty: true` at wrap-up; the snapshot
  commit `e7a7f6ddb` is the durable receipt.
- Reconstruction control: passed (this task recomputed the 12 boxes).
- Algebraic selftest: six cases `equal: true` in `raw-result.json`.
- Matched-null per-R: unavailable, as declared; not substituted.
- P5: untestable (sizes, not membership). Not scored here (not K1/K2).

---

## Joints (only)

| joint | verdict | deciding artifact |
| --- | --- | --- |
| K1 | **holds** | `scratch/k1_n1_pass1.json`: N1 (i)=16 same sixteen pairs, N1 (ii)=0; twist a_T=512 Tr=1; `parity-split.json` agrees pair-for-pair |
| K2 | **holds** | `independent-figures.json` cell-grain intervals and rerun controls |

The sixteen pairs are a **contract-wording defect**.

```yaml
validation_report:
  task_id: TASK-20260913-0d6586
  review_round_id: REVIEW-SEMBIN-20260913-911efe
  run_ids: [RUN-SEMBIN-8be036]
  joints:
    K1: holds
    K2: holds
  artifact_checks:
    - path: experiments/EXP-SEMBIN-911efe/runs/RUN-SEMBIN-8be036/
      snapshot_commit: e7a7f6ddb
      hash_match_vs_artifact-digests: true
      working_tree_only: false
  metric_recomputations:
    - N1_i: 16
    - N1_ii: 0
    - producer_N1: 16
    - keys_equal: true
  control_checks:
    - reconstruction_12_boxes: passed
    - known_false_empty_class: false (rerun)
    - random_V_E_no_depleted_pi_class: passed
    - odd_n_V2_enumerated_not_sampled: passed
  heuristic_validation_checks: []
  cost_model_checks: []
  proof_architecture_checks: []
  verdict: passed
  limitations:
    - n22_B_eq_1_reachable_D_95pct_CI_excludes_1_at_the_(n,B)_box
    - T_side_usable_identically_zero_at_t2_so_twist_shape_unscored
    - matched_null_per_R_unavailable
  artifact_paths:
    - coordination/review/sembin-20260913-911efe/TASK-20260913-0d6586/report.md
    - coordination/review/sembin-20260913-911efe/TASK-20260913-0d6586/attestation.yaml
    - coordination/review/sembin-20260913-911efe/TASK-20260913-0d6586/independent-figures.json
    - coordination/review/sembin-20260913-911efe/TASK-20260913-0d6586/validation_report.yaml
```
