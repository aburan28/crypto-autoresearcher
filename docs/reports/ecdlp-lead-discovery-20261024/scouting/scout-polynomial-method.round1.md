# Scout dossier: polynomial method and Combinatorial Nullstellensatz, aimed at B1-B7

Scout field: polynomial method (Alon's Combinatorial Nullstellensatz, Chevalley-Warning, Ax-Katz, Stepanov/Weil via
polynomials, Dvir Kakeya, slice rank, Croot-Lev-Pach, and polynomial-method algorithms), applied to whether
decompositions exist, how many there are, and lower bounds on membership and relation costs.
Date: 2026-10-24. Author: scout subagent (Opus). Status of every item: proposal. Nothing here changes research state.

Inputs read in full: ATLAS.md (all families), KRMAP.md, object-frame-ideation.md sections 1-3, idea-generator
"Search heuristics" and "Obstructions as generative material", target-result-profile.md part A, IC LEADERBOARD
tables A-C, FRONTIER.md (head). Lead YAML read directly: algebraic-membership, generic-table-decomposition,
generic-table-oracle (ICB), generic-sqrt, augmented-oracle-ggm, writability, decomposition-encoding-and-sat,
endo-scalar-action, representation-subset-sum, invertible-hint-subset, non-automorphism-equivalence,
charged-toy-ic-exponent-vs-rho, coincidence-harvest. Ledger records read for dedup: H-ECDLP-29f047,
H-ECDLP-a6d66b, H-PFDR-8a4f44, H-ECDLP-f6a43a, IDEA-20261003-cd1903, IDEA-20260928-4e2be7,
IDEA-20261002-3722ca, IDEA-20260808-0e9fa1, EV-SDEG-4a1c3d, EXP-ICEX-153c34/specification.yaml (G1 and O5).

Provenance legend: **retrieved** means the source text or abstract was read this session (URL given).
**recalled** means it was not read this session. **derived here** means an in-session derivation that nobody
has reviewed. Numbers marked PREDICTION were not measured. Numbers marked PILOT are my own toy runs
(scripts and outputs in `scout/pilot/`). They are preliminary, carry no review, and are not evidence records.

---------------------------------------------------------------------------------------------------------
## 0. One-paragraph summary

The polynomial method gives this program three useful things. All are cheap; two are closures.

**(C1)** Alon's CN Theorem 1.1 makes {g_A(x_i)} a degree-respecting basis of the grid ideal (retrieved). That
turns the approved heuristic HEUR-ICEX-6ca21f-1 ("G1 pays >= L^5") into a theorem for the static classes: the
quotient-basis linear algebra N2 covers, and dense Macaulay/XL. The binding quantity is |supp NF(1/f)| for
non-members and |supp NF(e/f)| for members.
- The pilot measured full support in 36 non-member cells and 15 of 16 member cells; the 16th is degenerate.
- So the per-success floor of those classes is about (m!/2^m)*q for every base size L, which is exponent 1.
- That equals the exhaustive exponent SO-TABLE already measured (0.99 / 1.01). C1 adds a proof, not a new
  number.
- G1 itself is lex Buchberger, a dynamic class. It is covered only conditionally: at the six v4 fixtures
  (L <= 11 < 16) the reduced input f-bar is predicted dense, so G1's input alone has about L^5 terms.
  Otherwise G1 waits on its smoke run.

**(C2)** Kelley's t-nomial root bound (2016, retrieved) says a high-precision sparse target test exists only if
the decomposable-target set x(A +- A) covers at least half of a large multiplicative coset. High precision here
means false positives < C_min/2. This is the "test sub-linear in |F|" of SO-TABLE's revisit_when. A
coset-coverage meter decides that sub-class; the pilot is at the null level. Tests with more false positives
are left open.

**(C3)** An elementary Bezout-on-translates bound gives |D_F| <= 1 + sqrt(8 d (M-1)) for any degree-d polynomial
agreeing with the discrete log. It needs no character sums and holds on anomalous curves too. It narrows the
M_deg window of LEAD-EXO-invertible-hint-subset from (1/2, 3/4] to (1/2, 2/3], and raises the regime-(ii)
floor from n^{1/4} to n^{1/3}. Anomalous curves give a free falsifier.

Everything aimed at binary and Koblitz curves (B4, B5) was killed with arithmetic (section 4). None of the
three live candidates is predicted to beat rho.

---------------------------------------------------------------------------------------------------------
## 1. Field scan (results considered; disposition)

