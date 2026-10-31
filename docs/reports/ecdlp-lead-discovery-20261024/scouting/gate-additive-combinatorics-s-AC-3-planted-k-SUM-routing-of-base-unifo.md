# Gate N1-N4: AC-3, planted k-SUM routing of base-uniform decomposition oracles

Candidate source: scout/scout-additive-comb.md section 3 (read in this gate). Gate run in the scratchpad only; nothing inside the repositories was edited, created, added or committed. Tool environment: `LEAD_ATLAS_CRYPTO`, `LEAD_ATLAS_CRYPTANALYSIS`, `LEAD_ATLAS_ECC_CHALLENGES` exported as specified; commands run from /Volumes/SSD990-2/crypto-autoresearcher.

## 0. Verdict

**advances_lead**, weak form. Lead anchor: LEAD-ICE-charged-toy-ic-exponent-vs-rho (open_blocked), with its scope-text consequences for LEAD-ICE-generic-oracle-arity-cost-floor and LEAD-ICP-generic-table-decomposition (both closed_obstructed).

Reasons in one paragraph.
- No lead, KR row or ledger record contains the reduction "planted m-SUM in Z/N embeds into any decomposition oracle that works on uniformly random bases". So it is not a duplicate of a mechanism, and it is not a recorded known result.
- It is not a new lead either. It proposes no oracle, no factor base and no speed-up (candidate's own tier X, predicted gain 0). Its decision-relevant content is (a) a conditional widening of the Scope clause of closed leads from "does not read coordinates" to "reads coordinates but is base-uniform", and (b) a decision rule for the matched-null arm N that EXP-ICEX-153c34 already contracts. Both attach to existing records.
- The one numeric consequence it advertises (T_dec >= p^0.3 at SO-TABLE's revisit point m = 4, B = p^{1/5}) is not established by the derivation as written: Cor. 4.9 bounds the cost on planted (decomposable) inputs, while T_dec in SO-TABLE and tau in the region lemma are per-attempt costs charged mostly on non-decomposable targets. See F1.
- Its first discriminating step is only partly "already designed": arm N exists on six fixtures at two sizes (16, 20 bits) with a preregistered prediction "ratio near 1"; the L-ladder and the closure rule are additions that need a contract amendment. See F4.
- The class it prunes (base-uniform) contains none of the oracle families the program is still building (interval, small-x, subgroup, subspace and window bases are all designed bases). The surviving class is exactly the KN-OPEN-020 open class plus the open leads already on the atlas. See F2, N4.

If the orchestrator reserves advances_lead for strictly sharper experimental next steps, the fallback reading is duplicate_of_lead of LEAD-ICE-generic-oracle-arity-cost-floor for lead-discovery purposes (no new direction), because the residual novelty is a conditional closure statement.

## 1. Citation verification (provenance per item)

| item | what was checked | provenance |
|:--|:--|:--|
| ASSVV23, "k-SUM in the Sparse Regime", arXiv 2304.01787 v3 (21 Nov 2023) / ePrint 2023/488 | WebFetch of the arXiv abstract page (title, authors, abstract); WebFetch of the PDF returned a byte stream, so the saved PDF was converted with pdftotext and read locally (text kept at scout/ac3-raw/assvv23.txt, not reproduced here). Found: Def. 3.1 (density Delta = k log r / log|G|, r = list size); Conjecture 3.5 (average-case k-SUM, folklore as formalised by DKK21, lower bound r^{ceil(k/2)-o(1)} for non-planted search at density 1); Theorem 4.8 (a planted-search algorithm at density Delta in (1/2,1] with r^Delta uniform elements and running time T gives a planted-search algorithm at density 1 in time about T r^{k(1-Delta)} log|G|, for any abelian group); Corollary 4.9 (under Conj. 3.5 the planted-search time at density Delta in (1/2,1] is r^{k(1-1/(2 Delta))-o(1)}, any abelian group); Theorem 4.12 (search-to-decision, implied by Impagliazzo-Naor, for Delta < 1: a decision algorithm with advantage eps gives planted search in time T(r) r log r (k/eps)^4) and Theorem 4.13 (no factor-r loss, but needs decision success 1-o(1)). Footnote 9 of the paper says section 4 uses the weaker r^{k/2-o(1)} form of Conj. 3.5 for simplicity. | retrieved |
| Candidate's reading of Cor. 4.9 and its exponent tau >= m - 1/(2 beta) | Recomputed from Thm 4.8: the density-Delta list size is n = r^Delta, so T_Delta >= r^{k/2} / r^{k(1-Delta)} = n^{k(1-1/(2 Delta))}. With Delta = m beta and n = B this is B^{m - 1/(2 beta)}. At m = 4, beta = 1/5: Delta = 4/5, tau >= 1.5, B^{1.5} = p^{0.3}. Matches the candidate. | derived here (arithmetic), on retrieved statements |
| DKK21 Theorem 4.6 (dense regime, Delta in (1,2], r^{k(1/Delta-1/2)-o(1)}) | Read only as quoted in ASSVV23 section 4.1 (the statement is the same as the candidate's). Primary paper not opened. | retrieved via ASSVV23 (secondary quote) |
| Kopelowitz-Porat, "The strong 3SUM-indexing conjecture is false", CoRR abs/1907.11206 (2019) | Bibliographic entry ([KP19]) read in the ASSVV23 reference list. Content not read. | retrieved (bibliography entry only) |
| Golovnev-Guo-Horel-Park-Vaikuntanathan, "Data structures meet cryptography: 3SUM with preprocessing", STOC 2020; Chung-Larsen, "Stronger 3SUM-indexing lower bounds", SODA 2023 | Bibliography entries in ASSVV23 only. These are the literature behind the candidate's amortised branch H3b; contents not read here. | retrieved (bibliography entry only); the H3b statement itself is the scout's conjecture |
| "ECDLP point decomposition is as hard as k-SUM" in the literature | Two WebSearch queries (PDP + k-SUM / generalized birthday; Semaev summation polynomials + k-SUM / generalized birthday) returned only PDP algorithmics (Karabina arXiv 1504.02347, Trimoska-Ionica-Dequen ePrint 2019/313, Yokoyama et al. J. Math. Cryptology 2020, Petit et al., Amadori-Pintore-Sala ePrint 2017/609, Mueller-McGuire talk). No k-SUM framing found. Absence in two searches is not evidence of absence. | retrieved (negative search result) |

## 2. N1 atlas collision

Top hits per run (score, id, disposition). Runs 1-3 are the candidate's `match_phrasings`; run 4 is my own phrasing ("average-case k-SUM sparse regime reduction random factor base planted decomposable target any algorithm"). Full raw output in section 7.

| run | top 5 |
|:--|:--|
| 1 planted k-SUM conjecture lower bound for base-uniform decomposition oracles | 10 LEAD-ICB-generic-table-oracle (closed_obstructed); 7 LEAD-ICE-curve-presentation-invariance (open_next_step); 7 LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed); 6 KR-IC-46d822; 6 KR-IC-8b9daa |
| 2 a decomposition algorithm that works on random factor bases is as hard as planted 4-SUM | 14 LEAD-ICB-kic-golden-base-exact-decomp (open_next_step); 14 LEAD-ICP-coppersmith-smallroot-semaev (open_next_step); 12 KR-IC-b0fcda; 12 LEAD-ICE-semaev-yield-model-coset-typing (open_next_step); 12 LEAD-ICP-coincidence-harvest-structured-base (open_next_step) |
| 3 decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off | 14 LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed); 14 LEAD-ICP-generic-table-decomposition (closed_obstructed); 12 LEAD-EXO-augmented-oracle-ggm (closed_obstructed); 12 LEAD-ICE-rootfind-pairtable-oracle (open_blocked); 11 LEAD-ICB-generic-table-oracle (closed_obstructed) |
| 4 (mine) average-case k-SUM sparse regime reduction ... | 13 LEAD-ICP-coppersmith-smallroot-semaev; 12 LEAD-ICB-cofactor-torsion-quotients (closed_obstructed); 12 LEAD-ICP-retained-setup-online (closed_dominated); 11 LEAD-ICP-isogeny-transported-relation-yield (open_blocked); 10 LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale) |

Lexical caveat: the scorer is keyword-based. I therefore also grepped all 147 lead YAML files for `m-SUM|k-SUM|3SUM|SUM-indexing|average-case|ASSVV|Dinur|Kopelowitz|Corrigan`. The only hits are the two table-oracle leads (they cite Corrigan-Gibbs--Kogan), the arity-floor lead (title and forecloses use "m-SUM"), and an unrelated rho row (average-case constant of store-all schedules). No lead contains an average-case or planted k-SUM conjecture.

Semantic reading of the top hits (all opened; mechanism, obstruction with Scope, revisit_when and forecloses are reproduced verbatim in 2b):

