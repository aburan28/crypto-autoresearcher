# Scout dossier: lattice reduction and small-root methods vs B1-B7

Scout field: Coppersmith / Howgrave-Graham (HG) / Jochemsz-May (JM), Ryan EUROCRYPT 2025 optimal shifts,
sumset bounds, Herrmann-May unravelled linearisation, Bauer-Joux, Kannan embedding, lattice attacks that use
algebraic structure. Date 2026-10-24. Claim tier: toy and analysis only. `sota_delta`: zero. No speedup is
claimed. Pollard rho is still the best known method.

## 0. Verdict

My field contains one structural ingredient that bears on the named bottlenecks. It bears on them
negatively, and strongly. It is a **leading-monomial ("corner") ceiling on every HG-type lattice**:

> **Corner lemma (C1).** Let f in Z[u] be a decomposition polynomial whose unknowns split into m slots. Suppose
> that for every choice of one coordinate c_i per slot, the monomial prod_i c_i^D occurs in f mod p and is the
> leading monomial in some monomial order. Then no lattice built from I_t = (f, p)^t can meet the
> Howgrave-Graham determinant criterion unless
> **D * log_p(box volume) < 1**.
> This holds for every t, every monomial support M and every choice of shifts. So it covers JM basic and
> extended, Ryan-optimal and cuso, Herrmann-May unravelled linearisation and superpolynomial dimension.

For Semaev's S_{m+1}(x_1..x_m; x_R), D = 2^{m-1}. The corner coefficient is 1: I give an inductive proof
below and checked it numerically for m <= 4. The premise holds for the following factor bases, so all of
them are closed at the single-equation level:
- small-x windows and rank-1 APs;
- rank-r GAPs, with any generators and any side lengths. The ceiling does not depend on r;
- Farey (rational-reconstruction) bases x = u/v;
- digit (base-B) lattice presentations.

Index calculus needs log_p(volume) > 1/2 + beta. The ceiling is 2^{-(m-1)} <= 1/2. **The single-equation
lattice family therefore cannot reach the demand at any m >= 2, by a margin of at least 0.5.**

The lemma does not cover one cell: **addition trees with kept windowed internal nodes (w > 0)**. This
includes the program's best cell, (m,w) = (4,2). Their S_3 blocks have no full corner. Candidate C2 is the
instrument that decides that cell. My prediction is that it closes.

For binary curves the lemma holds over F_2[z] (C3). The one oracle class that avoids the ICPERF writability
wall is polynomial-lattice decomposition. The lemma closes it by about 71 bits on ECC2K-130.

I found no lattice ingredient that opens B1-B7. Section 4 lists the 17 candidates I killed. Section 6 gives
one retrieved fact from outside my field (an LMFDB census). It refutes H-FROB-ff99bf.

## 1. What I read and what I produced

I read all of ATLAS.md (147 leads, every family), all of KRMAP.md, object-frame-ideation.md sections 1-6,
the idea-generator search heuristics, target-result-profile Part A, the lead YAMLs whose obstruction
statements are quoted below, `analysis/smallroot-reach/CLOSURE.md` and `CORRECTION.md`, and H-PFDR-3c7d1e.
I also grepped the ledger index for dedup.

Everything I produced is in `/private/tmp/claude-501/-Volumes/f265640f-2c93-4fe4-b63c-86aa0f1beb57/scratchpad/scout/`:

| artifact | what it computed | result (produced here) |
|---|---|---|
| `corner_probe.py` -> `corner_probe.out.json` | sympy S_3, S_4 (symbolic a, b, x_4) | corner coeff of x1^2x2^2 in S_3 = **1**; of x1^4x2^4x3^4 in S_4 = **1**; S_4 has 439 terms, degree 4 per variable, total degree 12 |
| `s5_corner.py` | coefficient of (x1x2x3x4)^8 in S_5(.; x_R) mod 10007, by Lagrange top-coefficient extraction on a 9^4 grid, 3 random (a, b, x_R) | **1, 1, 1** |
| `corner_probe.py` | exact dim V_k = dim((f^k mod p) ∩ F_p[M]) for f = S_3(x1, x2; x_R), p = 10007; HG-admissible beta_max = Σ_k dim V_k / Σ_{a∈M}(a1+a2) | box M, L = 8/12/16: beta_max **0.1296 / 0.1410 / 0.1471** (tends to the JM value 1/6); triangle 0.067-0.093; diagonal band 0.022-0.052; 1500-step hill-climb over subsets M ⊂ [0,L]^2 (L = 8, 10) found **no M above the box**; dim V_k for the box equals the corner count (L-2k+1)^2 exactly. **Never above the corner ceiling 1/4.** |
| `tools/smallroot_reach_hg.py --compare` (repo tool, run unmodified) | JM-HG reach table | (4,2) eps_avail 0.2803 vs 8/9; (4,0) 0.0479 vs 0.6667; every cell dead (repo numbers, reproduced) |
| LMFDB `av_fq_isog` (MCP) | census over q = 2, g = 1..6, 131 \| #A(F_2) | g <= 4: 0 classes; **g = 5: 24 of 14,325 (11 Jacobian)**; **g = 6: 617 of 164,937** (section 6) |

