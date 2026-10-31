# Novelty gate N1-N4: AC-Q, Latin-square Cauchy-Schwarz bound for bucket-resolved sum-compatible filters

Gate run in the final lead-discovery round. Read-only on all repositories. Everything written by this gate lives under
`/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`.

## 0. Verdict first

**advances_lead**, lead = `LEAD-EXO-four-list-ktree-join` (disposition `open_next_step`).

- Same mechanism as the lead (Wagner k-tree / four-list joins with cheap sum-compatible filters, bucket-resolved), and it
  is not a new route. AC-Q is a proof-plus-meter that would discharge the lead's own next step for one filter class.
- What is new relative to every record read here: (i) a rigorous per-bucket inequality for EVERY Latin square,
  pi_c <= alpha_c + sqrt(alpha_c) Gamma / Pr_c; (ii) the spectral statistic Gamma (max over xi != 0 of the l2 mass of the
  bucket Fourier coefficients), which replaces the relative bucket variance W as the quantity to measure; (iii) a
  quantitative "robust Theorem C" corollary. None of (i)-(iii) appears in the lead, KN-FIND-ffe1df, any document of the O2
  analysis directory (all of them were grepped, section 1b), H-ECDLP-2ade73 or IDEA-20260904-f7d47d (see sections 1-4).
  The nearest internal precursor is Theorem B of `O2_fourier_obstruction.md`, which uses the same building block S(xi); Lemma Q
  refines it (section 1b), so the novelty is a refinement of an existing step, not a new technique.
- What it does NOT do (so the verdict is not `new`): it is a closure (a no-go) for a class the lead already marks as closed
  at the bucket-averaged level, it moves no exponent, and it escapes none of the standing obstructions. The candidate's own
  header says tier X, predicted gain 0. Levels >= 2 and arbitrary cheap h stay open (KN-FIND-ffe1df items 6 and 2).
- Overlaps that reduce its marginal value, stated in section 5: the W-measurement hypothesis H-ECDLP-2ade73 asks the same
  discriminating question by measurement; the A/B interval-family Gamma measurement re-measures sums already measured in
  `LEAD-EXO-dl-character-sum-pseudorandom` (exhausted_at_scale); the Weil step is the same Theorem-A-prime-plus-Weil step the
  corpus already uses for the bucket-averaged closure.

## 1. N1 Atlas collision

Environment: `LEAD_ATLAS_CRYPTO`, `LEAD_ATLAS_CRYPTANALYSIS`, `LEAD_ATLAS_ECC_CHALLENGES` exported as instructed; run from
`/Volumes/SSD990-2/crypto-autoresearcher`. Command: `python3 tools/lead_atlas.py --match "<phrase>"`. Raw output, unedited.

### N1 run 1: `Latin square Cauchy-Schwarz per-bucket bound for quasigroup combining of sum-compatible filters`

```
    7  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
    5  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    4  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
    4  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    3  KR-RHO-5b1c0a                                known_result       Representation techniques do not beat rho over F_{p^2}
    3  LEAD-RHO-generic-sqrt-lower-bound            closed_obstructed  Beat the square-root exponent with any generic collision algorithm
    2  KR-RHO-ea34b8                                known_result       Precomputation: l^{1/3} online after l^{2/3} tables, and the lower bound
    2  LEAD-ICB-orbit-linear-algebra                exhausted_at_scale Linear algebra of the orbit-folded relation matrix (equivariant blocks, sparse filters, Wiedemann, CADO-style merge)
```

### N1 run 2: `can any bucket of a cheap filter be predictable from the buckets of two summands`

```
   10  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
    6  LEAD-STR-small-cm-disc-nonunit-endo          closed_obstructed  Small |D_0| or a cheap non-unit endomorphism beyond the automorphism constant
    4  LEAD-ICE-relation-graph-rank-large-prime     open_next_step     Relation-stage rank accounting, large-prime / cycle-basis enrichment and rank-aware collection
    4  LEAD-RHO-grumpy-store-all-schedules          open_next_step     Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks)
    4  LEAD-RHO-lhw-modular-filter-price            open_next_step     Residue-guess price of modular (mod-M) representation filters in prime-order groups
    3  KR-RHO-fbd582                                known_result       Nearly free P−Q alongside P+Q
    3  LEAD-EXO-invertible-hint-subset              open_next_step     The invertible half: dense, cheaply recognizable AND cheaply invertible subsets of E(F_p)
    3  LEAD-ICE-generic-oracle-arity-cost-floor     closed_obstructed  Generic (enumerative / MITM / free) decomposition oracles cannot reach rho at any arity
```

### N1 run 3: `approximately sum-compatible bucket index with quasigroup combining rule bucket-resolved agreement`

```
    9  LEAD-RHO-correlated-walks-shared-sums        closed_obstructed  Correlated walks: one shared index sequence or shared precomputed sums across walks
    6  KR-IC-5931ee                                 known_result       Naive Semaev index calculus over prime fields cannot beat generic methods
    6  KR-IC-a4dd54                                 known_result       Hyperelliptic index calculus and the genus threshold
    5  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
    5  LEAD-ICP-lattice-ic-relation-construction    open_blocked       Lattice index calculus - ideal/quaternion lattices, isogeny-adjoint witnesses and Newton-shift certificates as relation constructors on prime cyclic subgroups
    4  KR-IC-46d822                                 known_result       Gaudry: decomposition over E(F_{q^n}), n fixed
    4  KR-IC-9e610d                                 known_result       Survey consensus (2016)
    4  KR-IC-ae532f                                 known_result       Largest practical algebraic ECDLP computations
```

### N1 run 4: `multiplicative character filter Weil bound twisted character sum Kummer Lang level-1 k-tree join speedup  (my own 4th phrasing)`

```
   12  LEAD-EXO-four-list-ktree-join                open_next_step     Wagner k-tree / four-list joins with cheap sum-compatible filters
    8  LEAD-ICP-algebraic-membership-factor-base    closed_obstructed  Factor bases with low-degree algebraic membership over F_p (subgroup, coset, Dickson, j=0 orbit, images of low-degree maps, character-constant sets)
    7  LEAD-EXO-dl-character-sum-pseudorandom       exhausted_at_scale Additive-character bias of the discrete log on structured factor bases (H-PSEUDO)
    6  KR-IC-5ea2f8                                 known_result       GHS Weil descent and cover attacks
    6  LEAD-EXO-curve-model-representation          closed_obstructed  Alternative curve models and point representations (Edwards, Hessian, Montgomery, Kummer, x-only)
    6  LEAD-ICB-cofactor-torsion-quotients          closed_obstructed  Spending the cofactor and 2-torsion of binary curves: quotient labels, k-tree filters, 2-torsion translation quotients of the factor base
    6  LEAD-ICE-boolean-f4-f5-f6-engines            closed_dominated   Faster Boolean F4 / F5 / F6-IC / inherited-F4 / matrix-F5 engines for the descended Semaev system
    6  LEAD-TRF-ghs-binary-composite                closed_known       GHS / generalized GHS Weil descent (with Galbraith-Hess-Smart isogeny walks) for curves over F_{2^N}, N composite
```

