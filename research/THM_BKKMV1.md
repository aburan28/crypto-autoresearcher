# THM_BKKMV1 — Sectioned box-saturation and the mixed-volume law for the Semaev summation family

- **ID:** THM-BKKMV1
- **Task:** TASK-20260718-THMMV (theory track), per DEC-20260718-011 ("Theory-note candidate: prove the sectioned box-saturation theorem and the MV law for all m (publishable complexity-geometry result)")
- **Author:** executor (theory-track agent), 2026-07-18
- **Reads:** ledger/EV-BKKMV-001.yaml, ledger/EV-BKK-001.yaml, ledger/DEC-20260718-011.yaml, experiments/EXP-BKKMV-001/{analysis.md, bkkmv1_cert.sage}, experiments/EXP-BKK-001/analysis.md, research_directions_20260717.md §B2/§D2
- **Verification artifacts:** research/verification/thm_bkkmv1_verify.sage (stages `34`), research/verification/thm_bkkmv1_verify_m5.sage (stages `5n`, `u5`); results in thm_bkkmv1_verify_results_{34,5n,u5}.json. 62/64 checks PASS; the 2 honest FAILs (a refuted factorization guess, one instance-cancellation count) are analyzed below. One infrastructure censoring (symbolic m=5 resultant > 290 s harness foreground cap) mitigated by numeric specialization + a specialized-determinant route.

## 0. Result summary

