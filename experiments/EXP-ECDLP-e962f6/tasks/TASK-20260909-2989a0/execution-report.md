# Execution Report — EXP-ECDLP-e962f6 (Stages 1-2)

**Task:** TASK-20260909-2989a0 (role: executor)
**Contract:** experiments/EXP-ECDLP-e962f6/specification.yaml (version 1,
approved, frozen, execution_authorized, per DEC-20260909-0d8274)
**Worktree:** /Volumes/SSD990/llm/tmp/opencode/run-e962f6-20260909
**Branch:** runs/EXP-ECDLP-e962f6-20260909 (clean at origin/main e5859ae9bb at
start)
**Scope executed:** Stages 1-2 ONLY. Stage 0 (the validator audit of the
derivation document) is a separate reserved validator task and was NOT executed
here.

**Role discipline.** The Executor records observations only: it interprets
nothing, draws no conclusion, uses no hypothesis language in run records, and
changes no status. No ledger record (EV-*, DEC-*, H-*, KN-*) is written; no
commit, push, or pull request is made (the snapshot archive
TASK-20260909-b95f26 commits the declared paths). No Bedrock anywhere.

---

## 1. Run inventory

| Run | Kind | Status | Validity | Wall (s) | Peak RSS | Notes |
|-----|------|--------|----------|----------|----------|-------|
| RUN-ECDLP-e962f6-001 | quadrature | completed_valid | valid | 0.1 | 0.03 GB | deterministic; Q1-Q3 pass |
| RUN-ECDLP-e962f6-002 | anchor_exact_basins (N=2^26) | completed_valid | valid | 44.6 | **4.51 GB** | peak RSS exceeds the 4 GB machine-protection ceiling (anomaly, §7) |
| RUN-ECDLP-e962f6-003 | permutation_control (seed 1) | completed_valid | valid | 1.4 | 0.14 GB | |
| RUN-ECDLP-e962f6-004 | permutation_control (seed 2) | completed_valid | valid | 0.7 | 0.14 GB | |
| RUN-ECDLP-e962f6-005 | permutation_control (seed 3) | completed_valid | valid | 0.8 | 0.14 GB | |
| RUN-ECDLP-e962f6-006 | nonuniform_proves_too_much | completed_valid | valid | 1.9 | 0.15 GB | control fires via KS |
| RUN-ECDLP-e962f6-007 | stage2_residual_reread | **unknown (failed)** | — | 0.1 | 0.03 GB | implementation error (path bug); no results produced; preserved, never edited; superseded by RUN-008 (§7) |
| RUN-ECDLP-e962f6-008 | stage2_residual_reread (re-run) | completed_valid | valid | 0.5 | 0.03 GB | the Stage 2 re-read; uses the contract's spare run slot |

**Run count:** 8 run directories = the contract's 7 planned runs + 1 spare.
The spare is consumed by the RUN-007 -> RUN-008 re-run (an implementation
error, §7). This is within `maximum_runs: 8`.

**Per-run validity:** every executed run that produced results is
`completed_valid` / `valid`. The single failed run (RUN-007) is a defective
run record (implementation error, no results); it is preserved and superseded
by RUN-008, never edited.

**Inference (every run):** requested policy `executor-implementation`; resolved
model `vllm/qwen3.8-27b`; `model_verified: false` (the identifier is
unverified configuration; the adapter `doctor --probe` was not run in this
worktree); `fallback_used: false`; `degraded_requirements: []`. No Bedrock.

---

## 2. Quadrature anchor-reproduction table (RUN-001) — reported first

Per the completion gate, RUN-001's anchor reproduction is computed and reported
**before** any other Stage 1 number is interpreted.

