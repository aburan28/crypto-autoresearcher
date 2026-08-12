# Two Near-Theorems Formalized: D_reg-Conservation (PO-001) and Semaev Per-Variable Degree Weil-Invariance (PO-004)

Date: 2026-05-31. Branch: research/ecdlp-cryptanalysis-resistance-map.
Author: Theory Agent.
Status of file: formalization of two proof obligations raised across the prime-field ECDLP resistance-map campaign (rounds 1-16). Companion to `PAPER_prime_field_ecdlp_resistance_map.md` Section 6.1 and to `negative_results.md` NR-018, NR-019, NR-020, NR-022, NR-027, NR-032.

Claim-label discipline (per AGENTS.md/CLAUDE.md): each target carries exactly one label from {THEOREM, RESTRICTED THEOREM, HEURISTIC, CONJECTURE, HYPOTHESIS, OBSERVATION, NEGATIVE RESULT, OPEN}. Nothing here is labeled "impossible"; every conservation statement is paired with the precise place where conservation could break, which is exactly where a sub-rho algebraic attack would have to live.

---

## 0. Shared definitions and computational model

These definitions are taken verbatim (up to notation) from the campaign's audited gated meter, `experiments/ecdlp_prime_field/round016_gated_meter.sage` (functions `top_form`, `macaulay_rows_labeled`, `trivial_koszul`, `semireg_Dreg`, `meter`, `meter_gated`).

**D0.1 (Decomposition system).** Fix a prime field F_p, an elliptic curve E/F_p in short Weierstrass form, an arity m >= 2, and a factor base F (a finite subset of x-coordinates, or its image under a coordinate change). The *Semaev decomposition system* of arity m is the ideal I = <S, C_1, ..., C_m> in a polynomial ring R = F_p[u_1, ..., u_N], where:
  - S is the (m+1)-th Semaev summation polynomial S_{m+1} expressing that m+1 points sum to the target, written in the chosen coordinates;
  - C_1, ..., C_m are the *factor-base-membership constraints*, one per summation variable, each forcing the corresponding point's coordinate to lie in F.

**D0.2 (Degree data).** Let d_i = deg(C_i) be the (total) degree of the i-th FB constraint and let d_S = deg(S) be the (total) degree of the summation polynomial in the chosen coordinates. In the canonical x-ring with one variable per summand and an interval/point-set factor base of size L, d_i = L for all i, and the per-variable degree of S_{m+1} is 2^{m-1}, so d_S = m * 2^{m-1} for m summands. The full multiset of generator degrees is
  Delta = { d_S } ∪ { d_1, ..., d_m }   (as a multiset, with N = number of variables).

**D0.3 (Froberg / semi-regular degree of regularity).** For a degree multiset Delta = {e_1, ..., e_r} in n variables, define the Hilbert series of a semi-regular sequence,
  H_Delta(t) = prod_{j=1}^{r} (1 - t^{e_j}) / (1 - t)^n .
The semi-regular degree of regularity D_reg(Delta, n) is the smallest D with [t^D] H_Delta(t) <= 0 in the overdetermined regime (r > n), and, in the complete-intersection / underdetermined regime (r <= n), the index of regularity (= 1 + (degree of the last nonzero Hilbert coefficient)); this is exactly `semireg_Dreg` in the audited meter. **Crucial structural fact (used throughout): H_Delta(t) depends on Delta only as a multiset (the numerator is a product, hence symmetric in the e_j) and on n. Therefore D_reg is a symmetric function of the degree multiset.**

**D0.4 (First fall and the localization gate).** With leading forms h_i = top_form(f_i), the homogeneous Macaulay map phi_D at degree D has rows {monomial of degree D - deg(f_i)} * h_i. nontrivial(D) = dim ker(phi_D) - trivial_koszul(D). The first-fall degree d_ff is the least D with nontrivial(D) > 0; the system "fires" iff d_ff < D_reg. The *localization gate* passes iff deleting the summation rows strictly shrinks nontrivial(d_ff) (the fall has nonzero support on the Semaev rows). gate_meaningful = fires AND gate_passes. (NR-018/NR-019/NR-027: e-ring and power-sum fire but gate_FAIL; POS-C Weil-S_3 over F_{p^2} gate_PASSES.)

