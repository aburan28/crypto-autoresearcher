# IDEAS-20260726 — Special exploitable structure for generic prime fields: five falsifiable hypotheses from the newest measurements

```yaml
handoff_echo:
  id: TASK-20260726-001
  from: idea-generator
  to: coordinator
  objective: "propose special exploitable structure for generic prime fields, grounded in the program's newest measurements"
  deliverables: [research/IDEAS-20260726-generic-prime-structure.md]
date: 2026-07-26
role: idea-generator   # proposals only; no hypothesis statuses changed, no experiments run
scope: toy-scale boolean chained Semaev family (m=t=3), n <= 21; prime-field transfer stated per hypothesis (AGENTS rule 7)
```

**Inputs read (all claims below anchor to these records):** AGENTS.md; ledger/SYNTHESIS-20260718.md (incl. Addenda 1–2); ledger/EV-SIG-007.yaml, EV-DREG-004.yaml, EV-SIG-005.yaml, EV-SIG-003.yaml; ledger/EV-SIG-008.yaml + experiments/EXP-SIG-008/RESULTS.md (destroyed on disk; read from the preserved git record, commits d1d36dd/e32afbcf); ledger/EV-SIG-006.yaml (destroyed on disk; read from commit f6fa31b0); ledger/EV-DREG-002.yaml, EV-DREG-003.yaml; experiments/EXP-SIG-007/analysis.md (2026-07-26 completion section); experiments/EXP-DREG-004/analysis.md; research/THM_BKKMV2.md; research/THM_INCBARRIER2.md; research/dreg-linear-law/FINDING_v2.md; experiments/EXP-FCP-001/analysis.md; ledger/proposals/IDEA-20260726-001..005.yaml (non-overlap check).

---

## 0. Evidence anchor table (the numbers every hypothesis below stands on)

