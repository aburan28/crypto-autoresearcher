# 200 candidate CM/isogeny research jobs for elliptic-curve cryptanalysis

## Scope

This replaces the unrelated crypto-market/trading proposal. The subject is elliptic-curve cryptanalysis, especially the discrete-log problem (ECDLP), CM discriminants, endomorphism orders, and **horizontal isogenies on the same crater / same endomorphism-order level**, alongside controlled vertical moves between conductor levels.

These are **candidate research jobs**, not 200 claims of priority, attacks, or established findings. Novelty against the published literature is **unverified** for every entry; repository deduplication is partial and each item needs a focused prior-art check before becoming a canonical idea. The central comparison is between horizontal neighbors at the same crater / endomorphism-order level, with vertical conductor moves kept as a separate control.

## Mathematical guardrails

For an ordinary elliptic curve E/F_q with Frobenius trace t, the Frobenius discriminant is D_pi = t² − 4q = v²D_K, where D_K is the fundamental discriminant of the imaginary quadratic CM field. The actual endomorphism ring is an order Z + f O_K with f dividing v; knowing D_pi alone does not certify f. The curve’s Weierstrass discriminant Δ_E is a separate field element and must not be conflated with D_pi or D_K.

A horizontal crater comparison keeps q, t, group order, CM field, and endomorphism-order level fixed; vertical isogenies change the order conductor while preserving the isogeny class and point count. An observed finite-size runtime difference can be algorithm- or implementation-specific. It is not by itself a generic DLP hardness separation: Jao–Miller–Venkatesan prove random reducibility under stated hypotheses for curves with the same order and nearly the same endomorphism rings. Isogeny maps only transport the selected n-order subgroup bijectively when their action on that subgroup is invertible; certify this rather than assuming it.

For the CryptoPro-B audit thread, existing notes report D_K = −619, class number 5, and degree-5/7 horizontal neighbors, while explicit maps and several certifications remain unfinished. Treat those as leads to reproduce, not as verified cryptanalytic advantages.

## Relation to prior project work

The repository already contains a substantial CM/isogeny ECDLP program, including broad isogeny-class invariance, special-j/CM, volcano-depth, class-group, and Semaev/solver proposals. ECDLP-IDEA-434 specifically studies mean Semaev decomposition yield across a fixed isogeny class. This atlas avoids restating that exact question, but related follow-up dimensions may overlap other existing proposals. Treat the entries as an exploratory backlog, not as 200 repository-unique or literature-verified discoveries; deduplicate every candidate against the full active, deferred, rejected, and published-work records before canonical registration.

## How to read each job

Each entry is a falsifiable experiment lead. Before running it, the autoresearcher should instantiate: (1) hypothesis and mechanism; (2) exact curves, field, order, subgroup, and certified CM/order data; (3) comparison arms and baseline; (4) map, preprocessing, memory, and compute accounting; (5) paired seeds and controls; (6) explicit falsifier and stopping rule; (7) reproducible code, certificates, and outputs. The experiments should use tractable toy and medium curves to test mechanisms, and must not claim cryptographic-size breaks from toy-scale wins. A final verdict is **reject**, **monitor**, or **promote**; promotion requires independent replication and a measured end-to-end advantage over a suitable generic baseline.

## I. CM discriminants, orders, and individual curve fingerprints

1. Discriminant-separation test — Hypothesis: D_pi, the field discriminant D_K, the actual End(E) discriminant, and the Weierstrass discriminant Δ_E carry distinct predictive information; fit each separately against predeclared solver metrics on matched ordinary curves, then test whether any survives adjustment for q, group order, model, and subgroup.

2. Frobenius-conductor versus endomorphism-conductor test — For ordinary curves with D_pi = v²D_K, test whether the actual conductor f | v predicts a cryptanalytic observable after controlling for v; certify End(E) independently and falsify any apparent effect caused by substituting v for f.

3. Conductor-valuation fingerprint — Encode each curve’s conductor by its prime-valuation vector rather than its integer size; test whether this vector predicts held-out relation-matrix rank growth or polynomial-system degree on matched q,t,N cohorts.

4. Fundamental-discriminant factor signature — Test whether the prime factorization and local residue classes of D_K predict any pre-registered Semaev-system statistic beyond |D_K|; use matched discriminant-size bins and shuffled discriminant labels as negative controls.

5. Frobenius-discriminant square-part audit — Recompute the square factor v² of D_pi with certified arithmetic and test whether prior studies’ use of D_pi alone merged curves with different actual endomorphism orders; report misclassification rate, not a security score.

6. Class-number versus DLP-cost separation — Across fixed-q, fixed-N CM classes, regress class number h(D_K) against measured preprocessing and solver cost while independently varying group order factors; reject a class-number effect if order or field representation explains it.

7. Reduced-form shortest-vector descriptor — Derive shortest reduced binary quadratic forms for each CM order and test whether their norm spectrum correlates with curve-specific solver ideal statistics; compare against random forms with the same discriminant.

