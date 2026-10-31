# Scout dossier: HPC constants against ECDLP bottlenecks B1-B7

Field: HPC constants. Scope: memory hierarchy, GPU/FPGA throughput, batched-inversion scheduling, SIMD field arithmetic, cache-oblivious and sparse linear algebra over GF(2)/GF(p), bit-sliced binary arithmetic, and the cost of a rho step against an IC relation at matched hardware.
Date: 2026-10-24. Scout output only: no repository file was edited, and no experiment was run. Every number below is labelled as one of three kinds:
- derived from counters already recorded in the repository (arithmetic I did here, not a new measurement);
- a prediction (heuristics numbered H1, H2, ... per candidate);
- quoted from a lead row or study.

Inputs read:
- ATLAS.md, all families
- KRMAP.md
- LEADERBOARD.md tables A-C, phase shares, and leaderboard.json
- FRONTIER.md, prime toy domain
- object-frame-ideation.md, sections 1-3
- idea-generator.md, sections "Search heuristics" and "Obstructions as generative material"
- target-result-profile.md, parts A1-A2
- lead YAMLs for every lead quoted here
- docs/ic/calibration.json
- docs/ic/runs/ic-boundary-ledger-round5-2026-09-22.json, the native counters behind Table B
- research/ecbench_sat_pdp_20261009/count-qualified-main.resources.json
- research/k_conversion_20261018/README.md
- research/notes/ecc2k130/RESEARCH_ECC2K130_DESCENT_DEGREE.md, sections 2 and 6
- problems/rootfinding-complete-cost-calibration.md
- src/cryptanalysis/ic_boundary.rs: target walk, lane adder, pair-table builders

Dedup sources: the ledger index (grep), `tools/lead_atlas.py --match`, and `tools/build_frontier_map.py --match`. Raw match logs are in the same directory: `hpc-match-log.txt` and `hpc-frontier-match-log.txt`.

## 0. Bottom line (read this first)

1. **No HPC ingredient moves an exponent on B1-B3.**
   - Every prime-field oracle in Table B is inside SO-TABLE.
   - Hardware levers are symmetric between IC and rho (field multiplication, SIMD, GPU arithmetic) and cancel in the ratio, with one exception: the asymmetry in candidate C1.
   - The honest HPC contribution to prime-field IC is therefore:
     - one constant gain to the IC baseline (C1, about 1.8x predicted in Ir), which the owner's success criterion for LEAD-ICP-prime-ic-constant-engineering counts;
     - one instrument that unblocks two blocked leads (C2);
     - one correction to the premise of the named bottleneck B3 (C3).
2. **The B3 premise is mostly a denominator effect.**
   - "Table B gap widens from 5.47x to 13.5x" (11.9 to 23.4 bits) is more than fully explained by the rho reference converging to its floor: rho/floor goes 3.22 to 1.17, a factor of 2.75.
   - Over the same range IC/floor *fell*, by a factor of 0.89.
   - From 18 bits up, IC/floor grows as N^0.138 (derived), close to the N^(1/6) of the m = 2 two-term model.
3. **One binary-side lead can be decided with no new compute; a second can be decided cheaply.**
   - **C4, SAT/XOR oracle (B4), zero compute.**
     - On the recorded counters, the break-even price of a conflict is 0.0022 GAE against strong rho (about one CPU cycle).
     - Against the dominating Frobenius-MITM arm in the same session it is 0.051 GAE (about 6 ns).
     - At the lead's own 0.1 GAE band point, priced S/rho is 7.6. The lead closes as dominated.
   - **C5, the algebraic ECC2K-130 m = 4 route (B5), a cheap test.**
     - The +7.62-bit row that keeps three leads open charges w = 1 (one touch per Macaulay column).
     - The descent-degree note itself measures closure work growing as about C^2.2.
     - No known linear algebra reaches w < 2 on matrices without small separators. **If w ≥ 2 holds at scale,** the m = 4 rows are about +20 bits (closure degree 3) to +33.1 bits (degree 4) over rho.
     - In that case, no outcome of the memory-blocked degree runs (degree ≥ 3, the measured range) changes the ECC2K-130 verdict.
     - Whether w ≥ 2 holds at scale is exactly what C5's separator and Krylov certificate tests on cells that already run. It is not a zero-compute claim.

## 1. Field scan: what HPC knows, aimed at the named bottlenecks

| HPC ingredient (author, year) | provenance | bottleneck aimed at | verdict |
|:--|:--|:--|:--|
| x(P-Q) nearly free beside x(P+Q) with one shared inversion (Galbraith-Wang-Zhang, ePrint 2015/605; KR-RHO-fbd582). The slides price the joint P1+P2 and P1-P2 at I + 4M + 2S. | retrieved (ePrint 2015/605 landing page; Galbraith Ascona slides) | B3 target generation | **C1** (adaptation; the asymmetry is new) |
| Montgomery simultaneous inversion (Montgomery 1987; KR-RHO-cb1c58) | recalled; KR row | B3 | component of C1. Symmetric between IC and rho on its own, so killed as a stand-alone lever (K3). |
| Deterministic instruction counting plus cache simulation as a contention-free cost unit (Valgrind/Callgrind: Nethercote-Seward, PLDI 2007; already used here in research/k_conversion_20261018 and LEAD-RHO-native-step-cost) | retrieved (PLDI 2007 bibliographic record; valgrind.org publications page) | B1/B3 blocked pricing | **C2** |
| Finite-size bias of distinguished-point rho: fixed set-up plus DP tail (van Oorschot-Wiener, J. Cryptology 12(1):1-28, 1999; KR-RHO-6239aa; Bos-Costello-Miele constants, KR-RHO-825bca) | retrieved (bibliographic record and abstract) | B3 premise, B6 | **C3** |
| CDCL cost per conflict ≥ one clause-database traversal (Moskewicz et al., Chaff, DAC 2001: watched literals) | recalled | B4 | **C4** (needs only "a conflict costs more than one cycle") |
| Treewidth as min over elimination orderings of (max clique in filled graph) - 1, so every ordering's fill contains a (tw+1)-clique; separator-based nested dissection (George 1973; Lipton-Rose-Tarjan, "Generalized nested dissection", SIAM J. Numer. Anal. 16(2):346-358, 1979) | treewidth/chordal-completion characterization retrieved (Wikipedia "Chordal completion"; arXiv 1411.1745). LRT bibliographic data retrieved; a claimed LRT *expander lower bound* was **not** found, so it is not used. | B5 closure cost exponent w | **C5** |
| Wiedemann 1986 / block Wiedemann (Coppersmith 1994): sparse solve in O(C · nnz) and memory O(nnz) | recalled (KN-LIT-017 in repo) | B5 | component of C5. A GF(2) BW consistency test duplicates IDEA-20261018-1aff90 (K10). |
| Radix-partitioned / cache-blocked hash build and probe; xor and binary-fuse filters (Graf-Lemire 2020/2022) | recalled | B3 probes | killed (K2): the blocked/packed pair table already exists in source, and lookups price at 0.012-0.017 GAE |
| Wiener full cost (J. Cryptology 2004); Bernstein AT metric | recalled | B1/B3 | killed (K5): no exponent change at the m = 2 balance |
| Mesh linear algebra (Bernstein 2001) | recalled | B3 | killed (K6): linear algebra is ≤ 0.4% of S in prime Table B |
| Square roots faster than Tonelli-Shanks for large 2-adic valuation (Sarkar 2020) | recalled | B3 factor base | killed (K7): under 2% of S |
| Tag tracing (Cheon-Hong-Kim 2008/2012) on EC | recalled; KR-RHO-38be82 | B6 | killed (K8): the tag needs the full slope λ |
| Bit-sliced ECC2K-130 GPU kernels at 15.884 B updates/s (LEAD-RHO-ecc2k130-gpu-fpga-throughput) | repo | B6 | context only (K12): 2^60.9 / 1.5884e10 ≈ 1.3e8 s ≈ 4.2 RTX PRO 6000-years, derived. Already owned by the pool campaign. |

