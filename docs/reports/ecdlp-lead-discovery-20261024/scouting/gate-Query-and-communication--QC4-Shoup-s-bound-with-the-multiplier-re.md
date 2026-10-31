# Gate record: QC4, restricted-multiplier Shoup bound + census of algebraic H-invariants

Date of run: 2026-10-25. Gate author: scout subagent (read-only on the repositories; writes only under scratchpad/scout/).
Candidate field_key: Query and communication complexity / generic-group lower bounds. Candidate target: B6, LEAD-RHO-non-automorphism-equivalence (open_unexamined).

## Verdict (one paragraph)

**advances_lead.** The candidate is the execution of the open lead LEAD-RHO-non-automorphism-equivalence's own next_action (prove a per-step canonicalisation bound for h = |H| > 6; census H-invariants at h ~ N^1/3), with a sharper target than the lead states. It is NOT a new mechanism and it does not escape SO-GEN or SO-ENDO (its own text says the generic half is inside SO-GEN). Two parts must be separated. (a) The quantity "a generic canonicaliser of H-orbits costs Omega(sqrt h), hence no net gain" is already recorded at derivation tier as claim (C4) of IDEA-20260901-863e36 (via reduction to the global Shoup bound) and informally in IDEA-20260807-18d2f7 (E); what QC4 adds is a direct per-call statement with an explicit consistency parameter epsilon. (b) The census of rational-function H-invariants in Riemann-Roch spaces at finite N has no recorded run (EXP-EWALK-36ab1f has an empty runs/ directory; H-EWALK-29cb90 is `proposed`). It would be an empirical measurement, at toy N, of what the bounded-degree theorem of IDEA-20260811-332ce9 (d < N/(2(n+1)), stated for cheap endomorphisms) cannot reach for a generic scalar H. The degree floor itself is not credited as new (see G6); the increment is only the measured minimal degree d_min against the generic-position prediction, with the positive and relabelling controls. Predicted gain is 0 bits (candidate's own number), so this can only change a lead disposition; it is not a lead.

