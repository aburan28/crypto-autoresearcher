# EXP-GFPN-05ff43 — implementation note, protocol v2 (stage 1)

Executor card **TASK-20260923-cd932c**, stage 1 only (constraint EC-2: implement, do not run).
Protocol v2 = the frozen specification `experiments/EXP-GFPN-05ff43/specification.yaml`
(version 1, unedited), read with the amendment
`experiments/EXP-GFPN-05ff43/amendments/v1_to_v2_reanchor_and_arm_iii.yaml`
(AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii), approved with conditions AC-1 to AC-6 by
**DEC-20260923-e788a1**.

- **Binding check (step 0).** Before any file was written, the amendment's sha256 was computed
  and compared with the bound value. It matched:
  `e02d4976a5e773b9eee95aa4c376d6154e9c0a9da4e6c6118ed58748054924d3`.
- **Edits to frozen material.** None. The specification, the amendment, the preregistered
  prediction, HEUR-GFPN-DFLAT and every threshold were not edited.
- **v1 artifacts.** They were not written. `implementation/` was not imported, so its
  `__pycache__` is untouched.
- **Stage-1 end state.** No v2 run package exists. Nothing was committed, pushed or staged.
  Phase A of TASK-20260923-0fa03f commits this tree.

This note records what was implemented, every implementation reading and deviation, the
development checks, and what stands in front of stage 2. It reports no measurement.

## 1. Files

`experiments/EXP-GFPN-05ff43/implementation-v2/` (12 files):

| file | role |
|---|---|
| `v2_field.py` | F_q = F_p[z]/(M) for any monic M, at n = 3, 4 and 5. Weierstrass curves. Summation polynomials by two independent evaluators, product formula and resultant recursion, cross-checked by `self_test`. `OpCount`: F_q inversion priced at 2.57 F_q mul (DC-4 C-4). Generalised from v1 `gfpn5_core.py` (AC-2 permits the copy). |
| `v2_arms.py` | The arms, the DC-3 rescaling with its refusals, interpolation with held-out verification, the single-flip test, the rq relation equation, Weil descent, per-target raw grids. |
| `v2_solver.py` | Capped child runner: fork, `setrlimit`/`getrlimit` in the child, `/proc` read-back. Host checks, including the solver lock and the scan for other solvers. msolve I/O. The R-5 outcome classes. The substitution check. Instruction counting (perf, with callgrind as fallback). |
| `v2_child.py` | Child entry for builders and raw-grid interpolation. Always a separate capped process. |
| `v2_lift.py` | Lifting per arm (DC-3 lifting steps 1-5 for rq). Deduplicated sign search (R-3). G2-orbit keys for F-2(b). v2 certificates. |
| `v2_verify_independent.py` | Independent certificate verifier. Pure Python, generic n and modulus. It shares no code with the solver path. |
| `v2_scoring.py` | DC-2: P-1..P-5 as predictions only. T-1 to T-4. F1 and F1'. F3 undecidable. HEUR-GFPN-DFLAT. The F4 matched check. The B-1..B-4 band in both conventions. R-8 field emission. |
| `v2_common.py` | Paths, plan and watchdog lookup, v2 seeded streams, ladder and fixture data readers, PARI group orders, writers. |
| `v2_driver.py` | Subcommands: `fixture`, `anchor-identity`, `controls`, `fixture4`, `build`, `cells`, `aggregate`. |
| `v2_run_wrapper.py` | Stage-2 package wrapper. Refusal checks W-1 to W-9, then manifest (see section 7). |
| `v2_check_run.py` | Completion-gate check for one v2 package. |
| `v2_make_trial_plan.py` | Writes `trial-plan-v2.json` from the minted ids. |

The other two deliverables are `experiments/EXP-GFPN-05ff43/trial-plan-v2.json` and this note.

## 2. What the code computes

### 2.1 Arms

Arms follow DC-3's `arm_set_under_v2`. Here K = 2^{m-1}.