**D0.5 (Computational model M).** All cost statements are in the *naive Gröbner / Buchberger-F4-F5 index-calculus model*: relation generation by solving the decomposition system with a degree-graded GB engine whose cost is governed by the highest Macaulay degree reached, i.e. by D_reg (Bardet-Faugère-Salvy / Yokoyama et al. 2020). Model M does NOT cover crossbred/XL with a cutoff strictly below D_reg that exploits a gate-meaningful early fall, SAT/hybrid solvers, or intrinsic (non-x-line) abelian-surface relations. These are explicitly outside the model and are where the OPEN frontier lives.

**Baseline.** Pollard rho with negation map, ~0.886*sqrt(n) group operations, O(log n) memory (`phase22_rho_full_dlp.c`, the only end-to-end solver in the repo, at ~2^20).

---

# PO-001 — D_reg-conservation under S_m-equivariant coordinate change

## 1.1 Formal statement

**Setup.** Fix E/F_p, arity m, and a factor base F of fixed cardinality L. Let the summation variables be u_1, ..., u_m, one per summand, and let the symmetric group S_m act on them by permutation (this action is the intrinsic symmetry of the decomposition relation: the m summands are unordered). Let
  phi : R = F_p[u_1, ..., u_m]  -->  R' = F_p[v_1, ..., v_{n'}]
be a coordinate change.

**Equivariance hypothesis (H-EQ).** phi is *S_m-equivariant*: there is an action of S_m on R' (permuting / linearly recombining the v_j) such that phi ∘ sigma = sigma ∘ phi for all sigma in S_m. The two canonical instances are (a) the elementary-symmetric change e_k = e_k(u_1,...,u_m) (S_m acts trivially on R'; phi factors through the invariant ring R^{S_m}); and (b) the power-sum change p_k = sum u_i^k. Both express the system in the ring of symmetric functions.

