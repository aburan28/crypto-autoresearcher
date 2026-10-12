# TASK-20261002-a84e65 — zero-run design: HEUR-HARVEST-FV-1(a), the two-sum coincidence count of F_V against a closure-matched random null

- **Role and session:** idea-generator, policy research-deep, independent session, 2026-10-03. This session did not author TASK-20261001-9b3e70. See §12 for what that rests on.
- **Runs:** none. No N_2 value, decomposition count or statistic of any F_V was computed. Every number below is hand arithmetic, labelled **scratch**. None of it is a measurement.
- **Curve selection:** not done here. §4 specifies the procedure and its seed labels for the executor's pre-run step.
- **Status:** nothing committed and no status changed. The draft contract is `proposed-records/EXP-SEMBIN-3d9a71/specification.yaml`, with status `review_required` and `approved_by` absent. It cannot be approved until H-SEMBIN-c7e1d4, or a superseding record carrying HEUR-HARVEST-FV-1, is filed, and until JR-3's verdict on the statement has been composed (DEC-20261002-7a3f19 R11). If the statement changes, this contract is re-drafted. It is not amended.
- **Security:** nothing here is a statement about the security of any curve, in either direction.

---

## 0. One-page summary

**Statistic.** For a negation-closed list F of points of ⟨P⟩, let r_F(g) be the number of 2-element subsets {a, b} ⊂ F with a + b = g. Then

    N_2(F) = Σ_{g ≠ O} C(r_F(g), 2).

This is exactly the heuristic's count. It counts unordered pairs of distinct 2-subsets with equal sums, which excludes {a,b} = {c,d}. It also drops the g = O class, which excludes "both sides zero".

Each list also yields three derived counts:
- Z4 counts zero-sum 4-sets with no antipodal pair, up to global sign.
- Z3 counts zero-sum multisets {t, t, u, v}, up to sign.
- R_2 is the orbit count. It is Z4 + Z3 under ⟨−1⟩, and (Z4 + Z3)/n under ⟨−1, π⟩.

**N_2 = 6·Z4 + 2·Z3 holds exactly** (§2, A1). The counter must satisfy this identity, and it is a gate.

**Null.** For each sampled subspace V_i, M independent lists F* of exactly |F_{V_i}| elements are drawn. Each list is a union of k distinct closure orbits of uniform elements of ⟨P⟩: ±(r·P), or {±λ^j·r·P} on Koblitz curves with σ-stable V.
- The null is counted in Z/ℓ on the exponents r. That path is exact and cheap.
- A subset of null lists is also pushed through the point-arithmetic path that counts F_V. The two paths must agree exactly (gate G4).
- λ̂ is the null-sample mean. The scratch formula |F|^4/(8ℓ) is used only in a [½, 2] sanity band on the counter. It never enters a prediction.

**Decision rule.**
- Each cell (curve, D, V-distribution) has four pre-registered tests, all calibrated by the exact stratified permutation (V_i is exchangeable with its own M null lists under H0):
  - **S1:** the standardised cell total of N_2, as an exact convolution. Its maximum over cells, against the Bonferroni tail, is the card's "largest standardised excess".
  - **S2:** two-sample KS on N_2.
  - **S3:** Pearson goodness of fit of R_2 to Poisson(λ̂_R,null).
  - **S4:** the largest single-V R_2 against the null tail.
- Five arm-pooled S1 tests are added.
- **α = 10^-3 family-wise, Bonferroni, over m_max = 4·85 + 5 = 345 tests.** That is a raw p ≤ 2.90·10^-6, two-sided. m_max is frozen now. It counts every potentially admissible cell, so it does not shrink when Koblitz cells fail admission.
- **FALSIFIED** requires all of the following:
  - every gate and the mutation self-test pass;
  - the AP and GAP positive controls are flagged at corrected p < 10^-6;
  - the null-as-V placebo family rejects nothing;
  - the cell's null passes its Poisson calibration;
  - some F_V test reaches a raw p ≤ 2.90·10^-6.

  A pre-registered fresh-seed replication of the falsifying cell then labels the result REPLICATED or UNREPLICATED.
- **PASS** requires the same validity conditions, no rejection, and the planted-relation sensitivity check meeting its floor. A pass is reported with ρ̂ (the F_V/null rate ratio) and its 99% CI per cell and per arm.
- **INCONCLUSIVE** covers four cases: a positive control not flagged, a placebo rejection, null calibration failing at ≥ 2 cells, or no rejection while sensitivity is below its floor.
- **INVALID** covers any gate failure, an uncaught mutant, or a path mismatch. That is a defect, never evidence. A timeout, crash or memory stop is infrastructure. It checkpoints the run and is never evidence.

**Smallest detectable effect.** Per cell, power 0.9, excess side; scratch, normal approximation to the exact test.
- N_V = max(30, ⌈300/λ_2⌉) subspaces and M = 5 null lists per subspace give about E = 50 expected primitive relations per cell.
- The detectable rate ratio is **ρ_90 ≈ 2.0 (one bit) for every λ_2 ≤ 2^3, 1.80 at 2^4, 1.57 at 2^5 and 1.40 at 2^6.**
- The arm-pooled ρ_90 is about 1.14 for the h = 4 ordinary arm and 1.27 for the h = 2 ordinary arm.
- **At λ_2 = 2^-2** each list has P(R_2 = 0) ≈ e^{-1/24} ≈ 0.959 under the null. N_V = 1200 subspaces are needed to reach ρ_90 = 2. At that size:
  - per-cell deficits cannot be resolved, except a near-total absence of relations;
  - V-classes rarer than about 1/1200, such as V ⊂ ker Tr at density 2^-D, are invisible.
- V1's starting point of 10 subspaces and 100 null lists is the seconds-per-cell variant. It resolves only ρ ≳ 25 at λ_2 = 2^-2 and ρ ≈ 1.63 at 2^6 (§6), which is why it is not adopted.