| arm id | object | variables | group, order |
|---|---|---|---|
| `raw` (`raw_x`) | S_{m+1}(x_1..x_m, x_R), box [0,K]^m, per-target grid | x_i | trivial, 1 |
| `raw_u` (fixture) | S_{m+1}(λu_1..λu_m, x_R), box, per-target grid | u_i | trivial, 1 |
| `S{m}` | S_{m+1} in e(x), total degree ≤ K, X symbolic | e_i | S_m, m! |
| `S{m}_rescaled` | the same in e(u), x = λu (P-5, T-2) | e_i | S_m, m! |
| `torsion_S{m}_rq` | DC-3: L(u) = S_{m+1}(λu; X) / ∏u_i^{K/2} = A(σ) + wB(σ), with σ = e(t'), t'_i = u_i + β/u_i and w = ∏(u_i − β/u_i); A of σ-degree ≤ K/2, B of σ-degree ≤ K/2 − 1; plus w² − ∏(t'_i² − 4β) written in σ | s_1..s_m, w | (Z/2)^{m-1} ⋊ S_m, 2^{m-1} m! (1920 at m = 5) |
| `torsion_S{m}_norm` | the v1 construction, kept verbatim as the LABELLED NEGATIVE CONTROL | e_i of t = x + b/x | (Z/2)^m ⋊ S_m, **2^m m! (3840 at m = 5)**; never 1920 |
| `identity` | the interpolation machinery with the trivial group (control) | x_i | trivial |

### 2.2 Rescaling (DC-3 `definition.rescaling`)

- **β.** β is the smallest non-square mod p'. At odd n the code refuses unless β is a
  non-square.
- **λ.** λ = sqrt(b/β) in F_q. Of the two roots, the one with the lexicographically smaller
  coefficient vector is chosen. That rule is recorded, and it does not depend on the solver.
- **When (β, λ) is fixed.** (β, λ) is a function of (curve, p') only. It is computed and
  recorded before any target is drawn.
- **Cell checks.** Cells recompute (β, λ) and compare it with the build record. A difference
  marks the cell invalid, per the amendment's added invalidation rule.
- **Refusals.** Refusals are recorded values, never crashes (R-6):
  - `no rational 2-torsion`;
  - `b-square class mismatch`.

### 2.3 Construction and exactness

- **Interpolation.** Every symmetrised polynomial is built by exact interpolation. This is v1's
  machinery, generalised. It uses N + 96 distinct sample subsets and verifies on 96 held-out
  rows; `held_out_mismatches` is recorded.
- **Singular matrix.** A singular interpolation matrix triggers a deterministic resample from the
  same seeded stream, at most 3 times. The count is recorded as `interpolation_resamples`.
- **Single-flip test.** It runs on every built polynomial, at 12 fresh points (DC-3
  observation_collision (1)). The pass rules are:
  - **rq:** L = A + wB; L(flip) = A − wB; the even flip leaves L invariant; and L changes under a
    single flip at ≥ 1 point.
  - **norm:** L is invariant under the single flip, and the polynomial is exact at the fresh points.
  - **other arms:** exactness is required; flip behaviour is recorded but not scored.
- **What the flip test checks.** The even-flip invariance of the normalised Laurent form is the
  one step that DEC-20260923-e788a1 did not re-derive. It is therefore checked numerically on
  every built polynomial.
- **rq relation equation.** It is derived symbolically as P(y)P(−y) at y² = 4β, where
  P(y) = Σ(−1)^k s_k y^{m−k}. It is also checked numerically.

### 2.4 Lifting and certificates

- **rq lifting.** It follows DC-3 steps 1-5. The flip choice matching w is the lexicographically
  first matching assignment, so it is unique up to G2. A relation summing to R + T is accepted
  with `relation_mod_T: true`. Rejections carry their step and reason.
- **Certificates.** Every certificate carries: the modulus, the curve, G, k, R, the signed points
  and `relation_mod_T`. For the rescaled base it also carries `factor_base.{beta, lam, u_values}`.
- **`v2_verify_independent.py` checks:**
  - R = [k]G and [n]G = O;
  - every point is on the curve;
  - the factor-base condition for the arm's base; on the rescaled base: λ²β = b, β a non-square
    at odd n, and x(P_i)/λ ∈ F_p equal to the recorded u_i;
  - a6 = 0 for T-quotient arms;
  - the relation, as R, or as R + T (with 2·sum = 2R) when flagged.
- **Missing fields.** A certificate missing β, λ, `u_values` or `relation_mod_T` FAILS.
- **Invalid runs.** A run with any failing certificate is `invalid_measurement`.

## 3. DC-2: every hard-coded locus replaced

| v1 locus (amendment DC-2) | v2 replacement |
|---|---|
| `pdp_common.py` 219-221 (2^20 predictions as divisors; group orders 1 / 120 / 1920) | `v2_scoring.PREDICTIONS` holds P-1..P-5 as labelled predictions, never divisors. `v2_arms.group_order` gives S5 120, rq 1920, norm 3840. |
| `pdp_cell.py` 451-455 (non-freeness against D_raw = 2^20) | T-3 against the measured like-for-like reference (`score_like_for_like`) |
| `pdp_cell.py` 661 (supplementary group table) | rq 2^{m-1} m!, norm 2^m m!; no supplementary constructed-solvable ratio is computed (R-7) |
| `pdp_cell.py` 679-681 (2^20 / D; `min_required_log2`; non-freeness vs 2^20) | T-1 on measured D_raw on the same targets only; T-2; T-3 |
| `pdp_cell.py` 708 (success 1/120, 2/120) | `success_model`: 1/120 for raw and S; 1/(2^4·120) with halving for rq; 1/1920 with halving for norm |
| `pdp_common.py` 222-223 (min ratios; floor 142) | 2^6 and 2^9 kept as T-1 thresholds on measured D_raw; constants 142.4 (uncharged) and 149.3 (charged) |
| `pdp_cell.py` 683, 693, 725 (tail check above 2^36; 142) | F3 and the 2^36 tail check are the string `undecidable (AMD-EXP-GFPN-05ff43-20260923-reanchor-arm-iii DC-4)` |
| `pdp_cell.py` 710, 720-721 (N_rel for every arm; proxy point estimates) | relations halved for T-quotient arms; no proxy or instruction point estimate enters any band |
| `symmetrize.py` 88-89, 94 (inversion priced at 150 mul) | 2.57 (Pornin lines 522-523); the table's 2.61 (128/49) recorded next to it |

Guard rails:

- `v2_check_run.py` fails any package that contains a v1 constant-anchored field name.
- It also fails a package that reports F3 other than undecidable.
- It also fails a package that gives torsion_S5_norm an order other than 3840.

## 4. DC-4 cost unit

- **C-1, instruction counts.**
  - Every msolve child gets `perf_event_open(PERF_TYPE_HARDWARE, instructions, user only, inherit,
    enable_on_exec)`, opened on the forked child before exec.
  - **On this host it returns ENOENT: there is no hardware counter** (development note DN-3).
  - The fallback is valgrind callgrind. It reports total Ir and the inclusive Ir of msolve's F4
    core, `core_f4` in `libneogb-0.6.5.so`.
  - Scope, declared in the plan before any run: every fixture system, and target 0 of every
    m ≤ 4 cell.
  - Everything else is `not_measured` with the declared reason.
  - The figure is labelled "measured work proxy (instructions)". It is never converted to F_p
    operations and never compared with 2^36.
- **C-2, proxy bracket.** `[nnz, reduction]`, from msolve's per-round matrices. It is labelled
  "not a bound in either direction" and never enters a band.
- **C-3, identical construction charging.** One `OpCount` instrument, in every arm including raw.
  - Symmetrised arms count the per-target specialisation.
  - Raw arms count the per-target grid: every summation-polynomial evaluation and the Vandermonde
    solves.
  - Lifting is counted separately.
  - Rows carry `construction_ops`, `lifting_ops` and their mult-equivalent total.
  - The raw counts (F_q mul, F_q inv, F_p mul, F_p inv) are always reported.
  - 1 F_q mul = n² + (n − 1) F_p mul, which is 29 at n = 5. This is labelled a convention.
- **C-4.** Inversion is priced at 2.57 (see section 3).

## 5. DC-6 R-1 to R-10, rulings.DC-5, DC-7 / AC-1

- **R-1, cap and counters.**
  - `run_child` sets RLIMIT_AS in the child, reads it back with `getrlimit`, and sends the pair to
    the parent before exec.
  - A child that cannot set the cap, or reads back a different value, exits without exec. It is
    recorded `refused_to_start`.
  - `/proc/<pid>/limits` is also read.
  - The manifest's `resources.child_rlimit_as_read_back_by_getrlimit` holds the children's own
    read-backs, never a wrapper default.
  - Counters are derived from outcomes: attempted, measured, and one count per class
    (`ok`, `timeout`, `memory_exhausted`, `crashed`, `positive_dimensional`,
    `degenerate_parametrisation`, `refused_to_start`, `not_attempted`).
  - `m5_timeout_count` counts `timeout` only.
- **R-2.** `trial-plan-v2.json` enumerates every package and every (arm, shape, p', m,
  target_kind) cell. Every cell ends in a terminal row: measured, not_measured with class and
  envelope tuple, not_attempted with reason, or a recorded refusal. The aggregate lists any
  planned cell without a row. Early-stopped targets are `not_attempted` with the stop reason.
- **R-3.** A success rate is filled only for random targets. The fixture's planted targets are
  labelled `planted_square_nm`. Relations are deduplicated as signed-point multisets.
  `target_kind` is on every row.
- **R-4.** `threads_executed` is read from the argv actually executed. The manifest records the
  set; the checker requires {1}.
- **R-5.** Two added classes:
  - `positive_dimensional`: a non-zero msolve header, a log message, or output that does not
    parse as a zero-dimensional parametrisation.
  - `degenerate_parametrisation`: a non-square-free eliminating polynomial, eliminating degree
    ≠ D, or any parsed solution failing substitution into the descended system. Every solution
    is substituted.
  - Neither class is a measured non-decomposition.
- **R-6.** Build and cell refusals are recorded rows computed by the code before any condition.
- **R-7.** Only like-for-like ratios are computed: S with raw_x, rq with S_rescaled, rq with raw_u
  (for F1).
- **R-8.** The three modeled fields are emitted separately. The reasons are `heur_dflat_failed`
  (only when pass is false) and `heur_dflat_not_applicable`.
- **R-9.** random_with_2torsion runs at every prime for raw (m ≤ 4), S5, S5_rescaled, rq, and
  norm where S5 runs. random_without_2torsion runs raw and S5, and records the refusals of rq,
  S5_rescaled and norm.
- **R-10.** msolve inputs are retained for every fixture, anchor and control system, and for
  target 0 of every cell, up to 50 MiB. The sha256 of every input and output is always recorded.
- **R-11 / AC-3.** The wrapper refuses unless `implementation-v2/`, this note and the plan are
  tracked and clean (W-4). The manifest records HEAD, the last commit touching those paths, and
  `implementation_v2_clean`.
- **rulings.DC-5, `jv_anchor_system_trace_identity`** (driver `anchor-identity`).
  1. The comparator `k4a_anchor_system.py` is **executed** (Sage python, capped child, output to
     the package's `comparator/`). It is not imported and not copied.
  2. Our S4 system is built at p' = 16777291 on the archived anchor curve (`random_no2torsion`).
     The ladder coefficients are checked equal to RUN-GFPN-61bba9's recorded parameters. It is
     built on the comparator's own random x_R plus 3 v2 seeded known-scalar targets.
  3. Structure is checked: 4 variables, 5 equations, total degree 8, union support 495.
  4. For the comparator's target: the term count equals the comparator's, and the F_q
     polynomials are proportional. They are rebuilt from both descended systems.
  5. msolve `-g 1 -t 1` runs on every system and on the comparator's file. The per-round trace
     (degree, pairs, rows, columns, new, zero) must equal the archived `anchor_t*.ms.log` traces.
     The `sel` column is recorded too.
  6. If msolve is not 0.6.5, the reference switches to the fresh comparator-system trace, and the
     switch is recorded.
  7. The wall ratio against JV's 17.01 s is reported with the host description, and marked
     NON-BLOCKING.
  8. The v1 anchor outcome stays FAILED and is not re-scored.
- **DC-7 / AC-1, EC-4.**
  - The child cap is 10737418240 B (DP-4: no dispatcher guard process is running, so the cap is
    not lowered).
  - The driver checks its own VmRSS before each launch and refuses above 1 GiB.
  - One memory-heavy child runs at a time: an exclusive `flock`, plus a `/proc` scan that refuses
    if another solver-like process exists (EC-10).
  - msolve always runs `-t 1`.
  - Peaks are recorded from VmHWM/VmPeak and from the child's own `wait4` rusage.
  - Every not_measured row carries the A-6 envelope tuple: host RAM and swap, cap from the child,
    cap from `/proc`, threads, msolve version, arm and construction, p', m, n, and the last F4
    round.
  - The A-7 early stop is pre-declared: 2 consecutive `memory_exhausted` outcomes at the same F4
    degree in an m = 5 cell.

## 6. Fixture independence (EC-5 / AC-4)

- **Construction.** The n = m = 3 arms are built from the amendment's DC-3 definition by this
  tree's own code.
- **What is read from the red team.** From `coordination/.../TASK-20260923-404bf9/scratch/k5k7/`
  only the two JSON files are read, as data: curves, β, regression x_R, expected values. Their
  sha256 is recorded in each package.
- **What is not used.** No code there is imported, copied or executed. `square_analogue.py` and
  `square_analogue_m4.py` were not opened.
- **The comparator.** `k4a_anchor_system.py` (58953e scratch) is referenced only as the path the
  anchor package executes in stage 2. Stage 1 did not execute it. Its header and CLI were read
  only to learn how to invoke it (it takes one output directory and picks its own target).
- **Fixture targets.** Each prime gets:
  - the 2 regression x_R (degree only; no known scalar, so no lifting);
  - 2 fresh seeded known-scalar targets on the full group (order by PARI `ellcard`). A non-generic
    fresh target is reported and replaced by the next seeded one.
  - ≥ 2 planted targets on the rescaled base for F-2(b).
- **F-1 and F-3.** F-1 checks the six D values per target, and the structure: norm support equal
  to S3's, 35 monomials, total degree 4; rq deg_A 2, deg_B 1, 14 monomials. It also requires the
  single-flip and held-out checks to pass. F-3 checks D(S3_rescaled) / D(rq) = 4 per target.
- **F-2(a).** D(raw_u) = 24 · D(rq) per target, with non-freeness reported.
- **F-2(b).** A per-target bijection table between the G2-orbit keys (σ(t'), w) of the raw_u
  rational solutions and the rq rational solutions that pass lifting steps 1-3. The planted orbit
  must be present on both sides.
- **Reading a failure.** A failure is classified per AC-5. A mismatch confined to raw_u or
  S3_rescaled is "implementation or derivation", and the note names both explanations.

## 7. Trial plan (`trial-plan-v2.json`)

- **Size.** 31 packages, which is under the 48 ceiling:
  - 27 planned, in execution order;
  - 4 contingency ids.
- **Ids.** Every id was minted with `tools/allocate_id.py --next run --area GFPN` and confirmed free
  with `--check` (0 occurrences in 26244 identifier-bearing paths). No v1 id is reused; the plan
  lists all 49 v1 ids, including RUN-GFPN-bb78e5.
- **Cells.** 90 cells are enumerated.

Package order:

1. Fixture p' = 4111 (blocking).
2. Fixture p' = 16777291 (blocking).
3. Anchor identity (blocking).
4. Frozen controls (blocking).
5. F-4 (not blocking; runs after the gate).
6. Then, for each prime 4111, 262151 and 16777291 in turn:
   - a build;
   - three m = 5 cell packages (ecgfp5_shaped, random_2torsion, random_no2torsion);
   - three m = 4 cell packages.
7. The aggregate.

Wrapper enforcement:

- The wrapper refuses any package whose predecessor has no manifest (W-5).
- It refuses any post-gate package unless packages 1-4 all have `completed_valid` and
  `gate_pass: true` (W-6).

Watchdogs, declared uniformly per (arm, m) (AC-6):

| (arm, m) | per-target | per-cell (only while the cell has no measured target) |
|---|---|---|
| every arm at m = 3 (fixture, controls) | 1800 s | none |
| raw, S4, S4_rescaled, torsion_S4_rq, torsion_S4_norm at m = 4 (including the anchor and F-4) | 7200 s | 86400 s |
| S5, S5_rescaled, torsion_S5_rq, torsion_S5_norm at m = 5 | 43200 s | 172800 s |
| raw at m = 5 | none: not_attempted by design (A-6) | none |

Other timeouts:

- builders: 1800 s (m = 3), 7200 s (m = 4), 86400 s (m = 5);
- callgrind: 1800 s (m = 3), 14400 s (m = 4);
- comparator: 3600 s.

Expiry of any watchdog is `not_measured (timeout)`, never evidence about D.

## 8. Implementation readings and deviations (disclosed; none changes a threshold, control or branch)

- **D2-1 Target stream.**
  - Targets use `2026092001:v2:targets:<p>:<shape>`, keyed by (p', shape) only.
  - DC-3's quantifier order requires every arm to be solved on the same R, and T-1/T-2 need the
    same targets.
  - The amendment's "v2 streams are keyed by arm id" is therefore applied to the construction
    (sample-point) streams.
  - Every v2 stream carries `:v2:`, so no v1 stream is reused.
- **D2-2 Thresholds only at m = 5.**
  - T-1 (2^6, 2^9) and F1' (2^3) are applied only on m = 5 cells.
  - At other m the ratios are reported without a threshold.
  - F1 and F1' can fire only on ecgfp5_shaped cells (the aggregate applies the shape).
  - F1 pairs D_iii' with raw_u, the raw system on the same rescaled base (R-7's like-for-like
    rule). At m = 5 raw is not attempted, so F1 is not scoreable there, as the amendment expects.
- **D2-3 S5_rescaled band convention.** S5_rescaled uses S_5's band convention (1/5!, no halving).
  The amendment gives no band row for it.
- **D2-4 S5_rescaled runs unconditionally.** On both 2-torsion shapes, S5_rescaled runs
  unconditionally (R-9: "every arm it names at every ladder prime"). It does not wait on rq
  completing, as `budget_impact` describes.
- **D2-5 Linear-algebra field.** When HEUR-GFPN-DFLAT passes,
  `projected_linear_algebra_cost_at_p_2_64` is null with reason "not charged (DC-2 B-4)".
- **D2-6 Relative variation.** The v1 definition is kept: (max − min) / mean. max/min is also
  reported.
- **D2-7 Cell D.** A cell D is defined only when every measured target agrees (the v1 rule).
  Per-target D is always recorded.
- **D2-8 Memory classification.** `memory_exhausted` requires evidence of near-cap use (sampled
  VmPeak ≥ 80 % or VmHWM ≥ 60 % of the cap, rusage maxrss ≥ 60 %) or an allocation-failure
  message. Otherwise a signal death is `crashed` (infrastructure_error). msolve 0.6.5 does not
  check allocations (v1 note), and DN-4 observed it die on its first allocation under a tiny cap.
- **D2-9 Degenerate parametrisation.** `degenerate_parametrisation` also covers an eliminating
  polynomial of degree ≠ D.
- **D2-10 Instruction scope.** Callgrind scope as declared in section 4, on affordability grounds.
- **D2-11 Contingency ids.**
  - Four contingency ids, usable only as
    `v2_run_wrapper.py <id> --replaces <run>`.
  - They apply only to a NON-GATE package recorded `infrastructure_error`.
  - Each package can be replaced once, with identical arguments.
  - Never for a gate package: AC-5 ends the task on any gate failure.
  - Never for implementation_error, resource_exhaustion, invalid_measurement or a result.
- **D2-12 Per-cell watchdog scope.** The per-cell watchdog applies only while a cell has no
  measured target, so A-7's "continues to 20 targets" always holds.
- **D2-13 m = 4 packages.**
  - raw m = 4 runs unconditionally (R-9).
  - Every other m = 4 cell runs only if its m = 5 cell ran and measured no target (stopping rule
    3, "once per such cell").
  - A refused or not-attempted m = 5 cell triggers no fallback.
- **D2-14 F-4 construction path.** F-4 uses β = 1 and the modulus from `square_analogue_n4.json`.
  This is the even-n, b-square construction path, which the amendment calls different. The
  verifier's non-square-β rule applies at odd n only; at even n it checks λ²β = b.
- **D2-15 F-4 order.** F-4 runs only after the gate passes (the task stops at a failed gate).
- **D2-16 relation_mod_T points.** A relation_mod_T certificate keeps the points as found. v1
  instead moved P_1 to P_1 + T.
- **D2-17 Distinct samples.** Interpolation sample subsets are distinct. A repeated subset
  duplicates a row; this was found in DN-8.
- **D2-18 Host.** The host differs from v1's: Intel Xeon @ 2.10 GHz, 4 cores, 16481980 kB RAM,
  no swap, kernel 6.18.44. Each run records its host.

### KI-1: a ladder fact that the amendment's premise does not match (for the Coordinator)

`implementation/ladder.json` (v1, frozen) records **`b_is_square_in_Fq: true`** for the
ecgfp5_shaped curve at **p' = 16777291**. The curve is y² = x(x² + 2x + 59z), with order 4 · prime.

- **Recheck.** Stage 1 rechecked this by the norm criterion: N(59z) = 59⁵ · 2 is a square mod p'.
- **Other primes.** At 4111 and 262151 b is a non-square, as the amendment says.
- **Consequence for the construction.** DC-3 needs b a non-square at odd n. So at 16777291 both
  torsion_S5_rq and S5_rescaled on the EcGFp5-shaped curve record a `b-square class mismatch`
  refusal (R-6).
- **Consequence for HEUR-GFPN-DFLAT.** Arm iii' on EcGFp5-shaped curves can reach only 13 and 19
  bits (span 6). HEUR-GFPN-DFLAT for arm iii' on that shape is therefore `not_applicable` by
  construction.
- **Unaffected.** The matched random_2torsion curve at 16777291 has b a non-square.
- **Not changed here.** The frozen ladder is not changed.
- **Possible remedies for a Coordinator decision:**
  - an EcGFp5-shaped curve at the 25-bit rung with b a non-square;
  - or using the selected but unused 31-bit rung 1073741831, where b is a non-square.

## 9. Development checks (development notes; no run package; no number reported as a result)

Every check that ran msolve, a builder, PARI or valgrind ran under RLIMIT_AS = 10 GiB, one
process at a time, msolve with `-t 1`, and `PYTHONDONTWRITEBYTECODE=1`. Outputs went to the
session scratchpad. **No fixture system (n = m = 3 at 4111 or 16777291) was solved, and the
comparator was not executed.** So the stage-2 gate is not pre-empted.

- **DN-1.** `v2_field.self_test`: evaluators (A) and (B) agree at n = 3, 4, 5 on toy fields
  (p = 1033, 1009, 16777331), and closed-form S_3 matches Semaev. The first attempt used a
  reducible toy modulus; the self-test now selects an irreducible one.
- **DN-2.** Arm builders at n = m = 3 on a toy curve at p = 1033 (not a fixture prime; no solver
  run):
  - held-out exactness, and the single-flip test for S3, S3_rescaled, torsion_S3_rq,
    torsion_S3_norm and identity;
  - the rq relation equation, numerically at m = 3 and 5;
  - the b-square refusal path.
- **DN-3.** `perf_event_open` for hardware instructions returns ENOENT on this host. This led to
  the callgrind fallback (section 4).
- **DN-4.** Capped-child runner on toy msolve systems (a 2-variable zero-dimensional system and a
  positive-dimensional one):
  - the child's getrlimit read-back and `/proc` limits both equal 10737418240;
  - outcome classification, parametrisation parsing and the substitution check;
  - the refusal path for an unsettable cap (2^64) and for an invalid cap;
  - the watchdog path;
  - callgrind under the cap, which found `core_f4` in libneogb 0.6.5;
  - the memory path, with a Python child over-allocating under a 512 MiB cap.
  Findings that changed the code:
  - msolve prints "Dimension of quotient" on **stderr**, so the driver parses stdout and stderr
    together;
  - a non-generic staircase adds a linear form and a second F4 computation (counted as
    `n_f4_computations`);
  - under a 64 MiB cap msolve dies on its first unchecked allocation, which led to D2-8.
- **DN-5.** `fixture_core` exercised end to end on a NON-square toy object (n = 3, m = 2,
  p = 1033). Checked: capped builds, raw grids, solving, lifting, certificates, F-2(b) tables and
  outcome classes. Only pipeline health was inspected. `_run_cell` was run on the same toy
  including a forced timeout and forced memory exhaustion, and every not_measured row carried
  its envelope tuple.
- **DN-6.** Scoring arithmetic on synthetic inputs:
  - the B-2 band table reproduced for S5, raw, quotient and norm within 0.05;
  - R-8 reasons;
  - the T-2/T-3 rules at the free-orbit, short-drop and above-ceiling synthetic values;
  - Clopper-Pearson intervals;
  - the flatness decision.
  Finding: the thresholds were applied at m = 3 → D2-2.
- **DN-7.** Independent verifier on synthetic planted relations on the n = 5 ladder curve at 4111
  (no solver). Checked:
  - positive cases for all four factor-base kinds;
  - rejection of flipped signs, a missing `relation_mod_T`, missing β, λ or u_values, and a
    T-certificate on a curve without (0,0);
  - relation_mod_T accepted with the flag and rejected without it;
  - rq lifting of a planted (σ, w);
  - refusals: rq on random_no2torsion, and the KI-1 b-square refusal at 16777291;
  - independent group law equal to flint at n = 5 and at the n = 4 general modulus;
  - PARI `ellcard` on a toy curve.
  It also read two archived data files. The comparator's archived output
  `58953e/scratch/inv1/anchor25_random.ms` round-trips through the parser. The archived
  RUN-GFPN-61bba9 traces parse and are identical across t0-t4.
- **DN-8.** Toy-ladder integration at p' = 101 (n = 5, m ∈ {3, 2}), with the plan, ladder and runs
  directory redirected to scratch:
  - `build` → `cells` (conditions, refusals, fallbacks) → `aggregate`;
  - no planned cell without a row.
  Finding: repeated sample subsets made an interpolation matrix singular → D2-17. A deterministic,
  recorded resample was also added.
- **DN-9.** Wrapper refusals at stage 1:
  - W-4 (tree not committed), and unreserved or v1 ids including RUN-GFPN-bb78e5, all refused with
    nothing written;
  - the condition logic of the m = 4 fallback;
  - the completion-gate checker on a synthetic toy manifest: it passes, and fails when a model id
    is recorded.
- **DN-10.** `pyflakes` was installed with pip into the system Python to lint the tree. This is a
  tooling change outside the repository. The tree lints clean.

## 10. What could block or limit stage 2

- **KI-1** (section 8).
- **Lane claim (DP-3).** GOAL-GFPN-380702 has no dispatch queue, so `tools/goal_lanes.py claim`
  cannot run. This is reported by the dispatching session as an impediment for the phase-A
  Coordinator act. No queue was created here.
- **Phase-A precondition (DP-5).** The wrapper refuses until these three paths are committed and
  clean (W-4).
- **Build memory.** The m = 5 interpolation for S5, S5_rescaled and norm uses an N = 20349 dense
  matrix of about 3.3 GB. With flint's solve it may approach or exceed the 10 GiB child cap. v1
  built S5 under 12 GB. A build that exhausts the cap is recorded, and its cells are
  `not_attempted` with that reason.
- **Instruction counts.** Hardware counters are unavailable on this host. Instruction counts
  exist only where callgrind runs (section 4).
- **msolve 0.6.5 at the 19-bit rung.** The v1 note (D-3) records parametrisation segfaults for
  characteristics between about 2^16 and 2^18. 262151 is just above 2^18. A crash there is
  recorded `crashed` / infrastructure_error.
- **Sage at stage 2.** The comparator needs Sage at `/opt/conda-sage/envs/sage/bin/python`. It is
  present on this host.

## 11. Inference

- requested_policy: `executor-implementation`
- resolved_model_id: null
- fallback_used: false
- bedrock_used: false

Every stage-2 manifest records the same block; `v2_check_run.py` requires it.
