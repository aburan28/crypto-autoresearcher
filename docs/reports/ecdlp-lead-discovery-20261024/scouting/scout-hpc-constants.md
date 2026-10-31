# Scout dossier, round 2: HPC constants against ECDLP bottlenecks B1-B7

Field: HPC constants (memory hierarchy, batched-inversion scheduling, SIMD field arithmetic, GF(2)/GF(p) linear algebra, bit-sliced arithmetic, rho step cost against IC relation cost at matched hardware).
Date: 2026-10-24. Round 1 is preserved unchanged at `scout/scout-hpc-constants.round1.md`.

**What kind of numbers appear here.** No repository file was edited and no experiment was run. Every number is one of four kinds:
- **[derived]**: arithmetic on recorded files, done this round by the scripts in `scout/hpc-r2/` (`derive_b3.py`, `derive_c1.py`, `derive_c4.py`, `derive_c5.py`; outputs `*.out` beside them);
- **[prediction]**: carries numbered heuristics (H1, H2, ... per candidate);
- **[quoted]**: from a lead row, study or source file, with its path;
- **[recalled]** or **[retrieved]**: a citation; retrieved ones were fetched this round.

## 0. What changed against round 1 (read first)

1. **Round-1 C2 (the callgrind Ir ledger) is killed as a duplicate. Its C-7 claim is retracted.**
   - ecbench already has `src/cryptanalysis/ecbench/callgrind.rs` (solve-window Ir).
   - It also has two repricing twins: `full_price.rs` (measured field_mul/sqr/inv units) and `wordram_price.rs` (host-independent CurveSmash budgets).
   - C-7 is a machine-protection load gate, not a measurement-validity gate. DEC-20261001-36e4fa R-2: "The executor card must carry an RSS watchdog at 8 GiB and the C-7 load gate for every computation, including smoke and probes."
   - Callgrind does not lift C-7 and does not build the EXP-ICEX-153c34 backend. No candidate here claims to unblock LEAD-ICE-charged-toy-ic-exponent-vs-rho.
2. **New C2: what is actually missing.** Every admitted unit charges an affine addition at 1, whatever its field work:
   - `GroupOps::gae()` = adds + doubles (ic_boundary.rs:188-190);
   - `full_price.rs`: "additions and doublings at one each, the convention every ecbench row uses";
   - the `*_full` and `*_wordram` twins exist only for Koblitz and binary arms (`Applies::KoblitzOnly` / `BinaryOnly`, methods.rs:508-553).

   The sealed lane study measured the consequence: "Each matched pair has a counted GAE ratio of exactly 1" (research/ecbench_rootfinding_lanes_20261013/REPORT.md; lanes-pair-check.json `field_ops_available: false` for all 72 pairs). C2 is the small extension that makes batching and x-only arithmetic visible. It carries a fairness guard (section 3, C2).
3. **C1 is repriced fairly.**
   - The matched rho is serial. The sealed `rho.negation` records serialize field_ops with invs ≈ adds, one inversion per step (e.g. muls 2998, sqrs 1447, invs 1343).
   - C1's gain is now stated twice:
     - against the IC baseline (walk lanes, both batched);
     - as the distance to a **lock-stepped batched rho in the same unit**.
   - The batched-lane comparator already exists (`TargetSource::WalkPrimeLanes{batched}`, widths 4/8/16, integrated and sealed). It is C1's control arm. The two-level batching is not "unimplemented".
4. **C1's yield metric is independent rank per priced cost, not hits.** The equal-prefix instrument (FIXED_PREFIX_FRESH protocol) already exists.
5. **C1's nearest closed lead is LEAD-RHO-batched-inversion-shared-pm (closed_known).** It is quoted below. C1 is an adaptation, and it contests that row's sentence "The remaining use of the free P-Q is the best-of lead."
6. **Round-1 C5 is replaced by a sharper instrument.** The dense MutantXL closure's 3·C²/8 memory comes from `ReducedBasis::absorb` (inherited_f4.rs), which copies the whole basis and stacks the full round of products beneath it. A rank-bounded, copy-free blocked absorb needs at most C²/8 plus one block.
   - It brings the blocked C1 cell from 217 GB projected to at most 79 GB, so the cell fits under the 184 GB cgroup cap of the same 256 GB RunPod pod class that capped.
   - The separator/Krylov certificate stays as a second arm, now resting on a retrieved theorem (Alon-Yuster 2013).
   - Round 1's w_eff formula is corrected.
7. **Every round-1 number I reuse was re-derived this round.** It now comes from my scripts (section 2). The rho finite-size fit changed slightly (β = 0.275, not 0.285).
8. **Overlaps with sibling scouts.**
   - The B6 generic-canonicaliser proof (Shoup on a restricted multiplier set) is `scout-query-communication.md` C4, so it is not repeated (K9).
   - C4's direction overlaps kill 6 of `scout-sat-xor-planted.md` ("Closing B4 by the product law alone ... predicted closed_dominated once conflicts are priced"). C4 adds the computed break-even from the sealed counters.

## 1. Field scan aimed at B1-B7

| ingredient (authors, year) | provenance | bottleneck | used in |
|:--|:--|:--|:--|
| x(X − Y) obtained cheaply beside x(X + Y): Galbraith, Wang, Zhang, "Computing Elliptic Curve Discrete Logarithms with Improved Baby-step Giant-step Algorithm", IACR ePrint 2015/605. The abstract says: "for any two elliptic curve points X and Y, we can efficiently get X−Y when we compute X+Y." The shared denominator x_Y − x_X is the elementary identity behind it. | retrieved (eprint.iacr.org/2015/605 abstract). The cost count I + 2M + 2S for both x-values is derived here from the affine formulas, not quoted. | B3 | C1 |
| Montgomery simultaneous inversion: 3(n−1)M + 1I for n inverses (Montgomery 1987; KR-RHO-cb1c58) | recalled; repo KR row | B3, B6 | C1, C2 |
| CurveSmash word-RAM budgets as already ported (wordram_price.rs: A = 128(s+1), M = k(2A+64)+A, I = 2k(M+64)+A, C = I+16M+32A+4096) | repo source, read | B3 | C2 fairness check |
| Distinguished-point parallel collision search, fixed set-up and DP tail amortising against sqrt(r) (van Oorschot-Wiener, J. Cryptology 12(1):1-28, 1999; KR-RHO-6239aa) | recalled this round (round 1 retrieved the bibliographic record) | B3 premise | C3 |
| CDCL conflict cost ≥ one clause-database traversal (Moskewicz et al., Chaff, DAC 2001) | recalled; only "a conflict costs more than about one cycle" is used | B4 | C4 |
| Dense GF(2) elimination by blocked PLE decomposition, the M4RI hierarchy (Albrecht, Bard, Pernet, "Efficient Dense Gaussian Elimination over the Finite Field with Two Elements", arXiv:1111.6549, 2011). An echelon basis never exceeds rank ≤ #columns rows. | retrieved (arXiv abstract) | B5 | C5 arm A |
| Nested dissection over any field: Alon, Yuster, "Matrix sparsification and nested dissection over arbitrary fields", J. ACM 60(4):25, 2013. Theorem 1.1: planar or bounded-genus G_A gives O(n^{ω/2}). The method extends LRT's O(n^{ωβ}) for a β-separator tree to any non-singular matrix over any field (Las Vegas over finite fields). Lipton, Rose, Tarjan, "Generalized nested dissection", SIAM J. Numer. Anal. 16(2):346-358, 1979. | AY retrieved (PDF text, abstract and Theorem 1.1); LRT bibliographic record retrieved | B5 | C5 arm B |
| Treewidth equals the minimum over chordal completions of (maximum clique − 1), and minimal chordal completions are fill-in patterns of Gaussian elimination | retrieved (en.wikipedia.org/wiki/Chordal_completion) | B5 | C5 arm B |
| Wiedemann 1986 and block Wiedemann (Coppersmith 1994): O(d_K · nnz) for Krylov dimension d_K | recalled (KN-LIT-017 in repo) | B5 | C5 arm B |