**Controls.**
- (i) The null, plus a null-as-V placebo arm and a Poisson calibration of the null.
- (ii) The positive control F_AP = ±{P, …, (|F|/2)P}, together with random dilates ±{j·s·P}. All of them must give the identical N_2 that an independent integer computation gives.
- (iii) Planted lists with a known number of injected parallelograms {u, u+v, u+w, u+v+w}. The counter must return exactly the independent recount.
- (iv) Every λ_2 grid value at at least two n, across five n.
- (v) Seeds derived from unique labels, with a collision gate.
- (vi) A nearby object with known non-AP structure:
  - rank-2 GAPs ±{(i·g_1 + j·g_2)P}, with g_2 = λ·g_1 on Koblitz curves (a Frobenius GAP);
  - a deficit control, alteration-built Sidon lists with R_2 = 0;
  - a sensitivity calibration that injects planted relations at ρ ∈ {1.5, 2, 3}.
- A further reason is stated: by Theorem C of KN-FIND-ffe1df, no coordinate-defined set with exact additive structure exists in a prime-order group. The known-structure objects therefore have to be scalar-built.

**Arms.**
- **O4** — two ordinary h = 4 curves per n, random V.
- **O2** — one ordinary h = 2 curve per n, random V.
- **W** — window subspaces span{z^s, …, z^{s+D−1}}. This is the factor-base shape in the literature (KR-IC-73db3f).
- **KR** — Koblitz curves with random V, wherever the curve is admissible.
- **KS** — Koblitz curves with σ-stable V, exhaustive over all σ-stable V of the dimension. It is likely empty or nearly empty on this n-grid (A11).
- **V3** — the optional weak arm: ECC2K-130, D = 16. Its scratch prediction is λ ≈ 2^-76, so any non-zero count stops the arm and is certified. A zero confirms nothing about the dense regime.
- Transfer to n ≥ 97 is **by assumption** (TA-1).

**Cost.** Scratch, about 1.9·10^10 point additions and about 2·10^11 integer pair-sums in total. With a compiled kernel that is about 2 CPU-hours: seconds for the median cell, and up to about 8 minutes for the n = 47, λ ≤ 1 cells. Pure Python is about 100 times slower and is not viable.

**Draft id.** EXP-SEMBIN-3d9a71. The token was chosen by hand because no shell was available (§12).

**Ambiguities in HEUR-HARVEST-FV-1(a).** §2 gives each one with a proposed restatement.
- **A1 (material).** "N_2(F) is Poisson" is false for every negation-closed list, including F* itself. Coincidences come in clumps of 6 (and 2), so N_2(F*) has variance/mean ≈ 6, or ≈ 6n for π-closed lists. As worded, the clause is falsified by its own null. The Poisson clause belongs on R_2, not on N_2.
- **A2.** Whether {a, a} pairs count. On Koblitz σ-stable lists this decides whether |F| formal identities 2a = μπa − π²a are counted.
- **A3.** "π-images excluded" has three readings.
- **A4.** "Fix V" does not say whether it means every V or a random V.
- **A5–A6.** The size match and the omitted |F|^3/(2ℓ) term.
- **A7.** No tolerance is stated.
- **A8.** Which λ the falsification's tail clause uses.
- **A11.** The π-closure sub-clause may be untestable on this n-grid.

---

## 1. The heuristic, as stated (verbatim, not edited)

Source: `coordination/tasks/TASK-20261001-9b3e70/proposed-records/heuristic-restatement.md`, lines 24–26 (shared definitions) and 54–60 (§4). These are copied character for character. The file is not hash-fixed by any receipt (§12, DP-2).

> - **Group.** E/F_{2^n} is a binary curve with n prime. ⟨P⟩ ≤ E(F_{2^n}) has prime order ℓ and cofactor h ∈ {2, 4}.
> - **Factor base.** V ⊂ F_{2^n} is an F_2-subspace of dimension D. The factor base is F = F_V = {Q ∈ ⟨P⟩ : x(Q) ∈ V}, which is negation-closed, with |F| ≈ 2^D / h (heuristic count, not derived exactly here).
> - **Koblitz case.** On a Koblitz curve with σ-stable V, F is also π-closed.

> **Formal statement.** Fix (n, E, ⟨P⟩, V) as in §2, with ℓ prime, and let F = F_V. Let F* be a uniformly random negation-closed list of the same size, also π-closed on Koblitz curves with σ-stable V: a union of the same number of ±-orbits (or ⟨±π⟩-orbits) of uniformly random elements of ⟨P⟩. Two statistics must be indistinguishable between F and F*, up to the stated tolerance:
>
> - **(a) Two-sum coincidences.** N_2(F) is the number of unordered pairs {{a, b}, {c, d}} ⊂ F with a + b = c + d, excluding formal identities:
>   - excluded identities are {a, b} = {c, d}, and pairs where both sides are 0 (a = −b and c = −d);
>   - on the Koblitz case, π-images are also excluded.
>
>   N_2(F) is Poisson-distributed with the same mean λ_2 as N_2(F*). For a random list, λ_2 ≈ |F|^4/(8ℓ). The constant here is scratch and must be fixed by the null sample, not by this formula.

The falsification condition of FV-1, lines 69–71, is copied verbatim:

> At any tested cell, either of these, with the null F* passing its own calibration and the positive control detected:
> - the empirical distribution of N_2 or of the decomposition count departs from the F* null at p < 10^-3 after Bonferroni correction over all cells;
> - the largest-count cell exceeds the Poisson tail predicted by λ at p < 10^-3.

### 1.1 Every quantifier, named

| quantifier | as stated | as this contract reads it (scope of the test) |
|---|---|---|
| curves | "Fix (n, E, ⟨P⟩, V)": a binary E/F_{2^n}, n prime, ⟨P⟩ of prime order ℓ, cofactor h ∈ {2,4} | ∀ such (n, E, P). Tested on n ∈ {31, 37, 41, 43, 47}: 3 ordinary curves per n (2 with h = 4, 1 with h = 2), selected by seed, plus every admissible Koblitz E_a, a ∈ {0, 1} |
| V | "Fix … V", an F_2-subspace of dimension D | Read as ∀V. Tested by sampling: uniform D-dimensional V (arms O4, O2, KR); every window V_s = span{z^s,…,z^{s+D−1}} (arm W); every σ-stable V of dimension D (arm KS, exhaustive). A ∀V failure on V-classes of density below about 1/N_V is invisible (§6) |
| D | implicit, dim V | Integer D per (n, h), chosen so that the scratch λ_2 lands on the grid {2^-2,…,2^6}; odd exponents for h = 2 (§4) |
| closure group Γ | negation; also π "on Koblitz curves with σ-stable V" | Γ = ⟨−1⟩ for ordinary curves and for Koblitz curves with non-σ-stable V. Γ = ⟨−1, π⟩, orbits of size 2n, for Koblitz curves with σ-stable V |
| F* | uniform union of the same number of Γ-orbits | Matched per V_i to the realized k_i = |F_{V_i}|/|orbit|: distinct orbits of uniform r ∈ [1, ℓ−1] |
| exclusion set | {a,b} = {c,d}; a = −b and c = −d; "π-images" on Koblitz | The first two exactly, via N_2 = Σ_{g≠O} C(r(g),2) over 2-subsets. "π-images": A3; read as orbit counting in R_2. N_2 itself carries no π exclusion, because the null carries the same orbits |
| tolerance | "up to the stated tolerance" | None is stated in (a) (A7). The operative tolerance is this test's resolution, ρ_90 (§6) |

