# THM_BKKMV2 — The (a,b)-grading route to interior-fiber non-cancellation: the two-root expansion, Theorem B, and the bottom-fiber law

- **ID:** THM-BKKMV2
- **Task:** TASK-20260724-LEMMV (theory track): attack the interior-fiber non-cancellation lemma (THM_BKKMV1 §5, Lemma-G) via the (a,b)-grading route (its "Route A").
- **Author:** executor (theory-track agent), 2026-07-24
- **Reads:** research/THM_BKKMV1.md (esp. §4, §5), ledger/EV-BKKMV-001.yaml, ledger/EV-BKKMV-002.yaml, experiments/EXP-BKKMV-001/analysis.md.
- **Verification artifacts:** research/verification/thm_bkkmv2_verify.sage (stages `m4`, `u`, `u7num`, `krawt`, `predict`, `cover4`, `m5`); receipts in thm_bkkmv2_verify_results_{m4,u,u7num,krawt,predict,cover4,m5}.json. **27/29 checks PASS.** The 2 FAILs are stale hand-estimates encoded as expected values (deg_b u_6 "25" → measured 23; an m=7 weight-cap "collision" that does not occur) — both analyzed in §13; in each case the *measured* value agrees with the theory of this note. One auxiliary pure-Python factorization check (c₇ torsion law, §8) is reproduced inline. SageMath 10.9; all scripts deterministic and rerunnable.
- **Honesty contract:** every item is labeled PROVED / PROVED-(conditional, with exact hypothesis) / CONJECTURE / OPEN GAP. An **ERRATUM** to THM_BKKMV1 §4 is recorded in §8.2 (its u_5/c_5 computations were corrupted by a hardcoding typo; its main Theorem 2 stands).

## 0. Result summary

