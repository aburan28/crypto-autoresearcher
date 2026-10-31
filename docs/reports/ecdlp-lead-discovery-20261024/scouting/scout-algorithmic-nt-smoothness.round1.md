# Scout dossier: algorithmic number theory, smoothness and sieving

Field: smoothness and sieving (NFS/FFS, Pomerance, Canfield-Erdos-Pomerance), ECM stage-two batching, descent trees, large-prime variations, function-field sieve analogues (over F_p(t) and over the function field of E), relation collection as a smoothness problem.

Scope: prime field first (B1-B3), then binary/Koblitz (B4, B5). This is a proposal dossier. Nothing here is an experimental outcome unless it is marked **computed**. Computed means arithmetic I ran myself in `calc/` with the program's own conventions, not a measurement on curves. Expected values are marked **prediction**, and each one names its heuristic (H1-H7, section 6).

Inputs read in full:
- ATLAS.md (all families) and KRMAP.md
- object-frame-ideation.md, sections 1-3
- idea-generator.md ("Search heuristics", "Obstructions as generative material")
- target-result-profile.md, Part A
- LEADERBOARD Tables A-C and the phase table
- FRONTIER, prime toy section

Lead YAMLs read: ICP-residual-partial-relations, ICE-relation-graph-rank-large-prime, ICE-prime-field-semaev-solving-degree, ICE-charged-toy-ic-exponent-vs-rho, ICP-prime-ic-constant-engineering, ICP-coppersmith-smallroot-semaev, ICB-ecc2k130-jacobian-carrier, ICP-icperf-writability-boundary, and the obstruction statements of every SO lead quoted below.

Ledger and analysis records read: EV-SDEG-4a1c3d, EV-RELN-3c9a24, H-RELN-940f14, H-BINSTD-555991, IDEA-20260727-003, IDEA-20260731-012, H-ECDLP-d73cdb, IDEA-20261002-8f26ce, KN-FIND-aa2efc, analysis/smallroot-reach/{CLOSURE,CORRECTION}.md, EXP-ICPERF-783e9e budget_table.json.

Provenance: two load-bearing citations were checked with WebSearch at bibliographic or summary level and are marked **retrieved**. Everything else is **recalled**.

---

## 0. Why the field has so little direct purchase on E(F_p) (one paragraph, so nobody re-derives it)

The correspondence from smoothness to elliptic-curve decomposition is exact in one respect. A random point has about |F|^m/(m! N) decompositions into m points of a base of size |F| = N^{1/u}. At m = u that is 1/u!, which is about (e/u)^u. This is the Dickman rate u^{-u(1+o(1))} (Canfield-Erdos-Pomerance 1983, recalled).

So "smooth points" are as common as smooth integers. Every route then fails at the same place, the divisibility test. In Z, testing q | n is O(1) per q, and dividing out q shrinks the archimedean size. That size is what makes sieving (periodicity mod q), special-q lattice sieving and descent work.

On E(F_p) none of these exists:
- "Is P_1 a summand of R?" is always true, because R - P_1 is just another point.
- No size decreases under subtraction.
- The only modulus is p itself, which is larger than every sieve box.

The structural consequence is that every surviving lead from this field is about relation-combination accounting (large primes, cycle structure, budgets). None of them is a new divisibility test. Sections 1-4 are four such leads: two prime-field and two binary/Koblitz. Section 5 records the constructive ideas I tried and killed.

---

## 1. Candidate PC1 (prime, B1/B3): attempt-edge lemma. At arity m = 2 no oracle and no large-prime scheme beats rho

**Bottleneck.** This is B1 and B3 at m = 2, the arity of every Table B recipe ("folded, walked, m = 2"). It also covers the two open m = 2 large-prime lanes:
- LEAD-ICP-residual-partial-relations: 1LP sweep, exponent (1+beta)/2.
- LEAD-ICE-relation-graph-rank-large-prime: 2LP summation multigraph, B = p^{1/5}, B2 = p^{2/5}.

**External ingredients.**
- Large-prime cycle accounting: cycles = E - V + C. Lenstra-Manasse, "Factoring with two large primes", Math. Comp. 63 (1994), recalled.
- The genus/degree threshold of the double-large-prime variation: Gaudry-Thome-Theriault-Diem, Math. Comp. 76 (2007) 475-492, **retrieved** (bibliographic plus abstract-level summary, ePrint 2004/153). The n = 2 instance of Gaudry's O~(q^{2-2/n}) gives q = sqrt(group). Gaudry, J. Symb. Comput. 44 (2009), **retrieved** at summary level (MaRDI record; Vitse slides).
- The random-graph threshold for the first dependency: Erdos-Renyi (1960) and Janson-Knuth-Luczak-Pittel (1993) on complex components, both recalled.

**Mechanism and derivation.**

Setup:
- Full base F' = {x < B2}, with n ≈ B2 x-classes (sign-folded). The small base F ⊂ F' may be empty.
- An attempt is one fresh target R = aP + bQ, costing at least 1 GAE.
- The oracle (any oracle, including a free non-generic one) returns the 2-decompositions R = ±P_i ± P_j with P_i, P_j ∈ F'. Each returned relation costs at least 1 GAE, because the points must at least be formed.

Expected relations per attempt: y = #{unordered x-pairs} · (sign patterns)/N ≤ 2n²/N.

Relations with large legs are edges of a multigraph on the n vertices, with the small base merged into a root vertex. A dependency among targets needs a connected component with E_comp ≥ V_comp + 1, or a parity-balanced cycle.

**Lemma (under H1).** Model the multigraph as G(n, M). The first dependency appears at M* = c·n with median c ≈ 0.47. For c < 1/2:

  P(balanced cycle) ≈ 1 - exp(¼ ln(1 - 2c))

which reaches 1/2 at c = 0.469. Complex components only arrive at c ≈ 1/2.

Hence the total cost, attempts plus relations, satisfies

  T ≥ c·n·N/(2n²) + c·n = c·N/(2n) + c·n ≥ c·sqrt(2N),