1. LEAD-ICE-generic-oracle-arity-cost-floor (closed_obstructed, cost_model). Closest semantic neighbour (its cost model is stated for binary curves of prime degree n; the prime-field analogue is the SO-TABLE row in item 2). Its mechanism is the same abstraction AC-3 uses ("Treat the oracle as an abstract m-SUM search"). Its Scope clause is "oracles that do not read curve coordinates algebraically", and its revisit_when names "an oracle that reads coordinates with per-query cost polynomial in n at fixed degree ... or a non-generic yield exceeds C(B+m-1,m)/N on average". AC-3 neither measures such an oracle nor shows a yield excess. It argues, conditionally, that coordinate-reading oracles that are base-uniform cannot sit below the floor. That fills the flagged scope gap from the closing side; it does not meet the revisit_when from the opening side.
2. LEAD-ICP-generic-table-decomposition (closed_obstructed, theorem), the SO-TABLE row AC-3 targets. Its revisit_when ("A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4 ... or a decomposition test sub-linear in |F|") is phrased per attempt. AC-3 does not exhibit such an oracle. See F1 on the per-attempt versus planted mismatch.
3. LEAD-ICB-generic-table-oracle (closed_obstructed, theorem), binary SO-TABLE. Its revisit_when points to LEAD-ICB-prime-degree-algebraic-decomposition (an algebraic restriction on the unknowns, i.e. a subspace base). That is base-specific by construction, so AC-3's base-uniform bound says nothing about it. See F2.
4. LEAD-EXO-augmented-oracle-ggm (closed_obstructed, theorem). Closes oracles by GGM simulability. Its revisit_when asks for a publicly computable oracle that is not GGM-simulable. A coordinate-reading oracle is not GGM-simulable in general, and AC-3 provides no such oracle either.
5. LEAD-ICE-charged-toy-ic-exponent-vs-rho (open_blocked; not in the top 10 of any run but named by the candidate): next step is to build the EXP-ICEX-153c34 backend. That experiment's arm N is the candidate's first step. See F4.
6. LEAD-ICE-rootfind-pairtable-oracle, LEAD-ICB-kic-golden-base-exact-decomp, LEAD-ICP-coppersmith-smallroot-semaev, LEAD-ICE-semaev-yield-model-coset-typing, LEAD-ICP-coincidence-harvest-structured-base, LEAD-ICP-isogeny-transported-relation-yield, LEAD-EXO-dl-character-sum-pseudorandom, LEAD-ICE-curve-presentation-invariance: different mechanisms (pair-table constants, co-designed bases, lattice reach, yield or coincidence excess against a matched random base, isogeny transport, character sums). Relation to AC-3:
   - They all compare a designed base with a matched random base at the level of yield, coverage or coincidence counts, and report conservation (ratio 1.000000 in LEAD-ICP-algebraic-membership-factor-base; kappa_rel 0.998; R = 1.28-1.34 flat). None compares oracle cost exponents against a k-SUM-type lower bound.
   - KIC (base-specific) and Coppersmith (small-x window; reach defined only for small unknowns) are exactly the class AC-3 leaves open. For the lattice oracle the paired random-x arm is degenerate: small-root reach is undefined on a base whose elements are not small, so a "flat ratio" cannot occur and the arm adds no information.
   - LEAD-ICE-curve-presentation-invariance: AC-3's reduction is presentation-blind. An isogeny or model change that maps uniform bases to uniform bases (a bijection on a prime-order subgroup does) leaves AC-3's conditional bound unchanged. This is my observation, derived here; it is consistent with the lead's mean-yield invariance reading and is not stated in the lead.
7. KR-IC-46d822 (Gaudry, extension fields) and KR-IC-8b9daa (Karabina) are lexical hits on "decomposition" only.


## 2b. Lead rows read in full (mechanism + obstruction + forecloses), obstruction statements quoted verbatim from the YAML

### Closed leads (the standing obstructions AC-3 claims to reach past)

#### LEAD-ICE-generic-oracle-arity-cost-floor  (closed_obstructed)
- title: Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
- mechanism: Treat the oracle as an abstract m-SUM search or charge it nothing, and ask whether any arity m or base size puts point-decomposition IC below rho. The product law relations x targets x oracle = m 2^n is independent of dim V, and the store any sub-rho cell needs costs as much as rho's whole walk.
- obstruction.kind: cost_model
- obstruction.statement (verbatim, Scope included): For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc); in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC.
- revisit_when: An oracle that reads coordinates with per-query cost polynomial in n at fixed degree (see LEAD-ICE-descent-closure-degree-at-scale) is measured, or a non-generic yield exceeds C(B+m-1,m)/N on average.
- best_measured: free oracle at m = 3 on ECC2K-130: 2^68.58 vs rho 2^60.81 (KN-FIND-aa2efc)
- forecloses: free decomposition oracle lifts IC below rho; arity threshold for point-decomposition index calculus; generic m-SUM decomposition oracle; larger arity m makes enumeration IC beat rho; multi-target amortisation rescues exhaustive-solver IC

#### LEAD-ICP-generic-table-decomposition  (closed_obstructed)
- title: Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
- mechanism: Over F_p the roots of S_3/S_4 are exactly x(R -/+ F_i) matched against x(F_j +/- F_k), so the point-decomposition problem becomes a batched subtraction plus a table lookup (folded, walked targets; mitm tables of h-fold signed sums). With a factor base of size B and arity m this trades B^{m-1} advice for (m!/2^m) p / B^{m-1} work per relation, and was the hope for moving the Table B prime ladder toward rho.
- obstruction.kind: theorem
- obstruction.statement (verbatim, Scope included): Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p.
- revisit_when: A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4 (an S_5 oracle at B ~ p^{1/5}), or a decomposition test sub-linear in |F|.
- best_measured: S_IC/S_rho = 5.47x (log2 r = 11.9) to 13.5x (log2 r = 23.4), Table B prime ladder, unvalidated (pre-gate); FRONTIER fitted exponent 0.841 [0.500, 1.024] for folded mitm m = 2
- forecloses: pair-table meet-in-the-middle decomposition beats rho at higher arity; faster S_3 root finding or batched subtraction makes prime IC sub-rho; choose the factor-base size B optimally to cross rho; free decomposition oracle at m = 2 or m = 3; generic collision floor for x-key relations

#### LEAD-ICB-generic-table-oracle  (closed_obstructed)
- title: Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
- mechanism: Decide whether a target is an m-sum of factor-base points by table lookup, pair tables or meet-in-the-middle, collect relations, solve the orbit-folded matrix and descend. This is the production pipeline behind every Table A and Table C row; engineering it (K, arity, table layout) is how the baseline has improved.
- obstruction.kind: theorem
- obstruction.statement (verbatim, Scope included): Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged.
- revisit_when: An oracle that is not generic (algebraic restriction on the unknowns with membership degree far below |F|), which is LEAD-ICB-prime-degree-algebraic-decomposition; constant-factor engineering of this pipeline remains valid baseline work (LEAD-ICB-koblitz-setup-phase-cost).
- best_measured: Table A one-target S_IC/S_rho 5.23x (n47) to 21.0x (n61) as published; 9.13x to 41.1x against rho at the canonical step (validation sweep A). Frontier campaign: compact orbit 3.8-15x signed-Frobenius rho at w = 0.
- forecloses: bigger pair table or k-sum table for ECC2K-130; 5-sum or 6-sum compact-orbit extraction beats rho; meet-in-the-middle point decomposition as a sub-rho oracle; walk-carried or target-dependent factor base; arity lever at the cap locus for ECC2K-130

#### LEAD-EXO-augmented-oracle-ggm  (closed_obstructed)
- title: Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
- mechanism: Give the solver an extra public oracle (x-coordinate, y-coordinate, full point, halving query, endomorphism image, factor-base incidence, jet) and hope it supplies sub-birthday information or guided decomposition.
- obstruction.kind: theorem
- obstruction.statement (verbatim, Scope included): Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 (KN-FIND-002, KN-FIND-b7e091, KN-FIND-194294; EV-GGM-001 strong). Measured: the x-oracle gives Y_A = Y_B exactly (no yield advantage, EV-ECDLP-fd61e4 strong) and the m=3 MITM split saving is attributable to the split, not the oracle (EV-ECDLP-7367e2). Scope: oracles, not resources (see IDEA-20260808-ea3b4f).
- revisit_when: A publicly computable oracle that is NOT GGM-simulable is exhibited (the threshold oracle is the minimal non-simulable identifier, KN-FIND-982fdf, but needs private data).
- best_measured: x-oracle yield Y_A = Y_B exactly; oracle increases candidates (EV-ECDLP-284817)
- forecloses: x-coordinate oracle meet in the middle; y-coordinate oracle guided decomposition; full-point oracle; endomorphism image oracle; halving query oracle; generic group model simulable oracle

#### LEAD-ICB-multi-target-and-portfolio  (closed_obstructed)
- title: Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
- mechanism: IC pays its set-up once, so per-target cost after set-up falls as 1/L while batch rho falls as 1/sqrt(L); a restart portfolio of IC and rho could exploit heavy tails.
- obstruction.kind: theorem
- obstruction.statement (verbatim, Scope included): The multi-instance generic bound (L logarithms cost >~ sqrt(L r/|Aut|)) covers generic-oracle IC including its set-up, and batch rho (Kuhn-Struik) attains it; the L^-1 amortisation applies only to the online part after a set-up that obeys the same bound. A restart portfolio IC + rho cannot beat pure rho when IC cost is concentrated at a floor ratio >= 1 (H-BINSTD-32867d supported). The four-target union column is a rare-event linearisation, not a batch speed-up. Measured: Table C (32 targets) stays 3.62-14.9x above batch rho.
- revisit_when: A non-generic oracle (then amortisation matters), or IC attempt costs that are heavy-tailed with median within about two orders of magnitude of rho.
- best_measured: Table C per target, 32 targets: 3.62x (n41) to 14.9x (n19) above batch rho (reference from a different session, S20, at the canonical step).
- forecloses: index calculus amortises as 1/L so batch IC beats batch rho; IC and rho restart portfolio; four-target union column as a batch speedup; shared set-up across many Koblitz targets

