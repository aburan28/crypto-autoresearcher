# Novelty gates N1-N4: C3 "Exact all-target decomposition census from the log-domain spectrum (Li-Wan sieve)"

Field key: coding theory (ISD, AG codes, Riemann-Roch spaces as implicit factor bases). Gate agent run 2026-10-24.
Nothing was edited or created inside the repositories; everything below was written under this scratchpad `scout/` directory.

## 0. Verdict

**advances_lead.** Primary lead: `LEAD-ICE-decomposition-probability-audit` (open_next_step). Secondary: `LEAD-ICP-coincidence-harvest-structured-base` (open_next_step); and C3 evaluates the revisit clauses of `LEAD-EXO-dl-character-sum-pseudorandom` (exhausted_at_scale) and `LEAD-ICP-algebraic-membership-factor-base` (SO-ALGFB).

Why the audit lead is primary. Its next_action asks for "the exact count vector c_D and its variance against a size-matched random base" and points at EXP-RELN-dc761f. I verified from the specification (title and grep) that dc761f measures C34 short-cycle counts of the 2-LP multigraph against degree-preserving rewires and contains no c_D or count-vector measurement. C3 is the measurement the row asks for, and it adds h >= 4 and N > 2^20 beyond the stored enumeration evidence (EV-RELN-335cd2, m = 3, N = 2^14..2^20, inconclusive per the lead row; 5fa71b re-derives kappa_3 - 1 in about [-0.07, +0.01] from it).

Why coincidence-harvest is only secondary (post-check, Section N3b): C3 adds no decision rule there. a0830c already supplies the growth ladder, delta*(h) = 1/(2h-1) and the slope regression; 5fa71b supplies the kappa<->Delta identity, Parseval and plants. EXP-PFDR-ca5e01 (approved, 90 cells, bits 16-22, h = 2, planted {+-kG}; outcome O-MIXED per the lead row: 63 null / 16 intermediate / 11 underpowered cells, kappa in [0.889, 1.103]) already holds data on which the N-slope at fixed (theta, d) can be fitted at no new compute, and EXP-PFDR-bb0d26 (approved 2026-10-22, 45 cells, bits 20-28, r <= 3, five runs on disk) already is the dual F_p-additive label count to 28 bits. C3's dual Z/p arm therefore duplicates bb0d26 except for m > 2, and C3 reaches fewer bits than the PFDR engine runs on h = 2 (30-32 bits, no logs needed).

**Instrument-only caveat.** C3 is a measurement instrument, not a mechanism. No standing obstruction is escaped (SO-ALGFB and SO-TABLE are stated "NOT escaped" by the candidate, and its prediction is a null). At the IC operating point mean c ~ 1, i.e. B^m / m! ~ N, direct enumeration is already O(N) and the FFT also needs the N-point log table, so the FFT buys exactness and uniform ordered/multiset/distinct conventions, not an asymptotic saving (heuristic H1 below, not benchmarked). A strict reader could call it a duplicate of the combination 5fa71b + a0830c + 71a901; I keep advances_lead because the audit lead's own next_action is not met by its current spec.

What this report produced (vs read): I ran the 4 required + 3 extra `lead_atlas.py --match` and `build_frontier_map.py --match` queries (raw output in Appendix A); I read the lead YAMLs and ledger records named below; I verified the Li-Wan citation by WebSearch and the Li-Wan-Zhang / Cheng titles by WebFetch; I wrote and ran `_codingtheoryC3_raw/check_newton_identity.py` (Appendix B). I did **not** reproduce the candidate's pilot (`coding-isd/check_c3_spectrum_pilot.py`, `check_c3_kappa_identity.py`, outputs `c3_pilot_v2_summary.txt`, `c3_kappa_identity_out.txt` exist and match the description in the candidate text); every pilot number below is the candidate's, not mine. Reads beyond the three N3 records, disclosed: KN-OPEN-020, KN-FIND-ffe1df, IDEA-20260806-c5d183, IDEA-20260901-863e36 (required by N4); experiment specifications and index rows for EXP-RELN-dc761f, EXP-PFDR-ca5e01, EXP-PFDR-bb0d26 and DEC-20261022-f1efde (grep only) for verification.

## N1. Atlas collision

Runs: P1, P2, P3 = the three `match_phrasings`; P4 = my own ("multiset sum census characters of cyclic group: representation counts of a target as sum of base elements, variance and additive energy of the factor base"). Extras P5 (Fourier/character moment audit of coordinate statistics), P6 (AG-code minimum-weight / subset sums of points), P7 (break-even growth ladder). Raw: Appendix A. Score is the tool's lexical score; I list top 5 per run and what I read.

