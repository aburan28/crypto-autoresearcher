# Scout dossier: algebraic geometry of curves and covers (final lead-discovery round)

Field: Riemann-Hurwitz, Kummer / Artin-Schreier covers of E over F_p, split Jacobians, isogeny graphs and modular curves as carriers, trigonal/tetragonal constructions, Weil restriction in odd characteristic, decomposition of Jac(C) with E as a factor.
Author: scout subagent, 2026-10-24. Nothing in any repository was edited. Every number below is either (a) read from a cited record, (b) computed in this session (marked COMPUTED, with the command recipe), (c) retrieved from LMFDB or the web (marked RETRIEVED), or (d) a prediction (marked PREDICTION, with its numbered heuristic). Nothing is labelled promising.

## 0. Bottom line

1. **Prime fields.** This field does not give a prime-field exponent candidate that gets past the standing obstructions and is not already in the ledger. The reason is structural and is stated in section 2 (the "one-equation" or dimension gap). The prime-field output is therefore three deciders: a proof plus a construction (C1), an exact instrument covering three open leads (C2), and one cheap tower arm (C3).
2. **Koblitz (B5).** The strongest result of this scout is C4. Howe's principal-polarisation criterion, specialised by hand to the trace-zero variety A_n of a Koblitz curve, reduces to the sign and the prime factors of one Lucas number U_n(t_1, 2). It was computed for every prime n < 140 and for n = 163. It was validated against the exact LMFDB data (RETRIEVED): A_5 at q = 2, and A_3 at q in {2, 3, 4, 5, 7, 8, 9} (36 simple classes, all agreeing, including the inert-prime branch that n = 131 relies on). Consequences:
   - The genus-12 cell (genus = dim A, B = 0) of the planned n = 13 rung of LEAD-ICB-ecc2k130-jacobian-carrier is empty by theorem. The genus 13-14 cells (A_13 x B gluings) at n = 13 can still discriminate.
   - At n = 131 the class of A **does** contain principally polarised varieties. The genus-130 carrier is therefore not excluded by any obstruction, and a count model has to close it.
   - LMFDB data at g = 4, 5 calibrate that count model. It predicts about 2^-7583 genus-130 carriers.
3. **Transfer (B7).** C5 answers the revisit condition of LEAD-TRF-small-genus-cover-general for non-x-line covers. Degree-3 (cubic Kummer, trigonal) GHS-type covers exist in odd characteristic, with genus (3^m - 1)/2. At n = 3 the floor is genus 4. That ties Gaudry's q^{4/3} decomposition and does not reach the JV genus-3 class. At k = 6 the floor is 13, which is above the Kummer floor of 9. The derivation predicts a closure and no gain.

## 1. Inputs read

- ATLAS.md: all 147 leads, every family, read in full.
- KRMAP.md: read in full.
- object-frame-ideation.md, sections 1-3.
- idea-generator.md: "Search heuristics" and "Obstructions as generative material".
- target-result-profile.md, part A.
- IC LEADERBOARD.md (Tables A-D) and bounds FRONTIER.md (headers and prime rows).
- Lead YAMLs, with the obstruction statements quoted verbatim in section 6.
- Ledger index (grep only) and these individual records: IDEA-20260811-c05798, IDEA-20260902-a0ed78, IDEA-20260902-701458, IDEA-20260806-0c9de1, IDEA-20261017-9b7e04, IDEA-20261009-c8433d, IDEA-20261009-61fc7f, IDEA-20261017-e3a6f1, IDEA-20261018-e0857e, IDEA-20261022-727676, and EV-SDEG-4a1c3d.

## 2. Findings from the reading that matter to the orchestrator

**F1. The B2 numbers are an enumerative-backend measurement, not an algebraic solving degree.** The lead row LEAD-ICE-prime-field-semaev-solving-degree reads EV-SDEG-4a1c3d (0.797 interval/random, 0.647 subgroup) as a Groebner/eliminant result. The evidence record's own scope statement says the opposite. It is a "Semaev m=5 serial split ... with per-triple subresultant PRS", and "Nothing here is claimed ... for non-enumerative (Groebner/algebraic) decomposition solvers". Its binding floor is the backward-triple count, and its resource check names the open class as "non-enumerative algebraic decomposition (EXP-ICEX-fa2b37, Groebner)". The algebraic tower degree is measured somewhere else: in the f4_fp_tower / msolve lane, IDEA-20261018-e0857e reports D >= 8 at m = 4, N = 20, about one degree per eight unknowns, with no plateau, blocked by memory. Recommendation: any B2 reasoning should cite both records and keep the scopes apart.

**F2. Ledger coverage of this field is already dense.** Ideas I generated and then found in the ledger (now killed as duplicates, section 4):
- O-semicontinuity of Macaulay ranks over the curve-parameter space: IDEA-20260811-c05798.
- The cover pushforward reduction lemma and the Chebotarev size law: IDEA-20260902-a0ed78.
- CM-trace factor bases: IDEA-20260902-701458.
- The Miller-cocycle / generalized-Jacobian splitting: IDEA-20261017-e3a6f1, IDEA-20261009-c8433d, IDEA-20261009-61fc7f.
- Kummer vs isogeny towers in f4_fp_tower: IDEA-20261022-727676.

**F3. The prime-field dimension gap: one equation over F_p.** This is the generative reading of SO-COVER and SO-ALGFB together.
- Over F_{q^n}, Weil restriction does two things. It turns the factor-base condition x in F_q into a Zariski-closed linear condition on an n-dimensional F_q-variety. It also turns one summation equation into n equations, because Frobenius is a field automorphism and so produces conjugate equations.
- Over F_p, every algebraic subset of E(F_p) is either 0-dimensional, with O(degree) points (SO-ALGFB), or of dimension at least 1, with about p points. No intermediate size is available.
- Aut(F_p) = 1, so no descent can split one equation into several.
- Three routes survive:
  - Z-towers: zero-dimensional loci of degree >= |F| with a low-degree multivariable description (PKM, isogeny and volcano towers). These are measured with no plateau so far.
  - A-archimedean presentations: digits and windows with carries (the digit presentation and Coppersmith leads). These are not in this field.
  - G-Galois-type membership predicates (fibre splitting, characters, SEA traces). C1 shows these are invisible to every algebraic oracle.
- Same-field covers only re-describe an E-side base (IDEA-20260902-a0ed78 (R)). Extension embeddings pay p^{2-2/n} (LEAD-ICP-extension-field-embedding).

## 3. Candidates

### C1 (prime, B1). Galois-invisibility lemma, and the S_d fully-split base as the third polylog-membership family

