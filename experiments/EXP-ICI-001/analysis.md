# EXP-ICI-001 — Analysis: best-IC exponents with bootstrap CIs on the extended ladder

**Experiment:** EXP-ICI-001 v1 (frozen specification.yaml) · **Hypothesis:** H-ICI-001
**Handoff:** TASK-20260718-ICI · **Executor:** executor agent · **Date:** 2026-07-18
**Runs:** RUN-EXP-ICI-001-a (crossbred ladder), -c (MITM ladder), -d (rho control),
-e (matched-null control), -f (same-seed determinism re-run of -a).
All manifests in `runs/<run-id>/manifest.yaml` with artifact SHA-256s.

---

## 1. What was measured (cost model, all stages charged)

Binary-field chained-Semaev PDP (`semaev_tree.py`, vendored exact copy
sha256 `e9f1681b…`, ecdlp-autolab git `354d8d3`), the native testbed of the
frozen solver paths whose legacy numbers this experiment pins (crossbred 0.863,
MITM 0.667; T12/T23).

**Crossbred path** (port of `crossbred_exponent.py` / `crossbred_real_cost.py`):
per target R (planted t=3 decomposition), Weil-descend the chained S_3 system to
a Boolean system in `nb` vars; sweep the crossbred split `k_fix`
(fractions of nb); per split, `log2 total = k_fix + log2(median per-guess GB-seconds)`;
per-target cost = min over completed splits. **Total IC exponent = fitted per-PDP
slope + 1/t, t=3** (the corpus convention: relation generation costs the
factor-base term 2^{n/t}). Stages charged per cell: system build+descent
(`build_s`), brute-force relation side (the 2^{k_fix} term), solve side
(GB wall-seconds, which includes its internal sparse linear algebra), memory
(peak RSS per cell/run, recorded not priced — §6 deviation D6).

