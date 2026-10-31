# Gate N1-N4: CA "Exact torsion-cancellation and sum-set count law for native factor bases across isogeny-volcano levels" (field: algebraic geometry of curves and covers)

Scout: novelty gates only. Nothing inside the repositories was edited, created, added or committed. Everything here was written under `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`. Numbers marked "scout-check" were produced here (python, stdlib); numbers marked "candidate-reported" were NOT reproduced here. Provenance tags: recalled | retrieved. Expected values are labelled predictions.

## VERDICT: advances_lead (primary lead LEAD-STR-class-representative-ic-selection, open_next_step; co-lead LEAD-ICP-isogeny-transported-relation-yield, open_blocked). Novelty is narrow, and most of the candidate is already in the crypto repo or a same-round sibling scout.

What is NOT new (found in the repositories, so not a discovery):
1. "Volcano IC-yield effects (l=2 floor deficit, coordinate tau, horizontal tau) are effects of the base's cofactor classes" is a MEASURED result already: `crypto: research/generator_effect_ic_20261019/README.md` (E3a, read here; retrieved from the local copy). Gates G1-G4 pass: WLS slope 1.064 [1.040, 1.090], horizontal tau 0.34%, coordinate tau 0.19%, pooled l=2 contrast 99% explained by N0 = `exact_decomposition_ceiling`. The atlas rows of LEAD-STR-class-representative-ic-selection and LEAD-ICP-isogeny-transported-relation-yield do not cite E3a (no atlas lead mentions E3a, E3b, N0, `exact_decomposition_ceiling` or LEAD-19; `grep -rIl` over knowledge/leads/ecdlp returned nothing), so the atlas is stale on this point. That staleness is not novelty for the candidate.
2. The instrument: `exact_decomposition_ceiling(g, points, r, m)` in `src/cryptanalysis/ic_boundary.rs` (L467, read here) already counts class-cancelling m-multisets for m = 2 and m = 3 from the base's cofactor classes `[r]P_i` (the m = 3 branch walks class pairs and returns None above 4096 classes). The candidate's "first step (1): implement the exact distinct-3-sum count" re-implements the neighbouring statistic (it counts DISTINCT sums, which is the coverage object, not the multiset ceiling N0) but not a new instrument class.
3. The projected-base lever: `PrimeProjectedAbscissaBase` (ic_framework/plugins.rs L137-375) and `--base-arms raw,projected,subgroup` (`project_factor_base`, `prime_subgroup_factor_base`) exist; the binary-ladder version was RUN (`crypto: research/lead19_projected_base/README.md`, "Engineering", relation yield per trial rises by about h, prime-order control counter-identical across arms). E3b's PLAN (research/generator_effect_ic_20261019/PLAN.md) registers the same three arms at equal B. The candidate's "first step (2): recommend an ecbench session with PrimeProjectedAbscissaBase against prime-abscissa" is E3b.
4. The leading-order denominator law "a subgroup-scoped base beats a full-curve base by exactly the cofactor h" is ledger IDEA-20260829-c6e7a4 (opened); the exact-count object "P(decomp) = |mW intersect H|/|H|, an integer ratio, computed exactly instead of sampled" is ledger IDEA-20260830-21e7c4 (opened). Both proposed, never run.
5. The prime-order Poisson null for the P29/P37 arity-3 panel is already in the frozen plan: `research/conductor_relation_yield_20261014/README.md` says the expectation for nonempty targets is 1 - exp(-|F|^3/(6r)), "about 0.067 and 0.065". Scout-check: with |F| = 2B signed points, distinct signed triples without an opposite pair = C(2B,3) - B(2B-2) = 22,108,160 (P29, B = 256) and 5,451,097,600 (P37, B = 1600); 1 - exp(-N3/r) = 0.066737 (P29) and 0.064589 (P37). So the candidate's 0.06673/0.06674 and "5.45e9 signed triples" reproduce arithmetically. The panel's own null therefore already predicts floor/crater = 1 for prime-order endpoints; the candidate refines it to the exact coincidence-aware count (candidate-reported: ratio 1.0001; not reproduced here).
6. The candidate's own conservation statement (mean yield binomial(B+m-1,m)/N for every base of size B) is KN-FIND-007, stated for any finite abelian group G with the sums' group in the denominator.

What is new (not found in atlas, KRMAP, ledger index, E3a, E3b PLAN, PROTOCOL v2, or the v2.1 README):
a. The finite-B closed form with the diagonal (doubling) term, E[#pairs P_i + eps P_j in G] = B(B-1+t)/|H|, t = |E(F_p)[2]|, |H| = #E/r odd-coprime part. Scout-check of the derivation: off-diagonal pairs (2 C(B,2) signed pairs) land in G with probability 1/|H| when H-components are equidistributed; the B doublings 2P_i land in G iff the H-component is 2-torsion, probability t/|H| (G has odd order so H[2] = E[2]); sum = B(B-1+t)/|H|. So the m = 2 floor/crater ratio is (B-1+2)/(B-1+4) = 33/35 = 0.9429 at B = 32 (scout-check arithmetic; candidate-reported measured 0.9417 / README 0.942 [0.931, 0.953], not reproduced).
b. The attribution of E3a's N0 difference (and the v2.1 README's "cause of the l=2 effect stays open") to the 2-part of E(F_p) changing between volcano levels, via t. The v2 PROTOCOL (section 1, "Mechanism contrast") and the v2.1 README ("the explanation 'the l-power torsion changes between levels' is not supported") record that a COARSE version of this explanation was tested through the l=3 contrast and looked refuted; the candidate's law says only E[2] enters (off-diagonal terms are structure-independent), which is consistent with that failed contrast (t = 1 at every l=3 level). That refinement is the one genuinely new sentence. Note the same law was independently found by a sibling scout this round (see Prior-scout overlap below).
c. The proposal to read the 17 missing EXP-ECTD-0cf008 arms from exact finite-population counts instead of a hypergeometric sample, for the prime-order endpoints, plus the P37 compiled count. The idea of replacing a sampled P(decomp) by its exact integer ratio is IDEA-20260830-21e7c4; its application to the P29/P37 crater/floor panel is not recorded.

Corrections to the candidate's framing (these matter for the disposition mapping):
- The law is an EXPECTATION, not an identity or a proof. B(B-1+t)/|H| assumes the base's H-components are uniform on H. The exact per-base quantity is N0 (what `exact_decomposition_ceiling` already returns); the candidate's own per-class correlation of 0.785 (n = 14, candidate-reported) and model CV 6.2% are what an expectation law with realized fluctuation looks like. So the candidate's self_kill_risk wording "count identity" and the "closed_obstructed(proof)" mappings are overstated. For prime-order curves the "every representative lever is identically 0" claim has two different parts: the MEAN is closed by KN-FIND-007 (proved), while COVERAGE (distinct-sum count equal to Poisson within 1e-3, H-A1) is measured, candidate-reported, and not reproduced here.
- "Blocked arity-3 oracle" is a mislabel. The block recorded in `problems/prime-field-arity3-relation-oracle.md` (blocked_by of LEAD-ICP-isogeny-transported-relation-yield) is an infrastructure and Coordinator-access block: `psutil` absent from the interpreter, a macOS RSS read failure, the Coordinator backend model unverified / `ANTHROPIC_API_KEY` unset, disk headroom. It names no missing mathematical oracle. Its exit criteria require running the 17 arms under the admitted supervisor with independent replay and evidence review "before any hypothesis or lead decision". An exact count is a cheaper way to learn the finite-population values the arms estimate, but it does not discharge those exit criteria without a Coordinator amendment (the candidate lists this as its medium self-kill risk).
- Two fixed 29-bit and 37-bit pairs cannot decide the lead's own discriminator. LEAD-ICP-isogeny-transported-relation-yield says the only outcome that would matter is "a coverage or variance excess that grows with field size". H-ECTD-e88346's interpretation_limits: "Two purposively selected classes provide no population estimate or scaling law." An exact P29 and P37 pair gives a two-point slope at most.
- Proposed dispositions of the form closed_obstructed(proof) for LEAD-ICP-isogeny-transported-relation-yield and the IC-meter half of LEAD-TRF-teske-secret-isogeny-trapdoor would need the Teske lead's own wording: "ratios consistent with one, as the isogeny-fibre pullback theorem predicts, close the IC-meter half at toy scale". The pullback theorem concerns transported bases (RESEARCH_ISOGENY_FIBERS_ECDLP.md Thm 4.2; pair46 03-floor-pullback). The panel's primary contrast is native versus native, which is where an exact count adds something.
- Effect on named bottlenecks: predicted gain is 0 on prime order (the candidate says so). B3's gap lives on the eight prime-order Table B rows (h = 1, the arms coincide). So CA closes side leads; it does not move B1-B7.

## N1 Atlas collision

