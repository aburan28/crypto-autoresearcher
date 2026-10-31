# Novelty gate N1-N4: C1 Corner lemma (strategy-independent Howgrave-Graham ceiling, prime field)

Date 2026-10-24. Gate run by a scout subagent. Nothing was written inside the repositories (checked: no file under /Volumes/SSD990-2/crypto-autoresearcher newer than the run, no new __pycache__). Env: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as instructed. Claim tier of everything below: analysis. No speedup is claimed; nothing here is a measured outcome of an attack.

## N1 raw output: python3 tools/lead_atlas.py --match (5 runs: the 3 match_phrasings, then 2 of my own)

### lead_atlas run 1: corner lemma: Howgrave-Graham determinant ceiling D*log_p(volume) < 1 for summation-polynomial small roots, any shift set
```
    8  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    7  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    6  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    6  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    6  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
    6  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
    5  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
    5  LEAD-ICB-quasi-subfield-polynomials          closed_obstructed  Quasi-subfield-polynomial factor bases (Huang-Kosters-Petit-Yeo-Yun; Euler-Petit) at prime extension degree, ECC2K-130
```

### lead_atlas run 2: no Coppersmith-style lattice can find small-x point decompositions for any factor base shape
```
   18  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   14  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   12  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   12  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   11  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
```

### lead_atlas run 3: lattice-describable base of size B: decomposition oracle capped by leading-monomial weight while mean yield binomial(B+m-1,m)/N is fixed
```
   19  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
   13  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
   13  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
   12  LEAD-ICB-tau-horner-chain                    open_next_step     tau-Horner decomposition chain on Koblitz curves (R = tau^{m-1}P_1 + ... + P_m over one base)
   12  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   12  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   11  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
   11  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
```

### lead_atlas run 4: (own) Howgrave-Graham lattice small root multivariate modular polynomial determinant bound Jochemsz-May Semaev summation polynomial
```
   14  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   14  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   13  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   12  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
   10  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    9  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    9  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    9  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
```

### lead_atlas run 5: (own) Farey rational reconstruction height-minimal representative of x-coordinate digit lattice presentation factor base small-root bound
```
   17  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   13  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   10  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   10  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   10  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
```

## N2 raw output: python3 tools/build_frontier_map.py --match (same 4 phrasings)

### build_frontier_map run 1
```
KR-IC-5931ee  score=4  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-73db3f  score=3  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-46c2c6  score=3  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-898783  score=3  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
```

### build_frontier_map run 2
```
KR-IC-5a43e5  score=11  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-6654ba  score=7  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-955fd6  score=5  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
```

### build_frontier_map run 3
```
KR-IC-46d822  score=9  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5a43e5  score=7  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-b0fcda  score=6  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-081a58  score=5  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-1fcdbc  score=5  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-73db3f  score=5  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
```

### build_frontier_map run 4
```
KR-IC-5a43e5  score=14  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5931ee  score=13  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-1fcdbc  score=9  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-889857  score=8  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-73db3f  score=7  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
```

## N1 reading of the hits (mechanism + obstruction + forecloses read from the lead YAMLs)

Hits read: the tool printed 8 rows per run. For every distinct lead among those rows I opened the lead YAML and read mechanism, disposition, obstruction (where present), next_action/best_measured and forecloses (the last six read after a review pass: mov, frobenius-orbit, hnp-advice-leakage, quasi-subfield-polynomials, kic-golden-base, isogeny-transported-relation-yield; LEAD-EXO-augmented-oracle-ggm and LEAD-RHO-generic-sqrt-lower-bound read for the SO quotes below). KR rows appear in runs 1-5 as well; they are dismissed in N2.

