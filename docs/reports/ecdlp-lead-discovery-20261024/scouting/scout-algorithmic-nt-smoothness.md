# Scout dossier (round 2): algorithmic number theory, smoothness and sieving

Field: smoothness and sieving (NFS/FFS, Pomerance, Canfield-Erdos-Pomerance), ECM-style stage-two batching, descent trees, large-prime variations, function-field sieve analogues over F_p(t) and over the function field of E, and relation collection as a smoothness problem.

This file replaces the round-1 dossier written at the same path earlier on 2026-10-24. The round-1 text is preserved unchanged at `scout/scout-algorithmic-nt-smoothness.round1.md` so the orchestrator can reconcile the two. Section 1 lists every change.

## Labels used in this file

- **computed**: arithmetic this session ran itself, with the program's conventions, on read-only inputs. Scripts are in `scout/calc/` (round-1 scripts, re-run here) and `scout/calc-r2/` (new). None of it is a measurement on curves.
- **prediction**: an expected value. Each one names its heuristic (H1-H8, section 9).
- **retrieved**: a citation this session opened with WebSearch or WebFetch. **recalled**: from memory, not opened here.
- No outcome is reported that this session did not produce.

## Inputs read this session

- ATLAS.md (every family) and KRMAP.md, both read in full.
- object-frame-ideation.md, sections 1-3.
- idea-generator.md: "Search heuristics" and "Obstructions as generative material".
- target-result-profile.md, Part A.
- LEADERBOARD Table B, the phase table, the pair-table set-up table and the planner-validation table.
- Lead YAMLs: ICE-charged-toy-ic-exponent-vs-rho, ICE-relation-graph-rank-large-prime, ICE-decomposition-probability-audit, ICP-coincidence-harvest-structured-base, ICB-large-prime-variants, TRF-jv-nagao-genus2-cover-decomp, TRF-jv-sieve-fp6-weak-class, TRF-teske-trapdoor-fp6-weak-class.
- The obstruction.statement of every lead quoted below, extracted verbatim from the YAMLs.
- Ledger records: EV-ICEX-16e3ec, IDEA-20260727-003 (claim and mechanism), H-ICEX-87ad66 (scope and floor sections), the H-ICEX-ab1da2 index row, and the H-BINSTD-555991 index row.
- Read-only context from a concurrent workflow: `docs/reports/ecdlp-lead-discovery-20261024/PROPOSED-DIFFS.md` (sections 1-3) and report.md (AUD-4 notes). These propose a no-large-prime arity/oracle-order threshold theorem (`formal/CryptoResearch/IC/ArityOracleThreshold.lean`). Nothing in either file was edited.

## Provenance of the load-bearing citations

- **GTTD.** Gaudry, Thome, Theriault and Diem, "A double large prime variation for small genus hyperelliptic index calculus", Math. Comp. 76 (2007) 475-492. **Retrieved**: the bibliographic record and the ePrint 2004/153 abstract. The O~(q^{2-2/g}) exponent is **retrieved** from Diem's arXiv math/0606607 abstract, which proves it for plane curves and says it generalises the GTTD result.
- **Gaudry 2009** (index calculus on abelian varieties of small dimension). Stays **recalled**. A HAL summary giving O~(q^{4/3}) at n = 3 appeared only as a search snippet, and the journal attribution could not be confirmed.
- **DiPippo-Howe**, J. Number Theory 73 (1998) 426-450. **Retrieved**: the arXiv PDF, pages 1-2, including v_n and Theorem 1.1.
- **Recalled** (not opened here):
  - Erdos-Renyi (1960) and Janson-Knuth-Luczak-Pittel (1993), random-graph cycles and the giant component.
  - Lenstra-Manasse, Math. Comp. 63 (1994), two large primes.
  - Leyland-Lenstra-Dodson-Muffett-Wagstaff, ANTS-V (2002), three large primes.
  - Pomerance (1982), early abort.
  - Vallee, Math. Comp. 56 (1991), small modular squares.
  - Bostan-Gaudry-Schost, SIAM J. Comput. 36 (2007).
  - Bosch-Lutkebohmert-Raynaud, Neron Models (1990), section 7.6.
  - Tate, Invent. Math. 2 (1966).
  - Enge-Gaudry, Acta Arith. 102 (2002).

---

## 1. Changes since round 1

1. **PC2's free-oracle floor was not optimal. It is corrected here.**
   - Round 1 imposed m·beta = 1 (one full-base decomposition per target). That is the constraint a fixed base imposes in GTTD's setting.
   - A prime-field interval base has a free size. Freeing it lowers the large-prime floor from 2(m-1)/m² to **2/(m+2)**: 4/9 becomes **2/5** at m = 3, and 3/8 becomes **1/3** at m = 4.
   - The general law for an oracle of order k is **2/(m+2-2k)** for k <= 1.
   - The per-attempt budget at m = 3 rises from 1/12 to **1/8** (one output per attempt) and is unchanged at m >= 4.
   - All of this is computed in `calc-r2/lp_floor_r2.py` (section 3).
2. **PC1's claim is restated.** The exponent is exactly 1/2 for every oracle (under H1), and the constant headroom over ideal negation-rho is at most 1.34x. The proposed closed_obstructed disposition is scoped to the exponent question. Whole-solve S is a constant question.
3. **Round 1's fp28 "prediction" is withdrawn.** The planner-validation table already measures 21.7x at 28 bits. Section 5 recasts it as a consistency check of the N^{1/6} law against existing rows.
4. **KB1 is redone.**
   - It now includes total work and a memory cap, allows several partials per attempt, and uses a block-multidegree ANF support.
   - It is tied to the open LEAD-ICB-large-prime-variants next_action (EXP-BINSTD-e066d8 Stage 0) rather than filed under the closed writability row.
   - Round 1's figures reproduce: +23.30 at about 2^51 memory, in round 1's convention.
5. **KB2's carrier-count heuristic H6 is recomputed** with the retrieved DiPippo-Howe formula, which includes r(q) = 1/2.
   - n = 11 gives 0.006 (g = 10) and 0.012 (g = 10..14). Round 1 had 0.017.
   - The same model predicts 92 carriers at n = 5 through genus 8, where the lead found none.
   - H6 is therefore uncalibrated, and the toy ladder's power cannot be computed from it.
6. Every obstruction statement is quoted whole, Scope clause included.
7. New kills: K14 (three or more large primes, by a percolation argument) and K15-K19 (section 10).
8. **Re-owned computations:**
   - `calc/s4_reach.py` re-run: 0.1214 for all four box shapes.
   - `calc/lp_writability.py` re-run: the round-1 table reproduces exactly.
   - The frozen c5a377 design ratios were recomputed from `exact_yield_budgets_out.json`.
   - All 15 `--match` phrasings were re-run with the environment variables exported (`calc-r2/match_r2.txt`).
9. **PC2 also bears on the concurrent no-large-prime threshold theorem.** `arity_three_free_ties` is true within its hypotheses H1-H4, which exclude large primes. The problem is the proposed atlas diff (PROPOSED-DIFFS section 3), which would cite it as the SO-TABLE "m = 3 only ties rho even with T_dec = O(1)" clause with no qualifier. That diff needs the scope clause "two-term model, no large primes", because with two large primes a restricted free oracle at m = 3 reaches N^{2/5} (section 3).
10. **PC1's and PC2's outcome maps are re-keyed** on per-rung ratios against predicted values. They no longer rely on a fitted four-size exponent, which EV-ICEX-16e3ec found unidentifiable (CI [0.10, 2.32]; its proves-too-much control failed).

---

## 2. Why the field has little purchase on E(F_p) (orientation, carried from round 1)