| # | Quantity | Value | Source |
|---|---|---|---|
| a1 | n=21 D5 sem cell: ncols / nrows / rank / sr_pred | 778,394 / 279,048 / 265,950 / 268,674 | EV-SIG-007 (measurement COMPLETE; two-partition control IN PROGRESS — all n=21 sem numbers preliminary) |
| a2 | deficit_5(21) = A4_5 + residual_5 − 1 | 2,724 = 1,407 + 1,318 − 1 | EV-SIG-007 FINAL_numbers (dense-m4ri re-derivation, 2026-07-26) |
| a3 | Dead plateau then burst: cols [364,000, 449,000) fully dependent (17 k=0 units), then ONE burst unit [449,000, 454,000) k = 947, then rank frozen from col 454,000 (tail 324,394 cols, 65 k=0 units) | burst = 947 pivots after 85,000 dead columns | EXP-SIG-007/analysis.md; EV-SIG-007 unexpected_observations |
| a4 | Burst is tied to absolute column identity, not the chunk grid: C-forward control (split 389,197) reproduced it at [449,197, 454,197) = same columns shifted by the grid offset 197 | replicated | EV-SIG-007 two_partition_control.C_forward |
| a5 | n=12 D6 double-collapse: sem rank 138,570 vs column-matched null 149,410 vs sr_pred 156,520; sem defect exceeds null by 10,840; residual_6 = 2,722 INADMISSIBLE (null invalid); A5 closure 15,260 | deficit_6 sem 17,950, null 7,110 | EV-SIG-008 (git d1d36dd/e32afbcf), EXP-SIG-008/RESULTS.md |
| a6 | n=12 D6 sem support = 91.57% of C(24,≤6) = 190,051; missing 16,018 columns, ALL degree-6 (deg hist 1/24/276/2,024/10,626/42,504/118,578) | naive uniform-censoring rank-loss share would be 16,018·156,520/190,051 = 13,192; measured null deficit is 7,110 = 53.9% of that | EV-SIG-008 structural records |
| a7 | Support-induced share of sem D5 deficit: n=9: 369/909 = 40.6% (N1 column-matched null, extra 369, twice replicated); n=12: 0/1,321 = 0.0% (N1 null extra 0) | threshold somewhere in (n=9, n=12) at D5 | EV-SIG-006 (git f6fa31b0); EV-SIG-008 GATE 3 |
| a8 | Freeze-degree law (on-lattice): freeze = n/3 + 3 → n=9:6, 12:7, 15:8, 18:9; at freeze the null collapses to ncols − \|V\| exactly (n=9: 31,179 = 31,180 − 1); \|V_sem(9)\| = 6 = 3! (decomposition orderings), \|V_null\| = 1 | sr_pred baseline proved valid only BELOW freeze; "valid at D6 for n ≥ 12" prediction FALSIFIED at n=12 (a5) | EV-SIG-006; FINDING_v2 Part A |
| a9 | Column-formation law: cols(D) = up-closure of equation supports with degree slack; sem misses only top-slice monomials in balanced block compositions — deterministic, computable WITHOUT running the system | zero cancellation/parity deviation | EV-SIG-006 diagnosis (1) |
| a10 | deficit_5 on-lattice series (sem): 909 / 1,322 / 1,862 / 1,999 / 2,724 at n = 9/12/15/18/21; increments +413/+540/+137/+725; as fraction of sr_pred: 9.56% / 4.49% / 2.62% / 1.37% / 1.014% | relative weight decaying ×0.47–0.74 per +3n | EV-SIG-005, EV-DREG-002/003, EV-SIG-007 |
| a11 | residual_5 series: 344 / 878 / 1,158 / 974 / 1,318 at n = 9/12/15/18/21 (n=18 drop replicated, 2 seeds); residual_6 (INADMISSIBLE): 2,615 (n=9) / 2,722 (n=12) | residual_6(12) = 2,722 vs deficit_5(21) = 2,724: Δ = 2 | EV-SIG-005/003/007/008 |
| a12 | Pivot-share of columns (sem D5): 60.2% / 48.2% / 40.1% / 34.2% at n = 12/15/18/21 | dependent-column share GROWS with n | computed from EV-SIG-003, EV-DREG-001/002 anchors |
| a13 | Support fraction declines: 84.2 / 82.2 / 81.9 / 80.8 / 79.83% at n = 12/15/17/18/21 (null stays 100%) | | SYNTHESIS-20260718; EV-DREG-002/004 |
| a14 | DREG-004 rebuild (n=21 D5 sem, 29.55%): dependent-density k/c oscillating 57.9–94.8% in virgin territory (194k–230k), non-monotone; every aligned rank point bit-exact vs pre-incident lineage | oscillation, not collapse | EV-DREG-004 rebuild_20260725 |
| a15 | Cross-instrument continuity: SIG and DREG deficit instruments agree bit-exactly at every shared cell | | SYNTHESIS-20260718 Addendum 2 |
| a16 | Barriers proved: α ≤ 1/2 norm/moment ceiling (THM_INCBARRIER2 P3.3); box-saturation + MV law (THM_BKKMV1/2); TTN rank law χ(m) = C(2^{m−3}+2, 2), growth α > 1 (EXP-TTN-002); jet simulability (THM_JETBARRIER1); commutator kernel (THM_COMMUTATOR_KERNEL1); linear d_reg density c* ≈ 0.237479 (FINDING_v2) | do-not-repropose list | cited notes |

**Status caveats carried into every hypothesis:** (i) all n=21 sem numbers (a1–a3) are PRELIMINARY until the EV-SIG-007 two-partition control completes (C-forward 83%, C-reverse 10%); (ii) the n=21 DREG-arm deficit is UNMEASURED (EV-DREG-004, cell at 29.55%); (iii) residual_6 values (a11) are INADMISSIBLE as cascade evidence (no valid D6 null baseline at n=9 or n=12); (iv) everything is toy-scale boolean-family evidence (rule 7).

---

## 1. Framing: where "special structure" can still live

