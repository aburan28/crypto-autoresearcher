# RT-20261001-3359c3: J3 red team on HEUR-GENERIC-MSUM

- Task: TASK-20260928-62ad14. Joint J3 of review plan REVIEW-SEMBIN-20260928-04ec3c, carried in `ledger/handoffs/TASK-20260928-e4f7b2.yaml`.
- Under review: HEUR-GENERIC-MSUM in `ledger/hypotheses/H-SEMBIN-8e7ae3.yaml`. It is the heuristic EXP-SEMBIN-04ec3c (RUN-SEMBIN-c68773) inherits.
- Snapshot reviewed: HEAD `980abd8fe` with a clean tree. The run artifacts are those committed in `3c97c0d40`, whose message names TASK-20260928-e4f7b2, RUN-SEMBIN-c68773 and DEC-20260928-7c3d91.
- Not committed. This file is for the Coordinator's ledger archive task.

## Verdict on J3: `breaks`, in a direction that helps nobody below rho

The heuristic says m-SUM over the point group "admits no better generic time-store tradeoff than partial meet-in-the-middle: with store |F|^s the time is |F|^(m-s)". **That is false, and the counterexample is generic.** It is textbook parallel collision search, not a curve-structure trick.

1. **The plan's breaking artifact is produced, opened and marked `retrieved`.** van Oorschot and Wiener, §5.3, eq. (8) (vendored preprint `inputs/VOW-1996-PCS/paper_fulltext.md`, read this session) state two things:
   - A MITM with domains n1 ≤ n2 and memory w runs in `7·n2·sqrt(n1/w)` iterations by golden-collision search.
   - The paper compares this explicitly against "the standard approach whose run-time is n1·n2·t/(2wm)", and calls the new method "0.07·sqrt(n1/w) times faster".

   That "standard approach" (Even-Goldreich memory-limited MITM, their ref. [17]) is exactly HEUR-GENERIC-MSUM. With n1 = |F|^S, n2 = |F|^(m-S), S = floor(m/2) and w = |F|^s, it gives |F|^(m-s)/2. The golden-collision method gives `7·|F|^(m-S)·|F|^((S-s)/2)`. The gain is
   `G(m,s,d) = (S - s)·d/2 - log2 7` bits,
   which is positive for every s < S once (S - s)·d > 5.6. At the sweep's own ECC2K-130 operating cell (m = 8, d = 26.7) the gains are +23.9, +37.2, +23.9 and +10.5 bits at s = 0, 1, 2, 3. The table is in §2.
2. **For the relation-collection task the cost model actually prices, the frontier is lower still.** Batched multi-collision search (vOW §4.2; shown tight by Dinur, EUROCRYPT 2020) costs about `4·K·sqrt(N/w)` for K = |F| relations at memory w ≤ K. That is independent of m. At n = 131 with d = 10 and w = 2^10 the total is 2^71.5. The heuristic's best honestly costed cell is about 2^83.4, so this is 12 to 47 bits better depending on the store budget (§2, §3).
3. **Neither improvement produces a sub-rho cell, and none can.** Wagner 2002 §3, Corollary 1 (retrieved) states: "Every generic algorithm for the k-sum problem in a group G has running time Ω(√p), where p denotes the largest prime factor of the order of G". It is proved from Dai's reduction plus Shoup's generic DL bound. Shoup's bound counts group operations whatever the store (Galbraith-Gaudry 2016 §4, retrieved: BSGS's O(√r) operations with O(√r) storage "is optimal due to Shoup's lower bound"). So the hypothesis's conclusion, restricted to generic oracles, follows from known theorems and needs no heuristic. **J3's premise that the heuristic "carries the entire result" is also false.** What the heuristic carries is only the sweep's numbers.
4. **Those numbers are artifacts of an uncharged table fill (§1).**
   - Every sub-rho cell in RUN-SEMBIN-c68773 has a total trial count between 2^-37 and 2^-91.
   - At each of those cells, filling the |F|^s table alone costs more than rho's entire work.
   - The store-free branch reports generic index calculus 16 to 148 bits below √N. That contradicts Shoup's theorem: the accounting proves too much on an object where its conclusion is known false.
   - Charging the fill leaves no sub-rho cell at any degree, any m, or any store. The minimum margin is +16.5 bits at n = 97 and +19.1 bits at n = 131.

**Escalation.** The literal trigger in J3's `breaking_artifact` fires: a generic algorithm with time below |F|^(m-s) at store |F|^s now exists with a retrieved citation. The plan reads that as a breakthrough-shaped claim to send to review-breakthrough at max, but that reading does not hold. The break lowers the generic frontier toward Shoup's floor, not below rho, and it strengthens the negative. I make no breakthrough claim. Whether to convene the review-breakthrough round anyway is the Coordinator's call, and I have not downgraded anything. If anything warrants it, it is the accounting correction in §1, not a new attack.

**The ceiling the task asked about.** I found no exponential gain from Frobenius or from the 2-torsion.
- The Frobenius × negation orbit quotient buys at most log2(2n) ≈ 8.0 bits on relations and store, and ≈ 16.1 bits on linear algebra, at n = 131.
- The 2-torsion buys at most log2 h ≤ 2 bits.
- A premise of the attack plan is false at the two most important Koblitz degrees: an F_2-subspace factor base cannot be Frobenius-stable at n = 131 or n = 163 (§4).

The only exponential route I can name lies outside the generic class. It is the Weil-descended summation-polynomial oracle, under a solving-degree bound of FFDA type, which is open (§6).

