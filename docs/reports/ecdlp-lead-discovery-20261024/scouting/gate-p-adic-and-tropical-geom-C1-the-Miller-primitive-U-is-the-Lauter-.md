# Gate record: C1 Miller primitive U = Lauter-Stange perfectly periodic EDS ratio

Raw tool outputs (N1 atlas, N2 frontier map) follow, verbatim. Analysis is at the end.

## N1 run 1: lead_atlas.py --match "Miller primitive U = f_{N,P}^{1/N} equals the Lauter-Stange perfectly periodic EDS ratio phi(R-P)/phi(R)"
```
    8  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    7  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    4  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    4  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    3  LEAD-RHO-cheon-deployed-applicability        open_blocked       Where Cheon stops on deployed parameters: exact r+-1 divisor census times priced auxiliary supply
    2  LEAD-ICB-retained-setup-online               closed_dominated   Retained-setup online IC on Koblitz curves (n = 61, 71, 73, 83): online ratio after an uncharged precomputation
    1  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
    1  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
```

## N1 run 2: lead_atlas.py --match "recovering the scalar from the Miller function value is as hard as computing the elliptic divisibility sequence term"
```
   11  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
   11  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    9  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    6  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)
    6  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    3  KR-IC-8b9daa                                 known_result       Point decomposition via symmetric formulations (Karabina)
    3  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    3  LEAD-EXO-ideas-corpus-algebraic-transforms   open_blocked       ECDLP-IDEA breakthrough corpus: algebraic-geometric transforms awaiting constructors
```

## N1 run 3: lead_atlas.py --match "Somos identities hold for every k so net relations encode the group law on one k-fibre and not k; EDS association"
```
   16  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    8  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    8  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
    8  LEAD-ICP-residual-partial-relations          open_next_step     Crediting residuals as partial relations (single/double large prime) in prime-field IC
    7  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
    7  LEAD-ICB-free-relations-self-collision       exhausted_at_scale Free relations from self-collisions in the pair-root table (no-probe relations)
    6  LEAD-EXO-lossy-object-propagation            open_next_step     Lossy tracked objects propagated through scalar multiplication (doubling coordinates, rigidity, belief propagation)
    6  LEAD-ICB-tau-horner-chain                    open_next_step     tau-Horner decomposition chain on Koblitz curves (R = tau^{m-1}P_1 + ... + P_m over one base)
```

## N1 run 4: lead_atlas.py --match "elliptic divisibility sequence Lauter Stange EDS association"
```
   12  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    6  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    1  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
```

## N2 run: build_frontier_map.py --match "Miller primitive U = f_{N,P}^{1/N} equals the Lauter-Stange perfectly periodic EDS ratio phi(R-P)/phi(R)"
```
KR-IC-b0fcda  score=1  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
```

## N2 run: build_frontier_map.py --match "recovering the scalar from the Miller function value is as hard as computing the elliptic divisibility sequence term"
```
KR-IC-8b9daa  score=3  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-RHO-6654ba  score=3  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-755e35  score=2  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-RHO-13bf67  score=1  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
```

## N2 run: build_frontier_map.py --match "Somos identities hold for every k so net relations encode the group law on one k-fibre and not k; EDS association"
```
KR-IC-791cb7  score=5  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-53c89f  score=5  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-cb1c58  score=5  [known_mechanism/proven]  Simultaneous (batched) inversion
    sources: KN-LIT-e72678, KN-LIT-c75942, KN-LIT-095
KR-IC-f3da82  score=4  [known_mechanism/reported]  F4 trace reuse across many similar systems
    sources: KN-LIT-c137bd
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-755e35  score=3  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-RHO-1c2928  score=2  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
```

## N2 run: build_frontier_map.py --match "elliptic divisibility sequence Lauter Stange EDS association"
```
no row shares a term with the query -- this is NOT evidence of novelty; read the rendered map
```

## N1 extra (own phrasing): lead_atlas.py --match "perfectly periodic elliptic divisibility sequence"
```
    8  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    6  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    1  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
```

## N1 extra (own phrasing): lead_atlas.py --match "Weil reciprocity cocycle Miller function gcd(N,p-1)=1 N-th root canonical primitive"
```
   19  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
   14  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    6  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    6  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
    6  LEAD-TRF-cm-canonical-lift-heights           closed_obstructed  Serre-Tate canonical lift with CM: does the CM order shrink the heights of lifted points enough for xedni to bite?
    6  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    5  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    5  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
```

## N1 extra (own phrasing): lead_atlas.py --match "Tate pairing trivial non-homomorphic transfer into F_p^*"
```
   20  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
   15  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
   10  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    8  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    6  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup
    5  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class
    5  LEAD-TRF-second-torsion-direction            closed_obstructed  Reach a second N-torsion direction: nonequivariant trace-zero transfer, Kani/Robert graph kernels, Richelot gluing of E with E'
    4  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
```

## N1 extra (own phrasing): lead_atlas.py --match "division polynomial values psi_k(P) of a multiple kP"
```
   10  LEAD-STR-torsion-module-leak                 closed_obstructed  l-torsion (l != N) as a Galois/End module leaking k or attack cost
    5  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
    4  KR-IC-73db3f                                 known_result       Choosing the factor-base vector space V (small product spaces)
    4  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    4  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
    4  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    4  LEAD-ICB-decomposition-encoding-and-sat      closed_obstructed  Decomposition-oracle encodings and SAT/enumeration solving of binary PDP: SAT/XOR, Karabina, S_m symmetrisation, chained vs direct S_4, Nagao, basis and reduction-polynomial choice, trace replay
    4  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
```

