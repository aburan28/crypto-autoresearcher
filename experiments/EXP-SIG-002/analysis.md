# EXP-SIG-002 — Analysis: growth resolution of the residual non-rewritable D4 syzygy family

Experiment: EXP-SIG-002 (hypothesis H-SIG-001, question RQ-SIG-001)
Dispatched by: DEC-20260718-015 (next_actions); handoff TASK-20260718-SIG-F2.
Runs: RUN-EXP-SIG-002-a (gate), -b (boolean n=9,12), -c (n=15), -d (n=18),
-e (n=21), -f (n=12 extra seeds), -g (n=15 extra seeds), -h (D5 n=9,12),
-i (D5 n=15).
Instrument: bit-identical copy of the EXP-SIG-001 instrument
(`src/h013_f5_signatures.sage`, sha256
`1ba96fe477c9dc2e7c551c96353c8361d21e40134551342636b2f13015c09087`);
new driver `SIG2_run.sage`.
Git: commit df595e8ac25c5be078485dea50e3a7f07d4e9a5b, dirty tree.
Budget: 9 runs of 10 maximum; ≈ 470 s real of 3,300 s wall; peak RSS 2.19 GB
of 24 GB. No censoring, no timeouts, no infrastructure failures.

## 1. Scope executed vs approved spec

| # | Item | Spec | Executed |
|---|------|------|----------|
| 1 | n=12 non-degenerate re-run | ≥1 non-degenerate seed | 5 standard seeds {2,4,5,6,7} + degenerate seed 1 re-recorded |
| 2 | Residual D4 series | n ∈ {9,12,15,18,21}, ≥3 seeds/size | 3–5 standard seeds per size (see §4 for the instance filter) |
| 3 | D=5 arm if budget remains | one arm, n ≤ 15 | n=9 s1, n=12 s2 (standard), n=12 s1 (degenerate observation), n=15 s1; sem + matched null each |
| 4 | Controls | null extra=0; injected-syzygy detection; T2 anchors 8n/3 at n≥12; determinism | all executed, all PASS (§2) |
| 5 | n=9 D4 deficit 41 replication check | record across seeds | recorded: 41 on seeds 1,2,3 (§3) |

No deviations from the specification. No run was killed or censored; the
600 s per-invocation kill rule was never engaged (longest invocation
240.9 s, RUN-EXP-SIG-002-i).

## 2. Controls (all passed)

- **Gate V1** (support-matched null, n=9,12, D=3,4): extra = 0 and
  rank = sr_pred everywhere (RUN-a).
- **Gate V2** (injected 3-generator syzygy, n=9): detected with the correct
  constant-multiplier representation (RUN-a).
- **Gate V3** (T2 anchor continuity with EXP-SIG-001, n=15 seed 1): D3
  deficit 1, D4 deficit 40, residual 10, null extras 0 — reproduces
  EXP-SIG-001 exactly (RUN-a).
- **Determinism**: n=15 seed 2 cell computed twice, identical modulo timing
  fields (RUN-a).
- **Null control on every measurement cell**: all 22 boolean cells (D3, D4)
  and all 4 D5 null cells have extra = 0 and rank = sr_pred
  (`controls.null_extra_zero_all_cells: true` in every raw.json).
- **Cross-run continuity**: seed-1 cells reproduce EXP-SIG-001 bit-exactly at
  n=9 (41/23), n=12-degenerate (82/82), n=15 (40/10), n=18 (48/13).
- **Cross-instrument anchor (unplanned)**: D5 n=15 seed 1 sem rank = 69,073
  with sr_pred = 70,935 — the h012 anchors cited in the instrument header and
  the EXP-DREG-001 VALIDATE-N15-A cell. D5 n=12 seed 2 sem rank = 28,097
  (deficit 1,321) vs EXP-DREG-001's n=12 anchor 28,096 (deficit 1,322) on its
  seed-2026 instance — see §6, observation 4.

## 3. Measured numbers