#### LEAD-RHO-generic-sqrt-lower-bound  (closed_obstructed)
- title: Beat the square-root exponent with any generic collision algorithm
- mechanism: Any algorithm that uses only group operations and equality tests (rho, kangaroo, BSGS, grumpy giants, multi-walk, GPU variants) is a generic algorithm. If one of them could find logs in o(sqrt r) operations, every curve would weaken at once.
- obstruction.kind: theorem
- obstruction.statement (verbatim, Scope included): Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r.
- revisit_when: Never for generic algorithms; only a method that reads the representation (index calculus, transfer) can change the exponent.
- best_measured: all generic arms fit alpha <= 0.53 in FRONTIER (e.g. bsgs.negation 0.529 [0.485, 0.596], prime toy); no generic arm below the floor beyond CI noise
- forecloses: sub-square-root generic algorithm; beat sqrt(r) with a smarter walk; generic collision search below the birthday bound; new exponent from rho engineering

#### LEAD-ICP-algebraic-membership-factor-base  (closed_obstructed)
- title: Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
- mechanism: Over F_{q^n} the subfield makes membership x^q = x low degree after Weil restriction. Over F_p one would need a size-B subset cut out by equations of degree << B that survive substitution into S_{m+1} (multiplicative subgroups x^B = 1, cosets, Dickson images, x = g(t)), or a structured base whose multiplicative characters bias x(P +/- Q) and so raise yield.
- obstruction.kind: theorem
- obstruction.statement (verbatim, Scope included): A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B.
- revisit_when: KN-OPEN-020 is answered positively (a size-B set with sub-B-degree membership surviving substitution), or a base raises coverage or variance with an excess that grows with N.
- best_measured: mean-yield ratio vs matched random 1.000000 at N ~ 2^14..2^18 (EV-FBG-001); subgroup vs random within 7 % at 32 bits
- forecloses: multiplicative subgroup factor base x^B = 1; Dickson or coset factor base for prime-field index calculus; algebraic factor base with low-degree membership polynomial; character sums bias decompositions over a coset base; image of a low-degree map as factor base

#### LEAD-ICP-representation-subset-sum  (closed_obstructed)
- title: Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
- mechanism: Write k in base B so that Q = sum_j [d_j B^{j-1}] P is a structured subset-sum over the group, and use many representations of the solution to filter partial sums, as for knapsacks.
- obstruction.kind: theorem
- obstruction.statement (verbatim, Scope included): The method uses only group operations and equality of encodings, so it is a generic algorithm and is bounded below by T >~ sqrt(N) (Shoup) and S*T^2 >~ N with advice; the filter step has no non-generic handle on E(F_p) (KR-RHO-5b1c0a records the same failure over F_{p^2}). Scope: any representation/filter variant on a prime-order group.
- revisit_when: A filter predicate that reads non-generic coordinate structure with a measured bias.
- best_measured: 
- forecloses: representation technique for ECDLP; subset-sum of scalar digits with many representations; knapsack-style filtering of partial group sums

#### LEAD-ICB-cofactor-torsion-quotients  (closed_obstructed)
- title: Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
- mechanism: Use E -> E/2E -> E/4E coset labels on legs, homomorphic cofactor quotients or sum-compatible filters (Wagner k-tree) to prune decomposition candidates, or fold the factor base by 2-torsion translation.
- obstruction.kind: proof
- obstruction.statement (verbatim, Scope included): On ECC2K-130 gcd(4, l) = 1, so every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality); exactly sum-compatible filters on E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in; the corrected iota-stable classification (V_d = b^{1/4} F_{2^d}) empties the (subspace base, 2-torsion quotient) cell on every prime-degree standardized curve; the production 2-torsion census adds 0 relations. FGHR 2-torsion symmetrisation of the solve is a separate constant (engine family).
- revisit_when: A curve with a large smooth cofactor, or a non-homomorphic sum-compatible filter with more than log2(cofactor) bits.
- best_measured: 2-torsion census: 0 additional relations (improve-2 item 02).
- forecloses: Wagner k-tree on ECC2K-130; cofactor 4 coset label prunes decomposition; 2-torsion translation quotient of a subspace factor base; spend the cofactor on decomposition

#### LEAD-ICP-retained-setup-online  (closed_dominated)
- title: Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
- mechanism: Keep the factor base, logs and dense root table after one solve so that each new target costs only a geometric number of table probes; the online ratio against rho looked like 13.9x (n61) and 18.5x (n83).
- obstruction.kind: measured
- obstruction.statement (verbatim, Scope included): The online ratios compared against rho with an empty distinguished-point table. Bernstein-Lange preprocessing rho with equal or smaller advice is 53-317x faster online than IC at n = 41/53/61, and precomputed-table rho wins every N83 matched pair; orbit-folded m = 2 Koblitz IC is BSGS on the quotient and sits on the BL r/P law. Scope: retained-advice, many-target accounting on these curves.
- revisit_when: An IC online row that beats BL preprocessing rho at equal advice bytes and equal setup.
- best_measured: superseded: rho/IC 13.9x (n61) and 18.528x (n83) were against empty-table rho; BL at equal advice 53-317x faster online than IC
- forecloses: retained factor base makes later targets cheaper than rho; dense root table online index calculus; multi-target index calculus beats rho per target; orbit-folded m = 2 index calculus online

#### LEAD-ICE-prime-field-semaev-solving-degree  (closed_known)
- title: Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
- mechanism: Over F_p there is no Weil descent; the system in x-coordinates of an interval or random base has degree growing with the base, and the hope was a certificate-backed solving-degree law, an eliminant or subresultant route, or a structured base whose membership is low degree. Measured serial-S_3 eliminant exponent stays far above the sub-rho gate.
- obstruction.kind: literature
- obstruction.statement (verbatim, Scope included): Naive Semaev IC over prime fields cannot beat generic methods (KR-IC-5931ee). The program reproduced it: at balanced L = q^(1/5) on ordinary toy curves, beta_work(B1) = 0.797 on interval and random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold, 36/36 cells, 105/105 FGLM checks (EV-SDEG-4a1c3d, strong); in ecbench the root-finding/pair-table oracle dominates any prime-field Groebner arm.
- revisit_when: A prime-field factor base whose membership equation has bounded degree independent of p (the base-d digit-map / PFDR descent, IDEA-20260830-84cdb7) produces a measured solving degree that stays flat across >= 3 field sizes.
- best_measured: beta_work 0.797 (interval/random) and 0.647 (subgroup) vs 0.30 sub-rho gate, toy prime fields (EV-SDEG-4a1c3d)
- forecloses: prime-field Semaev Groebner solving degree law; serial S_3 eliminant for sub-rho prime-field IC; subresultant pivot tree for prime-field decomposition; grevlex versus lex solving degree on F_p summation systems; semi-regular null for prime-field decomposition

### Open leads touched by the candidate (first-step attachment points and neighbours)

#### LEAD-ICE-charged-toy-ic-exponent-vs-rho  (open_blocked)
- title: One fully charged toy-scale index-calculus exponent vs matched rho (GOAL-ICEX-001 / G7)
- mechanism: Aggregate SDEG/MONO/RELN outputs into one complete-cost IC exponent with a matched rho measured on the same instances, censoring charged and failures included. Audits found the four-size exponent unidentifiable and the 1/2 comparison mis-specified, and enumerative membership, not IC itself, is the bottleneck; the non-enumerative oracle is approved but unbuilt.
- next_action.step: Build the EXP-ICEX-153c34 backend (G1 membership, O5 oracle, S/G/X/V counters, admission-refusing driver) and pass S0 gates G0-1..G0-6 on smoke curves, then fit the crossover order log l* (IDEA-20260805-4d31bc) rather than a ratio exponent.
- next_action.discriminates: A measured crossover with both arms on the same instances fixes the distance to rho in one unit-invariant number; an empty crossover across the reachable range turns the lane into an exhausted_at_scale record with the reached size.
- blocked_by: EXP-ICEX-153c34 backend unbuilt; dispatch gated on the C-7 host-load gate (GOAL-ICEX-001 next_action)
- best_measured: no IC arm beats rho at any band weight, none has a fitted exponent below rho's (ic_frontier_campaign_20261015); Table A 5.23x at log2 r 36.6
- forecloses: charged toy index calculus exponent versus rho; fit IC exponent over four toy sizes; censoring-charged cost exponent; go/no-go on optimistic handed-over inputs

#### LEAD-ICE-sat-xor-pdp-oracle  (open_next_step)
- title: SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
- mechanism: Encode the descended S_3 / S_4 system as CNF-XOR and let a CDCL solver with Gaussian elimination find decompositions; the literature reports up to 300x over Magma F4 on the PDP step. Recorded group-operation S on n = 17 Koblitz is below strong rho, but SAT conflicts and propagations are unpriced, and a derived identity says the pdp CNF-XOR model is a complete enumerator of V^m mod S_m with no above-leaf pruning.
- next_action.step: Calibrate ns per conflict and per propagation against ns per group addition on the count-qualified-main hardware, reprice the native-XOR SAT arm of ecbench_sat_pdp at 0, 0.1 and 1 GAE per solver op, and fit alpha(m) of the conflict count at m in {3,4,5} (H-SATIC-5c526c).
- next_action.discriminates: Priced S/rho below 1 across the band would be a sub-rho toy row to send through the validation gate; above 1 with conflicts tracking 2^(ml)/m! confirms SAT is enumeration at a constant and closes the lead as dominated by the pair table.
- best_measured: native-XOR SAT S/rho 0.854 lower bound, conflicts unpriced, n = 17 Koblitz, 40/40 verified (ecbench_sat_pdp count-qualified-main)
- forecloses: SAT solver for point decomposition; CryptoMiniSat Gaussian elimination on Weil descent; WDSat XOR reasoning for summation polynomials; CNF-XOR encoding of the PDP; DPLL conflict law 2^(ml)/m!