| lead | disposition | same mechanism? | note |
|---|---|---|---|
| LEAD-ICP-coppersmith-smallroot-semaev | open_next_step | YES (same object) | Mechanism: small-x/windowed factor base turns decomposition into a multivariate small-root problem for S_{m+1}, cost set by lattice reach. next_action: "Compute the provably optimal shift set (Ryan, EUROCRYPT 2025; Feng-Luo-Chen-Nitaj-Pan sumset bounds) for the 13-monomial S_3 polytope and the full-tree (m, w) = (4, 2) system, and the rank-r >= 2 GAP substitution of H-PFDR-3c7d1e". discriminates: "optimal reach < 0.8889 everywhere turns the current heuristic -0.0481 closure into a strategy-independent one and closes the family." best_measured: eps margin -0.0481 at (m,w)=(4,2). It has no obstruction block (open lead). forecloses: Coppersmith small roots of summation polynomials; small-x factor base solved by LLL; windowed addition tree with lattice reduction; symmetric e1 e2 lattice for S_3; rank-r generalized arithmetic progression factor base; lattice-assisted meet-in-the-middle decomposition. |
| LEAD-ICP-lattice-ic-relation-construction | open_blocked | NO, except the "Newton shift certificates for small-window decompositions" clause | Mechanism: ideal/quaternion lattices, isogeny-adjoint witnesses as relation constructors, not point decomposition. The candidate claims to decide its "polynomial lane" (IDEA-20261015-9defe9). I did not open that proposal (3-record cap); the claim is unverified by me. |
| LEAD-ICP-generic-table-decomposition (SO-TABLE) | closed_obstructed | NO | Obstruction (theorem): "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup) ... Scope: any generic (enumeration/table) decomposition over F_p." revisit_when: "A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4 ... or a decomposition test sub-linear in |F|." The candidate does not claim to meet revisit_when; it claims a cap on the only non-enumerative oracle class the lead names (HG lattice). Consistent, not an escape. |
| LEAD-ICP-algebraic-membership-factor-base (SO-ALGFB) | closed_obstructed | NO (adjacent class) | Obstruction (theorem): "A target-independent algebraic locus of degree d yields O(d) usable points ... mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation ...). Scope: prime-order E/F_p, any base of size B." revisit_when: "KN-OPEN-020 is answered positively". The lattice-describable class (membership = archimedean inequality) is the open class that obstruction scopes out; the candidate's result lives inside it and uses the same conservation clause for the demand. |
| LEAD-RHO-generic-sqrt-lower-bound (SO-GEN) | closed_obstructed | NO | Obstruction (theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant ... Scope: all generic algorithms, any field, any r." revisit_when: "Never for generic algorithms; only a method that reads the representation (index calculus, transfer) can change the exponent." The candidate reads the representation (x as an integer) and claims no exponent change; it is a cap on that representation-reading oracle. Not an escape claim. |
| LEAD-EXO-augmented-oracle-ggm (SO-GEN) | closed_obstructed | NO | Obstruction (theorem): "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 ... Scope: oracles, not resources". The HG lattice oracle is not in the named list; a lattice oracle reading the integer representation is not an "augmented oracle" in that sense. The candidate claims no sub-1/2 exponent, so the lead is neither triggered nor answered. |
| LEAD-ICE-generic-oracle-arity-cost-floor, LEAD-ICB-generic-table-oracle, LEAD-ICE-rootfind-pairtable-oracle | closed_obstructed / open_blocked | NO | enumeration / MITM / pair-table oracles. The first two state revisit_when "an oracle that reads coordinates with per-query cost polynomial in n at fixed degree ... is measured" (arity-cost-floor) and "an oracle that is not generic (algebraic restriction on the unknowns ...)" (generic-table-oracle). An HG lattice oracle is such a coordinate-reading oracle; these leads do not foreclose it. |
| LEAD-ICP-digit-presentation-solving-degree | open_next_step | NO | digit presentation + Groebner first/last fall degree, not HG lattices. The candidate's "digit presentations" are lattice presentations of the same unknowns; different oracle. |
| LEAD-EXO-invertible-hint-subset, LEAD-EXO-dl-character-sum-pseudorandom, LEAD-STR-small-cm-disc-nonunit-endo, LEAD-TRF-mov-small-embedding-degree, LEAD-EXO-hnp-advice-leakage, LEAD-ICB-quasi-subfield-polynomials, LEAD-ICB-cofactor-torsion-quotients, LEAD-STR-class-representative-ic-selection, LEAD-ICE-decomposition-probability-audit, LEAD-ICE-semaev-yield-model-coset-typing, LEAD-ICB-tau-horner-chain, LEAD-STR-special-j-ic-semaev, LEAD-ICB-factor-base-subspace-choice, LEAD-ICP-icperf-writability-boundary | various | NO | lexical overlap only (structured factor base, yield conservation, Semaev support). None describes a determinant/leading-monomial bound on lattices. LEAD-ICE-decomposition-probability-audit and LEAD-ICE-semaev-yield-model-coset-typing both rest on KN-FIND-007 (mean yield fixed), which the candidate uses as its demand side, not as its result. |

### What the candidate does that the forecloses phrases do not cover (N1)

The six forecloses phrases of LEAD-ICP-coppersmith-smallroot-semaev name attack shapes. The lead's closure (analysis/smallroot-reach/CLOSURE.md) is stated for ONE strategy (Jochemsz-May extended, heuristic, algebraic independence assumed), for binary addition trees and rank-1 GAPs; its own section 6 lists rank-r >= 2 GAPs, non-tree strategies, superpolynomial dimension (IDEA-20260808-e2315e) and "the heuristic itself" as open. The candidate adds a quantifier those phrases do not carry: a determinant-level cap that holds for every shift set, every t, every monomial support M built from (f,p)^t, for single-equation cells (w = 0), for every GAP rank, Farey and digit presentations, and for superpolynomial dimension. That is a strictly stronger STATEMENT about the same mechanism, so it is not a lexical miss on a new mechanism; it is a sharper next step of an open lead.

What it does NOT cover (stated by the candidate itself): addition trees with kept windowed nodes (w > 0). The lead's decisive discriminator sits at (m,w) = (4,2), margin -0.0481 in CLOSURE.md, and the candidate leaves that cell to a separate candidate (C2). In CLOSURE.md the w = 0 cell at m = 4 was already heuristically closed with margin -0.4271 (the w = 1 cell, margin -0.4196, is outside the candidate's scope); the live cell is (4,2) at -0.0481. So the candidate upgrades the farthest-from-alive cells from heuristic to determinant-level theorem (conditional on H1 and on the corner premise) and moves the open cell by zero. Its stated outcome "LEAD-ICP-coppersmith-smallroot-semaev closed_obstructed(theorem) for all w=0 cells" cannot close the lead; the lead stays open_next_step until the (4,2) cell is decided.

