# Novelty gate N1-N4: C5 "Rank-bounded, block-streamed, copy-free MutantXL closure memory (217 GB -> <=79 GB at the blocked C1 cell), plus a separator/Krylov certificate of w on the same matrices"

Field key: HPC constants (memory hierarchy, batched-inversion scheduling, SIMD/field-op pricing, GF(2)/GF(p) linear algebra, bit-sliced arithmetic, rho step vs IC relation cost at matched hardware) - round 2.
Gate run 2026-10-25. Read-only on both repositories; everything here was written under the scout directory only.
Environment exported before the tool runs: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES as specified. Working directory /Volumes/SSD990-2/crypto-autoresearcher.

Provenance convention: [retrieved] = read from a file or web page in this session; [recalled] = from memory, not re-read. Predictions are labelled PREDICTION; heuristics are numbered H1..Hn; conditional claims stay conditional.

## 0. Raw tool output (verbatim; raw files kept in /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/_c5gate_raw/)

### 0.1  python3 tools/lead_atlas.py --match "rank-bounded streaming echelon closure holds at most rank times columns bits, plus separator tree and Krylov dimension certificate of the Macaulay closure"
```
    7  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    6  KR-IC-e847d1                                 known_result       Crossbred algorithm for Boolean systems
    6  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    5  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    5  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
    5  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    4  KR-RHO-cb1c58                                known_result       Simultaneous (batched) inversion
    4  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)
```

### 0.2  python3 tools/lead_atlas.py --match "run the degree-5 descended Semaev closure in under 72 GB instead of 217 GB and measure whether a sparse closure can avoid quadratic cost"
```
   10  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    9  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    9  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
    8  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    8  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    7  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    7  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    7  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
```

### 0.3  python3 tools/lead_atlas.py --match "memory column for block Wiedemann at the cap locus; descended ANF exceeds the per-decomposition rho budget; closure degree stays 4; 250 GB host or a sparse closure"
```
   33  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
   18  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
   18  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   14  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    9  LEAD-ICB-generic-table-oracle                closed_obstructed  Generic decomposition oracles for Koblitz IC: pair tables, compact-orbit 4-sum, MITM and enumeration, cap-locus arity, known-log pools
    9  LEAD-ICE-hybrid-guess-determine-l7           open_next_step     One-variable specialisation priced as hybrid guess-and-determine on the l = 7 descent cells
    8  KR-RHO-fbd7b1                                known_result       Grumpy giants and better-than-rho generic ordering
    8  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
```

### 0.4  python3 tools/lead_atlas.py --match "Macaulay closure memory MutantXL descended Semaev F2 elimination blocked streaming"
```
   12  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   11  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
   10  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
   10  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    9  LEAD-ICE-semaev-chain-cost-model             closed_obstructed  Chain length t, merge-tree topology and memory charging in Semaev's charged cost
    7  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    7  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    6  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
```

### 0.5  python3 tools/build_frontier_map.py --match "rank-bounded streaming echelon closure holds at most rank times columns bits, plus separator tree and Krylov dimension certificate of the Macaulay closure"
```
KR-IC-e847d1  score=6  [known_mechanism/reported]  Crossbred algorithm for Boolean systems
    sources: KN-LIT-139
KR-RHO-cb1c58  score=4  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-IC-0d2021  score=3  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-cd159a  score=3  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
KR-RHO-1c2928  score=2  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-73db3f  score=1  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-791cb7  score=1  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-38be82  score=1  [known_mechanism/reported]  Tag tracing and table-driven step shortcuts
    sources: KN-LIT-93696f, KN-LIT-20ef89
```

### 0.6  python3 tools/build_frontier_map.py --match "run the degree-5 descended Semaev closure in under 72 GB instead of 217 GB and measure whether a sparse closure can avoid quadratic cost"
```
KR-RHO-825bca  score=6  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-5a43e5  score=5  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-6654ba  score=4  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-18cc42  score=3  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
KR-RHO-1c2928  score=3  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-e2d81b  score=2  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
```

### 0.7  python3 tools/build_frontier_map.py --match "memory column for block Wiedemann at the cap locus; descended ANF exceeds the per-decomposition rho budget; closure degree stays 4; 250 GB host or a sparse closure"
```
KR-RHO-fbd7b1  score=8  [known_bound/proven]  Grumpy giants and better-than-rho generic ordering
    sources: KN-LIT-fbe4e0
KR-IC-fbdb61  score=7  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-RHO-1c2928  score=7  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-889857  score=6  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-f5c584  score=6  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
```

### 0.8  python3 tools/build_frontier_map.py --match "Macaulay closure memory MutantXL descended Semaev F2 elimination blocked streaming"
```
KR-IC-5a43e5  score=6  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-fbd7b1  score=4  [known_bound/proven]  Grumpy giants and better-than-rho generic ordering
    sources: KN-LIT-fbe4e0
KR-IC-5765d2  score=3  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-e847d1  score=3  [known_mechanism/reported]  Crossbred algorithm for Boolean systems
    sources: KN-LIT-139
KR-IC-f3da82  score=3  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-IC-fbdb61  score=2  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
```

