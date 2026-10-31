# Novelty gate N1-N4: C4 (prime) weighted homogeneity of summation polynomials

Field: commutative algebra. Session date 2026-10-24. Gate author: scout subagent (read-only on the repositories; every file written here lives under the scout directory).

Candidate (name as given): C4 (prime) Weighted homogeneity of summation polynomials: every Semaev decomposition system has the curve-free cuspidal (G_a) leading form +-prod x_i^{2^{m-1}}. A proof of H-TOP for all m, curve/j/target/isogeny blindness of all top-form invariants, and automorphism folding as a between-target equivariance.

## VERDICT: advances_lead

Primary lead: LEAD-ICP-digit-presentation-solving-degree (open_next_step), through hypothesis H-PFDR-4148b8 and its heuristic assumption HEUR-001 (= C4's "H-TOP"). Secondary lead: LEAD-ICP-xline-symmetry-special-j (open_unexamined), whose next_action C4's rank arm sharpens.

Why not "new": the ledger already holds C4's central object. IDEA-20260903-e1e38b and H-PFDR-4148b8 define the same top-form projection S~ -> S~_top, state the monomial top form c*prod x_k^{2^{m-1}} for every m as H-TOP (derived at m = 2, inferred at m = 3, symbolic obligation at m >= 4), and derive the closed form d_ff = m 2^{m-1} + floor((s - 2^{m-1})/2) + 1 as curve- and target-independent (D6). The lead row's best_measured already carries "curve-independent and reproduced by a curve-free block-factored null (EV-PFDR-1394a4)".

Why not "duplicate_of_lead": the lead is open, and C4 adds a discharge of HEUR-001 for all m (isobaric resultant argument, unchecked by me), a closed form for the top-form degree of regularity (no ledger record found), the use of the already-specified fall_dim meter (H-PFDR-4148b8, H-PFDR-232b3a) on special-j and 3-isogenous cells against a same-weight-block-support null, and the transfer of the top-form invariance to the special-j / isogeny / model leads. None of these changes a solving degree, a cost or an exponent, and C4 says so (tier X, predicted gain 0).

Why not "known_result": no KRMAP row states a curve-free top form of S_{m+1}. A literature relative exists in characteristic 2 (Kousidis-Wiemers, see Citations); I found no source stating the odd-characteristic, all-m, curve-free statement. A lexical miss proves nothing, so this stays conditional.

What C4 does NOT do (so the standing obstructions are untouched): it does not lower beta_work (B2: 0.797 / 0.647 against the 0.30 gate), it does not touch last fall degree or grevlex solving degree, it does not escape SO-ENDO, SO-ISO or SO-ALGFB, and it does not cover the Edwards shape or characteristic 2.

## Claim-by-claim delta (C4 against the atlas and ledger)

| C4 item | Already recorded | Where | Delta |
| --- | --- | --- | --- |
| Lemma W: S_{m+1} weighted-homogeneous (x:2, x_R:2, a:4, b:6), weight m 2^m | Partly. Weighted homogeneity of S_m in (a,b) is already used to force each degeneration locus onto one j-line point (6 weight-12 loci for S_3/S_4); division polynomials are weighted-homogeneous under the same scaling | IDEA-20260811-3e08e0 (mechanism, "weighted homogeneity forces every degeneration locus to be a single j-line point"), H-JINV-b3b975, IDEA-20260807-aabd67 | The x / x_R weights and the full F_kij decomposition for general m were not found. Corollary-level new. |
| H-TOP for all m (top form c*prod x_k^{2^{m-1}}) | Yes, as a heuristic assumption with a falsification condition and a validation experiment | H-PFDR-4148b8 HEUR-001 (EXP-PFDR-5726af); IDEA-20260903-e1e38b (D3, "symbolic at m >= 4" obligation); EV-PFDR-f71d7f "strong: deg S_{m+1} = m 2^{m-1}" (cited by the lead row) | C4's proof (isobaric resultant, S_3(u,0,X;0,0) = u^2 X^2) would discharge HEUR-001. This is the one real advance. I did not re-derive or re-run it. |
| Corollary F: d_ff closed form, now unconditional on HEUR-001 | The closed form itself, its numbers, and its exactness route (tensor-kernel identity plus Wilson, p > s) are recorded | H-PFDR-4148b8 (D4, D5); IDEA-20260903-e1e38b; lead best_measured (EV-PFDR-1394a4) | Only the HEUR-001 condition is removed. The Wilson condition (H-WIL) stays. |
| Corollary R: top-form d_reg = N - floor((s - 2^{m-1})/2) | No record found (ledger grep sets A-D; IDEA-20260905-df55e9 separates the degree notions but gives no closed form) | n/a | Plausibly the cokernel side of the same tensor/Wilson rank argument. Unverified by me. New at corollary level. |
| Corollary B: curve, j, target, model and isogeny blindness of top-form invariants | Curve and target blindness: yes. The fibre over S~_top "contains every curve, every target and every lower-order perturbation" | H-PFDR-4148b8 (D6, observable_fiber transform); IDEA-20260903-e1e38b mechanism | The j / isogeny-class / model labels are the same fibre statement under C4's weights. The Velu-augmented top form is derivation-only. Edwards is not covered. |
| Corollary E: automorphism folding relates targets only (x -> zeta x maps system(R) to system([omega]R)) | At m = 2 and for the factor-base side: yes | IDEA-20260807-1ea327 (S_3(zx) = zS_3 mod z^3 - 1 at a = 0), IDEA-20260807-5ddccf (semi-invariance facts, |Aut| scaling law), H-PFDR-ebec07, IDEA-20260901-863e36 (Gamma acting by R -> [gamma]R) | All-m statement. The conclusion (constant factor only) is the SO-ENDO / KR-RHO-0528e7 / LEAD-RHO-automorphism-class-walks ceiling sqrt|Aut|. |
| Corollary G: top form is the cusp / G_a signed subset-sum norm | No record found (no cusp / G_a hit in grep set B beyond an unrelated F_3[T] record, H-DRINF-cc79bb) | n/a | Interpretation, predicted gain 0. Not verified by me. |
| Corollary L: curve dependence lives only in weight-lowered components | Yes in substance | H-PFDR-4148b8 mechanism ("sub-top terms ... are exactly where the curve coefficients, the target and the digit offsets live"); EV-ENDO-e8d3e5 S_3 support 13 / 9 / 10 | Not new. |
| Fall-on-kernel meter (rank of the lower-weight map on K_d = ker of the top-form map); rank arm at j = 0, 1728, generic, a 3-isogenous pair, same-weight-block-support null | The meter itself: yes. fall_dim(D) = rank_full - rank_top is the specified measurement of H-PFDR-4148b8, and H-PFDR-232b3a states the nonzero fall image as U_D(ker T_D) with dimension rank(U_D) - rank(T_D), which is the rank of the lower-weight part on the top-form kernel. The question: same as the open lead's next_action | H-PFDR-4148b8 (MEASUREMENT), H-PFDR-232b3a, IDEA-20260905-e6e2e5; LEAD-ICP-xline-symmetry-special-j next_action (degree-d Macaulay ranks at j = 0, 1728 against generic and against a coefficient-block vanishing null of the same support, three toy primes; H-PFDR-df0127, H-PFDR-6b9f1a) | Not a new instrument. What is new is pointing the existing fall_dim meter at the special-j / 3-isogenous cells with a same-weight-block-support null, in place of the plain Macaulay ranks the xline lead names. That is a sharper next step for an open lead, so advances_lead; it is a refinement of the lead's measurement, not a new object. |

Answer to the B2 sub-question as asked ("is the digit lane's curve-free first fall an accident of small s?"): the ledger already says no for d = 2, every s >= 2^{m-1} with 2^s <= p (hence p > s), conditional on H-WIL (Wilson, retrieved only at snippet level by the proposing session) and on HEUR-001. C4 removes the second condition. The first condition stays.

## N1 Atlas collision: raw outputs

### N1 run 1

Command: python3 tools/lead_atlas.py --match "weighted homogeneity proves the leading form of the summation polynomial is a curve-free monomial so first fall degree is curve independent"

```
   22  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   19  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
   19  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   19  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   14  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   12  LEAD-ICB-prime-degree-algebraic-decomposition open_blocked       Bounded-degree algebraic decomposition (Weil-descended S_{m+1} on subspace bases) at prime extension degree: ECC2K-130, NIST K/B, sect571
   12  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
   10  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
```

### N1 run 2

Command: python3 tools/lead_atlas.py --match "prove the top-degree part of the Semaev polynomial does not depend on the curve or the target"

```
    9  LEAD-STR-special-j-ic-semaev                 open_next_step     Special j (0, 1728, small height, Semaev degeneration locus) in Semaev and index-calculus systems
    8  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    8  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
    8  LEAD-ICE-first-fall-degree-assumptions       open_blocked       First-fall-degree / Assumption-1 arguments for subexponential binary ECDLP (Semaev 2015, Nagao, Petit-Quisquater)
    7  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    7  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
    7  LEAD-TRF-pairing-target-field-recost         open_next_step     Recompute the post-MOV target-field DLP cost (exTNFS in GF(p^12)) for BLS12-381 and BN254 with memory charged
    7  LEAD-TRF-teske-secret-isogeny-trapdoor       open_next_step     Teske-style trapdoor on ordinary prime-field curves: a secret isogeny to an endpoint with a non-invariant ECDLP weakness
```

### N1 run 3

Command: python3 tools/lead_atlas.py --match "model-native PDP first fall degree and degree of regularity invariant across special j isogeny class and curve model; the lever is capped by a degree argument"

```
   26  LEAD-ICE-curve-presentation-invariance       open_next_step     Does decomposition difficulty change across an isogeny class, curve model or special j (transport to an easier presentation)?
   19  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
   19  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
   19  KR-RHO-755e35                                known_result       Isogenous curves are equally hard; isogeny walks do not find weak curves
   17  LEAD-STR-isogeny-transport-preprocessing     closed_obstructed  Multi-target and preprocessing tables shared across an isogeny class
   17  LEAD-TRF-prime-field-isogeny-to-weak         closed_obstructed  Isogeny transfer of a prime-field ECDLP to a weaker curve (anomalous, low embedding degree, descent-friendly) in the same class
   16  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   16  LEAD-STR-class-representative-ic-selection   open_next_step     Choose the isogenous curve or isomorphic model that minimises charged index-calculus cost
```

### N1 run 4

Command: python3 tools/lead_atlas.py --match "weighted homogeneous summation polynomial leading form cuspidal G_a Weierstrass scaling automorphism folding top-form invariants"
(phrasing supplied by the gate author, not one of the three given match_phrasings)

```
   15  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    9  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
    9  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
    8  KR-IC-1fcdbc                                 known_result       Characteristic-2 summation algorithms stay far slower than rho
    8  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
    7  KR-IC-955fd6                                 known_result       Symmetries and torsion speed up point decomposition
    7  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    7  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
```

### N1 run 5

Command: python3 tools/lead_atlas.py --match "Semaev summation polynomial homogeneity leading form degree of regularity closed form top-degree component"
(phrasing supplied by the gate author, not one of the three given match_phrasings)


```
   19  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
   18  KR-IC-fbdb61                                 known_result       Last fall degree and solving degree of Weil descent systems
   17  KR-IC-889857                                 known_result       Subexponential binary ECDLP under the first fall degree assumption
   15  KR-IC-5a43e5                                 known_result       Semaev summation polynomials
   14  LEAD-ICE-descent-closure-degree-at-scale     open_blocked       Does the MutantXL/F4 closure (refutation) degree of descended S_3/S_4 chains stay at 4 as l and n grow?
   12  LEAD-ICE-prime-field-semaev-solving-degree   closed_known       Groebner solving degree / eliminants of prime-field S_3 / S_4 decomposition systems
   12  LEAD-ICP-digit-presentation-solving-degree   open_next_step     Digit (base-B) presentation of prime-field Semaev systems as a Weil-descent analogue - first/last fall degree, staircase and representation tricks
   11  KR-IC-f5c584                                 known_result       The trace morphism forces a linear equation (first fall degree 2 for S_3)
```

### N1 run 6

Command: python3 tools/lead_atlas.py --match "automorphism zeta x maps system of R onto system of omega R folding relates targets only"
(phrasing supplied by the gate author, not one of the three given match_phrasings)


```
   13  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    8  LEAD-ICP-coincidence-harvest-structured-base open_next_step     Harvesting x-key / pair-sum coincidences of structured bases (label-GAP, window, log-GAP) and escaping conservation by target preselection
    6  LEAD-ICE-chained-semaev-dreg-vs-semiregular  open_next_step     Degree of regularity of the Boolean chained Semaev system (m = 3, t = 3) against a semi-regular null
    6  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
    5  LEAD-ICB-multi-target-and-portfolio          closed_obstructed  Batch IC and IC/rho portfolios: amortising the set-up over many targets, restart portfolios
    5  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    5  LEAD-ICP-icperf-writability-boundary         closed_obstructed  Writability of the descended system - arity forced to m >= 4 and the ANF too large to write inside the rho budget below n ~ 300
    4  KR-RHO-0528e7                                known_result       Automorphisms give a sqrt(m) constant factor
```

## N1 reading of the top hits (lead YAMLs and KRMAP rows opened; source rows in knowledge/leads/ecdlp/)

Note on the raw output: the first column is the match score, then the lead or KR id, disposition, title. Runs 1-3 use the three given match_phrasings in order. Runs 4, 5 and 6 are phrasings supplied by the gate author (run 4: weighted homogeneity / G_a / folding vocabulary; run 5: leading form and d_reg closed form; run 6: the equivariance statement). Every top-5 hit of every run was opened.

| Run | Rank | Hit | Disposition | Relation to C4 |
| --- | --- | --- | --- | --- |
| 1 | 1-3 | KR-IC-f5c584, KR-IC-889857, KR-IC-fbdb61 | known_result | f5c584: binary trace-morphism first fall 2 for S_3; 889857: first-fall-degree assumption for binary ECDLP (disputed); fbdb61: Caminata-Gorla invariants kept distinct, whose definitions C4 uses. Different object or definitions only. |
| 1 | 4 | LEAD-ICE-descent-closure-degree-at-scale | open_blocked | Boolean (binary) MutantXL closure degree at (m, l) scale; memory-blocked. Different object. forecloses phrases do not mention prime-field top forms. |
| 1 | 5 | LEAD-ICP-digit-presentation-solving-degree | open_next_step | SAME OBJECT. best_measured already: d_ff closed form, curve-independent, reproduced by a curve-free block-factored null (EV-PFDR-1394a4); evidence EV-PFDR-f71d7f "deg S_{m+1} = m 2^{m-1}". forecloses "first fall degree of the digit-presented decomposition system". C4's Corollary F falls inside that phrase. |
| 2 | 1 | LEAD-STR-special-j-ic-semaev | open_next_step | Its first-fall arm is what C4's Corollary B closes at top-form level. C4 leaves the charged-S arm open (it says so). Support counts 9 / 10 / 13 (EV-ENDO-e8d3e5) are the S_3 instance of "curve dependence lives in weight-lowered terms". |
| 2 | 2-3, 5 | KR-IC-5a43e5, KR-IC-889857, KR-IC-5931ee | known_result | 5a43e5: Semaev recursion, degree 2^{m-2} per variable (so per-variable degree of S_{m+1} is 2^{m-1}, the per-variable half of H-TOP, is known); 5931ee: naive prime-field IC cannot beat generic (B2 background). |
| 2 | 4 | LEAD-ICE-first-fall-degree-assumptions | open_blocked | Binary FFD assumption audit and a Lean bridge for the S_3 degree-2 trace fall. Different object. |
| 3 | 1 | LEAD-ICE-curve-presentation-invariance | open_next_step | Asks whether isogeny, model or special j lowers first-fall / solving degree. C4 settles only the first-fall / d_reg content. The lead's frozen EXP-DREG-dd668d (last-fall and grevlex solving degree on certified Velu edges) is untouched. forecloses "curve model invariance of solving degree", "Velu edge lowers Groebner degree": not covered by C4. |
| 3 | 2-3, 4 | KR-IC-889857, KR-IC-f5c584, KR-RHO-755e35 | known_result | 755e35: isogenous curves equally hard for generic methods; C4's B is the algebraic top-form analogue, not a restatement. |
| 3 | 5 | LEAD-STR-isogeny-transport-preprocessing | closed_obstructed (proof) | About transporting preprocessing tables; C4 has no table. No collision. |
| 3 | 8 | LEAD-STR-class-representative-ic-selection | open_next_step | (Rank 8, read for the B2 model / isogeny sub-question.) Arm (c) picks the best isomorphic model by small-abscissa base. Lemma W makes a model change an exact rescaling x -> lambda^2 x of the base, which that lead already treats as base-sampling; C4 makes no yield claim. Adjacent, not colliding. |
| 4 | 1 | LEAD-ICP-xline-symmetry-special-j | open_unexamined | Its next_action is C4's rank arm in plain form (see delta table). C4's E and B restate its "no excess confirms the known constant factor" outcome for the top-form arm. |
| 4 | 2-5 | KR-IC-5a43e5, LEAD-ICP-construction-normal-form, KR-IC-1fcdbc, KR-IC-fbdb61 | mixed | construction-normal-form (open_unexamined) is a dedup normal form; C4's "fibre over S~_top" would be one class of it. No collision. 1fcdbc: char-2 summation algorithms remain slower than rho. |
| 5 | 1 | LEAD-ICE-chained-semaev-dreg-vs-semiregular | open_next_step | Boolean chained S_3 d_reg against a semi-regular null; which null is right is contested. Shares only the matched-null discipline. Different object. |
| 5 | 2-5 | KR-IC-fbdb61, KR-IC-889857, KR-IC-5a43e5, LEAD-ICE-descent-closure-degree-at-scale | mixed | as above. |
| 5 | 6 | LEAD-ICE-prime-field-semaev-solving-degree | closed_known | B2 itself (beta_work 0.797 / 0.647 against 0.30). C4 does not touch it. |
| 6 | 1 | LEAD-ICP-xline-symmetry-special-j | open_unexamined | as run 4. |
| 6 | 2 | LEAD-ICP-coincidence-harvest-structured-base | open_next_step | Pair-sum coincidence excess kappa of structured bases. Different mechanism. |
| 6 | 3 | LEAD-ICE-chained-semaev-dreg-vs-semiregular | open_next_step | as run 5. |
| 6 | 4 | LEAD-RHO-automorphism-class-walks | closed_known (literature) | Ceiling sqrt|Aut|. C4's Corollary E (folding only relates targets) is consistent with it and does not exceed it. |
| 6 | 5 | LEAD-ICB-multi-target-and-portfolio | closed_obstructed (theorem) | Multi-instance bound; different mechanism. |

What C4 does that the forecloses phrases of the hits do not cover: (i) an all-m proof of the monomial top form (the lead rows record only the measured m = 2, 3 profile and the closed form), (ii) the top-form degree-of-regularity closed form, (iii) the explicit weighted-grading statement that the scaling action preserves the top-form projection, (iv) pointing the fall_dim meter at special-j and isogenous cells. What it does that they DO cover: first fall degree of the digit-presented system (digit lead), special-j degeneration and automorphism folding (xline lead, special-j lead), curve-model invariance (EXO model lead, for the first-fall level).

Closed-lead check (strict reading): the closed hits are LEAD-EXO-curve-model-representation (listed in the run 4 output), LEAD-ICE-prime-field-semaev-solving-degree, LEAD-STR-isogeny-transport-preprocessing, LEAD-RHO-automorphism-class-walks, LEAD-ICB-multi-target-and-portfolio. C4 does not answer any of their revisit_when clauses and does not claim to. For LEAD-EXO-curve-model-representation, C4's B is an all-m reason, inside the Weierstrass shape, for a first-fall-level invariance of the kind that lead measured at m = 2, 3 (d_reg = 2, Weierstrass against twisted Edwards); its forecloses phrase "curve model changes solving degree" concerns the solving degree, which C4 does not address, and Edwards is not covered. So C4 is not a duplicate of any closed lead, but it also cannot reopen one.

## Standing obstructions: quoted rows (obstruction.statement as written in the YAML)

C4 declares so_codes_touched = SO-ENDO, SO-ISO, SO-ALGFB and says it escapes none. I confirm that reading: it escapes none of them.

SO-ENDO, LEAD-STR-endo-scalar-action-generic (closed_obstructed, kind theorem): "For G of prime order N, End(G) = Z/N, so every endomorphism-image oracle is simulable by group operations and Shoup's bound applies (KN-FIND-b7e091, EV-GGM-79e710, DEC-20260804-3b4258). Augmenting the witness lattice with r eigenvalues leaves the index at N and the meet-in-the-middle exponent at 1/2 (H-ENDO-001). The one EV-ENDO-001 contradiction (first minimum exactly 1 on the J0 cells, by Vieta 1 + lambda_2 + lambda_3 = 0) is a certificate-void k-independent vector. It does not touch the exponent. Scope: any prime-field or binary curve, any size, prime-order subgroup." C4's E lives in the non-generic Groebner / Macaulay solver class, outside that GGM statement, but reaches the same constant-factor conclusion.

SO-ISO, LEAD-STR-isogeny-class-generic-invariance (closed_obstructed, kind theorem; the row has no Scope clause): "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (+-5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve." Its revisit_when names a level-dependent step-cost change as a constant belonging to LEAD-STR-class-representative-ic-selection.

SO-ALGFB, LEAD-ICP-algebraic-membership-factor-base (closed_obstructed, kind theorem): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B." C4 uses the digit (auxiliary-variable) presentation, not a bounded-degree algebraic base, and changes no membership degree.

Also relevant, not in the SO list: LEAD-EXO-curve-model-representation (closed_obstructed, measured): "Model-native PDP solving degree is invariant (d_reg = 2) between Weierstrass Semaev and twisted Edwards at m=2 and m=3, with Edwards a constant factor larger (EV-REP-001, EV-REP-002 replicated); the Kummer line is Bezout-optimal among coordinates E -> P^1 and the model lever is capped by a one-line degree argument (IDEA-20260905-d0fee4, IDEA-20260913-11d3cb, proposals). Exponent lever closed; at most constant factors (Hessian coordinate factor <= 2) remain." And LEAD-ICE-prime-field-semaev-solving-degree (closed_known, literature): "... beta_work(B1) = 0.797 on interval and random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold, 36/36 cells, 105/105 FGLM checks (EV-SDEG-4a1c3d, strong) ...".

## N2 Known results: raw outputs of python3 tools/build_frontier_map.py --match

### N2 run 1

Command: python3 tools/build_frontier_map.py --match "weighted homogeneity proves the leading form of the summation polynomial is a curve-free monomial so first fall degree is curve independent"

```
KR-IC-f5c584  score=22  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-889857  score=19  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-fbdb61  score=19  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-5a43e5  score=10  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-955fd6  score=10  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-53c89f  score=10  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-49c882  score=6  [known_bound/conjectured]  Quasi-subfield polynomials
    sources: KN-LIT-0a321c, KN-LIT-4fe9d2
```

### N2 run 2

Command: python3 tools/build_frontier_map.py --match "prove the top-degree part of the Semaev polynomial does not depend on the curve or the target"

```
KR-IC-5a43e5  score=8  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-889857  score=8  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-5931ee  score=7  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-955fd6  score=6  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-53c89f  score=6  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-755e35  score=6  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-791cb7  score=5  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
```

### N2 run 3

Command: python3 tools/build_frontier_map.py --match "model-native PDP first fall degree and degree of regularity invariant across special j isogeny class and curve model; the lever is capped by a degree argument"

```
KR-IC-889857  score=19  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-f5c584  score=19  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-755e35  score=19  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-fbdb61  score=16  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-791cb7  score=15  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-5ea2f8  score=10  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-RHO-53c89f  score=10  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-0d2021  score=8  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
```

### N2 run 4

Command: python3 tools/build_frontier_map.py --match "weighted homogeneous summation polynomial leading form cuspidal G_a Weierstrass scaling automorphism folding top-form invariants"
(phrasing supplied by the gate author, not one of the three given match_phrasings)

```
KR-IC-5a43e5  score=9  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-fbdb61  score=8  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-5931ee  score=6  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-889857  score=4  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
```

### N2 run 5

Command: python3 tools/build_frontier_map.py --match "Semaev summation polynomial homogeneity leading form degree of regularity closed form top-degree component"
(phrasing supplied by the gate author, not one of the three given match_phrasings)

```
KR-IC-fbdb61  score=18  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-IC-889857  score=17  [dispute/disputed]  Subexponential binary ECDLP under the first fall degree assumption
    sources: KN-LIT-005, KN-LIT-023, KN-LIT-fa346d, KN-LIT-71b758, KN-LIT-7607, KN-LIT-7604, KN-LIT-8d516e, KN-LIT-006
KR-IC-5a43e5  score=15  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-f5c584  score=11  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-IC-5931ee  score=9  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-0d2021  score=8  [known_bound/proven]  Modern Gröbner-basis complexity refinements
    sources: KN-LIT-27201d, KN-LIT-deca10, KN-LIT-c14d68, KN-LIT-14f2e0
KR-IC-1fcdbc  score=8  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-955fd6  score=7  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
```

### N2 run 6

Command: python3 tools/build_frontier_map.py --match "automorphism zeta x maps system of R onto system of omega R folding relates targets only"
(phrasing supplied by the gate author, not one of the three given match_phrasings)

```
KR-RHO-0528e7  score=4  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-46c2c6  score=3  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-6239aa  score=3  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
KR-IC-5ea2f8  score=2  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-RHO-53c89f  score=2  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
```

N2 reading (KRMAP rows opened: KR-IC-5a43e5, KR-IC-fbdb61, KR-IC-955fd6, KR-IC-f5c584, KR-IC-0d2021, KR-RHO-755e35, KR-IC-5931ee, KR-IC-889857). No KR row states a curve-free top form of S_{m+1}, a weighted-homogeneity statement, or an invariance of first-fall / d_reg across j, isogeny class or model for algebraic solvers. KR-IC-5a43e5 records only the recursion S_m = Res_X(S_{m-k+1}, S_{k+1}) and the per-variable degree 2^{m-2}. KR-IC-fbdb61 records that solving degree, last fall degree and degree of regularity are distinct (Caminata-Gorla; Semaev-Tenti). KR-IC-955fd6 records symmetry and torsion speedups (about 2^{omega(n-1)}). KR-RHO-755e35 records isogeny equivalence for generic methods. Verdict from N2 alone: known_result does not trigger. It stays conditional on the lexical-miss caveat, and one literature relative exists (Kousidis-Wiemers, characteristic 2; see Citations), which is why the sentence "no source states the odd-characteristic all-m statement" is a statement about what I found, not about the literature.

## N3 Ledger: grep of ledger/.index/{proposals,hypotheses}.jsonl

Method: a python scan of the two index files (script saved as scout/ledger_grep.py), counting how many of the given terms occur anywhere in each index record (case-insensitive), listing the top records per term set with id, status, area and the first 100 characters of the claim (or mechanism or title when the claim is empty). The index fields are truncated summaries, so a lexical miss here is weak evidence. Raw output follows, unedited.

```
## grep set A: weighted homogene | isobaric | leading form | top form | top-form | cuspidal | H-TOP
=== proposals.jsonl
3  IDEA-20260903-e1e38b  [proposed/None]  SETTING. Fix m >= 2, p > 3, E over F_p non-singular, an affine target R with x-coordinate x_R, the b
1  IDEA-20260807-aabd67  [proposed/None]  (A) THE ALGEBRAIC FACT, DERIVED HERE AND USED AS BOTH MECHANISM AND INSTRUMENT SELF-TEST. Division p
1  IDEA-20260811-3e08e0  [proposed/None]  (A) THE LOCUS IS A TWIST PAIR, EXACTLY. Fix a weight-12 form alpha a^3 + beta b^2 with 27 alpha - 4 
1  IDEA-20260816-a67f97  [proposed/None]  (A) The archived meter is described in EXP-ALPF-011's own text as a 'validated nontrivial-syzygy / B
1  IDEA-20260903-751062  [proposed/None]  (A) WHAT THE LEDGER SAYS AND WHAT THE ARCHIVE SAYS. EV-ALPF-001's observation line for EXP-ALPF-011 
1  IDEA-20260905-24d827  [proposed/None]  SCOPE: ordinary prime-field short-Weierstrass curves, p in 2^12..2^32, decomposition arity m in {2,3
1  IDEA-20260905-a6f98e  [proposed/None]  SCOPE: symmetrized binary pdp of SRC-SATIC-TRIMOSKA-2019 (m = 3, l in 3..8, n in {3l-1, 4l}) in its 
1  IDEA-20261018-70caad  [proposed/None]  Hand-derived, nothing executed. In the binary 2-decomposition system F_r(x1,x2)=b (x1,x2 in V, dim k
=== hypotheses.jsonl
2  H-PFDR-4148b8  [specified/PFDR]  TRACKED OBJECT: the top-form class S~_top in A_delta, followed through the Macaulay computation by g
1  H-PFDR-c88f14  [specified/PFDR]  THE LAST-FALL CLOSURE AS AN INSTRUMENT. Fix D. Start from W_0 = the degree-<= D Macaulay row space o
1  H-PFDR-e02f3b  [specified/PFDR]  TRACKED OBJECT: the pair (d_ff, localization bit) of the top-form syzygy module -- the first degree 

## grep set B: curve-free | curve-independent | curve independent | weight 2 | scaling | G_a | additive group | cusp
=== proposals.jsonl
1  IDEA-20260725-006  [mechanism/None]  Part A (correction, verified against committed data). The degree-4 witness recorded in experiments/E
1  IDEA-20260803-202a15  [proposed/None]  THIS PROGRAMME HAS EXACTLY ONE LIVE, UNEXPLAINED, POSITIVE-SIGNAL MEASUREMENT IN THE ENTIRE ECDLP LI
1  IDEA-20260807-5ddccf  [proposed/None]  (A) THE TWO SEMI-INVARIANCE FACTS, WITH THEIR BICONDITIONALS. For S_3(x1,x2,x3) = (x1-x2)^2 x3^2 - 2
1  IDEA-20260811-4a55dd  [proposed/None]  (A) THE STRUCTURAL CLAIM, STATED CONDITIONALLY AND WITH ITS ESCAPE NAMED. Let M = H_1(X_0(N), C, Z) 
1  IDEA-20260811-cd7c10  [proposed/None]  (A) THE IDENTITY AND ITS FRACTIONAL PART. By Deuring, for an ordinary trace t with gcd(t, p) = 1 the
1  IDEA-20260811-dcbea4  [proposed/None]  (A) THE TWO-SIDED SIZE IDENTITY. For a CM point of discriminant D, the largest archimedean conjugate
1  IDEA-20260815-ad4b55  [proposed/None]  Groebner solving degree and cost depend strongly on the monomial order, and the lane fixes one by co
1  IDEA-20260815-bd3fae  [proposed/None]  RQ-ECDLP-001 asked whether toy S_3 decomposition measurement is stable and cheap enough to justify s
1  IDEA-20260816-552e4c  [proposed/None]  (A) In an approximate homomorphic scheme the value a decryption returns is the message plus an error
1  IDEA-20260816-8ee479  [proposed/None]  (A) A deficit model earns the right to be called predictive only if the integer it computes moves wi
1  IDEA-20260820-cf1215  [proposed/None]  For two fixed public signing domains, aliasing the encoded domain tag at one declared hash or sample
1  IDEA-20260828-262f5c  [proposed/None]  eprint.iacr.org/2026/980 (retrieved, unverified beyond an abstract-level summary) reports a key-inde
1  IDEA-20260829-228ce4  [proposed/None]  Every proposal filed against this RQ prices the KEY-RECOVERY instance (2-QCSD, length 2n, weight 2w)
1  IDEA-20260829-359945  [proposed/None]  Every quantum ISD algorithm known to this corpus sits at one of two points: Grover-Prange, which cos
1  IDEA-20260830-8a767e  [proposed/None]  THE OBLIGATION. For a cover X -> B over F_p there is an exact sequence 1 -> G_geom -> G_arith -> Gal
=== hypotheses.jsonl
1  H-AES-5b6c2a  [specified/AES]  IDEA-20260828-262f5c Stage 0 freezes n=3 on the proposal's own identity names. Title: Cross-round sc
1  H-ALBIN-006  [analyzed/ALBIN]  Historical Autolab experiment contract + script + retained result artifacts, ported without re-execu
1  H-DRINF-cc79bb  [approved/DRINF]  The additive group is the ambient object. Phi is a ring homomorphism from F_3[T] into additive polyn
1  H-ECDLP-12bfd0  [specified/ECDLP]  IDEA-20260814-92f825 tracks the public overlap fingerprint and its exhaustive toy fiber. Stage 0 fre
1  H-ECDLP-15d016  [specified/ECDLP]  IDEA-20260906-e07475 Stage 0 hard gate is whether a declared feature plus one public action splits a
1  H-ECDLP-aecab6  [specified/ECDLP]  IDEA-20260905-579fcc (M1) says a shift multiset of x is injective unless S is centrally symmetric, i
1  H-ECDLP-e9d9bb  [specified/ECDLP]  Admissible short-Weierstrass unit scaling multiplies x by u^2 and A by u^4, so the ratio x^2/A is un
1  H-ICEX-357d9d  [proposed/ICEX]  The ideal and its variety are order-independent, so the underlying problem does not change with the 
1  H-JINV-c9c8ef  [specified/JINV]  PAIR (representation, Sigma), carried from IDEA-20261006-79bd0d. The representation is the scaling p
1  H-PFDR-724ad2  [proposed/PFDR]  A VERIFICATION PROTOCOL, NOT AN EXPERIMENT, AND DELIBERATELY NOT FORCED INTO ONE. Nothing here is sa
1  H-PFDR-727bfc  [specified/PFDR]  (From IDEA-20261017-078074.) Pair (R1 x-labels of points with known integer coefficients, Sigma = in

## grep set C: d_ff | first fall | degree of regularity | Wilson | p-rank | Caminata
=== proposals.jsonl
2  IDEA-20260731-009  [measurement/None]  The first-fall degree d_ff and Macaulay-bound degree d_reg of Semaev-shaped multihomogeneous systems
2  IDEA-20260905-df55e9  [proposed/None]  A certificate that binds the polynomial presentation, named degree invariant, admissible parameter d
2  IDEA-20260905-e6e2e5  [proposed/None]  For the m=2,d=2 prime-field binary-digit presentation with s>=2 and 2^s<=p, a verified first-fall la
1  IDEA-20260806-e4f96e  [proposed/None]  (A) WHAT THE PROGRAM MEASURES TODAY, AND WHY IT IS NOT A BOUND. KN-TECH-004 and KN-TECH-011 record t
1  IDEA-20260807-f6137c  [proposed/None]  (A) WHY AN AUDIT LANE OWES A CLOSURE. RQ-INSTR-f8faa0's decision target is that an instrument that c
1  IDEA-20260813-6e47e8  [proposed/None]  For the preregistered toy plain-UOV slice, saturating each same-instance attack ideal by the complem
1  IDEA-20260815-05c761  [proposed/None]  GOAL-SDEG-001 must deliver a scoped C_decomp(p,m) as the NUMERATOR of the ICEX exponent comparison. 
1  IDEA-20260816-6a7fa4  [proposed/None]  (A) EV-ALPF-001 states plainly that certificates were not re-verified and that claim_tier toy is a h
1  IDEA-20260816-746055  [proposed/None]  (A) The ALPF campaign's central output is a per-cell binary label -- fires / quiet, SURVIVED / SCOPE
1  IDEA-20260816-c1314e  [proposed/None]  (A) Every ALPF conclusion is stated at toy scale and every use of it presumes, silently, that the be
1  IDEA-20260826-2259f8  [proposed/None]  (A) THE INSTRUMENT GAP. The lane's model question was answered by a degree-of- regularity meter that
1  IDEA-20260828-661a28  [proposed/None]  Steiner (arXiv 2402.07852 / ePrint 2024/313), retrieved this session at abstract level only, develop
1  IDEA-20260903-399a18  [proposed/None]  (A) WHAT EXISTS AND WHAT DOES NOT, AS FLOORS. RQ-PFDR-ae2fba's decision target is a per-representati
1  IDEA-20260903-751062  [proposed/None]  (A) WHAT THE LEDGER SAYS AND WHAT THE ARCHIVE SAYS. EV-ALPF-001's observation line for EXP-ALPF-011 
1  IDEA-20260913-41c4f0  [proposed/None]  Nagao ePrint 2015/984 Theorem 1 states that under the first fall degree assumption ECDLP over F_{2^n
=== hypotheses.jsonl
2  H-PFDR-4148b8  [specified/PFDR]  TRACKED OBJECT: the top-form class S~_top in A_delta, followed through the Macaulay computation by g
1  H-ALPF-001  [analyzed/ALPF]  Historical Autolab experiment contract + script + retained result artifacts, ported without re-execu
1  H-ECDLP-60de36  [rejected_scoped/ECDLP]  PKM (PKC 2016) heuristic: a factor base with a low-degree, many-variable description (like a vector 
1  H-ICPERF-a5f550  [approved/ICPERF]  The proposal says the matrix size is the binomial in the variable count and the degree of regularity
1  H-MLKEM-677f84  [specified/MLKEM]  IDEA-20260828-661a28 Stage 0 freezes n=2 on the proposal's own identity names. Title: Does ML-KEM's 
1  H-PFDR-232b3a  [specified/PFDR]  For exact squarefree multipliers of degree D-4, construct the full reduced product map U_D and its d
1  H-PFDR-e02f3b  [specified/PFDR]  TRACKED OBJECT: the pair (d_ff, localization bit) of the top-form syzygy module -- the first degree 
1  H-SEMBIN-2d7708  [specified/SEMBIN]  The paper states the phenomenon and does not measure it. End of Section 4.5.1: "the maximal degree(r
1  H-SEMBIN-4a80f3  [weakened/SEMBIN]  Theorem 1 is arithmetic once its inputs are fixed, so the whole distance between "polynomial time al
1  H-SEMBIN-8e8bef  [approved/SEMBIN]  OBJECT FRAME. Representation R1: Boolean coordinates of the Weil-descended chained S_3 system (eq. (
1  H-SEMBIN-934774  [approved/SEMBIN]  Recombination by an invertible M preserves the F_2-span of the generators (at the witness, checked a
1  H-SEMBIN-d8c4fe  [approved/SEMBIN]  These are MEASUREMENT1's claims, carried over unchanged so that the run tests them rather than fits 
1  H-UOV-f58323  [proposed/UOV]  Take the intersection-attack system as M quadratic equations in N variables over F_q. The published-

## grep set D: semi-invarian | equivarian | weight-12 | Aut | zeta
=== proposals.jsonl
2  IDEA-20260807-1ea327  [proposed/None]  (A) THE INVARIANT RING, EXACTLY. For E/F_p with j = 0, i.e. a = 0 and E : y^2 = x^3 + b with p = 1 m
2  IDEA-20260807-4d7e8e  [proposed/None]  (A) THE THEOREM. Let p > 3 with p = 1 mod 3, let zeta be a primitive cube root of unity in F_p, and 
2  IDEA-20260807-eeb226  [proposed/None]  (A) THE GRADING, EXACTLY. For E : y^2 = x^3 + b over F_p with p = 1 mod 3, S_3(x1,x2,x3) = x3^2 (x1-
1  IDEA-20260805-5194f9  [control/None]  SelfTargetMSIS's concrete hardness is quoted as the minimum over two attack arms that share no resou
1  IDEA-20260805-591f9d  [measurement/None]  SelfTargetMSIS at ML-DSA parameters is an inhomogeneous short-vector problem whose entire difficulty
1  IDEA-20260805-9a2b09  [control/None]  GOAL-XEDN-001 exists to test whether a coefficient bound survives the REMOVAL of the mu_3 automorphi
1  IDEA-20260807-02b7b2  [proposed/None]  (A) THE ELEMENTARY FACT, STATED SHARPLY. Let E/F_p be ordinary with End_{F_p}(E) = O and Frobenius p
1  IDEA-20260807-0e4d83  [proposed/None]  (A) THE SETTING. E/F_p with j = 0 (a = 0), p = 1 mod 3, zeta a primitive cube root of unity in F_p, 
1  IDEA-20260807-267b95  [proposed/None]  (A) THE ABSENCE THIS ADDRESSES, STATED FROM THE RECORD. DEC-20260727-009 R3 records, of this entire 
1  IDEA-20260807-45a69f  [proposed/None]  (A) WHY THIS IS THE ONLY EXPONENT-SHAPED IDEA IN THE LANE. Every other L5 proposal is capped at a co
1  IDEA-20260807-5ddccf  [proposed/None]  (A) THE TWO SEMI-INVARIANCE FACTS, WITH THEIR BICONDITIONALS. For S_3(x1,x2,x3) = (x1-x2)^2 x3^2 - 2
1  IDEA-20260807-61049d  [proposed/None]  (A) THE FREE RELATIONS EXIST AND ARE ELEMENTARY. Let E : y^2 = x^3 + b over F_p, p = 1 mod 3, zeta a
=== hypotheses.jsonl
1  H-AUXIN-7c52b2  [proposed/AUXIN]  For prime r and nonzero x, choose a certified primitive zeta in F_r. Supplied Q_i=[x^d_i]P with d_i 
1  H-BINSTD-74b002  [supported/BINSTD]  OBJECT FRAME. Representation: x-coordinate in a fixed F_2-basis (R1 of RQ-ECDLP-623a32), with basis 
1  H-BINSTD-add204  [approved/BINSTD]  OBJECT FRAME. Representation R1: relation row vector over the factor base, in raw (dim B) or Z/n-Fou
1  H-BINSTD-f2512a  [approved/BINSTD]  The proposal prices a tau-adic pattern count by a binomial. This contract checks that count. It does
1  H-ECDLP-15d016  [specified/ECDLP]  IDEA-20260906-e07475 Stage 0 hard gate is whether a declared feature plus one public action splits a
1  H-ECDLP-2f1033  [specified/ECDLP]  The Cunningham SNFS exploited that 2^c - 1 = prod_{d | c} Phi_d(2) and that Z[zeta_c] maps onto Z/N:
1  H-EQIC-70a21a  [proposed/EQIC]  The mu_3-action x -> z x on the x-line of a j = 0 curve is linear and by scalars, so its invariant r
1  H-EQJ-7e870f  [proposed/EQJ]  EV-EQJ-001 rejected the isotypic linear-algebra cost mechanism cleanly - exactly 4 of 10 isotypes ca
1  H-FROB-24f425  [proposed/FROB]  Object: an equivariant Macaulay map decomposed into C_n character modules. Operation set Sigma: simu
1  H-FROB-73df22  [proposed/FROB]  ARM A rests on two facts. First, S_{m+1} for a curve over F_q has F_q-coefficients, so Frobenius on 
1  H-HAWK-44e496  [specified/HAWK]  IDEA-20260808-b1358c Stage 0 freezes n=3 on the proposal's own identity names. Title: Q(zeta_2n) has
1  H-ICEX-51839b  [proposed/ICEX]  THE OBJECT AND ITS PROJECTION. The projection is (fixed curve over Q, prime p) onto (a_p, D_0, f). I
```

Records that may be the same object (id | status | first 100 characters of the claim, title when the claim is empty):

| id | status | claim (100 chars) |
| --- | --- | --- |
| IDEA-20260903-e1e38b | proposed | SETTING. Fix m >= 2, p > 3, E over F_p non-singular, an affine target R with x-coordinate x_R, the b |
| H-PFDR-4148b8 | specified | The first fall degree of the d = 2 digit-presented Semaev system is a closed form in (m, s) alone -- |
| H-PFDR-e02f3b | specified | The one recorded prime-field early fall (EXP-ALPF-011 e-ring, quoted by EV-ALPF-001 and RQ-PFDR-ae2f |
| IDEA-20260903-751062 | proposed | (A) WHAT THE LEDGER SAYS AND WHAT THE ARCHIVE SAYS. EV-ALPF-001's observation line for EXP-ALPF-011  |
| H-PFDR-232b3a | specified | Separate top-kernel onset from nonzero survival in the prime-digit first fall |
| IDEA-20260905-e6e2e5 | proposed | For the m=2,d=2 prime-field binary-digit presentation with s>=2 and 2^s<=p, a verified first-fall la |
| IDEA-20260905-df55e9 | proposed | A certificate that binds the polynomial presentation, named degree invariant, admissible parameter d |
| IDEA-20260811-3e08e0 | proposed | (A) THE LOCUS IS A TWIST PAIR, EXACTLY. Fix a weight-12 form alpha a^3 + beta b^2 with 27 alpha - 4  |
| H-JINV-b3b975 | specified | Stage 0 verdict degeneration divisor decided counting rather identities — n=2 — before any later sta |
| IDEA-20260807-aabd67 | proposed | (A) THE ALGEBRAIC FACT, DERIVED HERE AND USED AS BOTH MECHANISM AND INSTRUMENT SELF-TEST. Division p |
| IDEA-20260807-5ddccf | proposed | (A) THE TWO SEMI-INVARIANCE FACTS, WITH THEIR BICONDITIONALS. For S_3(x1,x2,x3) = (x1-x2)^2 x3^2 - 2 |
| IDEA-20260807-1ea327 | proposed | (A) THE INVARIANT RING, EXACTLY. For E/F_p with j = 0, i.e. a = 0 and E : y^2 = x^3 + b with p = 1 m |
| H-PFDR-ebec07 | proposed | The x-coordinate map is the degree-two quotient by inversion, so any Mobius transformation of the x- |
| H-ECDLP-e9d9bb | specified | F = x^2/A on a unique n-torsion section is invariant under admissible short-Weierstrass unit scaling |
| H-JINV-c9c8ef | specified | Scaling-automorphism counts 6 and 2 on two models over F_13 |
| IDEA-20260901-863e36 | proposed | Let E/F_p be an ordinary short-Weierstrass curve, P a point of PRIME order n, G = <P>, and let Gamma |
| IDEA-20260806-c5d183 | - | (A) THE THEOREM-SHAPED CLAIM, WITH ITS PROOF STATED IN THE CLAIM BECAUSE IT IS FIVE LINES. Let G = < |
| IDEA-20260916-c38e50 | proposed | (A) THE DECOMPOSITION. Let F_q have characteristic coprime to m! (so q > m suffices for q prime), le |

Full records opened (limit 3):

1. ledger/hypotheses/H-PFDR-4148b8.yaml, read in full. It is the hypothesis C4's self-kill-risk names. Contents that overlap C4: (D3) / HEUR-001 "H-TOP", the top form of S_{m+1}(x, x_R) is c*prod_k x_k^{2^{m-1}} for every m >= 2 and every affine target, "rigorous at m = 2 by expansion", m = 3 "forces the single monomial" from the archived EXP-ALPF-011 profile [4, 4, 4, 12], "a finite symbolic identity per m", validation EXP-PFDR-5726af, falsification condition "a symbolic computation of S_4 (or S_5) ... whose top homogeneous part is not the single monomial"; (D4) tensor-kernel identity plus Wilson, exactness conditional on H-WIL with p > s; (D5) numbers; (D6) "Nothing in (D4) uses a, b, x_R or p beyond p > s: the first fall is curve- and target-independent"; mechanism: the projection S~ -> S~_top discards sub-top terms "exactly where the curve coefficients, the target and the digit offsets live" and "propagates homomorphically under the Macaulay layer operation"; nearby-object controls (mixed-block map, non-monomial top form); the MEASUREMENT line defining fall_dim(D) = rank_full - rank_top over F_p; (D7) first fall is not a solving degree, sigma >= 1.
2. ledger/proposals/IDEA-20260903-e1e38b.yaml, read lines 1-470 of 794 (claim, mechanism, novelty screen, citations, assumptions, proof_search_map, object_first_candidate including its lossiness / propagation / null_object_control entries, start of discriminated_from; lines 471-794 were not read). Source of H-PFDR-4148b8. Its novelty_screen says "UNVERIFIED ... may be folklore in the Boolean-function literature" and that no corpus record computes an annihilator degree, a tensor-kernel decomposition or an inclusion-matrix rank for a decomposition system. It lists "symbolic at m = 4" as a proof obligation, so the program had H-TOP open at m >= 4 when that record was written.
3. ledger/proposals/IDEA-20260811-3e08e0.yaml, read lines 1-90 (claim, mechanism opening). Uses weighted homogeneity of S_m (weights on a, b) to force each degeneration locus to a single j-line point and reports |Div(S_m)| for m = 3, 4, 5. This is the program's prior use of the same scaling grading, at the (a, b) level.

Records seen through their index fields only (not opened): IDEA-20260807-1ea327, IDEA-20260807-5ddccf, IDEA-20260807-aabd67, H-PFDR-232b3a, IDEA-20260905-e6e2e5, IDEA-20260905-df55e9, H-PFDR-ebec07, H-JINV-b3b975, H-JINV-c9c8ef, H-ECDLP-e9d9bb, IDEA-20260901-863e36, IDEA-20260806-c5d183, IDEA-20260916-c38e50. The N3 conclusions that depend on them are therefore limited to what the index text shows.

N3 conclusion: the same object. H-PFDR-4148b8 plus IDEA-20260903-e1e38b contain C4's top-form statement, the curve- and target-independence of the first fall, the tensor / Wilson derivation, and the lossy-projection reading. They contain H-TOP as an open heuristic, not as a theorem. C4's new content over them is the proof of H-TOP for all m, Lemma W as the cause of the sub-top structure, the d_reg closed form (no hit), the G_a reading (no hit), and the all-m equivariance statement.

## N4 Notation change (representation, operation set)

C4's pair, as I read it: representation R2, the short-Weierstrass family as a weighted family over (a, b, x_R) with weights (4, 6, 2) and the digit-substituted x-coordinates; operation set Sigma = translation by factor-base elements (the Macaulay layer operation g -> g*S in the decomposition system) together with the G_m scaling action (x, x_R, a, b) -> (lambda^2 x, lambda^2 x_R, lambda^4 a, lambda^6 b) on instances. Trichotomy class: partial-action (IC is Class I). The tracked object is the top-form projection S -> S_top.

Check against the recorded rigidity results, in the new notation:

- IDEA-20260806-c5d183 (a projection of a prime-order group that propagates under the full translation action is constant or injective): C4's Sigma does not contain the full translation action, and C4 does not claim a lossy projection of G. The projection S -> S_top is a projection of the polynomial system, compatible with the Macaulay layer operation by the identity top(g*S) = g_top * S_top. That compatibility is the lossy-projection test already written for the same projection in H-PFDR-4148b8 (mechanism). So the pair (digit-substituted R2, Macaulay layer operation) is a recorded pair. The added Sigma element, the G_m scaling, is a groupoid of F_p-isomorphisms E_{a,b} -> E_{lambda^4 a, lambda^6 b}; on the group it acts by the identity up to isomorphism. Two cases: lambda generic, then the action is a change of coordinates (the object-frame document says a projection that loses nothing "is a change of coordinates and is not returned"); lambda in the stabiliser, then it is the Gamma <= (Z/n)^* action of IDEA-20260901-863e36 (negation, GLV quotients) with the canonicalisation cost as its one open number, and the conclusion "constant factor sqrt|Aut|" is KR-RHO-0528e7 and LEAD-RHO-automorphism-class-walks.
- IDEA-20260901-863e36 (propagation belongs to a projection paired with an operation set; the lossy objects that propagate under Sigma are the block systems of <Sigma>): consistent. C4 adds no block system of <Sigma> on the group.
- KN-FIND-ffe1df Theorem C (exactly sum-compatible bucket index is a surjective homomorphism onto a group of order dividing N): not engaged; C4 has no bucket filter and no combining rule.
- KN-OPEN-020 (bounded-degree algebraic factor bases over F_p are scoped out; the open class is high-degree, implicit-membership or target-dependent descriptions): C4 introduces no factor-base description. Its base is the digit-presented interval, membership a_i^2 = a_i, which is the ledger's own digit lane (auxiliary-variable description). C4 does not move that lane out of or into the scoped-out class.

Result: C4's pair is the ledger's existing pair with the scaling grading made explicit. It is not a new rigidity result and not a rigidity result in new notation either; it is a corollary-level refinement of recorded objects. The only statement not already in the records is that the top-form projection is compatible with the weighted grading, which is Lemma W.

## Citations and provenance

- I. Semaev, Summation polynomials and the discrete logarithm problem on elliptic curves, IACR ePrint 2004/031. Provenance: retrieved (abstract page fetched this session: title, author, abstract confirmed). The recursion and the per-variable degree are not re-verified here; KRMAP row KR-IC-5a43e5 carries them (abstract_read).
- A. Caminata, E. Gorla, Solving degree, last fall degree, and related invariants, arXiv 2112.05579 / ePrint 2021/1611 / J. Symbolic Comput. Provenance: retrieved at search-result level (title, authors, venue, and a snippet of Theorem 3.1 relating solving degree and degree of regularity). Definitions 1.3 / 1.4 and Theorem 5.2 as used by C4 are NOT re-verified here; they come from the program note KN-LIT-4e8513, as the candidate says.
- S. Kousidis, A. Wiemers, On the first fall degree of summation polynomials, J. Math. Cryptol. (2019), arXiv 1906.05594. Provenance: retrieved. The abstract page was fetched directly. The content of Section 3 (Lemma 3.1, Remark 3.3) was read only through the fetch tool's summary of the ar5iv HTML version (the PDF did not decode), so it is a secondary summary: characteristic 2, m >= 3, the authors expand the Sylvester determinant of the resultant recursion and track the monomial (x_1...x_m)^{2^{m-1}-1} x_{m+1}, with (x_1...x_m)^{2^{m-1}} appearing in the constant-term coefficient, and they do not claim it is the overall top-degree term of S_{m+1}; the curve-coefficient independence is not stated. Reading: a binary-field relative that exhibits top-degree monomials of S_{m+1} by resultant expansion. The odd-characteristic, curve-free, all-m statement was not found in it. This is a search-level statement, not a literature survey.
- R. M. Wilson, A diagonal form for the incidence matrices of t-subsets vs. k-subsets, European J. Combin. 11 (1990) 609-615. Provenance: recalled here. The ledger records it as retrieved at snippet level only (H-PFDR-4148b8 HEUR-002). Load-bearing for exactness of the d_ff closed form, not for the upper bound.
- Isobaric property of resultants (Cox-Little-O'Shea, Using Algebraic Geometry, ch. 3) and Silverman AEC III.1 (scaling isomorphisms). Provenance: recalled; not re-verified. They are the external ingredients of Lemma W and H-TOP.
- The web tools were available this session, so the Semaev and Kousidis-Wiemers items are marked retrieved above and the others stay recalled.

## Heuristics and conditionals (numbered; none is a measured outcome of mine)

- G1 (conditional): C4's proof of H-TOP for all m is correct as the candidate states (checked symbolically at m = 2, 3 and numerically at m = 4 over GF(1000003) and GF(2^61-1), per the candidate). I did not re-derive or re-run it. If it fails at some m, HEUR-001 stays a heuristic and the verdict loses its only unconditional advance.
- G2 (conditional): the top-form d_reg closed form is the cokernel counterpart of the recorded kernel computation and rests on the same H-WIL (p > s). Not checked by me.
- G3: no source stating the odd-characteristic, curve-free, all-m top form was found by the searches above; the searches were lexical (atlas, KRMAP, ledger index) plus two web lookups.
- G4: the ledger index holds truncated fields; records I did not open (listed above) may contain more overlap, in particular IDEA-20260807-5ddccf and IDEA-20260807-1ea327 for the equivariance statement at higher m.
- G5: I made no prediction about any measurement. The candidate's predictions P4-1 to P4-3 are its own and are not evaluated here.
- G6: nothing in C4 changes B2 (beta_work), B1 or any exponent; the candidate says predicted gain 0, and the record supports that reading.
