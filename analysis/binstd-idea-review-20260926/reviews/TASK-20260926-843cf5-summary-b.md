# TASK-20260926-843cf5, half B: review of 2a3771, 493606, 845a77, faa8d2, 793fd8, 6237e5

Reviewer lane R3 (revision and hold), half B. Date 2026-09-26. Advisory input to
the next `/coordinate` selection point; this file changes no status and approves
nothing. Every number below was re-derived in short Python arithmetic unless
marked `unchecked` in the per-idea review. No experiment was run.

## Summary table

| idea | verdict | agrees with hold? | one-line concrete experiment | successor seam |
| --- | --- | --- | --- | --- |
| IDEA-20260922-2a3771 (rank 33, HOLD-S) | defective | agrees (and adds: toy ladder half empty; basis-conversion "cost" is O(n^2) bits once) | Zero-solver Lemma A2 check at n = 17, K1 (`y^2+xy=x^3+x^2+1`, #E = 2·65587), V = ker g(τ) of dim 8, m = 2: enumerate S(R) exhaustively and test closure under coordinate squaring and overlap with S(σR); predicted 0 and 0. | none (a sentence in the n = 41/43 stable-lane record; the soundness check as a required negative control) |
| IDEA-20260922-493606 (rank 34, HOLD-T) | defective | agrees (and deepens: re-choosing n does not rescue it, the divisor μ is the equivariance/symmetry confusion) | Two-arm S_4 (m = 3, l = 5) W_4-closure cost at n = 19: CERTBIN ordinary cell vs Koblitz-shaped `y^2+xy=x^3+1` (#E = 4·130873); pre-registered ratio 1.0; pure Python, WDSat missing. | m ≥ 4 cost cell on CERTBIN siblings with NO symmetry claim (G2 lane's seam; no new ID) |
| IDEA-20260922-845a77 (rank 29, HOLD-P) | dominated | agrees (correction: the hold's cited faa8d2 factor is not about this hash-join; the reason is the product law) | Two-list MITM at the CERTBIN n = 19 cell, m = 3, l = 6, against exhaustive enumeration and a relabelled Z/NZ control (predicted identical op counts). | tooling only: MITM as solver-free ground-truth oracle for m = 3/4 CERTBIN cells (instrument note, no ID) |
| IDEA-20260922-faa8d2 (rank 30, HOLD-P) | sound_with_corrections | agrees (the bound is right for a strawman; c_amort* is stated three inconsistent ways) | (L, b) meter on top-k residual truncation at RC-1 (n = 17, l = 9, k ∈ {5,7}) vs random bijection and Z/NZ; predicted b(π) near 2^k on E, about 2 on Z/NZ. | fixture only: calibrated (L, b) control for future "bucketed key" proposals (no ID) |
| IDEA-20260922-793fd8 (rank 35, HOLD-U) | defective | agrees, with both release conditions tightened (floor ratio < 1, not < 100; per-attempt α ≤ 1, not CV > 1) | Per-attempt cost distribution of the W_4 closure at RC-1 (400 archived unsat + 100 planted sat); expected CV ≈ 0 — a controlled null, since the closure is not a backtracking search. | none (schema columns for ICPERF's boundary table when a SAT engine exists) |
| IDEA-20260922-6237e5 (rank 36, HOLD-V) | sound_with_corrections | agrees (refinement: the trace-parity / 2E correlation must be conditioned out or it manufactures a factor-2 H_alt at m = 2) | Three-arm DP / uniform / filter-only yield test at n = 19 Koblitz-shaped (#E = 4·130873), m = 2, l = 7, all arms in the prime-order subgroup, normal basis constructed; band [0.7, 1.4]. | NEW: the weight set W_w = {x : HW_NB(x) ≤ w} as a Frobenius-stable implicit-membership factor base at n = 131 (novelty unverified) |

## Ranked: what in this half is worth designing next, and why

1. **Nothing in this half is worth a batch slot as filed.** Two records are
   defective on their core object (2a3771, 493606 both rest on a per-instance
   Frobenius symmetry that IDEA-20260906-a77711 shows is an equivariance between
   conjugate targets, and both name toy or deployed degrees that host no
   τ-stable subspace at all), one is a correct construction dominated at every
   arity on ECC2K-130 by the product law (845a77), one is a correct bound on a
   construction nobody proposed (faa8d2), one has a mechanism that does not
   survive the concentration of a sum of 2^{20+} attempt costs (793fd8), and one
   is a sound null-controlled measurement whose only structural content is a
   correlation it did not notice (6237e5).
2. **If one cheap thing is taken, take the 2a3771 Lemma A2 soundness check**
   (seconds of pure Python, no solver). It is not for 2a3771's sake: it converts
   a77711's zero-compute lemma into a measured control that every future
   "Frobenius symmetry-breaking on one instance" record (7ab503 is in half A) must
   pass, and it is the same enumeration the 493606 review needs at m = 3.
3. **The one new seam is 6237e5's DP set as an object.** `{x : HW_NB(x) ≤ w}` is
   Frobenius-stable (weight is shift-invariant in a normal basis), has an O(n)
   implicit membership test, and exists at n = 131 where no stable subspace does.
   It is priced against the product law like everything else (per-attempt budget
   2^4.4 at m = 4) and the pre-registered expectation is that a cardinality
   constraint is as inert under unit propagation as the F-set clauses of 3c7a91;
   but it is the first non-linear Frobenius-stable factor base with a cheap
   membership test this corpus has named at the ECC2K-130 degree, and no corpus
   record names it (grep for weight/Hamming + factor base: only NAF/relation-weight
   hits). Novelty unverified externally.
4. **6237e5 itself** is runnable in minutes once parity-conditioned and is the
   only record in this half whose pre-registered null is genuinely uncertain
   beyond the confound; it should ride as bycatch of the G3 lane's "2^33 DPs as
   data" seam rather than as its own design.
5. **HOLD-P's text should be corrected at the next ranking**, not to release the
   hold but to state the right reason: 845a77's hash-join is an undominated
   time/memory row against 96c4f3's loop and table variant; what kills it on
   ECC2K-130 is the product law (per-attempt budget 2^4.4–2^25 vs probe cost
   |V|^{floor(m/2)} = 2^54–2^65 at the balanced |V|), not faa8d2's factor, which
   bounds a solver-per-entry strawman.
6. **HOLD-U's release conditions should be tightened** to "floor ratio < 1" and
   "per-attempt tail index α ≤ 1", after which the portfolio claim is held
   permanently on ECC2K-130 (free-oracle floor 2^68.58 at m = 3 is 218× rho, and
   a floor is a deterministic lower bound no tail draw crosses).

## Arithmetic checks performed, by record

Commands were short Python (no solver, no experiment). Anything not listed here
is `unchecked` in the review file.

**Shared**
- ord_n(2): 17→8, 19→18, 23→11, 29→28, 31→5, 37→36, 41→20, 131→130, 163→162,
  233→29, 239→119, 283→94, 409→204, 571→114. τ-stable subspace dimensions are
  {0, 1} plus multiples of ord_n(2) (Φ_n splits into (n−1)/ord irreducibles of
  degree ord). So 29, 37, 131, 163 host none of index-calculus size; 17, 23, 31,
  41 do (8k, 11k, 5k, 20k). 233/283/409/571 lanes agree with 8fe0ef.
- Matched rho, brief convention sqrt(π r/(4k)): ECC2K-130 with r ≈ 2^129, k = 131
  → 2^60.81 (KN-FIND-aa2efc quotes 2^60.8090); K-163 with r ≈ 2^162, k = 163 →
  2^77.15 (record quotes 2^77.16). With k = 1 the ECC2K-130 column would read
  2^64.33.
- Product-law table (BRIEF §2): not recoverable exactly from KN-FIND-aa2efc's
  text ("required oracle speedup 2^-(70.19 + log2 m)" could not be reproduced);
  my naive balance 2·(m!·2^131)^{2/(m+1)} gives 2^89.00 / 67.79 / 55.23 / 46.97 /
  41.14 / 33.51 at m = 2/3/4/5/6/8 against the table's 89.25 / 68.58 / 56.40 /
  48.44 / 42.85 / 35.61 — within 0.25–2.1 bits, same ordering, same verdict
  (m ≤ 3 closed with a free oracle; m ≥ 4 open with a tiny per-attempt budget).
  Marked as a partial re-derivation in every review.
- Koblitz toy orders (Lucas recurrence from #E(F_2)): K0 `y^2+xy=x^3+1`:
  n = 17 → 4·137·239; 19 → 4·130873 (prime); 23 → 4·2095853 (prime); 31 →
  4·373·1439393; 37 → 4·149·230603167; 41 → 4·549756390943 (prime); 131 →
  4·680564733841876926932320129493409985129, which reproduces KN-FIND-aa2efc's r
  exactly. K1 `y^2+xy=x^3+x^2+1`: n = 17 → 2·65587 (prime), reproducing
  IDEA-20260915-8fe0ef's n = 17 cell.

**IDEA-20260922-2a3771**
- K-163 rho 2^77.15 (record 2^77.16): holds.
- ord_163(2) = 162 → no stable V: HOLD-S confirmed. Toy 29, 37 empty.
- Membership-indicator orbit constancy: re-derived via y = xz, z^2 + z = x + a + b/x^2,
  Tr(u^2) = Tr(u): holds, and true by construction on any orbit union.
- Orbit-system leaf count n·2^{ml}/(m!·n) = 2^{ml}/m!: no per-instance gain.

**IDEA-20260922-493606**
- 2^24/6 = 2,796,203; 2^32/24 = 178,956,971; /37 = 4,836,675 (ratio 1.7297);
  2^30/120 = 8,947,849; /29 = 308,547; 4·7 ≤ 37, 5·5 ≤ 29, 5·5 ≤ 23 false: all hold.
- ord_37(2) = 36, ord_29(2) = 28: HOLD-T confirmed; no 8- or 6-dimensional stable V.
- 96c4f3 (E): c = 1 − m/(2(m−1)) = 1/4, 1/3, 3/8 at m = 3, 4, 5: holds.
- log2 37 = 5.21, log2 29 = 4.86: hold.

**IDEA-20260922-845a77**
- 2·2401^2 = 11,529,602 = 2^23.46: holds (record's earlier 2^22.5 is its own
  inconsistency). Unordered-with-repetition table C(2402, 2) = 2,883,601 = 2^21.46.
- Attempts per relation at |F| = 2401, m = 4: 4·log2 2401 − log2 24 − 131 = −90.67
  → 2^90.7 (3f7a1c's 90.6 at d = 7; its ≥ 110 at d = 3 not re-derived).
- Pareto rows at m = 4, dim V = l: loop 2^{3l}/6 time / poly memory; 96c4f3 (D)
  2^l time / 2^{3l} memory; MITM 2^{2l} time / 2^{2l} memory — undominated.
- Balanced |V| on ECC2K-130 ≈ 2^{(131 + log2 m!)/(m+1)}: 2^27 at m = 4, 2^16 at
  m = 8; MITM probe |V|^{floor(m/2)} = 2^54 and 2^65 vs budgets 2^4.4 and 2^25.2.

**IDEA-20260922-faa8d2**
- 2^l (m−1)!/m2! = 192 at (4, 6), 1280 at (6, 6), 768 at (5, 6): hold.
  (m−1)!/m2! ≥ m−1 at m = 3..6 (2, 3, 12, 20): holds.
- c_amort* = 2^{−l} m2!/(m−1)! (= 2^{−l}/3 at m = 4); record's three versions:
  (C) 3·2^{−l} (inverted), predictions 2^{−l} (off by 3), Stage 3 m1!/(2^l (m−1)!)
  (right only where m1 = m2).
- Stage 1 anchors 2^18/6 = 43,691; 2^12/2 = 2,048; 2^12 = 4,096: hold.
- x(A+B) = λ^2 + λ + x_A + x_B + a, λ = (y_A + y_B)/(x_A + x_B): nonlinear in every
  coordinate; branching classification holds; Z/NZ analogue has b ≈ 2.

**IDEA-20260922-793fd8**
- V(β) for deterministic IC at ρ·μ_rho and exponential rho:
  V = μ_rho − (μ_rho/(1−β))(1 − e^{−ρ(1−β)/β}) ≤ 0 for all β ∈ (0,1) when ρ ≥ 1
  (reduces to t − 1 ≥ ln t at t = 1/β). Numeric grid check: max V = −0.005 over
  β ∈ {0.01..0.99}, ρ ∈ {1, 1.5, 2, 10, 100}; V(ρ = 0.5, β = 0.5) = +0.21 as expected.
- Pipeline total = sum of ~|V|/p i.i.d. attempt costs → concentrates for any finite
  mean; heavy lower tail needs per-attempt α ≤ 1.
- Free-oracle floor 2^68.58 / rho 2^60.81 = 2^7.77 = 218 > 100.

**IDEA-20260922-6237e5**
- 2^58.3/2^60.9 = 0.165; 60.9 − 25.27 = 35.63; 2^35.63 × 16 B = 2^39.63 B = 851 GB: hold.
- Normal basis: Tr(x) = Σ x_i (Tr(α) = 1) = HW(x) mod 2; with a = 0, P ∈ 2E iff
  Tr(x_P) = 0 (criterion carried by IDEA-20260922-1b16d7): the DP filter carries
  the E → E/2E quotient; subgroup x-coordinates have even weight (KN-LIT-661e97).
- Weight set is Frobenius-stable (squaring = cyclic shift). |W_34| ≤ 2^{131·H(34/131)}
  ≈ 2^108 (entropy bound; exact binomial sum unchecked).
- Toy m = 2 decomposition probability at n = 19, l = 7: 2^14/2^18 ≈ 1/16 (room for a ratio).

## Files written (this half)

- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-2a3771.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-493606.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-845a77.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-faa8d2.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-793fd8.yaml
- analysis/binstd-idea-review-20260926/reviews/IDEA-20260922-6237e5.yaml
- analysis/binstd-idea-review-20260926/reviews/TASK-20260926-843cf5-summary-b.md (this file)

No existing record was edited. No run, solver launch, or fabricated output. All
literature references in the reviewed records remain at the provenance the
records give them (recalled unless the record says retrieved); this half opened
no external source.