### 0.9  Ledger index grep (python over ledger/.index/{proposals,hypotheses}.jsonl; title/claim/mechanism/statement; 100-char claims; raw)
```
== term: M4RI|four russians
  P hits 2
    IDEA-20260828-770aa4 | The 11.73-12.22 GiB peak RSS measured this session during the n=15 D=6 Macaulay "prepare" phase (mac
    IDEA-20260829-cb2a65 | (A) THE DIAGNOSIS, READ OFF THE COMMITTED SOURCE RATHER THAN INFERRED. The program's exact GF(2) Mac
  H hits 0
== term: mutantxl|mutant xl
  P hits 1
    IDEA-20261018-88041d | At the cell (m,l)=(4,6) the solving degree of the Weil-descended Semaev system stays at 5, and at th
  H hits 0
== term: krylov|wiedemann|lanczos
  P hits 14
    IDEA-20260805-72bcb5 | A core-year is not a unit for the linear-algebra stage of the number field sieve. Three quantities a
    IDEA-20260807-9ecc6f | (A) WHAT THE PROGRAM'S COST MODEL ASSUMES. H-STR-002, IDEA-20260726-002 and the committed harness al
    IDEA-20260807-d20846 | (A) THE STAGE NOBODY IN THIS LANE HAS MEASURED. Production index calculus does not run Wiedemann on 
    IDEA-20260807-fafc04 | (A) THE QUESTION, SHARPENED. Wiedemann's method solves M x = b using 2 * deg(minpoly(M)) matrix-vect
    IDEA-20260809-1a5cb2 | The quoted security level for a pairing target field is an operation count with the memory of the li
    IDEA-20260815-fa6a12 | The ICEX exponent is relation cost plus linear-algebra cost. The lane measures the first and cites t
    IDEA-20260818-1fb37d | Every published security level for a pairing target field is the value of a cost function at a param
    IDEA-20260829-bb6e9b | (A) THE STRUCTURE THE COST MODEL IGNORES. Algorithm 2 of the in-repo text builds ONE table L(E,X,B) 
    IDEA-20260901-df12e1 | FOUR SEPARABLE CLAIMS. (A) THE OBJECT. After filtering and merge the number field sieve's linear alg
    IDEA-20260926-3cc0b8 | Representation class R1 of RQ-ECDLP-623a32 (the relation matrix and log vector over F_r); the attack
    IDEA-20261002-79a077 | Sparse linear algebra for index calculus is classical folklore, but RQ-BINSTD has no frozen toy-scal
    IDEA-20261018-1aff90 | A GF(2) block Wiedemann (Coppersmith) consistency test on the sparse Macaulay matrix decides, for th
    IDEA-20261018-1bc873 | Wiring the existing block Wiedemann and block Lanczos with CADO-style filtering (koblitz_sparse_la.r
    IDEA-20261018-670088 | Adding block Wiedemann with filtering to the genus-3 double-large-prime pipeline lowers the local li
  H hits 5
    H-ALISO-008 | Autolab package `p1486_hecke_krylov_probe` (isogeny / supersingular / Kani) produces a scoped empiri
    H-BINSTD-dcc004 | CLAIM (heuristic_validation / LA-solver instrument; NO ATTACK; NO EXPONENT). FORALL admitted toy cel
    H-ECDLP-326109 | TEST BOUNDARY FIRST. Post-merge sparse matrices produced by ONE implementation at 60, 80 and 100 dig
    H-ICEX-5666b2 | (A) THE OBJECT. The ICEX exponent is relation cost plus linear-algebra cost. The lane measures the f
    H-SDEG-3acfcf | SCOPE: the certificate-coverage accounting of a charged Semaev decomposition cost model C_decomp(p, 
== term: nested dissection|treewidth
  P hits 0
  H hits 0
== term: separator
  P hits 8
    IDEA-20260905-f9df88 | For two summation subsystems sharing one internal coordinate, the non-rewritable syzygy quotient may
    IDEA-20260905-fbe4a0 | For two summation subsystems sharing one internal coordinate, the non-rewritable syzygy quotient may
    IDEA-20260906-3493fe | A nested collision generator whose dependency DAG has a small regenerable separator may retain sqrt(
    IDEA-20260906-9f56ad | R3 representation at the decomposition/relation stage. On standalone binary pdp instances, a continu
    IDEA-20260906-a538a8 | R3 representation at the extension-field descended-system stage. A joint tensor/schedule choice can 
    IDEA-20260906-b035a5 | A high-degree or implicitly represented factor base whose three-point decomposition hypergraph has s
    IDEA-20260906-c8f2f6 | R3 representation at the decomposition/relation stage. A reusable low-degree separator polynomial ca
    IDEA-20260906-fca28f | A separator decomposition of a supplied sparse relation matrix can reduce peak linear-algebra memory
  H hits 7
    H-ECDLP-0ae933 | Fix the exact weighted replay identity T = sum_v r(v)c(v) on a frozen two-child fork before any nest
    H-FROB-2d6ccb | Test whether the jointly selected field presentation and exact elimination schedule costs at mosthal
    H-MONO-f25265 | Fix the exact count identity of IDEA-20260906-b035a5 before any later-stage claim. Stage 0 asserts o
    H-PAIR-810ca8 | Fix the exact count identity of IDEA-20260906-fca28f before any later-stage claim. Stage 0 asserts o
    H-SATIC-6fdb7a | On l4/5/6 and all three binary curves, test source K(l)<=2^(0.8*l), charged DAG size <=half the no-m
    H-SATIC-b58495 | On the complete 12/16/20-bit,s3/4/5,three-curve,32-target ladder, construct reusable E<=6 separator 
    H-SIG-01b048 | For the fixed finite panel, complete relative relation classes may be assembled from side modules an
== term: streaming|stream\+
  P hits 4
    IDEA-20260816-2c1f20 | (A) The security argument for Argon2 is a cost argument, and the cost currency is area-time: memory 
    IDEA-20260828-770aa4 | The 11.73-12.22 GiB peak RSS measured this session during the n=15 D=6 Macaulay "prepare" phase (mac
    IDEA-20260909-f66bed | Partial index calculus already works on named toys (full-rank FB, kernel-resolved LP logs, 96/96 or 
    IDEA-20260930-024033 | EXPONENT BUDGET, STATED FIRST. This record targets the MEMORY AXIS of the archived algorithm (inputs
  H hits 1
    H-SSIQ-d724f2 | CLAIM (heuristic_validation / group-theoretic census; NO ATTACK; NO EXPONENT). Let O be the standard
== term: sparse closure|sparse echelon|rank-bounded|copy-free
  P hits 0
  H hits 0
== term: 217 GB|256 GB|250 GB|large-memory|large memory
  P hits 3
    IDEA-20260815-1ac849 | Lattice (HNP/BKZ) attacks need few signatures and large memory; Bleichenbacher Fourier attacks need 
    IDEA-20260815-56f047 | SQIsign parameter sets were chosen against a p^(1/2) endomorphism-ring baseline. The Wesolowski resu
    IDEA-20261018-88041d | At the cell (m,l)=(4,6) the solving degree of the Weil-descended Semaev system stays at 5, and at th
  H hits 0
```

