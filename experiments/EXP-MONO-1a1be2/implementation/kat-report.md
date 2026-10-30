# EXP-MONO-1a1be2 known-answer report (TASK-20261029-a97206)

Status: implementation and known-answer tests only. Zero experiment runs. No cell of the contract was
computed (IM-2), and no KAT asserts a predicted value (IM-3). The specification
(`specification.yaml`, status `review_required`, sha256 `d81a85b3...c373`) and every ledger record are untouched.

## Result

```
cd /home/user/crypto-autoresearcher
PYTHONDONTWRITEBYTECODE=1 python3 -m pytest -p no:cacheprovider experiments/EXP-MONO-1a1be2/code/tests/test_kat.py
======================= 174 passed in 173.54s (0:02:53) ========================
```

174 passed, 0 failed, 0 skipped (the final run, which also wrote `kat-log.json` through `KAT_LOG_PATH`). An
earlier full run of the same suite before the last edits to the test file (removal of two tuple-length
combinations and of skip conditions) gave `174 passed, 2 skipped`; the two skipped cases are the removed
combinations. Environment: Python 3.11.17, numpy 2.4.6, pytest 9.2.0, PyYAML 6.0.1, gcc 13.3.0, flags
`-O3 -Wall -Wextra -shared -fPIC -std=c11` (`environment.json`). The kernel is built into a temporary
directory by the tests; no binary exists in the repository (tested).

## KAT cells and disjointness

Field/curve KAT cells: F_Q with q in {5, 13}, n in {2, 3} (`(5,2) (5,3) (13,2) (13,3)`), and prime fields
(n = 1) q in {7, 11, 17, 19, 23, 101, 103, 1009} plus the 20-curve point-count list below. Counter KATs use
the same cells with tuple size m up to 5. No (q, n) pair is an arm-A/arm-B contract cell
(`test_kat_cells_disjoint_from_contract`, `launcher --kat` refuses contract cells). Arm-C fields (n = 2..7,
q_n) were not touched. The only contract-cell computation anywhere is the generation of the identity
fields by `make_trial_plan.py` (IM-6), see below.

## What each KAT checks