minimized at n = sqrt(N/2). This holds for every choice of B, B2, small/large split and oracle. The m = 2 exponent is exactly 1/2. The floor is about 0.66·sqrt(N) at c = 0.47, against ideal negation-rho sqrt(πN/4) ≈ 0.886·sqrt(N). That leaves at most about 1.34x headroom over ideal rho before any oracle cost or linear algebra is charged. Measured rho.negation is 1.45x the floor at toy scale, so the realised margin is that of an idealised tie.

This is Gaudry's n = 2 boundary, transported to prime-field small-x bases, extended to arbitrary large-prime schemes and arbitrary (non-generic) oracles.

**Corollaries that decide leads.**

(a) EXP-RELN-c5a377 geometry (B = p^{1/5}, B2 = p^{2/5}):
- Attempts ≥ c·p/(2·B2) ≈ p^{3/5}/4, against rho p^{1/2}. With the honest enumeration oracle (B2 per attempt), S is about p^{1}.
- **Computed** from that run's frozen exact-yield design table (coordination/.../TASK-20261001-5a45b1/exact_yield_budgets_out.json, label-free; no new run). The frozen κ = 1 attempt budget A_1, divided by ideal rho sqrt(πq/4), is:
  - 2.9-3.6 at 16 bits
  - 4.1-4.7 at 20 bits
  - 5.1-6.1 at 24 bits

  That is about 0.10 per bit of log2 q, i.e. growing as q^{1/10}, as the lemma predicts. At κ = 2 the ratio doubles.
- **Prediction**: whole-solve S/matched rho in that lane is at least these ratios (attempts alone, oracle uncharged) and grows as q^{1/10}. The lane's discriminating quantity (δ against 1/4) cannot change this.

(b) LEAD-ICP-residual-partial-relations (sweep with 1LP, cost N^{(1+β)/2}). Two separate statements; the disposition is the coordinator's call:
- **Prediction for the lead's own test.** The ladder should show an IC-baseline improvement with relation-phase exponent (1+β)/2, below the incumbent 2/3 for β < 1/3. The lead counts that as a positive outcome ("distance to rho shrinks but stays > 1"), and the owner's criterion (LEAD-ICP-prime-ic-constant-engineering) values gains over the IC baseline.
- **On ECDLP cost.** At every β the method is dominated by bsgs.negation and rho.negation: its optimum β → 0 is a birthday collision among targets with stored partials, BSGS-shaped with memory sqrt(N·B). It cannot reach rho. The lemma gives the floor for any m = 2 variant.

**Quantifier scope of the lemma.** It covers non-adaptive target schedules under H1. Adaptive schedules, for example decomposing L_i + S with S fresh to grow edges at an existing vertex, produce rows {L_i, X, Y} with X and Y still uniform over F'. Such rows cannot concentrate inside a chosen vertex set W, since P(X, Y ∈ W) = (|W|/n)². So I expect c to be unchanged, but a proof for adaptive schedules is open and stated as such.

(c) Table-oracle variant (pair table of S entries plus 1LP or 2LP):
- Hit-count model (H2): T lookups yield T·S/N relations, and at least sqrt(S) vertices must be covered. So T ≥ N/sqrt(2S) and S + T ≥ 1.5·N^{2/3}. That is the same leading constant as the no-LP optimum (|F| = N^{1/3}, cost 1.5·N^{2/3}).
- **Prediction**: an LP arm added to the folded/walked recipe gives whole-solve ratio 1.00 [0.9, 1.1] in GAE. Large primes shift work from linear algebra to the table, and linear algebra is 0.0-0.4% of Table B's S anyway.

(d) B3 re-read from data already on the board (section 3): the board's "widening" is mostly the matched-rho reference converging. On same-recipe rows fp14 → fp24, rho S/sqrt(r) goes 2.03 → 1.04 while IC S/sqrt(r) goes 13.1 → 14.0, so about 90% of the 2.10x log-widening is rho's. Combined with (c), the m = 2 recipe's asymptotic ratio to rho grows as N^{1/6}. Constant engineering cannot produce a crossover. The engineering lead remains valid only as engineering.

**Representation and operation pair.** The representation is R1: x-coordinates in [0, p) split into small/large classes by an archimedean bound. The operation set Σ is translation by full-base elements plus cycle combination on the large-prime graph. Trichotomy: **partial-action** (Class I index calculus; the relation vector propagates only under translation by base elements, and the branching event "a decomposition exists" is priced by y).

**SO codes touched.** PC1 is a closing proof. It escapes nothing; it extends obstructions beyond their stated premises.
- SO-TABLE (LEAD-ICP-generic-table-decomposition): "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). ... Scope: any generic (enumeration/table) decomposition over F_p." PC1 removes the premise "enumerates or table-looks-up": at m = 2 the sqrt(N) floor holds for every oracle.
- SO-GEN (LEAD-RHO-generic-sqrt-lower-bound): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations ... Scope: all generic algorithms, any field, any r." PC1 is a non-generic analogue at m = 2, holding under H1. It does not escape SO-GEN; it adds a second wall that does not need the generic-model premise.
- SO-ALGFB (LEAD-ICP-algebraic-membership-factor-base): "mean per-target yield is binomial(B+m-1, m)/N for every base of size B ... Scope: prime-order E/F_p, any base of size B." Used, not escaped: y is the conservation mean.

**First discriminating step.**
1. Write the one-page lemma with explicit quantifiers: for all B, B2, splits and oracles, the expected cost of a dependency is at least c·sqrt(2N), with c the G(n,M) first-dependency constant.
2. Validate c with a free-oracle m = 2 simulation on prime-order toy curves at 16, 20, 24 and 28 bits:
   - Exhaustive, uncharged full-base pair enumeration at B2 ∈ {N^{0.4}, N^{0.5}}.
   - Record M*/n at the first target dependency.
   - Compare against G(n,M) and a degree-preserving rewire null, plus a relabelled Z/N control.
