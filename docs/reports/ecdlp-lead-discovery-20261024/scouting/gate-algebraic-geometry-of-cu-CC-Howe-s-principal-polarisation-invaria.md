# Novelty gates N1-N4: CC Howe's principal-polarisation invariant of the trace-zero variety A_n (ECC2K-130 Jacobian carriers)

Gate run: 2026-10-25. Read-only on all repositories; everything written here is under this scout directory.
Labels: "retrieved" = fetched or read this session; "recalled" = from memory, unverified; "computed" = arithmetic I ran this session; "prediction" = expected value, not an outcome.

## Verdict (summary)

- verdict: advances_lead. Lead: LEAD-ICB-ecc2k130-jacobian-carrier (open_next_step). Same object (is the trace-zero part A of Res(E) isogenous to a Jacobian), and the candidate is a sharper next step for it: an existence filter (necessary condition) that prunes cells of the lead's toy ladder. It is not a new route and it does not move any exponent (the candidate itself says predicted gain 0).
- It is NOT `new`: the identical test ("Howe's principal-polarisability criterion on T_n for deployed n", with LMFDB lookups showing T_3 and T_5 have no principal polarisation) is already lead L9 in crypto research/ecdlp_leads_20261018/README.md (status "derived (partial)"), and the ECC2K-130 note (research/notes/ecc2k130/RESEARCH_ECC2K130_HYPERELLIPTIC.md section 8) and the toy-ladder README (research/ic_next10_20261014/10-torelli-toy/README.md, "h_A was not computed") both flag the principal-polarisation count as the missing piece. L9 is a source document in the crypto repo, not an atlas lead row and not a ledger record, so the atlas does not know it. What the candidate adds over L9: a closed-form rule from the Lucas sequence U_n(t,2), a sweep over prime n < 140, the claim that the rule agrees with LMFDB on 38/38 classes (not re-run by me), and a concrete re-plan of the ladder. All of that is conditional on the candidate's derivation, which I only partly re-checked (see section 5).
- It does not close n = 131: by the candidate's own rule (which I recomputed from the Lucas sequence) a PPAV exists in the n = 131 class. So the lead's closure at 131 stays on the codimension heuristic, and the candidate's H-C1 / H-C2 are heuristics.

## N1 Atlas collision

Environment: LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES exported as instructed; run from /Volumes/SSD990-2/crypto-autoresearcher; --limit 8.

Run 1 (match_phrasings[0])
```
$ python3 tools/lead_atlas.py --match "Howe principal polarization obstruction for the trace-zero variety Jacobian carrier" --limit 8
   17  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
    7  LEAD-TRF-second-torsion-direction            closed_obstructed  Reach a second N-torsion direction: nonequivariant trace-zero transfer, Kani/Robert graph kernels, Richelot gluing of E with E'
    6  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
    6  LEAD-STR-p192-class-cm-relations             closed_obstructed  P-192 isogeny class, smooth principal CM relations and loops
    6  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    4  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    4  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
    4  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery
```
Run 2 (match_phrasings[1])
```
$ python3 tools/lead_atlas.py --match "can the ECC2K-130 trace-zero abelian variety be the Jacobian of a curve" --limit 8
   24  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
    9  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    7  LEAD-TRF-second-torsion-direction            closed_obstructed  Reach a second N-torsion direction: nonequivariant trace-zero transfer, Kani/Robert graph kernels, Richelot gluing of E with E'
    6  KR-RHO-18cc42                                known_result       ECC2K-130: expected work and 2009–2010 implementation rates
    6  LEAD-ICB-composite-degree-c2pnb              open_next_step     Composite-degree ANSI X9.62 binary curves (c2pnb176/208/272/304/368): Gaudry-Diem n = 4 with a pi_16 orbit base
    6  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    5  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    5  LEAD-EXO-split-jacobian-projection           closed_obstructed  Split-Jacobian projected smoothness and the pair (P,Q) as a genus-2 divisor
```
Run 3 (match_phrasings[2])
```
$ python3 tools/lead_atlas.py --match "codimension heuristic Torelli rarity genus 130 to 300 curve carrying A evaluable Jacobian" --limit 8
   38  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
    9  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    9  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    8  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    6  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
    5  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    5  LEAD-TRF-odd-char-descent-smith-quartic      open_blocked       Odd-characteristic Weil descent onto genus 3, then Smith's isogeny to a plane quartic and Diem's q^{4/3} attack
    4  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
```
Run 4 (my own phrasing)
```
$ python3 tools/lead_atlas.py --match "principally polarised abelian variety Weil restriction Koblitz curve Jacobian of a curve Torelli" --limit 8
   18  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
   14  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
   10  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
   10  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
    8  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    6  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    6  KR-IC-e2d81b                                 known_result       ecGFp5 and degree-5 extension curves: published estimates
    6  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
```
Run 5 (my own phrasing, targets the Howe-for-T_n mechanism directly)
```
$ python3 tools/lead_atlas.py --match "Howe principal-polarisability criterion certified lower bound on cover genus for Koblitz trace-zero T_n LMFDB" --limit 8
   10  LEAD-ICB-ecc2k130-jacobian-carrier           open_next_step     ECC2K-130 via a Jacobian carrying the trace-zero abelian variety A (Torelli rarity heuristic)
    9  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
    8  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
    8  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
    7  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    7  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
    7  LEAD-TRF-same-field-genus-g-embedding        closed_obstructed  Embed E/F_p as an isogeny factor of a genus-g Jacobian over the same field (covers, quadric pencils, quartic/bielliptic models)
    6  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
```
Run 6 (my own phrasing, targets the crypto L8 etale route sitting next to L9)
```
$ python3 tools/lead_atlas.py --match "etale cover of a small-genus curve over F_2 with order-n automorphism whose twist contains E x T_n" --limit 8
    9  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    8  LEAD-TRF-jv-sieve-fp6-weak-class             open_next_step     Joux-Vitse cover-and-decomposition sieve on the weak class of E(F_{p^6}) (genus-3 cover), with the isogeny walk into the class
    6  LEAD-ICP-gfp5-odd-char-cover                 open_blocked       Odd-characteristic GHS/Diem cover applicability for EcGFp5, EcMasFp5 and their isogeny classes
    6  LEAD-STR-safecurves-parameter-audit          closed_known       SafeCurves-style parameter audits (twist security, completeness, ladder, cofactor, transfer rows)
    6  LEAD-TRF-cover-catalog-jacobian-transfer     open_blocked       Catalogued cover maps (1,940 prime quadratic pullbacks, 160 binary cubic pullbacks): executable pushforward and subgroup recovery
    6  LEAD-TRF-small-genus-cover-general           closed_obstructed  Find small-genus GHS/Kummer covers beyond the Joux-Vitse weak class (other configurations over F_{q^3}, F_{p^k} with k = 6, 10, 14)
    5  LEAD-ICP-xline-symmetry-special-j            open_unexamined    x-line symmetry groups, automorphism folding and summation-polynomial degeneration at special j
    5  LEAD-TRF-jv-nagao-genus2-cover-decomp        closed_dominated   Nagao decomposition on a genus-2 cover of E(F_{p^6}) (examples/jv_cover.rs), with F4 and sparse-FGLM engineering
```