The proved barriers close: jet channels, NC correspondences, sparse/BKK exploitation of the S_m polytope (box-saturation), tensor-network compression, chord-richness/factor-base certificates below α = 1/2 by any norm method. What they do NOT close is the **internal linear algebra of the descent systems themselves**: the deterministic support law (a9), the syzygy-cascade scheduling (a3, a4), and the freeze/first-fall mechanics (a8) are measured, unexplained structure that sits *upstream* of every Macaulay/F4/F5 cost model. The five hypotheses below are ordered so that each is (a) mechanistically specific, (b) numerically falsifiable at n ≤ 21, and (c) explicitly marked for barrier consistency — including when the honest reading is that the structure is barrier-*reinforcing* rather than exploitable. Per the mission, each states: mechanism, concrete predictions, test boundary, falsification criteria, cheapest decisive experiment (sage, chunked ≤ 240 s invocations).

---

## 2. Hypothesis GPS-1 — Composition-class stratification of pivot yield: the dead plateau and the 947-burst are predictable class boundaries, and the dependent tail is harvestable

**Mechanism.** The sem Macaulay column support is a deterministic union of block-composition classes (a9: up-closure of equation supports; missing monomials concentrated in balanced compositions). Within the top-degree shell (at n=21 D5 the quintic shell is cols [124,314, 778,394) — 654,080 of 778,394 columns), the staircase's pivot yield is stratified by class: whole composition classes are rendered dependent by the multiplication closure of earlier syzygy families (K5, F3, F4 — the measured A3_5 = 800 / A4_5 = 1,407 closure at n=21), producing the 85,000-column dead plateau [364,000, 449,000); the burst is the LAST uncovered class entering the column order — 947 pivots whose monomials share a composition signature that the closure cannot reach; after it, every remaining class is covered (324,394-column fully-dependent tail). The burst's exact reproduction at shifted coordinates in the C-forward control (a4) already proves it is a property of column identity, not of processing order. Corroborating: the DREG-004 virgin-territory oscillation (a14) is what class boundaries look like mid-shell.

**Concrete predictions.**
- P1. Extracting the 947 burst pivots (carry_075, sha256-verified, git-mirrored blob 9a4e0452…) and classifying their monomials by block composition: ≥ 800 of 947 lie in ONE composition class; all 947 in ≤ 2 classes.
- P2. ≥ 95% of the 85,000 dead-plateau columns lie in classes whose whole-class pivot rate (measured over the full staircase) is < 2%.
- P3. A class-yield rule fitted at n=12 (46,709 cols) + n=21 predicts the recorded n=18 D5 late-column deficit-zone onset within ±5,000 columns.
- P4. Pivot-share decline (a12: 60.2/48.2/40.1/34.2%) continues: n=24 D5 pivot share ≤ 30%. The harvest ceiling at n=21 is 1/0.342 = 2.93× column-work reduction — growing with n but bounded by a constant factor per size.

**Test boundary.** Toy family n ≤ 21, D = 5, sem arm. The claim is about Macaulay-column scheduling of the descent system — NOT about S_m polytope sparsity (box-saturation stands) and NOT about d_reg: skipping certified-dependent columns leaves rank, quotient, and solving degree unchanged. Exploit ceiling: a constant-factor reduction of staircase reduce work (≤ 2.93× at n=21) for a solver that must build the same matrix; no asymptotic gain is claimed or expected.

**Falsification criteria.** (i) Burst monomials spread over > 5 composition classes with no common divisor/support pattern → class mechanism dead. (ii) n=18 onset prediction misses by > 5,000 columns or no boundary exists at n=18 → predictability dead (descriptive stratification may survive). (iii) n=12 class-yield table fails to reproduce the n=15 recorded unit-yield profile at class granularity → size-stability dead.

