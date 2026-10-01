# EXP-GFPN-05ff43 — Coordinator analysis (evidence review)

Written 2026-09-23 by the Coordinator under TASK-20260923-e52c88. It composes the independent review round opened by TASK-20260923-fe27e4. That round's plan and prior were frozen before any reviewer ran, and were archived in phase A of TASK-20260923-3b12c2 (commit 4c1773f1cee778ee830de7acd03a43c551facbfa). The two reviewer reports were archived in phase B (post-review receipt commit 6e08e10c0b4f41875bf370dd50b96f5eefe79f93):

- TASK-20260923-58953e (validator), joints K1-K4: `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-58953e/review-report.yaml`
- TASK-20260923-404bf9 (red team), joints K5-K7 and proves-too-much objects A-C: `coordination/goals/GOAL-GFPN-380702/reviews/TASK-20260923-404bf9/review-report.yaml`

`tools/check_review_independence.py` returned PASS. Two blindness disclosures were made and accepted, because no content passed between reviewers:

- The validator ran one early repo-wide grep that traversed reviews/. Its output was filtered, and no sibling path or content was shown.
- The red team disclosed its process listings and one regenerated, gitignored bytecode file.

The run set is 48 packages, bound by snapshot TASK-20260921-98561a (commit 520e7fea5628f2610c268074311a1b9986e8fab1). Read through CORR-20260923-d4220b, the tally is:

| outcome | runs |
|---|---|
| completed_valid | 34 |
| failed / infrastructure_error | 5 |
| failed / implementation_error | 3 |
| failed / resource_exhaustion | 6 |

The dispatching session re-checked two load-bearing reviewer claims ("dispatcher verification"):

- **The K5 n = m = 3 square-analogue degrees.** It re-ran the red team's own script. This is a reproduction, not an independent derivation.
- **The K7 frozen-text readings.** Pornin lines 138-149 and Joux-Vitse lines 278-290 say what the red team quotes.

The Coordinator had no shell and re-ran nothing.

---

## 1. Observation

### 1.1 Validity of the run set

- All 48 packages are present, and all 2122 snapshot hashes match.
- The frozen specification is byte-unchanged; it was committed on 2026-09-20, before any run.
- Seeds and target counts are recorded in the manifests.
- The aggregate RUN-GFPN-ca7b88 recomputes exactly: 30 runs, 29 cells, 1 excluded run (RUN-GFPN-61a67b, excluded correctly). The 17 non-cell packages are correctly outside it.
- Every exhausted cell is recorded not_measured, with D null and certificate.kind none.

The implementation was never committed before the runs. Run-time code is reconstructed from each run's logs and from the end-of-task committed version.

### 1.2 Per-joint composition against the frozen plan