## 2. The ingredient: corner lemma and proof

### 2.1 Setting

f in Z[u_1..u_n] reduces to a nonzero f̄ mod p. Each unknown u_c has bound p^{ω_c}. For an exponent vector a,
the weight is w(a) = Σ_c ω_c a_c. Take a finite monomial set M and the HG lattice L = I_t ∩ Z[M], with
I_t = (f, p)^t and coordinates scaled by p^{ω·a}. Any shift-built lattice is a sublattice, so its determinant
is larger. The HG determinant criterion, asymptotically, is

  (HG)  Σ_{a∈M} w(a) + e(L) < t|M|,  where p^{e(L)} = [Z^M : L].

### 2.2 Lemma A (index count)

e(L) >= t|M| - Σ_{k=1}^t dim V_k, where V_k = (f̄^k) ∩ F_p[M].

*Proof.* Filter L by L_j = L ∩ p^j Z^M. Then L_t = p^t Z^M, because p^t is in I_t. The graded piece
L_j / L_{j+1} injects into W_j = {h̄ : h in Z[M], p^j h in I_t}. The pair (p, f) is a regular sequence in
Z[u]: p is a nonzerodivisor, and f̄ ≠ 0 in the domain F_p[u]. So gr_I Z[u] is a polynomial ring over
Z[u]/(p, f), in which p* is a nonzerodivisor (recalled: Rees, Matsumura Th. 16.2). Hence
(I_t : p^j) = I_{t-j} and W_j ⊆ (f̄^{t-j}) ∩ F_p[M] = V_{t-j}. Summing over j gives
[L : p^t Z^M] <= p^{Σ_k dim V_k}. ∎

Consequently (HG) implies **Σ_{a∈M} w(a) < Σ_{k>=1} dim V_k**. This is the identity `t·dim - s_p = Σ|M_k|`
of CORRECTION.md, now stated for every lattice rather than for the JM shift set.

### 2.3 Lemma B (leading-monomial count)

Fix any monomial order σ. Then dim V_k <= N_σ(k) := #{a ∈ M : LM_σ(f̄)^k | u^a}. This holds because F_p[u]
is a domain, so LM(f̄^k q) = LM(f̄)^k LM(q), and an echelon basis of V_k has distinct leading monomials in M.

### 2.4 Corner lemma (averaged over orders)

Suppose that for every choice c = (c_1..c_m) of one coordinate in each slot there is an order σ_c with
LM_{σ_c}(f̄) = prod_i c_i^D. Pick c at random with P(c_i = c) = ω_c / vol_i, where vol_i is the slot volume
Σ_{c∈slot i} ω_c. Since a minimum is at most an average,

  Σ_k dim V_k <= Σ_k E_c N_{σ_c}(k) = Σ_{a∈M} Σ_k Π_i ( Σ_{c∈slot i} π_c 1[a_c >= kD] )
              <= Σ_a min_i Σ_c π_c a_c / D = Σ_a min_i w_i(a) / (D vol_i),

where w_i(a) is slot i's share of w(a). Then w(a) = Σ_i w_i(a) >= (Σ_i vol_i) · min_i (w_i/vol_i). So the
ratio Σ_k dim V_k / Σ_a w(a) is at most 1/(D · vol), with vol = Σ_i vol_i. Combined with Lemma A:

> **HG success ⇒ D · log_p(total box volume) < 1.** ∎

The bound is dimension-free and shift-free. It does not depend on how the slot's volume is spread over its
coordinates, and it does not depend on the GAP rank r.

### 2.5 Premise for S_{m+1}