8. Small-norm endomorphism inventory — Enumerate certified endomorphism norms below a fixed bound and test whether their availability changes only scalar multiplication cost or also relation collection and elimination; separate the two stages.

9. Norm-representation multiplicity — Count representations of small primes by the CM norm form and test whether this predicts rational low-degree isogeny availability and measurable point-map cost, with degree and field-size matched controls.

10. Automorphism-stabilizer control — Compare j=0, j=1728, and generic-j curves after quotienting known automorphisms; test whether any solver gain remains once duplicate variables and equivalent points are canonicalized.

11. CM class-polynomial coefficient-height fingerprint — For each D_K, measure exact H_D coefficient height and modular reduction behavior, then test whether these construction descriptors predict only curve-generation cost or any independent ECDLP measurement.

12. Root-specific class-polynomial residue test — Within one split CM class, compare the modular roots j_i under identical group and algorithm budgets; test whether root-specific solver variation exceeds seed-to-seed noise and persists on held-out targets.

13. Ring-class splitting vector — Compute the splitting of small rational primes in ring class fields attached to the tested orders; test whether this vector predicts crater edge labels or solver features after conditioning on local Kronecker symbols.

14. Discriminant-localization test — Change one local prime factor of D_K across synthetic ordinary-curve families while matching bit size and N; test for a causal change in a predeclared endomorphism or relation-generation metric.

15. Bad-prime denominator fingerprint — Measure primes dividing CM model denominators and class-polynomial discriminants; test whether excluding these primes removes apparent anomalous reductions in modular equation solvers.

16. CM lift sensitivity — Lift matched finite-field curves to several characteristic-zero CM models and test whether lift choice changes only representation metadata or the measured finite-field relation ideal after canonical reduction.

17. Trace ambiguity resolver — Given q and t, enumerate candidate orders dividing v and test how often a trace-only pipeline mislabels the actual End(E); require a certified endomorphism test before downstream correlation.

18. CM discriminant feature null test — Permute D_K labels among curves matched on q,t,N and conductor depth; determine whether any reported discriminant-feature effect exceeds this structure-preserving null distribution.

19. Coefficient-discriminant invariance audit — Apply admissible Weierstrass coordinate changes to the same curve and verify that Δ_E changes by the expected scaling while D_pi and D_K remain fixed; test whether any pipeline mistakenly treats Δ_E as a CM invariant.

20. CryptoPro-B discriminant replication — Independently certify the audit’s D_K = -619, h = 5, and maximal-order claim, then test the certification pipeline against curves with deliberately ambiguous conductor data; do not infer weakness from the small class number.

## II. Same-crater horizontal isogenies and class-group structure

21. Horizontal-neighbor solver fingerprint — For every certified same-order crater neighbor, compare relation collection, elimination, and extraction separately at equal budgets; test whether a vertex-specific effect remains after the exact same target points are transported.

22. Crater cycle-length predictor — Hypothesis: class-group cycle lengths for small split primes predict a measurable solver statistic; enumerate full horizontal cycles and evaluate the predeclared predictor on held-out isogeny classes.

23. Horizontal kernel-orientation asymmetry — Pair the two horizontal kernels for each split prime and test whether their orientation relative to Frobenius changes point-map cost or polynomial-system sparsity; swap kernel labels as a placebo.

24. Commuting horizontal square test — For distinct split primes ℓ and r, traverse both paths around each class-group square and compare composed maps and solver encodings; test whether path order leaves any effect after canonical point identification.

25. Class-group generator choice benchmark — Present the same crater vertex through different small-prime generating sets and test whether the chosen path basis affects only navigation cost or also downstream solver runtime.

26. Shortest horizontal path versus map cost — Compare shortest class-group path length with exact composite-isogeny evaluation cost, including intermediate normalization; fit and validate on unseen class polynomials.

27. Path multiplicity and endpoint fingerprint — When multiple horizontal paths reach one j-root, compare independently composed maps and resulting encoded DLP instances; test for path-dependent implementation artifacts versus mathematical invariance.

28. Crater automorphism stabilizer correction — Measure class-group orbit sizes with curve automorphisms included and excluded; test whether naive vertex counts spuriously correlate with relation yield or solver success.

29. Frobenius-orbit quotient of crater — Quotient the crater graph by Frobenius and compare its cycle statistics with the unquotiented graph; test which representation best predicts held-out map and solver costs.

30. Horizontal dual-map normalization — Compose each horizontal isogeny with its dual and verify the degree multiplication map exactly; test whether normalization bugs account for any apparent cross-vertex DLP discrepancy.

31. Same-crater model-isomorphism control — Represent each crater vertex in several isomorphic Weierstrass models and run identical arithmetic; estimate model-level variance before attributing any residual to j or CM structure.

32. Crater edge-degree ablation — Hold vertices fixed while removing one isogeny degree from the available path set; test whether access to a particular small-degree edge improves only transport overhead or a measured attack pipeline.