**Cheapest decisive experiment.** Stage 1 (forensics, no new cells): parse carry_075 + state.json unit log + the mirrored carry set; map pivot column indices → monomials via the a9 support law; classify; test P1/P2. Pure python/sage, 1–2 invocations ≤ 240 s. Stage 2 (class-yield tables): rebuild n=12 D5 sem with per-class yield logging (small: rank 28,097 — 1–2 invocations), back-test against recorded n=15/n=18 telemetry (0 new compute), then 1 invocation to emit the n=18 onset prediction and score P3. **Total ≈ 3–5 invocations.** No controls beyond the existing C-forward burst replication (a4).

**Barrier consistency.** Consistent with THM_BKKMV1/V2 (composition classes are column attributes of the descent Macaulay matrix, not polytope holes of S_m; the MV/box-saturation law is untouched), THM_INCBARRIER2 (orthogonal — no factor-base richness claim), TTN rank law (no tensor compression). Consistent with FINDING_v2's c* density: the harvest leaves d_reg invariant. **Verdict marking: barrier-consistent; genuine but constant-factor exploit ceiling.**

---

## 3. Hypothesis GPS-2 — The freeze-minus-one support-syzygy law: support censoring induces syzygies in ANY system on the sem support exactly at D = freeze(n) − 1, and the n=12 D6 null collapse is 100% support-induced

**Mechanism.** The semi-regular baseline is valid below freeze (a8). The measured violations all sit exactly ONE degree below freeze: at n=9, D5 = freeze−1, the column-matched null shows extra 369 (a7); at n=12, D5 = freeze−2, it is clean (extra 0); at n=12, D6 = freeze−1, it collapses by 7,110 (a5). Unifying law: at D = freeze(n) − 1 the last positive Hilbert piece is thin enough that the missing top-slice monomials (balanced block compositions, a9) remove pivot-carriers disproportionately — the missing columns are not average columns (measured: the null loses only 53.9% of the naive uniform-censoring share 13,192, a6) — and ANY generic system on the censored support develops support-induced syzygies at exactly that degree. At D ≤ freeze−2 the slack absorbs the censoring; at D = freeze the variety-collapse takes over (a8). If confirmed, the "D6 double-collapse" decomposes cleanly: null deficit 7,110 = support effect (baseline repair: the sr_pred baseline is valid below freeze−1 and support-correctable at freeze−1), and the sem-minus-null excess 10,840 = genuine equation-content cascade — the first admissible D6 cascade measurement.

**Concrete predictions.**
- P1 (decisive, binary): the FULL-support (old/T11-style) null at n=12 D6 — support 100% of C(24,≤6) = 190,051 — has rank == sr_pred(12,6) = 156,520 EXACTLY (extra_6 = 0). (This is the exact cell EV-SIG-006 scope-censored as "the decisive confirmation of the freeze theory"; SIG-008 falsified the prediction for the column-matched null, not this one.)
- P2: n=9 N1 column-matched null at D5, seed 2: extra = 369 exactly (the law is seed-stable; the 369 already appeared on two independent samplings — EV-SIG-006 RUN-c/RUN-d).
- P3 (bracket law): at D = freeze−1 the defect-per-missing-top-slice-column rate lies in [0.23, 0.90] (measured: 0.233 at n=9 D5; 0.444 at n=12 D6). At n=15: column-matched null at D6 (= freeze−2) has extra = 0 and rank == sr_pred(15,6) = 484,520 exactly; at D7 (= freeze−1) it has defect = rate × missing-count with rate in the band (missing-count computed exactly from the a9 law).

**Test boundary.** Toy family n ≤ 21 (decisive cell at n=12; bracket cell at n=15 is costed separately and gated). The hypothesis is about baseline validity and support effects; it makes NO claim that the support effect helps an attacker solve anything — support-induced syzygies are rank loss shared by random systems, i.e. baseline noise, not variety collapse. The genuine cascade content is what remains after the support correction (sem-minus-null delta).

