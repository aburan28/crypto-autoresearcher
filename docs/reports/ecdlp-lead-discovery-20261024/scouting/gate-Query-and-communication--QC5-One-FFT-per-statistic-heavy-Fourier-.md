# Gate N1-N4: QC5 "One FFT per statistic: heavy Fourier coefficient (list-decoding upper bound) and autocorrelation (SQ lower bound)"

Field key: Query and communication complexity (neighbouring tool: heavy-Fourier-coefficient learning with SQ lower bounds). Bottleneck: B7 (LEAD-TRF-miller-cocycle-nonhom-transfer). Candidate tier X, predicted gain 0 bits (candidate's own number; a prediction, not a result).

All commands were run from /Volumes/SSD990-2/crypto-autoresearcher with LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as instructed. Nothing was written inside any repository. Intermediate raw files live in `scout/_qc5_raw/`. Every number below is either copied from a tool output or a file I read (stated), or marked PREDICTION / ARITHMETIC.

Provenance tags used: `retrieved` = I opened the source text in this session (web fetch/search or a local file); `recalled` = from memory, not opened.

---------------------------------------------------------------------------
## N1  Atlas collision (python3 tools/lead_atlas.py --match ...)
---------------------------------------------------------------------------
Phrasings 1-3 are the candidate's match_phrasings; phrasing 4 is mine.

### N1 run 1: `lead_atlas.py --match "Fourier transform over Z/N of a character of the Miller cocycle value U(kP) as a list-decoding test"`
```
   13  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    8  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    6  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    4  LEAD-EXO-ideas-corpus-algebraic-transforms   open_blocked       ECDLP-IDEA breakthrough corpus: algebraic-geometric transforms awaiting constructors
    4  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
    3  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    3  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    3  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
```

### N1 run 2: `lead_atlas.py --match "does any function of the point coordinates correlate with a character of the discrete log"`
```
   13  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   11  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
   10  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    9  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    9  LEAD-STR-class-group-ecdlp-bridge            open_next_step     Reduction between Cl(O)-vectorization (or CM self-pairings) and ECDLP in the same class
    8  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    8  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
```

### N1 run 3: `lead_atlas.py --match "non-homomorphic point statistic gives partial information about k at less than sqrt(M) cost"`
```
   10  LEAD-STR-torsion-module-leak                 closed_obstructed  l-torsion (l != N) as a Galois/End module leaking k or attack cost
   10  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    9  LEAD-RHO-dp-multitarget-precomputation       closed_known       Distinguished points, multi-target batching and Bernstein-Lange precomputation (incumbent controls)
    9  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
    8  KR-RHO-38be82                                known_result       Tag tracing and table-driven step shortcuts
    8  LEAD-STR-jmv-random-self-reduction           closed_known       Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level
    7  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    7  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
```

### N1 run 4: `lead_atlas.py --match "heavy Fourier coefficient statistical query autocorrelation learnability of discrete log bits"`
```
   13  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   11  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
   10  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    8  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    7  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    7  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
    6  KR-RHO-898783                                known_result       Interval DLP: kangaroo and Gaudry–Schost constants
```

### N1 reading of the top-5 of every run (lead YAMLs opened under knowledge/leads/ecdlp/)

| Run | Top-5 (score, disposition) | Same mechanism? |
|---|---|---|
| 1 | LEAD-EXO-miller-pairing-cocycle (13, open_next_step); LEAD-TRF-miller-cocycle-nonhom-transfer (8, open_unexamined); LEAD-EXO-dl-character-sum-pseudorandom (6, exhausted_at_scale); LEAD-EXO-ideas-corpus-algebraic-transforms (4, open_blocked); LEAD-ICB-orbit-linear-algebra (4, exhausted_at_scale) | first three: yes (see below). Last two: lexical only (corpus of unconstructed ideas; linear algebra of relation matrices). |
| 2 | LEAD-EXO-dl-character-sum-pseudorandom (13); KR-RHO-ea34b8 (11); LEAD-EXO-ml-learned-models (10, open_next_step); KR-RHO-46c2c6 (9); KR-RHO-6654ba (9) | dl-character-sum, ml-learned-models: yes. KR rows: precomputation/multi-target/halving, lexical only (read in N2). |
| 3 | LEAD-STR-torsion-module-leak (10, closed_obstructed); LEAD-TRF-one-point-self-pairing (10, closed_obstructed); LEAD-RHO-dp-multitarget-precomputation (9, closed_known); LEAD-STR-automorphism-quotient-rho (9, closed_known); KR-RHO-38be82 (8) | torsion-module-leak: overlaps on the SO-TORS premise only. self-pairing: bilinear, QC5's U is not (SO-PAIR scope). Other three: lexical. |
| 4 (mine) | LEAD-EXO-dl-character-sum-pseudorandom (13); LEAD-EXO-ml-learned-models (11); LEAD-EXO-hnp-advice-leakage (10, open_blocked); KR-RHO-46c2c6 (9); KR-RHO-ea34b8 (8) | dl-character-sum, ml-learned-models, hnp-advice-leakage: yes. |

Also opened because the candidate names them: LEAD-EXO-coordinate-statistic-leakage (open_next_step), LEAD-EXO-elliptic-net-eds, LEAD-TRF-second-torsion-direction, LEAD-RHO-generic-sqrt-lower-bound, LEAD-EXO-augmented-oracle-ggm.

#### The four leads whose mechanism QC5 shares (mechanism / next_action / forecloses, as read)

1. **LEAD-TRF-miller-cocycle-nonhom-transfer** (open_unexamined). Mechanism: U(R)=f(R)^(1/N) canonical map into F_p^* when gcd(N,p-1)=1; "if log U(kP) carried structure in k ... it would be a cheap non-homomorphic transfer". next_action.step (verbatim): "Test H1 of IDEA-20261017-e3a6f1 at toy size: equidistribution of ell(k) = log_g U(kP) in Z/(p-1), Smart-ratio success and correlation with characters of Z/N, on special and matched random p, with planted-structure positive control." discriminates: "Equidistribution at the 1/p rate closes the lead (a non-homomorphic map of this kind is a hash); any character correlation would be the first one-point transfer signal". forecloses: Miller function transfer; generalized Jacobian transfer; unreduced Tate pairing value; Miller S-unit descent; zeta defect quasi-homomorphism. QC5's B7 half (FFT over Z/N of chi(U(kP)), planted positive control, special vs matched random p) IS this next_action.
2. **LEAD-EXO-dl-character-sum-pseudorandom** (exhausted_at_scale). Mechanism: max_k |sum_{P in F} e(2 pi i k DL(P)/N)| over a structured set F. This is the Z/N-Fourier coefficient of the indicator of F along the log coordinate, i.e. QC5's tau_s for s = 1_F up to normalisation. Obstruction (measured): "R = C_EC/C_null is flat at about 1.28-1.34 ... at 2^20-2^26 ... all six standard analytic proof routes are closed (KN-FIND-e7a3b1) ... EXP7 Fourier flatness (8-14 bit) found no candidate predicate." revisit_when: "R trends upward with p beyond 2^30 on the same matched null, or a structured set other than small-x shows R growing with N." forecloses: Fourier bias of x-coordinate sets in log order; exponential sum cancellation for the elliptic log. QC5's digit-character and census statistics are "structured sets other than small-x" read in exactly the quantity the lead measures; the lead names them as its revisit trigger, it does not leave them uncovered.
3. **LEAD-EXO-ml-learned-models** (open_next_step). next_action.step (verbatim): "Run a learnability control on toy prime-order groups: train a model to predict a log bit from coordinates, with a planted-structure positive control (a known homomorphic leak) and a random-relabelling null, at N up to 2^24". QC5's first step has the same positive control, the same null and the same N ceiling (2^24), with an exact FFT of a fixed feature in place of a trained model. forecloses: neural network predicts discrete log bits; representation learning of the group law.
4. **LEAD-EXO-hnp-advice-leakage** (open_blocked). Mechanism: "Turn any weak correlation between public coordinates and bits of the logarithm ... into full DL recovery via hidden-number-problem lattices or Cheon-style divisor walks. A conversion with exponent 2*beta below 1/2 would make a small statistic advantage an attack." blocked_by: no statistic with measured nonzero log-bit advantage. forecloses: hidden number problem from coordinate bias; bit security of the elliptic discrete log; convert a statistical distinguisher into key recovery. QC5's upper bound (cost ~ tau^-2, sub-rho iff tau >= N^(-1/4+eps)) is the same exponent comparison 2*beta vs 1/2.

Also LEAD-EXO-miller-pairing-cocycle (open_next_step; K1/K2 verification; "collapses into the closed elliptic-net lead" if r_k needs k) and LEAD-EXO-coordinate-statistic-leakage (open_next_step; digit-character family for (lambda, PGL_2-stability)): QC5 itself notes K2 adds nothing beyond U (matching the first lead's discriminator), and its digit-character cells are the second lead's named next step measured by a different observable (the Z/N-side coefficient instead of the F_p-side lambda).

#### Standing obstructions quoted (statement, Scope clause included)

- SO-TORS, LEAD-STR-torsion-module-leak (closed_obstructed, kind proof): "Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). Toy checks agree: the psi_5 factor-degree multiset does not change with k (H-TORS-3bed8a). Scope: prime-order G, any l != N."
- SO-PAIR, LEAD-TRF-second-torsion-direction (closed_obstructed, theorem): "Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1, i.e. the embedding degree divides k. Hence for N not dividing k, T_k(E)[N] = 0 (trace acts as [k] on the rational line), and an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N." (companion LEAD-TRF-one-point-self-pairing: "On a cyclic group G of prime order N every bilinear map G x G -> H is a scalar multiple of one fixed map ... Scope: ordinary curves over prime fields, N || #E, N != p.")
- SO-NET, LEAD-EXO-elliptic-net-eds (closed_obstructed, proof; no Scope clause): "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead); standard Hankel displacement rank of translated x-blocks is tautological and consecutive blocks have linear complexity >= (M-2)/3 (IDEA-006 gate). Measured at toy prime fields p in {101,431,1601}, n <= 1607: collision statistics are random-oracle-equivalent and the charged k-recovery exponent is 1.97-2.80 against BSGS 1.17-1.32 at identical accounting, with the sieve/BSGS gap growing (24x -> 135x)."
- SO-GEN, LEAD-RHO-generic-sqrt-lower-bound (closed_obstructed, theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). ... Scope: all generic algorithms, any field, any r." and LEAD-EXO-augmented-oracle-ggm: "Each named oracle is GGM-simulable ... Scope: oracles, not resources". Both are untouched by QC5, which reads the representation (revisit_when of the first: "only a method that reads the representation (index calculus, transfer) can change the exponent").

How QC5 relates to them: the "escape" of SO-TORS (the sqrt(M) penalty assumes enumeration of M candidates) is not new to QC5: IDEA-20260904-f68c7f (below, N3) already prices the non-enumerative conversion at eps^-2 n^o(1) and IDEA-20260905-b6154d already places the break-even at eps* = N^(-1/4) polylog. SO-PAIR is not engaged (U is non-bilinear; the lead's own mechanism says the same). SO-NET is not engaged either (the lead's own discriminator already excludes r_k).

#### N1 decision

The candidate has two halves. (i) Measurement: exact Z/N-FFT of chi(U(kP)), digit characters, census statistics and the ML feature map against matched nulls with a planted positive control, N up to 2^24. Each cell is the stated next_action of an open lead (items 1, 3, and the coordinate-statistic lead) or a revisit trigger of a measured lead (item 2). (ii) Conversion/lower bound: list-decoding upper bound (item 4's exponent comparison) and SQ autocorrelation lower bound. What the hits' forecloses phrases do NOT cover: the SQ-dimension read-out (see N3, no hit for statistical query / SQ in the atlas or the ledger index), and the use of power-residue characters of F_p^* of order 2,3,4 for U (which need no F_p^* log table; see N3/e3a6f1 for what is already specified).

---------------------------------------------------------------------------
## N2  Known results (python3 tools/build_frontier_map.py --match ...)
---------------------------------------------------------------------------
Same four phrasings.

### N2 run 1: `build_frontier_map.py --match "Fourier transform over Z/N of a character of the Miller cocycle value U(kP) as a list-decoding test"`
```
no row shares a term with the query -- this is NOT evidence of novelty; read the rendered map
```

### N2 run 2: `build_frontier_map.py --match "does any function of the point coordinates correlate with a character of the discrete log"`
```
KR-RHO-ea34b8  score=11  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-46c2c6  score=9  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-6654ba  score=9  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-955fd6  score=8  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-898783  score=6  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-8b9daa  score=5  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
```

### N2 run 3: `build_frontier_map.py --match "non-homomorphic point statistic gives partial information about k at less than sqrt(M) cost"`
```
KR-RHO-38be82  score=8  [known_mechanism/reported]  Tag tracing and table-driven step shortcuts
    sources: KN-LIT-93696f, KN-LIT-20ef89
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-cd0049  score=7  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-RHO-fb88e6  score=7  [known_mechanism/proven]  Negation map: sqrt(2) gain and fruitless cycles
    sources: KN-LIT-074c32, KN-LIT-c8e485, KN-LIT-5b238b, KN-LIT-a5c59c
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-RHO-0528e7  score=5  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
```

### N2 run 4: `build_frontier_map.py --match "heavy Fourier coefficient statistical query autocorrelation learnability of discrete log bits"`
```
KR-RHO-46c2c6  score=9  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-ea34b8  score=8  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-898783  score=6  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
KR-RHO-13bf67  score=3  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-5931ee  score=1  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-64659b  score=1  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-889857  score=1  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
```

### N2 reading

- Run 1 returned "no row shares a term with the query -- this is NOT evidence of novelty". I treated it as no information.
- Runs 2-4 return only precomputation / multi-target / halving / negation / generic-lower-bound / SAT-XOR rows (KR-RHO-ea34b8, KR-RHO-46c2c6, KR-RHO-6654ba, KR-RHO-38be82, KR-RHO-cd0049, KR-RHO-fb88e6, KR-RHO-13bf67, KR-IC-955fd6, ...). They match on words ("discrete log", "table", "bound", "point"), not on mechanism. None states a heavy-Fourier-coefficient conversion, a hard-core-predicate reduction, or an SQ bound.
- A lexical miss proves nothing, so I grepped KRMAP.md directly for: hard-core, hardcore, Akavia, list decod, Goldreich, Kushilevitz, statistical quer, SQ dim, Feldman, Blum, Boneh-Shparlinski, Jetchev, bit security, Hast, Verheul, Howgrave, Nguyen-Shparlinski, hidden number, character, exponential sum, Kohel, Winterhof, Bombieri, predicate, Fourier, spectr. Only unrelated rows matched (KR-RHO-93979e on Bos-Dudeanu-Jetchev rho collision bounds; KR-RHO-53c89f transfer attacks; etc.). Conclusion: **the known-results map has no row for bit security / hard-core predicates / list decoding / Weil-type character sums / SQ bounds.** That is a gap in the map, not novelty of the content.
- The knowledge corpus (knowledge/literature, status "read" in SOURCES.md) does hold the relevant literature notes: KN-LIT-4155 Duc-Jetchev "Hardness of Computing Individual Bits for One-way Functions on Elliptic Curves" (note says: predicting any input bit of an EC one-way function with non-negligible advantage inverts it; "list-decoding technique via discrete Fourier transforms due to Akavia-Goldwasser-Safra"); KN-LIT-7066 Morillo-Rafols "The security of all bits using list decoding" (all bits of the DLP in a prime-order group with multiplicative access); KN-LIT-4152 Fazio-Gennaro-Perera (all bits of a DH coordinate over F_p^2 via Akavia et al.); KN-LIT-4450 (EC-HNP bit security). I opened the first three; KN-LIT-5602 (Boneh-Shparlinski) and KN-LIT-043 (Boneh-Venkatesan) are cited by IDEA-20260905-b6154d and were not opened by me.

### Literature citations for the load-bearing steps (verification attempted with WebSearch / WebFetch)

| Citation | Used for | Provenance | What I actually saw |
|---|---|---|---|
| Akavia, Goldwasser, Safra, "Proving hard-core predicates using list decoding", FOCS 2003, pp. 146-157 | heavy-Fourier-coefficient learning over Z_N; list decoding of predicate codes | **retrieved (abstract/summary level)** | Search summary and repository listing confirm title, venue, pages, and that the paper gives a learning algorithm for heavy Fourier coefficients over Z_N and proves O(log log N) LSB/MSB security. I did not read the theorem statements or the 1/tau exponent of the FOCS algorithm. |
| Akavia, PhD thesis (MIT, 2008, supervisor Goldwasser), Theorem 1.18 "SFT algorithm" | cost of LOCATING a tau-heavy coefficient of f: Z_N -> C from queries | **retrieved (text opened)** | Thm 1.18: "There is a probabilistic algorithm solving qLCN in running time polynomial in log|G|, 1/tau and ||f||_inf." Remark: "for f : Z_N -> {+-1}, the running time is Theta~(log N / tau^5.5)" (raw-mode pdftotext of the fetched PDF; the layout-mode extraction garbles the fraction, the raw-mode lines read "e Theta logN / tau5.5"). The thesis also says this improves the earlier algorithm's poly(log N) dependence to Theta~(log N). |
| Duc, Jetchev, "Hardness of Computing Individual Bits for One-way Functions on Elliptic Curves", CRYPTO 2012 (ePrint 2011/329) | AGS list decoding applied to EC one-way functions | **retrieved (abstract level)** | Abstract: predicting any input bit with non-negligible advantage inverts the EC-based one-way function; proof via the AGS list-decoding technique plus an idea of Boneh-Shparlinski. |
| Blum, Furst, Jackson, Kearns, Mansour, Rudich, STOC 1994, pp. 253-262 | SQ dimension; weak SQ learning needs ~SQ-dim queries | **retrieved (search summary)** | Introduces SQ-dimension (max number of nearly uncorrelated concepts); a class of SQ-dimension n^omega(1) is not weakly SQ-learnable in poly time. |
| Yang, "New lower bounds for statistical query learning" | sharper SQ lower bounds | **title retrieved; COLT 2002 venue recalled** | Title confirmed via the J. Comput. Syst. Sci. listing; theorem statements not read. |
| Feldman, Guzman, Vempala 2017 (SQ simulation of gradient methods) | ML-lead direction | **recalled** (not opened; candidate also marks recalled) | - |

No other citation is load-bearing for the verdict. The candidate's own "retrieved ... abstract level; theorem statements not read" for AGS is consistent with what I could verify; I add the thesis theorem, which matters for the exponent (next section).

### Consequence for the candidate's cost claim (ARITHMETIC from a retrieved bound, not a measurement)

The candidate states total cost O~(log N / tau^2) "with the heavy coefficient found offline". Two different costs are being merged:
- phase read-off of a coefficient at a KNOWN frequency: Hoeffding, M = O(eps^-2 delta^-2 log(1/eta)) samples per phase (derived in IDEA-20260904-f68c7f, Lemma L2, which I read in full);
- LOCATING an unknown tau-heavy frequency from query access to g_s(k)=s(kP): the retrieved SFT bound is Theta~(log N / tau^5.5) for +-1-valued f (Akavia thesis). If that is the locating cost, then requiring it below sqrt(N) gives tau > N^(-1/11) (since 5.5 * (1/11) = 1/2), not N^(-1/4). Because g_s depends on (E, P, s) and not on the target Q, the locating step is a one-time precomputation per (curve, statistic); counting it as advice or amortising over targets is a separate accounting choice that the candidate does not make. So "sub-rho iff tau >= N^(-1/4+eps)" holds only with the frequency known (or with locating cost charged outside the single-target comparison); this is conditional, and it is the same condition IDEA-20260904-f68c7f states in its part (F).

---------------------------------------------------------------------------
## N3  Ledger dedup (grep of ledger/.index/{proposals,hypotheses}.jsonl)
---------------------------------------------------------------------------
Key terms grepped (case-insensitive regex over title/claim/statement/mechanism of 2678 proposals + 2131 hypotheses): heavy fourier; list decod; hard-core; bit security; autocorrel; statistical query / SQ; learnab / planted; fourier near Z/N or logarithm; character sum / additive character; digit character; miller+cocycle/primitive; hidden number / HNP; coordinate statistic / non-homomorphic; then a second sweep: SQ-dimension, neural / gradient / machine learning, Wiener / pair-sum, Akavia / SFT / sparse Fourier, DL-spectrum / DL-Fourier, unreduced / Lichtenbaum. Scripts and full outputs: `_qc5_raw/n3_grep.py`, `n3_grep_out.txt`, `n3_extra_out.txt` (pasted below).

Index claims are truncated by the index at ~200 chars; a term can sit past the truncation (the term Akavia is in f68c7f/b6154d novelty screens yet the index grep found it only in a66d70). I therefore also checked ids cited by the opened records.

### Hits that may be the same object (id, status, first 100 chars of claim)

- **IDEA-20260904-f68c7f** [proposed] "SETTING. E/F_p public, P of prime order n, G = <P>, Q = [k]P with k unknown and self-generated. Let " -- SAME OBJECT (conversion half). OPENED in full (first 14000 of 55298 bytes read).
- **H-ECDLP-1d8ff7** [specified] "Fix the closed-form conversion- threshold identities of IDEA-20260904-f68c7f before any Hidden Numbe" -- Stage-0 identities for f68c7f (2*beta vs 1/2). Index row only.
- **IDEA-20260905-b6154d** [proposed] "(A) THE CLASS. Fix E/F_p and a subgroup G = <P> of odd prime order N. Let C(D, L) be the coordinate " -- SAME OBJECT (spectrum + break-even half). OPENED (first 16000 of 25147 bytes read).
- **IDEA-20260905-f31bc4** [proposed] "(A) THE OBJECT. Let G = <P> be a subgroup of odd prime order N of E(F_p) and log_P: G -> Z/N its dis" -- SAME INSTRUMENT: FFT of a frozen library of coordinate functions along the log. Index row only.
- **H-ECDLP-0bc396** [proposed] "SCOPE: odd-prime-order subgroups G = <P> of cofactor 1 on deterministically generated ordinary short" -- Hypothesis for f31bc4 at field_bits 12..24. Index row only.
- **IDEA-20261017-e3a6f1** [proposed] "E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni" -- SAME TEST (Miller U half). OPENED in full (6928 bytes).
- **IDEA-20260901-a66d70** [proposed] "Setting. G = <P> of prime order N, Q = [x]P. An ORDER KEY is a map nu from G to Z/N (ties allowed), " -- AGS sparse-Fourier cascade (constant heavy coefficient regime), credited in f68c7f novelty_screen. Index row only.
- **IDEA-20260815-f558e4** [proposed] "(A) THE GAP THIS FILLS, STATED IN THE OWNING RECORD'S OWN WORDS. IDEA-20260807-df906f proved that on" -- Defines the observable A(v)=max_a|fhat(a)| and the propagation ceiling. Index row only (content as quoted in f68c7f).
- **IDEA-20260902-c17bf6** [proposed] "Setting. E/F_p, P of prime order n, G = <P>, and for R in G write x(R) for its x-coordinate lifted t" -- Thue-Morse / Rudin-Shapiro digit statistics at the DL coordinate. Index row only.
- **H-ECDLP-a4be60** [specified] "SETTING. E/F_p, P of prime order n, G = <P>, and for R in G write x(R) for its x-coordinate lifted t" -- Hypothesis for the digit-statistic cell. Index row only.
- **IDEA-20260921-1ec106** [proposed] "REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): cla" -- Digit-character family (lambda, PGL_2). Index row only.
- **IDEA-20260921-6a29df** [proposed] "REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): the" -- Lambda-registry (F_p-side spectral norm). Index row only.
- **H-ECDLP-4e1880** [weakened_pgl2_instability_and_cosets_at_random_level] "For each statistic v in the frozen registry of natural coordinate statistics on F_p (interval indica" -- Census of natural coordinate statistics, weakened. Index row only.
- **H-REPL-6c431d** [specified] "A neural model trained to predict a bit of the discrete logarithm from the coordinate representation" -- ML half: neural DL-bit predictor, zero structure, preprocessing argument. Index row only.
- **IDEA-20260806-94676a** [proposed] "(A) THE EXACT VERSION IS NOT IMPOSSIBLE -- IT IS THE DISCRETE LOGARITHM. Ask for an embedding z: <P>" -- ML half: latent linearisation = the DLP, costed. Index row only.
- **IDEA-20260811-8cf53a** [proposed] "(A) THE DICHOTOMY. Information about k comes in exactly two shapes. EXPONENT-SIDE information is a c" -- Source of the sqrt(M) claim behind SO-TORS. Index row only.

### Raw grep output, sweep 1

Note on the line `statistical query/SQ: 5 hits` below: the regex included the token `\bSQ\b` case-insensitively, so it matched the abbreviation `sq` (as in a square-root cost written `sq...`) and similar tokens in unrelated records (quantum ISD, degree counting). I checked the matching text of those hits: none concerns the statistical-query model. The dedicated sweep-2 pattern for `statistical quer` and `SQ-dimension` returned 0.
```
### heavy fourier: 0 hits
### list decod: 1 hits
  [p] IDEA-20260820-b87428 [proposed] If public transcript features induce a well-defined representation-invariant syndrome on a finite id
### hard-core: 1 hits
  [p] IDEA-20261007-20f660 [proposed] There exists a well-typed toy PKE syntax (KeyGen, Eval, Encrypt, Decrypt) where Encrypt uses only pk
### bit security: 2 hits
  [p] IDEA-20260816-72e5e5 [proposed] (A) OBJECT. An FO-bound evaluator is a function from a term list plus an input vector to a bit-secur
  [p] IDEA-20261006-77b06b [proposed] Representation class R1, x-coordinates. The attack stage is the shape of the decomposition ideal, sc
### autocorrel: 6 hits
  [p] IDEA-20260808-8a6cb5 [proposed] For ell-isogenous E, E' one has delta_{E'} <= ell^2 delta_E and delta_E <= ell^2 delta_{E'} (composi
  [p] IDEA-20260816-03a2f5 [proposed] (A) For an NTRU instance with secret (f,g) in a ring R of Z-rank n, modulus q, and lattice Lambda_h 
  [p] IDEA-20260816-6f9d8f [proposed] (A) THE OBJECT. For a support S contained in Z_n define its cyclic autocorrelation A_S(d) = #{(i,j) 
  [p] IDEA-20260922-96289a [proposed] Representation class R3 of RQ-ECDLP-623a32 (Weil restriction of a chained summation system), attack 
  [p] IDEA-20261018-71a901 [proposed] Prime-order E/F_p, m=3, B=ceil((6N)^(1/3)), x-interval / QR-class / small-height bases, N=2^14..2^22
  [h] H-DREG-6f667e [approved] The lag-1 ratio of a series is the sum of adjacent centered products divided by the sum of squared d
### statistical query/SQ: 5 hits
  [p] IDEA-20260829-359945 [proposed] Every quantum ISD algorithm known to this corpus sits at one of two points: Grover-Prange, which cos
  [p] IDEA-20260928-ce3ab0 [proposed] REPRESENTATION CLASS AND STAGE: R1 of RQ-ECDLP-623a32 (the point is keyed by x in F_p, and its sign 
  [p] IDEA-20261003-abf93e [proposed] Multiplication by 6 has degree 36. Multiplication by 5 has degree 25. Thirty-six exceeds twenty-five
  [p] IDEA-20261003-e7a959 [proposed] Multiplication by 10 has degree 100. Multiplication by 9 has degree 81. One hundred exceeds eighty-o
  [p] IDEA-20261007-1300af [proposed] On the smallest prime p' >= 3 such that F_{p'^5} contains both a nonsingular double-odd curve y^2 = 
### learnab: 72 hits
  [p] IDEA-20260802-007 [adaptation] A SINGLE SHARED CHARGED-UNIT ACCOUNTING LAYER - counting group operations, field multiplications and
  [p] IDEA-20260805-4f9881 [unverified] GOAL-ECTD-001's next_action queues BATCH-003 to execute EXP-ECTD-001: a ">=100x class max/median" he
  [p] IDEA-20260805-b6af55 [unverified] Two properties of the EXP-XEDN-004 measurement apparatus are proposed as checkable facts about its s
  [p] IDEA-20260805-ca92fd [unverified] The quantity that carries UOV's published key-recovery exponent is not the public map. It is the der
  [p] IDEA-20260807-a6a038 [unverified] Every ball-computable filter that measures a per-vertex arithmetic statistic on supersingular curves
  [p] IDEA-20260807-efc8de [proposed] (A) WHAT THE CAMPAIGN'S POSITIVE CONTROL DOES TODAY. harness/run_icinv.py::instrument_control draws 
  [p] IDEA-20260807-f6137c [proposed] (A) WHY AN AUDIT LANE OWES A CLOSURE. RQ-INSTR-f8faa0's decision target is that an instrument that c
  [p] IDEA-20260809-28289c [proposed] Every measurement in this goal is a claim that a specific structural event causes an observed behavi
  [p] IDEA-20260809-98c5ac [proposed] If a party's Paillier modulus is not proven well-formed, that party can choose it with small prime f
  [p] IDEA-20260813-16d752 [proposed] For a fixed toy plain-UOV public map and a fixed planted oil space, there is a parameter-explicit in
  [p] IDEA-20260813-2d839b [proposed] On a frozen toy recursive sampler with an exact public coefficient view, one can construct a planted
  [p] IDEA-20260813-5988b7 [proposed] After conditioning compressed and uncompressed toy public-map ensembles on the identical planted oil
  [p] IDEA-20260813-f2a6e7 [proposed] On preregistered toy plain-UOV instances, a certificate-labelled truncated syzygy module through deg
  [p] IDEA-20260815-bc26a3 [proposed] This program has run dozens of mechanism screens and reports a long run of negatives. Under docs/inv
  [p] IDEA-20260815-cce6e2 [proposed] DEC-20260810-2f92d8 selects expanding the GOAL-DREG-001 ladder under the admitted CTRL-B instrument 
  [p] IDEA-20260816-00b29e [proposed] (A) Every sweep in q that this goal contemplates resamples a fresh key at each modulus, so each cell
  [p] IDEA-20260816-0a9533 [proposed] (A) The in-repo treatment of signature-side leakage in this family is entirely about repetition: H-M
  [p] IDEA-20260816-41ab94 [proposed] (A) Four goals in this program compare four schemes against a plain-UOV baseline, and IDEA-20260807-
  [p] IDEA-20260816-49b818 [proposed] (A) The question of what ring structure buys is usually posed as a comparison of two points, structu
  [p] IDEA-20260816-554b67 [proposed] (A) Every ISD-related record in this repository -- IDEA-20260805-554b9d, IDEA-20260808-baf8bc, IDEA-
  [p] IDEA-20260816-6e6f2e [proposed] (A) Take the n rotations of the NTRU secret (f,g) as a rank-n planted sublattice, form their Gram ma
  [p] IDEA-20260816-8c5f12 [proposed] (A) Every cost figure in this bucket is a single number: the cost of recovering the oil space from n
  [p] IDEA-20260816-bd49b9 [proposed] (A) The ALPF campaign records many quiet cells and several explicit negatives -- EXP-ALPF-009 SCOPED
  [p] IDEA-20260816-fe3526 [proposed] (A) A screening decision needs three numbers and this lane has none of them written down together: h
  [p] IDEA-20260830-8a767e [proposed] THE OBLIGATION. For a cover X -> B over F_p there is an exact sequence 1 -> G_geom -> G_arith -> Gal
  [p] IDEA-20260905-55c34e [proposed] An obstruction certificate can support a negative only if its observable separates a planted positiv
  [p] IDEA-20260905-92dfe1 [proposed] An obstruction certificate can support a negative only if its observable separates a planted positiv
  [p] IDEA-20260906-cd7b7e [proposed] SETTING. W = V union -V, |W| = 2B, on a prime-order curve; for a target R let c(R) be the number of 
  [p] IDEA-20260910-321d6a [proposed] TRACKED CLAIM (adjudicable only against REF-A / REF-B / REF-C). There exists a secret-key distinguis
  [p] IDEA-20260915-7ef636 [proposed] P3b and P6 of H-ICPERF-cc4847 are measured on objects that differ in TWO ways at once, and as measur
  [p] IDEA-20260922-1d595f [proposed] Representation class R1 of RQ-ECDLP-623a32 (field coefficients of the decomposition generators), att
  [p] IDEA-20260930-f1d8ff [proposed] Representation class R1 of RQ-ECDLP-623a32 (x-coordinate in a polynomial basis). The attack stage wh
  [p] IDEA-20261001-2b71e5 [proposed] EXP-BINSTD-178742 Part 2 loads its O-SUPPORT reading on the triple CERT-LABEL/QUOT/BIND seal. CLAIM:
  [p] IDEA-20261005-9f4777 [proposed] At lattice dimension 128, a log-unit decoding certificate is produced for a principal ideal in Z[x]/
  [p] IDEA-20261006-06fe5e [proposed] On E: y^2 = x^3 + x + 2 over F_41, the points (0, 17), (1, 2), (3, 14), and (5, 3) lie on E. For eac
  [p] IDEA-20261006-11a1aa [proposed] On E: y^2 = x^3 + 2x + 5 over F_89, which this session counted as 101 points including infinity, an 
  [p] IDEA-20261006-12280d [proposed] In the generic group Z/251Z, with handles that hide the integer representative, 64 planted targets, 
  [p] IDEA-20261006-6374b1 [proposed] In the cyclic group Z/503Z, with the group law ordinary addition and the element written as an integ
  [p] IDEA-20261006-947b64 [proposed] In Z/401Z, one planted logarithm, an r-adding walk with r = 16, and 20 seeds, the lower median of st
  [p] IDEA-20261006-c5b972 [approved] A low-level P-192 scalar multiplication routine that accepts an unchecked affine point and exposes a
### fourier Z/N: 1 hits
  [h] H-BINSTD-add204 [approved] CLAIM (derivation + cost-model + toy measurement; HOLD-X2; NO ATTACK). Setting: binary Koblitz / sub
### character sum: 22 hits
  [p] IDEA-20260805-c4f675 [unverified] This goal's H-PSEUDO lane measures C(p) = max_{k=1..N-1} |sum_{P in F} e(2 pi i k DL_G(P)/N)| / sqrt
  [p] IDEA-20260808-726aa3 [proposed] Let H <= F_p^* be the subgroup of order B = (p-1)/d, so membership x in H is testable in O(log p) by
  [p] IDEA-20260816-f49ad1 [proposed] (A) THE STATE THIS REPLACES. Factor-base geometry results in this program are point estimates indexe
  [p] IDEA-20260829-4b34c5 [proposed] TWO-SIDED CLAIM, both sides informative. POSITIVE SIDE. The accepted set D_chi, defined as the set o
  [p] IDEA-20260905-5a1ea2 [proposed] (A) THE OBJECT. For a factor base F of size m inside a prime-order subgroup G of E(F_p), let H_F(x) 
  [p] IDEA-20260906-91453a [proposed] A nontrivial additive character component of a point-dependent torsion resolvent may retain informat
  [p] IDEA-20261002-8f26ce [proposed] The Artin-Schreier family y^2 + y = f(x) over F_2, f of odd degree 11 or 13, either contains a curve
  [p] IDEA-20261003-247e49 [proposed] The frozen symbol values are -1, 0, and 1. They number 3. The absolute values 1, 0, and 1 sum to 2 a
  [p] IDEA-20261003-76df35 [proposed] WHICH SIDE. The impossibility side: the duality stated and proved in a named model, with a toy certi
  [p] IDEA-20261006-5db10b [proposed] Let E be y^2 = x^3 + x + 3 over F_47, let s(P) = x(P) + x(2P) for affine points with y(P) ≠ 0 and s(
  [p] IDEA-20261018-c49f37 [proposed] Hand-derived, nothing executed. (T1) In the binary 2-decomposition system the curve enters only as a
  [h] H-ECDLP-1af1b2 [approved] The proposal writes the constant 4 as twice a degree, and writes that degree as 2 for the coordinate
  [h] H-ECDLP-32e5d7 [approved] SETTING (Stages 0-1 of IDEA-20261003-76df35). Let E/F_p be ordinary of prime order n, g a generator.
  [h] H-ECDLP-3f58db [specified] Fix the exact subgroup-order identity of IDEA-20260829-4b34c5 before any bilinear character-sum boun
  [h] H-ECDLP-954cae [approved] The proposal writes the window endpoints 3/4 and 1/2. Clearing the common denominator 4 gives the nu
  [h] H-ECDLP-e6772e [specified] Let E be y^2 = x^3 + x + 3 over F_47. Let s(P) = x(P) + x(2P) for affine points with y(P) ≠ 0 and s(
  [h] H-ECDLP-fea0be [approved] The fibre sizes 1, 2, 3 and 6 sum to 12. There are 4 fibres, so the average is 3 and the largest is 
  [h] H-ECDLP-feb405 [proposed] SCOPE: prime-field ordinary curves at bits in {20, 22, 24, 26}; the small-x factor base F = {P in E(
  [h] H-ECQ-f22688 [specified] Fix the exact splitting-degree identity of IDEA-20260829-ece95f before any isotypic concentration is
  [h] H-PFDR-0bc09b [approved] Sixteen cubed is 4096. Twelve times 4096 is 49152. The square 221 squared is 48841, which is 311 bel
  [h] H-PFDR-8a4f44 [proposed] THE SAVING A CHARACTER-SUM BOUND WOULD NEED IN ORDER TO CERTIFY A MULTIPLICATIVE-SUBGROUP FACTOR BAS
  [h] H-PSEUDO-83817b [specified] For any prime p, prime-order elliptic curve E/F_p with group order N, generator G, and factor base F
### digit character: 1 hits
  [p] IDEA-20260921-1ec106 [proposed] REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): cla
### miller cocycle U: 1 hits
  [p] IDEA-20261017-e3a6f1 [proposed] E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
### hidden number: 15 hits
  [p] IDEA-20260805-787c8b [unverified] For the standard Boneh-Venkatesan / Nguyen-Shparlinski lattice embedding of ECDSA partial-nonce leak
  [p] IDEA-20260807-0f49b6 [proposed] KN-OPEN-018 states the lattice/ECDLP boundary precisely: lattice reduction enters ECDLP work only vi
  [p] IDEA-20260808-0bde1a [proposed] SCOPE. The negative points of the memory-charged frontier GOAL-ECDSA-001 completion criterion 2 asks
  [p] IDEA-20260808-be161c [proposed] SCOPE. ECDSA/DSA partial-nonce leakage (the hidden number problem), exact or erroneous top-l-bit lea
  [p] IDEA-20260815-1ac849 [proposed] Lattice (HNP/BKZ) attacks need few signatures and large memory; Bleichenbacher Fourier attacks need 
  [p] IDEA-20260815-3f6b4c [proposed] HNP attacks embed the signature relations into a lattice, and several embeddings exist -- Boneh-Venk
  [p] IDEA-20260901-c7d8f6 [proposed] FIVE SEPARABLE CLAIMS. (A) THE PREMISE BEING TESTED. RQ-RSA-d46f02 and GOAL-RSA-002 state that ECDSA
  [p] IDEA-20260906-44daf9 [proposed] For a specified synthetic nonce-leakage channel, a hybrid solver can improve the time-memory-sample 
  [h] H-ECDLP-1d8ff7 [specified] Fix the closed-form conversion- threshold identities of IDEA-20260904-f68c7f before any Hidden Numbe
  [h] H-ECDSA-33554d [specified] Fix the exact count identity of IDEA-20260815-3f6b4c before any later-stage claim. Stage 0 asserts o
  [h] H-ECDSA-497cdd [specified] Fix the exact annihilator identity of IDEA-20260906-e306c1 before any HNP rewrite, any key recovery,
  [h] H-ECDSA-79aa4c [specified] Fix the exact dual-vector identities of IDEA-20260808-be161c before any Bleichenbacher product, any 
  [h] H-ECDSA-9946a0 [specified] Fix the exact k-cap arithmetic of IDEA-20260808-e40da2 before any merge tree, any Fourier coefficien
  [h] H-ECDSA-c57cd1 [specified] Fix the exact union-bound envelope of IDEA-20260905-c3ae38 before any coupling, any threshold compar
  [h] H-ECDSA-cc79dc [specified] Fix the exact fiber-agreement identity of IDEA-20260905-8fb675 before any nonce compression, any key
### coord statistic: 11 hits
  [p] IDEA-20260808-c4b462 [proposed] CONDITIONAL THEOREM TARGET, NOT A RESULT. Let G=<P> have prime order N and Q=[k]P. Put M=L=floor(N^(
  [p] IDEA-20260811-8cf53a [proposed] (A) THE DICHOTOMY. Information about k comes in exactly two shapes. EXPONENT-SIDE information is a c
  [p] IDEA-20260905-b6154d [proposed] (A) THE CLASS. Fix E/F_p and a subgroup G = <P> of odd prime order N. Let C(D, L) be the coordinate 
  [p] IDEA-20260909-4c5ee9 [proposed] An exact DLP-free residual label space of size O(q^{1/2-epsilon}), or a nonlinear gauge-invariant pr
  [p] IDEA-20260911-2dd68d [proposed] After (i) excluding the m=1 entry as a mathematical tautology (never entering any agreement statisti
  [p] IDEA-20260921-6a29df [proposed] REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): the
  [p] IDEA-20260930-8e3b75 [proposed] REPRESENTATION CLASS AND STAGE (RQ-ECDLP-623a32 vocabulary, filed under RQ-ECDLP-c1b7b1 because the 
  [p] IDEA-20261009-9e4a40 [proposed] Pr[omega(a) mod p^k is B-smooth] is about rho(k log p / log B), far below Pr[a in [0, p) is B-smooth
  [p] IDEA-20261017-e3a6f1 [proposed] E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
  [h] H-ECDLP-4e1880 [weakened_pgl2_instability_and_cosets_at_random_level] For each statistic v in the frozen registry of natural coordinate statistics on F_p (interval indica
  [h] H-ECDLP-c48f2a [proposed] THIS IS A NEW, SEPARATELY SCOPED SIBLING OF H-ECDLP-09125b, NOT AN EXTENSION OF ITS ALREADY-DECIDED 
```

### Raw grep output, sweep 2
```
### statistical query: 0
### SQ-dimension: 0
### gradient/neural/ML learner: 6
   IDEA-20260904-58ace7 KN-LIT-824baa concludes that neural-discovered differential-linear masks are locally strong but long
   IDEA-20260904-772029 KN-LIT-824baa's SipHash experiment is presented as evidence that differential-neural distinguishers 
   IDEA-20260904-b1d69f KN-LIT-824baa reports six data points in which a locally strong intermediate mask composes badly: fi
   IDEA-20260906-79ff48 (A) OBJECT FRAME, IN ONE CLAUSE. The tracked object is a LEARNED PREDICATE on the target's REPRESENT
   H-REPL-6c431d A neural model trained to predict a bit of the discrete logarithm from the coordinate representation
   H-SIMSPK-34ef92 Fix the exact count identity of IDEA-20260904-58ace7 before any later-stage claim. Stage 0 asserts o
### Wiener-Khinchin/pair-sum: 43
   IDEA-20260725-001 Wiener-style full-cost accounting applied to classical supersingular path-finding (MITM vs low-memor
   IDEA-20260801-001 The blocker for GOAL-CRYPTO-001 is not a missing mechanism but a missing shared ruler: a reproducibl
   IDEA-20260801-006 Wesolowski 2026's concrete van Oorschot–Wiener middle-memory cost for the supersingular isogeny prob
   IDEA-20260801-007 On GOAL-SSI-001's CSIDH lane, the concrete collision surface available to a van Oorschot–Wiener dist
   IDEA-20260802-002 An attack family on the ECDLP can be indexed by its TRACKED OBJECT, and that index can be made measu
   IDEA-20260805-554b9d A one-line derivation fixes the comparator that every published ISD ranking omits. Let an informatio
   IDEA-20260805-6253cf GOAL-CRYPTO-001 admits a candidate if it shows "a fully charged wall-clock or operation-count advant
   IDEA-20260805-bc8246 GOAL-SSI-001's completion criterion 1 requires a mechanism that "materially improves a matched basel
   IDEA-20260806-37eab9 (A) THE CEILING, DERIVED FIRST BECAUSE IT SIZES EVERYTHING ELSE. This program's baseline convention,
   IDEA-20260807-15b468 (A) THE SOUNDNESS CONSTRAINT, FIRST, BECAUSE IT IS THE ONE THAT CANNOT BE TRADED. Van Oorschot-Wiene
   IDEA-20260808-8a6cb5 For ell-isogenous E, E' one has delta_{E'} <= ell^2 delta_E and delta_E <= ell^2 delta_{E'} (composi
   IDEA-20260808-b16d04 Conditionally on H1-H5, a fixed public target-independent signed-y antisymmetric partition with root
   IDEA-20260808-f332da SCOPE. Class BD as defined in X1-02; single victim key; exact l-bit leakage. A COST-MODEL AND ALGORI
   IDEA-20260815-e94ea3 The published algorithm builds a keyed table and does claw finding, giving memory essentially equal 
### AGS / SFT: 2
   IDEA-20260901-a66d70 Setting. G = <P> of prime order N, Q = [x]P. An ORDER KEY is a map nu from G to Z/N (ties allowed), 
   H-JPR-5e33d6 SETTING. G = <P> of odd prime order N, Q = [x]P. An ORDER KEY is a map nu from G to Z/N (ties allowe
### DL-spectrum: 4
   IDEA-20260905-f31bc4 (A) THE OBJECT. Let G = <P> be a subgroup of odd prime order N of E(F_p) and log_P: G -> Z/N its dis
   H-ECDLP-0bc396 SCOPE: odd-prime-order subgroups G = <P> of cofactor 1 on deterministically generated ordinary short
   H-ECDLP-15d016 Fix the one-step next-feature split of a parity feature on a prime-order additive group before any p
   H-ECDLP-7b7398 Fix the multiplicative N^2-th-root uniqueness on F_p^* before any cubical point, division polynomial
### U(kP) character: 5
   IDEA-20260805-2acde5 If the audit of IDEA-20260805-c4ae3d holds, the headline claim about SQIsign is TRUE: no torsion ima
   IDEA-20261016-53ec5d (M) F_p^*, naive section s(a)=a in [1,p), q(a)=(a^(p-1)-1)/p, integer generator g, d in [2,n-2], k_d
   H-ISOU-d1a4a5 The pinned native command may construct and independently verify the selected compact known-CM M8191
   H-ISOU-ffa8b0 The pinned native command may construct and independently verify the selected compact known-CM M4449
   H-SEMBIN-ce9e29 On the single summation polynomial S_3 over F_2[z]/(z^3+z+1), with B = 1, the shift x1 -> x1+1 keeps
```

### N3 reading: the three full records opened, plus non-ledger evidence

Full ledger records opened (the permitted three): IDEA-20260904-f68c7f, IDEA-20260905-b6154d, IDEA-20261017-e3a6f1. Everything else from the ledger is at index-row level. Non-ledger files read: crypto repo research/prime_fourier_flatness_exp7_20261007/RESULT.md; experiments/EXP-ECDLP-56ee42/specification.yaml (head) and the key names / gate fields of its three run records; knowledge/open-problems/KN-OPEN-020.md; knowledge/findings/KN-FIND-ffe1df.md (Theorem C passage).

**IDEA-20260904-f68c7f (conversion).** Contains, as exact algebra, the identity g_c(j)=v(x([j]P+[c]Q))=f(j+ck), so that the c-scaled copy of the DL-Fourier coefficient carries k in its PHASE; the Hoeffding estimator M=O(eps^-2 delta^-2 log(1/eta)); an assembly into a Boneh-Venkatesan HNP with polylog memory; total cost eps^-2 n^o(1); and the threshold "A(v) > n^(-1/4 + o(1))", i.e. beta < 1/4. It reconciles the identity with the prime-order rigidity theorem in writing ("a strictly smaller action"). Its part (F) says the reduction consumes a KNOWN frequency and that locating it at cryptographic n "is a separate problem"; its novelty screen credits IDEA-20260901-a66d70 (AGS sparse-Fourier calls) as closest prior art and says it is "entirely possible that (A)-(D) is folklore". This is QC5's upper bound with HNP lattices in place of AGS recovery.

**IDEA-20260905-b6154d (spectrum, break-even, the remaining door).** Claims, conditional on two recalled results that its own record says were not opened (Bombieri/Kohel-Shparlinski character sums; Deligne), that every bounded-degree coordinate function g in a class C(D,L) has every DL-character correlation at the Weil level c*j*D*L*sqrt(p), "a WHITE DL-spectrum"; that detecting such a bias costs Theta(N/polylog) samples; that hard-core-bit amplification costs polylog(N)*eps^-c_amp with c_amp = 2 "recalled" under the AGS reduction (via KN-LIT-4155), giving the break-even eps* = N^(-1/4) polylog; and that "the door that remains" is functions cheap to evaluate but of degree exponential in the iteration count, with the Miller loop named as the existence proof. U(R)=f(R)^(1/N) is such a function. This is QC5's threshold, QC5's white-spectrum prior, and QC5's choice of U, all already recorded.

**IDEA-20261017-e3a6f1 (Miller U).** K1/K2 as quoted by the candidate; H1 "ell(k)=log_g U(kP) is uniform on Z/(p-1) jointly with characters of Z/N". minimal_test: "DFT over Z/N for multipliers a in {1,2,N,(p-1)/q} plus 128 random a", p<=2^20, special (m^d-c) and matched random primes, 30 curves each, controls "N | p-1 reduced pairing (peak)", "random F_p^*-valued function with equal marginal", "k-shuffled ell", "special vs random prime"; falsification at "spectral max above ln(256 N)+12". Differences from QC5's first step on U: QC5 restricts to power-residue characters of order 2,3,4 (a subset of the (p-1)/q multipliers), takes N up to 2^24 (e3a6f1 uses F_p^* logs by table, p<=2^20), uses 3 curves per N (e3a6f1: 30), and states the threshold as the maximum of N Gaussians (e3a6f1: a ln(256N)+12 tail bound, the same form). The k-shuffled null is QC5's random-relabelling null; the N|p-1 reduced-pairing cell is a positive control of the same kind as QC5's planted homomorphism.

**EXP7 (crypto repo, executed).** Exact FFT over Z/n of f(k)=predicate(x([k]G)) for six abscissa predicates (B-smooth, bounded partial quotients, base-3 Cantor digits, low Hamming weight, Farey height, Legendre triple) on four prime-order curves of 8, 10, 12, 14 bits, 512 matched random nulls per cell with the +-k symmetry preserved, a log-interval positive control (peak/null-95 ratios 2.58-15.43, passes), SHA-256 and random-pair controls; preregistered rule p<=0.05/24; "None met it" (smallest empirical p 0.01754, Legendre cell, Bonferroni-adjusted 0.42105). It also stores the inverse transform of F(j)^2 (ordered-pair sum vector). For x-coordinate predicates f(k)=f(-k), so F is real and F^2=|F|^2; for those cells the stored pair-sum vector is the autocorrelation QC5 calls A_s (my inference from the formulas; I did not recompute it from results.json). It does NOT cover chi(U(kP)), N above 2^14, or learned features.

**EXP-ECDLP-56ee42 (approved experiment, digit-statistic cell).** Exact A(v)=max|fhat(a)| and majority advantage for the Thue-Morse and Rudin-Shapiro digit signs of x over a six-rung ladder of 17-27 bit prime-order curves, keyed-random null (256 replicates), matched-marginal shuffle, two planted positives. Status approved (v1 2026-09-03, amendments v2-v5 on file). Run records RUN-ECDLP-56ee42-S0/S1/S2 exist; the S2 raw-result.json lists gates POS-A true, POS-B true, CONTROL-C false, static_provenance false and "validity: gate_failure". I read only these fields, not the amendments or reviews. Reading: the digit-character measurement QC5 proposes (its 2^16-2^24 slice of "digit characters of x") has an approved contract and a gate-failed run, so it is a repair/continuation of an existing experiment, not a new cell.

**ML half.** H-REPL-6c431d (specified): a neural model trained to predict a DL bit from coordinates "extracts ZERO coordinate structure"; its mechanism reads the model as S bits of advice (discrete log with preprocessing, generic-with-advice bound). IDEA-20260806-94676a: exact latent linearisation is the DLP. LEAD-EXO-ml-learned-models keeps the empirical learnability control open. No ledger or atlas record mentions statistical queries, SQ dimension or correlational queries (0 hits in both sweeps).

#### What the SQ half is, and its scope as I read it (OBSERVATIONS, not results)

- Under uniform examples (a, s(Q+aP)) with the dilation c fixed, the concepts kappa -> (a -> g_s(kappa+a)) have pairwise correlation A_s(kappa-kappa'). If max_{d!=0}|A_s(d)| = gamma_s, the N shifts are pairwise gamma_s-correlated, so the SQ dimension at threshold gamma_s is at least N. That is the BFJKMR94 characterisation (retrieved above) applied through a one-line identity; it contains no new mathematics.
- The same record's upper bound uses CHOSEN dilations c (queries to cQ+aP). A learner with that access is outside the c-fixed random-example SQ model, so the lower bound constrains only learners restricted to one target's labelled points. The candidate flags the scope itself ("SQ scope", "exact exponent is not claimed", "conditional on fixing the SQ-dimension statement used").
- For the ML lead, the learning problem is "predict a bit of log_P(R) from R" with P fixed, a single concept, not a class of shifts; the bridge from gamma_s to that problem is not supplied. H-REPL-6c431d argues the closure by the preprocessing bound instead.
- gamma_s is not implied by tau_s: A_s is the inverse transform of |ghat|^2, so a large A_s needs many moderate coefficients aligned in phase. It is an independent observable in principle. For the whitespectrum class of b6154d (C1) both sit at the random level together.

#### Conditional observation on the Miller-value slice (flag for the owner of LEAD-TRF-miller-cocycle-nonhom-transfer; I changed no disposition)

Provenance: **recalled** (Weil-Deligne bound for Kummer/Lang sheaves and the Grothendieck-Ogg-Shafarevich Euler-characteristic formula; none opened here, not checked against a source in this gate). The derivation below is mine; it is a conditional argument, not a result and not a measurement.

1. With gcd(N, p-1) = 1, U(R) = f(R)^(N') with N' = N^(-1) mod (p-1), so for a multiplicative character chi of F_p^* of order m, chi(U(R)) = chi'(f(R)) with chi' = chi^(N') of the same order m.
2. f = f_{N,P} has div f = N(P) - N(O). Because gcd(N, m) = 1, m does not divide N, so the Kummer sheaf L_chi'(f) is tamely ramified at exactly the two points P and O, for every nontrivial chi, whatever the size of N.
3. Tensor with the Lang-torsor sheaf of an additive character psi_a(R) = e(a log_P(R)/N) (lisse on E, no extra ramification). On E minus two points the Euler characteristic is -2, the tensor is geometrically nontrivial (it is ramified), so H^1 has dimension 2 and, conditionally, |sum_R chi(U(R)) psi_a(R)| <= 2 sqrt(p) + O(1) for every nontrivial pair (chi, a). For a subgroup G of index h > 1 one averages over the h extensions of psi_a to E(F_p), which keeps the same bound.
4. Then |ghat(a)| <= about 2 sqrt(p)/N and sqrt(N) * tau <= about 2 sqrt(p/N), which is about 2 for N close to p, below the maximum-of-N-Gaussians line (about 4.1 at N = 2^24, ARITHMETIC: sqrt(ln 2^24)). The multiplicity of the zeros/poles of f enters only through whether m divides it, not through its size.
5. Consistency check with the recorded cells: if m divides N (the pairing case N | p-1, m = N allowed) the sheaf is unramified and the sum can reach N, which is the "peak" of e3a6f1's N | p-1 positive control and the object (D2) of b6154d.
6. Scope: this covers multiplicative characters of U only. It does not cover the Smart-ratio part of H1, bits of log_g U, digit statistics of U as an integer, or any function whose expansion in multiplicative characters has a large L1 norm (the bound is multiplied by that norm and goes vacuous exactly as in the digit family). It says nothing about the coordinate/digit cells or the ML cells.
7. Consequences if it holds: b6154d's phrase "bounded degree" should read "bounded conductor" for the multiplicative case (its (B) states c*deg*sqrt(p), loose for case (ii)); the U-slice of QC5 would be a consistency check of an implementation against a bound, not a discriminating experiment; and e3a6f1's "rigorous_support: ... imitates random units" could be replaced by this argument. The owner of the lead should decide whether to verify it against a source.

---------------------------------------------------------------------------
## N4  Notation change (QC5 is a coordinate/representation candidate)
---------------------------------------------------------------------------
**Pair.** (representation, operation set) = (an F_p-coordinate statistic x(R) or y(R), or the Miller value U(R) in F_p^*, i.e. R1/R3 in the program's naming; Sigma = the affine maps Q -> cQ + aP on the discrete logarithm k -> ck + a, realised by known multiples of P and Q). Trichotomy class: coordinate-dependent (candidate's own assignment, consistent with e3a6f1's). The tracked object is the pulled-back function g_s on Z/N, which propagates exactly only through its Fourier phase under k-shifts and otherwise only as a correlation.

**Comparison with the recorded rigidity results.**
- IDEA-20260806-c5d183 and IDEA-20260807-df906f (index rows read; the theorem as stated in the rows): no lossy projection propagates deterministically under the FULL translation action on a prime-order group; every exactly propagating projection is constant or injective. QC5 does not claim a projection that propagates under full translation. Its object uses the one-parameter family of shifts by multiples of k. IDEA-20260904-f68c7f part (A)/mechanism (which I read) already makes this exact reconciliation, so the pair is not a new escape from the theorem; it is the recorded "probabilistic regime".
- IDEA-20260901-863e36 (index row read): propagation belongs to a projection PAIRED with an operation group, with Gamma a subgroup of (Z/n)^* acting by R -> [gamma]R and canonicalisation cost charged. QC5's Sigma includes dilations by arbitrary c in (Z/N)^*, each costing one scalar multiplication, and never forms a quotient, so no canonicaliser is needed or claimed. This is the standard random self-reduction used by Boneh-Shparlinski and AGS (recalled; Duc-Jetchev abstract retrieved), recorded in f68c7f. Not a new arithmetic.
- KN-OPEN-020 (read): the universal algebraic-factor-base no-go is open for high-degree, implicit-membership, target-dependent descriptions; bounded-degree is scoped out. QC5 builds no factor base and makes no IC claim. U is an implicit, high-degree description (Miller loop value, N-th root), so a set {R: chi(U(R))=1} used as a factor base WOULD sit in the open class, but QC5 only measures whether such a set's DL-character sums are above the random level; by the Betti-yield duality (KN-FIND-9d2f56, cited in the character-sum lead) that is the quantity a sub-rho combinatorial IC would need. Measuring it informs the open class and does not enter it. The bounded-degree statistics are covered by b6154d's Weil-level ceiling (conditional on two unopened recalled results).
- KN-FIND-ffe1df Theorem C (read, text of the finding): "A tree must invert f in each argument to index buckets, so f is a quasigroup. Exact sum-compatibility plus associativity of + on E forces f associative; an associative quasigroup is a group; so h is a surjective homomorphism E(F_p) -> ([M],f), impossible for N prime and M < N." QC5 uses no combining rule or tree, so Theorem C is not engaged. In new notation: Theorem C is the exact case (a filter compatible with +); a statistic correlating with a character of Z/N at level tau is the Fourier-analytic approximate case, and the same finding's Proposition 2 (as reported in the finding) notes the dlog-pullback reaches eps ~ 1/2 at any M so only a cost clause can exclude it. QC5's spectral test is exactly a test of that cost-restricted approximate case. Recorded, not new.

N4 outcome: the pair is recorded (f68c7f, b6154d, 863e36, c5d183/df906f); no new notation hides a rigidity conflict; no rigidity result is contradicted.

---------------------------------------------------------------------------
## Heuristics (numbered; all conditional)
---------------------------------------------------------------------------
H-1. (b6154d, conditional on Bombieri/Kohel-Shparlinski/Deligne-type bounds not opened there) For bounded-degree coordinate functions with F_p-spectral L1 norm L, every Z/N-Fourier coefficient is O(L N^(-1/2+o(1))). Digit-type statistics have L ~ p^0.39 (KN-FIND-ffe1df as quoted in f68c7f), so for them the bound is vacuous and only measurement speaks.
H-2. (e3a6f1 H1, unrun) chi(U(kP)) has a white Z/N-spectrum on special and matched primes. b6154d places U outside its class C(D,L) because its degree is about N, so b6154d's c*deg*sqrt(p) form is vacuous for it. A sharper, conductor-based form of the same Weil-Deligne input appears to reach U for every nontrivial multiplicative character: see "Conditional observation on the Miller-value slice" below (my derivation from recalled theorems, not opened, conditional). If it holds, the joint-character part of H1 and QC5's order-2,3,4 cells on U are decided by that bound, not by an FFT; the Smart-ratio part of H1 and non-character functions of U are not covered.
H-3. If a heavy frequency is known, conversion costs ~tau^-2 n^o(1) (f68c7f, Hoeffding + HNP; derivation read). If the frequency must be located by the SFT algorithm, the retrieved bound Theta~(log N / tau^5.5) (+-1-valued f, Akavia thesis) gives a single-target break-even tau > N^(-1/11) (ARITHMETIC), with the locating step independent of the target Q.
H-4. gamma_s at the random level gives SQ dimension >= N for the c-fixed shift class only; it does not bound algorithms with chosen dilations or generic algorithms (SO-GEN untouched).

Predictions (labelled; none is a result): the candidate's own prior of under 5 percent for any heavy coefficient at N >= 2^20 and its predicted gain of 0 bits are the candidate's predictions. The only measured facts I relied on are EXP7's 24 cells at 8-14 bits (no preregistered lead), the character-sum lead's R = 1.28-1.34 at 2^20-2^26, and the gate-failed state of EXP-ECDLP-56ee42 S2.

---------------------------------------------------------------------------
## Verdict
---------------------------------------------------------------------------
**duplicate_of_lead.** Lead: LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined) for the B7 measurement, with its next_action carried by IDEA-20261017-e3a6f1 (minimal_test); conversion half LEAD-EXO-hnp-advice-leakage via IDEA-20260904-f68c7f and IDEA-20260905-b6154d; digit-character cells LEAD-EXO-coordinate-statistic-leakage / EXP-ECDLP-56ee42; ML cells LEAD-EXO-ml-learned-models (same positive control, null and N ceiling).

Reasons, shortest first:
1. Upper bound (heavy coefficient at tau => DL, sub-rho iff tau >= N^(-1/4)) is recorded in the ledger twice with the same exponent comparison (f68c7f derivation; b6154d with c_amp=2 recalled) and in the literature (AGS 2003; Akavia thesis; Duc-Jetchev 2012). It is absent from KRMAP, which is a map gap, not novelty.
2. The Z/N-FFT instrument with matched nulls and planted positives has been specified (f31bc4, H-ECDLP-0bc396, e3a6f1), executed at 8-14 bits (EXP7, no lead), and contracted at 17-27 bits for the digit family (EXP-ECDLP-56ee42, S2 gate_failure).
3. The chi(U(kP)) first step is the open lead's own next_action; e3a6f1's minimal_test contains the DFT over Z/N, the k-shuffled null, the reduced-pairing positive control and the same Gaussian-max threshold.
4. Residual content not already specified, and why it does not change the verdict: (a) the SQ-dimension read-out through the autocorrelation (no hit anywhere in the atlas or ledger index; textbook identity, scope-limited to c-fixed examples, bridge to the ML lead not supplied); (b) a 2^24 slice for power-residue characters of order 2,3,4 on U without an F_p^* log table (a parameter extension, and a strict subset of the characters e3a6f1 already lists). Both can be filed as amendments to the existing next steps.
5. The candidate's cost line "O~(log N / tau^2) with the coefficient found offline" merges a known-frequency phase cost with the frequency-location cost. With the retrieved SFT algorithm (Theta~(log N / tau^5.5) for +-1-valued f, Akavia thesis; a better sparse-Fourier algorithm with a smaller exponent in 1/tau may exist, recalled) and the locating cost charged per target, ARITHMETIC gives a single-target break-even tau > N^(-1/11). With a precomputed frequency it is f68c7f's N^(-1/4). The location step does not depend on the target Q (an exact offline FFT is O(N log N) precomputation that yields only about log N bits of advice), so which threshold applies depends on an accounting choice the candidate does not make. This is a statement about the cost model, not a refutation.
6. Conditional and recalled (see "Conditional observation on the Miller-value slice"): a conductor-based Weil bound appears to place every nontrivial chi(U) cell at sqrt(N)*tau <= about 2, so QC5's power-residue cells on U would be decided by that bound, not by an FFT. This strengthens, and does not change, the verdict.

What I did not do: no computation of any FFT or statistic, no re-derivation of K1/K2, no reading of the EXP-ECDLP-56ee42 amendments or reviews, no opening of KN-LIT-5602 or KN-LIT-043, no verification of Feldman-Guzman-Vempala or of Yang's theorem statements.