### N1 reading: top hits of every run (lead YAML mechanism / obstruction / forecloses opened)

Distinct atlas rows in the top 5 of runs 1-6: LEAD-ICB-ecc2k130-jacobian-carrier (rank 1 in all six runs), LEAD-TRF-second-torsion-direction, LEAD-ICB-composite-degree-c2pnb, LEAD-STR-p192-class-cm-relations, LEAD-TRF-same-field-genus-g-embedding, LEAD-EXO-split-jacobian-projection, LEAD-TRF-cover-catalog-jacobian-transfer, LEAD-TRF-ghs-binary-composite, LEAD-TRF-odd-char-descent-smith-quartic, LEAD-TRF-jv-sieve-fp6-weak-class, LEAD-TRF-jv-nagao-genus2-cover-decomp, LEAD-TRF-small-genus-cover-general, LEAD-ICP-gfp5-odd-char-cover (plus KR rows, section N2). All YAMLs under /Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/.

1. LEAD-ICB-ecc2k130-jacobian-carrier, open_next_step (ic-binary). SAME OBJECT. Mechanism: if the 130-dimensional trace-zero part A of Res(E) were isogenous to an evaluable Jacobian of genus 130-300, plane/hyperelliptic IC there would cost about 2^37.2, 23.6 bits below rho; the closure "rests on a codimension heuristic (8,128), not a theorem". No obstruction row (it is open). next_action.step: toy ladder at the first faithful rungs n = 11 and n = 13, sampling curves of genus dim A to dim A + 2 over F_2 and testing whether the target polynomial divides P_C. best_measured: n = 5 no carrier through genus 8 (heuristic predicts about 0.42 classes, low power); n = 7 has 1,536 genus-7 hyperelliptic carriers from Weil-restriction structure that n = 131 lacks. forecloses: "ECC2K-130 trace-zero variety is a Jacobian", "genus 130 to 300 curve carrying A", "Torelli locus search for ECC2K-130". The candidate names this lead itself. It targets the lead's next_action (which cells to sample), not a different mechanism. Its Howe filter does not itself foreclose any of these three phrases at n = 131 (a PPAV exists there).
2. LEAD-TRF-second-torsion-direction, closed_obstructed (theorem, Balasubramanian-Koblitz; Scope: ordinary and supersingular curves over F_p, prime N). Different mechanism (second N-torsion direction, Kani/Robert graph kernels, Richelot gluing; trace-zero variety only as a torsion carrier). Not the same object; the candidate neither uses nor escapes it.
3. LEAD-ICB-composite-degree-c2pnb, open_next_step. Gaudry-Diem n = 4 decomposition on composite-degree ANSI curves with a pi_16 orbit base; its forecloses include "trace-zero variety decomposition breaks the ANSI c2pnb curves". Different mechanism (decomposition on the extension-field curve, no Jacobian carrier); the candidate's rungs are prime n (2 primitive mod n), where that lead does not apply.
4. LEAD-STR-p192-class-cm-relations, closed_obstructed. CM loops in the P-192 class; no overlap (lexical hit on "principal").
5. LEAD-TRF-same-field-genus-g-embedding, closed_obstructed (theorem). Statement: "Tate multiplicativity gives #Jac(C)(F_p) = N * #A(F_p) with #A = Theta(N^{g-1}); genus-g index calculus costs O~(q^{2-2/g}) >= q for g >= 2, at least a full exponent above rho's N^{1/2}; quadric-pencil and quartic models of E itself are isomorphic models with the same group. Scope: prime-field source curves, any same-field cover (DEC-20260902-4c82fd)." This is SO-COVER. The candidate's carrier has Jac(C) isogenous to A with #A(F_2) = r exactly (no N * #A inflation), over F_2 not over a prime field, so the Scope clause "prime-field source curves" excludes the setting and the Tate-multiplicativity inflation does not arise at genus = dim A. The lead's own price (2^37.2) already uses that. Note for genus dim A + 1 or + 2 the carrier is isogenous to A x B and #Jac(F_2) = r * #B(F_2), the inflation is by #B only, which is small for dim B <= 2; that is already inside the lead's "genus dim A to dim A + 2" window.
6. LEAD-EXO-split-jacobian-projection, closed_obstructed (proof). Statement: cross-genus Poincare-factor embedding cannot beat rho because the Hasse-Weil order inflation of the ambient Jacobian outweighs genus-2 IC savings (KN-FIND-61347e). Its revisit_when asks for "a same-field embedding whose ambient group order is O(N) rather than inflated". The carrier route at genus dim A is that exact case (ambient order = r), so it is the revisit_when trigger and is covered by the open lead, not a new object.
7. LEAD-TRF-cover-catalog-jacobian-transfer (open_blocked), LEAD-TRF-ghs-binary-composite (closed_known, literature: N prime is not weak under GHS / generalized GHS), LEAD-TRF-odd-char-descent-smith-quartic (open_blocked), LEAD-TRF-jv-sieve-fp6-weak-class (open_next_step), LEAD-TRF-jv-nagao-genus2-cover-decomp (closed_dominated), LEAD-TRF-small-genus-cover-general (closed_obstructed, proof; Scope: Kummer/GHS covers of the x-line in odd characteristic), LEAD-ICP-gfp5-odd-char-cover (open_blocked): all are explicit-cover (GHS/Kummer/Smith) or odd-characteristic leads. The candidate is not an explicit cover: it is an abstract existence filter on isogeny classes. None of their forecloses phrases covers "principal polarisation of the trace-zero variety" or "Jacobian in the isogeny class of Res(E)".

