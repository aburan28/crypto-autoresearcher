# EXP-MTBK-306bdb continuation notes (2026-08-06)

Purpose: continue the harness exploration for a valid std-vs-BKK divergence
under the same protocol and control assumptions.

Executed sweeps (all using the corrected harness logic in
`experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py`):

- `RUN-MTBK-20-seed-sweep1-30`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20.yaml --out-root experiments/EXP-MTBK-306bdb --run-suffix 20-seed-sweep1-30 --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --skip-rho`
  - Observed: only 30 cells were active because frozen 20-bit fixture contains seeds 1..5.
  - Outcome: 0 mismatches (`K_star_std == K_star_bkk` for all cells).

- Direct in-memory sweep (no frozen artifact, 16-bit):
  - Script variant: seeds 1..200, m∈{3,4,5}, b∈{0.6,0.7}, target_count=50, cap=20,000.
  - Outcome: 1200 cells, 0 mismatches; all cells had K* pair `(1,1)`.

- Direct in-memory sweep (no frozen artifact, 16-bit high arity):
  - Script variant: seeds 1..100, m∈{6,7,8}, b∈{0.6,0.7}, target_count=20, cap=20,000.
  - Outcome: 600 cells, 0 mismatches; all cells had K* pair `(1,1)`.

- Direct distribution audit (16-bit):
  - Script variant: seeds 1..50, m∈{3,4,5}, b∈{0.6,0.7}, target_count=50, cap=20,000.
  - Outcome: 300 cells, distribution `Counter({(1,1): 300})`.

- Out-of-protocol sensitivity run:
  - Script variant: seeds 1..200, m=3, b=0.3, target_count=50, cap=20,000 (16-bit).
  - Outcome: 200 cells with 171 mismatches; diverse finite and `inf` K* values.
  - Interpretation: indicates sensitivity when the factor-base exponent is pushed far
    below approved protocol (exploratory only, not a breakthrough for current target).

- `RUN-MTBK-16-b30-seed1-5-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-b30-1-30.yaml --run-suffix 16-b30-seed1-5-norho --seeds 1,2,3,4,5 --cell-ms 3,4,5 --b-exps 0.3,0.6 --skip-rho`
  - Outcome: 30 cells. `b=0.6` all `(1,1)` (ratio 1.0); `b=0.3` mixed outcomes, with
    11 cells where `K*`_bkk > `K*`_std and occasional high finite ratios.

- `RUN-MTBK-16-b30-seed1-30-b03-only-norho`
  - Command: same fixture, seeds 1..30, `--b-exps 0.3`, `--skip-rho`.
  - Outcome: 90 cells. 72 cells had `K*`_bkk > `K*`_std. Median finite K*-ratio=3.0.
    No stable BKK speedup on first-success K* despite lower check counts.

- `RUN-MTBK-16-b30-seed1-30-b06-only-norho`
  - Command: same fixture, seeds 1..30, `--b-exps 0.6`, `--skip-rho`.
  - Outcome: 90 cells. All K* pairs equal; ratio samples all 1.0.

- `RUN-MTBK-20-b30-seed1-5-b03-only-norho`
  - Fixture: `frozen-instances-20-b30-1-5.yaml` (20-bit, seeds 1..5, b=0.3/0.6).
  - Outcome: 15 cells. `b=0.3` yielded mostly `K*`_bkk > `K*`_std (one inf/edge case).
    Median finite K*-ratio ~2.25.

- `RUN-MTBK-20-b30-seed1-5-b06-only-norho`
  - Command: same 20-bit fixture, `--b-exps 0.6`, `--skip-rho`.
  - Outcome: 15 cells, all equal K* (ratio 1.0).

- `RUN-MTBK-16-b35-seed1-30-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-b35-1-30.yaml --run-suffix 16-b35-seed1-30-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 3,4,5 --b-exps 0.35 --skip-rho`
  - Outcome: 90 cells. 1 cell had `K*_bkk` lower (`1 < 2`) but with higher checks in both channels; no practical advantage.

- `RUN-MTBK-16-b40-seed1-30-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-b40-50-1-30.yaml --run-suffix 16-b40-seed1-30-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 3,4,5 --b-exps 0.4,0.5 --skip-rho`
  - Outcome: 90 cells (`b=0.4,0.5`), all `K*` equal (mostly `(1,1)`).

- `RUN-MTBK-16-b50-seed1-30-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-b40-50-1-30.yaml --run-suffix 16-b50-seed1-30-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 3,4,5 --b-exps 0.5 --skip-rho`
  - Outcome: 90 cells, all `K*` equal `(1,1)`.

- `RUN-MTBK-16-bscan-25-28-33-37-m678-b25-only`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-bscan-25-28-33-37.yaml --run-suffix 16-bscan-25-28-33-37-m678-b25-only --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 6,7,8 --b-exps 0.25 --skip-rho`
  - Outcome: 90 cells. `K*` counts: `lt=3`, `gt=79`, `eq=8`, and 0 non-worse-check cells. `ratio_median=6.0` (driven by `K*` mismatches against std with higher costs).

