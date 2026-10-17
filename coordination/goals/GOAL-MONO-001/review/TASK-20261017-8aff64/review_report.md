# Review report — TASK-20261017-8aff64 (red-team-breakthrough, GOAL-MONO-001, BATCH-dce635)

**Per-joint verdicts (the only verdicts; the Coordinator composes; no whole-goal verdict is given, RC-3/RA-C8).**

| joint | verdict | one-line reason |
|---|---|---|
| RA-1 ordered-base monodromy (CU-9 item 1) | **CONCUR (holds)** | Re-derived from the group law: generic monodromy over K(x_1..x_{m-1}) is (Z/2)^{m-2} acting regularly, arithmetic = geometric, uniform in the curve. My own S_4 sampling on j=0, j=1728, two supersingular, one generic and the census curves (20,000–50,000 tuples each, plus one exhaustive prime) shows only 1^4 and 2^2 on nondegenerate fibres, zero delta-rule mismatches, and 1^4 densities matching the exact finite-p expectation, not the order-2 competitor. |
| RA-2 symmetric-base monodromy (CU-9 item 2) | **CONCUR (holds)** | Re-derived: image of Z/2 wr S_{m-1} with kernel {±1} for m ≥ 4, order 2^{m-2}(m-1)!; S_4 = AGL(2,2) at m=4; 192, 1920, 23040 at m=5,6,7 (own permutation-group computation). Two scope corrections inside carve-out A2-d: m=6 is primitive; m=5 and m=7 each have exactly one block system (two blocks). My own symmetric-base sampling reproduces EXP-MONO-0e6e8f M1 (all five classes, S_4 densities) on six curves including j=0, j=1728 and a supersingular curve. |
| RA-3 the delta-rule (CU-9 item 3) | **CONCUR (holds)** | Derived as the specialization of RA-1 at unramified F_p-points. Holds on every squarefree full-degree fibre tested at m=3, 4 and 5 (zero mismatches on more than 500,000 fibres). OBS-1 reconciled: all 12,243 g-split "2+1+1" instances of the exhaustive C1/C2 blocks, regenerated here from the group law, are non-squarefree; my C3/C4 samples agree; no squarefree full-degree 2+1+1 exists. |
| RA-4 J4 adequacy | **CONCUR (holds)** | The J4 DISSENT holds on the merits on each of G-i (RA-1 holds in my own work), G-ii and G-iii. One anchored reading of criterion (a) is satisfied by the route-(a) object (exact S_4 identification on the symmetric base), but no committed text answers G-ii or G-iii on the merits, so RA-4's breaking artifact is not met. |
| proves-too-much | PT-1, PT-2, PT-3: the argument stops at the named step on each | PT-1: the Kummer group is trivial when the y_i lie in the base. PT-2: the independence step fails (f(x_1)f(x([2]P_1)) is a square). PT-3: the permutation part becomes A_3; image A_4. Numerics as the plan requires. |