## N1 extra (own phrasing): lead_atlas.py --match "Lauter Stange"
```
no lead or known result shares vocabulary with this idea; a low score is not novelty: read ATLAS.md by family
```

## N1 extra (own phrasing): lead_atlas.py --match "EDS Residue elliptic net discrete log"
```
   14  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    8  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    7  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    7  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
    6  KR-RHO-898783                                known_result       Interval DLP: kangaroo and Gaudry–Schost constants
```

## N2 extra (own phrasing): build_frontier_map.py --match "Lauter Stange"
```
no row shares a term with the query -- this is NOT evidence of novelty; read the rendered map
```

## N2 extra (own phrasing): build_frontier_map.py --match "perfectly periodic elliptic divisibility sequence"
```
no row shares a term with the query -- this is NOT evidence of novelty; read the rendered map
```

## N2 extra (own phrasing): build_frontier_map.py --match "Tate pairing trivial non-homomorphic transfer into F_p^*"
```
KR-RHO-53c89f  score=8  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-755e35  score=4  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-RHO-5b1c0a  score=1  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5
```

## N2 extra (own phrasing): build_frontier_map.py --match "division polynomial values psi_k(P) of a multiple kP"
```
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-1fcdbc  score=3  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=3  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-5a43e5  score=3  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-955fd6  score=3  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
```

---

# N3 raw: ledger index grep (script: scout/_gateC1_n3.py; output saved scout/_gateC1_n3.out)

```

## term /Lauter|Stange/ -> 2 index rows (title+claim+statement+mechanism, index-truncated fields)
  ids: IDEA-20261009-8d09c0, IDEA-20261009-9f89ae 

## term /perfectly periodic|periodic EDS/ -> 0 index rows (title+claim+statement+mechanism, index-truncated fields)
  ids:  

## term /divisibility sequence|EDS|elliptic net/ -> 6 index rows (title+claim+statement+mechanism, index-truncated fields)
  ids: IDEA-20260816-da106b, IDEA-20260905-24b41a, IDEA-20260920-376b00, IDEA-20261009-8d09c0, IDEA-20261009-9f89ae, H-ECDLP-753879 

## term /Miller/ -> 21 index rows (title+claim+statement+mechanism, index-truncated fields)
  ids: IDEA-20260807-5f24d7, IDEA-20260807-63ab15, IDEA-20260807-cb672c, IDEA-20260807-e7eb5d, IDEA-20260812-3182cf, IDEA-20260905-24b41a, IDEA-20261006-237ce0, IDEA-20261009-c8433d, IDEA-20261017-e3a6f1, H-ECDLP-1e5be9, H-ECDLP-4a00b8, H-ECDLP-69301c, H-ECDLP-74ecc8, H-ECDLP-84eb73, H-ECDLP-a89b28, H-ECDLP-aca677, H-ECDLP-f8cea6, H-JMV-001, H-JMV-002, H-JMV-71b222, H-JMV-c4ccf3 

## term /N-th root|N^2-th root|root section/ -> 8 index rows (title+claim+statement+mechanism, index-truncated fields)
  ids: IDEA-20260816-ec9a47, IDEA-20260818-f8dc30, IDEA-20260906-86cc17, IDEA-20261009-d2412c, IDEA-20261017-e3a6f1, IDEA-20261024-5f08bd, H-CZLIFT-d37231, H-ECDLP-7b7398 

## term /cocycle/ -> 13 index rows (title+claim+statement+mechanism, index-truncated fields)
  ids: IDEA-20260805-128f35, IDEA-20260805-6eac55, IDEA-20260807-add964, IDEA-20260808-b1358c, IDEA-20260821-3d5f22, IDEA-20260905-4b07f5, IDEA-20260905-b6ae7e, IDEA-20260905-da0612, IDEA-20261016-09fd08, IDEA-20261017-e3a6f1, H-CLGP-26d035, H-SSI-04aea1, H-SSI-c1e29a 

## term /U(kP)|r_k/ -> 4 index rows (title+claim+statement+mechanism, index-truncated fields)
  ids: IDEA-20260807-3d9c9f, IDEA-20261009-105291, H-AES-42c479, H-CZLIFT-89e169 

## intersection: (Miller|cocycle|root section|EDS|elliptic net) AND (N-th root|N^2-th|canonical section|r_k|U(kP)|periodic|Lauter|Stange|psi_)
IDEA-20260906-86cc17   proposed    'REPRESENTATION CLASS R3 (cubical and biextension lifts). ATTACK STAGE whose charged cost is claimed '
IDEA-20261009-8d09c0   proposed    '(i) the zero set of W mod p in a box is exactly a lattice of index |<P_1..P_r>| (Lauter-Stange); (ii'
IDEA-20261009-9f89ae   proposed    'The linear-complexity profile of (W_n mod p) for n <= L grows as L/2 (random profile) for L up to 10'
IDEA-20261017-e3a6f1   proposed    'E/F_p, P of prime order N, gcd(N,p-1)=1 (no pairing), f=f_{N,P} Miller function (div N(P)-N(O), moni'
H-ECDLP-753879         specified   'On y^2 = x^3 + 2 over F_11, the point P = (1, 5) has group-law order 12. The rank-1 division-polynom'
H-ECDLP-7b7398         specified   'Fix the multiplicative N^2-th-root uniqueness on F_p^* before any cubical point, division polynomial'
```