33. Horizontal path batching — Batch point maps across many target points along one fixed crater path and measure amortized cost; compare against independently optimized maps and include precomputation in the total.

34. Class-group relation matrix — Build the relation matrix of small split-prime ideal classes and test whether its Smith normal form predicts navigation effort to a target vertex, not DLP hardness by assertion.

35. Crater spectral-gap versus finite-sample walk test — Compare predicted mixing proxies with empirical mixing on complete small craters; test whether walk mixing predicts the number of trials needed to find a vertex with a chosen implementation property.

36. Same-level degree-prime holdout — Fit any horizontal-neighbor effect using one set of split primes, then predict effects for unseen split-prime degrees on the same order; reject if only degree-specific tuning explains it.

37. Kernel polynomial height along crater — Measure exact kernel-polynomial coefficient growth around one crater and test whether it predicts map evaluation cost after degree and field-operation counts are controlled.

38. Map composition versus direct kernel — Compare a composed path map to a directly computed endpoint isogeny at equal correctness guarantees; measure time, memory, and point-map throughput on held-out endpoints.

39. Crater endpoint selection without DLP oracle — Test whether cheap public descriptors select a vertex with faster measured solver setup, using nested training/holdout by entire isogeny class; never select on target logs.

40. CryptoPro-B five-root crater audit — Reconstruct all five roots for D_K = -619, certify the claimed rational degree-5/7 horizontal edges and explicit point maps, then quantify only reproducible vertex-level implementation differences.

## III. Vertical conductor strata and local volcano geometry

41. Prime-by-prime depth vector — Compare curves at the same q,t but different conductor valuation vectors; test whether local depth predicts a held-out solver metric beyond total conductor and field representation.

42. Split-versus-inert descent control — For primes ℓ with different Kronecker symbols (D_K/ℓ), compare observed horizontal and descending edge counts to theory, then test whether edge type changes exact transport cost.

43. Ramified-prime crater test — At ramified ℓ, enumerate the local graph with multiplicity-aware kernel data and test whether the exceptional edge pattern creates a solver-relevant invariant beyond ordinary depth.

44. Volcano-depth calibration — Infer depth from isogeny counts and independently certify End(E); measure false depth assignments when rationality, kernel multiplicity, or Frobenius action is mishandled.

45. Commuting-prime volcano grid — For conductor supported at distinct primes ℓ and r, construct a local product grid and test whether moving down in either order gives identical endomorphism-order labels and target map costs.

46. Local depth interaction — Test whether paired depths at ℓ and r have a non-additive effect on a fixed algebraic solver statistic; use factorial matched designs and held-out conductor combinations.

47. Frobenius versus Verschiebung edge classifier — Separate rational Frobenius/Verschiebung maps from ordinary volcano edges and test whether pipeline misclassification creates spurious low-degree endomorphisms.

48. Depth-zero versus first-descendant comparison — Compare crater vertices with their first vertical descendants under fixed q,t,N and subgroup order; measure map cost and relation-system geometry as separate outcomes.

49. Deep-descendant endpoint study — On tractable families, compare the deepest certified order in a chosen ℓ-direction with shallow levels; include total path and kernel-construction cost in any claimed gain.

50. Conductor support ablation — Construct matched orders whose conductors share size but differ in prime support; test whether local support, rather than conductor magnitude, predicts a predeclared ideal-system property.

51. Order inclusion versus isogeny degree — Verify the divisibility relation between adjacent endomorphism orders from explicit maps; test whether degree-only metadata incorrectly labels horizontal edges as descending.

52. Prime-to-conductor navigation test — Use isogenies of degree coprime to the conductor and test whether their actions preserve the same order as predicted; catch exceptional cases with certified endomorphism computations.

53. Multi-prime depth ambiguity — Infer a bivariate local level from two volcanoes and test whether single-prime depth heuristics misidentify curves when the conductor has multiple factors.

54. Local volcano topology completeness — Exhaustively enumerate all ℓ-kernels on small ordinary curves and compare with predicted vertex degree and edge orientation; make missing-edge rate a preregistered acceptance metric.

55. Conductor-changing map distortion — Compare coordinate-map degree, coefficient size, and evaluation count for vertical maps at equal ℓ-depth; test which is an arithmetic cost and which is merely representation cost.

56. Descending path reversal test — Compose a descending map with its dual and compare the result to [ℓ]; test scalar and kernel factors exactly before using transported DLP instances.

57. Ring-order-specific torsion emergence — Test whether rational ℓ-torsion appears or disappears across vertical levels as predicted by Frobenius; compare group structure and solver outcome without conflating them.

58. Volcano-neighbor matching by actual order — Re-run neighbor comparisons after certifying End(E), then quantify how much apparent same-level variance was actually conductor mismatch.

59. Vertical-path precomputation crossover — Measure the target-count threshold at which precomputing a vertical isogeny path pays off; include curve setup, maps, and inverse/verification costs.