| result (authors, year) | what it could do here | disposition |
|:--|:--|:--|
| Combinatorial Nullstellensatz Thm 1.1/1.2 (Alon, CPC 8, 1999) [retrieved: author PDF pp. 1-2] | grid ideal = <g_A(x_i)> with degree bounds, which pins static certificate size | **C1** (live) |
| Alon-Furedi zero counts on grids (1993) [recalled] | upper bounds on zeros only | killed K7 |
| Chevalley-Warning, Warning II, restricted-variable CW (Brink 2011; Clark-Forrow-Schmitt 2017) [recalled; CW as a consequence of CN noted in Alon p. 2, retrieved] | existence of decompositions from small degree | killed K3 |
| Ax-Katz p-adic divisibility (Ax 1964; Katz 1971) [recalled] | divisibility of decomposition counts | killed K4 |
| Fewnomial root structure: Bi-Cheng-Rojas (ISSAC 2013, arXiv 1204.1113) [retrieved abstract]; Kelley (arXiv 1602.00208, 2016) [retrieved abstract]; Kelley-Owen (arXiv 1510.01758) [retrieved via search snippet] | a sparse target test forces coset structure in the sumset | **C2** (live); BCR detection as an oracle is killed (K2) |
| Polynomial interpolation of ECDL (Lange-Winterhof, COCOON 2002) [existence retrieved, TU/e abstract; bound recalled]; Coppersmith-Shparlinski (J. Cryptology 2000) [recalled] | degree versus agreement with the log, Bezout on translates | **C3** (live; derived here, technique lineage recalled) |
| Stepanov method: Heath-Brown-Konyagin (2000); Corvaja-Zannier (2013); Shkredov-Vyugin (2012) [recalled] | caps on subgroup-coset coincidences below sqrt(p) | killed K8 (vacuous in IC regime) |
| Determinant method: Bombieri-Pila (1989); Heath-Brown (2002); Salberger; Walsh (2015) [recalled] | small-box point counts and enumeration | killed K9 (dominated: Coppersmith lead, IDEA-20260808-0e9fa1) |
| Croot-Lev-Pach (2017), Ellenberg-Gijswijt (2017), slice rank (Tao 2016) [recalled] | compression of the decomposition tensor | killed K5 |
| Dvir Kakeya (2009); method of multiplicities (Dvir-Kopparty-Saraf-Sudan 2009) [recalled] | none: no high-dimensional line structure | empty (K6) |
| GF(2) parity-counting solvers (Bjorklund-Kaski-Williams ICALP 2019; Dinur EUROCRYPT 2021) [recalled] | unconditional exponent for the descended Boolean PDP (B4) | killed K1 |
| PC size-degree (Impagliazzo-Pudlak-Sgall 1999); design lower bounds (Razborov 1998; Buss-Grigoriev-Impagliazzo-Pitassi 1999) [recalled] | PC size from degree on the Boolean digit encoding | killed K10 (too weak to decide); kept as a remark in C1 |
| Polynomial-method incidences (Guth-Katz; Rudnev; Stevens-de Zeeuw) [recalled] | m = 2 join as point-line incidence | killed K11 |

---------------------------------------------------------------------------------------------------------
## 2. Standing obstructions quoted (statement, scope clause included)

- **SO-TABLE** (LEAD-ICP-generic-table-decomposition, theorem):
  "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory
  trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); ... Scope: any generic
  (enumeration/table) decomposition over F_p."
  revisit_when: "A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity
  m = 4 (an S_5 oracle at B ~ p^{1/5}), or a decomposition test sub-linear in |F|."
- **SO-ALGFB** (LEAD-ICP-algebraic-membership-factor-base, theorem):
  "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has
  description degree >= B/3 and membership polynomial prod(x - v) of degree B ...; mean per-target yield is
  binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in
  N). ... msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
- **SO-GEN** (LEAD-RHO-generic-sqrt-lower-bound, theorem): "Shoup/Nechaev generic-group lower bound: any generic
  algorithm needs Omega(sqrt r) group operations for a prime-order-r group ... Scope: all generic algorithms,
  any field, any r."; LEAD-EXO-augmented-oracle-ggm: "Each named oracle is GGM-simulable ... Scope: oracles, not
  resources."
- **SO-ENDO** (LEAD-STR-endo-scalar-action-generic): "For G of prime order N, End(G) = Z/N, so every
  endomorphism-image oracle is simulable by group operations and Shoup's bound applies ... Scope: any prime-field
  or binary curve, any size, prime-order subgroup."
- **SO-PAIR** (LEAD-TRF-second-torsion-direction): "Balasubramanian-Koblitz: for N || #E(F_p), N != p,
  E(F_{p^k})[N] is larger than the rational line iff N | p^k - 1 ... Scope: ordinary and supersingular curves
  over F_p, prime N."
- **B2 measured obstruction** (EV-SDEG-4a1c3d, scope clause): "... Nothing here is claimed at other m, factor-base
  sizes, extension fields, for non-enumerative (Groebner/algebraic) decomposition solvers, or at cryptographic
  size." Its obstruction quantity is "eliminant degree / ((4/3)|V|^3), and beta_elim". The resource_check reads:
  "The open class left by the data is non-enumerative algebraic decomposition (EXP-ICEX-fa2b37, Groebner)."
- **B4** (LEAD-ICB-decomposition-encoding-and-sat, measured): "Every SAT or enumeration method measured has
  per-attempt UNSAT cost 2^{alpha l} with alpha ~ m ..., while beating rho needs alpha < m/2 - 1".
- Object-frame constraints applied throughout: a new arithmetic is a (representation, operation set) PAIR. On a
  prime-order group, translation-propagating projections are constant or injective. Bounded-degree algebraic
  bases are scoped out (KN-OPEN-020); the open class is high-degree, implicit-membership, or target-dependent.

---------------------------------------------------------------------------------------------------------
## 3. Live candidates

### C1. Grid-Nullstellensatz normal-form floor ("GNF meter") for Groebner-class decomposition oracles over univariately presented factor bases

**Bottlenecks:** B2. This is the open non-enumerative class left by EV-SDEG-4a1c3d's scope. It also bears on B1:
the approved but unbuilt oracle G1 of EXP-ICEX-153c34 (LEAD-ICE-charged-toy-ic-exponent-vs-rho, open_blocked).

