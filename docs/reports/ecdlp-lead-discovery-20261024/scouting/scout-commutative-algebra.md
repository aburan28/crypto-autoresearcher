# Scout dossier: commutative algebra (final lead-discovery round, revision 2)

**Field.** Castelnuovo–Mumford regularity, syzygies, Gröbner complexity, solving / last-fall / first-fall / regularity degrees, Hilbert series of Semaev ideals, Noether normalisation, border bases, resultant / subresultant / Dixon formulations, sparse elimination (BKK / Newton polytopes). Adjacent field used for the load-bearing lower bound: proof complexity (polynomial calculus, PC), the degree theory that Gröbner computations simulate.

**Relation to the earlier draft.** An earlier run of this same task wrote a dossier at this path (C1–C3, K1–K12) but never returned a structured result. That draft is preserved unchanged at `scout/ca2/prior-dossier.md`. This revision:
- keeps C1–C3, re-derives or re-checks their numbers in this session, and updates them;
- adds **C4**, a new prime-field proof (weighted homogeneity of summation polynomials);
- adds kills K13–K19.

**Inputs read this session.**
- Program sources:
  - ATLAS.md (every family), KRMAP.md;
  - object-frame-ideation.md §1–3, idea-generator.md "Search heuristics" and "Obstructions as generative material", target-result-profile.md;
  - the obstruction statements of every SO lead used below (extracted from the YAML rows);
  - the lead YAMLs LEAD-ICE-charged-toy-ic-exponent-vs-rho, LEAD-ICP-xline-symmetry-special-j, LEAD-ICP-digit-presentation-solving-degree, LEAD-STR-special-j-ic-semaev and LEAD-ICE-curve-presentation-invariance.
- Ledger records:
  - EV-PFDR-1394a4 and H-PFDR-4148b8 (the H-TOP heuristic);
  - IDEA-20261018-1aff90 (block-Wiedemann XL);
  - IDEA-20260816-a67f97 (leading-form meter);
  - index lines of H-PFDR-df0127, -6b9f1a and -ebec07.
- Literature notes KN-LIT-4e8513, -f37b9a, -0acb8c and -86a887.

**Hard-rule compliance.** Nothing inside any repository was edited. All outputs live under `scout/`:
- this file;
- `scout/margins.py` and `margins.out`, from the earlier run and re-run here (byte-identical, see `ca2/margins.rerun.out`);
- the new scripts and outputs in `scout/ca2/`, listed in the Appendix.

**Labelling rules.**
- Every number is computed by a named script in this session, labelled **derived**, or quoted from a named record.
- Expected values are labelled **prediction**.
- No experimental outcome is reported that this session did not produce.
- Figures carried over from the earlier draft were re-confirmed this session against their sources: `margins.out` (re-run), IDEA-20261018-e0857e, EV-DREG-008 and crypto `research/dreg_closure_m4l6_20261018/RESULTS.md` (all re-read).

---

## 0. The bottleneck read through commutative algebra

### O1. A binary descent has n equations; every prime-field presentation has one

- **Binary case.** Over F_{2^n}, a Semaev equation with x in an F_2-subspace descends to n F_2-equations, namely the Frobenius conjugates S(x)^{2^i}.
- **Prime-field presentations.** Over F_p, every presentation the program has tried gives one F_p-equation in about log2 p "small" unknowns:
  - digits, Boolean bits, the small-x box;
  - the PKM squaring tower x_{j+1} = x_j^2.
- **The tower has no conjugate equations.** The tower is the analogue of x, x^2, x^4, …, but x ↦ x^2 is not an automorphism of F_p, so no conjugate equations appear.
- **Consequences.**
  - Huang–Kosters–Yeo last-fall bounds do not transfer to prime fields. This agrees with H-PFDR-c88f14.
  - "One equation over a Boolean-like cube with about one solution" is the setting of knapsack proof-complexity lower bounds. That is candidate C1.

### O2. Tower monomials are characters

- On μ_{2^k} with x_0 = ζ^u, the squarefree tower monomial ∏_{j∈J} x_j equals ζ^{u·e}, where e = Σ_{j∈J} 2^j.
- The normal basis is therefore the character group of (Z/2^k)^m:
  - multiplication is exponent addition with carries;
  - degree is popcount.
- Restricting a tower system to one block is refutable in degree 2 by a Graeffe step, so C1's restriction argument cannot close towers. They are the residual open "implicit membership" class of KN-OPEN-020. That is candidate C2.

### O3. Deployed primes (recomputed this session, `ca2/o3_check.out`)

| curve | p mod 4 | v2(p−1) | v2(p+1) |
|:--|--:|--:|--:|
| P-256 | 3 | 1 | 96 |
| secp256k1 | 3 | 1 | 4 |

- No μ_{2^k} tower exists on either curve.
- P-256 carries a Chebyshev (Dickson) tower of length 96 in the norm-1 torus of F_{p^2}: x = z + z^{-1}, with x_{j+1} = x_j^2 − 2.
- So tower results transfer to P-256-type primes and not to secp256k1. This is transfer assumption T1.

### O4 (new). The leading form of every Semaev presentation is curve-free

- This is C4.
- The leading form of S_{m+1}(x_1..x_m, x_R) in the unknowns is ±∏ x_i^{2^{m−1}}, for every curve, every j and every target. It is the summation polynomial of the cusp y^2 = x^3, i.e. of the additive group G_a.
- Hence every top-form invariant (first-fall degree, degree of regularity, top-form Hilbert series) is blind to the curve.
- The curve enters only through weight-lowered components. This puts every remaining elliptic question at the solving / last-fall degree.

### Cost rule (derived; `margins.py`, re-run this session with byte-identical output)

- **Per-attempt budget.** Balanced IC needs B ≈ (m!·p)^{1/m} relations, at about one attempt each. The per-attempt budget is therefore T_max = p^{1/2}/B.
- **Linear algebra.** B^2 ≤ p^{1/2} additionally requires m ≥ 5 at P-256.
- **Solver price.** A degree-D total-degree Macaulay/XL/F4 oracle on N multilinear unknowns is priced at Σ_{d≤D} C(N,d) columns (ω = 1, attacker-optimistic).
- **Margin.** margin = log2 cols − log2 T_max at log2 p = 256:
  - ≥ +20 bits: closed;
  - [−10, +20): undecided;
  - < −10: open.
- **Caveat.** `margins.py` uses N = m·s and ignores the (m−2) internal F_p nodes of chained presentations. That understates columns, so the "closed" rows are conservative.

---

## C1 (prime; B2 and the digit arm of B1). IPS knapsack polynomial-calculus degree bound for digit / box presentations

**Bottleneck.**
- B2: prime-field Semaev solving degree (LEAD-ICE-prime-field-semaev-solving-degree, closed_known; EV-SDEG-4a1c3d is scoped to enumerative solvers).
- The digit arm of KN-OPEN-020's implicit class: LEAD-ICP-digit-presentation-solving-degree, open_next_step.
- C1 replaces that lead's degree-growth ladder (H-PFDR-d5f90f) with a scale-free proof for PC-simulable solvers.

**External ingredient.**
- Impagliazzo–Pudlák–Sgall 1999 (Comput. Complexity 8:127–144; ECCC TR97-042). **Retrieved this session**: PDF pp. 8–10 read via WebFetch.
  - Theorem 4.1: c_1..c_n nonzero reals, m arbitrary; then m − Σ c_i x_i "has no refutation of degree ⌈n/2⌉ in the field of reals".
  - Lemma 4.2: for nonzero p of degree < ⌈n/2⌉, the multilinearised product has degree deg(p)+1. The proof uses only full row rank of the k-set vs (k+1)-set inclusion matrix, rescaled by the c_i.
  - The induction on derivable lines is stated explicitly. Every line of a degree-≤⌈n/2⌉ proof is ML(p·(m − Σ a_i x_i)) with deg p ≤ ⌈n/2⌉ − 1.
  - §5 states that the Gröbner basis algorithm's "two main operations, reductions and S-remainders, can both be simulated by the polynomial calculus".