| run | rank | lead (score, disposition) | same mechanism? | what it covers vs C3 |
|---|---|---|---|---|
| P1 | 1 | LEAD-ICB-kic-golden-base-exact-decomp (19, open_next_step) | no | binary affine-flat bases with exact decomposition (SAT vs MITM). Lexical hit on "exact decomposition". No spectral or variance census. |
| P1 | 2 | LEAD-EXO-dl-character-sum-pseudorandom (17, exhausted_at_scale) | **same object family** | max_k abs(sum_{P in F} e(2 pi i k DL(P)/N)) is the sup-norm of C3's u_hat(t). Mechanism: super-random additive yield. C3 uses L^{2m} moments, structured sets beyond small-x, and a growth slope. Its `revisit_when` ("a structured set other than small-x shows R growing with N") is exactly the measurement C3 proposes; C3 does not answer the obstruction (predicts the same null). |
| P1 | 3 | LEAD-ICP-coincidence-harvest-structured-base (17, open_next_step) | **same mechanism** | forecloses: "pair-sum coincidence excess of structured factor bases", "additive energy of label-GAP bases gives free relations", "only attempt targets whose x(R) predicts a decomposition". next_action: break-even growth ladder, 3+ rungs 16-32 bits, planted controls, EXP-PFDR-bb0d26 log-GAP in the same instrument. C3 first_step is this ladder with a different instrument. |
| P1 | 4 | LEAD-ICB-cofactor-torsion-quotients (16, closed_obstructed) | no | binary cofactor-4 quotient labels; prime-order E(F_p) has no proper quotient. Not applicable. |
| P1 | 5 | LEAD-ICP-coppersmith-smallroot-semaev (16, open_next_step) | no | lattice small-root decomposition oracle for window/AP/GAP bases. Shares base families only; no count-vector census. |
| P2 | 1 | LEAD-ICP-coincidence-harvest-structured-base (19) | same mechanism | as above |
| P2 | 2 | LEAD-ICB-frobenius-orbit-factor-base (16, closed_obstructed) | no | binary Frobenius-stable bases; `revisit_when` asks for per-attempt decomposition probability above the birthday value at matched \|FB\| (a c_D-level question) but on Koblitz/subfield binary curves. C3 is prime-field/toy. Adjacent only. |
| P2 | 3 | LEAD-EXO-dl-character-sum-pseudorandom (14) | same family | as above |
| P2 | 4 | LEAD-ICP-isogeny-transported-relation-yield (14, open_blocked) | no (same measurable, different bases) | next_action wants coverage **and variance** of arity-3 yield, "a coverage or variance excess that grows with field size is the only outcome that would matter". Same statistic as C3 on isogeny-transported bases, which C3 does not test. |
| P2 | 5 | KR-IC-b0fcda (12, known_result) | no | Frobenius-invariant bases on subfield curves. |
| P2 | (8) | LEAD-ICP-algebraic-membership-factor-base (12, closed_obstructed) | **the SO-ALGFB row itself** | read in full; obstruction quoted in the SO section below. Its `revisit_when` ("a base raises coverage or variance with an excess that grows with N") is what C3 evaluates. Not escaped. |
| P3 | 1 | LEAD-ICE-linearization-excess-fb-prior (8, open_unexamined) | no | picks V to lower solving degree using the fitted excess e; relies on KN-FIND-007 (mean yield depends only on B). Different lever (degree, not count variance). |
| P3 | 2 | LEAD-ICE-decomposition-probability-audit (7, open_next_step) | **same measurable** | next_action: "reporting the exact count vector c_D and its variance against a size-matched random base" (BATCH-79a580 / EXP-RELN-dc761f). `discriminates`: variance beyond the random null names a clustering effect; no excess "confirms KN-FIND-007 to second order and retires the P(decomp) lane". C3 H-C3.1 is the same second-order statement. |
| P3 | 3 | LEAD-ICP-coincidence-harvest-structured-base (7) | same mechanism | as above |
| P3 | 4 | LEAD-ICB-factor-base-subspace-choice (6, exhausted_at_scale) | no | binary subspace choice; `revisit_when` "property of V predicting N_var or yield with a null-controlled effect that grows with n >= 31". Binary only. |
| P3 | 5 | LEAD-ICE-curve-presentation-invariance (6, open_next_step) | no | isogeny/model transport; states mean yield is a class invariant and the within-class variance claim was rejected at scope. |
| P3 | (6) | LEAD-ICE-semaev-yield-model-coset-typing (6, open_next_step) | partial (m! factor) | read in full. Coset typing changes the m! symmetry factor of the yield model; C3's distinct/multiset/ordered conventions price that factor exactly but do not test typed bases. |
| P4 | 1 | LEAD-EXO-dl-character-sum-pseudorandom (18) | same family | as above |
| P4 | 2 | LEAD-ICP-coincidence-harvest-structured-base (14) | same mechanism | as above |
| P4 | 3 | KR-IC-5a43e5 (13, known_result) | no | Semaev polynomials only define the counts. |
| P4 | 4 | LEAD-ICB-cofactor-torsion-quotients (12) | no | as above |
| P4 | 5 | LEAD-ICP-retained-setup-online (12, closed_dominated) | no | multi-target online accounting; C3 is not an attack stage. |
| P5 | 2 | LEAD-EXO-coordinate-statistic-leakage (17, open_next_step) | adjacent | census of coordinate statistics under the group law; best_measured "every structured additive set statistic is PGL_2-unstable and every stable multiplicative coset statistic sits at the random level (EV-ECDLP-81f4d4, strong)". Different statistic (action under P -> P+Q), same spirit of "structured set vs random level". |
| P6 | 1-5 | KR-IC-955fd6, KR-IC-5a43e5, KR-IC-081a58, KR-IC-46d822, KR-IC-8b9daa | no | no atlas lead mentions AG codes, Riemann-Roch spaces or code weight distributions (grep of ATLAS.md and KRMAP.md for "weight enumer", "minimum distance", "Riemann-Roch", "Li-Wan", "Fourier", "additive energy": zero hits except LEAD-EXO-dl-character-sum-pseudorandom for "Fourier"). |
| P7 | 1-3 | LEAD-ICP-coincidence-harvest-structured-base (13), LEAD-ICP-isogeny-transported-relation-yield (13), LEAD-ICE-decomposition-probability-audit (11) | same mechanism / same measurable | |