**Falsification criteria.** (i) Full-support null rank ≠ 156,520 by ANY amount → support-censoring-only mechanism rejected; if it lands at 149,410 exactly (the column-matched value), the freeze−1 collapse is column-set-INDEPENDENT — a new intrinsic below-freeze failure of semi-regularity, recorded as a new anomaly that invalidates every D6 baseline on record. (ii) n=9 seed-2 N1 extra ≠ 369 → seed variance, law weakened to "typical". (iii) n=15 D6 column-matched null shows extra > 0, or n=15 D7 shows extra = 0 → the freeze−1 boundary law dead.

**Cheapest decisive experiment.** The n=12 D6 full-support null staircase: ncols 190,051, nrows 183,312 — same cost class as SIG-008 GATE 1's completed 174,033-column null staircase (~11 units at 18k cols, each well under 240 s): ≈ 12–14 invocations. Plus P2: n=9 N1 D5 seed-2 cell (ncols ≈ 12,615 — 1–2 invocations). **Total ≈ 14–16 invocations.** Control: system_hash + column-set audit vs the a9 law; two-partition consistency per the DREG protocol only if rank ≠ prediction (a PASS at exactly 156,520 needs no partition split — the prediction is the control).

**Barrier consistency.** Consistent with all proved barriers (it is a baseline-methodology hypothesis). Note the asymmetry of outcomes: PASS (rank == 156,520) repairs the D6 baseline and is barrier-reinforcing; FAIL at exactly 149,410 breaks the semi-regular model one degree below freeze for RANDOM systems — that outcome is not closed by any proved theorem and would become the program's sharpest open object.

---

## 4. Hypothesis GPS-3 — Cascade growth law: polynomial absolute growth, exponentially decaying relative weight (deficit_5 ~ n^1.3, residual_5 ~ n^0.73) — versus resumed super-linear growth

**Mechanism.** The D5 syzygy cascade is a boundary phenomenon of the chained construction: its absolute size grows polynomially (fit across the on-lattice series a10: deficit_5 ~ n^{1.295±0.15}; residual_5 ~ n^{0.726±0.2}, a11) while sr_pred grows ~×2.2 per +3n, so the cascade's relative weight decays geometrically: 9.56% → 4.49% → 2.62% → 1.37% → 1.014% of sr_pred (a10). Under this law the cascade is scar tissue of the chain — it can never touch d_reg or the LA exponent, consistent with d_reg(sem) > d_reg(null) (FINDING_v2 Part D) and the c* density. The live alternative the experiment discriminates against: the increments are erratic and the n=21 increment (+725) is the LARGEST on record — a second cascade family switching on (cf. GPS-1's burst), in which case growth resumes super-linearly and the decay reading was premature.

