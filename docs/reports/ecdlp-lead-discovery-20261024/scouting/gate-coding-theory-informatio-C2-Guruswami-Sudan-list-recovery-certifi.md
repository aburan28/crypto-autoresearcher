# Novelty gate N1-N4: C2 Guruswami-Sudan list-recovery certifier for the elliptic log graph

Gate run date: 2026-10-24. Candidate text is workflow-computed (no user authority). Nothing was edited, created or committed inside the repositories. All raw outputs below were produced by this gate run (own raw directory `scout/rawC2/`; the shared `scout/raw/` was NOT used because another session writes there).

Environment exported before every tool call: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES as specified in the task.

## 0. Verdict (details and evidence follow)

Verdict: **advances_lead**, narrowly. Lead: **LEAD-EXO-invertible-hint-subset** (open_next_step).

- The object is the lead's object. Candidate pair = H-ECDLP-f6a43a pair (R1 affine x with integer lift of the log; operation set = degree-bounded polynomial evaluation on x; Class III). The candidate's mechanism sentence, its H-C2.1 (= H1 of f6a43a) and its blind spot (SLP-cheap omega) are all already recorded in IDEA-20261003-cd1903 / H-ECDLP-f6a43a. The `forecloses` list of the lead ("low-degree polynomial agreeing with the discrete log", "small-x set logarithm interpolation", "dense invertible subset", "hint family with cheap logarithms") covers the candidate's object word for word. There is no new lead here.
- The completeness lemma is not new: it is Lemma V of cd1903 (a total omega is its own chi by one scalar multiplication) combined with the break-even line of IDEA-20261016-0bacee (random self-reduction beats rho only above c/sqrt(n) success rate; it explicitly says the Weil allowance for a degree-k defect function has the same order as the break-even rate).
- What is not in the lead (the delta): (a) an instrument for d >= 2 beyond the lead's Stage-2 reach (A(2) at n <= 2^10 by O(n^3)); exact A(d) for d >= 2 is a maximum-agreement fit with no known polynomial-time exact algorithm for a general point set (maximum-likelihood RS decoding is NP-hard in general, Guruswami-Vardy; recalled, not retrieved; whether the log graph is easier is not claimed), and GS list recovery is the polynomial-time tool that certifies an UPPER bound on it above the Johnson floor; (b) the reading "no M_deg omega with 2 <= d < sqrt(N) has agreement above the rho-beating threshold on this curve", which is decision-relevant and which Theorem W (K_d <= 4d+2 recalled, H2, not retrieved) does not give: that bound is about N (0.95 N) at d = 8 and p = 2^20 and exceeds N at p = 2^12 for every d >= 1 (computed in section 5). Named outcome the existing protocol cannot read: a non-planted list at d >= 2 on a real curve at 2^11..2^20 that is absent from its NULL-1 matches.
- What the candidate does NOT do (strict reading, stated so the coordinator can demote the verdict): the census cannot read any of f6a43a's three scored outcomes. E-RANDOM / E-POWER / E-WEIL-TIGHT thresholds at p = 2^20 are about 8 to 710, below the GS floor sqrt(dN) = 1024 (d = 1), 1448 (d = 2), 1774 (d = 3). The candidate says so itself ("does not measure A(d) at the H1 scale"). Its own H-C2.2 puts the certified band at below 2^-10000 for a random labelling (recomputed here: about 2^-19526 at p = 2^20, d = 2, t = 2048). So the lead's discriminator "A(d) at the random-labelling level for all d" stays unmeasured for d >= 2, and the crypto-size extrapolation rests on H1, which the census cannot measure. Under the reading "advances only if it reads one of the lead's own scored outcomes" this is duplicate_of_lead; I chose advances_lead because the lead's mechanism sentence is the rho-beating criterion itself and the candidate certifies exactly that criterion for the d >= 2 half the lead cannot execute.
- Proposed disposition over-scopes: "closed_obstructed(measured)" for the whole lead. The lead's mechanism is any dense recognizable-and-invertible subset; an M_deg toy census closes at most the algebraic-omega sub-model (the lead's own wording), only for the rho-beating band, only on tested curves at toy tier.