**What C3 does that the hits' forecloses phrases do not cover** (each item with the nearest recorded counterpart):
1. The exact computation route: one length-N FFT of the log-domain indicator plus the S_m cycle-index (Newton-Girard) combination gives c_D at every target, in ordered, multiset and distinct conventions, for any m. Not in any forecloses phrase. Counterparts: EXP-PFDR-ca5e01's C kernel counts h = 2 pair-sum coincidences exactly by enumeration; the sibling RELN enumerator (EV-RELN-335cd2) gives c_D at m = 3 by enumeration.
2. Log-domain characters (Pontryagin dual of E(F_p)) as the basis in which E_m, Var and kappa are evaluated. Counterpart: IDEA-20261018-71a901 uses the dual of the **x-line** (characters of F_p) with a Parseval-exact null; the log-domain basis is only used in LEAD-EXO-dl-character-sum-pseudorandom (sup-norm, small-x set).
3. Reach: h = 4, 5 and N up to 2^28 on the c_D-variance side. Stored evidence: EV-RELN-335cd2 m = 3, N = 2^14..2^20 (inconclusive per the lead row); IDEA-20261018-5fa71b re-derives kappa_3 - 1 in about [-0.07, +0.01] from it. Note the opposite direction: the PFDR engine runs already reach 30-32 bits (EV-PFDR-ad6274, 21 cells) without logs, so C3 covers **fewer** bits than the existing kappa evidence on h = 2.
4. Exact preselection gain for any feature of x(R). Counterpart: IDEA-20260830-c5c614 / H-PFDR-1b2386 (the "one door conservation leaves open"), forecloses phrase "only attempt targets whose x(R) predicts a decomposition". Same question; C3 gives an exact evaluator.
Items 2-4 are instrument reach, not mechanism. Heuristic H1 (mine, from cost counting, not benchmarked): at the IC-relevant operating point mean c ~ 1, i.e. B^m / m! ~ N, direct enumeration of all m-sums costs O(N) as well, and the FFT additionally needs the N-point log table (an N-step walk). The FFT therefore buys exactness and a uniform treatment of conventions, not an asymptotic saving, except for B^m / m! >> N.

## N2. Known results

