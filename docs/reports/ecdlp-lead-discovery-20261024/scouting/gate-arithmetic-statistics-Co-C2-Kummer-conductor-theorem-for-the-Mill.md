# Novelty gate N1-N4: candidate C2 (field_key: arithmetic statistics)

Candidate: C2. Kummer-conductor theorem for the Miller primitive U = f_{N,P}^{1/N}: the Lang-torsor
character tensored with the Kummer sheaf of f has conductor 2, so every character correlation is <= 2 sqrt(p).
Bottleneck B7 (LEAD-TRF-miller-cocycle-nonhom-transfer; U-part of LEAD-EXO-miller-pairing-cocycle).

Gate run: 2026-10-25, tools from /Volumes/SSD990-2/crypto-autoresearcher with the three LEAD_ATLAS_* variables exported.
Nothing inside the repositories was edited. All work files are under this scout/ directory
(private work dir: scout/gate-C2-work/, from which every raw output pasted below is taken).
DISCLOSURE: early in this gate I wrote my first batch of --match outputs (limit 8) to scout/raw/atlas_{1..4}.txt and scout/raw/kr_{1..4}.txt before noticing the
directory is shared; files with those names there now hold another run's content for atlas_1..4 (and I may have overwritten that run's files at those eight paths).
I stopped using scout/raw/ at once; the orchestrator should check those eight paths. I also wrote scout/raw/miller_u_spectrum_v2.myrerun.{out,err} and miller_u_time.txt (my own rerun).

## VERDICT (summary; details and reasons below)

verdict = advances_lead; lead = LEAD-TRF-miller-cocycle-nonhom-transfer (open_unexamined), with the U-part of
LEAD-EXO-miller-pairing-cocycle (open_next_step).

* Same object, same question, same discriminator as the lead's own next_action (H1 of IDEA-20261017-e3a6f1):
  "correlation with characters of Z/N" of ell(k) = log_g U(kP). C2 turns the lead's toy
  measurement into a theorem for that clause (a proof route plus a replay). It is a sharper next step for an OPEN lead,
  not a new lead and not an escape from any standing obstruction (it is a closure candidate, predicted gain 0).
* It is NOT a KR duplicate: no KRMAP row states a character-sum / conductor bound for the Miller primitive or for
  group-character-twisted Kummer sums on E(F_p). But the technique is the Perel'muter / Kohel-Shparlinski / Weil-Deligne
  family, and the program's own KN-LIT-7639 + KN-FIND-ffe1df already carry the untwisted multiplicative form
  (2g-2+2m) sqrt(p) with m = number of distinct zeros and poles (degree-free). Having read both records (see the next bullet and N3), what is new is
  only: the COMBINATION of IDEA-20260905-b6154d (B)'s Lang-torsor twist and nontriviality criterion with KN-LIT-7639 (H1)'s degree-free zero/pole count, its instance
  F = f_{N,P} with gcd(N,p-1) = 1 (m = 2, deg ~N), the constant 2 instead of (H1)'s 4, the relocation of the (D2) break, and the replay.
* The Lang-torsor (x) Kummer mechanism itself is NOT new to the program: it is IDEA-20260905-b6154d (B) (proposed, unverified proof map,
  mapped to LEAD-EXO-coordinate-statistic-leakage), which bounds |g^(a)| by c*deg*sqrt(p), puts Miller-type functions outside its class and calls them "the door
  that remains". C2's delta is the degree-free tame-conductor count (2 instead of deg f = N; the count itself is KN-LIT-7639 (H1)'s) that moves the Miller function through that door for multiplicative characters
  of f, plus the constant 2, plus the replay. It also trips b6154d's own falsification clause: b6154d predicts that on (D2) "the break is ... at the bounded-degree step. A break elsewhere, or no break,
  falsifies the derivation as written"; with the degree-free count the (D2) break (N | p-1) is at the sheaf-nontriviality step (div f = 0 mod N makes the Kummer sheaf unramified), not at a degree step. The candidate's "absent from the ledger" is true of the words only (the index truncates bodies; see N3).
* The candidate's outcome (a) (close the lead as closed_obstructed) overreaches: C2 discharges the multiplicative-character (Z/N spectrum) clause of H1, not the
  Smart-ratio / 1/p clause, the cocycle three-point correlation, the K2/EDS route, zeta-defect or generalized-Jacobian sublines. Correct disposition: open_next_step with that clause closed by theorem.
* Replay accuracy: max|S| exceeds 2 sqrt(p) by about 1.94-1.97 and passes only via the +2 allowance for the two unevaluated points R = +-2P; the replay is consistent with the bound and
  shows the constant 2 is attained from below (>= 1.9994 sqrt(p)), but does not test the upper constant sharply.
* Claims I could not confirm: the exact Kummer x group-character statement is not located in a retrieved source (only the
  additive x group-character Kohel-Shparlinski form, and the GOS formula on P^1, were read). The proof sketch is sound as
  I re-derived it (see N4/verification), but it is a derivation, not a retrieved theorem.
* Still open after C2 (and so must stay open in any disposition): the single-value Smart-ratio clause (probability 1/p
  events are far below the 2 sqrt(p) noise floor), the cocycle bispectrum (a different sheaf, on E x E), the K2/EDS route,
  zeta-defect and generalized-Jacobian sublines.

## N1  Atlas collision (raw outputs, verbatim)

```
$ python3 tools/lead_atlas.py --match "Kummer sheaf of the Miller function tensored with the Lang-torsor character, conductor bound" --limit 10
   12  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    8  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    6  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    4  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    4  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
    4  LEAD-STR-koblitz-volcano-descendants         closed_obstructed  Curves below a binary Koblitz curve in its volcano (ECC2K-130, K-163, K-283, m=37..83)
    4  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
    3  KR-IC-8b9daa                                 known_result       Point decomposition via symmetric formulations (Karabina)
    3  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    3  LEAD-EXO-coordinate-statistic-leakage        open_next_step     Coordinate-statistic hunts: bias of x/y, slopes, bits, cross-ratios and trace functions under the group law
```