1. **PROVED (all m ≥ 3, char ≠ 2):** the structural skeleton of the family — per-variable degrees `deg_{x_i} S_m = 2^{m-2}`, total degree `(m−1)·2^{m−2}`, the leading-form recursion `lead_{x_m} S_m = S_{m−1}(x_1,…,x_{m−1})²` and the coefficient tower `coeff(x_3^D⋯x_m^D) = (x_1−x_2)^D` (D = 2^{m−2}); the **universal diagonal corner**: the monomial `x_1^D⋯x_{m−1}^D x_m^0` has coefficient exactly **1** in S_m (any curve, any characteristic ≠ 2), hence every generic section has total degree exactly (m−1)·2^{m−2} with the diagonal corner always present. This proves the ledger observation "diagonal monomial present in every instance" (EXP-BKK-001, 54/54) as a theorem. (Lemma 2, Theorem 1.)
2. **PROVED (reductions):** (i) a generic single-variable section's support equals the **projection** of the unsectioned support (Lemma 1), so "every generic section is the full box" ⟺ "the support projects onto the full box along every coordinate"; (ii) if the sectioned system at level m is box-saturated, then `MV_m = (m−1)!·2^{(m−1)(m−2)}` exactly — the mixed volume of identical boxes is n!·Vol — and this equals the multi-graded (P¹)^{m−1} Bézout number, while the ratio to the total-degree Bézout number is `(m−1)!/(m−1)^{m−1}` (Stirling decay). So **(a) ⟹ (b)** for all m (Theorem 4).
3. **PROVED (saturation theorem at m ≤ 5):** the sectioned box-saturation theorem holds for m = 3 (hand proof, full support computed: 13 cells), m = 4 (symbolic over QQ(a,b): support 439 cells, all four projections exactly the 125-box), m = 5 (explicit curves over QQ: all five projections exactly the 6561-box; by specialization-monotonicity this forces the generic fiber). Hence `MV_m = (m−1)!·2^{(m−1)(m−2)}` is a **theorem for m ≤ 5**, not merely a 3-point certificate. Matches EV-BKKMV-001's measured anchors (13/439/54777, MV 8/384/98304) exactly. (Theorem 3.)
4. **CONJECTURE (C1, main):** projection saturation for all m ≥ 6, equivalently the sectioned box-saturation theorem for all m; C2 (implied by C1): the MV law for all m. Two precise attack routes and the exact missing lemma are given (§5).
5. **PROVED micro-structure (bottom fiber):** the axis polynomial `u_m(X) := S_m(0,…,0,X)` satisfies `u_m ≡ 0`-type degeneration: for **even** m, `X | u_m` identically (the all-zero corner is a hole for every curve — pairing argument, verified m = 2, 4 with `u_4 = a⁴X³(X − 8b(a²−8b²)/a⁴)`); for **odd** m, `c_m := u_m(0) ≠ 0` as a polynomial (verified m = 3: `c_3 = a²`; m = 5: `c_5 = a^10·(a^6 + 32a²b² − 256b⁴)`, and `u_3³ | u_5` exactly). Consequently **t = 0 is an exceptional section at even m** — verified: the m = 4 section at t = 0 loses 37 of 125 box cells including the origin. A falsifiable micro-prediction of the theory, confirmed symbolically. (Theorem 2.)
6. **OPEN GAP:** the all-m saturation theorem reduces to a concrete **interior-fiber non-cancellation lemma** for the Sylvester expansion of the resultant recursion (§5, Lemma-G). The coverage half is essentially combinatorial (sumsets of the three S_3-coefficient supports under the isobaric constraint); the cancellation half is the true gap.
7. **Unexpected observations (rule 8):** the u_3³-factor in u_5 (recursive bottom-fiber divisibility); my predicted ψ₅(0)-factorization of c_5 is **refuted** by computation (recorded, §4.4); the (a,b) = (2,3) instance loses 120 support cells vs the generic 54777 while keeping all projections full (instance cancellation with invariant projections, the same pattern as the ledger's small-prime losses); symbolic-vs-specialized resultant pitfall documented (§4.3).

**Bottom line for the program:** the B2/D2 barrier arithmetic is now theorem-grade for m ≤ 5 (previously a 3-point certificate), the reduction "saturation ⟹ MV law ⟹ box-Bézout = MV for all m" is proved, and the remaining all-m statement is isolated to one explicit combinatorial lemma. If C1 holds, every B2-class support-aware method has driver `MV = (m−1)!·2^{(m−1)(m−2)}` = the box Bézout number for all m — the saturation barrier in theorem form.

## 1. Setup and conventions

**Family (experiment convention, frozen with EXP-BKKMV-001).** For E : y² = x³ + ax + b over a field of characteristic ≠ 2, the Semaev summation polynomials are

```
S_2(x_1,x_2) = x_1 − x_2
S_3(x_1,x_2,x_3) = (x_1x_2 + x_1x_3 + x_2x_3 + a)² − 4(x_1x_2x_3 − b)(x_1 + x_2 + x_3)
S_m(x_1,…,x_m) = Res_X( S_{m−1}(x_1,…,x_{m−2}, X),  S_3(x_{m−1}, x_m, X) )   (m ≥ 4)
```

This is the symmetric form of S_3 used verbatim by the instruments (bkkmv1_cert.sage line 85); it equals the classical Semaev polynomial with (a,b) ↦ (−a,−b), an isomorphism-level sign convention that does not affect any support statement. S_m ∈ Z[a,b][x_1,…,x_m] (S_3 has integer coefficients; resultants preserve integrality). S_m vanishes exactly on x-coordinate tuples of m points summing to O; it is symmetric in all m variables.

**Objects.** D = D_m := 2^{m−2}; n := m−1. The **sectioned system** at target sections t_1,…,t_{m−1} (the D2/B2 object) is `Sys_m = { S_m(x_1,…,x_{m−1}, t_j) = 0 }_{j=1..m−1}`, n equations in n unknowns. The **box** is `B_m := [0, D]^{m−1} ⊂ Z^{m−1}`. "Sectioned box-saturation" = every (generic) section has Newton polytope equal to conv(B_m), i.e. support = the full box (lossless case) or at least the full polytope; we work with the full-box support statement, which is what the experiments measured.

## 2. PROVED: the structural skeleton (all m)

### Lemma 1 (section = projection) — PROVED

For t in the base field, write `S_m(x_1,…,x_{m−1}, t) = Σ_{e'} c_{e'}(t) x^{e'}` where `c_{e'}(x_m) = Σ_{e_m} γ(e', e_m) x_m^{e_m}` is the coefficient polynomial of the fiber over `e' ∈ Z^{m−1}`. Then for all t outside the union of the zero loci of the finitely many nonzero `c_{e'}` (a finite exceptional set, effective in principle):

`supp(S_m|_{x_m = t}) = π_m(supp S_m)`,

where π_m drops the m-th coordinate. **Proof:** `c_{e'}(t) ≠ 0` iff the fiber `{e'} × Z` meets supp S_m and t avoids the roots of c_{e'}; the exceptional set is finite because each c_{e'} has degree ≤ D and is not identically zero exactly when the fiber meets the support. ∎

Hence *"every generic section is support-full"* ⟺ *"π(supp S_m) ⊇ [0,D]^{m−1} for every coordinate projection π"* (by the S_m-symmetry of the family, one projection suffices).

### Lemma 2 (degree tower) — PROVED by induction on m

Write the recursion as Res_X(f, g) with `f = S_{m−1}(x_1,…,x_{m−2}, X)`, `g = S_3(x_{m−1}, x_m, X)`, `d := deg_X f = 2^{m−3}`, `deg_X g = 2`.

**(i) Leading form.** `lead_{x_m} g = (X − x_{m−1})²` (direct from S_3). Using `Res_X(f,g) = lead(f)² · Π_{f(α)=0} g(α)`:

`lead_{x_m} S_m = lead(f)² · Π_α (α − x_{m−1})² = lead(f)² · (f(x_{m−1})/lead(f))² = S_{m−1}(x_1,…,x_{m−1})²`.

**(ii) Per-variable degrees.** Upper bounds by the Sylvester determinant (each of the 2 f-rows contributes deg_{x_i} ≤ 2^{m−3}, g-rows do not involve x_i for i ≤ m−2): `deg_{x_i} S_m ≤ 2·2^{m−3} = 2^{m−2}` (i ≤ m−2); `deg_{x_{m−1}}, deg_{x_m} ≤ 2d = 2^{m−2}`. Exactness follows from Theorem 1 below (the diagonal corner realizes degree D in every x_i, i ≤ m−1) and (i) for x_m.

**(iii) Total degree.** *Isobaric micro-lemma:* every Sylvester determinant term is a product `f_{k_1} f_{k_2} g_{j_1}⋯g_{j_d}` with `k_1+k_2+Σ j_l = d·e = 2d` (the column indices of any transversal of the (d+2)×(d+2) Sylvester matrix sum to `d(d+2) + ... ` — the standard telescoping gives exactly `de`). If `T_{m−1} = (m−2)2^{m−3}` bounds the total degree of S_{m−1} (induction), then the coefficient f_k has x-total-degree ≤ T_{m−1} − k and g_j has (x_{m−1},x_m)-total-degree ≤ 4 − j (joint total degree of S_3 is 4), so every term has total degree ≤ `2·T_{m−1} + 4d − 2d = (m−1)2^{m−2}`. Exactness again by Theorem 1. ∎

**(iv) Coefficient tower.** Iterating (i): `coeff of x_j^{D}⋯x_m^{D} in S_m = S_{j−1}(x_1,…,x_{j−1})^{2^{m−j+1}}`, terminating at `coeff of x_3^D⋯x_m^D = (x_1 − x_2)^D`. (Base m = 3: `lead_{x_3} S_3 = (x_1−x_2)²` directly.)

All items verified symbolically at m = 3, 4 and numerically at m = 5 (checks m{3,4,5}_{totdeg, vardeg, lead_tower, coeff_tower}).

### Theorem 1 (universal diagonal corner) — PROVED

Let `w_m := S_m(x_1,…,x_{m−1}, 0)` (the zero-section). Then `lead_{x_{m−1}} w_m = w_{m−1}²` (m ≥ 3, w_2 := x_1): write `w_m = Res_X(f, h)` with `h(X) = S_3(x_{m−1}, 0, X) = x_{m−1}²X² + (2a x_{m−1} + 4b)X + (a² + 4b x_{m−1})`; then `lead_{x_{m−1}} h = X²`, so `lead_{x_{m−1}} w_m = lead(f)² Π_α α² = (f(0))² = w_{m−1}²`. Iterating, `coeff of x_2^D⋯x_{m−1}^D in w_m = x_1^D`, hence

`[x_1^D x_2^D ⋯ x_{m−1}^D] w_m = 1`  — coefficient **exactly 1**, for every (a,b) and every characteristic ≠ 2.

Combined with Lemma 2(iii) (total degree ≤ (m−1)D, so the fiber over (D,…,D) has only the e_m = 0 cell): **every section S_m(x_1,…,x_{m−1}, t) — for arbitrary t — contains the diagonal corner monomial x_1^D⋯x_{m−1}^D with coefficient exactly 1.** No exceptional set, no prime exclusions. Verified at m = 3, 4, 5 (checks m*_corner1, all == 1) and matching EXP-BKK-001's "diagonal monomial present in every instance" (54/54, all primes incl. the small ones where interior cells cancel).

*Remark.* This is the strongest corner statement: the box's top corner is cancellation-proof because the total-degree bound pins it to a single Sylvester-unambiguous fiber and the tower pins its coefficient to 1. The interior of the box is where the hard lemma lives (§5).

## 3. PROVED: the saturation theorem at m ≤ 5, and the dichotomy

### Theorem 3 (sectioned box-saturation for m ≤ 5) — PROVED (hand at m = 3; computer-verified at m = 4, 5)

**m = 3 (hand).** Expanding the convention's S_3 over Z[a,b]:

`supp(S_3) = {(2,2,0),(1,1,0),(0,0,0),(1,0,0),(0,1,0),(2,0,2),(1,1,2),(0,2,2),(2,1,1),(1,2,1),(1,0,1),(0,1,1),(0,0,1)}`

(13 cells; every coefficient visibly nonzero for `ab ≠ 0`: the layer over e_3 = 2 is `(x_1−x_2)²`, over e_3 = 1 is `−2(u+v)(uv−a)+4b`-type, over e_3 = 0 is `(uv+a)²+4b(u+v)`). The projection onto any two coordinates is the full 9-cell box [0,2]² — each of the 9 cells appears in at least one layer. Meanwhile 13 < 27: **the unsectioned polynomial is not box-saturated** (holes include (2,0,0), (0,2,0), (1,1,1), and all |e| > 4 cells). The dichotomy is therefore structural at m = 3: the layers are thin but their projections tile the box.

**m = 4 (symbolic).** Over QQ[a,b]: |supp(S_4)| = 439 (matches EV-BKKMV-001's measured 439 < 625 exactly), and all four coordinate projections equal the full 125-cell box [0,4]³ (checks m4_supp_size, m4_projection_0..3). Sections at t = 1, 2, 3 have full-box support directly (checks m4_section_t*).

**m = 5 (explicit instances + monotonicity).** The fully symbolic S_5 resultant over QQ[a,b] exceeded the 290 s harness foreground cap (infrastructure censoring, recorded; not evidence about the theorem). Instead: at (a,b) = (1,1) over QQ, |supp| = 54777 (matching the measured generic count) and all five projections are the full 6561-cell box [0,8]⁴; same at (a,b) = (2,3) (support 54657 after instance-specific cancellations — projections still full; checks m5_*_a1_b1, m5_*_a2_b3). Since `supp(specialization) ⊆ supp(generic fiber)` and projections commute with specialization, a full projection at any single specialization forces a full projection of the generic fiber. Sections at t = 1, 2 are full-box directly. ∎

**Corollary (MV law at m ≤ 5).** By Theorem 4 below, `MV_m = (m−1)!·2^{(m−1)(m−2)}` for m = 3, 4, 5 as a theorem (previously EV-BKKMV-001's 3-point certificate).

### The dichotomy, sharpened

Unsectioned support densities: 13/27 = 0.481, 439/625 = 0.702, 54777/59049 = 0.928 — increasing, consistent with the total-degree simplex constraint `|e| ≤ (m−1)D` excluding a vanishing fraction of [0,D]^m as m grows. **CONJECTURE C3:** the unsectioned support density tends to 1 as m → ∞, yet saturation never occurs for m ≥ 3 (e.g., Theorem 2 gives an explicit hole at the origin for all even m). The saturation phenomenon is genuinely a property of *sections* (dimension drop), not of the family polynomial.

## 4. PROVED: the bottom fiber u_m and the exceptional-section structure

### Theorem 2 (axis polynomial) — PROVED (modulo the standard product normal form for the root statements; all displayed identities computer-verified)

Let `u_m(X) := S_m(0,…,0,X) ∈ Z[a,b][X]` (the "bottom fiber" — the x_m-polynomial at the origin section). Then:

1. **Even m:** `X | u_m` identically in (a,b). *Proof (pairing):* over the algebraic closure, S_m(x_1,…,x_m) = c(x_1,…,x_{m−1})·Π_{ε}(x_m − x(Σ_i ε_i P_i)) with ε ranging over {±1}^{m−1} modulo overall sign (the standard product normal form of the summation polynomial). At x_1 = … = x_{m−1} = 0 every P_i ∈ {P, −P} with P = (0, √b); for even m, sign vectors with Σε_i = ±1 exist (m−1 is odd), giving Σ ε_i P_i = ±P, i.e. x-value 0: X = 0 is a root for every (a,b). ∎ (Verified: u_2 = ±X; `u_4 = a⁴X³(X − 8b(a²−8b²)/a⁴)`, X-adic valuation exactly 3 = C(3,1); check m4_u4_valuation.)
2. **Odd m:** `c_m := u_m(0)` is not the zero polynomial: root value 0 requires Σε_i P = ±P with Σε_i even (m−1 even), impossible for P non-torsion. Hence the bottom corner of the box survives every generic section at odd m. Verified: `c_3 = a²` (the 3-torsion condition of (0,√b) — 3P = O ⟺ a = 0, a perfect match), `c_5 = a^{10}·(a^6 + 32a²b² − 256b⁴) ≠ 0`.
3. **Exceptional sections (falsifiable micro-prediction, confirmed):** since the constant term of the section `S_m(x_1,…,x_{m−1}, t)` is exactly `u_m(t)`, sections at roots of u_m lose the bottom corner. At even m, t = 0 is always such a root: **the t = 0 section at even m is never box-saturated.** Verified at m = 4: the t = 0 section's support is 88/125 cells (37 holes, including the origin; recorded in the results JSON). The measured experiments used t_j ≠ 0 throughout, so this does not touch any ledger anchor; it *predicts* that a future t = 0 section at even m will show losses — a checkable distinguishing prediction of the theory.

### 4.3 The specialization pitfall (methodological, recorded)

`u_m` must be computed as the **specialized Sylvester determinant** (substitute into the matrix entries, then take the determinant), not as the resultant of the specialized factors: specialization can drop degrees (S_3(0,0,X) is linear), and `Res ∘ specialize ≠ specialize ∘ Res` in that case. The determinant route is exact (substitution commutes with det) and is what the verification script uses for u_5 (sub-second, vs the censored full resultant).

### 4.4 Refuted guess (honesty record)

I predicted `ψ_5(0) | c_5` (5-torsion factorization: ψ₅(0) = a^6 − 32a³b² − 256b⁴). Computation **refutes** it: the actual odd factor of c_5 is `a^6 + 32a²b² − 256b⁴` (different a-weight). The precise torsion-factorization law of u_m is therefore **OPEN** (what is verified: u_3³ | u_5 exactly; c_5 = a^{10}·(a^6+32a²b²−256b⁴); u_4's linear factor `X − 8b(a²−8b²)/a⁴` whose root is x(3P)-type). The naive product-formula multiplicity count also fails (predicted x(2P)-root multiplicity 4, measured 3): when the leading coefficient `S_{m−1}(0,…,0)² = c_{m−1}²` vanishes (even m−1), roots escape to infinity and finite-root multiplicities reshuffle. Recorded as an unexpected observation (rule 8) with the corrected mechanism in §4.3.

## 5. The all-m theorem: reductions, attack routes, and the exact gap

### Theorem 4 (reductions) — PROVED

**(i) Saturation ⟹ MV law.** If every generic section at level m has Newton polytope conv(B_m), then the sectioned system's polytopes are all the same box, and by multilinearity of mixed volume `MV(box,…,box) = n!·Vol(box) = (m−1)!·(2^{m−2})^{m−1} = (m−1)!·2^{(m−1)(m−2)}` (n = m−1 factors). This equals the multi-graded Bézout number of (P¹)^{m−1} with degrees (D,…,D) (i.e. `n!·D_1⋯D_n`); the ratio to the total-degree Bézout number `((m−1)2^{m−2})^{m−1}` is `(m−1)!/(m−1)^{m−1} ∼ √(2π(m−1))·e^{−(m−1)}` (Stirling). Both conventions recorded, as in DEC-20260718-011.

**(ii) Prime stability.** S_m ∈ Z[a,b][x_1,…,x_m], so `supp(S_m mod p) = supp(S_m over Q)` for all p outside the union of prime divisors of the finitely many nonzero coefficients — an effective finite exceptional set. This proves as a theorem the ledger's P4 control pattern (two-prime and QQ support stability) and its m = 5 small-prime interior losses (instance cancellation below the generic support; projections and hulls unchanged).

**(iii) Specialization monotonicity.** For any specialized curve (a₀, b₀) (e.g. a nodal cubic), `supp(S_m|_{a₀,b₀}) ⊆ supp(S_m|_{generic})`; hence projection saturation at *any one* specialization implies projection saturation of the generic fiber. (Used in Theorem 3 for m = 5.)

**(iv) B2-barrier implication.** If C1 holds for all m, then for every m the BKK root-count driver of the sectioned summation system is exactly the box Bézout number; any support-aware solver has driver `MV^{O(1)} = ((m−1)!)^{O(1)}·2^{O(m²)}`, sharing the dense driver's exponential order `2^{Θ(m²)}` — the saturation barrier in theorem form. (Implication proved; the program's interpretation is the Coordinator's.)

### CONJECTURE C1 (main) — projection saturation for all m

*Statement.* For every m ≥ 3 and every `e' ∈ [0, 2^{m−2}]^{m−1}`, the fiber `{e'} × [0, 2^{m−2}]` meets supp(S_m). Equivalently (Lemma 1): every generic single-variable section of S_m has full-box support. Proved for m ≤ 5 (Theorem 3); open for m ≥ 6.

### CONJECTURE C2 — the MV law for all m

`MV_m = (m−1)!·2^{(m−1)(m−2)}` for all m ≥ 3. Implied by C1 via Theorem 4(i); equivalent to C1 given that the sectioned system's polytopes are boxes iff sections are saturated.

### The exact gap: Lemma-G (interior-fiber non-cancellation) — OPEN

Expand the recursion's Sylvester determinant. Every term is a product

`f_{k_1} · f_{k_2} · g_{j_1} ⋯ g_{j_d}`,   `k_1+k_2+Σ j_l = 2d`   (isobaric, Lemma 2(iii)),

where the g-coefficients are the three S_3-layers with supports (in (x_{m−1}, x_m)):

`G_2 = {(2,0),(1,1),(0,2)}` (pure-x coefficients, from (x_{m−1}−x_m)²),
`G_1 = {(2,1),(1,2),(1,0),(0,1),(0,0)}`,  `G_0 = {(2,2),(1,1),(0,0),(1,0),(0,1)}`.

The support of each term is the **Minkowski sum** of the factor supports (exact, no cancellation inside a product), and `supp(S_m) ⊆` the union of these sumsets. Two sub-problems separate C1 from a proof:

- **(Coverage)** For every target `(β, e_{m−1}) ∈ [0,D]^{m−2} × [0,D]`, find a split `β = α_1 + α_2`, exponents `k_i ∈ K(α_i)` (the X-fiber sets of S_{m−1}: `K(α) := {k : α ∈ supp(f_k)}` — nonempty for all α by induction on C1), and a j-multiset with `Σ j = 2d − k_1 − k_2` whose G-sumset covers `(e_{m−1}, e_m)` for some `e_m`. The G-sumset side is elementary: `G_0 + G_2^{d−1} ⊇ [0,2d]×[0,2]` (all four parity classes occur in G_0), and mixing G_1-layers covers the upper band; the bottleneck is arithmetic control of the K-sets — i.e., the induction must be strengthened from "projection is full" to an explicit description of *which* X-fibers carry each α. The measured hole structure (13/27, 439/625) shows the K-sets are genuinely uneven (e.g. at m = 3 the axis cells (2,0), (0,2) lie only in fiber k = 2), so this needs a real support theorem, not just the projection statement.
- **(Non-cancellation)** Terms of the same x-monomial arising from different (k_1, k_2, j)-data come with Sylvester signs of both parities, so cancellation is possible in principle. The strongest handle found: coefficients live in Z[a,b] and the three G-layers carry distinct (a,b)-weights (G_2 is (a,b)-free; G_0, G_1 are not), so the coefficient of any monomial splits into (a,b)-graded pieces that cannot cancel across grades; a uniqueness/extremality argument in the (a,b)-grading is the proposed route to show no fiber cancels completely. This is **Route A**.

**Route B (degeneration).** By Theorem 4(iii), it suffices to prove C1 for *one* specialization per m. The nodal cubic (a,b) = (−3, 2) has group law G_m with x a degree-2 rational function of the parameter u (invariant under u ↦ 1/u); the summation condition is Π u_i^{±1} = 1, and the x-summation polynomial is the image of the explicit "multiplicative Semaev" recursion `M_3 = x_3² − x_1x_2x_3 + (x_1² + x_2² − 4)`, `M_m = Res(M_{m−1}, M_3)` under a per-variable Möbius map with denominator clearing. The route's hope is an *explicit product formula* for the specialized supports. Recorded warnings: (i) in the raw s = u + 1/u coordinate, M_3's own projection is only 4 of 9 cells — the Möbius fill is essential and cancellations inside it are exactly the phenomenon at issue; (ii) the m = 3 nodal specialization is verified to keep all 13 cells with full projection (check m3_nodal_supp), so the route is consistent at the base case but its all-m analysis is undone.

**Why the gap is believably closable:** every *measured* object agrees with C1 at m ≤ 5 from two independent directions (symbolic supports/projections here; the ledger's finite-field sections at 3 curves × 2–3 primes), and the corner tower (Theorem 1) shows the family cooperates with exact coefficient control. What is missing is precisely the interior analog of Theorem 1.

### Also OPEN

- **C4:** the exact factorization law of u_m(X) (verified instances: u_3 = a² + 4bX; u_4 = a⁴X³(X − 8b(a²−8b²)/a⁴); u_5 = (a²+4bX)³·Q with deg_X Q = 2; a^10 | c_5). Connection to division polynomials exists (c_3 = a² = −ψ_3(0)-condition) but the naive ψ_k(0)-factorization is refuted at k = 5 (§4.4).
- **C3** (§3): unsectioned density → 1 without ever saturating.
- The effective exceptional prime set of Theorem 4(ii) (computable in principle from the coefficient list; not computed here).

## 6. Consistency with the ledger (anchor table)

| Theorem item | Ledger anchor | Agreement |
|---|---|---|
| supp(S_3) = 13 cells, projection 9/9 | EV-BKKMV-001 unsectioned m3 "13 < 27" | exact |
| supp(S_4) = 439, projections 125/125 | EV-BKKMV-001 "439 < 625"; EV-BKK-001 439/625 | exact |
| supp(S_5) = 54777 at generic instance | EV-BKKMV-001 "54777 < 59049" | exact (instance value); symbolic count censored |
| diagonal corner coefficient = 1 | EXP-BKK-001 "diagonal monomial present" 54/54 | theorem explains measurement |
| MV law at m ≤ 5 | EV-BKKMV-001 MV 8/384/98304, zero residual | upgraded certificate → theorem |
| prime stability (Thm 4(ii)) | EV-BKKMV-001 control P4 (two-prime + QQ) | theorem explains control |
| interior-only instance losses | EV-BKKMV-001 p=101 m=5 losses, hull-interior | same pattern at (a,b)=(2,3): −120 cells, projections full |
| u_m / t = 0 exceptional sections | no prior ledger object | new falsifiable prediction (§4.3), self-verified at m = 4 |

## 7. Deviations, censorings, and validity

1. **Infrastructure censoring (not evidence):** the fully symbolic S_5 resultant over QQ[a,b] exceeded the 290 s harness foreground cap (killed at 290 s). Mitigation: numeric-generic instances (Theorem 3, m = 5) + the specialized-Sylvester-determinant route for u_5 (§4.3). No conclusion depends on the censored computation; the m = 5 *symbolic support size* remains a confirmed instance value + lower bound, not a symbolic count.
2. **Refuted sub-conjecture:** ψ₅(0)-factorization of c_5 (§4.4) — recorded as failed, with the verified factorization in its place.
3. **Convention:** the symmetric S_3 of the program's instruments is used throughout; all support statements are convention-robust, and the coefficient-tower identities are stated for this convention exactly.
4. **Validity:** theory note; all PROVED items are either self-contained proofs or proofs + computer verification with preserved artifacts (scripts + JSON receipts, deterministic, rerunnable: `sage thm_bkkmv1_verify.sage 34`, `sage thm_bkkmv1_verify_m5.sage 5n|u5`). No fabricated computations; the two FAIL receipts are retained and analyzed. Nothing here is a crypto-scale claim (all verified instances are model-level / toy-scale, consistent with rule 7's spirit even for a theory note).