Raw: Appendix A (frontier_1..7). Top KR hits for the three required phrasings and mine: KR-IC-73db3f, KR-IC-b0fcda, KR-IC-5a43e5, KR-IC-5931ee, KR-IC-8b9daa, KR-IC-46d822, KR-IC-49c882, KR-IC-081a58, KR-RHO-7d93f6, KR-RHO-46c2c6, KR-IC-fbdb61, KR-RHO-fb88e6, KR-RHO-0528e7, KR-RHO-13bf67, KR-RHO-5b1c0a, KR-IC-f5c584.
- None states the instrument or its outcome. Grep of KRMAP.md for "additive energy", "Fourier", "character sum", "weight distribution", "Li-Wan", "elliptic code", "cycle index", "Parseval", "minimum distance": no hit.
- Closest by content: **KR-IC-5931ee** (Yokoyama-Yasuda-Takahashi-Kogure: under stated statistical assumptions about decomposition, naive Semaev IC over F_p costs at least generic; algebraic bases of Petit-Kosters-Messeng, Amadori-Pintore-Sala, Kudo et al. work only at small parameters). C3 tests a second-moment form of such an assumption empirically and, by its own prediction, agrees with the KR row. The KR-IC-5a43e5 row (Semaev polynomials) says novelty "must lie in representation, factor base, elimination or solver, never in 'use summation polynomials'"; C3 proposes a new instrument for the factor-base question, not a new representation, base, elimination or solver.
- Outside KRMAP, the technique is classical mathematics, not a program result: counting m-subset sums by the Fourier transform and Newton-Girard identities. I checked it numerically (Appendix B): the distinct-subset count from the cycle-index combination of power sums u(kt) equals brute force for m = 2..5 on random subsets of Z/97, Z/101, Z/211, and the pair-coincidence identity C(F) = sum_s binom(c_2(s), 2) holds (31 = 31). For a **single** set D the Li-Wan sieve reduces to this classical identity; Li-Wan's generality (different sets per coordinate) is not used.
- So by the rule "a KR hit means known_result unless you can state exactly what is new": there is no KR hit on the object; the identity is known; the application (growth-slope fit of exact c_D moments on window/x-GAP/subgroup/coset bases of prime-order curves) is new only as an instrument relative to the ledger (N3).
- Unreconciled item (heuristic H2, my observation, not tested): EV-ECDLP-f83a17 reports R = C_EC / C_null flat at about 1.28-1.34 for the sup-norm character-sum statistic, while C3 predicts moment ratios in [0.95, 1.05] and its pilot has var/null in [0.887, 1.074]. They are different statistics, but C3 should state whether R = 1.28-1.34 is explained by the null (for example a non-negation-symmetric random null, since x-defined bases satisfy D = -D and make u_hat real) before treating the moments as the sharper instrument. This is a methodological request to the candidate and is **non-blocking** for the gate verdict.

## N3. Ledger

Index greps (proposals.jsonl, hypotheses.jsonl, experiments.jsonl), terms: additive energy; Li-Wan / distinct coordinate / cycle index; weight distribution / elliptic code / AG code; log-domain / Fourier spectrum / FFT; count vector / c_D; kappa; coincidence; preselect; break-even; P(decomp) variance; m-fold / E_m. **Zero hits** for Li-Wan, distinct-coordinate, cycle index, weight distribution, elliptic code, AG code in either index (the coding-theory ingredient is not in the ledger). FFT hits are ML-KEM dual-attack records (unrelated).

Hits that may be the same object (id, status, first 100 characters of claim):
- IDEA-20261018-5fa71b (proposed): "BRIDGE. c(R) = h-sum count vector of a base, mu its mean, Delta = Var/mu. (I1) PFDR kappa_h (IDEA-20261017-0" **[opened]**
- IDEA-20261018-71a901 (proposed): "Prime-order E/F_p, m=3, B=ceil((6N)^(1/3)), x-interval / QR-class / small-height bases, N=2^14..2^22. F(x)=c_D" **[opened]**
- IDEA-20261018-a0830c (proposed): "BRIDGE of IDEA-20261017-bbc53e (law), EXP-PFDR-ca5e01 (design) and nine leads' stated bounds. (i) An excess X" **[opened]**
- IDEA-20261017-bbc53e (proposed): "Stage: relation decomposition by coincidence harvest. Relations needed are c*U (c in 0.92..1.0; U = base poin" (source of delta*(h) = 1/(2h-1))
- IDEA-20261017-077f12 (proposed) / H-PFDR-011a4b: "R1 labels, stage relation decomposition (table-table coincidences, h=2, i.e. TT3/TT4). On prime-order E/F_p let F" (EXP-PFDR-ca5e01 source)
- IDEA-20261017-078074 (proposed) / H-PFDR-727bfc: "R1 labels, stage factor-base membership. Let A = {c_1 P_1 + ... + c_r P_r : |c_i| <= T}, r in {1,2,3}, P_i points" (EXP-PFDR-bb0d26 source, log-GAP)
- IDEA-20261017-90d9c5 (proposed): "Stage: collision structure inside relation decomposition. Replace the stored table of S = B^h h-sums by disting"
- H-PFDR-2765d2 (specified): "On prime-order ordinary curves E/F_p with log2 p in 20..32, generated by generate_prime_order_curve(bits, c, p_f" (the 30-32 bit runs)
- IDEA-20260830-c5c614 (proposed) / H-PFDR-1b2386 (proposed): "(A) WHAT IS ALREADY CLOSED, SO THAT THIS IS NOT MISTAKEN FOR IT. KN-FIND-007 fixes the mean per-target decompos" (target preselection)
- IDEA-20260830-21e7c4 (proposed) / H-ICEX-c273c2 (proposed): "(A) THE OBJECT IS DETERMINISTIC. For a factor base V of B x-coordinates, the signed point set W = V union -V," (P(decomp) is an exact integer ratio)
- IDEA-20260815-f9e978 (proposed) / H-RELN-62a482 (specified): "GOAL-RELN-001 audits P(decomp) versus factor-base size. Every formulation in the lane treats P(decomp) as a s" (distribution over targets)
- IDEA-20260906-1f6bfe (proposed): "(A) THE QUESTION THIS INSTRUMENT DECIDES. For the decomposition-count vector c_D(r) of a size-B base D at arity" (symbolic regression on c_D statistics)
- IDEA-20260920-b6ad24 (proposed): "REPRESENTATION CLASS AND ATTACK STAGE ... R1 ... One-step additive branching b forces every fibre to have DOUBLING" (additive energy floor)
- IDEA-20261002-760272 (proposed): "On prime-order short-Weierstrass curves over the same toy prime, one with j = 0 and one with generic j, the add" (additive energy of seeds)
- H-PFDR-d3c527 (proposed): "SETTING. G is generated by P and has prime order N. A KEYED LEAF JOIN uses public maps alpha and beta from G to" (keyed additive energy, Fourier dual)
- H-MONO-663fb4 (supported, scoped): "SCOPE: prime fields F_p with p in [100, 3000]; E(F_p) as a finite abelian group; factor bases FB that are symmetri" (N_m as m-fold convolution)
- H-RELN-940f14 (specified): "On the honest two-large-prime summation multigraph produced by the EXP-RELN-c5a377 v4 generator" (name collision only: its kappa is the budget ratio, not the coincidence excess)
- Experiments (experiments.jsonl): EXP-PFDR-ca5e01 "exact nontrivial pair-sum coincidence counts of window (d = 1) and rank-d label-GAP" (approved, h = 2, bits 16-22, planted {+-kG: 1 <= k <= L}); EXP-PFDR-bb0d26 "exact nontrivial pair-sum coincidence counts of the x-label sets of rank-r log-GAP bases" (approved); EXP-RELN-dc761f "Short-cycle enrichment of the honest 2-LP summation multigraph against the degree-preserving rewire null" (review_required).