| a | x* (computed) | x* (anchor) | x* dev | C_max (computed) | C_max (anchor) | C_max dev | within 5e-5 |
|---|---------------|-------------|--------|------------------|----------------|-----------|-------------|
| 1 | 0.1903808702719756 | 0.1903808702719756 | 2.8e-17 | 0.6625998114129124 | 0.6625998114129124 | 0.0 | yes |
| 1/2 | 0.404530706776745 | 0.4045307067767451 | -5.6e-17 | 0.5247586384598777 | 0.5247586384598776 | 1.1e-16 | yes |
| 1/4 | 0.7423409681771702 | 0.7423409681771704 | -2.2e-16 | 0.388912012966371 | 0.3889120129663709 | 1.1e-16 | yes |
| 1/8 | 1.208552283397922 | 1.2085522833979216 | 5.6e-16 | 0.27161902810059746 | 0.27161902810059757 | 1.1e-16 | yes |

**Q1 (anchor within 5e-5 at all four a): PASS.** All deviations are at the
floating-point round-off level (~1e-16), far inside 5e-5.

**Q2 (assembly minimum):** the minimum of `sqrt(a)/C_max(a)` on the fine grid
`a in [0.05, 2]` (step 0.001) lies at `a = 0.207` (in `[0.2, 0.25]`) with value
`1.282904` (within 0.01 of 1.28). **PASS.**

**Q3 (baseline-embedding values):** `c_rand(a_m=1) = 0.4226497308` (target
0.423, within 5e-3) and `c_max(a=1) = 0.6625998114` (target 0.66, within 5e-3).
**PASS.**

The quadrature gate is cleared; the other Stage 1 numbers below stand on a
reproduced baseline.

---

## 3. The N = 2^26 exact-basin anchor (RUN-002)

Parameters (as executed): `N = 2^26 = 67108864`, `T = 256`, `a = 1/4`,
`W = 256.0`, `theta = 1/256 = 0.00390625`, `cap 8W = 2048`. Seeds: walk_key 1,
dp_key 101, tie_break 401. (See §7 for the W deviation from the contract text.)

| Metric | Value |
|--------|-------|
| nDP (marked points) | 262671 (expected ~262144) |
| pointer-jumping rounds | 27 |
| cycle mass | 101486 (frac 0.0015123) |
| capped mass (8W) | 5339 (frac 7.956e-05) |
| partition identity (sum basins + capped + cycle = N) | **holds digit-for-digit** |
| top-T share (cap 8W) | **0.38627196848392487** |
| C_max(1/4) (model) | 0.3889120129663709 |
| top-T share / C_max(1/4) | 0.99321 (0.68% below C_max) |
| mean walk length (exact, no cap) | 255.284 (W = 256; 0.28% below W) |
| mean walk length (capped 8W) | 257.993 (W = 256; 0.78% above W) |
| Spearman rho (walk length vs basin size of reached DP) | **0.8242794131641281** |
| Spearman p-value | 0.0 |
| Spearman significant at alpha = 0.01 | **True** |
| largest basin (cap 8W) | 517020 |
| Borel(1-theta) N/W-sample order-statistic 99% band | [303616, 1011307] |
| largest basin in band | True |
| oracle online constant sqrt(a)/top-T share | 1.29442 (within 10% of 1.28) |

**Observations (recorded, not interpreted):**
- The top-T share (0.38627) is 0.68% below C_max(1/4) (0.38891).
- The Spearman correlation of walk length with basin size is **0.824,
  significant at alpha = 0.01** (p = 0.0). This is the Lemma 6 independence
  check; the contract's falsification condition F2 names "Spearman correlation
  significant at alpha = 0.01" as the trigger. The Executor records the
  measurement; the Coordinator decides.
- The mean walk length (255.284 exact) is 0.28% below W (256), i.e. within W,
  not beyond a CI of W.
- The largest basin (517020) is within the Borel order-statistic 99% band.
- The oracle online constant (1.29442) is within 10% of 1.28.

---

## 4. Permutation nearby-object control (RUN-003/004/005)

Parameters (all seeds): `N = 2^20 = 1048576`, `T = 64`, `a = 1/4`, `W = 64.0`,
`theta = 1/64 = 0.015625`, `cap 8W = 512`. Permutation seed s in {1,2,3}
(Fisher-Yates via numpy); dp_key seed 101 + s. Full (uncapped) cycle segments.