Runs (raw output pasted verbatim in the Raw outputs section below): #1-#3 are the three match_phrasings in order; #4 is my own phrasing ("native factor base torsion H-component cancellation sum-set count distinct signed sums Poisson isogeny volcano level"). Each run printed exactly 8 rows. The top 5 of every run were opened (lead YAML: mechanism, obstruction where present, forecloses, next_action) and KR rows were read in KRMAP.

Top-5 per run and judgement:
- Run 1: LEAD-ICB-cofactor-torsion-quotients (closed_obstructed, proof); LEAD-ICP-isogeny-transported-relation-yield (open_blocked); LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale); LEAD-STR-class-representative-ic-selection (open_next_step); LEAD-STR-isogeny-class-generic-invariance (closed_obstructed, theorem).
- Run 2: LEAD-ICP-isogeny-transported-relation-yield; KR-IC-5931ee; LEAD-ICP-lattice-ic-relation-construction (open_blocked); LEAD-STR-class-representative-ic-selection; KR-IC-9e610d.
- Run 3: LEAD-ICE-decomposition-probability-audit (open_next_step); LEAD-ICE-linearization-excess-fb-prior (open_unexamined); LEAD-STR-class-representative-ic-selection; LEAD-ICB-factor-base-subspace-choice (exhausted_at_scale); LEAD-ICE-semaev-yield-model-coset-typing (open_next_step).
- Run 4: LEAD-ICP-isogeny-transported-relation-yield; LEAD-EXO-dl-character-sum-pseudorandom; LEAD-ICB-cofactor-torsion-quotients; LEAD-ICP-algebraic-membership-factor-base (closed_obstructed, theorem); LEAD-STR-isogeny-class-generic-invariance.

Same-mechanism hits (the candidate is a sharper next step, not a new mechanism):
1. LEAD-STR-class-representative-ic-selection (open_next_step). Mechanism: small-abscissa IC yield depends on which points the coordinates call small; transport to the crater or pick a better isomorphic model; includes the 5.8% l=2 yield effect and the 7.2% model effect with "mechanism unknown". best_measured: l=2 IC yield floor/crater 0.942 [0.928, 0.956]. Its `discriminates` says that if the effects vanish on held-out data they are "factor-base sampling noise or a selection artifact". forecloses: "floor versus crater index calculus yield", "pick the isomorphic model with the best small-x factor base", "large conductor gap changes index calculus cost". CA supplies a third explanation (neither a lever nor noise: exact cofactor-class bookkeeping, with the t-term fixing the size of the l=2 deficit at 33/35 for B = 32) and says the lead's arm (c) selection gain is a sub-1/B constant dominated by projecting the base into G. That is not covered by the forecloses phrases, but it is the lead's sharper explanation, so advances_lead.
2. LEAD-ICP-isogeny-transported-relation-yield (open_blocked). Mechanism: carry or compare factor bases across volcano levels (P29/P37 arity-3, native vs random). next_action: finish the 17 missing arms of EXP-ECTD-0cf008. discriminates: "transported/native yield ratios within the A/A band confirm the conservation prediction and close the lead; a coverage or variance excess that grows with field size is the only outcome that would matter". CA is a candidate replacement for the next_action's measurement by exact counts (same discriminator). forecloses: "walk the isogeny volcano to a curve with better relation yield", "crater versus floor index calculus". Not a different mechanism: advances_lead (conditional on the Coordinator accepting exact counts in place of the sampled arms).
3. LEAD-TRF-teske-secret-isogeny-trapdoor (open_next_step, not in the top 5 of any run but named by the candidate): the IC-meter half shares the 20-arm panel. Same remark as 2.

Not the same mechanism (what CA does that these forecloses phrases do not cover):
- LEAD-ICB-cofactor-torsion-quotients (closed_obstructed, proof). obstruction.statement (verbatim, no Scope clause): "On ECC2K-130 gcd(4, l) = 1, so every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality); exactly sum-compatible filters on E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in; ... the production 2-torsion census adds 0 relations." forecloses "spend the cofactor on decomposition". CA is prime-field and uses the quotient E(F_p) -> E/G only as a COUNTING device for which pairs cancel; it prunes nothing and claims no gain. The projected-base arm is exactly "work in the order-r projection", i.e. what that obstruction says rho already does. Not a duplicate; consistent with it.
- LEAD-ICP-algebraic-membership-factor-base (SO-ALGFB, closed_obstructed, theorem). obstruction.statement (verbatim): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B." CA does NOT escape it. The candidate's "volcano fixtures are cofactor curves, outside the Scope clause" is true but empty: the Scope clause narrows where the sentence is proved, KN-FIND-007 itself is stated for any finite abelian group with the sums' group in the denominator, IDEA-20260829-c6e7a4 already applies it to cofactor curves, and at h = 1 CA returns the obstruction (the candidate agrees). Its revisit_when ("a base raises coverage or variance with an excess that grows with N") is exactly what CA predicts will NOT occur.
- LEAD-STR-torsion-module-leak (SO-TORS, closed_obstructed, proof). obstruction.statement (verbatim): "Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). Toy checks agree: the psi_5 factor-degree multiset does not change with k (H-TORS-3bed8a). Scope: prime-order G, any l != N." CA's H-components are curve data independent of k; it uses no point-dependent torsion statistic. Consistent, escapes nothing.
- LEAD-STR-isogeny-class-generic-invariance (SO-ISO, closed_obstructed, theorem, no Scope clause). obstruction.statement (verbatim): "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (+-5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve." CA is about IC, not generic methods, so "escapes SO-ISO" is true but unneeded. Its revisit_when assigns "a level-dependent change in step cost (field-arithmetic model cost)" as a constant belonging to LEAD-STR-class-representative-ic-selection: that is the lead CA lands on.
- LEAD-ICP-generic-table-decomposition (SO-TABLE, closed_obstructed, theorem), obstruction.statement ends "Scope: any generic (enumeration/table) decomposition over F_p." The pair table is inside scope; CA moves a constant, only for h > 1. Not escaped (the candidate agrees).
- LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale): additive-character bias R = C_EC/C_null flat at 1.28-1.34 across 2^20..2^26; revisit_when "R trends upward with p beyond 2^30 ... or a structured set other than small-x shows R growing with N". CA's prime-order coverage statement (distinct-sum count equals Poisson within 1e-3) is a coarse-grained relative of this measurement. Adds a number at P29; does not address growth with N.
- LEAD-ICE-decomposition-probability-audit (open_next_step): exact integer-ratio P(decomp), "the mean is fixed by yield conservation; only the per-target distribution, clustering and charging remain"; next action reports the exact count vector c_D and variance against a size-matched random base (BATCH-79a580). Same family as CA's exact count at h = 1; no cofactor/2-torsion term and no volcano.
- LEAD-ICE-semaev-yield-model-coset-typing: "coset-typed" means Nagao-style disjoint shifts (typed vs untyped domain), a different object. LEAD-ICB-factor-base-subspace-choice, LEAD-ICE-linearization-excess-fb-prior, LEAD-ICP-lattice-ic-relation-construction: lexical or related-vocabulary hits only.

Standing obstructions: SO-GEN, SO-MULTI, SO-ENDO, SO-PAIR, SO-PADIC, SO-XEDNI, SO-COVER, SO-QSP, SO-MONO, SO-FROB, SO-WALK, SO-DECK, SO-CHEON, SO-NET are not touched (CA makes no walk, cover, pairing, p-adic, Frobenius-orbit or multi-target claim). SO-TABLE, SO-ALGFB, SO-TORS, SO-ISO: not escaped; CA claims no escape in substance.

## N2 Known results (build_frontier_map --match)

