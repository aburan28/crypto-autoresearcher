# EXP-SEMBIN-79a02d — Stage 0: frozen definitions (four degrees + operational rules)

Frozen by the Executor under TASK-20261002-fc71d6 before any Stage-1 write and
before any instance was built or any matrix was computed. Repository HEAD at
freeze: `dd387eed33ba3a5e4f08adc49a4d591e595c37fb` (branch
`claude/run-sembin-79a02d-fc71d6`). The freeze is the sha256 manifest in
`stage0/FREEZE.sha256`. Nothing below changes after the freeze; a needed change
is an amendment request to the Coordinator.

Where the frozen specification / hypothesis / source idea already fix a
definition, that definition is recorded and the source is cited. Where they
leave a choice open (pre-run notice N2 of DEC-20261005-3d5aea), the choice made
here is marked **[executor operationalization]** and is reported back to the
Coordinator; it is not a self-amendment of any criterion.

## 0. The system and the ring

* Ring: the Boolean ring `B = F_2[v_1..v_N]/(v_i^2 + v_i)`. Field equations
  are IMPLICIT (square-free monomials); they are never added as explicit rows.
  This is the convention of the DREG builder (`src/semaev_tree.py`
  `BooleanPolynomialRing`) and of `src/macaulay_export.py`.
* `B_{<=D}` = span of square-free monomials of degree `<= D`;
  `dim B_{<=D} = sum_{j<=D} C(N, j)`.
* System (Semaev 2015 eq. (5), t = 3, chained S_3, `inputs/SEMAEV-2015-310/paper_fulltext.md`
  eq. (14)): `S_3(a,b,c) = (ab+ac+bc)^2 + abc + B`, generators
  `S_3(u_1, x_1, x_2)` and `S_3(u_1, x_3, z)`, `u_1 in F_{2^n}`,
  `x_i in V = span_F2(1, alpha, ..., alpha^{k-1})`, Weil-descended to F_2 by
  equating coefficients of `alpha^l`, `l = 0..n-1` (power basis of the field
  defined by the builder's modulus). Variables ordered
  `u1_0..u1_{n-1}, x1_0..x1_{k-1}, x2_*, x3_*`; `N = n + 3k`. Generators are
  the nonzero descended polynomials in the order (equation, l). Curve
  convention of the DREG builder: `A = 1`, `B = alpha`
  (`src/semaev_tree.py:36-41`); paper Table 1 uses `B = 1`, Table 2 random `B`
  — recorded as a scope note, see §7.
* Frozen cells (specification `independent_variables`, scope Stage 2):
  `n in {12, 15}`, `m = t = 3`, `k = ceil(n/3)` → `(n,k,N) = (12,4,24)` and
  `(15,5,30)`; the Stage-1 cell is `n = 12, m = t = 3, k = 4`.

## 1. The four quantities, with explicit quantifiers

| # | Name | Definition (quantifiers explicit) | Source |
|---|------|-----------------------------------|--------|
| (i) | `d_F4-productive` and `d_F4-raw` | For ONE named engine `E`, monomial order `<` and selection strategy `s`: the run of `E` on generators `F` is a finite sequence of steps; each step has a "step degree" = the maximal total degree of the polynomials for which a row echelon form is computed in that step (paper §4.5.1). `d_F4-raw(F;E,<,s)` = max step degree over ALL steps. `d_F4-productive(F;E,<,s)` = max step degree over steps that produced at least one new (nonzero, not-yet-reducible) polynomial, i.e. EXCLUDING trailing steps that report "No pairs to reduce"/no new polynomial. Exists-quantified over (E,<,s): a value is a statement about that triple only. | paper_fulltext.md:629-637; H-SEMBIN-8e8bef C1 |
| (ii) | `d_ff` (first fall degree) | PRIMARY (the specification names `src/ic_first_fall_fast.py` "or equivalent"): `d_ff_ic(F) = min { D >= 2 : the row space of M_D(F) contains a nonzero polynomial all of whose monomials have degree <= 1 }`, where `M_D(F)` is the Macaulay matrix of §1(iv); searched for `D = 2..max_D` with `max_D = 4`; if none found, reported as `> 4` (censored, not a value). This is exactly the algorithm of `src/ic_first_fall_fast.py:57-100`, re-implemented without Sage. SECONDARY (diagnostic only, never used for a label): Semaev §4.4 fall, `d_ff_sem(F) = min { D : dim(U_D ∩ B_{<=D-1}) > dim(U_{D-1}) }` where `U_D = rowspace M_D(F)` (a degree-<D polynomial obtainable at level D that is not already obtainable at level D-1; trivial Boolean/Koszul relations produce nothing new and are therefore not counted). Forall-quantified over the generator set; exists over D. | specification Stage 2; paper_fulltext.md:505-518; IDEA-20260913-449d2b |
| (iii) | `SOLV4` / `d_solv` | See §2 (iterated closure W_4). `SOLV-D(F)` holds iff `codim_{B_{<=D}} W_D(F) = |V(F)|` where `|V(F)|` is the independently enumerated number of Boolean solutions (§4). `d_solv(F) = min { D in {2,3,4} : SOLV-D(F) }`, else `> 4`. SOLV4 is the `D = 4` instance. Order- and strategy-independent by construction (depends only on the degree filtration). | H-SEMBIN-8e8bef C2; IDEA-20260913-449d2b C2 |
| (iv) | Macaulay rank vs nrows (DREG instrument quantity) | `M_D(F)`: rows = all NONZERO Boolean products `m·f`, `f in F` with `deg f <= D`, `m` a square-free monomial with `deg m <= D - deg f` (all variable subsets, including variables already in `f`); columns = monomials that occur, ordered by (degree, sorted index tuple). `nrows`, `ncols`, `rank = rank_GF(2) M_D`. `rank_lt_nrows = (rank < nrows)`. `pred[D]` and `deficit = pred[D] - rank` use the semi-regular Hilbert-series prediction of `src/h012_peel_rank.py:50-67` (re-implemented). The DREG instrument OUTPUTS NO DEGREE; its `d_reg` is "first D at which full rank is reached" (EXP-DREG-001/specification.yaml:47), with "full rank" = `rank = nrows` (stage0/dreg-comparison-target.md). | src/macaulay_export.py:24-41; src/h012c_block_m4ri.py:316-319 |

`D` levels measured for (iv): `D in {4, 5}` (specification). `D = 5` at `n = 15`
is the dominant cost; see the budget priority in §6.

## 2. SOLV4 closure — the N2 items, stated explicitly

1. **Iterated vs single level.** ITERATED closure `W_4` to a fixed point. The
   specification fixes this ("degree-4 capped closure ... to fixpoint";
   metric `solv4_closure_iterations` "iteration count ... to fixpoint"); the
   source idea's text is "echelonize the span of {m*f : f a generator,
   deg(m*f) <= 4}; whenever a polynomial of degree d < 4 appears, re-admit its
   multiples up to degree 4; iterate to a fixed point R_4". This is the
   specification's definition, recorded as such. A single-level reading is NOT
   measured.