**Corner coefficient = 1.** S_{m+1} = Res_X(S_m(x_1..x_{m-1}, X), S_3(x_m, x_R, X)). Write A(X) = S_m and
B(X) = B_2X^2 + B_1X + B_0 with B_2 = (x_m - x_R)^2. Then Res = B_2^{deg A} · A(r_1) A(r_2).

By induction, the corner of A in x_1..x_{m-1} has coefficient 1, and that coefficient sits only at X^0. So
the corner of A(r_1)A(r_2) has coefficient 1. B_2^{2^{m-2}} = (x_m - x_R)^{2^{m-1}} supplies x_m^{2^{m-1}}
with coefficient 1. The argument does not depend on the characteristic. It agrees with the computed values
(S_3, S_4 symbolic; S_5 mod 10007, three draws).

**The corner is the leading monomial.** It is divisible by every monomial in the support, so it is the LM
in every order. The repo's own IDEA-20260723-006 (corner-coefficient induction: the full box outside an
O(m)-size exceptional target set) gives the whole box support for generic x_R.

**Substituted slots.**
- x_i = a_{i0} + Σ_j a_{ij} u_{ij} (rank-r GAP, digits): the coefficient of prod u_{i c_i}^D is
  prod a_{i c_i}^D ≠ 0. Lex order with c_1 > ... > c_m first makes it the LM.
- x_i = u_i / v_i (Farey): S^h is bihomogeneous of degree D per pair. The coefficients of u_i^D and v_i^D are
  box vertices of S, which are nonzero for generic targets.

The premise therefore holds for all of these.

### 2.6 Consequences (single equation, w = 0, the program's ε convention)

The JM-HG column is the repo tool's value under its n = l+1 convention. With x_R known (n = m) the full-box
JM value is 2/(D(m+1)), which is 0.125 at m = 3 and 0.05 at m = 4. Both are still below 1/D.

| m | D | IC demand ε_req = m/(2(m-1)) | JM-HG achieved (repo tool) | **corner ceiling 1/D (any lattice)** | margin <= |
|---|---|---|---|---|---|
| 2 | 2 | 1.000 | 0.333 | 0.500 | -0.50 |
| 3 | 4 | 0.750 | 0.100 | 0.250 | -0.50 |
| 4 | 8 | 0.667 | 0.048 | 0.125 | -0.54 |
| 5 | 16 | 0.625 | 0.021 | 0.063 | -0.56 |
| 8 | 128 | 0.571 | 0.002 | 0.008 | -0.56 |

Further consequences:
- **3-unknown S_3 block** (no full corner). Average over the three lex LMs x_i^2x_j^2 with
  q_ij ∝ ω_i + ω_j. Using min(a_i, a_j) <= (ω_i a_i + ω_j a_j)/(ω_i + ω_j), any HG lattice for one block
  needs **vol_block < 1/2**. JM gives 0.2803, which is consistent.
- **2-unknown S_3** (x_R known): vol < 1/2. JM gives 1/3. The exact probe gives 0.294 at L = 16 and
  approaches 1/3.
- **Lattice + guessing hybrid.** Guessing digits until the remaining box fits under p^{1/D} costs
  p^{vol - 1/D}. MITM costs p^{vol/2}. The hybrid wins only if vol < 2/D, i.e. m <= 2, where IC cannot beat
  rho with any oracle.
- **Superpolynomial dimension** (IDEA-20260808-e2315e). The inequality holds at every t, and BKZ
  approximation factors only make it worse. Decided negatively.

**Scope (what the lemma does NOT cover).**
1. Lattices whose short vectors are far below det^{1/dim} for a structural reason. The lemma is a
   determinant-level (Gaussian-heuristic, H1) statement, like every reach in CLOSURE.md. An unconditional
   version would extend Chinburg-Hemenway-Heninger-Scherr capacity theory beyond the univariate case.
2. Auxiliary ideals other than (f,p)^t. The larger ideal {g : g ≡ 0 mod p^t on all F_p-roots} adds only
   elements of degree >= p, such as p^{t-1}(x^p - x), which a polynomial-dimension lattice cannot hold.
3. **Systems of several equations.** Here only Lemma A carries over, with V_k = J̄^k ∩ F_p[M]. Lemma B needs
   in_σ(J̄^k), which can exceed in_σ(J̄)^k when the leading monomials share variables. This is C2.

### 2.7 Literature relation (provenance)