Additional index-only reads (claim text from proposals.jsonl / hypotheses.jsonl, not full records): IDEA-20261009-8d09c0 (hidden kernel lattice via elliptic nets, cites Lauter-Stange for the zero lattice), IDEA-20261009-9f89ae (period-finding on EDS mod p, cites Lauter-Stange: period = ord(P), ECDLP-equivalent), H-ECDLP-7b7398 (Stage-0 identity of IDEA-20260906-86cc17: unique N^2-th root on F_p^* when gcd(N,p-1)=1), H-ECDLP-753879 (rank-1 net, W(n)=0 iff nP=O), IDEA-20261016-09fd08 (additive analogue Z), IDEA-20261009-c8433d (generalized-Jacobian class = Tate pairing, trivial on l-parts with l not dividing p^k-1). IDEA-20261009-d2412c and H-CZLIFT-d37231 matched only the "root section" pattern and are the p-adic/Teichmuller analogue, not the same object.

Full ledger records opened (exactly 3, by exact path): ledger/proposals/IDEA-20261017-e3a6f1.yaml, ledger/proposals/IDEA-20260906-86cc17.yaml, ledger/proposals/IDEA-20260905-24b41a.yaml.

---

# ANALYSIS (all of what follows is written by this gate; raw outputs above are verbatim)

## N1 reads (top 5 of every run; lead YAML opened for each)

Runs 1-4 (+ 6 own phrasings, 12 runs in all) share a core cluster (the three Miller/EDS leads) plus lexical neighbours; the own-phrasing runs also surface further hits, all opened and listed in the 'own-phrasing top-5' bullet and the addendum below. Opened and read (mechanism, obstruction/next_action, forecloses):

* LEAD-EXO-miller-pairing-cocycle (open_next_step; top hit run 1, third in run 2, top in "Weil reciprocity" run). Mechanism: when gcd(N,p-1)=1 the N-th root U(R)=f(R)^(1/N) is the canonical primitive of the Miller cocycle and computable from R; "if U(kP) exposed k through a cheap closed form, the DLP would move to F_p^*". next_action.step: verify K1 and K2 (U(kP)=c*r_k*C^(k/N), r_k=psi_{k-1}/psi_k) exactly on toy prime-order curves with gcd(N,p-1)=1, then measure whether k is recoverable from U(kP) in fewer than sqrt(N) operations once r_k is charged. discriminates: "If K2 holds and r_k needs k (division-polynomial values), the primitive collapses into the closed elliptic-net lead and this lead closes as obstructed". forecloses include "pairing-free Miller cocycle". => C1 IS this lead's own pre-registered step and its pre-registered outcome. Same mechanism.
* LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined; run 1 #2, run 2 #1-2). Same object (U, IDEA-20261017-e3a6f1), next step is H1 (equidistribution of ell(k)=log_g U(kP), Smart-ratio, characters of Z/N). C1 does not test H1; it supplies the structural reason H1 is expected null (U is a coordinate function of R). The AUDIT.md in docs/reports/ecdlp-lead-discovery-20261024/ already records this lead as a duplicate of the EXO one (proposed closed_dominated).
* LEAD-EXO-elliptic-net-eds (closed_obstructed, kind proof; in every run). Obstruction.statement (verbatim, it has NO Scope clause): "Somos identities hold for every k, so net relations encode the group law on one k-fibre and not k (KN-FIND-002: net oracle GGM-simulable with O(log N) overhead); standard Hankel displacement rank of translated x-blocks is tautological and consecutive blocks have linear complexity >= (M-2)/3 (IDEA-006 gate). Measured at toy prime fields p in {101,431,1601}, n <= 1607: collision statistics are random-oracle-equivalent and the charged k-recovery exponent is 1.97-2.80 against BSGS 1.17-1.32 at identical accounting, with the sieve/BSGS gap growing (24x -> 135x)." revisit_when: a target-specific NONLINEAR locator outside the closed Hankel/translated-block classes, or a rank>=2 net whose relations are k-specific. forecloses: elliptic net relations for discrete log; Somos sequence sieve; short annihilator of an EDS; EDS period finding mod p; division-polynomial value collisions below birthday. This is a relation-supply/sieve obstruction. C1 is not a relation supply; it is a single-value map U. C1's closure therefore does NOT follow from this statement as written (U is a one-point map, not a net relation), and C1's own text concedes this. What C1 adds is the correct anchor: Lauter-Stange (not in this lead, not in any KR row). AUDIT.md AUD-2/AUD-6 had already proposed exactly this re-anchoring on KN-LIT-247.
* LEAD-STR-endo-scalar-action-generic, LEAD-RHO-cheon-deployed-applicability, LEAD-EXO-lossy-object-propagation, LEAD-RHO-correlated-walks-shared-sums, LEAD-EXO-ml-learned-models, LEAD-EXO-split-jacobian-projection, LEAD-ICP-residual-partial-relations, LEAD-EXO-coordinate-statistic-leakage, LEAD-ICP-construction-normal-form: opened; lexical neighbours only (score 3-8 from words like "scalar", "oracle", "propagate", "group law"). Different mechanisms; no collision. The only semantically adjacent ones: LEAD-EXO-lossy-object-propagation (open_next_step; rigidity theorem IDEA-20260807-df906f/IDEA-20260806-c5d183: no lossy single-point object propagates deterministically under the full translation action; the probabilistic regime is open) and LEAD-EXO-coordinate-statistic-leakage (open_next_step; census of coordinate statistics at random level). U is a high-degree coordinate statistic of R, so it is in the census's scope, not a new statistic class.
* Standing obstructions C1 touches (quotes, Scope clauses included):
  - SO-NET (LEAD-EXO-elliptic-net-eds): quoted above; no Scope clause exists in the row.
  - SO-PAIR (LEAD-TRF-second-torsion-direction, theorem): "Balasubramanian-Koblitz: for N || #E(F_p), N != p, E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1, i.e. the embedding degree divides k. Hence for N not dividing k, T_k(E)[N] = 0 (trace acts as [k] on the rational line), and an F_p-rational graph-type (N,N) kernel exists only when k_emb = 1; both reduce to MOV. Scope: ordinary and supersingular curves over F_p, prime N." C1 needs no second torsion direction and gains nothing from it. Not escaped, not needed.
  - SO-GEN (LEAD-EXO-augmented-oracle-ggm, theorem): "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 ... Scope: oracles, not resources (see IDEA-20260808-ea3b4f)." revisit_when: "A publicly computable oracle that is NOT GGM-simulable is exhibited (the threshold oracle ... but needs private data)." U/phi is a publicly computable field-valued oracle that reads coordinates (LS Thm 8), i.e. formally in the revisit_when class; but it is a function of kP, so it returns no information about k beyond what kP already contains. AUDIT.md X1 (unreviewed) argues the structured-GGM criterion "proves too much" for field-valued oracles; that is consistent with C1 not routing through GGM.