3. Read the attempts-to-first-dependency from the existing EXP-RELN-c5a377 v4 generator. No new generator is needed.

Outcomes:
- M*/n ∈ [0.3, 0.7] and attempts ≥ c·p/(2·B2):
  - LEAD-ICE-relation-graph-rank-large-prime, m = 2 arm → **closed_obstructed(proof)**.
  - LEAD-ICP-residual-partial-relations: its ladder is predicted to read as an IC-baseline improvement under the lead's own test, while being dominated on ECDLP cost by bsgs.negation and rho.negation at every β. Recommend **closed_dominated** for the ECDLP question, and leave the IC-baseline ladder as optional engineering at the coordinator's discretion.
  - LEAD-ICP-prime-ic-constant-engineering keeps open_next_step for engineering only; its "distance to rho" cannot reach 1.
- M*/n < 0.1 at two or more sizes (dependencies far earlier than random) → **open_next_step**, best_measured = M*/n. That would be a real structured-coincidence signal contradicting H1, the most valuable outcome this step could produce.
- Attempts below c·p/(2·B2) by more than 2x → the lemma's accounting is wrong → **open_next_step** (instrument audit).

**Tier.** X (a proof deciding exponent questions; it moves no exponent itself).

**Predicted gain.** 0 in exponent. The absolute m = 2 floor is about 0.66·sqrt(N) (H1, c = 0.47), at most 1.34x below ideal negation-rho before oracle or LA cost. LP arm on the table recipe: 1.00 [0.9, 1.1] (H2).

**Cost.** Implementation 1-2 days (derivation 0.5 day; simulation 1 day). Compute under 10 core-hours (28-bit full-base pair enumeration).

**Self-kill risk.** The proof is unlikely to be wrong, but it may be judged "implied by Gaudry n = 2 plus SO-TABLE". Its value is that it closes two open lanes without the 16-32-bit ladder they currently ask for.

**--match phrasings (top hit each).**
1. Own: "attempt-edge lemma: arity-2 point decomposition with any oracle and any large-prime cycle scheme costs at least c*sqrt(2N)". Top hit: LEAD-ICE-rootfind-pairtable-oracle (15), then LEAD-ICE-generic-oracle-arity-cost-floor (13).
2. Plain: "splitting a point into two factor-base points can never beat Pollard rho, even with large primes or a perfect solver". Top hit: KR-RHO-6239aa (13), then LEAD-ICE-relation-graph-rank-large-prime (12).
3. Obstruction vocabulary: "decomposition oracle enumerates or table-looks-up factor-base elements m = 2 two-term model residual partial relations". Top hit: LEAD-ICP-residual-partial-relations (16), then LEAD-ICP-generic-table-decomposition (14).

---

## 2. Candidate PC2 (prime, B2/B1): large-prime-aware floor, budget and reach calculus. Corrects the "m ≤ 4 is empty" claim and sets the O5 spec

**Bottleneck.** B2: the measured β_work is 0.797 or 0.647 against the 0.30 gate. B1: the O5 non-enumerative oracle is unbuilt, and its target arity and budget are set by a no-large-prime model.

**External ingredients.**
- GTTD (2007), **retrieved** as above: small base of size Q^{1-1/m}, at most 2 large legs, O~(Q^{2-2/m}) for both phases.
- Gaudry (2009), **retrieved** at summary level: O~(q^{2-2/n}) under Heuristic result 3.
- For the reach side: the Jochemsz-May extended strategy (ASIACRYPT 2006) with the Howgrave-Graham criterion (IMA 1997), both recalled. The program's corrected calculator is analysis/smallroot-reach/CORRECTION.md (CORR-20261024-b2a799).

**Mechanism and derivation.** Prime-order E/F_p. The full base is {x < Q}, Q = N^β. The small base is {x < Q^r}, so β_s = rβ.

A useful partial has at least m-2 small legs. Per attempt:

  yield ≈ (Q^r)^{m-2}·Q²/((m-2)!·2·N)

Edges needed ≈ Q (the large vertices). Attempts ≈ Q^{1+(1-r)(m-2)}·N^{1-mβ}. Sparse linear algebra ≈ w·Q^{2r} (H4). With mβ = 1 (decompositions Θ(1), the GTTD regime):

1. **Free-oracle floor** (H3, H4): e*(m) = 2(m-1)/m² at r = 1 - 1/m.
   - m = 3: **4/9 = 0.444**. m = 4: **3/8**. m = 5: 8/25. m = 6: 5/18.
   - This **contradicts** IDEA-20260727-003 ("admissible region ... EMPTY for every m <= 4 and non-empty only for m >= 5"). That free-oracle model, max(B, c_LA B^ω), has no large primes and no scope limit.
   - The clause in the SO-TABLE statement "m = 3 only ties rho even with T_dec = O(1)" is scoped to enumeration and table oracles, where it stands: a full-base pair table has Q² = N^{2/3} > N^{1/2} entries. It **does not extend** to non-table O(1) oracles.
   - Arithmetic check: B_s = N^{2/9}, attempts B²/B_s = N^{4/9}, LA B_s² = N^{4/9}.
   - Memory: about Q = N^{1/3} stored large-prime edges at time N^{4/9}. That is cheap next to a table, but it is not rho's O(1) plus distinguished points, so time×memory comparisons must charge it.

2. **Per-attempt oracle budget** at target total exponent e (oracle cost N^{β_o}):
   - With r < 1: β_o,max(e, m) = e·m/2 - (m-1)/m.
   - With r = 1: β_o,max = e - 1/m.
   - At e → 1/2: m = 3: **1/12**. m = 4: **1/4** (approached from below; at r = 1 linear algebra ties). m = 5: 0.30, unchanged, the program's gate. m = 6: 1/3.
   - Large primes never raise the e → 1/2 gate at m ≥ 4, because r is capped at 1. What they do is make m = 3 and m = 4 feasible at all, and lower the attainable e.
   - The cheapest systems the O5 oracle could target are S_4 (per-variable degree 4) and S_5 (degree 8), with the budgets above. Today's target is m ≥ 5 (S_6, degree 16).
   - Every measured backend is far over budget: the serial-split B0 floor is 0.59-0.67, B1 is 0.797, against at most 1/12 at m = 3.

