# EXP-CERTBIN-4e92d7 (spec v1) -- analysis of RUN-CERTBIN-3b7e05

- **Composed by:** the Coordinator in /review-evidence (step 2), under DEC-20260923-4d7a19 NA-5.
- **Review round:** REVIEW-CERTBIN-20260923-c51f07 (plan and addendum 1).
- **Records:** EV-CERTBIN-6c3e0a (evidence) and DEC-20260923-f25b97 (decision).
- **Refutation artifact:** `experiments/EXP-CERTBIN-4e92d7/derivation-note-replay-forms.md`.
- **Claim tier:** toy. `sota_delta` is zero on every ECDLP cost axis. Parallel Pollard rho dominates, and so does oracle A per attempt at m = 2.
- **Cell:** n = 17, f = t^17 + t^3 + 1; m = 2; l = 9, V = {deg < 9} (polynomial basis); one random ordinary curve (A = 97044, B = 126251, #E = 130412 = 4 * 32603).
- **Solver:** the declared fixed-shape multilinear Macaulay elimination, at D = 4 (primary) and D = 3 (secondary, DR-8).

The four sections below are kept separate. **Observation** reports what the archived run and the reviewers' recomputations show. **Comparison** sets those values against the frozen thresholds, the controls and the priors. **Inference** says what follows and at what basis (derivation or empirical). **Limitation** says what does not follow.

Two quantities appear in the package but are not quoted here as evidence. The first is the M2 `tail_extremes` figure, which is floating-point roundoff (F-J3-3, OBJ-2). The second is C-UNIF's "pass", which is structurally unable to fail at this cell (F-J2-2, OBJ-10).

---

## 1. Observation

### 1.1 Admissibility (composition rule of the review plan)

- **J1 holds** (VAL-20260923-a679de). On 15 archived F-S3 instances at D = 3 and D = 4, a spec-literal construction equals the impl's matrices with 0 differing bits. The same holds for its column/row orders, op logs, four trace hashes, Z_D and replay first-zeros (100 of 100 pairs). Each named misreading (the tie-break, current vs original matrix, no multilinear reduction, ascending order) builds a different object, so the check can fail.
- **J2 holds** (VAL-20260923-a679de).
  - Every binding verifies. manifest_v2.yaml adds exactly the three R-5 fields.
  - The sampling layer regenerates exactly from the 13 frozen seeds.
  - A third, independent oracle agrees with the archived solution SETS on 6,306 of 6,306 instances.
  - Findings F-J2-1..F-J2-4 are design-level. None is attributable to the producer.
- **J7 holds** (VAL-20260923-5f9b82). Of 3,944 compared items, 3,944 agree. The J6 blind re-derivation (TASK-20260923-7a2cd4, sealed `rederivation.json`) and the run agree on:
  - 5 references and 100 F-S3 targets at D = 4;
  - s by three routes, the arm, rank_4, |Z_4| and "1 in R_4";
  - the four trace hashes, 20 match flags per target, ops_strict and the exact saving ratios;
  - a_k at every step for the 3 unsat references (8,015 steps).
  The comparator's negative control detects every injected fault (N1-N6).
- **J3 holds** (VAL-20260923-a679de).
  - M1-M4 and DR-1..DR-8 recompute from the per-target records with 0 mismatches: 688 retention cells, 110 hazard tables and 12 sizing entries.
  - No DR verdict flips under any alternative reading of I-4, I-5, I-11, I-12, I-14, I-15 or I-24 that is consistent with the specification text.
  - One secondary statistic outside M1-M4 and DR-1..8, the M2 tail figure, does not reproduce (F-J3-3).
- **J5 holds** (RT-20260923-29e7af).
  - O1: identical instances match at all four granularities, with whole-replay survival.
  - O2: the synthetic constant-column family shows its provably invariant 2323-step prefix exactly (min f_div 0.931062, equal to the bound).
  - O3: no satisfiable instance in any family has 1 in R_D.
- **J8 holds** (RT-20260923-29e7af) for the run package's own text.
- **J4 breaks AS A READING.** There is no replay defect: 0 mismatches at every pivot for all 6 references on F-S3, and on the F-RANDX and F-PLANT cross-scores. What the M2/P2 statistics measure is reported in 1.4.
- **Independence checker.** The dispatching session reports both checks passed:
  - `check_review_independence.py --plan` (with addendum 1) `--reports`: PASS on 4 reports;
  - `--blind-history HEAD`: PASS on 65 protected values (PD-R6).
  The TASK-20260923-918a6d receipt records both outputs verbatim.

### 1.2 Arm sizes (non-degenerate test targets; identical at D = 3 and D = 4)

| family | unsat | sat | degenerate |
|---|---|---|---|
| F-S3 | 386 | 607 | 7 |
| F-S3-REV | 386 | 607 | 7 |
| F-PLANT | 0 | 200 | 0 |
| F-RANDX | 361 | 634 | 5 |
| F-AFF-1 / 2 / 3 | 115 / 126 / 127 | 878 / 867 / 866 | 7 each |
| F-NULLF2 | 138 | 862 | 0 |

F-PLANT's unsat arm is empty by construction. SR-3 flags it UNDERPOWERED, as the run report does.

### 1.3 Primary cell: F-S3, D = 4, T_strict

- **M1, unsat arm.** Retention is 0/386 for each of U1, U2 and U3 (CP95 upper bound 0.009511). It is 0/347 for the modal reference, scored on targets 101..1000 (CP95 upper bound 0.010574). retention_family = 0.
- **First divergence.** The median f_div in both arms is 0.000374 (U1, U2, S1, S2) or 0 (U3, modal): divergence at step 0 or 1. The arm difference is not significant (Mann-Whitney p between 0.525 and 0.829).
- **Coarser granularities, unsat arm, D = 4.**
  - T_set retention is 0 for every reference.
  - T_rank retention_family is 0.342 (132/386, U1). It equals the frequency of the reference's rank value: the ranks 2672, 2671 and 2670 give 0.342, 0.130 and 0.0144.
  - At D = 3: T_set retention is at most 0.0052, and T_rank is 0.991 (modal).
- **M4.** H(T_strict) = 9.956 bits = log2 993, with 993 distinct traces in 993. Every family is saturated at log2 N at D = 4. h(P_sat) = 0.964.
- **M3.** The numerator is 0/386. The denominators are 0/115, 0/126 and 0/127 (F-AFF-1..3).
- **K.** K_sampled is 2668-2671 and K_exact is 2670-2672 per reference. K_rank = 17 for every reference at both D.
- **Saving and size, D = 4.**
  - ops_masked_full = 11,836,352 full-row XORs. ops_strict ranges from 331,893 to 352,418.
  - saving_strict is 33.59-35.66. saving_set is 1.658-1.660, and the identity C R / rank^2 holds exactly.
  - The pruned matrix takes 1,266,915-1,267,864 B dense. For U1 it is 2672 x 3796, with 415,368 B in CSR form.

### 1.4 Replay-hazard structure (J4; exact linear algebra, recomputed independently)

- **P2 set.** 26 (reference, pivot) pairs, of which 15 are in [0.4, 0.6]. The median h is 0.4817. 11 pairs have h = 0 exactly.
- **The 11 zero pivots.** Every one is a pivot whose linear part a_k literally repeats an earlier pivot's form:
  - U2: k = 1 and 4 repeat r15, and k = 3 repeats r14;
  - U3: k = 1..3 repeat r16, and k = 5..9 repeat r13.
  The predicted h = 0 is matched on 26 of 26.
- **The 15 in-band pairs.** These are 8 distinct (form, survivor-set) measurements. U1, S1 and S2 contribute identical triples, and U2 shares a_0. All 8 are single bits or low-weight sums of r12..r16.
- **Over all live pivots.** Per reference, 76-78 of the 86-90 pivots with S_k >= 1 are forced to 0 as repeats. The 10-13 rank-increasing ones all lie within their 99.9% binomial bands.
- **Target constraint.** All 1000 F-S3 targets and all 5 references have r_0 = Tr(x_R) = 0. The affine hull of the curve targets has dimension 16. Each reference has exactly one pivot whose form is dependent only modulo r_0 (outside P2). Each also has a pivot with a_k = e_0, which is constant on curve targets and accounts for K_exact - K_sampled.
- **Survival set.** Solving the replay conditions explicitly for all 6 D = 4 references returns exactly one point, r = x_R(ref).

### 1.5 "1 in R_D" (Proposition S side; J8, J2 and J7)

- **Unsat arm, D = 4.**
  - F-S3: 324/386 = 0.839 (CP95 [0.799, 0.875]). F-S3-REV is identical.
  - F-RANDX: 252/361 = 0.698 [0.648, 0.745].
  - F-AFF-1/2/3: 0/115, 0/126 and 0/127. F-NULLF2: 0/138.
- **D = 3.** 0/386 on F-S3, and 0 everywhere except F-RANDX (1/361).
- **Satisfiable instances.** 0 in every family at both D. PS1 holds.
- **D\* on the F-S3 unsat arm.** {4: 324, "not reached at D <= 4": 62}.
- **Split by x_R position (F-RANDX unsat).** In x(2E): 87/103 = 0.845. In x(E) \ x(2E): 54/90 = 0.60. On the twist: 111/168 = 0.66.
- **Independent certificates.** 17 of 17 sampled instances agree with the pipeline on "1 in R_4" and rank_4. These use code with no impl import. All 9 flagged unsat instances yield an explicit combination sum lambda_i mu_i f_{k_i} = 1 (1297-1378 rows), each re-verified by XOR.
- **A linear consequence.** sum_k Tr(t^k / x_R^2) f_k = v_0 + v_9 + Tr(B / x_R^2) holds on all 2,210 curve-algebra instances. It fails on 600 of 600 F-AFF instances.
- **J7, unsat subsample.** On the 35 unsat subsample targets, the re-derivation and the run agree on each "1 in R_4" value (31 true, 4 false).

---

## 2. Comparison

### 2.1 Frozen decision-rule labels, with the review reading beside each

The frozen labels stand as recorded. The reading column does not replace any label.

| rule | granularity, D | frozen label (mechanical) | reading recorded by this review |
|---|---|---|---|
| DR-1 | T_strict, 4 | STRICT P-GPU FALSIFIED at this cell | 0/386 and 0/347, with divergence at step 0 or 1 (f_div, OBJ-6). At the T_ops/fixed-schedule level, retention 0 is an identity: the survival set is {x_R(ref)}. It is not a sample statistic. |
| DR-2 | T_strict + P2, 4 | between | The retention clause (<= 0.01) holds. The M3 clause is not evaluable (0 vs 0). The hazard clause fails, and only through the 11 repeated-form zeros. No falsifying clause fires. |
| DR-3 | T_strict, 4 | E2 FALSIFIED | Decided by retention 0 < 0.5. There is also no r-independent block: the first r-dependent pivot is at step 0, and K_exact is rank or rank - 1. |
| DR-4 | fixed-schedule replay, P2, 4 | not supported, not falsified | This is a three-way threshold on n_rep, the number of repeated forms: SUPPORTED iff n_rep <= 1, FALSIFIED iff n_rep >= 16, here n_rep = 11. The label is NOT a statistical inconclusive on TS1. See 3.2. |
| DR-5 | T_strict, 4 | not applicable | retention_family = 0 lies outside (0.01, 0.5). |
| DR-6 | T_set pruning, 4 | one system per SM FAILS; thousands per warp FAILS | 1,267,864 B dense is 5.43x the 233,472 B SM budget. The CSR form, 415,368 B, is 1.78x. D = 3 fits (32,902 B) but certifies no unsat instance. |
| DR-7 | T_strict and T_set, 4 | strict replay not closed; T_set replay not closed | This means ONLY that no saving is below 1.5. It does NOT mean that either replay survives. See 2.3. |
| DR-8 | -- | primary: F-S3, D = 4, T_strict | Every D = 3 reading and every T_set, T_rank or T_ops reading above is secondary. |

### 2.2 Preregistered predictions P1-P9 (H-CERTBIN-a73f1c) against the data

- **P1 held.** E1 predicts retention <= 0.01. Observed: 0.
- **P2 missed.** TS1 predicts at least 90% in band. Observed: 57.7% (15/26). Its falsification threshold (median < 0.2) did not fire (0.4817).
- **P3.** No direction was predicted. E2's K <= 1 is not met (K is about 2670).
- **P4 held.** 0 T_set matches. PS2 is non-vacuous at D = 4 for F-S3, F-S3-REV and F-RANDX.
- **P5 held.** Both arms have median f_div <= 0.1, with no arm difference.
- **P6 not evaluable.** 0 against 0.
- **P7.** The E1 threshold (8.97 bits) is met, but saturation makes this uninformative, since every null meets it too. P-GPU's condition H <= h(P_sat) + 0.1 is not met.
- **P8 missed.** saving_strict of about 35 exceeds the predicted <= 10. saving_set, at about 1.66, is above the 1.5 closure threshold.
- **P9 held.** No D = 4 matrix meets either the 32 B or the 228 KB budget, full or pruned.

### 2.3 DEC-20260923-b85c30 NA-5 conditions for T_set-level replay

- The saving conjunct holds: saving_set is 1.658-1.660, which is >= 1.5.
- The retention conjunct fails: T_set unsat retention is 0 < 0.5 at D = 4, for every reference.

T_set-level replay therefore does not meet NA-5's survival condition at this cell. Strict replay is falsified at this cell by DR-1.

### 2.4 Against the nulls and controls

- **Instability.** Whole-trace T_strict retention is 0 against U1 in every null family, the same as F-S3. Median f_div against U1 is <= 0.00036 in every null family, against 0.00037 on F-S3. Zero against zero: the instability is NOT S_3-specific (J5 O3). The run does not credit S_3 with it.
- **T_rank spread.** It is S_3-specific: every same-support null has T_rank retention 1.0.
- **"1 in R_4".** It is S_3-specific at this cell: 0.839 on F-S3 against 0/115 to 0/138 in the same-support nulls, under the identical constructor.
- **O2 control.** A provably stable 93.1% prefix also gives whole-trace retention 0 (J5 O2). M1 = 0 therefore does not by itself separate "unstable from step 0" from "stable prefix, unstable tail". f_div separates them. It puts F-S3 at step 0 or 1 and O2 at >= 0.931.

### 2.5 Against the pre-data prior (specification coordinator_prior (a)-(g))

- **(a) Not overturned.**
- **(b) Not overturned.** K_rank = 17 and K >> K_rank, as predicted.
- **(c) Not overturned.** The median is near 0.5 and the 90% clause failed. The review sharpened this: the dependent-pivot hazard is exactly 0, never 1.
- **(d) OVERTURNED at D = 4 only.** T_rank retention is <= 0.342 because rank_4 itself varies across targets. At D = 3 the prior holds (0.991).
- **(e) OVERTURNED.** 84% of the unsat arm reaches 1 in R_4, against the prior's "most not".
- **(f) OVERTURNED on saving_strict** (about 35 against [2, 10]). saving_set came in as expected.
- **(g) Not overturned.**

The review-round prior was post-data (PD-R1). Its concurrence with J4, F-J2-1 and J8 is therefore weak evidence.

---

## 3. Inference

### 3.1 On the strict P-GPU premise (C3 of H-CERTBIN-a73f1c)

At this cell no unsat-arm subgroup target reproduced the whole T_strict trace of any unsat or modal reference: 0/386 and 0/347, CP95 upper bounds <= 1.06%. The predefined survival threshold (retention >= 0.5) was therefore not met over the tested instances, parameters, solver and budget.

The fixed-schedule (T_ops) form of the same statement is not statistical. At this cell K_rank = n = 17 for every reference, so the replay's survival set is exactly the reference's own x_R. That follows by derivation from the exact affinity of M_D(r) in r (derivation note, Lemma 2).

The T_strict statement itself is empirical, from one run on one curve.

### 3.2 On HEUR-CERTBIN-TS1 and C2's mechanism

- **The frozen verdict.** DR-4 is "not supported, not falsified". That label stands.
- **The formal statement is false at this cell.** TS1 quantifies over every pivot that is nonconstant over the sampled targets. A pivot whose linear part repeats an earlier form is nonconstant over the target sample, yet its hazard on the survivors is exactly 0 (derivation note, Lemma 3). Explicit instances are the 11 P2 pairs listed in 1.4, and 76-78 further live pivots per reference.
- **The independence clause fails by construction.** "Strict retention is about 2^{-K} with near-independent divergences" cannot hold when K (about 2670) exceeds n = 17 >= K_rank.
- **The balance clause is consistent where it can be tested.** It holds on the rank-increasing pivots: 15 of 15 P2 pairs in band (8 distinct forms), and every rank-increasing live pivot inside its 99.9% band.
- **The basis of these statements.** They are derivations about the archived op logs, checked against three independent computations. They do not change DR-4's frozen threshold or its label.
- **The restricted reading.** A P2 set limited to rank-increasing pivots modulo the targets' affine hull would read DR-4 "SUPPORTED" and DR-2 "E1 CONSISTENT". That definition contradicts the frozen text ("nonconstant over the family's non-degenerate targets", F-J3-2), so it is recorded as a reading and not as a verdict. A successor contract must preregister it before any data.
- **Where C2 stands.** C2's DIRECTION, a learned strict trace that is unstable under re-targeting and far from E2, is corroborated at this cell. C2's stated MECHANISM (TS1 as written, retention about 2^{-K}) is refuted at this cell. The correct mechanism is the rank of the affine pivot forms, which saturates at n.

### 3.3 On T_set-level replay and the rerank (DEC-20260923-4d7a19 NA-6 / DEC-20260923-b85c30 NA-5)

- **What the conditions give.** Strict replay is falsified at this cell (DR-1), and T_set replay fails NA-5's retention conjunct at this cell. By NA-5's own text, regime B (Stage 2) is then the only remaining route for P-GPU.
- **No closure is recorded.** The tripwire (review plan tier_ruling; TASK-20260923-918a6d LC-2) forbids closing regime-A replay on this round alone. The regime-A result is recorded as a measurement with an obstruction block. It is not a lane closure.
- **Stage 3 for P-GPU.** A regime-A n-ladder (Stage 3) would re-measure an identity for P-GPU. Whenever K_rank = n, fixed-schedule retention is 0 by Lemma 2, and K_rank = n held at every reference. A ladder in n therefore carries information for P-GPU only if K_rank < n were to appear. It keeps value for a different question, the "1 in R_4" rate (3.4).

### 3.4 On "1 in R_4" (Proposition S; a resource, not a verdict)

At this cell, 84% of unsat subgroup-target attempts carry an explicit degree-4 multilinear Macaulay refutation. That is 324/386, with 9 of 9 sampled cases independently certified by an explicit combination equal to 1. The rate is 60-66% for uniform x_R off x(2E), and 0% for the same-support nulls.

Proposition S makes the signal one-sided and sound: no satisfiable instance can carry it, and none did. It is S_3-structural at this cell, not a construction artifact.

The exhibited linear consequence explains one degree fall, but not the degree-4 refutation. With one linear equation the semi-regular series still gives D_reg 5. The mechanism is open (KN-OPEN-3c8f51).

Cost context, charged: at m = 2 the filter is dominated by oracle A, which uses 2^9 root-findings per attempt against about 3.3 x 10^5 full-row XORs. Its value is conditional on m >= 3 or the chained regime, where the rate is unmeasured.

The 16% "not reached" is a scope limit of the plain Macaulay D <= 4 closure. It is not D* > 4 in any solver's sense.

---

## 4. Limitation

- **One run, one curve, one V, one field degree.** n = 17, h = 4 and the polynomial-basis V. Nothing transfers to other n without HEUR-CERTBIN-TS3, which is untested. Nothing transfers to other curves, V, orders or pivot rules, to m = 3, to regime B, or to F4 critical-pair traces (TA-1..TA-7 of RT-20260923-29e7af). No deployed or Certicom curve is touched.
- **Unpermitted model fallback at execution (R-1).** The implementation was authored under an unpermitted model fallback (fallback_used true, model_verified false). Its admissibility rests on J1 and J6/J7, which hold.
  - All reviewers ran on the same model family as the executor (PD-R3, A-3). J6/J7 are independent of the implementation, not of one model's reading of the specification. J1's discriminating misreading controls and J4's exact algebra partly mitigate this.
- **Blind re-derivation scope (PD-R2, PD-R4).** It covers 5 references and 100 targets at D = 4 only. It does not test the sampling layer, which J2 audits by regeneration instead.
- **Weak controls.**
  - PS0 is vacuous on the unsat arm (F-J2-1). Row content there is guarded only by the arm-agnostic construction, C-SELF, J1 (6 unsat instances bit-identical), J6/J7 (38 unsat instances) and the 17 independent J8 certificates. That guard is sampled, not exhaustive.
  - C-UNIF cannot fail at this cell (F-J2-2).
  - C-REV and C-NULLS are completion records, not tests (F-J2-3).
  - C-PROPS has 2 independent failure modes, not 4 (F-J2-4).
- **Specification defects that change no verdict.**
  - The M3 bullet precedence overlaps at 0 vs 0 (F-J3-1).
  - DR-4 depends on the P2 definition, but only under readings the text does not support (F-J3-2).
  - The tail statistic is roundoff (F-J3-3). stats.binom_sf cannot resolve tails below about 1e-13.
- **The development runs (D-2 / R-3)** precede the trial plan and cannot be audited from archived bytes. J3 found no verdict that flips under any text-consistent interpretation, so no audit of /home/user/certbin-dev/ is commissioned.
- **Self-reported timestamps.** The trial-plan-before-first-elimination order rests on timestamps the executor reported.
- **Scope of "1 in R_4".** It is a Macaulay D = 4 closure statistic on subgroup (x(2E)) targets at this cell. It is not F4 step degree, not evidence for or against Semaev's Assumption 1 (this cell lies on its diagonal, so the observation is the assumption's content at work, not a test of it), and not a cost claim.
- **Baseline.** At this cell the whole discrete logarithm (about 160 rho or 362 BSGS group operations at q = 32603, by derived arithmetic) costs less than one D = 4 relation attempt. Oracle A dominates the per-attempt solve at m = 2 (OBJ-9).
- **Unreplicated.** Cross-curve replication was planned for a later contract, and none exists yet. Every empirical statement above is single-run.