- **Bottleneck:** B1. Which non-enumerative oracle can exist for prime-field IC? It also gives LEAD-ICP-construction-normal-form (open_unexamined) a result-class axis, and it limits the O5 oracle design of LEAD-ICE-charged-toy-ic-exponent-vs-rho.
- **External ingredient:** the Chebotarev density theorem for function fields (Weil error term), and the Galois closure of a non-Galois cover. Explicit function-field error bounds: Fried-Jarden, *Field Arithmetic*, Prop. 6.4.8, and Murty-Scherk. RETRIEVED only as a secondary citation (arXiv:1901.06751); the book itself was not opened.
- **Construction (new relative to IDEA-20260902-a0ed78 (M)):**
  - Let g in F_p[t] be monic of degree d with Galois group S_d. Define F = { P in G : g(t) - x(P) splits completely over F_p }.
  - Membership costs one factorisation of a degree-d polynomial, O~(d^2 log p): polylogarithmic for d about log p / log log p.
  - The size is p/d! (Chebotarev for the Galois closure, of degree d!). Taking d! about p^{1-beta} gives |F| about p^beta, so every beta is reachable.
  - IDEA-20260902-a0ed78 (M) states that the cover-image bases with polylog membership "known to this session are exactly two families, and both are TOWERS". This is a third, non-tower family. Membership runs through the degree-d non-Galois cover, not through the degree-d! Galois closure that (S1) prices.
  - COMPUTED: for random monic g at p = 200003 and p = 1000003 (3 polynomials per cell, exhaustive over t in F_p), the fully-split counts divided by p/d! are 1.000, 1.001, 1.004, 0.995, 0.949 at p = 200003 and 1.000, 1.000, 0.995, 1.011, 1.042 at p = 1000003, for d = 3..7. The law holds at sizes where the Weil error term is vacuous; that it holds there is heuristic H1.1.
- **Lemma G (Galois invisibility):**
  - Setup: let pi: C -> E (or C -> P^1_x) be a finite F_p-morphism, and let F_tau be the set of P whose fibre has F_p-splitting type tau.
  - Let Sigma be any polynomial system over F_p in x-variables plus auxiliary fibre coordinates, built from S_{m+1} and the cover equations, that contains no polynomial vanishing on F_p but not on F_p-bar (no z^p - z, no prod(x - v)).
  - Then the projection of V_{F_p-bar}(Sigma) to x-space contains the whole decomposition variety V_R, of dimension m - 1. Over F_p-bar every fibre splits into points, and splitting type is Galois data, invisible to the ideal.
  - Corollary: any Groebner/F4/XL oracle that isolates F_tau-decompositions has to add field equations of degree >= p, or replace F_tau by its Zariski closure, whose membership polynomial has degree >= |F_tau|. The second option lands in SO-ALGFB, or in the Z-tower class when a low-width tower description exists, as for IDEA-20260902-701458's CM base (the roots of H_D).
  - Every other oracle for F_tau uses membership tests and group operations only, so SO-TABLE applies.
  - The proof is three lines (derived here; unreviewed). It explains the measured SO-MONO result at the level of mechanism: cycle types are Galois data.
- **Representation-operation pair:** (x-coordinate together with the auxiliary fibre polynomial g(t) - x; Sigma = translation by factor-base elements, the IC partial action).
- **Trichotomy:** partial-action (IC Class I). The relation vector propagates only under translation by base elements.
- **SO codes touched:**
  - SO-ALGFB, quoted in section 6. The premise "A target-independent algebraic locus of degree d yields O(d) usable points" covers Zariski-closed loci only. A Galois-type set is not Zariski-closed, so C1 sits outside that premise. Lemma G then shows the escape is worthless for algebraic oracles. This is a closure that extends SO-ALGFB, not a way around it.
  - SO-TABLE(p): the premise "Any decomposition oracle that enumerates or table-looks-up factor-base elements" is not escaped. By Lemma G, enumeration is the only oracle left.
  - SO-MONO: consistent. Lemma G is the general form of "cycle-type census is a no-go".
- **Tier:** X (classification of the B1 design space).
- **Predicted gain:** 0. PREDICTION: Lemma G survives review and the Galois-type cell closes.
  - H1.1: the fully-split density is (1 + o(1))/d! uniformly for d <= log p. Measured above at d <= 7, p <= 2^20.
  - H1.2: no non-algebraic oracle family other than enumeration and lattice methods reads the splitting type.
- **First step (about 0.5 day):**
  - (a) Write Lemma G and the corollary as a reviewed derivation.
  - (b) Toy confirmation at p about 2^16 with d in {4, 5}, m = 3. Run msolve on (S_4, the cover equations) and report the Hilbert dimension (expect m - 1 = 2). As a control, run the same base given by prod(x - v) (zero-dimensional) and record its solving degree.
  - (c) Amend IDEA-20260902-a0ed78 (M) with the S_d family.
- **Outcomes:**
  - Lemma G holds and the toy check gives dimension m - 1: closed_obstructed(theorem) for the Galois-type cell of KN-OPEN-020, recorded as a result class in LEAD-ICP-construction-normal-form.
  - A zero-dimensional Galois-type system of degree < |F| is found: open_next_step, best_measured = that system's solving degree.
- **Cost:** about 0.5 day of implementation, minutes of compute.
- **Self-kill risk:** high that a reviewer calls the lemma folklore. Its value lies in correcting (M), and in the routing it gives the O5 oracle.
- **--match phrasings, with the top hit from tools/lead_atlas.py:**
  - Own: "Galois-type fibre-splitting factor base invisible to Groebner". Top hits: LEAD-ICB-cofactor-torsion-quotients, LEAD-EXO-dl-character-sum-pseudorandom. No exact lead exists.
  - Plain: "factor base of x where a polynomial cover fully splits, membership by factoring". Top hit: LEAD-ICP-algebraic-membership-factor-base (18).
  - Obstruction vocabulary: "algebraic locus of degree d yields O(d) usable points membership polynomial prod(x - v) of degree B". Top hit: LEAD-ICP-algebraic-membership-factor-base (15).

### C2 (prime, B3 plus three open leads). Exact transport census: the full decomposition-count distribution on every vertex of a volcano, by FFT

- **Bottleneck:** B3 (constant engineering by choice of class representative). It decides:
  - LEAD-ICP-isogeny-transported-relation-yield (open_blocked on the arity-3 oracle).
  - The yield arms (b) and (c) of LEAD-STR-class-representative-ic-selection: the "5.8% l=2 yield effect" and the "7.2% model effect".
  - The count vector c_D and its variance in LEAD-ICE-decomposition-probability-audit.