---

## 1. The phantom cells

The run's cost (`code/memory_charged_family.py`, line 127) is
`relation = d + log2 m! + (nn - m·d) + oracle_t`.
It charges per-trial probe time but never the construction of the `|F|^s` table, which costs at least `|F|^s` group operations. The formula is self-consistent only while the **total trial count** `|F|·m!·N/|F|^m` is at least 1, so the table is amortised over at least one full probe sweep. Every sub-rho cell lies outside that domain.

Minimum-store sub-rho cell per degree, recomputed independently. The store and total columns match the run's `min_store_by_degree` exactly.

| n | m | d | store (log2) | reported total | vOW rho | total trials (log2) | true time ≥ (fill) |
|---|---|---|---|---|---|---|---|
| 97 | 8 | 21.35 | 85.4 | 48.28 | 48.33 | −37.15 | 2^85.4 |
| 109 | 8 | 23.35 | 93.4 | 54.26 | 54.33 | −39.15 | 2^93.4 |
| 131 | 8 | 26.70 | 106.8 | 64.20 | 64.33 | −42.60 | 2^106.8 |
| 163 | 8 | 32.35 | 129.4 | 81.25 | 81.33 | −48.15 | 2^129.4 |
| 191 | 10 | 29.40 | 147.0 | 95.19 | 95.33 | −51.81 | 2^147.0 |
| 233 | 10 | 34.65 | 173.3 | 116.19 | 116.33 | −57.06 | 2^173.3 |
| 239 | 10 | 35.40 | 177.0 | 119.19 | 119.33 | −57.81 | 2^177.0 |
| 283 | 10 | 40.90 | 204.5 | 141.19 | 141.33 | −63.31 | 2^204.5 |
| 409 | 12 | 46.75 | 280.5 | 204.09 | 204.33 | −76.41 | 2^280.5 |
| 571 | 14 | 53.70 | 375.9 | 285.14 | 285.33 | −90.76 | 2^375.9 |

This is a general fact, not a feature of the table. A sub-rho cell needs `trials·|F|^(m-s) < 2^(n/2)`, and P3a puts its store above 2^(n/2). Together these force total trials below 1. So **P3a plus "time ≥ store" implies that no sub-rho cell exists**.

