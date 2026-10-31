# Gate N1-N4: C3 "Cofactor-coset counting law E[K_G] = B(B-1+t)/|S|" (field: arithmetic statistics)

Scout: novelty gates only. Nothing inside the repositories was edited. Numbers marked "scout-check" were produced here from existing repo data (script and output under `_c3_raw/check_closed_form.{py,out}`); numbers marked "candidate-reported" were NOT reproduced here.

## VERDICT: advances_lead (lead = LEAD-STR-class-representative-ic-selection, open_next_step). Novelty is narrow.

What is already in the program (so not new):
1. The mechanism "volcano-level, model and horizontal IC-yield effects are cofactor-class effects of the small-abscissa base" is E3a (`crypto: research/generator_effect_ic_20261019/README.md`, retrieved): G1-G4 pass, slope 1.064 [1.040, 1.090], horizontal tau 0.34%, coordinate tau 0.19%, pooled l=2 contrast 99% explained by N0. The atlas row of the lead does not cite E3a (its evidence list and best_measured predate it), so the row is stale on this point.
2. The leading-order law "a subgroup-scoped base beats a full-curve base by the cofactor h in mean yield; the denominator is the order of the group the sums live in" is ledger IDEA-20260829-c6e7a4 (proposed 2026-08-29; children H-ECDLP-f79c89 proposed, EXP-ECDLP-933c10 draft, i.e. never run per the index). Its P1 says "EXACTLY h", band 5%.
3. "P(decomp) is the integer ratio |mW cap H|/|H|, computed exactly" is IDEA-20260830-21e7c4; it is implemented as `exact_decomposition_ceiling` (N0) in E3a.
4. E3b's own PLAN (research/generator_effect_ic_20261019/PLAN.md, section E3b) already registers arms prime-abscissa / subgroup=filter / subgroup=project at equal B, and predicts filter/current = N0(filter)/N0(current), "about h for evenly spread classes"; at h = 1 arms coincide (same digest, ratio 1.000).

What is new (not found in atlas, KRMAP, ledger index, or E3a/PLAN text):
a. The finite-B closed form with the diagonal (doubling) term: E[K_G] = B(B-1+t)/|S|, t = #E(F_p)[2], with N0 = 2*K_G + B. Relative to c6e7a4's leading-order "exactly h", the K_G-ratio is hB/(B-1+t) = 3.657 (h=4,t=4), 3.879 (h=4,t=2), 10.971 (h=12,t=4); it equals h exactly when t = 1 (odd cofactor) and falls below h by the factor B/(B-1+t): 3.0% for t = 2, 8.6% for t = 4 at B = 32. CONDITIONAL: whether that leaves c6e7a4's pre-registered 5% band (t = 4 would; t = 2 would not) depends on c6e7a4's multiset convention (2^m*binom(B+m-1,m) with a uniform 1/h weight for the diagonal, which is exactly the approximation the t-term corrects); I did not reconcile the two conventions beyond that. (Arithmetic checked here.)
b. Attribution of the l=2 floor/crater N0 difference to t: K_G ratio (B+1)/(B+3) = 33/35 = 0.9429 (arithmetic checked here). The Kohel/Miret level-to-2-torsion link is scout-checked on this dataset: in all three l=2 class files (every curve, not only the 800 workloads) level 3 (the floor, depth 3) has t = 2 on every curve and levels 0-2 have t = 4 on every curve, no exception; in all three l=3 class files t = 1 at every level (_c3_raw/check_level_t.out). All l=2 workloads have h = 4. Workload N0 means: floor cells 559.5 / 557.1 / 555.9 versus 560.0 predicted (2B(B-1+2)/4 + B); non-floor cells 581-598 versus 592.0 predicted (small cells, n = 4-48). E3a says the contrast is "explained by N0" but not why N0 differs; the v2.1 README (retrieved) says "the cause of the l = 2 effect stays open" after the "l-power torsion changes between levels" contrast failed for l = 3; C3 is consistent with that failure because only 2-torsion enters K_G and t = 1 at every l=3 level. E3a says the contrast is "explained by N0" but not why N0 differs; the v2.1 README (retrieved) says "the cause of the l = 2 effect stays open" after the "l-power torsion changes between levels" contrast failed for l = 3; C3 is consistent with that failure because only 2-torsion enters K_G.
c. The proposed closure wording (closed_obstructed, proof) for the lead.

