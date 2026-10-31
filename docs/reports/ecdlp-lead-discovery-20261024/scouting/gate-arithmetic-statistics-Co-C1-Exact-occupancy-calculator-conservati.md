# Gate N1-N4: arithmetic-statistics candidate C1 (exact occupancy calculator)

Gate run by the scout subagent; read-only on the repositories; all files written under this scout directory.
Candidate field_key: arithmetic statistics (second-moment / Poisson counting of decomposition counts).
Candidate one-line: exact target-free population coverage of the useful-triple sumset of a size-B signed base, with a two-sided band
lambda/(1+kappa2*lambda) <= coverage <= lambda and kappa2 tied to pair-sum coincidences, offered as a closure instrument for the
EXP-ECTD-0cf008 crater/floor arity-3 panel (B1/B3 instrument).

Scope note: I did NOT re-run the candidate's calculators (popcov/popsample/paircoin in scout/arith-stats-r2/) and I did NOT reproduce any
of its P29/P37 numbers. Every measured number below is quoted as "candidate-reported". The gate decides novelty only.
Tool note: the raw directory scout/raw/ also holds files from earlier scout runs (atlas_*.txt, frontier_*.txt, part1_analysis.md, ...).
Those are not mine and are not used. This gate's raw outputs are raw/la1..la4.txt (lead_atlas) and raw/fm1..fm4.txt (build_frontier_map),
pasted verbatim below.

======================================================================
## RAW OUTPUTS (verbatim)
======================================================================

### python3 tools/lead_atlas.py --match "exact population coverage of the useful-triple sumset of a factor base, crater versus floor"   (phrasing 1)
```
   25  LEAD-ICP-isogeny-transported-relation-yield  open_blocked       Isogeny-transported or volcano-level factor bases and the arity-3 relation oracle (crater vs floor)
   18  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
   14  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   10  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
   10  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
```

### python3 tools/lead_atlas.py --match "count every target a factor base can decompose instead of sampling targets"   (phrasing 2)
```
   15  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
   12  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   12  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   11  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   10  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   10  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   10  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
```

### python3 tools/lead_atlas.py --match "mean per-target yield conservation and coverage gain across isogenous curves"   (phrasing 3)
```
    9  LEAD-RHO-advice-table-variants               open_next_step     Variants of the advice table: batch-reselected, batch-grown, basin-instrumented and transported tables
    9  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
    8  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    7  LEAD-ICE-decomposition-probability-audit     open_next_step     Decomposition probability P(decomp) vs factor-base size, charged p_solve, and learned decomposability predictors
    6  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
    6  LEAD-ICB-factor-base-subspace-choice         exhausted_at_scale Choice of the factor-base subspace V at fixed dimension (geometric progression, dim(V.V), trace rank, cosets, greedy coverage, HW pools, trace-parity window)
    6  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
```

### python3 tools/lead_atlas.py --match "second-moment Paley-Zygmund Markov ceiling decomposition coverage pair-sum coincidences additive energy factor base"   (phrasing 4, my own)
```
   25  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
   17  LEAD-ICB-kic-golden-base-exact-decomp        open_next_step     Co-designed binary factor bases with exact decomposition: affine 2-flats, orbit-canonical abscissa lookup, SAT vs exact MITM (KIC lane)
   16  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
   16  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
   14  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
   12  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
   12  LEAD-ICE-semaev-yield-model-coset-typing     open_next_step     Semaev yield model (eq. 11, the m! factor) and coset-typed / trace-parity factor bases
```

### python3 tools/build_frontier_map.py --match "exact population coverage of the useful-triple sumset of a factor base, crater versus floor"
```
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
KR-RHO-1c2928  score=4  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-cd0049  score=3  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
```

### python3 tools/build_frontier_map.py --match "count every target a factor base can decompose instead of sampling targets"
```
KR-IC-5a43e5  score=12  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-b0fcda  score=9  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-6654ba  score=4  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-46c2c6  score=3  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-0528e7  score=2  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
```

### python3 tools/build_frontier_map.py --match "mean per-target yield conservation and coverage gain across isogenous curves"
```
KR-RHO-755e35  score=7  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-RHO-825bca  score=6  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-IC-1fcdbc  score=4  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-9e610d  score=4  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-RHO-1c2928  score=4  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-46c2c6  score=4  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-cb1c58  score=4  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-RHO-cd0049  score=4  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
```