60. CryptoPro-B 103-neighbor certification — Audit the reported 104 descending 103-isogeny neighbors and depth-one classification with exact maps on tractable fixtures; use the result to validate graph tooling, not to infer DLP weakness.

## IV. Isogeny maps, subgroup transport, and exact instance equivalence

61. Prime-to-order bijection audit — For a degree-d isogeny with gcd(d,n)=1, certify the induced map on the n-order subgroup is bijective and verify transported DLP instances across randomized targets.

62. Kernel-overlap transport test — When gcd(d,n) is not 1, enumerate kernel intersections with the target subgroup and measure exactly when a transported log is recoverable; use this as a rejection gate for invalid comparisons.

63. Point-map versus scalar-map cost — Compare evaluating φ(Q) once with applying φ to a full relation batch; measure field operations and memory while checking every output against an independent implementation.

64. Target-only versus full-instance transport — Compare transporting only Q, transporting both P and Q, and reconstructing a new generator; test whether benchmark changes came from subgroup generator choice.

65. Transported target distribution — Map random subgroup targets through a fixed isogeny and test uniformity and duplicate rates; use exact group enumeration on small curves and statistical tests on larger ones.

66. Isogeny-map sign and coordinate normalization — Generate equivalent maps under kernel and codomain normalization and verify identical abstract group maps; test whether sign conventions bias relation labels.

67. Dual-map recovery certificate — For every transported target, apply the dual and divide by degree where invertible; verify exact recovery and record failures as map-pipeline bugs.

68. Map evaluation arithmetic profile — Count additions, multiplications, inversions, and exceptional branches for each map; test whether predicted field-operation counts explain measured timing across curve models.

69. Map batch-size crossover — Benchmark scalar, vectorized, and batched map evaluation over increasing target sets; find the break-even point and validate on a second hardware/runtime stack.

70. Isogeny serialization equivalence — Serialize kernels and maps in independent formats, reconstruct, and verify point action; test whether serialization errors explain irreproducible cross-curve results.

71. Map-path certificate format — Create a compact proof object for each isogeny path and target transport; test independent replay and verification cost across class sizes and path lengths.

72. Transported relation verification — Map every point in a collected relation and verify the group sum on the destination curve; measure failure rate and establish a hard gate before counting a relation.

73. Same source points, native coordinates — Compare the image of a fixed source point set with a destination-native set matched by cardinality and distribution; isolate coordinate effects from point-selection effects.

74. Target-map conditioning — Test whether isogeny image coordinates have different low-degree, trace, or subspace statistics than native points; use random maps and source points as a conditional null.

75. Subgroup-generator conditioning — Across transported generators P′, compare coordinate fingerprints with random generators of the same order; test whether generator conditioning affects solver outcomes.

76. Map-induced x-coordinate multiplicity — Measure collisions in x(φ(P)) after sign quotienting and test whether they alter factor-base deduplication or relation rank.

77. Exceptional-point map handling — Enumerate kernel, infinity, and exceptional denominator cases and test branch coverage and correctness; quantify their contribution to any observed failure or speed.

78. Exact same-log transport — On small and medium groups with known logs, transport (P,Q) and assert the recovered scalar is unchanged modulo n; include negative and boundary test vectors.

79. End-to-end transfer-cost break-even — Compare solve-on-source, transfer-then-solve, and solve-on-destination strategies with all maps and setup charged; report the target-count threshold for each.

80. Map-induced implementation leakage audit — Test whether map branches and exceptional handling leak subgroup-dependent timing; classify findings as implementation leakage, not mathematical DLP advantage.

## V. Factor-base geometry and relation quality on isogenous curves

81. Relation-support entropy — Beyond mean decomposition yield, compare entropy of factor-base supports across same-crater curves at fixed support size; test whether higher entropy predicts independent relation growth.

82. Support co-occurrence spectrum — Build pairwise and higher-order co-occurrence matrices for accepted relations on matched isogenous instances; test spectral features against held-out rank increase.

83. Duplicate-relation burden — Measure the fraction of collected relations that are duplicates or scalar-equivalent on source and destination curves; test whether a curve-specific factor reduces useful relations per second.

84. Relation rank per CPU-second — Compare rank growth curves rather than total relation count at fixed time, using equal points and equal solver budgets; reject gains that disappear after map cost.

85. Incremental nullity profile — Track nullity after each batch of relations and test whether CM/isogeny descriptors predict the tail to full rank on held-out seeds.

86. Support-size conditioned rank — Stratify relations by support cardinality and compare rank contribution within each stratum; test whether vertex differences persist after this conditioning.

87. Relation overlap under transport — Transport an exact source relation set and measure how many relations remain distinct and independent on the destination; compare with destination-native relations of matched support.

88. Relation sign-orbit quotient — Canonicalize ±P, inverse points, and known automorphism orbits before counting support; test whether unquotiented counts create false crater effects.

89. Factor-base closure under horizontal maps — Map a base through crater edges and measure closure, duplication, and point loss; test whether closure predicts a practical reduction in base-construction work.