---

## 2. Ambiguities and untestable wording, reported separately, with a proposed restatement

These findings are reported, not designed around. JR-3 (REVIEW-SEMBIN-20261002-c7e1d4) rules on the statement in parallel. If the statement changes, this contract is re-drafted before approval.

**A1 (material). The Poisson clause is false under the heuristic's own null.**
- Take F negation-closed and a non-trivial coincidence {{a,b},{c,d}}. Then T = {a, b, −c, −d} is a zero-sum 4-set.
- Each such T with distinct elements and no antipodal pair yields exactly **six** coincidences: three pairings times two orientations, {{t_i,t_j},{−t_k,−t_l}}. The set −T yields the same six.
- A degenerate multiset {t, t, u, v} with 2t + u + v = O yields exactly **two**: {{t,u},{−t,−v}} and {{t,v},{−t,−u}}.
- Hence the exact identity **N_2 = 6·Z4 + 2·Z3**. This is scratch derivation, and it is checked by gate G9 and by brute force (G1).

Under the random model, Z4 ≈ Poisson(|F|^4/(48ℓ)) and Z3 ≈ Poisson(|F|^3/(4ℓ)), both scratch. So:
- E N_2 ≈ |F|^4/(8ℓ) + |F|^3/(2ℓ), which matches the restatement's leading term;
- Var/E ≈ 6.

On σ-stable Koblitz lists, ⟨π⟩-orbits of zero-sum sets have size exactly n:
- π^j T = ±T would need λ^{j·o} = ±1 with o ≤ 4 < n prime;
- λ has odd order n, so −1 is not a power of λ.

Clumps are therefore 6n, and Var/E ≈ 6n. **N_2(F*) is not Poisson, so "N_2(F) is Poisson-distributed with the same mean" fails for F* itself**, and the clause is falsified by its own null whatever F_V does. The quantity that is approximately Poisson is the orbit count R_2.

This contract therefore:
- tests "same distribution" on N_2 exactly as worded (S1, S2), using distribution-free permutation calibration;
- tests the Poisson clause on R_2 (S3, and N-POI on the null);
- pre-registers the A1 prediction as a secondary check: the null's N_2 variance/mean lies in [4.5, 7.5] pooled over ordinary cells with λ_2 ≥ 2^2. A VMR near 1 would refute this analysis, and A1 would then be withdrawn by a new record.

**A2. Are {a, a} "pairs" allowed?**
- The scratch λ_2 ≈ |F|^4/(8ℓ) counts 2-subsets, which suggests "no".
- On σ-stable Koblitz lists the characteristic polynomial π² − μπ + 2 = 0 makes 2a = μπ(a) − π²(a) a formal coincidence {a,a} = {μπa, −π²a} **for every a ∈ F**. With {a, a} allowed, N_2 would carry |F| deterministic formal identities, far above λ_2.
- Under the 2-subset convention, no exact identity with ±1 coefficients exists (scratch argument):
  - f(π) = 0 for f ∈ Z[x] forces (x² − μx + 2) | f;
  - so f ≡ x(x+1)g mod 2 and f(0) is even;
  - after factoring out x^k, a ±1 polynomial has odd constant term.
- Intra-orbit relations then occur only accidentally (f(π) ∈ 𝔩, about n^4/ℓ per orbit) and identically in F*.

Proposed reading: 2-subsets only.

**A3. "π-images are also excluded" has three readings:**
- (i) count ⟨π⟩-orbits of coincidences once;
- (ii) exclude the characteristic-polynomial identities, which only arise if {a,a} is allowed;
- (iii) exclude coincidences whose sides are π-related, which are already trivial, since π^j(a+b) = a+b forces a+b = O.

Proposed reading: (i), carried by R_2 on Γ = ⟨−1, π⟩. N_2 carries no π exclusion, and its null carries the same orbits.

**A4. "Fix V": every V, or a random V?**
- "Every V" is falsified by a single V.
- "Random V" is a distributional statement.
- Special V do exist:
  - V ⊂ ker Tr, at density 2^-D: for h = 2, F_V is empty if Tr(A) = 1 and doubled if Tr(A) = 0;
  - polynomial-basis windows, the literature's choice per KR-IC-73db3f;
  - σ-stable V.
- Proposed: split the claim into (a-rand), with V uniform, and (a-every), for every fixed V. This test addresses (a-rand) directly. It addresses (a-every) only through S4 and the two structured arms (W, KS).