Additional index rows read for N3 (not opened in full): IDEA-20260906-fca28f "Separator-aware elimination with certified fill bounds for relation matrices" (proposed, unverified; H-PAIR-810ca8 is Stage 0 only, status specified); IDEA-20260906-a538a8 / H-FROB-2d6ccb (proposed); IDEA-20260906-c8f2f6; IDEA-20260906-9f56ad / H-SATIC-6fdb7a (specified); IDEA-20260906-b035a5 / H-MONO-f25265 (specified).
Full records opened (the allowed three, exact paths): ledger/proposals/IDEA-20260829-cb2a65.yaml, ledger/proposals/IDEA-20261018-1aff90.yaml, ledger/proposals/IDEA-20261018-88041d.yaml.

---------------------------------------------------------------------------------------------------

## 1. N1 Atlas collision

Lead YAMLs opened and read (mechanism, disposition, next_action, obstruction, forecloses) [retrieved]: LEAD-ICE-descent-closure-degree-at-scale, LEAD-ICE-chained-semaev-dreg-vs-semiregular, LEAD-ICE-hybrid-guess-determine-l7, LEAD-ICP-icperf-writability-boundary, LEAD-ICE-boolean-f4-f5-f6-engines, LEAD-ICB-orbit-linear-algebra, LEAD-ICB-prime-degree-algebraic-decomposition, LEAD-ICB-generic-table-oracle, LEAD-ICE-semaev-chain-cost-model, LEAD-ICB-factor-base-subspace-choice, LEAD-ICB-frobenius-orbit-factor-base, LEAD-STR-class-representative-ic-selection. (The last three are lexical neighbours only: they share no mechanism with C5.)

### 1.1 Top-5 of each run, and what each says about C5

Run 1 top 5: LEAD-ICE-chained-semaev-dreg-vs-semiregular (7), KR-IC-e847d1 (6), LEAD-ICE-descent-closure-degree-at-scale (6), LEAD-ICB-factor-base-subspace-choice (5), LEAD-ICB-frobenius-orbit-factor-base (5).
Run 2 top 5: LEAD-STR-class-representative-ic-selection (10), LEAD-ICE-descent-closure-degree-at-scale (9), LEAD-ICE-semaev-chain-cost-model (9), LEAD-ICE-chained-semaev-dreg-vs-semiregular (8), LEAD-ICP-icperf-writability-boundary (8).
Run 3 top 5: LEAD-ICP-icperf-writability-boundary (33), LEAD-ICB-orbit-linear-algebra (18), LEAD-ICE-descent-closure-degree-at-scale (18), LEAD-ICB-prime-degree-algebraic-decomposition (14), LEAD-ICB-generic-table-oracle (9).
Run 4 top 5: LEAD-ICE-descent-closure-degree-at-scale (12), LEAD-ICP-icperf-writability-boundary (11), LEAD-ICE-boolean-f4-f5-f6-engines (10), LEAD-ICE-chained-semaev-dreg-vs-semiregular (10), LEAD-ICE-semaev-chain-cost-model (9).