```
$ python3 tools/lead_atlas.py --match "the Miller-function transfer into F_p^* is uncorrelated with the discrete log" --limit 10
   10  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    9  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    8  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    7  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    7  LEAD-EXO-ml-learned-models                   open_next_step     Machine learning / neural and RL approaches to ECDLP and its subroutines
    7  LEAD-RHO-lhw-polymem-collision-walks         open_next_step     Low-Hamming-weight DLP with polynomial memory: collision walks on the weight-w class
    6  KR-RHO-898783                                known_result       Interval DLP: kangaroo and Gaudry–Schost constants
    6  LEAD-EXO-elliptic-net-eds                    closed_obstructed  Elliptic nets / elliptic divisibility sequences as a relation or annihilator source
    6  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
```

```
$ python3 tools/lead_atlas.py --match "non-homomorphic transfer into F_p^* recovers the log only at the random rate" --limit 10
    8  LEAD-TRF-miller-cocycle-nonhom-transfer      open_unexamined    Non-homomorphic transfers into F_p^* when the pairing is trivial: Miller-cocycle primitive U, zeta-defect, generalized Jacobians
    7  KR-RHO-53c89f                                known_result       Transfer attacks apply only to special curves
    6  LEAD-ICP-self-pairing-prime-order            closed_obstructed  Nondegenerate self-pairings or bilinear maps on a prime-order E(F_p) subgroup
    6  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    6  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
    5  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    5  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    5  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    5  LEAD-STR-jmv-random-self-reduction           closed_known       Jao-Miller-Venkatesan isogeny-expander random self-reduction within a level
    5  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class
```

```
$ python3 tools/lead_atlas.py --match "Weil bound on multiplicative character sums of a rational function over E(F_p) twisted by a character of the group, square-root cancellation independent of degree" --limit 10
   14  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   12  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
   12  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
   11  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   10  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
    9  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
    9  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    9  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    8  LEAD-ICP-representation-subset-sum           closed_obstructed  Representation technique (Howgrave-Graham-Joux style) on the base-B digit subset-sum form of ECDLP
    8  LEAD-TRF-mov-small-embedding-degree          closed_known       MOV / Frey-Rueck pairing transfer of the ECDLP to F_{p^k}^* for small embedding degree k
```

```
$ python3 tools/lead_atlas.py --match "coordinate function character correlation with discrete log Weil bound bounded degree" --limit 10
   15  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   14  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   13  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
   12  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   11  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   10  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
   10  LEAD-EXO-hnp-advice-leakage                  open_blocked       Bit-security / hidden-number conversion of DL leakage, auxiliary inputs and advice
   10  LEAD-EXO-miller-pairing-cocycle              open_next_step     Miller functions, S-unit descent and pairing-free Miller cocycles on prime-order curves
    9  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    9  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
```

Phrasings 1-3 are the candidate's match_phrasings; phrasings 4 and 5 are my own (4: Weil bound / group-character twist / degree-free; 5: coordinate-function DL character correlation, bounded degree).
The limit-10 reruns pasted here supersede my first limit-8 batch (same ranking; only the cut-off differs).
Hits of run 5 not discussed above: KR-IC-fbdb61 and KR-IC-f5c584 (Weil descent, lexical; read in N2), LEAD-ICB-prime-degree-algebraic-decomposition (bounded-degree algebraic decomposition at prime extension degree, binary Weil descent; lexical on 'Weil' and 'bounded degree', no U), LEAD-EXO-hnp-advice-leakage (read: conversion of a statistic into key recovery; C2 gives no measured nonzero advantage, so it feeds nothing there), KR-IC-889857 (disputed first-fall-degree claim, binary).

### N1 reading notes (top-5 of every run opened; lead YAML mechanism + obstruction + forecloses read)