### 3.1 Boolean cells, all probed instances (t=3, D=3/4)

| n | seed | instance type | D3 def | D3 extra | D4 def | D4 extra | D4 rankK | v3 imgs | v3 rank mod K4 | **residual** | null extra D3/D4 |
|---|------|---------------|--------|----------|--------|----------|----------|---------|----------------|-----------|------------------|
| 9  | 1 | standard | 1 | 1 | 41 | 41 | 45  | 18 | 18 | **23** | 0/0 |
| 9  | 2 | standard | 1 | 1 | 41 | 41 | 45  | 18 | 18 | **23** | 0/0 |
| 9  | 3 | standard | 1 | 1 | 41 | 41 | 45  | 18 | 18 | **23** | 0/0 |
| 12 | 1 | degenerate R_x=0 | 0 | 0 | 82 | 82 | 78  | 0 | 0 | **82** | 0/0 |
| 12 | 2 | standard | 1 | 1 | 32 | 32 | 78  | 24 | 23 | **9** | 0/0 |
| 12 | 3 | linear-eq | 0 | 0 | 0 | 0 | 619  | 840 | 0 | **0** | 0/0 |
| 12 | 4 | standard | 1 | 1 | 32 | 32 | 78  | 24 | 23 | **9** | 0/0 |
| 12 | 5 | standard | 1 | 1 | 32 | 32 | 78  | 24 | 23 | **9** | 0/0 |
| 12 | 6 | standard | 1 | 1 | 32 | 32 | 78  | 24 | 23 | **9** | 0/0 |
| 12 | 7 | standard | 1 | 1 | 32 | 32 | 78  | 24 | 23 | **9** | 0/0 |
| 15 | 1 | standard | 1 | 1 | 40 | 40 | 120 | 30 | 30 | **10** | 0/0 |
| 15 | 2 | linear-eq | 0 | 0 | 0 | 0 | 976  | 1320 | 0 | **0** | 0/0 |
| 15 | 3 | standard | 1 | 1 | 40 | 40 | 120 | 30 | 30 | **10** | 0/0 |
| 15 | 4 | standard | 1 | 1 | 40 | 40 | 120 | 30 | 30 | **10** | 0/0 |
| 15 | 5 | standard | 1 | 1 | 40 | 40 | 120 | 30 | 30 | **10** | 0/0 |
| 15 | 6 | standard | 1 | 1 | 40 | 40 | 120 | 30 | 30 | **10** | 0/0 |
| 18 | 1 | standard | 1 | 1 | 48 | 48 | 171 | 35 | 35 | **13** | 0/0 |
| 18 | 2 | standard | 1 | 1 | 48 | 48 | 171 | 35 | 35 | **13** | 0/0 |
| 18 | 3 | standard | 1 | 1 | 48 | 48 | 171 | 35 | 35 | **13** | 0/0 |
| 21 | 1 | standard | 1 | 1 | 56 | 56 | 231 | 42 | 42 | **14** | 0/0 |
| 21 | 2 | standard | 1 | 1 | 56 | 56 | 231 | 42 | 42 | **14** | 0/0 |
| 21 | 3 | standard | 1 | 1 | 56 | 56 | 231 | 42 | 42 | **14** | 0/0 |

("v3 imgs / v3 rank mod K4" = multiplier images of the D3 syzygy inside D4 and
their rank mod K4; residual = D4 extra − that rank. On linear-eq instances
there is no D3 syzygy; the 840/1320 "images" column is the count of nonzero
multiplier images of the 35/44 K-family D3 syzygies — their rank mod K4 is 0
by construction, and residual = extra = 0.)

### 3.2 Growth series (standard instances; instance filter in §4)