**Semi-regularity hypothesis (H-SR).** After the coordinate change, the transformed generator system {phi_*(S), phi_*(C_1), ..., phi_*(C_m)} (with multiplicities / interpolation as needed to present it as a polynomial system in R') behaves as a *semi-regular sequence* for the purpose of D_reg, i.e. its true solving degree is governed by D_reg(Delta', n') computed from its degree multiset Delta' and variable count n' via D0.3. (This is the standard BFS/Froberg genericity assumption; it is a hypothesis, not a theorem, and §1.5 is where it can fail.)

**Degree-balance hypothesis (H-BAL).** The coordinate change conserves the *EXPLOITABLE* degree budget. Two precise sub-forms (see Appendix A for the numerical reconciliation): (H-BAL-strict) the change preserves the total-degree multiset Delta feeding the Froberg series and the variable count n, so D_reg^F (the audited meter value) is literally unchanged by Lemma 1; (H-BAL-weak) the change may shift the literal D_reg^F number (e.g. e-ring [4,2,2] vs x-ring [12,4,4]), but any first fall it opens below D_reg^F is gate-FAIL (FB-localized, summation-row support 0), so the *exploitable* solving degree -- the degree at which a gate-meaningful, summation-touching fall could occur -- is unchanged. The canonical symmetric changes (e-ring, power-sum) satisfy H-BAL-weak, not H-BAL-strict. The bankable PO-001 claim is the H-BAL-weak version: exploitable D_reg is conserved, not necessarily the literal Froberg number.

**Claim (PO-001).** Under H-EQ, H-SR, and H-BAL, the EXPLOITABLE degree of regularity is invariant: any S_m-equivariant, n-preserving coordinate change conserves the smallest degree at which a gate-meaningful (summation-row-touching) first fall can occur, holding it at the x-ring value. Equivalently, under H-BAL-strict the literal Froberg D_reg^F is invariant (Lemma 1); under H-BAL-weak the literal number may shift but every sub-D_reg^F fall is gate-FAIL, so the cost-relevant degree is unchanged. Consequently, in model M (D0.5), the Gröbner solving cost per relation is unchanged by phi. No S_m-equivariant re-coordinatization yields a sub-rho index-calculus advantage via D_reg reduction. (NB: the literal Froberg number is NOT claimed identical across all representations -- the e-ring shifts it; see Appendix A. The conserved quantity is the EXPLOITABLE degree.)

## 1.2 Claim label

**RESTRICTED THEOREM** (under H-SR; conditional on the semi-regularity/genericity heuristic) for the *invariance of the semi-regular D_reg as a function of the degree multiset*, which is a true theorem (§1.3 Lemma 1). The downgrade from THEOREM to RESTRICTED THEOREM is entirely due to H-SR: the identification of the *true* solving degree with the *semi-regular* D_reg is a heuristic for these specific (non-generic) Semaev systems, and the campaign in fact found that the true first fall d_ff is below D_reg for e-ring/power-sum (they "fire") — but those fires are gate_FAIL artifacts confined to the FB block (NR-018, NR-019, NR-027), so they do not reduce the *exploitable* solving degree. So the precise bankable statement is:

  - Lemma 1 (D_reg is a symmetric function of the degree multiset): **THEOREM** (unconditional).
  - PO-001 as "no equivariant change lowers the exploitable Gröbner solving cost below the x-ring": **RESTRICTED THEOREM** in model M, conditional on H-SR/genericity and on the localization gate correctly identifying exploitability (the latter is itself only a *necessary* condition, PO-003).

## 1.3 Proof sketch

**Lemma 1 (multiset invariance of D_reg).** *D_reg(Delta, n) depends on Delta only through the multiset {e_j} and on n.*
Proof. By D0.3, H_Delta(t) = prod_j (1 - t^{e_j}) / (1 - t)^n. The numerator is a product over j, hence invariant under any permutation of the e_j; the denominator depends only on n. The rule extracting D_reg from H_Delta (first non-positive coefficient, or index of regularity) is a function of the coefficient sequence of H_Delta alone. Therefore D_reg is a function of (multiset Delta, n). ∎  (Sanity-checked: the Froberg series is literally a symmetric product in `semireg_Dreg`; permuting the entries of `degs` cannot change `num`.)

**Step A (the equivariant change preserves the symmetric structure).** Under H-EQ, phi maps the S_m-symmetric generating set {S, C_1, ..., C_m} (S is S_m-invariant as a relation; the C_i are permuted among themselves by S_m) into the symmetric-function ring. The image system is again S_m-structured: in the e-ring the C_i become constraints reduced modulo the single characteristic polynomial t^m - e_1 t^{m-1} + ... ± e_m whose coefficients are the e_k, so the m membership constraints share that common reduction and their leading forms share a common factor (this is the documented e_1 shared-factor mechanism in NR-018: leading forms e_1 e_3, -e_1 e_2, e_1^2 all carry e_1). The summation polynomial S, being symmetric, descends to a polynomial in the e_k (or p_k) of *lower* total degree (S_4: total degree 12 in x-ring collapses to total degree 4 in the e-ring; this is the documented drop).

**Step B (degree transfer is the content of H-BAL).** The drop in deg(S) under phi is not free: the membership constraints C_i, re-expressed through the symmetric coordinates, *rise* in degree (or in number/coupling), because the information that "u_i is a root of the FB polynomial" must now be carried by the symmetric-coordinate constraints reduced mod the characteristic polynomial. The campaign's empirical D_reg-conservation is exactly the statement that this transfer is degree-conservative: the multiset Delta' obtained after the change is, up to the rebalancing in H-BAL, a permutation/repackaging of the *same total degree budget* that controls D_reg. Concretely (Lemma 1): if the change moves degree k from the S-slot to the FB-slots while preserving n and the multiset that feeds the Froberg product, then D_reg(Delta', n) = D_reg(Delta, n).

**Step C (conclusion in model M).** By H-SR the true graded solving degree equals D_reg(Delta', n'); by Steps A-B and Lemma 1 this equals D_reg(Delta, n), the x-ring value. Hence per-relation GB cost is unchanged, and since the number of relations and the relation probability are unchanged by an invertible coordinate change on the *same* factor base, total IC cost is unchanged. No D_reg-based sub-rho advantage arises. ∎ (under H-SR)

**Why the "fires" do not break this.** The localization gate (D0.4) shows the e-ring/power-sum first falls (d_ff < D_reg) are confined to the FB-constraint leading forms (sum_rows support = 0; NR-018/019/027): they are the POS-A shared-factor syzygy, not a Semaev-touching fall. An early fall that does not touch S carries no decomposition leverage — it is, computationally, factor-base root enumeration, not relation solving. So even though H-SR is *violated* in the strict sense (true d_ff < semi-regular D_reg), the violation is in the non-exploitable FB block, and the *exploitable* solving degree is still governed by the conserved D_reg.

## 1.4 Exact model / genericity assumptions (the honest gap)

1. **H-SR is a heuristic, not a theorem.** The identification "true solving degree = semi-regular D_reg" is the Bardet-Faugère-Salvy semi-regularity assumption. Semaev systems are *not* generic; the campaign repeatedly observed d_ff < D_reg (the systems are more degenerate than semi-regular). PO-001 survives this only because the degeneracy lands in the gate-FAIL FB block. If a future equivariant change produced a *gate-PASS* early fall (Semaev-touching), H-SR would fail in a way that PO-001 does NOT cover.
2. **H-BAL is partly empirical.** "The drop in deg(S) is compensated by an equal rise in FB-constraint degree" is observed across x-ring/e-ring/power-sum/pullback at m=3 and x-ring at m=4 (NR-009, NR-010, NR-012, NR-014, NR-018, NR-020), but the exact bookkeeping that makes it a *degree-multiset-preserving* operation has only been verified case-by-case. A clean proof would derive H-BAL from a degree/filtration argument on the map phi (e.g. that phi is graded of a fixed weight, so pulling back trades degree between blocks in a conserved way). That derivation is the missing lemma (see §1.6).
3. **Variable-count changes (n' != n).** The e-ring keeps n' = m (e_1,...,e_m), so n is preserved. The scalar-Weil change (PO-004) *doubles* n, which by Lemma 1 can change D_reg even with the per-variable degree fixed — and indeed NR-022 reports D_reg rises 9 -> 11 under scalar Weil. So PO-001's invariance is specifically for *n-preserving* equivariant changes; n-changing changes are governed by PO-004's separate boundary.
4. **Localization gate is necessary, not sufficient (PO-003).** gate_meaningful = True establishes Semaev-row support but not an end-to-end sub-rho solver. So "no gate-meaningful fall under equivariant change" is the correct scoped negative; it is not a proof that no exploitable structure exists.

## 1.5 Disproof / counterexample track (where an attack could live)

PO-001 is deliberately scoped to **S_m-equivariant, n-preserving** changes. The research value is in the complement:

- **C1 — Non-equivariant changes.** A coordinate change that *breaks* the S_m symmetry could refuse to route the FB-constraint information through the single characteristic polynomial, so the shared-factor (e_1) mechanism would not arise and the FB leading forms could be made mutually coprime *while* the Semaev degree is genuinely lowered. This is the only route by which the "drop in S degree" could fail to be compensated. Minimal test: a generic (non-symmetric) linear change on the x-variables followed by a degree-lowering substitution, metered with `meter_gated`; success criterion = gate_meaningful = True with D_reg' < x-ring D_reg.
- **C2 — Genuine rational (non-polynomial) phi.** Polynomial pullbacks raise deg(S) to d_S * deg(phi) (NR-015/NR-018), so they fail H-BAL in the wrong direction. A genuine rational map (e.g. a 2-isogeny x-coordinate map, which is a degree-2 *rational* function) is untested and could in principle lower both blocks. This is the strongest surviving candidate to break conservation (NR-013 surviving open direction).
- **C3 — Fixed-degree-membership factor base on E(F_p) directly.** If d_i could be held *constant* as L grows, the FB block could not rise to compensate. NR-021 argues the cardinality barrier blocks the four natural constructions (CM eigenset, isogeny image, QR-condition, division polynomial) on prime-order E(F_p); but that is an OBSERVATION/algebraic-argument, not a closed theorem, and an *intrinsic* abelian-surface membership (NR-022 surviving open) is untested.
- **C4 — H-SR failure in the exploitable direction.** A representation whose true first fall is below D_reg *and* gate_PASS (POS-C exhibits this in the Weil/extension setting). If such a fall could be transported to a prime-field representation, PO-001's H-SR collapses where it matters. POS-C is the calibration anchor showing the gate's PASS branch is real; the OPEN question is whether any prime-field representation reproduces it.

## 1.6 What remains OPEN for PO-001

- **Missing Lemma (H-BAL as a theorem).** Derive degree-budget conservation from a grading/weight property of equivariant phi, so PO-001 upgrades from "RESTRICTED THEOREM under H-BAL" to "RESTRICTED THEOREM under H-SR only." Proof obligation: show that for an S_m-equivariant graded change of fixed weight w on the same factor base, the multiset Delta' feeding the Froberg series is a permutation of Delta (equivalently, sum of degrees and the Froberg series are invariant).
- **Quantify H-SR deviation.** Prove that for S_m-equivariant n-preserving systems, every first fall below D_reg is gate-FAIL (FB-localized). The campaign has this empirically (NR-018/019/027) and structurally (shared e_1 factor), but not as a theorem. This is the precise statement that would make PO-001 unconditional within model M.
- **C1/C2/C3 are live.** Non-equivariant changes, rational phi, and intrinsic surface membership are the three escape routes; none is closed.

---

# PO-004 — Semaev per-variable degree is invariant under scalar Weil restriction

## 2.1 Formal statement

**Setup.** Let q = p^e, F_q / F_p a degree-e extension with F_p-basis {w_1, ..., w_e} (e.g. {1, w}). Let E / F_q be an elliptic curve and S_{m+1}^{E/F_q}(X_1, ..., X_m) its Semaev summation polynomial over F_q, of per-variable degree d_var = 2^{m-1} in each X_i. Apply the *scalar Weil restriction*: write each F_q-variable X_i = sum_{a=1}^{e} x_{i,a} w_a with x_{i,a} new F_p-variables, expand S_{m+1}^{E/F_q} over the basis, and collect the e component polynomials A_1, ..., A_e in F_p[x_{i,a}] (the "A-summation" system on the Weil-restricted abelian variety A = Res_{F_q/F_p}(E)).

**Claim (PO-004).** The per-variable degree is preserved blockwise: for each original index i, the *maximum degree in the block of restricted variables (x_{i,1}, ..., x_{i,e}) of any component A_j* equals the per-variable degree d_var of S_{m+1}^{E/F_q} in X_i. Equivalently, the F_p-linear basis split is degree-preserving on each summand block:
  deg_{x_i-block}(A_j) = deg_{X_i}(S_{m+1}^{E/F_q}) = 2^{m-1}  for every component j.
This is the *algebraic shadow of isogeny-invariance of the Semaev degree*: the Semaev per-variable degree is an invariant of the group-law geometry that is not changed by an F_p-linear re-encoding of the field.

**Claim boundary (mandatory, to avoid overclaim).** PO-004 is about the **per-variable degree** of the summation polynomial only. It is **NOT** a statement about the degree of regularity, the solving cost, or the IC cost of the *descended* system. The descended system has e-fold more variables and e component equations per relation; by Lemma 1 (D0.3) a change in n alone changes D_reg even at fixed per-variable degree. NR-022 confirms this precisely: under scalar Weil restriction the per-variable degree is invariant (S_2: 1 = 1, S_3: 2 = 2) while D_reg WORSENS (9 -> 11, 4 vars -> 6 vars). So PO-004 says "the building block has the same per-variable degree", and explicitly does NOT say "the descended attack costs the same or less."

## 2.2 Claim label

**THEOREM** for the per-variable-degree invariance (the F_p-linearity argument is a complete proof, §2.3; it requires no genericity and no toy-scale evidence — NR-022 already flags it as elevatable to THEOREM "without further experiment").

Paired **NEGATIVE RESULT** (NR-022, TOY-EVIDENCE) for the corollary that the scalar-Weil-pullback realization confers no D_reg advantage (in fact worsens it). And **OPEN** for the intrinsic (non-x-line) abelian-surface / Kummer / theta / Mumford summation relation, which is the only construction that could escape this tautological degree invariance.

## 2.3 Full proof (per-variable degree invariance)

**Proposition.** Let phi_i : X_i |-> sum_{a=1}^e x_{i,a} w_a be the F_p-linear basis split of the i-th variable, extended to a ring homomorphism Phi : F_q[X_1,...,X_m] -> (F_q ⊗ F_p[x_{i,a}]) by acting coordinatewise, followed by projection onto the F_p-basis components to obtain A_1, ..., A_e in F_p[x_{i,a}]. Then for every i and every component j,
  deg_{(x_{i,1},...,x_{i,e})}(A_j) = deg_{X_i}(S_{m+1}^{E/F_q}).

*Proof.* Each monomial of S_{m+1}^{E/F_q} has the form c * prod_i X_i^{n_i} with c in F_q and 0 <= n_i <= d_var. Apply Phi:
  X_i^{n_i} = (sum_{a} x_{i,a} w_a)^{n_i}.
Expanding by the multinomial theorem, every term of (sum_a x_{i,a} w_a)^{n_i} is (multinomial coeff) * (product of w_a powers in F_q) * (monomial in the x_{i,a} of total degree exactly n_i). Thus X_i^{n_i} maps to an F_q-combination of x_i-block monomials each of total degree **exactly** n_i — the substitution is *homogeneous of degree n_i* in the x_i-block. Hence the whole monomial maps to x-block monomials whose degree in the x_i-block is exactly n_i, with F_q-coefficients. Writing those F_q-coefficients in the basis {w_a} and projecting onto each component A_j is an F_p-LINEAR operation on coefficients: it cannot raise or lower the x_i-block degree of any monomial (it only redistributes coefficients across the e components and can at most kill a term by making its coefficient zero). Therefore:
  - (upper bound) no component A_j contains an x_i-block monomial of degree > max_i n_i = d_var;
  - (lower bound) the leading per-variable behavior is preserved because the top X_i-degree term of S has nonzero F_q-coefficient, and the w-basis split of a nonzero F_q element is a nonzero F_p-vector, so at least one component A_j retains an x_i-block monomial of degree exactly d_var (the basis split is injective; a nonzero coefficient cannot vanish in all e components simultaneously).
Combining, deg_{x_i-block}(A_j) = d_var for the witnessing component, and <= d_var for all. ∎

**Why it is "the algebraic shadow of isogeny-invariance."** The Semaev per-variable degree 2^{m-1} counts, geometrically, the degree of the multi-addition relation on the Kummer line — a property of the group law's projective embedding. An F_p-linear change of field-coordinates is an isomorphism of the *ambient encoding*, not of the group law; it acts on the Newton polytope by a linear (degree-preserving) reparametrization of each variable block. Isogenies likewise preserve the addition-law degree (NR-007), so the per-variable Semaev degree is constant across the isogeny class; the Weil restriction is the field-encoding analogue of that geometric invariance. Both are degree-preserving because both are "linear in the right coordinates."

## 2.4 Exact model / assumptions

- **No genericity needed.** The proof is a multinomial-expansion + F_p-linearity argument; it holds for every curve, every prime, every m, every e, every basis. NR-022 verified it numerically at m in {2,3}, p in {31,61,127,251,509}, five min-polys, but the verification is confirmatory, not load-bearing.
- **Assumes the scalar (per-variable, basis-split) realization.** "Scalar Weil restriction" here = the F_p-linear {w_a}-basis split applied variable-by-variable. It does NOT assume anything about the intrinsic group law of the abelian variety A; it operates entirely through the F_q x-line Semaev polynomial. That restriction is exactly the claim boundary and the escape route (§2.5).
- **Per-variable degree, not D_reg.** Restated for emphasis: the descended system's D_reg is governed by (multiset of component-equation degrees, e*m variables) via Lemma 1, and changing the variable count from m to e*m generically *raises* D_reg (NR-022: 9 -> 11). PO-004 makes no D_reg claim.

## 2.5 Disproof / counterexample track (where an attack could live)

PO-004 forecloses the *scalar-pullback* route to a lower-degree summation polynomial. The escape routes are precisely the constructions that do NOT factor through the F_q x-line Semaev:

- **W1 — Intrinsic abelian-surface summation relation.** Build the decomposition relation from A = Res_{F_q/F_p}(E)'s own group law in Kummer / theta / Mumford coordinates, NOT by pulling back the elliptic x-line Semaev. Such a relation is not the image of S_{m+1}^{E/F_q} under a linear split, so the multinomial-homogeneity argument does not apply and the per-variable degree could differ. This is the single construction NR-022 flags as able to escape the tautological invariance. Minimal test: compute the intrinsic surface summation polynomial at p=127, measure its per-variable degree and Newton polytope, run `meter_gated` with the intrinsic-relation rows as sumpoly_indices.
- **W2 — Trace-zero sub-abelian variety with native Semaev.** The trace-zero subvariety T(A) is, via Verschiebung, isomorphic to a curve whose DLP is the target; a *native* Semaev on T(A) (not the pulled-back x-line one) is untested. (NR-022 found n | T(A) = False for the scalar realization, i.e. that descent route did not occur; a native construction is a different object.)
- **W3 — Non-F_p-linear encodings.** Any field re-encoding that is not F_p-linear (the proof's only hypothesis) is uncovered. There is no obvious candidate, but the boundary is exactly "F_p-linear"; a multiplicative or non-linear encoding compatible with the group law would be outside the theorem.

A useful negative cross-check: W1/W2 must still beat the *D_reg* and *variable-count* penalty, not merely the per-variable degree. The scalar route worsens D_reg by adding variables (NR-022); an intrinsic route would have to lower per-variable degree by *more* than it costs in added variables/equations to net a D_reg win. That trade is the real bar.

## 2.6 What remains OPEN for PO-004

- **Intrinsic surface Semaev degree (W1).** Unknown whether the abelian-surface addition law yields a per-variable degree below 2^{m-1}; if it does, the D_reg bookkeeping (variable count vs degree) must be re-run. This is the live frontier (H14, NR-022 surviving open).
- **m >= 4 surface Semaev.** Only m in {2,3} tested for the scalar realization; the per-variable proof is m-uniform, but the intrinsic-surface degree at higher m is untested.
- **Whether degree-invariance + variable-count penalty is a *theorem* of no-advantage.** PO-004 (degree) + Lemma 1 (variable count raises D_reg) together strongly suggest scalar Weil can never help, but a clean combined statement "scalar Weil restriction never lowers D_reg of the descended decomposition system" has not been written as a proof (it would need a monotonicity lemma: adding variables at fixed per-variable degree does not lower D_reg).

---

## 3. Summary table

| Target | Statement (one line) | Label | Conditional on | Where it could break |
|---|---|---|---|---|
| Lemma 1 | D_reg(Delta, n) is a symmetric function of the degree multiset and n | THEOREM | nothing (Froberg series is a symmetric product) | n/a |
| PO-001 | No S_m-equivariant, n-preserving coordinate change lowers the exploitable Gröbner solving cost below the x-ring (D_reg conserved) | RESTRICTED THEOREM (model M) | H-SR (semi-regularity), H-BAL (degree balance), localization gate = necessary (PO-003) | non-equivariant change (C1), rational phi (C2), fixed-degree FB on E(F_p) (C3), gate-PASS prime-field fall (C4) |
| PO-004 | Per-variable Semaev degree is invariant under scalar (F_p-linear basis-split) Weil restriction | THEOREM | nothing (F_p-linearity / multinomial homogeneity) | intrinsic surface law (W1), native T(A) Semaev (W2), non-F_p-linear encoding (W3) |
| PO-004 corollary | Scalar-Weil-pullback realization confers no D_reg advantage (worsens it) | NEGATIVE RESULT (NR-022, TOY-EVIDENCE) | scalar realization only | intrinsic surface IC (OPEN) |

## 4. Next concrete actions (proof obligations, not closures)

1. **Prove the missing H-BAL lemma** (PO-001): show S_m-equivariant graded phi of fixed weight preserves the Froberg-feeding degree multiset, upgrading PO-001 to "RESTRICTED THEOREM under H-SR only."
2. **Prove the gate-FAIL theorem** (PO-001): every first fall below D_reg of an S_m-equivariant n-preserving Semaev system has zero support on the summation rows. This makes PO-001 unconditional in model M.
3. **Prove the variable-count monotonicity lemma** (PO-004): adding variables at fixed per-variable degree does not lower the semi-regular D_reg, converting PO-004 + Lemma 1 into a no-advantage theorem for scalar Weil.
4. **Empirical: build and meter the intrinsic abelian-surface summation relation** (W1) at p=127, m in {3,4}; this is the one construction that can escape both PO-001 and PO-004 and is the strongest surviving algebra-track frontier.
5. **Empirical: test a genuine rational (2-isogeny x-map) pullback** (C2) under `meter_gated`; the one untested phi that might violate H-BAL favorably.



---

## Appendix A. Reconciling the two D_reg conventions (sanity check, light Sage/Python)

The campaign uses two numbers both called "D_reg" and they must not be conflated:

1. **Yokoyama closed form** D_reg^Y = m*d + d_S - m, where d = FB-constraint per-variable degree and d_S = Semaev per-variable degree. For m=3, d=|FB|, d_S=2^{m-1}/... (the per-VARIABLE Semaev degree, =2 for m=3 in the x-ring x-line presentation). This is a *bound/formula* on the solving degree of the naive pipeline (NR-001).

2. **Audited Froberg meter** D_reg^F = first non-positive coefficient of prod(1-t^{e_j})/(1-t)^n where the e_j are the *total* generator degrees in the n-variable presentation, computed by `semireg_Dreg` in `round016_gated_meter.sage`. For the x-ring m=3 |FB|=4 presentation with total-degree multiset [12,4,4,4] in n=3 variables, D_reg^F = 10 (verified by an independent pure-Python re-implementation of the Froberg series; matches the campaign's reported {7,10,12} for |FB| {3,4,5}).

These differ (e.g. 13 vs 10 at |FB|=4) because they count in different variable/degree presentations (per-variable bound vs total-degree Froberg in the reduced ring). **PO-001 / Lemma 1 are stated for D_reg^F**, the meter's quantity, which is the one actually measured across the campaign. The conservation claim is about the meter's D_reg^F being invariant under the multiset-preserving rebalancing, NOT about the closed form D_reg^Y.

**Independent verification of Lemma 1 (multiset symmetry of D_reg^F):**

```
profile [12,4,4,4] n=3 -> D_reg^F = 10
profile [4,12,4,4] n=3 -> D_reg^F = 10   (permutation of the multiset)
profile [4,4,4,12] n=3 -> D_reg^F = 10   (permutation of the multiset)
```

All permutations of the same total-degree multiset give the same D_reg^F, confirming Lemma 1 numerically. This is the mechanism behind PO-001: an S_m-equivariant change that *permutes/rebalances degree among the generators while preserving the total-degree multiset and n* cannot change D_reg^F.

**The honest gap, made numerical.** A genuine attack would need a NON-multiset-preserving drop:

```
genuine drop (S deg 12->4, FB block unchanged) [4,4,4,4] n=3 -> D_reg^F = 7   (< 10)
```

This 10 -> 7 drop is exactly what a sub-rho representation change would have to achieve, and it is precisely what NO tested S_m-equivariant change achieves (because the FB block rises to compensate, keeping the multiset). The disproof tracks C1/C2/C3 in section 1.5 are the searches for a change that realizes a multiset-NON-preserving drop. The e-ring's apparent drop is illusory at the level of D_reg^F: the e-ring system [4,2,2] in n=3 (S_4 collapses to total degree 4, FB constraints to degree 2) has a DIFFERENT multiset and a DIFFERENT D_reg^F number, but its *exploitable* solving degree is unchanged because its sub-D_reg fall is gate-FAIL (FB-localized; NR-018/019/027/032). This is the subtle point that H-BAL (degree balance) plus the gate-FAIL theorem (action item 2) together formalize: literal D_reg^F can shift between representations, but the *exploitable* D_reg (the one a gate-meaningful fall would lower) is conserved.

This appendix corrects a potential overclaim: PO-001 is NOT "the literal Froberg number is identical across all representations" (it is not -- e-ring shifts it). PO-001 is "the exploitable solving degree, the gate-meaningful first fall, is conserved at the x-ring value." That is the bankable, evidence-grounded statement.