## 1. Tool commands run (from /Volumes/SSD990-2/crypto-autoresearcher)

    python3 tools/lead_atlas.py --match "<phrase>"        (N1, 5 phrases)
    python3 tools/build_frontier_map.py --match "<phrase>" (N2, 4 phrases)

N1 phrases: P1 = candidate match_phrasing 1; P2 = match_phrasing 2; P3 = match_phrasing 3; P4 and P5 = my own ("list decoding Reed-Solomon polynomial reconstruction agreement discrete log graph"; "maximal agreement of a low-degree polynomial with the elliptic curve discrete log as a function of x").

## 2. RAW N1 OUTPUT (lead_atlas.py --match)

### N1 run P1: python3 tools/lead_atlas.py --match "Guruswami-Sudan list-recovery certifier for the maximal agreement A(d) of the elliptic log graph with degree-d polynomials"
```
    6  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    5  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    4  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    4  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    4  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    4  LEAD-ICB-large-prime-variants                open_next_step     Single and double large-prime relation collection for binary and Koblitz IC (free-leg, GTTD on subspace bases)
    4  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
```

### N1 run P2: python3 tools/lead_atlas.py --match "check whether any low-degree polynomial of the x-coordinate equals the discrete log on a large set of curve points"
```
   19  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   14  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   13  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
   13  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
    9  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    9  LEAD-STR-torsion-module-leak                 closed_obstructed  l-torsion (l != N) as a Galois/End module leaking k or attack cost
    8  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    7  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
```

### N1 run P3: python3 tools/lead_atlas.py --match "non-homomorphic point statistic that is a function of the encoding and recovers the logarithm on a dense recognizable and invertible subset"
```
   22  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    9  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    9  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    7  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
    7  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    6  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    6  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    6  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
```

### N1 run P4: python3 tools/lead_atlas.py --match "list decoding Reed-Solomon polynomial reconstruction agreement discrete log graph"
```
   12  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
   11  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    9  LEAD-STR-torsion-module-leak                 closed_obstructed  l-torsion (l != N) as a Galois/End module leaking k or attack cost
    8  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    6  KR-RHO-898783                                known_result       Interval DLP: kangaroo and Gaudry–Schost constants
```

### N1 run P5: python3 tools/lead_atlas.py --match "maximal agreement of a low-degree polynomial with the elliptic curve discrete log as a function of x"
```
   15  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
   12  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    9  LEAD-STR-torsion-module-leak                 closed_obstructed  l-torsion (l != N) as a Galois/End module leaking k or attack cost
    8  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    8  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
```

## 3. RAW N2 OUTPUT (build_frontier_map.py --match)

### N2 run P1: python3 tools/build_frontier_map.py --match "Guruswami-Sudan list-recovery certifier for the maximal agreement A(d) of the elliptic log graph with degree-d polynomials"
```
KR-IC-5a43e5  score=6  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-955fd6  score=4  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5765d2  score=3  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-46c2c6  score=3  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-898783  score=3  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
```

### N2 run P2: python3 tools/build_frontier_map.py --match "check whether any low-degree polynomial of the x-coordinate equals the discrete log on a large set of curve points"
```
KR-RHO-46c2c6  score=13  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-ea34b8  score=9  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5931ee  score=6  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-955fd6  score=6  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-53c89f  score=6  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-6239aa  score=6  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-898783  score=6  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
```

### N2 run P3: python3 tools/build_frontier_map.py --match "non-homomorphic point statistic that is a function of the encoding and recovers the logarithm on a dense recognizable and invertible subset"
```
KR-RHO-6654ba  score=9  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-8b9daa  score=5  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5a43e5  score=3  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-RHO-ea34b8  score=3  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-fbd582  score=3  [known_mechanism/proven]  Nearly free P−Q alongside P+Q
    sources: KN-LIT-732e36, KN-LIT-a4b3d8
KR-IC-73db3f  score=1  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
```