3. **Reach demand for poly-time lattice oracles** with large primes. The box volume exponent is V = 2β + (m-2)β_s.
   - Minimising V under the collection and LA constraints gives V ≥ m/(2(m-1)) for m ≥ 4, the same as CLOSURE.md's ε_required(m, 0). So large primes do not lower the demand at m ≥ 4.
   - At m = 3 (infeasible without LP), V(e) = 2 - 5e/2: 0.75 at e = 1/2, 0.889 at e = 4/9. That 8/9 coincides numerically with ε_required(4, 2) but is a different object.
   - **Computed** supply (`calc/s4_reach.py`, the program's `jm_reach_extended` with the HG exponent t·dim - s_p): the target-side S_4(x1, x2, x3; x_R) block has generic support equal to the full box [0,4]³ (125/125 monomials). Its JM-extended HG reach is **0.121** (Richardson from t = 4, 8: 0.0777 and 0.0995; full-box closed form 2/(d(n+1)) = 0.125).
   - The reach is identical for the balanced box and for every large-prime-shaped box tried ((2/3,1,1), (1,1,2/3), (1/3,1,1)). The support is a full box, so JM volume reach is shape-invariant, and making the box unbalanced gains nothing for S_4.
   - Margin ≤ 0.121 - 0.75 = **-0.63**.

**Representation and operation pair.** The representation is R1 (interval x-bases, membership by archimedean inequality: lattice-describable, the open class of CLOSURE.md §0). Σ is translation by base elements plus large-prime cycle combination, as in PC1. Trichotomy: **partial-action**.

**SO codes and premises.**
- SO-TABLE: quoted in PC1. Escaped only through its premise "enumerates or table-looks-up": the floor and budget apply to algebraic or lattice oracles. The m = 3 "only ties" clause is corrected for non-table oracles.
- SO-GEN (quoted in PC1). Premise "any generic algorithm": a lattice oracle reads coordinates, so it is outside that premise.
- SO-ALGFB (LEAD-ICP-algebraic-membership-factor-base): "A target-independent algebraic locus of degree d yields O(d) usable points ... mean per-target yield is binomial(B+m-1, m)/N for every base of size B ... Scope: prime-order E/F_p, any base of size B." The interval base is not an algebraic locus, so that premise is escaped. Yield conservation is used, not escaped.
- LEAD-ICE-generic-oracle-arity-cost-floor (no SO code; binary): "on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc) ... Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells." The product law there has no large primes. The binary analogue of this correction is already in H-BINSTD-555991 (2LP budget 2^{8.71} at m = 3), so PC2 is the prime-field counterpart.

**First discriminating step.**
- (a) Done here, computed: reach supply 0.121 for S_4, against demand ≥ 0.75. Next, run the optimal-shift construction (Ryan 2025; Feng-Luo-Chen-Nitaj-Pan, as the Coppersmith lead's own next step names) on the same S_4 block.
- (b) Free-oracle m = 3 GTTD ladder on prime-order toy curves at 20/24/28/32 bits:
  - Full base Q = ⌈(6N)^{1/3}⌉ x-classes; uncharged exhaustive oracle (enumerate x_3 < Q, then look up R - P_3 in the full-base pair table, at most 2^{22} entries at 32 bits).
  - r ∈ {2/3, 3/4, 1}.
  - Measure attempts to |F_s| independent rank and the cycle rank, against the predicted Q^{2-r}·(constant) and G(n,M).
  - Controls: rewire null, relabelled Z/N group, planted dependency.

Outcomes:
- (a) Optimal-shift reach still < 0.75 → Coppersmith/JM route at m = 3 with LP → **closed_obstructed(cost_model)**. This appends the m = 3 row that CLOSURE.md lacks to LEAD-ICP-coppersmith-smallroot-semaev. Reach ≥ 0.75 → **open_next_step** (planted S_4 recovery at 40-56 bits).
- (b) Fitted attempt exponent within ±0.05 of (2-r)/3, and cycles tracking G(n,M) → the instrument is validated. Record the corrected floor as a correction to IDEA-20260727-003 and to the SO-TABLE m = 3 clause. Move LEAD-ICE-charged-toy-ic-exponent-vs-rho's O5 spec to S_4/S_5 with the budget table → that lead stays **open_blocked**, but with a numeric acceptance target.
- (b) Exponent ≥ (2-r)/3 + 0.1, or cycle depletion → the large-prime floor fails for prime-field point decomposition → **closed_obstructed(measured)** for prime m = 3 LP, and the "m ≤ 4 empty" claim is confirmed.

**Tier.** X (an exponent of the floor and gate; no realised speedup).

**Predicted gain.**
- Free-oracle floor exponent 0.444 at m = 3 and 0.375 at m = 4, prediction under H3/H4, against the stated "≥ 0.5 (empty)".
- Realisable gain with any known oracle: **0**. Lattice: 0.121 against 0.75 (computed; H7 for strategy dependence). Groebner: ≥ 0.59 against a 1/12 budget.

**Cost.** Implementation 2-3 days (simulation plus optimal-shift reach). Compute under 50 core-hours.

**Self-kill risk.** H3 might fail if structured bases concentrate legs; EV-RELN-3c9a24's null match argues against that. The correction could be judged "obvious once said". It changes where O5 should aim but supplies no oracle.

**--match phrasings (top hit each).**
1. Own: "double large prime free-oracle floor N^{2(m-1)/m^2} admissible at m = 3 and m = 4 prime-field Semaev". Top hit: LEAD-ICP-residual-partial-relations (21), then LEAD-ICP-digit-presentation-solving-degree (14).
2. Plain: "with two large primes a perfect three-point decomposition solver would beat rho over prime fields". Top hit: KR-IC-a4dd54 (17), then LEAD-ICE-relation-graph-rank-large-prime (15).
3. Obstruction vocabulary: "m = 3 only ties rho even with T_dec = O(1) free oracle floor admissible region empty for every m <= 4". Top hit: LEAD-ICE-generic-oracle-arity-cost-floor (15), then LEAD-ICP-generic-table-decomposition (13).

---

## 3. Supporting reanalysis for B3 (not a candidate): where the Table B "widening" comes from

Table B prime rows, S/sqrt(r) in GAE. All rows below use the same recipe ("folded, walked, base at the family optimum, m = 2"). The fp12 row, the board's 5.47x endpoint, uses a different recipe ("folded table, walked targets") and is set aside to remove that confound.

| log2 r | IC S | rho S | ratio |
|--:|--:|--:|--:|
| 14.0 | 13.1 | 2.03 | 6.43 |
| 18.0 | 8.41 | 1.45 | 5.82 |
| 23.4 | 14.0 | 1.04 | 13.5 |

From 14.0 to 23.4 bits, the rho reference falls by ×0.51 and IC moves by ×1.07. About 90% of the 2.10x widening, in log terms (log2 1.95 / log2 2.10), comes from the rho reference converging toward its asymptote (floor 0.886). IC's own excess appears only from 18 bits: log2(14.0/8.41)/5.4 = 0.136 per log2 r, against 1/6 for an N^{2/3} recipe. That is short-range and three points. (Including the different-recipe fp12 row, 15.6 → 14.0 against 2.85 → 1.04, gives the same conclusion.)

The atlas quotes the widening as exponent evidence in the SO-TABLE statement. It should cite the N^{2/3} model (PC1(c)) instead. It also ties into LEAD-RHO-matched-rho-calibration: there is no prime medium-tier rho bound, so Table B's ratios carry the rho finite-size bias.

**Prediction**: at fp28 (log2 r ≈ 28), IC S/sqrt(r) ≈ 14·2^{4.6·0.136} ≈ 22, rho ≈ 0.95-1.0, ratio ≈ 22-23x.

---

## 4. Candidate KB1 (binary/Koblitz, B4): a double-large-prime column for the writability wall

**Bottleneck.** B4, LEAD-ICP-icperf-writability-boundary, closed_obstructed: "At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]."

Its evidence (EV-ICPERF-784b25 Q1) says: "Charging sparse linear algebra against rho caps the factor-base dimension near n/4 + log_2(R)/2 ... The minimum viable arity is 4 at every degree without the Frobenius orbit quotient." That is a no-large-prime statement. With two large primes, the linear-algebra cap binds only the small base, and the decomposition box (full base) can grow until p_2 ≈ 1.

**External ingredient.** GTTD (2007), **retrieved**, in the (m-2, 2) partial form the program already approved for binary pricing (H-BINSTD-555991, heuristics H-621974-1..3). The new step is to apply it to the writability quantity, which H-BINSTD-555991 does not compute.

**Mechanism and derivation.** **Computed** with `calc/lp_writability.py`, using the conventions of EXP-ICPERF-783e9e's budget_table.json (read-only):
- budget = log2 rho - log2 attempts
- ANF = log2 Σ_{k≤deg} C(vars, k), deg = 3·2^{m-2}
- small-base dimension l_s = the table's LA-capped l (same LA charge)
- p_2 = (B_s^{m-2}/(m-2)!)(B'²/2)/N, attempts = θ·B'/p_2 with θ = 1, constraint p_2 ≤ 1
- scan the large-leg dimension l'

| n | no-LP best deficit (arity) | 2LP m=3: deficit [l_s, l', vars, budget, ANF] | 2LP m=4 deficit |
|--:|--:|--:|--:|
| 113 | +24.15 (4) | **+21.90** [29, 42, 113, 9.42, 31.32] | regime empty |
| 127 | +24.46 (3) | **+20.01** [35, 46, 127, 12.33, 32.34] | regime empty |
| 131 (ECC2K-130) | +40.81 (4) | **+23.30** [29, 51, 131, 9.31, 32.61] | +31.79 |
| 163 (K-163) | +37.44 (4) | **+21.37** [37, 63, 163, 13.15, 34.52] | +27.83 |
| 233 | +6.26 (4) | +13.74 | regime empty (l_s cap above LP range) |
| 283 | +18.79 (4) | +11.58 | **+7.93** |
| 409 | -4.92 (4) | -0.93 | -16.36 |

**Memory: the reduction is time-only.** With θ = 1, the 2LP row stores about one partial per large vertex, so log2 memory ≈ l':

| n | log2 memory |
|--:|--:|
| 113 | 42 |
| 127 | 46 |
| 131, m = 3 | 51 |
| 163, m = 3 | 63 |
| 233, m = 3 | 87 |
| 283, m = 4 | 75 |

The no-LP rows store the LA-capped base, about 2^{l_s}: 2^{29} at n = 131. Rho with distinguished points stores almost nothing. The program ranks rows by time × memory (the c2pnb lead "loses under time x memory vs vOW"), so every 2LP deficit above is a time-only figure. A memory-charged comparison adds about 51 - 29 = +22 bits of memory at ECC2K-130.

Readings:
- With two large primes the viable arity drops to **3** (descended S_4, Boolean degree 6, square system in about n unknowns) at n ≤ 163.
- The ECC2K-130 wall falls by **17.5 bits in time**, from +40.81 to +23.30, at a memory cost of about 2^{51} stored partials. It stays positive.
- n = 233 is unchanged, because the LP regime is empty there.
- The crossover stays inside (283, 409].
- Cross-check: the computed m = 3 and m = 4 budgets at n = 131 (9.31 and 23.31) agree with H-BINSTD-555991's claim C (2^{8.71} and 2^{22.34}) to within θ and sign-convention constants.

**Representation and operation pair.** R1: x-coordinates in a fixed polynomial-basis subspace, Weil-descended ANF. Σ is translation by base elements plus large-prime cycle combination with sign canonicalisation. Trichotomy: **partial-action**.

**SO codes and premises.**
- The writability statement (quoted above): its premise "best viable arity" was computed without large primes, and that premise is the one escaped. The conclusion "+ bits over budget" survives with smaller numbers.
- LEAD-ICE-generic-oracle-arity-cost-floor (quoted in PC2): its "free oracle at m = 3 still costs 2^68.58" is no-LP. The 2LP column already exists internally (H-BINSTD-555991).
- SO-FROB (LEAD-ICB-frobenius-orbit-factor-base): "At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty ... Scope: Koblitz/subfield curves over F_{2^n}, n prime". Not escaped; no orbit gain is used.

**First discriminating step.** Zero compute.
1. Append the 2LP column above to the writability table, with θ ∈ {1/2, 1} and the cycle-weight w of H-621974-3 added to the LA charge.
2. Replace the dense C(vars, ≤6) count with the exact support of the descended S_4 on (29, 51, 51) blocks at n = 131, by symbolic monomial counting (multidegree (2,2,2) in Frobenius-linear coordinates). This takes CPU-minutes.

Outcomes:
- Every standardised n ≤ 283 still has a positive time deficit → the obstruction stays **closed_obstructed**, as it does already. Re-scoping its statement to "+23.3 at ECC2K-130 with 2LP, arity 3" is proposed only if a memory-charged (time × memory against vOW) comparison, done in the same step, leaves the 2LP row competitive with the no-LP row. Otherwise the statement stays as written and the 2LP column is recorded as a time-only annex.
- Any standardised n with time deficit ≤ 0 under the exact support **and** a memory-charged comparison not dominated by vOW → **open_next_step** for that cell, best_measured = the deficit. The cell becomes a solver question at the 2LP budget. n = 283 at m = 4 (+7.93 time; memory about 2^{75}) is the nearest; the exact support (sparser than dense) could close up to about 8 bits of time.

**Tier.** I (constant, end-to-end at fixed deployed n). It moves no exponent; it relocates a wall.

**Predicted gain.** -17.5 bits on the ECC2K-130 writability deficit, time only, at about 2^{51} memory (computed under H3/H5 with θ = 1). No ECC2K-130 attack: the wall stays +23.3 bits in time (prediction). K-163: -16.1 bits, to +21.4, at about 2^{63} memory.

**Cost.** Implementation 0.5-1 day. Compute: minutes.

**Self-kill risk.**
- The θ, sign and orbit conventions of the EV table versus H-BINSTD-555991 could move the numbers by 1-3 bits.
- The internal reconciliation may already be in flight under EXP-BINSTD-e066d8 Stage 0. If so, this is a ready prediction for that stage, not a new lead.

**--match phrasings (top hit each).**
1. Own: "large-prime budget lowers the ECC2K-130 writability wall: descended ANF size against the double-large-prime per-attempt budget". Top hit: LEAD-ICP-icperf-writability-boundary (13), then LEAD-ICB-large-prime-variants (10).
2. Plain: "with two large primes each decomposition attempt gets a bigger share of the rho budget so a bigger equation system fits". Top hit: KR-IC-a4dd54 (13), then LEAD-ICE-relation-graph-rank-large-prime (12).
3. Obstruction vocabulary: "descended ANF exceeds the whole per-decomposition rho budget at the best viable arity minimum viable arity is 4". Top hits: LEAD-ICE-generic-oracle-arity-cost-floor (13) and LEAD-ICP-icperf-writability-boundary (13).

---

## 5. Candidate KB2 (Koblitz, B5): a Jacobian carrier is a cover. The adjunction lemma plus a power calculation for the toy ladder

**Bottleneck.** B5, LEAD-ICB-ecc2k130-jacobian-carrier (open_next_step). Its next step is a toy ladder at n = 11 and 13 testing whether P_A | P_C. Its stated payoff is that hyperelliptic or plane IC on a genus 130-300 carrier would cost about 2^{37.2}. Its source proposal, IDEA-20261002-8f26ce, states: "GHS does not apply: prime n has no intermediate subfield, and this curve is not a cover of the target (KR-IC-5ea2f8)". KN-OPEN-095df5 asks for "an explicit translation and a degree".

**External ingredients.**
- Weil-restriction adjunction: Hom_k(X, Res_{K/k} Y) = Hom_K(X_K, Y). Bosch-Lutkebohmert-Raynaud, Neron Models (1990) §7.6, recalled.
- Tate's isogeny theorem over finite fields (Invent. Math. 2, 1966), recalled.
- Subexponential discrete logs in high-genus Jacobians over small fields, the payoff side (function-field sieve analogue): Enge-Gaudry (Acta Arith. 102, 2002) and Hess (2005), recalled.
- Counting isogeny classes and Weil polynomials: DiPippo-Howe, J. Number Theory 73 (1998) 426-450, **retrieved** (bibliographic). The q^{g(g+1)/4}·v_g volume formula is recalled; it was not confirmed in the retrieved text.

**Mechanism and derivation.** Let A ⊂ R = Res_{F_{2^131}/F_2}(E) be the trace-zero part (dim 130), with A simple as the lead assumes.
1. If P_A | P_C, Tate gives Hom_{F_2}(Jac C, A) ≠ 0, hence Hom_{F_2}(Jac C, R) ≠ 0.
2. By adjunction, Hom_{F_{2^131}}(Jac(C)_{F_{2^131}}, E) ≠ 0.
3. With a degree-1 divisor as base point, the Albanese property makes this a non-constant morphism φ: C_{F_{2^131}} → E.
4. Its F_2-structure does not descend, because the image meets A, not only the diagonal E_0.

So **every carrier is a cover of E over F_{2^131} by a curve defined over F_2**. The "explicit translation" KN-OPEN-095df5 asks for is exactly φ (conorm then norm, the GHS mechanism), and its "degree" is deg φ.

Consequences:
- The proposal's statement "this curve is not a cover of the target" is false for any true carrier. It holds only for auxiliary curves that merely have 131 | #Jac(F_2), which is weaker than the lead's test.
- The lead is the general cover-existence problem for prime-degree Koblitz curves. KR-IC-5ea2f8 and KR-IC-791cb7 settle only the GHS/Artin-Schreier family ("N prime ... not weak under either attack"). General covers have no genus lower bound in the KRMAP; that gap is the real open item.
- Power of the planned toy (prediction, H6). Uniform-on-Weil-polynomials counting gives expected carriers ≈ #curves(g)/#W(g):
  - n = 11, g = 10: about 2^{27}/2^{32.9} ≈ 0.017. Terms for g = 11 and 12 add about 0.012. Total ≈ 0.03.
  - The same method at n = 5, g = 4 gives 1.4, against the lead's own heuristic prediction of 0.42 through genus 8. That suggests about a ×0.3 calibration, so n = 11 ≈ 0.01. n = 13 is smaller.
  - A null result at the faithful rungs therefore has power below 5% against "rare but present". It cannot "close the route with data" as the lead's discriminates field hopes.
- The payoff side (FFS analogue) is already priced in the lead (2^{37.2}). Enge-Gaudry L(1/2, √2) puts the useful genus window up to about 250 for a 2^{60.8} rho, consistent with the lead's 130-300.

**Representation and operation pair.** R2/R3: the point is represented as a divisor class on an auxiliary curve C/F_2 through R = E_0 × A. The transfer itself is an injective homomorphism on the r-part, a change of group representation, not a lossy object. The subsequent index calculus on Jac(C)(F_2) is Class I **partial-action** (factor base = places of degree ≤ d). Σ is the F_2-Frobenius plus pullback/norm along φ.

**SO codes and premises.**
- SO-COVER (LEAD-TRF-same-field-genus-g-embedding): "Tate multiplicativity gives #Jac(C)(F_p) = N * #A(F_p) with #A = Theta(N^{g-1}); genus-g index calculus costs O~(q^{2-2/g}) >= q for g >= 2 ... Scope: prime-field source curves, any same-field cover (DEC-20260902-4c82fd)." Escaped through the Scope clause: the source is an extension-field Koblitz curve, the cover descends to the subfield F_2, and the Jacobian is a large-genus, small-field Jacobian where index calculus is subexponential.
- SO-FROB (quoted in KB1). The orbit structure is not used.

**First discriminating step.**
1. Write the adjunction lemma (half a page) and attach it to IDEA-20261002-8f26ce and KN-OPEN-095df5.
2. At n = 7, where 1,536 carriers were found, exhibit φ: C → E over F_{2^7} and deg φ for 10 of them. This is the sanity check of the lemma; for these the Weil-restriction structure already supplies the map.
3. Before any n = 11/13 run, compute the expected carrier count at the faithful rungs with the lead's own heuristic.

Outcomes:
- Lemma confirmed on the n = 7 carriers, and expected count < 0.1 at n = 11/13 → re-scope. Merge the lead into the cover/transfer family (beside LEAD-TRF-cover-catalog-jacobian-transfer) and replace the P_C-divisibility ladder with a cover-degree search. Disposition **open_next_step** (best_measured = predicted power), or **closed_known** if a reviewer accepts that the GHS/Hess literature covers all covers of degree ≤ deg_max.
- An n = 7 carrier with no map φ → the carrier test or the lemma's premises are wrong (for example A is not simple) → **open_next_step** (instrument audit).

**Tier.** X (decides an exponent-moving route).

**Predicted gain.** 0 bits on ECC2K-130. Decision value: the toy ladder's power is below 5% (H6).

**Cost.** Implementation 1-2 days (lemma; n = 7 cover extraction from the existing toy code). Compute: hours.

**Self-kill risk.** The lemma is standard. The field fit is thin; only the payoff side is from this field. The lead may already intend "carrier" in a weaker sense; if so, its divisibility test is mis-specified.

**--match phrasings (top hit each).**
1. Own: "Weil restriction adjunction: a Jacobian carrier of the trace-zero variety is a cover of E over F_2^131". Top hit: LEAD-ICB-ecc2k130-jacobian-carrier (17), then KR-IC-5ea2f8 (15).
2. Plain: "any genus-130 curve whose Jacobian contains the ECC2K-130 group must map onto the elliptic curve". Top hit: LEAD-ICB-ecc2k130-jacobian-carrier (11), then KR-IC-791cb7 (9).
3. Obstruction vocabulary: "GHS Weil descent cover attack prime extension degree no intermediate subfield isogeny factor of a genus-g Jacobian". Top hit: KR-IC-5ea2f8 (39), then KR-IC-791cb7 and LEAD-TRF-ghs-binary-composite (30), and LEAD-TRF-same-field-genus-g-embedding (23).

---

## 6. Heuristics (numbered)

- **H1** (random large-prime graph). Relations from prime-field point decomposition form a multigraph distributed like G(n, M) conditional on degrees. The first target dependency comes at M* = c·n, median c ≈ 0.47. Support: EV-RELN-3c9a24 (cycle rank matched the rewire null, 0.033 ± 0.028) and H-RELN-940f14's prior (null-matched 0.80). Validation: PC1 step.
- **H2** (table hit-count). Each lookup into an S-entry pair table hits independently with probability S/N.
- **H3** (GTTD transfer). Per-attempt counts of (m-2, 2) partials are Poisson with mean (B_s^{m-2}/(m-2)!)(B'²/2)/N, and large legs are uniform over the full base. The mean is exact by yield conservation (KN-FIND-007); the shape is heuristic (H-621974-1 analogue).
- **H4** (cycle-weight LA). Sparse LA on cycle-combined rows costs w·B_s² with w = O(m log n) (H-621974-3).
- **H5** (ANF convention). Σ_{k≤deg} C(vars, k) is the right monomial count for the (m-2, 2) unbalanced descended system. This is an upper bound; the exact support is smaller.
- **H6** (carrier count). Curve L-polynomials are spread like uniform Weil polynomials at the DiPippo-Howe volume. Uncalibrated; the n = 5 comparison suggests a ×0.3 factor.
- **H7** (lattice strategy). JM-extended reach is within a small constant of the optimal-shift reach for dense full-box supports. A 6x gain would be needed and has no precedent.

---

## 7. Killed candidates (self-killed, with reasons)

**K1. Small-model integer parabola descent (prime).**
- Derivation: for S_3 with symmetric functions s = x1 + x2, t = x1·x2, the decomposition condition is G = (t - x_R s)² - (4x_R² + 2A)t - (2x_R A + 4B)s + A² - 4x_R B ≡ 0. That is a parabola, linear in s once w = t - x_R s is fixed, with γ = 4y_R².
- On a model with small A, B and a small-x target, G = kp over Z gives s = (w² - αw + c - kp)/γ_Z. Candidates come from residue classes mod γ_Z, so they are sieve-able.
- Cost per relation is about X² (or B²), below generic p/B when B < p^{1/3}.
- Killed: the targets must have small x_R, which costs p/X generic steps each, giving a total of about p^{5/3}/B. The FB-only version needs B ≥ p^{1/2}, which makes LA cost p. With K < 1 the route collapses to xedni (closed_known, JKSST).

**K2. Farey (rational-reconstruction) height base.**
- Exact finding: at m = 2 the condition is a ternary quadratic form Q_R(D, S, T) ≡ 0 mod p with (D, S, T) = (b1b2, a1b2 + a2b1, a1a2).
- Killed by PC1: m = 2 cannot beat rho with any oracle. Also, the factorisation condition turns Q_R back into the bidegree-(2,2) quartic in four variables of size N^{1/4} at critical volume.
- At m = 3 the image surface Σ_R ⊂ P³ is a quartic (the norm map is 2:1 only off the plane f(-R) = 0), so small points are Coppersmith-hard.

**K3. Special-q / lattice sieve in the Riemann-Roch space of E.** "f vanishes at P_i" is a hyperplane in L(kO), so sieving by hyperplanes is genuine. But the yield per hit is (|F|/N)^{k-1}: there is no size, so no smoothness density. It reduces to fixing k-1 zeros, which is generic enumeration.

**K4. Smooth-x factor base** (x(P) a B-smooth integer). Multiplicative smoothness of x has no group-law meaning, and |F| = ψ(p, B) is too large for LA.

**K5. ECM stage-2 / FFT-continuation membership** (multipoint evaluation of ∏(X - x(P_j)) at the points x(R - P_i)). This costs O~(|F|) per target, exponent 1, worse than the table's 2/3.

**K6. Bernstein batch smoothness / remainder trees.** On E(F_p) there is nothing smooth to batch.

**K7. den Boer-Maurer-Wolf auxiliary curve of smooth order over F_N** (ECM-style search for smooth #E'(F_N)). It needs a DH oracle. SO-CHEON (LEAD-RHO-cheon-aux-acquisition): "computing it is the square-DH problem, which has the same Omega(sqrt r) generic lower bound ... Scope: generic algorithms on any curve; non-generic acquisition is not excluded." No non-generic acquisition is known.

**K8. Bombieri / Kohel-Shparlinski character-sum control of decomposition-count variance, used for target preselection.** The additive-energy error O(|F|·p·log² p) is vacuous below |F| ≈ p^{2/3}, and every relevant base is smaller.

**K9. Char-2 m = 2 polynomial-basis linearisation.** With w = π + x_R s, the pair (s, π) is affine in w, so solvable by F_2-linear algebra. Killed: the split condition π = x1(x1 + s) restores 2^l enumeration. KN-FIND-aa2efc already measured the Riemann-Roch encoding at |F|².

**K10. GTTD rows of the ECC2K-130 free-oracle floor.** Duplicate of H-BINSTD-555991 (approved; 2LP budgets 2^{8.71} and 2^{22.34}). KB1 extends that hypothesis to writability instead.

**K11. Descent trees / special-q for individual logs** (prime and Koblitz). Descent is 0.3-1.4% of S in Table A and absent in Table B; it is not a bottleneck.

**K12. Constant engineering of the Table B m = 2 recipe as a route to crossover.** The asymptotic ratio grows as N^{1/6} (PC1(c), section 3). Killed as a crossover route; it is fine as engineering.

**K13. Joux-Vitse-style overdetermined Coppersmith oracle with large primes at m = 3.** Folded into PC2: computed margin -0.63, shape-invariant.

---

## 8. Fields searched with nothing surviving

- NFS/FFS lattice (special-q) sieving transferred to E/F_p: no periodic divisibility (K3).
- Canfield-Erdos-Pomerance / Dickman smoothness transfer: the rate transfers exactly (section 0), but the divisibility test does not.
- ECM stage-2 batching (K5) and Bernstein batch smoothness (K6).
- Function-field sieve over F_p(t): closed by xedni alpha = 3 (LEAD-ICP-xedni-function-field-sections). Over F_p(E): genus 1, so degree-1 places are the whole group.
- Smooth values of polynomials (Dartyge-Martin-Tenenbaum type): no polynomial parametrisation of targets aP + bQ exists.
- Descent trees (K11).
- B6 rho step cost and equivalence classes (tag tracing needs partial products; an EC addition needs a full inversion): no smoothness ingredient.
- B7 transfers (Miller cocycle, Teske F_{p^6}): no smoothness ingredient.

---

## 9. Reproduction

- `calc/s4_reach.py`: S_4(x1,x2,x3;x_R) support (125/125) and HG/JM-extended reach on four box shapes. Output: 0.1214 for every shape.
- `calc/lp_writability.py`: the 2LP column of the writability table (section 4), from EXP-ICPERF-783e9e/RUN-ICPERF-2f36fd/checkpoint/budget_table.json (read-only).
- Both import or read repository tools and data read-only. The interpreter runs with `sys.flags.dont_write_bytecode = 1`. A `find -newer` check after the runs found no new `.pyc` or other file written by this session inside /Volumes/SSD990-2/crypto-autoresearcher; the only newer paths are under formal/ and .git, which this session did not touch.