- `RUN-MTBK-20-b30-seed1-5-m678-b03-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-b30-1-5.yaml --run-suffix 20-b30-seed1-5-m678-b03-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5 --cell-ms 6,7,8 --b-exps 0.3 --skip-rho`
  - Outcome: 15 cells. `lt=2`, `gt=11`, `eq=2`, with no candidate cell improving checks.

- `RUN-MTBK-16-lowb-1-30-m678-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-lowb-1-30.yaml --run-suffix 16-lowb-1-30-m678-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 6,7,8 --b-exps 0.2,0.22,0.24 --skip-rho`
  - Outcome: 270 cells, `lt=6`, `gt=254`, `eq=10`.
  - Practical filter (non-timeout in descent for both channels) yielded 0 candidate improvements (`impr=0`).
  - All 6 `lt` cells had at least one descent timeout; no reproducible `K_star_bkk < K_star_std` with control-safe checks.
  - `ratio_median=5.67`, ratio_samples=174.

- `RUN-MTBK-16-lowb-1-30-m9-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-lowb-1-30.yaml --run-suffix 16-lowb-1-30-m9-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 9 --b-exps 0.2,0.22,0.24 --skip-rho`
  - Outcome: 90 cells, `lt=3`, `gt=83`, `eq=4`.
  - Practical filter (non-timeout in descent for both channels) yielded 0 candidate improvements (`impr=0`).
  - All 3 `lt` cells had descent timeouts in std and/or bkk channels.
  - `ratio_median=4.80`, ratio_samples=67.

- `RUN-MTBK-16-lowb-18-1-30-m678-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-lowb-18-1-30.yaml --run-suffix 16-lowb-18-1-30-m678-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 6,7,8 --b-exps 0.15,0.18 --skip-rho`
  - Outcome: 180 cells, `lt=0`, `gt=97`, `eq=83`.
  - Practical filter (non-timeout in descent for both channels) yielded 0 candidate improvements (`impr=0`).
  - `ratio_median=2.4286`, ratio_samples=7.

- `RUN-MTBK-16-lowb-1-30-m10-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-lowb-1-30.yaml --run-suffix 16-lowb-1-30-m10-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 10 --b-exps 0.2,0.22,0.24 --skip-rho`
  - Outcome: 90 cells, `lt=2`, `gt=81`, `eq=7`.
  - Practical filter (non-timeout in descent for both channels) yielded 0 candidate improvements (`impr=0`).
  - `ratio_median=8.00`, ratio_samples=56.

- `RUN-MTBK-16-lowb-14-1-30-m678-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-16-lowb-14-1-30.yaml --run-suffix 16-lowb-14-1-30-m678-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30 --cell-ms 6,7,8 --b-exps 0.12,0.14 --skip-rho`
  - Outcome: 180 cells, `lt=0`, `gt=72`, `eq=108`.
  - Practical filter (non-timeout in descent for both channels) yielded 0 candidate improvements (`impr=0`).
  - `ratio_median=None`, ratio_samples=0.

- `RUN-MTBK-20-lowb-1-5-m610-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-1-5.yaml --run-suffix 20-lowb-1-5-m610-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5 --cell-ms 6,7,8,9,10 --b-exps 0.12,0.14,0.15,0.18,0.2,0.22,0.24 --skip-rho`
  - Outcome: 175 cells, `lt=6`, `gt=60`, `eq=109`.
  - Practical filter (non-timeout in descent for both channels) yielded 0 candidate improvements (`impr=0`).
  - All 6 `lt` cells had descent timeouts in std and/or bkk channels.
  - `ratio_median=1.50`, ratio_samples=15.