#### LEAD-ICP-coppersmith-smallroot-semaev  (open_next_step)
- title: Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
- mechanism: A small-x or windowed factor base turns decomposition into a multivariate small-root problem for S_{m+1}, whose cost is set by lattice reach rather than solving degree. With binary addition trees and kept windowed internal nodes, all-S_3 degree-2 blocks have the largest reach; if reach exceeded the index-calculus demand the decomposition would cost polynomial time per attempt at a factor base large enough to beat rho.
- next_action.step: Compute the provably optimal shift set (Ryan, EUROCRYPT 2025; Feng-Luo-Chen-Nitaj-Pan sumset bounds) for the 13-monomial S_3 polytope and the full-tree (m, w) = (4, 2) system, and the rank-r >= 2 GAP substitution of H-PFDR-3c7d1e, with tools/smallroot_reach.py as the calibrated calculator; then a planted direct-box S_4/S_5 recovery (H-PFDR-621852) at 40-56 bits only if the computed reach clears 8/9.
- next_action.discriminates: Optimal reach >= 0.8889 at (4,2) (or any rank-r GAP cell with positive margin) reopens a concrete lattice decomposition oracle to be measured; optimal reach < 0.8889 everywhere turns the current heuristic -0.0481 closure into a strategy-independent one and closes the family.
- best_measured: S_3 reach rigorous delta <= 0.10, heuristic 0.12-0.16 (needs 1/2), Probes B/C at 40/56 bits; epsilon margin -0.0481 at (m,w) = (4,2) (JM extended 0.8408 vs demand 8/9)
- forecloses: Coppersmith small roots of summation polynomials; small-x factor base solved by LLL; windowed addition tree with lattice reduction; symmetric e1 e2 lattice for S_3; rank-r generalized arithmetic progression factor base; lattice-assisted meet-in-the-middle decomposition

#### LEAD-ICE-rootfind-pairtable-oracle  (open_blocked)
- title: Root-finding / pair-table decomposition oracle in place of a Groebner solve
- mechanism: The S_3 root in the last variable is x(R -/+ F_i), so an m = 2 decomposition is one batched inversion plus table probes (prime) or one pair-sum lookup (binary); m = 3 is |F| lookups. It is exact and complete like enumeration and replaces Macaulay row reduction. It is now the default oracle in every Table A/B row, and it moves the constant, never the p/|F| exponent.
- next_action.step: Price every native primitive of the rootfind-negfold m = 2 arm and of matched strong rho (table canonicalisation, inversions) at 0, 0.1 and 1 GAE/op, replay on a second host (L2+), and re-run the 17-bit Koblitz and 20-bit prime cold sessions.
- next_action.discriminates: If the cold complete IC / strong-rho ratio stays above 1 across the band, the pair-table engine is exhausted at toy scale and only a degree-bounded algebraic oracle (LEAD-ICE-descent-closure- degree-at-scale) can change the slope; if it falls below 1 across the band at two sizes, it is the first validated sub-rho cold row and goes to the IC leaderboard gate.
- blocked_by: problems/rootfinding-complete-cost-calibration.md (crypto); native work unpriced, L0 only, same-host replay
- best_measured: cold complete IC about 1.54x strong rho, 17-bit Koblitz, L0, natives unpriced (ecbench_rootfind_vs_rho_20261014); prime Table B 5.47x-13.5x rho at 9.7-23.4 bits
- forecloses: replace Groebner with root finding in point decomposition; pair-sum table meet-in-the-middle decomposition oracle; x(R minus F_i) direct subtraction relation sweep; batched inversion root-finding oracle beats rho; all-roots univariate solver for Semaev S_3

#### LEAD-ICB-kic-golden-base-exact-decomp  (open_next_step)
- title: Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
- mechanism: Design the factor base and the decomposition constraint together (affine-plane pools, one-hot shift encodings, orbit-canonical pair lookup with exact witness transport) so that charged decomposition cost drops without losing coverage.
- next_action.step: Coordinator evidence review of the five completed KIC runs (EXP-KIC-3df18c, -424885, -7bcef8, -c3c732, -d9c828), none of which has an EV record; then, for any arm whose advantage survives its null and A/A, a paired test inside the compact-orbit pipeline.
- next_action.discriminates: A reviewed wall or coverage advantage that survives the null is a candidate constant improvement for the IC baseline; none closes the lane as dominated by exact MITM.
- best_measured: N7 pilot (EXP-KIC-424885): flat SAT / direct MITM median wall 1.70x [1.02, 2.69] (SAT slower); candidate coverage 70 = null coverage 70; eligible_for_independent_review false.
- forecloses: golden factor base with easy SAT decomposition; affine 2-flat factor base; orbit-canonical abscissa pair lookup

#### LEAD-EXO-four-list-ktree-join  (open_next_step)
- title: Wagner k-tree / four-list joins with cheap sum-compatible filters
- mechanism: Run a Wagner-style k-list tree (or representation-technique subset-sum) on E(F_p) using a cheap filter h with h(P+Q)=f(h(P),h(Q)) often enough, or an output-sensitive partial verifier, aiming at N^(1/3+o(1)) end-to-end. Signed-y and Boolean-success cascades are the program's concrete instances.
- next_action.step: Measure the relative bucket variance W of the O2 agreement kernel (H-ECDLP-2ade73; IDEA-20260904-f7d47d second moment) on the covered families across N and fit its decay against 1/sqrt(N); EXP-ECDLP-5cad48 ran many stages without ever assigning a W class.
- next_action.discriminates: LARGE-W (decay slower than 1/sqrt(N)) reopens a bucket-concentrated filter for a four-tree; SMALL-W extends the bucket-averaged O2 barrier (KN-FIND-ffe1df) to a bucket-resolved one and closes the filter class.
- best_measured: j=2 four-tree at exponent 0.4167 closed for character filters under group-law or quasigroup combining, toy N <= 65539 (analysis/o2-sum-compatible-filters)
- forecloses: Wagner k-tree on elliptic curve points; four-list join with a cheap filter; sum-compatible hash on E(F_p); representation technique subset-sum for ECDLP; signed-y four-list cascade; output-sensitive partial verifier


## 2c. N1 conclusion: what AC-3 does that the hits' forecloses phrases do not cover

Forecloses phrases in play: "generic m-SUM decomposition oracle", "free decomposition oracle lifts IC below rho", "larger arity m makes enumeration IC beat rho" (arity floor); "pair-table meet-in-the-middle decomposition beats rho at higher arity", "free decomposition oracle at m = 2 or m = 3" (SO-TABLE prime); "meet-in-the-middle point decomposition as a sub-rho oracle", "walk-carried or target-dependent factor base" (SO-TABLE binary); "x-coordinate oracle meet in the middle", "generic group model simulable oracle" (augmented oracles). Every one of these is a claim that some oracle works; AC-3 claims none of a certain class works, so none of them is refuted by AC-3 or answered by it.

Not covered by any forecloses phrase, and therefore the only novel content:
- N-a. A reduction from planted m-SUM over Z/N to "any decomposition oracle that succeeds on a uniformly random base with a planted target", with preprocessing charged. It makes the lower bound independent of the oracle's internals (enumeration, table, Groebner, SAT, lattice), at the price of Conjecture 3.5 and the base-uniform restriction.
- N-b. The sparse-branch exponent tau >= m - 1/(2 beta) for Delta in (1/2, 1] (retrieved Cor. 4.9, arithmetic verified here).

Covered elsewhere (so not new):
- The (tau, mu) region lemma, the generic corollary and the placement of every built oracle outside R_m are in the same-round sibling scout/scout-query-communication.md (QC1), which AC-3 itself flags as unreviewed.
- The product law, and the "Theta(|F|^2) for 3SUM over a group, structureless null twice as cheap as Riemann-Roch" measurement, are KN-FIND-aa2efc (binary, m = 3).
- "Wagner's k-tree runs on modular k-SUM in Z_N, so prime order forbids nothing" is already in the ledger (IDEA-20260817-1e0111, IDEA-20260920-a5757d); AC-3's dense-branch sentence restates it.
- "The open class is high-degree, implicit-membership or target-dependent" is KN-OPEN-020 and docs/object-frame-ideation.md section 3 (FACTOR-BASE ESCAPE). AC-3's "must be base-specific" is a different axis (uniformity over bases), not a new class.
- The matched-null arm is EXP-ICEX-153c34 arm N (F4).

## 3. N2 known results (build_frontier_map.py --match; raw output in 7.2)