90. Base intersection graph — Compare overlaps among bases transported along different crater paths; test whether the graph predicts reuse savings for multi-target attacks.

91. Relation weight-tail test — Compare the upper tail of relation support weights, not just the mean; test whether rare heavy relations dominate matrix fill or elimination cost.

92. Pivotability score — Estimate how often new relations introduce low-degree pivots under fixed elimination ordering; test the score against actual sparse-matrix fill on untouched seeds.

93. Cycle-consistency of transported relations — Transport relations around a crater cycle and compare point sums and coefficient vectors on return; use discrepancies to detect mapping or canonicalization bugs.

94. Relation age and reuse — Measure whether relations collected before a horizontal move remain useful after transport; test the amortized gain in repeated target solves.

95. Adaptive base choice by local order — Compare bases chosen from the actual End(E) order with bases chosen from Frobenius-order surrogates; test relation quality and reject if only computational overhead changes.

96. Basis distribution fairness — Generate native and transported bases from matched pseudorandom seeds and test distributional balance in x-coordinate strata, trace, and point order.

97. First-fall event distribution — On feasible small fields, compare the distribution of decomposition-system first-fall degrees across same-order crater vertices; use exact systems and held-out seeds.

98. Relation-set graph cuts — Partition factor-base variables using support graph cuts and compare resulting matrix fill; test whether cut structure correlates with CM class position after base size is fixed.

99. Relation yield-to-rank conversion — Estimate the fraction of accepted relations contributing new rank and test whether structural features explain conversion rate better than raw decomposition count.

100. IDEA-434 successor audit — Keep its fixed-p,t,N, fixed-base mean-yield question as prior art; test the distinct rank-quality and support-dependence outcomes above, and reject any proposal that merely renames mean yield.

## VI. Polynomial systems, elimination, and solver fingerprints

101. Isogeny-substituted ideal profile — Substitute an explicit rational isogeny map into a small-parameter relation system and compare ideal dimension, degree, and Gröbner degree to the native destination system; hold the point set fixed.

102. Initial-ideal stability test — Compute initial ideals under several fixed monomial orders for matched transported/native systems; test whether CM or crater position predicts leading-monomial counts on held-out instances.

103. Hilbert-series predictor — Estimate Hilbert series on tractable systems generated from same-order curves and test whether early coefficients predict memory or F4 degree on larger held-out systems.

104. Degree-of-regularity calibration — Measure degree of regularity for matched systems and test its correlation with actual solver time after variable count, equations, and field representation are controlled.

105. Elimination-order crossover — Sweep a predeclared small set of elimination orders on each curve and test whether the best order transfers across horizontal isogenies; charge tuning time equally.

106. Variable encoding under isogeny — Encode the same abstract point variables via source and destination x-coordinates; test the effect on equation degree, sparsity, and solving time independently.

107. Resultant versus Gröbner profile — Compare elimination methods on identical relation ideals from two same-crater vertices; test whether map-induced coefficient shape predicts a stable solver crossover.

108. Coefficient support sparsity — Measure nonzero coefficient count and monomial support in coordinate equations after canonical normalization; test whether support predicts solver memory beyond polynomial degree.

109. Field-basis transport control — Express equivalent systems in polynomial, normal, and tower bases; test if apparent curve effects vanish under a basis-matched comparison.

110. Equation-scaling invariance — Randomly rescale equations and variables by valid field units and confirm ideal invariants and solution sets; quantify solver-time variance to avoid overinterpreting presentation noise.

111. Frobenius-coordinate elimination — On extension-field test families, include Frobenius-conjugate variables explicitly and compare elimination profiles with Weil-descent coordinates; test curve-order interactions.

112. First-fall distribution by conductor — Across conductor strata at fixed q,t, record the full first-fall degree distribution rather than the minimum; test predictive power on held-out strata.

113. Saturation cost under exceptional components — Measure the cost of removing components corresponding to infinity, kernel, and repeated-coordinate solutions; test whether isogeny maps change their frequency.

114. Extraneous-root rate after transport — Compare the proportion of algebraic solutions that fail point-sum verification in native and transported encodings; test if the rate is map-specific or intrinsic.

115. Modular regularity stability — Repeat solver measurements over multiple primes with the same small CM/order pattern; test whether low-parameter regularity is stable or a single-characteristic artifact.

116. Solver portfolio selection from CM features — Train a solver selector on discriminant/order features, then hold out entire CM fields and isogeny classes; test net wall-clock savings including prediction and failed runs.

117. Matrix-fill predictor from relation topology — Predict sparse linear algebra fill from relation-support graphs and compare with measured fill across isogenous endpoints; reject if the predictor fails under randomized support controls.

118. Solver restart sensitivity — Repeat the same normalized polynomial system with controlled row/variable permutations and seeds; estimate solver variance before assigning any residual to curve structure.

119. Memory-time Pareto frontier — For each matched system, measure time and peak memory across solver settings; test whether a curve is consistently better on the Pareto frontier rather than at one hand-picked configuration.