- `RUN-MTBK-20-lowb-1-5-b24-m610-cap100k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-1-5.yaml --run-suffix 20-lowb-1-5-b24-m610-cap100k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5 --cell-ms 6,7,8,9,10 --b-exps 0.24 --check-cap-std 100000 --check-cap-bkk 100000 --skip-rho`
  - Outcome: 25 cells, `lt=4`, `gt=20`, `eq=1`.
  - Practical filter (non-timeout in descent for both channels) yielded 0 candidate improvements (`impr=0`).
  - All 4 `lt` cells had descent timeouts in std and/or bkk channels.
  - `ratio_median=1.50`, ratio_samples=13.

### 2026-08-06 continuation extension (seeds 1..15 on low-b frontier)

- `frozen-instances-20-lowb-1-15.yaml`
  - Generated from field-20 seeds 1..15 for `b ∈ {0.12,0.14,0.15,0.18,0.2,0.22,0.24}`, target_count=50, and deterministic factor/base generation.
  - Added split helpers:
    - `frozen-instances-20-lowb-6-10.yaml` (seeds 6..10)
    - `frozen-instances-20-lowb-11-15.yaml` (seeds 11..15)
  - Verification:
    - `RUN-MTBK-20-lowb-6-10-verify`: 5 cells (`m=6,b=0.2`) passed material checks.
    - `RUN-MTBK-20-lowb-11-15-verify`: 5 cells (`m=6,b=0.2`) passed material checks.
  - `RUN-MTBK-20-lowb-1-15-verify` (single smoke command over the merged fixture): passed verification.

- `RUN-MTBK-20-lowb-6-10-b24-m10-cap100k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-6-10.yaml --run-suffix 20-lowb-6-10-b24-m10-cap100k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 6,7,8,9,10 --cell-ms 10 --b-exps 0.24 --check-cap-std 100000 --check-cap-bkk 100000 --skip-rho`
  - Outcome: 5 cells, `lt=0`, `gt=5`, `eq=0`, `impr=0`.

- `RUN-MTBK-20-lowb-11-15-b24-m10-cap100k-norho`
  - Command: same as above with `6..10` replaced by `11..15`.
  - Outcome: 5 cells, `lt=1`, `gt=3`, `eq=1`, `impr=0`.
  - The single `lt` was timeout-affected (`unsafe_lt=1`), so no safe practical improvement.

- `RUN-MTBK-20-lowb-6-10-b24-m10-cap500k-norho`
  - Command: same as above with `--check-cap-std 500000 --check-cap-bkk 500000`.
  - Outcome: 5 cells, `lt=0`, `gt=5`, `eq=0`, `impr=0`.

- `RUN-MTBK-20-lowb-11-15-b24-m10-cap500k-norho`
  - Command: same as above with seeds `11..15`.
  - Outcome: 5 cells, `lt=0`, `gt=2`, `eq=3`, `impr=0`.

- `RUN-MTBK-20-lowb-6-10-b24-m610-cap100k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-6-10.yaml --run-suffix 20-lowb-6-10-b24-m610-cap100k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 6,7,8,9,10 --cell-ms 6,7,8,9,10 --b-exps 0.24 --check-cap-std 100000 --check-cap-bkk 100000 --skip-rho`
  - Outcome: 25 cells, `lt=1`, `gt=24`, `eq=0`, `impr=0`.
  - The single `lt` was timeout-affected (`unsafe_lt=1`).
  - `ratio_median=5.0`, ratio_samples=25.

- `RUN-MTBK-20-lowb-11-15-b24-m610-cap100k-norho`
  - Command: same as above with `11..15`.
  - Outcome: 25 cells, `lt=1`, `gt=17`, `eq=7`, `impr=0`.
  - The single `lt` was timeout-affected (`unsafe_lt=1`).
  - `ratio_median=3.5`, ratio_samples=24.

Combined 20-lowb m610 `b=0.24`, `cap=100k` over seeds 1..15:
- `lt=6`, `gt=61`, `eq=8`, `impr=0`.
- 10/25/26? timeout-safe `lt` remained `0` (all `lt` cells had timeout involvement in at least one channel).