| KAT id | Tests (cases) | Check | KAT cells |
| --- | --- | --- | --- |
| F1 least irreducible | `test_least_irreducible_matches_definition` (4) | g equals the first monic polynomial in lexicographic order (constant term first) found by trial division by every monic factor of degree 1..n/2, independent of the Rabin test used by the code | (5,2) (5,3) (13,2) (13,3) |
| F2 field arithmetic | `test_field_arithmetic` (11), `test_quadratic_extension` (11) | associativity, distributivity, commutativity, Frobenius = q-th power, norm-method inverse = Fermat inverse, sqrt squares back, chi equals membership in the table of squares (whole field for Q <= 2197), F_{Q^2} inverse and lifted y | all 4 extension cells and 7 prime fields |
| F3 kernel field | `test_kernel_field_ops_match_python` (11) | compiled multiplication and inversion (norm method and reference Fermat mode) equal the Python field | same |
| C1 seed rule | `test_seed_rule`, `test_plan_seed_strings` | SHA-256 of the UTF-8 string, first 16 bytes big-endian, PCG64: recomputed in the test with `hashlib` and numpy; seed-string formats of the specification | specification example strings |
| C2 curve rules | `test_curve_selection_rules` (4), `test_curve_selection_prime_fields` (7) | a = 0 (j = 0), b = 0 (j = 1728) and a singular curve are caught; 30 generated curves per cell are nonsingular with j^q != j; at n = 1 only singularity is rejected | extension cells, prime fields |
| C3 group law | `test_group_law` (4) | on-curve, P + (-P) = O, associativity, commutativity, 5P by repeated addition, N P = O with N counted by definition | extension cells |
| C4 point counting | `test_point_counting_all_methods_and_definition` (6) | N from the definition (all Q^2 pairs), square-table count, chi sum, compiled exhaustive count, BSGS on the Hasse interval (with the quadratic twist) all equal, 3 curves per cell, Hasse bound, valid-target mask count = N, kernel target index = Python index on every point | (5,2) (5,3) (13,2) and primes 7, 11, 23 |
| C5 twenty curves | `test_point_counting_twenty_random_curves_exhaustive_vs_bsgs` | exhaustive (compiled) = BSGS on 20 random curves with Q < 2^27 outside the contract cells: 8 prime fields (Q from 1009 to 100000007) and 12 over q in {5, 13}, n in {2, 3} (IM-4) | listed in `kat-log.json` C4 |
| C5b above 2^27 | `test_bsgs_beyond_exhaustive_range_agrees_with_independent_count` | at a prime p > 2^28 BSGS lies in the Hasse interval, N P = O for 5 random points, and the compiled exhaustive count agrees | p = next prime above 2^28 |
| C6 factor base | `test_factor_base_and_torsion_from_definition` (6) | D, X, t2 and the F_Q 2-torsion roots equal brute-force enumeration from the definition | (5,2) (13,2) (5,3) (13,3) primes 11, 23 |
| P1 polynomial tools | `test_polynomial_tools` | a polynomial with 3 known linear factors and an irreducible quadratic: ddf pattern, both split tests, roots, squarefreeness, brute-force roots of random polynomials | F_{13^2} |
| S1 defining property | `test_semaev_defining_property_200_tuples` (18) | S_{k+1}(x(P_1)..x(P_k), x(sum)) = 0 on 200 random point tuples for k = 2, 3, 4, 5 (k = 2, 3 only over F_{13^3}) | (13,2) (5,3) (13,3) and primes 101, 1009 |
| S2 roots vs group law | `test_semaev_roots_agree_with_group_law_signed_sums` (12) | the F_Q roots of S_{n+1}(x_1..x_n, T) equal the x-coordinates in F_Q of the signed sums of lifts over F_{Q^2} on 200 random tuples per k = 2..5 and field (compared on squarefree full-degree fibres), and the two complete-split tests (ddf, x^Q = x) agree | (13,2) (5,3) prime 101 |
| S3 S_3 definition | `test_semaev_s3_matches_definition_and_known_answer` | S_3 vanishes on every x-triple of a sampled point set summing to O, and its roots at fixed (x1, x2) equal the signed-sum x-coordinates exactly | (13,2) |
| S4 recursion | `test_semaev_recursion_matches_nested_definition` | S_4(x1,x2,x3,T) from the interpolating recursion equals the Sylvester-determinant resultant of S_3(x1,x2,X) and S_3(x3,T,X) at 14 values of T for 6 tuples | (13,2) |
| S5 fast path | `test_analyse_fibre_fast_path_agrees_with_detailed_path` (4) | the speed path (complete-split by the first ddf stage) agrees with the detailed path on degree, squarefreeness, chi vector and split decision | (13,2) (5,3) (13,3) 101 |
| E1 exhaustive vs naive | `test_exhaustive_counters_match_naive_enumeration` (30) | kernel T_A, T_M, T_S, T_X, the T_M recount from x-multisets, the weighted helper arrays, the S set, the special and generic target sets and the generic T_M histogram each equal a naive Python enumeration written from the definition of the same convention, for the line base, a matched random base and a twin base; the independent recount (reversed order, Fermat arithmetic) equals the primary pass in every convention | cells `(13,2,m=2,3) (5,2,4) (5,3,2,3) (13,3,2,3) (7,1,4) (11,1,3) (7,1,5)` x 3 bases (field, tuple size m) |
| E2 sampled vs naive | `test_sampled_counter_matches_naive_enumeration` (14) | arm-C kernel: per-target counts at sampled targets and at S targets, number of multisets, cancellation-free multisets and m_S equal naive enumeration; target sampler output is distinct classes, chi = +1, outside S, deterministic | (13,2,m=2,3) (5,2,4) (5,3,3) (13,3,2) (101,1,2) (103,1,2), line and random base |
| E3 helpers | `test_ncf_coefficient_function_matches_series_expansion`, `test_poisson_*` (2), `test_target_sampler_chi_and_uniform_rule`, `test_random_and_twin_bases_structure` (4) | the generating-function coefficient function equals an independent series expansion (arithmetic of the formula only, no comparison with any count); Poisson KS, dispersion, tail, max-count p equal independent computations on synthetic data, chi-square equals ~0 on exact-expectation data; kernel chi equals Python chi; random/twin bases are symmetric, on the curve, have the stated t2, size and distinct classes, and are deterministic by seed | synthetic data; extension cells |
| T1 q rule | `test_q_rule_against_sieve_and_report_against_expected_list` | the generator's q_n equals a sieve evaluation of the rule; its agreement with the specification's list is recorded, not asserted | n = 2..7 |
| T2 s rule | `test_sample_size_rule_against_float_formula` | 60-digit decimal result within one unit of the float formula, equal to its ceiling | n = 2..7 |
| T3 plan structure | `test_trial_plan_enumeration_and_seed_derivation`, `test_plan_is_deterministic_for_a_cell_subset` | 54 + 12 + 12 + 18 cells, unique ids, seed strings follow the rules, arm B reuses arm-A curves, identity builder deterministic and exhaustive = BSGS on KAT parameters | stub builder; KAT cells (13,2) (5,3) (101,1) |
| L1 refusal | `test_launcher_refuses_contract_cell_while_specification_not_approved`, `test_launcher_approval_gate_logic_with_synthetic_specs`, `test_launcher_kat_flag_required_and_contract_cells_refused` | a non-KAT cell is refused (exit 3, no `runs/` created) while the specification is `review_required` with `approved_by: null` and no lock; gate logic over synthetic specs (missing lock, wrong hashes, null approver); `--kat` required for KAT cells and contract (q, n) refused | real status as on disk; synthetic specs |
| L2 KAT package | `test_launcher_kat_cell_writes_package_in_temp_dir_only` (4), `test_launcher_arm_b_chi_patterns_are_recorded`, `test_launcher_watchdog_marks_cell_failed_resource_exhaustion`, `test_launcher_derived_summaries_on_synthetic_inputs_only`, `test_environment_record_has_compiler_and_flags`, `test_no_binary_in_code_dir` | each arm writes manifest, command, environment, logs, raw result and summary under a temporary directory, never `runs/`; KAT mode strips cross-convention residuals and derived statistics; watchdog gives `failed`/`resource_exhaustion`; derived-statistic code paths are exercised on fabricated inputs only | (13,2) A and C, (13,3) B1, (5,3) B2 |