- Wilson 1990 (Europ. J. Combin. 11:609–615), diagonal form of W_{t,k}: entries C(k−i, t−i) with multiplicity C(v,i) − C(v,i−1); p-rank = sum over i with p ∤ C(k−i, t−i). **Retrieved via secondary sources only** (search result quoting the statement; arXiv 1302.4249), not the 1990 full text.
  - For t = k, k' = k+1 the entries are k+1−i ≤ ⌈n/2⌉. So full rank over F_p holds for p > ⌈n/2⌉ + 1, weaker than the p > s used below.

**Object frame.**
- Representation: R1. Each factor-base abscissa is written as x_i = Σ_j 2^j b_{ij} with Boolean b_{ij}.
- Operation set Σ: translation by factor-base elements, encoded either as S_{m+1}(x_1..x_m, x_R) = 0 (direct) or as an S_3 chain with internal nodes u_j ∈ F_p (chained).
- Trichotomy: **partial-action** (Class I index calculus). The relation vector propagates only under factor-base translation. C1 bounds the decomposition oracle's degree; it is not a new object.

**Derivation (single-responsibility lemmas; carried over from the earlier draft, with A1 now discharged by C4).**
- **L1-A (restriction).** Substituting constants maps a degree-D PC refutation to a refutation of the restricted system of degree ≤ D. A restriction of an unsatisfiable system stays unsatisfiable.
- **L1-B (branch substitution).**
  - Direct: fix blocks 2..m. The axiom becomes g(L(b_1)) = c·∏_t(L − r_t), with r_t ∈ F_{p^d}.
  - Chained: also substitute the internal nodes by one consistent algebraic branch. This is a ring homomorphism, so PC degree does not increase.
  - Either way the axiom is P·(L − r_1), with deg ML(P) ≤ min(2^{m−1} − 1, s) (direct) or ≤ 1 (chained).
- **L1-C (IPS over F_{p^d}).** Lemma 4.2 holds wherever the rescaled inclusion matrix has full row rank (Wilson, p > s). By the IPS invariant there is no refutation of degree ⌈s/2⌉. A refutation over F_p is also one over F_{p^d}.
- **L1-D (satisfiable attempts).**
  - With t solutions over F_p-bar (twist decompositions included), fix |J| ≤ log2 t + 1 bits to a value matched by no solution.
  - The resulting indicator lies in the radical, so D ≥ ⌈(s − log2 t − 1)/2⌉ + 1.
- **L1-E (axiom degree, direct presentations).** D ≥ deg ML(S_{m+1} in digits) = m·min(2^{m−1}, s), **now unconditional** at the deployed parameters:
  - By C4 (Theorem H-TOP) the x-leading form of S_{m+1}(x, x_R) is ±∏ x_i^{2^{m−1}}, coefficient ±1. Lower x-degree terms cannot reach the top multilinear degree.
  - For s ≥ k = 2^{m−1}, the top multilinear coefficient is ±(k!·∏_{j∈J} 2^j)^m, which is nonzero mod p for p > k.
  - For s < k it is ±c(s,k)^m, with c(s,k) = k!·[z^k] ∏_{j<s}(e^{2^j z} − 1). This session computed c(s,k) mod p for P-256 and secp256k1 at m = 7..10 (`ca2/a1_check.py`; formula cross-checked against brute-force expansion at four small (s,k)). It is **nonzero at every row**.
  - So assumption A1 of the earlier draft is discharged for m = 5..10 at both primes.
- **Conclusion (derived).** PC refutation degree ≥ ⌈s/2⌉ + 1 for direct and chained digit presentations. It holds for satisfiable attempts up to a log2 t loss, and for every Gröbner-order solver via IPS §5. The bound is tight for the all-ones knapsack (IPS Thm 3.2 gives the matching ⌈n/2⌉ + 1, read this session).
- **Against KR-IC-5931ee.** Yokoyama–Yasuda–Takahashi–Kogure is statistical and covers naive IC. C1 is assumption-free but scoped to PC-simulable solvers and digit / box presentations.

**Cost conversion** (`margins.out`, re-run this session; log2 p = 256):

| m | s | D_min | total-degree margin (chained) | direct axiom-degree margin | multidegree-truncating (chained) |
|--:|--:|--:|--:|--:|--:|
| 2 | 128 | 65 | +206.2 closed | +27.9 closed | +127.8 closed |
| 3 | 86 | 44 | +124.6 closed | +25.2 closed | +43.5 closed |
| 4 | 65 | 34 | +79.1 closed | +73.5 closed | +1.6 undecided |
| 5 | 53 | 28 | +50.1 closed | +155 closed | −22.9 open |
| 6 | 44 | 23 | +25.5 closed | +180 closed | −40.3 open |
| 7 | 38 | 20 | +9.4 undecided | +176 closed | −52.2 open |
| 8 | 34 | 18 | −1.7 undecided | +178 closed | −60.6 open |
| 9 | 30 | 16 | −13.1 open | +172 closed | −68 open |
| 10 | 28 | 15 | −19.0 open | +180 closed | −72.7 open |

**Scope.**
- The degree statement is a proof.
- The exponent consequence holds only for total-degree Macaulay / XL / F4 solvers.
- Multidegree-truncating solvers escape at m ≥ 5 (chained).
- SAT (resolution) and lattice solvers are not PC-simulable and are out of scope.
- The IPS size bound 2^{Ω(D²/N)} is too weak to close any exponent and is not used.

**SO codes touched.** Each obstruction.statement is quoted verbatim, Scope clause included.
- **SO-ALGFB** (LEAD-ICP-algebraic-membership-factor-base):
  > "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."

  - Premise escaped: "algebraic locus of degree d … membership polynomial prod(x − v)". A digit description is an auxiliary-variable (implicit) presentation, not a degree-d locus on the x-line.
  - C1 does not escape the obstruction's conclusion. It extends it to that implicit sub-class for PC-simulable solvers. Yield conservation still holds.
- **SO-TABLE** (LEAD-ICP-generic-table-decomposition):
  > "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p."

  - Premise escaped: "enumerates or table-looks-up". C1 covers the complementary non-enumerative algebraic oracles.
- **SO-GEN** (LEAD-RHO-generic-sqrt-lower-bound):
  > "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r."

  - Premise escaped: "generic algorithm". The oracle reads coordinates as digits.

**Tier.** X: an exponent-level closure.

**Predicted gain.** 0 for the attack; this is a closure.
- **Prediction:** the five-lemma proof goes through. At m = 4 on P-256, D ≥ 34, giving ≥ 2^141.9 columns against a 2^62.9 per-attempt budget.
- **H1:** IPS Lemma 4.2 transfers to F_{p^d} for p > s via Wilson's p-rank. Validation: the exact PC checker below.
- **H2 (was A1):** the top multilinear coefficient is nonzero mod p. **Discharged** by C4 for s ≥ 2^{m−1}, and computed nonzero for P-256 and secp256k1 at m = 7..10.

**First discriminating step.**
1. Write the five-lemma proof (Opus, about 1 day).
2. Build an exact PC-degree checker: the smallest D with 1 in the row space of the multilinear degree-D Macaulay closure over F_p.
3. Run it on the restricted knapsack (s = 6..14) and on direct and chained digit systems at m = 2, 3 with s ≤ 8, three toy primes each, against H-PCD-03be5a's support-matched null.

**Outcomes → dispositions.**
- Proof and checker agree:
  - The degree statement → **closed_obstructed(proof)** (best_measured "PC degree ≥ ⌈s/2⌉+1").
  - Direct presentations at every m, and chained at m ≤ 6, under total-degree solvers → **closed_obstructed(cost_model)**.
  - Chained m ≥ 7 (total degree) and m ≥ 5 (multidegree solvers) stay **open_next_step** on LEAD-ICP-digit-presentation-solving-degree, best_measured = the C1 table.
- The checker finds an unsatisfiable draw refuted below ⌈s/2⌉ + 1 → the proof is defective. The lead stays **open_next_step** with that counterexample as best_measured; it would be the first sub-knapsack F_p fall.

**Cost.**
- Implementation: 1–2 days (Opus proof; Sonnet checker reusing the DREG multilinear builder).
- Compute: minutes to an hour at N ≤ 24 on a laptop.

**Self-kill risk.**
- The value is mainly scoping; the lane was already expected to close at scale.
- The multidegree-solver escape at m ≥ 5 must not be over-claimed.
- Wilson is cited from secondary statements only.