120. CryptoPro-B toy-shape transfer — Reproduce the same local CM/isogeny pattern on tractable toy fields and test whether solver-profile features scale with field size; explicitly forbid extrapolating a toy win to a 256-bit break.

## VII. Endomorphism actions and algorithm-specific use

121. Endomorphism eigenspace decomposition — When a certified endomorphism acts on the target subgroup, compute its eigenvalue and test whether splitting relation variables by eigenspace reduces a measured solver system; compare with random endomorphisms of the same degree.

122. Small-norm map versus GLV baseline — Compare any CM-derived scalar decomposition against the best known endomorphism-based scalar multiplication baseline; test whether an alleged cryptanalytic gain remains after ordinary GLV acceleration is accounted for.

123. Endomorphism orbit compression — Canonicalize point orbits under a certified automorphism/endomorphism subgroup and test relation-base reduction against the increase in orbit bookkeeping and collisions.

124. Orbit-stabilizer relation bias — Measure how endomorphism stabilizers alter the number of distinct relation supports; use exact orbit enumeration on toy groups and validate on larger samples.

125. Endomorphism-generated torsion relations — Test whether small-norm endomorphisms yield independent relations among factor-base points beyond those generated by random scalar combinations; verify matrix rank exactly.

126. Polynomial action on x-coordinates — Derive the rational x-map for a certified endomorphism and test whether it preserves a candidate factor-base set or maps it to a cheaper encoding.

127. Endomorphism action commutation audit — Verify that the candidate endomorphism commutes with Frobenius and with each chosen horizontal map on points; reject all downstream results if the action is only a j-level correspondence.

128. CM norm and decomposition length — Test whether short CM norm representations predict shorter decompositions of target points under a fixed basis; compare with random norm forms and fixed group order.

129. Endomorphism eigenvalue leakage control — Determine whether the eigenvalue is already inferable from public curve parameters; test for additional information in any solver shortcut beyond public algebraic structure.

130. Automorphism-aware rho control — Compare generic Pollard rho with orbit-folded rho on curves with extra automorphisms; use the result only as a baseline correction when testing non-rho algebraic methods.

131. Endomorphism precomputation amortization — Measure the number of targets required for a CM endomorphism precomputation to pay off in relation collection; include code and storage cost.

132. Norm-155 CryptoPro-B check — Verify the audit’s minimum positive noninteger CM norm 155 and test whether the corresponding map gives any end-to-end gain over scalar multiplication alone; a norm fact alone is not a break.

133. Endomorphism matrix on subgroup — Compute the action matrix on E[n] for small certified fixtures and test whether its invariant factors predict relation splitting or only point arithmetic behavior.

134. Twist-conjugate endomorphism action — Compare endomorphism action on a curve and its quadratic twist where defined; test whether a transported solver can exploit the conjugation without changing subgroup order.

135. Endomorphism orbit versus x-sign quotient — Compare point orbits under CM actions before and after identifying ±P; quantify the exact reduction in unique factor-base entries.

136. Kernel-eigenspace conditioning — Test if selecting factor-base points by membership in endomorphism kernel images changes relation probability or only biases the sampling distribution.

137. Composition-ring generated action — For two independent endomorphisms, compute the generated action algebra modulo n and test whether its dimension predicts useful orbit compression.

138. Endomorphism arithmetic side-channel split — Benchmark map implementations for secret-independent versus variable-time branches; distinguish implementation leakage from any group-theoretic attack.

139. Certified endomorphism versus heuristic candidate — Run the same pipeline with fully certified and heuristic endomorphism candidates; measure false-positive rate and propagate uncertainty in reported gains.

140. Endomorphism ablation test — Remove one action at a time from an otherwise identical solver pipeline and test its marginal contribution with paired seeds and a predeclared stopping rule.

## VIII. Twists, torsion, subgroup structure, and field extensions

141. Twist-order control within CM class — Verify curve and twist orders for each tested same-crater vertex and test whether any solver comparison accidentally changed the DLP subgroup rather than only the curve model.

142. Rational torsion profile versus factor base — Compare full rational torsion structure across same-order curves and test whether torsion points alter relation rank after their known contributions are factored out.

143. Subgroup embedding transport — For each isogeny degree d, classify how the n-subgroup embeds in source and destination groups; test all gcd(d,n) cases on exhaustive small curves.

144. Embedding-degree minimality gate — Factor n and certify the exact embedding degree before any pairing-attack feature is considered; measure how often incomplete factorization produced false low-degree flags.

145. Extension-field torsion growth — Track E[n] rationality over small extensions for matched curves and test whether field-of-definition degree predicts a practical relation-system simplification.

146. Twist isogeny correspondence — Search for explicit isogenies between twists and test whether they preserve the selected prime-order subgroup; reject comparisons that rely only on matching cardinality.