**Concrete predictions.**
- P1 (the cheapest unmeasured cell): deficit_5(19) ∈ [1,950, 2,450] (central ≈ 2,220; off-lattice wobble historically −2%); ratio deficit/sr_pred(19) < 1.37% with sr_pred(19) ≈ 178,800 (continued decay).
- P2 (recorded for the Coordinator's future n=24 dispatch; NOT run under this budget): on-lattice power law predicts deficit_5(24) ∈ [3,050, 3,450]; the super-linear alternative requires > 3,800 (increment exceeding +1,076, i.e. acceleration beyond the max observed).
- P3: residual_5(19) ∈ [1,000, 1,300] (interpolating 974 → 1,318); residual_5/sr_pred(19) < 0.73%.

**Test boundary.** Toy family, sem arm, D = 5, n = 19 (single size, single seed + null control). Does not settle the asymptotic law from one point; it decides between the two live readings (smooth sub-quadratic decay vs erratic/resumed growth) at the cheapest unmeasured size. Null-arm control included to keep the cell admissible (support-matched null rank == sr_pred exactly, as at n = 12/15/17).

**Falsification criteria.** deficit_5(19) > 2,500 or ratio ≥ 1.45% → decay law rejected (resumed-growth regime; reopens the exploit clause of H-DREG-001). deficit_5(19) < 1,900 → power law rejected the other way (stall/decline — strengthens the barrier side beyond the hypothesis). residual_5(19) outside [1,000, 1,300] → the residual sub-law rejected independently.

**Cheapest decisive experiment.** n=19 D5 sem full-rank staircase + support-matched null: sr_pred ≈ 179k, ncols ≈ 430–480k (≈ 55–60% of the n=21 cell): ≈ 30–35 fires for the sem + 15–20 for the null + ≈ 5 verification/closure invocations, all ≤ 240 s under the RAWCARR1 codec pacing demonstrated in EXP-DREG-004. **Total ≈ 50–60 invocations** — the most expensive proposal in this slate; recommend dispatch only after GPS-1/GPS-2 receipts (a confirmed GPS-1 class filter could cut the sem arm ~40–50%).

**Barrier consistency.** The decay-law outcome is exactly the barrier-consistent one (consistent with c* density, α ≤ 1/2 ceiling — a polynomially growing defect is asymptotically negligible). The super-linear outcome is NOT excluded by any proved barrier; if measured, it becomes the first evidence re-opening a below-generic cost route and would require review-xhigh before any status change.

---

## 5. Hypothesis GPS-4 — The 2,722 ≈ 2,724 near-equality: a universal primitive-cascade count carried by chain nesting — tested by specialization embedding and the first admissible residual_6

**Mechanism (shared-origin candidate).** residual_6(12) = 2,722 and deficit_5(21) = 2,724 differ by 2 (a11). Candidate shared origin: the chain's block-nesting (composition-typed support law, a9) gives restriction/specialization embeddings of smaller subsystems' syzygy spaces into larger ones; the "primitive non-rewritable" component — the part not generated by multiplication closure of lower-degree syzygies — is a slow-growing universal count (~n^0.14 across the two residual_6 points, increment ≈ +107 per +3n) that dominates both the D6-born residual at n=12 and the D5 total deficit at n=21 (whose closure part A4_5 = 1,407 is separately accounted). Alternative (coincidence) reading: the two numbers come from unrelated combinatorics (different D, different n, different baselines) and the match is noise — note BOTH numbers currently carry status caveats (residual_6 INADMISSIBLE; deficit_5(21) PRELIMINARY), so the hypothesis must first make both sides admissible before the comparison even means anything.

**Concrete predictions.**
- P1 (nesting probe, cheap): under the shared-origin reading, specializing the n=12 D6 residual space to the n=9 subsystem (restriction map pinned in the spec from the a9 composition law) preserves ≥ 2,500 of 2,722 dimensions and lands on a space containing the n=9 residual (2,615); under independence, preserved rank ≤ 1,000.
- P2 (slow law): the first ADMISSIBLE residual_6 — at n=15 D6, admissible iff GPS-2's freeze−1 law holds there (D6 = freeze−2 at n=15, null predicted clean) — lands in [2,780, 2,880] (linear extrapolation 2,829; power-law 2,808).
- P3 (discriminator against coincidence): if the equality is noise, residual_6(15) tracks the residual_5-scale wobble instead — i.e. falls ≤ 2,600 or jumps ≥ 3,100.

**Test boundary.** Toy family; n=12 → n=9 specialization for P1; n=15 D6 sem + column-matched null for P2 (gated on GPS-2 PASS at the bracket level). No asymptotic claim: even if the universal count is real, its measured growth (~n^0.14–0.7) is polynomial — barrier-negligible relative to exponential sr_pred. The value of the hypothesis is organizational: it decides whether the cascade has ONE primitive generator count or several independent ones.

**Falsification criteria.** P1 nesting rank < 2,500 → shared-origin embedding rejected. P2 outside [2,780, 2,880] → slow-law rejected. Both failing → coincidence reading accepted (recorded as resolved-by-measurement, anomaly closed).

**Cheapest decisive experiment.** Stage 1: rebuild the n=9 D6 closure (small; 2–3 invocations with the pinned h013 instrument) + specialization rank test on existing n=12 D6 artifacts (work/sem_kernels.pkl, sem_f345.pkl on disk) — 1–2 invocations. **Stage 1 total ≈ 4–5 invocations.** Stage 2 (n=15 D6, ONLY if GPS-2 predicts admissibility): sr_pred(15,6) = 484,520, sem ncols ≈ 546k — ≈ 70–75 invocations; flag as expensive, Coordinator-gated. Recommend: run Stage 1 now; Stage 2 only after GPS-2 and GPS-3 receipts.

**Barrier consistency.** Neutral-to-consistent: a polynomial universal count is asymptotically irrelevant against the c* density and the α ≤ 1/2 ceiling; nothing proposed conflicts with box-saturation or TTN. No overlap with the proved barriers.

---

## 6. Hypothesis GPS-5 — Variety-multiplicity freeze law: the sem system's freeze-degree collapse is exactly ncols − 3!, and the collapse front is predictable

**Mechanism.** At the freeze degree the semi-regular quotient freezes but a real system's quotient collapses to its variety size (a8): the n=9 null saturated at EXACTLY ncols − |V| = 31,180 − 1. The sem variety at n=9 has |V| = 6 = 3! — the decomposition orderings of P1+P2+P3 = R (summation symmetry S_3). This is genuine special structure of Semaev systems (the S_m symmetry is intrinsic — cf. the symmetric S_3 recursion in THM_BKKMV1/2): the freeze-degree rank is predictable EXACTLY as ncols − m! for a decomposable-target system, the collapse is concentrated in the top-degree slice, and at freeze the ideal contains a univariate elimination polynomial of degree m! — solvable by rooting. Exploit assessment is honest: the O(1) multiplicity shift changes nothing asymptotic (the LA to REACH freeze is the whole cost, and freeze = n/3+3 grows linearly), but the law explains the freeze mechanics bounding what ANY cascade can deliver, and the |V| multiplicity is exactly the kind of structure a descent-tree composition (IDEA-20260726-005) must price in.

**Concrete predictions.**
- P1: |V_sem(12)| = 6 exactly (enumeration over 2^24 boolean assignments; early-exit on a 7th solution falsifies).
- P2: |V_null(12)| = 1 for the recorded null constructions.
- P3 (conditional stage 2): at n=12 D7 (= freeze): null rank == ncols_null(D7) − 1; sem rank == ncols_sem(D7) − 6; the collapse front is concentrated in the top-degree slice, replicating the n=9 shape.

**Test boundary.** Toy family n=12; stage 1 is a pure enumeration (no matrices); stage 2 measures the freeze-front ranks at D7. No claim beyond freeze mechanics; explicitly no assertion that the multiplicity lowers solving cost (it does not — reaching freeze costs the full staircase).

**Falsification criteria.** |V_sem(12)| ≠ 6 → multiplicity law dead at the second size. Stage-2 ranks off the predicted ncols − |V| values by any amount → the n=9 exact-saturation law was single-size luck.

**Cheapest decisive experiment.** Stage 1: 2^24 enumeration with early exit, chunked by variable prefix — 2–4 invocations ≤ 240 s (16.8M assignments × ~20 curve ops; parallelizable by prefix). Stage 2 (optional, Coordinator-gated): n=12 D7 staircases, sem ≈ 490k cols + null ≈ 536k cols — ≈ 35–40 invocations. **Recommend stage 1 only in this wave.**

**Barrier consistency.** Fully consistent — the hypothesis strengthens the freeze-side accounting of the same barrier complex (linear d_reg, d_reg(sem) > d_reg(null)). The m! multiplicity is the only item here with a prime-field echo worth recording: prime-field S_3 decomposition systems (EXP-FCP-001 pilot) carry the same S_3-ordering multiplicity; a transfer check (count decompositions over GF(p), p ≤ 2^16) costs ≈ 2–3 sympy/sage invocations and can ride on the EXP-FCP-001 harness. Marked as a transfer probe, not a claim.

---

## 7. Ranking by decisiveness / cost

| Rank | Hypothesis | Addresses anomaly | Decisiveness | Cost (sage invocations ≤ 240 s) | Ratio |
|---|---|---|---|---|---|
| 1 | GPS-1 composition-class stratification | #1 (burst), plus harvest ceiling | High: P1/P2 are near-binary forensic checks on existing artifacts | 3–5 | Best |
| 2 | GPS-2 freeze−1 support-syzygy law | #3 (double-collapse), #5 (40.6%→0.0%) | High: one binary rank equality gates ALL future D6 cascade admissibility | 14–16 | Excellent |
| 3 | GPS-4 stage 1 nesting probe | #2 (2,722≈2,724) | Medium-high: rank test with a wide separation (≥2,500 vs ≤1,000) | 4–5 | Very good |
| 4 | GPS-5 stage 1 variety enumeration | freeze mechanics (context for #3) | Medium: confirms/kills the exact-saturation law at a second size | 2–4 | Good |
| 5 | GPS-3 growth law (n=19 cell) | #4 (growth laws) | High for the program's central open clause, but one point cannot settle a law | 50–60 | Expensive — dispatch after 1–4 |

**Sequencing / dependencies.** (i) GPS-2 PASS is the admissibility gate for GPS-4 stage 2 (n=15 D6 residual_6) and reframes GPS-1's closure accounting; run it early. (ii) GPS-1's class filter, if confirmed, cuts GPS-3's sem-arm cost ~40–50% — run GPS-1 first. (iii) GPS-4 stage 2 (≈70–75) and GPS-5 stage 2 (≈35–40) are deferred to a later wave pending stage-1 receipts. Total cost of the recommended wave (GPS-1, GPS-2, GPS-4-s1, GPS-5-s1): ≈ 23–30 invocations.

## 8. Explicit non-overlap and do-not-repropose statement

- NOT re-proposed (closed by proof or scoped rejection): jet/tangent channels (THM_JETBARRIER1, EXP-JET-001/EXP-JETB-001); NC path correspondences (THM_COMMUTATOR_KERNEL1, EXP-NCP-001); sparse/BKK or designed-support solves of S_m (THM_BKKMV1/2 box-saturation + MV law, EXP-BKK-001/EXP-STR-001); tensor-network compression (EXP-TTN-001/002 rank law); chord-richness/factor-base certificates below α = 1/2 (THM_INCBARRIER1/2, EXP-INC-001/EXP-INCB-001); isotypic splits (EXP-EQJ-001); elliptic nets (EXP-NET-001); Koopman channels (EXP-TRA-001); UQ-hardened crossbred/IC exponents (EXP-ICI-001); explicit-base PDP (EXP-R6-001).
- Distinct from ledger/proposals/IDEA-20260726-001..005 (multi-target amortization, endomorphism-invariant factor base, fiber-difficulty predictor, GGM certificate, descent tree): those are attack-composition proposals; GPS-1..5 are mechanism hypotheses about the descent systems' linear algebra, grounded in measurements taken after those proposals were written. GPS-5's multiplicity accounting is a priced input to IDEA-20260726-005, not a duplicate.
- None of the five claims crypto-scale or prime-field impact (rule 7). The only prime-field touchpoint is GPS-5's optional S_3-multiplicity transfer probe on the EXP-FCP-001 harness. Every hypothesis here, if fully confirmed at toy scale, still requires a separate prime-field re-validation before entering any ECDLP cost model.

**Honesty footer.** All numbers quoted from EV/experiment records are reproduced without alteration; where the source records carry status caveats (EV-SIG-007 preliminary pending two-partition control; residual_6 inadmissible; EV-DREG-004 cell incomplete), the caveats are restated in §0 and inherited by every prediction that uses those numbers. No commands were run, no artifacts created beyond this file, no statuses changed.