| hit | disposition | same mechanism as C5? | what C5 does that the hit's forecloses do not cover |
|---|---|---|---|
| LEAD-ICE-descent-closure-degree-at-scale | open_blocked | Same measurement, same cells (frozen C1, A2/B1/B2, then (4,7)), same discriminates, same blocked_by ("memory (C1 capped at 169 GB of 184 GB; projection 217 GB)"). Its next_action offers two routes: a host >= 250 GB, or "a sparse closure". C5 Arm A is a third route: shrink the dense closure's memory so the existing 256 GB-class pod suffices. | Its forecloses ("solving degree of Weil descent stays 4", "MutantXL closure degree on summation polynomial systems", "degree-capped certified decomposition") concern what the closure degree is, not how much memory the engine needs. Nothing there forecloses a memory change. This is why the verdict is advances_lead, not duplicate. |
| LEAD-ICB-prime-degree-algebraic-decomposition | open_blocked | Same family of cells; its blocked_by is also memory ((4,5),(4,6), m = 5 |V| = 8 D = 4 "~112k columns" needing a 32-128 GB host). Arm A would serve this blocker too. | Its forecloses include "mutant or degree-4 closure as a sub-rho decomposition oracle". C5 claims no oracle; consistent. |
| LEAD-ICE-chained-semaev-dreg-vs-semiregular | open_next_step | Not the same object (plain Macaulay RANK of the D = 6 chained S_3 for GOAL-DREG-001, Python h012c instrument), but its next_action is the same memory idea one layer down: "Re-run item C1 (n = 15, D = 6 ...) with a streaming native Macaulay builder (IDEA-20260828-770aa4)". So "stream the Macaulay rows to cut peak RSS" is already a recorded next step for the rank instrument. | C5 targets the MutantXL closure in Rust (ReducedBasis in inherited_f4.rs), which re-multiplies falls, and adds the rank-bounded echelon (no basis copy). Different code path, different loop; same family of idea. |
| LEAD-ICE-hybrid-guess-determine-l7 | open_next_step | Not the same. Its E8 cell (m, n, l) = (3, 22, 8) is "about 10-12 GB ... per branch"; C5 uses E8 only as a go/no-go for the memory fix (<= 5.5 GB, PREDICTION). Its blocker is not memory. | C5 neither confirms nor changes its discriminates (k*). |
| LEAD-ICP-icperf-writability-boundary | closed_obstructed (cost_model) | Not the same. Obstruction statement [retrieved, quoted in full]: "At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]." forecloses: "memory column for block Wiedemann at the cap locus" (the run-3 phrasing hits this phrase lexically). | C5 does not price writability at n = 131: its cells are toy (n <= 22). Chained vs unchained is exactly the lead's own Scope escape, and its revisit_when ("a representation (e.g. chained S_3 at m = 5, 6, ~2^31-2^33 monomials) whose written size plus solve fits under the rho budget with memory charged") is NOT met by C5. The "memory column for block Wiedemann at the cap locus" phrase is about the ECC2K-130-scale ANF, not the toy-cell closure, so it does not foreclose C5's toy-cell memory work; it does foreclose reading Arm B's Krylov numbers as an ECC2K-130 feasibility statement. |
| LEAD-ICE-boolean-f4-f5-f6-engines | closed_dominated | Not the same claim. Obstruction [retrieved]: "Dominated by LEAD-ICE-rootfind-pairtable-oracle on Koblitz and random-binary curves n <= 31, m in {2,3,4}: once its word XORs are priced (#1774), inherited F4 is about 22x-33x strong rho at K13 (n13) and the complete-S pair table is about 17x-22x cheaper than F4; ... " forecloses "M4RI GF(2) elimination speedup for PDP". | C5 claims no speedup (its H2 predicts wall time 0.5-2x of dense) and no oracle comparison. The lead's own revisit_when names LEAD-ICE-descent-closure-degree-at-scale as the unblocker, which is C5's lead. If Arm A's result were ever reported as a speed gain it would fall under this foreclosure. |
| LEAD-ICB-orbit-linear-algebra | exhausted_at_scale | No. Obstruction: "Linear algebra is 0.0-2.7% of S in every Table A-C row ... Scope" refers to the orbit-folded RELATION matrix over Z/r. forecloses "block Wiedemann for the Koblitz relation matrix". | C5's Arm B is about the per-decomposition Macaulay-closure matrix over GF(2), a different matrix. The lead's "no LA speed-up moves the board" does not transfer or exclude it, but it is a reminder that a faster solve of this object moves nothing unless the closure degree and the oracle floor allow. |
| LEAD-ICB-generic-table-oracle | closed_obstructed (theorem) | Not the same. Obstruction [retrieved, quoted in full]: "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged." | C5's stated escape ("the closure reads coordinates algebraically") is the lead's own revisit_when, which names LEAD-ICB-prime-degree-algebraic-decomposition as the non-generic oracle. So C5 inherits that escape; it adds none. SO-TABLE holds for any statement about total IC cost; C5 makes none. |
| LEAD-ICE-semaev-chain-cost-model | closed_obstructed (cost_model) | No. Chain length / merge-tree topology / memory charging against vOW in Semaev's cost model. | "memory charging" there is the vOW operating-point memory, not engine RSS. No overlap. |
| LEAD-ICB-factor-base-subspace-choice, LEAD-ICB-frobenius-orbit-factor-base, LEAD-STR-class-representative-ic-selection | exhausted / closed / open | No (lexical neighbours). | C5 does not choose or alter the factor base. |
| KR-IC-e847d1 (Crossbred) | known_result | Different technique (Macaulay preprocessing + enumeration). | See N2. |

