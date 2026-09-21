# EXP-GPS-001 — analysis (Executor-GPS1, TASK-20260726-002, 2026-07-26)

Forensics on existing artifacts. GPS-1 stage 1 (composition-class stratification)
and GPS-4 stage 1 (2,722≈2,724 nesting probe). Pinned instrument
`experiments/EXP-SIG-007/src/h013_f5_signatures.sage` sha256-verified in every
sage run (`instrument_sha256_matches_pinned: true`).

## Runs (receipts in runs/RUN-EXP-GPS-001-*/)
- a: probe — all 76 EXP-SIG-007 rank5 carries sha256-verified vs state.json (Σ npiv = 265,950 = rank_acc ✓); EXP-SIG-008 pkl structure probe.
- b: exact n=21 D5 sem column set + composition segmentation (sage, 19 s).
- c: burst-unit [449,000,454,000) re-reduction vs carries 0..74 + column rank profile (sage, checkpointed, 3 invocations ≈ 470 s total).
- d: GPS-1 P1/P2 scoring (python).
- e: GPS-4 S9 closure ladder, bigint echelon — D3/D4/D5 done; D6 timed out (censored, rule 5).
- f: GPS-4 S9 D6 closure in m4ri — ranks through K6 done; F5-image closure exceeded 240 s cap (censored, rule 5).

## Integrity anchors
- Rebuilt n=21 s1 system **bit-identical** to the staircase's: `system_hash` match vs `s1_adjacency.pkl` (RUN-b).
- Exact column law at top degree (proved in-run): quintic column ⟺ contains a top-slice equation monomial; ncols = 778,394 == receipt exactly; since the exact set ⊆ up-closure and totals match, up-closure == exact everywhere. 0/500 adjacency row-count mismatches.
- Burst profile size 947 == state.json unit-92 k exactly (RUN-c); pivot cols ⊂ [449,000,454,000).

## GPS-1 P1 (burst composition) — **FALSIFIED as stated; coarse u-degree signature survives**
The 947 burst pivots:
- are exactly the contiguous window **[452,824, 453,770]** — 947 consecutive columns, **every one a pivot**;
- spread over **9 composition classes** (top class (1,2,1,1) holds 294/947 = 31.0%);
- **all have u-degree exactly 1**: classes {(1,4,0,0) 20, (1,3,1,0) 105, (1,3,0,1) 105, (1,2,2,0) 126, (1,2,1,1) 294, (1,2,0,2) 126, (1,1,3,0) 31, (1,1,2,1) 98, (1,1,1,2) 42}.

Prediction was ≥800/947 in ONE class and all in ≤2 classes → FAILS. Falsification
criterion (i) kills the mechanism only if the spread has "no common
divisor/support pattern" — but the u-degree-1 signature is exactly such a
pattern, so the honest verdict is: **the block-composition class is the wrong
stratification variable; a coarser u-degree-typed stratification fits the burst
perfectly**. Further texture: within the burst unit, every u≥2 class and the
u=1 class (1,1,0,3) (35 cols) contributed ZERO pivots; three window classes
were fully pivot within the unit ((1,2,1,1) 294/294, (1,2,2,0) 126/126,
(1,2,0,2) 126/126).

## GPS-1 P2 (dead-plateau class rates) — **NOT DECIDABLE from existing artifacts**
- The plateau [364,000,449,000) is **not a union of composition classes**: all 34 shell classes appear in it (top: (3,0,1,1) 7,946; (3,1,1,0) 7,938; (3,1,0,1) 7,938; (2,1,1,1) 7,644; (4,*,0,0) 3×5,110).
- Whole-class pivot rates need live-region [124,244,364,000) pivot attribution, which the unit log (k per 5,000 cols over interleaved classes) does not determine. Static bounds: plateau columns in classes PROVABLY <2% rate = **0%**; in classes whose rate COULD be <2% (lower bound) = **97.13%**. No verdict without new profiling.
- Decisive follow-up (resume): profile the 48 live units with the RUN-c engine (~3 h), or solve LP bounds from the unit-k log. Resume: `sage experiments/EXP-GPS-001/src/gps1_burst.sage --out <raw> --work experiments/EXP-GPS-001/work` after retargeting J0/J1 per unit.