## N2 reading

- KR-IC-5a43e5 (Semaev summation polynomials, known_mechanism/proven): framework row; its text says novelty "must lie in representation, factor base, elimination or solver". Not a hit on the claim.
- KR-IC-5931ee (known_negative/proven): "Yokoyama-Yasuda-Takahashi-Kogure prove, under stated statistical assumptions, that Semaev's naive index calculus over F_p costs at least as much as generic algorithms; algebraic factor bases ... work only at small parameters; McGuire-Mueller's Groebner-free variant is reported still worse than rho." Scope is Groebner-type naive Semaev IC and algebraic bases. It does not state or imply a lattice small-root ceiling, so it does not subsume the candidate; it is the general-context negative the lead already cites.
- Remaining KR rows in the top 5 of runs 1-4, one line each (none is about lattice small roots, leading monomials or Howgrave-Graham):
  - KR-IC-46d822 Gaudry decomposition over E(F_{q^n}), n fixed: extension-field Weil restriction, Groebner-type, not an F_p lattice ceiling.
  - KR-IC-73db3f factor-base vector-space choice (small product spaces): binary-field subspaces; no F_p lattice statement.
  - KR-IC-b0fcda Frobenius-invariant bases (GGMP): subfield curves, n-fold saving; unrelated.
  - KR-IC-791cb7 weak binary fields under GHS: binary / transfer; unrelated.
  - KR-IC-49c882 quasi-subfield polynomials: binary factor base degree; unrelated.
  - KR-IC-5765d2 SAT/XOR decomposition: char 2 solver; unrelated.
  - KR-IC-955fd6 symmetries and torsion speed up decomposition: constant factor on a Groebner-type step; unrelated.
  - KR-IC-8b9daa Karabina symmetric formulation: binary PDP constant/polynomial factor; unrelated.
  - KR-IC-081a58 Joux-Vitse n-1 decomposition: F_{q^n}, n >= 5; unrelated.
  - KR-IC-1fcdbc char-2 summation algorithms slower than rho: measured negative for binary; unrelated to lattice ceilings.
  - KR-IC-889857 subexponential binary ECDLP under first-fall-degree assumption (disputed): solving-degree assumption, not lattice reach.
  - KR-IC-fbdb61 last fall degree of Weil descent systems: solving-degree theory (Groebner), the quantity the lead says a lattice solver does not pay.
  - KR-RHO-ea34b8 precomputation l^{1/3} / S*T^2 lower bound and KR-RHO-13bf67 generic-group lower bound: the generic side (SO-TABLE, SO-GEN); the candidate is not a generic algorithm and does not touch them.
  - KR-RHO-53c89f transfer attacks (MOV, anomalous), KR-RHO-6654ba point halving, KR-RHO-46c2c6 multi-target, KR-RHO-898783 interval DLP: different bottleneck lanes.