Standing-obstruction check for the other SO-codes: C5 makes no claim touching SO-GEN, SO-MULTI, SO-ENDO, SO-ISO, SO-PAIR, SO-PADIC, SO-XEDNI, SO-COVER, SO-QSP, SO-MONO, SO-ALGFB, SO-TORS, SO-FROB, SO-WALK, SO-DECK, SO-CHEON or SO-NET. The candidate's own so_codes_touched = [SO-TABLE] is right, and the escape is trivial (C5 is an instrument, not an oracle claim). This also means C5 cannot, even if both arms succeed, move any cost row below rho: the program's own note says "The free-oracle floor still binds. At m = 4 it is 2^56.46, which leaves 2^5.71 an oracle call. So no row beats rho." [retrieved: research/notes/ecc2k130/RESEARCH_ECC2K130_DESCENT_DEGREE.md].

### 1.2 Things found in the code and run directories that the atlas rows do not show [retrieved]
1. The "sparse closure" in the lead's next_action already exists and was run: sparse_closure_refutes (src/cryptanalysis/koblitz_bench.rs, doc and test sparse_closure_matches_the_dense_closure; research/dreg_closure_driver_20261016/RESULTS.md "An independent closure implementation"). The program's own verdicts: "the sparse engine built on 10-17 is too slow" (research/ic_leads_review_20261018/README.md row 3; ledger IDEA-20261018-88041d mechanism). So "or a sparse closure" is a tried route, found slow, not an untried one. Arm A is not this route.
2. src/cryptanalysis/sparse_macaulay.rs states why Wiedemann/Lanczos were NOT used for the solving-degree measurement: "The measurement needs neither: it asks whether the reduced row space contains the constant 1 ... and whether it contains v or v + 1 ... Those are questions about a reduced basis, which a Krylov method does not produce." This bears directly on Arm B's kappa (see 1.3).
3. src/cryptanalysis/descent_treewidth.rs already computes the exact treewidth (Bodlaender-Fomin DP, <= 18 vertices) of the PRIMAL graph of the descended system as a predictor of the solving degree D* ("P2'"). That is treewidth of the system's variable graph at toy size, not a nested-dissection exponent of the Macaulay-closure matrix; it is adjacent prior art for Arm B's H4, not the same measurement.
4. research/ic_leads_rented_20261018/closure_c1/LAUNCH.md: a C1 degree-5 run was LAUNCHED on 2026-10-18 21:50Z on a 512 GB pod (cpu3m-64-512, $3.52/h; README row P7 "running"). I found no recorded outcome (the only deg5 run record, research/dreg_closure_m4l6_20261018/runs/deg5-m3-19-7.d0.log, is the capped 169,306,092 kB / abort at 17:27 min). The lead (last_reviewed 2026-10-24) still lists the cell as open_blocked. If that 512 GB run completed, C5's C1 target is already decided by hardware and Arm A's remaining value is C2 / (4,7) and other cells above the host class; if it did not, the program has an unreported run. Either way the candidate's premise "blocked at the C1 cell" should be re-checked against that pod before any rental.

### 1.3 Arm-by-arm reading

Arm A (memory of the dense closure). Code check [retrieved: src/cryptanalysis/inherited_f4.rs lines 2881-2906 and 2799-2870]: ReducedBasis::absorb calls materialise_all, copies every basis row into a full-width Vec<u64>, extends the matrix with the whole product batch and runs rref_f2_counted on the stack; close() holds all of a round's products as Vec<Vec<u64>> (u64 monomial lists) and then the packed rows. The doc comment says the batch rref was chosen on purpose ("a batch of closure products is large enough that the Four Russians kernel reduces it for a fraction of that"), which is exactly the speed risk the candidate calls H2. Candidate arithmetic [retrieved by recomputation]: C^2/8 + 65,536*C/8 bytes gives A1 17.3 GB, A2 22.7, B1 49.5, B2 63.2, C1 78.4, C2 126.8, matching the candidate's <=79 / <=64 / <=127. Two corrections to its premises:
 - "Peak is about 3*C^2/8, matching the protocol's fitted law exactly: 44/59/134/173/217/357 GB" is circular: those six numbers are the protocol's own projections (3*cols^2/8, "derived" from one scale-study point, 5.8 GB at 124,314 columns; PROTOCOL.md section 2). The only new large measurement, A1, read 25.8 GB, which is 0.59x that law (1.77*C^2/8; RESULTS.md "Recorded against expectation"). At C1 the as-built run had already reached 169 GB, i.e. >= 2.34*C^2/8, so the overhead factor is not constant in C. The saving at A1 is therefore 25.8 -> ~17 GB (1.5x), not 44 -> 17; whether the copy is the whole story at degree 5 is what the A1 and E8 go/no-go tests.
 - Candidate's kill rule (A1 > 17 GB or C1 > 150 GB refutes H1/H2) is a good one and unchanged.