N1 collision statement. Same mechanism: yes, with LEAD-ICB-ecc2k130-jacobian-carrier only. The candidate is a sharper next step for that OPEN lead (it changes which cells are worth sampling and states a theorem-level exclusion for the rest), so advances_lead, not duplicate_of_lead: the lead's next_action is ladder sampling, and the Howe filter is not what it prescribes. What the candidate does that the forecloses phrases do not cover: it gives a necessary condition (a PPAV must exist in the class) that is decidable without any curve search, and that the lead's heuristic (codimension count with unspecified h) never uses. What it does not do: it forecloses nothing at n = 131.

Standing obstructions the candidate lists as touched (statements quoted from the lead rows):
- SO-TABLE (LEAD-ICB-generic-table-oracle, theorem): "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work ... Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged." The candidate's own escape claim (Mumford smoothness reads the representation, so it is not a group-operation/membership oracle) is the lead's premise too; but note the escape applies to the conditional route only, which needs a carrier plus an evaluable isogeny that nobody has. The candidate delivers neither, so nothing is escaped in practice; it is a pruning of the search for a carrier.
- SO-GEN (LEAD-RHO-generic-sqrt-lower-bound, theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group ... Scope: all generic algorithms, any field, any r." Escaped only through coordinate access on a carrier, same caveat.
- SO-FROB (LEAD-ICB-frobenius-orbit-factor-base, proof): "... At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty ... Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure." The candidate does not use a Frobenius-stable factor base on E, so SO-FROB is not engaged rather than escaped. Note the same fact (2 primitive mod 131) is what makes A_131 simple and its Weil polynomial irreducible, which Howe's theorem needs.
- SO-COVER (LEAD-TRF-same-field-genus-g-embedding): quoted in item 5 above.

## N2 Known results

Same six phrasings through python3 tools/build_frontier_map.py --match (default --limit).

Frontier run 1
```
$ python3 tools/build_frontier_map.py --match "Howe principal polarization obstruction for the trace-zero variety Jacobian carrier"
KR-IC-5ea2f8  score=4  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-791cb7  score=1  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-cd159a  score=1  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
```
Frontier run 2
```
$ python3 tools/build_frontier_map.py --match "can the ECC2K-130 trace-zero abelian variety be the Jacobian of a curve"
KR-IC-5ea2f8  score=9  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-RHO-18cc42  score=6  [record/reported]  ECC2K-130: expected work and 2009–2010 implementation rates
    sources: KN-LIT-661e97, KN-LIT-448a0c, KN-LIT-c75942, KN-LIT-63a5c5, KN-LIT-2b7e8e
KR-IC-791cb7  score=5  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-482ed3  score=4  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-755e35  score=4  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-955fd6  score=3  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-cd159a  score=3  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
```
Frontier run 3
```
$ python3 tools/build_frontier_map.py --match "codimension heuristic Torelli rarity genus 130 to 300 curve carrying A evaluable Jacobian"
KR-IC-791cb7  score=9  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-5ea2f8  score=8  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-a4dd54  score=6  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-482ed3  score=4  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-755e35  score=4  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
KR-IC-955fd6  score=3  [known_mechanism/heuristic]  Symmetries and torsion speed up point decomposition
    sources: KN-LIT-004, KN-LIT-bba0c6
KR-IC-cd159a  score=3  [known_negative/proven]  Xedni calculus and lifting to characteristic zero fail
    sources: KN-LIT-020, KN-LIT-021
```
Frontier run 4
```
$ python3 tools/build_frontier_map.py --match "principally polarised abelian variety Weil restriction Koblitz curve Jacobian of a curve Torelli"
KR-IC-5ea2f8  score=14  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-RHO-482ed3  score=10  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-IC-791cb7  score=8  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-46d822  score=6  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-e2d81b  score=6  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
KR-RHO-1c2928  score=6  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-b0fcda  score=5  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-fbdb61  score=5  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
```
Frontier run 5
```
$ python3 tools/build_frontier_map.py --match "Howe principal-polarisability criterion certified lower bound on cover genus for Koblitz trace-zero T_n LMFDB"
KR-RHO-1c2928  score=7  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-IC-a4dd54  score=6  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-RHO-482ed3  score=6  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-IC-5ea2f8  score=5  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-b0fcda  score=5  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-791cb7  score=4  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-13bf67  score=4  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-ea34b8  score=4  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
```
Frontier run 6
```
$ python3 tools/build_frontier_map.py --match "etale cover of a small-genus curve over F_2 with order-n automorphism whose twist contains E x T_n"
KR-IC-5ea2f8  score=9  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-791cb7  score=4  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-ae532f  score=4  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-e2d81b  score=4  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
KR-RHO-0528e7  score=4  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-482ed3  score=4  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-RHO-53c89f  score=4  [textbook_fact/proven]  Transfer attacks apply only to special curves
    sources: KN-LIT-084, KN-LIT-085, KN-LIT-087, KN-LIT-088, KN-LIT-089
KR-RHO-755e35  score=4  [textbook_fact/proven]  Isogenous curves are equally hard; isogeny walks do not find weak curves
    sources: KN-TECH-061, KN-LIT-171
```

### N2 reading

KR rows opened: KR-IC-5ea2f8 (GHS Weil descent and cover attacks; known_mechanism/proven; claims GHS is effective only for special fields/curves and that isogenies can move a curve into a vulnerable class), KR-IC-791cb7 (weak binary fields under GHS and generalized GHS with isogeny walks; heuristic; "N prime, and N not divisible by 3, 5, 6, 7, 8, not weak under either attack"; subfield curves are not weakened), KR-IC-a4dd54 and KR-IC-46d822 (hyperelliptic IC genus threshold; Gaudry n fixed) as the cost basis of the lead's 2^37.2. Rows from the map named in the other hits (KR-RHO-18cc42, KR-RHO-482ed3, KR-RHO-1c2928, KR-RHO-53c89f, KR-RHO-755e35, KR-IC-e2d81b, KR-IC-955fd6, KR-IC-cd159a) are rho, Koblitz-rho, transfer-textbook or xedni rows and none states anything about principal polarisations or Jacobians in an isogeny class.

Findings:
- No KR row states or uses Howe's principal-polarisation criterion, a Torelli/codimension count, or a non-existence statement of the form "no Jacobian lies in the isogeny class of Res(E) / of its trace-zero part". Word search of KRMAP.md and ATLAS.md for Howe, polariz, ppav gives zero hits.
- KR-IC-791cb7 and KR-IC-5ea2f8 are statements about explicit GHS-type covers (magic number m, genus 2^(m-1)-type formulas). "N prime is not weak" there means no small-genus GHS cover. It does not say there is no Jacobian in the class at some larger genus, which is the lead's question and the candidate's. So the candidate's content is not in the KR map.
- Howe's theorem itself is a literature theorem outside the KR map. The corpus holds the surrounding papers as sources (KN-LIT-144, Howe's isogeny classes with no principal polarizations; KN-LIT-1287, Rybakov on principal polarizations on products), but no KR row, lead or ledger record cites them (grep of knowledge/, ledger/.index). So: the theorem is known literature (provenance: retrieved, section 5); its application to A_n is not in the KR map; whether the application appears in the literature is only partly checked (two web searches, section 5).
- Therefore N2 does not give known_result for the candidate, but it does for its ingredient: the novelty claim cannot be "a new theorem". It can only be "the application to A_n, and the ladder re-plan".

