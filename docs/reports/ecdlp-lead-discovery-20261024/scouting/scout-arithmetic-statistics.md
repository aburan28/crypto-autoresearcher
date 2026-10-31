# Scout dossier: arithmetic statistics against the named ECDLP bottlenecks (final round)

- Field: arithmetic statistics. That covers Cohen–Lenstra, Sato–Tate, Chebotarev, Katz–Sarnak and Deligne equidistribution, CM-point and isogeny-volcano statistics, Bhargava-style averaging, and second-moment / Poisson counting of decomposition counts.
- Date: 2026-10-24, final lead-discovery round.
- Write scope: only `scout/` under the session scratchpad. No repository file was edited, created, added or committed.
- The earlier dossier at this path, written by a prior run today at 18:52, is preserved at `scout/scout-arithmetic-statistics.prior-run-1852.md`. Its candidates and kills were re-checked, and its scripts were re-run here (§1).

**Provenance tags**

| tag | meaning |
|:--|:--|
| `measured-here` | A number this session computed. Toy or scout scale; not a repository run and not an admitted trial. |
| `rerun-here` | A prior-run script re-executed this session, with byte-identical output (§1). |
| `retrieved` | A source fetched and read this session, including repository records read this session. |
| `recalled` | From memory; not checked this session. |

**Prediction labels.** Every outcome of an experiment that has not run yet is labelled **prediction**.

## 0. Result in one paragraph

On prime-order curves this field's stated charge is closed: "pick instances or factor bases where decomposition counts deviate from the random model".
- The mean is fixed exactly (KN-FIND-007 conservation).
- Coverage is capped above by the mean (Markov).
- A count deviation can only lower the hit rate.

No exponent-moving (tier X gain) candidate survived inside the field. **B1 and B2 are not made tractable by anything here.** §5 records why for each sub-area, and §6 (K18, K19, K23) gives the kills that touched them.

What the field does contribute is three cheap instruments or proofs. All three are prime-field. Together they give the decisive first step for five open leads, and they decide one contrast exactly now: the P29 primary contrast of EXP-ECTD-0cf008. Everything else below is conditional on the stated first step:

- **C1 (B1/B3, prime field): exact occupancy calculator.** It combines conservation, the Markov ceiling and a Cauchy–Schwarz (Paley–Zygmund) floor, with the floor's one free number κ₂ pinned to the base's pair-sum coincidence count.
  - It computes target-free, from base data alone, the population parameter that the blocked 20-arm panel EXP-ECTD-0cf008 estimates.
  - Measured here, exact on all 12 P29 bases: population coverage 0.066695–0.066756, spread 0.09 %; primary floor/crater ratio **1.000125**.
  - Validated against both sealed P29 arms: z = +0.40 and +0.09.
  - P37 is sampled with my own targets, 10^5 per base: floor/crater **0.995 ± 0.017**, κ₂ ≈ 1.02.
  - The lead's positive outcome (ratio beyond 20 %) needs κ₂ ≥ 2.9–3.0 in one base.
  - It is the decisive first step for LEAD-ICP-isogeny-transported-relation-yield (P37 is a scout sample, not exact), the IC-meter half of LEAD-TRF-teske-secret-isogeny-trapdoor (pending P37 and review), and the second-order question of LEAD-ICE-decomposition-probability-audit (pending BATCH-79a580's own fixtures).
- **C2 (B7, prime field): Kummer-conductor theorem.** The Kummer sheaf of the Miller function, tensored with a Lang-torsor character, has conductor 2.
  - So the Miller primitive U has character correlation ≤ 2√p with every character of G.
  - Rerun here: max |S|/√p = 2.019 / 2.020 / 2.014 against bounds 2.020 / 2.020 / 2.014; the N | p−1 control peaks at 333/333.
  - It decides the equidistribution and character-correlation parts of the discriminator of LEAD-TRF-miller-cocycle-nonhom-transfer. The Smart-ratio part is proven only for d ≲ p^{1/4}.
- **C3 (B3 instrument, prime field with cofactor): cofactor-coset counting law** E[K_G] = B(B−1+t)/|S|.
  - Rerun here on v2.1: ℓ = 2 floor/crater predicted 0.9428 (closed form 33/35 = 0.9429) against measured 0.9417; ℓ = 3 predicted 1.0017 against measured 1.0062.
  - The E3a identity N0 = 2K_G + B holds on 800/800 rows. The predicted E3a slope is 1.044, inside E3a's OLS 1.054 [1.031, 1.080]; E3a's README calls the excess "not explained here".
  - It is the decisive first step for LEAD-STR-class-representative-ic-selection, conditional on the E3b test. On every prime-order curve the effect is identically 0.

Two candidates were demoted:
- The prior run's C2, the completion ledger for coordinate statistics: its technique is already Theorem W of the approved H-ECDLP-f6a43a, and it is vacuous on exactly the two statistics (Thue–Morse, Rudin–Shapiro) that its lead still owes.
- A polynomial-hint agreement bound for LEAD-EXO-invertible-hint-subset: the same Theorem W, plus Lange–Winterhof 2002.

## 1. Inputs read, and reruns

Read in full:
- ATLAS.md, every family.
- KRMAP.md.
- object-frame-ideation.md §1–3.
- idea-generator "Search heuristics" and "Obstructions as generative material".
- target-result-profile Part A.
- IC LEADERBOARD Tables A–D and phases.
- FRONTIER.md listing.

Lead YAMLs, read and quoted fresh (`scout/arith-stats-r2/so_quotes.txt`):
- LEAD-ICP-isogeny-transported-relation-yield, LEAD-TRF-teske-secret-isogeny-trapdoor, LEAD-TRF-teske-trapdoor-fp6-weak-class.
- LEAD-ICE-decomposition-probability-audit, LEAD-STR-class-representative-ic-selection, LEAD-TRF-miller-cocycle-nonhom-transfer.
- LEAD-EXO-coordinate-statistic-leakage, LEAD-EXO-invertible-hint-subset.
- Every SO-code lead.

Experiment and research records:
- EXP-ECTD-0cf008: the specification listing, all 20 `preparation/prepared/*/prepared.txt` files (header and base lines only; see the C1 note), and the sealed raw-result.json of RUN-ECTD-26d06d, -c769f1 and -f395a9.
- research/conductor_relation_yield_20261014: plan.json, ORACLE_FORMAT.md, count_verify.cpp.
- problems/prime-field-arity3-relation-oracle.md.
- KN-FIND-007.
- H-ECDLP-f6a43a statement and mechanism; EV-ECDLP-924941.
- crypto research/generator_effect_ic_20261019 (README, PLAN, n0.json, regression.json) and research/isogeny-volcano-cost-v2_20261017.

Ledger dedup was done by grepping `ledger/.index/{proposals,hypotheses}.jsonl` only. Hits:
- IDEA-20260930-4ebd85 and H-KIC-baee02: exact triple-sum coverage on *binary toy* subgroups. C1 is the prime-field, frozen-panel adaptation.
- IDEA-20261018-5fa71b: "one count vector, three moments".
- H-ECDLP-f6a43a: Theorem W (completion plus Kohel–Shparlinski).
- No hit for "Lang torsor", "Grothendieck–Ogg", "cofactor-coset" or "K_G".

**Reruns of the prior run's scripts.** Outputs are in `scout/arith-stats-r2/`, and each was compared with `cmp` against the prior output.

| script | prior output | rerun output | result |
|:--|:--|:--|:--|
| `miller_u_spectrum_v2.py` | `miller_u_spectrum_v2.out` | `miller_u_spectrum_v2.rerun.out` | byte-identical |
| `digit_l1.py` | `digit_l1.out` | `digit_l1.rerun.out` | byte-identical |
| `volcano_kg.py` + `volcano_compare.py` | `volcano_compare_v21.out` | `volcano_compare_v21.rerun.out` | byte-identical |
| `volcano_chi2.py` | `volcano_chi2_v21.out` | `volcano_chi2_v21.rerun.out` | identical after sort |
| E3a identity (inline, `n0_identity_check.rerun.out`) | prior "80/80" | 800/800 rows exact | re-derived; the prior count was on deduplicated keys |

New programs written this round:
- `scout/arith-stats-r2/popcov.cpp`: exact population coverage.
- `popsample.cpp`: sampled coverage with own targets.
- `paircoin.cpp`: pair-sum coincidences.

## 2. Field-level framing: where arithmetic statistics can and cannot bite

**F1, the Weil threshold.** IC works at |F|^m ≈ N with m ≥ 2, so |F| ≲ p^{1/2}.
- A per-target decomposition count is an incomplete sum of length ≲ √p.
- Deligne/Katz and Bombieri bounds carry an error of √p·log p, which is at least the main term.
- This is the wall that closed all six analytic routes of KN-FIND-e7a3b1 (`LEAD-EXO-dl-character-sum-pseudorandom`).

**F2, conservation and Markov.** For any base of size B on a prime-order group:
- Σ_R c(R) = binom(B+m−1, m) exactly, which is KN-FIND-007, read this session.
- Hence coverage P(c ≥ 1) ≤ E[c].
- Selection by count statistics cannot raise the per-attempt hit rate. The excess over Poisson is at most λ/(1−e^{−λ}) − 1 ≈ λ/2, which is 3.5 % at the panel's λ = 0.069; the global cap is 1.582 at λ = 1.

**F3, what is left.** Three places:
1. Complete sums over the whole group: C2.
2. Exact second-order bookkeeping of a fixed base: C1.
3. Group-structure statistics with a cofactor: C3.

None of the three moves an exponent. All three close or decide leads.

## 3. Candidates

### C1. Exact occupancy calculator with a conservation-plus-Paley–Zygmund band (B1 and B3; prime field)

**Bottleneck.**
- B1: the prime-field arity-3 relation-oracle panel EXP-ECTD-0cf008 is open_blocked (`problems/prime-field-arity3-relation-oracle.md`), with 17 of 20 arms missing.
- The same panel is the next step of the Teske trapdoor lead.
- The audit lead wants the "exact count vector c_D and its variance against a size-matched random base".

**External ingredient.**
- Paley–Zygmund / Cauchy–Schwarz second-moment inequality (Paley and Zygmund, 1932; textbook, recalled), giving P(u ≥ 1) ≥ (E u)²/E u².
- The Chen–Stein Poisson-approximation reading of κ₂ (Arratia, Goldstein and Gordon, "Two moments suffice for Poisson approximations: the Chen–Stein method", Ann. Probab. 17(1) (1989) 9–25; retrieved at abstract level this session).
- Tate's isogeny theorem (Tate 1966, Invent. Math. 2; recalled), which gives the isomorphism G → G′ for transport.
- KN-FIND-007 conservation (internal; retrieved, read this session).

**Statement (C1-Band).** Setting:
- E/F_p of prime order r, so G = E(F_p).
- F is a signed base of B distinct abscissae, consecutive pairs (P, −P).
- U is the set of *useful* triples. Per ORACLE_FORMAT.md (retrieved): three distinct point IDs and three distinct x-orbits, so |U| = M = 8·binom(B,3).
- u(R) = #{T ∈ U : ΣT = R}, for R uniform on G∖{O}. This is the panel's target law: dedup, nonidentity, uniform a, b.

Then:
1. **Exact mean.** E u = λ := (M − u_O)/(r−1), where 0 ≤ u_O ≤ 4·binom(B,2)/3, because a pair fixes the third point. The relative spread over all bases of size B is ≤ 1/(2(B−2)): 0.20 % at B = 256 and 0.03 % at B = 1600.
2. **Two-sided coverage band.** λ/(1 + κ₂λ) ≤ cov(F) ≤ λ, where κ₂ := E[u(u−1)]/λ², and κ₂ = 1 is the Poisson value.
3. **Ratio band.** For any two bases F, F′ of size B on any two curves of the class (the same r), cov(F)/cov(F′) ≤ 1 + κ₂(F′)·λ. A floor/crater ratio of at least 1.2 therefore requires κ₂ ≥ 0.2/λ, which is **2.90 at P29 and 3.00 at P37**.
4. **What κ₂ is made of.** Its excess over 1 is driven by the base's pair-sum coincidences P_a + P_b = P_c + P_d. Each one creates about 2(B−4) colliding triple pairs that share a point, so Δκ₂ ≈ 2·2(B−4)/((r−1)λ²) = 0.00066 per coincidence at P29 (heuristic H1-2). This is a 2-energy statistic of the base and can be computed in O(B²).
5. **Transport.** An isogeny or isomorphism restricted to G is a group isomorphism, so a transported base has a targetwise-identical u. Measured below: D is identical for native and u2-transport.

**Measured here, exact (P29, p = 320092037, r = 320091991 prime, #E = r).**
- Bases were read from the 12 prepared P29 inputs; target lines were not read.
- `popcov` enumerates all 22,108,160 useful triples, sorts the sums, and counts D = #distinct nonidentity sums. The population coverage is D/(r−1).
- λ = 0.0690681, Poisson 1 − e^{−λ} = 0.0667369.

| base (prepared input) | D | population coverage | κ₂ | pair coincidences (expected 26.6) | prediction: useful_targets of 32,768, mean ± sd |
|:--|--:|--:|--:|--:|:--|
| P29-crater native | 21,358,260 | 0.0667254 | 1.0051 | 24 | 2186.5 ± 45.2 |
| P29-crater u2-transport | 21,358,260 | 0.0667254 | 1.0051 | — | identical to native |
| P29-crater u2-native | 21,356,140 | 0.0667188 | 1.0082 | 32 | 2186.2 ± 45.2 |
| P29-crater random | 21,353,658 | 0.0667110 | 1.0109 | 36 | 2186.0 ± 45.2 |
| P29-floor native | 21,360,924 | 0.0667337 | 1.0014 | 24 | 2186.7 ± 45.2 |
| P29-floor u2-transport | 21,360,924 | 0.0667337 | 1.0014 | — | identical to native |
| P29-floor u2-native | 21,348,586 | 0.0666952 | 1.0183 | 48 | 2185.5 ± 45.2 |
| P29-floor random (u_O = 2) | 21,361,950 | 0.0667369 | 1.0002 | 30 | 2186.8 ± 45.2 |
| P29-E2 native (sealed: 2204) | 21,351,946 | 0.0667057 | 1.0142 | 36 | 2185.8 ± 45.2 → z = +0.40 |
| P29-E3 native (sealed: 2191) | 21,363,462 | 0.0667416 | 0.9983 | 20 | 2187.0 ± 45.2 → z = +0.09 |
| P29-E2 random | 21,353,164 | 0.0667095 | 1.0124 | 36 | 2185.9 ± 45.2 |
| P29-E3 random | 21,368,122 | 0.0667562 | 0.9912 | 12 | 2187.5 ± 45.2 |

- **Useful-triple check against the sealed arms.** Predicted 32768·λ = 2263.2 ± 47.6. Sealed: 2287 (z = +0.50) and 2270 (z = +0.14).
- **Primary P29 contrast (floor native / crater native).** Population ratio **1.000125**, exact.
  - **Prediction:** the panel's sampled ratio is about 1.000 with sd 0.029 from hypergeometric target sampling alone.
  - A deviation beyond ±20 % would be a 6.8σ event.
- **Spread across all 12 bases** (native, u2, random, E2/E3): 0.0915 % of D. Native and size-matched random bases overlap.
- **κ₂ against coincidences.** κ₂ = 0.983 + 0.00077 × (pair coincidences); corr 0.944, n = 10, residual sd 0.0029. The predicted slope is 0.00066 per coincidence (H1-2), and the value at the expected 26.6 coincidences is 1.0035.
- So the second-order deviation of every base is its pair-sum coincidence count, which is a random-like count. This is the "no excess confirms KN-FIND-007 to second order" outcome of the audit lead, on 12 real bases at N = 2^28.25, exactly.

**Measured here, sampled (P37, p = 81640512137, r = 81640511861 prime, #E = r).**
- The exact sumset (5.45·10^9 sums) was not attempted on this host.
- `popsample` draws its own uniform targets R = [k]G (mt19937_64, fixed seeds, not the panel's targets). It counts u(R) by meet-in-the-middle against the 5.1·10^6-entry pair table, using batch inversion.
- λ = 0.0667695 is the Markov ceiling; Poisson is 0.0645892.

| base | own targets | coverage estimate ± se | κ₂ estimate |
|:--|--:|:--|--:|
| P37-crater native | 100,000 | 0.06555 ± 0.00078 | ≈ 1.02 (± ≈ 0.07) |
| P37-floor native | 100,000 | 0.06520 ± 0.00078 | ≈ 1.02 |
| P37-floor u2-native (sealed: 2178/32768 = 0.06647) | 32,768 | 0.06427 ± 0.00135 → 1.1σ from sealed | ≈ 1.05 |

Calibration on P29 crater native: 20,000 own targets give 0.0675 ± 0.0018, against the exact 0.06673.

- **Primary P37 contrast (floor native / crater native).** Scout estimate **0.995 ± 0.017**, plus the panel's own sampling sd ≈ 0.030.
- κ₂ ≥ 3 is excluded by many standard errors in both native bases.
- This is a scout estimate of a population parameter, not a substitute for the panel's arms. The disposition stays with the panel and its review.

**Note on blinding.** Only header and base lines of the prepared inputs were read. The panel's target lines for unrun arms were not used, and no panel count was replicated on panel targets.

**Pair and trichotomy.**
- Pair: (signed small-abscissa or random base on a prime-order curve; Σ = translation by base elements, as triple sums).
- Class: **partial-action**, IC Class I. The tracked object is the existence of a decomposition (the branching event). The calculator prices it exactly at population level instead of by sampling.

**SO codes touched.** For each, the quoted obstruction.statement, Scope clause included, and the premise involved:

- **SO-ALGFB, `LEAD-ICP-algebraic-membership-factor-base` [theorem].** "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
  - C1 does **not** escape it; P29 and P37 are prime order, inside the Scope.
  - What C1 adds is the premise this statement leaves open: it caps coverage *gain*, not coverage *deficit*. C1 bounds the deficit by κ₂ and ties κ₂ to the base's 2-energy. That is the only channel through which one stratum could look better than another.
- **SO-ISO, `LEAD-STR-isogeny-class-generic-invariance` [theorem].** "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (±5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve."
  - Premise not covering the IC meter: "rho and BSGS depend only on the group order". IC occupancy depends on the encoding through the base.
  - C1 extends class invariance to the arity-3 IC meter on prime-order classes, within the band 1 ± κ₂λ.
- **SO-TABLE, `LEAD-ICP-generic-table-decomposition` [theorem].** "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). … Scope: any generic (enumeration/table) decomposition over F_p."
  - C1 is orthogonal: it fixes yield, not oracle cost.
  - Corollary for B1: because occupancy is a property of the base alone, **any** oracle, enumerative or not, inherits at most λ (an incomplete oracle finds only a subset of the decompositions) and the same κ₂ band. A non-enumerative oracle can change only the per-attempt cost T_dec, so B1 reduces to one number.

**Tier and gain.**
- Tier **I** (constant, end to end).
- Predicted gain **0**. This is a closure instrument. It moves no S; it removes 17 arms of planned compute and decides three leads.
- H1-1: the panel's target law is uniform without replacement over G∖{O}. This is true by protocol, so no heuristic is needed for P29.
- H1-2: Δκ₂ per pair-sum coincidence ≈ 4(B−4)/((r−1)λ²). Supported here by a fit slope of 0.00077 against 0.00066 predicted.
- H1-3: the P37 native bases have κ₂ < 1.1. Supported by the sampled 1.02 ± 0.07 and the sealed floor-u2-native arm, 2(2255−2178)/(32768λ²) = 1.05.

**First discriminating step.**
1. Coordinator files the calculator, which needs only base data, plus the tables above as a pre-registered population prediction for the EXP-ECTD-0cf008 recovery amendment.
2. Run one of:
   - `popcov` exact on the 8 P37 prepared bases: 5.45·10^9 sums each, a bucketed or out-of-core sort, about 1–2 h single-core per base on a host with ≥ 16 GB;
   - `popsample` at 10^6 own targets per base: se ≈ 0.25 %.
3. In the same session, run `popcov` or `paircoin` on BATCH-79a580's F-2 and F-1 fixtures for the audit lead.

**Outcomes → dispositions.**
- **(a)** All P37 bases have κ₂ ∈ [0.9, 1.1], and the P37 population ratio lies within ±2 %:
  - `LEAD-ICP-isogeny-transported-relation-yield` → closed_obstructed(theorem: conservation, the Markov ceiling and a Paley–Zygmund floor with κ₂ ≈ 1; Scope: prime-order classes, any size-B base, arity 3). best_measured: "P29 floor/crater population ratio 1.000125 exact (12 bases, coverage 0.066695–0.066756); P37 0.995 ± 0.017 (scout sample)".
  - The 17-arm rerun becomes optional: its expected information is hypergeometric noise around known parameters.
  - The IC-meter half of `LEAD-TRF-teske-secret-isogeny-trapdoor` closes by its own rule: "ratios consistent with one … close the IC-meter half at toy scale". This is still pending review.
  - `LEAD-ICE-decomposition-probability-audit` → exhausted_at_scale if BATCH-79a580's fixtures also show κ₂ explained by coincidences (native ≈ random), with best_measured the P29 κ₂ table. It stays open_next_step if not.
- **(b)** Some base has κ₂ ≥ 3, the lead's only positive channel → open_next_step. best_measured is that κ₂ and its pair-coincidence count; run that endpoint's arms.
- **(c)** The calculator misses a sealed arm by more than 3σ → open_next_step. best_measured: the sealed-arm z-scores (currently +0.40 and +0.09). Next step: fix the calculator.

**Costs.**
- Implementation: done; about 200 lines of C++.
- Compute: P29 exact took about 6 s CPU per base. P37 sampled took about 25 s CPU per 25k targets. P37 exact takes 1–2 h per base, bucketed.

**Self-kill risk.**
- High on novelty. The ingredient is second-moment and conservation reasoning, which is thin as "arithmetic statistics".
- KN-FIND-007 already states the mean and the Markov ceiling. The lead YAML cites the conservation/pullback expectation (`RESEARCH_PDP_SPEEDUP_AND_ISOGENY.md` §2.4; isogeny-fibres Thm 4.2), and exact triple-sum coverage exists for binary toys (IDEA-20260930-4ebd85, H-KIC-baee02).
- What is new: the two-sided band with κ₂ tied to 2-energy; exact population values for the actual frozen P29 bases, validated on sealed arms; the κ₂ ≥ 2.9–3.0 requirement; and the P37 scout estimate.
- Low on correctness.
- Value: it unblocks or obviates a blocked panel that two leads wait on.

**Match phrasings.**
- (own) "exact population coverage of the useful-triple sumset of a factor base, crater versus floor"
- (plain) "count every target a factor base can decompose instead of sampling targets"
- (SO-ALGFB vocabulary) "mean per-target yield conservation and coverage gain across isogenous curves"

lead_atlas tops the first phrasing with LEAD-ICP-isogeny-transported-relation-yield (25) and LEAD-STR-class-representative-ic-selection (18). The frontier map gives no KR row that forecloses the band. This advances existing leads' next_action; it is not a new lead. Log: `scout/arith-stats-r2/match.out`.

### C2. Kummer-conductor theorem closes the Miller-primitive transfer (B7, prime field)

**Ingredient (theorem).**
- Weil–Deligne via Grothendieck–Ogg–Shafarevich, for a rank-1 tame lisse sheaf 𝓕 on X∖S (Deligne, SGA 4½ "Sommes trig."; Weil II, 1980; recalled): |Σ_{x∈(X∖S)(F_p)} t_𝓕(x)| ≤ (2g − 2 + |S|)·√p.
- The elliptic case "additive character of x times a group character" is Kohel–Shparlinski, *Exponential sums and group generators for elliptic curves over finite fields*, ANTS-IV, LNCS 1838 (2000) 395–404, Cor. 1. Retrieved: the bibliographic record and abstract via search, and the statement as quoted in Ahmadi–Shparlinski, arXiv:1302.4210v3, Lemma 1, whose PDF text I extracted and read this session: "for any group character χ on E(Fq) … ≪ q^{1/2}".
- The author's PDF was unreachable (ECONNREFUSED).
- The Kummer-character version used below is the same proof with a Kummer sheaf in place of the Artin–Schreier sheaf. Ahmadi–Shparlinski §5 states that their results "have direct analogues for sums with multiplicative characters" and cite Mérai, Publ. Math. Debrecen 80 (2012) 199–213 for multiplicative-character sums over elliptic-curve points. That pointer is retrieved (excerpt saved under `arith-stats-r2/retrieval/`); the Kummer statement itself was not read in a source.

**Statement (C2-Theorem).** Setting:
- E/F_p with G = E(F_p) of prime order N, and gcd(N, p−1) = 1.
- f a rational function on E.
- χ a nontrivial character of F_p^* of order e.
- ψ any character of G.

Let s_e(f) = #supp(div f mod e). If div f ≢ 0 (mod e), then

  |Σ_{R∈G∖supp} χ(f(R))·ψ(R)| ≤ s_e(f)·√p.

Proof:
1. ψ is the trace function of 𝓛_ψ, the pushout of the Lang torsor 1 − Frob: E → E along ψ. It is rank 1 and lisse on E.
2. χ∘f is the trace function of the Kummer sheaf 𝓛_χ(f), which is tamely ramified exactly on supp(div f mod e) and is geometrically nontrivial.
3. The tensor product is rank 1, tame and lisse on E∖supp, so χ_c = −s_e. Also H⁰_c = H²_c = 0, and the weights are ≤ 1.

The bound does not depend on deg f.

**Corollary for U = f_{N,P}^{u}, u = N^{−1} mod (p−1).**
- χ∘U = (χ^u)∘f_{N,P}, and div f = N(P) − N(O) ≢ 0 (mod e) for every e | p−1 with e > 1, so s_e = 2.
- Hence max_{χ≠1, ψ} |S| ≤ 2√p, plus the excluded points.
- This is the random-function level: a random map has maximum character correlation ≈ √(N log N)/N.

**Rerun here.** `miller_u_spectrum_v2.py`, output byte-identical to the prior run. U was evaluated at every point by binary and NAF Miller chains plus random split chains. The chains agree on 10022/10022, 9914/9914 and 19854/19854 points; split chains agree on 10030/10030, 9932/9932 and 19882/19882.

| cell | p | N = #E | max over a ≠ 0, b of \|S\|/√p | bound (2√p+2)/√p |
|:--|--:|--:|--:|--:|
| theorem | 10007 | 10069 | 2.019 | 2.020 |
| theorem | 10009 | 9973 | 2.020 | 2.020 |
| theorem | 20011 | 19927 | 2.014 | 2.014 |
| control, N \| p−1 | 10111 | N = 337, h = 30 | \|S\| = 333 = all evaluated points (peak) | not applicable: the Tate pairing is alive |

The bound is attained and never exceeded, and the positive control peaks.

**Scope limits, stated.**
- The Smart-ratio event U(dR) = U(R)^d has a Kummer function g with s_e ≤ 2d² + 2. The theorem bounds the success count by 1 + (2d²+2)√p, which is nontrivial only for d ≲ p^{1/4}; larger d remains a cheap toy measurement.
- The zeta-defect subline (IDEA-20261016-09fd08) is F_p-valued, an Artin–Schreier analogue with a degree-dependent Swan conductor, so the bound is vacuous there; it stays open.
- Multi-query non-linear use of U is bounded only by the SO-TORS argument.

**SO codes touched.** Quoted statements, Scope included, and the premise each one does not cover:

- **SO-PAIR, `LEAD-TRF-second-torsion-direction` [theorem].** "Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1, i.e. the embedding degree divides k. Hence for N not dividing k, T_k(E)[N] = 0 (trace acts as [k] on the rational line), and an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N."
  - Premise: homomorphic or graph-type transfers. U is non-homomorphic.
  - C2 closes the non-homomorphic Kummer class. The pairing reappears as the unique exception, div f ≡ 0 (mod e), the control cell.
- **SO-PADIC, `LEAD-TRF-padic-canonical-section` [theorem].** "For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope: non-anomalous prime-field curves, all lifts of E."
  - Premise: sections into E(Q_p). U is F_p^*-valued.
  - C2 is its F_p^*-valued analogue, proved by sheaf theory, not by toy runs.
- **SO-GEN (the augmented-oracle lead), `LEAD-EXO-augmented-oracle-ggm` [theorem].** "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 (…). … Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."
  - Premise: simulability. A U-oracle needs the point, so it is not GGM-simulable.
  - C2 replaces simulability with a character-sum bound. That covers linear statistics only, which is stated.
- **SO-NET, `LEAD-EXO-elliptic-net-eds` [proof].** "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead); … with the sieve/BSGS gap growing (24x -> 135x)."
  - The K2 route of `LEAD-EXO-miller-pairing-cocycle`, U(kP) = c·r_k·C^{k/N} with r_k = ψ_{k−1}/ψ_k, needs an EDS prefix.
  - Obtaining r_k from kP alone is the EDS-association problem (Lauter–Stange, SAC 2008; recalled), which lands in this obstruction. This is a conditional reduction, not a theorem.

**Pair and trichotomy.**
- Pair: (F_p^*-valued Kummer coordinate R ↦ χ(f(R)); Σ = full translation, tested through the characters of G).
- Class: **coordinate-dependent**. U is a function of the representation, and no collision gain is claimed.

**Tier, gain, heuristics.**
- Tier **X**: it decides an exponent-tier transfer lead.
- Predicted gain **0**, a closure.
- HC2-1: none needed. The theorem is unconditional for χ ≠ 1 when gcd(N, p−1) = 1.
- HC2-2 (interpretive): a statistical conversion needs linear signal ε ≥ N^{−1/4} to beat rho (1/ε² ≤ √N). C2 gives ε ≤ 2√p/N ≈ 2N^{−1/2}.

**First discriminating step.** File C2-Theorem as a KN-FIND derivation (Lang torsor ⊗ Kummer sheaf; GOS; Weil II), with an optional Lean statement. Replay the lead's own panel: IDEA-20261017-e3a6f1 minimal test, p ≤ 2^20, special and matched random p, 30 curves each, plus the Smart-ratio success rate at d ≤ 2^8.

**Outcomes → dispositions.**
- **(a)** Every cell ≤ s_e√p + #excluded and the control peaks → `LEAD-TRF-miller-cocycle-nonhom-transfer` closed_obstructed(theorem: Kummer conductor 2; Scope: prime-order or N-part, gcd(N, p−1) = 1, linear character statistics of U). best_measured: "max |S|/√p 2.014–2.020 against the bound 2 + 2/√p". The zeta-defect and generalized-Jacobian sublines are recorded as open residuals.
- **(b)** A cell above the bound → open_next_step. best_measured: the measured max |S|/√p. Next step: re-derive the normalisation, because the theorem holds.
- **(c)** The control is not peaked → open_next_step. best_measured: the control's max |S|. Next step: repair the instrument before any reading.
- For `LEAD-EXO-miller-pairing-cocycle`: if K2 is confirmed exactly → closed_obstructed(theorem, via EDS association). If K2 is false → the U-part is closed by C2 and the K1 residue is recorded.

**Costs.** Implementation is done at toy scale; filing takes about 1 day. Compute: minutes.

**Self-kill risk.**
- Low on correctness: textbook sheaf theory, and the toy check is tight.
- Moderate on value: it kills a lead nobody expected to work.
- Novelty: the Kummer-twisted Kohel–Shparlinski bound is standard technique (Shparlinski school; recalled). It is not in the program ledger: the grep for "Lang torsor" and "Grothendieck-Ogg" returned 0 hits.

**Match phrasings.**
- (own) "Kummer sheaf of the Miller function tensored with the Lang-torsor character, conductor bound"
- (plain) "the Miller-function transfer into F_p^* is uncorrelated with the discrete log"
- (SO-PADIC vocabulary) "non-homomorphic transfer into F_p^* recovers the log only at the random rate"

lead_atlas returns LEAD-EXO-miller-pairing-cocycle (12) and LEAD-TRF-miller-cocycle-nonhom-transfer (8). The frontier map has no foreclosing KR row.

### C3. Cofactor-coset counting law: volcano-level IC yield is 2-torsion bookkeeping (B3 instrument; prime field with cofactor)

**Ingredients.**
- ℓ-Sylow structure by volcano level:
  - Kohel, thesis, 1996 (recalled).
  - Miret, Sadornil, Tena, Tomàs, Valls, "Volcanoes of ℓ-isogenies of elliptic curves over finite fields: the case ℓ = 3", Publ. Mat. Extra (2007) 165–180, DOI 10.5565/PUBLMAT_PJTN05_08. Retrieved at abstract level: the ℓ-Sylow subgroup is related to the volcano level.
  - Miret, Moreno, Sadornil, Tena, Valls, Appl. Math. Comput. 176 (2006) 739–750: the 2-volcano algorithm (retrieved bibliographic). Above the floor of a 2-volcano the 2-torsion is full (t = 4); on the floor there is one rational 2-torsion point (t = 2). This is also recorded in the program's v2.1 population table (retrieved).
- Exact class bookkeeping of the negation-folded pair table: the prime-abscissa base takes the B smallest abscissae with both signs, from all of E(F_p).

**Derivation (C3-Law).**
- With s_i = [r]P_i in the cofactor part S (|S| = h), a table key lands in G iff s_i = −s_j (for P_i + P_j), s_i = s_j (for P_i − P_j), or 2s_i = 0 (for a double).
- Hence K_G = Σ_{i<j}([s_i = s_j] + [s_i = −s_j]) + Σ_i [2s_i = 0].
- Under H3-1, i.i.d. uniform cofactor components: **E[K_G] = B(B−1+t)/|S|**, with t = #E(F_p)[2].
- Per-probe yield is about K_G/(r/2). The 2-volcano floor/crater ratio is (B−1+2)/(B−1+4) = **33/35 = 0.9429** at B = 32.
- ℓ = 3 volcanoes do not change t, so the ratio is 1. At h = 1, K_G = B² for every model and curve.

**Rerun here** (v2.1, 7,760 curve-models from recorded parameters; no new IC runs; outputs byte-identical to the prior run's).

| quantity | prediction (C3-Law) | v2.1 measured (program data, re-read) |
|:--|:--|:--|
| ℓ = 2 floor/crater, geometric mean of 14 classes | closed form 0.9429; exact K_G 0.9428 | 0.9417 |
| ℓ = 2, per class (l2-s1001 h=12; l2-s1009; l2-s1014) | 0.904; 0.926; 0.946 | 0.893; 0.926; 0.944 |
| ℓ = 3, geometric mean of 14 classes | 1.000; K_G 1.0017 | 1.0062 |
| l3-s1011 (h = 9, 3-torsion changes, t 1→1) | 1.019 | 1.025 [0.968, 1.085] |
| model τ (h > 1 classes) | K_G spread 0.027–0.104 | 0.048–0.110, each above its prediction by a target-sampling floor; the h = 1 classes, predicted 0, read 0.031–0.041 (e.g. l2-s1001 0.089 vs 0.101) |
| vertex-level pooled fit | slope 1 | slope 0.954, corr 0.665, n = 905 |
| E3a identity N0 = 2K_G + B (m = 2) | exact | 800/800 rows exact (recomputed here) |
| E3a slope of ln yield on ln N0/r | 1.0442, from K_G arithmetic alone | E3a regression.json: OLS 1.054 [1.031, 1.080], WLS 1.064 [1.040, 1.090]. The README says the excess "is not explained here" |
| H3-1 check: χ² of cofactor-class counts against uniform | χ²/df ≈ 1 | 0.935–1.088 over 25 classes with h > 1; minimum p_upper 0.021 (l2-s1009) |

**Reading.**
- `LEAD-STR-class-representative-ic-selection` carries best_measured "l=2 IC yield floor/crater 0.942 [0.928, 0.956]". That number is the closed form 33/35 to within 0.1 %.
- The lead's plan (b), "carry to the crater", earns exactly the 2-torsion term. That term is also available on the floor, without transport, from a G-restricted base: E3b's planned `prime-abscissa:subgroup=filter|project` arms (E3a PLAN.md, line 204).
- Its predicted hit-rate factor there is |S|·B/(B−1+t): ×3.66 (h=4, t=4), ×3.88 (h=4, t=2), ×10.97 (h=12, t=4). That dominates any representative selection.
- The plan (c) model effect is the deterministic K_G spread across models. It is selectable target-free, and it is again dominated by G-restriction.
- On prime-order curves, which means Table B and every deployed curve, the effect is identically 0.

**SO codes touched.**
- **SO-ALGFB** (quoted in C1). Escaped premise: "Scope: prime-order E/F_p". The volcano classes have h ∈ {1, 2, 4, 7, 8, 9, 12}. C3-Law is the cofactor extension of conservation and reduces to it at h = 1.
- **SO-ISO** (quoted in C1). Premise: "rho and BSGS depend only on the group order". A whole-group small-abscissa base depends on the full group structure, and t is not a class invariant. So the effect exists for IC and not for rho.
- **SO-TABLE(p)** (quoted in C1), with Scope "any generic (enumeration/table) decomposition over F_p". The pair-table oracle is inside this scope, and C3 changes constants only.

**Pair and trichotomy.**
- Pair: (whole-group small-abscissa signed base; Σ = translation by base elements, targets in G).
- Class: **partial-action**, IC Class I. The class-cancelling count is the block system of the cofactor quotient E(F_p) → S.

**Tier and gain.**
- Tier **I**.
- Predicted gain is 0 on every prime-order curve.
- On cofactor workloads the prediction is ×|S|B/(B−1+t) in per-probe hit rate from G-restriction, which is not an S prediction. H3-1 (i.i.d. uniform cofactor components) is supported by the χ² row above.

**First discriminating step.** Replace the lead's 3-arm 24–32-bit study with E3b on four v2.1 classes: ℓ=2 at h = 4 and h = 12, and ℓ=3 at h = 1 and h = 9. Arms: prime-abscissa, subgroup=filter, subgroup=project, at B = 32.

Pre-registered **predictions:**
- filter/current yield = |S|B/(B−1+t), within ±10 %;
- floor/crater under filter in [0.98, 1.02];
- model τ under filter at the h = 1 null;
- the arms byte-identical at h = 1.

**Outcomes → dispositions.**
- All four hold → `LEAD-STR-class-representative-ic-selection` closed_obstructed(proof: "level, model and horizontal IC yield effects are cofactor-coset counting E[K_G] = B(B−1+t)/|S|, dominated by G-restriction, identically 0 at h = 1").
- Any miss → open_next_step, with the residual ratio as best_measured.

**Scope limit.** C3-Law and 33/35 are m = 2. The m = 3 lead `LEAD-ICP-isogeny-transported-relation-yield` uses prime-order curves, where the h = 1 identity applies; that lead is decided by C1, not C3.

**Costs.** The re-analysis is done and took minutes. E3b needs a few CPU-hours; the arms are planned in E3a's PLAN.

**Self-kill risk.**
- High on novelty: the N0 mechanism is internal (E3a). New are the closed form, the v2.1 check, the slope identity and the domination argument.
- Low on correctness.
- Value: it removes the only positive-looking volcano lead.

**Match phrasings.**
- (own) "cofactor-coset class-cancelling count K_G = B(B-1+t)/|S| for small-abscissa bases"
- (plain) "volcano level index calculus yield difference is 2-torsion bookkeeping"
- (SO-ISO vocabulary) "index calculus yield across volcano levels depends only on the group structure and automorphisms"

lead_atlas returns LEAD-ICP-isogeny-transported-relation-yield (14), LEAD-STR-class-representative-ic-selection (10–14) and LEAD-STR-isogeny-class-generic-invariance (18). No foreclosing KR row.

## 4. Binary and Koblitz, one line

C3-Law and C1 apply verbatim to cofactor binary bases. Ordinary char-2 curves have t = 2, and a trace-zero subspace base lands in 2E. Check `exact_decomposition_ceiling` on the Table A/C bases before assuming they are G-restricted. Not pursued further.

## 5. Bottleneck-by-bottleneck verdict for this field

| bottleneck | verdict from arithmetic statistics |
|:--|:--|
| B1, prime-field non-enumerative oracle | Not made tractable. C1 proves the yield side is base-determined for every oracle, so B1 is purely a per-attempt-cost question; K18 and K19 kill the field's oracle ideas |
| B2, Semaev solving degree | Nothing in the field touches Gröbner degree (K23) |
| B3, prime IC constants | C1 and C3 are instruments. Table B rows are prime order, so C3 is 0 there, and the widening 5.47× → 13.5× gap is the r^{1/6} exponent of the m = 2 table oracle (SO-TABLE), not a constant |
| B4, SAT/XOR on ECC2K-130 | Out of field |
| B5, Koblitz Jacobian carriers | K20 (computed zeta identity, no obstruction) |
| B6, generic and rho | K22 |
| B7, transfer | C2 decides the Miller lead; K21 for F_{p^6} |

## 6. Killed candidates, with reasons

**New this round**
- **K15. Completion ledger for coordinate statistics** (the prior run's C2, demoted). Bound: ‖φ̂‖₁·(3√p+1).
  - Rerun here: Fourier-L1 exponents Thue–Morse 0.400 and Rudin–Shapiro 0.496 at p ≈ 2^22, with LSB and single digits O(log p).
  - (i) The technique is already Theorem W of the approved H-ECDLP-f6a43a ("Kohel-Shparlinski plus completion").
  - (ii) `LEAD-EXO-coordinate-statistic-leakage`'s next step is exactly Thue–Morse and Rudin–Shapiro. For translation correlation the cap is ‖φ̂‖₁²/√p, which is vacuous for both. For the HNP lead, Thue–Morse is capped only at β ≥ 0.1, short of 1/4.
  - So it cannot decide that next step.
- **K16. Polynomial-hint agreement bound** A(d) ≤ 2 + (2d+1)√p(ln p + O(1)) for `LEAD-EXO-invertible-hint-subset`. A duplicate of Theorem W in H-ECDLP-f6a43a. The literature analogue is Lange and Winterhof, *Polynomial interpolation of the elliptic curve and XTR discrete logarithm*, COCOON 2002, LNCS 2387, 137–143 (retrieved at abstract level: degree lower bounds for polynomials interpolating the EC discrete log). The bound sits about √p above the random-labelling level d+1, so it cannot decide the lead's discriminator; it closes only the d = n^{o(1)}, α > 1/2 regime, which H-ECDLP-f6a43a already states.
- **K17. Katz–Sarnak / Deligne second moment of decomposition-count families** on subgroup bases. Haar E|tr U|² = 1 gives κ₂ → 1. It explains, but adds nothing to, the measured κ₂ = 1 + O(coincidences); variance can only lower coverage (F2).
- **K18. A B1 non-enumerative oracle by counting points on the decomposition cover C_R** (Schoof–Pila, Harvey or Kedlaya, or a character expansion). For a μ_d base, C_R is a (Z/e)²-cover of genus about e² ≈ p²/d², and the character expansion needs e² sums of conductor about 6. Either way the cost is ≥ √p per target.
- **K19. Subgroup character-sum bounds** (Bourgain–Glibichuk–Konyagin; Heath-Brown–Konyagin; recalled) for μ_d bases. They bound one-variable sums over subgroups; c(R) is a two-variable correlated count with (p/d)² characters, so the F1 threshold is d ≥ p^{3/4}. The mean is fixed by conservation anyway.
- **K20. B5 carrier zeta identity** (computed here). If J(C) ~ A with g = n − 1:
  - Z_C(T)·Z_E(T) = L_{E/F_{2^n}}(T^n)/((1−T)(1−2T))², so N_k(C) = 2(2^k+1) − N_k(E) for n ∤ k.
  - Place positivity holds: for ECC2K-130's a_1 = −1, P_1 = 2, P_2 = 0 and P_3 = 4. Integrality at k = n is automatic (a_131 ≡ a_1 mod 131).
  - No obstruction; at most an early-abort filter (a constant) for the lead's own n = 11, 13 ladder. The Torelli-rarity heuristic is the lead's own (prior K12). Out of field priority.
- **K21. B7 Teske F_{p^6} weak-class walk length** via Cohen–Lenstra and 2-volcano statistics. Weakness is a 2-torsion Galois condition per curve, not a class statistic. The lead's own measurement of the public ISO-1 walk cost is cheaper and decisive.
- **K22. B6 H-invariant degree bound** via character positivity. #{(a,b): |a|,|b| ≤ T, a/b ∈ H} ≥ 4T²h/N holds rigorously, but forces non-trivial ratios only for T > N/h, giving deg ≥ h²/(2N). That is vacuous at h ~ N^{1/3}, and degree is not cost (prior K11).
- **K23. B2 via Chebotarev/Sato–Tate choice of p or curve.** The instance is fixed. The p − 1 of deployed primes is fixed. The subgroup-base β_work 0.647 already uses the best tower. Nothing in the field touches solving degree. SO-MONO (quoted below) closes cycle-type probes.
- **K24. Bhargava-style family averaging** (Bhargava–Shankar Selmer averages; geometry-of-numbers counts; recalled). These describe families of curves, not a fixed instance. Any family average of decomposition counts collapses to conservation (KN-FIND-007), and height counting feeds xedni, closed by Jacobson–Koblitz–Silverman–Stein–Teske (`LEAD-ICP-char0-lifting-xedni-smoothness`). No handle on one fixed E.

**Carried from the prior file.** The reasoning was re-checked here; no new measurement.
- K1: best-of-K isomorphic model by short-interval density. A √(2 ln K/X) gain that vanishes with size, dominated by selection cost.
- K2: target preselection by count deviation. Markov; the 1.582 cap.
- K3: Chebotarev or Katz–Sarnak cycle-type census on Semaev covers. SO-MONO, `LEAD-ICE-semaev-cover-monodromy` [proof]: "… on the factor-base locus S_m splits completely with an exact root multiset, so the generic-fibre cycle-type census is a no-go as a relation-rate probe at every m >= 3 (KN-FIND-4f0d84). GOAL-MONO-001 completed under DEC-20261022-a0f165."
- K4: proving Poisson for c(R) in the IC regime. F1 (incomplete sums); and F2 even if proved.
- K5: elliptic sum-product energy bounds. They sit far above random and cannot close anything.
- K6: small-coefficient model selection for small-root decomposition. Only in the lifting regime, which `LEAD-ICP-char0-lifting-xedni-smoothness` closes.
- K7: target-dependent multiplicative-coset base. No shared basis; a known-log pool (SO-TABLE).
- K8: subgroup base with sparse elimination. Total cost ≈ p at any d.
- K9: Ulmer high-rank surfaces. SO-XEDNI and the open step of the global-lift lead.
- K10: small-|D| non-unit endomorphism orbits. `LEAD-STR-small-cm-disc-nonunit-endo`.
- K11: B6 H-invariant rational-function census. Degree is not cost.
- K12: DiPippo–Howe counting for the Jacobian carrier. Duplicates the lead's heuristic.
- K13: Cohen–Lenstra or Gekeler group-structure selection on prime-order curves. SO-ISO; group structure varies only with a cofactor (C3).
- K14: Duke CM-point equidistribution for the class-group bridge. A GGM simulation lemma; no handle.

## 7. Match log

All 12 phrasings were run through `lead_atlas.py --match` and `build_frontier_map.py --match` with the three `LEAD_ATLAS_*` variables exported. The log is `scout/arith-stats-r2/match.out`.

Every candidate's top hits are the leads it decides. No KR row forecloses a mechanism: the top frontier rows are KR-IC-5931ee, KR-IC-5a43e5, KR-RHO-53c89f and KR-RHO-755e35, all generic context. So each candidate advances an existing lead's next_action and is not a duplicate lead.

## 8. Citations

| reference | used for | provenance |
|:--|:--|:--|
| Kohel, Shparlinski, LNCS 1838 (2000) 395–404, Cor. 1 | C2 special case | retrieved: bibliographic record and abstract via search; statement read in Ahmadi–Shparlinski arXiv:1302.4210v3, Lemma 1 (PDF text extracted this session); author PDF unreachable |
| Ahmadi, Shparlinski, arXiv:1302.4210v3 (2013) | Lemma 1 text | retrieved |
| Deligne, Weil II (1980); SGA 4½; Grothendieck–Ogg–Shafarevich | C2-Theorem (Kummer version) | recalled |
| Lange, Winterhof, COCOON 2002, LNCS 2387, 137–143, DOI 10.1007/3-540-45655-4_16 | K16 | retrieved at abstract level (TU/e research portal); exact bound not read |
| Paley, Zygmund (1932) second-moment inequality | C1 band (textbook step) | recalled |
| Arratia, Goldstein, Gordon, Ann. Probab. 17(1) (1989) 9–25 | C1 Poisson reading of κ₂ | retrieved: bibliographic record and abstract via search |
| Mérai, Publ. Math. Debrecen 80 (2012) 199–213 | C2 multiplicative-character analogue | retrieved as cited reference [22] in arXiv:1302.4210v3; not read |
| Tate, Invent. Math. 2 (1966) | C1 transport, SO-ISO T1 | recalled |
| Kohel thesis (1996) | C3 ℓ-Sylow by level | recalled |
| Miret, Sadornil, Tena, Tomàs, Valls, Publ. Mat. Extra (2007) 165–180; Miret, Moreno, Sadornil, Tena, Valls, Appl. Math. Comput. 176 (2006) 739–750 | C3 ℓ-Sylow structure against volcano level | retrieved at abstract and bibliographic level; theorem text not read; structure also in program data (retrieved) |
| Lauter, Stange, SAC 2008 | C2 r_k / EDS association | recalled |
| Katz, Sarnak (1999); Bourgain–Glibichuk–Konyagin; Heath-Brown–Konyagin | K17, K19 | recalled |
| KN-FIND-007; ORACLE_FORMAT.md; EXP-ECTD-0cf008 prepared inputs and sealed raw-results; H-ECDLP-f6a43a; E3a n0.json and regression.json; v2.1 volcano data; lead YAMLs | C1, C3, kills | retrieved (repository records read this session) |

## 9. Files

All files are under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.

| item | files |
|:--|:--|
| This dossier | `scout-arithmetic-statistics.md` |
| Prior dossier | `scout-arithmetic-statistics.prior-run-1852.md` |
| C1 | `arith-stats-r2/popcov.cpp`, `popsample.cpp`, `paircoin.cpp`, `pop/*.out` (12 exact P29 bases), `p37/*.out` (sampled P37) |
| C2 | `scripts/miller_u_spectrum_v2.py`, `arith-stats-r2/miller_u_spectrum_v2.rerun.out` |
| C3 | `scripts/volcano_{kg,compare,chi2}.py`, `arith-stats-r2/volcano_*_v21.rerun.*`, `n0_identity_check.rerun.out`, `e3a_slope.rerun.out` |
| K15 | `arith-stats-r2/digit_l1.rerun.out` |
| Obstruction quotes | `arith-stats-r2/so_quotes.txt` |
| Match log | `arith-stats-r2/match.out` |