- **External ingredients:** Velu's formulas (Velu 1971, C. R. Acad. Sci.; recalled) and Tate's isogeny theorem (recalled). An F_p-isogeny of degree coprime to N restricts to a group isomorphism phi: G -> G'. For the H2.1 prediction: Kohel-Shparlinski character sums over points of E(F_p) (LNCS 1838, 2000, pp. 395-404; RETRIEVED, abstract-level).
- **Theorem T (two lines, derived here):**
  - For any base F' in G', c_{phi^{-1}F'}(R) = c_{F'}(phi(R)), where c_F(R) = #{(P_i) in F^m : sum P_i = R}.
  - phi is a bijection on uniform targets, so every moment and the coverage of the transported base equal those of F' on E'.
  - Consequence, checked against experiments/EXP-ECTD-0cf008/specification.yaml:
    - The primary arms per endpoint are native, random, u2-transport and u2-native.
    - The specification already requires that the u = 2 transported arm agree "exactly" with its source, "any mismatch voids dependent science". It therefore treats isomorphic transport as Theorem T predicts.
    - It also excludes isogeny transport ("No same-point isogeny transport without a certified explicit evaluator and dual"). Theorem T shows an isogeny-transport arm would be another exact replica, so none is needed.
    - The contrasts that carry information are crater versus floor native, native versus random, and u2-native versus native. These are exactly what the FFT census computes, without the arity-3 relation oracle the lead is blocked on.