## N3 Ledger

Index files: /Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/proposals.jsonl (2678 rows) and hypotheses.jsonl (2131 rows). Search was a case-insensitive regex over the title, claim/statement and mechanism fields of each index row (script: _howe_raw/ledger_grep2.py), 100-char claim shown. Output below is the raw result (first part proposals, second part hypotheses; each term block lists up to 30 hits).
```
##### proposals.jsonl
--- term /\bHowe\b/ : 0 hits
--- term /polari[sz]/ : 7 hits
  IDEA-20260808-40aab9 | The Kani / Robert higher-dimensional embedding - the single largest re | (A) WHAT THE MACHINERY NEEDS. The SIDH-breaking machinery (Castryck-Decru; Maino-Martindale; Robert)
  IDEA-20260808-fa1d80 | Tracked object: the split-quotient certificate. ECDLP is exactly the p | Let G = <P> of prime order N, Q = [k]P, and consider the abelian surface A = E x E with its product 
  IDEA-20260812-104e1a | The isogeny class DOES supply rank-2 rational N-torsion, so the blocke | Let E/F_p be ordinary with prime N = #E(F_p) and p not congruent to 1 mod N, and let S be a set of c
  IDEA-20260813-c9bec2 | Actual-map polar and Jacobian-pencil audit: test whether TCitH's publi | Once the primary TCitH/MQOM public-map generator and exact parameters are filed, the span of its pol
  IDEA-20260821-211586 | The Kani template's requirement is an INEQUALITY, so the obstruction i | SCOPE FIRST, AS THIS QUESTION'S CONSTRAINTS REQUIRE. Every technical statement about SQIsign below i
  IDEA-20260829-70258e | The Autolab p1243 auxiliary-discriminant Kani family tracks a polariza | (A) WHAT THE FAMILY ACTUALLY DOES. Kani-style embeddings need an auxiliary endomorphism of norm S = 
  IDEA-20260901-1ddfd4 | THE BALL MEET-IN-THE-MIDDLE COST EXPONENT IS a_g TIMES b_g OVER 2, WIT | (A) THE LOWER BOUND, RIGOROUS WITHIN THE FAMILY. Fix a dimension g and let A be a superspecial princ
--- term /\bppav/ : 0 hits
--- term /Torelli/ : 1 hits
  IDEA-20261024-a29e53 | Is the cover floor the genus floor? Which isogeny classes of Res_{K/F_ | K = F_{q^n}, E/K ordinary of trace t. The isogeny class of W = Res_{K/F_q}E has L-polynomial 1 - tT^
--- term /trace[- ]zero/ : 8 hits
  IDEA-20260805-2d2c41 | Heuristic 1 is stated for a uniformly random curve, and every route th | TWO ASSUMPTIONS SIT UNDER THIS CAMPAIGN'S ARITHMETIC AND NEITHER HAS BEEN STATED AS A HEURISTIC ANYW
  IDEA-20260806-a3ef00 | A FUNDAMENTALLY DIFFERENT DECOMPOSITION -- LOCAL-GLOBAL RATHER THAN DE | (A) THE CORPUS SAYS THIS IS THE THREAT AND HAS NEVER RUN THE CHECK. knowledge/literature/KN-LIT-7648
  IDEA-20260808-b5b9ca | Heuristic 1 restated as a smoothness-graded equidistribution statement | A trace-zero element alpha of the two-sided ideal P with Nrd(alpha) = pd satisfies alpha^2 = -pd, so
  IDEA-20260808-d8510c | The one unproven step in the only viable proof route for Heuristic 1 i | This program's own analysis (research/P13-HEUR-001/heuristic_analysis.md, Route (b)) established tha
  IDEA-20260808-f313da | The three successive minima of the trace-zero lattice are NOT independ | Every treatment of Remark 1 in this corpus, including catalogue C1-3's Siegel-Rogers pricing, models
  IDEA-20260922-8278db | THE TRACE-ZERO-VARIETY DECOMPOSITION LINE, NAIVELY EXTRAPOLATED TO THE | SETTING. E/F_q, q = 2^16, over F_{q^k}, k in {11,13,17,19,23} prime (audit). IDEA-20260906-a77711 Ar
  IDEA-20261006-752e51 | Trace-zero split of the j=1728 and j=0 models over F_7 | Over F_7, each of the six models y^2 = x^3 + A x with A in {1,2,3,4,5,6} is nonsingular and has trac
  IDEA-20261007-1300af | Trace-zero share of affine x-coordinates on a toy double-odd curve | On the smallest prime p' >= 3 such that F_{p'^5} contains both a nonsingular double-odd curve y^2 = 
--- term /abelian variet/ : 6 hits
  IDEA-20260808-40aab9 | The Kani / Robert higher-dimensional embedding - the single largest re | (A) WHAT THE MACHINERY NEEDS. The SIDH-breaking machinery (Castryck-Decru; Maino-Martindale; Robert)
  IDEA-20260812-104e1a | The isogeny class DOES supply rank-2 rational N-torsion, so the blocke | Let E/F_p be ordinary with prime N = #E(F_p) and p not congruent to 1 mod N, and let S be a set of c
  IDEA-20260829-70258e | The Autolab p1243 auxiliary-discriminant Kani family tracks a polariza | (A) WHAT THE FAMILY ACTUALLY DOES. Kani-style embeddings need an auxiliary endomorphism of norm S = 
  IDEA-20260901-1ddfd4 | THE BALL MEET-IN-THE-MIDDLE COST EXPONENT IS a_g TIMES b_g OVER 2, WIT | (A) THE LOWER BOUND, RIGOROUS WITHIN THE FAMILY. Fix a dimension g and let A be a superspecial princ
  IDEA-20260926-5c26f9 | THE DIMENSION-5 AND DIMENSION-6 WEIL-POLYNOMIAL CENSUS OVER F_2 FOR 13 | CEILING FIRST. This is a structural-emptiness certificate for one column of RQ-BINSTD-b6f698's table
  IDEA-20261024-a29e53 | Is the cover floor the genus floor? Which isogeny classes of Res_{K/F_ | K = F_{q^n}, E/K ordinary of trace t. The isogeny class of W = Res_{K/F_q}E has L-polynomial 1 - tT^
--- term /Honda|Weil polynomial/ : 3 hits
  IDEA-20260926-5c26f9 | THE DIMENSION-5 AND DIMENSION-6 WEIL-POLYNOMIAL CENSUS OVER F_2 FOR 13 | CEILING FIRST. This is a structural-emptiness certificate for one column of RQ-BINSTD-b6f698's table
  IDEA-20260926-80209d | THE TOY CONTROL LADDER FOR ALGEBRAIC-GROUP FACTOR BASES, at primes n i | CEILING FIRST. A control fixture for RQ-BINSTD-b6f698's table (owner by the R2 rule); no arity, no o
  IDEA-20261005-2f5c3f | Cartier-Manin rank splits ordinary, intermediate, and superspecial p-t | No Honda-Tate research question exists in ledger/questions (searched for Honda, group scheme, p-tors
--- term /Lucas|U_n\b/ : 3 hits
  IDEA-20260807-30868b | A NON-TRIVIAL SELF-PAIRING ON THE CRYPTOGRAPHIC SUBGROUP FORCES EMBEDD | (A) THE SHARP QUESTION. RQ-PAIR-21313f asks whether a CM-specific self-pairing exists that is comput
  IDEA-20260807-569c82 | THE PAIRING ORACLE IS THE CONSTANT ORACLE ON A PRIME-ORDER SUBGROUP, A | (A) THE ORACLE. PAIR(h_1, h_2) returns the pairing value of two handles from G, in mu_N inside F_{p^
  IDEA-20261024-5f08bd | General-prime floor lemma: single-orbit genus floor 2^(n-3-e(n)) (n-4) | For prime n >= 5 and branch quadruples on one sigma-orbit (r = n), m = #{zeta in mu_n : s_S(zeta) !=
--- term /isogeny class.{0,40}(Jacobian|genus)|(Jacobian|genus).{0,40}isogeny class/ : 1 hits
  IDEA-20261024-a29e53 | Is the cover floor the genus floor? Which isogeny classes of Res_{K/F_ | K = F_{q^n}, E/K ordinary of trace t. The isogeny class of W = Res_{K/F_q}E has L-polynomial 1 - tT^
--- term /(ECC2K|Koblitz).{0,60}(Jacobian|genus)|(Jacobian|genus).{0,60}(ECC2K|Koblitz)/ : 0 hits
##### hypotheses.jsonl
--- term /\bHowe\b/ : 0 hits
--- term /polari[sz]/ : 2 hits
  H-ALISO-43049a | Stage 0 autolab p1243 auxiliary-discriminant kani family tracks identi | Fix the exact count identity of IDEA-20260829-70258e before any later-stage claim. Stage 0 asserts o
  H-SQISIGN-1d9721 |  | SCOPE FIRST, AS THIS QUESTION'S CONSTRAINTS REQUIRE. EVERY TECHNICAL STATEMENT ABOUT SQIsign BELOW I
--- term /\bppav/ : 0 hits
--- term /Torelli/ : 0 hits
--- term /trace[- ]zero/ : 5 hits
  H-BINSTD-6e3bd4 | Trace-zero-variety Gaudry Arm B naive cost at five deployed c2pnb rows | SETTING. E/F_q, q=2^16, over F_{q^k}, k in {11,13,17,19,23} prime (analysis/binstd-curve-audit/). ID
  H-BINSTD-84fab0 | Trace-zero-variety Arm B on five c2pnb rows: naive charged cost is a r | CLAIM (certificate + cost-audit control; NOT a break). Setting: E/F_q with q=2^16 over F_{q^k}, k∈{1
  H-BINSTD-b5d435 | For the five composite-degree ANSI rows, the naive trace-zero cost q^{ | Let q = 2^16 and k in {11, 13, 17, 19, 23}, g = k - 1. Then (k-1)! equals the preregistered integers
  H-FROB-73df22 | Frobenius orbit ideals versus the complete trace-zero index-calculus p | Audit source armA disjointness/equivariance/invariant-degree predictions without assuming x-only fre
  H-SSIQ-8f34d8 | Stage 0 successive minima trace-zero lattice independent aubry-oyono-v | Fix the exact count identity of IDEA-20260808-f313da before any later-stage claim. Stage 0 asserts o
--- term /abelian variet/ : 4 hits
  H-BINSTD-6feaa2 | An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, c | CLAIM (structural certificate; HOLD-X3). KN-OPEN-095df5 excludes Couveignes-Lercier bases at n=131 f
  H-BINSTD-944a66 | Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB | SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of 
  H-FROB-ff99bf | No abelian variety over F_2 of dimension 5 or 6 has 131 dividing its p | CLAIM (falsifiable either way; both outcomes are results). For every abelian variety A of dimension 
  H-SQISIGN-1d9721 |  | SCOPE FIRST, AS THIS QUESTION'S CONSTRAINTS REQUIRE. EVERY TECHNICAL STATEMENT ABOUT SQIsign BELOW I
--- term /Honda|Weil polynomial/ : 3 hits
  H-BINSTD-6feaa2 | An exact Rolle-pruned Weil-polynomial census at g in {5,6} over F_2, c | CLAIM (structural certificate; HOLD-X3). KN-OPEN-095df5 excludes Couveignes-Lercier bases at n=131 f
  H-BINSTD-944a66 | Exact g=5,6 Weil-polynomial census over F_2 for 131 | h(3), with LMFDB | SETTING. KN-OPEN-095df5 asks whether a commutative algebraic group over F_2 has a rational point of 
  H-ISOU-c5bfea |  | In the complete F_p-isogeny class of a P-256-shaped toy curve (ordinary, prime order N, conductor f 
--- term /Lucas|U_n\b/ : 1 hits
  H-SEMBIN-934774 | Committed, hash-pinned code reproduces the exploratory exhaustive coun | Let d'_ff(F) = min{ D : new_falls(D) > 0 }, new_falls(D) = dim(V_D cap R_{<D}) - dim V_{D-1}, comput
--- term /isogeny class.{0,40}(Jacobian|genus)|(Jacobian|genus).{0,40}isogeny class/ : 0 hits
--- term /(ECC2K|Koblitz).{0,60}(Jacobian|genus)|(Jacobian|genus).{0,60}(ECC2K|Koblitz)/ : 0 hits
```