| Seed | top-T share | below frozen 3TW/N = 0.046875 | below correct 3TW/N = 0.01171875 | dev from C_max(1/4) | KS stat (segments vs Geometric(theta)) | KS p | largest segment | Geometric 99% quantile |
|------|-------------|-------------------------------|----------------------------------|---------------------|----------------------------------------|------|-----------------|------------------------|
| 1 | 0.0247707 | **True** | False | 0.9363 (93.6% below) | 0.015625 | 0.000618 | 600 | 293 |
| 2 | 0.0252314 | **True** | False | 0.9351 (93.5% below) | 0.018125 | 4.36e-05 | 626 | 293 |
| 3 | 0.0250616 | **True** | False | 0.9356 (93.6% below) | 0.017000 | 0.00017 | 650 | 293 |

**Control verdict (per the frozen contract):**
- The top-T share is **below the frozen threshold 3 T W/N = 0.046875 at every
  seed** (0.0248, 0.0252, 0.0251). The control **passes as frozen** (C2).
- The top-T share does **not** reproduce C_max(1/4) = 0.38891 (it is ~93.6%
  below), so the control is **not void** (the object discriminated).
- **Secondary (arithmetically-correct threshold):** the contract text's
  "3 T W/N = 0.046875" is an arithmetic error; the correct value is
  `3 * 64 * 64 / 2^20 = 2^{-8} = 0.01171875` (see §7). Against the correct
  threshold, the top-T share (0.025) is **above** 0.01171875 at every seed.
  Both thresholds are reported; the frozen threshold governs the verdict.
- **Tail check:** the largest segment (600-650) exceeds the single-sample
  Geometric(theta) 99% quantile (293) at every seed — expected, since it is the
  maximum of ~16384 segment samples, not a single sample.
- The segment sizes are statistically distinguishable from Geometric(theta)
  (KS p < 0.01 at every seed), consistent with the cycle-segment structure.

---

## 5. Proves-too-much non-uniform-rule control (RUN-006)

Parameters: `N = 2^20 = 1048576`, `T = 64`, `a = 1/4`, `W = 64.0`,
`theta = 1/64 = 0.015625`, `cap 8W = 512`. Non-uniform rule: density `2theta`
on the even-hash half, `0` on the odd-hash half (average density `theta`).
Seeds: walk_key 1, dp_key 101, online 201. `M = 40000` online walks (cap 8W).

| Metric | Value | Loudness threshold | Fires? |
|--------|-------|--------------------|--------|
| mean walk length | 60.240 (W = 64) | dev from W > 10% | **No** (dev 5.87%) |
| KS vs Geometric(theta), zero-based (primary) | stat 0.015625, p 6.51e-09 | reject at alpha = 0.01 | **Yes** |
| KS vs Geometric(theta), one-based (secondary) | stat 0.016225, p 1.41e-09 | (secondary) | Yes |
| top-T share (cap 8W) | 0.378771 (C_max 0.388912) | dev from C_max > 15% | **No** (dev 2.61%) |

**Control verdict:** the control **fires at least one loudness threshold** (the
KS test rejects Geometric(theta) at alpha = 0.01, p = 6.5e-9), so it is **not
void** — the machinery fails on the non-uniform object as required.

**Observations (recorded, not interpreted):**
- The measured **mean walk length is 60.24, only 5.87% below W = 64**, not the
  contract's pre-registered prediction of "about W/2 + 1 = 33" (a 48%
  deviation). The random-function walk mixes between the even/odd hash halves,
  so the effective mark rate stays ~theta and the mean stays near W. The mean
  therefore does **not** cross the 10% loudness threshold.
- The KS deviation from Geometric(theta) is **statistically significant**
  (p = 6.5e-9) but **small in magnitude** (KS statistic 0.0156). The control
  fires via the KS p-value, not via a large mean or top-T deviation.
- Walk-length quantiles (measured vs Geometric(theta), zero-based): 10%: 6 vs
  6; 50%: 43 vs 44; 90%: 140 vs 146.

---

## 6. Stage 2 read-only residual re-read (RUN-008, re-run of RUN-007)