147. Pairing distortion-map audit — On eligible fixtures, verify whether a distortion map exists and test whether its cost creates any DLP reduction beyond standard embedding-degree attacks.

148. Group invariant factors versus order-only matching — Match curves by N but vary the invariant-factor decomposition where possible; test whether relation/solver differences are actually group-structure effects.

149. Prime subgroup generator conditioning — Sample multiple generators of the same subgroup on one curve and test variance in algebraic decomposition success; establish this noise floor for cross-curve experiments.

150. Small cofactor torsion correction — Repeat factor-base experiments with and without all cofactor torsion components; test whether mixed-group relations cause false rank gains.

151. Trace-zero and anomalous exclusions — Add explicit gates for anomalous, supersingular, and otherwise special trace cases; test whether automated filtering catches them before structural experiments.

152. Extension representation matched control — Represent the same field using distinct irreducible polynomials or towers and compare solver behavior; test whether field encoding dominates any CM signal.

153. Subfield descent falsification — For extension-field candidates, test all proper subfields and known descent maps before attributing a speedup to isogeny structure.

154. Twist-aware x-coordinate collision audit — Measure x-coordinate collisions and sign ambiguity on curve/twist pairs; test whether these alter decomposition counts under a fixed base.

155. Isogeny degree sharing subgroup factor — When an isogeny degree shares a factor with n, construct examples where the map is non-injective on E[n]; verify pipeline refusal and quantify the lost subgroup information.

156. Full group-structure certification — Compute invariant factors for every small fixture and compare with point-count-only metadata; test whether incomplete group data predicts incorrect solver success.

157. Pairing and transfer cost budget — Compare total attack cost with and without permitted pairings and field extensions, including construction and subgroup checks; separate generic isogeny transport from pairings.

158. Curve/twist matched solver pair — Run identical seeds and budgets on E and its twist after matching subgroup order; test model and endomorphism effects with cofactor and generator choice controlled.

159. Rationality of isogeny kernels — Predict and verify kernel field of definition for each candidate edge; test whether extension overhead, not abstract graph structure, dominates usable map cost.

160. Subgroup-verification portability — Transport subgroup membership certificates across an isogeny and test verification cost and soundness independently of the discrete-log solver.

## IX. Curve construction, encodings, and implementation-level structure

161. CM-generated versus random-trace curve control — Match ordinary curves on q,t,N and actual endomorphism order, then test whether CM construction provenance predicts any attack metric after all public invariants are controlled.

162. Seed-to-curve reproducibility fingerprint — Reconstruct published curve-generation seeds where available and test whether seed metadata leaks any additional structure beyond the final public curve parameters.

163. Model normalization crossover — Convert isogenous curves to short Weierstrass, Montgomery, and Edwards forms when valid; compare solver and map costs while verifying the same abstract curve and subgroup.

164. Coordinate formula confounder audit — Reimplement point arithmetic using independent coordinate systems and compare measured solver differences; classify gains due solely to faster group operations.

165. Field-operation microbenchmark bridge — Measure primitive field operations on each curve’s representation and test whether they explain high-level solver timing; avoid mistaking platform code generation for CM structure.

166. Constant-time versus variable-time arithmetic control — Repeat public research benchmarks with constant-time primitives where possible; measure the performance tax and confirm attack conclusions do not depend on unsafe shortcuts.

167. Endianness and encoding invariance — Round-trip points and kernels through independent encodings and test whether serialization artifacts change coordinate distributions or relation counts.

168. Exceptional model parameter audit — Enumerate singular or degenerate coefficient choices encountered during model conversion; require nonsingularity checks and test that excluded models do not bias results.

169. Public parameter feature leakage — Train a predictor using only public coefficients, j, trace, and order; hold out whole isogeny classes and test whether it predicts implementation costs rather than DLP difficulty.

170. Generated curve family clustering — Cluster candidates by construction family and test whether family labels add predictive value after D_K, f, q, t, and model are included.

171. Compiler and hardware replication — Repeat the same matched isogeny experiment across two compilers and hardware types; test whether a reported vertex ranking is stable.

172. Arithmetic operation count versus wall clock — Compare symbolic field-operation counts with wall-clock results across same-crater maps and solvers; identify cache and allocation effects separately.

173. Map cache locality experiment — Reorder batch point maps while holding the mathematical inputs fixed; test whether memory locality explains apparent per-vertex advantages.

174. Kernel storage compression — Compare compressed and expanded kernel representations for repeated map evaluation; measure exact memory/time tradeoffs without changing map arithmetic.

175. Precomputation provenance audit — Hash and independently verify all class polynomials, kernels, maps, and tables used in an experiment; test whether stale or mismatched artifacts can reproduce claimed outcomes.

176. Independent-library cross-check — Recompute CM data and isogeny maps in two unrelated math libraries on a small benchmark set; quantify disagreements and block results until resolved.

177. Model-selection leakage test — Train any feature-to-cost model using grouped splits by discriminant and class, then compare with random splits; test how much naive splitting overstates predictability.