scout-check (existing data, no yields read): for the 800 E3a workloads (n0.json joined to the volcano class curve files for n1,n2 -> t), N0 is an integer with N0-B even on 800/800 rows; h = 1 (l3-ramified, 128 rows): N0 = 2080 = 2B^2 + B on every row; cell means of N0 match 2*B(B-1+t)/h + B within |z| < 1.4 in all five (class family, h, t) cells (the table below uses K_hat = (N0-B)/2, i.e. it is the same one comparison written in K_G units): (l2,h4,t2) 262.7 vs 264.0, z -0.95; (l2,h4,t4) 278.4 vs 280.0, z -1.31; (l3,h5,t1) 204.2 vs 204.8, z -0.68; (l3,h7,t1) 146.9 vs 146.3, z +0.52; (l3,h1,t1) exact. The per-row identity N0 = 2*K_G + B was NOT checked here (K_G is not computed per row by E3a's census; I verified only integrality, parity, the exact h = 1 value and cell-mean agreement). This does not test yield ~ N0 (that is E3a G1, already passed) nor the E3b predictions.
Slope identity (scout-check, reproduces a candidate-reported number): if yield is proportional to 2*K_G = N0 - B (the B multisets {P_i,-P_i} all sum to O, one non-random target, so they cannot produce relations for random targets), the implied OLS slope of ln yield on ln(N0/r) over the 800 workloads is 1.0442 (_c3_raw/check_slope_ratio.out), the candidate's value; E3a measured OLS 1.054 (WLS 1.064 [1.040, 1.090]). This is consistent with, not a test of, yield ~ N0 - B; it needs yields, which I did not read.
Design caveat found while checking (affects the pre-registered E3b prediction, not the verdict): the candidate's x3.66 / x3.88 / x10.97 are ratios of 2*K_G. The E3b PLAN states the prediction as N0(filter)/N0(current), and the N0 ratios at B = 32 are 3.514 (h4,t4), 3.714 (h4,t2), 9.512 (h12,t4). The two conventions differ by 4.1%, 4.5% and 15.3%, so the candidate's "+-10%" tolerance would be met under one convention and missed at h = 12 under the other. E3b should pre-register which of N0 or N0 - B is the denominator (E3a's slope 1.054 vs 1 favours N0 - B, but that is a read of E3a, not a test).

Not reproduced here (candidate-reported): the 7,760-curve-model l=2 geometric mean 0.9428 vs measured 0.9417; l=3 1.0017 vs 1.0062; l3-s1011 1.019 vs 1.025; vertex slope 0.954 / corr 0.665; chi2/df 0.935-1.088 (all of these use measured yields, which I did not read). The E3a slope value 1.0442 is reproduced above (as an implied slope; the comparison to measured yields is E3a's).

Consequence for the named bottleneck B3: none. All Table B rows are prime order (h = 1, t = 1: K_G = B^2, arms identical), so C3 is a closure/explanation of a side lead, not a path on B3.

## N1 Atlas collision

Runs (raw outputs pasted at the end): #1-#3 are the three match_phrasings in order; #4 my own phrasing ("isogeny volcano floor crater index calculus yield cofactor 2-torsion"); #5 (G-restricted base filter/project), #6 (Sylow 2-torsion by volcano level), #7 (generator/exact decomposition ceiling) are extra. Top-5 of every run was opened (YAML mechanism + obstruction + forecloses + next_action). Each KR hit was read in KRMAP.

Read and judged:
- LEAD-STR-class-representative-ic-selection (open_next_step; top-3 in runs 3,4,5,7). Mechanism: small-abscissa IC yield depends on which points the coordinates call small; transport to the crater or pick the best isomorphic model. Next action: 3-arm ecbench study at 24-32 bits (floor; floor-carried-to-crater with transport charged; best-of-K models on held-out targets). Its own closure branch: "7.2% model effect and 5.8% l=2 yield effect are factor-base sampling noise or a selection artifact". Forecloses: floor vs crater IC yield; walk to the crater; pick the isomorphic model with the best small-x base. C3 does what the forecloses phrases do not: it supplies a third explanation (neither a usable lever nor noise: exact cofactor-coset bookkeeping) and a replacement experiment. Not the same mechanism as the lead's hope that selection is a free lever; it is the lead's sharper next step. Note what C3 actually shows: N0 is a property of the base alone and is computable before any target is drawn, so the lead's arm (c) (best-of-K isomorphic models picked on calibration targets) should SURVIVE its held-out test, and arm (b) should show a real l=2 gain. By the lead's own `discriminates` rule that is a "constant-factor success", so the lever is real and usable but DOMINATED: a G-restricted base reaches the maximum K_G = B^2 and no model or level choice can exceed it (and costs one [r] check per scanned candidate, charged). A reader must not mistake a successful held-out replication of arm (c) for an IC improvement. -> advances_lead. Caveats: (i) E3a already supplies most of the evidence for the pooled l=2 and model effects, so the lead's 3-arm study is superseded independent of C3; (ii) C3 does not cover the lead's large-prime conductor-gap and heavy-tail-screen parts, only predicts them null (odd-degree isogeny keeps E[2] and |S|, so t and h are unchanged: a PREDICTION, not tested).
- LEAD-ICP-isogeny-transported-relation-yield (open_blocked; top-1 in runs 2,4,6). Large-prime conductor-gap crater/floor arity-3 yields on P29/P37; best_measured floor/crater 0.975 [0.603, 1.451] and 1.127 [0.922, 1.342]. Different instrument (primes ~2^29-2^37, conductor steps 8209/131101), blocked on 17 missing arms. C3 predicts a null there (see above) and is consistent with the data; it does not advance this lead's next action.
- LEAD-STR-isogeny-class-generic-invariance (closed_obstructed). Obstruction.statement (theorem): "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. ... Transport is exact and costs at most 1.3% of a solve." revisit_when assigns level-dependent step-cost constants to class-representative-ic-selection. C3 does not contradict it (C3 says IC, not rho, sees the cofactor), and it does not claim to escape it; SO-ISO is about generic methods.
- LEAD-ICB-cofactor-torsion-quotients (closed_obstructed, proof, binary ECC2K-130). Obstruction.statement: "every full-translation homomorphic cofactor quotient reduces to the order-l projection rho already uses (Sylow coprimality) ... the production 2-torsion census adds 0 relations." forecloses: "spend the cofactor on decomposition". C3 is prime-field, odd-and-even cofactors, and uses the quotient E(F_p) -> S only as a COUNTING device for how many base pairs land in G; it prunes nothing. The G-restricted base arm is exactly "work in the order-r projection", i.e. what that obstruction says rho already does. Not a duplicate, but C3 cannot be read as a way to "spend the cofactor": it is the cost of NOT having projected.
- LEAD-ICP-algebraic-membership-factor-base (SO-ALGFB, closed_obstructed). Obstruction.statement includes: "mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N) ... Scope: prime-order E/F_p, any base of size B." C3 does NOT escape SO-ALGFB: for a base living in G the conservation constant is C/r, for a full-group base it is C/(hr); C3 is conservation with the denominator set by the group generated by the base, plus the diagonal 2-torsion term. "Scope: prime-order" is not an escape, because the law reduces to the obstruction at h = 1 and the cofactor case adds only a constant (h-fold for a G-restricted base, paid for by the filter scan).
- LEAD-ICP-generic-table-decomposition (SO-TABLE, closed_obstructed, theorem, Scope "any generic (enumeration/table) decomposition over F_p"). The pair-table oracle is inside scope; C3 changes only a constant and only when h > 1. Not escaped.
- LEAD-ICE-decomposition-probability-audit (open_next_step; surfaced by run #7): exact integer-ratio P(decomp), KN-FIND-007 to second order; same family as 21e7c4/E3a; no cofactor-coset or 2-torsion term. Related, not the same.
- LEAD-ICE-semaev-yield-model-coset-typing (open_next_step): "coset-typed" there means Nagao-style disjoint shifts raising yield per query, a different object (typed domain vs untyped), no E(F_p)->S cofactor count.
- LEAD-ICP-coincidence-harvest-structured-base (open_next_step): pair-sum coincidence excess kappa for structured bases on prime-order curves; kappa_rel ~ 1. Different statistic (excess over random base), cofactor absent.
- LEAD-ICP-full-width-arity-grid (open_blocked), LEAD-ICB-large-prime-variants, LEAD-ICB-kic-golden-base-exact-decomp, LEAD-ICP-coppersmith-smallroot-semaev, LEAD-ICP-lattice-ic-relation-construction, LEAD-ICP-char0-lifting-xedni-smoothness, LEAD-TRF-odd-char-descent-smith-quartic, LEAD-TRF-teske-secret-isogeny-trapdoor, LEAD-STR-jmv-random-self-reduction, LEAD-RHO-correlated-walks-shared-sums, LEAD-ICB-multi-target-and-portfolio, LEAD-EXO-quantum-ecdlp-resources: lexical/shared-vocabulary hits only; none states or forecloses a cofactor-coset count. LEAD-TRF-teske-secret-isogeny-trapdoor shares the crater/floor 20-arm panel (EXP-ECTD-0cf008) with the transported-yield lead; its prediction "ratios consistent with one" agrees with C3's null prediction for odd conductor steps.

Strictness note: C3 touches SO-ALGFB, SO-TABLE and LEAD-ICB-cofactor-torsion-quotients and escapes none of them; its claimed "Scope: prime-order" escape is not real (the law reduces to the obstruction at h = 1 and, for h > 1, adds only a constant). That does not make it a duplicate of those closed leads: C3 proposes no cost reduction those obstructions forbid; it is conservation with the denominator set by the group generated by the base, plus the diagonal t-term, and its job is to close an open lead, not to open one. It adds nothing on B1-B7 for prime-order curves (effect identically 0 there).

## N2 Known results (build_frontier_map)

Runs #1-#7 (raw below). No KR row states a cofactor-coset or 2-torsion count of base-pair hits. Nearest: KR-IC-955fd6 (FGHR / FHJRV: 2- and 4-torsion symmetries shrink PDP systems, Edwards/Jacobi models over F_{q^n}) is about reducing the algebraic system, not about counting base pairs that land in the target subgroup; KR-IC-5931ee (naive Semaev IC over F_p is not better than generic) and KR-RHO-755e35 (isogenous curves equally hard) are context only; the remaining hits (KR-IC-a4dd54, -46d822, -9e610d, -1fcdbc, -b0fcda, -5a43e5, -73db3f) are lexical.
Literature citations (verification status):
- Miret, Moreno, Sadornil, Tena, Valls, Appl. Math. Comput. 176(2) (2006) 739-750, DOI 10.1016/J.AMC.2005.10.020: retrieved (WebSearch: bibliographic record plus a secondary summary that the algorithm "relies on the link between a curve's 2-torsion structure and its level in the volcano"); full text NOT read.
- Miret, Sadornil, Tena, Tomas, Valls, Publ. Mat. 51 Extra (2007) 165-180, DOI 10.5565/PUBLMAT_PJTN05_08: retrieved (WebSearch: bibliographic record; abstract "relates the l-Sylow subgroup of an elliptic curve and the level of the volcano"); it is the l = 3 paper, so for the 2-torsion-by-level step the 2006 paper is the load-bearing one.
- Kohel, thesis (1996): recalled, not verified.
The 2-torsion-by-level fact is also visible in the program's own data: in the E3a workloads l=2 cells split into t = 2 (144 curves) and t = 4 (224 curves) via (n1, n2) (scout-check).
The counting identity itself is a birthday count on the cofactor quotient; I did not find it in the literature (recalled: not a standard statement, but it is elementary, so absence is weak evidence).
Verdict for N2: no known_result; the external ingredient is the volcano/2-torsion structure only.

## N3 Ledger (grep of ledger/.index/{proposals,hypotheses}.jsonl; terms: cofactor, factor.?base, subgroup|project|filter, volcano, 2-torsion, floor.*crater, N0|class-cancelling, exact_decomposition_ceiling, E3a|E3b, yield|relation)

Hits that may be the same object (id, status, claim start):
- IDEA-20260829-c6e7a4 (proposed): "(A) THE DENOMINATOR CORRECTION, DERIVED. KN-FIND-007 fixes the mean per-target decomposition yield at binom(B+m-1,m)/|G| ..." -> leading-order h law, full_curve vs target_subgroup base. OPENED. No torsion/volcano/t term (grep: none). Children H-ECDLP-f79c89 (proposed), EXP-ECDLP-933c10 (draft).
- IDEA-20260830-21e7c4 (proposed): "(A) THE OBJECT IS DETERMINISTIC. ... P(decomp) = |mW intersect H| / |H|" -> exact count. OPENED. No cofactor-coset closed form, no volcano.
- IDEA-20261017-3db2a8 (proposed): "SCOPE: derivation plus zero-compute arithmetic ... target group <P> of odd prime order, cofactor h=2^s ..." -> binary analogue: class of the multiset sum in E/<P>, mean d(V)*C(|W|+t-1,t)/N with equidistribution of cl(W) assumed (H2). OPENED. Same tracked-object family; no diagonal/2-torsion correction, binary-only.
- IDEA-20260830-1f2b8b (proposed; index row only, not opened): "THE DENSITY-INDEPENDENT OVER-DISPERSION ... pair (support of the target distribution, denominator of the rate), projected to n1 = the index of <G> in E(F_p)" -> same cofactor-denominator family (leading order).
- IDEA-20260906-86cd30 (proposed; index row only): "THE m = 2 DECOMPOSITION GRAPH OF A PRIME-ORDER CURVE IS A PATH ... exact closed form" -> the prime-order (no 2-torsion) analogue; C3 at t = 1, |S| = 1.
- IDEA-20261001-5628bc (proposed; index row only): "THE COFACTOR OF ECC2K-130 IS A FACTOR-BASE-SIZE PARAMETER, NOT A LEVER" -> binary; same conclusion type.
- IDEA-20260829-96bd39, IDEA-20260731-017, IDEA-20260807-a2b59a, IDEA-20260811-dcbea4, IDEA-20261015-e0b5dd, IDEA-20261024-7be1c6, H-ECTD-e88346, H-ECTD-19017a: volcano/crater-floor ideas (2-adic structure, conductor barrier, pushing crater bases through isogenies, 2-torsion type reachability); none carries the IC yield count.
Decision: no record is the same object. The pair {c6e7a4 + 21e7c4} contains the leading-order law and the exact-count object; C3's t-term and the volcano attribution are not in any of them.

## N4 Notation

Pair: (whole-group small-abscissa signed base on a cofactor curve E(F_p), #E = h*r; Sigma = translation by base elements, targets drawn in G). Tracked object: pi_S: E(F_p) -> S = E/G (a homomorphism, hence a block system of full translation on the composite-order group). Class: partial-action (IC Class I), as claimed.
Against the recorded rigidity results:
- IDEA-20260806-c5d183 / KN-FIND-ffe1df Theorem C / IDEA-20260901-863e36: all are non-existence statements for projections of a PRIME-order group (constant or injective; exactly sum-compatible bucket index is a homomorphism onto a group of order dividing N). C3 does not claim a projection of G; at h = 1 S is trivial and C3 returns B^2 (the null). So C3 is not a recorded rigidity result in new notation. Conversely it is not a new arithmetic either: pi_S is the homomorphic cofactor quotient that LEAD-ICB-cofactor-torsion-quotients (proof, Sylow coprimality) shows carries no DLP information in G; here it is only bookkeeping for which pairs cancel. By the object-frame rule "a new arithmetic is a (representation, operation set) pair", C3 is the already-recorded IC pair with targets restricted to a subgroup.
- KN-OPEN-020: C3 is inside the scoped-out class (bounded-degree/enumerative; small-abscissa base, membership by table), not one of the open classes (high-degree, implicit-membership, target-dependent). It makes no factor-base escape claim.
- Related recorded law in new notation: KN-FIND-007 conservation with the denominator = order of the group generated by the base (c6e7a4 states this; C3 adds the doubling term).

## Raw outputs (verbatim)

### lead_atlas.py --match #1 (match_phrasing[0]: cofactor-coset class-cancelling count K_G = B(B-1+t)/|S| for small-abscissa bases)
```
    6  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    5  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    4  LEAD-EXO-quantum-ecdlp-resources             open_next_step     Quantum ECDLP: reversible secp256k1 point-addition circuits for Shor (resource reduction)
    3  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    3  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
    3  LEAD-ICP-full-width-arity-grid               open_blocked       Full-width complete-solve IC arity grid (m = 2..8) at 50-63-bit subgroups - prime coset/small-x bases, Koblitz orbit and ordinary-binary bases
    3  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
    3  LEAD-STR-curve-generation-provenance-seeds   exhausted_at_scale Manipulated generation of standard curves (NIST P-curve seeds, Brainpool, BN, rigidity)
```

### build_frontier_map.py --match #1 (same phrase)
```
KR-IC-b0fcda  score=3  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5931ee  score=1  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-73db3f  score=1  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-RHO-482ed3  score=1  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
```

### lead_atlas.py --match #2 (match_phrasing[1]: volcano level index calculus yield difference is 2-torsion bookkeeping)
```
   14  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   10  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
   10  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   10  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   10  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
    8  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
```

### build_frontier_map.py --match #2 (same phrase)
```
KR-IC-5931ee  score=12  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-1fcdbc  score=10  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=8  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-b0fcda  score=6  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
```

### lead_atlas.py --match #3 (match_phrasing[2]: index calculus yield across volcano levels depends only on the group structure and automorphisms)
```
   18  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   14  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   14  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   13  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   11  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
   10  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    9  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
```

### build_frontier_map.py --match #3 (same phrase)
```
KR-IC-5931ee  score=13  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=8  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-RHO-13bf67  score=8  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-1fcdbc  score=7  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
```

### lead_atlas.py --match #4 (own: isogeny volcano floor crater index calculus yield cofactor 2-torsion)
```
   29  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   20  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   14  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
   12  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   11  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
   10  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
```

### build_frontier_map.py --match #4 (same phrase)
```
KR-IC-5931ee  score=12  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=12  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-1fcdbc  score=10  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-46d822  score=8  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=8  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=8  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-64659b  score=6  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-791cb7  score=6  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
```

### lead_atlas.py --match #5 (extra: factor base restricted to the prime-order subgroup: filter or project small-abscissa base points by cofactor to raise decomposition hit rate)
```
   22  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   16  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   16  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   15  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   15  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   14  LEAD-ICB-nonlinear-frob-stable-bases         open_next_step     Non-subspace Frobenius-stable factor bases at prime n: trace-spectrum, Hamming ball, multiplicative subgroup, tau-adic, algebraic-group (Couveignes-Lercier) points
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
```

### build_frontier_map.py --match #5 (same phrase)
```
KR-IC-5a43e5  score=15  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-8b9daa  score=7  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-081a58  score=6  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

### lead_atlas.py --match #6 (extra: Sylow 2-torsion rational points of isogeny volcano level full 2-torsion floor one rational 2-torsion point)
```
   13  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   12  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   11  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
   10  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
    9  LEAD-STR-jmv-random-self-reduction           closed_known       Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level
    8  LEAD-RHO-cheaper-step-primitives             open_unexamined    Cheaper step primitives never measured here: tag tracing on EC, point-halving steps on binary curves
    8  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    8  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
```

### build_frontier_map.py --match #6 (same phrase)
```
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-RHO-755e35  score=7  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-791cb7  score=6  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-1c2928  score=6  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
```

### lead_atlas.py --match #7 (extra: generator choice changes index calculus yield: exact decomposition ceiling counts cofactor classes of the factor base)
```
   22  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   21  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   21  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   19  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   19  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   18  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   18  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
   18  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
```

### build_frontier_map.py --match #7 (same phrase)
```
KR-IC-5931ee  score=19  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-b0fcda  score=18  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-a4dd54  score=16  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=14  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5a43e5  score=11  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-ae532f  score=11  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-1fcdbc  score=10  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
```

### scout-check script output (closed_form check; script _c3_raw/check_closed_form.py)
```
rows unmatched: 0  rows with non-integer N0 or (N0-B) odd: 0  of 800
cell(l,h,t)  n  mean_N0  SE_N0  Khat=(N0-B)/2  pred=B(B-1+t)/h  z=(Khat-pred)/(SE/2)
('l2', 4, 2) 144 557.5 2.67 262.7 264.0 -0.95
('l2', 4, 4) 224 588.8 2.42 278.4 280.0 -1.31
('l3', 1, 1) 128 2080.0 0.0 1024.0 1024.0 nan
('l3', 5, 1) 188 440.4 1.73 204.2 204.8 -0.68
('l3', 7, 1) 116 325.8 2.29 146.9 146.3 0.52
h=4 pred ratio K(t=2)/K(t=4) = (B+1)/(B+3) = 0.9429  ; 33/35 = 0.9429
G-restricted/current hit-rate factor h*B/(B-1+t), h=4 t=4 B=32: 3.657
G-restricted/current hit-rate factor h*B/(B-1+t), h=4 t=2 B=32: 3.879
G-restricted/current hit-rate factor h*B/(B-1+t), h=12 t=4 B=32: 10.971
```

### scout-check: level x t cross-tab and N0 cells (script _c3_raw/check_level_t.py)
```
class level dist_from_root t : count  (all curves in class files)
('l2-inert', 0, 2, 4) 4
('l2-inert', 1, 1, 4) 4
('l2-inert', 1, 3, 4) 8
('l2-inert', 2, 0, 4) 4
('l2-inert', 2, 2, 4) 4
('l2-inert', 2, 4, 4) 16
('l2-inert', 3, 1, 2) 8
('l2-inert', 3, 3, 2) 8
('l2-inert', 3, 5, 2) 32
('l2-ramified', 0, 3, 4) 4
('l2-ramified', 0, 4, 4) 4
('l2-ramified', 1, 2, 4) 4
('l2-ramified', 1, 4, 4) 4
('l2-ramified', 1, 5, 4) 8
('l2-ramified', 2, 1, 4) 4
('l2-ramified', 2, 3, 4) 4
('l2-ramified', 2, 5, 4) 8
('l2-ramified', 2, 6, 4) 16
('l2-ramified', 3, 0, 2) 4
('l2-ramified', 3, 2, 2) 4
('l2-ramified', 3, 4, 2) 8
('l2-ramified', 3, 6, 2) 16
('l2-ramified', 3, 7, 2) 16
('l2-split', 0, 3, 4) 4
('l2-split', 0, 4, 4) 8
('l2-split', 0, 5, 4) 8
('l2-split', 0, 6, 4) 8
('l2-split', 0, 7, 4) 8
('l2-split', 0, 8, 4) 8
('l2-split', 1, 2, 4) 4
('l2-split', 1, 5, 4) 8
('l2-split', 1, 6, 4) 8
('l2-split', 1, 7, 4) 8
('l2-split', 1, 8, 4) 8
('l2-split', 2, 1, 4) 4
('l2-split', 2, 3, 4) 4
('l2-split', 2, 6, 4) 16
('l2-split', 2, 7, 4) 16
('l2-split', 2, 8, 4) 8
('l2-split', 3, 0, 2) 4
('l2-split', 3, 2, 2) 4
('l2-split', 3, 4, 2) 8
('l2-split', 3, 7, 2) 32
('l3-inert', 0, 3, 1) 4
('l3-inert', 1, 2, 1) 4
('l3-inert', 1, 4, 1) 12
('l3-inert', 2, 1, 1) 4
('l3-inert', 2, 3, 1) 8
('l3-inert', 2, 5, 1) 36
('l3-inert', 3, 0, 1) 4
('l3-inert', 3, 2, 1) 8
('l3-inert', 3, 4, 1) 24
('l3-inert', 3, 6, 1) 12
('l3-ramified', 0, 1, 1) 4
('l3-ramified', 0, 2, 1) 4
('l3-ramified', 1, 0, 1) 4
('l3-ramified', 1, 2, 1) 8
('l3-ramified', 1, 3, 1) 12
('l3-ramified', 2, 1, 1) 12
('l3-ramified', 2, 3, 1) 24
('l3-ramified', 2, 4, 1) 12
('l3-ramified', 3, 2, 1) 36
('l3-ramified', 3, 4, 1) 12
('l3-split', 0, 3, 1) 4
('l3-split', 0, 4, 1) 8
('l3-split', 0, 5, 1) 8
('l3-split', 0, 6, 1) 8
('l3-split', 0, 7, 1) 8
('l3-split', 0, 8, 1) 8
('l3-split', 1, 2, 1) 4
('l3-split', 1, 4, 1) 4
('l3-split', 1, 5, 1) 16
('l3-split', 1, 6, 1) 16
('l3-split', 1, 7, 1) 8
('l3-split', 2, 1, 1) 4
('l3-split', 2, 3, 1) 8
('l3-split', 2, 5, 1) 12
('l3-split', 2, 6, 1) 24
('l3-split', 3, 0, 1) 4
('l3-split', 3, 2, 1) 8
('l3-split', 3, 4, 1) 24
('l3-split', 3, 6, 1) 12

E3a workloads: class level t h : n mean_N0 pred=2*B(B-1+t)/h+B
('l2-inert', 0, 4, 4) 4 582.0 592.0
('l2-inert', 1, 4, 4) 12 589.7 592.0
('l2-inert', 2, 4, 4) 24 581.2 592.0
('l2-inert', 3, 2, 4) 48 559.5 560.0
('l2-ramified', 0, 4, 4) 8 578.5 592.0
('l2-ramified', 1, 4, 4) 16 586.0 592.0
('l2-ramified', 2, 4, 4) 32 593.8 592.0
('l2-ramified', 3, 2, 4) 48 557.1 560.0
('l2-split', 0, 4, 4) 44 597.1 592.0
('l2-split', 1, 4, 4) 36 586.0 592.0
('l2-split', 2, 4, 4) 48 586.9 592.0
('l2-split', 3, 2, 4) 48 555.9 560.0
('l3-inert', 0, 1, 7) 4 320.5 324.6
('l3-inert', 1, 1, 7) 16 318.9 324.6
('l3-inert', 2, 1, 7) 48 324.3 324.6
('l3-inert', 3, 1, 7) 48 330.0 324.6
('l3-ramified', 0, 1, 1) 8 2080.0 2080.0
('l3-ramified', 1, 1, 1) 24 2080.0 2080.0
('l3-ramified', 2, 1, 1) 48 2080.0 2080.0
('l3-ramified', 3, 1, 1) 48 2080.0 2080.0
('l3-split', 0, 1, 5) 44 441.3 441.6
('l3-split', 1, 1, 5) 48 434.2 441.6
('l3-split', 2, 1, 5) 48 442.7 441.6
('l3-split', 3, 1, 5) 48 443.5 441.6
```

### scout-check: implied slope and N0 vs 2K_G ratios (script _c3_raw/check_slope_ratio.py)
```
implied OLS slope of ln((N0-B)/r) on ln(N0/r), n=800: 1.0442
h=4 t=4: ratio by N0 = 3.514 ; ratio by 2K_G = 3.657
h=4 t=2: ratio by N0 = 3.714 ; ratio by 2K_G = 3.879
h=12 t=4: ratio by N0 = 9.512 ; ratio by 2K_G = 10.971
```