Decision from the 3 opened records (Hit = same object, in part):
- **5fa71b** already states the exact identity "kappa_h = (Delta_D + mu - 1)/(Delta_null + mu - 1)" (I1), the Parseval tie of the periodogram energy to Delta (I4), the plant table (cofactor coset, log-GAP, sine), and bounds kappa_3 from EV-RELN-335cd2 ("Delta in band at four rungs, N = 2^14..2^20, m = 3"). C3's "kappa is exact" and "Var = E_m/N - mean^2" are the same algebra in another basis.
- **71a901** already runs a Parseval-exact Fourier audit of c_D (m = 3, N = 2^14..2^22, window/QR/small-height bases) with a blocking positive control and a CM control. It uses the F_p x-line characters and deliberately excludes the E-log (its multiplicative arm reads the F_p^* index of x, "never in E"). C3's log-domain basis is the part it does not do.
- **a0830c** already fixes the decision rule C3 calls H-C3.2 (an excess matters only if it grows as N^delta with delta >= delta*(h) = 1/(2h-1); required ratio R* = 6.35, 3.03, 2.21 at h = 2, 3, 4 over bits 14..22), the slope regression with planted gamma recovery, and "null cells at 2% give a 95% bound delta <= 0.02, a 15x sub-break-even closure".
- Verified from the specs: EXP-RELN-dc761f measures C34 short-cycle counts against degree-preserving rewires (grep finds no c_D or count-vector measurement), so C3's claim that dc761f is not the c_D measurement is correct; but the c_D variance at m = 3 up to 2^20 is already in EV-RELN-335cd2, so the gap C3 fills is h >= 4, N > 2^20, and exactness.
Conclusion: same object as 5fa71b + a0830c + 71a901 + the open lead's next_action; the log-domain exact instrument and reach are the delta.

### N3b. What already exists on the two PFDR experiments (post-check, grep and listings only)
- EXP-PFDR-ca5e01: runs RUN-PFDR-936605, -93c865, -b7c582, -c08b70, -e15482, -eb4733 and report run-20261021T1629Z exist. Its spec's secondary analysis is the slope of log kappa on **theta** (base-size axis), not on N at fixed (theta, d); grep of the report directory for "slope"/"delta_hat"/"growth with N" finds nothing. So the N-slope is not yet reported (consistent with the lead's "growth with N not measured"), but a0830c Stage 1 would obtain it from these outputs at no new compute for h = 2, bits 16-22.
- EXP-PFDR-bb0d26: approved by DEC-20261022-f1efde (five trials: selftest RUN-PFDR-e44a19, census-toy-main RUN-PFDR-4d8c71, ...); runs RUN-PFDR-089edc, -243425, -4d8c71, -cd03e2, -e44a19 and reports run-20261022T1218Z, run-20261023T2211Z exist; index row: 45 cells, bits 20 to 28, r <= 3, 256 <= n <= 4096. I did not read the outcome. The lead row still lists it as "scheduled", so the lead YAML may be stale.
- Effect on C3: the h = 2 growth question and the log-GAP/Z-p arm are covered or imminent; what remains for C3 is h >= 3, the c_D-variance side, the log-domain basis, and exactness.