| n | standard seeds | D4 deficit | 8n/3 | residual (per seed) | residual value |
|---|----------------|-----------|------|---------------------|----------------|
| 9  | 1,2,3       | 41 | 24 | 23, 23, 23          | 23 |
| 12 | 2,4,5,6,7   | 32 | 32 | 9, 9, 9, 9, 9       | 9  |
| 15 | 1,3,4,5,6   | 40 | 40 | 10, 10, 10, 10, 10  | 10 |
| 18 | 1,2,3       | 48 | 48 | 13, 13, 13          | 13 |
| 21 | 1,2,3       | 56 | 56 | 14, 14, 14          | 14 |

- Residual series: **23 → 9 → 10 → 13 → 14** at n = 9 → 21. Zero within-size
  variance across 3–5 independent seeds at every size.
- From n = 12 (the range where the 8n/3 law holds): monotone increasing
  9 → 10 → 13 → 14, increments +1, +3, +1.
- Including n = 9 the series is non-monotone (23 → 9): n = 9 is elevated,
  consistent with its D4-deficit anomaly.
- **T2 8n/3 law**: holds exactly at n = 12, 15, 18, 21 on every standard seed
  (first measurement at n = 12 non-degenerate: 32; first at n = 21: 56).
  Fails at n = 9 (41 ≠ 24) on all three seeds — the EXP-SIG-001 n=9 anomaly
  **replicates across seeds** (mission item: recorded).
- D3 deficit = 1 (the single non-Koszul degree-3 syzygy) on every standard
  seed at every size, n = 9 through 21.

### 3.3 D=5 count-only arm (sem; matched null control each cell)

| cell | instance | nrows | rank | sr_pred | deficit | kernel | rankK | extra | null extra |
|------|----------|-------|------|---------|---------|--------|-------|-------|-----------|
| n=9 s1  | standard | 10,440 | 8,595  | 9,504  | 909  | 1,845 | 935  | 910  | 0 |
| n=12 s2 | standard | 31,512 | 28,097 | 29,418 | 1,321 | 3,415 | 2,093 | 1,322 | 0 |
| n=12 s1 | degenerate R_x=0 | 31,512 | 27,257 | 29,418 | 2,161 | 4,255 | 2,094 | 2,161 | 0 |
| n=15 s1 | standard | 74,880 | 69,073 | 70,935 | 1,862 | 5,807 | 3,944 | 1,863 | 0 |

- D5 standard-deficit series: 909 / 1,321 / 1,862 at n = 9 / 12 / 15
  (n=12 is seed 2; the EXP-DREG-001 seed-2026 anchor reads 1,322 — §6.4).
- Null extra = 0 and rank = sr_pred on every D5 cell.
- The rewritten-rule decomposition at D=5 (D3-multiples by degree-2 monomials
  + D4-residual multiples) is **not** implemented in the copied instrument;
  D5 numbers are raw counts only (recorded as a scope note, not a deviation).

## 4. Instance classification (input-side filter, fixed before looking at outcomes)

Three instance types were observed, classified from **input structure only**
(recorded `R_x` and `eq_degs_hist`), not from syzygy outcomes:

1. **Degenerate R_x = 0** (2-torsion target): n=12 seed 1 (1 cell). Constant
   terms in block-1 quadrics; deficit profile 0/82. Reproduces EXP-SIG-001.
2. **Linear-equation instance** (eq_degs_hist contains a degree-1 equation):
   n=12 seed 3 (hist {1:1, 2:11, 3:12}), n=15 seed 2 (same pattern). The
   system is exactly semi-regular modulo K: deficit 0, residual 0, rankK
   inflated (35/619, 44/976) because the linear generator generates Koszul
   pairs with everything. 2 cells of 22 probed.
3. **Standard**: all other cells (19 of 22). Uniform profile per size.

The growth series (§3.2) is computed on standard instances. Types 1–2 are
retained in raw.json as recorded observations (AGENTS rule 8) and are
excluded from the series; this exclusion is the only post-hoc element of the
analysis and is flagged here explicitly.

## 5. Gate arithmetic (numbers only — status decision belongs to the Coordinator)