The Dickman rate transfers exactly. A random point has about |F|^m/(m!·N) decompositions over a base of size N^{1/u}. At m = u that is (e/u)^u, the Canfield-Erdos-Pomerance / Dickman u^{-u(1+o(1))} rate (recalled).

What does not transfer is the divisibility test that makes sieving, special-q and descent work:
- "Is P_1 a summand of R?" is always true.
- No archimedean size decreases under subtraction.
- The only modulus is p.

Mean yield is pinned by conservation (KN-FIND-007), so every surviving lead from this field is about **relation-combination accounting**: large primes, cycle and giant-component structure, budgets. None of them is a new divisibility test. The constructive sieve-type ideas tried this session are killed in section 10 (K15-K19).

---

## 3. Candidate PC2 (prime, B1/B2): the large-prime extension of the arity/oracle-order threshold. Free m = 3 reaches N^{2/5}, not a tie

**Bottleneck.**
- B1: the approved non-enumerative O5 oracle is unbuilt, and its arity and budget are set by no-large-prime models.
- B2: beta_work is 0.797 or 0.647 against a 0.30 gate.

The gate and the "m <= 4 is empty" belief both come from two-term models without large primes:
- IDEA-20260727-003: "the admissible region ... is predicted to be EMPTY for every m <= 4 and non-empty only for m >= 5". Its model is F = max(B, c_LA·B^omega) with B^m >= m!·N, and it has no large primes.
- The SO-TABLE statement clause "m = 3 only ties rho even with T_dec = O(1)".
- PROPOSED-DIFFS sections 1-3 (concurrent, unapplied). The exponent is >= 2/(m+1-k) for k <= 2, with "arity_three_free_ties". The report itself says the 1LP figure "needs the large-prime accounting the model does not have".

**External ingredient.**
- The double-large-prime variation of GTTD (Math. Comp. 76, 2007; exponent O~(q^{2-2/g}) via Diem arXiv math/0606607; both **retrieved**), with its structure transported to point decomposition:
  - a small base merged into a root;
  - partials with two large legs as edges;
  - linear algebra only over the small base.
- The Erdos-Renyi giant-component threshold (recalled).
- The new step is to free the full-base size, which GTTD's fixed set of degree-1 places cannot do.

**Derivation** (exponents of N; H1, H3, H4).
- Setup:
  - Full base Q = N^b (large legs) and small base Q_s = N^{rb}, r in [0, 1].
  - A partial has m-2 small legs and 2 large legs.
- Per-attempt partial yield, mean exact by conservation, shape from H3:
  - y = 2^m·Q_s^{m-2}·Q²/((m-2)!·2!·N) = N^{b(2+(m-2)r) - 1}.
- The relation stage needs the large-prime graph supercritical: edges about theta·Q with theta = O(1) (H1).
- Then:
  - attempts A = Q/y;
  - linear algebra = w·Q_s² (H4; cycles have length O(log Q) above threshold);
  - forming the partials costs at least Q.
- An oracle of order k costs N^{kb} per attempt and at least its output y.

Minimising e = max(log A + max(kb, log y), 2rb, b):
- For k < 1 the optimum is at r = 1/2, b = 2/(m+2-2k), so **e_LP(m, k) = 2/(m+2-2k)** for 0 <= k <= 1.
- For k >= 1, large primes do not help and the no-LP law 2/(m+1-k) applies. Both laws equal 2/m at k = 1.
- At the optimum the output constraint is exactly tight (log y = kb). The oracle must return O(1) partials per unit of its own cost.

**Computed** (`calc-r2/lp_floor_r2.py`, grid optimiser over (b, r)). The no-LP column reproduces the concurrent theorem's 2/(m+1-k) for k <= 1.

| m | k = 0 LP / no-LP | k = 1/4 LP / no-LP | k = 1/2 LP / no-LP | k = 1 (LP = no-LP) |
|--:|:--|:--|:--|:--|
| 2 | 0.500 / 0.667 | 0.571 / 0.728 | 0.667 / 0.800 | 1.000 |
| 3 | **0.400** / 0.500 | 0.444 / 0.534 | 0.500 / 0.571 | 0.667 |
| 4 | **0.333** / 0.400 | 0.364 / 0.421 | 0.400 / 0.445 | 0.500 |
| 5 | 0.286 / 0.334 | 0.308 / 0.348 | 0.333 / 0.364 | 0.400 |

Consequences:
1. **m = 3 with a free restricted oracle is sub-generic (0.400), not a tie.**
   - "Restricted" means the oracle returns only partials with at least one small leg.
   - The sub-generic line with large primes is k < (m-2)/2 at m <= 4. At m = 3 that is k < 1/2, where no-LP gives an empty set.
   - At m = 4 the line stays at k < 1, but every exponent below it drops.
   - Scope: H1, H3, H4, a restricted free oracle, and memory of about Q = N^{2/5} stored partials. Memory must be charged in any time×memory comparison.
2. **Per-attempt oracle budget at e -> 1/2**, with at most one output per attempt (**computed**):

   | m | budget | optimum (b, r) | round 1 |
   |--:|:--|:--|:--|
   | 3 | **N^{1/8}** | (3/8, 2/3) | N^{1/12} |
   | 4 | N^{1/4} | (1/4, 1) | unchanged |
   | 5 | N^{0.30} | (1/5, 1) | unchanged |
   | 6 | N^{1/3} | (1/6, 1) | unchanged |

   With many outputs per attempt the condition becomes "O(1) per returned partial". The cheapest arity an O5-type oracle could target is therefore **m = 3**: S_4 on the target side, per-variable degree 4, box shape (N^{1/4}, N^{3/8}, N^{3/8}) at the m = 3 optimum.
3. **No known oracle is anywhere near.**
   - Lattice reach demand at m = 3 is still V >= 3/4 for e <= 1/2. Re-derived with b and r free: the minimum sits at b = 1/4, r = 1.
   - Supply (**computed**, `calc/s4_reach.py` re-run): S_4(x1, x2, x3; x_R) has full-box support (125/125 monomials). Its Jochemsz-May extended Howgrave-Graham reach is **0.1214** for the balanced box and for every large-prime-shaped box tried. The margin is -0.63.
   - Groebner: beta_work >= 0.647 against a budget of 0.125.

**Representation and operation pair.**
- Representation R1: x-coordinates in [0, p), with two nested archimedean intervals (small, large).
- Sigma: translation by small-base elements, plus resolution of large legs along giant-component paths and cycles of the large-prime graph.
- **Trichotomy: partial-action.** This is Class I index calculus: the relation vector propagates only under translation by base elements, and "a decomposition exists" is the branching event priced by y.
- KN-OPEN-020 class: implicit-membership (archimedean, lattice-describable) description. It is not a bounded-degree algebraic locus.

**SO codes and the premise escaped** (statements quoted whole).
- **SO-TABLE** (LEAD-ICP-generic-table-decomposition, theorem): "Any decomposition oracle that enumerates or table-looks-up factor-base elements is a generic time/memory trade-off and obeys S*T^2 >~ N (Corrigan-Gibbs--Kogan) and T >~ sqrt(N) (Shoup); with linear algebra included the two-term model gives m = 2 >= 3 (pT_dec)^{2/3} and m = 3 only ties rho even with T_dec = O(1). Measured on generated prime-order E/F_p, 12-32 bits: exhaustive IC exponent 0.99 (m = 2) and 1.01 (m = 3), mitm 0.67 / 0.75 / 0.60 at m = 3/4/5 (4/7 at m = 7) against rho 0.50 [0.48, 0.52]; Table B gap to matched rho widens from 5.47x at log2 r = 11.9 to 13.5x at 23.4. Scope: any generic (enumeration/table) decomposition over F_p."
  - Escaped premise: "the two-term model". That model has no third channel (large-prime cycle and giant resolution). Its "m = 3 only ties rho even with T_dec = O(1)" clause is correct inside the model, and inside the statement's own scope of generic oracles. It does not extend to schemes with two large primes, where a restricted O(1) oracle gives N^{2/5}. The atlas text needs the qualifier "two-term model, no large primes".
  - The generic part of the statement stands: a table oracle for the (1, 2) partial needs a pair table of Q² = N^{4/5} entries.