**The proves-too-much version** uses a known-false object, chosen as the plan's control would want: the generic group, where "index calculus beats rho" is false by Shoup.
- `raw-result.json` `mitm_store_free` reports, at n = 131, m = 16, d = 19.5, a generic total of 2^39.28. That is 25.05 bits below the vOW column, with a table of 2^156 entries, larger than the group itself (N ≈ 2^129).
- At n = 571 the corresponding cell is 147.8 bits below.
- Of the 150 rows in that list, 90 are flagged below a baseline. (The commit message's 720 is a different count, which I did not reconcile.)

An accounting that produces generic DL algorithms below a proven generic lower bound is wrong in its bookkeeping, not informative about the curve. The A5 store budget hides this only by capping s. It does not charge time.

**Fill-charged floor** (store free, s ≤ floor(m/2), m ≤ 16, total = max(probes, |F|^s fill, |F|^2 LA)). By AM-GM the total is at least 2·sqrt(m!·N·|F|).

| n | 97 | 109 | 131 | 163 | 191 | 233 | 239 | 283 | 409 | 571 |
|---|---|---|---|---|---|---|---|---|---|---|
| min total | 64.87 | 72.01 | 83.44 | 102.87 | 118.87 | 142.55 | 145.88 | 170.32 | 239.82 | 328.03 |
| vs vOW rho | +16.54 | +17.69 | +19.12 | +21.55 | +23.55 | +26.22 | +26.55 | +29.00 | +35.49 | +42.70 |

At n = 131 the margin against the published 2^60.809 is +22.6 bits.

These are J1 territory (the cost-model algebra) and touch TASK-20260928-3f90b8's proves-too-much control. I report them because a break the plan did not anticipate is in scope. I have not read either sibling's report. Two more J1-adjacent defects, for routing:
- (i) The `MITM_CAPPED` model charges s = 0 at `m·d` bits, not ENUM's `(m-1)·d`. The heuristic's own statement does the same at s = 0, so it is beaten there by the contract's own ENUM row.
- (ii) Nothing guards the trials ≥ 1 domain.

## 2. The generic counterexample, with numbers

**Per-trial oracle at matched store |F|^s.** The heuristic's |F|^(m-s) is compared with vOW golden collision, `log2 7 + (m-S)·d + (S-s)·d/2`. At s = 0 the comparator is ENUM's |F|^(m-1). The d values are the sweep's n = 131 operating points.

| m, d | s=0 | s=1 | s=2 | s=3 | s=4 | s=5 | s=6 |
|---|---|---|---|---|---|---|---|
| 4, 20 | −2.8 | +7.2 | −2.8 | | | | |
| 6, 20 | +7.2 | +17.2 | +7.2 | −2.8 | | | |
| 8, 16 | +13.2 | +21.2 | +13.2 | +5.2 | −2.8 | | |
| 8, 20 | +17.2 | +27.2 | +17.2 | +7.2 | −2.8 | | |
| 8, 26.7 | +23.9 | +37.2 | +23.9 | +10.5 | −2.8 | | |
| 10, 16 | +21.2 | +29.2 | +21.2 | +13.2 | +5.2 | −2.8 | |
| 12, 12 | +21.2 | +27.2 | +21.2 | +15.2 | +9.2 | +3.2 | −2.8 |

Entries are gains in bits; positive means vOW is faster. The −2.8 entries are the s = S column (and m = 4, s = 0 against ENUM).

Closed forms:
- For s ≥ 1: gain = (S - s)·d/2 − log2 7.
- At s = 0 against ENUM: gain = (S/2 − 1)·d − log2 7.
- The heuristic survives only at the full-table endpoint s = S, where it wins by the constant log2 7.

Caveats, from vOW Table 1 and §4.2:
- The constant 2.5 in eq. (4) holds for w ≥ 2^10. Near w = 1 the coefficient is about 9, so the s = 0 entries are about 1.9 bits optimistic.
- The method needs |R| ≥ 2|D1|. That holds whenever |F|^S < N/2, which is true at every in-domain cell.
- vOW's cost is itself heuristic: a random-function model, calibrated by simulation. Comparing it with an unvalidated heuristic is like with like.

**Substituted into the model, inside its own validity domain** (total trials ≥ 1), at n = 131:

| store budget B | heuristic best | vOW-oracle best | gain | rho |
|---|---|---|---|---|
| 2^30 | 2^118.49 (m6, d10, s3) | 2^111.61 (m8, d20.5) | +6.9 | 2^64.33 |
| 2^40 | 2^111.99 | 2^106.61 | +5.4 | |
| 2^50 | 2^105.49 | 2^101.61 | +3.9 | |
| 2^60 | 2^98.49 | 2^96.61 | +1.9 | |
| 2^70 | 2^91.80 | 2^91.61 | +0.2 | |
| 2^80 | 2^84.30 (m8, d20, s4) | 2^86.61 | −2.3 | |

**Batched relation collection.** This does not use a per-target oracle. Walk `X → f(H(X))` on the group, with f(u) a sum of m−1 base points plus aP + bQ. With H injective on G, every collision is a relation. K = 2^d relations at memory w ≤ K cost about `4·K·sqrt(N/w)`. That figure is derived from vOW §4.2's simulation numbers (about 1.1w distinct collisions per version of 10w distinguished points at θ = 2.25·sqrt(w/n)). Dinur 2020 proves T²·S = Θ̃(C²·N) tight for S = Õ(C).

At n = 131:

| d | w | IC total | vs rho |
|---|---|---|---|
| 10 | 2^10 | 2^71.5 | +7.17 |
| 16 | 2^16 | 2^74.5 | +10.17 |
| 20 | 2^20 | 2^76.5 | +12.17 |
| 28 | 2^28 | 2^80.5 | +16.17 |

For comparison, the heuristic prices the relation phase at s = 1, m = 8 at 2^144.3.

This is just rho with |F| extra unknowns. Each relation costs a rho collision, and the total exceeds rho by at least sqrt(|F|). It is Shoup's bound made concrete.

## 3. Baselines and `dominated_by`

- **Pollard rho (vOW).** Work is 0.886·2^(n/2) along the whole memory curve. The published ECC2K-130 figure is 2^60.809 with ⟨−1⟩×⟨π⟩. No generic index-calculus cell beats either once fill is charged (§1). The best generic index-calculus figure I can construct at n = 131 is 2^71.5 (§2), +7.2 bits.
- **BSGS.** It uses √N store to reach √N time. It is the existence proof that a store of 2^(n/2) buys exactly the generic optimum and nothing below it.
- **Closest specialised baselines.**
  - vOW golden collision dominates the heuristic's oracle at every s < S.
  - Parallel-collision-search multi-collision dominates the relation phase at every store.
  - If the table is read as **free precomputation**, the right comparator is rho with precomputation, Bernstein-Lange 2012 (KN-LIT-7cc07f, `kb`): about 1.77·l^(1/3) online with a table of l^(1/3). At ECC2K-130 that is about 2^43.8 online with a table of about 2^43. Every store-free index-calculus cell loses to it at matched store.
  - The table of s-sums depends only on (E, V), not on (P, Q), so the precomputation reading is natural. That is the reversal reading (red-team item 8): the measured obstruction "store > 2^(n/2)" is the hypothesis of the preprocessing model, where it loses to Bernstein-Lange.
- **`dominated_by: null` is not supported.** The hypothesis says it was "checked rather than defaulted", but checked only against program records that bound the oracle family by memory. Two rows in this program's own corpus subsume or dominate it:
  - KN-LIT-011 (Shoup) subsumes the generic-class conclusion: time Ω(√N) at any store.
  - KN-LIT-012 (vOW) dominates the tradeoff (§5.3).

  Under AGENTS.md "Pareto honesty", a null not checked against every frontier row is a defect. `sota_delta` for the generic class is 0 against Shoup.

## 4. Frobenius: the orbit quotient, with numbers, and a false premise

**The premise is false at n = 131 and n = 163.** An F_2-subspace V ⊂ F_{2^n} is stable under squaring only if it is an F_2[x]/(x^n − 1)-submodule. Its dimension must then be a sum of degrees of irreducible factors of x^n − 1, which are 1 and ord_n(2). The orders, computed exactly with a cyclotomic-coset cross-check:

| n | 97 | 109 | 131 | 163 | 191 | 233 | 239 | 283 | 409 | 571 |
|---|---|---|---|---|---|---|---|---|---|---|
| ord_n(2) | 48 | 36 | **130** | **162** | 95 | 29 | 119 | 94 | 204 | 114 |
| stable dims in [2, n/2] | 48 | 36, 37 | **none** | **none** | 95 | 29, 30, 58, 59, 87, 88, 116 | 119 | 94, 95 | 204 | 114, 115, 228, 229 |

At ECC2K-130 and K-163, 2 is a primitive root mod n. The only Frobenius-stable F_2-subspaces there have dimension 0, 1, n−1 or n. Only n = 233 has a stable dimension near the sweep's operating d.

So F_2-linearity, which Weil descent needs, and Frobenius stability, which the orbit quotient needs, are incompatible at the two headline Koblitz degrees. A generic oracle does not care, because F can be any union of τ-orbits. An algebraic oracle using F' = ∪_j V^(2^j) pays for about n^(m−1) rotation patterns.

**What the orbit quotient buys** (generic F, group ⟨τ⟩ × ⟨−1⟩ of order 2n): relations divide by 2n, store by 2n, and linear algebra by (2n)². At n = 131 that is 8.03 bits on relations and store and 16.07 bits on linear algebra. It does not change the probes per relation.

Effect on P4's minimum store (m = 8):

| comparison | min store |
|---|---|
| no orbit (producer's model) | 2^106.6 |
| orbit on index calculus only, vOW column unchanged (flatters index calculus) | 2^87.9 |
| orbit on both sides (rho gets sqrt(2n)) | 2^93.2 |
| orbit on index calculus, against published 2^60.809 | 2^92.6 |

So the orbit quotient buys 13 to 19 bits, and the store still exceeds rho's work by about 29 to 33 bits. With fill charged and the orbit applied, the minimum total is 2^75.4 at m = 8, against 2^60.3 (vOW/sqrt(2n)) and 2^60.8 (published): +14.6 bits.

There is no exponential gain here, for a structural reason. The prime part of E(F_{2^n}) is Z/N, a simple Z[τ]-module with τ acting as an eigenvalue λ of order n. Its orbits are cosets of a multiplicative subgroup of order n, with no additive quotient to sort on. That the Z[τ]-module structure is cyclic is `recalled` (Lenstra 1996), but the simplicity argument needs only that N is prime.

Galbraith-Gaudry 2016 §10.4 (retrieved) calls using Frobenius to speed up index calculus on subfield curves "a major open problem". It says Gorla-Massierer's trace-zero approach "does not currently lead to a dramatic speed-up".

## 5. The 2-torsion, and transfer of KN-FIND-ffe1df to characteristic 2

- E(F_{2^n}) ≅ Z/h × Z/N with h ∈ {2, 4} and N prime, so every quotient has order dividing h. In a Schroeppel-Shamir, HGJ or Wagner style split, this buys at most log2 h ≤ 2 bits.
- The quotient onto E/2E is computable exactly from x. Tr(x(P)) = Tr(a) holds exactly when P ∈ 2E, for x ≠ 0. This is the halving criterion (Knudsen and Schroeppel; `recalled`).
- I verified it exhaustively, as a scratch computation and not a run record, on y² + xy = x³ + ax² + b over F_{2^7}, F_{2^11} and F_{2^13}, with a ∈ {0, 1} and random b. The curve orders were #E = 128, 126, 2052, 2110, 8204 and 8306. In every case #2E = #E/2, with **0 mismatches**.
- The 2-/4-torsion invariant variables (FGHR; Galbraith-Gebregiyorgis) give speedups polynomial in m and constant in n. The vendored GG-2014-806 text (lines 2180–2189) concludes: "our methods are worse than Pollard rho". Galbraith-Gaudry §9.1 says they "are not competitive with Pollard rho".

**What transfers from KN-FIND-ffe1df:**
- Theorem C transfers verbatim to the prime-order part. An exact sum-compatible filter is a homomorphism, and Z/N has none. This is exactly why Wagner, Schroeppel-Shamir, HGJ/BCJ and dissection do not apply. HGJ 2010 (retrieved) builds "the two subsets … containing elements respectively congruent to R and S−R modulo M", which needs a homomorphic image to sort on.
- The additive completion does **not** transfer. Its degeneracy lemma is stated "with p > 2". In characteristic 2, double poles are divisible by p, and the trace filter above is an explicit exact degenerate case of alphabet 2.

So the F_2-linear x-functional filters ℓ(x) at alphabet 2^j, j ≥ 2, are **uncovered** for binary curves, as is the approximate case generally. Theorem C caps the exact gain at h.

Also note ffe1df's own j = 2 headline is withdrawn as UNPROVED even for p > 2. Nothing in it supports or closes anything for binary fields beyond Theorem C.

## 6. What would have to be true for an exponential improvement

| class | exponential gain possible? | why |
|---|---|---|
| Generic (oracle sees F as an unstructured subset) | **No, by theorem** | Shoup / Wagner Cor. 1, at any memory |
| Automorphisms (τ, −1, translation by E[h]) | No | group of order ≤ 2n·h, so polynomial gain only |
| Exact quotients (k-tree, Schroeppel-Shamir, representation, dissection) | No | only quotients of order dividing h ≤ 4 (Theorem C) |
| Approximate sum-compatible x-filters in char 2 | Open | would need a cheap h: E → [M], M ≈ N^(1/(j+1)), with bucket gain growing in M; not covered by ffe1df for p = 2 |
| Algebraic oracle (Semaev / Weil descent / S_3-chaining / Riemann-Roch) | Open | needs the solving degree of the descended system, x_i ∈ V with dim V ≈ n/m, to be o(n/log n), e.g. bounded by f(m) (an FFDA-type statement) |

On the algebraic row: Galbraith-Gaudry 2016 §10.2 (retrieved) says there is "no consensus whether there is a subexponential algorithm for ECDLP in characteristic 2", and that "the FFDA approach seems to be too optimistic". ECMH (arXiv 1601.06502 §1, retrieved) calls Semaev's L[1/2] claim "based on heuristic assumptions that prevailing evidence suggests are unlikely to hold". The program's own check of Semaev's Assumption 1 reaches only n ≤ 21 (EV-ICPERF-a8080e, as cited in the contract's scope).

Only the last two rows can move an exponent, and both are outside HEUR-GENERIC-MSUM's class by definition. **The heuristic's failure is irrelevant to them, and so is its truth.**

## 7. Why the program's one supporting datum is worthless here

- **Wrong logical direction.** HEUR-GENERIC-MSUM is a lower bound over all algorithms ("admits no better"). The Riemann-Roch datum shows one oracle *achieving* Θ(|F|²). An achievability point cannot support an optimality claim.
- **Non-discriminating.** At m = 3 the heuristic's curve is flat: s = 0 (ENUM) and s = 1 both give |F|². vOW does not beat it either: about 7|F|² at w = |F|, worse by log2 7. So m = 3 cannot separate the heuristic from vOW. They first diverge at m ≥ 4 with 0 < s < S, and at s = 0 for m ≥ 6.
- **Unconferred grade.** It is graded `external_unreviewed` (A8).

## 8. Citations and provenance

| source | provenance | what was read / relied on |
|---|---|---|
| van Oorschot & Wiener, PCS, J. Cryptology 1999 (1996 preprint) | **retrieved** | vendored `inputs/VOW-1996-PCS/paper_fulltext.md` (source sha in `source_record.yaml`), read this session: §4.1 eq. (3); §4.2 including eq. (4) and Table 1; §5.3 eq. (8) and the "0.07·sqrt(n1/w)" comparison |
| Wagner, A Generalized Birthday Problem, CRYPTO 2002 | **retrieved** | iacr.org archive PDF, sha256 c7c41399…, text extracted: §2 (Z/mZ via intervals; Schroeppel-Shamir summary; collision search for single solutions); §3 Thm 1, Thm 2 (Dai), Cor. 1, Thm 3; §5 open problems |
| Shoup, Lower Bounds for DL, EUROCRYPT 1997 | `kb` (KN-LIT-011, itself "not re-read") | primary PDF fetched but unreadable (Type-3 fonts). The Ω(√p) statement used here is as stated in two retrieved secondaries: Wagner §3 and Galbraith-Gaudry §4 |
| Dinur, Tight Time-Space Lower Bounds for Finding Multiple Collision Pairs, EUROCRYPT 2020 (ePrint 2020/229) | **retrieved** (abstract only) | T²·S = Ω̃(C²·N) for S = Õ(C), matched by PCS |
| Galbraith & Gaudry, Recent progress on ECDLP, DCC 2016 (ePrint 2015/1022) | **retrieved** | full text: §4, §9.1, §9.2, §10.2, §10.3, §10.4 |
| Galbraith & Gebregiyorgis 2014 (ePrint 2014/806) | **retrieved** | vendored `inputs/GG-2014-806/paper_fulltext.txt`, conclusion |
| Howgrave-Graham & Joux 2010 (ePrint 2010/189) | **retrieved** | full text: modular 4-way merge; R mod M representation split |
| Becker, Coron & Joux 2011 (ePrint 2011/474) | **retrieved** (abstract only) | exponents only. The mechanism's dependence on modular constraints is by inheritance from HGJ (`recalled`) |
| Dinur, Dunkelman, Keller & Shamir 2012, "Efficient Dissection of Bicomposite Problems…" (ePrint 2012/217) | **retrieved** (abstract only) | applies to bicomposite problems. That knapsack dissection guesses partial sums through bit or modular structure is `recalled` |
| Schroeppel & Shamir 1981 | `recalled` | statement as relayed by Wagner §2 and the HGJ abstract (retrieved secondaries) |
| Maitin-Shepard, Tibouchi & Aranha, ECMH 2016 (arXiv 1601.06502) | **retrieved** | §1 "Are binary elliptic curves safe?"; §3 DL reduction for group k-sums |
| Halcrow & Ferguson, ECOH second preimage (ePrint 2009/168) | `recalled` | search snippet only, not opened |
| Bernstein & Lange 2012, Computing small DLs faster | `kb` (KN-LIT-7cc07f) | figures as relayed by the corpus record |
| Corrigan-Gibbs & Kogan 2018, DL with preprocessing | `recalled` | not opened |
| Petit & Quisquater 2012; Huang, Kosters & Yeo 2015; Kousidis & Wiemers | `recalled` / `kb` (KN-LIT-024) | FFDA status taken from the retrieved Galbraith-Gaudry §10.2 |
| Lenstra 1996, CM structure of E(F_{q^n}); Knudsen 1999 / Schroeppel 2000 halving | `recalled` | halving criterion checked by exhaustive toy computation (`internal`, scratch) |
| KN-FIND-ffe1df | `internal` | read in full |

---

```yaml
red_team_report:
  id: RT-20261001-3359c3
  task_id: TASK-20260928-62ad14
  review_plan: REVIEW-SEMBIN-20260928-04ec3c
  joint: J3
  verdict: breaks
  verdict_direction: >-
    The heuristic is false as a statement of the generic time-store frontier.
    The counterexample is generic (vOW 1999 golden-collision and multi-collision
    search) and lowers cost toward Shoup's floor. It never goes below rho. The
    hypothesis's conclusion, restricted to generic oracles, survives as a
    corollary of Shoup 1997 and Wagner 2002 Cor. 1, not of HEUR-GENERIC-MSUM.
  escalation_note: >-
    The literal breaking_artifact condition is met (retrieved citation: vOW
    §5.3 eq. 8). The stated rationale for escalation (a breakthrough-shaped,
    sub-rho route) is absent. No breakthrough is claimed here and nothing is
    downgraded. The decision is the Coordinator's.
  claim_under_review: >-
    HEUR-GENERIC-MSUM (H-SEMBIN-8e7ae3): m-SUM over E(F_2^n) admits no better
    generic time-store tradeoff than partial MITM, time |F|^(m-s) at store
    |F|^s, s <= floor(m/2). Plus J3's premise that it carries the entire result.
  objections:
    - id: O1
      severity: blocking
      text: >-
        False as stated. vOW §5.3 eq. (8) (retrieved) gives time
        7*|F|^(m-S)*|F|^((S-s)/2) at store |F|^s. That is a gain of
        (S-s)*d/2 - log2(7) bits for every s < S = floor(m/2), e.g. +37.2 bits
        at m=8, d=26.7, s=1. vOW names the heuristic's tradeoff as "the
        standard approach" and reports it beaten by 0.07*sqrt(n1/w).
    - id: O2
      severity: blocking
      text: >-
        For relation collection (what the cost model prices), PCS
        multi-collision gives about 4*K*sqrt(N/w), independent of m (Dinur 2020
        tight). This beats every honestly costed heuristic cell at n=131 by
        roughly 12-47 bits. It is still above rho, by at least sqrt(|F|).
    - id: O3
      severity: blocking (overlaps J1 and the proves-too-much control; routed, not owned)
      text: >-
        The table fill |F|^s is never charged (code line 127). Every sub-rho
        cell has total trial count 2^-37..2^-91. The store-free branch reports
        generic index calculus 16-148 bits below sqrt(N), contradicting Shoup.
        With fill charged there is no sub-rho cell at any degree, m or store.
        The minimum margin is +16.54 bits (n=97) and +19.12 (n=131).
    - id: O4
      severity: material
      text: >-
        J3's premise that the heuristic "carries the entire result" is false.
        The generic-class conclusion follows from Shoup (any memory). The
        heuristic carries only the sweep's numbers (P1, P4's 2^106.8 / 2^107.7,
        the 14 store-budget cells, the store-free cells), and section 1 shows
        those to be accounting artifacts.
    - id: O5
      severity: material
      text: >-
        The random_model_justification is an achievability datum (one oracle
        reaching |F|^2 at m=3) offered for an optimality claim, at the one
        arity where the heuristic and its generic alternative coincide. It is
        non-discriminating and of unconferred grade (A8).
    - id: O6
      severity: material
      text: >-
        The attack plan's premise that an F_2-subspace base is
        Frobenius-stable is false at n=131 and n=163, where ord_n(2) = n-1. At
        the other degrees, stable dimensions are multiples of ord_n(2); only
        n=233 lands near the operating d.
    - id: O7
      severity: minor
      text: >-
        At s=0 the heuristic's |F|^m (and MITM_CAPPED's m*d) is beaten by the
        contract's own ENUM |F|^(m-1).
  required_controls:
    - id: RC1
      what: >-
        Re-run the sweep with the fill term (total = lsum(total, s*d)) and a
        trials >= 1 guard.
      predicts: >-
        Zero sub-rho cells at all 11 degrees and every B. Minimum margins as in
        report section 1.
      cost: seconds
    - id: RC2
      what: >-
        Generic-lower-bound consistency flag: any generic-class cell below
        log2(sqrt(N)) minus a declared constant is an arithmetic defect, not a
        result.
      predicts: fires on all store-free sub-rho rows of RUN-SEMBIN-c68773
    - id: RC3
      what: >-
        Add oracle VOW_GC (log2 7 + (m-S)d + (S-s)d/2, w >= 2^10) and
        relation model PCS_BATCH (2 + d + (nn - w)/2, w <= d) beside
        MITM_CAPPED, reported per (m, s, d).
      predicts: section 2 tables; no sub-rho cell
    - id: RC4
      what: >-
        Optional measured check. Toy binary curve, m=6, d=6, s=1: table MITM
        about 2^30 against vOW golden collision about 2^26.8 per trial. Null
        object: the same two procedures on a random function with identical
        domain and range sizes.
      predicts: >-
        A gap of about 3.2 bits on both the curve and the null. A matching gap
        means the gain is generic, which is the claim.
    - id: RC5
      what: >-
        ffe1df RT-EXP-1 bucket-gain ladder transferred to binary toy curves,
        using F_2-linear x-functional filters at M = 2^j, a SHA null, and
        Tr(x) as the built-in positive control (exact gain at M=2).
      predicts: >-
        Gain 2 at j=1 from Tr; decay with the null for j >= 2 unless
        something new appears.
  counterexample_or_mutation: >-
    vOW golden-collision MITM (1999, §5.3 eq. 8) as the m-SUM oracle. For the
    accounting, the mutation is a single term: charge |F|^s. The verdict flips
    from "store-free sub-rho cells exist" to "none exist".
  baseline_comparison: >-
    Fill-charged generic index calculus stays above vOW rho at every listed
    degree (+16.5 to +42.7 bits) and above published ECC2K-130 2^60.809 by
    +22.6. Best constructed generic figure at n=131: 2^71.5 (PCS batch, d=10,
    w=2^10), +7.2 over rho. BSGS shows store 2^(n/2) buys exactly sqrt(N).
    Under a free-table (preprocessing) reading, Bernstein-Lange 2012
    (KN-LIT-7cc07f) dominates every store-free cell. dominated_by: null is not
    supported: KN-LIT-011 and KN-LIT-012 are in-corpus frontier rows.
  heuristic_challenges:
    - >-
      Inventory: HEUR-GENERIC-MSUM has no rigorous bound plus distribution
      theorem behind it. The "standard generalised-birthday accounting" it
      invokes is Even-Goldreich memory-limited MITM, which vOW shows is
      suboptimal. Wagner's k-tree, the usual meaning of "generalised
      birthday", does not apply to prime-order groups at all (Theorem C;
      Wagner §3).
    - >-
      Random-model transfer: F = {x in V} is F_2-linearly structured. In
      characteristic 2 the x-trace is an exact filter, so structure is
      exploitable at alphabet <= h. The cheapest deviation probe is RC5.
    - >-
      Scale: validation_experiment_ids is empty. The only datum is m=3, where
      the heuristic is untestable.
  cost_model_challenges:
    - The one-time table fill is uncharged (O3).
    - Total trials below 1 at every sub-rho cell, a fractional number of attempts.
    - MITM_CAPPED at s=0 is overcharged by |F| relative to ENUM (O7; J1).
    - >-
      vOW constants are disclosed: 2.5 (w >= 2^10), up to about 9 at w = 1, 7
      in eq. (8), about 4 per batched collision.
  reduction_and_scope_challenges:
    - >-
      The generic-class statement should be cited to Shoup 1997 and Wagner
      2002 Cor. 1, not derived from the sweep. sota_delta on the generic class
      is 0.
    - >-
      Dai's reduction (Wagner Thm 2) needs lists of random known-exponent
      elements. It does not bound oracles that exploit F's x in V structure.
      That is exactly the surviving non-generic route, and it is untouched.
  proof_architecture_challenges:
    - >-
      Quantifier order: a for-all-algorithms lower bound is supported by a
      there-exists datum.
    - >-
      Nearby / known-false object: the generic group. The store-free accounting
      finds sub-rho cells there (16-148 bits below sqrt(N)), so it proves too
      much.
    - >-
      Observation fiber: holding per-trial cost fixed and toggling only the
      fill charge flips the verdict. The missing separator is the fill term.
    - >-
      Method ceiling: in the generic class the ceiling is Shoup's sqrt(N) at
      any memory. Any exponential change must come from the encoding (report
      section 6, rows 4-5).
  resource_reading:
    examined: true
    reading: >-
      The s-sum table depends only on (E, V), so "store > 2^(n/2)" is a
      preprocessing-model statement. There it loses to Bernstein-Lange rho
      with precomputation.
    spawned_ids: []
    spawned_ids_note: >-
      No ledger write is in my scope. A candidate successor is RC5, the
      characteristic-2 filter ladder.
  narrowest_supported_statement: >-
    HEUR-GENERIC-MSUM is false as a statement of the generic frontier. Every
    cost and margin quoted in this statement is model arithmetic (claim tier
    heuristic_estimate) taken from section 1's re-derivation, not a
    measurement. vOW golden-collision search beats |F|^(m-s) at store |F|^s by
    (floor(m/2)-s)*d/2 - log2 7 bits, and PCS beats the relation phase at
    every store. No generic method, at any memory, gives a sub-rho index
    calculus on these curves (Shoup; Wagner Cor. 1). With the table fill
    charged, the contract's own accounting agrees: the minimum margin is +16.5
    bits at n=97 and +19.1 at n=131 against the vOW column. Frobenius x
    negation buys at most log2(2n) bits on relations and store and
    2*log2(2n) on linear algebra (8.0 and 16.1 bits at n=131). The 2-torsion
    buys at most 2 bits. No exponential improvement was found. The open
    exponential routes are non-generic: an FFDA-type solving-degree bound for
    the Weil-descended summation-polynomial system, or approximate
    sum-compatible x-filters in characteristic 2.
  next_concrete_action: >-
    Under an additive amendment to EXP-SEMBIN-04ec3c, re-run the ~18 s sweep
    with RC1 (fill term plus trials >= 1 guard) and RC2 (generic-lower-bound
    flag). The predicted outcome is zero sub-rho cells at every degree and
    store. Then restate H-SEMBIN-8e7ae3's generic-class conclusion as a
    corollary of Shoup 1997 / Wagner 2002 Cor. 1 rather than of
    HEUR-GENERIC-MSUM.
  artifact_paths:
    - coordination/goals/GOAL-SEMBIN-5078bc/reviews/TASK-20260928-62ad14/report.md
review_attestation:
  task_id: TASK-20260928-62ad14
  joints_owned: [J3]
  independent_session: true
  requested_policy: review-adversarial
  resolved_model_id: claude-opus-5-5
  model_verified: false
  read_sibling_reports: false
  paths_read:
    - AGENTS.md
    - agents/red-team.md
    - ledger/handoffs/TASK-20260928-e4f7b2.yaml
    - ledger/hypotheses/H-SEMBIN-8e7ae3.yaml
    - experiments/EXP-SEMBIN-04ec3c/specification.yaml
    - experiments/EXP-SEMBIN-04ec3c/code/memory_charged_family.py
    - experiments/EXP-SEMBIN-04ec3c/runs/RUN-SEMBIN-c68773/raw-result.json
    - knowledge/findings/KN-FIND-ffe1df.md
    - knowledge/literature/KN-LIT-011.md
    - knowledge/literature/KN-LIT-012.md
    - knowledge/literature/KN-LIT-2063.md
    - knowledge/literature/KN-LIT-2125.md
    - knowledge/literature/KN-LIT-327949.md
    - knowledge/literature/KN-LIT-124.md
    - knowledge/literature/KN-LIT-125.md
    - knowledge/literature/KN-LIT-6192.md
    - knowledge/literature/KN-LIT-024.md
    - knowledge/literature/KN-LIT-477.md
    - knowledge/literature/KN-LIT-7cc07f.md
    - knowledge/literature/KN-LIT-359dcc.md
    - inputs/VOW-1996-PCS/paper_fulltext.md
    - inputs/VOW-1996-PCS/source_record.yaml
    - inputs/GG-2014-806/paper_fulltext.txt
    - inputs/GG-2014-806/PROVENANCE.yaml
  read_notes:
    - The specification was read in full.
    - >-
      Of the code, lines 40-214 were read in full; the rest only through a
      grep outline.
    - >-
      Of raw-result.json, only the keys min_store_for_subrho,
      min_store_by_degree and mitm_store_free were used.
    - Of the KN-LIT entries, only the header and contribution sections were read.
    - >-
      Of the vOW text, lines 230-430 and 672-781. Of the GG-2014-806 text, a
      grep and lines 2176-2195.
    - The commit message of 3c97c0d40 was read via git show.
  not_read:
    - experiments/EXP-SEMBIN-04ec3c/RESULTS.md (absent at HEAD although TASK-20260928-e4f7b2 lists it)
    - ledger/decisions/DEC-20260928-7c3d91.yaml
    - every directory under coordination/goals/GOAL-SEMBIN-5078bc/reviews/ other than this task's
    - >-
      scratchpad files I did not create (gttd.*, m0_repro.json,
      rerun-raw-result.json, main_raw.jsonl, ours_raw.jsonl, a1_ref_high.log,
      curve_table.*, deep_research_frontier.md, exact_*); present in the
      session scratchpad, not opened
  external_sources_opened: >-
    Wagner 2002 PDF; Galbraith-Gaudry ePrint 2015/1022 PDF; HGJ ePrint
    2010/189 PDF; ECMH arXiv 1601.06502 PDF; ePrint abstract pages 2020/229,
    2010/189, 2011/474, 2012/217; Shoup 1997 PDF (fetched, not text-readable).
  procedure_deviations:
    - >-
      coordinator_prior was displayed before this verdict was recorded. The
      Read tool returned the whole handoff file in one call. The prior concerns
      P1-P5 and states no expectation about J3. Nothing here derives from it.
    - >-
      No TASK-20260928-62ad14 handoff card exists in ledger/handoffs at HEAD
      980abd8fe. I worked from the dispatching message and J3's text in
      TASK-20260928-e4f7b2.
    - >-
      The session was interrupted by an API spend limit and resumed on the
      dispatcher's instruction. No instruction changed.
    - >-
      The RT id was drawn as a random 6-hex token and checked unused across
      *.yaml and *.md, because tools/allocate_id.py has no RT type.
    - >-
      The harness refused to let this subagent write report.md. The full
      content is returned in the response, for the archive task to place at
      the path above. Nothing was committed.
  verdict: breaks
```

Sources:
- [van Oorschot & Wiener, Parallel Collision Search (author preprint)](https://people.scs.carleton.ca/~paulv/papers/JoC97.pdf), via vendored `inputs/VOW-1996-PCS/`
- [Wagner, A Generalized Birthday Problem, CRYPTO 2002](https://www.iacr.org/archive/crypto2002/24420288/24420288.pdf)
- [Dinur, Tight Time-Space Lower Bounds for Finding Multiple Collision Pairs (ePrint 2020/229)](https://eprint.iacr.org/2020/229)
- [Galbraith & Gaudry, Recent progress on the ECDLP (ePrint 2015/1022)](https://eprint.iacr.org/2015/1022)
- [Howgrave-Graham & Joux, New generic algorithms for hard knapsacks (ePrint 2010/189)](https://eprint.iacr.org/2010/189)
- [Becker, Coron & Joux, Improved generic algorithms for hard knapsacks (ePrint 2011/474)](https://eprint.iacr.org/2011/474)
- [Dinur, Dunkelman, Keller & Shamir, Efficient Dissection of Bicomposite Problems (ePrint 2012/217)](https://eprint.iacr.org/2012/217)
- [Maitin-Shepard, Tibouchi & Aranha, Elliptic Curve Multiset Hash (arXiv 1601.06502)](https://arxiv.org/pdf/1601.06502)
- [Galbraith & Gebregiyorgis (ePrint 2014/806)](https://eprint.iacr.org/2014/806), via vendored `inputs/GG-2014-806/`
- [Shoup, Lower Bounds for Discrete Logarithms (PDF, fetched but not text-readable)](https://www.shoup.net/papers/dlbounds1.pdf)
- [Halcrow & Ferguson, ECOH second preimage (ePrint 2009/168), search result only](https://eprint.iacr.org/2009/168)