**--match phrasings (top hits, run this session; `ca2/match_runs.txt`).**
- Own: "polynomial calculus knapsack lower bound for digit-presented prime-field decomposition via block restriction" → KR-IC-46d822 (13), LEAD-ICP-digit-presentation-solving-degree (11).
- Plain: "prove that writing factor-base x-coordinates in binary digits forces Groebner degree to grow like half the digit count" → LEAD-ICP-digit-presentation-solving-degree (17), LEAD-ICE-descent-closure-degree-at-scale (12).
- Obstruction vocabulary (nearest closed_known, LEAD-ICE-prime-field-semaev-solving-degree): "prime-field Semaev Groebner solving degree law for interval bases cannot reach the sub-rho threshold" → LEAD-ICE-prime-field-semaev-solving-degree (38).

---
## C2 (prime; B1). Popcount-filtered exact refutation-degree meter for squaring and Chebyshev tower factor bases, with an exponent threshold table

**Bottleneck.**
- B1, the non-enumerative oracle.
- The PKM tower is the prime-field line's one exponent-deciding open question (IDEA-20261018-e0857e, unmapped in the atlas). Its msolve cells are memory-blocked:
  - m = 4, N = 20: D ≥ 8, censored at 5 GB;
  - m = 3, N = 18–24: stopped by a 45-minute wall at D ≥ 7;
  - 256–512 GB hosts are requested.
  - All three figures were re-read in IDEA-20261018-e0857e this session.
- Recommended mapping: fold IDEA-20261018-e0857e, IDEA-20261022-727676 and IDEA-20261018-2d21b9 into LEAD-ICP-digit-presentation-solving-degree as its tower arm.

**External ingredients.**
- O2: tower monomials are characters (derived).
- Bardet–Faugère–Salvy Boolean semi-regular series (1+t)^N/∏(1+t^{d_j}) as the single-equation null. **Recalled.**
- IPS §5 Gröbner→PC simulation. **Retrieved this session.**
- Petit–Kosters–Messeng, PKC 2016, pp. 3–18, as the tower source. **Retrieved** (bibliographic record and summary only).

**Object frame.**
- Representation: R1. x ∈ μ_{2^k} (p ≡ 1 mod 2^k), or x = z + z^{-1} with z ∈ μ_{2^k} in the norm-1 torus (p ≡ −1 mod 2^k, P-256 type). It is written in tower variables x_j = x^{2^j}, or by the Chebyshev chain, in the squarefree character / cosine normal basis.
- Operation set Σ: translation by factor-base elements via S_{m+1} or an S_3 chain. A symmetric arm uses Graeffe-iterated coefficient vectors.
- Trichotomy: **partial-action** (Class I). Membership is implicit (k quadrics plus auxiliary variables), the KN-OPEN-020 implicit-membership class.

**Derived lemmas.**
- **L2-1 (restriction is useless for towers).** A one-block restriction is refuted in degree 2 by Graeffe steps.
- **L2-2 (ring ↔ quotient).** Lower bounds transfer from the quotient to the ring. Plateaus transfer within +1 degree.
- **L2-3 (Nullstellensatz side number).** popdeg(s^{-1}) ≤ NS-degree ≤ popdeg(s^{-1}) + popdeg(s), computable by one size-2^N FFT.
- **L2-4 (direct-tower axiom degree).**
  - This is m(m−1) when the max-popcount monomials ∏_i x_i^{2^{m−1}−1} are present (A2).
  - **This session computed the A2 coefficient** (`ca2/a2_check.out`):
    - m = 2: −2(a + x_R²);
    - m = 3: −8(5x_R³ + 3a x_R + 6b).
  - So A2 holds except at ≤ m target abscissas per curve. The coefficient has weight 2m, as C4 predicts. The curve enters exactly here, in a weight-lowered component.
  - Margins at P-256:
    - m = 3: −3.3, undecided;
    - m = 4: +4.3, undecided;
    - m = 5: +23.6, closed;
    - m = 6: +47.6, closed.
- **L2-5 (symmetric pullback).** sym-PC ≥ tower-PC / m.

**Threshold table** (`margins.out`, log2 p = 256). D* is the largest refutation degree with log2 Σ_{d≤D} C(N,d) ≤ T_max:

| m | N | T_max bits | D* (ω=1) | D*/N | D* (ω=2) |
|--:|--:|--:|--:|--:|--:|
| 3 | 258 | 41.8 | 6 | 0.023 | 2 |
| 4 | 260 | 62.9 | 11 | 0.042 | 4 |
| 5 | 265 | 75.4 | 13 | 0.049 | 5 |
| 6 | 264 | 83.8 | 15 | 0.057 | 6 |
| 8 | 272 | 94.1 | 18 | 0.066 | 7 |
| 10 | 280 | 100.2 | 19 | 0.068 | 8 |
| 12 | 288 | 104.3 | 20 | 0.069 | 8 |

**SO codes touched.**
- **SO-ALGFB** (quoted under C1).
  - Premise escaped: "membership polynomial prod(x − v) of degree B". Membership is k quadrics with auxiliary variables.
  - The yield-conservation clause still binds.
- **SO-TABLE** (quoted under C1). Premise escaped: "enumerates or table-looks-up".
- **SO-GEN** (quoted under C1). Premise escaped: "generic algorithm".
- **SO-QSP** (LEAD-ICB-quasi-subfield-polynomials). The row's statement carries no Scope clause:
  > "Euler-Petit Theorem 1: every linearized QSP has beta >= 3/4, so under the HKPYY cost model the exponent is >= 0.93, i.e. >= 2^122 at n = 131 against rho 2^60.9; for F_2-coefficient lambda only X^2 + X (n0 = 1) and L_Phi131 (n0 = 130) exist at n = 131 (Prop. 2), and multiplicative QSPs give |V| = 264 or p + 1, beta >= 1.02. The crypto census also shows Lemma 4.1 tight (the n mod n0 term cannot be removed; witnesses at n = 7). Measured at toy n = 31, k = 15: QSP bases yield 0.214 against 0.204-0.230 for random subspaces (no gain)."

  - Touched by analogy only: x^{2^k} − 1 is a completely splitting multiplicative splitter over F_p.
  - The premises "linearized" and "F_2-coefficient lambda at n = 131" do not apply.

**Tier.** X: it decides an exponent question.

**Predicted gain.**
- **Prediction (H2-a):** the quotient-PC degree on unsatisfiable draws grows as D(N) ≈ N/2 − c_m. At N ≈ 260 that is D ≈ 120 ≫ D* ≤ 20, so there is no gain and the line closes.
- **Minority branch, conditional on H2-b (plateau):**
  - A chained tower at m = 5 on P-256 plateauing at D = 8 costs about 2^49.0 columns per attempt (B = 2^52.6).
  - Total ≈ 2^101.6 for relations plus 2^105.2 for linear algebra, against rho's 2^128.
  - That is an exponent ≈ 0.41.
- **Heuristics:**
  - H2-a: single-equation semi-regular growth.
  - H2-b: plateau (the negation of H2-a).
  - H2-c: s^{-1} has full character support (validated by the FFT side number).
  - A2: max-popcount monomials present. Now computed for m = 2, 3: true off ≤ m target values.
  - T1: transfer only to primes with 2^k | p ∓ 1 (P-256 type; not secp256k1).

**First discriminating step.**
1. **Step 0.** Rebuild the recorded msolve PKM cells. Record their chain maps and whether S was direct or chained.
2. **Step 1.** Build the carry-aware multilinear Macaulay closure in the character basis for:
   - μ and Chebyshev chains;
   - direct and chained forms;
   - the symmetric arm.

   Measure the exact quotient-PC refutation degree at N = 12..28 (m = 2..6) on ≥ 4 unsatisfiable draws plus satisfiable controls, three toy primes per congruence class.
3. **Controls:**
   - a support-matched random null;
   - the knapsack-digit system as a positive control (it must reproduce C1);
   - the FFT side number.
4. Fit D(N) and apply the threshold table.

At N = 21, D = 9 the quotient matrix has 695,860 columns, against C(30,9) = 14,307,150 for the ring (both recomputed this session). That is a column-count model, not a measured msolve footprint.