What C1 does that the hits' forecloses phrases do not cover: (i) the identification U(R)=c' phi(R-P)/phi(R) with the Lauter-Stange perfectly periodic normalisation (a re-expression of the canonical N^2-th-root section d(P) already in IDEA-20260906-86cc17, see N3, plus LS's name and algorithm); (ii) a theorem-level literature anchor for the "r_k needs k" step; (iii) the exact K2 check at toy size (reproduced below); (iv) a minor erratum candidate on LS eq. (4). None of these is a new attack mechanism; predicted exponent gain 0 (the candidate says so itself).

## N2 reads

* No KR row for Lauter-Stange, EDS, perfectly periodic, Miller primitive: runs for "Lauter Stange" and "perfectly periodic elliptic divisibility sequence" returned "no row shares a term"; KRMAP.md has no row matching divisib|elliptic net|EDS|Lauter|Stange|Miller|cocycle|periodic. Per the tool's own warning this is not evidence of novelty. The literature result exists in knowledge/literature/KN-LIT-247.md (citation_verified: read, key claims "as reported" from the abstract) but in no KR row (AUDIT.md AUD-2 says so too).
* Adjacent KR rows returned: KR-RHO-53c89f "Transfer attacks apply only to special curves" (MOV/Frey-Ruck/Smart; says nothing about the unreduced Miller value, U, or EDS), KR-RHO-13bf67 (generic lower bound), KR-RHO-755e35 (isogenous curves equally hard). None states C1's content. So the KR rule ("a KR hit means known_result") is not triggered, but the literature fact C1 relies on is a published theorem (LS Prop. 1 / Thm 10), see below: the reduction half is known_result in the literature, merely unregistered in the map.

## Citation verification (Lauter-Stange), provenance RETRIEVED

WebFetch https://arxiv.org/abs/0803.0728 returned: title, authors, journal ref LNCS 5381 (2009) 309-327, DOI 10.1007/978-3-642-04159-4_20, v2 revised 4 Aug 2008 "small mathematical corrections". Full text: WebFetch of https://arxiv.org/pdf/0803.0728v2 saved the PDF; extracted with pdftotext to scout/ls-src/ls.txt and page 5 rendered to scout/ls-src/pg-05.png and read as an image. Statements checked against the text (not against the candidate's summary):
1. Problem 2 (EDS Association): given P, Q=[k]P, ord(P)>=4, determine W_{E,P}(k). Theorem 1 (char != 2): ECDLP, EDS Association for NON-perfectly periodic sequences, EDS Residue for non-perfectly periodic sequences, width-3 EDS Discrete Log for perfectly periodic sequences: if any is solvable in sub-exponential time then all are. Section 4: Association is trivial for a perfectly periodic sequence (phi(Q) computable in log q time).
2. Thm 6 eq (3): phi(P) = (W(q-1)/W(q-1+ord P))^(1/ord(P)^2), for ord(P) coprime to q-1, > 3. Thm 8: phi([k]P) computable from Q=[k]P in O((log q)^3) without k. Thm 7 (Shipsey): W(t) in O((log t)(log q)^2).
3. Eq (4) as PRINTED in arXiv v2 (page 5; the LNCS version was NOT read, and v2's comment says 'small mathematical corrections' relative to v1, so the LNCS text may differ): phi([n]P) = phi(P)^(n^2-1) W_{E,P}(n). At n=1 the printed form gives phi(P)^0 * W(1) = 1, which contradicts phi([1]P) = phi(P) unless phi(P)=1, so the printed exponent is inconsistent with the definition; n^2 is consistent (and the proof's own identity W_{[l]P}(n) W_P(l)^(n^2) = W_P(nl) has the n^2 power). Ratios such as eq (6) and Prop. 1 are insensitive to the -1, which is why the slip is harmless downstream. The candidate's erratum candidate is therefore supported on paper (my check) and numerically: I re-ran scout/padic-tropical-r2/ls_eq4_check_r2.py (a 12-line script; same seeds, so this is a reproduction and not an independent implementation): phi(kP)=phi(P)^(k^2) W(k) on 150/150 for each of 4 primes p in {10007,20011,30011,16381}; the n^2-1 form 0/150. Output identical to the stored .out.
4. Thm 10 (as cited by C1) needs W(k), W(k+1), W(k+2) AND the hypothesis "phi(P) is a primitive root in F_q^*"; it then reduces k to one F_q^* DLP, probabilistic O((log q)^4) plus the DLP. C1's text omits the primitive-root hypothesis. For a RATIO such as r_k=W(k-1)/W(k) the correct pinpoint is Section 6, Proposition 1: with knowledge of any product prod W(p_i(k))^(e_i) such that t(x)=sum e_i p_i(x)^2 is a non-constant polynomial of degree <= 2, and phi(P) of order q-1, k is determined in sub-exponential time. For r_k, t(k)=(k-1)^2-k^2=1-2k. The paper's own text in Section 6 says that in its example equation "it is only their quotient that is needed". So "an r_k-from-kP oracle gives ECDLP" is literally LS Prop. 1; it is known literature, not C1's discovery.
5. Granularity: Thm 1 and Prop. 1 are sub-exponential in q (they pay one F_q^* DLP, L_q[1/3]). They show an r_k-from-kP algorithm of cost T gives ECDLP at cost T + L_p[1/3]; at 256 bits that is far below sqrt(N), so a cheap r_k oracle would be a real attack, as C1 says. They do NOT prove a lower bound on computing r_k: the closure is a reduction relative to ECDLP, not a proof that no sub-sqrt r_k algorithm exists.

## Reproduction status of C1's toy claims (what this gate saw, what it did not run)

Present in scout/padic-tropical-r2/: miller_eds_r2.py (348 lines), miller_eds_r2.out/.json, ls_eq4_check_r2.py/.out. Read the .out: six prime-order curves (p = 10007, 20011, 30011, 16381, 19681, 32749), gcd(N,p-1)=1 by construction: distinct_r1 = 1 on n_U = 9932..32564 evaluable k (U*phi(R)/phi(R-P) takes one value), K2_agree n/n on all six, D_fit equals D_pred_phiP_m2 (=phi(P)^-2) on all six (D_match true), eq4_spot 0/150 for the n^2-1 form. This gate re-ran ONLY the 12-line eq (4) check. It did not re-run miller_eds_r2.py, so the 6/6 K2 claim is "outputs inspected, not reproduced by this gate". No independent implementation was written.

## N3 decisions (what may be the same object)

* IDEA-20261017-e3a6f1 (opened): C1's parent. K1, K2 and the sentence "constructive_transforms: observable_fiber, proposed_object: EDS ratio r_k, predicted_gain: none; H1 predicts a white spectrum". C1 = execution of its Stage and confirmation of K2.
* IDEA-20260906-86cc17 (opened): the same canonical N^2-th-root section. It defines d(P)=c_N(P)^(N^(-2) mod (p-1)) (c_N=phi_N(x(P)), numerator division polynomial), the exact covariance d([m]P) psi_m(x(P))^2 = d(P)^(m^2), and the three-term identity, and pre-registers gates G1-G4 (exact identities on 200 random P/m at 16-24 bits) and the closure outcome "d(P) uniform, spectrum white, chirp exactly cancelled". LS phi(P) is the same normalisation (unique N^2-th root making the sequence N-periodic); my reading is that d(P) corresponds to phi(P)^(+-1) up to sign and W-vs-psi convention, NOT numerically checked by this gate. So C1's "phi([n]P)=phi(P)^(n^2) W(n)" (verified 600/600 by the candidate) is the same law as the 86cc17 covariance, restated in LS notation. Status of 86cc17: proposed, novelty unverified, H-ECDLP-7b7398 specified (Stage-0 only).
* IDEA-20260905-24b41a (opened): nets, cubical lifts, Miller values are one G_m-torsor object; torsor coordinate forced constant by Hom(Z/N,F_p^*)=F_p^*[N]=1 when N does not divide p-1 (T2); twist-invariant part is a rational function of the point (T3); cites KN-LIT-247. This is C1's structural content (U is a coordinate function of R) recorded on 2026-09-05.
* IDEA-20261009-8d09c0 / IDEA-20261009-9f89ae (index claims only): Lauter-Stange already invoked for EDS zero lattice / period = ord(P) ECDLP-equivalence.
* Non-ledger but decisive: docs/reports/ecdlp-lead-discovery-20261024/AUDIT.md lines 3924 (AUD-5: "K2 holds on every k -> closed_obstructed, obstruction = reduction to the EDS residue"), 5251 ("Evaluating it from (P, kP) is an EDS-association/residue-type problem; KN-LIT-247 ... reports the three EDS problems equivalent to ECDLP at sub-exponential granularity"), 5564-5585 ("Re-anchor the closure on KN-LIT-247 ... add a KR row"), 6081 (SO-NET row: "gcd(N,p-1)=1 multiplier removal = Miller primitive U"). The audit predicted the outcome C1 reports and the row C1 proposes to add. The audit's own caveats stand: K2 "unreviewed"; the audit's X2 Weil-bound derivation for character statistics of U is "this audit, unreviewed".

## What is new and what is not

Not new: the mechanism (U canonical primitive, k-dependence only through r_k, collapse into the net lead), the pre-registered outcome, the closure direction, the statement that U is a coordinate function (24b41a T3, e3a6f1 LOSSY TEST), the identity phi([n]P)=phi(P)^(n^2) W(n) in the cubical-section form (86cc17 (C)), the LS equivalence at abstract level (KN-LIT-247, AUDIT).
New (modest, bookkeeping-level): (a) exact toy confirmation of K2 and of D = phi(P)^-2 (if reproduced; this gate inspected outputs only); (b) the dictionary U(R) = c' phi(R-P)/phi(R); (c) theorem-level anchoring on LS Prop. 1 / Thm 8 / Thm 7 with the phi(P)-primitive-root hypothesis made explicit (C1's text cited Thm 10 and omitted it); (d) the eq. (4) exponent erratum candidate (supported on paper and by 150/150 vs 0/150 on 4 primes in a reproduction).