## 2. Derivations from recorded files (scripts in `scout/hpc-r2/`)

### 2.1 Table B prime gap, decomposed (derive_b3.py)

Sources: `docs/ic/leaderboard.json` best rows, and the matched-rho reprice ledger `research/ic_rho_reference_20260923/reprice/ic-boundary-ledger-round5-2026-09-22.json` (24 runs per size). The floor is sqrt(π/4) = 0.886.

| log2 r | IC S | rho S | IC/rho | IC/floor | rho/floor | relations share | factor-base share |
|--:|--:|--:|--:|--:|--:|--:|--:|
| 9.7 | 22.85 | 3.605 | 6.34 | 25.78 | 4.068 | 0.930 | 0.053 |
| 11.9 | 15.62 | 2.855 | 5.47 | 17.62 | 3.221 | 0.681 | 0.302 |
| 14.0 | 13.07 | 2.034 | 6.43 | 14.75 | 2.295 | 0.865 | 0.123 |
| 16.0 | 11.68 | 1.740 | 6.71 | 13.18 | 1.963 | 0.805 | 0.187 |
| 18.0 | 8.41 | 1.446 | 5.82 | 9.49 | 1.631 | 0.734 | 0.261 |
| 20.0 | 10.72 | 1.292 | 8.30 | 12.10 | 1.458 | 0.747 | 0.250 |
| 21.7 | 12.77 | 1.216 | 10.50 | 14.41 | 1.372 | 0.753 | 0.245 |
| 23.4 | 13.97 | 1.038 | 13.46 | 15.76 | 1.171 | 0.716 | 0.283 |

**From 11.9 to 23.4 bits [derived].**
- IC/rho changes ×2.460.
- rho/floor improves ×2.751.
- IC/floor changes ×0.894.

**From 18.0 to 23.4 bits [derived].**
- IC/rho changes ×2.312, of which rho contributes ×1.393 and IC/floor ×1.660.
- The slope of log2(IC/floor) per log2 r is **0.138**, from four points. Leave-one-out gives 0.11 to 0.17; the m = 2 two-term model is 1/6.

**Matched rho finite-size fit [derived; one instance per size; not a sealed bound].**
- rho/floor = 1 + c·N^(−β) with β = 0.275, log2 c = 4.32, residual sd 0.056 in log2.
- Implied rho/floor: 1.096 at 28 bits, 1.045 at 32, 1.010 at 40.

**Fixed-cost shares of the matched rho [derived].**
- Set-up plus start: 0.539 at 9.7 bits, 0.350 (11.9), 0.278 (14.0), 0.334 (16.0), 0.227 (18.0), 0.132 (20.0), 0.089 (21.7), 0.111 (23.4).
- Verification: 0.097 at 9.7 bits, falling to 0.009 at 23.4.
- walk/own-floor: 1.48, 1.85, 1.50, 1.22, 1.21, 1.24, 1.23, 1.03.

### 2.2 fp24 counters and a field-operation repricing (derive_c1.py)

**Source rows.** `docs/ic/runs/ic-boundary-ledger-round5-2026-09-22.json`, instance log2 r 23.38, recipe `mitm_m2_negfold_walk_balanced`, three repetitions. Recorded counts:

| phase | counts |
|:--|:--|
| factor base | 12,432 adds for 12,300 pair-table entries; 111 sqrt; 216 Legendre |
| relations | trials 26,008-32,642; walk steps 25,984-32,609; set-up of about 840 adds plus 1,400-1,435 doubles (16 jumps, 16 pool offsets); one lookup and one guard probe per trial |
| totals | 42,091-48,911 GAE |

**Pinned 24-bit ratios** (calibration.json, `prime/generated-24bit-10935329`):

| unit | ratio to one add |
|:--|--:|
| inversion | 0.800 |
| lookup | 0.0138 |
| sqrt | 4.673 |
| Legendre | 0.575 |

**Matched rho mean.** 3,432 GAE: walk 3,020, set-up plus start 380, verify 31.

**Unit.** One unbatched affine addition, so walk-serial reproduces the board exactly. Additions are priced by their field operations:
- batched element: 3M + I/n;
- batched add: batched inversion + 3M (λ, λ², y3);
- x-only pair: (batched inversion + 2M + 2S)/2 per target;
- side target: (batched inversion + 5M)/2 per target.

Heuristics H1-H6 are listed under C1. Results are [prediction]:

| unit (M = S) | sampler | IC S / walk-lanes | relations / walk-lanes | IC / batched rho, same unit | IC / as-built serial rho (unfair) |
|:--|:--|--:|--:|--:|--:|
| pinned, M 0.065, n 1024 | walk serial (board) | 2.71 | 2.46 | 33.9 | **13.46** (the board) |
| pinned, M 0.065, n 1024 | walk lanes | 1 | 1 | **12.53** | 4.97 |
| pinned, M 0.065, n 1024 | side target | 0.771 | 0.710 | 9.67 | 3.83 |
| pinned, M 0.065, n 1024 | **x-only pair (sumset)** | **0.674** | **0.586** | **8.45** | 3.35 |
| pinned, M 0.065, n 8 | walk lanes / pairset | 1 / 0.653 | 1 / 0.565 | 12.28 / 8.02 | 6.08 / 3.97 |
| pinned, M 0.040, n 1024 | walk lanes / pairset | 1 / 0.696 | 1 / 0.607 | 13.10 / 9.12 | 3.24 / 2.26 |
| pinned, M 0.080, n 1024 | walk lanes / pairset | 1 / 0.667 | 1 / 0.580 | 12.36 / 8.24 | 6.00 / 4.00 |
| wordram k = 24, n 1024 | walk lanes / pairset | 1 / 0.701 | 1 / 0.595 | 11.94 / 8.37 | **1.21 / 0.85** |

**Reading the table.**
- With both sides batched, walk-lanes IC/rho stays at the board's level, 11.9 to 13.1. Batching is symmetric and cancels.
- The asymmetric part (x-only, ± sharing an inversion) moves IC/rho to 8.0-9.1 in every unit tried.
- The last column is the trap that C2 guards against: priced in wordram against the as-built serial rho, batched IC reads 0.85 to 1.21 "× rho". That is a pure unit artifact.
- The factor-base phase alone falls from 13,075 GAE to about 3,580 once its existing shared-inversion, x-only builder is priced by field work. That IC-only asymmetry already sits in the source and is invisible in GAE.