- Aono, Agrawal, Satoh, Watanabe, "On the optimality of lattices for the Coppersmith technique", ACISP 2012,
  ePrint 2012/108, AAECC (journal) [retrieved, by search]. They prove univariate and Boneh-Durfee optimality
  for Minkowski-sum lattices, by a related leading-term counting method. The multivariate corner/averaging
  form above is, as far as I know, not stated there. Novelty is `unverified` and best read as an adaptation.
- Chinburg, Hemenway, Heninger, Scherr, capacity-theory optimality of Coppersmith's univariate method,
  arXiv 1605.08065 / ePrint 2016/869 [retrieved, by search; ASIACRYPT 2016 venue recalled]. The repo has a
  title-level note, KN-LIT-3299.
- Keegan Ryan, "Solving Multivariate Coppersmith Problems with Known Moduli", EUROCRYPT 2025, LNCS 15606
  pp. 355-384, ePrint 2024/1577, tool `cuso` [retrieved: abstract read]. Its "provably optimal shift
  polynomials" are sublattices of I_t ∩ Z[M]. The abstract claims no upper bound on achievable reach, so
  Lemma A covers it.
- Jochemsz-May ASIACRYPT 2006; Howgrave-Graham 1997; Herrmann-May unravelled linearisation (ASIACRYPT 2009,
  PKC 2010); Bauer-Joux EUROCRYPT 2007 [all recalled]. Unravelled linearisation is an HG lattice in a
  triangular change of basis, so Lemma B applies to its LM set Λ. Bauer-Joux addresses algebraic
  independence, which can only lower reach.
- The Feng-Luo-Chen-Nitaj-Pan "sumset bounds" are as cited by the lead row [recalled from the row; not
  verified]. Shift-region optimisation of that kind stays inside Lemma A.

## 3. Candidates

### C1. Corner lemma: a strategy-independent closure of single-equation lattice decomposition (prime field, B1)

- **Bottleneck.** B1, the non-enumerative point-decomposition oracle. It is also the SO-TABLE revisit
  condition: "A non-generic decomposition oracle exists with per-attempt cost T_dec << p^{1/4} at arity m = 4
  (an S_5 oracle at B ~ p^{1/5})".
- **Ingredient.** Lemmas A+B and order averaging (section 2). Related work: Aono-Agrawal-Satoh-Watanabe 2012
  (retrieved); Ryan EUROCRYPT 2025 (retrieved).
- **Pair and trichotomy.** The representation is R1: the integer, Farey or GAP representative of x(P) in
  F_p. Σ is translation by factor-base elements. The oracle is an HG lattice on S_{m+1}(·; x_R).
  Class: **partial-action** (index calculus is Class I). The membership component is coordinate-dependent.