### N1 run 5: `robust quantitative form of exact sum-compatibility homomorphism rigidity Theorem C approximate bucket speedup bound  (my own 5th phrasing)`

```
    6  LEAD-ICP-construction-normal-form            open_unexamined    Normal form and calibrated instruments for proposed prime-field attack systems (dedup, result classes, estimator bias, dynamic range)
    5  KR-RHO-13bf67                                known_result       Generic-group lower bound for discrete logarithms
    4  KR-RHO-46c2c6                                known_result       Multi-target and batch discrete logarithms
    4  KR-RHO-482ed3                                known_result       Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    4  LEAD-RHO-grumpy-store-all-schedules          open_next_step     Exact average-case constant of store-all generic schedules (grumpy giants, compiled tiered walks)
    4  LEAD-RHO-matched-rho-calibration             open_next_step     The matched rho reference itself: finite-size bias and the missing prime medium tier
    3  KR-IC-791cb7                                 known_result       Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    3  KR-IC-b0fcda                                 known_result       Frobenius-invariant factor bases for subfield (Koblitz) curves
```

### N1 reading of the top hits (lead YAMLs opened under `/Volumes/SSD990-2/crypto-autoresearcher/knowledge/leads/ecdlp/`)

Lexical ranking is weak here: run 5 does not list `LEAD-EXO-four-list-ktree-join` in its top 8 although that lead is the
semantic owner of the object. A lexical miss proves nothing, so I judged by mechanism and forecloses text.