Conclusion (continuation status): still no protocol-valid breakthrough; no safe `K_star_bkk < K_star_std` evidence under the tested 20-bit low-b extensions.

### 2026-08-06 high-cap hotspot follow-up (timeout clearance checks, b=0.24, m610 family)

To test whether the remaining `lt` cells were artifacts of `check_cap=100k`, I ran focused
single-/small-cell sweeps with `--check-cap-std 500000 --check-cap-bkk 500000`:

- `RUN-MTBK-20-lowb-3-m6-b24-cap500k-norho`
- `RUN-MTBK-20-lowb-4-m10-b24-cap500k-norho`
- `RUN-MTBK-20-lowb-5-m7-b24-cap500k-norho`
- `RUN-MTBK-20-lowb-5-m8-b24-cap500k-norho`
- `RUN-MTBK-20-lowb-10-m6-b24-cap500k-norho`
- `RUN-MTBK-20-lowb-11-m10-b24-cap500k-norho`

Observed 6 hotspot cells:

- `seed=3,m=6,b=0.24`: `K*std=4`, `K*bkk=11`, `ratio=2.75` (`impr=0`).
- `seed=4,m=10,b=0.24`: `K*std=3`, `K*bkk=10`, `ratio=3.333...` (`impr=0`).
- `seed=5,m=7,b=0.24`: `K*std=2`, `K*bkk=8`, `ratio=4.0` (`impr=0`).
- `seed=5,m=8,b=0.24`: `K*std=2`, `K*bkk=5`, `ratio=2.5` (`impr=0`).
- `seed=10,m=6,b=0.24`: `K*std=3`, `K*bkk=3`, `ratio=1.0` (`impr=0`).
- `seed=11,m=10,b=0.24`: `K*std=1`, `K*bkk=1`, `ratio=1.0` (`impr=0`).

All six runs completed validly; none show protocol-safe `K_star_bkk < K_star_std`.
Notably, two previously timeout-involved `lt` cells at `cap=100k`
(`seed=3,m=6,b=0.24` and `seed=4,m=10,b=0.24`) flipped to `std`-better outcomes at higher cap.

Status: all additional high-cap checks still support `impr=0`; no breakthrough signal emerged on low-b frontier at 20-bit depth.

### 2026-08-06 lower-b hotspot follow-up (`b=0.18/0.22`, `m=8`)

To clear two prior low-cap outliers outside `b=0.24`, I ran:

- `RUN-MTBK-20-lowb-3-5-b18-22-m8-cap500k-norho`

Observed outcomes:

- `seed=3,m=8,b=0.18`: `K*std=23`, `K*bkk=40`, `ratio=1.739...` (`impr=0`)
- `seed=3,m=8,b=0.22`: `K*std=4`, `K*bkk=25`, `ratio=6.25` (`impr=0`)
- `seed=5,m=8,b=0.18`: `K*std=6`, `K*bkk=inf`, `ratio=inf` (`impr=0`)
- `seed=5,m=8,b=0.22`: `K*std=2`, `K*bkk=6`, `ratio=3.0` (`impr=0`)

All cells are non-improving under high-cap checks (`100k`-triggered timeout concerns did not hide protocol-safe improvements at `cap=500k`).

### 2026-08-06 high-cap completion (`m610`, `b=0.24`, `cap=500k`, remaining seeds)

- `RUN-MTBK-20-lowb-11-15-b24-m610-cap500k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-11-15.yaml --run-suffix 20-lowb-11-15-b24-m610-cap500k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 11,12,13,14,15 --cell-ms 6,7,8,9,10 --b-exps 0.24 --check-cap-std 500000 --check-cap-bkk 500000 --skip-rho`
  - Outcome: `25` cells, `lt=0`, `gt=17`, `eq=8`, `safe_lt=0`, `unsafe_lt=0`.
  - Median finite ratio: `ratio_median=4.0` (25 samples).

Combined `cap=500k`, `m=6,7,8,9,10`, `b=0.24` over seeds `6..15`:

- `RUN-MTBK-20-lowb-6-10-b24-m610-cap500k-norho`: `lt=0`, `gt=24`, `eq=1`, `safe_lt=0`.
- `RUN-MTBK-20-lowb-11-15-b24-m610-cap500k-norho`: `lt=0`, `gt=17`, `eq=8`, `safe_lt=0`.
- Combined: `n_total=50`, `n_lt=0`, `n_eq=9`, `n_better_safe=0`.