## N4. Notation change (IC / factor base / representation / coordinate candidate)

Pair as C3 states it: base **defined** in R1 (x-coordinate predicates: window, rank-d x-GAP, subgroup, coset), **evaluated** in the log frame (indicator 1_D on Z/N, N = #E(F_p) prime), operation set = translation by factor-base elements. Trichotomy class (c5d183): Class I, partial action.
- The log frame is the identity coordinate on G: P -> log P is a bijection, so it is the **injective** branch of the c5d183 rigidity theorem (a map that propagates under the full translation action is constant or injective; prime N has no proper subgroup). The Fourier transform on Z/N is unitary (Parseval), a change of basis, not a projection. Every quantity C3 computes (c_D at all targets, E_m, Var, kappa) is a function of the pair (G, D) alone, independent of the representation in which D was written. So the pair is **not** a new arithmetic; it is PAIR(R1 labels; translation by base elements) of IDEA-20261017-077f12 / 5fa71b / a0830c, seen through its Pontryagin dual.
- Against IDEA-20260901-863e36: forced excess arises only from block systems of the operation group, index d giving kappa = d; for translations on a prime-order group there are none (C2 there reproduces the rigidity theorem). C3 therefore measures only the unforced residual, which is also the stated scope of 5fa71b ("none exist on the prime-order subgroup") and of the open lead. Not a restatement of a rigidity result: it measures the residue those results leave open. Equally, it creates no object they do not already classify.
- Against KN-FIND-ffe1df: Theorem C (exact sum-compatibility + associativity forces a surjective homomorphism, impossible for prime N) is untouched; its Proposition 2 of the underlying derivation (the dlog-interval pullback reaches eps ~ 1/2 on every prime-order group, closed only by a definitional cost restriction) is the same fact as C3's own exclusion rule: a log-domain excess on group-defined bases (planted `{+-kG}`, log-AP, bb0d26 log-GAP) is a **known-log pool** (LEAD-ICB-generic-table-oracle, H-BINSTD-1447cf) and cannot be used without the DL. C3 states this exclusion; it is the recorded result in new notation, applied correctly.
- Against KN-OPEN-020: the tested bases (interval, rank-d GAP, subgroup, coset) are the explicit/bounded-degree classes the program scopes out (the bounded-degree theorem, IDEA-20260801-021). The open class named there (high-degree interpolation descriptions, implicit membership, target-dependent descriptions) is **not** tested; C3 proposes no such base. A null on the tested bases confirms the scoped negative's second-moment channel only.
Result: no new (representation, operation set) pair; no recorded rigidity result is restated, none is circumvented.

## Standing obstructions touched (verbatim obstruction.statement, Scope clause included)

- SO-ALGFB, LEAD-ICP-algebraic-membership-factor-base (closed_obstructed, theorem): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B." revisit_when: "KN-OPEN-020 is answered positively (a size-B set with sub-B-degree membership surviving substitution), or a base raises coverage or variance with an excess that grows with N." **Not escaped** (C3 evaluates the second clause; predicts none).
- SO-TABLE, LEAD-ICP-generic-table-decomposition (closed_obstructed, theorem): "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p." **Not escaped**; harvested coincidences remain table relations.
- LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale, measured; no Scope clause in the row): "Measured the character-sum constant against a matched random null at 2^20-2^26 (EV-ECDLP-f83a17): R = C_EC/C_null is flat at about 1.28-1.34, i.e. the curve behaves like a random set up to a constant; all six standard analytic proof routes are closed (KN-FIND-e7a3b1), so neither a proof nor a measured bias exists. EXP7 Fourier flatness (8-14 bit) found no candidate predicate." revisit_when: "R trends upward with p beyond 2^30 on the same matched null, or a structured set other than small-x shows R growing with N." C3's bases are "structured sets other than small-x" (window x-GAP, subgroup, coset), but it measures moments, not R, and reaches 2^28 not 2^30. Does not answer the obstruction.
- LEAD-ICB-generic-table-oracle (closed_obstructed, theorem), clause used by C3's exclusion: "Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf)." Scope there: "all binary and Koblitz curves, one target, setup charged"; C3 applies the clause to prime-order toys by analogy.
- SO-GEN (LEAD-RHO-generic-sqrt-lower-bound): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). ... Scope: all generic algorithms, any field, any r." C3 is not an algorithm; no escape claimed.

## Citation verification (provenance)