## 2. Data I derived from recorded counters (not new measurements)

### 2.1 What a Table B "trial" costs today (fp24, `icv1-fp24-t1577`)

Source: round-5 boundary ledger, recipe `mitm_m2_negfold_walk_balanced`.

**Recipe shape.** 111 abscissae (222 base points). Trials 26,008-32,642 across three repetitions. Relations 64-74.

**What the counters show.**
- *Relations phase.* adds ≈ trials, plus about 1,400 doubles and 66 scalar mults (walk set-up). Lookups and guard probes, one each per trial. `inversions: 0` counted natively.
- *Factor-base phase.* 12,432 adds for 12,300 pair-table entries, i.e. one GAE per signed sum. The source (`build_negation_folded_prime_batch`/`_blocked`) already shares one inversion per signed pair and keys on x only. That is why "blocked vs batched vs scalar pair-table build; same additions, S unchanged" (crypto `research/ic_oracle_setup_blocked_20261020`).

**Wall, L0, descriptive only, same file.**

| log2 r | rho ns per GAE | pair-table ns per entry | relation-phase ns per trial |
|--:|--:|--:|--:|
| 20.0 | 339 | 208 | 490 |
| 21.7 | 357 | 218 | 568 |
| 23.4 | 382 | 230 | 473 |

A walked trial costs more wall than a rho GAE. The x-only, shared-inversion pair entry costs about 0.6 of one.

**Consequence.** Under the GAE convention (one group addition = 1 GAE; calibration.json has no multiply unit), *any* shared-inversion or x-only trick is invisible. C1's first step therefore has to be priced in Ir (C2) or with a new pinned native unit.

### 2.2 Decomposition of the Table B prime gap

Source: leaderboard.json `best` rows.

| log2 r | IC S | rho S | IC/rho | IC/floor | rho/floor |
|--:|--:|--:|--:|--:|--:|
| 9.7 | 22.85 | 3.60 | 6.34 | 25.78 | 4.068 |
| 11.9 | 15.62 | 2.85 | 5.47 | 17.62 | 3.221 |
| 14.0 | 13.07 | 2.03 | 6.43 | 14.75 | 2.295 |
| 16.0 | 11.68 | 1.74 | 6.71 | 13.18 | 1.963 |
| 18.0 | 8.41 | 1.45 | 5.82 | 9.49 | 1.631 |
| 20.0 | 10.72 | 1.29 | 8.30 | 12.10 | 1.458 |
| 21.7 | 12.77 | 1.22 | 10.50 | 14.41 | 1.372 |
| 23.4 | 13.97 | 1.04 | 13.46 | 15.76 | 1.171 |

**From 11.9 to 23.4 bits.**
- IC/rho grows ×2.46.
- rho/floor improves ×2.75.
- IC/floor changes ×0.89.

**From 18.0 to 23.4 bits.**
- IC/rho grows ×2.31: rho contributes ×1.39 and IC/floor contributes ×1.66.
- Fitted slope of log2(IC/floor) per unit log2 r: **0.138**. The model value is 1/6 ≈ 0.167.
- Fitted slope of log2(IC/rho): 0.223. This is inflated by the denominator.

The 0.138 slope rests on four points (18.0-23.4 bits), one curve per size, three repetitions each. It has no interval.

**Rho finite-size fit.** I fitted rho/floor = 1 + c·N^(-β) on the eight rows: **β = 0.285**, log2 c = 4.47, residual sd 0.20 in log2. This is a derived fit with one instance per size, not a sealed bound. It implies rho/floor of about 1.09 at 28 bits and 1.04 at 32 bits.

**What converges in the matched rho.** The reference behind leaderboard.json's `reference_s` is the tuned negation walk `rho_reference_negation`: one implementation at all sizes, 24 runs per size (research/ic_rho_reference_20260923/reprice/ic-boundary-ledger-round5-2026-09-22.json). Its fixed costs as a share of its GAE:

| log2 r | set-up + start share | verification share | s_walk/floor |
|--:|--:|--:|--:|
| 9.7 | 0.54 | 0.097 | 1.48 |
| 11.9 | 0.35 | 0.075 | 1.85 |
| 14.0 | 0.28 | 0.069 | 1.50 |
| 16.0 | 0.33 | 0.047 | 1.22 |
| 18.0 | 0.23 | 0.028 | 1.21 |
| 20.0 | 0.13 | 0.018 | 1.24 |
| 21.7 | 0.089 | 0.013 | 1.23 |
| 23.4 | 0.11 | 0.009 | 1.03 |

So the convergence is mostly fixed set-up (jump table by joint double-and-add, starts) and verification amortising against sqrt(r). The walk part is noisy at about 1.0-1.5x floor. (The round-5 in-ledger `frozen-plain` rho, s ≈ 2.26 at fp24, is a different reference and is not used here.)