Top rows: KR-IC-46d822, KR-IC-8b9daa, KR-IC-081a58 (Joux-Vitse), KR-IC-5765d2 (SAT and XOR), KR-IC-955fd6 (symmetries) for phrasing 1; KR-IC-b0fcda, KR-IC-5a43e5, KR-IC-8b9daa, KR-IC-46d822, KR-IC-081a58 for phrasing 2; KR-IC-081a58, KR-IC-46d822, KR-IC-8b9daa, KR-IC-955fd6, KR-IC-5765d2 for phrasing 3; KR-IC-b0fcda, KR-IC-5a43e5, KR-IC-73db3f, KR-IC-5931ee, KR-IC-49c882 for my phrasing. Scores are 4-12 and the hits are lexical ("decomposition", "factor base").

Rows read in full (KRMAP.md) and what they state:
- KR-RHO-13bf67 (proven): generic-group Omega(sqrt p); a sub-sqrt algorithm must exploit the representation. This is SO-GEN, not AC-3's route.
- KR-RHO-ea34b8 (proven): preprocessing S*T^2 = Omega~(eps N) (Corrigan-Gibbs--Kogan), met by Bernstein-Lange. Generic with advice. The amortised branch of AC-3 would extend it to non-generic oracles, conditional on the scout's H3b.
- KR-IC-5931ee (known_negative, proven under statistical assumptions): naive Semaev IC over prime fields costs at least generic methods (Yokoyama et al.); algebraic bases work only at small parameters; the Groebner-free variant is reported still worse than rho. This is the nearest known result for coordinate-reading prime-field oracles. It is assumption-based and specific to Semaev-style Groebner solving; it is not a base-uniform reduction to k-SUM.
- KR-RHO-5b1c0a (known_negative, proven): the representation/subset-sum technique costs p^{1.314} over F_{p^2}. An algorithmic k-SUM-style result, not a lower-bound routing.
- KR-IC-5a43e5, KR-IC-73db3f, KR-IC-9e610d, KR-IC-5765d2, KR-IC-1fcdbc, KR-IC-b0fcda, KR-IC-49c882: mechanism, base choice, consensus, SAT, binary slowness, Frobenius bases, quasi-subfield polynomials. None states an average-case or planted k-SUM statement.

Corpus note (knowledge/, grep): genuine hits for `k-SUM|3SUM|SUM-indexing|Golovnev|Dinur-Keller|average-case k` are KN-LIT-1280 (Wagner k-tree as an average-case k-SUM algorithm), KN-LIT-5655 (quantum k-xor/k-sum merging), KN-LIT-7322 (entwined sum problem in multi-signatures), KN-LIT-5950 (fine-grained proofs of work) and KN-FIND-aa2efc (3SUM over a group in the binary free-oracle floor); the other file hits are the substring "checksum". None records ASSVV23, DKK21, 3SUM-indexing or a reduction from them to decomposition.

N2 verdict component: no KR row is the same claim. The generic part of AC-3 (enumerative, table, GGM-simulable oracles) IS covered by KR-RHO-13bf67, KR-RHO-ea34b8 and the closed leads. What is new relative to the KR map is exactly N-a and N-b, both conditional on Conj. 3.5 and unreviewed. Literature-side novelty of N-a is unverified: two searches found no ECDLP-to-k-SUM reduction, which is weak evidence; a reduction this short could exist in the fine-grained cryptanalysis literature without surfacing in two searches.

## 4. N3 ledger (proposals.jsonl, hypotheses.jsonl; raw grep in 7.4)

Terms grepped (regexp, case-insensitive, over claim/statement/mechanism/title): `k-?SUM`; `planted`; `3SUM|4SUM|m-SUM`; `Dinur|DKK|Kopelowitz|ASSVV|Agrawal`; `SUM-indexing|indexing conjecture`; `average-case`; `random[- ]x|random base|random factor base|equal L`; `base-uniform|base[- ]specific`; `subset[- ]sum|knapsack`; `fine-grained`; `153c34`; `Wagner|generalized birthday|k-tree`. Counts: `SUM-indexing` and `fine-grained`: 0; `Dinur|DKK|Kopelowitz|ASSVV|Agrawal`: 1 (IDEA-20261018-49fdf7, a different Dinur paper, DKM ePrint 2025/783); `planted`: 43 proposals and 29 hypotheses, almost all unrelated planted controls (UOV, nonce, divisor, syzygy); `153c34`: 1 proposal (IDEA-20261018-ac3694), and the experiments index has EXP-ICEX-153c34 itself (H-ICEX-6ca21f matched on its own id).


### N3 ledger hit list (id + first 100 chars of claim, taken from the index rows)

- IDEA-20261018-49fdf7 [proposed]: Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 and every n=85,89 rung is a non-adapt
- H-SEMBIN-8e7ae3 [specified]: On a binary curve of prime extension degree n, an m-summand index calculus whose decomposition oracl
- IDEA-20260930-4b7d1e [proposed]: (A) Under vOW's random-function behaviour, generic m-SUM on E(F_(2^n)) per target admits time about 
- IDEA-20261018-ac3694 [proposed]: DEPENDENCY NOTE, NOT A NEW EXPERIMENT. Building the approved non-enumerative membership oracle EXP-I
- H-ICEX-6ca21f [approved]: On the six frozen EXP-ICEX-aaccfc v4 fixtures (16 and 20 bits, seeds 21-23), with the v4 interval fa
- IDEA-20260816-5ea9b4 [proposed]: (A) THE HIDDEN DEGREE OF FREEDOM. Every geometry measurement in this bucket is a ratio against a mat
- IDEA-20260808-7c4e9d [proposed]: The true-null control experiment suggested by the red team ("Arm D: Random-from-F_p MITM") has alrea
- IDEA-20260817-1e0111 [proposed]: (A) THE COUNTEREXAMPLE TO UNIVERSALITY, WHICH IS THE RECORD'S MAIN CONTRIBUTION AND IS UNAFFECTED BY
- IDEA-20260920-a5757d [proposed]: (A) THE REBUTTAL. docs/n13-ecdlp-hint-family.md section 8 Route 3 argues: "Wagner's k-tree attains 2
- IDEA-20260922-845a77 [proposed]: Search heuristic 3 (agents/idea-generator.md) asks, for any bottleneck search, whether the target sp
- IDEA-20260921-da1896 [proposed]: REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): the
- IDEA-20260928-4e2be7 [proposed]: R1 representation. Stages: relation decomposition and linear algebra (rank). KN-OPEN-020 classes: im
- H-PFDR-673eed [proposed]: THE REPRESENTATION TECHNIQUE FAILS FOR ECDLP AT THE FILTER AND NOT AT THE COUNTING, AND THAT LOCALIS
- IDEA-20260808-24c61b [proposed]: Write k in base B with m = log_B N digits, so Q = sum_j [d_j B^{j-1}] P with d_j in [0,B). ECDLP is 


Records opened in full or in the load-bearing ranges (limit 3): (1) ledger/proposals/IDEA-20261018-49fdf7.yaml, whole record; (2) experiments/EXP-ICEX-153c34/specification.yaml, ranges 10-24, 236-252, 298-308, 394-410 plus a grep for arm and setup terms. Every other hit was judged from its index row (claim, mechanism, refs). 

Decisions on the hits that may be the same object:
- IDEA-20261018-49fdf7 (proposed): "formal frame for closing pair-table and k-sum work" via structured-GGM (ePrint 2026/384) and non-adaptive time-space bounds (DKM ePrint 2025/783). Same program role as AC-3 (formal closure of k-sum decomposition designs), different bound, and explicitly model-bounded: "a row outside the model (adaptive, or non-generic) is flagged, not forced in". AC-3 is the conditional complement for the non-generic base-uniform rows. Related, not the same object. The natural carrier is that record's mapping table: AC-3 would add one column ("base-uniform guarantee? yes/no") rather than a separate lead. Its own citation provenance for DKM is `recalled`.
- H-SEMBIN-8e7ae3 (specified): "an m-summand index calculus whose decomposition oracle is a generic m-SUM search cannot fall below the van Oorschot-Wiener rho baseline". Generic m-SUM on binary curves; AC-3 does not restate it.
- IDEA-20260930-4b7d1e (proposed): "HEUR-GENERIC-MSUM is contradicted as worded" by vOW golden-collision MITM, per-target time about 7|F|^(3m/4 - s/2) at store |F|^s. Cautionary precedent: a coarsely worded m-SUM closure was contradicted once already. H3b must be stated with the store parameter. Spot check (derived here, m = 4, 6, 8, integer mu): the vOW upper bound 3m/4 - mu/2 stays at or above H3b's lower bound min(ceil(m/2), m - mu), with equality at mu = m/2, so H3b does not contradict that record; this is a consistency check, not support.
- IDEA-20261018-ac3694 (proposed) and H-ICEX-6ca21f (approved): the unbuilt EXP-ICEX-153c34 backend, its arm N and the preregistered "Arm N ratio near 1". AC-3's first step is attached here (F4).
- IDEA-20260816-5ea9b4 (proposed): "what a matched random factor base actually is": three defensible definitions of "matched" (nominal size, effective size after negation collapse and dedup, and a third). AC-3's "random-x factor base of equal L" must pick one before the ratio means anything.
- IDEA-20260808-7c4e9d (proposed): the random-from-F_p MITM arm C already exists in EXP-SEMAEV-f48dd1. Precedent for a designed-versus-random control on a pair-table oracle.
- IDEA-20260817-1e0111, IDEA-20260920-a5757d (proposed): Wagner's k-tree runs on modular k-SUM in Z_N; the obstruction is the missing sum-compatible filter on E(F_p). Already records the observation in AC-3's dense-branch remark.
- IDEA-20260922-845a77 (proposed): MITM claw split of the point-decomposition step. The upper-bound side of the same m-SUM structure.
- IDEA-20260921-da1896, IDEA-20260928-4e2be7, H-PFDR-673eed, IDEA-20260808-24c61b: factor-base meter, coincidence census against a random base, representation-technique failure at the filter, base-B digit subset-sum. Context; none is a k-SUM lower-bound routing.