### 2.3 SAT arm break-even (derive_c4.py)

Source: `research/ecbench_sat_pdp_20261009/count-qualified-main.resources.json`, session ECBS1hb55a1bdabf18, records_sha256 8f499a1d6f981644, n = 17 Koblitz, 40/40 verified per arm.

**Counted GAE per run.**
- ic-sat-xor: 874.08 (lower bound; `solver_conflicts_uncharged`), with 68,899.15 conflicts per run (2,755,966 conflicts in 749 calls).
- rho-strong: 1,023.76 (lower bound: canonicalisations, partition hashes and table operations unpriced).
- ic-mitm-frob: 4,372.35 (fully counted).
- ic-mitm: 99,181.41.

**Break-even [derived].**
- Against strong rho: c\* = 0.00217 GAE per conflict.
- Against mitm-frob: c\* = 0.0508 GAE.
- At rho-strong's L0 wall of 115.6 ns per GAE, c\* is 0.25 ns per conflict, about one cycle.

**Priced S/rho [derived].**

| price per conflict | S/rho |
|:--|--:|
| 0 GAE | 0.854 |
| 0.01 GAE | 1.53 |
| 0.1 GAE | 7.58 |
| 1 GAE | 68.2 |

The SAT target_PDP wall is 15.1 µs per conflict (L0, descriptive).

### 2.4 Closure memory and ECC2K-130 repricing (derive_c5.py)

**Cost model reproduced exactly.** The model is `descent_degree_cost_20260930.py`, with at least one target per relation. It gives:
- m = 4, D = 4: w = 1 → 2^68.43 (+7.62); w = 2 → 2^93.91 (+33.10);
- m = 3, D = 4: w = 1 → +21.46; w = 2 → +39.44.

**Repriced rows over rho [derived].**

| m = 4 row | degree 3 | degree 4 |
|:--|--:|--:|
| w = 1.5 | +9.77 | +18.12 |
| w = 2 | +19.84 | +33.10 |
| w = 2.2 | +24.50 | +39.09 |

**Memory model.** PROTOCOL.md of dreg_closure_m4l6_20261018: "peak RSS ≈ 3 × C(N,≤4)²/8 bytes", fitted from 5.8 GB at 124,314 columns. The protocol's projections (44, 59, 134, 173, 217, 357 GB) equal 3·C²/8 for cells A1, A2, B1, B2, C1, C2. The rank-bounded floor is C²/8 per cell, plus one 65,536-row block [derived]:

| cell | columns C | as-built 3·C²/8 | rank-bounded C²/8 + block |
|:--|--:|--:|--:|
| A1 (4,15,6) D4 | 341,055 | 44 GB | 14.5 + 2.8 |
| A2 | 395,011 | 59 GB | 19.5 + 3.2 |
| B1 | 597,619 | 134 GB | 44.6 + 4.9 |
| B2 | 679,121 | 173 GB | 57.7 + 5.6 |
| **C1 (3,19,7) D5** | **760,099** | **217 GB** | **72.2 + 6.2** |
| C2 (3,21,7) D5 | 974,982 | 357 GB | 118.8 + 8.0 |
| E8 (3,22,8) D4 (hybrid lead) | 179,447 | 12.1 GB (the lead's "about 10-12 GB") | 4.0 + 1.5 |

The measured A1 control held 25.8 GB resident, against a 14.7 GB C²/8 floor.

**C1 cell as a sparse system [derived].** 38 cubic equations, 821 multipliers, 31,198 XL rows, at most 6,018 terms per row, so nnz ≤ 1.88e8 (0.75 GB as 4-byte indices). The bit-packed dense XL matrix is 2.96 GB.

## 3. Candidates

### C1. x-only ± sumset target sampler for prime m = 2 IC (B3)

**Bottleneck.**
- B3: the relation phase is 68-93% of S in prime Table B (0.716 at fp24).
- Each trial is one walked addition R ← R + J and one probe. The walk keeps y only so that it can take the next walk step.

**Ingredient.**
- GWZ 2015/605 (retrieved abstract): X − Y comes cheaply with X + Y.
- Montgomery batching (KR-RHO-cb1c58).
- The new content is an asymmetry. IC targets are independent probes into an x-keyed, negation-folded table. They need neither y nor a successor. A rho walk needs y3 for the next slope.

**Mechanism.**
- *Precompute.* A_i = A_{i−1} + T (T = tG + uQ random) for i ≤ J, and B_k = B_{k−1} + G′ for k ≤ K, with J ≈ K ≈ sqrt(trials/2) ≈ 128 at fp24. That is about 256 batched adds plus 3 scalar multiplications.
- *Per pair (i, k).* One batched inversion of x_B − x_A. Then λ± = (y_B ∓ y_A)·inv (2M) and x± = λ±² − x_A − x_B (2S). Two probes and two guard probes.
- *On a hit* (about 70 per solve), recompute A_i ± B_k once for the sign, charged at 1 add.
- *Minimal-code co-arm.* The existing lane walk also emits the free x(R − J) as a side target (relations ×0.70-0.74 predicted). About 1/16 of side targets repeat earlier walk points and are dropped by the existing repeat guard.

**Pair and class.**
- Representation: R1, affine short-Weierstrass x-coordinate in Montgomery u64.
- Tracked object: the IC relation vector.
- Σ: translation by negation-folded factor-base pair sums.
- Trichotomy: **partial-action** (IC Class I). The sampler changes only the cost of target generation. The factor base is unchanged (smallest abscissae), so this candidate sits inside the scoped-out bounded-degree class of KN-OPEN-020 and claims no factor-base escape.

**SO codes, quoted, with the premise escaped.**
- **SO-TABLE**, LEAD-ICP-generic-table-decomposition: "[theorem] Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). ... Scope: any generic (enumeration/table) decomposition over F_p."
  - **Not escaped.** C1 is inside the scope and claims a constant only.
  - It also does not claim the foreclosed phrase "faster S_3 root finding or batched subtraction makes prime IC sub-rho".
- **SO-GEN**, LEAD-RHO-generic-sqrt-lower-bound: "[theorem] Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant ... Scope: all generic algorithms, any field, any r."
  - Not escaped: constant only.
- **Nearest closed lead (closed_known)**, LEAD-RHO-batched-inversion-shared-pm: "Known (KR-RHO-cb1c58, KR-RHO-fbd582) and reproduced: batch inversion proved correct in Lean (rho_assurance); GPU NIST W-sweep 1.52x/2.61x cumulative with by-reference inversion; plain-step cost falls with batch size (179 ns at 1024 walks on P-256). The remaining use of the free P-Q is the best-of lead."
  - Its forecloses include "shared inversion for P+Q and P-Q".
  - C1 is an **adaptation** of that row's mechanism to IC relation targets. It contests its last sentence: the IC target sampler is a second use of the free P−Q, outside rho.
- **SO-WALK**, LEAD-RHO-correlated-walks-shared-sums (top `--match` hit for the own phrasing): "[proof] With a shared index sequence every walk adds the same R_i at every step, so pairwise differences P_i - P_j are invariant and two walks can never meet unless they started equal; ... Scope: any parallel rho."
  - Escaped premise: "two walks can never meet". Sumset targets never need to meet each other. They need to hit a fixed table, and the expected hit count is a sum of uniform marginals.
- **SO-MULTI**, LEAD-ICB-multi-target-and-portfolio: "The multi-instance generic bound (L logarithms cost >~ sqrt(L r/|Aut|)) ..."
  - Escaped premise: "L logarithms". C1 solves one target Q; the grid only generates relation targets for that Q.

**Tier.** I (constant, end-to-end).

**Predicted gain [prediction].**
- Against the IC baseline (walk lanes, same unit, both batched): **IC S ×0.67** [0.60, 0.70], relation phase ×0.59 [0.51, 0.61].
- Distance to rho in the same unit with a lock-stepped batched rho: **IC/rho at fp24 8.5 [8.0, 9.1]**, against 12.5 [11.9, 13.1] for walk lanes and 13.46 on the GAE board.

Heuristics:
- H1. S = M, and M ∈ [0.04, 0.08] of an unbatched add, from 2M + S ≈ 1 − 0.80. The wordram budgets were tried as a second unit.
- H2. Batched inversion costs 3M + I/n per element (Montgomery).
- H3. A target probed by x needs no y; the sign is resolved only on a hit.
- H4. The expected hit count per target is unchanged (uniform marginals). The independent rank per probe is within ±5% of the walk's. This is to be measured, not assumed: sumset targets sharing A_i are correlated.
- H5. The reference rho runs n lock-stepped walks with batched inversion. That is admissible under KR-RHO-cb1c58 and required for a fair same-unit ratio.
- H6. The 32 jump and offset scalar-multiplication chains run lock-stepped.

**First discriminating step.**
- Add `TargetSource::PairSet` (and the side-target co-arm) to the prime lane collector.
- Run on the sealed 20-bit and fp24 instances, with the equal-prefix protocol of FIXED_PREFIX_FRESH:
  - same bases and fresh public targets;
  - ≥ 24 runs per arm;
  - arms: walk lanes (batch-8 and batch-16, existing), side target, pairset, and a lock-stepped batched rho.negation.
- Priced in C2's field-operation unit and in callgrind Ir (existing `ecbench/callgrind.rs`).
- Metric: **independent rank per priced cost**, then complete cold S.

**Outcomes to dispositions** (all on LEAD-ICP-prime-ic-constant-engineering):

| outcome | disposition |
|:--|:--|
| pairset/walk-lanes S upper CI < 0.85 at ≥ 2 sizes, rank per probe within ±5% | open_next_step; best_measured = the ratio, under the owner's IC-baseline criterion. The IC/batched-rho ratio is reported beside it as the distance remaining. |
| interval spans 1, or rank per probe falls more than 10% | closed_obstructed(measured) for the sampler item |
| gain visible in Ir but not in GAE | expected by construction. The record must carry the C2 unit before any board move. |

**Cost.**
- Implementation: 1-2 days, Rust, prime lanes only.
- Compute: under 2 CPU-hours, including callgrind.

**Self-kill risk: medium.**
- Bookkeeping (hash, guard, coordinate round trips) may dilute the ratio toward 0.8.
- A reviewer may read it as the foreclosed "batched inversion speeds up prime index calculus" (LEAD-ICP-prime-ic-constant-engineering). The delta is the IC-only x-only asymmetry, which batching alone does not give.

**--match phrasings and top hits.**
- Own: "x-only plus-minus sumset target sampler for prime-field index calculus: x(A_i + B_k) and x(A_i - B_k) from one shared inversion"
  - Top hits: LEAD-RHO-correlated-walks-shared-sums 18, LEAD-ICP-residual-partial-relations 13, LEAD-ICP-prime-ic-constant-engineering 12; frontier KR-RHO-cb1c58 10.
- Plain: "generate two index calculus targets per field inversion without computing y"
  - Top hits: KR-IC-5931ee 15, KR-IC-a4dd54 12.
- Closed-lead vocabulary: "shared inversion for P+Q and P-Q as index calculus targets; the remaining use of the free P-Q beyond the best-of lead"
  - Top hits: **LEAD-RHO-batched-inversion-shared-pm 27**, KR-RHO-fbd582 16.
- No row claims IC target sampling.

### C2. Field-operation pricing for the prime arms, with a batched matched rho (B3/B1 instrument)

**Bottleneck.** Three open items cannot be discriminated in any admitted unit:
1. **LEAD-ICP-prime-ic-constant-engineering's next step** is "run the unimplemented two-level target batching ... as a paired ecbench arm ... (~2x predicted); an interval spanning 1 closes the batching item."
   - In ecbench.gae that paired ratio is **identically 1 by construction**: GroupOps::gae() = adds + doubles, and the lane adders add 1 per step on both schedules.
   - This is measured in the sealed lanes study: 72/72 pairs exact, "counted GAE ratio of exactly 1".
   - The goal scores its primary results "in hardware-independent primary units with wall time and memory secondary" (GOAL-ICPERF-e6b6a4 goal.yaml).
   - So the predicted ~2x is **invisible in every counted unit the program admits**. It can show only in wall time (secondary, behind the L2 isolation gate) or in a field-op unit (this candidate).
   - If the paired arm were scored in ecbench.gae, the lead's own rule ("an interval spanning 1 closes the batching item") would close the item for a bookkeeping reason. This is a zero-compute correction to how the step must be scored.
2. **LEAD-ICE-rootfind-pairtable-oracle** is blocked on "native work unpriced". Its problem file names the missing capability: "Serialization and common-unit pricing of native field operations ..."
3. **C1** needs the same unit.

**Ingredient.**
- The FieldOps tally already exists (ic_boundary.rs FieldOps).
- `rho.negation` records already serialize it; `ic.pipeline` prime records write `field_ops: null`.
- The `*_full` and `*_wordram` repricing twins already exist, but only for Koblitz and binary arms.
- Montgomery batching (KR-RHO-cb1c58) supplies the per-element price.

**Mechanism.**
- (a) Serialize FieldOps from the prime IC pipeline (all phases, including the batched pair-table builder).
- (b) Add prime twins `ic.pipeline_full`/`_wordram` and `rho.negation_full`/`_wordram`, whose rule charges each addition by its counted field operations instead of at 1. A batched inversion is charged 3M + I/n; I, M and S come from `ecbench price-units` or from the wordram budgets.
- (c) Register the existing `prime_fast::rho_parallel` (src/cryptanalysis/prime_fast.rs:826) as the strongest-available matched reference in that unit, with its field operations tallied. It already has:
  - lock-step walkers with Montgomery `Fp64::batch_inv`;
  - a 1024-entry r-adding table;
  - the negation map, with a deterministic fruitless-2-cycle escape and abandonment of cycles of length ≥ 4.

  It is not yet an ecbench method, and it runs on `FastCurve`, not on a `CountedGroup`, so it does not tally field operations. Its walk shape (table, DP rule, set-up) differs from `rho_reference_walk`'s tuned shape, so an A/A against `rho.negation` in GAE is part of the step.
- (d) Guard: no field-op-priced IC/rho ratio is reported against the serial `rho.negation`.

**Pair and class.**
- An instrument, with no tracked object of its own (stated, not dropped).
- The arms it prices are partial-action (IC, Class I) and full-translation generic (rho, F1).

**SO codes.**
- **SO-TABLE** (LEAD-ICP-generic-table-decomposition, quoted under C1, "... Scope: any generic (enumeration/table) decomposition over F_p."): nothing is escaped. It is a ruler for oracles inside that scope.
- **SO-GEN** (quoted under C1): nothing is escaped.

**Tier.** I (instrument). Predicted gain: none by itself. It decides leads.

**Predictions [prediction, from section 2.2].**

| quantity | predicted |
|:--|:--|
| walk-lanes / walk-serial relation phase at fp24 | ×0.50 (n = 8) to ×0.41 (n = 1024), i.e. 2.0-2.5x. Consistent with the lead's "~2x". |
| factor-base phase in the field-op unit | ×0.27 of its GAE |
| IC-lanes against the as-built serial rho | 5-6 (pinned) or 1.2 (wordram). The guard exists for this artifact. |
| IC-lanes against batched rho | 12-13 (all units) |

Heuristics:
- H1. Same as C1's H1-H2.
- H2. The field-operation counts in the prime lane adders are exact. The source tallies muls, sqrs and invs per lane step, ic_boundary.rs ~3790-3830.

**First discriminating step (zero compute, then about 1 day).**
- File the GAE-invisibility derivation against LEAD-ICP-prime-ic-constant-engineering's next step, citing lanes-pair-check.json.
- Then implement (a) to (c) and replay the sealed lanes session's 24 targets. The replay must reproduce the GAE ratio of 1 and give a nonzero field-op ratio.

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| field-op ratio batch/serial upper CI < 0.8 | LEAD-ICP-prime-ic-constant-engineering: open_next_step, best_measured = the ratio; the batching item is measured, not closed |
| no change in field-op units either | closed_obstructed(measured) for the batching item |
| always | LEAD-ICE-rootfind-pairtable-oracle has its first named missing capability discharged (field ops serialized and priced). Its L2 isolation and independent-host gates remain. It stays open_blocked on those, not on "native work unpriced". |

**Cost.**
- Implementation: 2-4 days (serialization, two repricing rules, field-op tallies and ecbench registration for `rho_parallel`, plus its A/A). The 1-2 days in round 1 was optimistic.
- Compute: CPU-minutes.

**Self-kill risk: low-medium.**
- The program may decline a field-op unit for the board. The zero-compute correction (item 1 above) stands either way.

**--match phrasings and top hits.**
- Own: "price prime-field additions from serialized field operation counts with batched inversion in a full or wordram twin of rho.negation and the prime ic pipeline"
  - Top hits: LEAD-ICP-prime-ic-constant-engineering 17, KR-RHO-e7f98e 16, KR-RHO-cb1c58 14, LEAD-RHO-batched-inversion-shared-pm 14.
- Plain: "make batched inversion visible in the benchmark cost unit for prime index calculus and rho"
  - Top hits: KR-IC-a4dd54 19, LEAD-ICP-prime-ic-constant-engineering 16, LEAD-ICE-charged-toy-ic-exponent-vs-rho 15.
- Closed-lead vocabulary: "native work unpriced; serialization and common-unit pricing of native field operations; two-level target batching counted GAE ratio exactly 1"
  - Top hits: LEAD-RHO-native-step-cost 10, LEAD-ICP-prime-ic-constant-engineering 7.
- No row proposes field-op-priced additions for the prime arms.

### C3. The B3 gap is mostly the rho denominator: a times-floor decomposition with a falsifiable 28/32-bit projection (B3 premise)

**Bottleneck.**
- B3 as stated: "Table B gap to matched rho widens from 5.47x at log2 r 11.9 to 13.5x at 23.4".
- Also LEAD-RHO-matched-rho-calibration: "no prime medium-tier bound exists".

**Ingredient.** The van Oorschot-Wiener DP cost structure (recalled). The fixed set-up (jump table, starts) and verification amortise against sqrt(r), so as-built rho converges to its floor from above.

**Mechanism.** Section 2.1. The gap widening is more than fully explained by rho converging: rho/floor improves ×2.75 from 11.9 to 23.4 bits, while IC/floor falls ×0.894 over the same span. From 18 bits up, IC/floor grows as N^0.138 (leave-one-out 0.11-0.17). That sits at or below the m = 2 model's 1/6, so the measured growth is the model's and no extra deterioration shows.

**Pair and class.** A derivation and instrument with no tracked object.

**SO codes, quoted.**
- **SO-TABLE**, LEAD-ICP-generic-table-decomposition (quoted under C1). Its measured clause "Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4" is re-attributed.
  - No premise is escaped. The theorem part is confirmed: IC/floor grows at 0.11-0.17 per bit against the model's 1/6.

**Tier.** I (derivation).

**Predicted numbers, current recipe [prediction].**

| log2 r | IC/floor (fitted) | IC/floor (model, 1/6) | rho/floor | IC/rho |
|--:|--:|--:|--:|--:|
| 28 | 25.4 | 26.9 | 1.10 | 23-25 |
| 32 | 37.2 | 42.6 | 1.05 | 36-41 |

Heuristics:
- H1. The 18-23.4-bit slope is asymptotic.
- H2. rho's fixed share decays as N^(−0.275).
- H3. The recipe stays at its family optimum.
- H4 (caveat). Above about 36 bits the m = 2 pair table, (2/3)-power growth from 12,300 entries at fp24, outgrows a 32 MB last-level cache. Probes may then carry DRAM latency that the toy-size ns_per_lookup does not price.
  - `calibrate_lookup` does measure on a table of the instance's own size, which partly covers this.
  - Probes are 1-3% of S at toy sizes.

If C1 lands, multiply IC/rho by about 0.67.

**First discriminating step.** Seal fp26, fp28 and fp32 rows plus the prime medium-tier rho bounds specified by LEAD-RHO-matched-rho-calibration: ≥ 24 runs per size, replay certificates, section 5a band.

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| IC/floor at 32 bits in [30, 48] and rho/floor ≤ 1.15 | B3 is restated as "IC/floor grows as N^{~1/6}". LEAD-RHO-matched-rho-calibration gets its fitted R(N): closed_known for the fit form, best_measured = β. |
| IC/floor at 32 bits < 30 | an unmodelled sub-1/6 regime: open_next_step on LEAD-ICP-prime-ic-constant-engineering, best_measured = the slope |
| rho/floor > 1.3 at 32 bits | the matched-rho implementation is the outlier: reopen LEAD-RHO-negation-map-fruitless-cycles |

**Cost.** The derivation is done (zero). Confirmation takes CPU-hours.

**Self-kill risk.** Low as arithmetic. Medium on novelty: it overlaps LEAD-RHO-matched-rho-calibration's R(N) fit and adds the IC-side attribution and the projection.

**--match phrasings and top hits.**
- Own: "times-floor decomposition of the Table B prime gap into matched rho finite-size bias and IC growth"
  - Top hits: LEAD-RHO-matched-rho-calibration 29, LEAD-ICB-koblitz-rho-reference 17, KR-RHO-cd0049 16.
- Plain: "the prime index calculus gap to rho widens because the rho reference converges to its floor"
  - Top hits: KR-IC-a4dd54 19, KR-IC-5931ee 18, KR-RHO-1c2928 17, LEAD-RHO-matched-rho-calibration 16.
- Closed-lead vocabulary: "Table B gap to matched rho widens from 5.47x to 13.5x; rho finite-size bias law; medium-tier prime rho bound"
  - Top hits: **LEAD-RHO-matched-rho-calibration 50**, KR-RHO-cd0049 18.

### C4. The SAT/XOR point-decomposition oracle decided by the break-even conflict price (B4)

**Bottleneck.**
- B4: LEAD-ICE-sat-xor-pdp-oracle, best measured "native-XOR SAT S/rho 0.854 lower bound, conflicts unpriced, n = 17 Koblitz".
- Its discriminates rule: "above 1 with conflicts tracking 2^(ml)/m! confirms SAT is enumeration at a constant and closes the lead as dominated by the pair table."

**Ingredient.** A CDCL conflict costs more than about one cycle (Chaff 2001, recalled). That trivial bound is all that is used.

**Mechanism.** Section 2.3.
- Break-even c\* is 0.00217 GAE against strong rho, about 0.25 ns at that arm's L0 wall, and 0.0508 GAE (about 6 ns) against Frobenius-MITM.
- The measured L0 price is 15.1 µs per conflict.

**Pair and class.**
- Representation: R1, F_2 coordinates of the Weil-descended chain as CNF-XOR.
- Σ: translation by factor-base elements.
- Trichotomy: **partial-action** (IC Class I). A decision instrument.

**SO codes, quoted, with the premise escaped.**
- **SO-TABLE**, LEAD-ICB-generic-table-oracle: "[theorem] Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply ... Scope: all binary and Koblitz curves, one target, setup charged."
  - Escaped premise: "built from group operations and membership tests". The SAT solver reads the descended coordinates, which is why the lead is open.
- LEAD-ICE-generic-oracle-arity-cost-floor: "... Scope: oracles that do not read curve coordinates algebraically ..."
  - Escaped: SAT does read them.
- Caught by LEAD-ICB-decomposition-encoding-and-sat: "[measured] Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5), while beating rho needs alpha < m/2 - 1; ..."
  - This supplies the second clause of the lead's rule.

**Tier.** I (decision). Predicted gain: none.
- Under the floor "a conflict costs ≥ 10 ns" (H1: about 40 cycles at about 4 GHz), priced S/rho ≥ 6.6 [prediction].
- H2. Even if rho's unpriced natives doubled its S, c\* ≤ 0.017 GAE (about 2 ns), still about 10^4 below the measured 15.1 µs.

**First discriminating step.**
- Zero compute: file the derivation against the sealed session (records_sha256 8f499a1d6f981644...).
- Optional confirmation: one ecbench callgrind run of the SAT arm for Ir per conflict against Ir per GAE of strong rho, using the existing `callgrind.rs`.

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| priced S/rho > 1 at the 0.1 band point (derived 7.58) and alpha ~ m (cited) | **closed_dominated** by the pair table and strong rho, by the lead's own rule |
| only a measured conflict price < 0.0022 GAE could reopen it | physically excluded by H1. It would read open_next_step with best_measured = the priced ratio. |

**Cost.** Zero, or 1 CPU-hour for the Ir confirmation.

**Self-kill risk.** Very low. Overlap: sibling scout `scout-sat-xor-planted.md` kill 6 predicts the same direction without the computed price.

**--match phrasings and top hits.**
- Own: "break-even price per SAT conflict from sealed counters decides the native-XOR SAT point-decomposition oracle"
  - Top hit: LEAD-ICE-sat-xor-pdp-oracle 15.
- Plain: "SAT conflicts cost too much for the SAT decomposition oracle to beat rho"
  - Top hits: LEAD-ICE-generic-oracle-arity-cost-floor 19, LEAD-ICE-rootfind-pairtable-oracle 15, LEAD-ICB-decomposition-encoding-and-sat 13.
- Closed-lead vocabulary: "per-attempt UNSAT cost 2^{alpha l} with alpha ~ m; SAT or XOR solver for point decomposition beats rho; conflicts unpriced"
  - Top hits: LEAD-ICB-decomposition-encoding-and-sat 31, KR-IC-5765d2 25, LEAD-ICE-sat-xor-pdp-oracle 22.

### C5. Rank-bounded, copy-free closure memory, plus a separator/Krylov certificate on the same matrices (B5, binary half of B4)

**Bottleneck.**
- LEAD-ICE-descent-closure-degree-at-scale is open_blocked: "memory (C1 capped at 169 GB of 184 GB; projection 217 GB)". The next step asks for a host with ≥ 250 GB "(or a sparse closure)".
- B5's LEAD-ICE-hybrid-guess-determine-l7 prices its stretch cell E8 at "about 10-12 GB ... per branch".
- The three leads that carry the +7.62 (w = 1) row:
  - LEAD-ICB-prime-degree-algebraic-decomposition;
  - LEAD-ICE-descent-closure-degree-at-scale;
  - LEAD-ICE-hybrid-guess-determine-l7.
- The note that produced the row says "the `w = 2` rows are the ones the measured closure tracks".

**Ingredient.**
- Arm A: an echelon basis over a field never holds more than rank ≤ C rows, and blocked PLE/M4RI elimination (Albrecht-Bard-Pernet 2011, retrieved) reduces a stream of new rows against it one block at a time.
- Arm B:
  - nested dissection over any field, O(n^{ωβ}) for a β-separator tree (Alon-Yuster 2013, retrieved);
  - treewidth equals the minimum over chordal completions of (maximum clique − 1), so every elimination order's fill holds a (tw+1)-clique (retrieved);
  - Krylov cost d_K · nnz (Wiedemann 1986 and Coppersmith 1994, recalled).

**Mechanism.**
- **Arm A: where the 3·C²/8 comes from.** `ReducedBasis::absorb` (src/cryptanalysis/inherited_f4.rs) does three things each closure round:
  - materialises every basis row into a fresh full-width copy (`self.rows.iter().map(... full ...)`);
  - appends the round's entire product batch (`matrix.extend(batch)`);
  - runs `rref_f2_counted` on the stack.

  Peak memory is therefore basis + copy + batch, about 3·C²/8 (the protocol's own fitted law). `close()` adds to this: it holds the whole round's `products` (monomial lists, one u64 per term) and the whole `packed` vector before `absorb` is even called. For dense falls at 760k columns the monomial-list form can exceed the bit-packed form.

  The fix has to stream both stages:
  - generate falls × monomials one block of B products at a time;
  - pack the block and reduce it against the basis in place, using M4RI Gray tables over the pivot columns;
  - echelonise the residue;
  - append its pivots;
  - free the block before generating the next;
  - never copy the basis.

  Peak becomes rank·C/8 + B·C/8 (+ one block's monomial lists) ≤ C²/8 + O(B·C). The saturated row space, the refutation verdict and the fall set are unchanged: same span, same column order.
- **Arm B.** Dump each closure's sparsity pattern, full and block-local (locality-2), on cells that already run. Measure:
  - the top nested-dissection separator s(C) with ndmetis, and fit s ~ C^β;
  - min-degree and minor-min-width treewidth bounds;
  - one GF(2) block-Wiedemann Krylov dimension d_K ~ C^κ.

  Then w_eff = max(1, min(ω·β, 1 + κ)). This corrects round 1's "1 + max(κ, 2σ − 1)".
  - w < 2 needs β < 2/ω (about 0.71 at Strassen ω = 2.81) or κ < 1.
  - Caveat H3: Alon-Yuster needs a square non-singular system. The refutation is "1 ∈ row space" of a rectangular matrix, so squaring it up must keep the separator structure.

**Pair and class.**
- Representation: R1, Boolean ANF of the Weil-descended chained S_3.
- Σ: translation by factor-base elements; the oracle is a bounded-degree row-space closure.
- Trichotomy: **partial-action** (IC Class I). An instrument.

**SO codes, quoted, with the premise escaped.**
- **SO-TABLE**, LEAD-ICB-generic-table-oracle (quoted under C4).
  - Escaped premise: "built from group operations and membership tests". The closure reads coordinates algebraically.
- LEAD-ICP-icperf-writability-boundary: "[cost_model] At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by ... +40.8 (ECC2K-130) ... the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]."
  - Escaped premise: "unchained descended ANF". The cells are chained.
- LEAD-ICE-boolean-f4-f5-f6-engines (closed_dominated) forecloses "M4RI GF(2) elimination speedup for PDP". Its statement: "Dominated by LEAD-ICE-rootfind-pairtable-oracle on Koblitz and random-binary curves n <= 31, m in {2,3,4} ..."
  - Escaped premise: the engine is used as an IC oracle at n ≤ 31. C5 claims no oracle speedup; it is a memory change for a degree measurement at scale.
- LEAD-ICB-orbit-linear-algebra (exhausted_at_scale): "Linear algebra is 0.0-2.7% of S in every Table A-C row ..."
  - Escaped premise: that is the relation matrix, not the per-decomposition closure.

**Tier.** I. An instrument for an exponent question (whether the closure degree stays constant, and w); hardware moves no exponent here.

**Predicted outcome [prediction].**
- Arm A, peak RSS:

  | cell | predicted peak | against |
  |:--|:--|:--|
  | C1 (3,19,7) D5 | ≤ 79 GB (H1) | 217 GB projected, 169 GB reached at the cap |
  | B2 | ≤ 64 GB | 173 GB |
  | C2 | ≤ 127 GB | 357 GB |
  | E8 | ≤ 5.5 GB | 12 GB |

  All of these fit under the 184 GB cgroup cap of the pod class that capped (C2 at ≤ 127 GB too, where the protocol required ≥ 420 GB). Wall time is within 0.5-2x of the dense closure's (H2).
- Arm B: β ≥ 0.8 and κ ≥ 0.8 on the full matrices (H4), so w_eff ≥ 2. ECC2K-130 m = 4 is then +19.8 (D = 3) to +33.1 (D = 4) bits over rho [derived conditional]. At w ≥ 1.5 every D ≥ 3 row is ≥ +9.8.

Heuristics:
- H1. The rank stays ≤ C (exact). With product generation streamed per block (not per round), one 65,536-row block (packed plus its monomial lists) plus overhead stays under 10% of C²/8.
- H2. Word operations per absorbed row are unchanged. Only the copy is removed.
- H3. Squaring up a rectangular refutation system preserves the separator structure.
- H4. Each descended S_3 row couples all l + l + n bits of its three points, so the column graph has no o(C) balanced separator.

**First discriminating step.**
- Arm A: implement block-streamed product generation and the copy-free absorb in inherited_f4.rs (1-3 days).
- Check it against the existing `sparse_closure_matches_the_dense_closure` and `closure_scan_*` tests (same verdicts).
- Local go/no-go, before any pod rental:
  - A1 (4,15,6) D4 must peak at ≤ about 17 GB (C²/8 + block), against the 25.8 GB measured as built;
  - E8 (3,22,8) D4 must peak at ≤ about 5.5 GB.
- Only if both pass, run the frozen C1 cell on the same pod class that capped: a RunPod memory-optimised CPU pod, 256 GB, 184 GB cgroup cap. Use the existing protocol, its memory cap and the C-7 load gate.
- Arm B: METIS, treewidth and Krylov scripts on the A1/(4,5)/m3 dumps (hours).

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| C1 refutes at degree 5 on ≥ 2 unsat draws, control not refuted | LEAD-ICE-descent-closure-degree-at-scale **open_blocked → open_next_step**, best_measured "degree 5 at (3,7)". This confirms the +10.32 bracket, per its discriminates clause. |
| C1 needs degree ≥ 6 | the degree grows with l: **closed_obstructed(measured)**, per its own rule |
| arm A peak > 150 GB | H1/H2 refuted: record the measured peak and keep the host blocker |
| arm B β ≥ 0.8 and κ ≥ 0.8 | **closed_obstructed(cost_model)** for the ECC2K-130 pricing consequence of LEAD-ICB-prime-degree-algebraic-decomposition and LEAD-ICE-hybrid-guess-determine-l7. Their decision rows reprice at w = 2 (+19.8 / +33.1), so no degree-≥ 3 outcome comes within 2^19 of rho. |
| arm B β < 0.65 on the block-local family | open_next_step for a nested-dissection closure (w_eff = ωβ); best_measured = β |

**Cost.**
- Implementation: 1-3 days for arm A, 1 day for arm B.
- Compute: minutes locally for the A1/E8 go/no-go; about 1-2 h on one 256 GB pod (184 GB cgroup) for C1; hours for arm B.

**Self-kill risk: medium.**
- The absorb rewrite may lose the Four Russians speed that the stacked rref gets (H2).
- H3 or H4 may fail, which would be a positive outcome for the sparse-closure path.

**--match phrasings and top hits.**
- Own: "rank-bounded streaming echelon closure holds at most rank times columns bits, plus separator tree and Krylov dimension certificate of the Macaulay closure"
  - Top hits: LEAD-ICE-chained-semaev-dreg-vs-semiregular 7, KR-IC-e847d1 6, LEAD-ICE-descent-closure-degree-at-scale 6.
- Plain: "run the degree-5 descended Semaev closure in under 72 GB instead of 217 GB and measure whether a sparse closure can avoid quadratic cost"
  - Top hits: LEAD-ICE-descent-closure-degree-at-scale 9, LEAD-ICE-semaev-chain-cost-model 9.
- Closed-lead vocabulary: "memory column for block Wiedemann at the cap locus; descended ANF exceeds the per-decomposition rho budget; closure degree stays 4; 250 GB host or a sparse closure"
  - Top hits: LEAD-ICP-icperf-writability-boundary 33, LEAD-ICB-orbit-linear-algebra 18, LEAD-ICE-descent-closure-degree-at-scale 18.
- No ledger record mentions a rank-bounded or copy-free closure (index grep: "rank-bounded" 0, "sparse closure" 0, "out-of-core" 0). IDEA-20260828-770aa4 concerns Python frozenset overhead in a different prepare phase.

## 4. Killed candidates (own weak ones first)

- **K14. Round-1 C2, the callgrind Ir ledger.** Duplicate of `ecbench/callgrind.rs` plus the `*_full`/`*_wordram` twins. Its claim to remove the C-7 dependency was wrong: C-7 is a machine-protection load gate (DEC-20261001-36e4fa R-2). Replaced by the new C2.
- **K15. Round-1 C1's fairness.** Pricing pairset IC in Ir against GAE-priced (serial) rho. In wordram that comparison reads 0.85 × rho, a unit artifact. Replaced by the same-unit batched-rho comparison.
- **K16. Round-1 C5 as stated.** Its w_eff formula was wrong, and its "+29 bits block-local" row was not re-derivable from data I could read. Replaced by C5 arms A and B.
- **K1. An "arithmetic floor" proof that IC/rho ≥ κ·N^{1/6} closes LEAD-ICP-prime-ic-constant-engineering.** It restates SO-TABLE's "m = 2 >= 3 (pT_dec)^{2/3}". It also cannot close a lead whose mechanism credits "each verified gain ... even though the exponent is fixed".
- **K2. Cache-blocked or radix-partitioned pair table, xor/binary-fuse probe filters.** `build_negation_folded_prime_blocked` and `PackedPairTable` already exist. Lookups are 0.012-0.017 GAE (calibration.json), 1-3% of S.
- **K3. Symmetric engineering** (Montgomery u64, SIMD/IFMA, tensor-core multiplication, batched walk inversion on both sides). It cancels in IC/rho: section 2.2's walk-lanes row stays at 12-13 in every unit. Foreclosed: "Montgomery native arithmetic for the relation search".
- **K4. GPU root-finding oracle as a ratio lever** (LEAD-ICE-gpu-rootfind-oracle). Rho steps are register arithmetic, while probes are random gathers. Once the table exceeds shared memory (about 25 bits), GPU IC/rho ≥ CPU IC/rho is predicted. Not a lever.
- **K5. Wiener full cost / AT metric.** At m = 2 balance, memory ≈ time ≈ N^{2/3}, so the metric only penalises IC. IDEA-20260809-bf5139 owns AT pricing.
- **K6. Mesh linear algebra or block Wiedemann for the relation matrix.** LA is 0.0-0.4% of S in prime Table B (fp24 LA 12-16 GAE of 42,000-49,000).
- **K7. Faster square roots for large 2-adic valuation (Sarkar 2020).** ns_per_sqrt is 4.67 at fp24, but 111 sqrt are about 1.1% of S.
- **K8. EC tag tracing** (LEAD-RHO-cheaper-step-primitives, prime branch). The next index must be a function of the next point. Any non-constant projectively invariant tag needs a division or a character, and a Legendre symbol has no Montgomery-trick batching, so it costs more than the batched step's 3M inversion share. The skippable work is zero. This is a prediction for that lead (closed_obstructed(cost_model) on the prime branch), not a candidate.
- **K9. Shoup bound for generic canonicalisers** (LEAD-RHO-non-automorphism-equivalence). Covered by `scout-query-communication.md` C4; not duplicated.
- **K10. GF(2) block-Wiedemann consistency test for the dreg cells.** Duplicate of IDEA-20261018-1aff90; its Krylov part is folded into C5 arm B.
- **K11. F4 engineering or an ω-rescaling argument for B2.** LEAD-ICE-prime-field-semaev-solving-degree is closed_known.
  - An ω-rescaling cannot close it either way without the column-count exponent: at ω_eff = 3, one touch per column would read 0.797/3 = 0.27 < 0.30.
  - The membership-degree-B floor that does close it is SO-ALGFB / KR-IC-5931ee (also `scout-sat-xor-planted.md` kill 5).
- **K12. ECC2K-130 GPU or FPGA throughput** (B6). `ecc2k130/ROOFLINE.md`: "The busiest unit is the ALU (logic) pipe, at 91% of its measured peak." So at most about 1.1x of kernel headroom remains. Owned by LEAD-RHO-ecc2k130-gpu-fpga-throughput.
- **K13. Medium-tier probe memory wall and sort-merge batched probing** (Balkesen et al. 2013 radix join, recalled). Not decisive.
  - Probes are independent of the walk's dependency chain, so out-of-order overlap hides much of the latency.
  - `calibrate_lookup` measures on a table of the instance's size.
  - It becomes relevant only above about 36 bits. Kept as C3's caveat H4.
- **K17. Side-target walk as a stand-alone candidate.** Dominated by pairset (relations ×0.70-0.74 against ×0.57-0.61). Kept only as C1's minimal-code co-arm.

## 5. Citations and provenance

| citation | provenance | used in |
|:--|:--|:--|
| Galbraith, Wang, Zhang, ePrint 2015/605 | retrieved (abstract, eprint.iacr.org/2015/605) | C1 |
| Montgomery simultaneous inversion (1987), KR-RHO-cb1c58 | recalled; repo KR | C1, C2 |
| CurveSmash word-RAM budgets as ported in `ecbench/wordram_price.rs` | repo source, read | C2 |
| van Oorschot, Wiener, J. Cryptology 12(1):1-28, 1999, KR-RHO-6239aa | recalled (round 1 retrieved) | C3 |
| Moskewicz et al., Chaff, DAC 2001 | recalled | C4 (only "≥ about 1 cycle per conflict") |
| Sealed session ECBS1hb55a1bdabf18 resources | repo, read (load-bearing for C4) | C4 |
| Albrecht, Bard, Pernet, arXiv:1111.6549 (2011) | retrieved (abstract) | C5 A |
| Alon, Yuster, J. ACM 60(4):25 (2013), Theorem 1.1 | retrieved (PDF text: abstract, Theorem 1.1) | C5 B |
| Lipton, Rose, Tarjan, SIAM J. Numer. Anal. 16(2):346-358 (1979), DOI 10.1137/0716027 | retrieved (bibliographic) | C5 B |
| Treewidth via chordal completion | retrieved (Wikipedia, "Chordal completion") | C5 B |
| Wiedemann 1986; Coppersmith 1994 | recalled | C5 B |
| Balkesen et al., ICDE 2013 (radix join) | recalled | K13 only |

## 6. Searched, nothing usable for B1-B7

- **B1, the non-enumerative oracle backend (EXP-ICEX-153c34).** No HPC lever. Its blockers are an unbuilt G1/O5 backend and the C-7 machine-protection gate. Its own design prior is that membership "hits the same floor as enumeration (1,041-8,438x the threshold)".
- **B2, cache-oblivious GF(p) LU and F4 linear algebra.** Constants on a closed_known exponent gap.
- **B6, GPU kernel throughput.** Roofline-bounded at 91% of ALU peak (ROOFLINE.md).
- **B6, tensor-core/IFMA multiprecision and energy-per-operation models.** Symmetric between IC and rho; the only asymmetry they expose is memory access, which penalises IC.
- **B6, non-automorphism canonicaliser cost.** Covered by a sibling scout.
- **B7, isogeny-step cost (√élu, Bernstein-De Feo-Leroux-Smith 2020) for the Teske F_{p^6} trapdoor.** A constant; it does not decide where the weak curve sits.
- **B7, Miller-cocycle non-homomorphic transfer.** No HPC content.