| run | rank | hit | disposition | relation to C2 |
|---|---|---|---|---|
| 1,4 | 1-2 | LEAD-EXO-miller-pairing-cocycle | open_next_step | SAME MECHANISM for the U-part. Its mechanism sentence is exactly "the N-th root U(R)=f(R)^(1/N) is a canonical primitive ... if U(kP) exposed k through a cheap closed form, the DLP would move to F_p^*". forecloses: "Miller function S-unit descent; pairing-free Miller cocycle". C2 is a statement about that U. Its next_action (K1/K2 on toy curves, then k-recovery cost) is the K2/EDS route; C2 does not touch K1/K2 and says so. |
| 1,3 | 2,1 | LEAD-TRF-miller-cocycle-nonhom-transfer | open_unexamined | SAME MECHANISM. next_action = "equidistribution of ell(k)=log_g U(kP) in Z/(p-1), Smart-ratio success and correlation with characters of Z/N, on special and matched random p, with planted-structure positive control"; discriminates: "Equidistribution at the 1/p rate closes the lead ...; any character correlation would be the first one-point transfer signal". forecloses: Miller function transfer; unreduced Tate pairing value; zeta defect quasi-homomorphism. C2 proves the 'characters of Z/N' clause (and the Kummer-mode equidistribution of ell mod every e | p-1, at the 2 sqrt(p) scale) instead of measuring it. => advances_lead. No obstruction row exists on this lead (open_unexamined), so there is no Scope clause to quote; the lead's evidence rows are IDEA-20261017-e3a6f1, -c8433d, -09fd08. |
| 1 | 3 | LEAD-EXO-curve-model-representation | closed_obstructed | Lexical ('Kummer' = Kummer line/surface, a different object). Obstruction (measured, d_reg=2 model-invariance; Kummer line Bezout-optimal) is about summation-polynomial degree under change of curve model. C2 does not change the model. No overlap. |
| 1 | 4 | LEAD-RHO-matched-rho-calibration | open_next_step | Lexical. Rho reference calibration. No overlap. |
| 1 | 5 | LEAD-STR-isogeny-class-generic-invariance | closed_obstructed | SO-ISO. theorem: "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group." C2 is a spectral statement about one coordinate function on a fixed curve, no isogeny transport. No overlap. |
| 2 | 1 | LEAD-EXO-dl-character-sum-pseudorandom | exhausted_at_scale | ADJACENT, not the same. Sum over the small-x SET F (|F|=B << N) of an additive character of DL; C2 is a sum over the WHOLE group of (Kummer character of a Miller value) x (additive character of DL). KN-FIND-e7a3b1 closes the Weil route for H-PSEUDO because the indicator of {x<t} is not algebraic; C2's weight chi o f IS algebraic with divisor support 2, so the objection does not bite. C2 therefore does not reopen H-PSEUDO, and H-PSEUDO's closure does not cover C2. Obstruction.statement (measured; no Scope clause present): "R = C_EC/C_null is flat at about 1.28-1.34 ... all six standard analytic proof routes are closed (KN-FIND-e7a3b1)". |
| 2,3 | 3,4 | LEAD-STR-safecurves-parameter-audit | closed_known | Lexical (transfer rows). No overlap. |
| 2 | 5 | LEAD-EXO-invertible-hint-subset | open_next_step | Different: dense subsets with cheap logs, degree-d polynomial agreement with log graph. C2's chi o U is not a hint family (its Fourier spectrum is flat at 2 sqrt(p)). No overlap. |
| 3 | 3 | LEAD-ICP-self-pairing-prime-order | closed_obstructed | theorem: "On a cyclic group of prime order N every bilinear map is determined by h = b(P,P) ... Galois equivariance puts t_N(P,P) in mu_N intersected with the base field, trivial above embedding degree 1. Scope: prime-order subgroups of E(F_p) with embedding degree > 1." U is non-bilinear, non-homomorphic; this obstruction does not cover it and C2 does not claim to escape it (U is the non-bilinear primitive of the trivial pairing's cocycle). Adjacent. |
| 3 | 5 | LEAD-TRF-mov-small-embedding-degree | closed_known | literature; embedding degree is a class invariant. C2's control cell is the k_emb = 1 (N | p-1) case where the reduced Tate character is alive. Adjacent, no overlap. |
| 4 | 3 | LEAD-ICP-algebraic-membership-factor-base | closed_obstructed | theorem: "A target-independent algebraic locus of degree d yields O(d) usable points ... mean per-target yield is binomial(B+m-1, m)/N for every base of size B ... Scope: prime-order E/F_p, any base of size B." If anyone turned chi o U into a factor base D={R: chi(U(R))=1} (a high-degree implicit-membership base, the open class of KN-OPEN-020) this conservation row applies to it unchanged (SO-ALGFB). C2 itself proposes no factor base. |
| 4 | 5 | LEAD-ICP-digit-presentation-solving-degree | open_next_step | Lexical ('Weil descent'). No overlap. |
| extra | run 1, rank 10 (score 3) | LEAD-EXO-coordinate-statistic-leakage | open_next_step | NEAREST STRUCTURAL NEIGHBOUR outside the top 5. Its next_action ends with "random-level lambda for it closes the natural-statistic registry, leaving only unnatural (unbounded-degree) statistics"; best_measured: "every stable multiplicative coset statistic sits at the random level". U is an unbounded-degree (degree N) multiplicative-character coordinate; C2 supplies a proof for one family of exactly that kind, with a degree-free constant. This is a second lead C2 advances (registry side), not a duplicate. |

Does the candidate do something the hits' forecloses phrases do not cover? Against LEAD-TRF-miller-cocycle-nonhom-transfer and
LEAD-EXO-miller-pairing-cocycle: no. "Miller function transfer", "unreduced Tate pairing value" and "pairing-free Miller cocycle"
cover it. What C2 adds is the METHOD (a conductor count) in place of the lead's planned measurement.

Quoted standing-obstruction statements the candidate cites were checked verbatim against the YAML rows
(LEAD-TRF-second-torsion-direction, LEAD-TRF-padic-canonical-section, LEAD-EXO-augmented-oracle-ggm, LEAD-EXO-elliptic-net-eds):
the candidate's quotations match, ellipses included. C2 answers none of them by escape: it is a closure statement
(tier X, predicted gain 0), so "escape_premises" is bookkeeping. The lead row LEAD-TRF-miller-cocycle-nonhom-transfer has no
obstruction block yet.

## N2  Known-results map (raw outputs, verbatim)

```
$ python3 tools/build_frontier_map.py --match "Kummer sheaf of the Miller function tensored with the Lang-torsor character, conductor bound" --limit 10
KR-IC-8b9daa  score=3  [known_mechanism/reported]  Point decomposition via symmetric formulations (Karabina)
    sources: KN-LIT-327949
KR-RHO-6654ba  score=3  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-13bf67  score=2  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-ea34b8  score=2  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-0d2021  score=1  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-RHO-1c2928  score=1  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-93979e  score=1  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
KR-RHO-cd0049  score=1  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
```

```
$ python3 tools/build_frontier_map.py --match "the Miller-function transfer into F_p^* is uncorrelated with the discrete log" --limit 10
KR-RHO-46c2c6  score=9  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-ea34b8  score=8  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-898783  score=6  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
KR-RHO-53c89f  score=5  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-13bf67  score=3  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-755e35  score=3  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
KR-IC-64659b  score=1  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-889857  score=1  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
```

```
$ python3 tools/build_frontier_map.py --match "non-homomorphic transfer into F_p^* recovers the log only at the random rate" --limit 10
KR-RHO-53c89f  score=7  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-46c2c6  score=3  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-6239aa  score=3  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-RHO-755e35  score=3  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-RHO-898783  score=3  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
KR-IC-081a58  score=2  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=1  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

```
$ python3 tools/build_frontier_map.py --match "Weil bound on multiplicative character sums of a rational function over E(F_p) twisted by a character of the group, square-root cancellation independent of degree" --limit 10
KR-IC-f5c584  score=14  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-fbdb61  score=11  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5ea2f8  score=7  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-e2d81b  score=7  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-791cb7  score=6  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-13bf67  score=6  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-0d2021  score=5  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-73db3f  score=5  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-889857  score=5  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
```

```
$ python3 tools/build_frontier_map.py --match "coordinate function character correlation with discrete log Weil bound bounded degree" --limit 10
KR-IC-fbdb61  score=15  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-f5c584  score=11  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-ea34b8  score=10  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-IC-889857  score=9  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-RHO-46c2c6  score=9  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-IC-5ea2f8  score=7  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-e2d81b  score=6  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
KR-RHO-898783  score=6  [known_bound/proven]  Interval DLP: kangaroo and Gaudry–Schost constants
    sources: KN-LIT-086517, KN-LIT-17fc11, KN-LIT-70aa30, KN-LIT-f466f7, KN-LIT-f7558f, KN-LIT-264e34
KR-IC-0d2021  score=5  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
```

### N2 reading notes

No row of the map states a character-sum, conductor, Weil-Deligne, Kummer or Lang-torsor bound for Miller values or for
group-character-twisted sums on E(F_p). `grep -i "character|Weil bound|Kummer|Shparlinski|Miller|Lang|sheaf|Deligne|cocycle"`
over KRMAP.md hits only KR-IC-5ea2f8 (GHS Weil descent), KR-IC-1fcdbc (char 2 summation) and KR-IC-cd159a (xedni/lifting).

* KR-RHO-53c89f (textbook_fact/proven) "Transfer attacks apply only to special curves": adjacent. It states that MOV/Frey-Ruck need small
  embedding degree and Smart needs trace one; it does not state or imply a spectrum bound for a non-homomorphic F_p^*-valued map.
* KR-RHO-13bf67 (generic lower bound), KR-RHO-ea34b8, KR-RHO-46c2c6, KR-RHO-755e35: lexical or generic-adjacent; no content on U.
* KR-IC-f5c584 and KR-IC-fbdb61: 'Weil descent' lexical hits; the trace morphism E -> F_2 is a GROUP homomorphism, the opposite of U.
* KR-IC-5931ee / KR-IC-cd159a: not matched here; cd159a is the SO-XEDNI / lifting cousin of the p-adic obstruction.

=> No KR hit, so known_result is not forced by the map. Outside the map, the technique is classical (recalled/retrieved list below), and
the candidate's own self_kill_risk line concedes this. I therefore state exactly what is new in the verdict reason rather than claiming novelty of the method.

## N3  Ledger dedup

Method. `grep -i` over ledger/.index/proposals.jsonl and hypotheses.jsonl (and experiments.jsonl for runs). LIMITATION found during this gate:
the index truncates `claim`/`mechanism` to about 200 characters, so a lexical miss in the index says nothing about the body of a record.
The candidate's "Lang torsor / Grothendieck-Ogg returned 0" is true of the index (I reproduced 0/0) and is NOT evidence of absence: the record
IDEA-20260905-b6154d carries the same sheaf argument in the body, as "Lang(chi_a)" and "Weil-Deligne", words the greps did not contain.

Term counts (proposals/hypotheses): Lang torsor 0/0; Grothendieck 0/0; Kohel-Shparlinski 0/0; Kohel 2/0 (CM conductor, unrelated);
Shparlinski 1/1 (ECDSA HNP lattices, unrelated); Deligne 0/1; sheaf 0/1; Weil bound 1/0; character sum 4/8; Kummer 24/12 (almost all Kummer line/surface);
conductor 32/19 (CM conductor / solving-degree); Miller 9/12 (hypotheses: eight Stage-0 'Fix the exact ...' identity records, three Jao-Miller-Venkatesan records where Miller is an author, and H-ECDLP-f8cea6); cocycle 10/3; zeta-defect 1/0;
Smart ratio 2/0; N-th root 4/0 (unrelated except e3a6f1); 'perel' hits are 'hyperelliptic' (noise). experiments.jsonl: 0 hits for e3a6f1, Miller cocycle,
miller_u, N-th root => the lead's H1 test has NOT been run anywhere in the ledger.

Hits that may be the same object (id | status | claim, about 100 chars):

| id | status | claim | verdict on identity |
|---|---|---|---|
| IDEA-20261017-e3a6f1 | proposed, unverified | "The Miller cocycle has a canonical primitive U: E(F_p)[N] -> F_p^* exactly when N does not divide p-1: a non-homomorphic transfer into F_p^*" | SAME OBJECT. Source of the lead. H1 = "uncorrelated with characters of Z/N"; its own rigorous_support reads "character sums of such terms are bounded in the recalled literature (unread)". C2 is the discharge of that clause. (opened in full, #1 of 3) |
| IDEA-20260905-b6154d | proposed, unverified | "THE WALL, MADE EXACT, AND THE TWO DOORS IN IT: for a bounded-degree coordinate function ... every discrete-log character correlation is at the Weil level c*deg*sqrt(p)" | SAME SHEAF MECHANISM, different (smaller) class. See below. (partial read, disclosed) |
| IDEA-20261016-0bacee | proposed, unverified | "Break-even line for full-value section predictors: Smart-ratio success rate rho beats the rho algorithm only above c/sqrt(n), where the Weil allowance does not..." | ADJACENT. Uses the recalled Kohel-Shparlinski ceiling rho_W ~ C k log n / sqrt(p) for additive degree-k defect functions and concludes "Weil does not exclude a break-even section". Bounds C2's reach: Weil-scale control cannot exclude single-value events at rate near 1/sqrt(n). (opened in full, #2 of 3) |
| IDEA-20260829-4b34c5 | proposed, unverified | "Replace the order-theoretic accepted set by a multiplicative subgroup of F_p*, and use bilinear character sums over elliptic curves ..." | TECHNOLOGY NEIGHBOUR, other object (chi(x(R_i+S_j)), bilinear Ahmadi-Shparlinski sums, join rectangles). No U, no Lang torsor. (opened in full, #3 of 3) |
| IDEA-20261016-8961d2 | proposed (index only) | "Exact census of a whole section class: Smart-ratio success over every defect function in L(kO) is k-wise independent with exact moments" | ADDITIVE cousin (p-adic section defects f in L(kO)); not U. |
| IDEA-20261016-09fd08 | proposed (index only) | "The zeta-defect Z: a lift-free canonical quasi-homomorphism on E(F_p)[n] whose carry is a division-polynomial log-derivative" | ADDITIVE primitive; the Artin-Schreier subline C2 itself says it does not cover. |
| IDEA-20261009-c8433d | proposed (index only) | "Generalized-Jacobian extension class equals the Tate pairing" | Trivial on l-parts with l not dividing p^k-1; same family (lead evidence row). |
| IDEA-20260928-fd7f5d | proposed, novelty 'adaptation' (index only) | "The incomplete-sum regime of Hom(E,G_m) = 0. Do multiplicative characters that are CONSTANT on a coset ... bias the characters of x(P+-Q)" | ADJACENT: character sums of chi(x(.)) against group characters; no Miller function. |
| H-PFDR-8a4f44 | proposed (index only) | "THE SAVING A CHARACTER-SUM BOUND WOULD NEED ... IS NOT A SMALL IMPROVEMENT OVER SQUARE-ROOT CANCELLATION - IT IS THE WHOLE OF IT" | ADJACENT: Weil-Deligne as the ceiling for windowed decomposition counts (error d^m times the bound). Agrees with C2's HC2-2 direction. |
| H-CRYPTO-fde1f1 | analyzed (index only) | "For the two fixed normalized sheaf families ... the addition-pullback correlation complex may admit an effective uniform fourth-moment bound" | Sheaf technology precedent (trace sheaf pulled back through x and addition); different sheaf. |
| H-ECDLP-f8cea6 | proposed (index only) | "A public reduced-Tate character can be evaluated and decoded without hidden scalar input on the finite frozen fixture panel" | The N | p-1 control family. |
| H-PSEUDO-83817b | specified (index only) | additive character sum of DL over the small-x factor base | ADJACENT, partial sums (see N1). |

Knowledge corpus (not ledger, read for context): KN-LIT-7639 records hypothesis (H1) of the O2 line verbatim: |sum chi(F(P))| <= (2g-2+2m) sqrt(p), m = number of
distinct zeros and poles of F, "not a constant times a k-th power", with the cubic/quartic case "NOT covered" on genus 1 ("needs either Bombieri's original or Perel'muter").
KN-FIND-ffe1df uses it (Theorem A' + Weil, families C/E/F/G) and states the general-k genus-1 case as open. So the UNTWISTED half of C2 (psi trivial) is already in the
corpus: with F = f_{N,P}, m = 2, g = 1 it gives 4 sqrt(p). KN-FIND-e7a3b1 closes the Weil route for H-PSEUDO only for the incomplete (small-x) sum.

### What IDEA-20260905-b6154d already says (read by targeted line ranges 1-30, 40-64, 80-135, 300-340, 370-392; DISCLOSURE: this is a fourth record read beyond the 'at most 3 full records' budget, partial only, taken after the index truncation hid the decisive body text)

* (B) "the character chi_a of G is the trace function of a rank-one Lang torsor on E (an unramified cover of E of degree N); ... eta(f) for a multiplicative eta is a Kummer sheaf; the product sheaf is geometrically nontrivial in case (i) always and in case (ii) unless the Kummer sheaf of eta(f) is geometrically isomorphic to the Lang torsor of some chi_a, which requires ord(eta) = N, hence N | p - 1; the Weil-Deligne bound then gives c * deg * sqrt(p)". Ingredients "Bombieri 1966, Kohel-Shparlinski 2000 (the subgroup twist), Deligne's Weil II ... NONE has been opened in this program; this is a proof MAP".
* Its class C(D,L) EXCLUDES Miller-type functions: "a function with a short description but exponential degree (Miller, itineraries) is outside the class, and mislabelling it inside would import a closure that does not apply."
* (D2) diagnoses the Tate-pairing break at small embedding degree as the failure of "bounded degree": "Miller evaluates a degree-N function fast".
* (E) "THE DOOR THAT REMAINS": fast evaluations of functions of exponential degree; "on a generic prime-order curve ... no pairing is cheap and no bounded-count iteration is known to approximate a character".
* Break-even: "the hard-core-bit amplification breaks even with rho only at advantage N^(-1/4)" (title), the source of HC2-2.

Consequences for C2 (stated strictly):
1. The Lang-torsor (x) Kummer mechanism, the nontriviality criterion and the Weil-Deligne step are NOT new to the program. The candidate's line "absent from the program ledger" is wrong about the mechanism; it is right only about the words.
2. C2's genuine delta over b6154d (B): for the Kummer part the relevant complexity is the number of points of supp(div f mod e) (tame ramification, Swan = 0), not deg f. With f = f_{N,P} and gcd(N,p-1) = 1 this is 2 while deg f = N, so b6154d's bound c*deg*sqrt(p) (vacuous at deg ~ N) improves to 2 sqrt(p). That moves the Miller function from "outside the class, door (E)" to "inside, for multiplicative characters of f". It also corrects the (D2) diagnosis: what fails at N | p-1 is not 'bounded degree' but div f = 0 mod ord(eta) (the sheaf becomes unramified and can equal the Lang torsor); degree N is irrelevant. This is a derivation I re-did and agree with (below), not a retrieved theorem. The relocated break also means b6154d's recorded prediction for (D2) ("the break is ... at the bounded-degree step. A break elsewhere, or no break, falsifies the derivation as written") is falsified as written; the orchestrator should treat b6154d (B)/(D2) as superseded in that detail if C2 is adopted.
   Combined statement of the delta (same in the summary and in the structured reason): b6154d (B) supplies the Lang-torsor twist and nontriviality criterion with a degree-based constant; KN-LIT-7639 (H1) supplies the degree-free zero/pole count for the untwisted sum; C2 = their combination at f_{N,P} with gcd(N,p-1) = 1, constant 2, the (D2) relocation, and the replay.
3. It does NOT cover what door (E) also names: walk itineraries; and not additive characters, bits or intervals of U (U = f^u with u = N^{-1} mod p-1 has degree ~p as a rational function, so Artin-Schreier/Swan counts are vacuous, and completing a bit or interval of F_p^* in multiplicative characters costs about sqrt(p)).

Index-only neighbours were not opened (budget). Nothing in the experiments index contradicts or replays C2.

## N4  Notation check (representation / coordinate candidate)

Pair (as in the candidate, restated): representation = F_p^*-valued Kummer coordinate R -> chi(U(R)) = chi^u(f_{N,P}(R)) with u = N^{-1} mod (p-1)
(equivalently any function whose divisor has bounded support mod e); operation set Sigma = full translation of G = E(F_p), probed only through the characters of G (the Fourier basis of Z/N).
Trichotomy class: coordinate-dependent (U is a function of the representation, not of the group element); no propagation and no collision gain claimed.

Is it a recorded rigidity result in new notation?
* IDEA-20260806-c5d183 (a projection propagating deterministically under full translation of a prime-order group is constant or injective) and IDEA-20260901-863e36 (propagation = block systems of <Sigma>): both are EXACT-propagation statements about lossy projections. C2 makes no propagation statement; it bounds the Fourier transform of one coordinate. chi o U is not translation-compatible (the defect U(R)U(S)/U(R+S) = g_{R,S}(P) is exactly what the Miller cocycle is), so those results do not apply to it and C2 does not restate them.
* KN-FIND-ffe1df Theorem C (exact sum-compatibility + associativity => h is a homomorphism, impossible for prime N): exact-case homomorphism rigidity. chi o U is only approximately sum-compatible, so Theorem C is inapplicable; C2 is an approximate Fourier no-go. Closest in kind is the Weil closure of ffe1df families C/E (Theorem A' + (H1)), which is first-order/level-1 and, per ffe1df, bounds a different quantity (T_t, a three-point correlation) than a linear Fourier coefficient. So C2 is not Theorem C in new notation, but it is a member of the same 'Weil-closed multiplicative coordinate' family and inherits its limits: it speaks about linear statistics, not the triple correlation sum_{R,S} chi(g_{R,S}(P)) (a sheaf on E x E), which is a different computation.
* KN-OPEN-020 (bounded-degree algebraic factor bases scoped out; open class = high-degree, implicit-membership, target-dependent): C2 proposes no factor base, so it is not a KN-OPEN-020 result. But D = {R : chi(U(R)) = 1} would be a high-degree implicit-membership base inside that open class; if anyone proposes it, LEAD-ICP-algebraic-membership-factor-base's conservation row ("mean per-target yield is binomial(B+m-1,m)/N for every base of size B") applies unchanged, and C2 gives, by my derivation, max_{a != 0} |sum_{R in D} psi_a(R)| <= ((e-1)/e) * 2 sqrt(p) <= 2 sqrt(p), using 1_D = (1/e) sum_{j=0}^{e-1} chi^j(U) with the j = 0 term vanishing for a != 0; this is the square-root-cancellation side of H-PSEUDO for this base, proved, at the cost of a factor 2 sqrt(e) over the random level sqrt(|D|) when |D| = N/e (so it excludes super-random yield by more than 2 sqrt(e) only).
* IDEA-20260905-b6154d is the only recorded result that is the same mechanism in other notation (see N3); it is a proof map for bounded degree, so C2 is its refinement, not a rigidity theorem.

Conclusion: not a rigidity result in new notation; a degree-free refinement of the b6154d wall, specialised to the Miller primitive.

### N4 provenance note
IDEA-20260806-c5d183 and IDEA-20260901-863e36 were characterized from docs/object-frame-ideation.md section 1 (the program's own table), NOT from the records: a lookup of those two ids as record ids in ledger/.index/proposals.jsonl returned nothing (they appear only inside other records' refs). KN-FIND-ffe1df and KN-OPEN-020 were read directly.

## Scope clauses of the obstruction rows touched (verbatim, extracted from the lead YAMLs)

- LEAD-ICP-self-pairing-prime-order [closed_obstructed, kind=theorem]: Scope: prime-order subgroups of E(F_p) with embedding degree > 1.
- LEAD-ICP-algebraic-membership-factor-base [closed_obstructed, kind=theorem]: Scope: prime-order E/F_p, any base of size B.
- LEAD-TRF-second-torsion-direction [closed_obstructed, kind=theorem]: Scope: ordinary and supersingular curves over F_p, prime N.
- LEAD-TRF-padic-canonical-section [closed_obstructed, kind=theorem]: Scope: non-anomalous prime-field curves, all lifts of E.
- LEAD-EXO-augmented-oracle-ggm [closed_obstructed, kind=theorem]: Scope: oracles, not resources (see IDEA-20260808-ea3b4f).
- LEAD-EXO-elliptic-net-eds [closed_obstructed, kind=proof]: (no 'Scope:' clause in the statement)
- LEAD-TRF-mov-small-embedding-degree [closed_known, kind=literature]: Scope: ordinary and supersingular curves over any finite field; the target-field cost is a separate lead (LEAD-TRF-pairing-target-field-recost).
- LEAD-STR-isogeny-class-generic-invariance [closed_obstructed, kind=theorem]: (no 'Scope:' clause in the statement)
- LEAD-EXO-curve-model-representation [closed_obstructed, kind=measured]: (no 'Scope:' clause in the statement)
- LEAD-EXO-dl-character-sum-pseudorandom [exhausted_at_scale, kind=measured]: (no 'Scope:' clause in the statement)
- LEAD-TRF-miller-cocycle-nonhom-transfer [open_unexamined]: NO obstruction block
- LEAD-EXO-miller-pairing-cocycle [open_next_step]: NO obstruction block
- LEAD-EXO-coordinate-statistic-leakage [open_next_step]: NO obstruction block

Reading against C2 (C2 is a closure statement and escapes none of these; "escape_premises" in the candidate is bookkeeping):
* SO-PAIR (LEAD-TRF-second-torsion-direction), Scope "ordinary and supersingular curves over F_p, prime N": C2's setting is inside this scope; the obstruction's premise is homomorphic / graph-type transfers, which U is not, so it neither covers nor is contradicted by C2.
* SO-PADIC (LEAD-TRF-padic-canonical-section), Scope "non-anomalous prime-field curves, all lifts of E": the statement "any non-homomorphic section recovers d only at the random 1/p rate" is for sections into E(Q_p); C2's F_p^*-valued statement is a Fourier-scale bound (2/sqrt(p)), weaker than a 1/p single-value rate, not the same claim.
* SO-GEN (LEAD-EXO-augmented-oracle-ggm), Scope "oracles, not resources (see IDEA-20260808-ea3b4f)": U is computed from the point by a Miller loop, a resource, not an oracle; the GGM argument does not apply to it, and C2 does not claim otherwise.
* SO-NET (LEAD-EXO-elliptic-net-eds): the row has no Scope clause; the K2 route U(kP) = c r_k C^(k/N) is not touched by C2.
* The primary target LEAD-TRF-miller-cocycle-nonhom-transfer and LEAD-EXO-miller-pairing-cocycle have NO obstruction block, so there is no Scope clause to quote for them; C2, if adopted, would be the first obstruction text for the multiplicative-character clause (kind: theorem, with the Scope the candidate proposes: G prime order or the N-part, gcd(N,p-1) = 1, multiplicative-character statistics of U).

## Verification work done in this gate (my own runs)

### Toy replay (scripts/miller_u_spectrum_v2.py, unmodified, numpy; python3 -I)
My rerun of the unmodified script reproduced the four data lines of the prior rerun file character for character
(`diff` shows only one extra trailing line `DONE` in the prior file, which the script itself never prints; so 'byte-identical' holds for the data lines only).
The script prints max|S| to one decimal; I reran a copy with more digits (copy: gate-C2-work/miller_u_spectrum_v2_hiprec.py, same RNG path), output gate-C2-work/hiprec.out:

```
theorem-cell: p=10007 #E=10069 N=10069 h=1 gcd(N,p-1)=1 evaluated=10065 bad=2 chains_agree=10022/10022 split_agree=10030/10030 max|S|=202.0107 at (a,b)=(9558, 6014)  max|S|/sqrt(p)=2.01940  bound 2+2/sqrt(p)=2.01999  N/sqrt(p)=100.7
theorem-cell: p=10009 #E=9973 N=9973 h=1 gcd(N,p-1)=1 evaluated=9969 bad=2 chains_agree=9914/9914 split_agree=9932/9932 max|S|=202.0462 at (a,b)=(1645, 7759)  max|S|/sqrt(p)=2.01955  bound 2+2/sqrt(p)=2.01999  N/sqrt(p)=99.7
theorem-cell: p=20011 #E=19927 N=19927 h=1 gcd(N,p-1)=1 evaluated=19923 bad=2 chains_agree=19854/19854 split_agree=19882/19882 max|S|=284.8916 at (a,b)=(14754, 4337)  max|S|/sqrt(p)=2.01393  bound 2+2/sqrt(p)=2.01414  N/sqrt(p)=140.9
control-N|p-1 (expect peak ~N): p=10111 #E=10110 N=337 h=30 gcd(N,p-1)=337 evaluated=333 bad=2 chains_agree=316/316 split_agree=316/316 max|S|=333.0000 at (a,b)=(3030, 240)  max|S|/sqrt(p)=3.31167  bound 2+2/sqrt(p)=2.01989  N/sqrt(p)=3.4
```

and a second copy that lists which k are left out of S (gate-C2-work/miller_u_missing_k.py, output gate-C2-work/missing_k.out): in every cell, including the control, the two 'bad' points are k = 2 and k = N-2, i.e. R = +-2P
(the first Miller step doubles P, so the vertical at x(2P) vanishes there), and k = 1 (R = P) is skipped by design; k = 0 (R = O) is not in the range. So S = sum over G minus {O, P, 2P, -2P}.

Precise reading of the replay (labelled; these are my computations from the output above):

| p | 2 sqrt(p) | max abs S | max abs S - 2 sqrt(p) | (max abs S - 2)/sqrt(p) |
|---|---|---|---|---|
| 10007 | 200.0700 | 202.0107 | 1.9407 | 1.99941 |
| 10009 | 200.0900 | 202.0462 | 1.9562 | 1.99956 |
| 20011 | 282.9205 | 284.8916 | 1.9711 | 1.99980 |

* Upper side: max abs S exceeds 2 sqrt(p) itself by about 1.94-1.97 and passes only through the +2 allowance for the two unevaluated points +-2P (printed bound 2 + 2/sqrt(p)). The replay is CONSISTENT with the bound; it does not test the sharp constant 2 from above, because |S_full| is only known to be <= |S| + 2.
* Lower side: by the triangle inequality the full sum satisfies max |S_full| / sqrt(p) >= 1.9994, 1.9996, 1.9998. So the constant 2 cannot be improved: the bound is attained to 0.06%, 0.04%, 0.02% in these cells (maximised over about p^2 pairs (a,b)). 'Tight' is supported from below; 'attained and not exceeded' is not established because of the +-2P gap. (Closing the gap needs +-2P evaluated by another chain; not done.)
* Chains: binary and NAF Miller chains agree on every evaluable point (e.g. 10022/10022), split evaluations agree (10030/10030): the evaluation of f_{N,P} is internally consistent.
* Control (N | p-1, p = 10111, N = 337): max abs S = 333.0000 = the number of evaluated terms, i.e. chi o f is exactly a group character (Tate pairing alive), peak ratio 3.31 against the bound 2.02. The control is peaked, but its separation from the theorem cells is only 1.6x because N is small (N / sqrt(p) = 3.4); it shows the instrument responds to a character, not that it resolves a modest excess at theorem scale. A control with N | p-1, N about 2^10 or larger, would separate by N / (2 sqrt(p)). Same caveat the program recorded for the P2 control in KN-FIND-ffe1df.
* These are toy-tier numbers at p about 10^4; no statement about cryptographic p is made.

### Re-derivation of the theorem (mine; labelled derivation, not retrieved)
Setting G = E(F_p) of prime order N, gcd(N, p-1) = 1, chi of exact order e | p-1, e > 1, chi' = chi^u (u = N^{-1} mod p-1, also order e), psi a character of G, f = f_{N,P}, div f = N(P) - N(O).
(1) The Lang isogeny x -> Frob(x) - x is finite etale with group E(F_p); L_psi is rank 1, lisse on all of E, pure of weight 0, trace function psi(+-R). (2) K = Kummer sheaf of chi' o f is rank 1, lisse on U = E \ {P,O}, tame, local monodromy at P and O is chi'^{+-N}, nontrivial because e does not divide N. (3) F = L_psi (x) K is lisse on U, tame, rank 1. By GOS, chi_c(U,F) = 1 * (2 - 2g - |S|) - 0 = -2 for g = 1, |S| = 2. (4) H^0_c = 0 (U affine); H^2_c = 0 since F is ramified at P while L_psi is not, so F is geometrically nontrivial. (5) dim H^1_c = 2, weights <= 1 (Weil II), so |sum over U(F_p)| <= 2 sqrt(p). Independent of deg f and of psi (including psi trivial). I find no gap. The step that fails at N | p-1 is (2): chi'^N = 1, K becomes unramified and can be the Lang torsor (the Tate pairing character), exactly the control. Tame case only; the Artin-Schreier (additive) variant has Swan terms that grow with pole orders and is not covered.

### Citation ledger (provenance)
| claim used | source | provenance | what I actually saw |
|---|---|---|---|
| sum over n in Z_T of psi(x(nG)) chi(nG) << q^{1/2}, E ordinary, any group character chi of E(F_q) | Kohel-Shparlinski, ANTS-IV, LNCS 1838 (2000) 395-404, Cor. 1 | retrieved, second hand | read in Ahmadi-Shparlinski arXiv:1302.4210v3 Lemma 1 (PDF text extracted and read here), which calls it "a special case of [17, Corollary 1]". The primary K-S text was NOT obtained (the author's PDF host refused the connection). This is the ADDITIVE x group-character case with an unspecified implied constant; it supports the twist technique only, not C2's tame Kummer conductor count. |
| multiplicative-character analogues exist | Ahmadi-Shparlinski sec. 5 ("many of our results have direct analogues for sums with multiplicative characters"); Merai, Publ. Math. Debrecen 80 (2012) 199-213 | retrieved as pointers | the AS sentence was read; Merai's abstract only (pseudorandom binary sequences from multiplicative characters on E); no bound read. |
| mixed additive x multiplicative sums along a curve are O(sqrt(q)) with constant depending on degrees | Perel'muter, Mat. Zametki 5 (1969), 'Estimation of a sum along an algebraic curve' | retrieved (search summary of the mathnet listing) | existence and nature only; the constant depends on DEGREES, so it does not give C2's degree-free count. |
| GOS formula, Kummer sheaf rank 1 tame, H^2_c = 0 for geometrically nontrivial irreducible, dim bounds | Kowalski, Lectures on applied l-adic cohomology, arXiv:1712.03173, Thm 4.2, sec. 4.1, 4.2.2 | retrieved (PDF text read) | stated for U in P^1; the genus-1 form chi_c(U) = 2-2g-|S| used above is recalled. |
| Deligne weights: H^1_c weights <= 1 for pure weight-0 lisse sheaves | Deligne, Weil II (1980) | recalled (consistent with the Kowalski search summary) | not opened. |
| Bombieri / Weil curve bound with m = distinct zeros and poles | KN-LIT-7639 (H1), KN-LIT-f6de4b | internal, partly traced | the program's own notes say the genus-1 general-order case is untraced. |
| character sums of psi_n(P) in n under shifts | Bhakta-Shparlinski arXiv:2507.09271 (2025) | retrieved (abstract summary) | relevant only to the K2 / r_k route (sum in n, short ranges averaged over shifts); not C2. |
| the Kummer x group-character statement with conductor 2 for a degree-N Miller function | none located | NOT FOUND in any retrieved source | C2 is a derivation here; flag as such. |

## Verdict reasoning in one place

advances_lead on LEAD-TRF-miller-cocycle-nonhom-transfer (and, on the registry side, LEAD-EXO-coordinate-statistic-leakage; U-part of LEAD-EXO-miller-pairing-cocycle).
Not duplicate_of_lead: the lead's planned step is a toy measurement; C2 is a proof route plus a replay for its Z/N-character clause, with a delta over IDEA-20260905-b6154d that is exactly what that record leaves open for Miller functions.
Not known_result: no KR row, and the exact statement is not located in a retrieved source, though the technique family is classical and the untwisted half is already in KN-LIT-7639.
Not new: the sheaf mechanism is IDEA-20260905-b6154d (B).

Downstream disposition, corrected: the candidate's outcome (a) (LEAD-TRF-miller-cocycle-nonhom-transfer closed_obstructed) overreaches. The lead's own discriminator
closes it on "equidistribution at the 1/p rate" (Smart-ratio success), which a 2 sqrt(p) noise floor cannot reach (events of probability 1/p, or near c/sqrt(n) per IDEA-20261016-0bacee,
are below it); its forecloses also list generalized-Jacobian transfer, Miller S-unit descent and zeta-defect, none touched. The defensible disposition is
open_next_step with the multiplicative-character (Z/N spectrum) clause of H1 discharged by theorem (Scope: G prime order, gcd(N,p-1) = 1, multiplicative-character statistics of U),
leaving open: single-value / Smart-ratio events, the three-point (cocycle) correlation, K2 / EDS, zeta-defect and generalized-Jacobian sublines.
For LEAD-EXO-miller-pairing-cocycle the candidate's own fork stands (K2 route unchanged).

Predictions (labelled, not results): if the lead's panel is replayed on p <= 2^20, I would predict the spectral maximum tracks 2 sqrt(p) from below and the N | p-1 control peaks at N; I have produced only the four p about 10^4 cells above.