- Card: `ledger/handoffs/TASK-20261017-8aff64.yaml` (sha256 computed here `222154b2…7745bb`, equal to the launch prompt's value); plan `REVIEW-MONO-20261017-8aff64` inline in the card.
- Role / binding: red-team / `red-team-breakthrough` (`.claude/agents/red-team-breakthrough.md`, `effort: max`, `model: claude-fable-5-1`); requested policy `review-breakthrough`.
- Snapshot read: branch `claude/quotient-summation-ecc2k-130-4y7t3o`, HEAD `ea22cdb551166a1732ecc13d6bbc2c7c0ed8c75e`.
- Write scope: `coordination/goals/GOAL-MONO-001/review/TASK-20261017-8aff64/` — exactly `review_report.md`, `computations.json`, `review_attestation.yaml`.
- Zero runs. No `RUN-*` directory. Nothing under `experiments/` read by code or written. Claim-tier ceiling toy (RC-8): nothing here is an ECDLP result; nothing is said about the relation-rate question, the D-4 count, extension fields or cryptographic scale.

## 0. Custody and order of work (RC-2)

**Step (1), digests.** Recomputed at HEAD before any other file was opened; all five equal the launch prompt's values:

| sha256 | path |
|---|---|
| 222154b2bf39557bb2bf6a3a256c09629df2f2672f85f8598362ddf85f7745bb | ledger/handoffs/TASK-20261017-8aff64.yaml |
| 86b9ea0d7275b9fcfeb5cb05ae87f63912847363f6b0d59a0ec723426ab6b779 | ledger/hypotheses/H-MONO-ebd400.yaml |
| f5f1b40e732e354acc45c5c64836e0f91dc79dccb7919dd7e4a619221288c33b | ledger/evidence/EV-MONO-e9dc3b.yaml |
| 7610b1fb7b40cc0f56da27260f1f8a44f81742cb5545e0dfa5d31ddea1fde36a | ledger/decisions/DEC-20260930-8553d4.yaml |
| 7de4f8805aa9fbd73edfa5dca7b8795ffe2b03c7f06bed84c104159657e87e7b | coordination/goals/GOAL-MONO-001/review/TASK-20260930-40470a/review_report.md |

**Steps (2)–(5), as executed.** The derivation of §1 was fixed, my own S_3, S_4 and S_5 were built (`rt_symbolic.py`), and the whole numeric programme (`rt_numeric.py`: defining-property checks, ordered-base and symmetric-base Frobenius sampling, the OBS-1 regeneration, the m=5 test, PT-2, PT-3, the sign-class group computation) was written, smoke-tested and launched **before** the TASK-20260930-40470a report was opened. That report, its handoff and its `computations.json` (by key) were read while the run was executing, and compared (§3–§5). The proves-too-much numerics are stages F and H of the same run (§6). RA-4 (§7) was read and written last. One addition after step (4): the ordered-base frequency comparison needed the exact finite-p expectation **conditioned on nondegeneracy**, so an exact enumeration of the degenerate locus (`rt_exact_cond.py`), a larger p=1009 sample (`rt_big1009.py`) and an independent validation (`rt_validate_exact.py`) were added; they changed no verdict.

**Blindness.** `coordination/goals/GOAL-MONO-001/review/TASK-20261017-ccd10c/` does not exist in this checkout; no claim or release record of that task and no part of `DEC-20261017-12e0f4` was opened. The session scratchpad is shared with other sessions and contained foreign directories (`blind/`, `rb/`, `held/`, `plan/`, `ptm/`, …); they were listed by name once and never opened; my files are named in `computations.json`. No sibling report of this round was found open to me.

**Provenance of citations.** Semaev 2004 (IACR ePrint 2004/031) is cited as `recalled` only: a pointer, not support. The two facts the derivation takes from it — the defining property of S_m and the resultant recursion — are stated in the card and were verified numerically here at m = 3, 4, 5 (§2.1), so no conclusion below rests on the recollection. TASK-20260930-40470a records retrieving the paper; this review does not rely on that reading. No public source was retrieved; no network was used.

## 1. Own derivation (written before the predecessor's report was opened)

Setting as the card states it: p > 3 prime; E: y² = f(x) = x³ + ax + b nonsingular over F_p, so f is squarefree; K an algebraic closure of F_p; S_m the m-th summation polynomial with the defining property S_m(x_1..x_m) = 0 iff there are P_i ∈ E(K) with x(P_i) = x_i and ΣP_i = O; F(T) = S_m(x_1..x_{m-1},T). Write L = K(x_1..x_{m-1}) with the x_i independent indeterminates, M = L(y_1..y_{m-1}) with y_i² = f(x_i), P_i = (x_i, y_i) ∈ E(M).

**D1 (roots).** By the defining property with Q_i = ±P_i, the roots of F in K̄(L) are the values r_ε = x(P_1 + Σ_{i≥2} ε_i P_i), ε ∈ {±1}^{m-2} (the overall sign is absorbed by x(−Q) = x(Q)); there are 2^{m-2} sign classes, matching deg_T S_m = 2^{m-2}. All r_ε lie in M, because the group law is rational over F_p.

**D2 (the Kummer group).** Gal(M/L) ≅ (Z/2)^{m-1}, generated by σ_i: y_i ↦ −y_i. Reason: by Kummer theory the degree is 2^{m-1} iff no product Π_{i∈S} f(x_i), S ≠ ∅, is a square in L. In the UFD K[x_1..x_{m-1}], f(x_i) = Π_j (x_i − e_j) with the three e_j distinct (f squarefree), and the linear factors x_i − e_j are pairwise non-associate irreducibles across all (i, j) because the x_i are distinct variables; so the product is squarefree, hence not a square in the fraction field. This is the only place nonsingularity is used, and it is used for every curve alike.

**D3 (action on sign classes).** σ = (s_1..s_{m-1}) sends P_i ↦ s_i P_i, hence r_ε ↦ x(s_1 P_1 + Σ s_i ε_i P_i) = x(P_1 + Σ (s_1 s_i) ε_i P_i) = r_{ε·δ(σ)}, δ(σ)_i = s_1 s_i. So Gal(M/L) acts on the 2^{m-2} sign classes by translations of the group {±1}^{m-2}; the kernel of this action on *labels* is the diagonal {(1..1), (−1..−1)}, and the image is (Z/2)^{m-1}/diag ≅ (Z/2)^{m-2} acting simply transitively.

**D4 (generic distinctness, the step that makes labels into roots).** r_ε = r_{ε'} with ε ≠ ε' iff P_1 + Σε_iP_i = ±(P_1 + Σε'_iP_i), i.e. iff Σ_{i∈D} 2ε_iP_i = O (D = {i : ε_i ≠ ε'_i} ≠ ∅) or 2P_1 + Σ_{i∉D} 2ε_iP_i = O. Each is a Z-linear relation Σ n_i P_i = O with some n_j ∈ {±2} ≠ 0. The map E^{m-1} → E, (Q_i) ↦ Σ n_i Q_i, is surjective (its restriction to the j-th factor is [n_j]), so its kernel is a proper closed subvariety of E^{m-1}; (P_1..P_{m-1}) is a generic point of E^{m-1} (transcendence degree m−1), so it lies on no proper closed subvariety. Hence the 2^{m-2} values r_ε are pairwise distinct in M and F is squarefree of full degree over L. **Consequently** the pointwise stabiliser of the root set is exactly diag, the splitting field N = L(r_ε) is the fixed field M^{diag} (Galois correspondence), and Gal(N/L) ≅ (Z/2)^{m-2} acts on the roots faithfully and regularly. This is CU-9 item 1 for every nonsingular curve: nothing about a, b, j, ordinarity or extra automorphisms enters (x(Q) = x(Q') ⇔ Q' = ±Q holds for every Weierstrass curve, whatever Aut(E) is).

**D5 (arithmetic = geometric).** Over L_0 = F_p(x_1..x_{m-1}) the same Kummer argument gives Gal(M_0/L_0) ≅ (Z/2)^{m-1}. A constant-field extension inside M_0 would be a quadratic subextension L_0(√c), c ∈ F_p non-square; every quadratic subextension of a Kummer (Z/2)^{m-1}-extension is L_0(√u) with u ≡ Π_{i∈S} f(x_i) modulo squares, which has odd valuation at x_i = e_j and so is never a constant times a square. Hence M_0 ∩ K = F_p, M_0 and K are linearly disjoint over F_p, N_0 K = N, and Gal(N_0/L_0) ≅ Gal(N/L): the arithmetic group equals the geometric one. (Empirical face in §2.4: the identity class occurs at F_p-points with density 1/4, which is impossible if the arithmetic group were a proper overgroup, since every F_p-Frobenius would then lie in a non-trivial coset.)

**D6 (the delta-rule as specialization).** Take x_1..x_{m-1} ∈ F_p with f(x_i) ≠ 0 and F squarefree of full degree. Put y_i = √f(x_i) ∈ F_{p²}; then y_i^p = χ(f(x_i)) y_i, so the p-Frobenius endomorphism φ of E (defined over F_p) satisfies φ(P_i) = δ_i P_i, δ_i = χ(f(x_i)). Since φ is a group endomorphism, φ(r_ε) = x(φ(P_1) + Σ ε_i φ(P_i)) = x(δ_1P_1 + Σ ε_iδ_iP_i) = r_{ε·δ'}, δ'_i = δ_1δ_i. Full degree and squarefreeness mean the r_ε are the 2^{m-2} distinct roots of F, so Frobenius acts on them as the translation by δ': all fixed iff δ' = (1..1) iff δ = ±(1..1); otherwise a fixed-point-free involution, cycle type 2^{2^{m-3}}. This is CU-9 item 3 at every m ≥ 3; the same argument shows the roots lie in F_{p²}, so no cycle longer than 2 can occur on any such fibre.

**D7 (where the hypotheses are used; the degenerate loci).** Root coincidences occur iff some P_i ∈ E[2] (f(x_i) = 0), or some P_i ± P_j ∈ E[2] including O (x_i = x_j, or x(P_i ± P_j) a root of f), and the degree drops by one iff some ±P_1 ± P_2 ± P_3 = O at m=4 (leading coefficient S_{m-1}(x_1..x_{m-1})²). These are exactly the plan's carve-outs A1-b/A3-a/A3-b. They are also the whole content of OBS-1's exceptions (§5) and the reason a finite-p density must be compared conditionally on nondegeneracy (§2.4).

**D8 (symmetric base).** Let L^S = K(e_1..e_{m-1}). Gal(L/L^S) = S_{m-1} (the generic polynomial extension), and M/L^S is Galois: it is the splitting field of Π_i (Z − x_i)(Z² − f(x_i)) ∈ L^S[Z]; the permutations π: (x_i, y_i) ↦ (x_{π i}, y_{π i}) extend D2's group, so Gal(M/L^S) ≅ Z/2 wr S_{m-1} of order 2^{m-1}(m−1)!. (s, π) sends r_ε to x(Σ_j ε_{π^{-1}j} s_j P_j), i.e. the natural action of the hyperoctahedral group on sign vectors modulo overall sign: on F_2^{m-1}/⟨(1..1)⟩ ≅ F_2^{m-2} it is the affine action v ↦ s + π(v). Kernel: s = ±(1..1) from v = 0, and then π(v) = ±v for all v forces π = id as soon as m−1 ≥ 3 (a vector with a single 1 cannot map to its complement); so the kernel is {±1} and the image is (Z/2)^{m-2} ⋊ S_{m-1}, of order 2^{m-2}(m−1)!, for every m ≥ 4 and every nonsingular curve, geometric and arithmetic alike (D5 applies verbatim). At m = 4 it is AGL(2,2) ≅ S_4 = Sym(4). **At m = 3 the kernel is larger** ((1, swap) acts trivially on the two classes), the image is S_2 of order 2 and the formula 2^{m-2}(m−1)! does not apply — consistent with H-MONO-93bc4d's recorded refutation of its symmetric-base extension at m=3. Primitivity: an affine group containing all translations is primitive iff its linear part S_{m-1} acts irreducibly on V = F_2^{m-1}/⟨1⟩; V is irreducible iff m−1 is odd (for m−1 even the image of the sum-zero submodule is a proper invariant subspace of codimension 1, giving exactly one block system of two blocks). Hence primitive at m = 4, 6 and imprimitive at m = 5, 7 with two blocks of size 2^{m-3} — confirmed by the permutation-group computation of §2.2.

**D9 (proves-too-much, by derivation).** PT-1: with the y_i in the base, D2's group is trivial and so is everything downstream; the rule then predicts complete splitting (all δ_i = +1). PT-2: at m=3 with x_2 = x([2]P_1), y([2]P_1) is an odd function of y_1 (since [2](−P) = −[2]P), so f(x_2) = f(x_1)·h(x_1)² and D2's independence fails: M = L(y_1), the only sign change acts as (s, s), δ' = 1, trivial group; roots x(P_1) and x([3]P_1) in K(x_1); at every x_1 ∈ F_p, χ(f(x_2)) = χ(f(x_1)) and the rule predicts complete splitting whatever χ(f(x_1)) is. PT-3: over L^S(√disc), Gal(L/·) = A_3 and D8's image shrinks to (Z/2)² ⋊ A_3 = A_4 of order 12: no odd permutation (no 2+1+1, no 4-cycle). All three stop where the plan's failure signature says they must.

## 2. Own constructions and computations (all code and raw output in `computations.json`)

### 2.1 S_3, S_4, S_5 and the defining property
- `rt_symbolic.py` (sympy 1.14.0): S_3 is **derived**, not recalled, from the chord law — the sum and product of x(P_1 ± P_2) reduced modulo y_i² = f(x_i) give S_3(x_1,x_2,T) = (x_1−x_2)²T² − 2[(x_1+x_2)(x_1x_2+a)+2b]T + (x_1x_2−a)² − 4b(x_1+x_2); it is symmetric in its three arguments and of degree 2 in each. S_4 = Res_X(S_3(x_1,x_2,X), S_3(x_3,x_4,X)) over Z[a,b]: 439 monomials in x_1..x_4 with coefficients in Z[a,b], degree 4 in each variable, invariant under every transposition, irreducible over Q(a,b) (a single factor of total degree 12), and lc_{x_4} S_4 = S_3(x_1,x_2,x_3)² exactly. Its T-coefficients were symmetrised in e_1,e_2,e_3 with zero remainder (used for the symmetric base). S_5(x_1..x_4,T) is the formal-degree (4,2) Sylvester resultant Res_X(S_4(x_1,x_2,x_3,X), S_3(x_4,T,X)), evaluated at 12 points and interpolated (degree ≤ 8 verified, two extra evaluation points re-checked per fibre).
- Defining property (`rt_numeric.py` stage A), on y² = x³+2x+3 / F_10007 and y² = x³+7 / F_10009, for each m ∈ {3,4,5}: 200/200 tuples of x-coordinates of points summing to O (both E(F_p) and quadratic-twist families) give S_m = 0; 200/200 uniformly random tuples agree with the group-law ground truth (S_m = 0 iff x_m is a sign-class sum); every planted-root tuple vanishes (105/105, 51/51, 21/21 and 88/88, 53/53, 30/30).

### 2.2 Sign-class permutation groups (curve-free; `rt_numeric.py` stage G, sympy `PermutationGroup`)
| m | degree 2^{m-2} | ordered-base image (translations) | symmetric-base image | 2^{m-2}(m−1)! | transitive | primitive | minimal block systems |
|---|---|---|---|---|---|---|---|
| 3 | 2 | 2, regular | **2** | (4, n/a) | yes | yes | — |
| 4 | 4 | 4, regular | 24 = Sym(4) | 24 | yes | yes | none |
| 5 | 8 | 8, regular | 192 | 192 | yes | **no** | one: two blocks of 4 |
| 6 | 16 | 16, regular | 1920 | 1920 | yes | **yes** | none |
| 7 | 32 | 32, regular | 23040 | 23040 | yes | **no** | one: two blocks of 16 |
The m=4 cycle-type census of the symmetric-base image is {1^4:1, 2+1+1:6, 2+2:3, 3+1:8, 4:6}, i.e. S_4.

### 2.3 Curves and primes used
j=0 at p ≡ 1 (mod 3): y² = x³+7 / F_10009 (#E = 10192). j=1728 at p ≡ 1 (mod 4): y² = x³+x / F_10009 (#E = 10016). Supersingular: y² = x³+1 / F_10007 (p ≡ 2 mod 3) and y² = x³+x / F_10007 (p ≡ 3 mod 4), both trace 0. Generic ordinary: y² = x³+2x+3 / F_10007. The EXP-MONO-0e6e8f census curves C1 (101,2,3), C2 (101,1,35), C3 (1009,5,7), C4 (1009,2,30). y² = x³+2x+3 / F_53 for an exhaustive ordered-base run. Seeds: master `random.Random(20261017)`, per-stage seeds recorded in `computations.json`.

### 2.4 Ordered base, m = 4 (`rt_numeric.py` stage B; `rt_exact_cond.py`; `rt_big1009.py`)
Instrument A factors my S_4 fibre over F_p (Yun + distinct-degree); instrument B builds the four sign-class roots in F_{p²} from the group law, checks F(r_ε) = 0 and checks that Frobenius permutes them exactly as the translation by δ'. "Nondegenerate" = squarefree of degree 4 (the plan's generic fibre); fibres with some f(x_i) = 0 are skipped and counted.

| curve | tuples | some f(x_i)=0 | degree-deficient | non-squarefree | nondegenerate | 1^4 | 2^2 | other types | delta-rule mismatches / instrument-B failures |
|---|---|---|---|---|---|---|---|---|---|
| j=0, p=10009 | 50,000 | 37 | 2 | 65 | 49,896 | 12,654 | 37,242 | 0 | 0 / 0 |
| j=1728, p=10009 | 50,000 | 48 | 3 | 64 | 49,885 | 12,441 | 37,444 | 0 | 0 / 0 |
| ss y²=x³+1, p=10007 | 50,000 | 14 | 6 | 31 | 49,949 | 12,304 | 37,645 | 0 | 0 / 0 |
| ss y²=x³+x, p=10007 | 20,000 | 5 | 4 | 9 | 19,982 | 4,951 | 15,031 | 0 | 0 / 0 |
| generic, p=10007 | 50,000 | 22 | 6 | 24 | 49,948 | 12,409 | 37,539 | 0 | 0 / 0 |
| C3, p=1009 | 20,000 | 59 | 21 | 111 | 19,809 | 4,797 | 15,012 | 0 | 0 / 0 |
| C4, p=1009 | 20,000 | 166 | 22 | 256 | 19,557 | 5,024 | 14,533 | 0 | 0 / 0 |
| generic, p=53, **exhaustive** | 148,877 | 23,877 | 2,400 | 27,848 | 95,328 | 19,488 | 75,840 | 0 | 0 / 0 |

Every ramified or degree-deficient fibre carries the census label 1^4 or 2+1+1 (never 4 or 3+1), as D7 predicts. Every tuple with all χ(f(x_i)) = +1 (the x-coordinates of F_p-points, PT-1's face) that was nondegenerate gave 1^4: 6,679 / 6,221 / 6,104 / 2,423 / 5,972 / 2,053 / 2,949 / 16,128 such fibres, no exception.

**Densities and the declared bound.** Chebotarev for the regular V_4 predicts identity density 1/4; for the order-2 competitor ⟨(12)(34)⟩, 1/2; C_4, D_4, A_4, S_4 and the non-regular Klein group each predict a positive density for a type never observed. The exact finite-p expectation over tuples with all f(x_i) ≠ 0 is (N_+³ + N_−³)/(N_+ + N_−)³ with N_± = #{x : χ(f(x)) = ±1} (so exactly 1/4 on a supersingular curve, where N_+ = N_−). Conditioning on nondegeneracy shifts it slightly downward, because D7's degenerate tuples over-represent equal signs; `rt_exact_cond.py` enumerates the degenerate locus exactly from the group law (no S_4) and gives the exact conditional expectation:

| curve | all-f≠0 prediction | exact conditional (nondegenerate) | observed | n | z |
|---|---|---|---|---|---|
| generic p=53 (exhaustive) | 0.2800 | 95,328 nondegenerate / 19,488 identity = 0.204431 | 0.204431 (19,488 / 95,328) | exact | identical counts |
| C3 p=1009 | 0.251429 | 0.249196 (1,017,094,248 / 253,455,864) | 0.242163 (20k sample); 0.251807 (200k sample, 197,957 nondegenerate); pooled 0.250932 | 217,766 | −2.29; +2.69; pooled +1.87 |
| C4 p=1009 | 0.252849 | 0.249123 (1,005,008,160 / 250,370,784) | 0.256890 (20k sample); 0.248210 (200k sample, 195,669 nondegenerate); pooled 0.249000 | 215,226 | +2.51; −0.93; pooled −0.13 |
| j=0 p=10009 | 0.250248 | ≈ 0.2499 (bound: degenerate fraction 0.13%) | 0.253608 | 49,896 | +1.7 to +1.9 |
| j=1728 p=10009 | 0.250000 | ≈ 0.2497 | 0.249394 | 49,885 | −0.1 to −0.3 |
| ss p=10007 (x³+1) | 0.250000 | ≈ 0.2496 | 0.246331 | 49,949 | −1.7 to −1.9 |
| ss p=10007 (x³+x) | 0.250000 | ≈ 0.2497 | 0.247773 | 19,982 | −0.6 to −0.7 |
| generic p=10007 | 0.250197 | ≈ 0.2499 | 0.248438 | 49,948 | −0.6 to −0.9 |

Against the order-2 competitor (density 1/2) every curve is 68 to 113 standard errors away; against V_4 the per-curve chi-squares (df 1) are 0.1–6.5. The exact enumeration was validated three ways: at p=53 it reproduces the exhaustive S_4-based classification **exactly** (95,328 / 19,488); on the predecessor's curve y² = x³−7x+6 / F_101 it reproduces TASK-20260930-40470a's exhaustive object-1 counts **exactly** (824,256 generic fibres, 176,544 of type 1^4) by a method that never touches S_4; and at p=59 on y² = x³+x+2 (whose f has exactly one rational root, the factor type of C3) it again reproduces the exhaustive S_4-based classification **exactly** (172,464 nondegenerate / 36,384 identity; `rt_validate_exact.py`). On C3 and C4 the two instruments were cross-checked tuple by tuple on 20,000 fresh tuples each (19,939 and 19,821 agree on the degeneracy flag, 0 disagree), and a 2,000,000-tuple group-law-only estimate on C3 gave 0.249200 (1,980,141 nondegenerate), z = +0.01 against the exact 0.249196. The single-sample excursions (C3: −2.29 then +2.69, pooled +1.87; C4: +2.51 then −0.93, pooled −0.13) are therefore ordinary sampling spread of the S_4-based samples, not a bias of either instrument; I report them rather than round them away. **Declared bound:** for p ≤ 1009 the exact conditional expectation with binomial error; for p ≈ 10⁴ the all-f≠0 exact value minus at most the degenerate fraction (≤ 0.2%), with binomial error. No observation lies outside it beyond ordinary sampling spread, and no competitor group is consistent with the data.

### 2.5 Symmetric base, m = 4 (`rt_numeric.py` stage C)
(e_1,e_2,e_3) uniform in F_p³ (seeded), the census's own exclusion Res(g,f) = 0 applied, my symmetrised S_4 fibre factored over F_p, g's factorisation type recorded; "nondegenerate" = F squarefree of degree 4 and g squarefree.

| curve | drawn | excluded / g non-sqf / deg-def / non-sqf F | nondegenerate | 1^4 | 2^2 | 2+1+1 | 4 | 3+1 | χ² vs S_4 (df 4) | S_4→S_3 structure violations |
|---|---|---|---|---|---|---|---|---|---|---|
| j=0 p=10009 | 20,000 | 4 / 2 / 1 / 11 | 19,984 | 798 | 2,489 | 4,972 | 5,044 | 6,681 | 2.11 | 0 |
| j=1728 p=10009 | 20,000 | 2 / 3 / 0 / 9 | 19,989 | 845 | 2,446 | 5,039 | 5,089 | 6,570 | 4.62 | 0 |
| ss p=10007 | 20,000 | 1 / 6 / 4 / 7 | 19,988 | 823 | 2,509 | 5,003 | 4,989 | 6,664 | 0.18 | 0 |
| generic p=10007 | 20,000 | 1 / 1 / 0 / 5 | 19,994 | 863 | 2,500 | 4,946 | 4,995 | 6,690 | 1.73 | 0 |
| C3 p=1009 | 20,000 | 19 / 19 / 20 / 31 | 19,930 | 788 | 2,481 | 4,951 | 5,008 | 6,702 | 3.06 | 0 |
| C4 p=1009 | 20,000 | 46 / 10 / 23 / 78 | 19,853 | 848 | 2,426 | 4,928 | 5,028 | 6,623 | 2.87 | 0 |

S_4 densities are 0.0417 / 0.125 / 0.25 / 0.25 / 0.3333. On every curve each proper transitive subgroup (A_4, D_4, C_4, V_4) and the point stabiliser S_3 has thousands of observations in a class it cannot realise. The structure check — on a nondegenerate fibre the quartic's class must lie in the block named by g's type (split → {1^4, 2^2}; (1)(2) → {2+1+1, 4}; irreducible → {3+1}) — has zero violations on 119,738 fibres. Every g-split "2+1+1" instance in these samples (4, 2, 3, 0, 12, 20) is non-squarefree.

### 2.6 OBS-1 regeneration (`rt_numeric.py` stage D) — see §5.
### 2.7 m = 5 (`rt_numeric.py` stage E), PT-2 (stage F), PT-3 (stage H) — see §5 and §6.

## 3. RA-1 — ORDERED-BASE MONODROMY — verdict: **CONCUR (holds)**

**Method.** D1–D5 and D7 of §1, then the attack plan: the m=3 baseline slice; Frobenius cycle-type sampling with my own S_4 on the three required curve types plus two more and the census curves; densities against V_4 and its competitors with the exact finite-p count; the candidate break points (extra automorphisms; constant-field extension); then the comparison with the predecessor.

**What was built, computed and read.** §2.1–2.4; `rt_exact_cond.py`; `rt_big1009.py`; `rt_validate_exact.py`. Read for comparison: the TASK-20260930-40470a report (J4 derivation, proves-too-much object 1), its `ptm.py` and `ptm_out.json`, H-MONO-93bc4d, KN-FIND-c41ea9.

**Where distinctness and faithfulness are used, and whether they are proved.** Distinctness is D4 (no Z-linear relation at the generic point of E^{m-1}); it is a proof, not an appeal to a witness, and it is uniform in the curve. Faithfulness is the Galois correspondence once distinctness holds (N = M^{diag}). The predecessor's J1 derivation makes the same two steps ("[2] ≠ 0" for distinctness; the product formula for the rest) and its J4 states the ordered-base group from them; I find no gap. H-MONO-93bc4d's earlier reviewers closed the same |S| ≥ 2 step by a dominance and a transcendence-degree argument; D4 is the transcendence-degree form.

**Baseline slice m = 3.** D3–D4 give S_2 on the two roots x(P_1 ± P_2), KN-FIND-c41ea9's statement; the m=3 group computation gives order 2; PT-2's rows show S_3(x_1,x_2,T) splitting iff χ(f(x_1)) = χ(f(x_2)) (D6 at m=3).

**Observation collision (plan).** The support {1^4, 2^2} is shared by regular V_4 and by ⟨(12)(34)⟩; the derivation separates them (the translation group is all of (Z/2)^{m-2}) and so do the densities: the identity frequency is 1/4, not 1/2, on every curve, 68–113 standard errors from the competitor (§2.4).

**Candidate break points.** (a) Extra automorphisms: j=0 (y² = x³+7) and j=1728 (y² = x³+x) at p ≡ 1 mod 3 / 1 mod 4 behave exactly like the generic curve (zero mismatches; identity density 0.2536 and 0.2494). The derivation never uses Aut(E) ⊆ {±1}; only x(Q) = x(Q') ⇔ Q' = ±Q, true for all Weierstrass curves. (b) Supersingular: both supersingular curves give zero mismatches and identity density 0.2463 / 0.2478 against an exact 0.25. (c) Constant-field extension: excluded by D5 and by the observed identity class (an arithmetic overgroup would put every F_p-Frobenius in a non-identity coset). (d) p > 3: used only through the short Weierstrass form and char ≠ 2 for the quadratic structure; A1-c carves out p ≤ 3 anyway.

**Comparison with the predecessor.** Same group on both counts, same mechanism, same delta-rule, same group orders and primitivity (its `J4_group_structure` equals my §2.2 table at m = 3..7, including m=3 symmetric order 2). Its object-1 exhaustive counts on y² = x³−7x+6 / F_101 (824,256 generic fibres; 176,544 of type 1^4) are reproduced exactly by my exact enumeration from the group law alone (§2.4). Its corroboration statement ("923,788 generic fibres, no transposition, 3-cycle or 4-cycle") is a support statement; its own p=1009 and p=1999 samples (12,501/49,806 = 0.2510; 12,316/49,726 = 0.2477) already sit at the V_4 density 1/4, and my sampling adds the densities on j=0, j=1728 and supersingular curves, which it did not test. Difference of coverage, not of result.

**Breaking-artifact assessment.** No nonsingular curve with a different generic group (derivation uniform in the curve; three special curve types tested). No cycle type outside the claimed group on a squarefree full-degree fibre with every f(x_i) ≠ 0 (0 of 334,354 such fibres across §2.4, plus 95,328 exhaustive at p=53). Frequencies: consistent with V_4 within the declared bound on every curve; inconsistent with every competitor. No gap in the derivation found.

**Corrections and carve-outs (RC-3).** None to the claim. Two observations, both inside carve-outs: the degenerate loci (D7) are exactly A1-b; the finite-p density comparison must be conditioned on nondegeneracy (a methodological point about the test, not about the group). Wording: "regular" = "simply transitive" (A1-d).

**Reading declaration (RA-1).** The card; `rt_symbolic.py`, `rt_numeric.py` (stages A, B, G), `rt_exact_cond.py`, `rt_big1009.py`, `rt_validate_exact.py` and their outputs; after the derivation: TASK-20260930-40470a review_report.md (J1, proves-too-much object 1, J4 derivation), its computations.json keys `scripts.ptm.py`, `outputs.ptm_out.json`, `notes`, `retrieved_sources`; H-MONO-93bc4d; KN-FIND-c41ea9; DEC-20260904-dd58c3 (limitations).

## 4. RA-2 — SYMMETRIC-BASE MONODROMY — verdict: **CONCUR (holds)**

**Method.** D8 of §1 (the independence step, Gal(K(x)/K(e)) = S_{m-1}, the affine action on F_2^{m-1}/⟨1⟩, its kernel and order, AGL(2,2) = S_4), the curve-free permutation-group computation at m = 3..7 with primitivity and block systems (§2.2), the baseline slice against EXP-MONO-0e6e8f M1, the reconciliation with the m ≥ 5 lemma that DEC-20260904-dd58c3's limitations attribute to H-MONO-93bc4d, and the empirical test at m=4 on six curves (§2.5).

**The independence step over the symmetric base (the plan's first candidate break).** The f(x_i) are not elements of L^S, so "independence over the symmetric base field" is the independence of D2 over L = L^S(x_1..x_{m-1}), which is what the tower M ⊃ L ⊃ L^S needs; D2 proves it from unique factorisation and nonsingularity, uniformly in the curve. The S_{m-1} step is the standard fact that K(x_1..x_n)/K(e_1..e_n) has group S_n. The two combine into the full wreath product because the permutations extend to M compatibly with the y_i.

**Kernel and order.** Kernel {±1} for m ≥ 4 (D8); hence order 2^{m-2}(m−1)!: 24, 192, 1920, 23040 at m = 4..7 — the computation agrees. Proper subgroup of Sym(2^{m-2}) for m ≥ 5 (192 < 40320). At m = 4 the image on 4 points has order 24, so it is Sym(4) = AGL(2,2).

**Baseline slice: EXP-MONO-0e6e8f M1.** My own symmetric-base census populates all five classes on all six curves, including the census's C3 and C4, with S_4 densities (χ² 0.18–4.6 on df 4) and with every proper transitive subgroup and the point stabiliser falsified by presence; the S_4 → S_3 compatibility with g's type has zero violations. So the m=4 result reproduces M1 on the producer's curves and extends it to j=0, j=1728 and a supersingular curve, where the group is the same.

**Reconciliation with the m ≥ 5 lemma.** H-MONO-93bc4d states the same lemma ("V semidirect S_{m-1}, order 2^{m-2}(m-1)!, … a proper imprimitive subgroup of Sym(2^{m-2}) at m>=5"), and DEC-20260904-dd58c3's limitation repeats "PROPER, imprimitive". Correct on order and properness; **inaccurate on primitivity at m = 6**, where the group of order 1920 on 16 points is primitive (D8: m−1 = 5 is odd, so S_5 acts irreducibly on F_2^5/⟨1⟩). The predecessor's S-1 already records this precision note; its own table ("imprimitive at m = 5 and 7; primitive but proper at m=6") is accurate, and the plan's paraphrase "primitivity varying for m = 5..7" is descriptive. The complete statement is: imprimitive with exactly one block system (two blocks of size 2^{m-3}) when m−1 is even, primitive when m−1 is odd.

**m = 3.** The symmetric-base image at m=3 is S_2 of order 2, not 2^{m-2}(m−1)! = 4 (D8; §2.2). CU-9 item 2 and the RA-2 joint state the formula for m ≥ 4 (S_4 at m=4; orders at m=5,6,7) and the breaking artifact names m in 4..7, so this is outside the claim as worded; it is recorded because the general-m formula must carry "m ≥ 4", exactly as H-MONO-93bc4d's status note already records for its own (D3).

**Curve dependence.** None: the derivation uses only f squarefree and the generic position of the x_i; the six-curve test (including j=0, j=1728, supersingular) shows the same group and the same densities.

**Breaking-artifact assessment.** No curve and no m in 4..7 with a different order or isomorphism type (derivation + computation); no cycle type or frequency inconsistent with S_4 at m=4 on any curve; no gap found.

**Corrections and carve-outs (RC-3).** (i) Primitivity: "imprimitive for m ≥ 5" (H-MONO-93bc4d statement; DEC-20260904-dd58c3 limitation) is corrected to "imprimitive iff m−1 is even; at m=6 primitive" — **within carve-out A2-d**, a scope correction, not a break. (ii) Block structure made explicit (one block system, two blocks) — A2-d. (iii) The m=3 value (order 2) — outside the joint's range; a scope note on the general-m wording, not a break. No correction meets the breaking artifact.

**Reading declaration (RA-2).** The card; `rt_symbolic.py`, `rt_numeric.py` (stages C, G) and outputs; TASK-20260930-40470a review_report.md (J4 derivation, S-1) and `ptm_out.json` `J4_group_structure`; H-MONO-93bc4d; DEC-20260904-dd58c3; H-MONO-ebd400; EV-MONO-e9dc3b; EXP-MONO-0e6e8f specification and execution report; EXP-MONO-815525 specification, execution report and red-team report (null-object section).

## 5. RA-3 — THE DELTA-RULE — verdict: **CONCUR (holds)**

**Method.** D6 of §1; the OBS-1 reconciliation from the census's own records and implementation plus an exhaustive regeneration; the m=5 test on two curves.

**Derivation.** D6: on a squarefree full-degree fibre with every f(x_i) ≠ 0, Frobenius is the translation by δ' on the 2^{m-2} distinct roots, so the cycle type is 1^{2^{m-2}} iff δ = ±(1..1) and otherwise a fixed-point-free involution, at every m ≥ 3. The three carve-outs A3-a/b/c are precisely D7's loci; A3-c (roots in P¹) matches the census's projective reading.

**OBS-1 reconciliation.** The census labels a fibre by the factor degrees of Q_e with Yun multiplicities (`RC.factor_pattern`), padded with the (4 − deg) roots at infinity, so (T − r)²·(irreducible quadratic) is labelled "2+1+1" and (T−r)²(T−r')² is labelled "1^4" (`run_uncond_census.py` lines 136–171; `run_census.py` lines 131–176). C1 and C2 are exhaustive over F_101³, so the g-split block is the set of monic cubics splitting with multiplicity, i.e. the multisets {x_1 ≤ x_2 ≤ x_3} ⊂ F_101, C(103,3) = 176,851 per curve. I regenerated all of them from the group law and my S_4 (stage D):

| curve | multisets | excluded (some f(x_i)=0) | label 1^4 | label 2+1+1 | label 2+2 | 2+1+1 non-squarefree / squarefree deg 4 / squarefree deg 3 | mechanisms of the non-squarefree 2+1+1 |
|---|---|---|---|---|---|---|---|
| C1 (101,2,3) | 176,851 | 5,151 | 44,759 | 7,323 | 119,618 | 7,323 / 0 / 0 | x_1=x_2: 2,441; x_2=x_3: 2,441; P_i±P_j a nonzero 2-torsion point: 2,441 (364+421+412+418+411+415) |
| C2 (101,1,35) | 176,851 | 0 | 50,161 | 4,920 | 121,770 | 4,920 / 0 / 0 | x_1=x_2: 2,460; x_2=x_3: 2,460; none of the 2-torsion kind (#E = 121 is odd, E[2](F_{p²}) = O) |

The three label counts equal the census's own joint cells "1+1+1 | 1^4", "1+1+1 | 2+1+1", "1+1+1 | 2+2" for C1 (44,759 / 7,323 / 119,618) and C2 (50,161 / 4,920 / 121,770) **exactly** (`raw-result.json` `stage_1.per_curve[*].joint_g_type_by_class_counts`). Hence all 12,243 g-split 2+1+1 instances on the two exhaustive curves (of OBS-1's 12,429) are non-squarefree, by D7's mechanisms, and none is a squarefree full-degree fibre. For C3 and C4 (random mode, 65 and 121 instances) my own uniform samples at p=1009 found 12 and 20 g-split 2+1+1 instances, all non-squarefree, and the EXP-MONO-0e6e8f validator's committed report states that it verified every OBS-1 exception, including "the 12429 pooled g-split instances landing in 2+1+1", to be non-squarefree (validation-report.yaml lines 345–349). The 14,963 "ramified 2+1+1" pooled count is consistent: on C1 it exceeds the g-split count (9,764 > 7,323) because (1)(2)-type cubics also produce non-squarefree 2+1+1 fibres. **No instance meets RA-3's or RA-1's breaking artifact; every one falls inside A3-a/A3-b.**

**m = 5.** 3,000 random tuples on each of y² = x³+2x+3 / F_10007 and y² = x³+7 / F_10009: 2,988 and 2,984 nondegenerate (degree 8, squarefree) fibres, predicted 1^8 iff all four χ(f(x_i)) agree and 2^4 otherwise — 2,988 / 2,988 and 2,984 / 2,984 agreements; observed types only {1^8, 2^4} (390 / 2,598 and 384 / 2,600), identity frequency 0.1305 and 0.1287 against the Chebotarev 1/8 of (Z/2)³ regular (z = +0.9, +0.6); instrument B (eight group-law roots, F(r) = 0, Frobenius = translation) failed on no subsampled tuple.

**m = 3 and m = 4.** m=3: PT-2's 40 rows and the m=3 identity of KN-FIND-c41ea9. m=4: zero mismatches on every nondegenerate fibre of §2.4 (334,354 sampled + 95,328 exhaustive + 395,914 in the larger p=1009 samples).

**Corrections and carve-outs (RC-3).** None. Reading declaration (RA-3): the card; `rt_numeric.py` stages B, D, E, F and outputs; `run_uncond_census.py` (classification and `handle`), `run_census.py` (helpers), `raw-result.json` by key; EXP-MONO-0e6e8f execution report (OBS-1, OBS-3), validator report lines 325–349; TASK-20260930-40470a report (object 1).

## 6. Proves-too-much control (PT-1, PT-2, PT-3)

The argument under test is D1–D8. On each object a correct argument must yield the smaller group, and it does; the step that changes is named.

- **PT-1 (generic points of E^{m-1}; group known trivial).** The step that changes is D2: with y_1..y_{m-1} in the base field, L(y) = L and the Kummer group is trivial; D3–D4 then act through the trivial group, every r_ε is rational over the base, and the group is trivial. The argument does not give (Z/2)^{m-2} here because D2's independence is a statement about the y_i being adjoined. Finite-p face: on tuples whose x_i are x-coordinates of F_p-points (all δ_i = +1) the rule predicts 1^{2^{m-2}}; §2.4 observed 1^4 on every such nondegenerate fibre (46,529 of them across eight runs) and never anything else. Stops at the right step.
- **PT-2 (the [2]-graph at m=3; group known trivial).** The step that changes is D2's independence: y([2]P_1) is an odd rational function of y_1, so f(x([2]P_1)) = f(x_1)·h(x_1)² and f(x_1)f(x_2) is a square in K(x_1); M = K(x_1, y_1), the one sign change acts as (s,s), δ' = 1, the roots x([3]P_1) and x(P_1) lie in K(x_1), group trivial. A rule that reads only the characters predicts complete splitting at every x_1 ∈ F_p because χ(f(x_2)) = χ(f(x_1)). Numerics (stage F, y² = x³+2x+3 / F_10007): 40 of 40 random x_1 with f(x_1) ≠ 0 and [2]P_1 ≠ O gave χ(f(x([2]P_1))) = χ(f(x_1)) and S_3(x_1, x([2]P_1), T) splitting completely over F_p with roots exactly {x_1, x([3]P_1)}, including all 24 cases with χ(f(x_1)) = −1. Stops at the right step.
- **PT-3 (square-discriminant cover at m=4; group known A_4).** The step that changes is D8's "Gal(K(x)/K(e)) = S_3", which becomes A_3 over K(e)(√disc); the image is (Z/2)² ⋊ A_3 = A_4 of order 12, containing no odd permutation. Numerics (stage H, y² = x³+2x+3 / F_10007): among 4,000 cubics with χ(disc g) = +1 and Res(g,f) ≠ 0, 3,998 nondegenerate fibres gave 1^4: 354, 2^2: 1,004, 3+1: 2,640 and **no 2+1+1 and no 4-cycle**; frequencies 0.0885 / 0.2511 / 0.6603 against A_4's 1/12 / 3/12 / 8/12, χ² = 1.56 on df 2. The argument gives A_4, not S_4. Stops at the right step.

**Failure signature:** not triggered on any object. The argument does not prove too much.

## 7. RA-4 — J4 ADEQUACY — verdict: **CONCUR (holds)**

**Method.** The readings table for criterion (a) with committed anchors; the ground table for G-i, G-ii, G-iii assessed on the merits (G-i only through RA-1, per A4-d); the hardest attack I could mount on G-ii and G-iii; then Q-C and Q-OI. Texts compared: criterion (a) "Committed decision that … (a) the census agrees with full symmetric/wreath monodromy within stated error"; the objective "Decide KN-OPEN-009 at toy scope via a frozen Chebotarev/monodromy census protocol: full monodromy (barrier for relation-rate attacks) versus an exceptional locus with deviant rates"; KN-OPEN-009's statement ("For the m-th Semaev summation cover over the parameter space of (x_1,...,x_{m-1}), is the geometric monodromy (Galois) group the full symmetric (resp. wreath) group for all ordinary E/F_p outside an explicit exceptional locus … or does an exceptional family … have imprimitive/smaller monodromy"); RQ-MONO-001; EXP-MONO-0e6e8f's specification (M1–M3, preregistered_prediction); H-MONO-ebd400; EV-MONO-e9dc3b; CORR-20260904-33fbf3; DEC-20260904-dd58c3; DEC-20260802-a51c82 N-2; DEC-20261017-435b01 (CS-QA, CS-K1d, closure_revisit_condition). The census was not re-run; its numbers are quoted.

### 7.1 Readings of criterion (a)

| reading | anchor in committed text | does the route-(a) object satisfy it? |
|---|---|---|
| **R-o** — the census must address KN-OPEN-009's cover over the **ordered** base (x_1..x_{m-1}) | KN-OPEN-009 statement ("over the parameter space of (x_1,...,x_{m-1})"); objective ("Decide KN-OPEN-009") | **No.** The object censuses the symmetric base (EXP-MONO-0e6e8f specification: "symmetric-base Semaev cover", base points (e_1,e_2,e_3)); on the ordered base the m=4 generic group is V_4 = (Z/2)² regular (RA-1), of order 4, imprimitive — neither Sym(4) nor the order-24 image of the wreath product — and it is the same for every nonsingular curve, so there is no exceptional locus either: "neither branch of the dichotomy". |
| **R-s** — the symmetric base of EXP-MONO-0e6e8f and H-MONO-ebd400 | EXP-MONO-0e6e8f specification title and inputs; H-MONO-ebd400 statement ("monodromy exactly AGL(2,2)=S_4") | The group clause, yes: S_4 (= Sym(4) = full image of Z/2 wr S_3, so "symmetric" and "wreath" coincide at m=4), established by M1 and forced for every curve by RA-2. The "within stated error" clause, no — see R-d. |
| **R-d** — distributional agreement within a pre-stated error | criterion (a) "within stated error"; specification M3 / preregistered_prediction ("Chi-square consistent … at conventional significance"); H-MONO-ebd400 (I) ("matches … within toy-scale statistical tolerance") and its validation_plan ("chi-square goodness-of-fit test, pre-registered before any draw") | **No.** M3 = 2447.84 pooled (df 4); 1175.81 (C1), 1765.88 (C2), 12.13 (C4, above 9.49), 4.38 (C3) — three curves and the pool fail; CORR-20260904-33fbf3 withdraws M3 as a wrong-null design defect, "NOT carried forward as evidence of any kind". No other pre-stated error exists in the committed texts. |
| **R-x** — exact group identification (M1) | specification M1; H-MONO-ebd400 falsification_condition; DEC-20260904-dd58c3 | **Yes**, on the symmetric base at m=4: observed 4-cycles and 3-cycles force S_4; "within stated error" is vacuous for a zero-tolerance existence check. |
| R-max (listed; **does not compose**, no anchor) — "full" read as "the largest group the cover's structure permits on the given base" | none of the five anchor texts defines "full" relative to the base | Would be satisfied on both bases uniformly in the curve (the ordered-base group is the full image of the sign-change group; the symmetric-base group is the full image of Z/2 wr S_{m-1}). Recorded for the composer; not a composing reading under A4-b. |
| R-post (listed; **does not compose**) — "stated error" read as an error stated after the data were seen (the exact finite-p null of CORR-20260904-33fbf3: 0.23 (C2), 2.90 (C3), 0.73 (C4), 171.67 (C1, residual = the identified 2,459-instance 4-torsion-leakage stratum)) | criterion (a) does not say "pre-registered"; CORR-20260904-33fbf3 calls the recomputed statistics "genuinely diagnostic" | This is the strongest attack on G-ii I found. It fails under the program's own pre-registration discipline: the exact null was derived after the data (CORR-20260904-33fbf3 finding_1), A01 K4's recorded precedent says exactly that "the exact null derived after the data were seen was not allowed to rescue it", agents/coordinator.md forbids changing success criteria after observing outcomes without an amendment, and even on its own terms C1 fails at 171.67 unless a further post-hoc stratum term is added. Listed, not composing. |

### 7.2 Ground table

| ground | status on the merits | committed text it rests on | assessment |
|---|---|---|---|
| **G-i** "on KN-OPEN-009's ordered base the m=4 monodromy is V_4 for every nonsingular curve" | **sustained** (A4-d: RA-1 holds in my own work) | KN-OPEN-009 statement (ordered parameter space); objective; CU-9 item 1, now re-derived here (§1 D1–D5) and tested on j=0, j=1728, supersingular, generic and census curves | True as stated, and strengthened: the group is V_4 regular, imprimitive, arithmetic = geometric, for every nonsingular curve; a census of that cover cannot "agree with full symmetric/wreath monodromy", and the route-(a) object never censused it. The hardest counter is R-max; it has no committed anchor. |
| **G-ii** "the only pre-registered 'within stated error' test (M3) failed and was withdrawn" | **sustained** | specification M3 and preregistered_prediction; H-MONO-ebd400 (I) and validation_plan; execution report stage_2 M3 values; CORR-20260904-33fbf3 finding_1 and finding_1_disposition | Verified by quote. The pass on C3 alone (4.38) is one curve of four, not "the census". The strongest attack (R-post) is listed above and does not compose. My own six-curve symmetric-base sampling does match S_4 within a declared binomial error (§2.5), but it is a review computation on a different sample, not the committed census meeting a pre-stated error; it cannot retroactively supply one. |
| **G-iii** "adoption would contradict DEC-20260802-a51c82 N-2 and DEC-20260904-dd58c3's scope_statement and completion_criteria_met []" | **sustained** | N-2: "no completion criterion is met, since criterion (a) required a census deciding full-versus-exceptional and the census was shown non-discriminating, and the derivation that did answer m=3 is not the committed decision the criterion asks for at m >= 4"; dd58c3: "Scoped to full S_4 monodromy at m=4 over the symmetric base, at toy scale, on 4 curves at 2 primes … Does not close KN-OPEN-009 … Does not extend to m != 4", `completion_criteria_met: []`, `closure_authorized: false`; DEC-20261017-435b01 CS-K1d and CS-QA carry both forward | Both statements say what the DISSENT says, and nothing committed since supersedes them. On distinguishability: N-2's reason is that the m=3 outcome was forced by derivation and the census therefore decided nothing the derivation had not; RA-2 shows the m=4 symmetric-base outcome is likewise forced for every curve, so the parity holds in kind. Candidate reasons a composer could cite to supersede N-2 with a stated reason exist — (d1) at m=3 the imprimitivity content is degenerate (degree 2) while at m=4 it is not; (d2) the m=4 design was pre-registered two-sided with falsification branches verified non-empty before dispatch, so it could have refuted S_4 ex ante — but neither is committed, and under N-2's own logic a derivation-decided answer is still not "the census agrees … within stated error". dd58c3 is the producer's own scope; adopting (a) on its object would need to supersede its own `completion_criteria_met: []`. |

**Verdict: CONCUR (holds).** The J4 DISSENT's claim — the committed route-(a) object does not satisfy criterion (a), read under the objective and KN-OPEN-009 — holds on each of G-i, G-ii and G-iii. RA-4's breaking artifact requires an anchored reading the object satisfies **together with** answers on the merits to each ground; R-x/R-s supply the first, nothing committed supplies the second for G-ii or G-iii, and G-i stands on RA-1. The verdict concerns the J4 claim; whether the goal closes, and whether a Coordinator supersedes N-2 on (d1)/(d2), are the composer's (A4-c).

**Corrections and carve-outs (RC-3).** No correction to the DISSENT's grounds. One precision on G-i's wording "corroborated on 923,788 generic fibres": that corroboration is by support; the densities, which alone separate V_4 from the order-2 group, are supplied by the predecessor's own p=1009/1999 figures and by §2.4 — a strengthening inside A4-a's spirit (not a ground).

### 7.3 Q-C — if RA-1 and RA-2 hold, is KN-OPEN-8a7432 Q2's monodromy question answered by derivation, uniformly in the curve, on both bases, and how does it read against (a), (b) and the dichotomy?

Reading, with anchors; the composer decides.
- **Answered by derivation, uniformly in the curve, on both bases, at every m ≥ 3** (symmetric-base order formula for m ≥ 4): for every prime p > 3 and every nonsingular E/F_p — ordinary or supersingular, any j including 0 and 1728 — the generic geometric monodromy equals the arithmetic monodromy and is (Z/2)^{m-2} regular over the ordered base and (Z/2)^{m-2} ⋊ S_{m-1} over the symmetric base (S_2 at m=3). There is **no exceptional locus** on either base at any m (anchors: §1 D1–D8; CU-9; the proves-too-much control passing; the three special curve types sampled). Claim tier of the derivation: derivation (docs/claims-and-verification.md), corroborated at toy primes only.
- **Against the objective's dichotomy** "full monodromy versus an exceptional locus with deviant rates": the exceptional-locus branch is false on both bases. The "full" branch holds only in the sense "the full image of the structural group" (R-max, unanchored): literally, Sym(2^{m-2}) is attained only at m=4 on the symmetric base; at m ≥ 5 the symmetric-base group is a proper subgroup (imprimitive for odd m, primitive for even m), and on KN-OPEN-009's ordered base the group is the small regular (Z/2)^{m-2}, imprimitive for every m ≥ 4 — a block system that exists **for every curve**, not for an exceptional family. The dichotomy as posed is therefore not exhaustive; the derived answer is its third case: uniformly smaller than full symmetric, uniform in the curve, no curve-specific deviation (nothing is said here about rates; CS-D2 binds).
- **Against criterion (a):** the group clause is met at m=4 on the symmetric base (R-x/R-s) and not on the ordered base (R-o); the "within stated error" clause is unmet as the committed texts stand (R-d). **Against criterion (b):** cannot be met — no exceptional locus exists, and the automorphism-artifact control the criterion asks for is answered by derivation (j=0 and j=1728 behave like every other curve).
- The cleanest committed home for the derived answer is RA-C5 (a derivation-tier finding superseding KN-OPEN-8a7432 Q2's text, with "every m" resting on the derivation and the measured corroboration listed), not an adoption of criterion (a) on the census.

### 7.4 Q-OI — do DEC-20260802-a51c82 N-3 and DEC-20260810-2f86db N-3 bear on the admissibility of EXP-MONO-0e6e8f as route-(a) evidence?

Facts found (sources in the attestation; four passages outside the declared inputs were read as single grep-located ranges and are declared as read-scope excess):
1. N-3 (both decisions): "No new census of any statistic may be dispatched before these [five OI-1 repairs] are carried"; the goal head on 2026-09-04 records the repairs as "still outstanding"; DEC-20260904-8c2580 (2026-09-04) records them as "unaffected by this decision and remain open" as blockers "on dispatching a new harness batch".
2. On the same date EXP-MONO-815525 and EXP-MONO-0e6e8f — both censuses of a statistic, on a new harness (`run_census.py` / `run_uncond_census.py`) — were approved, dispatched and run. Neither specification, execution report, implementation note, run manifest nor review mentions OI-1, CORR-20260802-1d8384 or any of the five repairs (grep: zero hits); the approving decision DEC-20260904-858cdc and the two task cards contain no occurrence of "1d8384", "OI-1" or "repair" (counts only; contents not read). DEC-20260904-4eb323 records that a reviewer had already flagged the OI-1 requirements' absence from EXP-MONO-917e3a's frozen spec and that the decision "does not audit whether … [this] affects any OTHER contract in this sub-lane". DEC-20260930-3a0b7b R-4 and DEC-20260904-0f525b R-4 engage the gate only for review-only batches ("a review runs neither").
3. **Were the repairs carried?** No record says so; the harness files do not carry them. **Were they inapplicable to the EXP-MONO-815525 harness?** Four of the five are inapplicable by construction: the reverification-disposition rule (there is no reverification or exception machinery; the outcome logic is M1 existence checks plus M3), the 2-torsion generator guard (there is no factor base or generator; the analogous 2-torsion concern is handled by the Res(g,f) = 0 exclusion and the disclosure of ramified fibres, and later analysed exactly by the review round), the relative tolerances on the two window controls and FAMILY_RATE_ALERT (there are no window controls or exception-family screens). The fifth, a uniform (A,B) draw, applies in spirit: the census's four curves are hand-picked small-height pairs, not a uniform panel, so nothing about "generic curves" can be inferred from the panel — which is exactly what DEC-20260904-dd58c3's scope_statement and CS-QA already confine. **Were they waived?** No committed record waives or discharges N-3 for these dispatches.
4. **Effect.** On the validity of what EXP-MONO-0e6e8f measured: none that I can identify — the S_4 identification is forced for every curve by RA-2, the classification was independently reproduced (validator report), and the degenerate strata were disclosed and later explained exactly. On admissibility as route-(a) evidence: N-3 bears **procedurally** — the dispatch of a new census occurred while an unwaived Coordinator precondition stood, which AGENTS.md "Dispatch preconditions bind the dispatcher" treats as a matter for a correction record supplying what followed, never a reason to edit a card. It is not a ground for excluding the measurement, and it supplies no new reading of criterion (a). I report it as an observation for the composer, not as a ground of RA-4.

**Reading declaration (RA-4).** goal.yaml; KN-OPEN-009; KN-OPEN-8a7432; RQ-MONO-001; H-MONO-ebd400; EV-MONO-e9dc3b; CORR-20260904-33fbf3; DEC-20260904-dd58c3; DEC-20260802-a51c82; DEC-20260810-2f86db; CORR-20260802-1d8384; DEC-20260930-8553d4; DEC-20261017-435b01; REVIEW-MONO-20260930-40470a-A01; EV-MONO-a0a89c; KN-FIND-c41ea9; KN-FIND-4f0d84; KN-FIND-edd62c; H-MONO-93bc4d; EXP-MONO-0e6e8f specification, execution report, reviews (by range); EXP-MONO-815525 specification, execution report, red-team report (by range); TASK-20260930-40470a report (J4) and handoff; the four grep-located ranges named in the attestation; agents/coordinator.md (Review architecture, Closure gate); docs/claims-and-verification.md (tiers, refutation artifacts); docs/inventor-protocol.md.

## 8. Observations outside the joints (not grounds; for the composer)

- **O-A.** The general-m symmetric-base formula 2^{m-2}(m−1)! needs "m ≥ 4"; at m=3 the group is S_2 (already recorded for H-MONO-93bc4d's (D3) by CORR-20260904-d2c631 as that record's status note describes it). Any promotion under RA-C5 should carry this.
- **O-B.** "Imprimitive at m ≥ 5" (H-MONO-93bc4d statement; DEC-20260904-dd58c3 limitation) is inaccurate at m=6 (primitive); the exact rule is parity of m−1. Inside A2-d.
- **O-C.** The goal's dichotomy is not exhaustive (§7.3): the derived ordered-base answer is a uniform, curve-independent block structure, which is neither "full symmetric" nor "an exceptional locus".
- **O-D.** The OI-1 dispatch-precondition finding of §7.4.
- **O-E.** DEC-20260930-8553d4 CU-9 paraphrases the predecessor's S-1 as "primitivity varying for m = 5..7"; the predecessor's own text is exact ("imprimitive at m = 5 and 7; primitive but proper at m=6").
- **O-F.** Nothing here reopens route (c) (closure_revisit_condition (iii) is not triggered: no ground against the route-(c) adoption was found or sought).
- **O-G.** Composition note (RA-C5, RA-C9): RA-1, RA-2 and RA-3 each CONCUR here; promotion remains conditional on the blind re-derivation's Q1–Q3 agreeing (A01 K4b), which I cannot see. No other composition question was identified.

## 9. Limitations

- One reviewer owned RA-1 to RA-4, the control and both questions (coverage, not cross-reviewer independence inside this task); the blind determination RB is a separate task.
- Model independence holds only as reported: this session is claude-fable-5-1 by the runtime's report and the binding, not probe-verified; the producers and the predecessor report claude-opus-5-5.
- Toy primes only (53 to 10009 here; 101 to 1999 in the records). The derivations are derivation-tier (docs/claims-and-verification.md), never "proved"; Semaev 2004 is a recalled pointer whose two used facts were verified numerically at m = 3, 4, 5.
- The exact conditional expectation was enumerated only for p ≤ 1009; at p ≈ 10⁴ a declared bound stands in for it. The single-sample excursions of about 2.3–2.7σ on C3 and C4 (opposite signs; pooled +1.87 and −0.13; the 2,000,000-tuple group-law-only C3 estimate at z = +0.01) are reported as sampling spread, with no mismatch of either instrument.
- RC-8: nothing here concerns the relation-rate question, the D-4 count, extension fields or cryptographic scale; no security estimate moves.

## 10. red_team_report

```yaml
red_team_report:
  id: null                      # not minted; identified by task, archived by TASK-20261017-fb4481
  task_id: TASK-20261017-8aff64
  claim_under_review: >-
    (P-a) route (a): DEC-20260904-dd58c3 / H-MONO-ebd400 / EV-MONO-e9dc3b, "full S_4 monodromy at m=4 over the
    symmetric base, at toy scale, on 4 curves at 2 primes", against GOAL-MONO-001 criterion (a); (P-J4) the J4
    DISSENT of TASK-20260930-40470a on grounds G-i, G-ii, G-iii; and the three CU-9 derivations of
    DEC-20260930-8553d4 (ordered-base (Z/2)^{m-2} regular; symmetric-base (Z/2)^{m-2} semidirect S_{m-1}; the
    delta-rule), each attacked on its own joint.
  objections: []                # no breaking artifact met on RA-1, RA-2, RA-3; the J4 DISSENT holds (RA-4)
  required_controls: []         # the plan's controls were run: null face (PT-1), nearby objects (PT-2, PT-3), competitors by density
  counterexample_or_mutation: >-
    Mutations PT-2 (dependent x_i) and PT-3 (square-discriminant cover) each collapse the group as a correct
    argument requires; no counterexample to any CU-9 statement was found on any curve, m, or fibre tested.
  baseline_comparison: >-
    Not an attack or cost claim, so no Pollard-rho/BSGS comparison applies (RC-8). Baseline slices reproduced:
    m=3 gives S_2 (KN-FIND-c41ea9); EXP-MONO-0e6e8f M1 (S_4 on the symmetric base at m=4) is reproduced on the
    producer's curves and on j=0, j=1728 and a supersingular curve.
  heuristic_challenges: []      # no heuristic-conditional claim; the derivations carry no heuristic
  cost_model_challenges: []     # no cost model is claimed (RC-8)
  reduction_and_scope_challenges:
    - the symmetric-base order formula 2^{m-2}(m-1)! applies for m >= 4 only (m=3: S_2)
    - "imprimitive for m >= 5" must read "imprimitive iff m-1 is even; primitive at m=6" (A2-d)
    - the goal's full-versus-exceptional dichotomy is not exhaustive on the ordered base (uniform imprimitive structure)
    - EXP-MONO-0e6e8f/815525 were dispatched while N-3 (OI-1 repairs) stood unwaived; four repairs inapplicable by construction, the uniform curve draw not carried (procedural; no validity effect found)
  proof_architecture_challenges:
    - observation collision: cycle-type support {1^4, 2^2} is shared by regular V_4 and the order-2 group; separated by the derivation and by densities (1/4 observed, 1/2 excluded at 68-113 standard errors)
    - quantifier order: the statements are uniform (for all p > 3, all nonsingular E, all m); the only witnesses are the explicit degenerate loci, which are carved out
    - boundary: m=3 (S_2) is embedded; m=4 symmetric base attains Sym(4) and is the only (m, base) where "full symmetric" literally holds
    - method ceiling: the group-law method determines the generic geometric and arithmetic monodromy completely and the finite-p class of every unramified F_p-fibre (delta-rule); it does not, and is not claimed to, say anything about rates
    - nearby objects: PT-1, PT-2, PT-3 all distinguished at the named step
    - compositional invariant: deleting nonsingularity breaks D2; deleting independence of the x_i breaks D2 (PT-2); deleting S_{m-1} breaks D8 (PT-3); deleting generic position breaks D4 (the degenerate loci)
  narrowest_supported_statement: >-
    For every prime p > 3 and every nonsingular E: y^2 = x^3 + ax + b over F_p (any j, ordinary or
    supersingular), and every m >= 3: the generic monodromy of T -> S_m(x_1..x_{m-1},T) over K(x_1..x_{m-1}) is
    (Z/2)^{m-2} acting regularly, equal to the arithmetic group over F_p(x_1..x_{m-1}); over K(e_1..e_{m-1}) it is
    (Z/2)^{m-2} semidirect S_{m-1} of order 2^{m-2}(m-1)! for m >= 4 (S_4 at m=4; 192, 1920, 23040 at m=5,6,7;
    imprimitive iff m-1 is even) and S_2 at m=3; on every squarefree full-degree F_p-fibre with all f(x_i) != 0
    the Frobenius cycle type is 1^{2^{m-2}} iff chi(f(x_i)) is constant and otherwise 2^{2^{m-3}}. Derivation tier;
    corroborated at p in {53, 101, 1009, 10007, 10009} and m in {3, 4, 5} as tabulated; toy tier; nothing about
    relation rates, the D-4 count, extension fields or cryptographic scale. The J4 DISSENT against adopting
    criterion (a) on the committed route-(a) object holds on G-i, G-ii and G-iii.
  next_concrete_action: >-
    No scientific run is needed. The composer compares RA-1 to RA-3 with the blind determination's Q1-Q4
    (A01 K4b); if they agree, RA-C5's promotion may carry the two scope corrections of RA-2; for route (a)
    the committed grounds stand until a Coordinator decision either declines (a) by concurrence (RA-C3) or
    supersedes N-2 with a stated reason (candidates d1, d2 in section 7.2).
  artifact_paths:
    - coordination/goals/GOAL-MONO-001/review/TASK-20261017-8aff64/review_report.md
    - coordination/goals/GOAL-MONO-001/review/TASK-20261017-8aff64/computations.json
    - coordination/goals/GOAL-MONO-001/review/TASK-20261017-8aff64/review_attestation.yaml
```

## 11. Reading declaration and attestation

The complete, ordered list of every path and tool-level access, the excluded paths not opened, the declared inputs not opened, and the four declared read-scope excesses are in `review_attestation.yaml` (`sources_read`, `excluded_paths_not_opened`, `declared_inputs_not_opened`, `read_scope_excess_declared`). Snapshot: HEAD `ea22cdb551166a1732ecc13d6bbc2c7c0ed8c75e`. No sibling report was read (`read_sibling_reports: false`). Runs launched: 0.