- No KRMAP row mentions Coppersmith, Howgrave-Graham, small roots, Jochemsz-May, LLL, Herrmann-May, Bauer-Joux or Ryan (grep of KRMAP.md for those terms: zero hits). So the map has NO known-result row for the object. That is a gap in the map, not evidence of novelty (see literature check).
- Literature check (WebSearch + WebFetch were available; provenance below is what I actually read):
  - Aono, Agrawal, Satoh, Watanabe, "On the Optimality of Lattices for the Coppersmith Technique", ACISP 2012 / ePrint 2012/108 [retrieved: ePrint abstract page fetched 2026-10-24]. Abstract: upper bound on the solution range for univariate modular equations asymptotically equal to Coppersmith's; optimality for the bivariate Boneh-Durfee equation; a framework built on Howgrave-Graham's relation with conditions for success or failure. The abstract does not mention more than two variables. A search snippet quoting CHHS says the optimality is under a random-lattice heuristic (second-hand, [retrieved] via search only). I did NOT read the paper body, so whether a multivariate leading-term bound is in its text is unverified.
  - Chinburg, Hemenway, Heninger, Scherr, capacity-theory optimality of Coppersmith, arXiv 1605.08065 / ePrint 2016/869 [retrieved: search results, abstract-level; the result is univariate, no auxiliary polynomial of Coppersmith's type reaches N^{1/d+eps}; the iacr.org cryptodb ASIACRYPT 2016 presentation appears in the results, consistent with the ASIACRYPT 2016 venue]. Already in the corpus as KN-LIT-3299 (title and contribution only). The authors list bivariate and multivariate as future work (search summary). Related: Chinburg et al., "Two variable polynomial congruences and capacity theory", arXiv 2111.14180 [retrieved: abstract page]; it shows the method succeeds on a positive proportion of linear two-variable congruences and fails on another positive proportion; the abstract claims no impossibility for all Coppersmith-type methods.
  - Ryan, "Solving Multivariate Coppersmith Problems with Known Moduli", EUROCRYPT 2025, LNCS 15606 pp. 355-384, ePrint 2024/1577 [retrieved: ePrint abstract page fetched; venue and pages from a search result]. Abstract: Groebner-based algorithm computing an optimal shift set plus a lattice provably containing all desired short vectors; no ceiling or impossibility statement in the abstract. Whether the provable lattice is the full ideal lattice restricted to a monomial set is not stated in the abstract; the full text was not read, so the candidate's remark that Lemma A "covers" Ryan's optimal lattice is unverified by me.
  - Jochemsz-May 2006, Herrmann-May 2009/2010, Bauer-Joux 2007: recalled, not re-checked.
  Verdict of the N2 literature check: no known-result row in the map; the nearest literature (Aono et al. ACISP 2012; CHHS) proves related optimality for one and two variables and is already partially in the corpus. The multivariate leading-monomial form is not in the abstracts I read. That is "not found at abstract depth", not "absent". The candidate's own dossier (section 2.7) rates novelty unverified and "best read as an adaptation"; I agree.

## N3 ledger (grep of ledger/.index/{proposals,hypotheses}.jsonl on title/claim/mechanism fields; index claim fields are truncated to about 200 characters, so a lexical miss proves little)

Terms tried: corner, leading monomial, howgrave, coppersmith, small-root, jochemsz|herrmann|bauer-joux, reach, regular sequence, shift set, GAP, lattice-describable, ceiling, determinant, strategy-independent, optimality|aono|chinburg|capacity theory|optimal shift, sumset, Newton polytope, box volume. Zero hits for: strategy-independent, aono/chinburg/capacity theory/optimal shift, box volume, ryan/cuso (as index terms).

Hits that may be the same object (id + 100-char claim/title):
- IDEA-20260904-39336c  "THE CLOSURE'S SUPPLY NUMBER IS ONE STRATEGY'S VALUE, NOT AN OPTIMUM, AND THE GAP IS 0.1592 WHILE THE MISS IS 0.0481: run the 2024-2026 prove..." (proposed, never run). Same goal (strategy-independent closure), computational route (Ryan, sumset) instead of a lemma. NEAREST RECORD.
- IDEA-20260808-e2315e  "Superpolynomial-dimension small-root solving: treat the Coppersmith shift-lattice dimension as a cost..." (unverified, never executed). The candidate claims to decide it negatively for w = 0.
- IDEA-20260808-c31f1c  "Beyond intervals: rank-r generalized arithmetic progressions are the full lattice-describable factor base..." (screened).
- IDEA-20260808-486ae2  "Windowed-tree point decomposition: the only factor-base family the algebraic no-go leaves open is th..." (unverified).
- IDEA-20260903-81a943  "The lattice-describable factor base is closed: small-root reach and index-calculus demand are monotone..." (the CLOSURE.md record).
- IDEA-20260904-8dccc9  "THE WINDOW DOES NOT HAVE TO BE ONE UNKNOWN: re-parametrizing the SAME interval factor base by r bounded..." (rank-r at the (4,2) cell).
- H-PFDR-3c7d1e  "The rank-1 closure of the lattice-describable factor-base family ... does NOT extend to rank-r >= 2 GAPs" (proposed). Its cells are the all-S_3 trees (w >= 1), outside the candidate's w = 0 scope.
- H-PFDR-621852  "Direct-box S4/S5 planted recovery with exact modular Jochemsz-May lattices and finite ideal extraction" (proposed). The empirical counterpart of the candidate's w = 0 cells.
- IDEA-20261009-85062c  "Small-root threshold for size-constrained decomposition (Coppersmith on S_3, S_4)" (unverified); IDEA-20260816-a321ac "Test whether achievable reach is a function of the Howgrave-Graham slack alone..."; IDEA-20260901-c75e81 "THE DIMENSION COST OF APPROACHING A SMALL-ROOT BOUND HAS AN EXPONENT AND NOBODY QUOTES IT..."; IDEA-20260913-c5f90d "F_p DOES HAVE A SIZE FUNCTION AND IT PUTS PRIME-FIELD INDEX CALCULUS EXACTLY ON THE SMALL-ROOT BOUND" (Farey / height-minimal representative); IDEA-20260923-9e4b71 "THE PREPROCESSING RE-READING OF THE SMALL-ROOT CLOSURE: in the S*T^2 model..." (not opened); IDEA-20261015-9defe9 "R1 relation-solving comparison: dense versus Newton-target shifted lattices..." (not opened).
- IDEA-20260723-006  "Corner-coefficient induction and exceptional-target saturation theorem" and IDEA-20260808-0e9fa1 "Rigorous windowed yield via the determinant method" are INGREDIENT or ADJACENT records, not the same object (see below).

Full records opened (3, by exact path):
1. ledger/proposals/IDEA-20260904-39336c.yaml (first 14 KB of 33 KB). Its claim (F2): JM prescribes one shift set; Ryan 2024/1577 computes an optimal one; eps_opt(S_3) and eps_opt(joint three-equation system at (4,2)) are "computable today with published tools" and the family is alive iff either exceeds 8/9. Its own novelty screen: eprint was blocked in that container, Ryan and Feng et al. read at abstract/snippet depth. This is the record the candidate advances: it proposes a computation per cell; the candidate proposes a lemma that bounds every cell with a full corner at once and needs no shift-set computation. They agree on the target and differ in route; the candidate does not reach the joint-system cell (F3).
2. ledger/proposals/IDEA-20260723-006.yaml (full). The corner-coefficient induction there is a BKK/Newton-polytope negative gate ("the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m)-sized exceptional target set"), disposition support, scoped negative. It is the ingredient the candidate cites for corner coefficient 1; it says nothing about Howgrave-Graham lattices. The candidate's Lemma B plus the averaging step is the new use; the corner premise itself is not new.
3. ledger/hypotheses/H-PFDR-3c7d1e.yaml (first 10 KB of 30 KB). Rank-r GAP substitution; predicted eps_naive(r=2) = 9/7 > 1 for the all-S_3 configuration; names attainment (not the polytope) as the residual obstruction. Different cells (w >= 1) from the candidate's w = 0; the candidate's "rank-independence" statement does not touch this hypothesis's cells. The candidate's claim to decide H-PFDR-3c7d1e is therefore NOT supported by the w = 0 lemma alone.

N3 decision: no ledger record states the leading-monomial ceiling or a strategy-independent HG bound. The nearest record (IDEA-20260904-39336c) has the same purpose by a computational route; the candidate is a sharper, cheaper route for the single-equation part, not a duplicate record.

## N4 notation check

Pair: (R1 = integer / Farey / rank-r GAP / digit representative of x(P) in F_p; Sigma = translation by factor-base elements; oracle = HG lattice built from (S_{m+1}(.; x_R), p)^t). Candidate's trichotomy class: partial-action (IC Class I) with a coordinate-dependent membership component.

Comparison with the recorded rigidity results:
- IDEA-20260806-c5d183: theorem that a projection pi: G -> S propagating deterministically under FULL translation is constant or injective (G prime order). It classifies projections. The candidate does not claim a lossy projection propagating under all translations; its Sigma is the partial set (factor-base translations), which is exactly the Class I escape that record names. No overlap in statement.
- IDEA-20260901-863e36: propagation is a property of (projection, operation group); lossy objects = block systems of the group action; translation slice reproduces the rigidity theorem. The candidate's statement is not a block-system classification; it bounds an oracle (a lattice) acting on a fixed representation. No overlap.
- KN-OPEN-020 / LEAD-ICP-algebraic-membership-factor-base: bounded-degree algebraic factor bases are scoped out; the open class is high-degree, implicit-membership or target-dependent. The candidate sits in the implicit-membership class (membership = archimedean inequality). If the lemma holds, it closes a sub-class of what KN-OPEN-020 left open (lattice-describable) at determinant level; it is a refinement of that open class's status, not a restatement of the algebraic-factor-base theorem. It does re-use the conservation clause (KN-FIND-007) for demand.
- KN-FIND-ffe1df Theorem C (exact sum-compatible filter plus associativity forces a homomorphism, impossible for prime N, M < N): statement about exact filters/quasigroup combining. Different object; no overlap.
Conclusion: the candidate is not a recorded rigidity result in new notation. Condition: that holds only for the w = 0, direct-box reading; the closure of the (4,2) cell would be a separate question.

## Numerics observation that bears on how the margins are read (NOT part of the gate verdict; unadjudicated)

While checking the candidate's table against CLOSURE.md I ran tools/smallroot_reach.py functions (imported without writing bytecode) on three full boxes. In jm_reach_extended the returned p-exponent s_p equals sum over box monomials of (t - k(a)), with k(a) = floor(min(a)/d), not sum of k(a):

| n, d, t | calculator s_p | sum k(a) | sum (t-k(a)) |
|---|---|---|---|
| 2, 1, 8 | 444 | 204 | 444 |
| 2, 2, 6 | 728 | 286 | 728 |
| 3, 2, 4 | 2420 | 496 | 2420 |

My reading of the Howgrave-Graham inequality for shifts x^{a-jd} f^j p^{t-j} (j = k(a)) is: det exponent in p = sum (t-j), right-hand side = t*dim - that = sum k(a). For n = 1 the two sums agree to leading order, which would make the univariate 1/d calibration unable to detect the difference. For multivariate full boxes they differ by a factor tending to n. Consequences, all labelled as observations from the calculator output:
- The calculator's closed form gives eps = 4/3 for (n=2, d=1), above the information ceiling eps = 1 that CLOSURE.md says is never exceeded.
- With the sum-k reading the full-box sum-exponent is 2/(d(n+1)): 1/3 for (n=2,d=2). The candidate's exact dim V_k probe gives 0.294 at L=16 tending to 1/3 for that object, and the lead's own best_measured "heuristic 0.12-0.16" (read as per variable, since its stated need is 1/2 = demand 1 over 2 unknowns; sum 0.24-0.32) is on the same scale; the calculator gives sum 0.674 (0.337 per variable) for it.
- CLOSURE.md's 0.8408 for the 3-variable S_3 block divided by 3 is 0.2803, the value the candidate's dossier quotes as "JM gives 0.2803, which is consistent", without remarking the factor 3.
Status: derived from reading code and three toy counts; I did not run lattice reduction, did not recompute the sparse 13-monomial JM-extended value, and did not consult the Jochemsz-May paper (the extended strategy's set definitions could make the calculator's indexing legitimate in cases I did not test). If the factor-n reading is right, CLOSURE.md's supply numbers are over-credited toward the attack (the closure would be stronger, not weaker), but the lead's discriminating quantity "reach >= 0.8889 at (4,2)" would then be measured in the wrong unit. The parent should adjudicate this before scoring C1 or C2 against -0.0481.

## Conditions and numbered heuristics

H1. The lemma is determinant-level (Gaussian-heuristic) like every reach in CLOSURE.md; a structurally short vector with no determinant reason is not excluded (candidate's own self_kill_risk). Any "closure" from it is conditional on H1.
H2. The corner premise (the full-box corner of S_{m+1}(.; x_R) has coefficient 1, leading monomial in every order) is the candidate's own induction plus a numeric check for m <= 4 (S_5 at one prime, 3 draws); IDEA-20260723-006 is the only ledger precedent and it is a BKK gate. I did not re-derive it.
H3. Aono et al. and CHHS prove related optimality for one and two variables; a multivariate leading-term version in their full texts, or in Ryan's, is not excluded by what I read (abstracts only). If it exists, the verdict moves toward known_result.
H4. The claim covers w = 0 only. Any statement about LEAD-ICP-coppersmith-smallroot-semaev as a whole, H-PFDR-3c7d1e, or the polynomial lane of LEAD-ICP-lattice-ic-relation-construction needs the w > 0 cells (or, for the last, a read of IDEA-20261015-9defe9, which I did not open).

## Verdict

advances_lead. Lead: LEAD-ICP-coppersmith-smallroot-semaev (open_next_step), nearest ledger record IDEA-20260904-39336c. The candidate is a lemma-route alternative to the lead's own next_action (compute the provably optimal shift set), covering the single-equation (w = 0) cells for all GAP ranks and presentations; it does not decide the (m,w) = (4,2) cell that the lead's discriminator names, so it does not close the lead. No KR row subsumes it (the map has no Coppersmith row), and no ledger record states it, but it is literature-adjacent (Aono et al. 2012 for one and two variables; CHHS 2016 univariate) and its novelty is unverified beyond abstract level.