**Outcomes → dispositions.**
- D(N) slope puts D(260) above D* for every m ≤ 12 → tower arm **exhausted_at_scale** (toy, fitted slope). It becomes **closed_obstructed(cost_model)** if a scale-free bound is later proved.
- Plateau at ≤ D*(m) for some m, with controls intact → **open_next_step**, best_measured = plateau degree and N range. Next step: full charged IC vs matched rho on toy curves.
- PC plateaus but msolve keeps growing → **open_next_step** as a solver gap.
- Anchor not reproduced → stop and record the instrument mismatch.

**Cost.**
- Implementation: 2–3 days.
- Compute: hours at N ≤ 24 (64 GB); about 1 day at N = 28 (128 GB).

**Self-kill risk.**
- The predicted outcome is closure.
- A positive result transfers only to P-256-type primes.
- For direct towers at m ≥ 5 the axiom degree alone closes the line, so only the chained and symmetric arms are informative.
- The Macaulay meter is itself an XL oracle and is priced as one.

**--match phrasings (top hits, run this session).**
- Own: "tower-presented subgroup factor base characters popcount filtration exact refutation degree PKM tower plateau" → LEAD-ICP-algebraic-membership-factor-base (16), LEAD-ICB-nonlinear-frob-stable-bases (14).
- Plain: "cheaply measure whether the squaring-chain subgroup factor base keeps a bounded Groebner degree as the chain grows" → LEAD-ICB-nonlinear-frob-stable-bases (15), LEAD-ICB-quasi-subfield-polynomials (15), LEAD-ICP-algebraic-membership-factor-base (15).
- Obstruction vocabulary (SO-ALGFB): "multiplicative subgroup factor base x^B = 1 with low-degree membership surviving substitution into the summation polynomial" → LEAD-ICP-algebraic-membership-factor-base (42).

---

## C3 (binary; B4/B5). Block-multilinear (multigraded) truncated closure for chained descended S_3 cells, to unblock the (m, l) = (3, 7) degree-5 question

**Bottleneck.**
- B5 / B4: LEAD-ICE-descent-closure-degree-at-scale is open_blocked. Its (m, n, l) = (3, 19, 7) degree-5 cell hit 169 GB under a 184 GB cap; the projection is 217 GB.
- The answer decides the ECC2K-130 m = 4 row (+7.6 vs +10.32 bits) and feeds LEAD-ICE-hybrid-guess-determine-l7.

**Structural fact (derived).**
- In characteristic 2, x and x² are F_2-linear in the bits. S_3 has degree ≤ 2 per variable, so every descended S_3 equation has block-degree ≤ 1 in each of its three blocks (x_i, x_j, u). Chained S_3 systems are therefore block-multilinear.
- Unchained S_4 is not block-multilinear.
- The full-closure count Σ_{d≤5} C(40,d) = 760,099 reproduces the program's projection at 3·cols²/8 bytes: 216.7 GB here against the 217 GB recorded in crypto RESULTS.md (re-read).
- Calibration from the same RESULTS.md: the solved (4,15,6) degree-4 closure measured 25.8 GB RSS against 44 GB projected, and its recorded column count 342,537 matches the 342,541 computed here to within 4 columns. The dense model therefore over-states memory by about 1.7×, so the truncated figures below are conservative.

**External ingredient.**
- Faugère–Safey El Din–Spaenlehauer, arXiv 1001.4004 (2010; JSC 2011): Hilbert series of generic bilinear ideals and a degree-of-regularity bound for generic affine bilinear systems. **Retrieved this session** (abstract). The specific bound min(n_x, n_y) + 1 is **recalled**.
- Bender–Faugère–Tsigaridas, ISSAC 2018 (arXiv 1805.03577): multihomogeneous Gröbner algorithms. **Recalled.**
- Applicability to Boolean systems with field equations is heuristic H3-a.

**Object frame.**
- Representation: R3, Weil restriction to F_2.
- Operation set Σ: factor-base translation.
- Trichotomy: **partial-action**. C3 is an instrument (multidegree truncation of the Macaulay closure).

**Column / memory figures** (`margins.out`; dense, 3·cols²/8 bytes):

| cell | full cols / GB | u-deg ≤ 1 | u-deg ≤ 2 | u-deg ≤ 3 |
|:--|--:|--:|--:|--:|
| (3,19,7) D=5 | 760,099 / 216.7 | 171,289 / 11.0 | 438,391 / 72.1 | 663,199 / 164.9 |
| (4,15,6) D=4 (solved) | 342,541 / 44.0 | 82,701 / 2.6 | 213,636 / 17.1 | 315,136 / 37.2 |
| (4,15,6) D=5 | 3,505,051 / 4,607 | 443,985 / 73.9 | 1,455,360 / 794 | — |

**Adjacent record (dedup).** IDEA-20261018-1aff90 (proposed, unmapped) is a GF(2) block-Wiedemann consistency test on the plain-XL Macaulay matrix, memory O(nnz).
- It loses closure semantics: plain XL is 2–3 degrees pessimistic, as that record states.
- C3 keeps closure semantics inside a smaller monomial space.
- The two are complementary: Wiedemann can run the truncated closure's final consistency step.

**SO codes touched.**
- **SO-TABLE (binary)** (LEAD-ICB-generic-table-oracle):
  > "Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, so with |Aut| = 2n no 4-, 5- or 6-sum table can beat sqrt(r/2n) in total work; the balanced generic-IC cost is ~ r^{2/3}/n^{4/3} against rho r^{1/2}. Measured: rungs sit 2^25-2^27 above the generic line; ln(IC/rho) grows 0.165 [0.117, 0.213] per ln r. Target-dependent and walk-carried bases are known-log pools (H-BINSTD-1447cf). At ECC2K-130 this route needs K* ~ 4e11 columns and ~8e9 core-years. Scope: all binary and Koblitz curves, one target, setup charged."

  - Premise escaped: "built from group operations and membership tests". The oracle is algebraic.
- **B4 writability** (LEAD-ICP-icperf-writability-boundary):
  > "At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]."

  - Premise escaped: "unchained descended ANF". Chained S_3 is block-multilinear, with O(l²n) terms per equation.
- **SO-GEN** (quoted under C1). Premise escaped: "generic algorithm".

**Tier.** I: a memory constant that unblocks an exponent-relevant degree question.

**Predicted gain.**
- **Prediction (H3-b):** the refutation certificates of the solved (4,15,6) degree-4 draws live at u-degree ≤ 2. If so, (3,7) at degree 5 needs 72.1 GB instead of 216.7 GB (3.0× less) and fits the existing 184 GB host.
- H3-a: multigraded truncation preserves refutations for block-multilinear Boolean systems.
- No board gain. ECC2K-130 m = 4 stays ≥ +7.6 bits over rho in every branch.

**First discriminating step.**
1. Re-run the solved (4,15,6) degree-4 closure on draws 42 and 214 plus satisfiable control 0, truncated to u ≤ 1 and u ≤ 2 (2.6 / 17.1 GB).
2. If refutations persist, run (3,19,7) degree 5 at u ≤ 2 (72 GB) on ≥ 4 unsatisfiable draws plus a control.

**Outcomes → dispositions.**
- (3,7) refutes at degree 5 → LEAD-ICE-descent-closure-degree-at-scale moves open_blocked → **open_next_step**, best_measured "(3,7) refutes at 5". The +10.32 bracket input is confirmed.
- (3,7) refutes at 4 → **open_next_step** (+7.6 row restored).
- Truncation loses the (4,6) refutations → C3 killed; the lead stays **open_blocked**.
- (3,7) truncated does not refute → inconclusive, since truncation is one-sided; the lead stays **open_blocked**.

**Cost.**
- Implementation: about 1 day.
- Compute: 1–2 h for the (4,6) re-runs; about 1 h for (3,7).

**Self-kill risk.**
- Truncation is one-sided.
- H3-b is unverified.
- Binary is secondary priority.
- Block-multilinearity may be implicit in the program's `s3_multilinear` code; the new part is the multidegree truncation.

**--match phrasings (top hits, run this session).**
- Own: "multigraded block-multilinear truncated closure for chained descended S_3 systems" → LEAD-ICE-descent-closure-degree-at-scale (11).
- Plain: "shrink the memory of the binary decomposition refutation by limiting degree in the internal-node variables" → LEAD-ICE-descent-closure-degree-at-scale (19), LEAD-ICB-prime-degree-algebraic-decomposition (16).
- Obstruction vocabulary (writability): "descended ANF too large to write inside the rho budget chained Semaev system memory column" → LEAD-ICP-icperf-writability-boundary (35).