### N2 run P4: python3 tools/build_frontier_map.py --match "list decoding Reed-Solomon polynomial reconstruction agreement discrete log graph"
```
KR-RHO-46c2c6  score=9  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-ea34b8  score=8  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-898783  score=6  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-1fcdbc  score=3  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

## 4. N1 analysis: top hits read (mechanism + obstruction/next_action + forecloses)

Lead YAMLs opened under /Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/. Read in full: LEAD-EXO-invertible-hint-subset, -dl-character-sum-pseudorandom, -coordinate-statistic-leakage, -hnp-advice-leakage, -ml-learned-models, -miller-pairing-cocycle, LEAD-STR-torsion-module-leak, -jmv-random-self-reduction, LEAD-ICP-algebraic-membership-factor-base, LEAD-TRF-miller-cocycle-nonhom-transfer, LEAD-RHO-lhw-polymem-collision-walks. Read first 35-40 lines only (mechanism, disposition, obstruction, start of evidence): LEAD-TRF-padic-canonical-section, LEAD-RHO-non-automorphism-equivalence, LEAD-RHO-generic-sqrt-lower-bound, LEAD-EXO-augmented-oracle-ggm. NOT opened (rank 6-8 in a run, lexical only): LEAD-ICB-large-prime-variants, LEAD-ICE-sat-xor-pdp-oracle, LEAD-ICB-frobenius-search-symmetry, LEAD-ICP-retained-setup-online.

Hit table (disposition from the atlas row):

| hit | disposition | same mechanism? | what the candidate does that the hit's `forecloses` does not cover |
|---|---|---|---|
| LEAD-EXO-invertible-hint-subset (top in P2, P3, P4, P5; 5th in P1) | open_next_step | YES. Mechanism: "a low-degree polynomial agreeing with log_g on the small-x set", random self-reduction into D. `forecloses` includes "low-degree polynomial agreeing with the discrete log", "small-x set logarithm interpolation", "dense invertible subset", "hint family with cheap logarithms". | Only the instrument and the reading: GS/Sudan list recovery as an upper-bound certifier for A(d), d >= 2, above the Johnson floor; the rho-beating threshold reading. Not covered by the lead's next_action (exact A(1), A(d) vs the random-labelling null). |
| LEAD-EXO-dl-character-sum-pseudorandom (2nd in P1, P2; 3rd in P4, P5) | exhausted_at_scale | NO. Statistic is the pure additive-character sum of log over a factor base, R = C_EC/C_null flat 1.28-1.34 at 2^20-2^26 (EV-ECDLP-f83a17). | Polynomial agreement is a mixed sum S(c,t) = sum e_p(cF(x)) e_n(t log Q) (Theorem W route in cd1903). A flat pure-log sum does not bound it. Same analytic family, different quantity. Its revisit_when (R trending up beyond 2^30) is not touched. |
| LEAD-STR-torsion-module-leak (SO-TORS; in P2, P4, P5 top 6) | closed_obstructed | NO. Scope clause (quoted): "Scope: prime-order G, any l != N." Subject is l-torsion / division-polynomial statistics. | The candidate uses no torsion statistic. Its listing of SO-TORS as "touched" is imprecise: the sentence it cites ("partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a)") concerns partial-information statistics; the full-value regime is priced by IDEA-20261016-0bacee instead. |
| LEAD-ICP-algebraic-membership-factor-base (SO-ALGFB; P2, P5) | closed_obstructed | NO (no factor base). Scope: "prime-order E/F_p, any base of size B." | Adjacent only through the "high-degree description" class that KN-OPEN-020 leaves open; see N4. |
| LEAD-EXO-augmented-oracle-ggm (SO-GEN family; not in top 5, read for the escape premise) | closed_obstructed | Partly. An omega that reads x is an x-oracle consumer; the lead records "the x-oracle gives Y_A = Y_B exactly (EV-ECDLP-fd61e4 strong)" and "Scope: oracles, not resources". | The predicted-empty outcome is exactly what GGM simulability predicts; a real-curve list absent from NULL-1 would be the first non-GGM-simulable event of this kind. |
| LEAD-RHO-generic-sqrt-lower-bound (SO-GEN) | closed_obstructed | NO. Quote: "Scope: all generic algorithms, any field, any r." revisit_when: "only a method that reads the representation (index calculus, transfer) can change the exponent." | The candidate reads x, so it is outside the scope clause, but its expected outcome is the generic one; f6a43a already records "Theorem W is generic-strength" for the relabelled group. |
| LEAD-EXO-coordinate-statistic-leakage (read; open) | open_next_step | Adjacent. Its next_action leaves "only unnatural (unbounded-degree) statistics" after the natural-statistic registry closes. | A degree ladder d in {2..sqrt N} is a candidate way to quantify the "unbounded-degree" residue. Not in its forecloses. |
| LEAD-EXO-ml-learned-models (P1, P4, P5; open) | open_next_step | NO, but same experimental pattern (planted positive control + random-relabelling null at N up to 2^24). | Hypothesis class differs (degree-d polynomial on x with exact-value agreement vs a learned log-bit predictor). |
| LEAD-TRF-miller-cocycle-nonhom-transfer (P3; B7 arm) | open_unexamined | NO for the primary arm. For the secondary arm: its next_action is H1 of IDEA-20261017-e3a6f1 (equidistribution of log_g U(kP), Smart ratio, character correlation, planted control). | A polynomial-structure census is not in that next_action. But the arm is under-specified: the abscissa log_g U(kP) lives in Z/(p-1), the ordinate k in Z/N, so GS needs a stated common field and lift. And LEAD-EXO-miller-pairing-cocycle's next_action (verify K2: U(kP) = c r_k C^(k/N), then charge r_k) comes first: if K2 holds the polynomial question reduces to structure of log r_k. |
| LEAD-RHO-lhw-polymem-collision-walks, LEAD-TRF-padic-canonical-section, LEAD-RHO-non-automorphism-equivalence, KR-IC-5a43e5, KR-IC-955fd6, KR-RHO-ea34b8, KR-RHO-46c2c6, KR-RHO-6654ba, KR-RHO-898783 | various | NO. Lexical hits ("polynomial", "memory", "set", "large"). | Not the same object. |

Quoted obstruction text (Scope clauses) for the standing obstructions the candidate names:
- SO-GEN (LEAD-RHO-generic-sqrt-lower-bound): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant ... Scope: all generic algorithms, any field, any r."
- SO-TORS (LEAD-STR-torsion-module-leak): "... A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). ... Scope: prime-order G, any l != N."
- SO-ALGFB (LEAD-ICP-algebraic-membership-factor-base): "... Scope: prime-order E/F_p, any base of size B."

Answer to "does the candidate escape SO-GEN / SO-TORS": it leaves the SO-GEN scope clause by reading x (non-generic), but its predicted outcome is the generic one and the lead's cd1903 record already treats the relabelled generic group as the null. SO-TORS is not on point (no torsion statistic).

## 5. Numbers recomputed by this gate (python, own script, not from the candidate)

Candidate's quantities, recomputed at N = p = 2^bits (N = p is a simplification; Hasse gives N within 2 sqrt p). GS Johnson floor = sqrt(dN). t_rho = 1.03 d sqrt(N) uses the matched baseline constant quoted in IDEA-20261016-0bacee (negation-map BSGS 1.03 sqrt(n)); the candidate writes d sqrt(N). E-WEIL-TIGHT = 0.05 sqrt(p) ln p (H-ECDLP-f6a43a). E-POWER = N^0.15. H1 = (d+1) ln p / ln((d+1) ln p). Theorem W = 2 + (4d+2) sqrt(p) (1 + ln(pN)) with K_d <= 4d+2 taken from H2 of f6a43a (recalled there, NOT retrieved; conditional).

| bits | d | GS floor sqrt(dN) | t_rho | E-WEIL-TIGHT | E-POWER | H1 | Theorem W (K=4d+2) | ThmW / floor |
|---|---|---|---|---|---|---|---|---|
| 12 | 2 | 91 | 132 | 27 | 3.5 | 7.8 | 11289 (2.76 N) | 125 |
| 16 | 1 | 256 | 264 | 142 | 5.3 | 7.2 | 35608 (0.54 N) | 139 |
| 16 | 2 | 362 | 527 | 142 | 5.3 | 9.5 | 59345 (0.91 N) | 164 |
| 20 | 1 | 1024 | 1055 | 710 | 8.0 | 8.3 | 176494 (0.17 N) | 172 |
| 20 | 2 | 1448 | 2109 | 710 | 8.0 | 11.2 | 294155 (0.28 N) | 203 |
| 20 | 3 | 1774 | 3164 | 710 | 8.0 | 13.8 | 411816 (0.39 N) | 232 |
| 20 | 8 | 2896 | 8438 | 710 | 8.0 | 25.9 | 1000122 (0.95 N) | 345 |

Readings (all conditional on the recalled K_d):
1. The GS floor sits above E-WEIL-TIGHT (710 at 2^20; 142 at 2^16) and far above E-POWER and H1 at every size and d. So the census cannot read E-RANDOM, E-POWER or E-WEIL-TIGHT as defined in f6a43a. It reads only the band between the floor and Theorem W.
2. The candidate's "about 162x" is reproduced to order of magnitude (172x at d = 1, 203x at d = 2, 232x at d = 3 at p = 2^20); its exact constant 5.7(1+2 ln p) = 163.7 was not derived by this gate.
3. With K_d <= 4d+2, Theorem W is already about N at d = 8 and p = 2^20 (0.95 N), exceeds N at p = 2^12 for every d >= 1 (1.65 N at d = 1), and at p = 2^16 exceeds N from d = 3 (1.27 N). Where Theorem W says nothing, GS would be the only instrument for d >= 8. This is the strongest reason the delta is real. It is conditional on K_d, which is unretrieved.
4. First moment recomputed: p^{d+1} C(n_x, t) (2/p)^t with n_x = p/2, d = 2, t = 2048, p = 2^20 gives log2 about -19526. The candidate's "below 2^-10000" holds. This bound is for a random labelling and says nothing about the real curve; the real-curve statement is what the census would add.
5. At d = 2, d sqrt(N) = sqrt(2dN) = 2 sqrt(N) exactly: "exceeds Sudan's threshold" is strict only for d >= 3. Only the s = 1 Sudan variant is at issue; GS multiplicity lowers the floor to the Johnson value sqrt(dN).
6. Completeness lemma constants: beating rho needs N d / a < c_rho sqrt(N), i.e. a > d sqrt(N) / c_rho, with c_rho >= 1.03 in this ledger's measured baselines. The candidate's "only if a > d sqrt(N)" is therefore a necessary condition only up to the factor c_rho; harmless for d >= 2 against the Johnson floor, but it should be restated.

## 6. N2 analysis: known results

KR rows returned (see raw): KR-IC-5a43e5, KR-IC-955fd6, KR-RHO-ea34b8, KR-IC-49c882, KR-IC-5765d2, KR-RHO-46c2c6, KR-RHO-898783, KR-IC-081a58, KR-IC-5931ee, KR-RHO-53c89f, KR-RHO-6239aa, KR-RHO-6654ba, KR-IC-8b9daa, KR-RHO-fbd582, KR-IC-73db3f, KR-IC-889857, KR-IC-f5c584, KR-IC-1fcdbc. None states anything about polynomial agreement with, interpolation of, or list decoding for the elliptic discrete log. Scores come from the words "polynomial", "set", "multi-target", "precomputation". KR-RHO-ea34b8 (S T^2 = Omega(eN)) is the only row with bearing: the census needs the full log table (N-size advice), so it is a toy-tier measurement, not an attack, and the row is not violated. KR-RHO-13bf67 (generic bound) was not a top hit but is the relevant row for SO-GEN (KRMAP line 32). A KR hit means known_result unless something exact is new; here no KR hit is the object, so known_result is not the verdict via KRMAP.

Literature outside KRMAP (not in the frontier map; provenance stated per item):

| item | what it is | relation to the candidate | provenance |
|---|---|---|---|
| V. Guruswami, M. Sudan, IEEE Trans. Inf. Theory 45(6):1757-1767 (Sept 1999); ECCC TR98-043 (27 Jul 1998) | GS list decoding, threshold sqrt(kn) | the engine | retrieved (bibliographic details via web search; the sqrt(kn) threshold also appears in a secondary summary). The list-recovery / weights extension with l values per position and threshold sqrt(k l n): recalled, not retrieved. |
| C.-P. Jeannerod, V. Neiger, E. Schost, G. Villard, Computing minimal interpolation bases, arXiv 1512.03503 | cost O~(m^(omega-1)(sigma+|s|)) | engine cost | retrieved (arXiv abstract page via search). The candidate's end-to-end cost d N^((omega+1)/2) is its derivation, not checked here. |
| Roth-Ruckenstein root finding | polynomial root finding step | engine | recalled |
| D. Coppersmith, I. Shparlinski, On polynomial approximation of the discrete logarithm and the Diffie-Hellman mapping, J. Cryptology 13(3):339-360 (2000) | degree and agreement lower bounds for polynomials coinciding with DL mod p | prior art for "polynomial agreeing with a DL on a set" (F_p^*, not the elliptic group) | retrieved at bibliographic level only; content recalled |
| T. Lange, A. Winterhof, Polynomial interpolation of the elliptic curve and XTR discrete logarithm, COCOON 2002, LNCS 2387:137-143 | degree lower bounds for interpolating the EC DL | prior art for the object (degree side, not an agreement census) | retrieved at bibliographic level only; content recalled (cd1903 already searched it) |
| Kohel-Shparlinski exponential sums on elliptic curves; Ahmadi-Shparlinski arXiv:1302.4210 Lemma 1 | the mixed-sum bound behind Theorem W | basis of Theorem W | as recorded in H-ECDLP-f6a43a ("retrieved" for the d = 1 Lemma 1; general K_d "recalled"); not re-retrieved by this gate |
| Q. Cheng, On the bounded sum-of-digits discrete logarithm problem in Kummer and Artin-Schreier extensions, arXiv math/0311120 | GS list decoding as the main tool for DL with restricted exponents in F_{q^n} | precedent for GS applied to DL data, in a different group and to SOLVE, not to certify absence | retrieved (abstract only) |
| Q. Cheng, D. Wan, On the list and bounded distance decodability of Reed-Solomon codes, arXiv math/0405082 | RS list decoding beyond a radius is as hard as DL in finite fields | opposite direction (decoding hard because DL hard) | retrieved (abstract only) |
| F. Zhang, S. Liu, Solving ECDLP via list decoding, ePrint 2018/795 (corpus KN-LIT-643) | minimum-weight codewords of elliptic AG codes from the ECDLP | different object (code built from the instance) | corpus note, abstract-level, "reported" |
| Morillo-Rafols (KN-LIT-7066), Duc-Jetchev (KN-LIT-4155) | hard-core bits via list decoding | needs a predictor on all inputs; cd1903 already contrasts it with Theorem W | corpus notes |
| Bleichenbacher-Nguyen, noisy polynomial interpolation | GS-style noisy interpolation in crypto | related method | recalled, not searched |

One web search (standard mode) for "GS + polynomial agreeing with the discrete log graph on elliptic curve x-coordinate" returned nothing connecting GS to the elliptic log graph. Absence in one search is not proof of absence in the literature.

Conclusion of N2: no recorded result states the candidate's certificate. The topic (polynomial approximation of the DL, degree and agreement bounds) is classical and known, and the ledger already has the elliptic version (cd1903). So known_result is not the verdict, but the novelty is limited to the instrument and the band reading.

## 7. N3 ledger grep

Files grepped: ledger/.index/proposals.jsonl (2678 rows) and ledger/.index/hypotheses.jsonl (2131 rows). Index text fields are truncated (about 200 chars), so a zero count is weak. Terms and index-field hit counts (proposals / hypotheses): guruswami 0/0; sudan 0/0; polynomial reconstruction 0/0; list decod|recover 2/2 (both unrelated: SQIsign conversion-fibre syndrome IDEA-20260820-4467d2, IDEA-20260820-b87428, H-SQISIGN-8062ae, H-SQISIGN-ed6027); reed-solomon 2/0 (IDEA-20260816-7269da folding low-degree test; IDEA-20260816-b0322a HQC decoder; unrelated); A(d) 0/0; Theorem W 0/0; hint family 2/1; invertible half|hint 2/0; low-degree polynomial 5/1; interpolat 9/4; agreement 28/16.

Exact-path grep (12 files: f6a43a, 42f434, 03e287, 32e5d7, cd1903, 0c5564, 76df35, faca6f, 4c39d3, EV-ECDLP-924941, EV-ECDLP-8a5106, RQ-ECDLP-bc7a54) for guruswami|list decod|list recover|sudan|reed-solomon|polynomial reconstruction|Johnson|decoding|Berlekamp|Welch|Roth: the only hits are "list decod" at cd1903 line 593 (the Duc-Jetchev contrast entry) and "Lagrange" at line 394 (Stage 2 anomalous interpolation degree). So the GS engine is not in the ledger; the object is.

Ledger hits that may be the same object (id, 100-char claim):

- H-ECDLP-f6a43a [approved]: "SETTING (Stages 0-1 of IDEA-20261003-cd1903). Let E/F_p be ordinary of prime order n, g a generator,"  -> SAME object and pair; A(1) census by anchor-slope, E-RANDOM/E-POWER/E-WEIL-TIGHT, Theorem W, H1, H2.
- IDEA-20261003-cd1903 [proposed]: "WHICH SIDE. The impossibility side of the duality, in a NAMED MODEL. Model M_deg: omega is a polynom"  -> SAME model M_deg, Lemma V, Theorem W, H1, SLP-cheap ceiling.
- H-ECDLP-03e287 [specified] / IDEA-20261006-4c39d3 [proposed]: "For an ordinary prime-order subgroup of size N on a short-Weierstrass curve over F_p, the minimal to"  -> same object class, dual quantity (minimal interpolation degree on the small-x set vs a random labelling).
- IDEA-20261003-0c5564 / H-ECDLP-42f434 [approved]: "WHICH SIDE. Neither side is assumed: this record changes the OBJECT the RQ asks about. The note (sec"; "SETTING (Stages 0-1 of IDEA-20261003-0c5564). A hint family is a triple (D, chi, omega). Lemma V: a "  -> graded hint family, Lemma V; EV-ECDLP-8a5106 voided its planted control (O-ARTIFACT).
- IDEA-20261003-76df35 / H-ECDLP-32e5d7 [approved]: "WHICH SIDE. The impossibility side: the duality stated and proved in a named model, with a toy certi"  -> uncertainty principle, Wiener norms (mixed spectrum), the other half of the same RQ.
- IDEA-20260920-faca6f [proposed]: "(A) THE GAP. RQ-ECDLP-bc7a54's decision_target (a) is \"record the lane as closed with a MEASURED or "  -> hint-family detector calibration against anomalous curves (a real hint family); relevant as the positive-control design.
- IDEA-20261016-0bacee [proposed]: "O = any cheap procedure outputting one candidate for dlog_P(R) (the lane's Smart ratio), success rat"  -> the break-even line c/sqrt(n) and random self-reduction collision test; this is the candidate's completeness lemma in general form.
- IDEA-20260806-c5d183, IDEA-20260901-863e36: rigidity records (N4).
- IDEA-20261017-e3a6f1 [proposed]: "E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni"  -> B7 arm source.
- IDEA-20260807-631e80, IDEA-20260906-7304fe: not the same object (isogeny-class self-reduction; function-field section interpolation-defect kernels).

Ledger records opened: read in full: H-ECDLP-f6a43a; EV-ECDLP-8a5106 (evidence, 3 KB). Read in part: IDEA-20261003-cd1903 (lines 1-60, 380-400, 575-610 plus grep lines), IDEA-20261006-4c39d3 (lines 1-70), IDEA-20261016-0bacee (lines 1-40). Others: index rows only. This is more than three partial reads; no ledger directory was listed.

EV-ECDLP-8a5106 matters for instrument validity: it is the voided planted control of the H-ECDLP-42f434 line (planted kangaroo/rho null, M4 missed its 0.10 band, O-ARTIFACT). It is not the candidate's NULL-1 polynomial-planting control, so it neither supports nor weakens it; it shows that this program's planted controls have voided runs, so the 1.2t recovery check carries real weight.

## 8. N4 notation check

Pair (representation, operation set) of the candidate: representation = R1, the affine x coordinate with the integer lift of log_g Q (mod p; values in [N, p) cannot agree when p > N); operation set = evaluation of a degree-<=d polynomial F on x, agreement tested by equality of integer lifts, membership decided by [F(x)]G == Q (Lemma V). Translation is not in the operation set; negation enters only through x(-Q) = x(Q) with log(-Q) = N - log Q (the "two values per abscissa"). Class III, coordinate-dependent.

This is exactly the pair recorded in H-ECDLP-f6a43a ("Representation R1: affine x-coordinate with integer lifts. Operation set: degree-bounded polynomial evaluation on x (not the translation action). Class III"). There is no notation change; nothing is renamed to a new pair.

- IDEA-20260806-c5d183 (index title: no lossy ECDLP object propagates deterministically under the FULL translation action; object-frame doc: such a projection on a prime-order group is constant or injective). Hypothesis = propagation under full translation. The candidate's operation set has no translation, and it claims no propagating projection, so the theorem neither forbids nor supports it; it is the same status as f6a43a's. Not a rigidity result being re-stated: the candidate's claim is a measurement claim inside M_deg.
- IDEA-20260901-863e36 (propagation is a property of a projection PAIRED with an operation group; Gamma-orbit tracked object). The candidate's pair carries no Gamma-action; the pairing principle is satisfied (pair stated), no rigidity statement is being circumvented.
- KN-OPEN-020 (read in full): bounded-degree algebraic factor bases are scoped out (Bezout: O(d) points for a degree-d locus); open: "high-degree interpolation descriptions, multiple constructible predicates, target-dependent descriptions, and implicit membership or source-recovery algorithms". The candidate's D_F is an implicit-membership, target-independent set described by a degree-d interpolant; it lies in the open class by description type, but it is a hint family, not a factor base, and the census does not use it for relation generation. Heuristic G3 below: a degree-d F with agreement >= d sqrt(N) would carry >= sqrt(N) agreeing points per coefficient, versus 3 per degree for the algebraic loci of the KN-OPEN-020 bounded-degree theorem; this contrast is a heuristic, not a theorem, and it is not a statement about D_F-based IC.
- KN-FIND-ffe1df Theorem C (read lines 194-232): exact sum-compatible quasigroup combining forces a homomorphism, impossible for N prime. The candidate does no combining, so Theorem C does not apply. The "additive completion" paragraph of the same finding uses the same additive-character route as Theorem W, conditional on (H1'); related method, different claim.

Net: not a recorded rigidity result in new notation, and not escaping one either. It is a measurement in an existing recorded model.

## 9. Review items for the candidate (conditional, not outcomes)

R1. Completeness lemma is cd1903 Lemma V + IDEA-20261016-0bacee; restate with the rho constant (section 5, item 6) and at d = 2 the s = 1 Sudan threshold equals d sqrt(N), not exceeds it.
R2. The SLP-cheap blind spot (c(F) sqrt(N) < a < sqrt(deg F N)) is the ceiling cd1903 names ("Smart / Semaev-Satoh-Araki"; anomalous curves). Not a candidate finding.
R3. Planted recovery at 1.2t tests sensitivity at or above the floor only; it supports no claim below the floor. The pilot results (18/18 empty on real curves, 18/18 planted recovered, bits 9-11) are the candidate's claims; this gate did not run them. The pilot script exists at scout/coding-isd/check_c2_gs_pilot.py (header read: Sudan s = 1, dense kernel, planted control on a NULL-1 relabelling); not executed.
R4. Disposition over-scope (section 0, last bullet). Also "d up to floor(sqrt N)" ladder: for d > sqrt(N) the rho-beating condition a > d sqrt(N) exceeds N and is vacuous, so the ladder is complete in that sense (candidate's own reading, not checked).
R5. B7 secondary arm: under-specified field and lift, and downstream of the K2 check in LEAD-EXO-miller-pairing-cocycle; do not schedule before that.
R6. SO-TORS listing in so_codes_touched is not on point; SO-GEN/SO-AUG (x-oracle GGM-simulable) is the relevant standing obstruction and predicts the null.
R7. Crypto-size statements (the window (1/2, 3/4]) rest on H1 (= H-C2.1), which the census cannot measure; at crypto size that window is exactly as open as in cd1903.

## 10. Gate heuristics used (numbered)

G1. When the candidate's (representation, operation set) pair and its stated bottleneck lead coincide with a recorded hypothesis's pair, the object is identical and the question is only whether the instrument or the reading is new.
G2. A certificate that begins above a lead's scored thresholds cannot read that lead's scored outcomes; it can only add outcomes outside them.
G3. High-degree-description contrast with KN-OPEN-020 (section 8) is heuristic only.
G4. A lexical zero in a truncated index is weak evidence of absence; exact-path greps and full-record reads were used where the object was known.
G5. Pilot and predicted numbers in the candidate are claims; only section 5 numbers were produced by this gate.