| joint | owner | attested | artifact | attacked, not broken | residual / not attacked |
|---|---|---|---|---|---|
| K1 m = 5 absence classified | 58953e (validator) | **breaks** (honesty of scope) | `scratch/readcheck_output.json`; cell logs (`# RLIMIT_AS = 11811160064`); manifests lines 79/129/146/148; `run_wrapper.py` line 153; `symmetrize.py` lines 393-400 | D classification: every exhausted cell is not_measured, with D null and certificate.kind none. No artifact reads an exhaustion as evidence about D. D-5 lists every unattempted target. | The cap recorded (12 GB) is not the cap in force (11 GiB RLIMIT_AS, -t 4). ulimit failed in 29 validation/anchor logs, so their cap is unrecorded. Attempt counters contradict the logs. Arm (i) at m = 5, every arm at m = 5 on both control shapes, and arm (i) on contract targets at any m were never attempted, and nowhere recorded as not_attempted. |
| K2 heur_dflat and band follow mechanically | 58953e | **breaks** (narrowly) | `k2_rule_table` in the report | heur_dflat_pass is not_applicable for all 9 pairs. The band is null. No F1-F4 fired or was reported. The aggregate is correct. Stopping rules 3 and 4 were applied. | The modeled_note literal reason "heur_dflat_failed" was emitted as "heur_dflat_not_applicable" in one "band" field. This is undisclosed, but it is the more accurate reason. random_with_2torsion and random_without_2torsion were discharged only at p' = 4111, m = 4, and never for arm (i). |
| K3 supplementary cells kept apart | 58953e | **breaks** | RUN-GFPN-cdf887/d3f21e/d4415d manifest line 144; ca7b88 ladder-table lines 357/394/431; 18 unlabelled per-run tables | No supplementary value enters heur_dflat_pass, D_variation_across_ladder or the band. The 12 S/torsion supplementary manifests are fenced. No sentence reads supplementary D as heuristic evidence. | See the K3 leaks below. |
| K4 the n = 4 anchor | 58953e | **breaks** | `scratch/inv1` (independent derivation), `scratch/inv2` (crash reproduction, rc 139), `scratch/inv3` (25-bit trace) | See the K4 detail below: system identity, easier-system check and reference-row timing all hold. | Wall-clock timing is host-dependent. Joux-Vitse do not state whether their timed instance was consistent. |
| K5 arm (iii) validity | 404bf9 (red team) | **breaks** | derivation in the report; RUN-GFPN-42a000/-c16d20/-405554 build records; `scratch/k5k7/square_analogue_n3.json`, `_n4.json`; `scratch/k6/k6_objB_summary.json` | The relation path of arm (iii) (lifting and the R + T fix-up) is not incorrect, and its certificates re-verify. | See the K5 detail below. |
| K6 *_proxy fitness | 404bf9 | **breaks** | `scratch/k6/k6_objB_summary.json`, callgrind annotations | On the one cross-shape pair, the F4-only proxy is within 2x of executed core_f4 instructions (148.7 vs 81.3). Proxies recompute exactly from committed logs in 9/9 cells. | See the K6 detail below. |
| K7 cost-model premise | 404bf9 | **breaks** | Pornin lines 138-149; Joux-Vitse lines 278-290 and 353 (dispatcher-verified); box-vs-simplex derivation; `square_analogue_n3.json` (raw 384 vs S3 64) | The design note's own arithmetic, 2^102.4 x 2^40 -> 2^142.4, reproduces. | See the K7 detail below. |
| proves-too-much A | 404bf9 | did NOT prove too much | `scratch/objA/` (exact enumeration by own PARI/GP code; producer's unchanged cell path) | At p' = 11 (curve C2, N = 1400): 13 verified decompositions against N f = 11.29 (99% interval [4, 21]), with no false positive. Exhaustive test: 295/324 decomposable x-values recovered, with certificates re-verified. | All 29 misses are located and silent: 22 positive-dimensional 2-sum systems recorded as measured non-decompositions, and 7 degenerate msolve parametrisations accepted without substitution. Run at p' = 11 only. |
| proves-too-much B | 404bf9 | did NOT prove too much | `scratch/k6/k6_and_objB.py` part B | Arm (iii) refuses without rational 2-torsion, at three layers. | This object could not expose K5's defect. |
| proves-too-much C | 404bf9 | PROVED TOO MUCH | reading of committed raw-results | Every supplementary D equals the planted-orbit size in every cell: raw 6 on 60 targets, symmetrized 1 on 240. | The "flat" statistic discriminates nothing. |

**K3 leaks.**

- The raw m = 3 decomposition_success_rate is 1.0. The producer disclosed this.
- The aggregate's success_rate column carries 1.0 in the same three rows.
- The 18 supplementary per-run ladder-table.yaml and heur-dflat.yaml files carry no target_kind.
- The supplementary D is the planted-orbit size of an overdetermined system: 6 = 3! for raw, 1 for the symmetrized arms.
- Raw certificates are counted six times each. The distinct counts are 300 decompositions and 1020 lifted points, out of the 600 certificates and 1920 lifted points bound by the snapshot.

**K4 detail.**

- **System identity HOLDS strongly.** The validator derived the system independently: 4 variables, 5 equations of total degree 8, 495 monomials and 2471 terms. msolve reproduced an F4 trace identical, round by round, to all five RUN-GFPN-61bba9 logs.
- **Unit ideal matches the relation-search setting.** All five targets are unit ideals, which matches Joux-Vitse's relation-search setting.
- **Reference row fixed before the measurement.** The reference row (JV own-C F4, 17.01 s) was fixed in code before the 25-bit anchor ran.
- **Control FAILED its literal band.** The ratio is 0.470, outside [0.5, 2.0], on the fast side.
- **Reference row not frozen anywhere.** It was fixed in no frozen record.
- **"n=4" notation defect.** The control's "n=4" means the (n-1) = 4-point decomposition on F_{p^5}.
- **D-3 contradicted.** msolve -g 1 crashes inside F4 at the degree-9 round at p' = 65551, not during parametrization.
- **Thread count misstated.** The anchor manifests say "threads=4", but the anchors ran with -t 1.

**K5 detail.**

- **Arm (iii) as built is a norm.** It is the norm Q = A^2 - w^2 B^2 of the G2-invariant polynomial, and its group is (Z/2)^m x| S_m, not (Z/2)^{m-1} x| S_m. The Coordinator checked the single-flip step via the pair identity.
- **Its support equals arm (ii)'s.** 20349 = 20349 at m = 5, 495 = 495 at m = 4, 35 = 35 at m = 3.
- **Its F4 traces equal arm (ii)'s.** The committed m = 4 F4 traces are identical, and the m = 5 traces are identical from degree 17 to degree 32.
- **Its ideal degree equals arm (ii)'s in square analogues.** 64 = 64 at n = m = 3 at two primes (dispatcher-reproduced), and 4096 = 4096 at n = m = 4. The F_p-rational quotient gives 16 and 512.
- **FHJRV's form does not apply.** The Prop. 8 / Prop. 13 form needs b to be a square, and double-odd b is not (Pornin lines 871-875).
- **Not tested:** no m = 5 system of any construction was run by anyone. The F_p-rational arm was not built at n = 5.

**K6 detail.**

- The committed cross-arm ratio of 39.63 becomes:
  - 13.0-14.2 under measured CPU;
  - 81.3 under executed F4 instructions;
  - 148.7 under consistent accounting;
  - 123.5 with the source's inversion cost.
- The raw arm's construction is never charged.
- The 150-mul inversion constant is unsourced; Pornin gives about 2.57.
- The proxy has no bound direction.
- The producer's two proxies differ by a factor of 2^8.4.
- Instructions per proxy operation range from 6 to 101 across shapes.
- Proxy flatness restates the p-independence of the F4 shapes, while msolve's printed CPU moves by 11-17%.

These findings leave open whether an instrumented F_p-operation count is feasible. No committed F3 verdict exists.

**K7 detail.**

- **The design note's system is the symmetrized one.** Its total-degree-16 system with D ~ 2^20 is the S_5-symmetrized one.
- **The raw degree is larger.** The raw system's mixed volume is 5! 16^5 = 2^26.9.
- **The frozen prediction is mis-anchored by 120.** The frozen D_raw ~ 2^20, D_S5 ~ 2^20/120, D_torsion ~ 2^20/1920 and the band 2^121-2^132 are all off by 5! = 120.
- **The band omits a factor.** It omits the inverse success probability.
- **The scoring code hard-codes the wrong constants.** Scored against them, a correct rerun would fire F1 spuriously.
- **Re-anchored figures are model only.** They are the design note's model: 2^134.4 to 2^152.7 for a genuine torsion quotient, and 2^144.3 to 2^162.6 with the inverse success probability charged. None is a measurement.

---

## 2. Comparison

### 2.1 Against the frozen contract

- **Success criterion.** Met for no arm. It needs 3 or more completed m = 5 cells spanning 12 or more bits, and there are none. Clause B (arms with only an m = 4 fallback report heur_dflat_pass = not_applicable) is met for S5 and torsion_S5. It does not literally cover arm (i), which has neither m = 5 cells nor a random-target fallback. The producer's own rating, protocol_complete PARTIAL with a rerun required, is consistent with this.
- **Falsification criteria F1-F4.** None can fire; each requires completed m = 5 cells. By K5 and K7, F1 would fire *by construction* on a completed arm (iii) as built, and against the frozen constants, even under a correct measurement.
- **Invalidation rules.**
  - "Scoring a timeout as evidence that D is large" did not happen.
  - "Counting solutions instead of verified lifted points" is touched only in the supplementary raw cells, which count certificates once per ordering. It affects no contract success metric.
- **Blocking controls.**
  - n4_published_timing_anchor: FAILED on its literal band.
  - random_with_2torsion and random_without_2torsion: discharged at 1 of 3 primes, never for arm (i).
  - degenerate_symmetrization_identity, orbit_lifting_verifier and known_scalar_instances: passed.
- **Stopping rules.** D-4's single-rung stop is consistent with rule 2 if an OOM counts as "timed out"; rule 3 pairs "timeout or OOM", which supports that reading. For arm (i) the rule was never triggered. D-5's early stop deviates from rule 1, is disclosed, and changes no classification.

### 2.2 Against H-GFPN-9a29be

- **Not tested:** the statement's measurable content — D per arm at m = 5, HEUR-GFPN-DFLAT, and the band at p = 2^64.
- **Premise.** The statement says the design note's floor is "computed for the RAW descended ... system". That is false by K7 (CORR-20260923-27ce4f).
- **Mechanism.** Arm (iii) "giving (Z/2)^4 x| S_5" does not describe what was built (CORR-20260923-064d0d).
- **The ratio predictions survive re-anchoring.** D_raw / D_torsion >= 2^9 becomes 2^26.9 / 2^16 = 2^10.9, and D_raw / D_S5 >= 2^6 becomes 2^6.9.
- **The band prediction does not survive in its frozen form.** "Upper edge below 2^135" does not hold under the note's own model, re-anchored. That is model arithmetic, not a measurement. The hypothesis exists to replace that model with measured quantities.

### 2.3 Against the recorded coordinator_prior (TASK-20260923-fe27e4)

| prior item | recorded | outcome |
|---|---|---|
| K7 premise wrong | 0.70 | agreed; hand figure 2^134.4 confirmed |
| K5 arm (iii) not a valid test | 0.65 | agreed |
| K5 b-square question | 0.40 | realised: b is a non-square, so FHJRV's form is unavailable |
| K6 unfit for flatness and F3 | 0.70 | agreed |
| K6 fit as a within-shape relative indicator | 0.50 | agreed, on one pair |
| K4 genuine JV system | 0.75 | agreed, with an identical F4 trace |
| K4 literal FAIL | 0.55 | agreed |
| K4 "n=4" names a different object | 0.50 | agreed as a notation defect |
| K4 reference row not pinned before measurement | 0.40 | partly: fixed in code, not in a frozen record |
| K4 D-3 contradicted | 0.50 | agreed, by reproduction |
| K1 classification holds | 0.85 | agreed |
| K1 envelope defect | 0.50 | agreed, and larger than expected (11 GiB; attempt counters) |
| K2 holds | 0.85 | agreed on the load-bearing outputs |
| K2 modeled_note wording | 0.35 | agreed |
| K2 undischarged controls | 0.30 | agreed |
| K3 unfenced adjacency | 0.60 | agreed, with leaks beyond the disclosed one |
| object A proves too much | 0.30 | not realised |
| modal outcome ("inconclusive; amendment owed") | 0.70 | realised almost exactly |

The prior was recorded and non-blind, so this agreement is weak evidence as agreement. Each verdict rests on an artifact the reviewer built:

- an independent anchor derivation with an identical trace;
- a crash reproduction;
- committed identical supports and square-analogue degrees;
- measured CPU and instruction counts;
- frozen-text quotations with a degree derivation;
- an exact enumeration.

The prior anticipated none of the following, which the round found beyond it:

- the 11 GiB limit and the attempt-counter defect;
- the two silent loss paths in the m = 4 driver;
- a concrete replacement construction for arm (iii).

---

## 3. Inference

1. **Inconclusive.** Nothing about D, HEUR-GFPN-DFLAT or the p = 2^64 band is established, refuted or constrained. The m = 5 absence is scoped to: arms (ii) and (iii), the EcGFp5-shaped curve and p' = 4111 only, under an 11 GiB (11811160064-byte) RLIMIT_AS on each msolve 0.6.5 child running 4 threads, with F4 dying in the degree-33 round after about 836 s per target, and two targets per arm. Arm (i) and both control shapes were not attempted at m = 5. This is an infrastructure boundary, never evidence that D is large (AGENTS.md core rule 5).
2. **The protocol could not have discriminated even with more resources.**
   - Arm (iii) as built delivers arm (ii)'s system (K5).
   - The frozen prediction and scoring constants describe the wrong system (K7).
   - The proxy cannot score F3 (K6).
   - The anchor control failed its literal band while confirming system identity (K4).

   A rerun needs a versioned protocol_amendment made BEFORE it runs. Its design is TASK-20260923-aa277e.
3. **The mechanism is untested, and the lane is more open than the run set suggests.** In the red team's square analogues (toy scale, reviewer scratch; n = m = 3 reproduced by the dispatcher), a genuine F_p-rational (Z/2)^{m-1} x| S_m quotient realised the predicted 2^{m-1} drop exactly, and its m = 5 system is about 10x sparser than the one that exhausted the cap. This is recorded as KN-OPEN-9b4a2b.
4. **The m <= 4 random-target driver finds decompositions at the exactly enumerated rate at p' = 11.** Its two silent loss paths must be flagged before EXP-GFPN-659e34 reuses it. Its planned arm (iii) is the same norm construction. /run EXP-GFPN-659e34 therefore waits for the amendment design's ruling. This is a sequencing hold, not a closure.
5. **No closure and no security statement.** No reading of this run set as "the 2-torsion symmetrization does not help" or as "EcGFp5's 128 bits holds" is admissible. The re-anchored 2^134.4 is model arithmetic and not a finding about EcGFp5.

---

## 4. Limitation

- **Scope of every statement here.**
  - Curves: EcGFp5-shaped toy curves at p' in {4111, 262151, 16777291}, with matched controls at 4111 only, and anchors at 65551 and 16777291. Not EcGFp5 or EcMasFp5 themselves.
  - Degree: n = 5, with m = 5 attempted only for arms (ii) and (iii) at p' = 4111.
  - Solver and host: msolve 0.6.5 on the 2026-09-21 host (Xeon @ 2.80GHz, about 15 GB, no swap).
  - Transfer: none to p = 2^64.
- **Square-analogue degrees.** The K5/K7 values are reviewer scratch computations at toy size. At n = m = 3 they were reproduced by re-running the red team's script, which is not independent. At n = m = 4 they were not reproduced. The committed identical supports and identical F4 traces do not depend on them.
- **Re-anchored floors are model arithmetic.** They use the design note's conventions (D^2 floor, nominal 5 D^3, p^{2-2/5} systems).
- **Object A.** Run at p' = 11 only. Transferring its loss-path estimates to p' >= 2^10 is an untested extrapolation.
- **Anchor timing is host-dependent.** The reference is a 2010 Core 2 Duo. The producer's host ran at 2.80 GHz; the validator's at 2.10 GHz, where the anchor took 5.88 s.
- **Code provenance.** Run-time code is reconstructed. The implementation was not committed before the runs.