**Read-only guarantee:** 16 committed files read (15 from EXP-ECDLP-869870 at
N in {2^20, 2^22, 2^24}, 5 seeds each, a = 1/4 cell; 1 from
EXP-ECDLP-612fb1-002, the N = 2^20 cross-check) plus the new RUN-002 anchor.
The sha256 of **every** committed file at read time **matches** the committed
state (`git show HEAD:<path>`): `all_sha256_match_committed_state = True`,
`mismatches = []`. The read-only guarantee **holds**. No committed file was
modified; no re-simulation.

**Anchor cross-check (RUN-ECDLP-612fb1-002, N = 2^20):** `C_max_model =
0.3889120129663709` and `x_star_model = 0.7423409681771704` **match** the
contract's `anchor_values` for a = 1/4.

**Corrected residual** `R(N) = (top_T_share + cycle_mass_frac +
capped_mass_8W_frac - C_max(a)) / C_max(a)` (cycle and capped mass added back,
as they are not in the model). Per-N median |R|:

| N | per-seed |R| (5 seeds, except 2^26) | per-N median |R| |
|---|----------|--------------------------|
| 2^20 | 0.1330, 0.0104, 0.0198, 0.0339, 0.0288 | **0.02883** |
| 2^22 | 0.0116, 0.0371, 0.0244, 0.0387, 0.0290 | **0.02905** |
| 2^24 | 0.0198, 0.0231, 0.0498, 0.0297, 0.0142 | **0.02314** |
| 2^26 | 0.0027 (1 seed, the new anchor) | **0.00270** |

**Decay-check verdicts:**
- **D1 (|R(2^26)| <= 0.15):** |R(2^26)| = 0.002695. **PASS.**
- **D2 (per-N median |R| non-increasing up to a 2pp noise floor):**
  0.02883 -> 0.02905 (increase 0.0002, within the 0.02 floor) -> 0.02314
  (decrease) -> 0.00270 (decrease). **PASS.**
- **D3 (log-log slope of per-N median |R| vs N over the points with |R| > 0.01,
  in [-0.7, -0.1]):** the three points with |R| > 0.01 are 2^20 (0.02883),
  2^22 (0.02905), 2^24 (0.02314); 2^26 (0.00270) is below the 0.01 floor and
  excluded. The log-log slope over these three points is **-0.0793**, which is
  **outside** the band [-0.7, -0.1]. **D3 does not pass.** (Three points exceed
  the 0.01 floor, so the D2-substitution clause is not triggered; D3 is
  computed and reported as-is.)

**Observation (recorded, not interpreted):** the per-N median |R| is roughly
flat across 2^20 -> 2^24 (0.0288, 0.0290, 0.0231) and then drops sharply to
0.0027 at 2^26. The residual at 2^26 is small (D1 passes) and the per-N median
is non-increasing (D2 passes), but the log-log slope over the |R| > 0.01 points
is near-flat (-0.0793), not the predicted -1/3. The committed calibration
points (read, not re-derived) are R(2^20) ~ -0.072, R(2^22) ~ -0.013,
R(2^24) ~ +0.008 (seed 1). The single largest |R| cell is
RUN-ECDLP-869870-001-N20-s1 (|R| = 0.1330).

---

## 7. Infrastructure events and protocol deviations

### 7a. RUN-007 implementation error (superseded by RUN-008)

RUN-007 (the first attempt at the Stage 2 re-read) **failed with an
implementation error**: a path bug resolved the committed-file paths against
the experiment directory (`experiments/EXP-ECDLP-e962f6`) instead of the
repository root, so every committed `summary.json` lookup raised
`FileNotFoundError`. The run produced **no results** (exit code 1; no
raw-result.json, summary.json, or run-meta.json). Per the contract, a defective
run is **superseded by a new run record, never edited**: RUN-007 is preserved
as-is, the bug is fixed in `source/run_reread.py` (the repo root is now resolved
via `git rev-parse --show-toplevel`), and the re-read is re-run as **RUN-008**,
which uses the contract's **spare run slot** (8th of `maximum_runs: 8`).