**MITM path** (port of `mitm_tree_resolution.py`, t=4 tree split): per target,
left/right list enumeration with quadratic junction solves; records work units
(combinatorial count), wall seconds, list-build/match split, L1 entries
(memory stage), relations found. **Total = per-PDP slope + 1/t, t swept** (the
spec's "1/2+1/t family").

Instances per cell: 3 curves (seeds 1,2,3 — spec `replication.seeds`) ×
8 targets, targets = planted decomposable R (seeded), per n.
Bootstrap: 2000 seeded resamples of per-target costs within each n-cell →
cell median → OLS slope vs n; 90% CI = 5/95 percentiles (seed 20260718).

## 2. Controls

| # | Control | Result | Status |
|---|---------|--------|--------|
| C1 | **Rho baseline on the same curves** (H040 op convention: 1 op = 1 point addition, exact first-repeat seen-set, plain walk; RUN-d) | fitted ops slope **0.498, 90% CI [0.471, 0.522]** over n=10…24 (24/24 cells, 192 targets, 190 solved+verified — 2 walks returned k via the g>128 gcd fallback, ops still counted); median constant 1.289 vs theory 1.2533 | **PASS** — sits at 0.5 |
| C2 | **Matched random polynomial system** (T11-style support/degree-matched null, GF(2) adaptation; same instances as crossbred — 7/7 built systems hash-identical to run-a; RUN-e + dev long-probe) | null certified shape-matched on every built system. Null solve cost at n=12: k_fix=2 ≥ 5.0 (t/o), 3 ≥ 6.0 (t/o), 4 ≥ 9.64 (50 s t/o), 6 = **8.76 measured** vs Semaev best **−4.45** at the same n ⇒ instrument contrast **≥ 2^13.2×** on measured splits. n=16 null: censored (infrastructure; AGENTS rule 5 — not evidence) | **PASS** — instrument is structure-sensitive; Semaev cost is genuinely low, not an instrument artifact |
| C3 | **Same-seed re-run** (RUN-f = identical command/seeds as RUN-a) | 216/216 instance system-hashes **identical**; k_fix* argmin flips 45/216 (timing noise on near-ties); slope 0.5581 vs 0.5666 (Δ 0.008 < CI half-width 0.022); total 0.8914 vs 0.8999 | **PASS** — generation deterministic; metric noise quantified and inside CIs |

Planted-target exact verification (sidecar `runs/*/verification.json`, junctions
by quadratic root-propagation): run-a/f 216/216 membership, 216/216
decomposition-sum, **214/216 chain-consistent**; run-c 120/120, 120/120,
**111/120** — see O1 below.

## 3. Fits (primary metrics)

### 3.1 Crossbred (RUN-a): 9 ladder points, 27/27 cells, 216/216 targets measured

| n | nb | cell-median log2 per-PDP cost (3 curves × 8) | per-cell implied total exp (CI90) |
|---|----|----------------------------------------------|-----------------------------------|
| 10 | 22 | −3.86 | −0.052 [−0.081, −0.009] |
| 12 | 24 | −3.87 | 0.011 [−0.048, 0.032] |
| 14 | 29 | −1.84 | 0.202 [0.183, 0.233] |
| 16 | 34 | −0.57 | 0.298 [0.247, 0.310] |
| 18 | 36 | −0.07 | 0.329 [0.311, 0.347] |
| 20 | 41 | 1.05 | 0.386 [0.369, 0.424] |
| 22 | 46 | 3.31 | 0.484 [0.467, 0.489] |
| 24 | 48 | 2.56 | 0.440 [0.425, 0.454] |
| 26 | 53 | 5.09 | 0.529 [0.517, 0.534] |

Per-cell implied values below 0.5 at n ≤ 24 are **constant-regime artifacts**
(sub-second costs divided by small n) — they are not exponents and are not
admissible for the gate; the gate uses the fitted slope. Recorded to prevent a
bookkeeping-leak reading.

- **Fitted per-PDP slope: 0.558, 90% CI [0.536, 0.580]**
- **Fitted total exponent (t=3): 0.891, 90% CI [0.869, 0.914]**
- Legacy-ladder-only (n ≤ 20) fit: slope 0.531 [0.488, 0.599] → total 0.864 —
  reproduces the corpus point estimate 0.5295 → 0.8628 almost exactly.
- Extension-arm-only (n ≥ 18) fit: slope 0.592 [0.532, 0.629] → total 0.925.
- Sensitivity excluding the 2 chain-inconsistent targets (O1): slope 0.559
  [0.535, 0.586] → total 0.892 — unchanged.

### 3.2 MITM (RUN-c): 5 measured ladder points + 1 partial (n=28), 15 full cells

| n | k | median log2 work | median wall s | per-cell implied total (work, t=4) |
|---|---|------------------|---------------|-------------------------------------|
| 8 | 2 | 5.0 | 0.01 | 0.875 |
| 12 | 3 | 7.0 | 0.05 | 0.833 |
| 16 | 4 | 9.0 | 0.25 | 0.812 |
| 20 | 5 | 11.0 | 1.19 | 0.800 |
| 24 | 6 | 13.0 | 5.95 | 0.792 |
| 28 | 7 | 15.0 (2/8 targets) | 27.39 | 0.786 |

- **Per-PDP work slope: 0.500, 90% CI [0.500, 0.500]** (degenerate: work units
  are exact combinatorial counts, log2 = 2k+1, k = ⌈n/4⌉).
- **1/2 + 1/t family, t swept:** t=4: **0.750**, t=6: **0.667**, t=8: **0.625**,
  t=10: 0.600, t=12: 0.583 (work-model CI degenerate at the slope).
- **Honest wall-clock fit: slope 0.573 [0.566, 0.579] → total at t=4: 0.823
  [0.817, 0.829]** — superlinear wall time (list/memory effects, L1 grows
  13 → 16 281 entries); see O3.

### 3.3 Legacy-vs-extension drift (secondary metric)

Crossbred total: legacy ladder 0.864 → full ladder 0.891 → extension arm 0.925.
The full-ladder point (0.891) sits **inside** the legacy-ladder CI
[0.488+1/3, 0.599+1/3] = [0.821, 0.932]. The extension does **not** move the
estimate outside its small-ladder CI; the drift that exists is **upward**
(the legacy 0.863 was, if anything, optimistic). MITM work slope is exactly
its predicted 0.5 across the whole measured range.

## 4. Gate arithmetic (numbers vs the frozen criteria)

H-ICI-001 promotion/success criterion: *any solver path with fitted total
exponent whose bootstrap 90% CI upper bound is < 0.5 on ≥ 4 ladder points.*

- Crossbred: 0.891, CI90 [0.869, 0.914] — upper 0.914 ≮ 0.5. **Not met.**
- MITM family: best concrete t=12 → 0.583 (t=6 → 0.667, t=4 → 0.750); all
  above 0.5; wall-fit 0.823 (t=4). **Not met.** (The family's t→∞ limit is 0.5,
  never below, by construction of 1/2+1/t.)

H-ICI-001 falsification criterion: *both paths CI-separated above 0.5, or CIs
overlapping 0.5 with point estimates stable across the extension.*

- Crossbred CI [0.869, 0.914] — entirely above 0.5. ✔
- MITM totals 0.750/0.667/0.625/0.600/0.583 (t = 4…12), work-slope CI
  degenerate, wall-fit CI [0.817, 0.829] — all entirely above 0.5. ✔
- Point estimates stable across the extension (§3.3). ✔

⇒ The falsification branch **is satisfied numerically**; the promotion branch
is not. (The Coordinator owns the status transition; this file supplies the
arithmetic only.)

Stacked-constants check (review_stacked_compat.py's "loses by 2^43"): at
n=256, MITM t=6: 0.667·256 = 170.7 vs rho 128 ⇒ gap 42.7 ≈ **2^43** — now
backed by a CI-degenerate work slope and a wall-fit that only widens the gap
(0.823·256 = 210.7 ⇒ 2^83 at t=4). Crossbred at n=256: 0.891·256 = 228.2 ⇒
loses by 2^100 (CI90 on the gap: [94.5, 105.7]). H040/T24 rho anchor (1.2533 /
0.8862) re-verified on the same curves (C1).

## 5. Censoring table (stopping rules applied)

| Cell(s) | Terminal state | Reason |
|---|---|---|
| crossbred, all 27 cells (n=10…26) | measured (216/216 targets) | — |
| MITM n=8, curves 1–2 | measured, random-target fallback | |V|=4 too small to plant t=4 decompositions; cost is target-independent (full enumeration), fits unaffected |
| MITM n=28, curve 1 | measured_partial (2/8 targets, 27.4 s each) | cell budget 90 s |
| MITM n=28, curves 2–3 | censored_budget | script budget after partial cell; ladder stops (two consecutive censored) — infrastructure, not evidence (rule 5) |
| null n=16, all curves | censored_budget | null GBs exceed every budget (C2); infrastructure, not evidence |
| crossbred n=28/30 (planned RUN-b/b2) | not executed | Coordinator consolidation directive 2026-07-18 ("avoid new heavy ladders"); extension requirement already met at n=22/24/26 |

No run was killed by the 600 s/285 s outer guards; every planned cell has a
terminal state. Peak RSS: a 0.38 GB, c 0.28, d 0.28, e 1.03, f 0.44 (≪ 40 GB cap).

## 6. Deviations from the frozen spec / legacy harness

- D1 Handoff budget for this execution (3 000 s wall, 12 runs) is far smaller
  than the spec campaign budget (120 runs, 7 200 s/run); executed 5 runs.
  Spec-level instance minimums (≥3 curves × ≥8 targets/n) **met** for both
  solver paths at every measured size.
- D2 Per-GB timeout 6 s (legacy 20 s), guesses 2 (legacy 4), k_fix fractions
  trimmed to ≥ 0.15 (0.15·nb floor; the 0.1 arm only added timeout cost in
  probes and was never optimal at n ≥ 16). Every target's minimum remains
  bracketed; the per-target bias check (a timed-out split could hide the
  optimum only if k + log2(timeout) < best) fired **0** times in 216 targets.
  Effect direction is conservative (costs can only be over-estimated).
- D3 MITM n=8 curves 1–2: random (non-planted) targets (see §5).
- D4 Null control: 4 targets/cell at n=12, n=16 censored; control remains
  decisive on measured splits (C2).
- D5 T11 GF(2) adaptation: Boolean coefficients are all 1, so "randomized
  coefficients on identical support" is degenerate; the null instead keeps
  per-generator monomial count AND monomial-degree multiset with randomized
  support (the T11 matching principle), certified per system.
- D6 Memory stage recorded (peak RSS per cell/run; MITM L1 entries) but not
  priced into GB-seconds — the legacy convention; no stage left unrecorded.
- D7 Testbed is binary F_{2^n} (the frozen solver paths' native objects, whose
  exponents the hypothesis cites). RQ's "generic E/F_p" framing inherits the
  corpus convention that these are the best-IC numbers to pin. Toy scale
  throughout (n ≤ 28 bits); AGENTS rule 7 applies to everything above.

## 7. Unexpected observations (AGENTS rule 8)

- O1 **x-collision degeneracy of planted decompositions.** 2/216 (t=3) and
  9/120 (t=4) planted targets have decomposition x-tuples that do NOT satisfy
  the chained S_3 system under any junctions (exact root-propagation check).
  Cause: sampling picks both y-variants of one x-coordinate; the partial sum
  then hits O and the summation-polynomial chain degenerates. These targets are
  still valid DLP-style instances (membership + sum verified) but their planted
  decomposition is invisible to the Semaev chain — a small fraction of
  "decomposable" targets are effectively non-decomposable for this system
  shape. Sensitivity: fits unchanged (§3.1). Side effect: the in-run
  `planted_verified` flags used a geometric-junction shortcut that mis-reports
  exactly these degenerate cases (Sage's O[0] = 0 masked it); the sidecar
  verification supersedes those flags. Recorded, not silently patched.
- O2 Cell-median log-cost is **non-monotone** in n (n=24 < n=22): cost tracks
  the k = ⌈n/3⌉ plateau (k=8 spans n=22…24) more than n itself.
- O3 MITM wall-time slope (0.573) exceeds its combinatorial work slope (0.500
  exactly): memory/list effects are superlinear; honest wall accounting makes
  MITM worse than the work-model family quotes (0.823 vs 0.750 at t=4).
- O4 The matched null is ≥ 2^13.2× harder than the Semaev system at identical
  shape (n=12): the Semaev structure yields a huge **constant** win, and the
  structured exponent nevertheless loses to rho — structure helps constants,
  not the exponent.
- O5 Crossbred exponent drift is **upward** with the extension (0.864 → 0.891
  → 0.925 arm-only), opposite to the hypothesis's bend-down hope.
- O6 Rho control: 2/192 walks returned an unverified k (gcd(den, ord_P) > 128
  fallback); their ops are counted and flagged, not silently dropped.

## 8. Reproducibility

- Vendored builder: `src_copies/semaev_tree.py` sha256 `e9f1681b4e422f…`.
  Source ports credited in `ici_lib.py` header with upstream sha256s
  (crossbred_exponent `ae934a…`, crossbred_real_cost `9f49b4…`,
  mitm_tree_resolution `444c1e…`, h040_rho_const `53b56f…`, t11_null_harness
  `3085e3…`; ecdlp-autolab git `354d8d38761f4b4e0cdad1749ae1909ccd45f7ab`).
- Harness repo at git `e111dd3731a21f3345114b7bb4c04a8f54d4b4c9`, dirty tree
  (recorded in every manifest). SageMath 10.9, sage-python 3.14.3, macOS 15.6
  arm64.
- All randomness seeded (layout in `ici_lib.py`); bootstrap seed 20260718;
  same-seed re-run verifies bit-identical instance generation (C3).
- Each run dir: manifest.yaml (command, commit, env, params, timings, peak RSS,
  artifact SHA-256s), raw.json (per-candidate/per-target machine-readable
  records), stdout.txt, stderr.txt, verification.json (a/c/f).
- dev/: timing probes, smoke runs, deep null probe, finalize_manifest.py,
  reverify.sage (development records, not evidence runs).

## 9. Honest bottom line (no status claim)

Over the tested instances (binary toy curves, n ≤ 26 crossbred / n ≤ 24 MITM
measured, n ≤ 28 attempted), seeds 1–3, 8 targets per cell, and this budget:
no solver path's fitted total exponent came within CI-reach of 0.5; both paths
are CI-separated above 0.5 with stable point estimates across the extension.
The numbers satisfy the experiment's frozen falsification arithmetic and leave
the promotion arithmetic unmet. Per AGENTS rules 6–7 this closes only the
tested scope; nothing here is a crypto-scale statement or a proof about
untested parameterizations.