- **SO-GEN** (LEAD-RHO-generic-sqrt-lower-bound, theorem): "Shoup/Nechaev generic-group lower bound: any generic algorithm needs Omega(sqrt r) group operations for a prime-order-r group (KR-RHO-13bf67). Every lead in this family moves only the constant (automorphism classes divide it by sqrt|Aut|, KR-RHO-0528e7). Scope: all generic algorithms, any field, any r."
  - Escaped premise: "any generic algorithm". A sub-generic restricted oracle must read coordinates (lattice or algebraic), so the floor is a statement about non-generic oracles only.
- **SO-ALGFB** (LEAD-ICP-algebraic-membership-factor-base, theorem): "A target-independent algebraic locus of degree d yields O(d) usable points, so a size-B algebraic base has description degree >= B/3 and membership polynomial prod(x - v) of degree B (bounded-degree factor-base theorem, IDEA-20260801-021); mean per-target yield is binomial(B+m-1, m)/N for every base of size B (KN-FIND-007 conservation; coverage gain <= 1.582, constant in N). Measured: subgroup, small_x and random bases within 7 % at 32 bits; exact mean-yield ratio 1.000000 for six geometries at N ~ 2^14..2^18 (EV-FBG-001); msolve on subgroup bases grows deg^{4.4} at m = 3. Scope: prime-order E/F_p, any base of size B."
  - Escaped premise: "algebraic locus". The interval base is archimedean.
  - The yield-conservation clause is **used**, not escaped: it fixes the mean of H3.
- **LEAD-ICE-generic-oracle-arity-cost-floor** (cost_model, no SO code): "For oracles of class ENUM, MITM and MITM_CAPPED on binary curves of prime degree n, the replicated v2 cost model has zero in-domain sub-rho cells (EV-SEMBIN-b6d042); on ECC2K-130 a free oracle at m = 3 still costs 2^68.58 against rho's 2^60.81 (KN-FIND-aa2efc); in-model, structured generic-group bounds (CHW 2026/384) and non-adaptive time-space bounds (DKM 2025/783) give the same wall. Scope: oracles that do not read curve coordinates algebraically; the FREE control does have sub-VOW cells, so the obstruction is the oracle class, not IC."
  - Consistent, not escaped. Its 2^68.58 is a no-large-prime figure. The binary 2LP column already exists internally (H-BINSTD-555991, approved: 2LP budget 2^{8.71} at m = 3). This candidate is the prime-field counterpart, with the base size freed.

**Dedup.**
- H-ICEX-87ad66 (proposed) is a one-large-prime (m-1, 1) table/lookup exchange-rate hypothesis that explicitly states "No assembled single-target ECDLP exponent moves" and leaves the IDEA-20260727-003 floor "not touched".
- H-ICEX-ab1da2 is about rank versus coverage.
- Neither carries a 2LP prime-field floor.
- The concurrent AUDIT.md, FOLD.md, report.md and PROPOSED-DIFFS.md were grepped for "2/(m+2", "2/5", "giant", "double large", "two large", "2LP" and "large prime". None derives a large-prime floor.
  - AUDIT.md AUD-4 on LEAD-ICE-relation-graph-rank-large-prime says a large-prime gain must come from (i) oracle asymmetry or (ii) "cycle elimination being cheaper than carrying L as columns", and that (ii) is at most about 0.5% of Table B S.
  - That holds at m = 2 and at measured sizes. PC2 shows that (ii) is the exponent lever at m >= 3 in the free-oracle limit, because there no-LP linear algebra Q² is the binding term. The two statements are complementary.
- `lead_atlas.py --match` and `build_frontier_map.py --match` both name KR-IC-a4dd54 (GTTD) as nearest prior work.
- **Novelty: adaptation** (known technique, new setting with a free base size). It advances LEAD-ICE-relation-graph-rank-large-prime and LEAD-ICE-charged-toy-ic-exponent-vs-rho. It is not a new lead.

**First discriminating step.** This is the shared free-oracle large-prime ladder, section 4, m = 3 arm, plus a zero-compute algebra step. The algebra step: write the large-prime model (H1, H3, H4 and the output constraint) as a second theorem family beside ArityOracleThreshold.lean. It is proposed only; nothing is edited here.

The outcomes are keyed on per-rung quantities checked against H1/H3 predictions, not on a fitted four-size exponent. EV-ICEX-16e3ec found such a fit unidentifiable at these sizes (CI [0.10, 2.32]), and fixed costs give spurious sub-1/2 slopes there. Once H1, H3 and H4 are validated, the exponent follows from the derivation.

Outcomes:
- **Validated.** At every rung (20, 24, 28, 32 bits):
  - measured attempts to the giant threshold / A* = N/(8·Q·Q_s) is in [0.5, 2];
  - giant fraction and E - V + C match G(n, M) and the rewire null within their 95% band;
  - the relabelled Z/N control agrees;
  - W/(0.886·sqrt(N)) is below 1 at >= 28 bits for the 0 and 0.1 GAE linear-algebra weights.

  Then:
  - record the scope clause "no large primes" on IDEA-20260727-003, on the SO-TABLE m = 3 clause and on the concurrent threshold diffs;
  - LEAD-ICE-charged-toy-ic-exponent-vs-rho stays **open_blocked**, with the O5 acceptance target re-aimed to m = 3 with large primes at N^{1/8} per attempt, and best_measured = the per-rung W/(0.886·sqrt(N)) ratios.
- **Contradicted.** Measured/predicted attempts above 2 at two or more rungs with a growing trend, or giant or cycle depletion against the null:
  - **closed_obstructed(measured)** for prime m = 3 large primes; the no-LP "tie" stands as written.
- **Drift.** A systematic drift of measured/predicted across rungs that stays inside [0.5, 2], or a deviating relabelled control:
  - **open_next_step** (instrument audit), best_measured = the per-rung ratios.

**Tier.** X: it moves the exponent of the free-oracle floor and the gate. It realises no speedup.

**Predicted gain** (H1, H3, H4).
- Free-oracle exponent: 0.400 at m = 3 (no-LP 0.500), 0.333 at m = 4 (no-LP 0.400).
- Toy constant at 32 bits with Q = N^{0.4} and Q_s about 30: W/(0.886·sqrt(N)) of about 0.17 at 0.1 GAE per linear-algebra op, and about 0.7 at 1 GAE per op. The ratio falls as N^{-0.1}.
- Realised gain with any known oracle: 0.

**Cost.**
- Implementation: 2 days, with the m = 3 arm sharing PC1's harness.
- Compute: about 10 core-hours for the 20-32-bit ladder in compiled code (the oracle is uncharged; it is exhaustive at Q_s·Q per attempt).

**Self-kill risk.**
- H3 could fail if structured bases concentrate legs. EV-RELN-3c9a24's null match argues against that.
- The free-oracle statement could be judged "GTTD, obviously". Its decision value is that it reverses a stated "tie/empty" claim that three records and one pending theorem diff rely on.
- It supplies no oracle.