Memory shape already diagnosed in the ledger: IDEA-20260829-cb2a65 [retrieved, opened] states the same floor for the plain-rank instrument: "A carrier holding r pivot rows over an n-column space costs r times n bits regardless of the chunk width, so column chunking bounds the WORKING SET but not the ACCUMULATOR." C5's rank <= #columns floor (H1) is this observation; C5's fix keeps the dense accumulator (floor C^2/8) where cb2a65 proposed to abandon it for Krylov. So the floor is known; the copy-free, block-streamed closure for the Rust MutantXL is not recorded anywhere.

Arm B (separator/Krylov certificate of w).
 - Technique prior art in the ledger: IDEA-20260829-cb2a65 (black-box Krylov rank of the Macaulay matrix, density pre-test, H-ECDLP-a0d5d6 proposed, not run); IDEA-20261018-1aff90 [retrieved, opened] (GF(2) block Wiedemann consistency test on the Macaulay matrix, memory O(nnz), "gives the plain-XL degree as an upper bound ... a bound, not the measurement", recommended_priority low, "Dominated by the large-memory run of the degree cells if a node can be had"); IDEA-20260906-fca28f (separator decomposition with certified fill bounds for sparse RELATION matrices, Stage 0 only). No record uses nested dissection, METIS, or the Alon-Yuster theorem (0 hits in proposals, hypotheses, experiments, knowledge, ATLAS, KRMAP; the "Alon" hits in text are substrings of other words).
 - What is not recorded: a separator exponent beta of the Macaulay-CLOSURE sparsity pattern and a w_eff = max(1, min(omega*beta, 1+kappa)) price. That specific measurement is open.
 - Why it adds little as stated: (a) the w = 2 rows are already in the program's note and are already "the rows the measured closure tracks" (closure work ~ cols^2.2): m = 4, D = 4, w = 2 is +33.10 and m = 4, w = 1 is +7.62 [retrieved, RESEARCH_ECC2K130_DESCENT_DEGREE.md]. The candidate's PREDICTION w_eff >= 2 reproduces a recorded row; only beta < 0.71 or kappa < 1 would be new, and the candidate itself predicts beta, kappa >= 0.8. (b) sparse_macaulay.rs's own argument (1.2 item 2) says Krylov does not give the fall set; the closure iterates on falls, so kappa prices a consistency decision on a static matrix (plain XL; 1aff90's own limit), not the closure, unless H3 (squaring up preserves the structure) is proved or measured. (c) Citation correction in section 6.
 - So Arm B's technique is not new in the ledger (Krylov and separator elimination on sparse matrices both proposed), its object (closure matrices) is unmeasured, and its expected result is a recorded row.

---------------------------------------------------------------------------------------------------

## 2. N2 Known results

Frontier-map runs 0.5-0.8 (raw above). Highest-scoring rows and their relation to C5 [retrieved: KRMAP.md rows]:
- KR-IC-e847d1 Crossbred (Joux-Vitse; Macaulay preprocessing plus enumeration), score 6 on run 1 only: a different algorithm; it is already tried in-repo at m = 2, 3 (LEAD-ICE-hybrid-guess-determine-l7). Not C5.
- KR-IC-0d2021 Modern Groebner-basis complexity refinements (Las Vegas F4 with proven probability bound, probabilistic row echelon in F4): F4 engineering at the level of probability/complexity; no memory-bounded MutantXL closure and no separator analysis. Not C5.
- KR-IC-fbdb61 Last fall degree and solving degree of Weil descent systems (known_bound/proven): the theory of the QUANTITY C5's cells measure (bounded last fall degree; semi-regular predictions do not describe descended summation systems). C5 does not change it; it would supply one more measured degree.
- KR-IC-889857 (disputed) first-fall-degree subexponential claim, KR-IC-1fcdbc (measured: summation algorithms stay far slower than rho; "experiments reach only small n and l"), KR-IC-f5c584, KR-IC-5765d2 (SAT/XOR), KR-IC-f3da82 (F4 trace reuse), KR-IC-5a43e5 (Semaev polynomials), KR-IC-5931ee (prime field, irrelevant here): context for the question, not the same object.
- KR-RHO-* hits (cb1c58 batched inversion, fbd7b1, 1c2928, 825bca, 6654ba, ...) are lexical noise from "constants/rho" words.
Searches of KRMAP.md for "m4ri|wiedemann|nested dissection|treewidth|separator|krylov|macaulay|mutantxl|streaming|memory" returned only the Crossbred row and one rho DP-memory row (KR-RHO-7d93f6). Thus: no KR row records (i) memory-bounded or streaming dense Macaulay/MutantXL elimination, (ii) nested dissection or a separator exponent for Boolean Macaulay matrices, or (iii) block Wiedemann on a Macaulay closure. The ingredients (M4RI/PLE; nested dissection; Wiedemann/Coppersmith) are standard external linear algebra, cited by the candidate, and not KR rows. N2 verdict: no KR hit is the same claim; the candidate has a defined new element (the rank-bounded streamed closure and the closure-matrix beta), but the new element is engineering and an instrument, with no exponent claim.