**Deviation from the contract's required_artifacts:** the contract names the
Stage 2 re-read as RUN-007; the successful re-read resides in **RUN-008**
because RUN-007 is the preserved defective record. Routed to the Coordinator.

### 7b. RUN-002 peak RSS exceeds the 4 GB machine-protection ceiling

RUN-002 (the N = 2^26 anchor) completed valid (exit 0, all metrics computed,
partition identity holds) but its **peak RSS was 4.51 GB (4839391232 bytes),
exceeding the 4 GB (4294967296 bytes) machine-protection ceiling**
(`within_memory_limit: false` in the manifest). The contract's budget_note
estimated the 2^26 arrays at ~1.3 GB; the actual peak was higher due to
intermediate arrays (the int64 bincount, the float64 rank arrays for the
Spearman correlation, the basin histogram). This is an **anomaly**, not a
failure: the run completed and the machine had sufficient memory. The 4 GB
figure is a machine-protection ceiling, not an expectation, and exceeding it is
not in the contract's invalidation list (the run did not OOM). Recorded, not
interpreted.

### 7c. Two internal contract arithmetic inconsistencies (recorded, not edited)

Two places in the frozen contract text contain arithmetic that is inconsistent
with the contract's own definitions. The Executor **did not edit** the frozen
contract; it executed per the contract's own definitions and records both
inconsistencies here for the Coordinator.

1. **Anchor W (RUN-002).** The contract text says "W = 2048, theta = 1/2048,
   cap 8W = 16384," but the contract's own definition `W = sqrt(a N / T)` with
   `(N = 2^26, T = 256, a = 1/4)` gives `W = sqrt(0.25 * 2^26 / 256) = 256`,
   `theta = 1/256`, `cap 8W = 2048`. The committed N = 2^24 run
   (RUN-ECDLP-869870-011-N24-s1) uses `W = 128 = sqrt(0.25 * 2^24 / 128)`,
   confirming the `W = sqrt(a N / T)` convention. **Executed with W = 256**
   (theta = 1/256, cap 8W = 2048). The "W = 2048" text appears to be a
   transcription of the cap, not the model W.
2. **Permutation 3 T W/N (RUN-003/004/005).** The contract text says
   "3 T W/N = 2^{-6} = 0.015625" (and uses 0.046875 as the frozen threshold in
   the success/falsification criteria), but `T W/N = 64 * 64 / 2^20 = 2^{-8} =
   0.00390625`, so `3 T W/N = 0.01171875`. The frozen threshold **0.046875**
   governs the control verdict (the top-T share is below it at every seed); the
   arithmetically-correct **0.01171875** is reported as the secondary threshold
   (the top-T share is above it at every seed). Both are reported; the frozen
   value governs.

---

## 8. Stages not yet run

- **Stage 0 (the validator audit of the derivation document)** is a separate
  reserved validator task (review-adversarial, independent session), dispatched
  after the snapshot archive TASK-20260909-b95f26. It was **not** executed
  here. The derivation document
  (`experiments/EXP-ECDLP-e962f6/derivation/derivation-lemmas-1-6.md`) is
  written and self-checked (per-lemma check box blocks present); the Stage 0
  audit verdicts are **not** written into it (it is immutable once archived).
- No other stage of this contract remains: Stages 1 and 2 are complete.

---

## 9. Completion-gate status

1. **Stopping rules met for every stage executed:** yes. No timeout, crash, or
   memory exhaustion produced a result; the single failed run (RUN-007) is an
   implementation error, re-planned within the spare run (RUN-008), never
   interpreted. No budget exhaustion (8 runs = the maximum; 0.5 CPU-hours not
   reached; wall clock well under 600 s per run).
2. **Every required artifact present for every executed run:** yes. Each valid
   run has a schema-complete manifest (command, commit, dirty state,
   environment, requested policy, resolved model, fallback flag, seeds, wall
   clock, peak_rss_bytes), raw-result.json, summary.json, stdout, stderr. The
   derivation document has the per-lemma check box blocks, present and
   self-checked.