### 2.3 SAT/XOR arm, count-qualified-main session

Source: `research/ecbench_sat_pdp_20261009`, n = 17 Koblitz, 40 measured runs per arm, 40/40 verified.

**Counted GAE per run.**
- strong rho 1,023.76 (its canonicalisations, partition hashes and table operations are unpriced);
- SAT arm 874.08 (lower bound);
- conflicts (`relations.solver_ops`) 68,899.15 per run, in 749 solver calls over the 40 runs.

**Break-even price per conflict: c\* = (1023.76 - 874.08) / 68,899 = 0.00217 GAE.**
- Even if rho's unpriced work doubled its S, c\* rises only to 0.017 GAE.

Priced S/rho across the lead's band:

| price per conflict | priced S/rho |
|:--|--:|
| 0 GAE | 0.854 |
| 0.1 GAE | 7.58 |
| 1 GAE | 68.2 |

**Wall, L0, descriptive.**
- The SAT target_PDP phase totals 41.61 s, i.e. 15.1 µs per conflict.
- Rho wall is 115.6 ns per GAE (rho-strong) and 443 ns per GAE (rho-aa). That is 34-131 GAE per conflict, or S/rho of about 2,300-8,800 (the same as the raw wall ratio).
- At 115.6 ns per GAE, c\* is 0.25 ns: about one cycle per conflict.

## 3. Candidates

Every candidate is stated as a (representation, operation set) pair with its trichotomy class, per object-frame-ideation.md section 3.

### C1. x-only sumset target sampler for prime-field m = 2 IC (B3)

**Bottleneck.** B3: the relation phase is 68-93% of S in prime Table B (71.6% at fp24). Each trial is one walked group addition R ← R + J plus one probe.

**Ingredient.** Galbraith-Wang-Zhang (ePrint 2015/605; KR-RHO-fbd582): x(X - Y) comes almost free beside x(X + Y), sharing one inversion. Combined with Montgomery batching (KR-RHO-cb1c58). Provenance: retrieved.

**Mechanism (new content: an IC-only asymmetry).**
- A rho step must output a full point (x, y), because the *next* step's slope needs y. A walk cannot drop y or share an inversion between two successors without becoming best-of-two in-degree concentration, which is a different, measured lead (net 0.95-1.12 per step).
- An IC target is an independent sample that only has to be *probed* in an x-keyed folded table. It needs neither y nor a walk.
- So generate targets as the sumset x(A_i ± B_k), where:
  - A_i = a_i G + b_i Q, i ≤ J;
  - B_k = c_k G, k ≤ K;
  - J = K ≈ sqrt(trials/2) full points are precomputed. This costs J + K adds, about 250 at fp24, negligible next to about 30,000 trials.
- Each (i, k) costs one batched inversion of (x_{B_k} - x_{A_i}), plus λ± = (y_B ∓ y_A)·inv (2M), plus x± = λ±² - x_A - x_B (2S). That is about (3M + 2M + 2S)/2 ≈ 2.5M + 1S per target.
- A rho step or walked target costs about 3M + 3M + 1S (batched), or I + 3M + 1S (unbatched).
- On the rare hit (about 70 per solve at fp24), recompute the signed point once to fix R = ±(F_u ± F_v), and charge it.
- The hit count is unchanged: linearity of expectation over uniform targets, H4.

**Pair and class.**
- Representation: R1, affine short-Weierstrass x-coordinate in Montgomery u64 form.
- Tracked object: the IC relation vector.
- Operation set Σ: translation by factor-base pair sums.
- Trichotomy: **partial-action** (IC is Class I: the relation vector propagates only under translation by factor-base elements). The sampler changes only the cost of the target stage.

**SO codes touched, with the premise escaped.**
- **SO-TABLE**, LEAD-ICP-generic-table-decomposition: "[theorem] Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). ... Scope: any generic (enumeration/table) decomposition over F_p."
  - **Not escaped.** C1 is inside this scope and claims only a constant on the IC baseline.
  - It also matches that row's foreclosed phrase "faster S_3 root finding or batched subtraction makes prime IC sub-rho". C1 does **not** claim sub-rho.
- **SO-WALK**, LEAD-RHO-correlated-walks-shared-sums. It was the top `--match` hit, so it is addressed explicitly: "[proof] With a shared index sequence every walk adds the same R_i at every step, so pairwise differences P_i - P_j are invariant and two walks can never meet unless they started equal; ... Scope: any parallel rho."
  - Escaped premise: "two walks can never meet". IC targets never need to meet each other. They need to hit a *fixed* table, and the expected hit count is a sum of marginals, each uniform.
- **SO-GEN**, LEAD-RHO-generic-sqrt-lower-bound: "[theorem] Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations ... Every lead in this family moves only the constant ... Scope: all generic algorithms, any field, any r."
  - Not escaped. The gain is a constant.

**Tier.** I.

**Predicted gain.** All numbers below are priced in callgrind Ir (C2 harness), not in GAE.
- Relation-phase cost per trial ×**0.40** [0.25, 0.55], pairset/walk.
- Complete S_IC ×**0.55** [0.45, 0.70] at fp20-fp28.
- Hence an Ir-priced IC/rho at fp24 of about 13.5 × 0.55 ≈ 7.4x, against today's 13.5x in GAE.
- The two-level batching co-arm is predicted at ×0.6-0.75 on the relation phase. It removes the inversion but keeps y and one target per add.

Heuristics behind the prediction:
- H1. M ≈ S. I/M ≈ 12 at 24 bits, from I = 0.80 GAE and an affine add of I + 2M + S ≈ 1 GAE in calibration.json.
- H2. Batched inversion costs 3M per element.
- H3. The current walk does not amortise its inversion. The Table B recipe's targets are `TargetSource::Walk`; `lane_config` is set only for `TargetSource::WalkPrimeLanes`, so Table B uses no lanes and makes one serial `g.add` per trial (ic_boundary.rs:6686-6689).
  - The per-target arithmetic ratio is therefore (2.5M + S)/(I + 3M + S) ≈ 0.22.
  - Bookkeeping (hash probe, guard probe, repeat guard) dilutes it, because L0 wall shows 473 ns per trial against 230 ns per pair entry. Hence the interval.
