# Gate N1-N4: C3 valuation-triviality lemma (p-adic tropical initial-form decoder, closure of IDEA-20260814-c3af09)

Gate run by a scout subagent, read-only on the repositories; everything below was written under this scout directory only.
Candidate text is the workflow-computed task text; its numbers are labelled "candidate" unless this gate reproduced them.

## 0. Raw tool output (pasted verbatim)

Environment: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as specified; run from /Volumes/SSD990-2/crypto-autoresearcher.

### python3 tools/lead_atlas.py --match "p-adic tropical initial-form decoder for Semaev systems collapses to the w=0 cell whose initial form is the residue system"   (phrasing 1)
```
   15  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   12  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
   12  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
   11  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   10  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
    9  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    9  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    8  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
```

### python3 tools/build_frontier_map.py --match "p-adic tropical initial-form decoder for Semaev systems collapses to the w=0 cell whose initial form is the residue system"
```
KR-IC-fbdb61  score=7  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-e847d1  score=6  [known_mechanism/reported]  Crossbred algorithm for Boolean systems
    sources: KN-LIT-139
KR-IC-5a43e5  score=5  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-f3da82  score=4  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-IC-0d2021  score=3  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-53c89f  score=3  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
```

### python3 tools/lead_atlas.py --match "lifting the decomposition polynomial to the p-adics and using Newton polygons gives no pruning"   (phrasing 2)
```
    8  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    8  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    7  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    7  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    7  LEAD-ICB-oakley-quintic-tower                open_next_step     Gaudry-Diem n = 5 point decomposition on the Oakley EC2N curves over F_{2^155} and F_{2^185}
    7  LEAD-ICP-coppersmith-smallroot-semaev        open_next_step     Small-root (Coppersmith / Jochemsz-May) decomposition with lattice-describable (window, AP, GAP) factor bases
    7  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    6  KR-IC-081a58                                 known_result       Joux–Vitse n−1 decomposition and oracle-assisted static DH
```

### python3 tools/build_frontier_map.py --match "lifting the decomposition polynomial to the p-adics and using Newton polygons gives no pruning"
```
KR-IC-955fd6  score=8  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-1fcdbc  score=7  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-081a58  score=6  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5a43e5  score=6  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-8b9daa  score=6  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-5765d2  score=5  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d
KR-IC-73db3f  score=5  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
```

### python3 tools/lead_atlas.py --match "valuation profile collapses to the fibre indicator; computable Teichmuller-style contrast reads as chance"   (phrasing 3)
```
    7  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    3  LEAD-EXO-global-lift-height                  open_next_step     Height-compressing global lifts (Q, number fields, function fields / elliptic surfaces)
    3  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    1  KR-RHO-0528e7                                known_result       Automorphisms give a sqrt(m) constant factor
    1  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    1  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    1  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    1  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
```

### python3 tools/build_frontier_map.py --match "valuation profile collapses to the fibre indicator; computable Teichmuller-style contrast reads as chance"
```
KR-RHO-0528e7  score=1  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-1c2928  score=1  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-cd0049  score=1  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
```

### python3 tools/lead_atlas.py --match "Newton polygon p-adic lift Semaev summation polynomial Hensel tropical"   (phrasing 4, own extra phrasing)
```
   14  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   14  LEAD-TRF-anomalous-padic-lift                closed_known       Smart / Satoh-Araki / Semaev p-adic lift for anomalous (trace one) curves
   13  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
   10  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    9  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    9  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    9  LEAD-ICE-syzygy-cascade-signatures           open_next_step     Exploiting the degree-born non-rewritable syzygy (F5 signature) cascade of Semaev systems
    9  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
```

### python3 tools/build_frontier_map.py --match "Newton polygon p-adic lift Semaev summation polynomial Hensel tropical"
```
KR-IC-5a43e5  score=14  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-5931ee  score=9  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-889857  score=8  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-cd159a  score=4  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
```