3. **RUN-001 anchor reproduction reported first; RUN-008 read-only guarantee
   verified; decay checks D1-D3 stated with verdicts:** yes (§2, §6). D1 PASS,
   D2 PASS, D3 does not pass (slope -0.0793 outside [-0.7, -0.1]).
4. **Control verdicts stated per control:** yes (§4 permutation: below the
   frozen 0.046875 at every seed, not void, secondary 0.01171875 reported; §5
   proves-too-much: fires via KS p = 6.5e-9, not void, mean 60.24 not the
   predicted 33).
5. **Infrastructure failures recorded; no protocol edit; no status language;
   runs immutable:** yes. RUN-007 recorded as a defective run (implementation
   error), superseded by RUN-008; no protocol field edited; no status or
   hypothesis language; all run records immutable.

**Completion gate: MET** for Stages 1-2, with the deviations and anomalies in
§7 recorded and routed to the Coordinator.

---

## 10. Observations for the Coordinator (recorded, not interpreted)

The following are measurements the contract's success/falsification criteria
name. The Executor records them; the Coordinator decides after independent
review. No conclusion is drawn here.

- **F2 (Lemma 6) trigger is present in the data:** the Spearman correlation of
  walk length with basin size at the 2^26 anchor is **0.824, significant at
  alpha = 0.01** (p = 0.0). The contract's F2 names this as the condition under
  which "the online cost is not W/C and every cost figure in the batch must be
  re-derived from the measured length-conditional law." (The mean walk length,
  255.284, is within W, so the F2 mean-deviation alternative is not the
  trigger; the Spearman condition is.)
- **F1 (decidable negative) is not triggered:** |R(2^26)| = 0.0027 <= 0.15
  (the 15% half is not met) and D2 passes (the residuals are non-increasing).
  F1 requires both |R(2^26)| > 0.15 AND (D2 or D3 fails); the first conjunct
  is false.
- **D3 does not pass** (slope -0.0793 outside [-0.7, -0.1]): the per-N median
  |R| is near-flat over 2^20..2^24 and drops at 2^26, so the log-log slope over
  the |R| > 0.01 points is not the predicted -1/3. This bears on success
  criterion S3 ("the residual decays as N^{-1/3} per checks D2 and D3").
- **F3 (permutation) is not triggered under the frozen threshold** (top-T share
  below 0.046875 at every seed) **but would be triggered under the
  arithmetically-correct threshold** 0.01171875 (top-T share above it at every
  seed). The contract-text arithmetic error (§7c.2) is the reason the two
  thresholds differ.
- **The proves-too-much control fires via the KS test** (p = 6.5e-9), not via
  the mean (60.24, only 5.87% from W) or the top-T share (2.6% from C_max). The
  contract's pre-registered mixture-mean prediction (W/2 + 1 = 33) is not borne
  out by the measurement (60.24); the non-geometricity is detected
  statistically, with a small KS magnitude (0.0156).
- **RUN-002 peak RSS (4.51 GB) exceeds the 4 GB machine-protection ceiling**
  (§7b); the run completed valid.

---

## 11. Artifact inventory

- `experiments/EXP-ECDLP-e962f6/source/` — the instrument (one code path,
  object selection by configuration): `instrument.py` (shared core),
  `runcommon.py` (run wrapper), `run_quadrature.py`, `run_anchor.py`,
  `run_permutation.py`, `run_nonuniform.py`, `run_reread.py`. Hash-pinned per
  run manifest.
- `experiments/EXP-ECDLP-e962f6/derivation/derivation-lemmas-1-6.md` — the
  derivation document (Lemmas 1-6, two routes each, citations with provenance,
  per-lemma check box blocks, quantifier statement, baseline-embedding check,
  permutation collapse argument, proves-too-much argument).
- `experiments/EXP-ECDLP-e962f6/runs/RUN-ECDLP-e962f6-001..008/` — the run
  records (RUN-007 is the preserved defective record; RUN-008 is the Stage 2
  re-read).
- This execution report.