- **SO codes touched** (obstruction text quoted; premise escaped):
  - SO-TABLE (LEAD-ICP-generic-table-decomposition): "Any decomposition oracle that enumerates or
    table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N ... Scope: any
    generic (enumeration/table) decomposition over F_p." **Escaped premise:** "enumerates or table-looks-up".
    A lattice oracle reads x as an integer.
  - SO-GEN (LEAD-RHO-generic-sqrt-lower-bound): "... any generic algorithm needs Omega(sqrt r) group
    operations ... Scope: all generic algorithms, any field, any r." **Escaped:** "generic". The oracle reads
    the representation.
  - SO-ALGFB (LEAD-ICP-algebraic-membership-factor-base): "A target-independent algebraic locus of degree d
    yields O(d) usable points ... mean per-target yield is binomial(B+m-1, m)/N for every base of size B ...
    Scope: prime-order E/F_p, any base of size B." **Escaped:** "algebraic locus of degree d". Membership is
    an archimedean inequality (KN-OPEN-020's implicit-membership class). **Not escaped:** the conservation
    clause, which is what pins the demand.
- **Tier X** (a decision at exponent level). **Predicted gain: 0.** The prediction is a closure, with margin
  <= -0.50 at every m (H1, H2, H3).
- **First discriminating step.** Run three checks:
  - (i) independent review of section 2.2-2.5, the AGENTS rule-12 analogue for a closure;
  - (ii) extend `corner_probe.py` to the rank-2 GAP substitution of S_3 (4 unknowns, L <= 6) and the Farey
    form, and check Σ_k dim V_k <= the averaged bound;
  - (iii) run `cuso` (Ryan) on S_3(x1, x2; x_R) and S_4 at a toy prime, and check its certified bound against
    1/D.

  Items done here: the corner coefficient for m <= 4 and the exact S_3 box/shape/hill-climb probe. Neither
  violates the bound.
- **Outcomes → dispositions.**
  - Lemma confirmed → LEAD-ICP-coppersmith-smallroot-semaev **closed_obstructed(theorem)** for every w = 0
    cell, every GAP rank, and Farey/digit bases. The same applies to H-PFDR-3c7d1e, IDEA-20260808-e2315e,
    IDEA-20260808-486ae2 and its siblings, and the polynomial lane (dense or Newton-target shifted lattices,
    IDEA-20261015-9defe9) of LEAD-ICP-lattice-ic-relation-construction. The lead's w > 0 cells stay open for C2.
  - Exact dim V_k exceeds N_σ(k), or cuso certifies a reach above 1/D → the lemma is wrong. Record the
    counterexample M and keep the lead at **open_next_step**, with best_measured = that reach.
- **Cost.** Implementation about 1 day (derivation review plus probe extensions). Compute: minutes; the two
  probes here ran in under 15 minutes on a laptop.
- **Self-kill risk.** Low for the algebra. The main risk is H1: a structurally short vector with no
  determinant reason. The determinant-level reach is the program's own convention. An unconditional version
  needs a multivariate capacity argument.
- **Match phrasings.**
  1. "corner lemma: Howgrave-Graham determinant ceiling D*log_p(volume) < 1 for summation-polynomial small roots, any shift set"
  2. "no Coppersmith-style lattice can find small-x point decompositions for any factor base shape"
  3. "lattice-describable base of size B: decomposition oracle capped by leading-monomial weight while mean yield binomial(B+m-1,m)/N is fixed"

### C2. Initial-ideal ceiling for addition-tree systems, plus an HG-admissibility gate (prime field, B1)

- **Bottleneck.** The w > 0 cells that C1 leaves open, including the program's best cell (m,w) = (4,2):
  ε_req = 8/9, JM-HG 0.2803. These are the only cells of LEAD-ICP-coppersmith-smallroot-semaev that survive C1.
- **Ingredient.** Lemma A for J = (f_1..f_s) with (f_1..f_s, p) regular (checkable). This gives
  V_k = J̄^k ∩ F_p[M]. Then the bound dim V_k <= #{a ∈ M : u^a ∈ in_σ(J̄^k)}, averaged over orders. Ryan
  EUROCRYPT 2025 (retrieved) is the matching *achievability* side, for an exact optimal lattice at small t.
- **Pair and trichotomy.** Same as C1, with the representation extended by kept internal node values
  (windowed). **Partial-action.**
- **SO codes touched.** SO-TABLE, SO-GEN and SO-ALGFB, with the same quotes and escaped premises as C1.
- **Tier X. Predicted gain: 0.** The prediction is a closure, with ε_avail(4,2) <= 1/2 vs 8/9, margin
  <= -0.39 (H4). Derivation: under H4, the root block S_3(u1, u2; x_R) has a full corner (u1^2u2^2), so
  γ1 + γ2 < 1/2. Demand (I) needs 3β + γ1 + γ2 > 5/2 with β < 1/4, which is impossible.
- **First discriminating step.**
  1. With msolve or sage (both installed), compute reduced Gröbner bases of J̄^k for k <= 4 on the (3,1) and
     (4,2) trees at p ≈ 2^16, random x_R, and 10-20 random lex/grevlex orders.
  2. From these, compute the per-direction order function ν_σ(a) = lim k_max^σ(λa)/λ, and the ratio
     max_a E_σ ν_σ(a)/w(a) at the demand point.
  3. In parallel, run the exact HNF of I_t ∩ Z[M] (cuso, t <= 3) on the (3,1) tree as an achievability
     cross-check.
- **Outcomes → dispositions.**
  - Ratio < 1 at every demand-feasible (β, γ) → all tree cells **closed_obstructed(theorem)**. Lead closed
    in full.
  - Ratio >= 1 in some direction → **open_next_step**. Build the exact (Ryan) lattice on that M and run a
    planted-root recovery at 40 bits (H-PFDR-621852). best_measured = the exact reach.
  - GB computation infeasible at k = 4 → **exhausted_at_scale**, with the largest k reached.
- **Byproduct (instrument).** The same code is a zero-compute **HG-admissibility gate**. Given any proposed
  small-root system with its box and demand volume, it returns the averaged corner or initial-ideal ceiling.
  This serves LEAD-ICP-construction-normal-form (open_unexamined) and every future lattice proposal.
- **Cost.** Implementation 2-4 days. Compute: hours on one host; memory small at toy p.
- **Self-kill risk.** Moderate. in_σ(J̄^k) can exceed in(J̄)^k when the leading monomials share u1 or u2, so
  the averaged bound may be too loose to decide. The exact-HNF arm is then the decider.
- **Match phrasings.**
  1. "averaged initial-ideal ceiling for Howgrave-Graham lattices on chained S_3 trees with kept windowed internal nodes"
  2. "can a lattice solve the tree of small S_3 equations used for windowed decompositions"
  3. "kept internal windows welded to block degree: demanded reach 8/9 at (m,w)=(4,2) vs strategy-independent per-block ceiling 1/2"

### C3. Function-field corner lemma: F_2[z] polynomial-lattice decomposition on ECC2K-130 (binary/Koblitz, B4/B5)

- **Bottleneck.** B4, the writability wall: the descended ANF exceeds the per-decomposition rho budget by
  +40.8 bits. A polynomial-lattice (Popov-form) Coppersmith oracle on the polynomial-basis factor base
  V = {x : deg_z x < l} (FPPR / Petit-Quisquater, KR-IC-73db3f) **never writes the descended ANF**. It works
  in F_2[z]/(F) with polynomial-size objects, so it is the one oracle class that escapes that wall. This has
  never been tried in the atlas.
- **Ingredient.** Lemmas A+B over F_2[z]. The degree of the determinant is exact (Popov form), and log_p is
  replaced by deg / n. Over F_2[z] the HG argument is exact: deg h(x(z)) < t·n implies h(x(z)) = 0. Char-2
  S_3 = x1^2x2^2 + x1^2x3^2 + x2^2x3^2 + x1x2x3 + a6 has the corner x1^2x2^2 with coefficient 1, and the
  section 2.5 induction is characteristic-free. Background: Guruswami-Sudan and function-field Coppersmith
  [recalled].
- **Pair and trichotomy.** The representation is R1: polynomial-basis coordinates of x in F_2[z]/(F). Σ is
  translation by factor-base elements. **Partial-action.**
- **SO codes touched.**
  - LEAD-ICP-icperf-writability-boundary: "At the best viable arity the descended ANF exceeds the whole
    per-decomposition rho budget by ... +40.8 (ECC2K-130) ... Scope: standardised binary curves with
    n <= 283, unchained descended ANF". **Escaped premise:** "descended ANF". No descent is performed.
  - LEAD-ICB-decomposition-encoding-and-sat: "Every SAT or enumeration method measured has per-attempt UNSAT
    cost 2^{alpha l} with alpha ~ m". **Escaped premise:** "SAT or enumeration".
  - LEAD-ICB-generic-table-oracle (SO-TABLE, binary): "Every oracle built from group operations and
    membership tests makes IC a generic-group algorithm with advice". **Escaped premise:** "group operations
    and membership tests".
- **Tier X. Predicted gain: 0.** The prediction is a closure. The ceiling is m·l < n/2^{m-1} = 16.4 bits of
  total box degree at n = 131, m = 4. The demand is m·l > n·m/(2(m-1)) = 87.3 bits (with LA, l < 32.75).
  The gap is about 71 bits (H1, H5). Koblitz-specific note: Frobenius-stable subspaces are not of the form
  deg < l, so the oracle cannot even use the orbit saving.
- **First discriminating step.**
  - (i) Check the char-2 corner coefficient of S_4 and S_5 symbolically, with the s5_corner.py method over
    GF(2^k).
  - (ii) Write a 50-line Popov-form planted-root probe: S_3 at n = 31, m = 2, l in {2..6}. Show that recovery
    stops at 2l ≈ n/2 and never above it.
- **Outcomes → dispositions.**
  - Confirmed → record **closed_obstructed(theorem)**: the lattice oracle class for the polynomial-basis base
    is dead. This is a pre-emptive closure, filed under LEAD-ICB-decomposition-encoding-and-sat.
  - The probe recovers roots at 2l > n/2 → the lemma's function-field transfer is wrong → **open_next_step**,
    best_measured = the recovered l.
- **Cost.** Implementation 0.5-1 day. Compute: minutes.
- **Self-kill risk.** Low. The risk is a binary demand-model mismatch (p → 2^n in CLOSURE.md §1), which I
  checked: |F| = 2^l, P(decomp) = 2^{ml-n}/m!, LA 2^{2l}.
- **Match phrasings.**
  1. "function-field corner lemma: F_2[z] Popov-form Coppersmith decomposition with polynomial-basis subspace factor base"
  2. "lattice reduction over binary polynomials as a point-decomposition solver for ECC2K-130"
  3. "an oracle that never writes the descended ANF escapes the writability boundary but its reach is below n/2^{m-1}"

### C4 (out-of-field side finding, retrieved). LMFDB census decides H-FROB-ff99bf

- **Bottleneck.** B5-adjacent. The LEAD-ICB-nonlinear-frob-stable-bases next step reads "finish the
  dimension-5/6 Weil-polynomial census over F_2 for 131 | #A (H-FROB-ff99bf hit an impediment at dims 5-6)".
- **Retrieved from LMFDB `av_fq_isog`, q = 2.**
  - g <= 4: 0 classes with 131 | #A(F_2).
  - **g = 5: 24 of 14,325 classes, all simple. 11 of them contain a Jacobian.** Example: `5.2.b_d_e_h_n`,
    with poly coefficients [1,1,3,4,7,13,14,16,24,16,32], P(1) = 131 (checked by hand), so
    #A(F_2) = 131, is_simple, has_jacobian = 1.
  - g = 6: 617 classes (149 simple ones contain a Jacobian).
- H-FROB-ff99bf claims that "for every abelian variety A of dimension g in {5, 6} over F_2, #A(F_2) is NOT
  divisible by 131". **That claim is refuted**, assuming LMFDB's q = 2, g <= 6 tables are complete (their
  stated coverage). A genus-5 curve over F_2 with #Jac(F_2) = 131 gives a commutative algebraic group over
  F_2 with a rational point of order 131 (KN-OPEN-095df5). Whether that helps a factor base is the
  coordinator's call. I make no cost claim.