## 0b. Raw ledger-index greps (N3), id + status/novelty + first 100 chars of claim (script: _c3val_raw/ledger_grep.py, regex over title+claim+mechanism of .index/proposals.jsonl and .index/hypotheses.jsonl)
```
$ ledger_grep 'tropical'
prop IDEA-20260814-c3af09 [proposed/unverified] CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta,
--- proposals.jsonl hits for ['tropical']: 1
--- hypotheses.jsonl hits for ['tropical']: 0
$ ledger_grep 'Newton poly'
prop IDEA-20260723-006 [None/speculative] For every m>=3, the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m)
prop IDEA-20260808-c31f1c [proposed/screened] The classification in E1-01 leaves "lattice-describable" as the one open factor-base family; this re
prop IDEA-20260811-97e244 [proposed/adaptation] (A) THE PRECISE REASON SUPPORT IS THE WRONG FUNCTIONAL. The campaign's standing puzzle is committed:
prop IDEA-20260816-6fc66c [proposed/unverified] (A) H-ALR-001 asserts an exact gcd-equivalent subresultant interface, with Norm(R_P) = Res(W, R_P) =
prop IDEA-20260904-8dccc9 [proposed/unverified] Setting exactly as analysis/smallroot-reach/CLOSURE.md at its optimum (m, w) = (4, 2): full binary t
--- proposals.jsonl hits for ['Newton poly']: 5
hypo H-ECDLP-30a2a1 [proposed/None] Source proposal IDEA-20260808-2e14f7 (RQ-ECDLP-002, class representation). For E/F_p ordinary with p
hypo H-ECDLP-c3d48a [specified/None] Fix the exact threshold identities of IDEA-20260808-486ae2 before any Coppersmith / Howgrave-Graham 
hypo H-JINV-28621d [specified/None] Fix the exact count identity of IDEA-20260811-97e244 before any later-stage claim. Stage 0 asserts o
--- hypotheses.jsonl hits for ['Newton poly']: 3
$ ledger_grep 'initial.form'
prop IDEA-20260814-c3af09 [proposed/unverified] CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta,
--- proposals.jsonl hits for ['initial.form']: 1
--- hypotheses.jsonl hits for ['initial.form']: 0
$ ledger_grep 'Hensel'
prop IDEA-20260905-dacf4f [proposed/unverified] (A) THE GAP. harness/toycurve.py provides exact F_p arithmetic and point counting only. The only ano
--- proposals.jsonl hits for ['Hensel']: 1
hypo H-ECDLP-e9d9bb [specified/None] Fix an ordinary short-Weierstrass model y^2 = x^3 + A x + B over Z/p^2 Z with p > 3, A a unit, and a
--- hypotheses.jsonl hits for ['Hensel']: 1
$ ledger_grep 'p-adic'
prop IDEA-20260807-dbb250 [proposed/adaptation] (A) WHY THIS ROUTE IS TEMPTING AND MUST BE ADDRESSED. The Serre-Tate canonical lift of an ORDINARY c
prop IDEA-20260811-dc6ece [proposed/adaptation] (A) THE CANONICAL ARM, CLOSED BY IDENTITY AND NOT BY MEASUREMENT. For an ordinary E/F_p the Frobeniu
prop IDEA-20260901-b4e6eb [proposed/unverified] Frozen setting, inherited verbatim from the repaired hypotheses of the 2026-08-31 ECDLP-IDEA-436 err
prop IDEA-20260905-3a30d5 [proposed/unverified] (A) THE THREE FUNCTIONS. E/F_p ordinary, cofactor 1, n = #E coprime to p, E^ the naive lift with the
prop IDEA-20260905-848b77 [proposed/unverified] (A) THE SETTING AND THE SPLITTING. E/F_p with good reduction, p >= 3, E^/Q_p any lift (the naive one
prop IDEA-20260905-dacf4f [proposed/unverified] (A) THE GAP. harness/toycurve.py provides exact F_p arithmetic and point counting only. The only ano
prop IDEA-20261009-843cfd [proposed/adaptation] In Z_p^* the Teichmuller character gives the unique homomorphic section of Z_p^* -> F_p^* with image
prop IDEA-20261009-bec077 [proposed/unverified] For random ordinary curves at p in 2^20 .. 2^48, h(D) fits c * sqrt(p) times a slowly varying factor
prop IDEA-20261009-d2412c [proposed/adaptation] For E/F_p with a prime-order subgroup <P>, n != p, let s_tor be the torsion section (the unique n-to
prop IDEA-20261017-5c1d2a [proposed/unverified] p=m^d-c prime; pi=alpha-m generates the degree-1 prime of Z[alpha]=Z[X]/(X^d-c), N(pi)=+-p; psi2: Z[
--- proposals.jsonl hits for ['p-adic']: 10
hypo H-CANL-613cfc [specified/None] Fix the exact count identity of IDEA-20260807-dbb250 before any later-stage claim. Stage 0 asserts o
hypo H-CANL-b77100 [specified/None] Fix the exact count identity of IDEA-20260811-dc6ece before any later-stage claim. Stage 0 asserts o
hypo H-CZLIFT-fba874 [analyzed/None] Let E/F_p have a prime-order subgroup <P>, n != p, and let s_tor be the torsion section on a lift E^
--- hypotheses.jsonl hits for ['p-adic']: 3
$ ledger_grep 'Teichm'
prop IDEA-20260905-3a30d5 [proposed/unverified] (A) THE THREE FUNCTIONS. E/F_p ordinary, cofactor 1, n = #E coprime to p, E^ the naive lift with the
prop IDEA-20260905-dacf4f [proposed/unverified] (A) THE GAP. harness/toycurve.py provides exact F_p arithmetic and point counting only. The only ano
prop IDEA-20260911-2dd68d [proposed/adaptation] After (i) excluding the m=1 entry as a mathematical tautology (never entering any agreement statisti
prop IDEA-20261009-843cfd [proposed/adaptation] In Z_p^* the Teichmuller character gives the unique homomorphic section of Z_p^* -> F_p^* with image
prop IDEA-20261009-9e4a40 [proposed/unverified] Pr[omega(a) mod p^k is B-smooth] is about rho(k log p / log B), far below Pr[a in [0, p) is B-smooth
--- proposals.jsonl hits for ['Teichm']: 5
hypo H-CZLIFT-d37231 [rejected/None] For 40 primes 50 < p < 2000 with generator g and precision 4: the Teichmuller section is a homomorph
hypo H-ECDLP-f1e714 [proposed/None] SCOPE: cofactor-1 non-anomalous ordinary curves over F_p at field_bits in {10, 12, 14, 16, 18, 20}, 
--- hypotheses.jsonl hits for ['Teichm']: 2
$ ledger_grep 'integral (lift|model)'
prop IDEA-20260814-c3af09 [proposed/unverified] CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta,
prop IDEA-20261016-3049ff [proposed/unverified] For a live arm (IDEA-20261016-6ad2a5) and admissible coprime (a,b) with aP^+bQ^=O, every exact torsi
--- proposals.jsonl hits for ['integral (lift|model)']: 2
hypo H-ECDLP-5b4ade [proposed/None] Formalises IDEA-20260814-c3af09, WITH ITS PRUNING BASELINE DISAMBIGUATED BECAUSE ONE OF THE TWO READ
--- hypotheses.jsonl hits for ['integral (lift|model)']: 1
$ ledger_grep 'Z/p\^2'
prop IDEA-20260905-4dca34 [proposed/unverified] The testable prediction is that F(P)=x(P)^2/A modulo p^2 is unchanged by admissible short-Weierstras
prop IDEA-20261006-a984aa [proposed/unverified] R1 coordinates in Z/p^2 Z; no attack stage is assigned a new charged cost, and no scalar is claimed 
prop IDEA-20261017-5c1d2a [proposed/unverified] p=m^d-c prime; pi=alpha-m generates the degree-1 prime of Z[alpha]=Z[X]/(X^d-c), N(pi)=+-p; psi2: Z[
--- proposals.jsonl hits for ['Z/p\\^2']: 3
hypo H-ECDLP-e9d9bb [specified/None] Fix an ordinary short-Weierstrass model y^2 = x^3 + A x + B over Z/p^2 Z with p > 3, A a unit, and a
--- hypotheses.jsonl hits for ['Z/p\\^2']: 1
$ ledger_grep 'Semaev.*(lift|valuation)|(lift|valuation).*Semaev'
prop IDEA-20260805-5ac0a2 [None/unverified] The frozen review-only protocol for this goal (coordination/goals/GOAL-RELN-001/batches/BATCH-001/ta
prop IDEA-20260814-c3af09 [proposed/unverified] CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta,
prop IDEA-20260830-c5c614 [proposed/unverified] (A) WHAT IS ALREADY CLOSED, SO THAT THIS IS NOT MISTAKEN FOR IT. KN-FIND-007 fixes the mean per-targ
prop IDEA-20261006-06fe5e [proposed/unverified] On E: y^2 = x^3 + x + 2 over F_41, the points (0, 17), (1, 2), (3, 14), and (5, 3) lie on E. For eac
prop IDEA-20261006-52015b [proposed/unverified] On one complete ordinary 2-isogeny volcano over a prime p in (300, 2000), with j-invariants 0 and 17
--- proposals.jsonl hits for ['Semaev.*(lift|valuation)|(lift|valuation).*Semaev']: 5
hypo H-DREG-dbf17b [proposed/None] For the fixed literal integer matrices and two supplied integral membership models of one Semaev cha
hypo H-ECDLP-36d25e [specified/None] Fix the exact 2-bit residue identity of IDEA-20260913-fa01b7 before any doubling map, any 4-letter w
hypo H-ECDLP-4a00b8 [specified/None] Fix the exact two low bits of the {0,...,p-1} lift of affine x of one frozen toy before any Gamma or
hypo H-ECDLP-5b4ade [proposed/None] Formalises IDEA-20260814-c3af09, WITH ITS PRUNING BASELINE DISAMBIGUATED BECAUSE ONE OF THE TWO READ
hypo H-ECDLP-7b7398 [specified/None] Fix the multiplicative N^2-th-root uniqueness on F_p^* before any cubical point, division polynomial
hypo H-ECDLP-98f679 [specified/None] Fix the exact remainder identity rem = r mod g before any transposed half-gcd, subresultant product 
hypo H-ECDLP-b169f6 [specified/None] Fix the exact 2-bit complete-residue lift of affine y of one frozen toy before any Gamma orbit, Sema
hypo H-ECDLP-cacf58 [specified/None] Fix the ring Z[i] before any Coppersmith small-root solve, Semaev polynomial, Velu map, yield ratio,
hypo H-VOLC-520108 [approved/None] TEST BOUNDARY. Search primes upward from 307 inclusive while p < 2000. The sample is the first prime
--- hypotheses.jsonl hits for ['Semaev.*(lift|valuation)|(lift|valuation).*Semaev']: 9
$ ledger_grep 'valuation'  (62 proposal + 22 hypothesis hits, mostly unrelated CSIDH/AES/FHE text; relevant ones picked by hand below)
```