## Deviations, implementation choices, findings (record, not conclusions)

1. **Scope finding F-1 (KAT coverage at n >= 4).** IM-3 permits extension-field KATs only for q in {5, 13}
   at n <= 3. The Python and compiled arithmetic at field degrees n = 4..7 and at the contract q sizes
   (up to q = 32771) is therefore not covered by any KAT. The code paths are the same loops with larger n
   (inversion loop, reduction loop, Frobenius table), exercised at n <= 3 and, for large q, by prime fields up
   to 1e8 (products fit in 64 bits for all contract q), but this is an untested extrapolation. A KAT field
   such as F_{5^n}, n = 4..7, is disjoint from every contract cell; adding it needs the Coordinator to widen
   IM-3, so none was run.
2. **Throughput finding F-2 (measured on KAT cells only, contract sizes not run).** Compiled ordered
   enumeration: about 0.2 microsecond per tuple at F_{13^2} and 0.4 at F_{13^3}; the recount (Fermat mode)
   about 3 times slower per tuple. Python arm-B analysis per x-tuple with the speed path: about 0.006 s
   (F_p, tuple length 5) and 0.03 s (F_{13^3}, tuple length 5); the S_{n+1} polynomial alone is about 0.004 s
   there, the rest is the gcd and x^Q work. If those per-tuple costs carried to the contract, 10^6 tuples
   would take the order of 2 to 8 hours per B1 cell on one core (modeled extrapolation, not measured; the
   contract fields n = 3..5 at q = 41, 23, 11 are costlier per multiplication than the KAT cells). The launcher
   takes `--workers`. A compiled port of the B1 loop is the obvious speed-up if the budget needs it. This is a
   note for the approval act, not a correctness finding.
3. **Identity fields of contract cells.** `make_trial_plan.py` computed N (exhaustive compiled count, with a
   BSGS cross-check on every curve below 2^27, all 54 arm-A curves agreed), t2, B, |X|, g, a, b for arm A/B
   (54 curves) and arm C (18 curves, BSGS) as IM-6 allows. No convention count, coverage, ratio or split frequency
   was computed on any contract cell. The generated q_n and s_n are in the plan; q_n agrees with the
   specification's list (recorded in the plan and in KAT T1).
4. **Interpretations the specification leaves open** (listed in `code/README.md`): cell-id format; the draw of
   (a, b) from the generator; no j-in-F_q rejection at n = 1; T_X taken from IDEA L4; B2 read as 12 cells with two
   instances each and unordered n-subsets of X; every 100th B1 tuple as the 1 percent group-law subsample;
   replicate numbering of the A/A seeds; arm-C target exclusion of S classes; the approval-lock content; the
   meaning of the independent recount (reversed order plus reference arithmetic); the P2(iv) residual is the
   count of targets with T_X > T_M and the T_M recount mismatch count (in `exhaustive_cell`'s `identities`,
   withheld in KAT mode).
5. **KAT discipline.** No KAT asserts a cross-convention identity or a value from the predictions; P2
   residuals and ratios are not written in KAT mode (tested) and not in `kat-log.json`. Development probes
   (scratch, not artifacts, deleted) on non-contract prime-field and F_{13^2}, F_{5^3} cells printed the P2
   residual counts while the kernel was being debugged; none was recorded or asserted.
6. **Housekeeping events.** A `pip download numpy` run from the repository root left a wheel file there; it was
   removed within the same session before any other action (no tracked file was involved). numpy and pytest
   were installed with `pip` into the Python 3.11 interpreter that `python3` resolves to (absent before), which is
   an environment change recorded here and in `environment.json`. Scratch files lived under the session
   scratchpad and were deleted at the end.
7. **Trial-plan reproducibility.** `make_trial_plan.py` was run three times (6 to 10 minutes each, sequential
   or concurrent); all outputs are byte-identical, sha256 `9ccbe614...fb4a`; the committed preview is the first of the
   final-code invocations and the second invocation (`--out` scratch) was compared with `cmp`.
8. **Blockers.** None. No value needed from the specification was missing; where it was silent the choices in
   item 4 were made and are stated, never written into the specification.

## Cells of the trial plan that need attention at approval

* Arm A/B/C counts are 54, 12, 12 (24 instances) and 18; the sum 96 matches the specification.
* Cells flagged `repeat_dominated_flag` (B < n^2) are listed in the plan identity fields.