178. Structural fingerprint stability under isomorphism — Recompute the entire feature vector after random admissible model changes; require invariant features to match and label non-invariants explicitly.

179. CryptoPro-B arithmetic implementation separation — Benchmark the audit curve and each certified crater neighbor with one shared arithmetic backend and then with best-per-curve code; report both structural and engineering deltas.

180. Side-channel boundary declaration — For every benchmark, specify whether timing, memory, or cache behavior is attacker-observable; test only the declared threat model and do not conflate it with generic DLP complexity.

## X. Experimental design, falsification, and research automation

181. Pre-registered crater experiment — Freeze target curves, path set, factor bases, algorithms, seeds, timeouts, and metrics before runs; test whether preregistration changes the rate of retained same-class claims.

182. Whole-isogeny-class holdout — Train any structural predictor on some D_K classes and evaluate on unseen classes; compare with naive curve-level random splits to expose class leakage.

183. Frobenius-orbit holdout — Keep complete Frobenius orbits out of training and test sets; measure whether prediction survives after removing near-duplicate vertices.

184. Repeated-target paired design — For each source/destination pair, transport the same targets and use paired seeds; estimate confidence intervals for relation and solver differences.

185. Budget-equalization audit — Give each curve the same tuning, preprocessing, compute, and memory budgets; test whether adaptive effort alone created a claimed advantage.

186. Rho-normalized threshold — Compare each candidate pipeline against a correctly implemented generic Pollard-rho baseline on the same subgroup and hardware; promote no practical claim without an end-to-end margin.

187. Preprocessing amortization curve — Vary number of targets per curve and calculate the complete break-even curve for CM data, isogeny maps, factor bases, and solver setup.

188. Negative-result retention — Store every failed discriminant, conductor, crater, and solver experiment with configuration and reason; test whether later agents rediscover rejected hypotheses.

189. Novelty-dedup gate — Before assigning a canonical idea ID, search the repository corpus and primary literature for the exact mechanism, observable, and control; test the gate with known duplicates such as IDEA-434.

190. Mathematical-claim verifier — Require symbolic or exact checks for D_pi, D_K, f, class number, edge orientation, and subgroup order; test the checker against intentionally corrupted metadata.

191. Independent red-team audit — Have a second analysis pass challenge each apparent advantage for data leakage, invalid map degree, changed subgroup, uncharged preprocessing, or selection bias; test detection using seeded faults.

192. Compute-budget ladder — Run each idea first on toy curves, then medium curves, and only then on large descriptors; define explicit stop conditions from time and memory before scaling.

193. Parameter-sweep multiplicity correction — Record every tried base, solver order, conductor, and curve; test whether a corrected selection statistic removes apparent best-of-many wins.

194. Falsification-first queue — Order tests by expected ability to disprove the mechanism per compute-hour; compare the final retained fraction with the project’s ordinary queue ordering.

195. Reproducible map/solver artifact — Package exact inputs, certificates, code revision, seeds, runtime, memory, and outputs for a crater comparison; have an independent worker replay it from scratch.

196. Novelty confidence calibration — Label proposals as unverified, literature-screened, or demonstrated-new-within-scope; audit whether the labels track actual duplicate discovery rather than author confidence.

197. Cross-scale feature stability — Measure the same structural descriptor on toy, medium, and cryptographic-size curves; test monotonicity and explicitly reject extrapolation when scale trends reverse.

198. Mechanism-specific stopping rule — For each hypothesis define a measurable falsifier and maximum experiment count before tuning; test whether this prevents indefinite parameter search.

199. Promotion gate for structural claims — Require exact curve classification, paired controls, independent replication, a generic baseline, and an end-to-end cost comparison; test the gate on known negative and positive controls.

200. Autoresearcher idea-family ablation — Disable CM features, crater graph features, map-cost features, or solver features one family at a time; measure whether the discovery engine’s validated hit rate improves beyond an ordinary baseline.

## Primary references and prior-art anchors

- David Jao, Stephen D. Miller, and Ramarathnam Venkatesan, [“Do All Elliptic Curves of the Same Order Have the Same Difficulty of Discrete Log?”](https://arxiv.org/abs/math/0411378). The result is random reducibility under GRH and near-same endomorphism-ring conditions; it is a guardrail against overstating generic difficulty differences.
- Andrew V. Sutherland, [“Isogeny volcanoes”](https://arxiv.org/abs/1208.5370), and Kohel’s volcano work. These give the classical order/conductor structure behind horizontal and vertical edges.
- Igor Semaev, [“New algorithm for the discrete logarithm problem on elliptic curves”](https://arxiv.org/abs/1504.01175). Summation-polynomial decomposition and algebraic solving are established methods; this catalog proposes tests of specific structural effects, not novelty of the method itself.
- Project prior: ECDLP-IDEA-434, the existing fixed-p,t,N, fixed-base mean Semaev-yield study over an isogeny class. Search the complete active, deferred, and rejected corpora before creating any canonical follow-on.