Additional term run separately (raw not pasted, count only): /ECC2K/ gives 27 proposal and 20 hypothesis hits, all about relation-finding, rho or Frobenius factor bases at n = 131, none about Jacobians or isogeny classes (the combined ECC2K/Koblitz with Jacobian/genus regex above gives 0 hits).

### N3 reading: records that may be the same object

- IDEA-20261024-a29e53 (RQ-PEXT-7c3e91, proposed 2026-10-24): "Is the cover floor the genus floor? Which isogeny classes of Res_{K/F_q}E hold a genus-n Jacobian, exhaustively at n = 3 ... and a Torelli-density exponent for general prime n". OPENED IN FULL. Nearest record. Same question family (does a genus-n Jacobian exist in the class of Res E, via Torelli plus Serre), but: odd characteristic and q = 2..5 toy, n = 3 enumeration, density heuristic e(n) = (-n^2 + 11n - 12)/4, no cost and no ECC2K-130. It lists as an assumption "the class contains an indecomposable ppav; to be checked per class at design", and its citation to Serre/Oort-Ueno/Howe-Nart-Ritzenthaler is marked recalled with verified_by null. It does not apply Howe's criterion to T_n of a Koblitz curve and has no Lucas-sequence rule. Relation: adjacent (shares the Torelli-density heuristic that the candidate's H-C1b also uses; the candidate's PPAV filter is the missing check that record defers). Not the same object.
- IDEA-20260926-5c26f9 (dimension-5 and -6 Weil-polynomial census over F_2 for 131 dividing the point count): opened (searched for polariz|Howe|ppav|Jacobian|Torelli). It screens classes by non-negative place counts a_r >= 0 and states that passing "is NECESSARY, not sufficient"; it does not test principal polarisability. Different object (dimensions 5 and 6, question about 131 | #A(F_2)), adjacent as a necessary-condition screen.
- IDEA-20261024-5f08bd (general-prime floor lemma for single-orbit cover genus): opened (same search). Explicit-cover genus floor, not an existence statement. Different object.
- H-FROB-f3d248 / IDEA-20261002-8f26ce (the lead's own ledger_refs): Artin-Schreier genus 5 and 6 over F_2 and the order-131 question; they do not mention A_n, Howe or Torelli by the index fields.
- IDEA-20260922-8278db / H-BINSTD-6e3bd4 / H-BINSTD-84fab0 / H-BINSTD-b5d435: trace-zero-variety Gaudry decomposition cost for composite-degree c2pnb (q = 2^16, k prime); no Jacobian-carrier content.
- IDEA-20260808-40aab9, IDEA-20260808-fa1d80, IDEA-20260812-104e1a, IDEA-20260829-70258e, IDEA-20260821-211586, IDEA-20260901-1ddfd4 ("polari[sz]" hits): Kani/Robert higher-dimensional embedding and SQIsign polarisation lines; they use principal polarisations as a gluing tool for (N,N)-isogenies, not as an existence filter on a Jacobian in an isogeny class. Different object.

N3 conclusion: no ledger record applies Howe's criterion (zero "Howe" and zero "ppav" hits in both indices) or states the principal-polarisation obstruction for A_n. The nearest record (a29e53) defers exactly that check. No duplicate in the ledger.

## Prior art outside the atlas and the ledger (found while reading the lead's evidence; this is the finding that lowers the novelty)

These are source documents in the sibling repositories (read-only, retrieved this session). They are not atlas leads and not ledger records, so N1 and N3 cannot see them.

1. /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/research/ecdlp_leads_20261018/README.md, lead L9 "Certified lower bounds on the cover genus" (status: "derived (partial); (a = 0, n = 5) at genus 5 excluded by LMFDB"; "first experiment: Howe's principal-polarisability test on T_n for deployed n; point-count positivity"). Its body says "LMFDB. T_3 and T_5 have no principal polarisation for either a." and tabulates 14 LMFDB classes over F_2 with a "principally polarisable" column (T_3 and T_5 rows: no, 0 Jacobians; Res(E) rows: yes). The lead text proposes turning this into a per-n certified lower bound g_min(n) using Howe's criterion for ordinary isogeny classes, Serre and Oesterle bounds, and place-count positivity. This is the candidate's core mechanism, recorded 2026-10-18, status partial (n = 3 and 5 only, by LMFDB lookup, no general rule, no sweep over prime n).
2. /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/research/notes/ecc2k130/RESEARCH_ECC2K130_HYPERELLIPTIC.md sections 6 and 8: the codimension count "ignores that the isogeny class of A carries a class-number-sized family of principal polarisations. A defensible version would count principally polarised members of this isogeny class against Jacobians among them, which needs the class number of a degree-260 CM field." The candidate's H-C1a (Brauer-Siegel-size h^-) is a response to this sentence.
3. /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/research/ic_next10_20261014/10-torelli-toy/README.md: "The ppav count h of A_5's class is not computed ... h could exceed 1 ... That condition is not established" and "h_A was not computed. It is reported as a band, h in [1, 8]." The L9 LMFDB lookup contradicts the band for the class of A_5 itself (zero principal polarisations in the class of A_5). The toy multiplies by h for a genus-5 carrier, whose class is A_5 x (elliptic), not A_5, so the relevant count is for the product class; the candidate's LMFDB observation "A_5 x B has PPAVs but 0 Jacobians" is the corresponding datum. This is my reading of the README, not a measurement.
4. /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/crypto-main/research/cover_decomposition_gap_search_20261018/README.md lines 109, 224, 231, 274: cites Howe / Maisner-Nart as excluding gluing for prime-order curves and DiPippo-Howe class counts. Adjacent (gluing, not trace-zero PPAV).
5. Corpus sources KN-LIT-144 (Howe, isogeny classes with no principal polarizations) and KN-LIT-1287 (Rybakov, principal polarizations on products): read-state "read", never cited by a KR row, lead or ledger record.