**External ingredient:** N. Alon, "Combinatorial Nullstellensatz", Combin. Probab. Comput. 8 (1999) 7-29,
**Theorem 1.1**. Let S_1, ..., S_n be nonempty, g_i(x_i) = prod_{s in S_i}(x_i - s), and suppose f vanishes on
all common zeros. Then f = sum h_i g_i with deg(h_i) <= deg(f) - deg(g_i). Provenance: **retrieved**
(author PDF, https://web.math.princeton.edu/~nalon/PDFS/null2.pdf, pages 1-2 read).

**Setup.** A a subset of F_p, |A| = L, J = <g_A(x_1), ..., g_A(x_m)>. This is exactly G1's ideal
I_R = <f6(x1..x5, x_R), g_V(x1), ..., g_V(x5)> (EXP-ICEX-153c34 backend, D-2: G1 "works in the quotient ring
R5 = F_p[x1..x5]/<g_V(x_i)> in the MONOMIAL basis"). For a non-decomposable target, f = f_R has no zero on A^m.
Let mu* = NF_J(1/f) be the unique polynomial with every deg_{x_i} < L that equals 1/f on A^m.

**Lemmas (derived here, unreviewed):**
- **N1 (exact static degree).** Theorem 1.1 implies that division by {g_A(x_i)} never raises degree (graded
  order). So every certificate 1 = mu f + sum lambda_i g_A(x_i) has NF_J(mu) = mu*, deg mu >= deg mu*, and the
  minimum Nullstellensatz degree is exactly deg f + deg mu*. The lambda_i stay within degree by Thm 1.1.
  A degree floor comes for free: mu f - 1 is a nonzero element of J. Lemma 2.1 of Alon forces some
  x_i-degree >= L, hence deg mu* >= L - deg f.
- **N2 (quotient-basis linear algebra).** Multiplication by f is invertible on R_m = F_p[x]/J. Take the rows
  {x^a * f mod J} for the L^m standard monomials x^a, every exponent below L. The coefficient vector expressing
  1 in those rows is unique and equals mu*, so any refutation by linear algebra in the quotient basis needs at
  least |supp mu*| rows. SCOPE: only standard-monomial multiples. Once higher-degree multiples are allowed the
  rows become dependent, so sparse F4 is NOT covered by N2; it is in R1.
- **N3 (sparse presentations).** For A = mu_k (g = x^k - 1), monomials are characters of (Z/k)^m. Folding
  exponents mod k cannot create support, so every certificate, reduced or not, has |supp mu| >= |supp mu*|,
  the Fourier support of 1/f.
- **N4 (dense Macaulay).** The axiom degree forces D >= L, and the degree-D Macaulay matrix in m variables
  has >= C(L+m, m) >= L^m/m! columns. This covers dense Macaulay/XL by column count.
- **N5 (member targets; derived here).** If R decomposes, the zero set Z of f on A^m is nonempty. Take the
  certificate of the eliminant e(x_m) = prod_{v in proj_m Z}(x_m - v), i.e. that e lies in <f> + J. Its
  cofactor h must satisfy h*f = e on A^m. So h is forced (= e/f) at the L^m - |Z| non-zeros and free on Z, and
  the minimal support is >= L^m - |Z| whenever the L^m delta functions are in general position. Finding a
  decomposition therefore costs as much as refuting one, and the (1-y) factor disappears.

**Assembly (cost per success).** O5's yield is y = |S_m|/q ~ 2^m L^m/(m! q). By N2/N4 for non-members and N5
for members, every attempt in the static classes costs at least s*L^m, where s is the measured support
fraction. So the cost per success is at least s*L^m/y = s*(m!/2^m)*q, and **L cancels**: the floor holds for
every base size. For m = 5 it is 3.75*q*s. Without N5 the floor would carry a factor (1-y), and it would hold
only when y << 1.

**Relation to existing records.** This exponent (1) is the exhaustive exponent SO-TABLE already measured
("exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3)"). The approved heuristic HEUR-ICEX-6ca21f-1
(H-ICEX-6ca21f) already predicts it for G1 by the random-interpolant argument, explicitly "not a lower bound for
algorithms that skip the certificate". C1's contribution is the theorem (CN Thm 1.1 plus N1-N5) for the static
classes, the member-target extension (N5), the measured support on real Semaev f, and the explicit R1 counterexample.
That counterexample shows why the heuristic cannot hold as a theorem for dynamic algorithms on sparse
presentations.

**What this covers and what it does not.** The floor covers every univariately presented grid (interval,
random-x, subgroup, coset, Dickson images), but only for the static classes: NS, quotient-basis linear algebra
(N2), and dense Macaulay/XL (N4). It does NOT cover three residual classes:
- (R1) dynamic derivations that multiply derived elements by monomials and recombine (Buchberger/PC). Example:
  for A = mu_k, m = 1 and f = x - c, PC derives x^{2^j} - c^{2^j} in log k binomial lines. That is
  exponentially below |supp mu*| = k. Sparse F4 and lex Buchberger are here, **and G1 is lex Buchberger**.
- (R2) non-product (implicit or target-dependent) descriptions.
- (R3) presentations that adjoin variables (digits, chained S_3).

**Pair and trichotomy.** Representation R1: abscissas as elements of the quotient ring R_m in the monomial
basis. Operation set: R_m-module operations (monomial multiplication, F_p-linear combination), plus translation
by factor-base elements for the relation vector. Class: **partial-action** (IC is Class I). The meter prices the
decomposition event's refutation size.

**SO codes:**
- SO-TABLE: premise "oracle that enumerates or table-looks-up factor-base elements". G1 does neither, so the
  premise does not apply. C1 supplies the missing non-generic floor, i.e. it EXTENDS the closure rather than
  escaping it.
- SO-ALGFB: premise "mean per-target yield is binomial(B+m-1, m)/N for every base of size B". Not escaped:
  the yield is unchanged and C1 prices only the per-attempt cost. The degree-B membership is the case C1
  covers.
- SO-GEN: premise "any generic algorithm". G1 reads coordinates, so it is not generic. C1 gives its floor.

**Tier:** X (exponent decision for a class).

**Predicted gain, as a decision.**
- **H1** (numbered heuristic): for Semaev f_R and every univariately presented grid, s >= 0.99 at all sizes.
  The PILOT supports it at toy scale.
- Under H1, the static classes cost >= (m!/2^m)*0.99*q per success: exponent 1.0 against rho's 0.5.
- For G1 itself (lex Buchberger, class R1) this is a PREDICTION, conditional on the smoke run.
- A conditional sharpening at the six v4 fixtures: there L in {3, 5, 6, 7, 11, 5}, all below 16, the
  per-variable degree of S_6. So reduction mod g_V folds f6, and f-bar is predicted nearly dense in R5. If
  |supp f-bar| ~ L^5 is measured, G1 pays >= L^5 just to hold its per-query input, whatever Buchberger does.
  That would make HEUR-ICEX-6ca21f-1 hold at those fixtures. This argument does not carry to large L.
- **H1b:** for dense presentations (interval, random-x), no repeated-squaring chain exists because g_A is
  dense. So G1's Buchberger units grow at least like L^m*c (PREDICTION). SO-ALGFB's measured "msolve on subgroup
  bases grows deg^{4.4} at m = 3" (deg^{4.4} > L^3) points the same way, even on a sparse presentation where R1
  shortcuts could exist in principle.

**PILOT (mine; toy; `scout/pilot/grid_ns_support.py`, `controls.py`):**
- 36 cells: p in {10007, 20011}; m in {2, 3}; |A| in {2..32} (m = 2) and {6..12} (m = 3); bases interval,
  random-x and full subgroup mu_k; 4 non-decomposable targets per cell.
- Support fraction 1.0000 and degree fraction deg mu*/(m(L-1)) = 1.000 in **every** cell.
- Planted controls: f = x1 on interval |A| = 30 gives 0.0333 (predicted 1/30). f = x1*x2 on mu_10 gives 0.0100
  (predicted 1/100). f = x1 + x2 + 7 gives 1.0. The meter detects sparsity when it is present.
- Caveat: at p = 10007 the subgroup cell had |A| = 2 only (p - 1 = 2*5003).
- Member targets (`member_targets.py`): 16 cells, p in {20011, 40009}, m in {2, 3}, L in {8, 12, 16, 32},
  interval and random bases, 4 member targets each, |Z| = 1-22. In 15 of 16 cells min supp(h_0)/L^m is
  0.9988-1.0000, at or above the generic floor (L^m - |Z|)/L^m.
- The 16th cell (p = 20011, m = 3, interval, L = 8) has one target with |Z| = 22 whose projection covered all
  of A, so e is in J and the certificate is trivial (support 0). That is a tiny-L degeneracy: N5's floor needs
  |proj Z| < L.

**First discriminating step (about 1-2 days implementation, CPU minutes to hours):**
1. Extend the pilot to m = 4 (S_5 by numeric resultants). Bases: interval, random-x, subgroup, coset, Dickson
   D_k(u, a). L up to 64/16/8 for m = 2/3/4; 3 primes 2^14-2^24; >= 32 non-member targets per cell. Keep the
   planted sparse-inverse controls.
2. Measure |supp f-bar| (f6 reduced mod g_V) on the six v4 fixtures, the conditional sharpening above.
3. Run EXP-ICEX-153c34's S0 smoke of G1 on 3 sizes. Record per-query units against |supp mu*| and
   |supp f-bar| on the same targets; this is the R1 arm.

**Outcome to disposition:**
- s >= 0.99 everywhere: **closed_obstructed(theorem)** for the static classes over univariate grids, whatever
  G1 does.
- If also G1 units >= c*|supp mu*| (or |supp f-bar| ~ L^5 at the v4 fixtures): the G1 arm of
  LEAD-ICE-charged-toy-ic-exponent-vs-rho becomes **closed_obstructed(cost_model)**, with predicted exponent 1.
  Recommendation: do not build G1 beyond the smoke test.
- s >= 0.99 but G1 units << |supp mu*|: R1 is real, so **open_next_step**, best_measured = G1 unit slope in
  log L. That slope is then the number to fit against the p^{1/4} gate.
- Some family with s(L) ~ L^{-gamma}, gamma > 0: **open_next_step**, best_measured = gamma. The predicted
  per-success exponent is 1 - gamma*beta (L = q^beta). Sub-rho requires gamma*beta > 1/2.
- A planted control missed: instrument void.

**Nearest priors and differentiation:**
- HEUR-ICEX-6ca21f-1 (approved heuristic) is the same floor, stated as a random-interpolant heuristic. C1 proves
  the static part, adds members (N5), measures s on real Semaev f, and isolates R1.
- H-ECDLP-29f047 (proposed) measures PC *degree*, encoding by encoding, against a matched-random null. C1
  differs in three ways. It gives the *exact* static degree in closed form (N1). It states the binding
  quantity as *support size*, not degree, which is what costs work. It prices G1 per success with L cancelling.
- LEAD-ICE-prime-field-semaev-solving-degree's EV-SDEG-4a1c3d covers the enumerative serial-split backend only,
  by its own scope clause.

**Self-kill risk:** medium. The theorem covers only the static classes. G1 (lex Buchberger) is R1, and an R1
shortcut would leave G1 open. The exponent it closes at is the one SO-TABLE already measured, so the
candidate's yield is a closure of a class, not a gain.

**Matches** (`tools/lead_atlas.py`, `tools/build_frontier_map.py`; full output in
`scout/match-polynomial-method.txt`). Nearest are LEAD-ICE-rootfind-pairtable-oracle,
LEAD-ICP-construction-normal-form, LEAD-ICP-algebraic-membership-factor-base and
LEAD-ICE-prime-field-semaev-solving-degree. KR rows: KR-IC-f3da82, KR-IC-73db3f, KR-IC-5931ee. No row forecloses
"support of NF(1/f) on the grid" or "per-success floor independent of L".

### C2. Sparse decomposable-target tests: fewnomial root structure forces multiplicative-coset structure in x(A +- ... +- A)

**Bottlenecks:** B1 ("a decomposition test sub-linear in |F|", SO-TABLE revisit_when), and B3 as a consequence.
If a test existed, Table B's m = 2..4 pipeline would change exponent.

**External ingredients:**
- **Kelley**, "Roots of sparse polynomials over a finite field" (arXiv 1602.00208, 2016). Quoted: "the number
  of distinct, nonzero roots of f is bounded above by 2 (q-1)^{1-ε} C^ε, where ε = 1/(t-1) and C is the size of
  the largest coset in F_q^* on which f vanishes completely." Provenance: **retrieved** (abstract).
- **Bi-Cheng-Rojas** (arXiv 1204.1113, ISSAC 2013). The nonzero roots of a t-nomial partition into few cosets
  of two nested subgroups S_1 <= S_2 <= F_q^*. **retrieved** (abstract). Rendering caveat: the fetched text
  printed the exponents as "(t-2)(t-1)"; the paper's title ("sub-linear") implies (t-2)/(t-1), and I use that
  reading.

**Mechanism.** A target test is a polynomial f in F_p[X] with Z(f) approximately equal to
Sigma_m(A) = {x(+-P_1 +- ... +- P_m)}, evaluated at x(R) at cost O(t log p) when f is a t-nomial. This is the
cheapest high-degree class, which KN-OPEN-020's open class allows.
- Let |Z(f)| = p^{mu}. Kelley then forces a full coset of size C >= p^{1-(1-mu)(t-1)}/2^{t-1} inside Z(f).
- Kelley guarantees the coset inside Z(f), not inside S = x(Sigma_m(A)), and C_min is far smaller than |S|
  (about p^{0.6} against p^{0.8} at balanced m = 4). So a test with up to |S| false positives could have an
  all-false-positive coset. Hence the closure is scoped to the **high-precision sub-class H2'**: false
  positives fewer than C_min/2. Under H2', S covers at least half of a coset of size >= C_min.
- Tests with false positives between C_min/2 and about |S| are **residual** (not closed). The Bi-Cheng-Rojas
  containment form (all roots lie in few cosets, so S concentrates in few cosets) would cover them. Its exact
  statement was not retrieved (rendering caveat), so it stays a note.
- Example: m = 4 with balanced A (|A| = p^{1/5}, mu ~ 0.8) at t = 3 needs C >= p^{0.6}/4. The constraint is
  non-vacuous for t < 1 + 1/(1-mu) (t <= 5 at mu = 0.8).
- Composed sparse forms g(x^k) and Dickson-type maps are pulled back the same way, giving unions of cosets and
  their images.

**Pair and trichotomy.** Representation R1: x(R) in F_p. Operation set: power maps x -> x^e plus F_p-linear
combination, i.e. sparse evaluation; it never uses translation. Class: **coordinate-dependent** (the test is a
function of the representation of R). IC remains Class I around it.

**SO codes:**
- SO-TABLE: premise "enumerates or table-looks-up factor-base elements". **Escaped**: one polynomial evaluation
  at x(R), with no enumeration and no lookup. This is the revisit_when's "test sub-linear in |F|".
- SO-GEN / augmented-oracle-GGM: premise "GGM-simulable". **Escaped**: the test reads field coordinates.
- SO-ALGFB: premise "mean per-target yield is binomial(B+m-1, m)/N for every base of size B". **Not escaped**:
  the yield is conserved. C2 moves only the per-attempt cost. Its high-degree object sits on the TARGET side
  (the sumset), not the base side, which is a transport of KN-OPEN-020's "high-degree" class.

**Tier:** X.

**Predicted gain (conditional, low prior):**
- **H3**: a test with t <= 5 and high precision (H2') exists for some A at balanced m = 4.
- **H4**: a nested coset chain gives search-to-decision in O(log L) tests.
- Under H3 and H4, the IC exponent becomes the free-oracle value 2/(m+1) = 0.40 at m = 4, against rho 0.50.
  This is a PREDICTION. The prior for H3 is very low: the coordinate-statistic census found "every stable
  multiplicative coset statistic sits at the random level" (EV-ECDLP-81f4d4).

**PILOT (mine; toy; `scout/pilot/coset_coverage.py`):**
- Setup: p = 1048681; bases subgroup mu_k, interval, random, with k in {216, 270}; |S| = 9.2k-20.5k
  (mu ~ 0.66-0.72); Kelley t = 3 gives C_min = 20-100.
- For every D | p-1 with D >= C_min/4, max coset coverage minus the max over 5 random nulls is <= +0.04,
  except a single-count +0.10 at D = 10.
- Max coverage at any D <= 0.40, all at D <= 27. No coset near full coverage. Null level throughout, with 5
  nulls only.

**First discriminating step (about 1 day; hours CPU):**
- Ladder p in {2^20, 2^24, 2^28}; |A| chosen so mu in {0.6, 0.7, 0.8}.
- Bases: subgroup, coset, Dickson images, interval, random. Sigma_2, plus Sigma_3 by an uncharged MITM at the
  small rungs.
- Measure coset coverage for every D | p-1 with D >= C_min(t)/4, t in {3, 4, 5}, against >= 100 equal-size
  random nulls. Repeat on Dickson pullbacks (u -> u + a/u).
- Planted positive: a union of cosets of mu_D plus noise, which must be detected.

**Outcome to disposition:**
- No coset of size >= C_min(t) with coverage >= 1/2 at any rung, and null-level coverage elsewhere:
  **closed_obstructed(theorem, scoped)** for high-precision (H2': false positives < C_min/2) t-nomial and
  composed-sparse target tests with t < 1 + 1/(1-mu). The residuals are low-precision sparse tests (false
  positives up to |S|) and general short-SLP tests.
- Coverage excess growing with p: **open_next_step**, best_measured = coverage excess. Build the t-nomial test
  and price it end to end against matched rho.
- Planted positive missed: void.

**Nearest priors and differentiation:**
- IDEA-20260928-4e2be7 makes coset and Dickson BASES cheap to test for membership: "membership tests costing
  O(log d)". That is the base side.
- IDEA-20261002-3722ca models subgroup-base attempt cost B^theta.
- Neither asks for a sparse test of the SUMSET, and neither uses Kelley or Bi-Cheng-Rojas. The ledger has no
  hits for "fewnomial", "Kelley" or "Rojas".

**Self-kill risk:** high. The theorem only bites for t < 1 + 1/(1-mu) and only for the high-precision sub-class
H2'. Low-precision sparse tests and general short-SLP tests stay open, and the prior for a positive outcome is
close to zero. The value is mostly a scoped closure.

**Matches** (output in `scout/match-polynomial-method.txt`): nearest leads LEAD-ICP-algebraic-membership-factor-base,
LEAD-ICE-rootfind-pairtable-oracle, LEAD-ICB-prime-degree-algebraic-decomposition,
LEAD-ICP-generic-table-decomposition, LEAD-ICB-frobenius-search-symmetry. KR rows: KR-IC-955fd6, KR-IC-5931ee,
KR-IC-f5c584, KR-IC-46d822. No row forecloses "sparse polynomial test of the decomposable-target sumset" or a
Kelley-type coset argument.

### C3. Bezout-on-translates (BTL) agreement bound: |D_F| <= 1 + sqrt(8 d (M-1)) for any degree-d polynomial agreeing with the discrete log

**Bottleneck:** this is not B1-B3, and I do **not** count it toward the prime-field B1-B3 minimum. It decides
part of LEAD-EXO-invertible-hint-subset (open_next_step). That lead is the "invertible half", dual to B1's
recognizable factor-base membership. It also has degree-charged corollaries for B6
(LEAD-RHO-non-automorphism-equivalence) and B7 (LEAD-TRF-miller-cocycle-nonhom-transfer).

**Theorem (derived here, unreviewed).**
- Setting: E/F_p, n = #E(F_p) prime, G a generator, M = min(n, p). The proof never uses n != p, so the bound
  also holds on anomalous curves (n = p). F in F_p[X] nonconstant
  of degree d. D_F = {Q != O : iota_p(F(x(Q))) = iota_n(log_G Q)}, the definition in H-ECDLP-f6a43a.
- Statement: |D_F| <= 1 + sqrt(8 d (M-1)). For F in F_p[X, Y] of total degree d it is
  |D_F| <= 1 + sqrt(12 d (M-1)).
- Proof (5 lines):
  1. K = {log Q : Q in D_F} lies in [1, M).
  2. For k1 < k2 in K with integer difference j in [1, M-1], P = k1*G is a zero of
     Phi_j = F∘x∘tau_{jG} - F∘x - j. The integer lifts are equal, so no wrap-around arises.
  3. F∘x has its only pole at O, of order 2d. F∘x∘tau_{jG} has its only pole at -jG != O, of order 2d. So Phi_j
     is nonconstant with exactly 4d poles, hence at most 4d zeros.
  4. Hence r(j) = #{k in K : k + j in K} <= 4d and |K|(|K|-1)/2 = sum_j r(j) <= 4d(M-1).
  5. The (x, y) case uses pole order 3d.
- The advisor's variant (H*(H+n) with 8d poles) gives the same constant.

**Lineage:** degree lower bounds for polynomials interpolating ECDL exist in Lange and Winterhof,
"Polynomial interpolation of the elliptic curve and XTR discrete logarithm", COCOON 2002, LNCS 2387, 137-143.
Their existence is **retrieved** (TU/e portal abstract,
https://research.tue.nl/en/publications/polynomial-interpolation-of-the-elliptic-curve-and-xtr-discrete-l/).
Their exact bound and method were **not** retrievable, so the lineage is **recalled**. C3 may be an adaptation
of a known bound; the application to the window is the new part.

**Consequences for IDEA-20261003-cd1903 / H-ECDLP-f6a43a (Theorem W was N(F) <= 2 + K_d sqrt(p)(1 + ln(pn)),
with K_d from a RECALLED Kohel-Shparlinski bound for d >= 2):**
- (i) Regime (i), total omega with polylog degree: alpha <= 1/2 + o(1) **unconditionally**. This removes the
  d >= 2 retrieval obligation and the (1 + ln pn) loss. In M_deg (Horner-charged), total-omega HINTWALK costs
  T >= (n/|D|)*d >= sqrt(n d/8).
- (ii) Regime (ii), promised input with budget d <= n^{1-alpha}: s n^alpha <= 1 + sqrt(8 n^{2-alpha}) excludes
  **alpha > 2/3** (Theorem W excluded alpha > 3/4). The open window shrinks from (1/2, 3/4] to **(1/2, 2/3]**.
  Equivalently, T >= s sqrt(n/(8d)) + d >= c*n^{1/3}. The M_deg floor rises from n^{1/4} to n^{1/3}.
- The n^{1/3} target (alpha = 2/3, d = n^{1/3}) sits **exactly on the boundary**, with |D_F| <= 2.83 n^{2/3}.
  The constant, or the census E-RANDOM outcome, decides it.

**Corollaries (degree-charged only; do not close the leads):**
- **B6:** an H-invariant psi of pole order delta for H <= (Z/N)^*, with every lambda = a/b in H, satisfies
  delta (a^2 + b^2) >= N - 1. Pigeonhole gives some lambda with |a|, |b| <= N/h + 1, hence
  delta >= ~h^2/(2N) (rigorous). Lattice minima heuristically give delta ~ h. Straight-line cost is only
  >= log delta, so the charged gain sqrt(h)/log h can still exceed 1. This does NOT close the lead. It tells
  the N < 2^20 exhaustive search to look at high-degree, low-SLP invariants.
- **B7:** for Phi of pole order delta and fixed zeta, #{k : Phi(kG) = zeta^k} <= 1 + 2 sqrt(delta (n-1)).
  Phi∘tau_{jG} = zeta^j Phi identically would force delta >= n. Miller functions have pole order about n, so
  BTL is vacuous for the Miller-cocycle U. This names that lead's live object exactly: the high-degree,
  low-SLP class.

**Pair and trichotomy:** representation R1 (x and its integer lift). Operation set: degree-<=d polynomial
evaluation (M_deg). Class: **coordinate-dependent** (Class III, as IDEA-20261003-cd1903 places it).

**SO codes:**
- SO-GEN: premise "any generic algorithm". Hint families read coordinates. BTL is the non-generic floor in
  M_deg.
- SO-ENDO (B6 corollary): premise "every endomorphism-image oracle is simulable". A non-automorphism lambda is
  not an endomorphism of E, so BTL addresses what SO-ENDO leaves.
- SO-PAIR (B7 corollary): premise "E(F_{p^k})[N] larger than the rational line iff N | p^k - 1" covers
  homomorphic transfers. BTL covers non-homomorphic low-degree ones.

**Tier:** X (model-level exponent: the regime-(ii) floor moves from n^{1/4} to n^{1/3}).

**First discriminating step (hours; nearly zero new compute):**
- Falsifier first. On anomalous curves, BTL predicts that any (x, y) interpolant of the FULL log
  (|K| = n - 1) has total degree >= (n-2)^2/(12(n-1)), about n/12. For x-only F it predicts >= (n-2)^2/(8(n-1)).
  H-ECDLP-f6a43a's Stage 2 already computes the anomalous interpolation degree by exact Lagrange. A measured
  degree below the bound voids C3.
- Write the BTL proof as the Stage-0 replacement for Theorem W's d >= 2 retrieval obligation.
- Add the audit max |D_F| / (1 + sqrt(8 d (M-1))) <= 1 to the approved H-ECDLP-f6a43a Stage-1 census on its
  A(1) and A(2) cells.
- Retrieve the Lange-Winterhof full text to settle novelty.

**Outcome to disposition:**
- Proof checks and audit holds: the lead stays **open_next_step**. The window is recorded as (1/2, 2/3], and the
  decision target narrows to A(n^{1/3}) on D_x(n^{2/3}) at the constant level. If E-RANDOM also holds:
  **closed_obstructed(theorem + measured)** for M_deg.
- Lange-Winterhof already contains BTL: **closed_known** (adaptation; cite).
- Audit violated: derivation error, C3 void.

**Self-kill risk:** novelty (likely a known technique). It covers only M_deg, and it is not a named
bottleneck.

**Matches** (output in `scout/match-polynomial-method.txt`): top lead LEAD-EXO-invertible-hint-subset (score 65
on the forecloses vocabulary), then LEAD-EXO-dl-character-sum-pseudorandom, LEAD-RHO-lhw-polymem-collision-walks.
KR rows: KR-RHO-46c2c6, KR-RHO-ea34b8, KR-RHO-13bf67. The closed-lead phrasing (augmented-oracle-ggm /
dl-character-sum vocabulary) returns LEAD-EXO-dl-character-sum-pseudorandom first. No KR row forecloses a
degree-agreement bound.

---------------------------------------------------------------------------------------------------------
## 4. Killed candidates (own kills, with arithmetic)

- **K1. GF(2) polynomial-method solvers (Bjorklund-Kaski-Williams ICALP 2019; Dinur EUROCRYPT 2021, recalled)
  on the descended Boolean PDP (B4/B5).**
  - The system has >= m*l unknown bits. A solver at 2^{cN} gives alpha = c*m bits per unit l.
  - Beating rho needs alpha < m/2 - 1, i.e. c < 1/2 - 1/m.
  - Known c >= 0.6943 (quadratic, recalled; H-ECDLP-a6d66b flags it never-read). The degree-d bound is
    1 - 1/(2.7d) >= 0.81. Dead at every m.
  - Chained S_3 adds (m-2)n intermediate bits. At ECC2K-130, m = 4: N = 262 + 132 = 394, giving
    2^{0.69*394} = 2^{273} against 2^{60.9}.
- **K2. Bi-Cheng-Rojas sparse-root DETECTION as the per-query oracle.** It costs 2^{O(t)} q^{(t-2)/(t-1)+o(1)}
  (retrieved; exponent reading as noted). At t = 3 that is >= p^{1/2} per query, above the p^{1/4} per-attempt
  gate. Dead. The structure theorem survives into C2.
- **K3. Chevalley-Warning / Warning II / restricted-variable CW (Brink; Clark-Forrow-Schmitt) for existence of
  decompositions over F_p.**
  - With x_i in A the condition (p-1)*deg f < sum(|A_i| - 1) fails by a factor of about p/(mL).
  - Over unrestricted F_p^m it holds trivially but says only "number of zeros is 0 mod p" about zeros that are
    plentiful.
  - Dead.
- **K4. Ax-Katz divisibility of decomposition counts.** It needs #vars - sum deg > 0. For the m-variate Semaev
  hypersurface, m - (total degree) <= 0, so it is vacuous. Dead.
- **K5. Croot-Lev-Pach / slice rank / cap-set compression of the decomposition tensor.**
  - The addition tensor of the prime cyclic Z/N has slice rank N.
  - On binary curves the descended indicator prod(1 + f_j) has degree >= 2n. A nontrivial slice-rank bound
    needs degree < about 3l/2 < n. Dead.
- **K6. Dvir Kakeya / method of multiplicities.** It needs F_q^n with n -> infinity and lines in every
  direction. Neither Z/N nor the x-line carries a Kakeya structure. Empty.
- **K7. CN Theorem 1.2 / Alon-Furedi to prove EXISTENCE of decompositions.**
  - CN proves non-vanishing. Existence via 1 - f^{p-1} needs |A| > (p-1) deg f/m.
  - Alon-Furedi gives zero upper bounds only.
  - Dead. CN survives as the normal-form tool in C1.
- **K8. Stepanov caps (Heath-Brown-Konyagin; Corvaja-Zannier; Shkredov-Vyugin, recalled) on subgroup and coset
  coincidences.**
  - The cap is about |H|^{5/3} relations against a random expectation of |H|^3/p, a ratio of
    p^{1 - 4 beta/3}. That is >= p^{2/3} at beta = 1/4: vacuous.
  - The coincidence-harvest lead's FAM-1 geometries (label-GAP, window, log-GAP) contain no subgroup base.
    Decides nothing. Dead.
- **K9. Determinant method (Bombieri-Pila 1989; Heath-Brown 2002; Salberger; Walsh 2015, recalled) as a
  small-box enumerator.**
  - It gives upper bounds only.
  - Its algorithmic form is Coppersmith (Cohn-Heninger correspondence), already
    LEAD-ICP-coppersmith-smallroot-semaev (reach 0.10-0.16 against 1/2).
  - The count route is IDEA-20260808-0e9fa1. Dominated.
- **K10. Impagliazzo-Pudlak-Sgall size-degree on the Boolean-digit encoding (to decide
  LEAD-ICP-digit-presentation-solving-degree).**
  - With D ~ s/2 (measured d_ff growth) and N = m*s bits, size >= 2^{Omega((D-d0)^2/N)} = p^{Omega(1/(4m))}.
  - That is below the p^{1/4} gate, so it cannot decide. Dead. The lead's own degree ladder is the right
    instrument.
- **K11. Polynomial-method incidences (Guth-Katz, Rudnev, Stevens-de Zeeuw) for the m = 2 join.**
  S_3(u, v, c) = <(1, u, u^2), M_c (1, v, v^2)>. Both families are one-parameter, so the incidences are exactly
  the A x A points of the curve C_c. No gain. Dead.
- **K12. Decomposable-target polynomial Phi_A = prod_{s in Sigma_2(A)}(X - s) with fast multipoint evaluation
  (B3 batching).** Building it needs all L^2 pair sums, which is the folded table. A hash lookup is O(1) per
  target. Dominated.
- **K13. Semi-regular / linearization counting of closure degree at l ~ n/m on binary curves.** KR-IC-fbdb61
  forecloses "semi-regular estimate for summation polynomial systems", and LEAD-ICE-linearization-excess-fb-prior
  exists. Dominated.
- **K14. Stepanov auxiliary polynomial as a sub-linear H cap (H - c) algorithm.** deg Psi >= |H|, so
  root-finding costs >= |H|. Dead.

Binary/Koblitz coverage: B4 and B5 received K1, K5, K13 and the binary half of K10. No live polynomial-method
candidate survived for them. The measured fact that descended systems refute at degree 4 through (4, 6) shows
the binary descent is NOT a dense grid. So C1's floor does not transfer: the field-equation quotient behaves
differently once Frobenius-linearity enters.

---------------------------------------------------------------------------------------------------------
## 5. Fields searched but empty

Slice rank / Croot-Lev-Pach / cap sets; Dvir Kakeya and the method of multiplicities; Ax-Katz and Chevalley-
Warning (including restricted-variable forms) for decomposition existence; polynomial-method incidence geometry
over F_p for the m = 2 join; GF(2) parity-counting solvers for binary descended PDP; Stepanov-method subgroup
caps in the IC regime; the determinant method as a small-box enumerator.

## 6. Files

- `scout/scout-polynomial-method.md`: this dossier
- `scout/match-polynomial-method.txt`: lead_atlas and frontier --match output for the 9 phrasings
- `scout/pilot/grid_ns_support.py`, `grid_ns_support.out`: C1 pilot
- `scout/pilot/controls.py`, `controls.out`: C1 planted controls
- `scout/pilot/member_targets.py`, `member_targets.out`: C1 member-target extension (N5)
- `scout/pilot/coset_concentration.py`, `coset_coverage.py`, `coset_coverage.out`: C2 pilot