## GPS-1 P3 (n=18 onset back-test) — not run (budget); no new cells measured.

## Unexpected observations (rule 8)
1. **70 pure-u quartics (4,0,0,0) are missing** from the sem column set → the true quintic shell starts at col **124,244**, not 124,314 (IDEAS-20260726 §2 estimate 654,080 → corrected: 654,150 quintic columns).
2. **ALL 20,349 pure-u quintics (5,0,0,0) are missing** (the entire class), i.e. the missing set is NOT confined to "balanced block compositions" as the a9 gloss had it — the pure-u (maximally unbalanced) class is entirely absent. Missing-set histogram (56 classes) in RUN-b raw.json; top: (5,0,0,0) 20,349; then the balanced (2,1,1,1)/(1,2,1,1)/(1,1,2,1)/(1,1,1,2) 14,406 each.
3. The burst is a *contiguous all-pivot window*, not a scattered yield spike — sharper than either the analysis.md "947-pivot burst" description or GPS-1's "last uncovered class" phrasing.
4. EXP-SIG-008 `sem_kernels.pkl` contains only {k3,k4,k5} (D3/D4/D5 kernel bases) — no D6 kernel basis survives anywhere on disk.

## GPS-4 P1 (nesting probe) — **NOT SCORED (infrastructure, rule 5; hypothesis untouched)**
What was measured (VALID):
- S9 = the n=9 subsystem of the n=12 seed-2 sem system under the pinned specialization (V9 = u_0..8 + first 3 vars of each x-block; W = remaining 6 vars → 0; no equation vanishes, no constant equation; 24 eqs, degs 12×2 + 12×3).
- S9 ladder: D3 def 1 / extra 1 / B 1; D4 def 88 / extra 88 / B 88; D5 def 564 (rank 10,218 vs sr 10,782) / extra 2,077 / B 2,077; D6 nrows 60,432, ncols 29,254, **rank6 = 28,805**, kernel6 = 31,627, K6 family 16,230, F3/F4 images 988 / 15,136 (misses 0).
Two gaps block the gate:
1. The n=12 D6 residual space (2,722-dim) cannot be formed: no D6 kernel basis was ever persisted (RUN-a probe), and reconstructing it (kernel-tracked staircase or mutual carry back-reduction ≈ 15–20 min) exceeded the turn budget.
2. The S9-side necessary-condition number residual_6(S9) needs the F5-image closure rank, whose bigint construction exceeded the 240 s cap.

Resume (both cheap now):
- residual_6(S9): rerun RUN-f with F5 images built as position-lists + m4ri stack (checkpoint after F4 exists in stdout timings; add `--skip-to-f5`): `sage experiments/EXP-GPS-001/src/gps4_s9_d6.sage --out <raw>` — 1 invocation.
- Full P1: regenerate the n=12 D6 kernel basis (mutual back-reduction of `EXP-SIG-008/work/sem_rank6/` carries, 4–5 invocations), reduce mod K6∪F345 (on disk: `sem_f345.pkl`, `sem_s2_base_*.pkl`), apply the RUN-e specialization map, score preserved rank vs ≥2,500 / ≤1,000.

## Notes
- S9 (specialized subsystem) is NOT the recorded n=9 sem system: e.g. S9 D6 ncols 29,254 vs n=9 sem 29,332; S9 D5 deficit 564 vs 909. residual_6(n=9 sem) = 2,615 remains the reference, per EV-SIG-005/006.
- All GPS-1 numbers derive from git-mirrored, sha256-verified carries and the bit-identical rebuilt system; no new rank matrices were measured for GPS-1.