Conclusion: across the completed high-cap window of seeds `6..15`, no protocol-safe improvement appears (`K_star_bkk < K_star_std` never holds), consistent with timeout-only artifacts at lower cap.

### `RUN-MTBK-20-lowb-1-5-b24-m610-cap500k-norho` (final seeds tranche)

I completed the last missing tranche in the same high-cap condition:

- Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-1-5.yaml --run-suffix 20-lowb-1-5-b24-m610-cap500k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5 --cell-ms 6,7,8,9,10 --b-exps 0.24 --check-cap-std 500000 --check-cap-bkk 500000 --skip-rho`
- Outcome: `25` cells, `lt=1`, `gt=24`, `eq=0`, `safe_lt=0`, `unsafe_lt=1`.
- The single `lt` cell was unsafe under timing controls (`m=10`, `seed=3`, `K*std=4`, `K*bkk=1`, `ratio=0.25`) due timeout involvement in the same channel pair.

Full `20-lowb` m610 high-cap (`m={6,7,8,9,10}`, `b=0.24`, `cap=500k`) tranche over seeds `1..15` now complete:

- `n_total=75`, `n_lt=1`, `n_eq=9`, `n_gt=65`.
- `n_safe_lt=0` (all lt observations are timeout-compromised and `unsafe`).

Conclusion update: the full high-cap `m610,b=0.24` low-b 20-bit sweep over seeds `1..15` remains protocol-negative (`K_star_bkk < K_star_std` with no timeout-safe channel control is still 0 cells).

### `RUN-MTBK-20-lowb-1-15-b22-m610-cap500k-norho`

Expanded high-cap coverage to the neighboring `b=0.22` setting:

- Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-1-15.yaml --run-suffix 20-lowb-1-15-b22-m610-cap500k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15 --cell-ms 6,7,8,9,10 --b-exps 0.22 --check-cap-std 500000 --check-cap-bkk 500000 --skip-rho`
- Outcome: `75` cells, `lt=0`, `eq=4`, `gt=71`, `safe_lt=0`, `unsafe_lt=0`.

Thus, `b=0.22` also shows no protocol-safe low-b improvement at high cap under this `m610` slice.

### 2026-08-06 continuation: full `b=0.2` high-cap sweep (`m610`, `cap=500k`, seeds `1..15`)

To close the final `b=0.2` frontier under the high-cap control:

- `RUN-MTBK-20-lowb-1-5-b20-m610-cap500k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-1-5.yaml --run-suffix 20-lowb-1-5-b20-m610-cap500k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5 --cell-ms 6,7,8,9,10 --b-exps 0.2 --check-cap-std 500000 --check-cap-bkk 500000 --skip-rho`
  - Outcome: `25` cells, `lt=0`, `eq=1`, `gt=24`, `safe_lt=0`, `unsafe_lt=0`.

- `RUN-MTBK-20-lowb-6-10-b20-m610-cap500k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-6-10.yaml --run-suffix 20-lowb-6-10-b20-m610-cap500k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 6,7,8,9,10 --cell-ms 6,7,8,9,10 --b-exps 0.2 --check-cap-std 500000 --check-cap-bkk 500000 --skip-rho`
  - Outcome: `25` cells, `lt=0`, `eq=0`, `gt=25`, `safe_lt=0`, `unsafe_lt=0`.

- `RUN-MTBK-20-lowb-11-15-b20-m610-cap500k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-11-15.yaml --run-suffix 20-lowb-11-15-b20-m610-cap500k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 11,12,13,14,15 --cell-ms 6,7,8,9,10 --b-exps 0.2 --check-cap-std 500000 --check-cap-bkk 500000 --skip-rho`
  - Outcome: `25` cells, `lt=1`, `eq=0`, `gt=24`, `safe_lt=0`, `unsafe_lt=1`.
  - The single `lt` cell (`seed=14,m=8`) was timeout-affected (`std` descent timed out at the bkk-improving index `K*=4`), so it is protocol-unsafe.

Combined full `b=0.2`, `m610`, `cap=500k` sweep over seeds `1..15`:

- `n_total=75`, `n_lt=1`, `n_eq=1`, `n_gt=73`.
- `n_safe_lt=0`, `n_unsafe_lt=1`.
- No protocol-safe improvements (`K_star_bkk < K_star_std`).
 
Conclusion: `b=0.2` remains protocol-negative under the same `m610`, timeout-hardened high-cap protocol checks; no safe candidate improvement emerged across all 75 cells.

### 2026-08-07 continuation: full `b=0.15` `m610` high-cap-comparison sweep (`check_cap=100k`)

To close whether low-b `b=0.15` had timeout-only artifacts, I completed three disjoint seed-tranche sweeps:

- `RUN-MTBK-20-lowb-1-5-b15-m610-cap100k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-1-5.yaml --run-suffix 20-lowb-1-5-b15-m610-cap100k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 1,2,3,4,5 --cell-ms 6,7,8,9,10 --b-exps 0.15 --check-cap-std 100000 --check-cap-bkk 100000 --skip-rho`
  - Outcome: `25` cells, `lt=0`, `eq=24`, `gt=1`, `safe_lt=0`, `unsafe_lt=0`.
  - `ratio_median=--` (`ratio_samples=0`).

- `RUN-MTBK-20-lowb-6-10-b15-m610-cap100k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-6-10.yaml --run-suffix 20-lowb-6-10-b15-m610-cap100k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 6,7,8,9,10 --cell-ms 6,7,8,9,10 --b-exps 0.15 --check-cap-std 100000 --check-cap-bkk 100000 --skip-rho`
  - Outcome: `25` cells, `lt=0`, `eq=16`, `gt=9`, `safe_lt=0`, `unsafe_lt=0`.
  - `ratio_median=1.0` (`ratio_samples=2`).

- `RUN-MTBK-20-lowb-11-15-b15-m610-cap100k-norho`
  - Command: `python3 experiments/EXP-MTBK-306bdb/code/run_mtbk_full.py --frozen experiments/EXP-MTBK-306bdb/frozen-instances-20-lowb-11-15.yaml --run-suffix 20-lowb-11-15-b15-m610-cap100k-norho --out-root experiments/EXP-MTBK-306bdb --seeds 11,12,13,14,15 --cell-ms 6,7,8,9,10 --b-exps 0.15 --check-cap-std 100000 --check-cap-bkk 100000 --skip-rho`
  - Outcome: `25` cells, `lt=0`, `eq=20`, `gt=5`, `safe_lt=0`, `unsafe_lt=0`.
  - `ratio_median=--` (`ratio_samples=0`).

Combined across all three tranches (`1..15` seeds), this `m610`, `b=0.15`, `check_cap=100k` sweep gives:

- `n_total=75`, `n_lt=0`, `n_eq=60`, `n_gt=15`.
- `n_safe_lt=0`, `n_unsafe_lt=0`.
- No protocol-safe `K_star_bkk < K_star_std` evidence emerged in this window.

This does not yet include `cap=500k` for `b=0.15`, but it removes the seed-tranche ambiguity seen earlier from low-cap-only data: at `cap=100k`, the entire `m610` low-b tranche for `b=0.15` is strictly non-improving under timeout-safe controls.

### 2026-08-07 continuation: full `b=0.15` `m610` high-cap-comparison sweep (`check_cap=500k`)

To complete the same frontier at higher cap, I ran the remaining micro-sweeps and the matching seeded tranches:

- `RUN-MTBK-20-lowb-1-5-b15-m6-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-1-5-b15-m7-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-1-5-b15-m8-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-1-5-b15-m9-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-1-5-b15-m10-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-2-5-m6-b15-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-2-5-m7-b15-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-2-5-m8-b15-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-2-5-m9-b15-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-2-5-m10-b15-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-6-10-b15-m610-cap500k-norho`
- `RUN-MTBK-20-lowb-11-15-b15-m610-cap500k-norho`

Summary for the completed full `b=0.15`, `m610`, `cap=500k`, seeds `1..15` sweep:

- `n_total=75`
- `n_lt=0`, `n_eq=53`, `n_gt=22`
- `n_safe_lt=0`, `n_unsafe_lt=0`

No protocol-safe improvements were observed (`K_star_bkk < K_star_std` with timeout-safe controls remained 0 cells). This extends the 100k-comparison result to higher cap: `b=0.15` remains non-improving across the full tested 20-bit low-b low-exponent frontier.
