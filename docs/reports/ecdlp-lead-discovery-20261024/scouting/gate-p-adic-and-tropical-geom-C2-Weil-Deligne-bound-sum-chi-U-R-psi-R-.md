# Gate record: C2 Weil-Deligne bound |sum chi(U(R)) psi(R)| <= 2 sqrt(p) for the Miller primitive twisted by group characters; Smart-ratio arm measured null (B7)

Field key: p-adic and tropical geometry (etale / character-sum corner). Bottleneck B7. Tier X. Candidate provenance field: recalled (GOS and Weil II recalled; the additive Kohel-Shparlinski form was retrieved by the candidate and re-retrieved by this gate; the multiplicative-times-group-character form with constant 2 is the candidate's derivation).
Gate run: 2026-10-24/25. Environment: LEAD_ATLAS_CRYPTO=.../scratchpad/crypto-main LEAD_ATLAS_CRYPTANALYSIS=.../scratchpad/cryptanalysis-main LEAD_ATLAS_ECC_CHALLENGES=/Volumes/SSD990-2/ecc-challenges; tools run from /Volumes/SSD990-2/crypto-autoresearcher.

Raw tool outputs follow VERBATIM (N1 atlas, N2 frontier map, N3 ledger grep); each block is the unedited stdout (lead_atlas/frontier runs were piped through head -80/-120/-40 caps, none reached). Analysis is at the end.

## N1 raw: python3 tools/lead_atlas.py --match, phrasings 1-3 (given) and 4 (own)
```
=== N1 run 1: python3 tools/lead_atlas.py --match "Weil-Deligne bound 2 sqrt(p) for multiplicative characters of the Miller function twisted by group characters of E(F_p)" ===
   11  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
   10  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
    9  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    8  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    8  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    7  KR-RHO-cd0049                                known_result       Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    7  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
    6  KR-RHO-0528e7                                known_result       Automorphisms give a sqrt(m) constant factor

=== N1 run 2: python3 tools/lead_atlas.py --match "the log of the Miller value is equidistributed and uncorrelated with the discrete log" ===
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    9  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    8  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    8  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    7  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    7  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class

=== N1 run 3: python3 tools/lead_atlas.py --match "any non-homomorphic section recovers d only at the random 1/p rate" ===
    6  LEAD-STR-jmv-random-self-reduction           closed_known       Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level
    5  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    5  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    4  LEAD-ICE-semaev-cover-monodromy              closed_obstructed  Semaev summation-cover monodromy / Frobenius cycle types as a relation-rate gate
    4  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    4  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    4  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    3  KR-RHO-6239aa                                known_result       Parallel collision search with distinguished points

=== N1 run 4: python3 tools/lead_atlas.py --match "Miller function character sum exponential sum Weil bound" ===
   12  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    8  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    6  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    6  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    5  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    5  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
    4  KR-IC-5a43e5                                 known_result       Semaev summation polynomials

```

## N2 raw: python3 tools/build_frontier_map.py --match, same four phrasings
```
=== N2 run 1: python3 tools/build_frontier_map.py --match "Weil-Deligne bound 2 sqrt(p) for multiplicative characters of the Miller function twisted by group characters of E(F_p)" ===
KR-RHO-13bf67  score=9  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-cd0049  score=7  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-RHO-0528e7  score=6  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-fb88e6  score=5  [known_mechanism/proven]  Negation map: sqrt(2) gain and fruitless cycles
    sources: KN-LIT-074c32, KN-LIT-c8e485, KN-LIT-5b238b, KN-LIT-a5c59c
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-93979e  score=4  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007

=== N2 run 2: python3 tools/build_frontier_map.py --match "the log of the Miller value is equidistributed and uncorrelated with the discrete log" ===
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
KR-IC-64659b  score=1  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-889857  score=1  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-93979e  score=1  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2

=== N2 run 3: python3 tools/build_frontier_map.py --match "any non-homomorphic section recovers d only at the random 1/p rate" ===
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-6239aa  score=3  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-53c89f  score=2  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5931ee  score=1  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5ea2f8  score=1  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-791cb7  score=1  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007

=== N2 run 4: python3 tools/build_frontier_map.py --match "Miller function character sum exponential sum Weil bound" ===
KR-IC-5ea2f8  score=6  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-fbdb61  score=5  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-8b9daa  score=4  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-46d822  score=3  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-5765d2  score=3  [known_mechanism/measured]  SAT and XOR reasoning for point decomposition
    sources: KN-LIT-92b022, KN-LIT-102cdb, KN-LIT-6e036d

```

## N1 + N2 raw, two further own phrasings (5, 6)
```
=== N1 run 5 (own phrasing): python3 tools/lead_atlas.py --match "Kohel Shparlinski exponential sums over a subgroup of E(F_p) twisted by group characters Lang isogeny Bombieri" ===
   10  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    9  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    9  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    9  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
    8  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
    7  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    6  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
=== N2 run 5 (own phrasing): python3 tools/build_frontier_map.py --match "Kohel Shparlinski exponential sums over a subgroup of E(F_p) twisted by group characters Lang isogeny Bombieri" ===
KR-IC-791cb7  score=10  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-755e35  score=7  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-5ea2f8  score=3  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-955fd6  score=1  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-ae532f  score=1  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-e2d81b  score=1  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772

=== N1 run 6 (own phrasing): python3 tools/lead_atlas.py --match "Fourier spectrum of a canonical non-homomorphic quasi-homomorphism onto F_p^* is white" ===
    7  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    6  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    5  LEAD-TRF-padic-canonical-section             closed_obstructed  Canonical point sections E(F_p) -> E(Q_p) and their p-adic digits on non-anomalous curves
    4  LEAD-EXO-padic-jet-canonical-lift            closed_obstructed  Prime-to-p jets, canonical/Teichmuller lifts and p-adic formal-group digits
    3  KR-IC-cd159a                                 known_result       Xedni calculus and lifting to characteristic zero fail
    3  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    2  LEAD-TRF-global-lift-small-height            closed_known       Global lifts to E(Q) or E(K) with small canonical height (xedni, SNFS / cyclotomic / Solinas number fields, rational 2-torsion lifts)
    2  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
=== N2 run 6 (own phrasing): python3 tools/build_frontier_map.py --match "Fourier spectrum of a canonical non-homomorphic quasi-homomorphism onto F_p^* is white" ===
KR-IC-cd159a  score=3  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-5b1c0a  score=1  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5

```

## N3 raw: ledger index grep (python3 c2_n3.py over /Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/{proposals,hypotheses}.jsonl; fields claim, statement, mechanism, title; case-insensitive; regex shown per term)
```
##### proposals.jsonl: 2678 rows
--- term [miller] regex /miller/ -> 9 hits (first 14 shown)
  IDEA-20260807-5f24d7 | proposed | THE MOV COST FUNCTIONAL IS A MINIMUM OVER THREE BRANCHES, NO | (A) THE DEFECT BEING REPAIRED, AND ITS TWIN. This campaign has a recorded cost-model failure - accor
  IDEA-20260807-63ab15 | proposed | Both approved JMV hypotheses declare their central input LOA | H-JMV-001 rests on the claim that Figure 1 of Jao-Miller-Venkatesan misreports c_pi for P-256 and re
  IDEA-20260807-cb672c | proposed | THE BRIDGE DETECTOR, AND THE NULL IT MUST CLEAR FIRST: a mut | (A) THE PROBLEM THIS SOLVES. Every other L10 proposal in this batch predicts a null: the bridge from
  IDEA-20260807-e7eb5d | proposed | THE SELF-PAIRING INSTRUMENT AND ITS NULL - a pure-Python Mil | (A) WHY THIS EXISTS. This lane's three closure records (IDEA-20260807-464ff8, IDEA-20260807-30868b, 
  IDEA-20260812-3182cf | proposed | Which re-randomiser does the ordinary prime-field lane actua | Three statements, E1-E3, of which E1 costs no compute at all and is a written audit, E2 is a bounded
  IDEA-20260905-24b41a | proposed | NETS, CUBICAL LIFTS, MILLER FUNCTIONS AND DUAL-NUMBER LIFTS  | REPRESENTATION CLASS AND STAGE (RQ-ECDLP-623a32): class R3 (non-function representations - elliptic 
  IDEA-20261006-237ce0 | proposed | The Weil pairing of one order-5 point with itself is 1 on y^ | Let E be y^2 = x^3 + 2x + 3. Let p be the smallest prime with p > 20 and p < 120 such that E is nons
  IDEA-20261009-c8433d | proposed | Generalized-Jacobian extension class equals the Tate pairing | The connecting homomorphism agrees with Miller's algorithm up to a fixed convention on 100% of insta
  IDEA-20261017-e3a6f1 | proposed | The Miller cocycle has a canonical primitive U: E(F_p)[N] -> | E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
--- term [weil bound / deligne] regex /weil[- ]?(bound|deligne)|deligne|hasse-weil/ -> 1 hits (first 14 shown)
  IDEA-20260926-cafcf1 | proposed | THE ABSCISSA DENSITY OF A SUBSPACE FACTOR BASE IS NOT CONTRO | Representation class R1 of RQ-ECDLP-623a32 (the abscissa in any F_2-basis); the attack stage whose c
--- term [multiplicative character / Hom(E,G_m)] regex /multiplicative[- ]characters?|Hom\(E,\s*G_m\)/ -> 3 hits (first 14 shown)
  IDEA-20260913-1eb65c | proposed | Cubic residue of affine y under doubling | The cubic residue symbol chi_3(y(P)) = y^{(p-1)/3} in F_p, for p=1 mod 3, is a lossy R1 multiplicati
  IDEA-20260913-d76b38 | proposed | Quadratic residue of affine x under doubling | The Legendre symbol chi_2(x(P)) = x^{(p-1)/2} in F_p is a lossy R1 multiplicative-character projecti
  IDEA-20260928-fd7f5d | proposed | The incomplete-sum regime of Hom(E,G_m) = 0. Do multiplicati | R1 representation; the stage is relation decomposition (target selection). KN-OPEN-020 classes: targ
--- term [lang torsor / kummer sheaf] regex /lang torsor|kummer sheaf|tame sheaf/ -> 0 hits (first 14 shown)
--- term [character sum / exponential sum] regex /character[- ]sum|exponential sum/ -> 7 hits (first 14 shown)
  IDEA-20260805-c4f675 | unverified | The H-PSEUDO character-sum constant has never been divided b | This goal's H-PSEUDO lane measures C(p) = max_{k=1..N-1} |sum_{P in F} e(2 pi i k DL_G(P)/N)| / sqrt
  IDEA-20260808-726aa3 | proposed | Name the missing exponential-sum ingredient: quantify exactl | Let H <= F_p^* be the subgroup of order B = (p-1)/d, so membership x in H is testable in O(log p) by
  IDEA-20260816-f49ad1 | proposed | Test whether one scalar - the largest non-trivial character- | (A) THE STATE THIS REPLACES. Factor-base geometry results in this program are point estimates indexe
  IDEA-20260829-4b34c5 | proposed | Replace the order-theoretic accepted set by a multiplicative | TWO-SIDED CLAIM, both sides informative. POSITIVE SIDE. The accepted set D_chi, defined as the set o
  IDEA-20261002-8f26ce | proposed | Artin-Schreier curves of genus 5 and 6 over F_2 as the expli | The Artin-Schreier family y^2 + y = f(x) over F_2, f of odd degree 11 or 13, either contains a curve
  IDEA-20261003-247e49 | proposed | The symbol values -1, 0, and 1 number 3 and their absolute v | The frozen symbol values are -1, 0, and 1. They number 3. The absolute values 1, 0, and 1 sum to 2 a
  IDEA-20261006-5db10b | proposed | Doubling-sum character sum on one prime-field curve exceeds  | Let E be y^2 = x^3 + x + 3 over F_47, let s(P) = x(P) + x(2P) for affine points with y(P) ≠ 0 and s(
--- term [smart-ratio] regex /smart[- ]?ratio/ -> 2 hits (first 14 shown)
  IDEA-20261016-0bacee | proposed | Break-even line for full-value section predictors: Smart-rat | O = any cheap procedure outputting one candidate for dlog_P(R) (the lane's Smart ratio), success rat
  IDEA-20261016-8961d2 | proposed | Exact census of a whole section class: Smart-ratio success o | E/F_p ordinary, <P> of prime order n!=p, V_k=L(kO)(F_p) (dim k, k=3,4). Each f in V_k gives the sect
--- term [e3a6f1|c8433d|09fd08] regex /e3a6f1|c8433d|09fd08/ -> 0 hits (first 14 shown)
--- term [zeta-defect] regex /zeta[- ]defect/ -> 1 hits (first 14 shown)
  IDEA-20261016-09fd08 | proposed | The zeta-defect Z: a lift-free canonical quasi-homomorphism  | y^2=x^3+ax+b/F_p, G=<P> odd order n prime to p, chord slope lam(R,S)=(y_R-y_S)/(x_R-x_S) (tangent at
--- term [cocycle|canonical primitive] regex /cocycle|canonical primitive/ -> 10 hits (first 14 shown)
  IDEA-20260805-128f35 | unverified | The involution budget of a cyclotomic conductor: an exact ce | The engine of the disclosed HAWK attack (KN-LIT-7592) is stated by its own entry as "the object hidi
  IDEA-20260805-6eac55 | unverified | The tau-cocycle lattice as an integral quadratic form: a sie | The whole load-bearing step of the disclosed HAWK key-recovery attack (KN-LIT-7592, Straznickas-Weis
  IDEA-20260807-add964 | proposed | THE SIGN COCYCLE: an x-coordinate factor base only determine | (A) THE OBJECT EVERY x-COORDINATE FACTOR BASE ACTUALLY HAS. A factor base given by x-coordinates x_1
  IDEA-20260808-b1358c | proposed | Q(zeta_2n) has THREE order-2 Galois involutions and the publ | For HAWK-n over R_n = Z[X]/(X^n+1), n = 2^{l-1}: (A) the involution sigma_{n-1} : zeta -> -zeta^{-1}
  IDEA-20260821-3d5f22 | proposed | THE n-TORSION EDGE CHARACTER chi IS THE EXPLICIT BRIDGE MAP  | FIVE CLAIMS. C1-C4 ARE DERIVATIONS COSTING NO COMPUTE AND TOGETHER DISCHARGE RQ-CLGP-b99df5'S DECISI
  IDEA-20260905-4b07f5 | proposed | Descent-cocycle obstruction as a compositional isogeny certi | An isogeny representation equipped with explicit field-descent isomorphisms can certify exactly when
  IDEA-20260905-b6ae7e | proposed | Pointed torsor holonomy as the missing reduction interface | A class-group torsor cannot supply a point-group bridge merely from unpointed endpoints. Conjecture:
  IDEA-20260905-da0612 | proposed | Descent-cocycle obstruction as a compositional isogeny certi | An isogeny representation equipped with explicit field-descent isomorphisms can certify exactly when
  IDEA-20261016-09fd08 | proposed | The zeta-defect Z: a lift-free canonical quasi-homomorphism  | y^2=x^3+ax+b/F_p, G=<P> odd order n prime to p, chord slope lam(R,S)=(y_R-y_S)/(x_R-x_S) (tangent at
  IDEA-20261017-e3a6f1 | proposed | The Miller cocycle has a canonical primitive U: E(F_p)[N] -> | E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni
--- term [section recovers / random 1/p] regex /non-homomorphic section|random 1/p/ -> 0 hits (first 14 shown)
--- term [bombieri|kohel|perel] regex /bombieri|kohel|perel/ -> 5 hits (first 14 shown)
  IDEA-20260807-15f103 | known_in_substance | CLOSURE with named obstruction: smooth-conductor descent wit | Within an ordinary isogeny class (fixed trace t, fixed group order N), the CM conductor f varies fro
  IDEA-20260903-fc1355 | proposed | THE NESTED DIGIT LADDER IS PROFILE-BLIND UNDER THE SEMI-REGU | Setting as in IDEA-20260830-84cdb7: base d >= 2, nested windows V_s = {x in [0, d^s) : f(x) a square
  IDEA-20261001-9d8520 | proposed | DOES DOUBLING THE LARGE-PRIME BOUND ABSORB ≥α OF ORPHANED SE | Double-large-prime variants are standard in hyperelliptic / extension-field IC (KR-IC-a4dd54 / KR-IC
  IDEA-20261002-711e84 | proposed | Mumford u-coefficient eliminant of a genus-2 Jacobian fibre  | On a genus-2 curve C/F_2 whose Jacobian has a rational point of order 19, the Couveignes fibre of tr
  IDEA-ISO-7f3e2d | known_in_substance | CLOSURE with named obstruction: smooth-conductor descent wit | Within an ordinary isogeny class (fixed trace t, fixed group order N), the CM conductor f varies fro
##### hypotheses.jsonl: 2131 rows
--- term [miller] regex /miller/ -> 12 hits (first 14 shown)
  H-ECDLP-1e5be9 | specified | Exact affine sum x+y Stage 0 identity — S=5 and S'=8; claimi | Fix the exact affine sum S=x+y of one frozen toy before any Gamma orbit, Semaev S_m, nested LHW gene
  H-ECDLP-4a00b8 | specified | Exact two low bits of the integer lift of affine x Stage 0 i | Fix the exact two low bits of the {0,...,p-1} lift of affine x of one frozen toy before any Gamma or
  H-ECDLP-69301c | specified | Stage 0 cubic-residue identities — p=7, (p-1)/3=2, chi_3(1)= | Fix the exact cubic-residue exponent identity of IDEA-20260913-1eb65c before any doubling map, any 3
  H-ECDLP-74ecc8 | specified | Exact quadratic residue of affine x Stage 0 identity — chi_2 | Fix the exact quadratic residue of affine x of one frozen toy before any Gamma orbit, Semaev S_m, ne
  H-ECDLP-84eb73 | specified | Embedding-order Stage 0 identity — ord_N(p) and the forced c | Fix the embedding-degree integer k = ord_N(p) and the forced cyclotomic factor-degree multiset {1} u
  H-ECDLP-a89b28 | specified | Exact cubic residue of affine y Stage 0 identity — chi_3(y)= | Fix the exact cubic residue of affine y of one frozen toy before any Gamma orbit, Semaev S_m, nested
  H-ECDLP-aca677 | specified | Exact affine doubling-slope Stage 0 identity — lambda=18 and | Fix the exact affine doubling slope of one frozen toy before any Gamma orbit, Semaev S_m, nested LHW
  H-ECDLP-f8cea6 | proposed |  | A public reduced-Tate character can be evaluated and decoded without hidden scalar input on the fini
  H-JMV-001 | approved |  | Figure 1 of Jao-Miller-Venkatesan 2005 (arXiv:math/0411378v3) misreports the Frobenius conductor c_p
  H-JMV-002 | supported |  | Under the PROVEN (GRH-conditional, explicitly constant-tracked) form of the Jao-Miller-Venkatesan Le
  H-JMV-71b222 | proposed |  | SCOPE: (A) the primary text of Jao-Miller-Venkatesan 2005 (arXiv math/0411378) as retrieved and doub
  H-JMV-c4ccf3 | specified | Stage 0 re-randomiser ordinary prime-field lane actually com | Fix the exact count identity of IDEA-20260812-3182cf before any later-stage claim. Stage 0 asserts o
--- term [weil bound / deligne] regex /weil[- ]?(bound|deligne)|deligne|hasse-weil/ -> 2 hits (first 14 shown)
  H-BINSTD-61dad7 | approved | Weil-bound vacuity of subspace abscissa density at every ind | CLAIM (control / structural certificate; HOLD-X4). On E_a : y^2 + xy = x^3 + a x^2 + b over F_{2^n} 
  H-PFDR-8a4f44 | proposed |  | THE SAVING A CHARACTER-SUM BOUND WOULD NEED IN ORDER TO CERTIFY A MULTIPLICATIVE-SUBGROUP FACTOR BAS
--- term [multiplicative character / Hom(E,G_m)] regex /multiplicative[- ]characters?|Hom\(E,\s*G_m\)/ -> 0 hits (first 14 shown)
--- term [lang torsor / kummer sheaf] regex /lang torsor|kummer sheaf|tame sheaf/ -> 0 hits (first 14 shown)
--- term [character sum / exponential sum] regex /character[- ]sum|exponential sum/ -> 9 hits (first 14 shown)
  H-ECDLP-1af1b2 | approved | Twice 2 is the written constant 4 | The proposal writes the constant 4 as twice a degree, and writes that degree as 2 for the coordinate
  H-ECDLP-3f58db | specified | Stage 0 index-L subgroup identities — |H|=2 in F_7* — before | Fix the exact subgroup-order identity of IDEA-20260829-4b34c5 before any bilinear character-sum boun
  H-ECDLP-954cae | approved | The cleared numerators 3 and 2 differ by 1 | The proposal writes the window endpoints 3/4 and 1/2. Clearing the common denominator 4 gives the nu
  H-ECDLP-e6772e | specified | Doubling-sum character sum on y^2 = x^3 + x + 3 over F_47 | Let E be y^2 = x^3 + x + 3 over F_47. Let s(P) = x(P) + x(2P) for affine points with y(P) ≠ 0 and s(
  H-ECDLP-fea0be | approved | The largest fibre raises the bound from 1/8 to 1/4, and a do | The fibre sizes 1, 2, 3 and 6 sum to 12. There are 4 fibres, so the average is 3 and the largest is 
  H-ECQ-f22688 | specified | Stage 0 isotypic-degree identities — [k:Q]=829440 at geometr | Fix the exact splitting-degree identity of IDEA-20260829-ece95f before any isotypic concentration is
  H-PFDR-0bc09b | approved | The product 49152 lies strictly between 221 squared and 222  | Sixteen cubed is 4096. Twelve times 4096 is 49152. The square 221 squared is 48841, which is 311 bel
  H-PFDR-8a4f44 | proposed |  | THE SAVING A CHARACTER-SUM BOUND WOULD NEED IN ORDER TO CERTIFY A MULTIPLICATIVE-SUBGROUP FACTOR BAS
  H-PSEUDO-83817b | specified |  | For any prime p, prime-order elliptic curve E/F_p with group order N, generator G, and factor base F
--- term [smart-ratio] regex /smart[- ]?ratio/ -> 0 hits (first 14 shown)
--- term [e3a6f1|c8433d|09fd08] regex /e3a6f1|c8433d|09fd08/ -> 0 hits (first 14 shown)
--- term [zeta-defect] regex /zeta[- ]defect/ -> 0 hits (first 14 shown)
--- term [cocycle|canonical primitive] regex /cocycle|canonical primitive/ -> 3 hits (first 14 shown)
  H-CLGP-26d035 | proposed | The n-torsion edge character chi is the explicit bridge map  | Let E/F_p be ordinary with Frobenius pi, O = End_{F_p}(E), and N a prime with N exactly dividing #E(
  H-SSI-04aea1 | specified | Stage 0 descent-cocycle obstruction compositional isogeny ce | Fix the exact count identity of IDEA-20260905-da0612 before any later-stage claim. Stage 0 asserts o
  H-SSI-c1e29a | specified | Stage 0 descent-cocycle obstruction compositional isogeny ce | Fix the exact count identity of IDEA-20260905-4b07f5 before any later-stage claim. Stage 0 asserts o
--- term [section recovers / random 1/p] regex /non-homomorphic section|random 1/p/ -> 0 hits (first 14 shown)
--- term [bombieri|kohel|perel] regex /bombieri|kohel|perel/ -> 0 hits (first 14 shown)
```


---

# ANALYSIS (written after the raw outputs above; provenance tags are recalled | retrieved)

Verdict: **advances_lead** (lead: LEAD-TRF-miller-cocycle-nonhom-transfer; sibling LEAD-EXO-miller-pairing-cocycle). No new mechanism. The candidate is the execution of the open lead's own next_action (H1 of IDEA-20261017-e3a6f1) plus a derivation for its character-correlation half. The theorem layer is a classical Weil-type bound that the program already carries as "recalled / owed" in three places (below). Nothing here is labelled promising or a breakthrough; the candidate itself claims predicted_gain 0 on the exponent.

## What I did and did not produce

- Produced by me: the N1/N2 runs above (verbatim), the N3 grep, the reads of the lead rows / KB entries / ledger records named below, the literature retrievals listed under N2 (provenance there), and a re-derivation by reading of the Euler-characteristic count (chi_c(E minus {P,O}) = -2, h^0_c = h^2_c = 0 for a geometrically nontrivial rank-one sheaf, weights <= 1 by Weil II). That re-derivation is reading, not computation, and relies on recalled GOS and Weil II.
- Read but NOT produced or re-run by me: the candidate's scripts and outputs under scout/padic-tropical-r2/ (weil_bound_r2.py, smart_ratio_r2.py, miller_eds_r2.py; weil_job0-7.out, smart_job0-5.out). They exist and the numbers the candidate quotes match those files (max |S|/sqrt(p) = 1.99995, 1.99996, 1.99998, 1.99995, 1.99996, 1.99996 on 6 curves with p in 10007..32749; N | p-1 controls 49.99 and 70.91 times sqrt(p), i.e. |S| = N-ish; Smart-ratio successes 1,2,1 and 0,0,3 with z in [-1.00, 2.01]). I did not re-run any of it. Treat every number as the candidate's observation.

## N1 verdict: same mechanism as an OPEN lead

Hits read (YAML mechanism + obstruction + forecloses), top 5 of every run (6 lead_atlas runs: the 3 given phrasings plus 3 of my own; the distinct leads are listed):

| hit | disposition | relation to C2 |
|---|---|---|
| LEAD-TRF-miller-cocycle-nonhom-transfer | open_unexamined | SAME OBJECT. Its next_action is "Test H1 of IDEA-20261017-e3a6f1 at toy size: equidistribution of ell(k)=log_g U(kP), Smart-ratio success and correlation with characters of Z/N ... planted-structure positive control". Its discriminator: "Equidistribution at the 1/p rate closes the lead". C2 is that step. forecloses "Miller function transfer", "zeta defect quasi-homomorphism", "generalized Jacobian transfer" covers C2's U. |
| LEAD-EXO-miller-pairing-cocycle | open_next_step | Same ledger root (e3a6f1). Its next_action is K1/K2 exact on toys, then "whether k can be recovered from U(kP) in fewer than sqrt(N) group operations once r_k is charged". C2 does NOT address K2 or the r_k charging; the Weil bound constrains character correlations only. |
| LEAD-EXO-dl-character-sum-pseudorandom | exhausted_at_scale | Different object (additive DL character of the small-x factor base, incomplete sums). Its closed Weil route (KN-FIND-e7a3b1: "DL_G(P) is non-algebraic") does not apply to C2 because U is algebraic and the sums are complete. C2 does not answer it and does not need to. |
| LEAD-EXO-elliptic-net-eds | closed_obstructed | K2 writes U(kP) = c r_k C^{k/N} with r_k an EDS ratio, so any use of U by relations among net values is inside this obstruction ("net relations encode the group law on one k-fibre and not k; GGM-simulable"). C2 lists SO-PADIC/TORS/PAIR but not SO-NET. |
| LEAD-TRF-padic-canonical-section | closed_obstructed | SO-PADIC. C2 is an analogue for a non-section map (below). |
| LEAD-EXO-coordinate-statistic-leakage | open_next_step | Appeared on my own-phrasing run. Its residual open class is "unnatural (unbounded-degree) statistics". C2 proves one unbounded-degree statistic (degree N, divisor supported on 2 points) is Weil-white for complete sums. This is a cross-lead data point, not a duplicate. |
| LEAD-EXO-padic-jet-canonical-lift | closed_obstructed | Top-5 of run 6. Mechanism: lift to jets / canonical prime-to-p torsion lifts and read a formal-group digit linear in the scalar. Obstruction (kind proof, Scope: ordinary prime-field curves, toy primes 10-14 bits for the measured parts): prime-to-p torsion lifts with zero formal defect, jet oracles GGM-simulable, the Teichmuller-style contrast "reads as chance under a resolution-matched repaired test". forecloses: prime-to-p jet logarithm, canonical lift formal logarithm, Teichmuller lift digit, Serre-Tate canonical lift attack. None names a canonical non-homomorphic map into F_p^* or a white-spectrum phrasing, so C2 is not a duplicate. Its revisit_when sets the program's resolution bar for such nulls: "against a matched null at a resolution that could detect a 3x effect" (best_measured: power >= 0.90 for a 3x effect, alpha = 0.01). Used in O3 below. |
| LEAD-TRF-cm-canonical-lift-heights | closed_obstructed | Top-5 of run 6. Serre-Tate/CM canonical lift and xedni heights; obstruction is a cost model (Hilbert class polynomial degree ~ p^{1/2}) and the height-coverage obstruction. forecloses: canonical lift for ECDLP, CM lifting, Serre-Tate lift heights, Hilbert class polynomial lift. Not C2's object (C2 does no lift). |
| LEAD-TRF-teske-secret-isogeny-trapdoor | open_next_step | Top-5 of run 5 (query words "Lang isogeny"). A weakness varying inside one isogeny class behind a secret isogeny; its panel is Semaev/factor-base yield by conductor level. Nothing in common with a sum over one curve's group. Not a duplicate. |
| LEAD-ICP-representation-subset-sum | closed_obstructed | Top-5 of run 5. Howgrave-Graham-Joux representations on the digit subset-sum; obstruction: generic (Shoup, S*T^2 >~ N). Scope: any representation/filter variant on a prime-order group. C2 uses no filter and no group-operation-only access (it reads coordinates), so not covered, not a duplicate. |
| LEAD-TRF-ghs-binary-composite | closed_known | Top-5 of runs 4 and 5 (query word "Weil"). GHS Weil descent on F_{2^N}, N composite; scope is binary composite-degree fields. "Weil" here is Weil restriction, not the Weil bound. Not a duplicate. |
| LEAD-RHO-generic-sqrt-lower-bound, KR-RHO-13bf67, LEAD-STR-jmv-random-self-reduction, LEAD-ICE-semaev-cover-monodromy, LEAD-ICP-coincidence-harvest-structured-base, LEAD-RHO-automorphism-class-walks, LEAD-STR-automorphism-quotient-rho, LEAD-TRF-function-field-xedni-lift, KR-RHO-46c2c6, KR-RHO-ea34b8, KR-IC-5ea2f8 | various | Read (lead YAMLs: mechanism, obstruction, forecloses; KR rows via the N2 output and KRMAP). Lexical neighbours only; none shares the mechanism. SO-GEN is not engaged: U reads the representation (transfer-type), which is exactly the "revisit_when" carve-out of LEAD-RHO-generic-sqrt-lower-bound ("only a method that reads the representation (index calculus, transfer) can change the exponent"). SO-WALK (LEAD-RHO-correlated-walks-shared-sums) and SO-DECK/SO-CHEON are not engaged by a complete character sum on one group. |

What C2 does that the forecloses phrases do not cover: only (a) a derivation that the U-twisted-by-characters sums have conductor 2 (so |S| <= 2 sqrt(p)), and (b) toy measurements. Neither is a new mechanism; both are the discriminator outcome the lead asked for. The lead is therefore not duplicated (it is not yet answered by any record) and not new.

### The three standing obstructions the candidate lists (verbatim obstruction.statement, Scope included)

- SO-PADIC (LEAD-TRF-padic-canonical-section): "For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope: non-anomalous prime-field curves, all lifts of E."
- SO-TORS (LEAD-STR-torsion-module-leak): "Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). Toy checks agree: the psi_5 factor-degree multiset does not change with k (H-TORS-3bed8a). Scope: prime-order G, any l != N."
- SO-PAIR (LEAD-TRF-second-torsion-direction): "Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1, i.e. the embedding degree divides k. Hence for N not dividing k, T_k(E)[N] = 0 (trace acts as [k] on the rational line), and an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N."

Escape check (strict). C2 does not escape any of the three. It sits inside them:
1. SO-PADIC: U is not a section E(F_p) -> E(Q_p), so the Scope ("all lifts of E") does not literally contain it. But the obstruction's conclusion ("recovers d only at the random 1/p rate") is what C2 supports for U, so C2 is an analogue-closure, not an escape. Note also the Weil bound alone does not give the 1/p rate (item O3 below).
2. SO-TORS: the candidate says F_p^* is not l-primary so U "escapes that premise". That reads only the first sentence of the statement. U is a non-homomorphic point statistic, i.e. the statement's second clause applies to it directly ("a function of the encoding of Q ... costs more than it saves"). U is inside SO-TORS, not outside it; C2's bound is a proof of white spectrum for one such statistic. Its "revisit_when" ("A point-dependent l-torsion statistic computable in o(sqrt N) correlates with k beyond a k-resampled null") concerns l-torsion statistics, which U is not.
3. SO-PAIR: the candidate says the N | p-1 control "is exactly the case that obstruction leaves open". The statement says k_emb = 1 gives a rational graph-type kernel that "reduce[s] to MOV". It is covered (as MOV), not open. C2's regime (gcd(N,p-1)=1, so k_emb != 1) is the regime where the statement gives no second N-torsion direction; C2 does not touch it. The peaking control is the Tate pairing at k_emb = 1, which is textbook (KR-RHO-53c89f).
4. Not listed by the candidate but engaged through K2 (U(kP) = c r_k C^{k/N}, r_k an EDS ratio): SO-NET (LEAD-EXO-elliptic-net-eds, closed_obstructed). Verbatim obstruction.statement: "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead); standard Hankel displacement rank of translated x-blocks is tautological and consecutive blocks have linear complexity >= (M-2)/3 (IDEA-006 gate). Measured at toy prime fields p in {101,431,1601}, n <= 1607: collision statistics are random-oracle-equivalent and the charged k-recovery exponent is 1.97-2.80 against BSGS 1.17-1.32 at identical accounting, with the sieve/BSGS gap growing (24x -> 135x)." The statement carries no explicit Scope clause; its revisit_when asks for "a target-specific NONLINEAR locator outside the closed Hankel/translated-block classes". C2 supplies no locator and does not use net relations, so it neither escapes nor engages the nonlinear-locator carve-out; the sibling lead LEAD-EXO-miller-pairing-cocycle (K2, r_k charging) is where this obstruction would be tested. SO-ENDO, SO-GEN, SO-WALK are not engaged.

## N2: no KR row; classical result, not in the map

Six build_frontier_map runs (same six phrasings): nothing shares the mechanism. Nearest rows are KR-RHO-53c89f (transfer attacks need small embedding degree; relation: adjacent, C2's control is that row's regime), KR-RHO-13bf67, KR-RHO-46c2c6/ea34b8 (lexical only). "No KR hit" is not evidence of novelty: the map is curated, and the bound C2 uses is classical.

Literature check (WebSearch/WebFetch were available; results):
- Kohel-Shparlinski, ANTS-IV, LNCS 1838 (2000) 395-404, Cor. 1: provenance **retrieved**, additive-character form only, via two restatements I read as extracted PDF text. (i) Ahmadi-Shparlinski arXiv:1302.4210, Lemma 1: for ordinary E/F_q and G of order T, any group character chi on E(F_q): sum over n in Z_T of psi(x(nG)) chi(G) << q^{1/2} (implied constant not given there). (ii) arXiv:1706.08710, Lemma 6 (citing [14, Cor. 1]): E ordinary, f in F_q(E), f != z^p - z, psi nontrivial additive: |sum over Q in H of psi(f(Q))| <= 2 deg f q^{1/2} for any subgroup H of E(F_q). The primary K-S PDF (kohel's site) refused the connection and was not read. Neither restatement contains a multiplicative character of F_q^* applied to f. So the candidate's description of its own provenance ("retrieved via Lemma 1 of arXiv:1302.4210, additive form; multiplicative form my derivation") is accurate. The retrieved forms assume E ordinary; the candidate's étale argument as stated has no ordinarity hypothesis (my reading; I did not test supersingular p).
- Perel'muter, Mat. Zametki 5(3) (1969) 373-380: provenance **retrieved at bibliographic/abstract-summary level only** (mathnet.ru search result: mixed additive and multiplicative character sums along an algebraic curve over F_q, bound C sqrt(q) with C depending on degrees); theorem statement and constant not read. Classical home of the multiplicative-times-additive curve bound.
- Bombieri (Amer. J. Math. 88 (1966)), Grothendieck-Ogg-Shafarevich, Deligne Weil II: provenance **recalled**, not opened.
- Program KB: KN-LIT-7639 (Kopparty-Ta-Shma-Yakirevitch, ECCC TR24-069; provenance retrieved from the local KB, entry read) records H1 as "|sum_P chi(F(P))| <= (2g-2+2m) sqrt(p), m the number of distinct zeros and poles of F", with the general character-order k > 2 on a curve flagged "not covered, needs Bombieri's original or Perel'muter". KN-FIND-ffe1df lists "family D (cubic/quartic/octic residue characters)" as NOT closed for exactly that reason. KN-OPEN-d3a6f0 already cites Kohel-Shparlinski ANTS-IV for "twisted by chi" sums (status reported).

So the theorem layer is known, support-governed (not degree-governed), and already carried by the program as owed. C2's Euler-characteristic count (chi_c(U) = -2, rank-1 tame sheaf geometrically nontrivial because monodromy at P is chi != 1, hence h^1_c = 2, weights <= 1) gives constant 2 where the KB's stated shape gives 2g-2+2m = 4 for m = 2; the sharper constant follows from h^1_c = 2g-2+m for a nontrivial tame rank-one sheaf (my reading, conditional on GOS and Weil II being recalled correctly). The candidate's observed maxima 1.99995..1.99998 sit just under 2, which is consistent with the bound being sharp (observation by the candidate; heuristic H-4 below).

## N3: ledger

Index terms searched (full output in the N3 section above): miller, weil bound/deligne, multiplicative character, lang torsor, character sum, smart-ratio, e3a6f1|c8433d|09fd08, zeta-defect, cocycle, bombieri|kohel|perel. The index stores only ~200 chars of each claim, so "Lang torsor" is not searchable there (0 hits) even though a record uses it; absence is not evidence.

Records that may be the same object (id + claim head):
- IDEA-20261017-e3a6f1 (proposed, unverified): "The Miller cocycle has a canonical primitive U ... non-homomorphic transfer into F_p^*". The SOURCE of H1. Opened in full. Its H1 "rigorous_support" field already says: "character sums of such terms are bounded in the recalled literature (unread); imitates random units", and predicts a white spectrum. C2 is H1's validation plan plus a proof of its rigorous_support.
- IDEA-20260905-b6154d (proposed, unverified): "THE WALL, MADE EXACT, AND THE TWO DOORS IN IT: for a bounded-degree coordinate function ... every discrete-log character correlation is at the Weil level". Opened (read to its end). Claim (B) is the SAME proof shape as C2: Lang torsor of chi_a tensored with a Kummer sheaf of eta(f), "geometrically nontrivial ... unless ord(eta) = N", Weil-Deligne, citing Bombieri, Kohel-Shparlinski, Deligne as recalled and "NONE has been opened". It restricts to degree <= D and says Miller/iterated evaluations are OUTSIDE the class, naming the Tate pairing (N | p-1) as the object where "bounded degree" fails. C2's derivation shows the bound is governed by the number of ramified points (conductor), so the degree hypothesis can be replaced for functions with bounded divisor support such as f_{N,P}, and the Tate-pairing control then fails at the nontriviality step (ord(chi)=N), which b6154d also lists. This is the precise thing C2 adds over the ledger: it extends the b6154d class from bounded degree to bounded conductor and runs the one Miller-type instance. It is an extension of an existing proof map, not a new idea.
- IDEA-20260928-fd7f5d (proposed, adaptation): "The incomplete-sum regime of Hom(E,G_m)=0. Do multiplicative characters constant on a coset base bias the characters of x(P+-Q)". Opened (claim section). Different regime: incomplete sums over a base of size B << sqrt(p); it records that complete mixed sums cancel (Deligne-type, recalled) and that the IC regime is below any theorem. C2 is a complete-sum statement; it does not touch this gap.
- IDEA-20261009-c8433d (generalized-Jacobian extension class equals the Tate pairing, trivial on l-parts with l not dividing p^k - 1), IDEA-20261016-09fd08 (zeta-defect Z, additive primitive; C2 does not cover it, as the candidate says), IDEA-20261016-0bacee and -8961d2 (Smart-ratio break-even line c/sqrt(n) and exact census over L(kO) defect functions): index rows read, not opened. 0bacee is relevant to O3 below.
- IDEA-20260905-24b41a ("NETS, CUBICAL LIFTS, MILLER FUNCTIONS AND DUAL-NUMBER LIFTS ARE ONE OBJECT", class R3) and IDEA-20260905-7e154b (arithmetic characters of the curve group, intake): index rows only.
- H-ECDLP-f8cea6 ("public reduced-Tate character can be evaluated and decoded without hidden scalar input"): index row only; the N | p-1 regime, not C2's.
- Full records opened for the dedup decision: 3 (e3a6f1 in full; b6154d in full; fd7f5d claim and mechanism sections only, about 4.2 kB of 17 kB). For N4 I additionally read the claim sections of IDEA-20260806-c5d183 and IDEA-20260901-863e36, which N4 names explicitly.

## N4: notation check (representation, operation set)

PAIR: representation = the F_p^*-valued statistic U(R) = f_{N,P}(R)^{1/N} (R1 coordinate reading through one Miller loop and one exponentiation, then a map to F_p^*); operation set Sigma = translations R -> R + S, acting on U only through the explicit defect g_{R,S}(P) = line(R,S)/vertical(R+S) evaluated at P (K1 of e3a6f1). The defect depends on the coordinates of R and S, not on U(R) alone.

- IDEA-20260806-c5d183 (rigidity theorem, five lines): pi: G -> S propagating deterministically under the FULL translation action is constant or injective. U is non-constant (f_{N,P} is a non-constant function and the exponent N^{-1} mod p-1 is invertible, so U = f^{N'} is non-constant). U is non-injective by pigeonhole whenever N - 2 > p - 1 (the sum domain has N-2 points and F_p^* has p-1): this holds on 5 of the 6 curves in weil_job0-5 (N = 10069, 20231, 30347, 19753, 32869 against p = 10007, 20011, 30011, 19681, 32749; weil_job3 has N = 16187 < p - 1 = 16380 and is not covered by counting). So on those curves U cannot propagate deterministically under full translation, which puts it in **Class III (coordinate dependence)** of the c5d183 trichotomy directly, without K2. (Independent confirmation from K1/K2, both unreviewed in e3a6f1: the defect g_{R,S}(P) is a coordinate function, and U(kP) = c r_k C^{k/N} is not a function of U((k-1)P).) The candidate's own label "coordinate-dependent" agrees. This is a recorded case, not a new arithmetic.
- IDEA-20260901-863e36 (C1: propagation iff the fibre partition is a block system of the operation group; C2: translation slice = c5d183): U's fibre partition is not a coset partition, so under Sigma = translations it fails the block-system criterion. Same conclusion.
- KN-FIND-ffe1df Theorem C (exact sum-compatible combining forces a homomorphism): applies to exact quasigroup combining rules; U is a quasi-homomorphism with an unbounded F_p^*-valued defect, so Theorem C does not literally apply to it ("approximate quasigroup combining" is listed there as NOT established). It also does not matter: U does not claim to propagate. KN-FIND-ffe1df's own coverage table and Theorem A' + Weil route are the same tools C2 uses.
- KN-OPEN-020 (universal algebraic-factor-base no-go): bounded-degree bases are scoped out; the open class is high-degree, implicit-membership or target-dependent descriptions. U is a high-degree (degree N), implicit-membership (log N steps) description, so it lies in the open class on paper. C2 shows that for COMPLETE sums such a description has conductor 2 and is Weil-white. It says nothing about incomplete sums over a base of size B << sqrt(p) (the IC regime, where no theorem exists; see fd7f5d), so KN-OPEN-020 is not answered or narrowed beyond the complete-sum case.

N4 result: the pair is an instance of recorded Class III and is not an escape from any rigidity result; no new notation is needed to see this.

## Over-claims and limits to carry into the disposition (strict reading)

- O1. "Escape premises" for SO-TORS and SO-PAIR are misreadings (see escape check). C2 closes ground inside those obstructions; it does not escape them.
- O2. outcomes_to_dispositions says the generalized-Jacobian component (c8433d, the Tate pairing) is closed by C2. C2's bound is about U only. The c8433d component stands or falls on its own record (extension class = Tate pairing, trivial when gcd(N, p^k-1) excludes the l-part). It should not be credited to C2.
- O3. The Weil bound does not give the Smart-ratio statement. The event {khat = k} is sparse (null rate 1/p). A bound of the form "each Fourier coefficient is <= 2 sqrt(p)", summed over the p-1 multiplicative characters after completion of the integer-lift phase e(-jck/(p-1)), controls the success count only to O(sqrt(p) log p) out of about p targets, i.e. a success-rate bound of order log p / sqrt(p), the same order as the break-even line c/sqrt(n) named in the title of IDEA-20261016-0bacee (index row only; not opened). So the Smart-ratio arm is a measurement, not a corollary (my reading of the completion step; the candidate does not claim otherwise and says "measured at reduced scale"). Resolution of the measurement (my Poisson arithmetic, independent counts assumed, alpha = 0.01 one-sided, null mean = 1 success per curve): 3 curves in one arm (null mean 3) has power 0.54 at a 3x effect and needs a 4.35x effect for power 0.90; pooling both arms (6 curves, null mean 6) has power 0.91 at 3x; the pre-registered 30 curves per arm would reach 1.8x per arm at power 0.90. The program's own bar for this kind of null is "a resolution that could detect a 3x effect" at power >= 0.90, alpha = 0.01 (LEAD-EXO-padic-jet-canonical-lift, revisit_when and best_measured). So the per-arm reading (the e3a6f1 pre-registration) does not meet the bar; the pooled reading just meets it. Observed counts 1,2,1 and 0,0,3 (total 4 and 3) are compatible with the null either way. The measurement does exclude rates near the Weil allowance (hundreds of times null at p of about 2e4), not modest multiples of 1/p. PREDICTION (not run): a 30-curve-per-arm replication would meet the 3x bar per arm.
- O4. Multiplicative-times-group-character with constant 2 is the candidate's derivation (provenance: derived; the additive form is retrieved, GOS/Weil II recalled). It has not been checked by anyone else in this program (KN-LIT-7639 says the k > 2 case is untraced). Until reviewed it is a derivation-tier statement. The candidate's numerics (max 1.99995..1.99998 of 2, never above) are evidence for the constant on 6 curves at p <= 32749.
- O5. Scope of what is closed: character correlations of chi(U(kP)) with psi_a(k), all chi != 1, all a. The same sheaf argument covers shift-correlations such as chi(U(kP)) chi'(U((k+m)P)) psi_a(k) for fixed m (divisor still supported on a bounded number of points; conductor grows with the number of shifts). That extension is my derivation by analogy, unchecked, and the candidate does not claim it. Not covered: K2/r_k cost accounting (the sibling lead's question), the zeta-defect Z component, any extraction that is not a character correlation, and the incomplete-sum regime.
- O6. The "toy tier" caveat: p <= 32749, F_p^* logs by table, ECDLP at crypto scale untouched. predicted_gain 0 is the candidate's own.

## Heuristics (numbered; conditional)

- H-1. Weil-type character-sum bounds on a curve depend on the number of ramified points (conductor), not on the degree of the function (classical; KN-LIT-7639 states it as m = number of distinct zeros and poles). Provenance: recalled + KB. Conditional on that: every Miller-type function with a divisor supported on boundedly many points has a Weil-level white spectrum for complete sums.
- H-2. Therefore the part of "unbounded-degree statistics" (LEAD-EXO-coordinate-statistic-leakage residual class) that is not closed by character-sum arguments must have large conductor, e.g. walk itineraries or iterated maps whose divisors are supported on many points. Conditional on H-1; unverified.
- H-3. Fourier-uniformity of the graph {(k, U(kP))} cannot see sparse-event predictors between rate 1/p and about log p / sqrt(p) (O3). Break-even for full-value predictors is c/sqrt(n) (0bacee, unverified record). Conditional.
- H-4. The observed maxima just under 2 (deficit 1.7e-5 to 4.8e-5 over 2.6e6 to 8.4e6 (chi, psi) pairs per curve) are what an eigenvalue-repulsion (U(2)-type) extreme-value law predicts (deficit of order n^(-2/3)); a free-phase model would predict a far smaller deficit. This is my explanation of the candidate's number, a prediction I did not test; it would be refuted by a curve where the maximum is farther from 2 by orders of magnitude at the same sample count or above 2 anywhere.

## Verdict and routing

- verdict: advances_lead. Route it as the execution record for LEAD-TRF-miller-cocycle-nonhom-transfer next_action (H1), character-correlation half. Suggested disposition text (the coordinator's call): the U component's character arm is closed at derivation tier with toy support; the lead stays open_next_step for the Z component (IDEA-20261016-09fd08), the K2/r_k charging (LEAD-EXO-miller-pairing-cocycle) and a full-size Smart-ratio replication; the generalized-Jacobian component is not attributable to C2.
- Do not file as a new lead; do not count as a new escape of SO-TORS, SO-PAIR or SO-PADIC.
- Housekeeping suggestion: add the classical bound (Perel'muter / Kohel-Shparlinski / Weil II, support-governed) to the known-results map as a known_mechanism row and have KN-LIT-7639's "k > 2 on a curve" gap point to the étale derivation once it is independently reviewed.