2. **Multiplier budget [executor operationalization of "re-admit its
   multiples up to degree 4"].**
   * Level 0: `W^(0) = span { m·f : f in F, m square-free monomial with
     deg m <= D, deg(m·f) <= D }` (Boolean product degree, so products whose
     degree falls are included even when `deg m + deg f > D`; `deg m > D` is
     never needed since every term of `m·f` then has degree `> D` unless the
     product is 0).
   * Round j >= 1: `L^(j-1) = W^(j-1) ∩ B_{<=D-1}`;
     `W^(j) = W^(j-1) + span { v_i · g : g in L^(j-1), i = 1..N }`.
     Multiplication by single variables only; multiples by higher-degree
     monomials are reached by iteration through intermediate polynomials of
     degree `<= D-1`. Degree-D elements of `W` are not re-multiplied (the
     source text re-admits multiples of polynomials of degree `d < D` only).
   * Fixed point: the first round `j` with `W^(j) = W^(j-1)`.
     `solv4_closure_iterations` = number of rounds that added at least one new
     dimension (round 0, the level-0 echelon, is not counted).
   * Implementation: only basis vectors of `L` that are new since the previous
     round are multiplied (linearity makes this equivalent).
3. **Monomial order.** Columns ordered by DEGREE DESCENDING, ties by
   lexicographic order of the sorted variable-index tuple (graded). The order
   is used only to read off `W ∩ B_{<=D-1}` from an echelon form (rows whose
   pivot lies in a degree `<= D-1` column span it). `W_D` itself does not
   depend on the order.
4. **Sufficiency.** BOTH quantities are recorded: the rank deficiency
   `codim = dim B_{<=D} - dim W_D` and the flag `one_in_W = (1 in W_D)`.
   `SOLV-D` holds iff `codim == |V|` (enumerated). For `|V| = 0` this is
   equivalent to `one_in_W` (if `1 in W` then closure under variables gives
   `W = B_{<=D}`; conversely `codim = 0` gives `1 in W`). Also recorded:
   `r_V` = rank of the evaluation map `B_{<=D} -> F_2^{V}` (equals `|V|` when
   degree-`<=D` polynomials interpolate the solution set); `r_V < |V|` is
   reported as an anomaly.
5. **Soundness certificate (independent of the closure code).** Every basis
   vector of the final `W_D` is evaluated at every enumerated solution by
   separate Python code; any nonzero value is an `invalid_measurement`.

## 3. Reading of C2 "SOLV4 agrees with enumeration" [executor operationalization]

The source idea requires both "C2 established if SOLV4 ... agrees with the
enumerated solution count on every calibration cell and both known-false
objects" AND predicts `SOLV4 = false` on known-false arm (b). The only reading
consistent with both is a CONSISTENCY reading, frozen here:

* SOLV4 "disagrees with enumeration" on an instance iff any of: (a) the
  soundness certificate (§2.5) fails; (b) `one_in_W` is true while
  `|V| > 0`; (c) `codim < r_V`; (d) the two independent enumerations (§4)
  disagree on `|V|`.
* `SOLV4 = false` (`codim > |V|`) is NOT a C2 disagreement; it is a SOLV4
  verdict and feeds O-A1-COST-FAIL only at paper-reported cells (§5).
* SOLV4 true/false counts are reported per (n, arm, stratum) in full so a
  reviewer can apply the other reading.

## 4. Instances, strata, arms, enumeration

Seeds: `s in {0..7}` (8 per (n, stratum, arm); specification `stage2_seeds: 8`).
RNG: `random.Random("EXP-SEMBIN-79a02d|<arm>|n=<n>|s=<s>")` (Python string
seeding, sha512-based, deterministic and independent of PYTHONHASHSEED).

| arm / stratum | construction |
|---|---|
| `primary/planted` | `z = x(P_1+P_2+P_3)` for 3 distinct affine points with `x(P_i) in V` sampled uniformly from all such points of `E: y^2+xy = x^3 + x^2 + alpha`; redraw if the sum is the point at infinity. |
| `primary/uniform_z` | `z` uniform in `F_{2^n} \ {0}`. Post-hoc sub-strata `uniform_z/sat` and `uniform_z/unsat` by enumeration. |
| `null` | support-matched null of the `primary/planted` instance with the same seed: each generator replaced by the same number of DISTINCT random square-free monomials of each degree (the `boolean_null` rule of `src/h012_peel_rank.py:30-47`, re-implemented with this experiment's RNG). |
| `known_false_a` | the `primary/planted` instance of the same seed with ONE coefficient flipped: the constant term of one generator chosen uniformly (equivalently `S_3^{(j)} + alpha^l`). Accepted only if BOTH enumerations give `|V| = 0`; otherwise redrawn from the same RNG stream, at most 16 draws, every draw recorded. |
| `known_false_b` | off-diagonal family `k' = ceil(n/3) + 1 > ceil(n/m)` (paper_fulltext.md:1054-1056), planted as `primary/planted` with `V' = span(1..alpha^{k'-1})`. `N = n + 3k'`. |

Planted and uniform-z strata, and every arm, are NEVER pooled in any statistic.

Enumeration (two independent routes, both required where available):
* `E1` field-level: for all `(x_1,x_2) in V^2` solve the quadratic
  `S_3(u, x_1, x_2) = 0` in `u` over `F_{2^n}` (closed form / trace test), then
  test every `x_3 in V` against `S_3(u, x_3, z) (+ corruption) = 0`. Applicable
  to primary, known_false_a, known_false_b; NOT to null.
* `E2` Boolean brute force: evaluate the Boolean generators at all `2^N`
  assignments (bit-sliced C). Applicable to every arm with `N <= 30`.
* `known_false_b` at `n = 15` has `N = 33`; there `E1` alone is used (recorded).
* The null arm uses `E2` only (it has no field structure).
* Every enumerated solution is checked against the Boolean generators.

## 5. Outcome rule (mechanical) [precedence is an executor operationalization]

The frozen texts do not order the labels when several conditions hold. The
precedence below is frozen before any data and reported for Coordinator
ratification; RESULTS.md lists EVERY triggered condition, not only the label.

1. `O-BUILDER-MISMATCH` — Stage-1 coefficient-wise equality fails (SR-2; stop).
2. `O-IMPEDIMENT` — Stage 2 cannot produce `census.json` with at least one
   valid primary-arm instance per frozen `n` (infrastructure/budget; SR-6).
3. `O-ARTIFACT` — any dual-rank disagreement (SR-3) or any pooling of strata,
   or soundness-certificate failure.
4. `O-C2-FALSE` — any C2 disagreement per §3 on a primary, known-false or
   null instance.
5. `O-A1-COST-FAIL` — SOLV4 false on every instance of BOTH strata at a cell
   the paper reports as `d_F4 = 4` (tables.yaml). Evaluability: neither frozen
   cell `(12,3,3,4)` nor `(15,3,3,5)` is a row of Table 1 or Table 2, so this
   condition is NOT EVALUABLE in this experiment and cannot fire.
6. `O-DFF-ANOMALY` — `d_ff_ic < 4` on at least one valid primary-arm instance
   (rebuilt generators). Escalate (SR-7).
7. `O-C3-FALSE` — Stage-0 target is not nrows (degree-exactly-D monomial count)
   OR `rank = nrows` at any measured `(n, D >= 4)` cell of the primary arm.
8. `O-C1-FALSE` / 9. `O-C1b-FALSE` — only if Stage 3 ran.
10. `O-COINCIDE` — all four quantities equal on every reproduced cell incl.
    known-false arms; requires Stage 3 (d_F4) — not evaluable if Stage 3 is
    impeded.
11. `O-SEPARATED` — Stages 0-2 complete, builder passes, C2 and C3 hold, no
    condition 3-9 triggered; Stage 3 supports C1/C1b or is O-IMPEDIMENT.

## 6. Dual GF(2) rank, budget priority, resource caps

* Arm A: `implementation/gf2_ge.c` — dense bit-packed Gaussian elimination
  (column-pivot forward elimination), written here, M4RI-free.
* Arm B: an algorithmically different, separately written M4RI-free routine
  under `implementation/` (Four-Russians style table elimination in C, plus a
  pure NumPy arm where size allows). Library name / version / build provenance
  recorded per cell. No apt `libm4ri` 0.0.20200125 is installed or linked.
* Every SOLV4 and Macaulay cell gets both arms on the identical matrix (for
  SOLV4: the final closure row set). Disagreement → cell invalid, O-ARTIFACT;
  never averaged.
* External anchor: the Stage-1 DREG-matched instance's `D = 5` rank is compared
  with EXP-DREG-001's recorded Sage/M4RI value (28,096 at n = 12; 69,073 at
  n = 15 if the n = 15 instance is also matched).
* Budget priority (frozen): (1) Stage 1; (2) all arms at n = 12, D = 4 and 5;
  (3) all arms at n = 15, D = 4 and SOLV-2/3/4; (4) n = 15, D = 5: DREG anchor
  first, then primary planted, primary uniform_z, null, known-false seeds in
  seed order, until the wall-clock reserve. Cells not reached are recorded as
  censored (O-IMPEDIMENT-type, never evidence).
* Caps: 8 GB RSS (per-process `RLIMIT_AS`/watch), 14,400 s total wall clock,
  at most 8 RUN ids; disk checked with `df -h /` before large steps; no matrix
  is written to disk beyond transient scratch.

## 7. Scope notes

* `B = alpha`, `A = 1` (DREG builder convention), not the paper's `B = 1`
  (Table 1) or random `B` (Table 2). Degree statements are A-independent; the
  B convention is recorded, not varied.
* Stage 3 (step-degree TRACE) requires a vendored or installed open-source
  F4/XL engine exposing per-step degree; if none, `stage3/impediment.json`.
* No statement about Assumption 1 at cryptographic scale, no exponent, no
  deployed curve.