---------------------------------------------------------------------------------------------------

## 3. N3 Ledger

Hits that may be the same object (id | 100-char claim) [retrieved from the index rows]:
- IDEA-20260829-cb2a65 | (A) THE DIAGNOSIS ... column-chunked dense M4RI elimination costs memory proportional to rank times rows ... black-box Krylov instead. OPENED. Same memory floor (r*n bits), plain-rank instrument not closure; proposes Krylov, not streaming. Hypothesis H-ECDLP-a0d5d6 proposed, not run.
- IDEA-20261018-1aff90 | A GF(2) block Wiedemann (Coppersmith) consistency test on the sparse Macaulay matrix decides, for the (4,6) cell at degree 5 ... OPENED. Same blocker (memory at (4,6)/degree 5), Krylov route, plain-XL bound only; priority low; its premise "(4,6) ... about 70 GB dense at degree 5" is stale after the A1 measurement (A1 refutes at degree 4 in 25.8 GB). Overlaps Arm B's Krylov part, not Arm A.
- IDEA-20261018-88041d | At the cell (m,l)=(4,6) the solving degree ... stays at 5 ... Large-memory run of the degree cells. OPENED. The hardware version of the same measurement ("256-512 GB host, about one week"; "the sparse closure built 2026-10-17 is too slow"). C5 Arm A is the software alternative to it.
- IDEA-20260828-770aa4 | The 11.73-12.22 GiB peak RSS measured ... n=15 D=6 Macaulay "prepare" phase ... stream+bitmask ... (index row only). Streaming Macaulay builder for the Python rank instrument; the same idea family as Arm A's "generate falls x monomials one block at a time", not the Rust closure.
- IDEA-20260906-fca28f | A separator decomposition of a supplied sparse relation matrix can reduce peak linear-algebra memory only when exact Schur fill ... (index row only; H-PAIR-810ca8 Stage 0). Separator elimination with certified fill bounds, on the relation matrix.
- IDEA-20260906-a538a8 / H-FROB-2d6ccb (separator schedule on the descended multiplication-tensor hypergraph), IDEA-20260906-9f56ad / H-SATIC-6fdb7a, IDEA-20260906-c8f2f6 / H-SATIC-b58495, IDEA-20260905-f9df88 / EXP-SIG-e768a8 (chain-separator syzygy gluing): separators of the chained S_3 SYSTEM, not of the closure matrix.
- IDEA-20260906-b035a5 | A high-degree or implicitly represented factor base whose three-point decomposition hypergraph has small certified separators ... (H-MONO-f25265). Separator-based DP on the decomposition hypergraph; related to C5's H4 but a different object.
- IDEA-20260807-fafc04, IDEA-20261002-79a077, IDEA-20261018-1bc873: Wiedemann/Lanczos on RELATION matrices (Z/r), not Macaulay.
Decision (three full records opened, none identical): no ledger record proposes a block-streamed, copy-free, rank-bounded echelon for the MutantXL closure, and none proposes a nested-dissection exponent of the closure matrices. Records cb2a65 and 1aff90 overlap Arm B on "Krylov on a Macaulay matrix", and cb2a65 states Arm A's memory floor. Neither was executed.

---------------------------------------------------------------------------------------------------

## 4. N4 Notation change

The candidate is an IC / factor-base / representation candidate, so N4 applies.