## Procedure disclosure
- I ran `ls ledger/proposals | grep -E "20260806-c5d183|20260901-863e36"` and `ls ledger/hypotheses | grep -i trop` (directory listings filtered to a fixed id / one keyword) while locating the N4 records and checking for H-TROP files. The task says never to read ledger/proposals/ as a directory; these were filename checks, no listing was read or reused beyond confirming the two exact paths. Disclosed here.
- Full ledger records opened for N3 (3): ledger/proposals/IDEA-20260814-c3af09.yaml, ledger/hypotheses/H-ECDLP-5b4ade.yaml, ledger/proposals/IDEA-20260723-006.yaml. The reads of ledger/proposals/IDEA-20260806-c5d183.yaml and IDEA-20260901-863e36.yaml were partial head reads (first ~60-70 lines) done for N4, which names them explicitly; they are not counted as N3 decision reads.
- Beyond N3: knowledge records read for N1/N4: lead YAMLs listed in section 1, KN-FIND-1ba0fe, KN-FIND-ffe1df (Theorem C passage), KN-OPEN-020, KN-OPEN-3417fc, KR-IC-5931ee, KR-IC-cd159a, coverage.tsv lines for c3af09 / H-ECDLP-5b4ade, and the candidate's scratch files tropical_r2.py / tropical_r2.out (read only).
- No file inside the repositories was created, edited or staged. Writes: this file and scout/_c3val_raw/*.

## 1. N1 atlas collision (top hits of every run read at lead-YAML level: mechanism + obstruction + forecloses)

No lead row in the atlas has a tropical / initial-form / Newton-polygon mechanism (grep of ATLAS.md and of all lead YAMLs for tropical, Newton poly, initial form, Hensel: zero hits in ATLAS.md; the only YAML hits for valuation/Hensel are the p-adic lift leads, digit-presentation, and three structure leads that use "valuation" in an unrelated sense). Lexical miss is therefore NOT the end; the semantic matches are:

1. LEAD-EXO-padic-jet-canonical-lift (closed_obstructed, kind proof; run 3 rank 1). Mechanism: lift POINTS to Z/p^2 / E(Q_p) and read a formal-log or valuation digit. forecloses: prime-to-p jet logarithm; dual-number lift of the addition law; canonical lift formal logarithm; Teichmuller lift digit; Serre-Tate canonical lift attack; extend Smart anomalous attack to ordinary curves; valuation profile of torsion lift. Obstruction (verbatim, Scope included): "For gcd(n,p)=1 the prime-to-p torsion lifts uniquely (finite etale) with zero formal defect and multiplication by l is invertible on every native jet, formal and p-typical target, so every additive order-l image is zero (IDEA-004 gate, independently verified); jet oracles are GGM-simulable with O(1) overhead (KN-FIND-002). The digit identity d(mS^)=m*d(S^) holds only on the HARD global lift (1360/1360 exact, KN-FIND-85845f), whose cost is the lift itself; the computable Teichmuller-style contrast reads as chance under a resolution-matched repaired test (KN-FIND-e8cfdc); IDEA-436 D1 valuation profile collapses to the +/- fibre indicator (KN-FIND-1ba0fe). Scope: ordinary prime-field curves, toy primes 10-14 bits for the measured parts." What the candidate does that the forecloses phrases do not cover: it lifts the POLYNOMIAL SYSTEM and tracks branch cells, not a point or a curve; no forecloses phrase names it. Same phenomenon (valuation data of a lift of F_p data is constant), different object. Not the same mechanism; same obstruction class (sibling of KN-FIND-1ba0fe).
2. LEAD-TRF-padic-canonical-section (closed_obstructed, theorem; run 4 rank 3). SO-PADIC. Obstruction (verbatim): "For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope: non-anomalous prime-field curves, all lifts of E." The candidate escapes the Scope clause only in the trivial sense (it lifts the system, not E or points); it does not answer the obstruction, it agrees with it.
3. LEAD-ICE-prime-field-semaev-solving-degree (closed_known; run 1 rank 5; this is B2). Obstruction (verbatim): "Naive Semaev IC over prime fields cannot beat generic methods (KR-IC-5931ee). The program reproduced it: at balanced L = q^(1/5) on ordinary toy curves, beta_work(B1) = 0.797 on interval and random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold, 36/36 cells, 105/105 FGLM checks (EV-SDEG-4a1c3d, strong); in ecbench the root-finding/pair-table oracle dominates any prime-field Groebner arm." The candidate's own conclusion ("the pruned decoder is exactly solve f mod p then Hensel") lands the decoder on this object. The candidate does not answer this obstruction (no non-enumerative oracle is supplied).
4. LEAD-ICP-generic-table-decomposition (closed_obstructed, theorem; SO-TABLE). coverage.tsv line 406 maps H-ECDLP-5b4ade (the formalisation of the same decoder) to this lead. Obstruction (verbatim): "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); ... Scope: any generic (enumeration/table) decomposition over F_p." Candidate's escape premise (algebraic, not enumerative) is not exercised: after the lemma the factor-base membership step is again "residue roots then index recovery".
5. LEAD-ICP-algebraic-membership-factor-base (closed_obstructed, theorem; SO-ALGFB; not in a top-5 but named by the candidate). Obstruction (verbatim, Scope included): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). ... Scope: prime-order E/F_p, any base of size B." Candidate: target-conditioned, so it escapes "target-independent" only nominally; the lemma itself says the conditioned branch is the whole system.
6. LEAD-ICP-coppersmith-smallroot-semaev (open_next_step; run 2 rank 6). coverage.tsv line 1631 maps IDEA-20260814-c3af09 here. The lead's mechanism is lattice small-root reach (next step: optimal shift set, reach vs 8/9). The valuation-triviality lemma does not touch that next step. The coverage mapping of c3af09 (Coppersmith) and of its own hypothesis H-ECDLP-5b4ade (generic-table) disagree; the c3af09 -> Coppersmith edge looks like a nearest-neighbour fallback, not a mechanism match. Flag for the lead-atlas skill.
7. Others read and judged not the same object: LEAD-ICP-digit-presentation-solving-degree (open_next_step; digit/Weil-descent analogue; not p-adic), LEAD-ICE-syzygy-cascade-signatures (F5 signatures), LEAD-ICP-construction-normal-form, LEAD-ICE-chained-semaev-dreg-vs-semiregular (Boolean), LEAD-ICP-icperf-writability-boundary (binary), LEAD-STR-special-j-ic-semaev (support sparsity at j=0,1728; relevant only in that special j shrinks A_0, which the lemma already allows), LEAD-ICE-descent-closure-degree-at-scale, LEAD-ICB-decomposition-encoding-and-sat, LEAD-ICB-oakley-quintic-tower (binary), LEAD-TRF-one-point-self-pairing, LEAD-TRF-anomalous-padic-lift (closed_known; Smart, trace one), LEAD-ICE-semaev-cover-monodromy, LEAD-TRF-cm-canonical-lift-heights, LEAD-EXO-global-lift-height (open_next_step; function-field/xedni lifts, a different lift of a different object).

N1 conclusion: no lead is the same mechanism, so not a literal duplicate_of_lead. But the lemma's output is "this mechanism is the residue solve", i.e. it reduces to leads 3/4 (closed) and is a sibling of lead 1's valuation collapse. It advances no OPEN lead (lead 6's next step is untouched).

## 2. N2 known results

- KR hits: KR-IC-5931ee (known_negative/proven: naive Semaev IC over prime fields cannot beat generic methods; run 1 score 3, run 4 score 9), KR-IC-5a43e5 (Semaev summation polynomials), KR-IC-cd159a (lifting to characteristic zero fails; run 4 score 4), KR-IC-fbdb61 (last fall degree; run 1 score 7), KR-IC-955fd6 (symmetries/torsion; run 2 score 8; irrelevant mechanism). No KR row mentions tropical geometry, initial forms or valuations (KRMAP.md grep: zero).
- The decoder reduces, by the lemma, to the naive prime-field Semaev residue solve, which is KR-IC-5931ee. The lemma's route to it is not a KR row.
- Mathematics of the lemma, citation provenance: (a) Einsiedler-Kapranov-Lind, J. reine angew. Math. 601 (2006) 139-157, arXiv math/0408311: RETRIEVED this session (abstract via WebFetch; abstract states the non-archimedean amoeba of a hypersurface is its tropical variety; the abstract does not mention the trivial-valuation case). (b) Maclagan-Sturmfels, Introduction to Tropical Geometry (AMS 2015): RECALLED; the book itself was not opened. A web search returned lecture-note snippets (arXiv 1207.1925, Maclagan's introduction, and problem sets on Maclagan-Sturmfels) stating that for the trivial valuation the residue field is the field itself and the initial form keeps the original coefficients, and that in_w(I) is then an ordinary Groebner-theory initial ideal. That is retrieved at snippet level only, secondary source. So the load-bearing fact "constant-coefficient systems have the Groebner/normal-fan structure, and F_p has only the trivial valuation" is textbook mathematics (retrieved at snippet level, recalled at book level).
- What is new, stated exactly: nothing at the mathematics level and nothing at the frontier level. The only new content is an internal one: applying the fact to the interface of IDEA-20260814-c3af09 / H-ECDLP-5b4ade (see section 5).

## 3. N3 ledger

Ledger index greps (raw in section 0b). Hits that may be the same object:
- IDEA-20260814-c3af09 [proposed/unverified] "CONDITIONAL ALGORITHM TARGET, NOT A RESULT. Fix m in {3,4}, a public factor base F of size B=N^beta, a target-independent integral lift rule..." : the object being closed. OPENED (record 1 of 3).
- H-ECDLP-5b4ade [proposed] "Formalises IDEA-20260814-c3af09, WITH ITS PRUNING BASELINE DISAMBIGUATED BECAUSE ONE OF THE TWO READINGS HAS BAND WIDTH ZERO..." : OPENED (record 2 of 3). Status proposed; implementation "Not yet written"; EXP-ECDLP-5551b6 declared, never run. It lists H-TROP-1 supporting_results as "None internal" and names the three tropical/Semaev sources as recalled. So the valuation-triviality lemma is NOT in the ledger.
- IDEA-20260723-006 [speculative; disposition support, EV-CRYPTO-009] "For every m>=3, the target-sectioned Semaev Newton polytope is the full box outside an explicit O(m)-sized exceptional target set": OPENED (record 3 of 3). This already records the candidate's "Newton polytopes are a square and a cube" (F_p side).
- IDEA-20260901-b4e6eb, IDEA-20260905-3a30d5, IDEA-20260905-848b77, IDEA-20260905-dacf4f, H-CZLIFT-6d4ed1/-fba874/-d37231, H-ECDLP-e9d9bb, IDEA-20261006-a984aa: p-adic lifts of POINTS / Teichmuller / Hensel instrument (index text only, not opened): different object (lift of points), same sibling family as LEAD-EXO-padic-jet-canonical-lift.
- IDEA-20260801-021 / H-RELN-a44c18 (bounded-degree factor-base theorem) : the SO-ALGFB source; index text only.
- H-DREG-dbf17b "Exact exceptional-characteristic and kernel-lifting certificates for fixed integral presentations" (index text only): integral presentations of a Semaev chain, specialisation maps; not a decoder.
- Legacy ideas ECDLP-IDEA-085/087/098/103/436 (named by c3af09's own novelty_note) are legacy-tree records, not in the index; c3af09 records its own screen against them. Not re-read.
Decision: no ledger record states the lemma; c3af09 + H-ECDLP-5b4ade are the targets it would close, and both are open (proposed). So the lemma is not a duplicate of a ledger record; it is a would-be disposition of two of them.

## 4. N4 notation check

Pair: representation R1 = Z_p-lift of the coordinates and of the polynomial system (ordered monomial-valuation vector + residue initial form of a branch); operation set Sigma = {initial form, substitution, Hensel refinement}; Sigma contains neither full nor partial translation by group elements.
- IDEA-20260806-c5d183 (constant-or-injective under FULL translation; trichotomy partial action / branching / coordinate-dependent): p-adic lifts are listed there verbatim in class III (coordinate dependence). The lemma's two tracked projections realise the two alternatives: source -> valuation vector is CONSTANT (0) on unit-coordinate sources; source -> residue initial-form root is the identity on F_p-coordinates (INJECTIVE). So the lemma is an instance of the recorded dichotomy in the class-III slot, with translation replaced by lift-compatible operations; it is not a new rigidity statement and not an escape.
- IDEA-20260901-863e36 (projection paired with an operation group; lossy objects = block systems): the only non-constant part of the valuation projection is the x_i = 0 stratum (and infinity), which is invariant under Gamma = {+1,-1}: a two-block system. That is exactly the "trap" named in (C3) there (lossy, propagates, shrinks nothing, |S| = 2), and it is the same collapse as KN-FIND-1ba0fe (valuation profile = +/- fibre indicator).
- KN-OPEN-020 (bounded-degree algebraic factor bases scoped out; open class = high-degree, implicit-membership, target-dependent descriptions): the c3af09 decoder is an implicit-membership, target-conditioned description, i.e. inside the open class. The lemma does NOT close KN-OPEN-020; it removes one candidate realisation of the class (a Z_p lift of the Semaev system) by showing its implicit membership test is the F_p residue test. KN-OPEN-020 stays open.
- KN-FIND-ffe1df Theorem C (exact sum-compatible filter on E(F_p) is a quasigroup, hence a group homomorphism, impossible for prime N with M < N): the valuation vector is not a sum-compatible filter (no combining rule on valuation values), and forcing it to be one would give Theorem C's homomorphism contradiction. Consistent with, not a restatement of, Theorem C.
N4 conclusion: in new notation the lemma is a recorded-class instance (c5d183 class III + 863e36 trap block system + 1ba0fe fibre indicator), carrying one genuinely different ingredient only in the object it is applied to (a lifted polynomial system with a branch structure, not a lifted point).

## 5. Checks of the candidate's own evidence (done in this gate run)

C1. Candidate's tropical_r2.py Part B (scout/padic-tropical-r2/tropical_r2.py, output tropical_r2.out) was READ, not re-run. Output matches the candidate's numbers: m=2: 59 sources, 600/600 init-form checks; m=3: 10 sources, 120/120; total 69 sources and 720/720. 
C2. Part B cannot fail by construction: the factor base is x in {1..B} (no x = 0), so "0 of 69 sources with non-zero valuation" is forced; and each lift is built as (c mod p) + p*k on the support (so in_0 = residue is forced) plus p-multiples off support. Part B tests the code against the lemma's own definition; it is an illustration, not an empirical test. The lemma is a proof-level statement; Part B adds no evidence for or against it.
C3. Part B's "sources" are F_p-roots of S_{m+1}(x1..xm, xR) with x in 1..B and random xR in [1,p); there is no check that those x are x-coordinates of E(F_p) points (twist x-values are admitted) and no point-sum certificate. The count 69 is therefore not a certified E(F_p) source count. Does not affect the lemma.
C4. OWN check (_c3val_raw/own_check.py, python3 -I): curve a=115, b=144 over F_211, b a QR so x = 0 is on E(F_p); factor base = 14 x-coordinates of E(F_p) points including 0; S_3 sources over 40 targets xR in x(E(F_p)): 69 sources (coincidence with the candidate's 69, different object), of which 7 have a coordinate equal to 0 and fall in the boundary cell w = (1,0) (valuation vector with a 1 under the lift rule 0 -> p), not at w = 0. Consequence: the lemma needs the qualifier "sources with all coordinates nonzero mod p"; zero-coordinate sources (at most one x-value per coordinate, i.e. the pair +/-(0, sqrt b), and the point at infinity in a projective chart) live in coordinate-hyperplane faces whose face polynomials are the residue restricted to x_i = 0, again F_p computations. This is a qualifier on "exactly one source-bearing branch", it does not rescue pruning.
C5. ARITY CONVENTION (checked against c3af09 text: "integral model of the Semaev polynomial S_{m+1}", "Fix m in {3,4}"). In c3af09 and H-ECDLP-5b4ade the gate arities m = 3, 4 are S_4 and S_5 (decomposition into m factor-base points, m variables plus the target). The candidate's Part B, its K = 5 / 19 and its "S_3 / S_4" labels are m = 2 and m = 3 in that convention (tropical_r2.py uses m = number of variables). So the candidate's panel covers only ONE of the two gate arities (m = 3); S_5 (m = 4) is untested, and the candidate's H3 line "m in {3,4}" next to "K = 5 (S_3) and 19 (S_4)" mixes two conventions. This is harmless to a proof-level lemma but must be stated.
C5b. OWN count of the normal fan of a full box [0,d]^m (cube): 3^m cones in total, 2^m maximal; non-maximal cones (the cells of the trivial-valuation tropical hypersurface of a unit-coefficient lift) = 3^m - 2^m. m = 2: 9 total / 5 non-maximal (matches the candidate's K = 5); m = 3: 27 / 19 (matches K = 19); m = 4: 81 / 65 (extrapolation, conditional on full-box support of the target-sectioned S_5, which IDEA-20260723-006 asserts for every m >= 3 outside an O(m) exceptional target set; that record is "support" disposition, preliminary; the candidate's Part A verified full support only for m = 2, 3). Under H-ECDLP-5b4ade's baseline ("pruning-erased decoder visits every cell of the declared normal fan") the cell-count ratio of a naive tropical arm is 1 - (2/3)^m: 0.556 (m = 2, outside the gate), 19/27 = 0.704 (m = 3), 65/81 = 0.802 (m = 4, conditional). Both GATE arities exceed 0.70, deterministically, independent of curve and lift. So the candidate's claim that the 0.70 metric "is met trivially in branch count (1/K)" is wrong for a naive tropical arm under the record's own baseline (its 1/K is source-bearing cells over visited cells, a different quantity). A lemma-informed arm that visits only w = 0 plus the coordinate-ray cells would pass on cell count; its work ratio is predicted to be ~1 (H1 below). Either way the interface is vacuous: the cell-count gate fails or is passed by an arm whose work is the residue solve.
C6. By inspection of the record's own gate (iv): the matched random null shares support (full box) and valuation histogram (all zero) with the elliptic arm, so the visited-cell counts are identical by construction and the "elliptic minus null >= 0.15" criterion has value exactly 0 in cell count. This is a second, independent way the record's own falsification condition 4 would fire deterministically. (Derived by reading definitions; not measured.)
C7. Not produced by anyone yet: the work-unit ratio. Heuristics, numbered, all PREDICTIONS:
  H1 (candidate's H3): charged-F_p-operation ratio vs the pruning-erased decoder is >= 0.95 at the gate arities m in {3,4} (S_4, S_5; the candidate's own panel only reaches S_3, S_4), because the w = 0 cell carries the full residue solve and the other cells carry face polynomials (binomial/low-dimensional).
  H2 (this gate): the naive-tropical-arm cell-count ratio is exactly 1 - (2/3)^m (19/27 at m = 3, 65/81 at m = 4 if the S_5 support is the full box) for every lift whose support coefficients are units (combinatorial, from C5b; derived, checkable without compute; the m = 4 value is conditional).
  H3 (this gate): any decoder in this family returns exactly the F_p-root set of the residue system intersected with F, so recall 1.000 is automatic and carries no evidence about pruning.
  Until the c3af09 panel (or a cheap count run) is executed, the "falsified on its own interface" wording is a proof-backed prediction, not a measured outcome.

## 6. Verdict

verdict: known_result.
- Mathematical core = trivial-valuation tropical geometry (textbook; EKL abstract retrieved, Maclagan-Sturmfels book recalled, lecture-note snippets retrieved): F_p-points tropicalise to the origin, in_0 is the residue, other cells carry face polynomials.
- Consequence = the decoder equals the naive prime-field Semaev residue solve: KR-IC-5931ee, B2 (LEAD-ICE-prime-field-semaev-solving-degree, beta_work 0.797 / 0.647 vs 0.30), with the generic-table obstruction (LEAD-ICP-generic-table-decomposition) on the enumeration side. The candidate answers none of those obstructions and says so (tier X, predicted gain 0).
- Why this is not read as the "closed lead whose obstruction the candidate does not answer" duplicate trigger: the candidate is a no-go argument against a proposal, not an attack mechanism that fails B2's obstruction; no closed lead records a lifted-system / initial-form decoder; and it extends LEAD-EXO-padic-jet-canonical-lift (sibling of KN-FIND-1ba0fe) rather than restating it. If a reviewer reads the strict rule literally, the nearest duplicate lead is LEAD-ICE-prime-field-semaev-solving-degree, and either label drops the candidate as a lead, so the downstream action is the same.
- Not duplicate_of_lead in the strict mechanism sense (no lead has a lift-the-system / initial-form mechanism), not advances_lead (no open lead's next step is touched), not new (frontier delta zero, nothing in the SO list is escaped, N4 instance of recorded classes).
- What survives as a deliverable: a ledger disposition for IDEA-20260814-c3af09 / H-ECDLP-5b4ade (proposal + hypothesis still "proposed"), with the qualifiers C2-C6, filed as a scope extension of SO-PADIC / LEAD-EXO-padic-jet-canonical-lift (lift of the system, sibling of KN-FIND-1ba0fe) and cross-referenced to LEAD-ICE-prime-field-semaev-solving-degree. Also fix the coverage.tsv inconsistency (c3af09 -> Coppersmith, H-ECDLP-5b4ade -> generic-table). Do not carry as an attack lead.