N3 verdict component: no record contains a planted or average-case k-SUM conjecture, a k-SUM-indexing conjecture, or a reduction from either to a decomposition oracle. The closest records are IDEA-20261018-49fdf7 (same role, generic and non-adaptive models only) and the arm-N contract (same control, no decision rule).

## 5. N4 notation check

Pair. Representation R1: the x-coordinates (equivalently the points) of the factor-base elements over F_p, with any presentation. Operation set Sigma: translation by factor-base elements. Trichotomy: partial-action, index calculus Class I, which is the baseline pair of docs/object-frame-ideation.md section 1. AC-3 introduces no new tracked object and no projection.

Comparison with the recorded rigidity results:
- IDEA-20260806-c5d183: a projection that propagates deterministically under the full translation action is constant or injective on a prime-order group. AC-3 states nothing about projections, and its Sigma is not the full translation action. Not a restatement.
- IDEA-20260901-863e36: propagation under Sigma means block systems of <Sigma>. AC-3 makes no block-system or quotient claim. Not a restatement.
- KN-FIND-ffe1df Theorem C: an exactly sum-compatible bucket index is a surjective homomorphism onto a group of order dividing N, impossible for prime N. AC-3 does not use it. Its dense-branch remark ("AC-Q closes those at level 1") leans on the adjacent (O2) line, and KN-FIND-ffe1df says in its own title that (O2) is conditional, class-restricted, bucket-averaged and NOT a closure of the k-tree lane. LEAD-EXO-four-list-ktree-join is open_next_step on exactly that gap (relative bucket variance W never measured). The remark must not be read as a closure (F5).
- KN-OPEN-020: bounded-degree algebraic bases over F_p are scoped out; the open class is high-degree, implicit-membership or target-dependent descriptions, and its "Required next result" is a lower bound for an implicit membership/source solver or a classification of relation mechanisms. AC-3 gives a conditional, base-uniform lower bound for any decomposition solver on random bases. That is orthogonal to the KN-OPEN-020 classes (it concerns the complement: bases with no description), so it neither answers KN-OPEN-020 nor re-derives the bounded-degree theorem in new notation. It also declares no factor-base class, so the object-frame FACTOR-BASE ESCAPE constraint is met only trivially ("proposes no base").

N4 verdict component: not a rigidity result in new notation. It is a hardness-reduction statement in the (tau, mu) cost plane for the unchanged Class I pair.

## 6. Defects and required amendments (numbered; all derived here unless marked retrieved)