Pair for the measured object (the same pair the lead already uses): R1 = Boolean ANF of the Weil-descended chained S_3 (variables = F_2 coordinates of the points x_i, each constrained to an F_2-subspace V of F_{2^n}, so the representation is "x_i in V in a fixed F_2-basis"), Sigma = translation by factor-base elements (partial action, IC Class I in IDEA-20260806-c5d183's trichotomy, with coordinate dependence: Class III in the representation sense). Oracle = the bounded-degree row-space (MutantXL) closure. This is word for word LEAD-ICB-prime-degree-algebraic-decomposition's mechanism ("restricts x_i to an F_2-subspace and solves the Weil-descended S_{m+1} system algebraically"). Arm A adds a second pair only for the computation: (packed GF(2) rows indexed by monomials of degree <= D, Sigma2 = {row XOR, multiply a fall by a monomial}); C5 claims the span, refutation verdict and fall set are unchanged, so it is the identity on that object and changes only storage and traversal order.
Not a recorded rigidity result in new notation:
 - IDEA-20260806-c5d183 [retrieved]: a projection that propagates under the FULL translation action of a prime-order group is constant or injective. C5 asserts no propagation and no lossy projection; it explicitly sits in the partial-action class that theorem leaves open (translation by factor-base elements only). Nothing to restate.
 - IDEA-20260901-863e36 [retrieved]: propagation under an operation group is a block system of that group's action; the cost law is the cost of canonicalising an orbit, with Omega(sqrt r) for generic canonical forms. C5 has no orbit canonicalisation and no quotient.
 - KN-OPEN-020 [retrieved]: bounded-degree algebraic factor bases over GENERIC PRIME-FIELD subgroups are scoped out; open class = high-degree, implicit-membership, target-dependent. C5 is characteristic 2 with an F_2-linear subspace base (membership degree 1 over F_2; as an F_{2^n} polynomial the vanishing set is a linearized polynomial of degree 2^{n-l}, i.e. on the high-degree side). It is outside KN-OPEN-020's scoped-out class and also makes no factor-base-size or yield claim.
 - KN-FIND-ffe1df Theorem C [retrieved]: Wagner k-tree combining with quasigroup rules cannot be exact on E(F_p) filters; unrelated to a Boolean closure.
Conclusion: the notation adds nothing and removes nothing: C5 is not an object-frame claim, so no rigidity theorem is being re-derived and none is escaped; its novelty can only rest on the engineering of Arm A and the unmeasured closure-matrix exponent of Arm B.

---------------------------------------------------------------------------------------------------

## 5. Dispositions the candidate proposes, against the lead's own discriminates

C5's outcomes_to_dispositions repeats the lead's discriminates: degree 5 at (3,7) -> "confirms the +10.32 bracket"; degree >= 6 -> closed_obstructed. Nothing new is decided by C5 beyond the memory route. Arm B's proposed disposition "closed_obstructed(cost_model) for the ECC2K-130 pricing consequence of LEAD-ICB-prime-degree-algebraic-decomposition and LEAD-ICE-hybrid-guess-determine-l7 (rows repriced at w = 2)" restates +33.10 (m = 4, w = 2, D = 4), already printed in RESEARCH_ECC2K130_DESCENT_DEGREE.md; the +19.8 (D = 3) figure I did not find in that note and did not recompute. It stays a candidate-supplied number.

## 6. Citations

| citation | provenance | check |
|---|---|---|
| Albrecht, Bard, Pernet, "Efficient Dense Gaussian Elimination over the Finite Field with Two Elements", arXiv:1111.6549 | retrieved (arxiv.org/abs/1111.6549 fetched: title and authors match; abstract names M4RI and a block iterative PLE decomposition; the page does not itself say "Four Russians") | OK. |
| Alon, Yuster, "Matrix sparsification and nested dissection over arbitrary fields", J. ACM 60(4):25 (2013) | retrieved (web search: J. ACM 60(4), Art. 25, Aug 2013, DOI 10.1145/2508028.2505989; full text read from the author's PDF, web.math.princeton.edu/~nalon/PDFS/sparsesystem1.pdf) | CORRECTION. The candidate's statement "O(n^{omega*beta}) for a beta-separator tree, Las Vegas over finite fields" is Theorem 3.1, not Theorem 1.1. Theorem 1.1 is the planar / bounded-genus (O(n^{omega/2})) and H-minor-free (O(n^{3 omega/(omega+3)})) corollary. Theorem 3.1: for a delta-sparse hereditary family with an algorithm giving (O(n^beta), 2/3)-separations in O(n^gamma) time, a NON-SINGULAR system is solved in O(n^{omega beta} + n^gamma + n log n); deterministic over R, Q, C, randomized Las Vegas over finite fields; time = algebraic complexity. Two hypotheses the candidate must meet: A square and non-singular (Macaulay closures are rectangular and rank-deficient, hence H3), and a graph-family separator algorithm. Over a small field the proof draws random diagonal entries from an extension field with at least n^4 elements (text: "If F has q <= n^4 elements ..."), so on GF(2) the dense top-level blocks live in GF(2^k) with k >= 4 log2 n (roughly 80 bits per entry at n ~ 10^6): the bit-packed Four Russians kernel does not apply as is, and a memory/ops constant of that order multiplies omega*beta. This is not in the candidate's w_eff formula. |
| Lipton, Rose, Tarjan, "Generalized nested dissection", SIAM J. Numer. Anal. 16(2):346-358 (1979) | recalled (not re-read; Alon-Yuster cite the Lipton-Tarjan planar separator lineage in the same context) | Used for the (tw+1)-clique/fill bound only. |
| Treewidth = min over chordal completions of (max clique - 1); fill of an elimination order holds a (tw+1)-clique | the candidate marks it retrieved; I did not independently re-fetch it (standard fact; I treat it as recalled) | Not load-bearing for the verdict. |
| Wiedemann 1986; Coppersmith 1994 | recalled for Coppersmith (Math. Comp. 62); Wiedemann (IEEE Trans. Inform. Theory 1986) appears in the Alon-Yuster reference list, so retrieved there | Block Wiedemann is the GF(2) route; over F_2 the plain scalar version is weak (cb2a65 and sparse_macaulay.rs both say so). |