- J. Li, D. Wan, "A new sieve for distinct coordinate counting", Sci. China Math. 53(9):2351-2362 (2010), DOI 10.1007/s11425-010-3121-9: **retrieved** (WebSearch this session). Verified content: the number of terms drops from 2^{C(k,2)} (inclusion-exclusion) to k! and to p(k) in the symmetric case; later used for the distance distribution of Reed-Solomon codes; multiset extension by Li-Yu (arXiv 1909.10898).
- J. Li, D. Wan, J. Zhang, "On the minimum distance of elliptic curve codes", arXiv 1501.01138: **retrieved** (WebFetch abstract). The abstract gives an explicit minimum-distance formula for ECAG codes when the evaluation set is at least 2/3 of the group order, via a sieving technique of the first two authors. It does **not** mention counting minimum-weight codewords.
- Q. Cheng, "Hard Problems of Algebraic Geometry Codes", arXiv cs/0507026: title, author and the NP-hardness of minimum distance and ML decoding for an elliptic-curve code family **retrieved** (abstract). "Theorem 1" and the statement that c_D(R) equals the number of minimum-weight codewords of C_L(D, R+(m-1)O): **recalled / not verified** (PDF is compressed and unreadable by the fetch tool). This link is an interpretation with no cost-model consequence; the novelty verdict does not depend on it.
- The candidate marked its provenance "retrieved"; only the first two citations are confirmed as retrieved here, and the third only at title/abstract level.

## Candidate claims I did not reproduce

Pilot numbers (42 structured cells var/null in [0.887, 1.074], 3 cells with |z| > 2.5, slopes delta_hat -0.004..+0.018 with se <= 0.019, planted log-AP delta_hat 0.50/0.68/0.78): present in `coding-isd/c3_pilot_v2_summary.txt` (read, not re-run). Predictions (E_m and variance ratios in [0.95, 1.05], delta_hat in [-0.02, 0.02], preselection gain <= 1 + O(N^{-1/2})) are the candidate's predictions, not outcomes. The conditional dispositions listed in its `outcomes_to_dispositions` would be inferences, not measurements, until the ladder is run.


## Appendix A. Raw --match output (verbatim)

Environment: LEAD_ATLAS_CRYPTO=.../scratchpad/crypto-main LEAD_ATLAS_CRYPTANALYSIS=.../scratchpad/cryptanalysis-main LEAD_ATLAS_ECC_CHALLENGES=/Volumes/SSD990-2/ecc-challenges; cwd /Volumes/SSD990-2/crypto-autoresearcher.

### Run 1. phrase: exact decomposition count vector over all targets from the log-domain Fourier spectrum of the factor base via the Li-Wan distinct-coordinate sieve and additive energy

```
$ python3 tools/lead_atlas.py --match "exact decomposition count vector over all targets from the log-domain Fourier spectrum of the factor base via the Li-Wan distinct-coordinate sieve and additive energy"
   19  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   17  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   17  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   16  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   15  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
$ python3 tools/build_frontier_map.py --match "exact decomposition count vector over all targets from the log-domain Fourier spectrum of the factor base via the Li-Wan distinct-coordinate sieve and additive energy"
KR-IC-73db3f  score=15  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=11  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-8b9daa  score=7  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
```

### Run 2. phrase: count for every target how many ways it splits over the factor base and test whether structured bases cluster more than random ones

```
$ python3 tools/lead_atlas.py --match "count for every target how many ways it splits over the factor base and test whether structured bases cluster more than random ones"
   19  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   16  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   14  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   14  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   12  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
$ python3 tools/build_frontier_map.py --match "count for every target how many ways it splits over the factor base and test whether structured bases cluster more than random ones"
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-5931ee  score=8  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5a43e5  score=8  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-7d93f6  score=5  [known_bound/proven]  Time–space bounds for many collisions and DP memory
    sources: KN-LIT-fe066e, KN-LIT-b19b9b
KR-IC-f3da82  score=3  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-RHO-46c2c6  score=3  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
```

### Run 3. phrase: mean per-target yield conservation binomial(B+m-1,m)/N with a variance excess or coverage gain that grows with N

```
$ python3 tools/lead_atlas.py --match "mean per-target yield conservation binomial(B+m-1,m)/N with a variance excess or coverage gain that grows with N"
    8  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
    7  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
    7  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    6  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    6  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
    6  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
    4  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  LEAD-ICB-tau-horner-chain                    open_next_step     tau-Horner decomposition chain on Koblitz curves (R = tau^{m-1}P_1 + ... + P_m over one base)
$ python3 tools/build_frontier_map.py --match "mean per-target yield conservation binomial(B+m-1,m)/N with a variance excess or coverage gain that grows with N"
KR-IC-fbdb61  score=3  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-RHO-fb88e6  score=3  [known_mechanism/proven]  Negation map: sqrt(2) gain and fruitless cycles
    sources: KN-LIT-074c32, KN-LIT-c8e485, KN-LIT-5b238b, KN-LIT-a5c59c
KR-IC-8b9daa  score=1  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-RHO-0528e7  score=1  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-46c2c6  score=1  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
```