**A5. "Of the same size".** |F_V| is a random variable of V. It fluctuates by about ±2^{(D−h')/2}, giving about ±25% in λ at D = 10 (scratch). The null is matched to the realized size per V_i, never to 2^D/h. The approximation |F| ≈ 2^D/h is itself an unstated count heuristic. It is recorded as a secondary measurement and plays no part in the decision.

**A6.** λ_2 ≈ |F|^4/(8ℓ) omits the Z3 term |F|^3/(2ℓ), a relative 4/|F| ≤ 1.6% here. It is harmless, because λ̂ comes from the null.

**A7. Tolerance.** "Up to the stated tolerance" points to no tolerance in clause (a). The operative tolerance becomes the reported resolution ρ_90.

**A8. Which λ in the falsification's tail clause?** Proposed: λ̂_R from the null sample, on R_2 (S4 calibrates the tail by permutation).

**A9. Direction.** "Indistinguishable" is read as two-sided. Excess and deficit both falsify.

**A10. Scope.** The statement quantifies over all prime n. Only n ≤ 47 is measured, plus the V3 weak arm at n = 131. Transfer is TA-1.

**A11. The π-closure sub-clause may be untestable on the declared n-grid.**
- σ-stable dimensions are sums of the degrees of the irreducible factors of x^n − 1, which are 1 and ord_n(2). Scratch values: ord_31(2) = 5, ord_37(2) = 36, ord_41(2) = 20, ord_43(2) = 14, ord_47(2) = 23.
- Only n = 31 (D ∈ {10, 11}) and n = 43 (D ∈ {14, 15}) give cells with λ_2 ≤ 2^8.
- EXP-BINSTD-c9c8a2 lists n = 31, a = 0 as Koblitz-inadmissible. That is a contract statement, not verified here.
- The KS arm therefore holds at most 7 cells, possibly none. Even when present it is gross-effect-only: 3 to 15 subspaces, E_R ≈ 0.08 to 10.
- If it is empty, the π-closure clause is recorded **UNTESTED**. Recommended: choose the next design's n by (Koblitz admissibility) × (σ-stable dimension near (n+9)/4).

**Proposed restatement (draft for JR-3, not adopted).**

> HEUR-HARVEST-FV-1(a′). Fix (n, E, ⟨P⟩, V) as in §2 with ℓ prime. Let Γ = ⟨−1⟩, or ⟨−1, π⟩ on Koblitz curves with σ-stable V. Let F = F_V, and let F* be a uniform union of the same number of distinct Γ-orbits of ⟨P⟩∖{O}. For a list L let r_L(g) = #{{a,b} ⊂ L : a ≠ b, a + b = g}, N_2(L) = Σ_{g≠O} C(r_L(g), 2), and R_2(L) = the number of Γ-orbits of zero-sum configurations, where Z4 is 4-sets with no antipodal pair and Z3 is multisets {t,t,u,v} (so that N_2 = 6·Z4 + 2·Z3). Then:
> - (i) N_2(F) and N_2(F*) have the same distribution;
> - (ii) R_2(F) is Poisson with mean λ_R = E R_2(F*), estimated from samples of F*.
>
> (a′-rand) holds for V uniform among D-dimensional subspaces. (a′-every) holds for every fixed V. Tolerance: no departure at Bonferroni-corrected 10^-3 in EXP-SEMBIN-3d9a71, at the resolution that experiment reports.

---

## 3. Statistic, null and arms (definitions the contract freezes)

- **Counting.** N_2 = Σ_{g≠O} C(r(g), 2), computed by hashing all 2-subset sums.
- **Z3** = ½·Σ_{t∈F} [r(−2t) − 1{−3t ∈ F}]. This is a closed form from the same table, independent of collision enumeration.
- **Z4** = (N_2 − 2·Z3)/6. It must be a non-negative integer (gate G9).
- **R_2** = Z4 + Z3, or (Z4 + Z3)/n on KS, which must also be an integer.
- **Structural identities checked on every list:**
  - Σ_g r(g) = C(|F|, 2), which is KN-FIND-007's conservation identity at m = 2;
  - r(O) = |F|/2;
  - r(g) = r(−g).
- **N_2 is a non-degenerate discriminator.** By KN-FIND-007 the first moment Σ r is fixed by |F| for every list. N_2 is the second moment, the additive energy of 2-subsets, which structure can move.
- **Null, integer path.** Exponents r drawn by a seeded DRBG, uniform in [1, ℓ−1]. Orbits must be distinct, with rejection on repeats. The KS null uses orbits {±λ^j·r}, with λ the eigenvalue of π on ⟨P⟩, checked by π(P) = [λ]P. Every list is counted in Z/ℓ.
- **Path equivalence.** At least 5 null lists per cell, plus every planted list and one AP/GAP list per cell, are materialised as points and counted by the F_V point path. All four counts must match exactly (G4).
- **Arms and cells.** The full table is in the contract.
  - **O4** (h = 4; 2 curves per n): cells (31,10), (31,11), (37,11–13), (41,12–14), (43,13–14), (47,14–15). That gives scratch λ_2 exponents e = 4D − n − 9 ∈ {−2, 0, 2, 4, 6}.
  - **O2** (h = 2; 1 curve per n): (31,9–10), (37,11–12), (41,12–13), (43,12–13), (47,13–14), with e = 4D − n − 6 ∈ {−1, 1, 3, 5}.
  - **W** (on O4a and O2): the same D, with all n − D + 1 windows. M = 20.
  - **KR**: the O4 D-set for a = 0 and the O2 D-set for a = 1, on each admissible Koblitz curve.
  - **KS**: (31,0,10), (31,0,11), (31,1,10), (31,1,11), (43,0,14), (43,0,15), (43,1,14). Each is exhaustive over σ-stable V (15, 15, 15, 15, 3, 3, 3), with M = 200 and λ_2 up to 2^8. That range exceeds the card's grid and is disclosed. The cell (43,1,15) is dropped: λ = 2^11 with |F| ≈ 2^14 exceeds the 4 GB key budget without an orbit-reduced counter.
- **C_max = 24 + 10 + 22 + 22 + 7 = 85 cells.**

## 4. Curve selection procedure (specified; executed by the executor's pre-run step, not here)

- **Field.** f_n is the irreducible trinomial z^n + z^k + 1 with least k, else the lexicographically least irreducible pentanomial. Irreducibility is shown by z^{2^n} ≡ z (mod f) together with f(0) = f(1) = 1, which is sufficient for prime n.
- **Ordinary curves.** y² + xy = x³ + A·x² + B, with A = 0 for the h = 4 roles and A = 1 for h = 2 (Tr(1) = 1 for odd n).
  - B is drawn by a SHA-256 counter DRBG under label `EXP-SEMBIN-3d9a71|curve|n|role|attempt`, with B ∉ F_2.
  - #E is found by baby-step giant-step for the order of a random point in the Hasse interval, required unique and confirmed on 20 random points.
  - Accept if #E = h·ℓ with ℓ proved prime by complete trial division to ⌊√ℓ⌋ (at most about 6·10^6 divisions at n = 47). No recalled Miller–Rabin bound is used.
  - Roles: O4a and O4b are the first two acceptances with A = 0; O2 is the first with A = 1.
- **Koblitz curves.** E_a: y² + xy = x³ + a·x² + 1. #E is computed from the Lucas sequence and cross-checked against BSGS on 10 points. The curve is admissible iff #E/h is prime, again by trial division.
- **Generator.** P = [h]R ≠ O, with [ℓ]P = O.
- **Calibration curves for the gates only.** CAL-13 and CAL-19 (n = 13, 19; ℓ ≤ 2^18) carry full discrete-log tables. They are never evidence.

## 5. Pre-registered prediction, scale and transfer

**H0, as worded (§1), on every cell.**
- **H0(a).** N_2(F_{V_i}) is exchangeable with N_2 of its M matched null lists.
- **H0(b).** R_2(F_V) ~ Poisson(λ̂_R), where λ̂_R is the cell's null-pool mean of R_2.

**Predicted reading.** No test rejects, ρ̂ ≈ 1. This prediction is true of a null. It is the reading the placebo arm must give.

**Sources.**
- HEUR-HARVEST-FV-1(a) (heuristic-restatement.md §4, draft, `internal`).
- The random-model justification there: the Poisson approximation for sparse sums of weakly dependent indicators, `recalled` (a pointer only). On R_2, not N_2: see A1.
- No constant comes from the scratch formula.

**Secondary predictions** (checks, not decision tests):
- the null VMR of N_2 lies in [4.5, 7.5] (A1);
- AP dilates give identical N_2, equal to the independent integer count;
- the ladder slope of log ρ̂ on log2 ℓ is 0 (S-TREND, reported with its CI).

**Scale.**
- Toy n ∈ {31, …, 47}. By the mechanical rule in docs/claims-and-verification.md, n = 31 is `toy` and n = 37–47 is `medium`. All are far below n ≥ 97.
- V3 at n = 131 (ECC2K-130, parameters from `inputs/BAILEY-2009-541-ECC2K130/paper_fulltext.md` lines 1093–1098) is a **disclosed-weak arm**:
  - D = 16 and 3 random V, with predicted N_2 = 0 (scratch λ_2 ≈ 2^56/2^132 = 2^-76);
  - a non-zero count stops the arm, emits a certificate (the four points, re-verified by independent arithmetic) and routes to the Coordinator, since it is rule-12 material as a contradiction of a heuristic at cryptographic labels;
  - a zero confirms nothing about the dense-regime rate.
- n = 163 is excluded, because no primary source for its parameters is vendored.

**Transfer.**
- **TA-1, BY ASSUMPTION.** The rate ratio ρ(λ) = E N_2(F_V)/E N_2(F*) at matched λ is the same at n ≥ 97 as measured at n ≤ 47. No sampling shortcut comparable to the Deuring correspondence is known (heuristic-restatement §5 V3).
- **TA-2.** Random-V results say nothing about structured V at other n.

## 6. Sample-size derivation (scratch)

**The unit is primitive events.** Under H0 the count R_2 of a list is Poisson with mean μ_R ≈ λ_2/6 (ordinary) or λ_2/(6n) (KS). The cell total of the V-sample has E = N_V·μ_R.

**Exact test, normal approximation for sizing.** The stratified permutation test compares each V_i with its own M + 1 values. Against a uniform rate ratio ρ = 1 + δ, power 0.9 at two-sided α′ = 2.90·10^-6 (z = 4.68) requires

    δ·(M/(M+1))·E ≥ (4.68 + 1.28)·√E   ⇒   δ_90 = 5.96·(M+1)/(M·√E) = 7.15/√E  (M = 5).

The design target is **E = 50, giving ρ_90 ≈ 2.0, i.e. one bit of relation yield**. That sets N_V = max(30, ⌈300/λ_2⌉). The floor of 30 is set by S2, S3 and S4.

| λ_2 (scratch, nominal) | per list P(R_2 = 0) | N_V | E = N_V·λ/6 | ρ_90 excess | ρ_90 deficit |
|---|---|---|---|---|---|
| 2^-2 | 0.959 | 1200 | 50 | 2.01 | none resolvable (only ρ ≈ 0) |
| 2^-1 (h=2) | 0.920 | 600 | 50 | 2.01 | none |
| 2^0 | 0.846 | 300 | 50 | 2.01 | none |
| 2^1 (h=2) | 0.717 | 150 | 50 | 2.01 | none |
| 2^2 | 0.513 | 75 | 50 | 2.01 | none |
| 2^3 (h=2) | 0.264 | 38 | 51 | 2.00 | none |
| 2^4 | 0.069 | 30 | 80 | 1.80 | ≤ 0.20 |
| 2^5 (h=2) | 0.005 | 30 | 160 | 1.57 | ≤ 0.43 |
| 2^6 | ~2e-5 | 30 | 320 | 1.40 | ≤ 0.60 |

- **Arm-pooled ρ_90**, excess side, scratch: O4 ≈ 1.14 (E ≈ 2460); O2 ≈ 1.27 (E ≈ 722); KR ≈ 1.16 when every Koblitz curve is admissible; W ≈ 1.17 (E ≈ 1280, M = 20).
- **W arm.** N_V = n − D + 1 is fixed by the arm. At low λ, per-cell E runs from 1.1 to 5.7, so those cells are gross-effect only, while cells with λ ≥ 2^4 reach E = 56–299.
- **KS arm.** E_R runs from 0.08 to 10.3, so it is gross-effect only throughout (A11).

**At λ_2 = 2^-2:**
- **Can detect:** a uniform excess of ρ ≥ 2 in a cell; a near-total absence of relations; a structured sub-population of V at density ≥ about 1% with a large per-V excess (S3, S4).
- **Cannot detect:**
  - any deficit except ρ ≈ 0;
  - V-classes rarer than about 1/1200, which includes the ker-Tr class at density 2^-D ≈ 2^-11 to 2^-12;
  - effects below a factor 2 per cell, which only the pooled arm test at about 1.14 reaches;
  - any statement about the dense-regime constant.

**Why not V1's 10 / 100?** With N_V = 10, E = 10λ/6:
- at λ = 2^-2, E = 0.42, and the one-sided exact Poisson threshold at 1.45·10^-6 is T ≥ 7, so ρ_90 ≈ 25;
- at λ = 2^6, E = 107 and ρ_90 ≈ 1.63.

That is the seconds-per-cell design, and it can only see gross structure. The card's "seconds per cell" is honoured for the median cell, not for the largest (§10).

**M = 5** null lists per V gives a variance factor of 1.2. The null is cheap in Z/ℓ, so M is set by the factor (M+1)/M, not by cost. W uses M = 20 and KS uses M = 200.

## 7. Controls

| id | what | required reading |
|---|---|---|
| (i) NULL | Matched null, M per V; placebo arm, one held-out null list per stratum run as "V"; N-POI, the Poisson heterogeneity of the null's R_2 by conditional-multinomial Monte Carlo; N-SCALE, λ̂_null/(|F̄|^4/(8ℓ)) ∈ [½, 2] as a counter sanity band only | Placebo: no test at raw p ≤ 2.90·10^-6. N-POI: p ≥ 10^-3/85 per cell. N-SCALE inside the band |
| (ii) PC-AP | F_AP = ±{jP : 1 ≤ j ≤ k} and 29 random dilates ±{j·s·P}, k = median |F_V|/2, against matched nulls | S1 corrected p < 10^-6 at every admitted random-V cell. All 30 N_2 identical and equal to the independent integer count over ±{1..k} (G5) |
| (iii) PLANT | Null lists with k_inj ∈ {1, 2, 5, 20} injected parallelograms {u, u+v, u+w, u+v+w}, each adding one Z4 orbit. On KS lists the four elements' full ⟨±π⟩-orbits are added, giving N_2 += 6n and R_2 += 1. Also Z3-type injections t, u, −2t−u | Point path = integer path = brute force where |F| ≤ 48. Increment = injected count, except accidental extras identified by the exact integer recount |
| (iv) SCALE | Each λ grid value at ≥ 2 n; five n; S-TREND | Reported; a band with fewer than 2 admitted n is INCONCLUSIVE for that band |
| (v) SEEDS | Every random draw keyed by a unique label `EXP-SEMBIN-3d9a71|<cell>|<role>|<i>|<j>`; V, null, placebo, plant and control streams disjoint | G11: no label collision; no repeated V within or across cells; no repeated null orbit set |
| (vi) NEARBY | PC-GAP: rank-2 GAP ±{(i·g1 + j·g2)P : 1≤i≤L1, 1≤j≤L2}, L1·L2 = k; Koblitz curves use g2 = λ·g1 (a Frobenius GAP). PC-SID: an alteration-built Sidon list (R_2 = 0) at cells with λ ≥ 2^2. PC-SENS: resampled pseudo-cells with Poisson((ρ−1)μ̂) injected relations, ρ ∈ {1.5, 2, 3}, 200 pseudo-cells per random-V cell | GAP: S1 corrected p < 10^-6. SID: S1 lower-tail corrected p < 10^-6. SENS: power(ρ=2) ≥ 0.5 at the cell and ≥ 0.9 at the arm, else PASS is unavailable there |

**Why no coordinate-defined nearby object.** By Theorem C of KN-FIND-ffe1df, a prime-order group has no exact sum-compatible coordinate projection. So no coordinate-defined subset with exact additive structure exists at toy scale. The known-structure objects must be built by scalar multiplication. The Frobenius GAP is the most curve-natural such object.

## 8. Gates (no shared code) and the mutation self-test

**R3 compliance.** Nothing reuses `experiments/EXP-SEMBIN-04ec3c/code/v2/`. Every JV-2 defect class has a designed counterpart here:

| JV-2 class | here | gate |
|---|---|---|
| off-grid d | size mismatch and D/λ mislabel | G6, G7 |
| domain predicate | the exclusion rules | G1, G3 |
| enumerator (sweep) | pair enumerator and cell enumerator | G2 |
| shared input | ℓ, λ, f_n, #E read once | G8 |
| baseline column | the null / λ̂ | G7, NULL controls |

- **G0 ARITH.** Two independently written GF(2^n) and curve-addition modules. Module B is used only by gates. They must agree on 10^4 random additions per curve, on [ℓ]P = O and on [#E]R = O.
- **G1 BRUTE.** A literal O(|F|^4) enumeration from the §1 definition, using module B, on:
  - 50 lists each at |F| ∈ {16, 24, 32, 48}, in Z/101, Z/1009 and Z/10007 (the dense regime);
  - F_V on CAL-13 and CAL-19 at |F| ≤ 48, where a full dlog table also gives the integer path;
  - all planted lists with |F| ≤ 48.

  The fast counters must match on N_2, Z4, Z3 and R_2 exactly.
- **G2 ENUM.** Every list must satisfy:
  - Σ r(g) = C(|F|, 2) and r(O) = |F|/2;
  - r(g) = r(−g);
  - a per-row partner tally of |F| − 1, recorded by the enumerator's caller rather than by the enumerator.

  Separately, the emitted cell set must equal the frozen cell table, read from an independent copy.
- **G3 EXCL.** Hand-built cases with expected values written before code:
  - {±a, ±b} gives N_2 = 0;
  - one parallelogram gives N_2 = 6, Z4 = 1;
  - {±t, ±u, ±(2t+u)} gives N_2 = 2, Z3 = 1;
  - {±t, ±3t} gives N_2 = 0 and Z3 = 0;
  - one full ⟨±π⟩-orbit at n ≥ 31 gives N_2 = 0. At the calibration curves the expected value is the brute-force value, because accidental intra-orbit relations of order n^4/ℓ can occur there.
  - one parallelogram whose four elements lie in distinct ⟨±π⟩-orbits, closed under π, gives N_2 = 6n, Z4 = n, R_2 = 1.
- **G4 PATH.** Integer path = point path on the §3 subsets.
- **G5 DILATION.** As in control (ii).
- **G6 MEMBERSHIP.** Checked on every element:
  - x(Q) ∈ V, Q on E, [ℓ]Q = O (module B, sampled at 1%, all at small cells);
  - F_V is negation-closed;
  - an independent recount of |F_V| on 3 V per cell.
- **G7 NULL.** |F*| = |F_V| per stratum. Orbits are distinct. KS orbits have size exactly 2n. λ² − μλ + 2 ≡ 0 (mod ℓ) and π(P) = [λ]P. A top-8-bit histogram χ² check with p > 10^-6 serves as a weak sanity check.
- **G8 INPUT.** ℓ is recomputed from the curve by module B: Lucas plus BSGS, from two independent points. It is checked prime by trial division, and f_n is re-tested for irreducibility.
- **G9 IDENTITIES.** N_2 = 6·Z4 + 2·Z3 with Z4 a non-negative integer. On KS, Z4 and Z3 are both ≡ 0 (mod n).
- **G10 STATS.** Checked on synthetic inputs:
  - the exact convolution agrees with brute-force enumeration on N_V = 3, M = 2;
  - 1000 placebo p-values are not rejected as U(0,1) at 10^-3;
  - planted shifts reject;
  - m_max = 345 is a constant.
- **G11 SEEDS.** As in control (v).
- **G12 MUTATION SELF-TEST.** Mutants M1–M20 are listed in the contract, at least one per defect class:
  - exclusion logic, by two mutants;
  - pair enumerator;
  - hash key;
  - field reduction;
  - the a = −b special case;
  - null size, null closure and null range;
  - KS closure;
  - ℓ input and λ input;
  - stratification and p-value;
  - orbit count;
  - cell enumerator;
  - Bonferroni m;
  - seed reuse;
  - V rank;
  - window basis.

  Each mutant must make at least one gate fail, and the unmutated code must pass. An uncaught mutant makes the run INVALID.

## 9. Decision rule and outcomes (decidable from the metrics)

- **Validity.** G0–G12 pass, N-SCALE holds at every cell, and the placebo family has no rejection.
- **Controls OK.** PC-AP and PC-GAP are flagged at every admitted random-V cell, and PC-SID at every cell with λ ≥ 2^2.

| outcome | condition |
|---|---|
| **INVALID** (defect, not evidence) | Any gate fails, any mutant is uncaught, N-SCALE is out of band, or a path mismatch occurs. Nothing is read |
| **INCONCLUSIVE** | Valid, but one of: a placebo rejection; PC-AP or PC-GAP not flagged; PC-SID not flagged; N-POI fails at ≥ 2 cells. A single N-POI failure makes only that cell inconclusive |
| **FALSIFIED** (HEUR-HARVEST-FV-1(a), at the cell's scope) | Valid, controls OK, and the cell's N-POI passed; any F_V test (S1–S4 at any admitted cell, or an arm-pooled S1) reaches raw p ≤ 2.90·10^-6. The direction (excess, deficit, non-Poisson, tail), the arm and the cell are recorded. A pre-registered replication follows (fresh label `rep1`, same N_V, one test, α = 10^-3): **REPLICATED** if it rejects, **UNREPLICATED** otherwise |
| **PASS** (at the stated resolution) | Valid, controls OK, no rejection, and PC-SENS power(ρ=2) ≥ 0.9 at each arm-pooled level and ≥ 0.5 at ≥ 80% of random-V cells. Reported with ρ̂ and a 99% CI per cell and per arm |
| **PASS-UNDERPOWERED** (reported as INCONCLUSIVE) | Valid, no rejection, but the sensitivity floor is unmet |
| **UNTESTED** (sub-clause) | KS arm empty: the π-closure sub-clause. A W cell with E < 1: that cell |
| **V3** | Any N_2 ≥ 1: STOP, certify, route (FALSIFIED at that cell, with no multiplicity needed at p ≈ 2^-76). Zero: recorded as consistent; confirms no rate |

- A timeout, crash or memory stop is infrastructure. It is never evidence.
- A FALSIFIED reading routes the cell to the Coordinator before any interpretation. An excess at fixed λ that grows along the n-ladder would be the exponent-relevant signature that makes F_V an object worth attacking. A one-off constant-factor excess or deficit falsifies the distributional premise of HEUR-HARVEST-FV-2's random-model justification and moves no exponent by itself.
- **Link to OPEN-A.** F_V is the 0-fibre of the F_2-linear filter x ↦ x mod V. An excess of N_2 there would be weak first evidence of approximate sum-compatibility of that filter, which is OPEN-A's question, and R10 ranks OPEN-A as exponent-relevant. The test is also a cheap one-fibre probe of OPEN-A. It does not settle it.

**What each outcome discriminates:**
- E1, the heuristic holds: PASS.
- E2, the linear condition leaks additive structure: an excess, possibly growing on the ladder.
- E3, repulsion, i.e. F_V more Sidon-like than random: a deficit.
- E4, instrument artifact: caught by the placebo, path, gate and control set.
- E5, a size-only effect: |F_V| ≠ 2^D/h while the rate at matched size is null. That is not a falsification of (a); it is recorded as a secondary measurement.

## 10. Cost estimate (scratch; advisory)

**Point-path additions for F_V**, at |F|²/4 per V using negation symmetry:
- O4: 2.82·10^9 per curve, so 5.64·10^9 for two curves;
- O2: 4.22·10^9;
- W: 2.12·10^9;
- KR: ≤ 7.04·10^9;
- KS: < 10^8;
- **total about 1.9·10^10.**

The heaviest cells are n = 47, h = 2, D = 13 at 2.5·10^9 and n = 47, h = 4, D = 14 at 1.26·10^9.

**Integer-path null.** About 1.5·10^11 for M = 5 and W's M = 20, plus about 5·10^10 for the controls.

**Throughput assumptions.** Unmeasured, recorded at S0:
- about 5·10^6 affine additions per second with a portable C kernel using Montgomery batch inversion (KR-RHO-cb1c58);
- about 10^8 integer sums and hashes per second.

**Totals.** About 2 CPU-hours: about 20 s for the median cell and about 500 s for the largest. Pure Python is about 10^2 times slower (around 10 CPU-days) and is not viable. If no compiled kernel or numpy is available, that is an infrastructure stop, or an amendment that reduces N_V with ρ_90 recomputed. It is never a silent cut.

**Memory.** The largest list is |F| = 2^13, so 2^24 to 2^25 keys of 16 bytes, i.e. ≤ 512 MB. KS is capped at |F| ≤ 2^13. That is within 4 GB.

**Advisory envelope.** 8 scientific runs plus up to 8 infrastructure reruns, a 14,400 s watchdog per run, and 6 CPU-hours.

## 11. dominated_by and sota_delta

- **dominated_by: "n/a (no result claimed)".** A heuristic-validation experiment claims no algorithm.
- **Checked against:**
  - KN-FIND-ffe1df (read in full): Theorem C and the bucket-gain statistic. F_V is one fibre of an approximate filter. Adjacent, not dominated.
  - All 24 KR-RHO claim lines (read by Grep this session; none is an additive-energy statement).
  - KR-IC-73db3f, KR-IC-889857 and KR-IC-b0fcda, read in full.
  - KN-FIND-007, lines 1–80. The first-moment conservation means only N_2's second moment can move.
- **sota_delta: 0** on time, memory and data/queries, whatever the outcome. A falsification removes a premise and opens a routed attack question. It moves no frontier row without a separate algorithm and record.
- **Novelty of the design: `unverified`.**
  - N_2 is a normalisation of the additive energy of 2-subsets, standard additive combinatorics (`recalled`).
  - Character-sum bounds for points with x in a structured set exist for prime fields and intervals: Kohel–Shparlinski, a `recalled` pointer surfaced by a web search whose result titles only were seen, not opened.
  - No source stating a rigorous energy bound for {Q : x(Q) ∈ V} over F_{2^n} at density 4D ≈ n was found. A Weil-type error term on the 3-dimensional variety a + b = c + d is about q^{5/2}, against a main term of about 2^{4D−n} = O(1). That is scratch and `recalled`, and it is why the heuristic has no rigorous half at this density.

## 12. Honest accounting (inventor-protocol §5) and disclosures

```yaml
honest_accounting:
  objects_considered:
    - "N_2(F_V): the 2-subset additive energy (second moment of the pair-sum multiplicity) of the 0-fibre of x -> x mod V"
    - "R_2(F_V): Gamma-orbit count of zero-sum configurations (Z4, Z3)"
    - "closure-matched random lists F* (integer path) as the null object"
  lossy_projection_test: >-
    Not applicable as an object proposal. This is a measurement of a
    distributional premise. For the record: N_2 is invariant under the
    dilation action of (Z/l)^* and under Gamma. It is a lossy projection of
    the list, propagating under no group operation. KN-FIND-ffe1df Theorem C
    excludes an exact sum-compatible projection, so N_2 measures only an
    approximate residue in one fibre.
  depth_of_verified_structure: >-
    Derivation-grade, single session, unreviewed: the identity
    N_2 = 6 Z4 + 2 Z3, the Z3 closed form, the absence of +-1 pi-identities
    under 2-subsets, the ord_n(2) values and all sizing arithmetic. Every
    item is scratch and is checked by a gate before any reading.
  dominated_by: "n/a (no result claimed)"
  dominated_by_check: >-
    KN-FIND-ffe1df read in full; all 24 KR-RHO claim lines read; KR-IC-73db3f,
    KR-IC-889857 and KR-IC-b0fcda read in full; KN-FIND-007 lines 1-80. The
    other KR-IC rows were checked by title only.
  sota_delta: "0 on time, memory and data/queries; measurement-design contribution only"
  enumerated_closures:
    - closure: none
      note: >-
        Nothing is closed. A PASS would be a scoped, conditional validation at
        resolution rho_90, not a closure of the F_V attack question.
  open_directions:
    - "OPEN-A one-fibre probe: a FALSIFIED-excess reading feeds the J3 RC5 bucket-gain ladder directly"
    - "Choose n for the pi-closure sub-clause by (Koblitz admissible) x (sigma-stable dimension near (n+9)/4) (A11)"
    - "Clause 1(b), the decomposition counts V2: second moment only, by KN-FIND-007; not designed here"
    - "A rigorous energy bound for {Q : x(Q) in V} over F_{2^n} would supply the missing rigorous half of FV-1"
```

**Dispatch preconditions.** These are disclosed, not waived. They bind the dispatcher. The user requested this run now.
- **DP-1.** The receipt of TASK-20261002-31c9d7 does not exist (per the dispatch note). Its records are reported committed on main, which this session could not verify because it had no shell or git.
- **DP-2.** No receipt of TASK-20261001-d815a6 was found. A Glob of `coordination/tasks/TASK-2026100[12]-*/*` returned only DERIVATION.md. The heuristic-restatement.md bytes I read are therefore not hash-fixed. §1 quotes them verbatim, with line numbers, so that a reviewer can diff them.
- **DP-3.** archived_by TASK-20261002-5f0b2c is bound in the card. Its archive record was not checked.
- **DP-4.** No lane claim was made by me. I had no shell.

**Other disclosures.**
- **Identifiers.** No shell, so `allocate_id.py` was not run. EXP-SEMBIN-3d9a71 is a hand-chosen random 6-hex token. A Glob for `**/*3d9a71*` and Greps of `ledger/`, `experiments/**.yaml` and `knowledge/` found nothing. A committed-state check is owed: `allocate_id.py --check` and `git grep 3d9a71`.
- **Independence.** This session was started fresh on 2026-10-03 for TASK-20261002-a84e65. TASK-20261001-9b3e70's author was a 2026-10-01/02 session. That rests on the session boundary only. `tools/check_review_independence.py` was not run, and both sessions are one model family.
- **kb MCP.** Not in this session's tool surface. Grep and Glob were used instead.
- **Write scope.** Only `coordination/tasks/TASK-20261002-a84e65/`. No `knowledge/literature/` note was written, although the idea-generator role permits one. The card's write scope governs.
- **In-session rewrites, before handoff.** Both draft files were rewritten once by their author. DESIGN.md was rewritten to correct the wording of a G3 case and of the KS planted relation. specification.yaml was rewritten to quote three brace-containing scalars and to make `correspondence` a true null. No other content changed.
- **Mid-session web lookup.** One web search (Shparlinski / additive energy). Only the result titles were seen, and no source was opened. Pointers only.

**Read in full or in the relevant part:**
- the card;
- agents/idea-generator.md;
- AGENTS.md lines 150–239 and 491–580;
- DEC-20261002-7a3f19;
- heuristic-restatement.md;
- H-SEMBIN-c7e1d4.yaml;
- DERIVATION.md;
- EV-SEMBIN-b6d042;
- red_team_report.yaml (b2c916);
- .claude/skills/design-experiment/SKILL.md;
- templates/research-records.md lines 200–439;
- docs/claims-and-verification.md;
- docs/inventor-protocol.md;
- docs/target-result-profile.md;
- KN-FIND-ffe1df;
- KN-FIND-007 lines 1–80;
- knowledge/frontiers/ecdlp/README.md and the rows named in §11;
- EXP-BINSTD-c9c8a2 specification, lines 1–626, as a format and curve-procedure pattern only;
- inputs/BAILEY-2009-541-ECC2K130/paper_fulltext.md lines 1085–1100.