- **Tier I. Predicted gain: 0** (it decides a census hypothesis). Disposition for that sub-step: done. The
  lead's next step moves on to reading the Couveignes-Lercier primary source.

## 4. Candidates I killed (strongest first)

| # | candidate | reason it dies |
|---|---|---|
| K1 | Farey / rational-reconstruction base x = u/v, \|u\|,\|v\| <= p^{β/2} (bihomogeneous S^h; every monomial has equal weight, so it looked like an escape) | The single-order bound only gives vol < 2/D (vacuous at m = 2). The **averaged** corner lemma gives vol < 1/D, the same as small-x. Closed for m >= 2, and m = 2 IC can never beat rho. |
| K2 | Rank-r GAP substitution (H-PFDR-3c7d1e; its eps_naive(r) = 9/7 > 1 is in the superseded TOOL convention) | The averaged corner lemma is r-independent: vol < 1/D. JM-HG falls with r, as (r+1)/(2(3r+1)). Decided by C1. |
| K3 | Multilinear hyperplane-section presentation (E ⊂ P^{n-1} by \|nO\|; n points sum to O iff coplanar, which is a determinant of degree 1 per slot and escapes the D >= 2 premise) | **Self-corner.** "Small coordinates" makes F non-empty only at coordinate size p^{(n-2+β)/n}. There the curve's own quadrics have LM weight 2(n-2+β)/n >= 1 (n >= 4), and the plane cubic has 1 + β. The membership equations are heavy. |
| K4 | Symmetric coordinates (e1, e2): the m = 2 decomposition curve is a conic | Same corner (e2^2 has weight 4β). m = 2 needs β > 1/2 against LA β < 1/4 under any oracle. |
| K5 | Lattice + guessing hybrid | Costs p^{vol-1/D} against MITM p^{vol/2}. It wins only if vol < 2/D, which forces m <= 2. |
| K6 | Linearisation + fixed-dimension integer programming (Lenstra 1983, Kannan 1987 [recalled]) | The linearised box holds p^{βΣ\|α\| - 1} spurious lattice points (S_3, m = 2: p^{18β-1}). That is far above MITM. |
| K7 | Integer Coppersmith on S(x) - kp = 0 with k unknown | Equivalent to or dominated by the modular form (Blömer-May toolkit [recalled]). The corner sits on the same monomials. |
| K8 | Superpolynomial lattice dimension (IDEA-20260808-e2315e) | The corner inequality is dimension-free, and BKZ factors only hurt. Decided by C1. |
| K9 | Simultaneous Coppersmith across targets sharing factor-base unknowns | Random targets do not share decomposition unknowns. The expected incidence is L·C(K,m)/N, far below 1. |
| K10 | Special-prime (generalised Mersenne) digit lattice / SNFS residue-field view | The digit presentation is a rank-s GAP (K2). The number-field lift is closed by LEAD-TRF-global-lift-small-height. |
| K11 | HNP / Bleichenbacher conversion gate for coordinate-to-log-bit statistics | Already held as H-ECDLP-a4be60 ("exponent 2β vs 1/2"). Blocked on a measured leak; nothing new to add. |
| K12 | Guruswami-Sudan list decoding to measure A(d) (LEAD-EXO-invertible-hint-subset) | The GS radius sqrt(2dN) is far above random-function agreement. A(1) is exact in O(N^2) by hashing pairs. |
| K13 | Mordell-Weil-lattice CVP for a bounded-height section through a prescribed fibre point (LEAD-EXO-global-lift-height) | The coset needs Q written in the specialised generators. That is a multi-dimensional DLP, i.e. SO-XEDNI. |
| K14 | Skew (Ore) polynomial lattices to search for quasi-subfield polynomials | Euler-Petit: β >= 3/4 for linearised QSPs (SO-QSP). |
| K15 | Lattice enumeration of Weil polynomials for Jacobian carriers (B5) | Enumeration speed is not the obstruction; Torelli rarity is, and it is unchanged. |
| K16 | Stripping r_k = ψ_{k-1}/ψ_k from Miller-cocycle values by lattice (B7) | There is no archimedean handle on EDS ratios. Lauter-Stange equivalence (SO-NET). |
| K17 | NFS-style special-q lattice sieve for EC relation collection | The norm N(f) lives in F_p[x]; there are no integer norms to sieve. |