- H4. Yield per target is unchanged (targets uniform; duplicates negligible at J·K ≪ N).
- H5. The relation share of S is 0.72, from Table B fp24.

Under the GAE-add convention the predicted change is 0 unless a pinned native unit "x_pm" is added, measured as ns(x-only ± pair)/ns(add) the way calibration.json's other natives are. The L0 pair-entry wall suggests a value of about 0.6.

**First discriminating step.**
- Add `TargetSource::PairSet` to the prime lanes in ic_boundary.rs (precomputed A/B sets, shared-inversion ± x-values, hit-time recompute charged).
- Arms on identical bases, targets and seeds, ≥ 24 seeds per size, sizes fp20, fp22, fp24, plus new fp26 and fp28:
  - walk (current);
  - two-level lock-step batching (the program's own planned next step, predicted ~2x);
  - pairset.
- Price all arms in callgrind Ir with phase toggles (C2), plus the GAE record.

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| pairset/walk Ir upper CI < 0.8 at ≥ 3 sizes, yield/ceiling within ±3% | open_next_step; best_measured = the ratio. A measured IC-baseline constant improvement under the owner's criterion. It also supersedes the two-level batching item if pairset/batched < 0.9. |
| interval spans 1, or yield drops | closed_obstructed(measured) for the sampler variant |
| gain appears only in Ir, not in GAE | report both. The GAE board would need a new pinned native before any leaderboard move. |

**Cost.**
- Implementation: 1-2 days, Rust, prime lanes only.
- Compute: under 2 CPU-hours (callgrind is about 50x slower; an fp28 solve is ~2.5e5 GAE).

**Self-kill risk: medium.**
- Bookkeeping may dominate Ir and pull the ratio to about 0.85.
- A reviewer may file it under the foreclosed phrase "batched inversion speeds up prime index calculus" (LEAD-ICP-prime-ic-constant-engineering). Novelty: adaptation of KR-RHO-fbd582 to IC targets; not novel as a trick, novel as the IC/rho asymmetry.

**--match phrasings.**
- Own: "x-only sumset target sampler: x(A_i + B_k) and x(A_i - B_k) from one shared inversion as index calculus targets"
- Plain: "generate index calculus targets two at a time from one inversion without computing y"
- Closed-lead vocabulary: "batched subtraction and table lookup decomposition with cheaper target generation"
- Top hits: LEAD-RHO-correlated-walks-shared-sums (18), LEAD-ICE-rootfind-pairtable-oracle (18), LEAD-ICP-generic-table-decomposition (17); frontier KR-RHO-cb1c58 (10). No row claims the sumset sampler.

### C2. Ir-priced native ledger for every arm and matched rho (B1/B3 instrument)

**Bottleneck.**
- B1/B3 pricing is blocked.
- LEAD-ICE-rootfind-pairtable-oracle is open_blocked on "problems/rootfinding-complete-cost-calibration.md (crypto); native work unpriced, L0 only, same-host replay".
- LEAD-ICE-charged-toy-ic-exponent-vs-rho is blocked on "EXP-ICEX-153c34 backend unbuilt; dispatch gated on the C-7 host-load gate".
- LEAD-ICE-sat-xor-pdp-oracle asks for "ns per conflict and per propagation against ns per group addition".

**Ingredient.**
- Deterministic instruction counts are independent of host load and replay bit-identically on any host running the same binary (Valgrind/Callgrind, Nethercote-Seward 2007; provenance recalled).
- Cachegrind's simulated D1/LL misses times a pinned per-level latency give the memory-bound upper band.
- Repo precedent: the K-conversion study (Ir per column touch against Ir per rho step, A/A spread 0.0048%), and LEAD-RHO-native-step-cost's Ir work.
- The rootfinding problem file asks for an L2 host. It never considers Ir.

**Mechanism.**
- One binary.
- Callgrind toggle markers around every native unit and phase: target query, PDP, probe, guard, LA, verify; for rho, canonicalisation, partition hash, DP insert and query, and step.
- Emit Ir per native unit and the D1/LL miss vector.
- Price both arms as Ir_total. Give a memory band Ir_total + Σ misses × latency(level), with latencies pinned from one pointer-chase microbenchmark per host class.
- This replaces "native work unpriced" with an exact count, and the L2 wall gate with a load-independent unit.

**Pair and class.**
- Instrument. It tracks no object of its own, so it has no trichotomy placement (stated, not dropped).
- The arms it prices are partial-action (IC) and full-translation generic (rho).

**SO codes touched.**
- SO-TABLE (it prices oracles inside the scope of LEAD-ICB-generic-table-oracle: "[theorem] Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice ... Scope: all binary and Koblitz curves, one target, setup charged."). Nothing is escaped; it is a ruler.
- SO-GEN (as for C1).

**Tier.** I (instrument).

**Predicted gain: none; it decides leads.**
- The ratios recorded with natives unpriced are 17-bit Koblitz rootfind-negfold m = 2 at 21.80 against strong rho at 14.15 (1.54x), and prime fp20 at 8.3x in GAE.
- Predicted Ir-priced cold IC/strong rho: 17-bit Koblitz ∈ [1.2, 2.5]; prime fp20 ∈ [5, 12].

Heuristics:
- H1. Rho's unpriced canonicalisation and table work adds 10-40% to rho in Ir.
- H2. IC's unpriced natives (probes, coordinate conversion, guard) add 10-60% to IC.
- H3. Ir underprices DRAM, but at toy sizes all tables are ≤ 1 MB, so LL misses are a rounding error. That is why the cachegrind band exists.

**First discriminating step.**
- Instrument the two sealed sessions named in the problem file (20-bit prime, 17-bit Koblitz).
- Run 8 targets × 3 rounds per arm under callgrind, with the A/A rho control, on the current shared host. No isolation is needed for Ir.

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| IC/rho > 1 across the whole Ir-plus-miss band at both sizes | LEAD-ICE-rootfind-pairtable-oracle → exhausted_at_scale at toy scale, by its own discriminates clause ("the pair-table engine is exhausted at toy scale") |
| < 1 across the band at both sizes | open_next_step, sent to the leaderboard validation gate |
| either way | the same harness answers LEAD-ICE-sat-xor-pdp-oracle (Ir per conflict) and gives EXP-ICEX-153c34 a host-load-free counter set, removing the C-7 gate dependency for its X counter. Program admission of Ir as a priced unit is a policy decision, not mine. |

**Cost.** Implementation 2-4 days (toggle markers plus ecbench schema fields). Compute: a few CPU-hours.

**Self-kill risk.** Low-medium. The program may decline Ir as admissible, or require the miss band to be calibrated per host class.

**--match phrasings.**
- Own: "callgrind instruction-count ledger pricing every native operation of IC arms and matched rho"
- Plain: "price the unpriced native operations of index calculus and rho in one deterministic unit"
- Closed-lead vocabulary (LEAD-ICB-generic-table-oracle): "every oracle built from group operations and membership tests priced end to end with setup charged in one deterministic unit"
- An earlier blocked-lead phrasing, "native work unpriced: common-unit pricing of field operations, hash probes and canonicalisation", is kept in the log.
- Top hits: LEAD-ICB-koblitz-rho-reference (15), LEAD-ICE-charged-toy-ic-exponent-vs-rho (15 and 11), LEAD-RHO-native-step-cost (14), LEAD-EXO-augmented-oracle-ggm (7). No row proposes Ir as the admission unit.

### C3. The B3 gap is mostly the rho denominator: times-floor decomposition with a falsifiable 28/32-bit projection

**Bottleneck.** B3 as stated: "Table B gap to matched rho widens from 5.47x at log2 r 11.9 to 13.5x at 23.4". Also LEAD-RHO-matched-rho-calibration: "no prime medium-tier bound exists".

**Ingredient.**
- The finite-size cost of DP-based parallel rho is fixed set-up (jump table, starts) plus the distinguished-point tail and verification, which together decay relative to sqrt(r) (van Oorschot-Wiener 1999, KR-RHO-6239aa; retrieved).
- In the *matched* reference (`rho_reference_negation`, the leaderboard's `reference_s`), set-up + start falls from 54% of GAE at 9.7 bits to 11% at 23.4 bits, and verification from 9.7% to 0.9% (section 2.2, derived from its recorded counters).

**Mechanism.** Section 2.2 above. Report Table B against the floor, not against as-built rho, and project.

**Pair and class.** Instrument and derivation; no tracked object.

**SO codes touched.**
- SO-TABLE, LEAD-ICP-generic-table-decomposition. Its measured clause "Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4" is re-attributed.
- No premise is escaped. The theorem part of that obstruction is untouched and confirmed: IC/floor grows at 0.138 per bit, against the model's 1/6.

**Tier.** I.

**Predicted numbers, current recipe.**

| log2 r | IC/floor (fitted slope 0.138) | IC/floor (model slope 1/6) | IC/rho |
|--:|--:|--:|--:|
| 28 | 24.5 | 26.9 | 21-26 |
| 32 | 35.9 | 42.6 | 31-41 |

- rho/floor at 32 bits: 1.04 (β = 0.285 fit).

Heuristics:
- H1. The 18-23.4-bit slope is the asymptotic one. Below 18 bits, fixed IC costs make IC/floor *fall* with size.
- H2. Rho's set-up share decays as N^(-0.29) (fitted, one instance per size).
- H3. The recipe stays at its family optimum.

If C1 lands, multiply the IC/rho projection by about 0.6.

**First discriminating step.** Seal the fp26, fp28 and fp32 rows plus the prime medium-tier rho bounds that LEAD-RHO-matched-rho-calibration already specifies: ≥ 24 runs per size, replay certificates, and the section 5a band.

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| IC/floor at 32 bits in [30, 48] and rho/floor ≤ 1.15 | the B3 statement is corrected to "IC/floor grows as N^{~1/6}". LEAD-RHO-matched-rho-calibration gets its fitted R(N) (open_next_step → closed_known for the fit form; best_measured = β). No change to the closed lead. |
| IC/floor at 32 bits < 30 | the m = 2 recipe has an unmodelled sub-1/6 regime: open_next_step on LEAD-ICP-prime-ic-constant-engineering, best measured = the slope |
| rho/floor > 1.3 at 32 bits | the matched-rho implementation, not IC, is the outlier: open_next_step on the rho side |

**Cost.** Zero for the derivation (done). The confirming runs take CPU-hours.

**Self-kill risk.** Low as arithmetic. Medium as novelty: it overlaps LEAD-RHO-matched-rho-calibration's R(N) fit and adds the IC-side attribution and the projection.

**--match phrasings.**
- Own: "times-floor decomposition of the Table B prime gap into rho finite-size bias and IC growth"
- Plain: "the prime index calculus gap widens because the rho reference approaches its floor"
- Closed-lead vocabulary: "Table B gap to matched rho widens; matched rho finite-size bias and the missing prime medium tier"
- Top hits: LEAD-RHO-matched-rho-calibration (23 and 35), KR-RHO-cd0049 (16).

### C4. SAT/XOR point-decomposition oracle: decided by the break-even conflict price (B4)

**Bottleneck.** B4. LEAD-ICE-sat-xor-pdp-oracle has best measured "native-XOR SAT S/rho 0.854 lower bound, conflicts unpriced, n = 17 Koblitz". Its next step is to calibrate ns per conflict and reprice at 0, 0.1 and 1 GAE.

**Ingredient.**
- A CDCL conflict cannot cost less than one clause-database traversal: at least a decision, a propagation to a falsified clause, and conflict analysis, each touching cache lines (Chaff, 2001; recalled).
- The decision needs only the trivial bound "more than one cycle".

**Mechanism.** Arithmetic on the recorded resource vector (section 2.3). Break-even c\* = 0.00217 GAE ≈ 0.25 ns ≈ 1 cycle per conflict on the host that measured it. The lead's band gives S/rho of 0.854, 7.58 and 68.2 at 0, 0.1 and 1 GAE.

**Pair and class.**
- Representation: R1, F_2 coordinates of the Weil-descended chain as CNF-XOR.
- Operation set: translation by factor-base elements.
- Trichotomy: **partial-action**, IC Class I. The oracle reads coordinates algebraically.

**SO codes touched, with the premise escaped.**
- **SO-TABLE**, LEAD-ICB-generic-table-oracle: "[theorem] Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice: Shoup T >= sqrt(r/|Aut|) and Corrigan-Gibbs-Kogan S*T^2 >~ r/|Aut| apply, ... Scope: all binary and Koblitz curves, one target, setup charged."
  - Premise escaped: "built from group operations and membership tests". A SAT solver on the descended system reads coordinates, so SO-TABLE does not close it. That is why the lead is open.
- It is caught by LEAD-ICB-decomposition-encoding-and-sat: "[measured] Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5), while beating rho needs alpha < m/2 - 1; ...".
  - This supplies the second clause of the lead's own discriminates rule ("conflicts tracking 2^(ml)/m!").

**Tier.** I (decision).

**Predicted gain: none.**
- Against the pair-table class the lead's rule names: in the same session the Frobenius-MITM arm is 17.073 (4.27x rho, fully counted). Break-even against it is (4,372.4 - 874.1) GAE per run / 68,899 conflicts = **0.051 GAE per conflict ≈ 5.9 ns** (derived). SAT therefore loses to the pair table for any conflict costing more than about 24 cycles.
- Priced S/rho ≥ 6.6 under the floor "a conflict costs at least 10 ns" (H1: about 40 cycles at about 4 GHz, i.e. at least 0.086 GAE at 115.6 ns per GAE).
- The L0 wall ratio is 2,300-8,800 (descriptive, not admitted).
- H2: rho's unpriced natives can at most double rho's S, giving c\* ≤ 0.017 GAE ≈ 2 ns, still more than three orders of magnitude below the measured 15.1 µs per conflict.

**First discriminating step.**
- Zero compute: file the derivation against the sealed session (receipt SHA-256 a03b673e...).
- Optional confirmation: one callgrind run of the SAT arm on `specs` of count-qualified-main for Ir per conflict, against Ir per GAE of strong rho (the C2 harness).

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| priced S/rho > 1 at the 0.1 GAE point (derived: 7.58) and conflicts follow 2^{alpha l} with alpha ~ m (cited) | **closed_dominated** by the pair-table oracle and strong rho ("SAT is enumeration at a constant", the lead's own rule) |
| only a measured conflict price below 0.0022 GAE could reopen it | physically excluded (H1). Would read as open_next_step with best_measured = the priced ratio. |

**Cost.** Zero, or 1 CPU-hour for the Ir confirmation.

**Self-kill risk.** Very low.

**--match phrasings.**
- Own: "break-even price per SAT conflict from recorded counts decides the native-XOR SAT oracle"
- Plain: "SAT conflicts cost too much for the SAT decomposition oracle to beat rho"
- Closed-lead vocabulary: "per-attempt UNSAT cost 2^{alpha l} with alpha ~ m; SAT conflicts unpriced; CNF-XOR complete enumerator"
- Top hits: LEAD-ICE-generic-oracle-arity-cost-floor (19), LEAD-ICE-sat-xor-pdp-oracle (14), KR-IC-5765d2.

### C5. Separator/treewidth certificate for the Macaulay closure: the w that decides ECC2K-130 m = 4 (B5, binary side of B4)

**Bottleneck.** B5 and the binary half of B4. Three leads carry the +7.62-bit row (+9.78 at median K) as the ECC2K-130 decision value:
- LEAD-ICB-prime-degree-algebraic-decomposition (open_blocked);
- LEAD-ICE-descent-closure-degree-at-scale (open_blocked; 169 GB cap, 217 GB projected);
- LEAD-ICE-hybrid-guess-determine-l7 ("never below the +7.62 floor").

**What that row actually charges.**
- The descent-degree note prices the oracle as "C(N, ≤D)^w a target ... `w = 1` prices one touch per column, which no elimination beats. `w = 2` is the usual estimate at `ω = 2`".
- The same note says: "The closure's counted work. It grows roughly as its column count to the power 2.2. So the `w = 2` rows are the ones the measured closure tracks."
- The w = 2 degree-4 m = 4 row is 2^93.91, **+33.10 bits** over rho 2^60.81.
- K grows with matrix size, from 4.0 up to 83 at 17,902 columns (k_conversion study), which is the same w > 1 signature.

**Ingredient.**
- Every symmetric elimination ordering produces a filled graph containing a clique of size tw + 1 (treewidth = min over orderings of the max clique - 1; retrieved). Dense work on that clique is at least (tw+1)³/3 bit-operations divided by the word width.
- Graphs with no balanced separator smaller than s have tw ≥ s - 1 (recalled).
- Krylov methods (Wiedemann 1986, Coppersmith 1994) cost O(C · nnz) and are the only known sub-dense route (recalled).
- So w < 2 for a refutation needs either small separators, which nested dissection (George 1973; Lipton-Rose-Tarjan 1979) would exploit, or a Krylov dimension of o(C).
- Reading the matrix alone already costs nnz ≥ C · (mean column weight). Hence w = 1 understates even the read cost by log2(column weight) bits.

**Mechanism.** Measure the structural quantities that set w on the closure matrices that already run:
- s(C), the METIS nested-dissection top separator size, and a treewidth upper bound (min-degree) and lower bound (minor-min-width);
- the BW/Berlekamp-Massey Krylov dimension d_K of the refutation system;
- mean column weight.

Do this on both the full Macaulay closure and the block-local (locality-2) closure, which the program found also refutes. Fit s ~ C^σ and d_K ~ C^κ, then price the n = 131 rows at w_eff = 1 + max(κ, 2σ - 1) instead of w = 1.

**Delta over IDEA-20261018-1aff90.** That idea proposes a GF(2) block-Wiedemann *consistency test* for plain XL at degree 5. C5 adds:
1. the separator/treewidth certificate, which decides whether *any* sparse closure (the program's named successor) can have w < 2;
2. the repricing consequence for three leads.

**nnz projection for the blocked C1 cell** (m = 3, n = 19, l = 7, D = 5; derived, upper bound):
- N = (m-2)n + m·l = 40 unknowns;
- C(40, ≤5) = 760,099 columns;
- 2n = 38 cubic equations × C(40, ≤2) = 821 multipliers = 31,198 XL rows;
- at most C(33, ≤3) = 6,018 terms per row, so nnz ≤ 1.9e8, about 0.75 GB at 4 B per index.

Against the 217 GB dense-closure projection, this is the memory a Krylov or sparse route would need, about 290x less. Mutant rows and fill are exactly what s(C) predicts.

**Pair and class.**
- Representation: R1, Boolean ANF of the Weil-descended chained S_3.
- Operation set: translation by factor-base elements.
- Oracle: bounded-degree linear algebra.
- Trichotomy: **partial-action**, IC Class I.

**SO codes touched, with the premise escaped.**
- **SO-TABLE**, LEAD-ICB-generic-table-oracle: "[theorem] Every oracle built from group operations and membership tests makes IC a generic-group algorithm with advice ... Scope: all binary and Koblitz curves, one target, setup charged."
  - Premise escaped: "built from group operations and membership tests". The closure reads coordinates algebraically, which is why this route is the one non-generic binary oracle.
- Non-SO but B4-named, LEAD-ICP-icperf-writability-boundary: "[cost_model] At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by ... +40.8 (ECC2K-130) ... the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF".
  - The chained system escapes the premise "unchained descended ANF". C5 prices the chained closure's linear algebra, which is the cost left once writability is escaped.

**Tier.** I. It is an instrument that settles an exponent *question* (w); hardware does not move the exponent.

**Predicted outcome.**
- H1. Each descended S_3 equation touches all l + l + n bits of its three points, so rows form near-cliques of about 10^3 columns and the column graph has a Θ(1) spectral gap.
- H2. GF(2) unsymmetric elimination with pivoting inherits the symmetric fill bound through the bipartite or M^T M structure (heuristic, not a theorem here).
- H3. The block-local closure's largest block dominates: C(295, ≤4) ≈ 3.1e8 against the full C(394, ≤4) ≈ 9.9e8.

From these: σ ≥ 0.9 and d_K/C ≥ 0.5 on full matrices, so w_eff ≥ 2.

**Conditional on w ≥ 2 holding at scale** (the thing this candidate tests), the ECC2K-130 m = 4 rows over rho are:
- **degree 4: +29 bits** (block-local, largest block at w = 2) **to +33.1 bits** (full, w = 2; the note's 2^93.91 row);
- **degree 3: about +20 bits.** This is derived here, not in the note: C(398, ≤3) ≈ 2^23.33 columns, squared, times the 2^34.0 targets of the ℓ = 34 row, gives 2^80.7.

The note's degree-2 w = 2 row (+8.83) is excluded, because measured refutation degree is 3-4. No outcome of the blocked degree runs (degree ≥ 3) then comes within 2^20 of rho.

**First discriminating step.**
- On the existing degree-3/4 cells (N = 26-44: k_conversion cells m4-11-5, m4-12-5, m3-16-6, m3-11-5-deg4; dreg_closure_scale draws), dump each Macaulay sparsity pattern, full and block-local.
- Run ndmetis (separator sizes), min-degree / minor-min-width treewidth bounds, and one GF(2) block-Wiedemann Krylov-dimension probe.
- Standard host, minutes to hours.

**Outcomes to dispositions.**

| outcome | disposition |
|:--|:--|
| σ ≥ 0.8 and κ ≥ 0.8 on both matrix families | **closed_obstructed(cost_model)** for the ECC2K-130 pricing consequence in LEAD-ICB-prime-degree-algebraic-decomposition and LEAD-ICE-hybrid-guess-determine-l7. Their discriminates rows are repriced at w = 2 (≈ +20 at degree 3, +29 to +33 at degree 4), so no degree-≥ 3 outcome brings them within 2^20 of rho. LEAD-ICE-descent-closure-degree-at-scale keeps only its scientific degree question; its large-memory run loses decision value for ECC2K-130. |
| σ ≤ 0.6 on the block-local family | **open_next_step**: nested-dissection closure with w_eff = 3σ (direct) or 1 + κ (Krylov); best_measured = σ. This is the only HPC-side escape from w ≥ 2, worth a sparse-closure build. |
| mixed | price both rows and report the band |

**Cost.** Implementation 1-2 days (pattern dump plus METIS/BW scripts). Compute: under 4 CPU-hours.

**Self-kill risk: medium.**
- H2 may fail for GF(2) with pivoting.
- A small block-local separator would be a *positive* outcome. The candidate reopens the lane rather than closing it.

**--match phrasings.**
- Own: "nested-dissection separator certificate of the Macaulay closure column graph bounds the closure work exponent"
- Plain: "can a sparse Groebner closure avoid quadratic linear algebra cost on descended Semaev systems"
- Closed-lead vocabulary (LEAD-ICP-icperf-writability-boundary): "descended ANF exceeds the whole per-decomposition rho budget, paid before any solver runs; Macaulay closure linear algebra cost per column"
- An earlier blocked-lead phrasing, "degree-capped certified decomposition; Macaulay or block-Wiedemann memory; closure degree stays 4", is kept in the log.
- Top hits: LEAD-ICE-descent-closure-degree-at-scale (31), LEAD-ICB-prime-degree-algebraic-decomposition (18), LEAD-ICP-icperf-writability-boundary (16), LEAD-ICB-orbit-linear-algebra (16 and 13). No row prices the closure via separators or treewidth.

## 4. Killed candidates (own weak candidates first)

- **K1. "Arithmetic-floor ceiling" proof that IC/rho ≥ κ·N^{1/6} closes LEAD-ICP-prime-ic-constant-engineering.**
  - Derivation: with relations ≈ 0.62·C, the pair table is C², targets are 0.31·N/C, and S·sqrt(N) ≥ c_x·3(0.15N)^{2/3} ≈ 0.85·c_x·N^{2/3}. With c_x/c_step ≥ 0.5 this gives IC/rho ≥ 0.41·N^{1/6}.
  - Killed:
    - it restates the closed obstruction "m = 2 >= 3 (pT_dec)^{2/3}" of LEAD-ICP-generic-table-decomposition;
    - it cannot close a lead whose mechanism says "Each verified gain is an improvement over the current IC baseline under the owner's success criterion even though the exponent is fixed".
  - Kept only as the C3 projection.
- **K2. Cache-blocked / radix-partitioned pair table, or xor and binary-fuse probe filters.**
  - Killed: `build_negation_folded_prime_blocked` and `PackedPairTable` already exist.
  - ns_per_lookup is 0.012-0.017 GAE in calibration.json, about 1-2% of the relation phase at toy sizes.
- **K3. Symmetric engineering** (Montgomery u64, SIMD/IFMA multiprecision, batched walk inversion, tensor-core multiplication).
  - Killed: it cancels in IC/rho.
  - The lead's forecloses list already names "Montgomery native arithmetic for the relation search".
- **K4. GPU root-finding oracle as a ratio lever** (LEAD-ICE-gpu-rootfind-oracle).
  - Prediction for that lead: GPU IC/rho ≥ CPU IC/rho once the pair table exceeds per-SM shared memory (C²·8 B > ~100 KB, roughly log2 r ≳ 25). Rho steps are coalesced arithmetic, while probes are random gathers. Below that size the two are about equal.
  - Not a lever.
- **K5. Wiener full cost / AT metric** for prime m = 2.
  - At balance, memory ≈ time ≈ N^{2/3}, and probes parallelize at P ≈ M, so full cost stays Θ(N^{2/3}).
  - It only penalizes IC. IDEA-20260809-bf5139 already owns AT pricing.
- **K6. Mesh LA / block Wiedemann for the relation matrix.**
  - LA is 0.0-0.4% of S in prime Table B.
  - LEAD-ICB-orbit-linear-algebra is exhausted_at_scale.
- **K7. Faster square roots for p ≡ 1 mod 2^k.**
  - calibration.json shows sqrt at 5.80 GAE at bench-16bit and 4.67 at fp24, against about 0.8 elsewhere: a large 2-adic valuation of p - 1.
  - But sqrt_solves = |F| (111 at fp24), under 2% of S.
- **K8. EC tag tracing** (LEAD-RHO-cheaper-step-primitives, prime branch).
  - The next index must be a function of the next point.
  - Any non-constant tag of x(P + R) needs λ = Δy/Δx at full precision (inversion share + M + S), and y3 is needed for the following slope. The skippable work per step is zero.
  - Predicted net ns per useful step ≥ 0.98 of the batched plain step, so the prime-EC branch would read closed_obstructed(cost_model). The binary halving branch is untouched.
  - Killed as a candidate: its best case only confirms rho's constant.
- **K9. A Shoup-based bound for LEAD-RHO-non-automorphism-equivalence.**
  - Argument: a GGM-simulable canonicaliser of cost c per step makes the quotient walk generic with about (1 + c)·sqrt(πN/2h) operations, so Shoup forces c = Ω(sqrt h). That discharges the generic half of the proof obligation, stronger than the requested Ω(log h).
  - The real-cost half (a cheap H-invariant of the encoding) is coordinate-dependent and outside HPC.
  - Killed as an HPC candidate; recorded here for the lead owner.
- **K10. GF(2) block-Wiedemann consistency test for the blocked dreg cells.**
  - Duplicate of IDEA-20261018-1aff90 (adaptation). Its memory delta is folded into C5.
- **K11. F4 engineering for B2** (GBLA-style block elimination, msolve linear algebra).
  - LEAD-ICE-prime-field-semaev-solving-degree is closed_known.
  - beta_work 0.797 / 0.647 against the 0.30 gate is an exponent gap, which constants cannot cross.
- **K12. ECC2K-130 GPU campaign arithmetic** (≈ 4.2 RTX PRO 6000-years at 15.884 B/s).
  - Not new. It is owned by LEAD-RHO-ecc2k130-gpu-fpga-throughput and the pool campaign.
- **K13. Medium-tier memory-hierarchy repricing of probes.**
  - Real but not decisive. The m = 2 optimum table at 63 bits is (0.15·2^63)^{2/3} ≈ 2^40.2 entries (≈ 8 TB), so the 63-bit m = 2 cell of LEAD-ICP-full-width-arity-grid is memory-capped regardless.
  - Prediction for that panel: under a 64 GB cap, m = 2 S/rho ≥ 2^12.

## 5. Citations and provenance

| citation | provenance | used in |
|:--|:--|:--|
| Galbraith, Wang, Zhang, "Computing Elliptic Curve Discrete Logarithms with Improved Baby-step Giant-step Algorithm", IACR ePrint 2015/605 (slides: P1+P2 and P1-P2 together cost I + 4M + 2S) | retrieved (eprint.iacr.org/2015/605; math.auckland.ac.nz/~sgal018/ascona.pdf) | C1 |
| Montgomery simultaneous inversion (1987), KR-RHO-cb1c58 | recalled + repo KR | C1 |
| Nethercote, Seward, "Valgrind: A Framework for Heavyweight Dynamic Binary Instrumentation", PLDI 2007 (callgrind/cachegrind) | retrieved (doi 10.1145/1273442.1250746; valgrind.org/docs/pubs.html) | C2 |
| van Oorschot, Wiener, "Parallel Collision Search with Cryptanalytic Applications", J. Cryptology 12(1):1-28, 1999 (DP tail), KR-RHO-6239aa; Bos-Costello-Miele, KR-RHO-825bca | retrieved (bibliographic record and abstract; people.scs.carleton.ca/~paulv/papers/JoC97.pdf draft) | C3 |
| Sealed ecbench session ECBS1hb55a1bdabf18 (count-qualified-main, research/ecbench_sat_pdp_20261009), full-replay receipt SHA-256 a03b673e...; resources file count-qualified-main.resources.json | retrieved (read in repo) | C4, load-bearing |
| Moskewicz et al., "Chaff", DAC 2001 | recalled | C4 (only "a conflict costs ≥ 1 cycle" is used) |
| Treewidth = min over chordal completions of ω - 1, i.e. min over elimination orderings | retrieved (en.wikipedia.org/wiki/Chordal_completion; arXiv 1411.1745) | C5 |
| Lipton, Rose, Tarjan, "Generalized nested dissection", SIAM J. Numer. Anal. 16(2):346-358, 1979; George 1973 | bibliographic data retrieved; content recalled. An expander fill lower bound attributed to LRT was **not** found and is not used. | C5 |
| Wiedemann 1986; Coppersmith 1994 block Wiedemann (KN-LIT-017) | recalled | C5 |

## 6. Searched but empty (no decisive HPC ingredient found)

- **GPU tensor-core / IFMA multiprecision multiplication.** Symmetric between IC and rho; cancels.
- **Energy-per-operation hardware models** (Horowitz-style tables). The only IC/rho asymmetry they expose is memory access, and it penalizes IC.
- **Cache-oblivious GF(p) LU / F4 linear algebra** (Frigo-Leiserson-Prokop-Ramachandran 1999). Constants on the closed_known B2.
- **FPGA bit-sliced GF(2^m) multipliers for Macaulay elimination.** Constant; w unchanged (C5 decides w).
- **B7 transfer: isogeny-step cost** (√élu, Bernstein-De Feo-Leroux-Smith 2020) for LEAD-TRF-teske-trapdoor-fp6-weak-class. A constant; it does not decide where the weak curve sits.
- **B7 transfer: non-homomorphic Miller-cocycle transfers.** No HPC content.