### Run 4. phrase: multiset sum census characters of cyclic group: representation counts of a target as sum of base elements, variance and additive energy of the factor base

```
$ python3 tools/lead_atlas.py --match "multiset sum census characters of cyclic group: representation counts of a target as sum of base elements, variance and additive energy of the factor base"
   18  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   14  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   13  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   11  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
   11  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
$ python3 tools/build_frontier_map.py --match "multiset sum census characters of cyclic group: representation counts of a target as sum of base elements, variance and additive energy of the factor base"
KR-IC-5a43e5  score=13  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-73db3f  score=8  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-5b1c0a  score=5  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
```

### Run 5. phrase: Fourier character bias of a coordinate statistic of points under the group law, additive characters of E(F_p) evaluated on a factor base, moment and variance audit

```
$ python3 tools/lead_atlas.py --match "Fourier character bias of a coordinate statistic of points under the group law, additive characters of E(F_p) evaluated on a factor base, moment and variance audit"
   25  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   17  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
   17  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   12  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   10  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
$ python3 tools/build_frontier_map.py --match "Fourier character bias of a coordinate statistic of points under the group law, additive characters of E(F_p) evaluated on a factor base, moment and variance audit"
KR-IC-5a43e5  score=12  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-73db3f  score=8  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-46c2c6  score=5  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
```

### Run 6. phrase: minimum distance and minimum-weight codewords of elliptic curve codes, AG codes Riemann-Roch spaces and subset sums of points as decomposition

```
$ python3 tools/lead_atlas.py --match "minimum distance and minimum-weight codewords of elliptic curve codes, AG codes Riemann-Roch spaces and subset sums of points as decomposition"
    8  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    6  KR-IC-081a58                                 known_result       Joux–Vitse n−1 decomposition and oracle-assisted static DH
    6  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    6  KR-IC-8b9daa                                 known_result       Point decomposition via symmetric formulations (Karabina)
    6  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points
    6  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    6  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
$ python3 tools/build_frontier_map.py --match "minimum distance and minimum-weight codewords of elliptic curve codes, AG codes Riemann-Roch spaces and subset sums of points as decomposition"
KR-IC-955fd6  score=8  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-081a58  score=6  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-482ed3  score=5  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
```

### Run 7. phrase: exact break-even growth ladder slope of relation excess kappa versus N, planted control, matched null, structured base

```
$ python3 tools/lead_atlas.py --match "exact break-even growth ladder slope of relation excess kappa versus N, planted control, matched null, structured base"
   13  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   13  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   11  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
    9  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
    9  LEAD-ICP-xedni-function-field-sections       closed_obstructed  Function-field xedni - Mordell-Weil sections of elliptic surfaces over F_p(t) as a relation source
    8  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    8  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    8  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
$ python3 tools/build_frontier_map.py --match "exact break-even growth ladder slope of relation excess kappa versus N, planted control, matched null, structured base"
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-b0fcda  score=3  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-RHO-482ed3  score=1  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
```

(Runs 1-3 = match_phrasings of the candidate, run 4 = the gate agent's own phrasing, runs 5-7 = extra probes.)

## Appendix B. Independent identity check (written and run by the gate agent)

Script: scout/_codingtheoryC3_raw/check_newton_identity.py (python3 -I). Tests the cycle-index/Newton-Girard Fourier formula for distinct m-subset sums of a subset D of Z/N against brute force. This checks the identity on cyclic groups only; it does not touch elliptic curves.

```
N=101 B=14 m=2 FFT==brute: True  total=91 C(B,m)=91
N=101 B=14 m=3 FFT==brute: True  total=364 C(B,m)=364
N=101 B=14 m=4 FFT==brute: True  total=1001 C(B,m)=1001
N=101 B=14 m=5 FFT==brute: True  total=2002 C(B,m)=2002
N=211 B=16 m=2 FFT==brute: True  total=120 C(B,m)=120
N=211 B=16 m=3 FFT==brute: True  total=560 C(B,m)=560
N=211 B=16 m=4 FFT==brute: True  total=1820 C(B,m)=1820
N=211 B=16 m=5 FFT==brute: True  total=4368 C(B,m)=4368
N=97 B=12 m=2 FFT==brute: True  total=66 C(B,m)=66
N=97 B=12 m=3 FFT==brute: True  total=220 C(B,m)=220
N=97 B=12 m=4 FFT==brute: True  total=495 C(B,m)=495
N=97 B=12 m=5 FFT==brute: True  total=792 C(B,m)=792
C(F)=sum C(c2,2) identity: True 31 31
ALL OK
```