| run | hit | disposition | read mechanism / obstruction / forecloses | same mechanism as AC-Q? |
|---|---|---|---|---|
| 1,2,3,4 | `LEAD-EXO-four-list-ktree-join` | open_next_step | mechanism: "Run a Wagner-style k-list tree ... on E(F_p) using a cheap filter h with h(P+Q)=f(h(P),h(Q)) often enough". Next step: "Measure the relative bucket variance W of the O2 agreement kernel ... SMALL-W extends the bucket-averaged O2 barrier (KN-FIND-ffe1df) to a bucket-resolved one and closes the filter class." forecloses includes "sum-compatible hash on E(F_p)" and "four-list join with a cheap filter". best_measured: j=2 four-tree closed for character filters under group-law or quasigroup combining, toy N <= 65539. | YES, same object. AC-Q is a sharper next step on this OPEN lead (see section 0). Not a duplicate: the lead's next step is a measurement of W; AC-Q supplies a theorem-backed bound in a different statistic (Gamma) and a worst-Latin-square meter. |
| 1,4 | `LEAD-ICB-cofactor-torsion-quotients` | closed_obstructed (proof) | obstruction: on ECC2K-130 "exactly sum-compatible filters on E(F_{2^131}) carry 2 bits (the cofactor), so Wagner k-tree has no quotient to work in". revisit_when "a non-homomorphic sum-compatible filter with more than log2(cofactor) bits". | Binary sibling, exact case only. AC-Q is prime-field and approximate. Not a duplicate. AC-Q does not answer the revisit_when clause for binary curves (the Artin-Schreier step is not done). |
| 1 | `LEAD-RHO-generic-sqrt-lower-bound` | closed_obstructed (theorem) | Shoup/Nechaev, "Scope: all generic algorithms, any field, any r". | Not the same mechanism. A coordinate-reading filter is non-generic, so AC-Q lies outside this obstruction's premise; it does not escape it either, because AC-Q proposes no algorithm. |
| 1,5 | `LEAD-RHO-matched-rho-calibration` | open_next_step | finite-size bias of the matched rho reference. | Lexical only (words "bound", "calibration"). |
| 2 | `LEAD-STR-small-cm-disc-nonunit-endo` | closed_obstructed | cheap non-unit endomorphisms, orbit size h = ord_N(lambda). | Lexical only. |
| 2 | `LEAD-ICE-relation-graph-rank-large-prime` | open_next_step | large-prime / cycle-basis relation-stage accounting. | Lexical only. |
| 2,5 | `LEAD-RHO-grumpy-store-all-schedules` | open_next_step | store-all generic schedules. | Lexical only. |
| 2 | `LEAD-RHO-lhw-modular-filter-price` | open_next_step | residue-guess price of mod-M representation filters in the low-Hamming-weight DLP. | Adjacent: a mod-M filter in a prime-order group, but for the LHW-DLP (subset-sum on a Hamming-weight-bounded exponent), a different problem and a different quantity (residue-guess multiplier G_M). Not the same. |
| 2 | `LEAD-EXO-invertible-hint-subset` | open_next_step | dense, cheaply recognizable and invertible subsets of E(F_p). | Adjacent only. Its dichotomy (recognizable vs invertible) shares the intuition that a filter agreeing with the log is a log oracle. Different statistic (agreement of polynomials with log_g). |
| 2 | `LEAD-ICE-generic-oracle-arity-cost-floor` | closed_obstructed | generic decomposition oracles cannot reach rho. | Lexical only. |
| 3 | `LEAD-RHO-correlated-walks-shared-sums` | closed_obstructed (proof) | walks sharing one index sequence. | Lexical only. |
| 3 | `LEAD-ICP-lattice-ic-relation-construction` | open_blocked | lattice relation constructors. | Lexical only. |
| 4 | `LEAD-ICP-algebraic-membership-factor-base` | closed_obstructed (theorem) | bounded-degree algebraic factor base; forecloses "character sums bias decompositions over a coset base". Scope: prime-order E/F_p, any base of size B. | Same SHAPE of result (a scoped negative for bounded-description-complexity objects: bounded degree there, bounded divisor support s here) but a different object (factor-base yield vs k-tree bucket agreement). Not a duplicate; a notation check is in section 4. |
| 4 | `LEAD-EXO-dl-character-sum-pseudorandom` | exhausted_at_scale | measured max_k abs(sum over small-x set of e(k DL/N)) against a matched random null at 2^20-2^26: R flat 1.28-1.34. | PARTIAL OVERLAP in the measurement, not in the question. For an x-interval bucket A_a the coefficient A^_a(xi) is exactly this kind of sum. See section 5. |
| 4 | `LEAD-EXO-curve-model-representation` | closed_obstructed (measured) | alternative curve models and summation polynomial degree. | Lexical only. |
| 5 | `LEAD-ICP-construction-normal-form` | open_unexamined | normal form and calibrated instruments (dedup, estimator bias, dynamic range) for proposed prime-field attack systems; forecloses "instrument must show dynamic range before a null counts". | Lexical only. It is relevant in spirit to the meter (the candidate's positive control sits at 0.385-0.485 of the bound, which is the dynamic-range check) but it is a different object. |
| 1,3,4,5 | KR rows in the lead_atlas output (KR-RHO-13bf67, KR-RHO-5b1c0a, KR-RHO-ea34b8, KR-IC-5931ee, KR-IC-a4dd54, KR-IC-46d822, KR-IC-9e610d, KR-IC-ae532f, KR-IC-5ea2f8, KR-RHO-46c2c6, KR-RHO-482ed3, ...) | known_result | see N2. | none is the same object |

**What AC-Q does that the forecloses phrases do not cover.** The forecloses of `LEAD-EXO-four-list-ktree-join` name the
objects ("sum-compatible hash on E(F_p)", "four-list join with a cheap filter") but no phrase covers a proof of a
per-bucket, all-quasigroup bound or a Gamma-type meter. The lead's only quantitative next step is W. So a record that
proves or measures a bucket-resolved bound is exactly the kind of progress the lead lists as outstanding.

### 1b. Internal-precursor check: the whole O2 analysis directory

Files grepped for `latin`, `sigma_c`, `bijection`, `S(xi)`, `l2`, `3/2`, `level-set`, `Theorem B` (all under
`/Volumes/SSD990-2/crypto-autoresearcher/analysis/o2-sum-compatible-filters/`): `O2_fourier_obstruction.md`,
`O2_derivation_attempt.md`, `O2_composition_closure.md`, `O2_additive_completion.md`, `claim_a_adjudication.md`,
`F1_sum_compatible_filter_search.md`, `reviews/VALIDATION.md`, `reviews/RT-EXP-1-RESULT.md`; the README, `O2_quasigroup_gap.md`,
`O2_quasigroup_scaling.md`, `reviews/REDTEAM.md` (V1) and `knowledge/findings/KN-FIND-ffe1df.md` were read in full or in the relevant parts.
Result: the word "Latin" occurs only for the Jacobson-Matthews / exhaustive sampling of Latin squares (`VALIDATION.md`, `quasigroup_*.py`);
there is no per-bucket Latin-bijection step, no `sigma_c`, and no `M^{3/2}` anywhere.

**Nearest precursor, Theorem B** (`O2_fourier_obstruction.md` section 3, copied): "For every f ... eps_f := Pr[h(x+y) = f(h(x), h(y))]
<= max_c alpha_c + M * delta(h)", with delta(h) the largest nontrivial Fourier coefficient of a level-set indicator. Its proof sums over all
M^2 pairs (a,b), sets s(xi) = sum_a abs(A^_a(xi)), applies Cauchy-Schwarz over the M level sets (s(xi)^2 <= M * sum_a abs(A^_a(xi))^2) and Parseval.
The text says the factor M "is not known to be tight" and `O2_fourier_obstruction.md` section 8 item 1 calls killing it "the single
highest-value open item". `REDTEAM.md` V1 says the per-bucket repair "is Theorem B territory, where the factor M is exactly what is not
known to be removable".

What Lemma Q shares with Theorem B: the quantity S(xi) = sum_a abs(A^_a(xi))^2, Parseval over xi, and Cauchy-Schwarz over level sets.
What Lemma Q adds, which I could not find in any file:
1. **A single target bucket c.** Conditioning on f(h(P),h(Q)) = c restricts the double sum to the M pairs (a, sigma_c(a)), not M^2 pairs.
   That is what removes the s(xi)^2 <= M S(xi) loss: with the bijection, abs(sum_a A^_a A^_sigma(a)) <= S(xi) directly.
2. **The Latin hypothesis is used exactly once**, as the bijectivity of sigma_c. Theorem B needs no hypothesis on f and pays M for it.
3. **A second Cauchy-Schwarz over xi** instead of the max-coefficient bound abs(A^_{f(a,b)}(xi)) <= delta, which yields Gamma.
4. **The statistic Gamma** and its comparison: S(xi) <= M delta^2, so Gamma <= sqrt(M) delta, hence the bucket-averaged corollary
   sqrt(M) Gamma <= M delta. Lemma Q is never worse than Theorem B on the averaged rate, and strictly better whenever Gamma < sqrt(M) delta. With
   the character-level coefficient Lambda (Parseval over the label group) one has Gamma <= Lambda, which is where the saving over the
   red-team M^2 Lambda_W comes from. Against the group-law bound of Theorem A-prime (eps <= 1/M + Lambda, no sqrt(M) loss) Lemma Q
   is weaker for the averaged rate by sqrt(M); its gain is that it is per bucket and holds for every Latin square.

Consequence for the verdict: no document supplies a per-bucket bound with an l2-over-buckets step, so the verdict does not drop to
`duplicate_of_lead`. It stays `advances_lead`, and a reviewer should treat Lemma Q as a refinement of Theorem B's proof, which is a smaller
claim than "new technique".

## 2. N2 Known results

Command: `python3 tools/build_frontier_map.py --match "<phrase>"`. Raw output, unedited.

### N2 run 1: `Latin square Cauchy-Schwarz per-bucket bound for quasigroup combining of sum-compatible filters`

```
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-5b1c0a  score=3  [known_negative/proven]  Representation techniques do not beat rho over F_{p^2}
    sources: KN-LIT-ae78e5
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

### N2 run 2: `can any bucket of a cheap filter be predictable from the buckets of two summands`

```
KR-RHO-fbd582  score=3  [known_mechanism/proven]  Nearly free P−Q alongside P+Q
    sources: KN-LIT-732e36, KN-LIT-a4b3d8
KR-IC-5ea2f8  score=1  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-RHO-13bf67  score=1  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-6654ba  score=1  [known_mechanism/reported]  Point halving as a rho step on binary curves
    sources: KN-LIT-359dcc
KR-RHO-fbd7b1  score=1  [known_bound/proven]  Grumpy giants and better-than-rho generic ordering
    sources: KN-LIT-fbe4e0
```

### N2 run 3: `approximately sum-compatible bucket index with quasigroup combining rule bucket-resolved agreement`

```
KR-IC-5931ee  score=6  [known_negative/proven]  Naive Semaev index calculus over prime fields cannot beat generic methods
    sources: KN-LIT-d8e1b9, KN-LIT-025, KN-LIT-99dfe4, KN-LIT-17ea20, KN-LIT-6966ea
KR-IC-a4dd54  score=6  [known_bound/heuristic]  Hyperelliptic index calculus and the genus threshold
    sources: KN-LIT-92caf4, KN-LIT-fbb9fd, KN-LIT-3bccde
KR-IC-46d822  score=4  [known_bound/heuristic]  Gaudry: decomposition over E(F_{q^n}), n fixed
    sources: KN-LIT-002, KN-LIT-006
KR-IC-9e610d  score=4  [textbook_fact/reported]  Survey consensus (2016)
    sources: KN-LIT-006
KR-IC-ae532f  score=4  [record/reported]  Largest practical algebraic ECDLP computations
    sources: KN-LIT-634555, KN-LIT-54c462, KN-LIT-006
KR-IC-1fcdbc  score=3  [known_negative/measured]  Characteristic-2 summation algorithms stay far slower than rho
    sources: KN-LIT-95d1e4, KN-LIT-19665f
KR-IC-64659b  score=3  [known_bound/proven]  Diem: rigorous subexponential ECDLP for suitable n
    sources: KN-LIT-003, KN-LIT-65f76d
KR-IC-b0fcda  score=3  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
```

### N2 run 4: `multiplicative character filter Weil bound twisted character sum Kummer Lang level-1 k-tree join speedup  (my own 4th phrasing)`

```
KR-IC-5ea2f8  score=6  [known_mechanism/proven]  GHS Weil descent and cover attacks
    sources: KN-LIT-007, KN-LIT-fa389d, KN-LIT-bf1772, KN-LIT-b4a89c, KN-LIT-54c462
KR-IC-fbdb61  score=5  [known_bound/proven]  Last fall degree and solving degree of Weil descent systems
    sources: KN-LIT-7607, KN-LIT-86a887, KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c, KN-LIT-029
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-IC-5a43e5  score=4  [known_mechanism/proven]  Semaev summation polynomials
    sources: KN-LIT-001, KN-LIT-006
KR-IC-73db3f  score=4  [known_mechanism/heuristic]  Choosing the factor-base vector space V (small product spaces)
    sources: KN-LIT-6d3c24, KN-LIT-023, KN-LIT-005, KN-LIT-19665f
KR-IC-791cb7  score=4  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-e2d81b  score=4  [record/reported]  ecGFp5 and degree-5 extension curves: published estimates
    sources: KN-LIT-8aff72, KN-LIT-8146f9, KN-LIT-004, KN-LIT-bf1772
KR-IC-f5c584  score=4  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
```

### N2 run 5: `robust quantitative form of exact sum-compatibility homomorphism rigidity Theorem C approximate bucket speedup bound  (my own 5th phrasing)`

```
KR-RHO-13bf67  score=5  [textbook_fact/proven]  Generic-group lower bound for discrete logarithms
    sources: KN-LIT-011, KN-TECH-005, KN-LIT-006
KR-RHO-46c2c6  score=4  [known_bound/proven]  Multi-target and batch discrete logarithms
    sources: KN-LIT-f47b10, KN-LIT-7e25f1
KR-RHO-482ed3  score=4  [known_mechanism/proven]  Koblitz signed-Frobenius rho: sqrt(m) beyond negation
    sources: KN-LIT-c5d918, KN-LIT-042, KN-LIT-661e97
KR-IC-791cb7  score=3  [known_mechanism/heuristic]  Weak binary fields under GHS and generalized GHS with isogeny walks (Menezes-Teske-Weng, Menezes-Teske), with the exact densities and costs
    sources: KN-LIT-d7995a, KN-LIT-f64d86, KN-LIT-fc822d, KN-LIT-0e854b, KN-LIT-007
KR-IC-b0fcda  score=3  [known_mechanism/heuristic]  Frobenius-invariant factor bases for subfield (Koblitz) curves
    sources: KN-LIT-0d9d28
KR-IC-f5c584  score=3  [known_mechanism/proven]  The trace morphism forces a linear equation (first fall degree 2 for S_3)
    sources: KN-LIT-7604, KN-LIT-440ec2, KN-LIT-7607
KR-RHO-0528e7  score=3  [known_mechanism/proven]  Automorphisms give a sqrt(m) constant factor
    sources: KN-LIT-db2a90, KN-LIT-042, KN-LIT-a5c59c, KN-TECH-018
KR-RHO-6239aa  score=3  [known_mechanism/proven]  Parallel collision search with distinguished points
    sources: KN-LIT-73f7e1, KN-LIT-012, KN-TECH-006
```

### N2 reading

No hit is a KR row on Wagner k-tree, sum-compatible filters, quasigroup combining or character-sum bounds for point filters.
`KRMAP.md` contains no occurrence of wagner, k-tree, sum-compat, quasigroup, latin, kohel, shparlinski, bilinear, character sum
or "weil bound" (grep run on `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/atlas/KRMAP.md`).
The closest rows, read in full from `knowledge/frontiers/ecdlp/`:

- `KR-RHO-13bf67` (textbook_fact, proven), generic-group lower bound Omega(sqrt p). Context only: AC-Q concerns non-generic filters.
- `KR-RHO-5b1c0a` (known_negative, proven), Delaplace-May representation technique over F_{p^2} costs p^{1.314}. Adjacent
  (subset-sum structure for ECDLP) but it is about F_{p^2} and the lists, not about a prime-field filter bound.
- `KR-RHO-ea34b8` (known_bound), preprocessing S T^2 bound. Not the same object.
- `KR-IC-5931ee`, `KR-IC-a4dd54`, `KR-IC-5ea2f8`, `KR-RHO-fbd582`, ... : lexical noise (index calculus, hyperelliptic, GHS, P-Q).

Verdict from N2: no KR hit, so `known_result` is not triggered. What is classical and is NOT claimed as new here:
(a) the Parseval plus Cauchy-Schwarz handling of a convolution trilinear form on Z/N (the standard "Fourier control of 3-term
counts" step, recalled, not retrieved), and (b) the Weil-type bound for twisted character sums on E, which the corpus already
uses (KN-LIT-7639, partly traced). The composition of (a) with a Latin-square row bijection and the bucket-resolved reading is
internal.

## 3. N3 Ledger

Greps ran over `/Volumes/SSD990-2/crypto-autoresearcher/ledger/.index/{proposals,hypotheses}.jsonl` with
`acq_ledger.py` (all terms must occur, case-insensitive; the script and its raw outputs are in the scout directory).
Output format: `id|status|title[:70]|claim[:100]`.

### N3 raw greps, batch 1

```
QUERY (AND): ['quasigroup']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['latin square']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['sum-compatible']
IDEA-20260926-136bd3|proposed|THE k-TREE ROUTE ON ECC2K-130 IS A FILTER-CAPACITY QUESTION: exact sum|SEAM. The brief asks what replaces the additive low-bits coordinate that Wagner's k-tree needs and t
# proposals.jsonl count 1
H-BINSTD-0126fe|specified|On the composite ambient group of ECC2K-130 every exactly sum-compatib|Let E be a binary Koblitz curve and G a finite abelian group written additively. Call h from G onto 
H-BINSTD-17cf9d|specified|On the composite ambient group of ECC2K-130 every exactly sum-compatib|Let E be a binary Koblitz curve and G a finite abelian group written additively. Call h from G onto 
H-BINSTD-9b29a0|review_required|On the composite ambient group of ECC2K-130 every exactly sum-compatib|Let E be a binary Koblitz curve and G a finite abelian group written additively. Call h from G onto 
H-BINSTD-de2808|specified|On the composite ambient group of ECC2K-130 every exactly sum-compatib|Let E be a binary Koblitz curve and G a finite abelian group written additively. Call h from G onto 
# hypotheses.jsonl count 4
QUERY (AND): ['bucket', 'filter']
IDEA-20260904-f7d47d|unverified|THE O2 LINE'S LOAD-BEARING HOLE IS A SECOND MOMENT NOBODY HAS MEASURED|(A) THE EXACT CLAIM. Let E/F_p have #E(F_p) = N prime, let h : E(F_p) -> [M] be a cheaply computable
# proposals.jsonl count 1
H-ECDLP-2ade73|specified|Relative bucket variance W of the O2 agreement kernel decays slower th|Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
# hypotheses.jsonl count 1
QUERY (AND): ['cauchy', 'bucket']
# proposals.jsonl count 0
H-ECDLP-2ade73|specified|Relative bucket variance W of the O2 agreement kernel decays slower th|Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
# hypotheses.jsonl count 1
QUERY (AND): ['k-tree']
IDEA-20260808-e40da2|proposed|A closed-form, zero-compute location of the 1-bit-leakage boundary for|SCOPE. The BIAS-DETECTION CLASS of nonce-leakage attacks, defined formally below; group order N bits
IDEA-20260817-1e0111|proposed|Wagner's k-tree needs no algebraic structure at all, so KN-FIND-5c1a03|(A) THE COUNTEREXAMPLE TO UNIVERSALITY, WHICH IS THE RECORD'S MAIN CONTRIBUTION AND IS UNAFFECTED BY
IDEA-20260904-f7d47d|unverified|THE O2 LINE'S LOAD-BEARING HOLE IS A SECOND MOMENT NOBODY HAS MEASURED|(A) THE EXACT CLAIM. Let E/F_p have #E(F_p) = N prime, let h : E(F_p) -> [M] be a cheaply computable
IDEA-20260920-a5757d|proposed|THE BRANCHING WINDOW b < sqrt(M): the note's Route-3 ceiling is FALSE |(A) THE REBUTTAL. docs/n13-ecdlp-hint-family.md section 8 Route 3 argues: "Wagner's k-tree attains 2
IDEA-20260926-136bd3|proposed|THE k-TREE ROUTE ON ECC2K-130 IS A FILTER-CAPACITY QUESTION: exact sum|SEAM. The brief asks what replaces the additive low-bits coordinate that Wagner's k-tree needs and t
# proposals.jsonl count 5
H-ECDSA-9946a0|specified|Stage 0 1-bit k-cap identities — 160/5=32 >= 16 and 160/6 < 32 — befor|Fix the exact k-cap arithmetic of IDEA-20260808-e40da2 before any merge tree, any Fourier coefficien
# hypotheses.jsonl count 1
QUERY (AND): ['wagner', 'filter']
IDEA-20260823-835868|proposed|Joinable partial-verifier certificate for source-labelled four-list EC|The decision-relevant gate for a Wagner-style prime-order ECDLP route is not a scalar pruning ratio.
IDEA-20260904-f7d47d|unverified|THE O2 LINE'S LOAD-BEARING HOLE IS A SECOND MOMENT NOBODY HAS MEASURED|(A) THE EXACT CLAIM. Let E/F_p have #E(F_p) = N prime, let h : E(F_p) -> [M] be a cheaply computable
IDEA-20260926-136bd3|proposed|THE k-TREE ROUTE ON ECC2K-130 IS A FILTER-CAPACITY QUESTION: exact sum|SEAM. The brief asks what replaces the additive low-bits coordinate that Wagner's k-tree needs and t
# proposals.jsonl count 3
H-JPR-3a00f0|proposed|Source-resolved output-sensitive joinability is the missing Wagner-to-|Let G be a prime-order elliptic-curve subgroup of order N and let four independently sampled, source
# hypotheses.jsonl count 1
QUERY (AND): ['o2', 'agreement']
IDEA-20260904-f7d47d|unverified|THE O2 LINE'S LOAD-BEARING HOLE IS A SECOND MOMENT NOBODY HAS MEASURED|(A) THE EXACT CLAIM. Let E/F_p have #E(F_p) = N prime, let h : E(F_p) -> [M] be a cheaply computable
# proposals.jsonl count 1
H-ECDLP-2ade73|specified|Relative bucket variance W of the O2 agreement kernel decays slower th|Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
# hypotheses.jsonl count 1
```

### N3 raw greps, batch 2

```
QUERY (AND): ['theorem c']
IDEA-20260727-008|adaptation|Endomorphism-rank cost curve - the cheapest decisive test that adding |This record isolates part C1 of IDEA-20260727-005 as a standalone, cheap, pre-registered measurement
IDEA-20260808-481e07|proposed|PAUSE-FLAGGED - complete splitting on the factor-base locus means the |REQUIRES THE GOAL-MONO-001 PAUSE TO CLEAR BEFORE DISPATCH; filed now because the content is a correc
IDEA-20260816-98ab8e|proposed|Reproduce the bounded-degree factor-base obstruction as a measured cur|(A) THE AUDIT THIS SKIPS OTHERWISE. The inventor protocol's proof-architecture section requires base
IDEA-20260829-390ccc|proposed|Join-key rigidity from Cauchy-Davenport and Vosper: any O(L)-time conc|CONDITIONAL THEOREM CANDIDATE, stated for falsification. Let G = <P> have prime order N, let D subse
IDEA-20260904-cb1199|proposed|THE RQ'S DECISION TARGET IS A FALSE DISJUNCTION AND ONE EXTERNAL 2025 |(A) THE EXTERNAL INGREDIENT, RETRIEVED THIS SESSION AT ABSTRACT LEVEL. S. D. Galbraith, "Climbing an
IDEA-20260926-136bd3|proposed|THE k-TREE ROUTE ON ECC2K-130 IS A FILTER-CAPACITY QUESTION: exact sum|SEAM. The brief asks what replaces the additive low-bits coordinate that Wagner's k-tree needs and t
# proposals.jsonl count 6
H-CZLIFT-9a32e9|weakened|Small rational points on E/Q (and on E(K) for a quadratic K) grow like|For E/Q of rank r the number N_E(H) of rational points of naive height H(x) <= H grows like c_E (log
# hypotheses.jsonl count 1
QUERY (AND): ['bucket variance']
# proposals.jsonl count 0
H-ECDLP-2ade73|specified|Relative bucket variance W of the O2 agreement kernel decays slower th|Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
# hypotheses.jsonl count 1
QUERY (AND): ['bucket-resolved']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['kohel']
IDEA-20260807-15f103|known_in_substance|CLOSURE with named obstruction: smooth-conductor descent within an iso|Within an ordinary isogeny class (fixed trace t, fixed group order N), the CM conductor f varies fro
IDEA-ISO-7f3e2d|known_in_substance|CLOSURE with named obstruction: smooth-conductor descent within an iso|Within an ordinary isogeny class (fixed trace t, fixed group order N), the CM conductor f varies fro
# proposals.jsonl count 2
# hypotheses.jsonl count 0
QUERY (AND): ['weil', 'filter', 'bucket']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['weil', 'character', 'wagner']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['max_c']
# proposals.jsonl count 0
H-ECDLP-2ade73|specified|Relative bucket variance W of the O2 agreement kernel decays slower th|Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
H-ICINV-6c7920|rejected_scoped||SCOPE: toy ordinary prime-field short-Weierstrass curves at p in {2003, 4001, 6007}, complete F_p-is
# hypotheses.jsonl count 2
QUERY (AND): ['best bucket']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['quotient homomorphism']
IDEA-20261018-9fc21f|proposed|The block-system dichotomy: trace-parity confinement is kappa = d(V) a|BRIDGE of H-SEMBIN-83a856 (supported), IDEA-20261017-3db2a8, EXP-PFDR-ca5e01, EV-RELN-335cd2, IDEA-2
# proposals.jsonl count 1
H-BINSTD-7c3629|approved|At odd n, within the Newton bound, the half {c_0 = Tr(a)} of Semaev's |CLAIM (mechanism measurement; U-LABEL; NO ATTACK). Setting: binary curves E: y^2 + xy = x^3 + a x^2 
# hypotheses.jsonl count 1
QUERY (AND): ['approximate', 'combining']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['lang torsor']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['cauchy-schwarz', 'filter']
# proposals.jsonl count 0
H-ECDLP-2ade73|specified|Relative bucket variance W of the O2 agreement kernel decays slower th|Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
# hypotheses.jsonl count 1
QUERY (AND): ['fourier', 'filter', 'sum-compat']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['o2', 'sum']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
```

### N3 raw greps, batch 3

```
QUERY (AND): ['robust', 'theorem c']
# proposals.jsonl count 0
# hypotheses.jsonl count 0
QUERY (AND): ['bucket', 'max_c', 'pi_c']
# proposals.jsonl count 0
H-ECDLP-2ade73|specified|Relative bucket variance W of the O2 agreement kernel decays slower th|Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P
# hypotheses.jsonl count 1
QUERY (AND): ['second moment', 'bucket']
IDEA-20260904-f7d47d|unverified|THE O2 LINE'S LOAD-BEARING HOLE IS A SECOND MOMENT NOBODY HAS MEASURED|(A) THE EXACT CLAIM. Let E/F_p have #E(F_p) = N prime, let h : E(F_p) -> [M] be a cheaply computable
# proposals.jsonl count 1
# hypotheses.jsonl count 0
QUERY (AND): ['vosper']
IDEA-20260829-390ccc|proposed|Join-key rigidity from Cauchy-Davenport and Vosper: any O(L)-time conc|CONDITIONAL THEOREM CANDIDATE, stated for falsification. Let G = <P> have prime order N, let D subse
# proposals.jsonl count 1
# hypotheses.jsonl count 0
QUERY (AND): ['cauchy-davenport', 'propagation']
IDEA-20260815-f558e4|proposed|THE PROPAGATION CEILING, AND WHY THE EXTREMAL OBJECT IS THE ONE YOU CA|(A) THE GAP THIS FILLS, STATED IN THE OWNING RECORD'S OWN WORDS. IDEA-20260807-df906f proved that on
# proposals.jsonl count 1
# hypotheses.jsonl count 0
```

### N3 hits that may be the same object

Zero hits for "quasigroup", "latin square", "bucket-resolved", "lang torsor", "robust ... theorem c", "approximate ... combining",
"best bucket" in proposals and hypotheses. So the Latin-square / quasigroup framing and the robust-Theorem-C target exist only in
`knowledge/findings/KN-FIND-ffe1df.md` and `analysis/o2-sum-compatible-filters/`, not as ledger proposals.

| id | status | claim (first 100 chars) | relation to AC-Q |
|---|---|---|---|
| `H-ECDLP-2ade73` | specified | Let E/F_p have prime order N, let h : E(F_p) -> [M] be a cheap filter, and for uniform independent P ... | OPENED. Measures W = sum_c q_c (pi_c/delta - 1)^2 and fits the exponent a. Its proof obligation `max_c pi_c/delta <= 1 + sqrt(W / min_c q_c)` is the same question AC-Q answers by theorem for the character class. Only Stage 0 (one frozen fixture) is authorized; Stages 1-2 are not. Same discriminating question, different statistic and method. |
| `IDEA-20260904-f7d47d` | unverified | THE O2 LINE'S LOAD-BEARING HOLE IS A SECOND MOMENT NOBODY HAS MEASURED ... | OPENED. Proposes to bound max_c pi_c by a second moment and to do "the sum over c INSIDE the character expansion, where orthogonality in the bucket variable collapses the frequency count". AC-Q's Lemma Q is a concrete realization of that mechanism with the extra input that the Latin row bijection gives |sum_a A^_a A^_sigma(a)| <= S(xi). The idea leaves the surviving frequency count (the exponent a) as an open measured quantity. Lemma Q supplies M^{3/2} Gamma. So AC-Q advances this idea; it is not the same record, because the idea has no Latin-square step and no Gamma. |
| `IDEA-20260920-a5757d` | proposed | THE BRANCHING WINDOW b < sqrt(M): the note's Route-3 ceiling is FALSE as stated ... | OPENED. Branching class in the SET-VALUED, deterministic-support sense (sumset A_i + A_j meets at most b fibres), with a Freiman closure at constant b. AC-Q's branching is probabilistic (a rate pi_c). Adjacent, same class label in IDEA-20260806-c5d183, different quantity. Complementary rather than duplicate. |
| `IDEA-20260829-390ccc` | proposed | Join-key rigidity from Cauchy-Davenport and Vosper: any O(L)-time concentrating four-list join key ... has AP fibers | NOT opened (limit of 3). Index text only. Same family of conclusion (a concentrating key carries dlog structure) from an EXACT-soundness hypothesis. AC-Q's corollary (agreement >= 1/2 forces Gamma >= about 1/(2 sqrt M)) is the robust Fourier analogue. Nearest semantic neighbour after the three opened. A reviewer should check that the corollary adds anything beyond it. |
| `IDEA-20260815-f558e4`, `IDEA-20260807-df906f` (index only) | proposed | propagation ceiling / Cauchy-Davenport ceiling: strict propagation rate of every balanced lossy partition is zero | Exact (strict) propagation. AC-Q is the approximate regime. Not the same. |
| `IDEA-20260817-1e0111` | proposed | Wagner's k-tree needs no algebraic structure at all ... counterexample to universality | Index text only. Its object is the k-tree arithmetic on Z/N with low-bit projections (branching 2). Different filter, adjacent lane. |
| `IDEA-20260926-136bd3`, `H-BINSTD-0126fe/-17cf9d/-9b29a0/-de2808` | proposed / specified | k-tree route on ECC2K-130 as a filter-capacity question; exactly sum-compatible filters on the composite ambient group | Binary exact case only. AC-Q is prime-field. |
| `IDEA-20260823-835868`, `H-JPR-3a00f0` | proposed | joinable partial-verifier certificate for source-labelled four-list ECDLP | Output-sensitive joinability. A different gate on the same lane (can survivors be found without L^2 work). AC-Q bounds the filtering gain, not joinability. |
| `H-ECDLP-07c7c6`, `H-ECDLP-af453b` | specified / proposed | digit-vector / digit-sign of the canonical p-adic lift followed through the group law in the probabilistic regime | The "branching in the probabilistic regime" instance for p-adic digits. Same class label; different filter family. |

Records opened in full: `H-ECDLP-2ade73`, `IDEA-20260904-f7d47d`, `IDEA-20260920-a5757d` (three, as allowed). Decision: none is the same
object as AC-Q. The two nearest (`H-ECDLP-2ade73`, `IDEA-20260904-f7d47d`) are the lead's own next-step records, which is
consistent with the N1 verdict `advances_lead`.

## 4. N4 Notation change

**Pair.** (representation, operation set) = (R1: the affine x(P) in F_p read through a multiplicative-character label
h(P) = ind_psi(F(P)) mod M, product filters for M = k^r; Sigma: the group law on pairs of inputs together with a quasigroup f on
the label alphabet, a Wagner merge having to invert f in each argument). Trichotomy class per IDEA-20260806-c5d183:
branching. The candidate declares this.

**Is it a recorded rigidity result in new notation?** Checked against each record named in the task.

| record | what it fixes | relation |
|---|---|---|
| IDEA-20260806-c5d183 | deterministic propagation under the full translation action on prime order is constant or injective; the branching class is where the rest lives | Not restated. Lemma Q is a statement INSIDE the branching class: it prices the rate. c5d183 does not bound the branching rate. |
| KN-FIND-ffe1df Theorem C | exact sum-compatibility with a quasigroup f forces a homomorphism, impossible for N prime | Lemma Q contains Theorem C as its limiting case only in the weak sense that pi_c = 1 for all c would force Gamma large. In that limit Theorem C is the stronger statement (it needs no character-sum input), so Lemma Q adds nothing there. The content is the approximate regime 0 < pi_c - alpha_c < 1, which Theorem C does not address and KN-FIND lists as "no robust Theorem C is proved". So it is the robust form the corpus asks for, not a re-notation. |
| IDEA-20260901-863e36 | propagation is a property of a projection paired with an operation set; exact propagation = block systems of <Sigma> | Not restated. Sigma here is not a group acting with block systems; the label operation is a quasigroup and the agreement is approximate. |
| KN-OPEN-020 | bounded-degree algebraic factor bases are scoped out; the open class is high-degree, implicit, or target-dependent | No factor base appears, so KN-OPEN-020 does not apply. But NOTE the analogy: the Lemma Q plus Weil closure holds for bounded divisor support s, the exact analogue of "bounded description complexity". It therefore proves another scoped negative of the same shape. It says nothing about high-degree, implicit or target-dependent filters, which is where the lead's open item (arbitrary cheap h, KN-FIND Proposition 2) lives. |
| IDEA-20260807-df906f, IDEA-20260815-f558e4 | strict propagation rate of balanced lossy partitions is zero (Cauchy-Davenport) | Strict, not approximate. Not restated. |

**Standing obstructions quoted from the lead rows (Scope clauses included).**

- SO-GEN, `LEAD-RHO-generic-sqrt-lower-bound` (closed_obstructed, theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r." AC-Q: its premise "generic algorithm" does not cover a coordinate-reading filter, but AC-Q proposes no algorithm, so it escapes nothing and gives a barrier for a non-generic class.
- SO-TORS, `LEAD-STR-torsion-module-leak` (closed_obstructed, proof): "Any statistic of the curve alone is k-independent by construction. Any homomorphic invariant from the prime-order group G to an l-primary group (l != N) is trivial (coprimality, IDEA-20260807-6eab6a). A non-homomorphic point statistic is a function of the encoding of Q. Using it is index calculus or a generic query, and partial information about k on the point costs more than it saves, by sqrt(M) (IDEA-20260811-8cf53a). Toy checks agree: the psi_5 factor-degree multiset does not change with k (H-TORS-3bed8a). Scope: prime-order G, any l != N." AC-Q: not escaped. It is a statement about non-homomorphic point statistics (cheap labels of x), so it lies inside SO-TORS's non-homomorphic clause, and Lemma Q quantifies the filter case. The "by sqrt(M)" of IDEA-20260811-8cf53a is an information-side dichotomy (exponent-side vs point-side information), a different derivation from the Cauchy-Schwarz sqrt(M) saving in Lemma Q; the coincidence of the factor name is not an equivalence and a reviewer should check there is no hidden overlap (index text only, record not opened).

**Result of N4.** Not a recorded rigidity result in new notation. It is the quantitative, bucket-resolved repair that
`KN-FIND-ffe1df` ("What is NOT established" item 1 and the RT-20260803-be45a8 bucket hole), `O2_quasigroup_gap.md` section 6.2
("a robust Theorem C ... the sharpest remaining mathematical target") and `REDTEAM.md` V1 option (b) ("a direct bound on the
single-bucket rate that beats 1 + M^2 Lambda_W") each ask for. Remaining caveat: for the multiplicative-character class the Weil
step is the same step already used by the bucket-averaged closure (Theorem A-prime plus Weil), so the new mathematics is the
Latin-square / l2 step, not the Weil step.

## 5. Overlaps and weaknesses a reviewer must weigh (not hidden)

1. **Level 1 only.** Both KN-FIND-ffe1df item 6 and the candidate's H-Q2 say the bootstrap to levels >= 2 is unproved. The
   lead cannot be closed by AC-Q.
2. **Closure, not escape.** None of SO-GEN, SO-TORS, SO-WALK etc. is escaped (the candidate says so). The result is not a B1-B7
   bottleneck and moves no exponent (A1 of `docs/target-result-profile.md`: closures are not target-class results).
3. **Marginal value against H-ECDLP-2ade73.** If the Lemma Q proof survives review, the W measurement is retired for the
   character class; if it fails, W stays as the next step. Either way the gate for the lead is the same review.
4. **Interval/window families overlap an exhausted measurement.** For x-interval buckets, A^_a(xi) is an additive-character-of-dlog
   sum over a small-x-type set, the statistic of `LEAD-EXO-dl-character-sum-pseudorandom` (EV-ECDLP-f83a17, 2^20-2^26, R flat
   1.28-1.34). The candidate's A/B runs at p = 2^12..2^20 would repeat that sum at smaller size, aggregated in l2 over
   buckets. The new information is the other families (I popcount / digit sums, J y-sign, y-based, nonlinear).
   `reviews/RT-EXP-1-RESULT.md` is a second overlap: it already measured G = M_eff * max_{c,d} pi_c(d) at M = round(N^{1/3}) on 8 primes
   (p = 523..65539), 3 curves per prime, exactly and whole-group, for x mod M, floor(Mx/p), popcount, digitsum, x([2]P) and a target-dependent
   h_Q, with SHA and matched-marginal shuffle nulls and a planted theta = p^{-1/9} positive control. Step (2) of the candidate's first
   step therefore adds only: (a) the worst case over all Latin squares (Dinkelbach ratio-optimal sigma), (b) the growth exponent of Gamma sqrt(N) in p
   with a CI, and (c) the y-based and nonlinear families (x+-y, xy, x^{-1}, y-sign), which RT-EXP-1 did not list.
5. **The Weil ingredient is not retrieved in the form used.** See section 6.
7. **Not like-for-like with the red-team column.** The candidate's table column "red-team 1 + M^2 Lambda" evaluates the dlog-Fourier
   Lambda, whereas the red team's Lambda_W is a coefficient of the trilinear form (T-hat_{t,t,u}). Both sit at the Weil scale but they are
   different statistics, so 47.3 against 3.67 should not be read as a measured ratio of two bounds on one quantity.
8. **Definition of speedup.** Lemma Q bounds pi_c / alpha_c (excess over the marginal bucket frequency). RT-EXP-1 reports G = M * max pi_c
   (excess over 1/M). The two agree up to the balance factor kappa for kappa-balanced filters, and balance is automatic in the
   non-degenerate character class. For unbalanced filters (popcount, digit sums) they differ, and that gap is precisely the free
   marginal-bias floor that made popcount and digitsum trip RT-EXP-1's criterion as false positives. A reviewer must check which of
   the two quantities a Wagner level is actually charged for outside the character class.
6. **Nearest unreviewed neighbour:** `IDEA-20260829-390ccc` (Cauchy-Davenport / Vosper join-key rigidity) was not opened (limit of 3).

## 6. Citations and provenance

| item | provenance | notes |
|---|---|---|
| Ahmadi-Shparlinski, "Exponential sums over points of elliptic curves", arXiv 1302.4210, Lemma 1: for an ordinary curve over F_q and a point G of order T, any group character chi on E(F_q), sum over n in Z_T of psi(x(nG)) chi(G) is << q^{1/2}; the paper introduces it as "a special case of the bound of [17, Corollary 1]" | **retrieved** (this session: WebFetch of `https://arxiv.org/pdf/1302.4210`, text extracted with pdftotext; bibliography entry [17] reads Kohel and Shparlinski, ANTS IV, LNCS 1838 (2000), 395-404) | Confirms the additive, x-only case with an unspecified implied constant. The printed chi(G) is presumably chi(nG) (typo in the arXiv text; not verified). The hypothesis "ordinary" holds automatically for the lead's curves: for p > 3 a supersingular E/F_p has #E = p+1, which is even, so it is never of prime order N (standard fact, recalled). |
| Kohel-Shparlinski, ANTS IV, LNCS 1838, 395-404 (2000), Cor. 1 | **recalled** (existence and venue confirmed by a web search result and by the bibliography above) | The primary text was not retrieved: the fetch of `https://www.i2m.univ-amu.fr/perso/david.kohel/pub/character.pdf` failed with ECONNREFUSED. |
| Multiplicative form with conductor s: abs(E_P psi(F(P)) chi(P)) <= (s sqrt(p) + s + 1)/N via Kummer sheaf tensored with the Lang torsor of chi | **recalled / derived by the dossier author**, not retrieved | A web search for a published statement of exactly this mixed sum on E(F_q) found nothing matching (it found Weil-type bounds for rational functions in several variables and a 2025 paper on multiplicative character sums of division polynomials, neither with a group-character twist). The corpus's `KN-LIT-7639` verifies the form of the small-genus multiplicative bound, not the explicit constant and not general k > 2 on a genus-1 curve. |
| Lemma Q (Parseval, Cauchy-Schwarz over a using the bijection sigma_c, Cauchy-Schwarz over xi) | **recalled / derived**; standard Fourier technique, instance new | I re-derived the five steps by hand and they hold: the xi = 0 term is alpha_c Pr_c; |sum_a A^_a A^_sigma(a)| <= S(xi); error <= sqrt(alpha_c) Gamma by Parseval; divide by Pr_c. |

**My own check (produced in this gate, scope stated).** `acq_check/lemmaq_sanity.py` (scout directory) tests only the INEQUALITY
pi_c <= alpha_c + sqrt(alpha_c) Gamma/Pr_c on abstract filters h : Z/N -> [M] (random, biased, interval and mod-M of the dlog
coordinate; N in {101, 211, 307}; M in {3, 5, 8, 13}), with the joint count taken by brute force over all N^2 pairs and a random bijection
sigma and bucket c per trial. Result: 1800 trials, 0 violations; the largest (pi_c - alpha_c)/(bound - alpha_c) seen was 0.371.
This says nothing about the Weil step, about elliptic-curve filters, or about the candidate's 96-cell table, which I did not re-run.

## 7. Conditional claims and numbered heuristics (carried, not upgraded)

- C1 (conditional on review of Lemma Q and on the multiplicative Kummer-Lang constant): for non-degenerate multiplicative-character
  filters of bounded divisor support s, the level-1 per-bucket speedup is <= 1 + kappa^{3/2} s (1 + o(1)) at M = p^{1/3} and 1 + o(1)
  for M <= p^{1/3 - eps}, for every quasigroup. This is the candidate's claim; I did not verify the Weil step.
- H-Q1 (candidate): for the non-character families Gamma sqrt(N) = O(log p). A prediction, based on measured 1.28-2.2 values for xmod and sha.
- H-Q2 (candidate): level-1 speedup p^{o(1)} implies whole-tree speedup p^{o(1)}. Unproved bootstrap lemma.

## 8. Files

- This gate: `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/gate-additive-combinatorics-s-AC-Q-Latin-square-Cauchy-Schwarz-bound-f.md`
- Raw outputs: `acq_n1_run1.txt`..`acq_n1_run5.txt`, `acq_n2_run1.txt`..`acq_n2_run5.txt`, `acq_n3_run1.txt`..`acq_n3_run3.txt`, helper `acq_ledger.py`, check `acq_check/lemmaq_sanity.py`.