## Hard-rule compliance
- No repository file was edited, created, staged or committed. Only files under the scout/ directory were written (all of this run's scratch files are prefixed `qc4_`).
- Environment exported as instructed (LEAD_ATLAS_CRYPTO, LEAD_ATLAS_CRYPTANALYSIS, LEAD_ATLAS_ECC_CHALLENGES); commands run from /Volumes/SSD990-2/crypto-autoresearcher.
- The 21-cell census numbers, the positive controls, the "H5" pole-order prediction and the theorem are the CANDIDATE's claims. This gate did not reproduce any of them. Nothing below is an outcome this gate produced except the search outputs and record readings it cites.

## N1. Atlas collision (raw outputs, default top-8 display)

### Run A (candidate match_phrasings[0])
`python3 tools/lead_atlas.py --match "restricted-multiplier Shoup bound for generic canonicalisation of multiplier-subgroup orbits"`
```
    9  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    7  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
    7  LEAD-STR-endo-scalar-action-generic          closed_obstructed  Endomorphism-augmented generic and witness-lattice attacks on a prime-order subgroup
    6  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    6  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
    6  LEAD-RHO-prime-gpu-rho                       open_blocked       GPU rho on prime and generic binary curves with an admitted CPU/GPU comparison
    6  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
    5  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
```

### Run B (candidate match_phrasings[1])
`python3 tools/lead_atlas.py --match "canonicalising orbits of a subgroup of scalar multipliers costs the square root of the orbit size"`
```
    9  LEAD-ICP-retained-setup-online               closed_dominated   Retained-setup online IC (compact orbit n61, dense K1798 root table n83, orbit-folded m = 2) as a per-target win
    7  KR-RHO-5b1c0a                                known_result       Representation techniques do not beat rho over F_{p^2}
    7  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    7  LEAD-ICP-generic-table-decomposition         closed_obstructed  Enumeration, subtraction and meet-in-the-middle pair-table decomposition for prime-field Semaev IC (arity 2 to 7)
    7  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
    6  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    6  LEAD-EXO-torsor-deck-period                  closed_obstructed  Torsor, deck-orbit, cubical/biextension and scalar-orbit elliptic-period descent
    6  LEAD-ICB-frobenius-orbit-factor-base         closed_obstructed  Frobenius/endomorphism-invariant factor bases and orbit columns on Koblitz and subfield curves, beyond the trivial orbit saving
```

### Run C (candidate match_phrasings[2])
`python3 tools/lead_atlas.py --match "every endomorphism-image oracle is simulable by group operations so quotient rho by a multiplier subgroup gains nothing"`
```
   16  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
   13  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   12  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
   12  LEAD-EXO-augmented-oracle-ggm                closed_obstructed  Augmented oracles (x-, y-, full-point, halving, endomorphism-image, incidence) and GGM simulability
   11  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
   10  LEAD-ICE-rootfind-pairtable-oracle           open_blocked       Root-finding / pair-table decomposition oracle in place of a Groebner solve
   10  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups
   10  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
```

### Run D (own phrasing)
`python3 tools/lead_atlas.py --match "non-automorphism equivalence classes larger than Aut(E) rho H-invariant canonical form"`
```
   24  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
   15  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   14  LEAD-STR-automorphism-quotient-rho           closed_known       Rho on E/Aut (negation, j=0 order-6, j=1728 order-4) and anything beyond sqrt(|Aut|)
   13  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
   13  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
   11  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
    9  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
    8  LEAD-RHO-negation-map-fruitless-cycles       closed_known       Negation-map rho on {+-P} classes with fruitless-cycle escape (prime curves)
```

### Run E (own phrasing)
`python3 tools/lead_atlas.py --match "rational function invariant under multiplier subgroup pole order Riemann-Roch census coordinate-dependent invariant of point encoding"`
```
   14  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
    9  KR-RHO-6654ba                                known_result       Point halving as a rho step on binary curves
    8  LEAD-TRF-function-field-xedni-lift           closed_obstructed  Function-field xedni: lift relations to sections of elliptic surfaces y^2 = x^3 + a(t)x + b(t) over F_p(t)
    8  LEAD-TRF-one-point-self-pairing              closed_obstructed  A non-degenerate self-pairing or distortion map computable from one point of the prime-order subgroup
    6  LEAD-ICB-frobenius-search-symmetry           closed_obstructed  Frobenius as a symmetry of the decomposition search: orbit CNF encodings, conjugate attempts, equivariant elimination
    6  LEAD-ICE-sat-xor-pdp-oracle                  open_next_step     SAT / native-XOR (CryptoMiniSat, WDSat) point-decomposition oracle with honest pricing
    6  LEAD-ICP-char0-lifting-xedni-smoothness      closed_known       Lifting to characteristic zero - classical xedni, prescribed rational lifts (Cheon 2-isogeny form) and smoothness of integer lifts of x
    6  LEAD-ICP-icperf-binary-pdp-solver            open_next_step     Solver choice for the Weil-descended binary PDP (WDSat/CDCL+XOR vs Groebner/F4/BRiAl, side-constrained cores) on the ICPERF boundary
```

### Run F (own phrasing)
`python3 tools/lead_atlas.py --match "per-step canonicalisation cost lower bound for equivalence class rho"`
```
   15  LEAD-STR-isogeny-class-generic-invariance    closed_obstructed  Generic (rho, BSGS) ECDLP cost across an isogeny class and across volcano levels
   14  LEAD-RHO-native-step-cost                    open_next_step     Native cost of one rho step: canonicalisation, field arithmetic and admitted CPU timing
   14  LEAD-RHO-non-automorphism-equivalence        open_unexamined    Equivalence classes larger than Aut(E): quotients by subgroups H of (Z/N)^*
   13  LEAD-ICP-gfp5-rho-reference-audit            closed_known       Rho ruler and SafeCurves-style parameter audit for EcGFp5/EcMasFp5 (affine F_{p^5} rho cost, inversion paths, partition, multi-instance, interval kangaroo)
   12  LEAD-RHO-automorphism-class-walks            closed_known       Rho on automorphism/Frobenius orbits: sqrt(2m) on Koblitz, order-4/6 maps on j=1728/j=0
   11  KR-RHO-825bca                                known_result       Practical rho cost on standard curves
   11  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
   10  KR-RHO-1c2928                                known_result       Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
```

Observation on retrieval: candidate phrasing 1 does not return LEAD-RHO-non-automorphism-equivalence at all in its top 8, and phrasing 2 returns it at rank 5, although that is the lead the candidate targets. A lexical miss is not evidence of non-overlap; own phrasings D, E and F rank it first, first and third.

### N1 reading: top-5 of every run, lead YAML opened (mechanism + obstruction + forecloses)

| lead (disposition) | same mechanism? | what it says that bears on QC4 |
|---|---|---|
| LEAD-RHO-non-automorphism-equivalence (open_unexamined) | **Yes, this is the target lead.** | next_action: "Prove or refute H-EWALK-29cb90's per-step canonicalisation bound: show that for h = |H| > 6 on ordinary prime-field curves any canonicaliser costs Omega(log h) group operations per step (charged gain <= 1), and search the encoding for a non-constant H-invariant at h ~ N^{1/3} on toy curves (exhaustive at N < 2^20)." forecloses: quotient rho by multiplier subgroup; equivalence classes beyond automorphisms; H-invariant of the point encoding; N^{1/3} rho with free canonicalisation. QC4 = this next_action with a sharper bound (sqrt h) and a stated census method. Note the lead's own parenthetical "(charged gain <= 1)" does not follow from Omega(log h): the step gain is sqrt(h) so the per-step cost must be of order sqrt(h) to cancel it; QC4's sqrt(h) is the bound the lead actually needs. |
| LEAD-RHO-generic-sqrt-lower-bound (closed_obstructed, SO-GEN) | generic half is inside | statement (quoted): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r." QC4 does not escape it; it is a constant-level per-call accounting inside it. |
| LEAD-STR-endo-scalar-action-generic (closed_obstructed, SO-ENDO) | generic half is inside | statement (quoted): "For G of prime order N, End(G) = Z/N, so every endomorphism-image oracle is simulable by group operations and Shoup's bound applies ... Scope: any prime-field or binary curve, any size, prime-order subgroup." revisit_when: "A proposed oracle is shown not to be GGM-simulable (it returns field data or curve data, resource R1/R2 in DECOMPOSITION.md, not a group element)." QC4's premise argument ("a canonicaliser is an orbit selector, a different object") does not remove it from this scope: lambda*R is a scalar multiple, hence computable by group operations, so a generic selector is a group-operation algorithm. Only the coordinate-reading (R1) residual is outside, and that residual is the one 18d2f7 (E) and 332ce9 (S1-S4) already name. |
| LEAD-STR-small-cm-disc-nonunit-endo (closed_obstructed) | nearest closed lead | statement (quoted): "A rho class of size h costs about h evaluations of alpha to canonicalise, so the net factor is at most sqrt(h)/kappa with kappa about h times c(alpha) ... Scope: ordinary prime-field curves, prime-order G." This is the enumeration cost model; QC4 upgrades "enumeration costs h" to "every generic canonicaliser costs >= sqrt(h/2)-ish". It does not answer the obstruction's coordinate-dependent side. |
| LEAD-STR-automorphism-quotient-rho (closed_known) | same family | statement (quoted): "Quotienting by the full End(E) action leaves two classes and is useless, because a non-unit endomorphism has orbits of size ord_N(lambda), so the ceiling is sqrt(|Aut|) for any equivalence-class walk on a prime-order group." revisit_when: "A canonicalisation with per-step cost kappa below 1 group operation is found for a group larger than Aut ..." |
| LEAD-RHO-automorphism-class-walks (closed_known) | same family | ceiling sqrt|Aut|; revisit only for a larger efficiently computable automorphism group. QC4 claims none. |
| LEAD-EXO-augmented-oracle-ggm (closed_obstructed) | generic half inside | "Each named oracle is GGM-simulable ... Scope: oracles, not resources". |
| LEAD-ICE-generic-oracle-arity-cost-floor, LEAD-ICP-generic-table-decomposition, LEAD-ICP-retained-setup-online, LEAD-ICP-algebraic-membership-factor-base (IC leads) | lexical neighbours only | IC decomposition-oracle and factor-base leads. SO-ALGFB uses the same Bezout/degree idea (an algebraic locus of degree d yields O(d) points) for a different predicate (factor-base membership), so QC4's census is not a duplicate of it; it shares a method, not a mechanism. |
| LEAD-RHO-native-step-cost (open_next_step) | no | prices the Koblitz (Frobenius rotation) canonicaliser in field multiplications; different H, different object. |
| LEAD-STR-isogeny-class-generic-invariance, LEAD-RHO-negation-map-fruitless-cycles, LEAD-RHO-prime-gpu-rho, LEAD-ICP-gfp5-rho-reference-audit, LEAD-ICB-frobenius-search-symmetry, LEAD-TRF-function-field-xedni-lift, LEAD-TRF-one-point-self-pairing, LEAD-RHO-lhw-modular-filter-price, LEAD-EXO-torsor-deck-period, LEAD-ICB-frobenius-orbit-factor-base | no | opened and read at mechanism/obstruction level; no shared mechanism. |
| LEAD-ICP-construction-normal-form (open_unexamined, rank 6 of run D) | not assessed | TITLE ONLY ("Normal form and calibrated instruments for proposed prime-field attack systems"); the YAML was not opened. It is outside the top 5 of every run and its title is about IC system normal forms, but this gate did not read it. |

What QC4 does that the target lead's forecloses phrases do not cover: those phrases are the lead's own (open, unexamined) topic, so they do not constrain it. Against the closed leads' forecloses phrases ("sub-square-root generic algorithm", "add endomorphism images to the oracle to beat sqrt(N)", "cheap endomorphism of degree 2 gives rho equivalence classes", "quotient the walk by the full endomorphism ring", "automorphism speedup beyond sqrt(|Aut|)") QC4 claims no gain and so is not foreclosed as an attack; it is a bound inside them.

## N2. Known results (raw outputs of tools/build_frontier_map.py --match)

```
### FRONTIER: restricted-multiplier Shoup bound for generic canonicalisation of multiplier-subgroup orbits
KR-RHO-13bf67  score=6  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-0528e7  score=4  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-1c2928  score=4  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-cd0049  score=4  [known_bound/measured]  Measured (toy, prime): negation-map BSGS at 1.160 [1.068, 1.248] x the generic floor with a 0.50 sqrt(r) table
    sources: KN-FIND-4e12fa
KR-IC-5931ee  score=3  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-RHO-ea34b8  score=2  [known_bound/proven]  Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    sources: KN-LIT-7cc07f, KN-LIT-013, KN-LIT-7e2964
KR-RHO-fbd7b1  score=2  [known_bound/proven]  Grumpy giants and better-than-rho generic ordering
    sources: KN-LIT-fbe4e0
KR-IC-081a58  score=1  [known_bound/heuristic]  Joux–Vitse n−1 decomposition and oracle-assisted static DH
    sources: KN-LIT-673219, KN-LIT-022, KN-LIT-41fe5c
### FRONTIER: canonicalising orbits of a subgroup of scalar multipliers costs the square root of the orbit size
KR-RHO-5b1c0a  score=7  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5
KR-RHO-13bf67  score=6  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-482ed3  score=5  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-IC-791cb7  score=4  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-0528e7  score=4  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-IC-1fcdbc  score=1  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-5931ee  score=1  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=1  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
### FRONTIER: every endomorphism-image oracle is simulable by group operations so quotient rho by a multiplier subgroup gains nothing
KR-RHO-13bf67  score=12  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-1c2928  score=8  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-482ed3  score=7  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-791cb7  score=6  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-825bca  score=6  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-93979e  score=6  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
### FRONTIER: non-automorphism equivalence classes larger than Aut(E) rho H-invariant canonical form
KR-RHO-482ed3  score=13  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-IC-1fcdbc  score=6  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-RHO-1c2928  score=6  [known_bound/measured]  Measured (toy, Koblitz): lean signed-Frobenius rho at 4.996 [2.985, 7.374] x the generic floor; beats the strong lock-step reference at the constant level because the reference set-up is 71 % of its total at these sizes
    sources: KN-FIND-4e12fa
KR-RHO-6654ba  score=6  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-825bca  score=6  [record/reported]  Practical rho cost on standard curves
    sources: KN-LIT-a5c59c
KR-RHO-93979e  score=6  [known_bound/proven]  Rigorous collision bounds for rho walks
    sources: KN-LIT-369623, KN-LIT-6762f2
KR-RHO-e7f98e  score=6  [record/reported]  GPU Pollard rho: academic state of the art is thin
    sources: KN-LIT-c75942, KN-LIT-2b1b99, KN-LIT-34a845, KN-LIT-74dfa6, KN-LIT-2c4f3d, KN-LIT-a4b3d8
KR-IC-9e610d  score=4  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
```

### N2 reading
- KR-RHO-13bf67 (textbook_fact/proven, Omega(sqrt p) generic) is the top hit on phrasings 1 and 3. KR-RHO-0528e7 (automorphisms give a sqrt(m) constant), KR-RHO-482ed3 (Koblitz signed-Frobenius), KR-RHO-93979e, KR-RHO-1c2928 follow. No KR row states a per-call lower bound on canonicalising orbits of a multiplier subgroup, and none reports an H-invariant census.
- The statement "a generic canonicaliser has c_can = Omega(sqrt r), so no net gain" is a two-line corollary of KR-RHO-13bf67 (if the canonicaliser is generic the whole walk is a generic algorithm, so steps x cost >= Omega(sqrt N) with steps ~ sqrt(N/r)). So at corollary level it is known. What is new relative to the KR rows, stated exactly: (i) the per-call form (no walk-length heuristic) with an explicit consistency parameter epsilon; (ii) the finite-N census of rational-function invariants. Neither changes any exponent or constant of a known algorithm.
- Literature search this session (WebSearch, 3 queries): no published statement of a generic-group lower bound for canonicalising orbits of a scalar-multiplier subgroup was found. The searches returned the standard equivalence-class rho framing (Gallant-Lambert-Vanstone; Wiener-Zuccherato; Bos-Costello-Miele on automorphism groups) as "constant speedup in some groups". Search coverage is limited; absence of a hit is not evidence of absence (the ledger records the same caveat in IDEA-20260811-332ce9 and IDEA-20260901-863e36).

## N3. Ledger
Index greps (python over ledger/.index/{proposals,hypotheses,experiments}.jsonl; fields searched: id, title, claim/statement, mechanism, which the index truncates to roughly 200 characters). Terms, first pass: canonicalis(z)ation; EWALK; equivalence class; H-EWALK-29cb90; multiplier subgroup / subgroup H; H-invariant / non-automorphism / beyond automorphism / larger than Aut; Riemann-Roch / pole order; restricted-multiplier / Shoup. Second pass: arithmetic selector / orbit selector / c_can / kappa / canonical representative / scalar-orbit / lambda-orbit / Gamma-orbit. The terms "Shoup" and "restricted-multiplier" returned ZERO hits, yet IDEA-20260901-863e36 contains the Shoup-based c_can = Omega(sqrt r) claim in its full text (opened below): the index is truncated, so a lexical miss there proves nothing. Per the instruction, full-text search of ledger/proposals/ was not performed.

Hits that may be the same object (id [status] 100-char claim/title from the index):
- IDEA-20260901-863e36 [proposed] Let E/F_p be an ordinary short-Weierstrass curve, P a point of PRIME order n, G = <P>, and let Gamma
- IDEA-20260807-18d2f7 [proposed] (A) THE TOP OF THE LADDER IS TRIVIALLY USELESS, AND SAYING SO CLOSES A FAMILY THAT KEEPS REAPPEARING
- IDEA-20260811-332ce9 [proposed] (A) THE OPEN RUNG BEING ATTACKED, QUOTED RATHER THAN PARAPHRASED. IDEA-20260807-18d2f7 (lane RQ-EWAL
- IDEA-20260812-b68bc0 [proposed] Let E/F_p be ordinary with prime N = #E(F_p), let O = End_{F_p}(E) = Z[pi], and let Lambda = <lambda
- IDEA-20260826-506ba2 [proposed] THREE SEPARABLE CLAIMS. NO ATTACK IS PROPOSED, NO EXPONENT MOVES, AND NO CANDIDATE IS ASSERTED TO EX
- IDEA-20260901-6b63a4 [proposed] Four statements. T1 is a theorem, C1 and C2 are its corollaries, and M is the measurement that turns
- IDEA-20260807-ebcae6 [proposed] (A) WHAT IS BEING CLOSED, AND WHAT IS NOT. This record asserts a CEILING on one family: rho-type col
- IDEA-20260802-005 [None] H-ENDO-001 stands `approved` WITH NO EVIDENCE. This control decides it cheaply and in both direction
- IDEA-20260906-906dcc [proposed] Selected coefficients of the scalar-orbit polynomial could provide a cheap canonical sketch if their
- IDEA-20260913-04fb8c [proposed] Let E/F_p be ordinary with prime group order n, P a generator, and lambda in (Z/n)^* of large multip
- IDEA-20260806-c5d183 [None] (A) THE THEOREM-SHAPED CLAIM, WITH ITS PROOF STATED IN THE CLAIM BECAUSE IT IS FIVE LINES. Let G = <
- IDEA-20260901-3e68ad [proposed] (A) SETTING. E/F_p ordinary, E(F_p) = G cyclic of prime order N > 3 (the RQ's primary cells). The F_
- IDEA-20260904-742c48 [proposed] (A) THE COST CLAIM BEING CORRECTED. IDEA-20260901-6b63a4 proves the norm-order tradeoff T1 - for alp
- H-EWALK-29cb90 [proposed] On a prime-order subgroup G of an elliptic curve over F_p, the equivalence-class ladder indexed by s
- H-EWALK-401e20 [specified] Fix the exact count identity of IDEA-20260812-b68bc0 before any later-stage claim. Stage 0 asserts o
- H-EWALK-aeeee9 [specified] Fix the exact count identity of IDEA-20260826-506ba2 before any later-stage claim. Stage 0 asserts o
- H-JINV-f73bb6 [specified] Fix the exact count identity of IDEA-20260811-332ce9 before any later-stage claim. Stage 0 asserts o
- EXP-EWALK-36ab1f [review_required] The quotient ladder with both degenerate ends - enumerative verification of class counts and orbit s
- EXP-EWALK-b57ffb [draft] THE QUOTIENT LADDER, INCLUDING ITS TRIVIAL TOP AND ITS ONE OPEN RUNG: quotienting G by the FULL End(
- EXP-EWALK-6433b1 [draft] THE sqrt(|Aut|) CEILING, STATED AS A THEOREM RATHER THAN AS FOLKLORE: an equivalence-class rho walk 
- EXP-EWALK-98bac0 [approved] Closed-form n=3 P-S0-DEGRFLOO calibrator

Full records opened (exact paths, the maximum of three):
1. /Volumes/SSD990-2/crypto-autoresearcher/ledger/proposals/IDEA-20260901-863e36.yaml (read through the mechanism, novelty_screen and citations blocks). Decisive. (C1) propagation under Sigma iff the fibre partition is a block system of <Sigma>; (C3) for Gamma <= (Z/n)^* the orbit partitions are the only quotients that shrink the search; (C4) "If c_can is achieved by a GENERIC procedure ... the Shoup bound forces sqrt(n/r) * c_can >= const * sqrt(n), hence c_can = Omega(sqrt(r)), hence NO net gain, for EVERY Gamma, at every r. A super-constant speedup therefore requires a NON-GENERIC canonical form"; (C5) variety quotients exist only for Aut(E), |Gamma| <= 6; (C6) the open cell is arithmetic selectors, e.g. the element of the orbit with smallest x-coordinate, with c_can predicted LINEAR in r. Its Stage 2 explicitly lets lambda NOT come from an endomorphism (sweep r freely), which is QC4's H. No hypothesis beyond Stage 0 (H-ECDLP-62befe) exists for it; no measurement of c_can is recorded.
2. /Volumes/SSD990-2/crypto-autoresearcher/ledger/proposals/IDEA-20260807-18d2f7.yaml (read through the null_object_control block). The ladder H <= (Z/N)^*; two independent costs (canonicalisation per step, disambiguation per collision); payoff N^1/3 at h = N^1/3 (the source of the lead's "h ~ N^1/3"); (E) "the only generic route is to compute the h orbit elements, which costs h" and Shoup does not forbid a NON-generic encoding invariant; (F1-F3) failed candidates; (G) OUTCOME 2 = "someone proves no such invariant exists for a stated class of computations". Explicitly refuses to claim the absence of a cheap invariant.
3. /Volumes/SSD990-2/crypto-autoresearcher/ledger/proposals/IDEA-20260811-332ce9.yaml (read through the heuristic_assumptions block). Props 1-2: exact invariance forces deg(alpha) = 1; pointwise invariance of a degree-d function on G forces it when N > 2d(n+1); Cor 1: arithmetic SLPs of length L need L >= log2 N - log2(n+1) - log2 6; Cor 2: the whole power-map family x^m decided by one lcm. Its residual classes: S1 high-degree cheaply evaluable functions, S2 non-rational encoding functions (comparisons, min/max, hashing), S3 cheap selectors, S4 extension and subfield curves. Its bound is vacuous for a generic scalar lambda (the integer representative m has deg [m] = m^2, so N > 2d(m^2+1) fails), which is where QC4's census adds content.

Not opened (cap reached), judged by index title/claim only: IDEA-20260812-b68bc0 ("The degree floor for orbit invariants", Lambda <= (Z/N)^* of order r acting by scalar multiplication, statements C1-C3; its Stage 0 is H-EWALK-401e20 / EXP-EWALK-98bac0). This is the nearest record to QC4's "rational invariants have degree >= h" sentence and may already contain that floor; it must be opened before the census half is written up as new. Also unopened: IDEA-20260906-906dcc (coefficient-sketch canonicalizers, coordinate-dependent; Stage 0 only, H-ECDLP-2b270e), IDEA-20260826-506ba2 (charged ratio sqrt(m)/kappa, source of the cost model quoted in LEAD-STR-small-cm-disc-nonunit-endo), EXP-EWALK-6433b1 / IDEA-20260807-ebcae6 (sqrt|Aut| ceiling as a theorem from admissibility conditions on cheap automorphisms; declines to prove nonexistence of an instance-dependent O(1) canonicalisation).

State of execution: EXP-EWALK-36ab1f (ladder enumerative verification, `review_required`) has runs/ containing only .gitkeep (checked); EXP-EWALK-b57ffb is `draft`; H-EWALK-29cb90 is `proposed`; EXP-EWALK-98bac0 and EXP-EWALK-95fc04 are closed-form Stage 0 calibrators. No ledger census of H-invariants exists.

## N4. Notation change
Pair stated by the candidate: (R1 affine (x, y) encoding, Sigma = multiplication by a subgroup H <= (Z/N)^*). This is exactly the "multiplication slice" of IDEA-20260901-863e36 (docs/object-frame-ideation.md section 1 row: "multiplication by a subgroup Gamma <= (Z/n)^* is another [slice] and yields the negation and GLV quotients. The quotient-search family reduces to one measurable number [the cost of canonicalising a Gamma-orbit]"), with Gamma = H. So the pair is NOT a new arithmetic and the candidate does not claim one; it claims to price the recorded "one open number".
- vs IDEA-20260806-c5d183 and KN-FIND-ffe1df Theorem C: both are about the full translation action (constant-or-injective projections; surjective homomorphism onto a group of order dividing N). QC4's Sigma is multiplicative, a block system of <H> acting freely on G \ {O}, not of translation, so neither rigidity statement applies or is restated. (The object-frame constraint "Sigma must not be the full translation action" is satisfied.) The walk step itself is translation; the orbit partition is compatible with it only after canonicalisation, which is the same point 863e36 makes.
- vs IDEA-20260901-863e36: same pair, same trichotomy class (partial-action), same priced quantity (c_can). Its (C4) already gives the generic value Omega(sqrt r). So the generic half of QC4 IS a recorded result in nearly identical notation; the non-generic half is 863e36's open cell (C6), of which QC4's census measures only the sub-class "functions in L(dO) restricted to G" (rational functions of pole order <= d), not the arithmetic selector (min x) that 863e36 freezes.
- Trichotomy (object-frame section 3 asks for exactly one class): QC4 is two objects and straddles it. The generic half (the H-orbit partition under Sigma = multiplication by H) is partial-action, a block system of <H> acting freely on G \ {O}; the census half (functions of (x, y) in L(dO) restricted to G) is coordinate-dependent. They are treated separately in this gate for that reason.
- vs KN-OPEN-020: concerns algebraic factor bases (IC). QC4 has no factor base. It touches the same "bounded-degree algebraic description" boundary from the orbit-label side: its census class is degree up to ~N, i.e. the high-degree side, but a degree floor does not bound evaluation cost (power maps, implicit membership, selectors stay open; 332ce9 Cor 2 and S1-S3).
- Off-limits lens check (object-frame-ideation section 2): QC4's lens is F1 (walk-collision) plus F6 (orbit representative); both are off-limits as the PRIMARY lens, allowed as components if named. QC4 is a bound on that lens, not an attack through it.

## Citation provenance (this session)
- Shoup, "Lower bounds for discrete logarithms and related problems", EUROCRYPT 1997, LNCS 1233:256-266, doi 10.1007/3-540-69053-0_18: **retrieved** (WebSearch: multiple independent bibliographic records agree on title, venue, volume, pages, DOI; abstract headline: generic algorithms need Omega(p^1/2) group operations, p the largest prime dividing the group order).
- Shoup's proof technique: **retrieved at secondary level**. The Stanford CS259C final report on generic groups (web.stanford.edu/class/cs259c/finalpapers/genericgroups.pdf, text extracted with pdftotext) reproduces it: random encoding sigma, Schwartz-Zippel on a nonzero linear form (vanishes with probability <= 1/p), O(m^2) pairs of forms, success probability O(m^2/p). The primary PDF at shoup.net/papers/dlbounds1.pdf was fetched but its text layer is garbled (Type 3 fonts), so the primary text was NOT read. The restricted-multiplier step (a pair collides with probability <= 1/h once the unknown is uniform on h values) is the candidate's own derivation; I checked it only by reading it against the secondary description, not by proving it. Provenance for that step: derived (candidate), unverified here.
- Gallant-Lambert-Vanstone, Wiener-Zuccherato, Bos-Costello-Miele: **retrieved** only as secondhand statements in search-result excerpts ("orbits of group elements under a fast computable group homomorphism", "constant speedup"); original papers not read.

## Numbered heuristics and conditionals, G1-G6 (none verified by this gate; the prefix G avoids the candidate's own "H5" pole-order prediction)
- G1 (conditional on the candidate's Theorem as stated): any generic canonicaliser consistent on (R, lambda R) with probability >= 1 - epsilon needs q >= sqrt(h(1 - 2 epsilon - O(1/h))/2) - O(1) queries. The expression is vacuous for epsilon >= 1/2.
- G2 (conditional on G1): the corollary "charged gain <= 1 + O(h^-1/2) over negation rho" additionally needs (a) the constants to match exactly (step gain sqrt(h/2) against per-call cost >= sqrt(h/2) is borderline, not strictly below 1, so a constant factor can survive), and (b) behaviour of a walk whose canonicaliser is only approximately consistent (epsilon > 0), which is not part of G1. Prediction, not produced: partial canonicalisers using m evaluations detect about m/2 equivalent partners (min over random m-subsets of an h-orbit agrees with probability about m/(2h)), giving a step gain about sqrt(1 + m/2) at cost m, a net loss for every m. This is my back-of-envelope, not a theorem.
- G3: the census null (every cell at generic position within 1) is what a pure dimension count of the f(lambda^i R) = f(R) constraints predicts, so a null is low-information; the informative event is a deviation below generic position, and the positive controls (h = 2 pole 2; j = 0 with h = 3 pole 3 and h = 6 pole 6) are what make a null interpretable. The 21-cell results are the candidate's and not reproduced here.
- G4: the lead's literal exhaustive scale (N < 2^20) is not reachable by dense elimination; 2^13-2^14 is the candidate's proposed rung. Statements from a census at N <= 2^14 are about that range only.
- G5 (scope of any closure): the census class (rational functions in L(dO)|_G) is a stated computation class in the sense of 18d2f7 (G) OUTCOME 2, wider than 332ce9's bounded-degree class, but it excludes 332ce9's S2 (non-rational encoding functions: comparisons, min/max, hashing), S3 (selectors) and power-map-like high-degree cheap functions (332ce9 Cor 2). Recording the lead as closed_obstructed on this basis would overstate it; the candidate's own proposal to scope it to "generic unbatched canonicalisers" and list the rest as open residue is the defensible disposition.
- G6 (what is not new in the census half): the floor "a non-constant rational H-invariant has degree >= h" is elementary (the fibre f^-1(c) of a point of G contains a whole H-orbit, i.e. >= h points, and a degree-d function has fibres of at most d points), and the consequence "only Omega(log h) field operations are forced" is the SLP-doubling argument of IDEA-20260811-332ce9 Corollary 1 (deg f <= 3*2^L, so L >= log2(d/3)). IDEA-20260812-b68bc0 (unopened) very likely states the same floor. The census increment is therefore only the measured d_min against the generic-position prediction (N-1)(1 - |H cap Aut|/h) + O(1), together with the positive controls and the random-relabelling control. This does not block the verdict: whatever b68bc0 contains, the census is unrun and the lead stays open.

## Recommended handling (not an action taken)
Attach QC4 to LEAD-RHO-non-automorphism-equivalence as its executor, not as a new lead. Before writing it up: open IDEA-20260812-b68bc0 to see whether the degree floor is already stated; cite IDEA-20260901-863e36 (C4) as the recorded form of the generic bound and state the per-call and epsilon-dependent content as the increment; carry 863e36 (C6) and 332ce9 S1-S3 as the open residue.