Four runs (the same four phrasings, raw below), 8 rows each. No KR row states a cofactor-class cancellation count, a 2-torsion diagonal term, or a volcano-level IC-yield law.
- KR-IC-955fd6 (known_mechanism, heuristic; FGHR/FHJRV): small-order torsion and S_m symmetry shrink point-decomposition SYSTEMS (Edwards/Jacobi, F_{q^5}). Different object (algebraic system size, not a count of base pairs landing in the target subgroup).
- KR-IC-5931ee (known_negative, proven): naive Semaev IC over F_p cannot beat generic. Context and the standing negative CA sits under.
- KR-RHO-755e35 (textbook_fact, proven): "Isogenous curves are equally hard; isogeny walks do not find weak curves." Context for the Teske/volcano leads; CA does not contradict it (it concerns constants of native IC bases).
- KR-IC-5a43e5 (Semaev polynomials), KR-IC-73db3f (choice of V; binary), KR-IC-b0fcda (Frobenius-invariant bases), KR-IC-49c882 (QSP), KR-IC-1fcdbc, KR-IC-a4dd54, KR-IC-46d822, KR-IC-9e610d, KR-RHO-825bca, KR-RHO-cb1c58, KR-RHO-1c2928: lexical or context hits.
Internal known result (not a KR row): KN-FIND-007 yield conservation (confidence established, proof_status derivation), which states the mean for any finite abelian group.
Literature citations for the load-bearing external ingredient (the 2-part of E(F_p) varies with the volcano level), with provenance:
- Miret, Moreno, Sadornil, Tena, Valls, "An algorithm to compute volcanoes of 2-isogenies of elliptic curves over finite fields", Appl. Math. Comput. 176(2) (2006) 739-750, DOI 10.1016/J.AMC.2005.10.020: retrieved at bibliographic/abstract level only (WebSearch this session: the bibliographic record, plus the search tool's own paraphrase that the abstract relates the 2-torsion structure of a curve to its level in the volcano; that paraphrase is not a quotation from the paper); the theorem for intermediate levels and the floor was NOT read, so the level statement stays recalled-plus-locally-observed. 
- Ionica-Joux, "Pairing the Volcano", ANTS IX / Math. Comp. 2013, arXiv:1110.3602: retrieved at abstract level (WebFetch this session: title, authors, abstract; the abstract says it treats 2-isogeny volcanoes and a group-structure invariant, and does not itself state the level theorem). Load-bearing level theorem remains unverified from this source.
- Kohel, thesis (1996): recalled, not verified.
- Isogeny of degree coprime to n induces an isomorphism E[n] -> E'[n] commuting with Galois (candidate ingredient ii): recalled, standard; follows because kernel and E[n] meet trivially and orders agree.
The program's own data supports the level statement: the v2 PROTOCOL class table lists floors as cyclic (for example Z/15810996) and the other levels as Z/n x Z/2 (retrieved, local file); #E = 15810996 = 2^2 * 3 * 1317583 and 13904116 = 2^2 * 3476029 (scout-check factorizations). The candidate's computation over all 14 l=2 classes (|E[2]| = 4 versus 2) was not reproduced here.
Verdict for N2: no known_result for the counting law; the external ingredient is the textbook volcano 2-torsion structure.

## N3 Ledger (grep of ledger/.index/proposals.jsonl and hypotheses.jsonl; script `ca-torsion-raw/lgrep.py`, raw in `ca-torsion-raw/ledger_grep_raw.txt`, pasted below)

Key terms: volcano/crater/floor; cofactor + factor base/abscissa; 2-torsion|E[2] + yield/relation; class-cancelling | cofactor class | exact ceiling | denominator | N0; conservation + isogeny/volcano/conductor; distinct|Poisson|sum-set + coverage/occupancy; project|subgroup + factor base; E3a|E3b|generator effect (zero hits); 2-torsion + level/volcano (no relevant hit); coverage excess growing with N (zero hits).
Hits that may be the same object (id, 100-char claim):
- IDEA-20260829-c6e7a4 "(A) THE DENOMINATOR CORRECTION, DERIVED. KN-FIND-007 fixes the mean per-target decomposition yield at binom(B+m-1,m)/|G| ..." OPENED. Leading-order cofactor law (ratio EXACTLY h for subgroup-scoped versus full-curve base), no torsion, volcano or diagonal term (grep inside the record: none). Children H-ECDLP-f79c89 (proposed), EXP-ECDLP-933c10 (draft).
- IDEA-20260830-21e7c4 "(A) THE OBJECT IS DETERMINISTIC. For a factor base V of B x-coordinates ... P(decomp) = |mW intersect H| / |H| ..." OPENED. The exact integer-ratio object and the per-cell decidability table; no volcano or 2-torsion term. This is the nearest record to CA's instrument half.
- H-ECTD-e88346 (approved) "For the two specified ordinary prime-field crater/floor pairs with prime conductor steps 8209 and 131101, native first-B-abscissa signed factor bases may have a repeatable difference in verified useful three-summand relation occupancy ..." OPENED. This is the panel CA wants to decide. Its mechanism already says "Equal base cardinality and shared group order fix the all-target ordered multiplicity mean but permit a different distribution of triple sums", prediction "different" at >= 20%, with the isomorphic-transport arm as the exact control.
- IDEA-20260805-a25f11 "For a prime-field Semaev factor base of B x-coordinates on E(F_p) with N = #E(F_p), the mean number of size-m decompositions ... mu(B,m) = C(2B+m-1,m)/N ..." (index row only): conservation for the signed set, whole group.
- IDEA-20260906-86cd30 "THE m = 2 DECOMPOSITION GRAPH OF A PRIME-ORDER CURVE IS A PATH ... exact closed form" (index row only): the prime-order m = 2 analogue of CA's h = 1 case.
- IDEA-20261017-3db2a8 "The Semaev yield is an exact first moment d(V)*C(|W|+t-1,t)/N ... the class of the multiset sum in E/<P>" (index row only): binary cofactor-class first moment, equidistribution of the class assumed; no diagonal term; binary-only.
- IDEA-20260830-1f2b8b (cofactor index n1 = [E(F_p): <G>] as the denominator of the rate, over-dispersion), IDEA-20261018-5fa71b (one h-sum count vector, three moments; pair "R1 x-labels; Sigma = translation by base elements", Class I partial-action), IDEA-20260830-c5c614 and H-PFDR-1b2386 (conservation binds only on the whole group; target preselection), H-ICEX-7af505, H-ICLIFT-d31664 (EXP-FB3-001 counting convention): conservation family, no volcano or 2-torsion term.
- IDEA-20260731-017 / H-ECTD-19017a / H-ECTD-001 (weakened) / IDEA-20260901-2fb77b (depth buys a count of rational l-isogeny fibrations of the x-line; ell+1 at the crater, 1 in the interior) / H-VOLC-e733db (Stage 0 identities only): volcano-level IC ideas with a different tracked object (fibrations, heavy tails), none states the cofactor cancellation count.
Decision: no ledger record is the same object. The pair {c6e7a4, 21e7c4} carries the leading-order law and the exact-count instrument; H-ECTD-e88346 carries the target panel; the t-term and the volcano-level attribution are in none of them. Three full records opened (c6e7a4, 21e7c4, H-ECTD-e88346); the others from index rows only.

## N4 Notation

(representation, operation set) pair: (the x-coordinate of a point of a chosen model (u-scaling) of a chosen vertex curve of an l-volcano, base = the B smallest abscissae of the full group E(F_p); Sigma = translation by base elements, the IC partial action, with presentation changes by Velu isogenies and isomorphisms). This is the program's existing Class I partial-action pair ("PAIR (R1 x-labels; Sigma = translation by base elements)", IDEA-20261018-5fa71b); it is not a new arithmetic.
Tracked object: pi_S: E(F_p) -> S = E(F_p)/G, a homomorphism (a block system of full translation, which exists only because #E is composite). At h = 1, S is trivial, the object carries nothing, and CA reduces to conservation plus the Poisson coincidence count.
Against the recorded rigidity results:
- IDEA-20260806-c5d183 (no lossy object on a prime-order group propagates deterministically under full translation except constant or injective) and KN-FIND-ffe1df Theorem C (exact sum-compatibility plus associativity forces a surjective homomorphism onto a group of order dividing N, impossible for prime N and M < N): both are non-existence statements for projections of a PRIME-order group. CA proposes no projection of G; it uses a homomorphism of the composite-order ambient group whose kernel is G. So it is not a recorded rigidity result in new notation. Conversely it is not a new arithmetic: pi_S is the homomorphic cofactor quotient that LEAD-ICB-cofactor-torsion-quotients (Sylow coprimality) shows carries no DLP information in G; here it is bookkeeping for which pairs cancel.
- IDEA-20260901-863e36 (propagation is a property of a projection paired with an operation group): CA's pair is the plain translation pair, with the quotient used only to count. No new operation group.
- KN-OPEN-020 (bounded-degree algebraic factor bases over F_p scoped out; open class: high-degree, implicit-membership, target-dependent descriptions): CA's base is a small-abscissa enumerated base (table membership), inside the scoped-out class; it makes no factor-base escape claim.
- Related recorded law in new notation: KN-FIND-007 with the denominator equal to the order of the group generated by the base (IDEA-20260829-c6e7a4), plus the doubling term.

## Prior-scout overlap (non-authoritative, same round)

`gate-arithmetic-statistics-Co-C3-Cofactor-coset-counting-law-E-K-G-B-B.md` in this scratchpad (a sibling scout, read here, its raw files not reused) reached the same law (E[K_G] = B(B-1+t)/|S|, 33/35 for the l=2 floor/crater, t from the volcano level, the same ledger precedents c6e7a4 and 21e7c4, the same verdict advances_lead on LEAD-STR-class-representative-ic-selection). CA is that candidate plus the arity-3 exact-occupancy extension for the P29/P37 panel and the 7,760-model validation. If the coordinator already has C3's verdict, CA's marginal novelty over it is the arity-3 / panel-deciding part, which is the part already pre-empted by the plan's Poisson null (item 5 above) and IDEA-20260830-21e7c4.

## Raw outputs (verbatim)

### lead_atlas.py --match run a1
```
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   11  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   11  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   10  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
    9  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
    8  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
    7  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
```

### lead_atlas.py --match run a2
```
   22  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   15  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   14  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   14  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   12  KR-IC-9e610d                                 known_result       Survey consensus (2016)
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
   12  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
```

### lead_atlas.py --match run a3
```
   14  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
   12  LEAD-ICE-linearization-excess-fb-prior       open_unexamined    Linearization excess as a factor-base design prior inside descent cells
   10  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    9  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    9  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
    8  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    8  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    7  LEAD-ICB-tau-horner-chain                    open_next_step     tau-Horner decomposition chain on Koblitz curves (R = tau^{m-1}P_1 + ... + P_m over one base)
```

### lead_atlas.py --match run a4
```
   18  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   13  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   11  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
```

### build_frontier_map.py --match run f1
```
KR-IC-955fd6  score=6  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-RHO-cb1c58  score=4  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-b0fcda  score=3  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
```

### build_frontier_map.py --match run f2
```
KR-IC-5931ee  score=15  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-9e610d  score=12  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=11  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-1fcdbc  score=10  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-e2d81b  score=9  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
```

### build_frontier_map.py --match run f3
```
KR-IC-5931ee  score=6  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-b0fcda  score=6  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-RHO-755e35  score=6  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-RHO-825bca  score=6  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-1fcdbc  score=5  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-cd0049  score=5  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
```

### build_frontier_map.py --match run f4
```
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=8  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-RHO-1c2928  score=8  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-791cb7  score=6  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-955fd6  score=6  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
```

### phrasings used (runs a1/f1, a2/f2, a3/f3, a4/f4)
```
1: exact cofactor torsion cancellation yield law for prime-abscissa base across volcano levels
2: why floor curves of a 2-isogeny volcano give fewer index calculus relations than crater curves
3: isogenous curves F_p-isomorphic prime-order subgroups mean per-target yield for every base of size B coverage or variance excess that grows with N
4: native factor base torsion H-component cancellation sum-set count distinct signed sums Poisson isogeny volcano level
```

### ledger index grep (ca-torsion-raw/lgrep.py output)
```
### GREP A volcano floor/crater yield | ALL: ['volcano|crater'] | ANY: ['floor|crater']
  [prop] IDEA-20260726-010 (2026-07-26, unverified) :: Write Delta = t^2 - 4p = f^2 * Delta_K. If |Delta_K| is small, E sits at the floor of a volcano whos
  [prop] IDEA-20260731-017 (2026-07-31, unverified) :: Let E_floor and E_crater be ordinary F_p-isogenous curves whose endomorphism rings differ by an inde
  [prop] IDEA-20260807-94f953 (2026-08-07, adaptation) :: (A) THE CARDINALITY FACT, AND THE DICHOTOMY IT FORCES. For an ordinary isogeny class over F_p with f
  [prop] IDEA-20260807-a2b59a (2026-08-07, novel) :: (A) THE FACT THE DESIGN EXPLOITS. For distinct primes ell_1, ell_2 dividing c, the coordinates v_{el
  [prop] IDEA-20260807-cbe8c1 (2026-08-07, adaptation) :: (A) THE EXACT CRITERION, DERIVED HERE. Let E/F_p be ordinary, t its trace, t^2 - 4p = c^2 D_K with D
  [prop] IDEA-20260808-28361d (2026-08-08, unverified) :: (A) THE TWO SIZES, PUT SIDE BY SIDE. For ordinary E/F_p with trace t, D = t^2 - 4p, and O = End_{F_p
  [prop] IDEA-20260808-621df3 (2026-08-08, successor_reanalysis) :: The G3 excursions above four in the prior volcano audit are caused by the declared B=10^6 norm cutof
  [prop] IDEA-20260811-22b6b8 (2026-08-11, adaptation) :: (A) THE T5 GATE, RESTATED AND THEN ANSWERED. DECOMPOSITION.md T5 admits a cost-minimising vertex onl
  [prop] IDEA-20260811-99cc67 (2026-08-11, adaptation) :: (A) THE OBJECT EXISTS AND IS UNIQUE IN THIS PROGRAM. Write N = #E(F_p) and t for the trace, so p = N
  [prop] IDEA-20260811-dcbea4 (2026-08-11, adaptation) :: (A) THE TWO-SIDED SIZE IDENTITY. For a CM point of discriminant D, the largest archimedean conjugate
  [prop] IDEA-20260812-c49409 (2026-08-12, adaptation) :: Let E/F_p be ordinary with prime N = #E(F_p), Delta = t^2 - 4p = f^2 * D_K with D_K the fundamental 
  [prop] IDEA-20260821-ad7c97 (2026-08-21, unverified) :: STATED AS FOUR SEPARABLE CLAIMS, THE FIRST THREE OF WHICH ARE DERIVATIONS COSTING NO COMPUTE AND THE
  [prop] IDEA-20260826-d61c49 (2026-08-26, unverified) :: (A) THE PROJECTION. Transport theorem T1 carries an ECDLP instance (E, P, Q, k) along any F_p-isogen
  [prop] IDEA-20260826-f412a0 (2026-08-26, unverified) :: THREE SEPARABLE CLAIMS. NO ATTACK IS PROPOSED, NO EXPONENT MOVES, AND NOTHING IS CLAIMED TO EXCEED T
  [prop] IDEA-20260828-f3c50e (2026-08-28, unverified) :: (A) THE OBJECT AND WHY IT IS NOT d61c49's OBJECT. IDEA-20260826-d61c49 tracks |Cl(O_{D_0})| = h(D_0)
  [prop] IDEA-20260829-882739 (2026-08-29, unverified) :: Let E/F_p be ordinary with j(E) = 0 and p congruent to 1 mod 3 (respectively j(E) = 1728 and p congr
  [prop] IDEA-20260901-2fb77b (2026-09-01, unverified) :: FIVE SEPARABLE CLAIMS. (A) AND (B) ARE DERIVATIONS. (C) IS THE PREDICTED PENALTY. (D) IS THE ONE MEA
  [prop] IDEA-20260901-48b364 (2026-09-01, unverified) :: FOUR SEPARABLE CLAIMS. (A) IS A DERIVATION. (B) IS AN EXPONENT. (C) IS THE HEURISTIC-CONDITIONAL DEN
  [prop] IDEA-20260901-c7e601 (2026-09-01, unverified) :: FIVE SEPARABLE CLAIMS. (A) AND (B) ARE DERIVATIONS COSTING NO COMPUTE. (C) IS THE COST STATEMENT. (D
  [prop] IDEA-20260922-1f9967 (2026-09-22, unverified) :: Representation class R1 of RQ-ECDLP-623a32 (summation coordinates, split into isotypic blocks), atta
  [prop] IDEA-20260930-39ad61 (2026-10-01, unverified) :: CEILING FIRST. No per-target exponent moves. The per-target online cost of the one-table-per-class a
  [prop] IDEA-20261003-e3ce5b (2026-10-03, unverified) :: Setting: ordinary E0/F_p with End(E0) = O_K, h(D0) = 1, D0 < -4, Frobenius discriminant t^2 - 4p = f
  [prop] IDEA-20261005-b4c2bf (2026-10-05, unverified) :: Let p be the least prime in the closed interval from 17 to 199 for which an ordinary 2-isogeny volca
  [prop] IDEA-20261006-52015b (2026-10-06, unverified) :: On one complete ordinary 2-isogeny volcano over a prime p in (300, 2000), with j-invariants 0 and 17
  [prop] IDEA-20261015-96ae0e (2026-10-15, adaptation) :: (A) The crater is E_d mod p for E_d the quadratic twist of a CM(-19) curve E_0/Q (j = -96^3, recalle
  [prop] IDEA-20261015-e0b5dd (2026-10-15, adaptation) :: (A) Frobenius is -1 on E[v] (pi + 1 = vw), so all v+1 subgroups of E[v] are F_p-rational kernels; ea
  [prop] IDEA-20261017-9b7e04 (2026-10-17, unverified) :: K=Q(sqrt(-D0)) small, p=pi*pibar split, 4p=t^2+D0 f^2. (1) The F_p-curves of trace t number H(t^2-4p
  [prop] IDEA-20261024-7be1c6 (2026-10-24, unverified) :: K = F_{q^n}, n prime >= 5, E/K ordinary with Frobenius pi, trace t. (a) Exact: the number of K-isomo
  [hypo] H-ALISO-028 (None, analyzed) :: Autolab package `iso_genus_filtered_crater_ancestor` (isogeny / supersingular / Kani) produces a sco
  [hypo] H-ALISO-029 (None, analyzed) :: Autolab package `iso_genus_filtered_crater_sweep` (isogeny / supersingular / Kani) produces a scoped
  [hypo] H-CANL-d4190b (2026-09-13, specified) :: Fix the exact count identity of IDEA-20260811-dcbea4 before any later-stage claim. Stage 0 asserts o
  [hypo] H-CMFB-7d4e1a (2026-10-16, specified) :: Let E be a crater-type curve (End = O_K, K = Q(sqrt(-19)), w = (1 + sqrt(-19))/2, w^2 - w + 5 = 0) o
  [hypo] H-CMFB-9b2eed (2026-10-15, specified) :: On prime-field curves y^2 = x^3 + A x + B over F_p of prime order N with 2^14 < p <= 2^25, in each o
  [hypo] H-ECDLP-3cf1d8 (2026-08-25, proposed) :: SCOPE, AND IT IS DELIBERATELY NARROWER THAN THE PARENT PROPOSAL. This hypothesis covers ARM S (struc
  [hypo] H-ECDLP-5bc40d (2026-09-13, specified) :: Fix the exact Aut-orbit partition identities of IDEA-20260829-8bde84 before any isogeny-walk sampler
  [hypo] H-ECTD-19017a (None, specified) :: Let E_floor and E_crater be ordinary F_p-isogenous curves whose endomorphism rings differ by an inde
  [hypo] H-ECTD-e88346 (None, approved) :: For the two specified ordinary prime-field crater/floor pairs with prime conductor steps 8209 and 13
  [hypo] H-ECTD-ffcb64 (None, approved) :: TEST BOUNDARY. One prime and three short-Weierstrass models over that prime. The prime is p = 41. Th
  [hypo] H-JINV-3a5637 (2026-09-13, specified) :: Fix the exact count identity of IDEA-20260828-f3c50e before any later-stage claim. Stage 0 asserts o
  [hypo] H-JINV-434c3e (2026-09-13, specified) :: Fix the exact count identity of IDEA-20260826-d61c49 before any later-stage claim. Stage 0 asserts o
  [hypo] H-VOLC-1fb326 (2026-09-13, specified) :: Fix the exact count identity of IDEA-20260901-48b364 before any later-stage claim. Stage 0 asserts o
  [hypo] H-VOLC-8cb396 (2026-09-13, specified) :: Fix the exact count identity of IDEA-20260826-f412a0 before any later-stage claim. Stage 0 asserts o
  -> hits: 42
### GREP B cofactor + factor base/abscissa | ALL: ['cofactor'] | ANY: ['factor.?base|abscissa|small.?x']
  [prop] IDEA-20260829-c6e7a4 (2026-08-29, unverified) :: (A) THE DENOMINATOR CORRECTION, DERIVED. KN-FIND-007 fixes the mean per-target decomposition yield a
  [prop] IDEA-20260922-8ac1ea (2026-09-22, unverified) :: R1 representation (field representation of the coordinates, in the FIPS reduction basis); the attack
  [prop] IDEA-20260926-ae8f0a (2026-09-26, unverified) :: CEILING FIRST. m = 2 at the toy cell where oracle A and rho dominate; sota_delta zero, no exponent m
  [prop] IDEA-20261001-5628bc (2026-10-02, unverified) :: SCOPE. ECC2K-130: E: y^2 + xy = x^3 + 1 (a = 0, b = 1) over F_2[z]/(z^131 + z^13 + z^2 + z + 1), #E 
  [prop] IDEA-20261017-3db2a8 (2026-10-17, unverified) :: SCOPE: derivation plus zero-compute arithmetic from the frozen paper and one toy check. No security 
  [hypo] H-BINSTD-336b2d (2026-10-01, approved) :: Let q = 2^16 and let k be one of 11, 13, 17, 19, 23, corresponding to the named curves c2pnb176v1, c
  [hypo] H-BINSTD-a45444 (2026-10-01, analyzed) :: SETTING. ECC2K-130: E: y^2+xy=x^3+1 over F_2^131 with #E = 4*l, l a 129-bit prime (KN-LIT-661e97). T
  [hypo] H-CERTBIN-151be9 (2026-10-02, approved) :: CLAIM (measurement / attempt-mix instrument; HOLD-X11; NO ATTACK). Setting: binary Koblitz-shaped cu
  [hypo] H-CERTBIN-6e6287 (2026-10-02, approved) :: CLAIM (cost-model measurement; HOLD-X1; NO ATTACK). Setting: binary fields F_{2^n}, n in {17,19,23,2
  [hypo] H-ECDLP-5b245d (2026-09-05, proposed) :: SCOPE: factor bases inside cofactor-1 prime-order subgroups at field_bits in {12, 16, 20, 24}: the i
  -> hits: 10
### GREP C 2-torsion yield | ALL: ['2-torsion|two-torsion|e\\[2\\]|full 2'] | ANY: ['yield|relation|decompos']
  [prop] IDEA-20260807-0ff796 (2026-08-07, adaptation) :: (A) THE OBJECT. Fix E/F_p: y^2 = f(x) = x^3 + a x + b, non-singular, and a target point R in E(F_p) 
  [prop] IDEA-20260906-86cd30 (2026-09-06, unverified) :: SETTING. E/F_p short Weierstrass with N = #E(F_p) an odd prime. There is no 2-torsion, so every on-c
  [prop] IDEA-20260915-3f1964 (2026-09-15, adaptation) :: Let E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, b != 0, and let x_1, x_2, x_3, x_R in F_q with 
  [prop] IDEA-20260920-0490f5 (2026-09-20, unverified) :: Galbraith's "larger group actions" slide asks whether groups bigger than (Z/4Z)^{m-1} x| S_m can act
  [prop] IDEA-20260921-457a46 (2026-09-21, unverified) :: A factor base chosen in the quotient coordinate u=x+1/x, together with an exact two-torsion lift rul
  [prop] IDEA-20261006-77b06b (2026-10-06, adaptation) :: Representation class R1, x-coordinates. The attack stage is the shape of the decomposition ideal, sc
  [prop] IDEA-20261006-aaf1a8 (2026-10-06, unverified) :: On a double-odd curve over F_{p'^5} with exactly one F_{p'^5}-rational 2-torsion point, the rank of 
  [hypo] H-GFPN-8aaf70 (2026-10-05, approved) :: Let p be in {7, 19, 59} and let E be y^2 = x^3 + x + 1 over F_p. The cubic has no root in F_p at the
  [hypo] H-GFPN-9a29be (2026-09-20, inconclusive) :: The EcGFp5 design note's "≥ 2^142" Gaudry floor is computed for the RAW descended n=5, m=5 system (i
  [hypo] H-GFPN-ce885c (2026-10-05, approved) :: Let q be 5, 7, or 11. Let L be F_q[z] modulo x^6 + x + 2 when q is 5 or 11, and modulo x^6 + 2 when 
  [hypo] H-GFPN-d48ae1 (2026-10-05, approved) :: Let p be in {7, 11, 19} and let E be y^2 = x^3 + x over F_p. For x in F_p with f(x) = x^3 + x nonzer
  -> hits: 11
### GREP D class-cancelling / cofactor class / denominator | ALL: ['class.?cancel|cofactor class|classes? cancel|exact ceiling|denominator|n0\\b|\\[r\\]p'] | ANY: []
  [prop] IDEA-20260805-a25f11 (2026-08-05, unverified) :: For a prime-field Semaev factor base of B x-coordinates on E(F_p) with N = #E(F_p), the mean number 
  [prop] IDEA-20260805-d38a8c (2026-08-05, unverified) :: Every measurement this goal has made is an ABSOLUTE syzygy count, and the goal's decision target ("i
  [prop] IDEA-20260807-4fc635 (2026-08-07, adaptation) :: (A) THE CONTROL THIS LANE CANNOT DO WITHOUT, STATED AS AN OBJECT RATHER THAN AS A CAVEAT. Every L11 
  [prop] IDEA-20260808-2df781 (2026-08-08, unverified) :: FrodoKEM samples chi from a tabulated CDF over a fixed number of uniform random bits, so the realise
  [prop] IDEA-20260816-405086 (2026-08-16, unverified) :: (A) WHY THE RAW RATIO IS THE WRONG CURRENCY FOR A GROWTH QUESTION. This program's central factor-bas
  [prop] IDEA-20260816-6bce56 (2026-08-16, unverified) :: (A) A REPRESENTATION CHOICE CREATES AN OBSERVABLE. Incomplete addition formulas -- Jacobian addition
  [prop] IDEA-20260816-79af89 (2026-08-16, unverified) :: (A) Everything in the nrd-PIP lane operates on the public Gram matrix G, and every downstream record
  [prop] IDEA-20260816-839444 (2026-08-16, unverified) :: (A) H-ARGON-ef2f0b's central prediction is a ratio rho = |S*_real| / |S*_unif|, where the denominato
  [prop] IDEA-20260816-86a78d (2026-08-16, unverified) :: (A) H-PMA-001 predicts nonvacuous_obstruction_count at least 1 and false_obstruction_count exactly 0
  [prop] IDEA-20260816-f2575b (2026-08-16, unverified) :: (A) KN-OPEN-028 is closed_all_questions_answered and stays closed; its Q1 closure records that the a
  [prop] IDEA-20260829-02418a (2026-08-29, unverified) :: Let E/Q be a specialisation E_{t0} of a non-isotrivial family E/Q(t) whose Mordell-Weil group over Q
  [prop] IDEA-20260829-a03f74 (2026-08-29, unverified) :: Write R for GF(2)[x]/(x^32 + 1) with a 32-bit word read as a polynomial and the one-bit left rotatio
  [prop] IDEA-20260829-bc9cc5 (2026-08-29, unverified) :: (A) THE STRUCTURAL ASYMMETRY. A NIST security-category verdict is the sign of a difference: log2(bes
  [prop] IDEA-20260829-c6e7a4 (2026-08-29, unverified) :: (A) THE DENOMINATOR CORRECTION, DERIVED. KN-FIND-007 fixes the mean per-target decomposition yield a
  [prop] IDEA-20260829-d81e3b (2026-08-29, unverified) :: Let C be the SHA-1 linearized message-expansion code, the set of 80-tuples of 32-bit words with W_i 
  [prop] IDEA-20260829-f2ffc1 (2026-08-29, unverified) :: Let C be the SHA-1 linearized message-expansion code, i.e. the set of 80-tuples of 32-bit words sati
  [prop] IDEA-20260830-1f2b8b (2026-08-30, unverified) :: EV-ENDO-10109d records a replicated, density-independent within-class over-dispersion of the m = 3 d
  [prop] IDEA-20260905-0cc259 (2026-09-05, unverified) :: For two rationally equivalent curve presentations, a favorable low-degree profile may come from omit
  [prop] IDEA-20260905-3c4579 (2026-09-05, unverified) :: For two rationally equivalent curve presentations, a favorable low-degree profile may come from omit
  [prop] IDEA-20260905-7d14f8 (2026-09-05, unverified) :: A finite atlas of rational coordinate maps with compatible local completions can certify that a conv
  [prop] IDEA-20260905-8e4994 (2026-09-05, unverified) :: A bounded polynomial certificate can prove that a declared set of addition formulas covers every val
  [prop] IDEA-20260905-dd547f (2026-09-05, unverified) :: For two rationally equivalent curve presentations, a favorable low-degree profile may come from omit
  [prop] IDEA-20260906-76f29a (2026-09-06, unverified) :: R3 representation at the function-field section-incidence stage. At equal total coefficient budget, 
  [prop] IDEA-20260906-c9f6e0 (2026-09-06, unverified) :: For a block of k simultaneous independent affine normalizations inside a fixed CSIDH action circuit,
  [prop] IDEA-20260920-204828 (2026-09-20, unverified) :: In the affine rho step the denominator d = x_R - x_T in F_{p^5} can be inverted as d^{-1} = c / N(d)
  [prop] IDEA-20260926-3cc0b8 (2026-09-26, unverified) :: Representation class R1 of RQ-ECDLP-623a32 (the relation matrix and log vector over F_r); the attack
  [prop] IDEA-20261005-8276a8 (2026-10-05, adaptation) :: Let p=19. Let C_cm be y^2=x^3+1 over Q with integral point P_cm=(2,3), C_n1 be y^2=x^3+x+1 over Q wi
  [prop] IDEA-20261006-76e247 (2026-10-06, unverified) :: Among primes p with 29 ≤ p ≤ 149 and p ≡ 1 (mod 4), let N0 be the number of such primes for which th
  [prop] IDEA-20261006-8aedbe (2026-10-06, unverified) :: Over F_41, let E_d be the affine Edwards curve x^2 + y^2 = 1 + d x^2 y^2. Let d_ns be the smallest d
  [prop] IDEA-20261006-9deda5 (2026-10-06, unverified) :: Let E_cm be the integer model y^2 = x^3 + 1 and let E_gen be the integer model y^2 = x^3 + x + 1. Re
  [prop] IDEA-20261007-9711d4 (2026-10-07, unverified) :: Let E be the lexicographically first nonsingular ordinary short-Weierstrass curve y^2 = x^3 + a x + 
  [prop] IDEA-20261007-a9c4c1 (2026-10-07, unverified) :: Given the certified curve and twist cofactor slices as inputs (not re-proposed), the defensive costs
  [prop] IDEA-20261014-25b2b6 (2026-10-14, unverified) :: Primitive fi*omega transports with denominator fj/gcd(fi,fj). Bidirectional denominators identify ra
  [prop] IDEA-20261015-c6f017 (2026-10-15, unverified) :: (1) A three-limb signed-Frobenius walk at n=131 (polynomial basis with CLMUL, table-driven basis cha
  [hypo] H-BINSTD-6013c8 (2026-10-03, approved) :: The surplus multipliers are 1, 3/2, and 2. On the denominator 2 their numerators are 2, 3, and 4. Th
  [hypo] H-BINSTD-637cbf (2026-10-03, approved) :: The surplus multipliers are 1, 5/4, 3/2, and 2. On the denominator 4 their numerators are 4, 5, 6, a
  [hypo] H-CANL-b9033d (2026-10-07, specified) :: Let E_cm be the integer model y^2 = x^3 + 1 and let E_gen be the integer model y^2 = x^3 + x + 1. Re
  [hypo] H-CRYPTO-b2c203 (2026-08-25, proposed) :: A reproducible group-operation-equivalent (GOE) cost ruler can be installed at secp256k1-adjacent pa
  [hypo] H-DIFFP-718e3b (2026-09-13, specified) :: Fix the exact count identity of IDEA-20260829-a03f74 before any later-stage claim. Stage 0 asserts o
  [hypo] H-DREG-575e48 (2026-10-02, approved) :: For y^2 = x^3 + A x + B, away from characteristics 2 and 3, the invariant is 1728 times 4 A^3 over 4
  [hypo] H-ECDLP-954cae (2026-10-03, approved) :: The proposal writes the window endpoints 3/4 and 1/2. Clearing the common denominator 4 gives the nu
  [hypo] H-ECDLP-fe2646 (2026-10-03, approved) :: The proposal writes the thresholds 1 and 1/2. Clearing the common denominator 2 gives the values 2 a
  [hypo] H-ENDO-3ecfa3 (2026-10-12, proposed) :: Exact conjugation of a primitive CM multiplication matrix by an integer isogeny matrix has least den
  [hypo] H-ENDO-58fc5c (None, specified) :: Over Q with the standard grading and window D = 4, the denominator-torsion module T = (I : d^infinit
  [hypo] H-GFPN-a170eb (2026-10-02, approved) :: The factor 1 + 1/(2r) at r = 32 is 65/64. It exceeds 97/100 by the cross gap 292 and falls short of 
  [hypo] H-ICLIFT-d31664 (None, proposed) :: SCOPE: the frozen EXP-FB3-001 counting convention -- unsigned m-multisets of factor-base elements, t
  [hypo] H-ICPERF-888b38 (2026-10-02, approved) :: Three halves exceeds 23/20 by 14 on the denominator 40, which is 7/20. Six fifths exceeds 23/20 by 5
  [hypo] H-SSI-fbe68d (None, proposed) :: For every accepted CEST-PKE key whose complete evaluable End(E) witness W makes CanonicalBoundedEnd 
  -> hits: 48
### GREP E conservation + isogeny | ALL: ['conservation|mean yield|binom'] | ANY: ['isogen|volcano|conductor']
  [prop] IDEA-20260807-94f953 (2026-08-07, adaptation) :: (A) THE CARDINALITY FACT, AND THE DICHOTOMY IT FORCES. For an ordinary isogeny class over F_p with f
  [prop] IDEA-20260808-621df3 (2026-08-08, successor_reanalysis) :: The G3 excursions above four in the prior volcano audit are caused by the declared B=10^6 norm cutof
  [prop] IDEA-20261015-e0b5dd (2026-10-15, adaptation) :: (A) Frobenius is -1 on E[v] (pi + 1 = vw), so all v+1 subgroups of E[v] are F_p-rational kernels; ea
  -> hits: 3
### GREP F distinct sums / Poisson / coverage | ALL: ['distinct|poisson|sum.?set'] | ANY: ['coverage|occupancy|yield']
  [prop] IDEA-20260727-002 (2026-07-27, known) :: The H-IC-001 result supported by DEC-20260726-005 (T_desc / sqrt(N) decreasing monotonically by 300x
  [prop] IDEA-20260805-a7a716 (2026-08-05, unverified) :: Two derivable statements about the EXP-FB3-001 measurement apparatus, neither of which requires a ne
  [prop] IDEA-20260808-b16d04 (2026-08-08, unverified) :: Conditionally on H1-H5, a fixed public target-independent signed-y antisymmetric partition with root
  [prop] IDEA-20260809-1143bf (2026-08-09, unverified) :: A prime-order group encoding with a canonical serialization is the object this whole divergence clas
  [prop] IDEA-20260809-c8027c (2026-08-09, unverified) :: For a combiner that hashes only the two shared secrets, an adversary who generates its own post-quan
  [prop] IDEA-20260813-945a67 (2026-08-13, unverified) :: Under a frozen single-fault model for stateless SLH-DSA address handling, every fault that makes two
  [prop] IDEA-20260816-c50b84 (2026-08-16, unverified) :: (A) Every measurement contract in this bucket rests on the same instrument: complete enumeration of 
  [prop] IDEA-20260828-033cb3 (2026-08-28, unverified) :: (A) THE TWO OPEN THREADS THIS RECORD CONNECTS. IDEA-20260821-121612 measured whether a FIXED compari
  [prop] IDEA-20260830-c5c614 (2026-08-30, unverified) :: (A) WHAT IS ALREADY CLOSED, SO THAT THIS IS NOT MISTAKEN FOR IT. KN-FIND-007 fixes the mean per-targ
  [prop] IDEA-20260905-be63be (2026-09-05, unverified) :: For a complete automorphism-orbit factor base, stabilizer-weighted tuple-target incidence and its se
  [prop] IDEA-20260906-3d57e8 (2026-09-06, unverified) :: If a named protocol supplies D-d+1 suitably distinct shifted degree-D source-group tokens with the s
  [prop] IDEA-20260930-4ebd85 (2026-09-30, unverified) :: For a frozen explicit point set B of size m on the prime-order subgroup of a toy binary Koblitz curv
  [prop] IDEA-20261006-5bfbcf (2026-10-06, speculative) :: Representation R1, attack stage relation yield. On E: y^2 = x^3 + x + 4 over F_61, let F be the four
  [prop] IDEA-20261009-57140c (2026-10-09, unverified) :: (i) the relation yield ratio R(H) = #trace relations from K-points of height <= H divided by #distin
  [prop] IDEA-20261017-3db2a8 (2026-10-17, unverified) :: SCOPE: derivation plus zero-compute arithmetic from the frozen paper and one toy check. No security 
  [prop] IDEA-20261018-5fa71b (2026-10-18, unverified) :: BRIDGE. c(R) = h-sum count vector of a base, mu its mean, Delta = Var/mu. (I1) PFDR kappa_h (IDEA-20
  [hypo] H-CMFB-9b2eed (2026-10-15, specified) :: On prime-field curves y^2 = x^3 + A x + B over F_p of prime order N with 2^14 < p <= 2^25, in each o
  [hypo] H-FROB-855915 (None, approved) :: On the frozen toy Koblitz cells of EXP-FROB-5e15ed, exact ordered-tuple enumeration gives a pooled y
  [hypo] H-ICEX-7af505 (None, proposed) :: (A) THE EXACT IDENTITY, WHICH IS A PROOF AND NOT AN ARM. KN-FIND-007 states VERBATIM that for a fact
  [hypo] H-KIC-9416d9 (None, proposed) :: Under normative completion SHA256=1419bc2107601476c4fd44f90d67475ec15e98eef68a35888df9abfaed0aa3e5, 
  [hypo] H-KIC-baee02 (None, specified) :: For the lexicographic bases at n=7 with m in {8, 12} and at n=11 with m in {12, 16}, the absolute re
  [hypo] H-LHW-e54b1b (2026-10-03, approved) :: CLAIM (heuristic_validation / integer sumset instrument; NO ATTACK; NO EXPONENT MOVE). Let W = W(m,w
  [hypo] H-PFDR-1b2386 (2026-09-04, proposed) :: (A) WHAT IS ALREADY CLOSED, SO THIS IS NOT MISTAKEN FOR IT. The mean per-target decomposition yield 
  -> hits: 23
### GREP G projected/subgroup base | ALL: ['project|subgroup'] | ANY: ['factor.?base|abscissa']
  [prop] IDEA-20260727-001 (2026-07-27, known) :: For the j=0 GLV instances of EXP-STR-002, the measured O(1) displacement rank of the phi-invariant r
  [prop] IDEA-20260731-010 (2026-07-31, unverified) :: On a fixed prime-field curve with prime-order subgroup order N, collecting one factor-base relation 
  [prop] IDEA-20260731-012 (2026-07-31, adaptation) :: Let E/F_p carry a prime-order subgroup G of order N, let F be a factor base of size B = N^beta, and 
  [prop] IDEA-20260731-015 (2026-07-31, adaptation) :: Let E/F_p carry a prime-order subgroup G = <P> of order N, and let the factor base be chosen as F = 
  [prop] IDEA-20260801-021 (2026-08-01, adaptation) :: Let E/F_p be a nonsingular geometrically irreducible plane elliptic curve, let G <= E(F_p) have prim
  [prop] IDEA-20260807-5dfe4a (2026-08-07, known) :: (A) THE OBSTRUCTION, NAMED. Let G = <P> have PRIME order N, let phi be any endomorphism of E defined
  [prop] IDEA-20260807-d329e2 (2026-08-07, adaptation) :: (A) THE CONSTRUCTION. On an ordinary curve with F_p-rational Aut of order 2r (r = 3 for j=0 with p c
  [prop] IDEA-20260808-9ef88c (2026-08-08, screened) :: Take B | p-1 and V = c * mu_B, the coset of the order-B multiplicative subgroup. Then f_V(x) = x^B -
  [prop] IDEA-20260808-afe4ce (2026-08-08, screened) :: Let V subset F_p, |V| = B, and let J = I(V) subset F_p[x] be its vanishing ideal, generated by f_V o
  [prop] IDEA-20260815-90f638 (2026-08-15, adaptation) :: The program records a confirmed bug in its shared Semaev implementation and a factor-base sampler th
  [prop] IDEA-20260815-f9e978 (2026-08-15, unverified) :: GOAL-RELN-001 audits P(decomp) versus factor-base size. Every formulation in the lane treats P(decom
  [prop] IDEA-20260816-0027ac (2026-08-16, unverified) :: (A) The committed EXP-ALPF-011 table varies representation (x-ring baseline, e-ring elementary-symme
  [prop] IDEA-20260816-6a2bea (2026-08-16, unverified) :: (A) H-ALR-002 records that exactly 2c weighted source moments recover a degree-c candidate locator b
  [prop] IDEA-20260816-f50ee4 (2026-08-16, unverified) :: (A) KN-OPEN-020 is currently a sentence, not an instrument. It asks whether every algebraically desc
  [prop] IDEA-20260826-4bc5d2 (2026-08-26, unverified) :: (A) THE FUNCTIONAL. Fix a window [0, B) in F_p and let S_B(E) = #{ P in G \ {O} : lift x(P) to [0, p
  [prop] IDEA-20260829-57b1eb (2026-08-29, unverified) :: (A) THE OBJECT. Fix an ordinary curve E over F_{2^n}, a factor base of B points whose x-coordinates 
  [prop] IDEA-20260829-b5a2c8 (2026-08-29, unverified) :: (A) THE ACCOUNTING. Let G have prime order N, let the factor base have size B, let D be the cost in 
  [prop] IDEA-20260829-c6e7a4 (2026-08-29, unverified) :: (A) THE DENOMINATOR CORRECTION, DERIVED. KN-FIND-007 fixes the mean per-target decomposition yield a
  [prop] IDEA-20260830-21e7c4 (2026-08-30, unverified) :: (A) THE OBJECT IS DETERMINISTIC. For a factor base V of B x-coordinates, the signed point set W = V 
  [prop] IDEA-20260830-2993a4 (2026-08-30, unverified) :: (A) THE OBSERVABLE. For a point-decomposition pipeline at arity m over a factor base of size B, defi
  [prop] IDEA-20260830-4ab603 (2026-08-30, unverified) :: (A) THE COUPLING THAT THE TWO-TERM MODEL LEAVES OUT. In the charge T(B) = m!*N*D/(2^m*B^{m-1}) + c_L
  [prop] IDEA-20260830-f2e5b7 (2026-08-30, unverified) :: (A) THE OMITTED CHANNEL, STATED AS A SPECIFIC DEFECT IN A LIVE PROPOSAL. At arity m = 2 over a prime
  [prop] IDEA-20260902-2327a5 (2026-09-02, unverified) :: Setting: E/F_p ordinary, p > 3, G a subgroup of prime order N, factor base V a set of B on-curve x-c
  [prop] IDEA-20260902-701458 (2026-09-02, unverified) :: Setting: E/F_p ordinary, p > 3, G a subgroup of E(F_p) of prime order N, x the x-coordinate map, 2-t
  [prop] IDEA-20260903-e0a3e8 (2026-09-03, unverified) :: Setting as in IDEA-20260808-486ae2: E/F_p, window W = [0, B) on the x-line, factor base V = {R : x(R
  [prop] IDEA-20260905-5a1ea2 (2026-09-05, unverified) :: (A) THE OBJECT. For a factor base F of size m inside a prime-order subgroup G of E(F_p), let H_F(x) 
  [prop] IDEA-20260905-a94b5f (2026-09-05, unverified) :: SCOPE: binary pdp CNF and CNF-XOR models at m in {3,4}, l in 4..9, three factor-base families - gene
  [prop] IDEA-20260909-4c5ee9 (2026-09-09, unverified) :: An exact DLP-free residual label space of size O(q^{1/2-epsilon}), or a nonlinear gauge-invariant pr
  [prop] IDEA-20260913-04fb8c (2026-09-13, unverified) :: Let E/F_p be ordinary with prime group order n, P a generator, and lambda in (Z/n)^* of large multip
  [prop] IDEA-20260913-8138a0 (2026-09-13, adaptation) :: SCOPE. Standalone mathematical instances and derivations from Semaev 2015 (KN-LIT-fa346d, frozen at 
  [prop] IDEA-20260913-cedd2f (2026-09-13, speculative) :: Let E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, and let Tr be the absolute trace F_q -> F_2. Tw
  [prop] IDEA-20260921-0d2a43 (2026-09-21, unverified) :: Exact backward support clauses derived from a target-independent point-pair sum table may reject par
  [prop] IDEA-20260921-da1896 (2026-09-21, unverified) :: REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): the
  [prop] IDEA-20260922-6cf862 (2026-09-22, unverified) :: SETTING. The five composite-degree ANSI X9.62 binary curves are subfield curves E/F_q with q = 2^16,
  [prop] IDEA-20260922-845a77 (2026-09-22, unverified) :: Search heuristic 3 (agents/idea-generator.md) asks, for any bottleneck search, whether the target sp
  [prop] IDEA-20260922-d11575 (2026-09-22, known) :: Let E be any of c2pnb176v1, c2pnb208w1, c2pnb272w1, c2pnb304w1, c2pnb368w1, so (audit, analysis/bins
  [prop] IDEA-20260926-d06324 (2026-09-26, unverified) :: CEILING FIRST. No cost claim, no exponent, no attack. Representation class R1 of RQ-ECDLP-623a32 (th
  [prop] IDEA-20260926-d1adfc (2026-09-26, unverified) :: CEILING FIRST. No exponent, no attack. Representation R1; the attack stage is the PER-ATTEMPT DECOMP
  [prop] IDEA-20260926-dacb83 (2026-09-26, unverified) :: CEILING FIRST. No exponent, no attack; a cost-model column. Representation R1; the attack stages cha
  [prop] IDEA-20260930-bbef7f (2026-09-30, unverified) :: On the prime-degree binary Koblitz curves at n=11 and n=23, with the factor base equal to the subgro
  [prop] IDEA-20261001-39014f (2026-10-01, unverified) :: SETTING. E: y^2 + xy = x^3 + a x^2 + b over F_q, q = 2^n, b != 0; Tr: F_q -> F_2 the absolute trace;
  [prop] IDEA-20261001-5628bc (2026-10-02, unverified) :: SCOPE. ECC2K-130: E: y^2 + xy = x^3 + 1 (a = 0, b = 1) over F_2[z]/(z^131 + z^13 + z^2 + z + 1), #E 
  [prop] IDEA-20261002-3722ca (2026-10-02, unverified) :: On a generic prime-order short-Weierstrass curve E/F_p, represent each candidate abscissa by its dis
  [prop] IDEA-20261002-6e6ce8 (2026-10-02, unverified) :: On a generic prime-order short-Weierstrass curve over F_p, let H_0 be a fixed public subgroup of F_p
  [prop] IDEA-20261002-760272 (2026-10-02, unverified) :: On prime-order short-Weierstrass curves over the same toy prime, one with j = 0 and one with generic
  [prop] IDEA-20261002-e2a340 (2026-10-02, unverified) :: On a generic prime-order short-Weierstrass curve over F_p, index the implicit base H (abscissae in a
  [prop] IDEA-20261004-31991f (2026-10-04, adaptation) :: Setting: q odd, K = F_{q^n}, L = F_{q^{2n}}, sigma the generator of Gal(L/K), E: y^2 = f(x) over K w
  [prop] IDEA-20261006-4e827a (2026-10-06, unverified) :: On the first ordinary short-Weierstrass curve over F_73, with m = 3, thirty-six targets from the pri
  [prop] IDEA-20261006-6c27fc (2026-10-06, unverified) :: On the first ordinary short-Weierstrass curve over F_17, with m = 3 and one factor base of B = 4 x-c
  [prop] IDEA-20261006-8bae3b (2026-10-06, unverified) :: On the first ordinary short-Weierstrass curve over F_37, with m = 3, one factor base of B = 5 x-coor
  [prop] IDEA-20261006-b6b4ce (2026-10-06, unverified) :: On the first ordinary prime-field curve E with a rational 2-torsion point, prime p in [211, 500), j 
  [prop] IDEA-20261007-611573 (2026-10-07, unverified) :: On an ordinary prime-order subgroup of size N in (2^{10}, 2^{12}), let F be the ceil(N^{1/3}) subgro
  [prop] IDEA-20261015-9defe9 (2026-10-15, unverified) :: R1 relation-solving comparison: dense versus Newton-target shifted lattices must yield achieved norm
  [prop] IDEA-20261017-3db2a8 (2026-10-17, unverified) :: SCOPE: derivation plus zero-compute arithmetic from the frozen paper and one toy check. No security 
  [prop] IDEA-20261018-b90b0c (2026-10-18, unverified) :: Two bookkeeping defects are bounded. (a) Re-running the 21 archived runs touched by the shared harne
  [hypo] H-BINSTD-336b2d (2026-10-01, approved) :: Let q = 2^16 and let k be one of 11, 13, 17, 19, 23, corresponding to the named curves c2pnb176v1, c
  [hypo] H-BINSTD-4a07ff (2026-10-01, analyzed) :: SETTING. ECC2K-130: E: y^2 + xy = x^3 + 1 over F_{2^131}, order 4*l with l a 129-bit prime (KN-LIT-6
  [hypo] H-BINSTD-a45444 (2026-10-01, analyzed) :: SETTING. ECC2K-130: E: y^2+xy=x^3+1 over F_2^131 with #E = 4*l, l a 129-bit prime (KN-LIT-661e97). T
  [hypo] H-BINSTD-f379d5 (2026-09-30, approved) :: SETTING. The five composite-degree ANSI X9.62 binary curves are subfield curves E/F_q with q = 2^16,
  [hypo] H-CERTBIN-6e6287 (2026-10-02, approved) :: CLAIM (cost-model measurement; HOLD-X1; NO ATTACK). Setting: binary fields F_{2^n}, n in {17,19,23,2
  [hypo] H-DS-001 (None, analyzed) :: For prime-field Semaev index calculus at arity m in {4,5} with factor-base size B in {64,128,256} on
  [hypo] H-ECDLP-5b245d (2026-09-05, proposed) :: SCOPE: factor bases inside cofactor-1 prime-order subgroups at field_bits in {12, 16, 20, 24}: the i
  [hypo] H-ECDLP-79fa89 (None, proposed) :: TEST BOUNDARY FIRST. Toy scale throughout, p at most 6007, factor bases of at most 22 x-coordinates,
  [hypo] H-ECDLP-a4c9c1 (None, proposed) :: Formalises IDEA-20260731-015. For a prime-field curve E/F_p with a prime-order subgroup G = <P> of o
  [hypo] H-ECDLP-f79c89 (None, proposed) :: TEST BOUNDARY FIRST. This is an INSTRUMENT AND BOOKKEEPING AUDIT of two factor-base constructions in
  [hypo] H-ICEX-6f3e4b (None, proposed) :: (A) THE COUPLING THE TWO-TERM MODEL LEAVES OUT. In a charge of the form T(B) = m! N D / (2^m B^{m-1}
  [hypo] H-ICEX-7af505 (None, proposed) :: (A) THE EXACT IDENTITY, WHICH IS A PROOF AND NOT AN ARM. KN-FIND-007 states VERBATIM that for a fact
  [hypo] H-ICEX-c273c2 (2026-09-04, proposed) :: THE DECOMPOSITION PROBABILITY IS NOT A PROBABILITY TO BE ESTIMATED. For a factor base V of size B, i
  [hypo] H-ICEX-f1109f (None, proposed) :: Let F be a public coordinate-defined factor base in the prime-order subgroup G = <P> of a toy curve,
  [hypo] H-ICI-063e91 (None, weakened) :: For a random ordinary prime-field curve E/F_p with prime-order subgroup G of order N, and a Semaev i
  [hypo] H-PFDR-064546 (2026-09-04, proposed) :: (A) THE ACCOUNTING. Let G have prime order N, the factor base have size B, D be the cost in group op
  [hypo] H-PFDR-8a4f44 (2026-09-04, proposed) :: THE SAVING A CHARACTER-SUM BOUND WOULD NEED IN ORDER TO CERTIFY A MULTIPLICATIVE-SUBGROUP FACTOR BAS
  [hypo] H-RELN-a44c18 (2026-08-25, proposed) :: SCOPE. The frozen interface of the bounded-degree algebraic factor-base theorem (ideas/artifacts/IDE
  -> hits: 73
```