---
## C4 (prime; B2, and where B1 can still meet the curve). Weighted homogeneity of summation polynomials: every Semaev decomposition system has the curve-free leading form ±∏ x_i^{2^{m−1}} (the cusp / G_a limit)

**What C4 is.**
- A cheap proof with an attached instrument.
- It discharges the numbered heuristic H-TOP (HEUR-001 of H-PFDR-4148b8, "a symbolic obligation at m ≥ 3") for every m.
- It promotes EV-PFDR-1394a4's empirical closed form for the first fall degree to a derivation.
- It gives a new closed form for the top-form degree of regularity.
- It decides the top-form (first-fall / d_reg / leading-form-meter) arms of three open leads. It does not decide their last-fall or solving-degree arms:
  - LEAD-ICP-xline-symmetry-special-j;
  - LEAD-STR-special-j-ic-semaev;
  - LEAD-ICE-curve-presentation-invariance.
- It proves that automorphism folding at j = 0 / 1728 is a between-target equivariance.

**Bottleneck.**
- B2: prime-field solving degree. Specifically, its sub-questions "can special j, an isogenous curve or another Weierstrass model lower the degree?" and "is the digit lane's curve-free first fall an accident of small s?".
- B1: C4 says where an elliptic, non-generic advantage could still live, namely only in weight-lowered terms. That shapes any non-enumerative oracle instrument.