## 5. Numbered heuristics

- **H1.** Reach is the determinant-level (Gaussian-heuristic) HG criterion, as in CLOSURE.md and
  smallroot_reach_hg.py. Validation: planted-root probes (done for S_3 shapes); `cuso` certificates; a
  multivariate capacity-theory extension for an unconditional statement.
- **H2.** For generic targets, S_{m+1}(·; x_R) has full-box support with corner coefficient 1. Status: proved
  by induction here; computed for m <= 4 (three draws mod 10007); IDEA-20260723-006 gives the box outside
  O(m) exceptional targets.
- **H3.** The IC demand of CLOSURE.md §1 (KN-FIND-007 yield conservation, relation count, LA) does not depend
  on the representation. The repo already holds this, and CORRECTION.md left it unchanged.
- **H4 (C2 only).** Per-block corner ceilings stay binding in the joint ideal of the tree. This is to be
  tested: it is exactly what C2 measures.
- **H5 (C3 only).** The binary demand model is CLOSURE.md §1 with p → 2^n, and the polynomial-basis subspace
  is the factor base.

## 6. Side finding: details

The SQL was run through the LMFDB MCP; I quote the outputs as returned.
- `SELECT g, COUNT(*), SUM(MOD(abvar_counts[1],131)=0) FROM av_fq_isog WHERE q=2 GROUP BY g` →
  - g = 1: 5 classes, 0 divisible;
  - g = 2: 35, 0;
  - g = 3: 215, 0;
  - g = 4: 1,645, 0;
  - g = 5: 14,325, 24;
  - g = 6: 164,937, 617.
- Among the g = 5 hits: 13 simple with has_jacobian = -1, and 11 simple with has_jacobian = 1.
- Among the g = 6 hits: 96 non-simple and 24 non-simple-Jacobian; 348 simple and 149 simple-Jacobian.
- `5.2.b_d_e_i_k` also has 131 points, with jacobian_count = 3.

## 7. Fields searched with no live candidate

Coppersmith/HG with optimal shifts (Ryan 2025); JM basic and extended; Herrmann-May unravelled linearisation;
Bauer-Joux; Kannan embedding/CVP on linearised systems; fixed-dimension IP (Lenstra, Kannan); the
Bombieri-Pila / Heath-Brown determinant method (it builds the same auxiliary-polynomial object, so the corner
lemma applies [recalled]); EC-HNP (Boneh-Venkatesan, Shani PKC 2017 [recalled]); function-field lattices
(Popov form, Guruswami-Sudan); skew-polynomial lattices; the NFS lattice sieve; Mordell-Weil lattices;
capacity theory (CHHS).

Every one of these either reduces to an HG lattice inside (f,p)^t, and so is capped by the corner lemma, or
loses to a counting argument (section 4).