- **Instrument:**
  - For each vertex v of a whole toy volcano (24-28 bits; the crypto repo's 26-bit three-volcano census already carries verified Velu maps), take the native small-x base F_v at fixed L and also at matched |F_v|.
  - Compute L_v = log-set of F_v in Z/N (one enumeration of G per curve).
  - Compute c_v = 1_{L_v}^{*m} exactly by FFT of length N, for m = 3 and 4.
  - Report mean, variance, coverage and the full histogram, against freshly sampled random **negation-symmetric** subsets of equal size. Symmetry matters: x-bases satisfy F = -F.
- **Representation-operation pair:** (coordinates of P on the curve E_v of vertex v, class R2; Sigma = F_p-rational Velu isogenies between vertices plus isomorphic model changes x -> u^2 x + r, with translation by base points as the relation action).
- **Trichotomy:** coordinate-dependent. The native base is a function of the chosen presentation.
- **SO codes touched:**
  - SO-ISO, quoted. Its premise "rho and BSGS depend only on the group order and the automorphism group" binds generic algorithms. IC over a native small-x base is coordinate-dependent and escapes that premise. The census measures exactly that dependence.
  - SO-ALGFB, quoted. Its premise "mean per-target yield is binomial(B+m-1, m)/N for every base of size B" is not escaped. Theorem T extends it from the mean to the full distribution under transport. The census tests the higher moments of native bases, which the conservation statement does not fix.
- **Tier:** I.
- **Predicted gain:** factor 1.00 +- 0.02 at matched |F|. PREDICTION:
  - H2.1: native small-x sets behave like random symmetric subsets for m-fold sum statistics. The second-moment ratio is within the spread of the null draws at every vertex, with no trend in N. The basis is Kohel-Shparlinski-type equidistribution of x-intervals, which is not provable at |F| < sqrt(p); that is why H2.1 is a heuristic.
  - H2.2: at fixed L, the vertex-to-vertex yield differences are size effects (|F_v|^m), which accounts for the 5.8% and 7.2% readings.
- **First step (2-3 days of implementation, hours of compute):**
  - Reuse the verified volcano fixtures.
  - Write the log-set and FFT routine (numpy float64; N <= 2^26 fits in 1 GB per array).
  - Run 3 volcanoes x all vertices x m in {3, 4} x {fixed L, matched |F|}, with 32 null subsets per cell.
- **Outcomes:**
  - All matched-|F| ratios fall inside the null band and nothing grows over 20-28 bits: LEAD-ICP-isogeny-transported-relation-yield becomes closed_obstructed(measured, plus Theorem T), its block lifted; the yield half of LEAD-STR-class-representative-ic-selection closes as a size artifact (exhausted_at_scale at 28 bits).
  - A variance or coverage excess grows with N: open_next_step, best_measured = the excess and its slope. Only then run the IC panel.
- **Cost:** 2-3 days of implementation; about 10 CPU-hours.
- **Self-kill risk:** medium. It is an instrument and moves only constants. FFT memory caps it at about 2^28; P37 needs sampled moments.
- **--match phrasings:**
  - Own: "exact FFT convolution yield distribution across isogeny volcano". Top hit: LEAD-ICP-isogeny-transported-relation-yield (11).
  - Plain: "compare how many decompositions each curve in an isogeny class gives, exactly". Top hits: KR-IC-791cb7, KR-RHO-755e35, LEAD-STR-isogeny-transport-preprocessing.
  - Obstruction vocabulary: "isogenous curves F_p-isomorphic prime-order subgroups transport is exact level ratios equivalent". Top hits: KR-RHO-825bca, LEAD-STR-isogeny-transport-preprocessing.

### C3 (prime, B1/B2). Volcano-ball (level-restricted CM) tower factor base: a correspondence-step arm for the tower cell

- **Bottleneck:** B1/B2, the tower cell of KN-OPEN-020. Is the measured degree growth of tower-descended systems (IDEA-20261018-e0857e: about 1 degree per 8 unknowns, no plateau) universal across tower step types?
- **External ingredients:** volcano structure: Sutherland, "Isogeny volcanoes", ANTS X, Open Book Series 1 (2013) 507-530, arXiv:1208.5370, RETRIEVED (listing); Kohel 1996 thesis and Fouquet-Morain 2002, recalled, Schoof's count by Kronecker class numbers, and the modular polynomials Phi_l.
- **Construction:**
  - Pick t_0 with 4p = t_0^2 + |d_K| f^2, with |d_K| small (d_K = -4 is the extreme case, where the crater is j = 1728) and l^d dividing f exactly.
  - J_k = { j : the l-isogeny distance from the crater is <= k } is a set of F_p-rational j-invariants of size about h(d_K) l^k, tunable through k. Crater and non-floor vertices have all l+1 neighbours F_p-rational, so all walks of length k <= d stay rational.
  - F_k = { P in G : x(P) in J_k }.
  - Description: Phi_l(x_{i,j}, x_{i,j+1}) = 0 for j < k, and H_{d_K}(x_{i,k}) = 0. That is a zero-dimensional tower with bidegree (l+1, l+1) correspondence steps, compared with (2, 1) for PKM squaring.
  - Side result: IDEA-20260902-701458 (S2) states "NO single trace condition realises beta < 1/4" and names "intersecting F_t0 with a second cheap predicate" as the way past it. The level restriction is a concrete instance of that predicate, priced at polylog via volcano climbing, and it reaches any beta. This instantiates the record's named escape; it is not a correction.
  - Not available "for every p" cheaply at cryptographic size. Deep low-l volcanoes need l^k | f, probability l^-k per discriminant. Toy p can be constructed directly (p = a^2 + (2^k u)^2).
- **Representation-operation pair:** (x(P) read as the j-invariant of an auxiliary CM curve together with its volcano address; Sigma = translation by base points, with the Hecke correspondences T_l used only inside the description).
- **Trichotomy:** partial-action (IC Class I).
- **SO codes touched:**
  - SO-ALGFB, quoted. The premise "a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B" is met, not escaped (the degree is about |F|). The bounded-degree scope is escaped (KN-OPEN-020's open class "high-degree"). The conservation half still binds. The only open quantity is the oracle cost, which the statement prices only for the prod(x - v) description ("msolve on subgroup bases grows deg^{4.4} at m = 3").
  - SO-TABLE(p): the premise "enumerates or table-looks-up factor-base elements" is escaped, since F4 on the tower is non-enumerative.
- **Tier:** X.
- **Predicted gain:** none. PREDICTION H3.1: the degree-per-unknown slope is >= the Kummer-tower slope (about 1/8 at m = 4). Phi_2 has bidegree (3,3), and the walk variety carries a backtracking multiplicity of (l+1)/l per step, giving a larger quotient.
- **First step (1-2 days):**
  - Add a Phi_2 / Phi_3 arm to f4_fp_tower beside the existing Kummer and isogeny arms.
  - Use 3 constructed primes with 2-volcano depth >= 8, m in {3, 4}, matched N in {12, 15, 18, 20}, the same msolve options, and the existing positive control.
- **Outcomes:**
  - Slope >= Kummer within CI: closed_dominated (the correspondence-tower subcell), with best_measured = slope.
  - Slope lower, CI separated: open_next_step, best_measured = slope; escalate to the m = 3, N = 21-27 host of IDEA-20261018-e0857e.
  - Degree plateau over 3 values of N: open_next_step and escalate.
- **Cost:** 1-2 days of implementation; hours of compute, <= 5 GB at N <= 20.
- **Self-kill risk:** high (H3.1 predicts domination). It is kept because it is cheap on an existing engine, it is the one unmeasured step type, and it carries the beta-floor correction.
- **--match phrasings:**
  - Own: "modular polynomial walk ball around crater factor base". Top hit: LEAD-ICP-isogeny-transported-relation-yield (19).
  - Plain: "factor base of j-invariants near the top of an isogeny volcano". Top hit: LEAD-ICP-isogeny-transported-relation-yield (17).
  - Obstruction vocabulary: "subgroup coset Dickson images of low-degree maps msolve grows deg^{4.4}". Top hit: LEAD-ICP-algebraic-membership-factor-base (26).

### C4 (Koblitz, B5). Howe's polarisation invariant of the trace-zero variety A_n: theorem-level rung exclusions and a calibrated count model for ECC2K-130 carriers

- **Bottleneck:** B5, LEAD-ICB-ecc2k130-jacobian-carrier (open_next_step). Its closure "rests on a codimension heuristic (8,128), not a theorem". Its next step samples n = 11 and n = 13.
- **External ingredients:**
  - (i) Howe 1995/1996, as stated on Howe's VaNTAGe slides (1 March 2022, corrected), RETRIEVED. For a simple isogeny class with CM field K:
    - (2) "If K/K+ is ramified at a finite prime, or if pi - pibar is divisible by a prime of K inert in K/K+, then C contains a PPAV".
    - (3) "Suppose the middle coefficient c of f is coprime to q, and that C does not satisfy the conditions in (2). Then there is an integer s > 0 with N_{K/Q}(pi - pibar) = s^2, and C contains a PPAV if and only if c ≡ s mod m ... m = 4 if q is even."
  - (ii) Howe 2020, arXiv:2005.14365, RETRIEVED at abstract level: the number of PPAVs in a simple ordinary class with a given endomorphism ring is either 0 or a ratio of class numbers.
  - (iii) LMFDB av_fq_isog: complete for q = 2, g <= 6, RETRIEVED.
  - (iv) The Weil-restriction adjunction, Hom_{F_2}(J, Res E_K) = Hom_K(J_K, E_K). Recalled.
- **Derivation (here, unreviewed; validated at n = 3 and n = 5 against LMFDB):**
  - Res_{F_{2^n}/F_2}(E_K) has Frobenius eigenvalues tau zeta^j, j = 0..n-1. So P_A(T) = (T^{2n} - t_n T^n + 2^n)/(T^2 - t_1 T + 2). Its coefficients are the Lucas numbers U_k(t_1, 2), and its middle coefficient is c = U_n.
  - K = Q(pi_A) = Q(zeta_n, sqrt(-7)). This has degree 2(n-1) for n != 7, so A_n is simple for every prime n != 7; that holds whether or not 2 is primitive mod n. **Disagreement with the lead's wording:** the next step pairs "2 primitive mod n, A simple". Over F_2, simplicity does not need 2 primitive; primitivity bears on the stable-subspace and magic-number structure (SO-FROB). Which rungs are faithful should be chosen by Howe type (below), not by primitivity alone.
  - Complex conjugation is (-1, -1) in (Z/n)* x {+-1}. It lies in neither inertia group (at n: (Z/n)* x 1; at 7: 1 x {+-1}). So K/K+ is unramified at every finite prime.
  - N_{K/Q(sqrt-7)}(pi - pibar) = prod_b (tau zeta^b - taubar) = (tau^n - taubar^n)/(tau - taubar) = U_n. Hence s = |U_n|.
  - Every prime l dividing U_n has l ≡ (-7/l) mod n (Lucas rank of apparition n). Primes above l are inert in K/K+ iff (-7/l) = -1.
  - Result: **A_n has a PPAV iff U_n has a prime factor l ≡ -1 mod n, or U_n > 0.**
- **Branch validation at n = 3 (RETRIEVED plus COMPUTED):**
  - For A_3 over any F_q, the L-polynomial is 1 + t_1 T + (t_1^2 - q) T^2 + ..., so a = t_1 and b = U_3 = t_1^2 - q, and a^2 - b = q holds identically.
  - The Howe-Maisner-Nart-Ritzenthaler surface criterion (arXiv:math/0602650, RETRIEVED at snippet level): no PPAV iff a^2 - b = q, b < 0 and every prime dividing b is ≡ 1 mod 3. At n = 3 this coincides with the Lucas rule.
  - Checked against LMFDB has_principal_polarization for every ordinary simple A_3 over q in {2, 3, 4, 5, 7, 8, 9}: 36 of 36 classes agree.
  - The branches covered are: the unit, negative branch (2.2.ab_ab, 2.5.ac_ab); the split prime, negative branch (2.8.ab_ah, U_3 = -7 with 7 ≡ 1, no PPAV); and the **inert-prime branch** (2.3.ab_ac, 2.5.ab_ae, 2.9.ac_af, 2.9.ab_ai: U_3 < 0 with a factor ≡ -1 mod 3, PPAV).
  - Scope: this validates the branch logic at n = 3 only. The argument that K/K+ is unramified for n >= 5 at q = 2 remains this scout's own derivation, checked only through the n = 5 LMFDB row.
- **COMPUTED** (python/sympy; t_1 = -1, as for ECC2K-130, y^2 + xy = x^3 + 1, #E(F_2) = 4; n odd gives the same U_n for t_1 = +1):

| n | 2 primitive mod n | U_n | type |
|--:|:--:|:--|:--|
| 3 | yes | -1 | NO PPAV (matches LMFDB 2.2.ab_ab: has_principal_polarization = -1) |
| 5 | yes | -1 | NO PPAV (matches LMFDB 4.2.ab_ab_d_ab: -1) |
| 11 | yes | 23 (≡ 1 mod 11) | PPAV (sign) |
| 13 | yes | -1 | NO PPAV |
| 19 | yes | -457 | NO PPAV |
| 29 | yes | -8641 (≡ -1 mod 29) | PPAV (inert prime) |
| 131 | yes | 38531015900842053623 = 263 x 146505763881528721; second factor ≡ -1 mod 131, (-7/l) = -1 | PPAV (inert prime) |
| 139 | yes | negative, all factors ≡ 1 | NO PPAV |
| 163 | yes | positive, factors include 56498081 and 8610311 (≡ -1 mod 163) | PPAV (inert prime) |

- **RETRIEVED (LMFDB, q = 2):**
  - A_5 has neither a PPAV nor a Jacobian at g = 4.
  - A_5 x B has PPAVs but **no Jacobian** for all 5 classes at g = 5 and all 35 classes at g = 6. The rung n = 5 is therefore exactly carrier-free through genus dim A + 2; the atlas's "no carrier through genus 8 (... low power)" is partly a Howe zero at g = 4.
  - For comparison, A_3 x B has Jacobians in 2-3 of 5 classes at g = 3 and in 11-27 of about 210 classes at g = 5.
  - Calibration of Jacobian count against PPAV count, over simple ordinary classes: g = 4: jac/pp = 66/188, 90/328, 27/95 across PPAV-count bins (2, 8, 32); g = 5: 43/499, 279/4221, 705/12549, 154/3111 across bins (2, 8, 32, 128). The ratio is roughly flat in the PPAV count (0.27-0.35 at g = 4; 0.050-0.086 at g = 5), and falls by about 5x per genus against a moduli prediction of 2^{(3g-3) - g(g+1)/2} (4x per genus).
- **Consequences:**
  1. The n = 13 rung named in the lead's next step has no genus-12 carrier (B = 0), by theorem (no PPAV). The genus 13 and 14 cells (A_13 x B with dim B = 1, 2) are untouched: LMFDB's A_5 x B rows show such products do carry PPAVs via gluings. So n = 13 still tests the heuristic at genus dim A + 1 and dim A + 2, but a null at genus dim A carries no information. n = 19 and n = 139 behave the same way at genus dim A.
  2. n = 131 is of type "PPAV via inert prime", like n = 29, 37, 59, 61, 67, 83, 101, 107. No obstruction excludes a genus-130 carrier.
  3. Count model. #PPAV in the class is about h^-(K) (Howe 2020). With |d_K| = 131^{258} 7^{130} and K/K+ unramified, |d_K| = |d_{K+}|^2, and Brauer-Siegel gives log_2 h^- about 545. Multiplied by the calibrated Jacobian fraction c 2^{387 - 8515}, this gives about 2^{-7583} expected genus-130 carriers (PREDICTION; H4.1 Brauer-Siegel size of h^-; H4.2 Jacobian fraction among PPAVs of a class is about c_g 2^{3g-3-g(g+1)/2}, roughly independent of the class, as supported at g = 4, 5).
  4. The same model at n = 11 (degree-20 K, log_2 h^- about 22.6, fraction about 2^-28) predicts about 0.01 carriers. A random-zeta heuristic predicts about 0.7. The n = 11 search can discriminate between the two models only weakly.
- **Representation-operation pair:** (a divisor-class representation on a carrier curve C/F_2 whose Jacobian has A as isogeny factor; Sigma = Frobenius together with the F_2-rational Z/n Galois action on Res, under which A is the sum of constant-field twists E ⊗ psi).
- **Trichotomy:** coordinate-dependent (Jacobian IC reads Mumford coordinates).
- **SO codes touched:**
  - SO-TABLE(b), quoted. Its premise "Every oracle built from group operations and membership tests" is escaped: Jacobian IC uses divisor smoothness (factoring u(x)). Its scope "all binary and Koblitz curves" covers the target but not the carrier route.
  - SO-GEN: the premise "generic algorithm" is escaped (coordinate access).
  - SO-COVER: its scope "prime-field source curves" excludes this setting.
  - SO-FROB, quoted: "At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty". This route is not a factor-base route. A carries the Z/131 action as constant-field twists, and the carrier must realise all of them.
- **Tier:** X. The route itself, conditional on a carrier, is the lead's 2^37.2 against rho's 2^60.9.
- **Predicted gain:** 0 (closure). PREDICTION: the genus-130 rung closes on the count model.
- **First step (about 1 day):**
  - (a) Freeze the derivation above as a reviewed record, including the cross-check against LMFDB at n = 3, 5.
  - (b) Fit jacobian_count ~ alpha_g pp_count over all simple ordinary q = 2 classes at g = 3-5, from LMFDB (with the residual dispersion).
  - (c) PARI bnfinit on K_11 = Q(zeta_11, sqrt(-7)) for h^- and Howe's exact PPAV count. Predict the n = 11 genus-10 carrier count.
  - (d) In the lead's ladder, drop the genus-12 cell at n = 13 (vacuous by theorem). Keep n = 13 at genus 13-14, and run n = 11 at genus 10-12. Filter early on the prescribed place counts; for the B = 0 cell these are a_1 = 2, a_2 = 0, a_3 = 4, a_4 = 4, from a_k(C) = 2a_k(P^1) - a_k(E).
- **Outcomes:**
  - Calibration holds (dispersion within 2x) and the 131 prediction is << 1: closed_obstructed(cost_model) for the genus-dim-A rung of LEAD-ICB-ecc2k130-jacobian-carrier. The genus-dim-A cells at n = 13, 19, 139 are recorded as closed by theorem; their dim A + 1 and + 2 cells stay in the ladder.
  - The calibration fails, or an n = 11 carrier is found: open_next_step, best_measured = the carrier count at n = 11.
  - The genus 131-300 rungs stay open_next_step unless Howe-Lauter gluing counts close them.
- **Cost:** about 1 day of implementation; minutes to hours of compute.
- **Self-kill risk:** low on the theorem part (validated against LMFDB: A_5 at q = 2, and 36 A_3 classes over seven fields covering all three branches); medium on H4.2.
- **--match phrasings:**
  - Own: "Howe principal polarization obstruction trace-zero variety Jacobian". Top hit: LEAD-ICB-ecc2k130-jacobian-carrier (17).
  - Plain: "can the ECC2K-130 trace-zero variety be a Jacobian at all". Top hit: LEAD-ICB-ecc2k130-jacobian-carrier (22).
  - Obstruction vocabulary: "subfield curve not weakened by GHS descent map kills the large subgroup". Top hits: KR-IC-791cb7, KR-IC-5ea2f8, LEAD-TRF-ghs-binary-composite.

### C5 (transfer, B7). Cubic-Kummer (trigonal) GHS covers in odd characteristic: the non-x-line family that the revisit condition asks for

- **Bottleneck:** B7 and the revisit condition of LEAD-TRF-small-genus-cover-general: "a non-Kummer cover family (Hess Artin-Schreier analogue, non-x-line function) is constructed in odd characteristic". A larger weak class would also enter LEAD-TRF-teske-trapdoor-fp6-weak-class.
- **External ingredients:**
  - The Kani-Rosen idempotent decomposition of Jacobians (Kani-Rosen 1989; RETRIEVED via citing papers, e.g. arXiv:1702.00484).
  - The trigonal / S_3-closure structure: the S_3 closure of a degree-3 map E -> P^1 is an unramified Z/3 cover of the genus-2 discriminant curve H.
  - Hess's generalised GHS (Hess 2004, LMS JCM; recalled).
  - Diem's plane-curve index calculus O~(q^{2-2/(d-2)}) (ePrint 2005/119 and the later proven version; RETRIEVED).
- **Derivation (here, unreviewed):**
  - Let f: E -> P^1_K have degree 3, with K = F_{q^3}. It has 6 simple branch points, the discriminant curve H has genus 2, and E corresponds to a 3-torsion class alpha in Jac(H)[3].
  - If the branch locus is sigma-stable after a K-Moebius map, H is defined over F_q. The F_3[sigma]-span W of {alpha, sigma alpha, sigma^2 alpha} has dimension m (the cubic magic number). For n = 3, sigma - 1 is nilpotent, since x^3 - 1 = (x - 1)^3 in characteristic 3.
  - The (Z/3)^m-cover X of H is Galois over P^1 with group (Z/3)^m ⋊ Z/2. The component C = X/<tau> has genus (3^m - 1)/2: 1, 4, 13, 40 for m = 1..4.
  - For m = 2: Jac(C) ~ product over the 4 lines L of W of E_L. The 3 lines in sigma's cyclic orbit give E, E^sigma, E^sigma^2. The sigma-fixed line gives a subfield curve. So Jac(C) ~ Res_{K/F_q}(E) x E_0, at genus 4.
  - Dimension count: genus-2 H/F_q (3 parameters) with a size-2 unipotent block at eigenvalue 1 on Jac(H)[3] (a positive fraction of H) gives a family of E over F_{q^3} of the same dimension as all E. Unverified: whether this family is generic in j, and whether 3 divides #E(F_{q^3}).
  - Cost: IC on a non-hyperelliptic genus-4 curve via a degree-5 plane model is q^{4/3}. That **ties** Gaudry's n = 3 decomposition on every E(F_{q^3}) and stays above the JV/Smith plane-quartic q^1.
  - The comparator was checked (RETRIEVED, search abstracts). Gaudry's ePrint 2004/073 abstract gives O(q^{10/7}) for GF(q^3). The later version (HAL inria-00337631; J. Symbolic Comput. 2009) gives heuristic O~(q^{4/3}), i.e. q^{2-2/n}.
  - **Inconsistency flag:** KR-IC-46d822 writes "F_{q^3}: O(q^{10/7}) ... with double large primes". The 10/7 belongs to the 2004 preprint; the double-large-prime figure is 4/3. Against the 10/7 comparator a q^{4/3} cover would look like a gain; against the correct 4/3 it is a tie.
  - At k = 6 over F_p: dim_{F_3} Jac(H)[3] = 4 caps m at 4, and Res(E) of dimension 6 needs a sigma-orbit of 6 lines, so m >= 3 and genus >= 13. That is above the Kummer floor 9 quoted in the lead.
- **Representation-operation pair:** (divisor classes on the descended curve C/F_q; Sigma = the F_q-Frobenius together with the deck action of (Z/3)^m ⋊ Z/2).
- **Trichotomy:** coordinate-dependent.
- **SO codes touched:**
  - SO-COVER: its scope "prime-field source curves" excludes this setting (the source curve is over F_{q^3}).
  - Nearest closed lead (quoted): "Scope: Kummer/GHS covers of the x-line in odd characteristic". C5 lies exactly outside that scope; that is the revisit object.
- **Tier:** X.
- **Predicted gain:** 0. PREDICTION H5.1: the minimal genus of cubic-Kummer covers carrying Res(E) is 4 at n = 3 and 13 at k = 6; no configuration falls below the Kummer floors.
- **First step (1-2 days):**
  - (a) Census in Sage/GAP: monodromy over all branch-coincidence patterns and over m = 1..4, computing the genus and the line-orbit structure.
  - (b) An explicit m = 2 example over F_q, q in {7, 13}: build H, find alpha with (sigma - 1)^2 alpha = 0 != (sigma - 1) alpha, construct E_alpha, and check Jac(C) ~ Res(E) x E_0 by point counts over F_{q^k}, k <= 4. Record j(E_alpha) and #E_alpha(F_{q^3}) mod 3.
- **Outcomes:**
  - The census confirms genus >= 4 at n = 3 and >= 13 at k = 6: LEAD-TRF-small-genus-cover-general records the trigonal revisit as answered and stays closed_obstructed (proof); no change to the JV weak class.
  - A configuration with genus <= 3 at n = 3, or < 9 at k = 6: open_next_step for LEAD-TRF-small-genus-cover-general, with best_measured = that genus and its density.
- **Cost:** 1-2 days of implementation; minutes of compute.
- **Self-kill risk:** medium. The novelty is unverified (Hess-type constructions may already cover it), and the predicted outcome is no gain.
- **--match phrasings:**
  - Own: "trigonal fibre product cover genus odd characteristic Weil descent". Top hit: LEAD-TRF-odd-char-descent-smith-quartic (21).
  - Plain: "Weil descent using a degree-3 map instead of the x-coordinate". Top hits: KR-IC-5ea2f8, LEAD-TRF-ghs-binary-composite, LEAD-TRF-odd-char-descent-smith-quartic.
  - Obstruction vocabulary: "Riemann-Hurwitz census Kummer GHS covers of the x-line in odd characteristic genus". Top hits: LEAD-TRF-odd-char-descent-smith-quartic, KR-IC-791cb7, LEAD-TRF-small-genus-cover-general.

## 4. Killed candidates (killed by me before proposing)

- **K1. Degeneracy-locus scan of the model x isogeny-class family for solving-degree drops.** A duplicate of IDEA-20260811-c05798 (O-semicontinuity). Lower semicontinuity of Macaulay rank makes special loci no better for rank functionals.
- **K2. Same-field covers C -> E (bielliptic, quadric-pencil, catalog pullbacks) as relation sources.** IDEA-20260902-a0ed78 (R) shows they reduce to an E-side base phi(C(F_p)) whose description degree is multiplied by deg phi. SO-COVER applies for the ambient reading.
- **K3. The S_d fully-split base as an exponent candidate.** Lemma G (C1) leaves it enumeration-only, so SO-TABLE applies. It survives only as C1's correction.
- **K4. Elliptic-torsion / Lattes / Velu x-map towers on an auxiliary curve (a PKM analogue for any p).** The f4_fp_tower already has an isogeny-tower arm (IDEA-20261022-727676, "Kummer vs isogeny tower"). Dominated by the existing measurement.
- **K5. Generalized-Jacobian splitting giving a computable Miller-cocycle primitive U.** A duplicate of IDEA-20261017-e3a6f1 K1 ("the graph R->(R,U(R)) is a subgroup ... a change of coordinates") and IDEA-20261009-c8433d. It leaves only a coordinate-statistic hunt, which is LEAD-EXO-coordinate-statistic-leakage's question.
- **K6. Bielliptic genus-2 "small-square" base x = t^2.** A sub-base of the small-x base, with the degree doubled and the reach unchanged. Covered by LEAD-EXO-split-jacobian-projection.
- **K7. Small-integer-coefficient curves (secp256k1, a = 0, b = 7) with integer summation relations.** Integer points of height <= L on S_m = 0 number about L^{m - deg}. This is the xedni obstruction (KR-IC-cd159a).
- **K8. Res_{F_{p^2}/F_p} of a non-F_p-rational isogenous E'' (Res E'' ~ E x E').** The extension-embedding cost model applies: "Gaudry's cost on E(F_{p^n}) is O~(p^{2-2/n})".
- **K9. The conic quotient E/<P -> R - P> = P^1 for small roots.** This is FGHR symmetrisation (KR-IC-955fd6), already in the Coppersmith lead. In any case m = 2 is at least N^{2/3} whatever the oracle.
- **K10. A target-dependent window base (a model with x(R) = 0).** Relations from different targets do not share a base. This is a known-log pool (H-BINSTD-1447cf).
- **K11. Hess-type Moebius-twisted x on ECC2K-130.** The branch-locus Galois orbit has size about 2n, giving genus about 2^{n-1} (MMT Remark 21).
- **K12. Superelliptic (y^131 = f) or F_2-rational cyclic-cover Pryms as ECC2K-130 carriers.** A is a sum of **constant-field** twists E ⊗ psi. Pryms of geometric covers are sums of **geometric** twists L(D, chi), which contain constant-field twists only by coincidence. In addition, ramified F_2-rational Z/131 covers need residue degree in 130Z (genus >= 8320).

## 5. Session computations (reproducible)

- **Fully-split density:** /private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/splitcount.py (stdlib). Value-histogram counting of g(t) over all t in F_p, p in {200003, 1000003}, d = 3..7, 3 random monic g per cell, seed 20261024. Ratios are given in C1.
- **Howe type of A_n:** sympy. Lucas U_n(-1, 2) by recurrence, factorint, a residue check mod n and (-7/l). The table is in C4. Spot check: 146505763881528721 is prime, ≡ 130 mod 131, (-7/l) = -1; 263 ≡ 1 mod 131.
- **LMFDB SQL (av_fq_isog, q = 2):**
  - g <= 6 totals.
  - The labels 2.2.ab_ab, 2.2.b_ab, 4.2.ab_ab_d_ab, 4.2.b_ab_ad_ab, 6.2.ab_ab_d_ab_af_h and 6.2.b_ab_ad_ab_f_h.
  - Grouped counts of classes containing A_3/A_5 at g = 3-6.
  - PPAV-count bins against jacobian_count at g = 4, 5.
  - has_principal_polarization for the 42 A_3 labels over q in {2, 3, 4, 5, 7, 8, 9}: 36 simple classes, all matching the Lucas/Howe rule; the 6 non-simple classes at q = 7 excluded.

## 6. Quoted obstruction statements (verbatim from the lead YAMLs)

- SO-GEN = `LEAD-RHO-generic-sqrt-lower-bound` [theorem]: "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r."
- SO-GGM = `LEAD-EXO-augmented-oracle-ggm` [theorem]: "Each named oracle is GGM-simulable (jet, endomorphism O(1); incidence O(m); halving equivalent to x; net O(log N)), so the Shoup lower bound closes its candidate family at exponent 1/2 (KN-FIND-002, KN-FIND-b7e091, KN-FIND-194294; EV-GGM-001 strong). Measured: the x-oracle gives Y_A = Y_B exactly (no yield advantage, EV-ECDLP-fd61e4 strong) and the m=3 MITM split saving is attributable to the split, not the oracle (EV-ECDLP-7367e2). Scope: oracles, not resources (see IDEA-20260808-ea3b4f)."
- SO-TABLE(b) = `LEAD-ICB-generic-table-oracle` [theorem]: "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged."
- SO-TABLE(p) = `LEAD-ICP-generic-table-decomposition` [theorem]: "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p."
- SO-ISO = `LEAD-STR-isogeny-class-generic-invariance` [theorem]: "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (±5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve."
- SO-COVER = `LEAD-TRF-same-field-genus-g-embedding` [theorem]: "Tate multiplicativity gives #Jac(C)(F_p) = N * #A(F_p) with #A = Theta(N^{g-1}); genus-g index calculus costs O~(q^{2-2/g}) >= q for g >= 2, at least a full exponent above rho's N^{1/2}; quadric-pencil and quartic models of E itself are isomorphic models with the same group. Scope: prime-field source curves, any same-field cover (DEC-20260902-4c82fd)."
- SO-ALGFB = `LEAD-ICP-algebraic-membership-factor-base` [theorem]: "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
- SO-MONO = `LEAD-ICE-semaev-cover-monodromy` [proof]: "For every p > 3 and nonsingular E/F_p, the generic monodromy is (Z/2)^{m-2} (ordered base) and (Z/2)^{m-2} x| S_{m-1} (symmetric base, m >= 4) with an exact Frobenius rule on unramified fibres (KN-FIND-bdcd60, two blind re-derivations); on the factor-base locus S_m splits completely with an exact root multiset, so the generic-fibre cycle-type census is a no-go as a relation-rate probe at every m >= 3 (KN-FIND-4f0d84). GOAL-MONO-001 completed under DEC-20261022-a0f165."
- SO-FROB = `LEAD-ICB-frobenius-orbit-factor-base` [proof]: "For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more (H-FROB-6774fb supported, DEC-20260923-e6cd5d; the tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value for orbit-union, normal-basis and polynomial bases, n = 11..23). At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty (H-BINSTD-b1f016 replicated). Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0. Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure."
- SO-DECK = `LEAD-EXO-torsor-deck-period` [proof]: "For a generically Galois cover every rational deck-invariant factors through the quotient; a transitive fibre-orbit label is base data; a connected nontrivial cover has no rational section, so a rational target-compatible selector is a missing section or trivialization (IDEA-010 gate, independently verified). The cubical/biextension lift lands on the invertible side of the recognizable/invertible duality, i.e. computing its label costs the log (IDEA-20260920-376b00)."
- NEAR-SMALLGENUS = `LEAD-TRF-small-genus-cover-general` [proof]: "Riemann-Hurwitz census g = 1 - 2^m + 2^{m-2} R: among 2-torsion Kummer covers of E/F_{q^3} only the JV configuration gives g <= 3 (others g in {1, 7, 9, 13}); for E/GF(p^k) with F_p(j) = GF(p^k) every GHS cover has genus >= 9, 49, 41 at k = 6, 10, 14, which repriced 247 of 846 cover_descent rows down to marginal/boundary. Scope: Kummer/GHS covers of the x-line in odd characteristic."
- NEAR-EXTEMB = `LEAD-ICP-extension-field-embedding` [cost_model]: "Gaudry's cost on E(F_{p^n}) is O~(p^{2-2/n}) against the original sqrt(p): p at n = 2 and p^{4/3} at n = 3; the embedding enlarges the problem faster than the subfield helps. Scope: any fixed n."
- NEAR-SPLITJAC = `LEAD-EXO-split-jacobian-projection` [proof]: "Cross-genus Poincare-factor embedding cannot beat Pollard rho on the embedded elliptic factor because the Hasse-Weil order inflation of the ambient Jacobian outweighs genus-2 IC savings (KN-FIND-61347e); the IDEA-002 projected-smoothness counting gate finds no route with lambda,mu <= 0.45 and its projected endpoint fails the known-log interface."
- NEAR-SEMSD = `LEAD-ICE-prime-field-semaev-solving-degree` [literature]: "Naive Semaev IC over prime fields cannot beat generic methods (KR-IC-5931ee). The program reproduced it: at balanced L = q^(1/5) on ordinary toy curves, beta_work(B1) = 0.797 on interval and random bases and 0.647 on subgroup bases against the 0.30 sub-rho threshold, 36/36 cells, 105/105 FGLM checks (EV-SDEG-4a1c3d, strong); in ecbench the root-finding/pair-table oracle dominates any prime-field Groebner arm."

## 7. Citations and provenance

- Howe, theorem on PPAVs in simple isogeny classes (Howe 1995 Trans. AMS; Howe 1996), quoted from Howe's VaNTAGe slides "Deducing information about a curve over a finite field from its Weil polynomial", 1 March 2022 (corrected slides), https://math.mit.edu/~drew/vantage/HoweSlides.pdf. **RETRIEVED** (PDF text extracted). The primary Trans. AMS text was not opened.
- Howe, "Variations in the distribution of principally polarized abelian varieties among isogeny classes", arXiv:2005.14365 (2020). **RETRIEVED** (abstract only).
- LMFDB av_fq_isog (q = 2, g <= 6), via the LMFDB MCP SQL mirror. **RETRIEVED**.
- Howe-Maisner-Nart-Ritzenthaler surface criterion, arXiv:math/0602650. RETRIEVED (search snippet only). Consistent with A_3.
- Kohel-Shparlinski, LNCS 1838 (ANTS IV, 2000), 395-404. RETRIEVED (abstract-level).
- Diem, Math. Comp. 80 (2011), 443-475, O~(q^{2-2/g}); Diem, ePrint 2005/119 (plane curves, O~(q^{2-2/(d-2)})). RETRIEVED (listing and abstract).
- Kani-Rosen, "Idempotent relations and factors of Jacobians", Math. Ann. (1989). RETRIEVED via citing papers (arXiv:1702.00484); volume and pages unverified.
- Sutherland, "Isogeny volcanoes", Open Book Series 1 (ANTS X, 2013) 507-530. RETRIEVED (listing).
- Chebotarev for function fields with explicit error (Fried-Jarden, Prop. 6.4.8; Murty-Scherk). RETRIEVED only as a secondary citation, arXiv:1901.06751.
- Gaudry, ePrint 2004/073 (q^{10/7}) and the HAL / JSC 2009 version (q^{4/3} = q^{2-2/n} at n = 3). RETRIEVED (abstracts).
- EXP-ECTD-0cf008 specification.yaml: read locally (internal).
- Velu (1971); Tate isogeny theorem; Kohel (1996, thesis); Fouquet-Morain (2002); Hess, "Generalising the GHS attack" (LMS JCM, 2004); Petit-Kosters-Messeng (PKC 2016). All **recalled**, not opened here.

## 8. Sub-areas of this field searched with no candidate

- **X_0(N)/X_1(N) carriers for prime-field E.** The genus is about N^2/24, and the diamond-operator reformulation is already in the ledger (IDEA-20260806-0c9de1).
- **CM-volcano point names** (IDEA-20261017-9b7e04). Covered there.
- **Artin-Schreier covers of E over F_p.** These are degenerate: y^p - y = f(P) has a rational fibre point only when f(P) = 0.
- **Kummer covers of E over F_p.** These give character-constant sets, covered by SO-ALGFB.
- **Tetragonal and Donagi constructions for prime-field E.** These re-describe E-side bases (IDEA-20260902-a0ed78 (R)) or inflate the group (SO-COVER).
- **Odd-characteristic Weil restriction for prime-field sources.** No subfield exists; the extension-embedding cost model applies.
- **Split Jacobians E x E' and Richelot/Kani gluings over F_p.** Covered by SO-COVER and LEAD-EXO-split-jacobian-projection.
- **Isogeny-class or model selection for solving degree.** Covered by IDEA-20260811-c05798 (O-semicontinuity).
- **Generalized Jacobians as a transfer.** Covered by IDEA-20261017-e3a6f1 and IDEA-20261009-c8433d.