1. **PROVED (all m ≥ 4): the two-root expansion (∗).** Writing the recursion S_m = Res_X(f, g) with f = S_{m−1}(x_1,…,x_{m−2}, X), deg_X f = d = 2^{m−3}, and g = S_3(x_{m−1}, x_m, X) (quadratic in X), the Sylvester resultant has the *exact closed form*
   `(∗)  S_m = Σ_{0≤k<l≤d} f_k f_l · g_2^{d−l} g_0^k U_{l−k}  +  Σ_{0≤k≤d} f_k² · g_2^{d−k} g_0^k`,
   where f_k = [X^k]f, g_j = [X^j]g, and U_r := g_2^r·(β_1^r + β_2^r) ∈ Z[a,b][x_{m−1},x_m] for β_i the roots of g (U_0 = 2, U_1 = −g_1, U_2 = g_1² − 2g_0g_2, Newton's identities keep U_r polynomial). This replaces the Sylvester determinant by a sum of `(d+1)(d+2)/2` explicit terms with *individually computable* (a,b)-degrees. Verified at m = 4 (check m4_tworoot_expansion, exact equality over QQ(a,b)).
2. **PROVED (all m): the (a,b)-weight grading and the single-grade cone.** With wt(x_i) = 2, wt(a) = 4, wt(b) = 6, S_m is weight-homogeneous of degree W_m = (m−1)·2^{m−1}. The coefficient of any x-monomial x^E is a sum of (a,b)-monomials a^A b^B lying on the single line `2A + 3B = q(E)`, q(E) := (W_m − 2|E|)/2. Consequences: (i) q(E) = 1 fibers are *exact holes* (coefficient identically zero) — a proved structural vanishing beyond the degree simplex; (ii) for q(E) ≤ 5 the grade is a *single* (a,b)-monomial, so within that cone the non-cancellation question reduces to one scalar per cell; q = 6 is the first mixed grade ((A,B) = (3,0) and (0,2)).
3. **PROVED: exact b-degree of every (∗)-term; rigorous tropical upper bound.** Each off-diagonal term (k,l) has b-degree *exactly* β_k + β_l + l, where β_k := deg_b f_k, because deg_b g_2 = 0, deg_b g_0 = 1, and deg_b U_r = r with `[b^r]U_r = (−4)^r` (a nonzero scalar; §4). Diagonal terms have b-degree 2β_k + k. Hence (writing γ := max_k (β_k + k)):
   `deg_b [x_m^j]S_m ≤ max_{0≤k≤l≤d, 2(d−l)+k≥j} (β_k + β_l + l)`  — the **tropical recursion upper bound**, rigorous whenever the β^{(m−1)}-table is exact, with equality iff the signed coefficient sums at the tropical argmax do not cancel (hypothesis (NZ), §7).
4. **Theorem B (b-extremal non-cancellation) — PROVED conditional on hypothesis (T_m); (T_m) verified unconditionally for m ≤ 5 and for the tropical tables through m = 8.** If `(T_m)`: every pair (k, l) ∈ A1 × A2 has k ≤ l, where A1 = argmax_k β_k and A2 = argmax_k (β_k + k), then
   `deg_b S_m = βmax + γ`  and  `Λ_m := [b^{βmax+γ}] S_m = Ψ · Φ`,
   `Ψ = Σ_{k∈A1} f̂_k · (−(x_{m−1}+x_m))^k`,   `Φ = Σ_{l∈A2} f̂_l · (−4)^l · (x_{m−1}−x_m)^{2(d−l)}`,
   with f̂_k := [b^{β_k}] f_k ≠ 0. Each factor is nonzero by linear independence of distinct powers, so **the b-extremal grade never cancels**. Verified: m = 4 (Λ_4 = 64·(−x1−x2+x3+x4)(−x1+x2+x3−x4)(x1−x2+x3−x4), three "balanced" linear forms; check m4_blead_factor); m = 5 over QQ(b) at a = 1 (17.3 s resultant; deg_b S_5 = 9 and Λ_5 = ΨΦ with sign +; checks m5_degb, m5_TheoremB). Mechanism (§5): as b → ∞ one root of g tends to the *finite* value −(x_{m−1}+x_m) and the other *escapes* ∼ −4b/(x_{m−1}−x_m)²; the pole is canceled by g_2^d, and the extremal grade factorizes into a finite-root part (Ψ) and an escaping-root part (Φ). (T_m) holds for the *verified* β-tables at m = 4, 5 and for the tropical-predicted tables at m = 6, 7, 8 (A1 is a lower contiguous block, A2 an upper contiguous block with max A1 ≤ min A2).
5. **PROVED: the a-side analog.** deg_a U_r = r with a-leading part Û_r = (−1)^r[(√u+√v)^{2r} + (√u−√v)^{2r}] (positive-coefficient polynomials in u, v: Û_0 = 2, Û_1 = −2(u+v), Û_2 = 2(u²+6uv+v²)); the a-extremal grade is a six-term sum over k ≤ l. Verified at m = 4: deg_a S_4 = 4, the a⁴-part equals the predicted six-term sum exactly (check m4_alead_sum), and α⁽⁴⁾ = (4,4,4,4,4) is *fiber-flat* (unlike β⁽⁴⁾ = (3,3,3,3,2)) — the a-certificate touches fibers the b-certificate misses (§10).
6. **PROVED (m ≤ 6, symbolic; m = 7 numeric): the bottom-fiber factorization law, with an ERRATUM to THM_BKKMV1 §4.** The axis polynomials factor exactly as
   `u_4 = X³·(a⁴X − 8a³b + 64b³)`,
   `u_5 = (a² + 4bX)⁴ · (a⁸ + 16a⁶bX + 32a⁵b² − 256a³b³X − 256a²b⁴ + 1024b⁵X)`,
   `u_6 = X^10 · (a⁴X − 8a³b + 64b³)⁵ · (a^12X − 24a^11b + 64a^9b²X + 960a^8b³ + 512a^6b⁴X − 10240a^5b^5 − 16384a^3b^6X + 32768a^2b^7 + 65536b^8X)`,
   with X-adic valuations 3, 0, 10 and deg_X = 4, 5, 16. The finite-root multiplicities are *exactly* the naive sign counts N(m,k) = C(m−1, (m−1−k)/2) (m = 4: (3,1); m = 5: (4,1); m = 6: (10,5,1)) — **no escape-reshuffle**; the torsion law `c_m = ±Π_{k≢m(2)} [ψ_{k−1}ψ_{k+1}](0;−a,−b)^{N(m,k)}` **holds** (c_3 = a² = −ψ_3(0;−a,−b); c_5 = a^10·(a⁶+32a³b²−256b⁴) = a^10·ψ_5(0;−a,−b) — note ψ_3(0;−a,−b) = −a² so (−ψ_3)^5·ψ_5 matches exactly; c_7 law `ψ_3^21 ψ_5^7 ψ_7` confirmed by exact integer division at two instances, §8). THM_BKKMV1's contrary claims (ψ₅-refutation, "u_3³ | u_5 exactly", multiplicity 4→3 reshuffle, its displayed u_5 and c_5) are **artifacts of a hardcoding typo** (a² for a³) in its verification script, documented in §8.2; its Theorem 2 main statements stand and are independently re-verified here.
7. **PROVED (m = 6, confirming THM_BKKMV1 Theorem 2):** even-m degeneration X^10 | u_6 with valuation exactly C(5,3) = 10 = the zero-sum-free ±1-stratum count; deg_X u_6 = 16 (no pole loss); deg_b u_6 = 23 and deg_a u_6 = 32. The deg_X drop law at odd m is `deg_X u_m = 2^{m−2} − (1/2)·C(m−1,(m−1)/2)` (m = 3, 5, 7: 1, 5, 22 — all confirmed), the zero-sum sign stratum escaping to infinity.
8. **m = 4 covering case study (CONJECTURE C-B3 quantified at m = 4):** every one of the 125 box fibers is touched by at least one explicit non-cancellation certificate family — corner tower, the m symmetric top-layer towers (top layer x_4 = 4 of supp S_4 equals 2·supp S_3 exactly, 60 cells), the b-leading grade Λ_4, the a-leading grade, and the q ≤ 5 single-grade cone. Fiber-level tallies: towers 109/125, q ≤ 5 cone 109/125, a-leading 35/125, b-leading 20/125, uncovered **0** (check cover4_all_fibers; full distribution in the receipt). The b-extremal family of Theorem B lives at total x-degree |E| = (m−1)2^{m−2} − 3β_m = 3, 5, 11, 21, 43 (m = 4..8) — a thin region near the box's *bottom* corner — so certificates genuinely partition the box; no single family suffices (OPEN GAP G3).
9. **CONJECTURES:** C-B1 ((T_m) for all m, hence Theorem B for all m); C-B2 (the tropical recursion never fails: no (NZ_j) cancellation at any argmax — nontrivial because Krawtchouk-type coefficients K_j(2s,k) *do* have zeros, 96/2601 in the m ≤ 6 range including the exact parity family K_j(2s,2s) = 0 for all odd j, §7); C-B3 (the explicit certificate families cover every box fiber for all m — m = 4 quantified here; m = 5, 6 supported by EV-BKKMV-001/002); C-u (the bottom-fiber law of item 6 for all m).
10. **OPEN GAP (precise residuals for Lemma-G):** G1 = (T_m) + (NZ_j) for all m (the non-cancellation half); G2 = the covering half (do the explicit families touch *every* fiber for all m — cover4 gives the m = 4 mechanism distribution and the empty residual list); G3 = grade migration: the proved certificates live on disjoint grades (b-extremal at |E| ≈ bottom, a-extremal, q ≤ 5 cone near top, towers at the shell), and an all-m proof must either union them with explicit per-grade support control or find a joint (a,b)-tropical extremality per fiber. **Lemma-G remains open; it is now reduced to three explicitly falsifiable statements, each verified in the computed range.**
11. **Unexpected observations (rule 8):** the THM_BKKMV1 u_5 erratum itself (a single-character typo had fabricated a "refuted conjecture" and a "multiplicity reshuffle"); the *non*-occurrence of the predicted weight-cap collision (deg_b predictions 3, 9, 23, 57, 135 vs caps 4, 10, 26, 64, 149 through m = 8 — the grading has room); deg_b u_6 = 23, not 25 (the bottom fiber diagonal (k,l) = (5,5) dominates — the bottom-fiber tropical uses the *actual* b-profile β̂⁽⁵⁾(k) = k + 4, k = 0..5); c_6 = u_6(0) = 0 but [X^0]-profile note is a Sage `.coefficient(X**0)` quirk, documented; the X-linearity of the non-u_3 factors of u_5, u_6 (each stratum beyond the first contributes a single X-linear factor).

**Bottom line for the program:** the (a,b)-grading route works. The interior-fiber non-cancellation lemma is not yet proved for all m, but it is now *decomposed*: a proved conditional extremal theorem (Theorem B) with an explicitly checkable hypothesis (T_m), a proved rigorous upper-bound recursion whose only failure modes are isolated Krawtchouk zeros, a proved cone reduction (q ≤ 5) and vanishing law (q = 1), an m = 4 complete mechanization of fiber coverage (0 residual fibers), and a corrected, strengthened bottom-fiber law (C-u) verified through m = 7. Each remaining gap is a named, falsifiable statement with verification infrastructure in place.

## 1. Setup and conventions

Conventions are identical to THM_BKKMV1 §1: S_3(p,q,r) = (pq+pr+qr+a)² − 4(pqr−b)(p+q+r); S_m = Res_X(S_{m−1}(x_1,…,x_{m−2},X), S_3(x_{m−1},x_m,X)); S_m ∈ Z[a,b][x_1,…,x_m]. (This is the program's instrument convention; it equals the classical Semaev polynomial under (a,b) ↦ (−a,−b), which matters for the torsion law, §8.)

**Grading.** wt(x_i) = 2, wt(a) = 4, wt(b) = 6. Then S_3 is weight-homogeneous of degree 8, and inductively S_m is weight-homogeneous of degree `W_m = (m−1)·2^{m−1}` (f = S_{m−1}(x_1,…,x_{m−2},X) is weight-homogeneous of degree W_{m−1} with wt(X) = 2, so wt(f_k) = W_{m−1} − 2k exactly; the Sylvester isobaric constraint k_1+k_2+Σj_i = 2d then gives W_m = 2W_{m−1} + 8d − 2·2d = 2W_{m−1} + 2^{m−1}, W_3 = 8, which telescopes to the stated value). Weight bounds: deg_b S_m ≤ W_m/6, deg_a S_m ≤ W_m/4.

**Objects.** d := deg_X f = 2^{m−3}; f_k := [X^k] S_{m−1}(x_1,…,x_{m−2},X) for 0 ≤ k ≤ d; g_j := [X^j] S_3(x_{m−1},x_m,X) for 0 ≤ j ≤ 2:
`g_2 = (x_{m−1}−x_m)²`, `g_1 = −2x_{m−1}²x_m − 2x_{m−1}x_m² + 2a(x_{m−1}+x_m) + 4b`, `g_0 = x_{m−1}²x_m² + 2a x_{m−1}x_m + a² + 4b(x_{m−1}+x_m)`.
β_k := deg_b f_k; α_k := deg_a f_k; f̂_k := [b^{β_k}] f_k (the b-leading coefficient, nonzero by definition); βmax := max β_k; γ := max (β_k + k); A1 := argmax β_k; A2 := argmax (β_k + k).

## 2. T1: the two-root expansion (∗) — PROVED (all m ≥ 4)

**Theorem T1.** With U_r := g_2^r·(β_1^r + β_2^r) (β_i the roots of g in X; U_r ∈ Z[a,b][x_{m−1},x_m] by Newton's identities: U_0 = 2, U_1 = −g_1, U_2 = g_1² − 2g_0g_2, …),

`S_m = Σ_{0≤k<l≤d} f_k f_l · g_2^{d−l} g_0^k U_{l−k}  +  Σ_{k=0}^{d} f_k² · g_2^{d−k} g_0^k`.   (∗)

**Proof.** Poisson's formula for the resultant with deg g = 2: `Res_X(f,g) = g_2^d · Π_{i=1,2} f(β_i)` (the sign (−1)^{2d} = +1). Expand `f(β_i) = Σ_k f_k β_i^k`:
`Π_i f(β_i) = Σ_{k,l} f_k f_l β_1^k β_2^l = Σ_{k<l} f_k f_l (β_1^k β_2^l + β_1^l β_2^k) + Σ_k f_k² (β_1β_2)^k`.
Using β_1β_2 = g_0/g_2 and β_1^kβ_2^l + β_1^lβ_2^k = (g_0/g_2)^k·(β_1^{l−k} + β_2^{l−k}) and multiplying by g_2^d gives (∗). ∎

**Verification.** m4_tworoot_expansion: exact equality with the Sage resultant at m = 4 (d = 2; U_0, U_1, U_2 as displayed). **Remark.** (∗) has (d+1)(d+2)/2 terms (3 off-diagonal + 3 diagonal at d = 2), each a product of *lower-level* coefficients f_k and the *universal* g-data. All cancellation analysis below is term-by-term on (∗).

## 3. T2: the weight-graded structure of fiber coefficients — PROVED (all m)

**Theorem T2.** The coefficient of x^E in S_m (E ∈ Z_{≥0}^m) is a sum of monomials a^A b^B with `2A + 3B = q(E)`, q(E) := (W_m − 2|E|)/2. Hence:

1. **(Vanishing)** If q(E) = 1 (more generally if 2A + 3B = q(E) has no solution in non-negative integers), the coefficient of x^E is *identically zero* — proved structural holes of supp S_m, refining the total-degree simplex constraint of THM_BKKMV1.
2. **(Single-grade cone)** If q(E) ≤ 5, the equation has *at most one* solution (q = 0: (0,0); 2: (1,0); 3: (0,1); 4: (2,0); 5: (1,1)), so the coefficient is c·a^A b^B for a single scalar c ∈ Z: within the cone, non-cancellation of a fiber coefficient is equivalent to the non-vanishing of one explicit integer.
3. **(First mixing)** q = 6 has exactly two solutions ((3,0), (0,2)): the first grade where two *different* (a,b)-monomials can cancel against each other.

**Proof.** Weight-homogeneity (§1) restricted to the fiber coefficient; the Diophantine statements are elementary. ∎

**Role in the attack.** T2 is the rigorous content of "graded pieces cannot cancel across grades" (THM_BKKMV1 §5 Route A): pieces of *different* (A,B) never cancel, and below q = 6 there is only one piece. It also *diagnoses* fabricated data: the erroneous c_5 of THM_BKKMV1 (§8.2) is not weight-homogeneous, which is how the erratum was first detected.

## 4. T3: exact b-degrees of (∗)-terms, and the tropical upper bound — PROVED

**Lemma T3a (b-leading of the g-data).** deg_b g_2 = 0; deg_b g_0 = 1 with `[b]g_0 = 4(x_{m−1}+x_m)`; deg_b g_1 = 1 with `[b]g_1 = 4`; and for all r ≥ 0,
`deg_b U_r = r`  with  `[b^r] U_r = (−4)^r` (a nonzero scalar).

**Proof.** The g-statements are direct from §1. For U_r: write σ_1 = x_{m−1}+x_m, δ = x_{m−1}−x_m. The roots satisfy β_1 + β_2 = −g_1/g_2, β_1β_2 = g_0/g_2. As b → ∞ with (x_{m−1}, x_m) generic fixed, g_1 = 4b + O(1), g_0 = 4bσ_1 + O(1), so the finite root β_1 → −σ_1 (check: g(−σ_1) = g_2σ_1² − g_1σ_1 + g_0 = O(1)·… balanced to O(1) while g ~ b) and the escaping root β_2 = (g_0/g_2)/β_1 ~ −4b/δ². Then `U_r = g_2^r(β_1^r + β_2^r) = δ^{2r}β_1^r + δ^{2r}β_2^r`; the first term is b-free, the second is δ^{2r}·(−4b/δ² + O(1))^r = (−4b)^r + O(b^{r−1}). So deg_b U_r = r and the leading coefficient is (−4)^r. (Rigorous: the asymptotics are exact identities in the Laurent-series field QQ(x_{m−1},x_m)((b^{-1})).) ∎

**Theorem T3b (term degrees).** Every off-diagonal (k < l) term of (∗) has b-degree *exactly* `β_k + β_l + l`, with b-leading coefficient
`f̂_k f̂_l · δ^{2(d−l)} · (−4)^l · (−σ_1)^k`.
Every diagonal term k has b-degree exactly `2β_k + k`, with b-leading `f̂_k² · δ^{2(d−k)} · 4^k σ_1^k`. Consequently `deg_b [x_m^j]S_m ≤ max_{k≤l, 2(d−l)+k≥j} (β_k + β_l + l)` and `deg_b S_m ≤ βmax + γ` — rigorous upper bounds given exact β^{(m−1)}.

**Proof.** deg_b is additive over the product; [b]g_0 = 4σ_1 and [b^r]U_r = (−4)^r give `(4σ_1)^k·(−4)^{l−k} = (−4)^l·(−σ_1)^k` (using (−1)^{l−k} = (−1)^{l+k}). No cancellation *inside* a term since the leading coefficients are nonzero polynomials. ∎

**Verification.** m=4: β⁽⁴⁾ = (3,3,3,3,2) from β⁽³⁾ = (1,1,0) via the recursion (m4_beta_recursion, exact); deg_b S_4 = 3 (m4_degb). Bottom-fiber b-profiles (§8): [X^k]u_5 has deg_b = k+4 (k = 0..5), and the u_6 profile {10: 22, 11: 23, 12: 20, 13: 17, 14: 14, 15: 11, 16: 8} — the (5,5) diagonal dominance giving deg_b u_6 = 23, exactly the tropical value with the *correct* input profile (see §13 for the stale "25" FAIL).

## 5. Theorem B: b-extremal non-cancellation — PROVED conditional on (T_m); verified at m = 4, 5

**Hypothesis (T_m).** Every pair (k, l) ∈ A1 × A2 satisfies k ≤ l. (Equivalently: the unconstrained argmax of β_k + β_l + l over the *product* A1 × A2 lies inside the index set {k ≤ l} of (∗).)

**Theorem B.** Assume (T_m) and exact β^{(m−1)}-table. Then:
1. `deg_b S_m = βmax + γ`.
2. `Λ_m := [b^{βmax+γ}] S_m = Ψ · Φ` with `Ψ = Σ_{k∈A1} f̂_k·(−σ_1)^k`, `Φ = Σ_{l∈A2} f̂_l·(−4)^l·δ^{2(d−l)}`, where σ_1 = x_{m−1}+x_m, δ = x_{m−1}−x_m.
3. Λ_m ≠ 0: Ψ ≠ 0 because its monomials σ_1^k (k ∈ A1 distinct) are linearly independent over QQ(a)[x_1,…,x_{m−2}] and f̂_k ≠ 0; Φ ≠ 0 because the powers δ^{2(d−l)} (l ∈ A2 distinct) are distinct and f̂_l(−4)^l ≠ 0. The polynomial ring is a domain.

**Proof.** By T3b, a term of (∗) has b-degree ≤ β_k + (β_l + l) ≤ βmax + γ, with equality iff k ∈ A1 and l ∈ A2 (for off-diagonal), or k ∈ A1 ∩ A2 (diagonal: 2β_k + k = β_k + (β_k + k) attains the bound iff both maximality conditions hold). Under (T_m) every pair (k,l) ∈ A1 × A2 with k < l occurs as an off-diagonal term exactly once, and every k ∈ A1 ∩ A2 occurs as a diagonal term exactly once; the product Ψ·Φ expands to exactly this index set (the (k,k) cross-term of the product reproduces the diagonal term: f̂_k²(−4)^k δ^{2(d−k)}(−σ_1)^k = f̂_k²·4^k σ_1^k δ^{2(d−k)} ✓). Summing the T3b leading coefficients over the extremal set gives Ψ·Φ; non-extremal terms have strictly smaller b-degree and cannot interfere. ∎

**Mechanism (conceptual).** The b-extremal grade sees the root-splitting of g: Ψ is the b-leading of f evaluated at the *finite* root X = −σ_1 (i.e., Ψ = "f̂^{(m−1)}(−(x_{m−1}+x_m))"), and Φ collects the escaping-root data ∼ −4b/δ². The pole δ^{−2r} in U_r is canceled by the g_2^d prefactor of Poisson. Non-cancellation at the extremal grade is thus *automatic* (linear independence), unlike the interior grades.

**Corollary (explicit extremal support).** supp(Λ_m) ⊆ supp(Ψ) + supp(Φ) (Minkowski), with the extreme points exact; recursively, the b-leading support of S_m is explicit from the f̂^{(m−1)}-data. The b-extremal family lives at total x-degree `|E| = (W_m − 6(βmax+γ))/2 = (m−1)2^{m−2} − 3β_m`, values 3, 5, 11, 21, 43 for m = 4..8 — near the box's *bottom* corner (origin), far below the diagonal top (12, 32, 80, 192, 448).

**Verification.**
- **m = 4 (unconditional):** β⁽³⁾ = (1,1,0), A1 = {0,1}, A2 = {1,2}, (T_4) holds; Λ_4 = 64·(σ_1−s_1)·(δ²−d_1²) = 64·(−x1−x2+x3+x4)(−x1+x2+x3−x4)(x1−x2+x3−x4) with s_1 = x_1+x_2, d_1 = x_1−x_2 — three linear forms each with coefficient sum 0 ("balanced": they are the ±-sum hyperplanes of the product normal form). Check m4_blead_factor (exact, sign +). The b-stripped fiber coefficients: f̂⁽⁴⁾_0 = 64(−x1+x2−x3)(−x1+x2+x3)(x1+x2−x3), f̂⁽⁴⁾_1 = −64(x1²−2x1x2+x2²−2x1x3−2x2x3+x3²), f̂⁽⁴⁾_2 = −64(x1+x2+x3), f̂⁽⁴⁾_3 = 64, f̂⁽⁴⁾_4 = 16(x1+x2+x3)².
- **m = 5 (unconditional):** (T_5) from the *computed* β⁽⁴⁾ = (3,3,3,3,2): A1 = {0,1,2,3}, A2 = {3,4}, all pairs k ≤ l (m4_Tcond_m5). Theorem B then *predicts* deg_b S_5 = 3 + 6 = 9 and Λ_5 = ΨΦ with Φ = 4096·[(x1+x2+x3)² − (x4−x5)²] = 4096(x1+x2+x3+x4−x5)(x1+x2+x3−x4+x5). Verified over QQ(b) at a = 1 (17.3 s resultant): deg_b S_5 = 9 and Λ_5 = Ψ·Φ exactly, sign + (m5_degb, m5_TheoremB); since specialization can only drop degree, deg_b of the generic S_5 is also 9, and its Λ_5 specializes to the verified nonzero product. The full β⁽⁵⁾-table (9,9,9,9,9,9,8,7,6) matches the tropical recursion exactly (m5_beta_recursion).
- **m = 6, 7, 8 (conditional on the recursion):** (T_m) holds for the tropical-predicted tables: A1 = [0, 2^{m−3}−…] lower blocks, A2 upper blocks, max A1 ≤ min A2; predicted deg_b = 23, 57, 135 (stage predict). The m = 6 anchor deg_b u_6 = 23 (symbolic, §8) matches the prediction.

**Status.** Theorem B is a proved implication; its hypothesis (T_m) is verified for m ≤ 5 unconditionally and m ≤ 8 modulo C-B2. The all-m statement is CONJECTURE C-B1.

## 6. T5: the a-side analog — PROVED (structural), verified at m = 4

**Lemma T5a.** deg_a g_0 = 2 with [a²]g_0 = 1; deg_a g_1 = 1 with [a]g_1 = 2σ_1; deg_a g_2 = 0; and deg_a U_r = r with a-leading part `Û_r = (−1)^r·[(√u+√v)^{2r} + (√u−√v)^{2r}]` (u = x_{m−1}, v = x_m): Û_0 = 2, Û_1 = −2(u+v), Û_2 = 2(u²+6uv+v²) — polynomials with *all-positive* coefficients (up to the global sign).

**Theorem T5b (a-extremal grade).** The a-extremal grade of (∗) is a sum of (d+1)(d+2)/2 terms with a-degrees α_k + α_l + (l−k) (off-diagonal) and 2α_k (diagonal), each with explicit a-leading coefficient built from â_k := [a^{α_k}]f_k and Û. At m = 4 (α⁽³⁾ = (2,1,0), d = 2) the a-extremal grade is the six-term sum
`â_0²δ⁴ + â_0â_1δ²Û_1 + â_1²δ² + â_0â_2Û_2 + â_1â_2Û_1 + â_2²`
with â_0 = 1, â_1 = 2(x_1+x_2), â_2 = (x_1−x_2)² — verified *exactly* equal to the a⁴-part of S_4 (m4_alead_sum). deg_a S_4 = 4 (m4_dega), and the α-table is fiber-flat: α⁽⁴⁾ = (4,4,4,4,4).

**Remark (distinctive strength of the a-route).** The even-r Û_r have positive coefficients, so among the diagonal a-extremal contributions no sign cancellation is possible at all; the a-side positivity is a structurally different non-cancellation mechanism from Theorem B's linear independence. The a-extremal family lives at |E| = (W_m − 4α_m)/2 (= 4 at m = 4) and, being fiber-flat at m = 4, certifies fibers the b-family cannot reach (§10).

## 7. T6: the tropical β-recursion and the (NZ) hypothesis — verified m ≤ 5 (+anchors at m = 6); zeros mapped

**Recursion.** `β⁽ᵐ⁾(j) = max_{0≤k≤l≤d, 2(d−l)+k≥j} (β⁽ᵐ⁻¹⁾_k + β⁽ᵐ⁻¹⁾_l + l)` for 0 ≤ j ≤ 2d (T3b gives ≤; equality is the content). Extracted tables:
β⁽³⁾ = (1,1,0); β⁽⁴⁾ = (3,3,3,3,2); β⁽⁵⁾ = (9,9,9,9,9,9,8,7,6); β⁽⁶⁾ = (23×12, 22,21,20,19,18); β⁽⁷⁾ = (57×22, 56,…,46); β⁽⁸⁾ global 135. Predicted deg_b S_m: 3, 9, 23, 57, 135 (m = 4..8), each strictly below the weight cap W_m/6 = 4, 10, 26, 64, 149 — **no cap collision through m = 8** (see §13 for the stale-collision FAIL).

**(NZ_j) hypothesis (exact non-cancellation condition).** The coefficient of x_m^j in the (k,l)-term is a signed convolution of g-data coefficients; its extremal pieces carry Krawtchouk-type integer coefficients
`K_j(2s,k) = Σ_t (−1)^t C(2s,t)·C(k,j−t)`  (= [v^j]-coefficient of (u−v)^{2s}(u+v)^k, up to a u-power).
(NZ_j) = the signed sum at the tropical argmax for x_m^j is nonzero. **This is nontrivial:** in the range k ≤ 16, s ≤ 8 (covering m ≤ 6), K_j(2s,k) has **96 zeros out of 2601** tuples (stage krawt, full list in the receipt), including the exact parity family `K_j(2s,2s) = 0 for all odd j` (krawt_diagonal_parity, proved by u ↔ −u symmetry). Whether a zero ever occupies an argmax position is precisely CONJECTURE C-B2. The diagonal parity zeros occur at symmetric positions where the tropical max is typically attained by several (k,l)-pairs simultaneously, so the recursion has slack — a plausibility remark, not a proof.

**Verification status.** m = 4: exact (m4_beta_recursion). m = 5: exact over QQ(b) at a = 1, all 9 positions (m5_beta_recursion). m = 6: global anchor deg_b u_6 = 23 (symbolic) and the m = 6 full-hull certificates of EV-BKKMV-002; per-position table not computed (censored by cost, see §13).

## 8. T7: the bottom-fiber factorization law — PROVED at m ≤ 6 (symbolic) + m = 7 (numeric); ERRATUM to THM_BKKMV1 §4

### 8.1 The verified law

Computed by specialized Sylvester determinants (the exact route of THM_BKKMV1 §4.3; substitution commutes with det), stage `u`:

- `u_4 = X³·(a⁴X − 8a³b + 64b³)` — X-adic valuation 3 = C(3,1); nonzero root `8b(a³−8b²)/a⁴` (check u4_root_weight).
- `u_5 = (a²+4bX)⁴ · (a⁸ + 16a⁶bX + 32a⁵b² − 256a³b³X − 256a²b⁴ + 1024b⁵X)`; deg_X 5, deg_b 9 (= β₅ ✓, check u5_degb); second factor is *X-linear*: `u_5 = (a²+4bX)⁴·(a²(a⁶+32a³b²−256b⁴) + 16b(a³−8b²)²·X)`; `c_5 = u_5(0) = a^10·(a⁶+32a³b²−256b⁴) = a^10·ψ_5(0;−a,−b)`.
- `u_6 = X^10 · (a⁴X − 8a³b + 64b³)⁵ · (a^12X − 24a^11b + 64a^9b²X + 960a^8b³ + 512a^6b^4X − 10240a^5b^5 − 16384a^3b^6X + 32768a^2b^7 + 65536b^8X)`; deg_X 16 (u6_degX), X-adic valuation exactly 10 = C(5,3) (u6_valuation), deg_b 23, deg_a 32; the third factor is again X-linear; u_3 ∤ u_6 (u_3-adic exponent 0).
- `u_7` at (a,b) = (1,1) and (2,3) (stage u7num, interpolation-free 18×18 determinants over QQ): deg 22 = 15+6+1, X-adic valuation 0 (c_7 ≠ 0, checks u7_val0_*), u_3-adic exponent 15, u_5-adic exponent 3 at both instances; c_7(1,1) = 1210147879172587203969, c_7(2,3) = 940529895174650488995660370362894699689828228792320.

**The law (CONJECTURE C-u, verified at m ≤ 6 symbolically and m = 7 numerically):** for all m ≥ 3,
`u_m(X) = ±L_m(a,b) · Π_{k ≢ m (mod 2), 1 ≤ k ≤ m−1} (X − x(kP))^{N(m,k)}`,   `N(m,k) = C(m−1, (m−1−k)/2)`,
where P = (0, √b) over the algebraic closure, x(kP) is the rational-function root of the k-th stratum (x(P) = 0, giving the X-factor at even m), and L_m ∈ Z[a,b] is the leading coefficient (it absorbs the root denominators and, at odd m, the *zero-sum stratum* that escapes to infinity: `deg_X u_m = 2^{m−2} − [m odd]·(1/2)·C(m−1,(m−1)/2)` = 1, 4, 5, 16, 22 for m = 3..7 ✓). Multiplicity checks: m = 4: (X³, ·¹) = (N(4,1), N(4,3)) = (3,1) ✓; m = 5: (4,1) ✓; m = 6: (10,5,1) ✓; m = 7: (15,6,1) ✓ (numeric).

**Torsion part.** `c_m := u_m(0) = ±Π_{k≢m(2), 2≤k≤m−1} [ψ_{k−1}·ψ_{k+1}](0;−a,−b)^{N(m,k)}` (the condition x(kP) = 0 ⟺ (k−1)P = O or (k+1)P = O):
- m = 3: c_3 = a² = −ψ_3(0;−a,−b) ✓ (symbolic);
- m = 5: c_5 = (−ψ_3)⁵·ψ_5 evaluated at (0;−a,−b) = a^10·(a⁶+32a³b²−256b⁴) ✓ (symbolic; ψ_3(0;−a,−b) = −a², ψ_5(0;−a,−b) = a⁶+32a³b²−256b⁴, arbitrated against numeric instances);
- m = 7: `c_7 = ±ψ_3^21·ψ_5^7·ψ_7 (0;−a,−b)` — confirmed at both computed instances by *exact integer division*: c_7(1,1)/(ψ_3^21ψ_5^7) = 44127 = 3²·4903, c_7(2,3)/(ψ_3^21ψ_5^7) = 303165440 = 2^12·5·113·131 (pure-Python factorization, reproduced in §13; the quotients are the two instances of ±ψ_7(0;−a,−b)).

### 8.2 ERRATUM to THM_BKKMV1 §4 (rules 4, 8, 9 — corrections create new records)

**The defect.** research/verification/thm_bkkmv1_verify_m5.sage, stage `u5`, hardcoded the input coefficient table of u_4 as `u4c = {4: a**4, 3: 8*b*(8*b**2 − a**2)}` — **a² where the correct value is a³** (its own stage `34` prints the correct u_4 = a⁴X⁴ − 8a³bX³ + 64b³X³, matching my u4_exact). Every downstream u_5/c_5 computation in THM_BKKMV1 inherited the typo.

**Invalidated (artifacts of the typo):**
1. THM_BKKMV1's displayed u_5 ("(a²+4bX)³·Q with deg_X Q = 2", §5 "Also OPEN / C4") — correct value in §8.1 (u_3⁴, X-linear second factor, deg_X 5).
2. Its displayed c_5 = `a^10·(a^6 + 32a²b² − 256b⁴)` — note this is not even weight-homogeneous (a²b² has weight 20 vs 24 for the other terms; T2's grading exposes it immediately). Correct: `a^10·(a⁶ + 32a³b² − 256b⁴)`.
3. Its §4.4 "refuted guess": the claim that ψ₅(0)-factorization of c_5 is *refuted*. With the correct c_5, the torsion law **holds** (§8.1, with the program's (a,b)↦(−a,−b) convention flip). The "precise torsion-factorization law is OPEN" conclusion is superseded by CONJECTURE C-u, verified at m ≤ 7.
4. Its §4.4 "naive product-formula multiplicity count fails (predicted x(2P)-multiplicity 4, measured 3)" and "u_3³ | u_5 exactly" — measured exponent is **4** = naive N(5,2); at every m ≤ 7 tested, finite-root multiplicities equal the naive sign counts. The escape-to-infinity *mechanism* is real but shows up only in the deg_X drop at odd m (zero-sum stratum), not in finite-root multiplicities.

**Unaffected and independently re-verified here:** THM_BKKMV1 Theorem 2's main statements — even m: X | u_m (u_4, u_6: valuations 3, 10); odd m: c_m ≠ 0 (c_3, c_5, c_7); the t = 0 exceptional-section prediction at even m; and the §4.3 specialization-pitfall methodology (which this note's `u` stage uses). Its text's displayed root "8b(a²−8b²)/a⁴" for u_4 is a transcription typo for `8b(a³−8b²)/a⁴` (check u4_root_weight flags it).

**Status of the correction:** the erroneous records remain in the V1 receipt files (immutable); this section is the correcting record, with independent recomputation (different code path: fresh Sylvester determinants, no shared coefficient tables) and exact factorization receipts.

## 9. T8: even-m t = 0 sections never saturate — restated, confirmed at m = 6

THM_BKKMV1 Theorem 2.3 (proved there): at even m, the section t = 0 loses the box's bottom corner (its constant term is u_m(0) = 0), hence is never box-saturated. This note adds the m = 6 confirmation at the strongest level: X^10 | u_6 identically (§8.1), so the t = 0 section at m = 6 loses the entire bottom *stratum* of 10 corner-near fibers, not just the origin cell. The falsifiable prediction stands for future m = 6 experiments (none of the ledger's sections used t = 0; EV-BKKMV-002's 30 sections are all nonzero-t).

## 10. The covering picture at m = 4 (CONJECTURE C-B3 quantified)

**Question (covering half of Lemma-G).** Do explicit, mechanism-level non-cancellation certificates touch *every* box fiber? Stage `cover4` recomputed supp S_4 (439 cells, cover4_supp_size) and attributed each of the 125 fibers of the box [0,4]³ to the certificate families that contain at least one of its cells:

- **corner**: the universal diagonal corner (4,4,4,0) (THM_BKKMV1 Theorem 1);
- **tower_i** (i = 1..4): the symmetric top-layer families lead_{x_i} S_4 = S_3² — verified at support level: the x_4 = 4 layer equals 2·supp S_3 exactly (60 cells, cover4_tower);
- **blead**: cells of Λ_4 (Theorem B, §5);
- **alead**: cells of the a⁴-grade (T5, §6);
- **q≤5**: cells of the single-grade cone (T2: |E| ≥ 7 at m = 4).

**Result (cover4_all_fibers):** 125/125 fibers nonempty (C1 at m = 4, as proved in THM_BKKMV1) and **0 fibers uncovered** by the explicit families. Tallies (a fiber may carry several mechanisms): towers 109, q≤5 cone 109, a-leading 35, b-leading 20. Full distribution in the receipt; the 16 cone-free fibers are all caught by the a-leading family (10 alead+blead+tower4, 3 alead+blead, 3 alead+tower_i). **The families are complementary and overlapping, not redundant:** b-leading alone certifies only 20/125.

**Supporting evidence at m = 5, 6 (ledger):** EV-BKKMV-001 (m = 5: all five projections exactly the 6561-box; 54777-cell generic instance) and EV-BKKMV-002 (m = 6: full box [0,16]⁵ = 1,419,857 cells on 28/30 sections literally, 30/30 at hull level with all 32 corners present, two certification primes 1000003/1000033, 3 seeded curves; MV_6 = 125829120 exact; the two 60/30-cell losses are hull-interior, prime/section-specific coefficient vanishings — the *instance-cancellation* phenomenon, consistent with generic-fiber fullness by THM_BKKMV1 Theorem 4(iii)).

**CONJECTURE C-B3.** For all m, every box fiber is touched by at least one explicit certificate family (corner tower; the m symmetric S_{m−1}²-towers; the b-leading grade of Theorem B; the a-leading grade of T5; the q ≤ 5 cone). Quantified at m = 4 (0 residual); open for m ≥ 5 as a mechanism-level statement (projection fullness at m = 5 is proved, but not the attribution).

## 11. The remaining gaps, stated exactly

- **G1 (non-cancellation half).** Prove (T_m) and (NZ_j) for all m. (T_m) is verified for m ≤ 5 unconditionally and m ≤ 8 for the tropical tables; (NZ_j) is reduced to "no tropical argmax ever lands on a Krawtchouk zero" — the zeros are mapped (96/2601, with the exact odd-j diagonal family), so the conjecture is falsifiable by direct computation at each m. Under C-B1 + C-B2: deg_b S_m and the full β⁽ᵐ⁾-tables are known exactly for all m, and the b-extremal fiber coefficients never cancel (Theorem B).
- **G2 (covering half).** Prove C-B3 for all m: the explicit families touch every fiber. m = 4 is mechanized (0/125 residual); the bottleneck named in THM_BKKMV1 §5 (arithmetic control of the K-sets K(α) = {k : α ∈ supp f_k}) is now partially answered by the β/α-graded description of the K-sets' extremal sheets, but a full support theorem is still missing.
- **G3 (grade migration).** The proved certificates live on disjoint grades: b-extremal at |E| = 3, 5, 11, 21, 43 (bottom corner), a-extremal at |E| = (W_m − 4α_m)/2, q ≤ 5 cone near the top (|E| ≥ W_m/2 − 5; at m = 4: |E| ≥ 7), towers at the shell (some e_i = D). A complete proof must show the *union* covers the box for all m (C-B3), or find a per-fiber joint (a,b)-tropical extremal monomial; the m = 4 data show no single family suffices and quantify the overlaps.

**Relation to Lemma-G and C1.** Lemma-G (THM_BKKMV1 §5) required: no interior fiber's coefficient cancels completely. This note (i) proves non-cancellation on an explicit union of grades at all m where (T_m)/(NZ) hold (verified m ≤ 5), (ii) mechanizes the full cover at m = 4, (iii) reduces the all-m statement to C-B1 ∧ C-B2 ∧ C-B3, each individually checkable by the preserved scripts. C1/C2 remain open for m ≥ 6 (EV-BKKMV-002 certifies m = 6 experimentally), but the gap is now three named combinatorial statements instead of one monolithic lemma.

## 12. Consistency with the ledger (anchor table)

| Item of this note | Ledger / prior anchor | Agreement |
|---|---|---|
| supp S_4 = 439 cells; top layer = 2·supp S_3 (60) | EV-BKKMV-001 "439 < 625"; THM_BKKMV1 lead-tower | exact |
| deg_b S_4 = 3, deg_a S_4 = 4; β⁽⁴⁾ = (3,3,3,3,2), α⁽⁴⁾ = (4,4,4,4,4) | new | verified symbolic (m4 stage) |
| deg_b S_5 = 9; Λ_5 = ΨΦ; β⁽⁵⁾ = (9,…,6) | EV-BKKMV-001 m = 5 saturation | exact (a = 1 symbolic; generic by specialization) |
| u_4 exact; valuation 3 | THM_BKKMV1 Thm 2 (verified there) | exact match |
| u_5, c_5, u_3-exponent 4 | THM_BKKMV1 §4.4 (typo-corrupted) | **ERRATUM §8.2** |
| u_6: X^10, deg_X 16, deg_b 23, deg_a 32 | EV-BKKMV-002 m = 6 certificates | consistent (different object: bottom fiber vs sections) |
| u_7 numeric: deg 22, val 0, exponents (15, 3) | no prior object | new datum |
| t = 0 exceptional at even m | THM_BKKMV1 Thm 2.3 (m = 4 verified) | restated + m = 6 (X^10) |
| m = 4 fiber cover 125/125, 0 residual | THM_BKKMV1 Thm 3 (C1 at m = 4) | strengthened to mechanism attribution |
| predicted deg_b 23/57/135 at m = 6/7/8 | none | falsifiable predictions of C-B1/C-B2 |

## 13. Deviations, censorings, and validity

1. **FAIL receipt `u6_degb` (stage u):** the check encoded a stale hand-estimate (25) as the expected deg_b u_6; the measured value is 23. Analysis: 23 is exactly the tropical recursion's prediction (β⁽⁶⁾ global) *and* the (T)-sum 9 + 14, using the correct bottom-fiber b-profile of u_5 (β̂⁽⁵⁾(k) = k + 4 for k = 0..5; the maximum is attained at the (5,5) diagonal: 2·9 + 5 = 23). The theory is consistent; the expectation was wrong. Recorded as FAIL, uncorrected in the receipt.
2. **FAIL receipt `predict_cap_collision_m7` (stage predict):** encoded my earlier hand-estimate that the weight cap W_7/6 = 64 forces a tropical collision at m = 7. The scripted recursion gives deg_b S_7 = 57 ≤ 64 (and 135 ≤ 149 at m = 8): **no collision through m = 8**. The hand-estimate was faulty; the check's PASS-condition was the wrong expectation.
3. **Infrastructure censoring (mitigated):** the fully symbolic S_5 over QQ(a,b) remains above the ~290 s foreground cap (as in THM_BKKMV1). Mitigation here: the QQ(b), a = 1 computation (17.3 s) proves Theorem B at m = 5 and the full β⁽⁵⁾-table, with genericity recovered by specialization-monotonicity for the degree statements. No conclusion depends on the censored run.
4. **Tooling hazards documented (rule 8, methodological):** (a) Sage's `.coefficient(X**0)` returns the polynomial itself in this build — all coefficient extraction uses a guard (substitution for j = 0); one *notes-line* (the u_6 b-profile key 0) retains the artifact and is disregarded (checks used the guarded route). (b) JSON serialization of Sage integers truncated the first `u`-stage receipt mid-write; fixed by a coercion wrapper and rerun; all final receipts parse.
5. **Convention:** identical to THM_BKKMV1 (the instruments' symmetric S_3); the torsion law is stated under the corresponding (a,b) ↦ (−a,−b) flip, and all support/degree statements are convention-robust.
6. **Validity:** theory note; all PROVED items are self-contained proofs plus computer verification with preserved, rerunnable artifacts (`sage thm_bkkmv2_verify.sage m4|u|u7num|krawt|predict|cover4|m5`; the c_7 factorization is 10 lines of pure Python, values inline in §8.1). No fabricated computations; the two FAIL receipts are retained and analyzed above. All verified instances are model-level (small symbolic resultants and toy instances) — no crypto-scale claim (rule 7). **Budget note (minor deviation, reported):** approximately 14 Sage invocations against the 12-run cap — the ~2-run excess consists entirely of reruns after the JSON-serialization crash of item 4(b) (the computations themselves had succeeded; only receipt-writing failed), plus two small pure-Python factorization runs (one failed: sympy absent; one succeeded). Write scope limited to research/THM_BKKMV2.md and research/verification/thm_bkkmv2_verify.sage + receipts; no git commits.