H-SIG-001 success clause (minimum_effect): "non-rewritable count growing in n
on any family (CI-separated from the null's rewritable-only profile)."
Measured: residual 9 → 10 → 13 → 14 at n = 12 → 21 (monotone increasing,
increments +1/+3/+1, +55.6% over the range), zero within-size variance over
3–5 seeds; null profile is exactly 0 at every (n, seed, D) — any positive
residual is separated from the null by the full count. With n = 9 included
the series is 23 → 9 → 10 → 13 → 14 (non-monotone; n=9 elevated).

H-SIG-001 falsification clause (a): "all extra syzygies rewritable/Koszul."
Measured: false on every standard seed at every size (residual > 0
everywhere; the D3 non-Koszul syzygy present at every n = 9..21).

H-SIG-001 falsification disjunct: "deviations constant-sized in n."
Measured on standard instances: residual not constant over n = 12..21
(9,10,13,14); over n = 9..21 the series (23,9,10,13,14) is non-monotone.

n=9 D4 law check: deficit 41 vs 8n/3 = 24 on seeds 1,2,3 — anomaly
replicates; the 8n/3 law holds at every measured n ≥ 12 including the new
n = 21 (56).

## 6. Unexpected observations (AGENTS rule 8)

1. **Linear-equation instances exist** (type 2 above): at n=12 seed 3 and
   n=15 seed 2 one descended S_3 equation is linear; the instance then shows
   NO deficit and NO residual at D3/D4 — the entire syzygy space is
   Koszul/Frobenius. Frequency 2/22 probed cells. These instances are
   semi-regular in practice; they are a second instance-generation anomaly
   class alongside R_x = 0 (1/22).
2. **n=9 is uniformly exceptional**: D4 deficit 41 (≠ 24) and residual 23 on
   all three seeds — the small-n deviation from the 8n/3 law is a property of
   n=9, not of a particular instance.
3. **D5 extra = deficit + 1 on standard cells** (910/909, 1322/1321,
   1863/1862 at n=9/12/15) but extra = deficit on the degenerate cell and on
   every D4 cell: rankK is exactly 1 short of nrows − sr_pred on standard D5
   cells (935 vs 936; 2,093 vs 2,094; 3,944 vs 3,945). One K-model vector is
   dependent/vanishing on the Semaev system at D=5 that is independent on the
   null; the same phenomenon may be visible at D4 as the n=12 standard cell's
   24 D3-multiplier images having rank 23 mod K4. Not resolved; recorded.
4. **D5 deficit shows O(1) seed-dependence at n=12**: seed 2 gives rank
   28,097 (deficit 1,321) where EXP-DREG-001's seed-2026 instance gives
   28,096 (deficit 1,322), same sr_pred 29,418. At n=15 the two seeds agree
   exactly (69,073). The D4 residual/deficit quantities showed zero seed
   variance; the D5 raw count does not (variance ≤ 1 observed).
5. **Residual increments are uneven**: +1, +3, +1 over n = 12→15→18→21 (vs
   D4-deficit increments +8 every step, exactly 8n/3). No smooth law fit is
   attempted here.

## 7. Artifacts

- `specification.yaml`, `implementation.md`, `SIG2_run.sage`,
  `make_manifests.py`
- `src/{h013_f5_signatures.sage, semaev_tree.py, ic_first_fall_fast.py,
  macaulay_export.py}` — bit-identical instrument copies (sha256 in every
  manifest)
- `runs/RUN-EXP-SIG-002-{a..i}/{manifest.yaml, raw.json, stdout.txt,
  stderr.txt, command.txt, environment.json}`
- `ledger/EV-SIG-002.yaml`

All raw.json files contain: exact CLI args, environment (SageMath 10.9,
Python 3.14.3, macOS-15.6 arm64), UTC timestamps, per-cell
ranks/predictions/kernel data/quotient reps, R_x and equation histograms,
degeneracy flags, per-cell and run-level control outcomes. Manifests carry
peak RSS, CPU seconds (user+sys from `/usr/bin/time -l`), git commit/dirty
state, and instrument hashes.