### python3 tools/build_frontier_map.py --match "second-moment Paley-Zygmund Markov ceiling decomposition coverage pair-sum coincidences additive energy factor base"
```
KR-IC-b0fcda  score=12  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-5a43e5  score=11  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=9  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
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

### N3 raw ledger grep output (proposals.jsonl + hypotheses.jsonl; title/claim/statement/mechanism fields, case-insensitive; helper scout/C1work/lgrep.py)
```
##### lgrep all crater floor
[prop] IDEA-20260731-017 | unverified | Large-conductor vertical barrier — measure ECDLP-meter discontinuity across a prime conduc | Let E_floor and E_crater be ordinary F_p-isogenous curves whose endomorphism rings differ by an inde
[prop] IDEA-20260807-a2b59a | proposed | THE TWO-ell MISMATCH CONTROL: one curve carries two contradictory depths -- crater in the  | (A) THE FACT THE DESIGN EXPLOITS. For distinct primes ell_1, ell_2 dividing c, the coordinates v_{el
[prop] IDEA-20260811-dcbea4 | proposed | THE COST OF WRITING A GLOBAL CM LIFT DOWN IS |D|^{1+o(1)} AT THE FLOOR AND |D_0|^{1+o(1)}  | (A) THE TWO-SIDED SIZE IDENTITY. For a CM point of discriminant D, the largest archimedean conjugate
[prop] IDEA-20260922-1f9967 | proposed | Per-block new_falls on symmetry sectors, crater automorphism versus floor | Representation class R1 of RQ-ECDLP-623a32 (summation coordinates, split into isotypic blocks), atta
[prop] IDEA-20261005-b4c2bf | proposed | Least rational root of the 3-division polynomial across one height-2 volcano, against a co | Let p be the least prime in the closed interval from 17 to 199 for which an ordinary 2-isogeny volca
[prop] IDEA-20261006-52015b | proposed | Floor-versus-crater gap in liftable roots of one S_3 slice on a toy ordinary 2-volcano | On one complete ordinary 2-isogeny volcano over a prime p in (300, 2000), with j-invariants 0 and 17
[prop] IDEA-20261015-e0b5dd | proposed | Pushing crater bases through the conductor-v isogeny: exact conservation through a group i | (A) Frobenius is -1 on E[v] (pi + 1 = vw), so all v+1 subgroups of E[v] are F_p-rational kernels; ea
-- proposals.jsonl: 7 hits for all ['crater', 'floor']
[hypo] H-CANL-d4190b | specified | Stage 0 cost writing global lift down floor identities — n=3 — before any later stage is a | Fix the exact count identity of IDEA-20260811-dcbea4 before any later-stage claim. Stage 0 asserts o
[hypo] H-ECTD-19017a | specified |  | Let E_floor and E_crater be ordinary F_p-isogenous curves whose endomorphism rings differ by an inde
[hypo] H-ECTD-e88346 | approved |  | For the two specified ordinary prime-field crater/floor pairs with prime conductor steps 8209 and 13
-- hypotheses.jsonl: 3 hits for all ['crater', 'floor']
##### lgrep all conservation coverage
[prop] IDEA-20260805-a7a716 | unverified | The coverage channel of factor-base geometry is bounded by e/(e-1) = 1.581977 for every ba | Two derivable statements about the EXP-FB3-001 measurement apparatus, neither of which requires a ne
[prop] IDEA-20260830-772cff | proposed | THE CHANNEL-SCOPED KILL, AT THE CLOSURE STANDARD. Three named bounds - yield advantage exa | (A) WHAT THIS RECORD IS. It is a derivation-level closure argument for RQ-FBG-001's decision target,
-- proposals.jsonl: 2 hits for all ['conservation', 'coverage']
[hypo] H-ICEX-ab1da2 | proposed |  | THE ONE CHANNEL THIS PROGRAM'S CONSERVATION FINDING NAMES AS UNCAPTURED IS RELATION RANK, AND THIS R
[hypo] H-PFDR-26bcee | proposed | A CHANNEL-SCOPED closure of the factor-base geometry family on the yield, coverage and ran | (A) WHAT THIS RECORD IS. A derivation-level closure argument for RQ-FBG-001 decision target, written
-- hypotheses.jsonl: 2 hits for all ['conservation', 'coverage']
##### lgrep all second moment
[prop] IDEA-20260805-5a4409 | unverified | Parseval energy budget of the dual-FFT distinguisher: an exact conservation law that force | In the FFT variant of the dual attack the scores of ALL p^{k_fft} candidate secrets are, exactly and
[prop] IDEA-20260805-637a3b | unverified | The width homotopy from NTRUSign to FN-DSA: sigma is the parameter that is supposed to des | RQ-FNDSA-001's motivating analogy is that NTRUSign died from distributional rather than timing error
[prop] IDEA-20260805-64aef4 | unverified | The section-incidence over-dispersion factor: the second moment of the archived xedni cens | DEC-20260724-021 rejected H-XEDN-001 on an exact FIRST-moment identity, P_lift(p) = (1 - 2/p + p^-3)
[prop] IDEA-20260807-3d9c9f | unverified | Across-key overdispersion phi = Var_K(N)/E_K(N) of a truncated-differential hit count as a | FORMALIZATION OF CATALOGUE ENTRY A1-7 (ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/A1.md, lines 550-
[prop] IDEA-20260808-d8510c | proposed | The one unproven step in the only viable proof route for Heuristic 1 is a second-moment bo | This program's own analysis (research/P13-HEUR-001/heuristic_analysis.md, Route (b)) established tha
[prop] IDEA-20260813-2d839b | proposed | Sibling-copula defect probe: a public cross-node interaction statistic for sampler errors  | On a frozen toy recursive sampler with an exact public coefficient view, one can construct a planted
[prop] IDEA-20260816-0a9533 | proposed | Signatures without repetition as the tracked object: measure whether the empirical second- | (A) The in-repo treatment of signature-side leakage in this family is entirely about repetition: H-M
[prop] IDEA-20260816-50d270 | proposed | Every decoding-failure number this campaign has produced rests on a single implementation  | (A) THE EXPOSURE. GOAL-HQC-001's committed evidence chain - EV-HQC-b71230's 17-cell joint-moment tab
[prop] IDEA-20260904-f7d47d | unverified | THE O2 LINE'S LOAD-BEARING HOLE IS A SECOND MOMENT NOBODY HAS MEASURED: Lemma 5 bridges th | (A) THE EXACT CLAIM. Let E/F_p have #E(F_p) = N prime, let h : E(F_p) -> [M] be a cheaply computable
[prop] IDEA-20260905-64397d | proposed | Orbit stabilizers and the second factorial moment of relation supply | For a factor base consisting of complete automorphism orbits, the mean raw tuple count is insufficie
[prop] IDEA-20260905-9a5462 | proposed | Second-moment geometry of Frobenius correspondences before rare-stratum claims | A uniform second-moment bound for the multiplicity of short primitive Frobenius correspondences can 
[prop] IDEA-20260905-be63be | proposed | Orbit stabilizers and the second factorial moment of relation supply | For a complete automorphism-orbit factor base, stabilizer-weighted tuple-target incidence and its se
[prop] IDEA-20260905-cea1d6 | proposed | Second-moment geometry of Frobenius correspondences before rare-stratum claims | A uniform second-moment bound for the multiplicity of short primitive Frobenius correspondences can 
[prop] IDEA-20260906-d1494b | proposed | THE POINT-RELATION HYPERGRAPH AND THE SECOND-MOMENT IDENTITY: 'clusters of easier decompos | SETTING. G a cyclic group of prime order N: either E(F_p) of prime order or the abstract Z/N as cont
[prop] IDEA-20261017-3db2a8 | proposed | The Semaev yield is an exact first moment d(V)*C(|W|+t-1,t)/N: the Poisson link is second- | SCOPE: derivation plus zero-compute arithmetic from the frozen paper and one toy check. No security 
-- proposals.jsonl: 15 hits for all ['second', 'moment']
[hypo] H-EQIC-aa2c3a | specified | Stage 0 orbit stabilizers factorial moment relation supply identities — n=2 — before any l | Fix the exact count identity of IDEA-20260905-be63be before any later-stage claim. Stage 0 asserts o
[hypo] H-EQIC-e0c65e | specified | Stage 0 orbit stabilizers factorial moment relation supply identities — n=2 — before any l | Fix the exact count identity of IDEA-20260905-64397d before any later-stage claim. Stage 0 asserts o
[hypo] H-FNDSA-58b464 | proposed |  | SCOPE: the second-moment tensor of the signature cloud produced by a Klein-family sampler at width s
[hypo] H-ICEX-77c62a | proposed |  | The coordinate-placement channel of RQ-JINV-8fc13a is a SECOND-MOMENT object and it is predicted to 
[hypo] H-RELN-427bfd | proposed |  | A deterministic, pinned symbolic-regression pipeline -- primary engine an exhaustive bounded grammar
[hypo] H-SSI-63817e | specified | Stage 0 complementary second-moment identities — two moments retained — before any multipl | Fix the exact two-moment identity of IDEA-20260905-cea1d6 before any multiplicity is assumed uniform
[hypo] H-SSI-bdbb2c | specified | Stage 0 second-moment identities — two named moments — before any rare-stratum claim is ma | Fix the exact two-moment identity of IDEA-20260905-9a5462 before any rare-stratum claim is made. Sta
-- hypotheses.jsonl: 7 hits for all ['second', 'moment']
##### lgrep all paley
-- proposals.jsonl: 0 hits for all ['paley']
-- hypotheses.jsonl: 0 hits for all ['paley']
##### lgrep all chen-stein
-- proposals.jsonl: 0 hits for all ['chen-stein']
-- hypotheses.jsonl: 0 hits for all ['chen-stein']
##### lgrep any poisson
[prop] IDEA-20260807-3d9c9f | unverified | Across-key overdispersion phi = Var_K(N)/E_K(N) of a truncated-differential hit count as a | FORMALIZATION OF CATALOGUE ENTRY A1-7 (ideas/catalogue-20260806-mlkem-aes-ssi-ssqi/A1.md, lines 550-
[prop] IDEA-20260808-bfee7e | proposed | A CLOSED-FORM null for the campaign's own r=5 yoyo excess, derived from ShiftRows/MixColum | GOAL-AES-003 records an r=5 yoyo hit count of 59 for AES against a null expectation of 4.0 (BATCH-00
[prop] IDEA-20260816-fa2fe6 | proposed | Audit the load-bearing heuristic instead of the sampler: H-FNDSA-6a9cbb's divergence bound | (A) The closed-form divergence result recorded in this corpus as H-FNDSA-6a9cbb derives a per-signat
[prop] IDEA-20260906-74c257 | proposed | Capacity-controlled hitting of low-degree Frobenius strata | A publicly evaluable approximate hitting potential for the low-degree Frobenius stratum can improve 
[prop] IDEA-20260906-cf3b76 | proposed | THE OFFSPRING-VARIANCE INVARIANCE CONTROL: every point-local distinguishing rule at fixed  | (A) THE ARGUMENT (derivation of this record, to be re-derived by a validator). Under H1 of IDEA-2026
[prop] IDEA-20260910-c5d0e5 | proposed | Larger exchanged-boomerang trail clusters with joint inactive-diagonal predicates and hone | TRACKED CLAIM (REF-A / REF-B / REF-C only). There exists a secret-key distinguisher for AES-128 at r
[prop] IDEA-20260923-5d07e3 | proposed | THE WALK'S IN-DEGREE VARIANCE IS A TABLE CONSTANT: an r-adding walk has in-degree Binomial | (A) THE LAW (derivation of this record). For a walk f(x) = g_{h(x)}(x) with bijections g_1..g_r (r-a
[prop] IDEA-20261017-3db2a8 | proposed | The Semaev yield is an exact first moment d(V)*C(|W|+t-1,t)/N: the Poisson link is second- | SCOPE: derivation plus zero-compute arithmetic from the frozen paper and one toy check. No security 
-- proposals.jsonl: 8 hits for any ['poisson']
[hypo] H-AES-42c479 | proposed |  | At AES-128, r in {5, 6}, with M = 2^20 truncated-differential pairs per key and m = 2^12 keys, the a
[hypo] H-AES-bd82dc | specified | Stage 0 larger exchanged-boomerang trail clusters joint inactive-diagonal identities — n=4 | Fix the exact count identity of IDEA-20260910-c5d0e5 before any later-stage claim. Stage 0 asserts o
[hypo] H-ECDLP-fadd65 | approved | Binomial(r, 1/r) has variance (r-1)/r for r in {2, 3, 4, 16}, which is 1/r below the Poiss | For r in {2, 3, 4, 16}, the variance r*(1/r)*(1-1/r) equals (r-1)/r. The four values are 1/2, 2/3, 3
-- hypotheses.jsonl: 3 hits for any ['poisson']
##### lgrep all factorial moment
[prop] IDEA-20260905-64397d | proposed | Orbit stabilizers and the second factorial moment of relation supply | For a factor base consisting of complete automorphism orbits, the mean raw tuple count is insufficie
[prop] IDEA-20260905-931866 | proposed | Local-density corrected factorial moments for smooth primitive norm values | Conditioning smoothness on primitive norm representability requires a local-density correction and a
[prop] IDEA-20260905-be63be | proposed | Orbit stabilizers and the second factorial moment of relation supply | For a complete automorphism-orbit factor base, stabilizer-weighted tuple-target incidence and its se
[prop] IDEA-20260905-c6aae0 | proposed | Local-density corrected factorial moments for smooth primitive norm values | Conditioning smoothness on primitive norm representability requires a local-density correction and a
-- proposals.jsonl: 4 hits for all ['factorial', 'moment']
[hypo] H-EQIC-aa2c3a | specified | Stage 0 orbit stabilizers factorial moment relation supply identities — n=2 — before any l | Fix the exact count identity of IDEA-20260905-be63be before any later-stage claim. Stage 0 asserts o
[hypo] H-EQIC-e0c65e | specified | Stage 0 orbit stabilizers factorial moment relation supply identities — n=2 — before any l | Fix the exact count identity of IDEA-20260905-64397d before any later-stage claim. Stage 0 asserts o
[hypo] H-ICLIFT-4d4384 | proposed |  | SCOPE: the frozen EXP-XEDN-002 family y^2 = x^3 + b(t) over F_p with deg b = 6 exactly, the frozen i
[hypo] H-RELN-427bfd | proposed |  | A deterministic, pinned symbolic-regression pipeline -- primary engine an exhaustive bounded grammar
[hypo] H-SSIQ-8de17f | specified | Stage 0 local-density corrected factorial moments smooth primitive identities — n=2 — befo | Fix the exact count identity of IDEA-20260905-c6aae0 before any later-stage claim. Stage 0 asserts o
[hypo] H-SSIQ-ee9627 | specified | Stage 0 local-density corrected factorial moments smooth primitive identities — n=2 — befo | Fix the exact count identity of IDEA-20260905-931866 before any later-stage claim. Stage 0 asserts o
-- hypotheses.jsonl: 6 hits for all ['factorial', 'moment']
##### lgrep all coverage floor
[prop] IDEA-20260808-9d6677 | proposed | Marginal Boolean-success signed-y four-list cascade with matched-mean clustering, repeated | CONDITIONAL ALGORITHM TARGET, NOT A RESULT OR ATTACK CLAIM. Let G=<P> have prime order N, let Q=[k]P
[prop] IDEA-20260816-c9565d | proposed | Calibrate the detection floor of factor-base geometry measurement by planting a tunable am | (A) THE PROBLEM. This program has recorded coverage excesses for structured factor bases of 1.0012, 
[prop] IDEA-20260828-b0694b | proposed | Audit the fragmentation, not just the criterion: real independently-versioned deployed cop | (A) Every detector-audit proposal in this batch -- the symbolic coverage enumeration (IDEA-20260816-
[prop] IDEA-20260930-79c17d | proposed | THE THREE-CLASS COVERAGE FLOOR AND THE OVERLAP-LOSS DECOMPOSITION OF THE GRUMPY CONSTANT:  | SETTING. Generic group of prime order l >= 5, realised as Z/l with generator 1; target x uniform on 
-- proposals.jsonl: 4 hits for all ['coverage', 'floor']
-- hypotheses.jsonl: 0 hits for all ['coverage', 'floor']
##### lgrep all additive energy
[prop] IDEA-20260805-15258a | unverified | The additive energy of the secret support makes HQC's decoding failure rate a per-key quan | HQC's analytic model computes one number p* by averaging over the key (x, y) and the ciphertext rand
[prop] IDEA-20260808-d21021 | proposed | HQC's error vector has an exactly-invariant marginal and an adversarially-steerable covari | Let e' = x.r2 - r1.y + e in R = F_2[X]/(X^n - 1) with S_x, S_y the secret supports of size omega and
[prop] IDEA-20260811-7734c5 | proposed | FOURIER FLATNESS OF THE COORDINATE-DEFINED FACTOR BASE, THE FUNCTIONAL IDEA-20260807-0ff79 | (A) THE OBJECT. Fix p, a complete ordinary F_p-isogeny class X, and ONE factor base V subset of F_p 
[prop] IDEA-20260901-d77aa8 | proposed | THE CONCENTRATION ROW IS AN ADDITIVE-ENERGY ROW, AND ITS FOURIER DUAL CLOSES THE WHOLE gam | Setting. G = <P> of prime order N. A KEYED LEAF JOIN uses public maps alpha, beta from G to a key se
[prop] IDEA-20260920-b6ad24 | proposed | THE SPECTRAL FLOOR OF THE BRANCHING WINDOW. One-step additive branching b forces every fib | REPRESENTATION CLASS AND ATTACK STAGE (one clause, per docs/object-frame-ideation.md section 4): the
[prop] IDEA-20261002-760272 | proposed | Seed additive energy on a j = 0 curve versus a generic j curve, above the constant automor | On prime-order short-Weierstrass curves over the same toy prime, one with j = 0 and one with generic
-- proposals.jsonl: 6 hits for all ['additive', 'energy']
[hypo] H-PFDR-d3c527 | proposed | The conditioned cross-collision row of a keyed LEAF join is the keyed ADDITIVE ENERGY of t | SETTING. G is generated by P and has prime order N. A KEYED LEAF JOIN uses public maps alpha and bet
-- hypotheses.jsonl: 1 hits for all ['additive', 'energy']
##### lgrep all pair-sum
[prop] IDEA-20260808-b16d04 | unverified | Reachable-tail signed-partition propagation with occupancy-calibrated duplicates and quoti | Conditionally on H1-H5, a fixed public target-independent signed-y antisymmetric partition with root
[prop] IDEA-20260829-3f0f4b | proposed | The (gamma, s) exponent surface: retarget the lane from output-sensitive joins to any sub- | The entire source-labelled four-list family has a single two-parameter cost law. Let the level-1 joi
[prop] IDEA-20261017-078074 | proposed | Dual sum-product probe: do log-domain GAP bases carry label-additive structure that a labe | R1 labels, stage factor-base membership. Let A = {c_1 P_1 + ... + c_r P_r : |c_i| <= T}, r in {1,2,3
[prop] IDEA-20261017-90d9c5 | proposed | Rho-trail harvest of pair-sum coincidences: the table family's memory exponent drops from  | Stage: collision structure inside relation decomposition. Replace the stored table of S = B^h h-sums
-- proposals.jsonl: 4 hits for all ['pair-sum']
[hypo] H-CRYPTO-9557c5 | approved | On Z/17 the set {0, 1, 3} has 6 pair-sums, not 3 and not 9. | Ordered pairs from {0, 1, 3} number 9. Their sums in Z/17 are exactly {0, 1, 2, 3, 4, 6}, so the ima
[hypo] H-ECDLP-298630 | approved | One lambda fills all 36 pair sums, and the other stops at 28. | On y^2 = x^3 + x + 3 over the field of 151 elements, the point (1, 55) lies on the curve and 167 tim
[hypo] H-JPR-3a00f0 | proposed | Source-resolved output-sensitive joinability is the missing Wagner-to-ECDLP primitive | Let G be a prime-order elliptic-curve subgroup of order N and let four independently sampled, source
[hypo] H-PFDR-011a4b | proposed | Base-size axis of pair-sum coincidences: the nontrivial pair-sum coincidence count of wind | On prime-order ordinary curves E/F_p generated by curve.generate_prime_order_curve(bits, seed) (vend
[hypo] H-PFDR-727bfc | specified | Dual sum-product probe at toy scale: the x-label sets of rank-r log-GAP bases {c_1 P_1 + . | Let E/F_p be a generated prime-order ordinary curve, N = #E(F_p), f(x) = x^3 + ax + b, and L = {x in
-- hypotheses.jsonl: 5 hits for all ['pair-sum']
##### lgrep all occupancy
[prop] IDEA-20260805-705614 | unverified | Quantifier-order audit of the FORS interleaved-target bound: the reachable occupancy set,  | The FORS multi-target bound is a statement of the form FOR ALL adversaries A with at most q signing 
[prop] IDEA-20260805-fbe36a | unverified | The occupancy moment is the whole multi-target term: re-deriving SLH-DSA's FORS interleave | The entire multi-target amplification of the FORS layer of SLH-DSA is carried by ONE integer-valued 
[prop] IDEA-20260808-b16d04 | unverified | Reachable-tail signed-partition propagation with occupancy-calibrated duplicates and quoti | Conditionally on H1-H5, a fixed public target-independent signed-y antisymmetric partition with root
[prop] IDEA-20260816-cf82f2 | proposed | Treat the map from the message randomizer to the selected hypertree leaf index as a distri | (A) Every occupancy statement this program has made about the FORS layer is conditional on an antece
[prop] IDEA-20260930-4ebd85 | proposed | Triple-sum occupancy against a relabelled cyclic group, two toy binary scales | For a frozen explicit point set B of size m on the prime-order subgroup of a toy binary Koblitz curv
[prop] IDEA-20261018-5f37a1 | proposed | Log-blind golden bases: coverage gained without discrete logarithms is an order statistic  | Koblitz toy, n prime, G of prime order r, tau = scalar lambda of order n, base = K signed orbit colu
-- proposals.jsonl: 6 hits for all ['occupancy']
[hypo] H-FIND-271c04 | specified | Stage 0 reachable-tail signed-partition propagation occupancy-calibrated duplicates quotie | Fix the exact count identity of IDEA-20260808-b16d04 before any later-stage claim. Stage 0 asserts o
[hypo] H-SLHDSA-9e09aa | proposed |  | The FORS interleaved-target bound is a statement of the form "for all adversaries A with at most q s
-- hypotheses.jsonl: 2 hits for all ['occupancy']
##### lgrep all cauchy-schwarz
[prop] IDEA-20261018-6507e6 | proposed | Occam-priced lift frontier plus a null-on-null calibration: what the Cauchy-Schwarz envelo | (A) Design false-halt rate. EXP-RELN-82f487 halts a cell when any null check trips; EV-RELN-99c688 l
-- proposals.jsonl: 1 hits for all ['cauchy-schwarz']
[hypo] H-ECDLP-2ade73 | specified | Relative bucket variance W of the O2 agreement kernel decays slower than 1/sqrt(N) (LARGE- | Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
-- hypotheses.jsonl: 1 hits for all ['cauchy-schwarz']
##### lgrep all population coverage
[prop] IDEA-20260828-033cb3 | unverified | Call-site specialization: does a single source-level comparison symbol fracture into disti | (A) THE TWO OPEN THREADS THIS RECORD CONNECTS. IDEA-20260821-121612 measured whether a FIXED compari
-- proposals.jsonl: 1 hits for all ['population', 'coverage']
-- hypotheses.jsonl: 0 hits for all ['population', 'coverage']
##### lgrep all useful triple
[prop] IDEA-20260926-3cc0b8 | proposed | THE BYTES COLUMN AT THE ECC2K-130 CAP LOCUS: block Wiedemann at n0 = 64 needs about 435 GB | Representation class R1 of RQ-ECDLP-623a32 (the relation matrix and log vector over F_r); the attack
-- proposals.jsonl: 1 hits for all ['useful', 'triple']
-- hypotheses.jsonl: 0 hits for all ['useful', 'triple']
##### lgrep any 0cf008
-- proposals.jsonl: 0 hits for any ['0cf008']
-- hypotheses.jsonl: 0 hits for any ['0cf008']
##### lgrep all conservation yield
[prop] IDEA-20260830-772cff | proposed | THE CHANNEL-SCOPED KILL, AT THE CLOSURE STANDARD. Three named bounds - yield advantage exa | (A) WHAT THIS RECORD IS. It is a derivation-level closure argument for RQ-FBG-001's decision target,
[prop] IDEA-20260830-c5c614 | proposed | THE ONE DOOR CONSERVATION LEAVES OPEN. KN-FIND-007 forces the mean only when the average r | (A) WHAT IS ALREADY CLOSED, SO THAT THIS IS NOT MISTAKEN FOR IT. KN-FIND-007 fixes the mean per-targ
-- proposals.jsonl: 2 hits for all ['conservation', 'yield']
[hypo] H-CMFB-9b2eed | specified |  | On prime-field curves y^2 = x^3 + A x + B over F_p of prime order N with 2^14 < p <= 2^25, in each o
[hypo] H-ECTD-110aef | proposed |  | SCOPE: the three yield-shaped meters of the frozen contract EXP-ECTD-001 -- semaev_m3_relation_densi
[hypo] H-PFDR-1b2386 | proposed | Conservation binds only on the WHOLE group, so relation collection is free to attempt only | (A) WHAT IS ALREADY CLOSED, SO THIS IS NOT MISTAKEN FOR IT. The mean per-target decomposition yield 
[hypo] H-PFDR-26bcee | proposed | A CHANNEL-SCOPED closure of the factor-base geometry family on the yield, coverage and ran | (A) WHAT THIS RECORD IS. A derivation-level closure argument for RQ-FBG-001 decision target, written
-- hypotheses.jsonl: 4 hits for all ['conservation', 'yield']
##### lgrep all kappa coincidence
[prop] IDEA-20261017-bbc53e | proposed | Break-even excess for coincidence-harvested relations: kappa must reach the unknown count  | Stage: relation decomposition by coincidence harvest. Relations needed are c*U (c in 0.92..1.0; U = 
-- proposals.jsonl: 1 hits for all ['kappa', 'coincidence']
-- hypotheses.jsonl: 0 hits for all ['kappa', 'coincidence']
##### lgrep all transport yield
-- proposals.jsonl: 0 hits for all ['transport', 'yield']
-- hypotheses.jsonl: 0 hits for all ['transport', 'yield']
##### lgrep all isogeny yield
[prop] IDEA-20260807-0ff796 | proposed | CLOSURE WITH A NAMED OBSTRUCTION: length-2 relation yield and factor-base decomposition pr | (A) THE OBJECT. Fix E/F_p: y^2 = f(x) = x^3 + a x + b, non-singular, and a target point R in E(F_p) 
[prop] IDEA-20260808-ee5d81 | proposed | A commitment-curve COLLISION across two signatures under one key yields a non-scalar endom | In a SQIsign-shaped protocol each signature publishes a commitment curve E_com and a response isogen
[prop] IDEA-20261007-6553d5 | proposed | ER-McE: seed a code-decoding trapdoor from a canonical complete supersingular endomorphism | A complete evaluable End(E) basis can be canonicalized and used as the deterministic seed of a McEli
[prop] IDEA-20261015-1e8145 | proposed | Auxiliary finite-coset isogeny bases priced by verified quotient-rank yield | R1/R2 membership/relation/LA comparison: price identical auxiliary finite-coset bases as list, expan
[prop] IDEA-20261018-3f16fc | proposed | Ceiling attainment and the charged favourable-member search: if a random classmate already | Hand-derived, nothing executed. Since r_d(b) <= rho_hat_d for every b (IDEA-20261018-70caad ceiling)
[prop] IDEA-20261018-c49f37 | proposed | One Fourier family couples the isogeny class to the descended system: exact class-yield co | Hand-derived, nothing executed. (T1) In the binary 2-decomposition system the curve enters only as a
-- proposals.jsonl: 6 hits for all ['isogeny', 'yield']
[hypo] H-ECDLP-60de36 | rejected_scoped | Chain-encoded isogeny factor base versus dense encoding of the same set, a random set of e | For prime p = 3 mod 4 with 2^L | p+1 and target curve y^2 = x^3 - 3x + b, encoding the factor-base x
[hypo] H-ENDO-3ecfa3 | proposed |  | Exact conjugation of a primitive CM multiplication matrix by an integer isogeny matrix has least den
[hypo] H-ICINV-b96cc7 | proposed |  | THE LENGTH-2 SEMAEV RELATION LOCUS IS AN F_p-ISOMORPHIC COPY OF THE CURVE, SO ARITY-2 RELATION YIELD
-- hypotheses.jsonl: 3 hits for all ['isogeny', 'yield']
```

======================================================================
## N1 ATLAS COLLISION (top 5 of every run, YAML mechanism + obstruction + forecloses read)
======================================================================
Leads read in full (YAML under knowledge/leads/ecdlp/): ICP-isogeny-transported-relation-yield, STR-class-representative-ic-selection,
ICE-decomposition-probability-audit, ICP-coincidence-harvest-structured-base, TRF-teske-secret-isogeny-trapdoor, ICB-kic-golden-base-exact-decomp,
ICB-cofactor-torsion-quotients, EXO-dl-character-sum-pseudorandom, ICP-retained-setup-online, ICB-frobenius-orbit-factor-base,
RHO-advice-table-variants, STR-isogeny-transport-preprocessing, ICP-coppersmith-smallroot-semaev, plus the three SO rows
(STR-isogeny-class-generic-invariance, ICP-algebraic-membership-factor-base, ICP-generic-table-decomposition).

Run 1 (exact population coverage ... crater versus floor)
 1. LEAD-ICP-isogeny-transported-relation-yield, open_blocked (score 25): SAME OBJECT. Mechanism: compare arity-3 relation yield of native / transported / random
    bases on P29/P37 crater/floor pairs. next_action: finish the 17 missing arms of EXP-ECTD-0cf008, "reporting coverage and variance, not only mean yield".
    discriminates: ratios inside the A/A band confirm the conservation prediction and close the lead; "a coverage or variance excess that grows with field size
    is the only outcome that would matter". The candidate computes that same coverage/variance exactly at population level instead of by 32,768-target
    sampling. Same measured object, same decision rule, different instrument -> advances_lead, not a new lead. No obstruction row exists (lead is open).
    forecloses phrases ("walk the isogeny volcano to a curve with better relation yield", "transport the factor base along an isogeny", "crater versus floor
    index calculus") cover the candidate's subject entirely.
 2. LEAD-STR-class-representative-ic-selection, open_next_step (18): related. Its evidence already records "a pushed crater base gives exactly the crater yield
    on the floor; yield is a set property" (pair46 03-floor-pullback) and a measured l=2 yield floor/crater 0.942 [0.928,0.956] at 24 bit that the lead itself
    suspects is factor-base sampling noise. The candidate's band is a possible explanation tool for that 5.8% effect (not claimed by the candidate; I note it
    as an unrun application). Not a collision, a neighbour the instrument could also serve.
 3. LEAD-ICB-kic-golden-base-exact-decomp, open_next_step (14): binary KIC lane, exact coverage vs a size-matched null on binary toys (EXP-KIC-424885: coverage 70 =
    null coverage 70). Same observable (exact triple-sumset coverage vs matched null), different field and no second-moment band. Neighbour.
 4. LEAD-ICB-cofactor-torsion-quotients, closed_obstructed (12): quotient/Wagner mechanism. No overlap (lexical hit on "coverage"/"base").
 5. LEAD-EXO-dl-character-sum-pseudorandom, exhausted_at_scale (10): additive-character bias of DL on small-x bases; measured R = C_EC/C_null flat 1.28-1.34 at
    2^20-2^26 ("the curve behaves like a random set up to a constant"). The multiset additive energy E_m = (1/N) sum_chi |S_D(chi)|^{2m} (stated in ledger
    IDEA-20260906-d1494b) is exactly the quantity kappa2 reduces to, so the candidate's "kappa2 about 1, native = random" is the energy-side restatement of this
    exhausted measurement. revisit_when ("R trends upward with p beyond 2^30 ... or a structured set shows R growing with N") is not touched by 2 sizes.
Run 2 (count every target ... instead of sampling targets)
 1. LEAD-ICP-retained-setup-online, closed_dominated (15): retained-advice online IC vs Bernstein-Lange. Obstruction is about per-target online cost. No overlap.
 2. KR-IC-5a43e5 known_result (12): Semaev summation polynomials; framework only.
 3. LEAD-ICB-cofactor-torsion-quotients (12): no overlap. 4. LEAD-ICB-frobenius-orbit-factor-base, closed_obstructed (11): per-attempt decomposition probability
    "equal to the birthday value" for orbit/normal/poly bases (n = 11..23). Binary, Koblitz; same flavour of "occupancy equals random/birthday value" but a different
    object (per-attempt probability), no overlap in mechanism. 5. LEAD-EXO-dl-character-sum-pseudorandom (10): see above.
 (6-8, outside top 5 but read for the phrasing: LEAD-ICB-kic-golden-base-exact-decomp; LEAD-ICP-coincidence-harvest-structured-base (10); LEAD-ICP-coppersmith-smallroot-semaev.)
Run 3 (mean per-target yield conservation and coverage gain across isogenous curves)
 1. LEAD-RHO-advice-table-variants, open_next_step (9): rho advice tables (re-selected/grown/transported). Only "transport" in common. No overlap.
 2. LEAD-STR-class-representative-ic-selection (9): see above. 3. LEAD-STR-isogeny-transport-preprocessing, closed_obstructed (8): obstruction "transporting each target
    reduces M targets on M isogenous curves exactly to M targets on one curve" (theorem-grade); preprocessing-table object, not IC occupancy. No overlap, but the same
    "transport is exact" mechanism is what makes the candidate's transported-base identity trivial.
 4. KR-RHO-755e35 (7): isogenous curves equally hard (see N2). 5. LEAD-ICE-decomposition-probability-audit, open_next_step (7): SAME OBJECT, second-order. Mechanism:
    "The mean is fixed by yield conservation; only the per-target distribution, clustering and charging remain." next_action: BATCH-79a580, report "the exact count
    vector c_D and its variance against a size-matched random base"; discriminates: "no excess confirms KN-FIND-007 to second order and retires the P(decomp) lane".
    The candidate's outcome (a) (kappa2 in [0.9,1.1], native about random) is this same decision rule; the candidate itself lists the audit as its second-order question.
Run 4 (own phrasing: second-moment / Markov ceiling / pair-sum coincidences / additive energy)
 1. LEAD-ICP-coincidence-harvest-structured-base, open_next_step (25): SAME STATISTIC. kappa_rel = pair-sum-coincidence excess of a structured base over a random
    base; best_measured EXP-PFDR-ca5e01 O-MIXED, kappa in [0.889,1.103], planted kappa ~2.6 recovered, kappa_rel 0.998 (small_x TT m=4, 30-32 bits); "kappa constant in N
    (as observed so far) closes the family". The candidate's measured kappa2 0.991-1.018, "native and size-matched random alike", is the same finding on a different
    statistic (population second factorial moment at P29 instead of a coincidence census at 30-32 bits). Its "excess of kappa2 is the pair-sum coincidence count" is the
    standard energy accounting (ledger d1494b INV-2). 2-5: kic-golden-base, cofactor-torsion, coppersmith-smallroot (decomposition solve, unrelated), dl-character-sum.
Closed leads the candidate must answer (strictness check):
 - ICP-algebraic-membership-factor-base (SO-ALGFB), closed_obstructed, theorem. Candidate is inside its stated Scope and says it escapes no premise. Its revisit_when
   ("a base raises coverage or variance with an excess that grows with N") is precisely what popcov would measure; candidate-reported answer at two sizes: no excess.
 - STR-isogeny-class-generic-invariance (SO-ISO), closed_obstructed, theorem + measurement. The candidate's isogeny content is Tate/Velu: G -> G' is an isomorphism, so a
   transported base is targetwise identical. Its revisit_when assigns IC-level (non-generic) effects to STR-class-representative-ic-selection (open), i.e. the candidate
   lives in that open lead's territory, not in the closed one.
 - ICP-generic-table-decomposition (SO-TABLE): orthogonal as the candidate says (it fixes yield, not oracle cost). Its statement "B1 is purely a per-attempt-cost
   question" is the already-recorded split in KN-FIND-007 ("says nothing about the cost of finding a decomposition").
Net N1: no run returns a lead whose mechanism the candidate does not already sit inside. The candidate is not a new mechanism; it is an instrument for three open leads
(isogeny-transported-relation-yield, decomposition-probability-audit, coincidence-harvest). Its forecloses coverage: all of the open lead's forecloses phrases apply to it.

======================================================================
## N2 KNOWN RESULTS (frontier map)
======================================================================
No KR row matches the second-moment band or the exact-occupancy calculator. Nearest rows and what each does/does not cover:
 - KR-RHO-755e35 textbook_fact/proven (Tate; isogenous curves equally hard; ECDLP random-self-reducible across a class under JMV). Covers "same order -> same generic
   difficulty". It is about generic ECDLP weakness classes, not IC occupancy. The candidate's transported-base identity (G ~ G') is the same fact applied to a factor
   base; the candidate's own cited provenance for it is Tate, so no new literature content.
 - KR-IC-5931ee known_negative/proven (naive Semaev IC over F_p is no better than generic, under statistical assumptions). Context for the B1/B2 bottleneck, not for coverage.
 - KR-IC-5a43e5 (Semaev summation polynomials), KR-IC-73db3f (choosing V; binary), KR-IC-b0fcda (Frobenius-invariant bases; binary): framework, no coverage statistics.
 - KR-RHO-46c2c6 (multi-target / batch DL), KR-RHO-825bca: rho side.
Literature ingredients of the candidate are textbook: Cauchy-Schwarz/Paley-Zygmund second-moment inequality (the lower bound P(u>0) >= (E u)^2 / E u^2 is Cauchy-Schwarz;
the PZ label with theta = 0), and the Chen-Stein reading of E[u(u-1)] (Arratia-Goldstein-Gordon). A KR hit does not force known_result here because no KR row states the
quantity, but nothing literature-side is new. What is not in KRMAP and not in the program literature surveyed: a two-sided coverage band keyed to the base's
multiset energy. That is an internal derivation, not a literature result, and it is a corollary (see N3).

======================================================================
## N3 LEDGER (grep of .index/proposals.jsonl + hypotheses.jsonl; raw above)
======================================================================
Hits that may be the same object (id | status | 100-char claim):
 - IDEA-20260906-d1494b | proposed | "THE POINT-RELATION HYPERGRAPH AND THE SECOND-MOMENT IDENTITY": sum_r c_D(r)^2 = E_m(D) (multiset additive energy); random-base value Poisson; CS envelope on every lift  [OPENED]
 - IDEA-20260906-cd7b7e | proposed | "SAMPLE THE DECOMPOSITION, NOT THE TARGET": size-biased fibre identity for #{R: c(R)>=1}; defines E_m = sum c(R)^2 as the additive m-energy  [index row only]
 - IDEA-20260930-4ebd85 | proposed | Triple-sum occupancy against a relabelled cyclic group, two toy binary scales: coverage of unordered distinct triple sumset vs 1-(1-1/r)^M null, band [0.75,1.25]  [OPENED]
 - H-KIC-baee02 | specified | lexicographic bases at n=7/11: |cov_curve - cov_cyclic|/max(cov_cyclic,1/r) <= 0.25 (the hypothesis of 4ebd85)  [index row only]
 - IDEA-20261015-e0b5dd | proposed | Pushing crater bases through the conductor-v isogeny: yield, coverage, rank of phi(S) equal those of S exactly (KN-FIND-007 through an isomorphism)  [OPENED]
 - IDEA-20260805-a7a716 | unverified | The coverage channel of factor-base geometry is bounded by e/(e-1) = 1.581977 for every base, every N and every m  [index row only]
 - IDEA-20260830-772cff | proposed | CHANNEL-SCOPED KILL: yield advantage exactly 1, coverage advantage at most 1.582, rank advantage at most 1+...  [index row only]
 - IDEA-20260830-c5c614 | proposed | THE ONE DOOR CONSERVATION LEAVES OPEN: conservation binds only over the whole group, target-conditional lift  [index row only]
 - IDEA-20260905-64397d / IDEA-20260905-be63be | proposed | Orbit stabilizers and the second factorial moment of relation supply (automorphism-orbit bases)  [index rows only]
 - IDEA-20260906-86cd30 | proposed | m = 2 decomposition graph is a path; exact random-base p_exist; "m = 3 Janson bracket" (per d1494b's citation line; NOT opened)
 - IDEA-20261018-5f37a1 | proposed | Log-blind golden bases: coverage gained is an order statistic of the orbit-class occupancy null (Koblitz toy, lam = M_c/N_c)  [index row only]
 - IDEA-20261017-bbc53e / H-PFDR-011a4b | proposed | Break-even excess for coincidence-harvested relations (kappa); base-size axis of pair-sum coincidences on prime-order curves 16-22 bits
 - H-ECTD-e88346 | approved | the two crater/floor pairs (conductor steps 8209, 131101), native first-B-abscissa signed bases, verified usef... (index claim truncated at 200 chars): the approved hypothesis the panel tests
 - IDEA-20261017-3db2a8 | proposed | Semaev yield exact first moment; Poisson link is second order (binary Semaev, eq. (15)-(..)); not the same object
Provenance of the ledger material: IDEA-20260906-d1494b, IDEA-20261015-e0b5dd, IDEA-20260930-4ebd85 = retrieved (full record opened; d1494b read in part). All other ids = retrieved (index row only, claim/mechanism fields
truncated at ~200 chars by the index).
Three full records opened (cap respected). What each decides:
 1. IDEA-20260906-d1494b (prime-order G, any m): states (i) sum c_D(r)^2 = E_m(D) exactly, hence Var and the dispersion index Delta = E_m/M - mu, "over-dispersion of the
    count vector IS excess additive energy of the base"; (ii) the random-base value is Poisson, E[Delta] = 1 - 1/N; (iv') Cauchy-Schwarz: |rho_S - 1| <= sqrt(Delta(1-sigma)/(sigma mu))
    for every lift; Chebyshev bound on k-rich targets; coverage <= min(1, mu) quoted from KN-FIND-007; a planned exact-enumeration battery at four toy rungs.
    This is the same second-moment/energy framework the candidate calls kappa2. What I did not find (grep for coverage/support/paley/floor/crater/isogen in that record;
    I read lines 28-140, 370-400, 455-480, 640-660, 826-850 plus grep, not all 1107 lines): an explicit support-size FLOOR cov >= M^2/(N E_m), and any crater/floor application.
 2. IDEA-20261015-e0b5dd: claim (A) is the candidate's transport statement verbatim in content: phi restricts to a group isomorphism G -> G_f, so "the yield, coverage and relation
    rank of phi(S) equal those of S exactly (KN-FIND-007 through an isomorphism)". Its own nearest-prior-art row for KR-RHO-755e35 reads "(A) is the index-calculus form for one edge".
 3. IDEA-20260930-4ebd85 (+ H-KIC-baee02): the same observable as popcov (exact fraction of the subgroup in the unordered distinct triple sumset of a frozen B) against a Poisson
    occupancy null 1-(1-1/r)^M and a relabelled-cyclic null, with a gap band, at binary toy scales. The candidate concedes this in its self_kill_risk. Prime-field scale (3e8, 8e10),
    the crater/floor pairing, and the kappa2 band are not in it.
IMPORTANT CAVEAT (cap on opens): IDEA-20260906-cd7b7e was NOT opened (three-record cap used on d1494b, e0b5dd, 4ebd85). Its index row ("SAMPLE THE DECOMPOSITION, NOT THE TARGET: the size-biased
fibre identity #{R : c(R) >= 1} = sum over multisets ...", "supplies a size-biased estimator for coverage and E_m") shows that (i) "count coverage from the decomposition side instead of sampling
targets" is itself a recorded headline (candidate phrasing 2 almost word for word), and (ii) coverage and E_m already sit in one record, so the support floor cov >= M^2/(N E_m) may be stated there.
I could not check. Every "not found" below is therefore conditional on that unopened record.
Same-object call: the OBSERVABLE (exact triple-sumset coverage vs occupancy null), the SECOND-MOMENT FRAMEWORK (energy, Poisson, CS) and the TRANSPORT IDENTITY are each already
recorded. The residual that is not recorded is (a) the one-line support floor with kappa2, (b) the pairing of that floor with the panel's prepared P29/P37 bases and its
sealed arms, (c) the numerical values (candidate-reported, unreproduced here).

======================================================================
## N4 NOTATION CHANGE (IC / factor-base / representation candidate)
======================================================================
Pair declared by the candidate: (signed small-abscissa or random base of B abscissae on a prime-order E/F_p ; Sigma = translation by base elements, read as useful-triple sums
landing on uniform targets). Trichotomy: partial-action, Class I. This IS the recorded pair "index calculus is Class I, partial-action (translation by factor-base elements only)"
(docs/object-frame-ideation.md section 1 and constraint block; IDEA-20260806-c5d183 / IDEA-20260901-863e36). The tracked object is the existence of a decomposition (a sum
of base elements hitting the target), i.e. the standard IC branching event; no new projection of the group is introduced, so the Theorem-C / full-translation rigidity
(KN-FIND-ffe1df Theorem C; c5d183) is not engaged and not escaped. The lossy-projection test is vacuous: coverage is a count on the image of the multiset-sum map, nothing
is discarded beyond the order of summands (S_3 symmetry, as in 4ebd85).
KN-OPEN-020 class: explicit-list bases (small-abscissa window, random). Not in any of the three open classes (high-degree, implicit-membership, target-dependent); it is inside the
scoped-out class and the candidate says so ("Inside SO-ALGFB scope; escapes no premise"). The result is a recorded identity set (KN-FIND-007 conservation + the E_m second-moment
identity of IDEA-20260906-d1494b) re-expressed as kappa2, with the isogeny step reducing to e0b5dd (A). Conclusion for N4: a recorded result in new notation plus an instrument; no rigidity is bypassed.

======================================================================
## STANDING OBSTRUCTIONS TOUCHED (obstruction.statement quoted from the lead YAML; Scope clauses included)
======================================================================
SO-ALGFB (LEAD-ICP-algebraic-membership-factor-base, closed_obstructed, kind theorem): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B
 algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is
 binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits;
 exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
 revisit_when: "KN-OPEN-020 is answered positively ..., or a base raises coverage or variance with an excess that grows with N."  -> candidate is inside Scope, escapes no premise.
SO-ISO (LEAD-STR-isogeny-class-generic-invariance, closed_obstructed, kind theorem): "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on
 the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: ... v2.1 rho floor/crater is 1.004
 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve." (no explicit "Scope:" clause in this row;
 the theorem text is limited to prime-order subgroups and isogenies of degree prime to N). revisit_when sends IC-level step-cost effects to LEAD-STR-class-representative-ic-selection.
SO-TABLE (LEAD-ICP-generic-table-decomposition, closed_obstructed, kind theorem): "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic
 time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); ... Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4.
 Scope: any generic (enumeration/table) decomposition over F_p."  -> orthogonal; candidate prices yield only.

======================================================================
## CITATIONS AND PROVENANCE (as used in this gate)
======================================================================
Labels allowed: recalled | retrieved. Internal records and tool outputs read in this gate are labelled retrieved; textbook steps not looked up are recalled.
 - KN-FIND-007 (knowledge/findings/KN-FIND-007.md): provenance retrieved (internal file, read in full this gate). Already states exact conservation, coverage <= min(1, mean), the 1.582 ceiling,
   and "additive structure that creates repeated sums lowers coverage".
 - Arratia, Goldstein, Gordon, "Two moments suffice for Poisson approximations: the Chen-Stein method", Ann. Probab. 17(1) (1989) 9-25: retrieved at bibliographic +
   abstract-summary level via WebSearch (Project Euclid record euclid.aop/1176991491 listed; USC-hosted PDF listed). A direct WebFetch of the Project Euclid page returned empty,
   so the full text was not read. The citation is decorative for the candidate: the calculator is exact and needs no Poisson approximation.
 - Cauchy-Schwarz / Paley-Zygmund second-moment step: recalled (textbook). Tate 1966 isogeny theorem: recalled (textbook; also in KR-RHO-755e35 via KN-TECH-061).
 - ORACLE_FORMAT.md, EXP-ECTD-0cf008 prepared inputs and sealed raw results, and all P29/P37 numbers: candidate-reported; I read problems/prime-field-arity3-relation-oracle.md
   (sealed arms P29-E2-native 2,204, P29-E3-native 2,191, P37-floor-u2-native 2,178 useful of 32,768; 17 arms missing) but did not recompute anything.
 - Spot arithmetic check done by hand (not a reproduction): 32768 x 0.0690681 = 2263.3, matches the candidate's predicted 2263.2; 1 - exp(-0.0690681) = 0.066737 matches its
   "Poisson 0.0667369"; 0.2/0.0690681 = 2.90 matches its kappa2 threshold at P29. These confirm internal consistency of the quoted figures only.

======================================================================
## VERDICT: advances_lead   (lead: LEAD-ICP-isogeny-transported-relation-yield)
======================================================================
Why not "new": the observable (exact triple-sumset coverage), the second-moment/energy/Poisson framework, and the transport identity are each recorded (4ebd85, d1494b, e0b5dd,
KN-FIND-007); the candidate itself says predicted gain 0, escapes no standing obstruction and sits inside SO-ALGFB scope.
Why not "duplicate_of_lead": the open lead's next_action is a sampled 17-arm run; the candidate replaces it with an exact target-free calculation of the same quantities (coverage and variance), with
a pre-registered necessary condition for a floor/crater ratio of 1.2 (kappa2 >= 0.2/lambda, 2.90 at P29, candidate-reported 3.00 at P37) and a candidate-reported agreement with the three sealed arms.
It is the same decision rule at lower cost, so it sharpens the lead's discriminating step.
Why not "known_result": no KR row states it; but the literature ingredients are textbook, so there is nothing literature-new either.
What is new (precisely, none of it a mechanism). FIRM residual: (a) application of an exact population count to the EXP-ECTD-0cf008 prepared P29/P37 bases, validated against the sealed arms;
(b) the pre-registered threshold kappa2 >= 0.2/lambda for a 1.2 floor/crater ratio; (c) the numerical values, unreproduced here (candidate-reported).
CONDITIONAL residual: (d) the support-size floor coverage >= lambda/(1 + kappa2*lambda) and the ratio bound cov/cov' <= 1 + kappa2'*lambda for equal-size bases. This is a Cauchy-Schwarz corollary of
the E_m identity in d1494b; grep did not find it in d1494b (read only in part), and it may be stated in the unopened cd7b7e. "Count the decomposable targets instead of sampling targets" itself is NOT new: it is
cd7b7e's headline. The ratio bound does not use isogenies at all (it holds for any two equal-size bases in prime-order groups of the same order).
Limits the candidate's headline "decides the panel from base data alone" does not respect: the panel also owes rank-prefix and interval outputs, independent ordered-count and group-law replay,
and targetwise transported-base equality checked with a point evaluator (problems/prime-field-arity3-relation-oracle.md exit criteria 3-4; no general prime-degree isogeny point evaluator exists). A
population calculator can discharge only the two fixed-pair occupancy comparisons, and exit criterion 4 still requires independent evidence review before any lead disposition. Its proposed
dispositions (close ICP-isogeny-transported-relation-yield; close the IC-meter half of TRF-teske-secret-isogeny-trapdoor) are therefore predictions conditional on outcome (a), not results.
Also advances (secondary): LEAD-TRF-teske-secret-isogeny-trapdoor (its next_action is literally "Re-run the approved 20-arm panel EXP-ECTD-0cf008"; its discriminates rule "ratios consistent with one ... close the IC-meter half
at toy scale" is the candidate's outcome (a)); LEAD-ICE-decomposition-probability-audit (same second-order test of KN-FIND-007 on BATCH-79a580 fixtures), LEAD-ICP-coincidence-harvest-structured-base (kappa evidence on
a different statistic, 2 sizes only), LEAD-STR-class-representative-ic-selection (possible explanation instrument for its l=2 0.942 effect; unrun).
Heuristics, numbered for the record: G1 the band is only informative when lambda*kappa2 is O(1): at the panel's lambda 0.069 and kappa2 about 1 the band is [0.0646, 0.0691], width 7%, so a 20% crater/floor
effect is excluded by arithmetic, not by data (conditional on kappa2 < 2.9). G2 the P37 conclusion rests on a sampled kappa2 1.02 +- 0.07 (candidate-reported), not an exact count. G3 two field sizes
(about 28 and 36 bits) cannot test "excess that grows with N"; the candidate's own self-kill note (High on novelty) is accurate.