**--match phrasings** (top hits from this session's runs).
1. Own: "double-large-prime oracle-order threshold 2/(m+2-2k): free three-point decomposition oracle reaches N^(2/5) with two large primes". Top hits: LEAD-ICE-generic-oracle-arity-cost-floor (17), then LEAD-ICE-relation-graph-rank-large-prime (12).
2. Plain: "with two large primes a perfect three-point decomposition solver would beat rho over prime fields". Top hits: KR-IC-a4dd54 (17), then LEAD-ICE-relation-graph-rank-large-prime (15).
3. Obstruction vocabulary: "two-term model with linear algebra included: m = 3 only ties rho even with T_dec = O(1); free oracle at m = 3 still costs more than rho". Top hits: LEAD-ICE-generic-oracle-arity-cost-floor (16), then LEAD-ICB-orbit-linear-algebra (13), then LEAD-ICP-generic-table-decomposition (10).

---

## 4. Shared instrument for PC1 and PC2: the free-oracle large-prime ladder (prime field)

One harness, two arms, on generated prime-order E/F_p at log2 N in {20, 24, 28, 32}. The oracle is exhaustive and **uncharged**. Charged work is attempts, plus formed partials, plus linear-algebra ops priced at 0, 0.1 and 1 GAE per op.

**m = 2 arm (PC1).**
- Full base {x < n} with n in {N^{0.4}, N^{0.5}} (sign-folded).
- Exhaustive pair enumeration per target.
- Record M*/n at the first target dependency (a balanced cycle, or a complex component) and the attempts to it.

**m = 3 arm (PC2).**
- Q = ⌈c1·N^{0.4}⌉ and Q_s = ⌈c2·N^{0.2}⌉, with c1 in {1/2, 1, 2} and Q_s about 15-60.
- The oracle returns the (1 small, 2 large) and (2 small, 1 large) partials. For each small P_s it hash-checks pairs over F: Q_s·Q point operations per attempt, uncharged.
- Record:
  - attempts and partial counts;
  - giant fraction and cycle rank E - V + C;
  - attempts to rank Q_s + 1 over the small base;
  - the free work W(N).
- **Prediction** (H1, H3): the giant threshold is at 2A·y_2/Q = 1, i.e. A* = N/(8·Q·Q_s) at m = 3. That is about 900 attempts at 32 bits with c1 = c2 = 1.

**Controls.**
- Degree-preserving rewire null of the partial graph.
- Relabelled Z/N group with a random base of the same size. Under conservation this should match.
- A planted dependency as positive control.

**Cost.** The m = 3 arm at 32 bits is about 1.2e6 uncharged point operations per attempt × about 2,500 attempts, i.e. 3e9: 1-3 core-hours. The whole ladder is under 10 core-hours, and one harness serves both leads.

---

## 5. Candidate PC1 (prime, B1/B3): attempt-edge lemma. Arity-2 decomposition has exponent exactly 1/2 under any oracle and any large-prime scheme

**Bottleneck.**
- B1 and B3 at m = 2, the arity of every Table B recipe ("folded, walked, m = 2").
- The two open m = 2 large-prime lanes:
  - LEAD-ICP-residual-partial-relations: the 1LP sweep, exponent (1+beta)/2.
  - LEAD-ICE-relation-graph-rank-large-prime: the 2LP multigraph at B = p^{1/5}, B2 = p^{2/5}, edge density "against the 1/4 supercritical threshold".

**External ingredients.**
- Random-graph cycle statistics: Erdos-Renyi (1960) and Janson-Knuth-Luczak-Pittel (1993), recalled.
- Lenstra-Manasse large-prime cycle accounting (recalled).
- GTTD's n = 2 boundary (retrieved, as in section 3).

**Derivation (under H1).**
- Setup:
  - The full base is n sign-folded x-classes.
  - Each attempt is a fresh target R = aP + bQ, costing at least 1 GAE.
  - The oracle (any oracle, including a free non-generic one) returns all R = ±P_i ± P_j, each costing at least 1 GAE to form.
- Expected relations per attempt: y = 2n²/N.
- Relations are edges of a multigraph on n vertices. In G(n, M = cn) the number of cycles is Poisson with mean -½·ln(1-2c). A cycle is parity-balanced with probability 1/2, and an unbalanced cycle only resolves one vertex.
- So P(dependency) is about 1 - (1-2c)^{1/4}, which reaches 1/2 at **c = 15/32 = 0.469**.
- Total cost: T >= c·N/(2n) + c·n >= c·sqrt(2N), minimised at n = sqrt(N/2), for every B, B2, small/large split and oracle.
- The large-prime threshold law of section 3 gives the same at m = 2: e = 2/(2+2) = 1/2 for k = 0.

**The claim, stated precisely.**
- The m = 2 exponent is exactly 1/2 for every oracle.
- The free-oracle constant floor is c·sqrt(2) = 0.66·sqrt(N). That is 0.75 of ideal negation-rho sqrt(pi·N/4) = 0.886·sqrt(N): at most **1.34x constant headroom** before any oracle or linear-algebra cost.
- At toy scale measured rho.negation sits 1.45x above its floor, so a realised m = 2 scheme with a non-free oracle is not expected to beat it. That expectation is a constant question, not part of the lemma.

**Computed, from the frozen design table of the c5a377 lane.** Source: GOAL-RELN-001 BATCH-9fba5a, TASK-20261001-5a45b1, `exact_yield_budgets_out.json`, label-free. This is arithmetic on frozen design budgets, not a run.

| bits | A_1/sqrt(pi·q/4) | A_1·B2/q |
|--:|:--|:--|
| 16 | 2.92, 3.00, 3.60 | |
| 20 | 4.08, 4.44, 4.66 | |
| 24 | 5.14, 5.22, 6.08 | |
| all | | 0.89-1.09 |

The A_1·B2/q column confirms attempts of about q/B2 = q^{3/5}. The ratio therefore grows as about q^{1/10}, as the lemma predicts.

**Corollaries.**
- (a) **Prediction**: whole-solve S/matched rho in the c5a377 lane is at least these attempt ratios (oracle uncharged) and keeps growing. Its discriminating quantity, delta against 1/4, cannot change this.
- (b) LEAD-ICP-residual-partial-relations: under the lead's own test the ladder should read as an IC-baseline improvement with relation exponent (1+beta)/2 below 2/3. That matches report.md AUD-4, which derives the same 2/3. On ECDLP cost the lead is dominated by bsgs.negation and rho.negation at every beta, by the lemma.
- (c) Table-oracle variant (H2): S + T >= 1.5·N^{2/3}, the same leading constant as the no-LP optimum. An LP arm on the table recipe is predicted at 1.00 [0.9, 1.1]. Linear algebra is 0.0-0.4% of Table B S.

**Representation and operation pair.**
- Representation R1: x in [0, p), split small/large by an archimedean bound.
- Sigma: translation by full-base elements, plus cycle combination on the large-prime graph.
- **Trichotomy: partial-action** (Class I).

**SO codes and premises.** PC1 is a closing proof. It extends obstructions past their premises; it escapes none.
- SO-TABLE (quoted whole in section 3). Premise removed: "enumerates or table-looks-up". At m = 2 the sqrt(N) floor holds for every oracle under H1.
- SO-GEN (quoted in section 3). Premise not needed: "any generic algorithm". PC1 is a second, non-generic wall at m = 2, conditional on H1.
- SO-ALGFB (quoted in section 3). Used: y is the conservation mean.

**Quantifier scope.**
- The lemma covers non-adaptive target schedules under H1.
- Adaptive schedules (decompose L_i + S to grow edges at a chosen vertex) give rows whose other legs are still uniform over the base: P(both in W) = (|W|/n)². I expect c to be unchanged, but the adaptive case is open and stated as open.

**First discriminating step.**
1. Write the one-page lemma with explicit quantifiers.
2. Run the m = 2 arm of the shared ladder (section 4).
3. Read the attempts to the first dependency from the existing EXP-RELN-c5a377 v4 generator. No new generator is needed.

Outcomes, keyed per rung (no fitted exponent):
- M*/n in [0.3, 0.7] at every rung, and attempts to the first dependency >= 0.5·c·N/(2n) at every rung:
  - LEAD-ICE-relation-graph-rank-large-prime, m = 2 arm → **closed_obstructed(proof)** on the exponent question. Whole-solve S stays a constant question.
  - LEAD-ICP-residual-partial-relations → **closed_dominated** for ECDLP cost; its IC-baseline ladder becomes optional engineering.
  - LEAD-ICP-prime-ic-constant-engineering keeps open_next_step as engineering only.
- M*/n < 0.1 at two or more sizes (dependencies far earlier than random) → **open_next_step**, best_measured = M*/n. That would be a structured-coincidence signal contradicting H1.
- Attempts below c·N/(2n) by more than 2x at any rung → **open_next_step** (the accounting is wrong; instrument audit).

**Tier.** X: a proof that decides exponent questions. It moves no exponent.

**Predicted gain.**
- 0 in exponent.
- Free-oracle constant floor 0.66·sqrt(N), at most 1.34x below ideal negation-rho (H1).
- LP arm on the table recipe: 1.00 [0.9, 1.1] (H2).

**Cost.** Derivation 0.5 day. The m = 2 arm takes 1 day and under 5 core-hours, shared with section 4.

**Self-kill risk.** It may be judged implied by Gaudry n = 2 plus SO-TABLE. Its value is that it closes two open lanes without the 16-32-bit ladders they ask for.

**--match phrasings** (this session).
1. Own: "attempt-edge lemma: arity-2 point decomposition with any oracle and any large-prime cycle scheme has exponent exactly 1/2, floor 0.66 sqrt(N)". Top hits: LEAD-ICE-rootfind-pairtable-oracle (16), then LEAD-ICE-gpu-rootfind-oracle (13), then a 12-way tie including LEAD-ICE-relation-graph-rank-large-prime and LEAD-ICP-generic-table-decomposition.
2. Plain: "splitting a point into two factor-base points has square-root cost even with large primes and a perfect solver". Top hit: LEAD-ICE-relation-graph-rank-large-prime (13).
3. Obstruction vocabulary: "decomposition oracle enumerates or table-looks-up factor-base elements m = 2 two-term model residual partial relations". Top hits: LEAD-ICP-residual-partial-relations (16), then LEAD-ICP-generic-table-decomposition (14).

### 5a. B3 consistency check (not a candidate). The N^{1/6} law against rows already on the board

**Table B, same recipe**, S/sqrt(r):

| log2 r | IC | rho | ratio |
|--:|--:|--:|--:|
| 14.0 | 13.1 | 2.03 | 6.43 |
| 18.0 | 8.41 | 1.45 | 5.82 |
| 23.4 | 14.0 | 1.04 | 13.5 |

About 90% of the 2.10x log-widening from 14.0 to 23.4 bits comes from the rho reference converging to its floor (0.886).

**Planner-validation table**, S(plan)/S(rho) measured. These are already on the board: planner plans, partly on supplementary curves, so a different recipe and a different curve set.

| curve | log2 r | S(plan)/S(rho) |
|:--|--:|:--|
| fp24 | 24.00 | 14.4 [11.6, 18.4] |
| fp26 | 25.35 | 14.6 |
| fp28 | 28.00 | 21.7 [17, 28.3] |
| c24 | 23.47 | 12.6 |
| c28 | 27.69 | 21.8 |
| c30 | 29.62 | 25.8 [19.9, 35.2] |

**Computed slopes** of log2(ratio) per bit:
- fp24 → c30: log2(25.8/14.4)/5.62 = **0.150**.
- c24 → c30: log2(25.8/12.6)/6.15 = **0.168**.

Both are against 1/6 = 0.167 for an N^{2/3} recipe divided by N^{1/2} rho. The existing rows are consistent with PC1(c)'s N^{1/6} law. Round 1's "22-23x at fp28" is not a prediction: 21.7 is already measured.

---

## 6. Candidate KB1 (binary, B4): the double-large-prime time-memory frontier of the writability wall

This advances the open LEAD-ICB-large-prime-variants next_action (EXP-BINSTD-e066d8 Stage 0) by adding the writability column. It is not filed as a new lead.

**Bottleneck.** B4: the writability wall.

LEAD-ICP-icperf-writability-boundary (closed_obstructed, cost_model), quoted whole: "At the best viable arity the descended ANF exceeds the whole per-decomposition rho budget by +6.3 bits (n = 233), +18.8 (283), +24.2 (113), +25.6 (127), +40.8 (ECC2K-130) and +37.4 (K-163); the cost is paid before any solver runs. Scope: standardised binary curves with n <= 283, unchained descended ANF; the crossover is inside (283, 409]."

Its "best viable arity" and its per-decomposition budget were computed without large primes, with a dense C(vars, <= 3·2^{m-2}) ANF count.

**External ingredient.** GTTD's (m-2, 2) partial form (retrieved), in the version the program already approved for binary pricing (H-BINSTD-555991, H-621974-1..3). The new step applies it to the writability quantity, with:
- several partials per attempt;
- total work W = attempts·max(2^ANF, p_2) + 2^{l'};
- a memory cap 2^{l'} on stored partials;
- the block-multidegree support of the descended S_{m+1}: Boolean degree at most w per variable block (w = 2 at m = 3, 3 at m = 4), so the count is at most the product of C(l_block, <= w).

**Computed.** Budgets and LA-capped l_s are read-only from EXP-ICPERF-783e9e `budget_table.json`, theta = 1. Columns are the time deficit log2 W - log2 rho:
- round-1 convention (dense, p_2 <= 1);
- total work with a memory cap, dense;
- total work with a memory cap, block support.

| n | no-LP dense / block | 2LP round-1 convention | 2LP dense, cap 2^50 / 2^60 / none | 2LP block, cap 2^50 / 2^60 / none |
|--:|:--|:--|:--|:--|
| 113 | +24.2 / +19.4 | +21.90 (m3) | +15.1 / +7.9 / +7.9 (m3); +12.9 / +7.2 / +7.2 (m4) | +12.0 / +6.3 / +6.3 (m3); +7.3 / +3.9 / +3.9 (m4) |
| 127 | +25.6 / +20.7 | +20.01 (m3) | +16.5 / +7.8 / +5.5; +9.3 / +2.0 / +2.0 | +13.6 / +4.7 / +3.8; +4.0 / **-1.1 (2^57)** / -1.1 |
| 131 (ECC2K-130) | +40.8 / +36.0 | +23.30 (m3, 2^51) | +24.2 / +15.4 / +8.7; +22.0 / +14.1 / +8.2 | +21.1 / +12.1 / +6.7; +16.4 / **+8.0** / +4.7 (2^65) |
| 163 (K-163) | +37.4 / +32.5 | +21.37 (m3) | +32.9 / +24.0 / +5.6; +23.9 / +15.8 / +1.8 | +29.9 / +21.0 / +3.8; +18.6 / +10.2 / -1.4 (2^74) |
| 233 | +6.3 / +1.1 | +13.74 (m3) | n/a / +38.4 / -3.9; n/a / +10.7 / -17.4 | n/a / +35.6 / -5.5; n/a / +5.5 / -20.4 |

(n/a: the LA-capped l_s exceeds the cap. The no-LP column is the m = 4 cell, the convention of the quoted statement. At n = 127 the table's minimum over m is +24.46 at m = 3, and its `minimum_viable_arity` field reads 3 at n = 113, 127 and 233.)

Readings:
- On ECC2K-130 the block-support deficit drops from **+36.0 (no-LP)** to **+16.4 at 2^50** and **+8.0 at 2^60** stored partials (m = 4). That is time only. It stays positive at every memory cap.
- Linear algebra is LA-capped near rho (2^{60.0} at n = 131), so the total can never fall more than about 1-2 bits below rho in this model.
- At n = 127, m = 4 the writability deficit is -1.1 at 2^57 memory. Adding the 2^{58.0} linear algebra gives a total of about 2^{59.1} against rho 2^{59.33}: a tie in time. Under time×memory against vOW it is dominated, because 2^57 entries far exceed the memory of a DP rho run.
- Apart from n = 127, the deficits go negative only with memory near rho-scale: 2^74 at K-163 (rho 2^{77.2}), and 2^90-2^105 at n = 233.

**Representation and operation pair.**
- Representation R1: x-coordinates in nested F_2-subspaces of a polynomial basis, as a Weil-descended ANF.
- Sigma: translation by small-subspace base elements, plus large-prime graph resolution, with signed-Frobenius canonicalisation of large legs.
- **Trichotomy: partial-action.**

**SO codes and premises.**
- The writability statement (quoted above): escaped premises are "best viable arity" (computed without large primes) and the implicit dense support. The conclusion survives as a time-memory frontier.
- SO-FROB (LEAD-ICB-frobenius-orbit-factor-base, proof), quoted whole: "For E/F_q attacked over F_{q^n}, the base {x(P) in V} is pi-stable exactly when V is sigma-stable, the stable subspaces form an arithmetic lattice fixed by the factorisation of X^n-1 over F_q, and the gain is exactly n on relations (n^2 on LA) and never more (H-FROB-6774fb supported, DEC-20260923-e6cd5d; the tau-factor-base pilot finds the per-attempt decomposition probability at matched |FB| equal to the birthday value for orbit-union, normal-basis and polynomial bases, n = 11..23). At prime n with ord_n(2) = n-1 (131, 163) the usable stable dimensions are empty (H-BINSTD-b1f016 replicated). Rho gets the matching sqrt(2n) from the same automorphisms, so the matched gap is unchanged. Prime-field phi-stable bases (EQIC) are bounded by the eigenvalue-subgroup order (at most 6) and measured +4% Ir at order 6 on j = 0. Scope: Koblitz/subfield curves over F_{2^n}, n prime, toy to n = 61 measured; ECC2K-130 by structure."
  - Not escaped. No orbit gain beyond the table's convention is used.
- LEAD-ICB-decomposition-encoding-and-sat (measured), quoted whole: "Every SAT or enumeration method measured has per-attempt UNSAT cost 2^{alpha l} with alpha ~ m (WDSat 2.9985 bits per unit l at m = 3, reproducing 2^{3l}/3!; alpha 4.09-4.33 at m = 4, l = 3..5), while beating rho needs alpha < m/2 - 1; at m = 3, 4 the measured families extrapolate 50-150 bits above budget at n = 131. Ladders n = 11..31: no arm grows slower than the enumeration floor (m = 3 slopes 0.53-0.58 vs floor 0.21; m = 4 wide chain 0.805 vs 0.333). Encoding levers are constants: S_m symmetrisation saturates product spaces at m >= 5 at balanced l (H-BINSTD-770ec3 supported), closure outcomes are basis-invariant (Proposition B), reduction-polynomial weight is a constant confound, Nagao coset yield weakened vs chained S_3, trace replay is a constant at most."
  - Not escaped. A writability deficit <= 0 is necessary, not sufficient; the solver wall stands.

**First discriminating step.** Zero to low compute.
1. Append the 2LP column (all three conventions) to the writability table, with theta in {1/2, 1} and H-621974-3's cycle weight added to the LA charge.
2. Replace the block bound with the exact support of the descended S_4 and S_5 at the frontier points (n = 127 and 131: l_s = 35 or 29, l' = 50-60), by symbolic monomial counting. This takes CPU-minutes.
3. Do the time×memory comparison against vOW in the same step.

Outcomes:
- Every standardised n <= 163 still positive under exact support at memory <= 2^60:
  - the writability row stays **closed_obstructed**, with a proposed scope clause "(no large primes; with 2LP a time-memory frontier, ECC2K-130 +8.0 bits at 2^60)";
  - the column becomes Stage 0's predicted row for EXP-BINSTD-e066d8 under LEAD-ICB-large-prime-variants.
- A cell at <= 0 under exact support whose time×memory is not dominated by vOW (n = 127, m = 4 is the nearest) → that cell is **open_next_step** under LEAD-ICB-large-prime-variants (a solver question at the 2LP budget), best_measured = the deficit.
- If it is dominated under time×memory → **closed_dominated** for that cell.

**Tier.** I: constant, end-to-end at fixed deployed n. It relocates a wall and moves no exponent.

**Predicted gain** (H3, H5, theta = 1).
- ECC2K-130 writability deficit +36.0 → +16.4 bits at 2^50 memory and +8.0 at 2^60 (time only). No ECC2K-130 attack.
- n = 127 per-attempt ANF deficit at about -1 bit with 2^57 memory, so the total is about tied with rho in time.

**Cost.** 0.5-1 day. CPU-minutes.

**Self-kill risk.**
- Conventions (theta, signs, orbit) move numbers by 1-3 bits.
- The memory-charged reading likely dominates every <= 0 cell.
- Stage 0 of EXP-BINSTD-e066d8 may already plan this column. If so, this is its pre-registered prediction, not a new lead.

**--match phrasings** (this session).
1. Own: "double-large-prime time-memory frontier of the ECC2K-130 writability wall: descended ANF block support against the 2LP per-attempt budget". Top hit: LEAD-ICP-icperf-writability-boundary (16).
2. Plain: "with two large primes and lots of memory each decomposition attempt gets a bigger budget so a bigger equation system fits". Top hits: LEAD-ICP-icperf-writability-boundary (13), then LEAD-ICE-relation-graph-rank-large-prime (12).
3. Obstruction vocabulary: "descended ANF exceeds the whole per-decomposition rho budget at the best viable arity unchained descended ANF". Top hits: LEAD-ICP-icperf-writability-boundary (14), then LEAD-ICE-generic-oracle-arity-cost-floor (13).

---

## 7. Candidate KB2 (Koblitz, B5): a Jacobian carrier is a cover. The Weil-restriction adjunction lemma

**Bottleneck.** B5, LEAD-ICB-ecc2k130-jacobian-carrier (open_next_step).
- Its next step is a toy ladder at n = 11 and 13 testing whether P_A divides P_C.
- Its payoff: hyperelliptic or plane index calculus on a genus 130-300 carrier would cost about 2^{37.2}. This is the function-field-sieve-analogue side of this field.
- Its source (IDEA-20261002-8f26ce) says the carrier "is not a cover of the target", and KN-OPEN-095df5 asks for "an explicit translation and a degree".

**External ingredients.**
- Weil-restriction adjunction, Hom_k(X, Res_{K/k} Y) = Hom_K(X_K, Y): Bosch-Lutkebohmert-Raynaud section 7.6, recalled.
- Tate's isogeny theorem (recalled).
- Subexponential index calculus in high-genus Jacobians over small fields: Enge-Gaudry 2002 (recalled).
- DiPippo-Howe for the counting side (**retrieved**).

**Lemma** (derivation; A ⊂ R = Res_{F_{2^131}/F_2}(E) is the trace-zero part, assumed simple as the lead assumes).
1. P_A | P_C ⇒ Hom_{F_2}(Jac C, A) ≠ 0 (Tate) ⇒ Hom_{F_2}(Jac C, R) ≠ 0.
2. By adjunction, Hom_{F_{2^131}}(Jac(C)_{F_{2^131}}, E) ≠ 0.
3. With a degree-1 base divisor, the Albanese property gives a non-constant φ: C_{F_{2^131}} → E.
4. Conversely, a curve C/F_2 with a non-constant φ: C → E over F_{2^131} maps to every conjugate E^{σ^i} through φ^{σ^i}. The image of Jac C in ∏E^{σ^i} is F_2-rational, so it contains A up to isogeny (unless it lands in E_0). Hence g(C) >= 130.

So **every carrier is a cover of E over F_{2^131} by a curve over F_2, and conversely**. The "explicit translation" is φ, and the "degree" is deg φ. The source's "not a cover" holds only for auxiliary curves with 131 | #Jac(F_2), which is weaker than the lead's test.

**H6 re-computed** (`calc-r2/dipippo_howe.py`). The formula is retrieved: #I(q, n) ~ v_n·r(q)·q^{n(n+1)/4}, with v_n = (2^n/n!)·∏_{j=1}^n (2j/(2j-1))^{n+1-j} and r(2) = 1/2. Curves are counted at about q^{3g-3}. Under uniform L-polynomials, the expected number of carriers of genus g for dim A = d is q^{3g-3}·#I(g-d)/#I(g).

| n (dim A) | genus | expected carriers |
|:--|:--|:--|
| 11 (d = 10) | g = 10 | 0.006 |
| 11 (d = 10) | g = 10..14 | 0.012 |
| 13 (d = 12) | g = 12..16 | 1.6e-4 |
| 5 (d = 4) | g = 4 | 0.77 |
| 5 (d = 4) | g = 4..8 | **92** |

The lead found no carrier at n = 5 through genus 8; its own heuristic predicts about 0.42. The uniform model is therefore falsified at n = 5. DiPippo-Howe's Theorem 1.2 also warns that the asymptotic needs q ≫ 6^{n²}.

**Conclusion:** the power of the n = 11/13 toy ladder **cannot be computed** from H6. The decision-relevant content is the lemma, not a count.

**Representation and operation pair.**
- Representation R2/R3: the point becomes a divisor class on C/F_2 through R = E_0 × A. That is an injective homomorphism on the r-part, a change of group representation.
- Sigma: the F_2-Frobenius, plus pullback and norm along φ. The index calculus on Jac C(F_2) uses places of degree <= d.
- **Trichotomy: partial-action.** The transfer is lossless, and the subsequent index calculus is Class I.

**SO codes and premises.**
- **SO-COVER** (LEAD-TRF-same-field-genus-g-embedding, theorem), quoted whole: "Tate multiplicativity gives #Jac(C)(F_p) = N * #A(F_p) with #A = Theta(N^{g-1}); genus-g index calculus costs O~(q^{2-2/g}) >= q for g >= 2, at least a full exponent above rho's N^{1/2}; quadric-pencil and quartic models of E itself are isomorphic models with the same group. Scope: prime-field source curves, any same-field cover (DEC-20260902-4c82fd)."
  - Escaped through its Scope: the source is an extension-field Koblitz curve, the cover descends to F_2, and Jac C is a large-genus, small-field Jacobian where index calculus is subexponential.
- **SO-FROB** (quoted in section 6): not used.
- KR-IC-791cb7 / KR-IC-5ea2f8 ("N prime ... not weak under either attack") cover only the GHS/Artin-Schreier family. The KRMAP has no genus lower bound for general covers, and the lemma's g >= 130 bound is the only one available.

**First discriminating step.**
1. Write the lemma (half a page) and attach it to IDEA-20261002-8f26ce and KN-OPEN-095df5.
2. At n = 7 (1,536 carriers found), exhibit φ and deg φ for 10 carriers. This is the sanity check; there the Weil-restriction structure supplies φ.

Outcomes:
- Lemma confirmed at n = 7 → re-scope the lead into the cover/transfer family (beside LEAD-TRF-cover-catalog-jacobian-transfer) and replace the P_C-divisibility ladder with a cover-degree search.
  - Disposition **open_next_step**, best_measured = the n = 7 cover degrees.
  - Or **closed_known**, if a reviewer accepts that the GHS/Hess literature bounds every cover of degree <= deg_max.
- An n = 7 carrier with no φ → the carrier test or a premise (A simple) is wrong → **open_next_step** (instrument audit).

**Tier.** X: it decides an exponent-moving route.

**Predicted gain.** 0 bits on ECC2K-130. The decision value is the lemma. H6 cannot supply the ladder's power.

**Cost.** 1-2 days. Compute: hours.

**Self-kill risk.**
- The lemma is standard.
- The field fit is thin; only the payoff side comes from this field.
- The lead may mean "carrier" in a weaker sense, in which case its divisibility test is mis-specified.

**--match phrasings** (this session).
1. Own: "Weil restriction adjunction: a Jacobian carrier of the trace-zero variety is a cover of E over F_2^131". Top hits: LEAD-ICB-ecc2k130-jacobian-carrier (17), then KR-IC-5ea2f8 (15).
2. Plain: "any genus-130 curve over F_2 whose Jacobian contains the ECC2K-130 group must map onto the elliptic curve". Top hits: LEAD-ICB-ecc2k130-jacobian-carrier (11), then KR-IC-791cb7 (9).
3. Obstruction vocabulary: "same-field cover Tate multiplicativity genus-g index calculus costs O~(q^{2-2/g}) any same-field cover Jacobian carrier". Top hits: LEAD-TRF-same-field-genus-g-embedding (15), then KR-IC-a4dd54 (14).

---

## 8. Ranking

1. **PC2.** It reverses a stated tie/empty claim that three records and one pending theorem diff rely on, and it re-aims O5 to m = 3 at N^{1/8}.
2. **PC1.** It closes two open m = 2 lanes by proof.
3. **KB1.** It turns a fixed wall into a time-memory frontier. Every cell stays dominated.
4. **KB2.** A lemma that re-scopes the lead.

Every candidate's realised ECDLP gain with known oracles is 0.

---

## 9. Heuristics (numbered)

- **H1** (random large-prime graph). Partial-relation graphs from prime-field point decomposition behave like G(n, M) conditional on degrees:
  - the first m = 2 dependency is at median c = 15/32;
  - the giant forms at average degree 1;
  - cycles in the supercritical regime have length O(log n).

  Support: EV-RELN-3c9a24 (cycle rank matched the rewire null). Validation: section 4.
- **H2** (table hit-count). Each lookup into an S-entry pair table hits independently with probability S/N.
- **H3** (Poisson partials). Per-attempt counts of (m-j small, j large) partials are Poisson with mean 2^m·Q_s^{m-j}·Q^j/((m-j)!·j!·N), and large legs are uniform over the full base. The mean is exact by conservation (KN-FIND-007); the shape is heuristic.
- **H4** (cycle-weight linear algebra). Sparse linear algebra on cycle-combined rows costs w·Q_s² with w = O(m log Q), above the giant threshold.
- **H5** (ANF support). The block-multidegree product bound, at most the product of C(l_block, <= w), is an upper bound on the descended S_{m+1} support. The table's dense count is a weaker upper bound.
- **H6** (carrier count). Uniform L-polynomials at the DiPippo-Howe density. **Falsified as a calibrated model** at n = 5 (section 7). Kept only to show that the ladder's power is not computable.
- **H7** (lattice strategy). JM-extended reach is within a small constant of optimal-shift reach for full-box supports. A 6x gain would be needed.
- **H8** (mean-field percolation). With mixed partial types, a large vertex is resolved once some incident partial has every other leg resolved. The mean-field fixed point w = mu·(1+w)^{m-1} governs the take-off from the small base (K14).

---

## 10. Killed candidates (self-killed, with reasons)

K1-K13 are carried from round 1. This session re-derived each reason and agrees.

- **K1. Small-model integer parabola descent for S_3.** The targets need small x_R (about p/X generic steps each). The base-only version forces B >= p^{1/2}, with linear algebra costing p. As K < 1 it collapses to xedni (closed_known, JKSST).
- **K2. Farey / rational-reconstruction height base.** At m = 2 it is killed by PC1. At m = 3 the image surface is a quartic.
- **K3. Special-q / lattice sieve in L(kO).** Hyperplane sieving is genuine, but with no size the yield per hit is the generic one. **Derived this session** (by hand, not by script): sieving all lines in a (lambda, mu) box costs (p/B)² per relation, against p/B for pair enumeration.
- **K4. Smooth-x factor base.** Multiplicative smoothness of x has no group-law meaning.
- **K5. ECM stage-2 / FFT-continuation membership.** O~(|F|) per target, exponent 1.
- **K6. Bernstein batch smoothness / remainder trees.** On E(F_p) there is nothing smooth to batch.
- **K7. den Boer-Maurer-Wolf smooth-order auxiliary curve.** It needs a DH oracle; SO-CHEON (LEAD-RHO-cheon-aux-acquisition), whose Scope is "generic algorithms on any curve; non-generic acquisition is not excluded", and no non-generic acquisition is known.
- **K8. Kohel-Shparlinski character-sum control of yield variance.** The error term is vacuous below |F| of about p^{1/2+o(1)}, and every relevant base is smaller.
- **K9. Char-2 m = 2 polynomial-basis linearisation.** The split condition restores 2^l enumeration.
- **K10. GTTD rows of the ECC2K-130 free-oracle floor.** Duplicates H-BINSTD-555991.
- **K11. Descent trees / special-q individual logs.** 0.3-1.4% of S; not a bottleneck.
- **K12. Constant engineering of the m = 2 recipe as a crossover route.** The ratio grows as N^{1/6} (section 5a).
- **K13. Joux-Vitse overdetermined Coppersmith oracle with large primes at m = 3.** Folded into PC2: reach 0.1214 against demand 0.75.
- **K14 (new). Three or more large primes (Leyland-Lenstra-Dodson-Muffett-Wagstaff 3LP, recalled).**
  - Mean-field percolation from the small base (H8): w = mu·(1+w)^{m-1} with mu proportional to attempts. Take-off needs mu >= mu*.
  - With 1-2 large legs, mu* = 1/(m-1). With all legs allowed, mu* = (m-2)^{m-2}/(m-1)^{m-1}.
  - **Computed** (`calc-r2/lp_floor_r2.py`) attempt-savings ratio: 2.00 (m = 3), 2.25 (m = 4), 2.37 (m = 5), 2.59 (m = 12), tending to e.
  - The attempts exponent is unchanged, since y_1·y_3 = y_2². Resolution rows become sums over trees, so their weight grows up to Q_s, and the 3-leg partials need an oracle for the larger box.
  - Killed as an exponent lever. It is at most a constant of e, recorded as a constant for any future 2LP arm.
- **K15 (new). Vallee's quasi-uniform generator of small modular squares (Math. Comp. 1991, recalled), used on the m = 2 S_3 parabola.**
  - In (s, t) = (x1+x2, x1·x2) the condition is a conic whose points in the box can be sampled.
  - But the box holds 2B³/p conic points, of which only B²/p have a square discriminant. The factorisation condition costs about B per relation, which is enumeration.
  - The real object is a genus-1 curve, and Vallee's method needs genus 0.
- **K16 (new). Pollard-Strassen / Bostan-Gaudry-Schost polynomial-product membership (SIAM J. Comput. 2007, recalled).**
  - The interval base has the Pochhammer membership polynomial, evaluable in O~(sqrt(Q)).
  - The product over pairs then factors as c^Q·Φ(x(T-P_a))·Φ(x(T+P_a)), so per target it costs Q^{1.5}. That is worse than hashing, at O(1) per lookup.
- **K17 (new). Two-sided NFS analogue (a target and its image on an isogenous E').** Logs transport through φ, so the second side is the base φ^{-1}(small-x) on E. That is a larger target-independent base, and conservation applies. No gain.
- **K18 (new). Pomerance early abort.** It needs a partial-size invariant that predicts smoothness after removing small factors. E(F_p) has no size that decreases under subtraction, so a predictor would be a coordinate statistic (LEAD-EXO-coordinate-statistic-leakage census, random level).
- **K19 (new). Schirokauer maps / virtual logarithms.** A linear map E(F_p) → Z/N that is not identically 0 is the DLP itself, since End(G) = Z/N. SO-ENDO (LEAD-STR-endo-scalar-action-generic): "Scope: any prime-field or binary curve, any size, prime-order subgroup."

---

## 11. Fields searched with nothing surviving

- NFS/FFS special-q lattice sieving on E/F_p: no periodic divisibility (K3).
- Canfield-Erdos-Pomerance / Dickman transfer: the rate transfers, the test does not (section 2).
- ECM stage-2 batching (K5), Bernstein batch smoothness (K6), and the Pollard-Strassen / BGS product (K16).
- Function-field sieve over F_p(t): closed by xedni alpha = 3 (LEAD-ICP-xedni-function-field-sections). Over F_p(E) the genus is 1, so degree-1 places are the whole group.
- Smooth values of polynomials (Dartyge-Martin-Tenenbaum type): there is no polynomial parametrisation of aP + bQ.
- Two-sided NFS analogues (K17), early abort (K18), virtual logarithms (K19), Vallee small squares (K15).
- Triple and higher large primes: constant only (K14).
- B6, rho step cost: an ECM-stage-2-style differential-addition walk has a pair state, so collisions are birthdays on N² states. Tag tracing needs partial products, and an EC step needs a full inversion. Nothing from this field.
- B6, equivalence classes beyond Aut(E): a degree-counting argument is vacuous for generic CM discriminants (the coding scout reached the same conclusion, its K9).
- B7, Miller-cocycle and Teske F_{p^6}: no smoothness or sieving ingredient. The JV F_{p^6} sieve lane is a validation question, not a smoothness one.

---

## 12. Reproduction (all read-only on the repositories; Python run with `-B` and `PYTHONDONTWRITEBYTECODE=1`)

| script | output |
|:--|:--|
| `calc/s4_reach.py` (round 1, re-run) | support 125/125; V_reach 0.1214 for all four shapes (raw 0.0777 at t = 4, 0.0995 at t = 8) |
| `calc/lp_writability.py` (round 1, re-run) | the round-1 2LP column reproduces exactly |
| `calc-r2/lp_floor_r2.py` | section 3 table, budgets and K14 constants |
| `calc-r2/lp_writability_v2.py`, `lp_writability_v3.py`, `lp_writability_frontier.py`, `lp_writability_blocksupp.py`, `nolp_blocksupp.py` | section 6 |
| `calc-r2/dipippo_howe.py` | section 7 H6 numbers |
| `calc-r2/match_r2.txt` | all `--match` runs of this session |

The section 5 c5a377 ratios were computed inline from `coordination/goals/GOAL-RELN-001/batches/BATCH-9fba5a/tasks/TASK-20261001-5a45b1/exact_yield_budgets_out.json`.

A `find -newer` check after the runs showed new paths inside crypto-autoresearcher: docs/reports/ecdlp-lead-discovery-20261024, analysis/smallroot-reach, problems, tools (directory mtime) and .git. These belong to concurrent sessions. No `__pycache__` or other file was written there by this session.