**External ingredients.**
- **Weierstrass scaling isomorphisms.** (x, y) ↦ (λ²x, λ³y) maps E_{a,b} to E_{λ⁴a, λ⁶b}, preserving O and the group law. Standard; **recalled** (e.g. Silverman, AEC III.1).
- **Semaev 2004 summation polynomials** (IACR ePrint 2004/031). **Retrieved** (abstract page). The resultant recursion S_{n} = Res_X(S_{n−k}(…, X), S_{k+2}(…, X)) and the S_3 formula are **recalled**, and match KR-IC-5a43e5 and the S_3 used in this session's scripts.
- **Isobaric property of resultants.** The resultant of weighted-homogeneous polynomials in a weighted variable is weighted-homogeneous. Classical; **recalled** (e.g. Cox–Little–O'Shea, *Using Algebraic Geometry*, ch. 3).
- **Caminata–Gorla 2021**, "Solving degree, last fall degree, and related invariants" (ePrint 2021/1611; JSC). **Retrieved** (abstract page this session; the definitions and theorems below are quoted from the program's full-text note KN-LIT-4e8513).
  - Def 1.3: d_ff = min{d : Syz(F^top)_d / Triv(F^top)_d ≠ 0}.
  - Def 1.4: d_reg = min{d : (F^top)_d = R_d}.
  - Thm 5.2 (Semaev–Tenti): with the field equations of F_q, sd ≤ 2 d_reg − 2.
- **Wilson 1990** p-rank of inclusion matrices (as in C1).

**Object frame.**
- Representation: R2, the short-Weierstrass model family viewed as a weighted family over (a, b, x_R), with weights x: 2, x_R: 2, a: 4, b: 6.
- Operation set: factor-base translation (Class I), plus the G_m scaling action on instances, (x, x_R, a, b) ↦ (λ²x, λ²x_R, λ⁴a, λ⁶b).
- Trichotomy: **partial-action.** IC is Class I; the scaling acts on the family of instances, not on the prime-order group.
- Lossy-projection reading: the top-form truncation is a projection that discards all weight-lowered components (all curve and target data). C4 proves that this projection is constant on the family. So the leading-form meters measure the cusp, not the curve.

**Derivation (single-responsibility).**
- **Lemma W (weighted homogeneity; correctness).**
  - S_3 = (x1−x2)²x3² − 2((x1+x2)(x1x2+a)+2b)x3 + (x1x2−a)² − 4b(x1+x2). All 13 monomials have weight 8 (`ca2/leadform.out`).
  - Induction: by the isobaric property, S_{m+1} = Res_X(S_m(x_1..x_{m−1}, X), S_3(x_m, x_{m+1}, X)) is weighted-homogeneous of weight W_{m+1} = m·2^m.
  - S_4 has weight 24, checked with all 540 terms (`ca2/leadform.out`).
- **Decomposition into weight components (size).** S_{m+1}(x, x_R; a, b) = Σ_{k,i,j} x_R^k a^i b^j F_{kij}(x), with F_{kij} homogeneous in x of degree W/2 − k − 2i − 3j. The top x-component is therefore F_000(x) = S_{m+1}(x, 0; 0, 0) whenever that is nonzero.
- **Theorem H-TOP (correctness).**
  - **Statement.** For every m ≥ 2, every field of characteristic ≠ 2, 3, every (a, b) (singular or not) and every x_R, the top x-degree component of S_{m+1}(x_1..x_m, x_R; a, b) is ε_m ∏_{i≤m} x_i^{2^{m−1}}, with ε_m = ±1.
  - **Proof.**
    1. S_3(u, 0, X; 0, 0) = u²X².
    2. Res_X(f, cX²) = ±c^{deg f}·f(0)², so S_{m+1}(x, 0; 0, 0) = ±x_m^{2^{m−1}}·S_m(x_1..x_{m−1}, 0; 0, 0)².
    3. Induction from S_3(x_1, x_2, 0; 0, 0) = x_1²x_2² gives ±∏ x_i^{2^{m−1}}. The degree is m·2^{m−1} = W/2, so this is F_000.
  - **Side condition (H4-1).** deg_X S_m(·, X; 0, 0) = 2^{m−2}: the X-leading coefficient does not vanish at the cusp. It is recalled to be a square of a lower summation polynomial; a failure would have changed the checked top forms.
  - **Checks produced this session.**
    - m = 2, 3 (symbolic): leading forms x1²x2² and x1⁴x2⁴x3⁴, coefficient +1 (`ca2/leadform.out`).
    - m = 4 (numeric): the λ³²-coefficient of S_5(λc, x_R), recovered by degree-32 interpolation, equals (c1c2c3c4)⁸ exactly. This holds at 3 random points for each of two (p, a, b, x_R) draws: p = 1000003 and p = 2^61 − 1 (`ca2/leadform_m4_numeric.out`).
- **Corollary G (the cusp is G_a; structure).**
  - The full top form of S_n is S_n(x; 0, 0), the summation polynomial of y² = x³. Its smooth locus is G_a via t = x/y, x = t^{−2}.
  - Hence S_n(x; 0, 0) = c·(∏ x_j)^{2^{n−2}} ∏_ε (Σ_j ε_j x_j^{−1/2}).
  - Checked at m = 4: the ratio is exactly 1 at 6 random points of GF(1000003) (`ca2/leadform_m4_numeric.out`).
  - **Reading:** the leading-form layer of every elliptic decomposition problem is a signed subset-sum in the additive group. This is why knapsack proof-complexity bounds (C1) are the natural lower-bound tool, and why nothing elliptic can appear at the top-form level.
- **Corollary F (first fall degree, exact; promotes EV-PFDR-1394a4).**
  - d_ff here is the Boolean adaptation of the top-form first-fall definition used by H-PFDR-4148b8 (D1), in Λ = F_p[b]/(b²). Caminata–Gorla Def 1.3 is stated in F_q[x]/(x^q − x) with the base field's own field equations; the digit systems use b² − b over F_p. In either reading, d_ff depends only on F^top.
  - For the base-2 digit system, F^top = {±∏_i L_i^{2^{m−1}}} ∪ {b_ij²}, so H-PFDR-4148b8's (D4) computation applies verbatim with H-TOP now proved:
    - d_ff = m·2^{m−1} + ⌊(s − 2^{m−1})/2⌋ + 1, for s ≥ 2^{m−1} and p > s.
  - **Recomputed this session** in Λ = F_p[b]/(b²) at (m, s) ∈ {(2, 3..6), (3, 5)}: it equals the closed form at every cell with d_ff ≤ N. The boundary cells s = 2^{m−1} fall at N + 1, as in the record (`ca2/lambda_check.out`).
- **Corollary R (top-form degree of regularity; new closed form).**
  - d_reg = min{d : (F^top)_d = R_d} = (m−1)s + ⌈(s + 2^{m−1})/2⌉ = N − ⌊(s − 2^{m−1})/2⌋, for s ≥ 2^{m−1} and p > s.
  - **Derivation.** A multidegree-(d_1..d_m) component of Λ_d is hit by f·Λ iff each block's up-map e_k: Λ_s^{(d_i − k)} → Λ_s^{(d_i)} is surjective. By Wilson (p > s) that holds iff d_i ≥ ⌈(s + k)/2⌉. The largest d with a failing block is therefore (m−1)s + ⌈(s+k)/2⌉ − 1.
  - **Checked** at all 7 cells (`ca2/lambda_check.out`).
  - **Consequence (K14).** Semaev–Tenti's sd ≤ 2 d_reg − 2 would give about 2N − s + 2^{m−1} − 2, above the trivial Boolean bound. So no curve-free upper bound sandwiches C1's lower bound. The hypotheses also differ: field equations of F_q there, Boolean constraints over F_p here.
- **Corollary B (curve / j / target / model / isogeny blindness of every top-form invariant).**
  - **Scope.** Any presentation whose membership top forms are curve-free:
    - digits and the box;
    - μ_B (x^B);
    - squaring / Chebyshev towers (x_j²);
    - orbit bases;
    - chained presentations, whose top forms are S_3^{cusp}(x_i, x_j, u) and u²x_m².
  - **Statement.** F^top is identical for every short-Weierstrass curve (every j, every isogeny class), every target x_R, and every Weierstrass model x ↦ u²x + r, which acts on top forms by a scalar. Its coefficients (±1, 2^j) also make it identical for every p above a computable threshold.
  - **Consequences.**
    - d_ff, d_reg, the top-form Hilbert series and every leading-form meter cannot distinguish special j, an isogenous curve, another model or another target. The meters covered include EXP-ALPF-011's "first-fall meter on homogeneous leading forms" and H-PFDR-4148b8's fall_dim.
    - For IDEA-20260816-a67f97: C4 shows that the leading-form verdict is the same for every curve and target, so it carries no curve information. It does **not** measure the leading-form vs full-system agreement rate that claim (C) asks for; that measurement stays open.
  - **Vélu-augmented ideals** (EXP-DREG-dd668d's eliminated arm). Vélu gives X = x + O(1/x), so the cleared relation X·D(x) − N(x) has the top form x^{deg D}(X − x). That is curve- and kernel-free for a fixed kernel size. (Derivation only, validation pending: compute one certified ℓ = 3 edge. Vélu is recalled.)
- **Corollary E (automorphism folding is a between-target equivariance; proof).**
  - At j = 0, take λ² = ζ_3, so λ⁶ = 1 and Lemma W gives S_{m+1}(ζx, ζx_R; 0, b) = λ^W S_{m+1}(x, x_R; 0, b).
  - The substitution x_i ↦ ζx_i maps the system of (R, F) onto that of ([ω]R, ζF).
  - For an orbit-stable base the systems of R, [ω]R and [ω²]R are therefore linearly equivalent: same Hilbert function, same Macaulay ranks at every degree, same PC degree, same F4 trace up to scaling.
  - Same at j = 1728 with x ↦ −x (λ² = −1, so λ⁴ = 1).
  - Per instance nothing changes. The only gain is the known orbit factor in relations, matched by rho's √|Aut| (KR-IC-955fd6, KR-RHO-0528e7). This is the prime-field analogue of LEAD-ICB-frobenius-search-symmetry's proof.
- **Corollary L (where the curve can enter).**
  - Every curve, j or target effect on Macaulay ranks lives in the components x_R^k a^i b^j F_{kij} with (k, i, j) ≠ 0:
    - at j = 0 the i > 0 blocks vanish identically;
    - at j = 1728 the j > 0 blocks vanish identically.
  - So "coefficient-block vanishing" (H-PFDR-df0127 / -6b9f1a) is an identity, not a null. The informative comparison is special-j against a random-coefficient system with the same weight-block support.
  - Example produced this session: C2's A2 coefficient −8(5x_R³ + 3a x_R + 6b), of weight 6.
  - This suggests a **fall-on-kernel meter**:
    - compute K_d = ker(top-form map at degree d) once per presentation shape (curve-free);
    - per curve, compute only the rank of the lower-weight map on K_d.
  - Whether a top-form syzygy lifts to a genuine degree fall is exactly this rank.

**SO codes touched.**
- **SO-ENDO** (LEAD-STR-endo-scalar-action-generic):
  > "For G of prime order N, End(G) = Z/N, so every endomorphism-image oracle is simulable by group operations and Shoup's bound applies (KN-FIND-b7e091, EV-GGM-79e710, DEC-20260804-3b4258). Augmenting the witness lattice with r eigenvalues leaves the index at N and the meet-in-the-middle exponent at 1/2 (H-ENDO-001). The one EV-ENDO-001 contradiction (first minimum exactly 1 on the J0 cells, by Vieta 1 + lambda_2 + lambda_3 = 0) is a certificate-void k-independent vector. It does not touch the exponent. Scope: any prime-field or binary curve, any size, prime-order subgroup."

  - Premise: "endomorphism-image oracle … simulable by group operations" is a generic-model statement.
  - C4 does not escape it. Corollary E extends the same conclusion (the automorphism acts only between targets) into the non-generic Gröbner / PC solver class, which the premise does not cover.
- **SO-ISO** (LEAD-STR-isogeny-class-generic-invariance). The row's statement has no Scope clause:
  > "Isogenous curves have F_p-isomorphic prime-order subgroups (T1), and rho and BSGS depend only on the group order and the automorphism group. The automorphism group is a class invariant except at the j=0/1728 crater. Measured with controls: the crypto 26-bit census of three whole volcanoes (403,168 runs, every instance carried by verified Velu maps) found 33/35 level ratios equivalent under TOST (±5% rho/BSGS), 0 different, and no curve effect beyond the isomorphic-control spread. v2.1 rho floor/crater is 1.004 [0.990, 1.016]. 40- and 48-bit volcano-rho studies found no level effect. Transport is exact and costs at most 1.3% of a solve."

  - Premise: "rho and BSGS depend only on the group order …", i.e. generic algorithms.
  - Corollary B carries class invariance to the top-form invariants of a non-generic algorithm class, within each presentation shape.
- **SO-ALGFB** (quoted under C1). C4 supplies C1's discharged A1 and does not escape SO-ALGFB.
- **Nearest closed lead: LEAD-EXO-curve-model-representation** (kind measured):
  > "Model-native PDP solving degree is invariant (d_reg = 2) between Weierstrass Semaev and twisted Edwards at m=2 and m=3, with Edwards a constant factor larger (EV-REP-001, EV-REP-002 replicated); the Kummer line is Bezout-optimal among coordinates E -> P^1 and the model lever is capped by a one-line degree argument (IDEA-20260905-d0fee4, IDEA-20260913-11d3cb, proposals). Exponent lever closed; at most constant factors (Hessian coordinate factor <= 2) remain."

  - Premise "measured … at m=2 and m=3". C4 supplies the all-m reason for Weierstrass models, special j and isogenous curves.
  - Edwards is a different equation shape and is not covered.

**Tier.** X: a closure of exponent-level top-form questions, with no gain. It does not decide the solving degree.

**Predicted gain.** 0; this is a closure / scoping proof.
- **Predictions:**
  - P4-1: H-TOP holds at m = 5 by the same λ-interpolation check.
  - P4-2: at every toy cell, j = 0, j = 1728, generic and isogenous curves give identical d_ff, d_reg and top-form Hilbert series. This is a theorem; a mismatch means an instrument defect.
  - P4-3: lower-weight fall ranks at special j do not exceed those of the random same-support null. This is a genuine prediction, the semi-regular expectation, not a theorem.
- **Heuristics:**
  - H4-1: X-degree non-drop at the cusp (side condition above; validated m ≤ 4).
  - H4-2: p > s (Wilson), for the exact d_ff / d_reg.
  - H4-3: Vélu X − x = O(1/x).

**First discriminating step.**
1. Write Lemma W, Theorem H-TOP and Corollaries F, R, B, E and L as a derivation (Opus, half a day). Extend `ca2/leadform_m4_numeric.py` to S_6 (m = 5) to check P4-1 (minutes).
2. Build the fall-on-kernel meter on the existing Macaulay rank builder. Run it on the m = 2, 3 digit systems (s ≤ 6) at three toy primes for:
   - j = 0 and j = 1728;
   - three generic curves;
   - one certified 3-isogenous pair;
   - a random-coefficient null with the same weight-block support.

   Record d_ff and d_reg (must agree by theorem), the lower-weight fall rank per degree, the last-fall degree and the grevlex solving degree.

**Outcomes → dispositions.**
- **Proof checks (P4-1 passes).** HEUR-001 of H-PFDR-4148b8 is discharged.
  - LEAD-ICP-digit-presentation-solving-degree keeps **open_next_step** (last-fall degree).
  - best_measured adds "d_ff closed form proved (Wilson, p > s); d_reg(top) = N − ⌊(s − 2^{m−1})/2⌋ (derived)".
  - The forecloses phrase "first fall degree of the digit-presented decomposition system" becomes proof-backed.
- **A measured top-form invariant differs across curves.** This is an instrument defect, since the theorem forbids it. Repair the meter; no disposition change.
- **Lower-weight fall ranks, last-fall and solving degrees at j = 0 / 1728 / isogenous equal those of generic curves and the null at every cell.**
  - LEAD-ICP-xline-symmetry-special-j → **closed_obstructed(proof)** for the folding and top-form arms, and **exhausted_at_scale** (toy, s ≤ 6) for the rank arm.
  - LEAD-STR-special-j-ic-semaev: first-fall arm → **closed_obstructed(proof)**; its charged-S arm continues as **open_next_step**.
  - LEAD-ICE-curve-presentation-invariance: only the first-fall / d_reg content of its mechanism text is settled by proof. Its frozen next step (EXP-DREG-dd668d: last-fall and grevlex solving degree on certified Vélu edges) is **not** pre-decided by C4. If that experiment and the fall-on-kernel meter both show no difference, the lead becomes **exhausted_at_scale** (toy).
- **Special j shows a strictly larger lower-weight fall rank (an earlier last fall) than generic curves and the null.**
  - **open_next_step** on LEAD-STR-special-j-ic-semaev, best_measured = (cell, degree, fall-rank excess).
  - Next: charged S against matched rho with the √|Aut| discount.
- **An isogenous pair differs in last-fall degree beyond the null.** **open_next_step** on LEAD-ICE-curve-presentation-invariance, with that edge as best_measured.

**Cost.**
- Implementation: 0.5–1 day (the derivation plus a kernel-restricted rank routine).
- Compute: minutes to hours at s ≤ 6.

**Self-kill risk.**
- (a) H-PFDR-4148b8 (D6) already asserts curve-independence conditional on H-TOP, and EV-PFDR-1394a4 measured it. The delta is:
  - the proof at all m;
  - the d_reg closed form;
  - the G_a reading;
  - the equivariance proof;
  - the transfer to the special-j, isogeny and model leads.
- (b) Only top-form invariants are decided. The solving degree, where the curve enters, is untouched, and the gain is 0.
- (c) Characteristic ≠ 2, 3 only. Binary descended systems (y² + xy = x³ + ax² + b) are not weighted-homogeneous under this action, so nothing transfers to B4/B5.
- (d) Normalisation: a different but nonzero-scalar normalisation of S_m changes the leading form by that scalar only.

**--match phrasings (top hits, run this session).**
- Own: "weighted homogeneity proves the leading form of the summation polynomial is a curve-free monomial so first fall degree is curve independent" → KR-IC-f5c584 (22), KR-IC-889857 (19), KR-IC-fbdb61 (19), LEAD-ICE-descent-closure-degree-at-scale (19), LEAD-ICP-digit-presentation-solving-degree (14).
- Plain: "prove the top-degree part of the Semaev polynomial does not depend on the curve or the target" → LEAD-STR-special-j-ic-semaev (9), KR-IC-5a43e5 (8).
- Obstruction vocabulary (nearest closed lead LEAD-EXO-curve-model-representation): "model-native PDP first fall degree and degree of regularity invariant across special j isogeny class and curve model; the lever is capped by a degree argument" → LEAD-ICE-curve-presentation-invariance (26), KR-IC-889857 (19), KR-RHO-755e35 (19).

---
## Killed candidates (self-kills, with reasons)

K1–K12 are carried over from the earlier draft (`ca2/prior-dossier.md`) and summarised here. K13–K19 are new in this session.

- **K1. Bézout / geometric-degree lower bound ("any Gröbner oracle pays about p solutions").** Invalid: with completely split membership, every geometric solution is rational. The cost lies in the solving degree, not the output degree.
- **K2. Positive-dimensional implicit factor bases with #W(F_p) ≈ p^{1/m}.** Lang–Weil (recalled) forces (d−1)(d−2) ≳ √p, and finding F_p-points needs x^p − x.
- **K3. Weil-reciprocity / Miller evaluation of the norm ∏_{ζ∈μ_B} G(ζ).** Θ̃(B) for m ≥ 2, which is enumeration.
- **K4. Bi–Cheng–Rojas sparse root detection (recalled).** Its exponent (t−2)/(t−1) tends to 1 at the support size t ~ 10^3.
- **K5. Symbolic powers / Rees valuations beyond Jochemsz–May.** (p, f_1..f_r) is a complete-intersection prime, so P^{(k)} = P^k (recalled). Nothing to add; advance LEAD-ICP-coppersmith-smallroot-semaev's own next step.
- **K6. Invariant theory for B6 (non-automorphism equivalence).**
  - Invariant degree d ≥ h/√|D|, which is vacuous on deployed curves.
  - **B6 is not covered by any surviving candidate**, nor is B7 (see empty fields).
- **K7. Multigraded Hilbert-series null for the chained-dreg deficit.** The support-restricted null already reaches semi-regular rank (EV-DREG-008), so the 17,947 deficit is coefficient-born. Folded into C3 as memory only.
- **K8. Multivariate Graeffe norm chain as an oracle.** The tower degree grows to m(m−1)k, worse than enumeration.
- **K9. Kronecker geometric resolution for the writability wall.** poly(L)·δ² with δ up to 2^{ml}.
- **K10. HKY / HKYY last-fall transfer to F_p towers.** It needs the n Frobenius-conjugate equations (O1).
- **K11. The S_3 degree-two "nonzero bridge".** Already a formalization task with a finite counterexample; not a discovery.
- **K12. Riemann–Roch / symmetric Graeffe presentation as a standalone lead.** Decided by C2 via L2-5.
- **K13 (new). Block-Wiedemann XL as the instrument for the memory-blocked cells.**
  - Duplicate of IDEA-20261018-1aff90 (proposed, unmapped).
  - A static Macaulay matrix gives plain XL only, which that record itself states is 2–3 degrees pessimistic. Its kernel vectors with nonzero constant coordinate are plain-XL pseudo-solutions, not duals of the degree-D closure.
  - Folded into C3 as the truncated closure's final consistency step.
- **K14 (new). Upper/lower sandwich of the digit solving degree via Semaev–Tenti (sd ≤ 2 d_reg − 2) or Caminata–Gorla (sd ≤ reg).**
  - The curve-free top-form d_reg is N − ⌊(s − 2^{m−1})/2⌋ (C4 Corollary R, checked at 7 cells). So the upper bound exceeds the trivial Boolean bound.
  - Thm 5.2 also assumes F_q field equations, not Boolean constraints over F_p.
  - No sandwich exists with C1's ⌈s/2⌉ + 1.
- **K15 (new). Group-algebra unit test for μ_B bases.**
  - A decomposition exists iff S_{m+1}(·, x_R) mod (x_i^B − 1) is a zero divisor of F_p[(Z/B)^m].
  - Deciding this needs the norm ∏_ζ S(ζ) or a size-B^m DFT, i.e. enumeration.
  - m = 1 is O(log B) (x^B mod f), the useless arity.
- **K16 (new). Counting decompositions mod p (Chevalley–Warning / Cartier operator / Fedder-type coefficient of S^{p−1}).**
  - N ≡ B^m − Σ_{x∈μ_B^m} S(x)^{p−1} (mod p) is exact, and N mod p = N because N is small at the balanced point. Halving μ_B cosets would turn decision into search.
  - But the μ_B-restricted sum is either the enumeration itself, or a point count on the cover S(y^e) = 0 with e = (p−1)/B and genus of order e². Every known point-counting method is at least polynomial in the genus, about p^{2−2/m} ≫ rho.
- **K17 (new). Treewidth / junction-tree degree bound for chained systems (path structure, width about s + 2).** Internal nodes are unrestricted F_p variables. Eliminating them is the resultant recursion, which rebuilds S_{m+1}. Boolean-CSP treewidth bounds do not apply.
- **K18 (new). Comprehensive Gröbner systems (Weispfenning 1992; Kapur–Sun–Wang 2010; recalled) over (a, b, x_R) to map every special locus.**
  - C4's weighted homogeneity reduces the parameter space to the weighted projective plane P(2, 4, 6) and decides the top-form part outright.
  - For the remainder, the fall-on-kernel meter is far cheaper than a CGS on digit systems.
- **K19 (new). Alekhnovich–Razborov expansion bounds to lift C1 from one free block to k free blocks (target degree about k·s/2).**
  - The chained system's equation–block incidence graph is a path with no expansion, and direct S_{m+1} is one non-local equation.
  - Not applicable. Open problem: a k-block knapsack PC bound would close C1's undecided chained rows m = 7, 8 and its open rows m ≥ 9.

## Fields searched but empty (with reasons)

- **Castelnuovo–Mumford regularity.**
  - sd ≤ reg(F^h) (Caminata–Gorla Thm 5.1) and d_reg ≤ reg (Thm 5.3) are upper bounds.
  - For the digit systems they are vacuous for a sub-rho claim; see K14 and C4 Corollary R.
- **Noether normalisation.**
  - No target-independent, product-preserving normalisation exists.
  - A target-dependent one destroys the fixed factor base that linear algebra needs (known-log pools, H-BINSTD-1447cf).
- **Border bases.** They change the normal set, not the ideal. PC degree is independent of order and normal set.
- **Resultant / subresultant / Dixon formulations.**
  - Subresultant pivot trees are foreclosed by LEAD-ICE-prime-field-semaev-solving-degree.
  - Dixon / Macaulay resultants inherit membership degree B per variable, or are PC-simulable (C1, C2).
  - The one new resultant fact is C4's isobaric recursion.
- **BKK / Newton polytopes.** There is no rational excess for split membership (K1), and mixed volumes are upper bounds. Multigraded structure is used constructively in C3.
- **Hilbert series of Semaev ideals.**
  - The top-form Hilbert series is curve-free (C4 Corollary B).
  - The support-restricted null is already at semi-regular rank (K7).
- **Solving / last-fall / first-fall / regularity degrees.**
  - First fall and d_reg are top-form invariants, decided by C4.
  - The last-fall / solving degree is the residual open object (C4 Corollary L). No theorem bounds it for F_p digit systems beyond C1's lower bound and vacuous upper bounds (K14).
- **B4 SAT-conflict pricing.** CDCL / resolution proof complexity is outside commutative algebra. Nothing beyond the lead's own calibration step.
- **B6 (rho step cost, equivalence classes beyond Aut(E), GPU/FPGA throughput) and B7 (Miller-cocycle transfer, Teske over F_{p^6}).** No commutative-algebra ingredient converts them. The B6 invariant-theory route is K6.
- **B3 (prime-field IC constant engineering).** The Table B m = 2 oracle is x(R ± P) membership after a point subtraction. That is arithmetic batching, not algebra, and nothing in this field changes its constant.

## Citations (provenance; "retrieved" means fetched or read in this session unless stated)

- **Impagliazzo, Pudlák, Sgall**, "Lower bounds for the polynomial calculus and the Groebner basis algorithm", Comput. Complexity 8 (1999) 127–144; ECCC TR97-042. Thm 4.1, Lemma 4.2, §5 (Lemma 5.1, Thm 5.2, Cor. 5.3–5.4, and the Gröbner simulation paragraph). **Retrieved** (PDF pp. 8–10 read this session).
- **R. M. Wilson**, "A diagonal form for the incidence matrices of t-subsets vs. k-subsets", Europ. J. Combin. 11 (1990) 609–615. **Retrieved via secondary sources only** (search-result statement of the diagonal form and p-rank; arXiv 1302.4249). The full text was not read.
- **I. Semaev**, "Summation polynomials and the discrete logarithm problem on elliptic curves", IACR ePrint 2004/031. **Retrieved** (abstract page). The resultant recursion is recalled; the PDF fetch returned 403.
- **A. Caminata, E. Gorla**, "Solving degree, last fall degree, and related invariants", ePrint 2021/1611 / JSC. **Retrieved** (abstract page this session). Def 1.3/1.4 and Thm 5.1–5.3 are quoted from the program's full-text note KN-LIT-4e8513.
- **J.-C. Faugère, M. Safey El Din, P.-J. Spaenlehauer**, "Gröbner bases of bihomogeneous ideals generated by polynomials of bidegree (1,1)", arXiv 1001.4004 (JSC 2011). **Retrieved** (abstract).
- **C. Petit, M. Kosters, A. Messeng**, "Algebraic approaches for the elliptic curve discrete logarithm problem over prime fields", PKC 2016, LNCS 9615, 3–18. **Retrieved** (bibliographic record and summary).
- **Recalled, not verified this session:**
  - Bardet–Faugère–Salvy (Boolean semi-regular series);
  - Semaev–Tenti, J. Algebra 2020 (as quoted in KN-LIT-4e8513);
  - Huang–Kosters–Yeo 2015; Bender–Faugère–Tsigaridas 2018;
  - Bi–Cheng–Rojas 2013; Lang–Weil / Cafure–Matera;
  - Hochster (symbolic powers); Giusti–Lecerf–Salvy 2001;
  - Weispfenning 1992; Kapur–Sun–Wang 2010; Alekhnovich–Razborov 2001;
  - Vélu 1971; Silverman AEC III.1; Cox–Little–O'Shea ch. 3.
- **Internal:**
  - H-PFDR-4148b8 (HEUR-001 H-TOP; D1–D7), EV-PFDR-1394a4, H-PFDR-df0127, H-PFDR-6b9f1a, H-PFDR-ebec07;
  - IDEA-20261018-1aff90, IDEA-20260816-a67f97, IDEA-20261018-e0857e;
  - H-PCD-03be5a, EV-SDEG-4a1c3d, EV-DREG-008, EV-ENDO-e8d3e5 (S_3 supports 13/9/10, reproduced in `ca2/leadform.out`);
  - KN-LIT-4e8513, KN-LIT-f37b9a, KN-LIT-0acb8c.

## Appendix: files produced or re-run this session (all under `scout/`)

| file | what it holds |
|:--|:--|
| `margins.py` / `margins.out` | earlier run's derivation; re-run this session, byte-identical (`ca2/margins.rerun.out`) |
| `ca2/prior-dossier.md` | earlier draft, unchanged copy |
| `ca2/leadform.py` / `.out` | Lemma W and H-TOP at m = 2, 3 (symbolic): weights 8 / 24, leading forms x1²x2² and x1⁴x2⁴x3⁴, cusp equality, supports 13/9/10 (S_3) and 439/191/225 (S_4) |
| `ca2/leadform_m4_numeric.py` / `.out` | H-TOP at m = 4 (λ-interpolation, two primes) and the G_a norm identity at 6 points |
| `ca2/leadform_m4.py` | symbolic S_5 attempt; superseded by the numeric check and stopped unfinished |
| `ca2/lambda_check.py` / `.out` | top-form d_ff and d_reg in Λ at 7 cells against both closed forms |
| `ca2/a1_check.py` / `.out` | A1 coefficient c(s,k) mod p for P-256 and secp256k1 at m = 5..10; brute-force cross-check at 4 small cells |
| `ca2/a2_check.py` / `.out` | A2 max-popcount coefficients at m = 2, 3 |
| `ca2/o3_check.out` | 2-adic valuations of p ± 1 for P-256 and secp256k1 |
| `ca2/match_runs.txt` | `tools/lead_atlas.py --match` output for all 12 phrasings |
| `ca2/src_ips/ips97.pdf` | ECCC TR97-042, the downloaded source PDF (data only) |