F1. Planted cost versus per-attempt cost (not in the candidate's self_kill_risk).
- Cor. 4.9 and Thm 4.8 bound the time on planted instances (a solution exists). SO-TABLE's T_dec and the region-lemma tau are charged on every attempt, and an attempt is a fresh random target decomposable with probability pi = B^m/N << 1.
- An oracle that rejects non-members cheaply and pays the planted cost only on a pass is not excluded by Cor. 4.9. Excluding it needs a decision bound. ASSVV23 Thm 4.12 (retrieved) gives search-from-decision with a factor r = B loss at constant advantage, so the decision cost is only >= B^{tau-1}. Thm 4.13 (retrieved) has no loss but needs decision success 1-o(1).
- Arithmetic (prediction, unreviewed): with tau_search = m - 1/(2 beta) and tau_filter = tau_search - 1, the relation term is N * B^{1+tau_filter-m} = N * B^{-1/(2 beta)} = N^{1/2}. So for a cheap-rejecting oracle the sparse branch gives a tie with sqrt(N), not the strict exclusion beta > beta/(1-2 beta) the candidate writes. The strict exclusion holds when non-member cost >= member cost (an exact Groebner solve does not depend on whether a solution exists).
- At SO-TABLE's revisit point (m = 4, B = p^{1/5}): planted bound B^{1.5} = p^{0.3}; filter bound B^{0.5} = p^{0.1}, below p^{1/4}. So "unreachable by base-uniform unamortised oracles" needs the class qualified as "no cheap rejection", or must be re-derived with the decision form.

F2. Binary scope. The only non-generic binary oracle class on the atlas restricts x_i to an F_2-subspace and solves the Weil-descended system (LEAD-ICB-prime-degree-algebraic-decomposition, LEAD-ICE-descent-closure-degree-at-scale, LEAD-ICE-hybrid-guess-determine-l7, SAT/XOR arms). A subspace of dimension l is not a uniform random subset of F_{2^n}, so the base-uniform reduction does not apply. AC-3's listing of LEAD-ICB-generic-table-oracle as "same premise escaped" is an overstatement; B4 and B5 are untouched. The claim "AC-3 prunes only base-agnostic designs" in the candidate's own self_kill_risk (3) is correct and should also be the headline.

F3. Outcome rule versus the existing record.
- A designed-versus-random cost-exponent gap is already on record for the prime Groebner arm: beta_work 0.797 on interval and random bases against 0.647 on subgroup bases, 36/36 cells (LEAD-ICE-prime-field-semaev-solving-degree, EV-SDEG-4a1c3d). Applying the candidate's third outcome ("ratio falls as L^{-gamma}, gamma > 0, CI excluding 0: first base-specific signal, the only admissible escape") to that record would reopen a closed_known lead, although both exponents sit far outside the region (the sibling QC1 converts them to tau 3.99 and 3.24 against a bound below 1.5; that conversion is itself unreviewed).
- So branch C needs an entry criterion (the designed arm's (tau, mu) enters the region), not just gamma > 0.
- Branch A (flat slope, CI inside +-0.1, mu <= tau, then closed_obstructed) turns a toy-scale slope (fixtures of 16-24 bits) into an asymptotic closure. Cor. 4.9 is an ensemble statement with o(1) terms and a log|G| per group operation that dominate at these sizes. The program's own label for empirical flatness at reached sizes is exhausted_at_scale; closed_obstructed(cost_model) additionally needs F1 repaired and the region lemma reviewed.
- Existing measured flatness at the yield level (LEAD-ICP-algebraic-membership-factor-base: mean-yield ratio 1.000000 over six geometries; LEAD-ICP-coincidence-harvest-structured-base: kappa_rel 0.998; LEAD-EXO-dl-character-sum-pseudorandom: R flat at 1.28-1.34) is conservation, not cost, and does not substitute for the cost-ratio test.

F4. Arm N as contracted. EXP-ICEX-153c34 arm N: six v4 fixtures (b16 and b20, three seeds each), 32 held-out attempts per fixture, each decided by G1 twice (interval V and the v4 random-x deck of equal L); the reported statistic is the median interval/random-x cost ratio per fixture; a matched_null control, with preregistered prediction "Arm N ratio near 1" (spec, preregistered_prediction). L is fixed per fixture and takes two values. The 20-fixture frozen-L panel (arm X, five sizes) has no random-x pair. A ratio-versus-L slope over three or more sizes therefore needs a contract amendment (an N arm on the panel fixtures), not just a decision rule. The experiment is approved and its backend unbuilt (LEAD-ICE-charged-toy-ic-exponent-vs-rho, IDEA-20261018-ac3694), so nothing here can run before the backend exists. "Equal L" must also be pinned to one of the three definitions of a matched random base (IDEA-20260816-5ea9b4).

F5. Dense branch. The statement that sum-compatible filters are closed at level 1 by AC-Q must not carry closure weight: KN-FIND-ffe1df's title says the (O2) line is not a closure, and LEAD-EXO-four-list-ktree-join is open_next_step. The m >= 7 residual is the same Wagner-on-Z_N observation already in IDEA-20260817-1e0111 and IDEA-20260920-a5757d.

F6. Amortised branch. H3b (planted m-SUM-indexing, tau >= min(ceil(m/2), m - mu)) is the scout's own conjecture. The indexing literature it leans on (Golovnev et al. STOC 2020, Chung-Larsen SODA 2023, Kopelowitz-Porat) was only seen as bibliography entries here. The candidate's remark that G1 is unamortised (setup about L^4, per-query at least L^5) comes from scout-polynomial-method C1, unreviewed. The two sibling scouts book G1's setup differently (QC1 table: mu = 0; AC-3: setup about L^4, mu <= tau), and the contract reports P_setup per fixture and a with-setup slope as a secondary only, so mu is not measured by anything in the contract.

F7. Dependency on an unreviewed lemma. AC-3 quotes R_m = {tau < m/2 - 1, tau + mu < m - 1}. The sibling file states R_m^find = {tau < min(m/2 - 1, m - 3), tau + mu < m - 1} and R_m^list = {tau < m - 3, ...}. The two coincide for m >= 4 (m/2 - 1 <= m - 3), which is the only range used, but the find-one versus list-all semantics (one decomposition per attempt versus all) is not carried into AC-3's reduction, which returns one decomposition.

F8. Form of the conjecture. Section 4 of ASSVV23 uses the weaker r^{k/2-o(1)} form of Conj. 3.5 (footnote 9, retrieved); the candidate's exponent m - 1/(2 beta) is that weaker form, so for odd m the true conditional bound would be stronger. Conservative, not a defect. The signed variant (H3a) is the scout's claim; the unsigned planted instance is a special case of a signed decomposition, and a spurious signed solution with a different sign sum would have to satisfy sum(eps_j x_{i_j}) = (m - sum(eps_j)) u for a hidden uniform u, which happens with probability about 1/N, so H3a looks safe up to the 2^m density constant (derived here, unreviewed).

## 6b. Handling recommendation (not a status change)

1. Do not open a stand-alone lead. Carry AC-3 as (a) one column ("base-uniform guarantee") in the mapping table proposed by IDEA-20261018-49fdf7; (b) a decision-rule note on arm N of EXP-ICEX-153c34, after F1, F3, F4 are repaired; (c) a one-sentence conditional extension of the Scope clause of LEAD-ICE-generic-oracle-arity-cost-floor, stated with its conditions (Conj. 3.5, base-uniform, no cheap rejection, unamortised).
2. The candidate's outcome mapping, assessed: branch A should read exhausted_at_scale plus a conditional note until F1 and the region lemma are reviewed, not closed_obstructed; branch B (flat, mu > tau, open_next_step with best_measured (tau, mu)) is consistent with the record; branch C needs an R_m-entry criterion (F3).
3. No outcome has been measured. Every exponent above is arithmetic on retrieved statements or a prediction, labelled as such.


## 7. RAW OUTPUTS (verbatim)

### 7.1 lead_atlas.py --match (4 phrasings, --limit 10; env LEAD_ATLAS_* exported as specified)

```
PHRASE: planted k-SUM conjecture lower bound for base-uniform decomposition oracles
   10  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
    7  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
    7  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    6  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    6  KR-IC-8b9daa                                 known_result       Point decomposition via symmetric formulations (Karabina)
    6  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
    6  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    6  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
    6  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
    6  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
```

```
PHRASE: a decomposition algorithm that works on random factor bases is as hard as planted 4-SUM
   14  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   14  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   12  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   11  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   10  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
    9  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
    9  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
```

```
PHRASE: decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off
   14  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   14  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   12  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
   12  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   11  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   11  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
   10  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    9  LEAD-ICP-gfp5-oa-sdhp-jv                     open_next_step     Joux-Vitse oracle-assisted static DH and (n-1)-point decomposition on E(F_{p^5}), p = 2^64 - 2^32 + 1
    7  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
```

```
PHRASE: average-case k-SUM sparse regime reduction random factor base planted decomposable target any algorithm
   13  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   11  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
    9  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    9  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
```

### 7.2 build_frontier_map.py --match (same 4 phrasings, --limit 10)

```
PHRASE: planted k-SUM conjecture lower bound for base-uniform decomposition oracles
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-a4dd54  score=4  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-f3da82  score=4  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
```

```
PHRASE: a decomposition algorithm that works on random factor bases is as hard as planted 4-SUM
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-8b9daa  score=7  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-5931ee  score=5  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-73db3f  score=5  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
```

```
PHRASE: decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off
KR-IC-081a58  score=6  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-955fd6  score=6  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-a4dd54  score=4  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-f3da82  score=4  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
```

```
PHRASE: average-case k-SUM sparse regime reduction random factor base planted decomposable target any algorithm
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=8  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=8  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-e847d1  score=4  [known_mechanism/reported]  Crossbred algorithm for Boolean systems
    sources: KN-LIT-139
KR-RHO-53c89f  score=3  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-0528e7  score=2  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-482ed3  score=2  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
```

### 7.3 First pass, default --limit (8 rows), phrasings 1-3 plus my own (4: random factor base decomposition oracle average-case hardness reduction from k-SUM sparse regime); files from my first pass in scout/raw/ are no longer present (that directory is shared with other runs), so this is a re-run with the default limit; the top-5 order matches the first pass I read

```
PHRASE: planted k-SUM conjecture lower bound for base-uniform decomposition oracles
   10  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
    7  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
    7  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    6  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    6  KR-IC-8b9daa                                 known_result       Point decomposition via symmetric formulations (Karabina)
    6  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
    6  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    6  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
```

```
PHRASE: a decomposition algorithm that works on random factor bases is as hard as planted 4-SUM
   14  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   14  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   12  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   11  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   10  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   10  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
```

```
PHRASE: decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off
   14  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   14  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   12  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
   12  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   11  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   11  LEAD-ICE-gpu-rootfind-oracle                 open_blocked       CUDA root-finding 2-decomposition oracle (embarrassingly parallel target x factor-base cells)
   10  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
```

```
PHRASE: random factor base decomposition oracle average-case hardness reduction from k-SUM sparse regime
   19  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   17  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   16  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   16  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   14  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   13  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
```

### 7.4 Ledger index grep (proposals.jsonl, hypotheses.jsonl; fields claim/statement/mechanism/title)

```
=== TERM: k-?SUM
  [prop] IDEA-20260816-a681fa | proposed | "(A) The one-time layer's entire structural defence against extension is an order-theoretic fact abou"
  [prop] IDEA-20260817-1e0111 | proposed | "(A) THE COUNTEREXAMPLE TO UNIVERSALITY, WHICH IS THE RECORD'S MAIN CONTRIBUTION AND IS UNAFFECTED BY"
  [prop] IDEA-20260920-a5757d | proposed | '(A) THE REBUTTAL. docs/n13-ecdlp-hint-family.md section 8 Route 3 argues: "Wagner\'s k-tree attains 2'
  [prop] IDEA-20261018-49fdf7 | proposed | 'Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 and every n=85,89 rung is a non-adapt'
  -- proposals.jsonl: 4 hits
  -- hypotheses.jsonl: 0 hits
=== TERM: planted
  [prop] IDEA-20260802-007 | adaptation | 'A SINGLE SHARED CHARGED-UNIT ACCOUNTING LAYER - counting group operations, field multiplications and'
  [prop] IDEA-20260805-4f9881 | unverified | 'GOAL-ECTD-001\'s next_action queues BATCH-003 to execute EXP-ECTD-001: a ">=100x class max/median" he'
  [prop] IDEA-20260805-b6af55 | unverified | 'Two properties of the EXP-XEDN-004 measurement apparatus are proposed as checkable facts about its s'
  [prop] IDEA-20260805-ca92fd | unverified | "The quantity that carries UOV's published key-recovery exponent is not the public map. It is the der"
  [prop] IDEA-20260807-a6a038 | unverified | 'Every ball-computable filter that measures a per-vertex arithmetic statistic on supersingular curves'
  [prop] IDEA-20260807-efc8de | proposed | "(A) WHAT THE CAMPAIGN'S POSITIVE CONTROL DOES TODAY. harness/run_icinv.py::instrument_control draws "
  [prop] IDEA-20260807-f6137c | proposed | "(A) WHY AN AUDIT LANE OWES A CLOSURE. RQ-INSTR-f8faa0's decision target is that an instrument that c"
  [prop] IDEA-20260809-28289c | proposed | 'Every measurement in this goal is a claim that a specific structural event causes an observed behavi'
  [prop] IDEA-20260809-98c5ac | proposed | "If a party's Paillier modulus is not proven well-formed, that party can choose it with small prime f"
  [prop] IDEA-20260813-16d752 | proposed | 'For a fixed toy plain-UOV public map and a fixed planted oil space, there is a parameter-explicit in'
  [prop] IDEA-20260813-2d839b | proposed | 'On a frozen toy recursive sampler with an exact public coefficient view, one can construct a planted'
  [prop] IDEA-20260813-5988b7 | proposed | 'After conditioning compressed and uncompressed toy public-map ensembles on the identical planted oil'
  -- proposals.jsonl: 43 hits
  [hypo] H-AES-d677fa | proposed | 'SCOPE: the container the dispatched task actually runs in, on its run date; the verifier pair the AE'
  [hypo] H-AUXIN-e73988 | specified | 'Fix the exact planted-divisor cost identity of IDEA-20260831-bd0356 before any Cheon solver, any rec'
  [hypo] H-BINSTD-953387 | approved | 'SETTING. Part-2 certificate objects CERT-LABEL, CERT-QUOT, CERT-BIND as declared by EXP-BINSTD-17874'
  [hypo] H-CERTBIN-a3d441 | analyzed | 'CLAIM (control / law-index instrument; NO ATTACK; NO EXPONENT). Representation class R1 (x-coordinat'
  [hypo] H-CRYPTO-830d47 | specified | 'The fixed (M+S+100I)/16 conventional GOE ruler can be made exactly reproducible for the specified in'
  [hypo] H-CZLIFT-cb95b8 | weakened | 'For p in {101, 211, 401, 809, 1601, 3203, 6421, 12809}, random y^2 = x^3 + a x + b over F_p, and r i'
  [hypo] H-DREG-49869c | approved | 'Let f1 = x^2 + y and f2 = y^2 + x in F_2[x, y]. Both vanish at (0, 0). The planted generators are x*'
  [hypo] H-ECDLP-1d8ff7 | specified | 'Fix the closed-form conversion- threshold identities of IDEA-20260904-f68c7f before any Hidden Numbe'
  [hypo] H-ECDLP-38f4b4 | specified | 'Fix one Boolean ring GF(2)[x]/(x^2-x) before any rank is read. Stage 0 asserts only the certificate-'
  [hypo] H-ECDLP-42f434 | approved | 'SETTING (Stages 0-1 of IDEA-20261003-0c5564). A hint family is a triple (D, chi, omega). Lemma V: a '
  [hypo] H-ECDLP-536b21 | specified | 'Fix one synthetic 3-block positive CNF on six variables a0,a1,b0,b1,c0,c1, frozen before any Aut is '
  [hypo] H-ECDLP-af796a | specified | 'On the preregistered constant Weierstrass surface y^2 = x^3 + x + 30 over F_31, with planted degree-'
  -- hypotheses.jsonl: 29 hits
=== TERM: 3SUM|4SUM|m-SUM
  [prop] IDEA-20260920-9e672a | proposed | 'The design note waves the Joux-Vitse variant away as "O(Cp^2), again above 128" without a constant. '
  [prop] IDEA-20260930-4b7d1e | proposed | "(A) Under vOW's random-function behaviour, generic m-SUM on E(F_(2^n)) per target admits time about "
  [prop] IDEA-20261018-5f37a1 | proposed | 'Koblitz toy, n prime, G of prime order r, tau = scalar lambda of order n, base = K signed orbit colu'
  -- proposals.jsonl: 3 hits
  [hypo] H-SEMBIN-8e7ae3 | specified | 'On a binary curve of prime extension degree n, an m-summand index calculus whose decomposition oracl'
  [hypo] H-SUBRES-001 | weakened | 'In the serial-S3 split of the m = 5 Semaev summation relation with a 2 | 3 arity split over a balanc'
  -- hypotheses.jsonl: 2 hits
=== TERM: Dinur|DKK|Kopelowitz|ASSVV|Agrawal
  [prop] IDEA-20261018-49fdf7 | proposed | 'Every recorded pair-table, k-sum and 6-sum design at ECC2K-130 and every n=85,89 rung is a non-adapt'
  -- proposals.jsonl: 1 hits
  -- hypotheses.jsonl: 0 hits
=== TERM: SUM-indexing|indexing conjecture
  -- proposals.jsonl: 0 hits
  -- hypotheses.jsonl: 0 hits
=== TERM: average-case
  [prop] IDEA-20260828-9643b1 | proposed | '(A) THE CALIBRATION QUESTION RQ-MLDSA-001 ASKS, RESTATED PRECISELY. The RQ\'s decision_target asks "w'
  -- proposals.jsonl: 1 hits
  [hypo] H-MLDSA-2c10d3 | specified | 'Fix the exact count identity of IDEA-20260828-9643b1 before any later-stage claim. Stage 0 asserts o'
  -- hypotheses.jsonl: 1 hits
=== TERM: random[- ]x|random base|random factor base|equal L
  [prop] IDEA-20260808-7c4e9d | proposed | 'The true-null control experiment suggested by the red team ("Arm D: Random-from-F_p MITM") has alrea'
  [prop] IDEA-20260816-5ea9b4 | proposed | '(A) THE HIDDEN DEGREE OF FREEDOM. Every geometry measurement in this bucket is a ratio against a mat'
  [prop] IDEA-20260816-79aec0 | proposed | '(A) Merkle-Damgard strengthening pins bits in the last block: a one bit, zeros, and a 64-bit length '
  [prop] IDEA-20260816-c9565d | proposed | '(A) THE PROBLEM. This program has recorded coverage excesses for structured factor bases of 1.0012, '
  [prop] IDEA-20260928-4e2be7 | proposed | 'R1 representation. Stages: relation decomposition and linear algebra (rank). KN-OPEN-020 classes: im'
  [prop] IDEA-20261006-4e827a | proposed | 'On the first ordinary short-Weierstrass curve over F_73, with m = 3, thirty-six targets from the pri'
  [prop] IDEA-20261006-5bfbcf | proposed | 'Representation R1, attack stage relation yield. On E: y^2 = x^3 + x + 4 over F_61, let F be the four'
  [prop] IDEA-20261017-2cecfc | proposed | 'A target-blind Frobenius-orbit base can be compared after cofactor projection with a same-column ran'
  -- proposals.jsonl: 8 hits
  [hypo] H-INCB-dc5010 | proposed | 'SCOPE. The three toy primes of EXP-INCB-001, the same factor-base x-sets and the same random x-subse'
  -- hypotheses.jsonl: 1 hits
=== TERM: base-uniform|base[- ]specific
  [prop] IDEA-20260921-da1896 | proposed | 'REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): the'
  -- proposals.jsonl: 1 hits
  -- hypotheses.jsonl: 0 hits
=== TERM: subset[- ]sum|knapsack
  [prop] IDEA-20260807-0085af | proposed | 'EV-NCP-001 is a clean replicated negative -- the commutative signed-subset-sum quotient reproduced 1'
  [prop] IDEA-20260808-24c61b | proposed | 'Write k in base B with m = log_B N digits, so Q = sum_j [d_j B^{j-1}] P with d_j in [0,B). ECDLP is '
  [prop] IDEA-20260808-d25ea7 | proposed | 'An extra (non-Koszul, non-rewritable) syzygy in degree D is by definition a coefficient vector c wit'
  [prop] IDEA-20260813-8aa6ea | proposed | "Simon 2026's claimed algorithm needs Q = k*n^(c+1) coherent DSP samples with c >= 12, k > c -- KN-OP"
  [prop] IDEA-20260901-871141 | proposed | '(A) THE SHAPE NOBODY HAS USED. CSIDH key recovery, in the vectorization formulation, is: given E_0 a'
  [prop] IDEA-20260922-40003d | proposed | '(A) EXACT TABLE, computed this session by ord_m(2) and the subset-sum rule of IDEA-20260918-9abf42(B'
  [prop] IDEA-20260922-845a77 | proposed | 'Search heuristic 3 (agents/idea-generator.md) asks, for any bottleneck search, whether the target sp'
  [prop] IDEA-20260930-750de2 | proposed | 'SETTING. Generic group G of prime order n with generator P; target Q = [x]P with x in W(m, w) = {0 <'
  -- proposals.jsonl: 8 hits
  [hypo] H-NISTBIN-7f68cc | approved | 'Each degree m is prime. The multiplicative order of 2 modulo m is 162, 29, 94, 204, and 114. That or'
  [hypo] H-PFDR-673eed | proposed | 'THE REPRESENTATION TECHNIQUE FAILS FOR ECDLP AT THE FILTER AND NOT AT THE COUNTING, AND THAT LOCALIS'
  [hypo] H-SSI-5d6b1d | specified | 'Fix the exact count identity of IDEA-20260901-871141 before any later-stage claim. Stage 0 asserts o'
  -- hypotheses.jsonl: 3 hits
=== TERM: fine-grained
  -- proposals.jsonl: 0 hits
  -- hypotheses.jsonl: 0 hits
=== TERM: 153c34
  [prop] IDEA-20261018-ac3694 | proposed | 'DEPENDENCY NOTE, NOT A NEW EXPERIMENT. Building the approved non-enumerative membership oracle EXP-I'
  -- proposals.jsonl: 1 hits
  -- hypotheses.jsonl: 0 hits
=== TERM: Wagner|generalized birthday|k-tree
  [prop] IDEA-20260808-e40da2 | proposed | 'SCOPE. The BIAS-DETECTION CLASS of nonce-leakage attacks, defined formally below; group order N bits'
  [prop] IDEA-20260809-4969d8 | proposed | 'Two solvers exist for the same problem: a sub-exponential generalized-birthday approach and the poly'
  [prop] IDEA-20260813-710293 | proposed | "Kuperberg's sieve combines coherent coset-sample pairs (k=2) at each of Theta(sqrt(log N)) rounds, b"
  [prop] IDEA-20260817-1e0111 | proposed | "(A) THE COUNTEREXAMPLE TO UNIVERSALITY, WHICH IS THE RECORD'S MAIN CONTRIBUTION AND IS UNAFFECTED BY"
  [prop] IDEA-20260823-835868 | proposed | 'The decision-relevant gate for a Wagner-style prime-order ECDLP route is not a scalar pruning ratio.'
  [prop] IDEA-20260904-f7d47d | unverified | '(A) THE EXACT CLAIM. Let E/F_p have #E(F_p) = N prime, let h : E(F_p) -> [M] be a cheaply computable'
  [prop] IDEA-20260920-a5757d | proposed | '(A) THE REBUTTAL. docs/n13-ecdlp-hint-family.md section 8 Route 3 argues: "Wagner\'s k-tree attains 2'
  [prop] IDEA-20260926-136bd3 | proposed | "SEAM. The brief asks what replaces the additive low-bits coordinate that Wagner's k-tree needs and t"
  -- proposals.jsonl: 8 hits
  [hypo] H-ECDSA-9946a0 | specified | 'Fix the exact k-cap arithmetic of IDEA-20260808-e40da2 before any merge tree, any Fourier coefficien'
  [hypo] H-JPR-3a00f0 | proposed | 'Let G be a prime-order elliptic-curve subgroup of order N and let four independently sampled, source'
  [hypo] H-QALG-adfff4 | specified | 'Fix the exact count identity of IDEA-20260813-710293 before any later-stage claim. Stage 0 asserts o'
  [hypo] H-ROS-9e078a | specified | 'Fix the exact count identity of IDEA-20260809-4969d8 before any later-stage claim. Stage 0 asserts o'
  -- hypotheses.jsonl: 4 hits
```