## Flags on C1's wording (conditional claims must stay conditional)

F1. "closed_obstructed(proof)" overstates. The support is a REDUCTION relative to ECDLP at sub-exponential granularity plus a toy identity. Suggested kind: reduction (to ECDLP) + measured identity; revisit_when: an r_k-from-kP algorithm (equivalently W(k), W(k-1) from kP) cheaper than sqrt(N) is exhibited.
F2. Reduction scope: needs phi(P) of order p-1 (primitive root). For phi(P) in a subgroup of order d, A=B^t(k) yields t(k) mod d only. Heuristic density of good P is phi(p-1)/(p-1); not computed here. Also char != 2 (Thm 1) and ord(P) coprime to p-1 and > 3.
F3. "All k-dependence of K2 sits in r_k" is loose: by the dictionary r_k=phi(P)^(2k-1) phi((k-1)P)/phi(kP) and C^(k/N)=phi(P)^(-2k), so U(kP)=c'' phi((k-1)P)/phi(kP) has no integer-k dependence at all; the drift in C^(k/N) cancels r_k's phi(P)^(2k). The reading "recovering k from U(kP) requires r_k" is therefore not the right logical shape: U(kP) is a function of the point kP (a coordinate), so inverting it is no easier than inverting x(kP); the content of the closure is that the other handle, the integer-indexed ratio r_k, is DLP-hard by LS. This is also why no GGM argument is needed and why SO-GEN is not the mechanism.
F4. SO-NET as written (Somos identities / relations) does not by itself apply to a one-point map; the applicable closure is LS (SO-NET's lead has LS in none of its evidence). A lead update would be a change to LEAD-EXO-elliptic-net-eds's evidence/obstruction, which the AUDIT already proposed.
F5. LEAD-TRF-miller-cocycle-nonhom-transfer's H1 (equidistribution, Smart-ratio) is not run by C1. Its closure by C1 is by the coordinate-function argument only; the AUDIT's X2 (Deligne bound on character statistics of U) is an unreviewed derivation.

## N4 notation check

(representation, operation set) pair of C1: (F_p^*-valued canonical normalisation U = c' phi(R-P)/phi(R) of the point, i.e. the N^2-th/N-th-root section of the Miller/cubical G_m-torsor; translation by S acting on U through the Miller line cocycle g_{R,S}(P)). Recorded identical pairs:
* IDEA-20261017-e3a6f1 mechanism: "PAIR: representation = F_p^*-valued canonical quasi-homomorphism U (R2, transfer); Sigma = translation by S, acting on U only through the explicit defect g_{R,S}(P). TRICHOTOMY: coordinate-dependent." Verbatim same pair and class as C1's.
* IDEA-20260906-86cc17: (cubical point with canonical section s and defect d; Sigma = cubical scalar multiplication [m]~, NOT translation), Class III. Same object under a different operation set; its law is C1's identity.
* IDEA-20260905-24b41a: (torsor point of the G_m cubical structure = net value = Miller value; Sigma = full translation lifted to the torsor), declared constant-or-injective via (T2) and IDEA-20260806-c5d183 (A) / KN-FIND-ffe1df Theorem C.
Rigidity in the new notation: U does not propagate under translation as a function of U alone (T_S(U(R)) = U(R)U(S)/g_{R,S}(P) needs R through g), so by the trichotomy of IDEA-20260806-c5d183 it is Class III (coordinate-dependent) with auxiliary state; the pair (R, U(R)) propagates deterministically but is injective (e3a6f1 LOSSY TEST: its graph is a subgroup isomorphic to E(F_p)[N], a change of coordinates). A deterministic lossy U is excluded by the orbit argument (c5d183 (A): every projection propagating under the full translation action is constant or injective; df906f: single-point rigidity). KN-OPEN-020 scopes out bounded-degree algebraic factor bases; U is a degree ~N^2 rational function of x(R) evaluated in O(log N), i.e. it sits in the open class "high-degree, implicit-membership", but C1 offers no membership or decomposition structure for it, so it neither enters nor changes that class. Conclusion: not a new arithmetic; C1's pair is a recorded Class III cell.

## Verdict

advances_lead, lead = LEAD-EXO-miller-pairing-cocycle (open_next_step). Reading: C1 is the pre-registered discriminating step of that lead executed, with the pre-registered branch ("K2 holds and r_k needs k -> collapses into the elliptic-net lead") reported. It is not a new lead and not a new mechanism (the mechanism is a duplicate of that lead, of 86cc17 and of 24b41a); the advance is (a) K2 confirmed exactly at toy size, (b) the dictionary to Lauter-Stange phi, (c) the theorem-level anchor (LS Prop. 1) in place of the abstract-level KN-LIT-247 reading, (d) a minor erratum. The disposition change C1 proposes (closed_obstructed collapsing into LEAD-EXO-elliptic-net-eds) is consistent with the lead's own rule, but the obstruction kind should be "reduction, sub-exponential granularity" not "proof", and the sub-claims in F2-F5 should be fixed. Expected exponent effect: none (candidate's own prediction; no measurement of an attack was made).

---

# ADDENDUM (after reviewer pass): lead cross-reference, completeness of N1, N3, N4

## A1. Every lead that references the object (grep -rl "e3a6f1|primitive U|Miller|canonical primitive|canonical section|Teichm|torsion section|s_tor" knowledge/leads/ecdlp/)
Files: LEAD-EXO-miller-pairing-cocycle, LEAD-TRF-miller-cocycle-nonhom-transfer, LEAD-EXO-padic-jet-canonical-lift, LEAD-TRF-padic-canonical-section, LEAD-EXO-torsor-deck-period, LEAD-STR-jmv-random-self-reduction (the "Miller" there is Jao-Miller-Venkatesan, a different object), coverage.tsv.

* LEAD-EXO-torsor-deck-period (closed_obstructed, kind proof; this is standing obstruction SO-DECK, which C1 did not list). It is the closed lead whose scope contains C1's object. forecloses: 'torsor deck-orbit descent', 'cubical lift of the prime-order subgroup', 'biextension label of the target', 'scalar-orbit elliptic period', 'theta-structure linearisation of translation'. ledger_refs include IDEA-20260906-86cc17, IDEA-20260920-376b00, IDEA-20260905-24b41a, H-ECDLP-7b7398; evidence note for 24b41a: "Nets, cubical lifts, Miller functions and dual-number lifts as one torsor object". obstruction.statement (verbatim, it has NO Scope clause): "For a generically Galois cover every rational deck-invariant factors through the quotient; a transitive fibre-orbit label is base data; a connected nontrivial cover has no rational section, so a rational target-compatible selector is a missing section or trivialization (IDEA-010 gate, independently verified). The cubical/biextension lift lands on the invertible side of the recognizable/invertible duality, i.e. computing its label costs the log (IDEA-20260920-376b00)." mechanism of that row: place the instance on a G_m/G_a-torsor and use deck-orbits or a period as a public label routing the target to a small fibre. C1 does not escape this row and does not claim to; it uses the same object (N^2-th-root canonical section of the cubical G_m-torsor = LS phi = 86cc17's d) and reaches the same verdict (no usable handle). C1's use (U as an F_p^*-valued transfer value) differs from the row's use (deck-orbit label for routing), and the row's evidence never mentions the unreduced Miller primitive U or the EDS ratio r_k, which is why the open Miller lead was not considered covered. Net: C1's object sits inside a closed family; its escape premises should have listed SO-DECK.
* LEAD-TRF-padic-canonical-section (closed_obstructed, theorem; SO-PADIC), obstruction.statement verbatim: "For p not dividing #E(F_p) the only homomorphic section is the prime-to-p torsion section, which the formal logarithm kills (log vanishes on torsion), exactly as log_p kills the Teichmuller section of F_p^*; any non-homomorphic section recovers d only at the random 1/p rate. Toy runs (p < 2000 and 10^4..10^5) met the frozen criteria; the only failure (naive F_p^* section) is a size effect for g^d < p, not a p-adic one. Scope: non-anomalous prime-field curves, all lifts of E." forecloses: canonical point lift to E(Q_p), p-adic digits of the torsion section, Teichmuller section for elliptic curves, formal logarithm on non-anomalous curves, Hensel lift section. Its objects are sections E(F_p) -> E(Q_p) with additive/formal-group digits; U is an F_p^*-valued (multiplicative) section value on E(F_p). So U is not within its forecloses or Scope. AUDIT.md notes the clause "any non-homomorphic section recovers d only at the random 1/p rate" is false as worded (DEC-20261024-23d64d, per the audit's cross-family observation), so this row's closure is itself under revision; not a support for C1.
* LEAD-EXO-padic-jet-canonical-lift (closed_obstructed, proof; SO-PADIC family), statement (verbatim, Scope included): "For gcd(n,p)=1 the prime-to-p torsion lifts uniquely (finite etale) with zero formal defect and multiplication by l is invertible on every native jet, formal and p-typical target, so every additive order-l image is zero (IDEA-004 gate, independently verified); jet oracles are GGM-simulable with O(1) overhead (KN-FIND-002). The digit identity d(mS^)=m*d(S^) holds only on the HARD global lift (1360/1360 exact, KN-FIND-85845f), whose cost is the lift itself; the computable Teichmuller-style contrast reads as chance under a resolution-matched repaired test (KN-FIND-e8cfdc); IDEA-436 D1 valuation profile collapses to the +/- fibre indicator (KN-FIND-1ba0fe). Scope: ordinary prime-field curves, toy primes 10-14 bits for the measured parts." Additive prime-to-p lifts and formal digits; not the multiplicative Miller primitive.
* Consequence for the candidate's field_key: C1 contains no p-adic or tropical structure. The p-adic analogue of its object (Teichmuller/torsion section; additive) is closed by the two rows above and by H-CZLIFT-d37231 (rejected); the F_p^*-valued analogue is U. The AUDIT table row for SO-PADIC says this line "generates U, Z, s_tor; U provably flat (X2)", with X2 an unreviewed derivation. So the field_key is nominal; the p-adic closed rows do not cover U by their forecloses/Scope, hence they do not make C1 a duplicate of them.

## A2. Own-phrasing top-5 hits not previously opened (now opened, one line each)
* LEAD-ICP-self-pairing-prime-order (closed_obstructed, theorem): "On a cyclic group of prime order N every bilinear map is determined by h = b(P, P) ... t_N(P, P) in mu_N intersected with the base field, trivial above embedding degree 1. Scope: prime-order subgroups of E(F_p) with embedding degree > 1." Adjacent: it closes bilinear maps; U is a quasi-homomorphism with a nonzero defect cocycle, not bilinear, so it is outside the row's mechanism; consistent with C1 (no pairing in the gcd(N,p-1)=1 cell).
* LEAD-TRF-mov-small-embedding-degree (closed_known, literature): MOV/Frey-Ruck; "Scope: ordinary and supersingular curves over any finite field". C1 lives in the k > 1 cell where the reduced pairing is trivial; adjacent, not the same.
* LEAD-EXO-dl-character-sum-pseudorandom (exhausted_at_scale, measured): additive-character sums of the DL over the small-x set measured R = C_EC/C_null about 1.28-1.34 (flat) at 2^20-2^26. Relevant to H1-type character statistics but over a different set and function; does not cover U.
* LEAD-STR-torsion-module-leak (closed_obstructed, proof; SO-TORS): statistics of psi_l for fixed l != N; "Scope: prime-order G, any l != N". C1 uses psi_n at integer index n = k (not a fixed-l torsion statistic); adjacent only.
* LEAD-EXO-invertible-hint-subset (open_next_step): hint family of subsets with cheap membership and cheap logs; the recognizable/invertible duality cited by SO-DECK's statement. U is a coordinate function, not a hint family; adjacent only.
* LEAD-TRF-cm-canonical-lift-heights (closed_obstructed, cost_model): CM canonical lift heights; unrelated to U.

## A3. N3 completion: same-object records (id + claim) 
* IDEA-20260920-376b00 [index claim, not opened as a 4th record]: "THE CUBICAL / BIEXTENSION LIFT LANDS ON THE INVERTIBLE SIDE OF THE DUALITY ... its only Sigma-compatible invariant is the Tate pa[iring]" (R3; cited by LEAD-EXO-torsor-deck-period as the basis of its cubical clause). Same G_m-torsor object as 86cc17/24b41a. C1's object, so its closure statement is already filed under SO-DECK.
* IDEA-20260901-863e36 [index claim, not opened]: propagation is a property of a (projection, operation group) PAIR with Gamma subgroup of (Z/n)^* acting by R -> [gamma]R, tracked object the Gamma-orbit. That is the operation-set formalism of 86cc17 (Sigma = [m], m in (Z/N)^*, composed with renormalisation); C1's eq (4) identity phi([n]P) = phi(P)^(n^2) W(n) is the statement for that operation set, propagating only with the auxiliary W(n) = psi_n(P) (escape E2 of IDEA-20260807-df906f, priced by H-PROP-c95932 per 86cc17).

## A4. N4 completion
* IDEA-20260901-863e36: C1 has two operation sets: translation (K1, the e3a6f1 pair) and scalar multiplication [n] (eq (4), the 86cc17/863e36 Gamma-pair). In both, the object is Class III with auxiliary state: translation needs g_{R,S}(P) (a function of R), scalar multiplication needs W(n)=psi_n(P). Rigid under c5d183 (A): a deterministic propagator under the full translation action is constant or injective.
* KN-OPEN-020 (knowledge/open-problems/KN-OPEN-020.md; status open, confidence unverified), scope quoted from the file: bounded-degree theorem is a scoped negative; "'Algebraically defined' can include high-degree interpolation descriptions, multiple constructible predicates, target-dependent descriptions, and implicit membership or source-recovery algorithms. A generic-group lower bound does not cover those concrete curve-structure interfaces". U/phi is a degree ~N^2 rational function of x(R) evaluated in O(log N) (a high-degree description computable by the Shipsey ladder, LS Thm 7/8). C1 neither supplies a membership/source-recovery algorithm for a factor base on it nor claims one, so it does not touch the open class; U is merely an instance of it that C1 shows to be a coordinate function of R. KN-FIND-ffe1df Theorem C (quasigroup combining rules for Wagner trees, file section "O2_quasigroup_gap") and IDEA-20260806-c5d183 (A) are the rigidity statements; C1 is not an escape from either (it claims none).

## A5. Verdict, final (supersedes the Verdict paragraph above where they differ)

advances_lead, lead = LEAD-EXO-miller-pairing-cocycle, with these stated limits:
1. Mechanism-level: duplicate. Every ingredient is already recorded: U and K2 (IDEA-20261017-e3a6f1, the open lead's own next_action and discriminates clause), the N^2-th-root canonical section with the exact covariance law (IDEA-20260906-86cc17, inside closed LEAD-EXO-torsor-deck-period, whose forecloses include 'cubical lift of the prime-order subgroup'), the torsor-coordinate-is-trivial/coordinate-function argument (IDEA-20260905-24b41a), the Association/Residue equivalence at abstract level (KN-LIT-247, AUDIT.md). C1 does not escape SO-DECK, SO-NET (as the row is worded) or SO-PAIR, and it claims no escape. It also lists no SO-DECK in so_codes_touched; it should.
2. What is advanced: the open lead's pending step is executed (K2 and D = phi(P)^-2 on six prime-order curves, per the candidate's saved outputs; this gate inspected them and re-ran only the 12-line eq (4) script, which imports the candidate's own module and is therefore not independent), the dictionary U(R) = c' phi(R-P)/phi(R) connects the open lead to 86cc17's d(P), and the reduction step is pinned to LS Prop. 1 (Section 6) rather than Thm 10. The LS reduction itself is known literature absent from the KR map.
3. Conditional claims to keep conditional: reduction at sub-exponential granularity, needs phi(P) of order p-1, char != 2, ord(P) coprime to p-1 and > 3; no lower bound on r_k; closure kind should be 'reduction' not 'proof'.
4. If the harness treats closing an object that already lies in a closed family as a duplicate, the nearest closed lead is LEAD-EXO-torsor-deck-period; the open lead is the one whose state C1 changes, hence advances_lead.
5. The field_key (p-adic and tropical) is nominal; C1 uses neither, and the p-adic closed rows (LEAD-TRF-padic-canonical-section, LEAD-EXO-padic-jet-canonical-lift) neither cover nor are covered by it.
