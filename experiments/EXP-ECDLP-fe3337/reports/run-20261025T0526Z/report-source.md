# Completed classical ECDLP finite diagnostic pilot

25 October 2026. **Observations only.** Experiment `EXP-ECDLP-fe3337`, run `RUN-ECDLP-d7f049`, hypothesis `H-ECDLP-98a95a`, goal `GOAL-ECDLP-087fc3`. All ten declared tracks produced outputs from five C++ programs, with up to three concurrent measurement processes. The genuine repository supervisor records `output_validated`, `measurement_complete: true`, and zero remaining trials. This qualifies output integrity; scientific review remains unverified.

The batch produced **241 rows**: 205 completed measurement rows, 24 completed control rows and 12 inapplicable residue-map rows. There were no failed, timed-out or truncated measurement modules. Five strict builds and all five development self-tests completed before the measurement pool. Supervisor wall time was **22.363381 seconds**, including builds, self-tests and the measurement driver. It is not a solver benchmark.

## Inputs and provenance

The eight public synthetic fixtures are an additive pilot at subgroup sizes 5, 6 and 8 bits. Six main fixtures are ordinary, non-anomalous and non-special-j; two j=0 fixtures are separate endomorphism controls. Exact field primes, coefficients, points, group orders, rejection history and certificates are in the [input manifest](../../../../harness/classical_ecdlp_pilot/protocol/fixtures.tsv) and its sibling preparation records. Input manifest SHA-256: `607f41f2ba6be5433a2095b82ccf94f6a991191f1fb53ab92fb271989cdcc18b`.

| Fixture | p | (a,b) | P | r | #E |
| --- | ---: | --- | --- | ---: | ---: |
| main-r5-0 | 61 | (1,4) | (41,55) | 19 | 57 |
| main-r5-1 | 37 | (29,3) | (30,30) | 17 | 34 |
| main-r6-0 | 127 | (13,45) | (26,68) | 41 | 123 |
| main-r6-1 | 127 | (95,36) | (38,15) | 47 | 141 |
| main-r8-0 | 457 | (73,39) | (193,306) | 211 | 422 |
| main-r8-1 | 383 | (299,157) | (199,117) | 199 | 398 |
| j0-r6-0 | 127 | (0,20) | (63,2) | 37 | 148 |
| j0-r6-1 | 127 | (0,62) | (65,42) | 43 | 129 |

The code and fixture snapshot was published before measurement. Exact-byte prospective admission returned `approvable: true` with no blockers. The approved selector returned `ready` with decision holds respected, and the genuine executor claim was committed and published before launch. Launch authority/source commit: `b7ce88e21bf2a96adaecb0cacd32c7a4ce7cb65b`. Raw-data archive commit: `6689f7036932ba0a4e9a9a6b6511af285a7987a0`.

All **110 sealed run files** are preserved. The 241 JSONL records occupy 22 of 64 declared part slots; unused slots are intentionally empty. The part manifest reconstructs 1,157,410 original bytes exactly. An isolated raw-plus-snapshot commit was checked by the unchanged repository `GitRepositoryVerifier` against all 111 paths, including its snapshot receipt. No sealed run file was edited during reporting.

The source [trial plan](../../trial-plan.json), [launch receipt](../../runs/RUN-ECDLP-d7f049/launch.json), [execution receipt](../../runs/RUN-ECDLP-d7f049/execution-receipt.json), [raw summary](../../runs/RUN-ECDLP-d7f049/raw-result.json), [parts manifest](../../runs/RUN-ECDLP-d7f049/parts-manifest.json) and [derived arithmetic summary](observations-summary.json) make the observations replayable. Compiler: g++ 14.2.0; runtime: Linux/Python 3.12.14; declared envelope: 12 GiB and driver plus three module workers. Module programs use no nested threads. Prior ASan/UBSan development checks disabled unavailable leak detection explicitly; the admitted measurements used optimized ordinary builds.

## Scope of completion

This campaign completed the implemented finite diagnostics and their control panels. It does not replace the larger 8/10/12-bit discovery panel or the blinded 192-target solver study in the parent plan. An EC-specific cancellation constructor, target-local decoder, global planar reduction and algorithmic advantage remain unsupplied where identified below. No quantum computation, simulated quantum attack, factor base, relation collection or index calculus was used.

\newpage

# Recorded observations from the admitted classical pilot

EXP-ECDLP-fe3337 / RUN-ECDLP-d7f049; source `b7ce88e21bf2a96adaecb0cacd32c7a4ce7cb65b`. The sealed supervisor receipt records `output_validated`; its checker records `output_integrity_pass`. This summary reads all 64 sealed part slots, checks their recorded hashes, and performs only labeled arithmetic on the recorded rows. No cryptographic calculation or trial was rerun, no inferential test was conducted, and this is not independent scientific review.

## Coverage

The five modules produced 241 rows covering all ten tracks. There are 205 `complete_valid`, 24 `complete_control`, and 12 `not_applicable` rows. D, L1, L2, L3, L5, L6, L7, and L8 each have eight fixture rows. L4 is one shared finite-grammar row. L9 has 22 projection families × eight fixtures = 176 rows; 164 are measured and 12 residue-map rows are inapplicable because d does not divide p−1.

The fixtures have subgroup orders 19, 17, 41, 47, 211, 199, 37 and 43. Six are main-stratum fixtures and two are separately marked j=0 controls. They are toy fixtures at 5, 6 and 8 subgroup bits, not the earlier proposed 8/10/12 discovery cohort or a blinded solver confirmation cohort. There are eight curves, not 614 independent curves.

## D — bit circuit instrumentation

Eight circuits contain 119,681–878,885 scalar gate nodes each. Derived totals: 832 scalar cases, 247,456 target-predicate cases, 828,896 tagged boundary cells, and 520 rejected corrupted witnesses. No discrepancy is reported in the completed rows; a separate numerical mismatch counter was not emitted. All rows explicitly record no new cancellation rule and no solver-gain claim. These are real deterministic forward gate circuits and exact fixed-window controls, not a new inversion algorithm.

## L1 — computable local section

The recorded section has nonzero additivity defects in every fixture: a derived total of 89,574 of 91,880 enumerated pairs. The fixed predictor has 25 hits across 614 targets, including its anchored labels; excluding 0,+1,−1 gives 9/590. The sum of the eight recorded matched-null mean hit counts on those nontrivial targets is 7.353535. Each fixture's observed score is inside its own 99-null minimum/maximum. This is a descriptive in-sample comparison, not a significance conclusion or decoder result.

| Fixture | Nontrivial hits / targets | Matched-null mean | Matched-null range |
| --- | ---: | ---: | ---: |
| pilot-main-r5-0 | 1/16 | 0.595960 | 0–3 |
| pilot-main-r5-1 | 1/14 | 0.747475 | 0–4 |
| pilot-main-r6-0 | 1/38 | 0.939394 | 0–4 |
| pilot-main-r6-1 | 0/44 | 0.868687 | 0–3 |
| pilot-main-r8-0 | 1/208 | 1.090909 | 0–4 |
| pilot-main-r8-1 | 0/196 | 1.090909 | 0–5 |
| pilot-endo_j0-r6-0 | 4/34 | 0.979798 | 0–5 |
| pilot-endo_j0-r6-1 | 1/40 | 1.040404 | 0–4 |

## L2 — EDS and finite prediction

Across the fixtures, the recorded checks include 606 EDS-coordinate checks and 1,088 Ward-identity checks. Every recorded EDS prefix complexity is one half its recorded prefix length; the final prefix length/complexity pairs are 20/10, 18/9, 42/21, 48/24, 212/106, 200/100, 38/19 and 44/22. These are finite-prefix measurements.

The 15-monomial quadratic grammar produced consistent fits only for the r=19 and r=17 fixtures: 36 fits total, all underidentified, with 2 exact matches among 235 untouched-window predictions. The other 578 translated target fits were inconsistent. The 99 shuffled controls per fixture produced 199 consistent fits (198 underidentified), with 23/1,303 prediction matches. These differently sized in-sample/null panels are reported as counts, not a comparative significance claim. Infinity-crossing windows remain explicitly excluded from this chart diagnostic. No nonlinear index locator was produced.

## L3 — known endomorphism redundancy

Negation was verified on all 614 canonical targets and its witness retained all 614 compatible scalars. The two j=0 rows have p=127, beta=19, and (r,lambda)=(37,10) and (43,6). Both subgroups were stable; all 80 action checks completed and every witness retained all r possible scalars. These are known-action controls with charged eigenvalue lookup, not new scalar information.

## L4 — the finite common-basis grammar

The 81 matrices with entries in {−1,0,1} contain 48 invertible matrices. None satisfies the complete signature bundle; all 48 first rejections are at AND. The row records eight signatures, 60,288 matchgate-identity checks and 199 calibration checks. This exhausts that exact finite grammar. It does not test every rational basis, every per-wire basis or another encoding; no global planar construction was produced.

## L5 — branch/CRT controls

For every fixture the explicit idempotent evaluation ranks are 2,4,8,16,32,64, equal to the retained labelled support at depths 1–6. Six fixtures have actual point-projection collisions once branch labels wrap around their subgroup; the two 8-bit fixtures do not wrap at these depths. The summed loss count is 208 across overlapping depths, not 208 distinct scalars. Canonical target pinning checks record 614 singleton targets and 614 incompatible-full-prefix empty cases. The original theorem-deferred quotient solver was not executed and no target-local constructive invariant was obtained.

## L6 — enumerated residual automata

| Fixture | x residual states | Full-point control | Null state range |
| --- | ---: | ---: | ---: |
| pilot-main-r5-0 | 50 | 50 | 50–50 |
| pilot-main-r5-1 | 45 | 48 | 48–48 |
| pilot-main-r6-0 | 104 | 104 | 104–104 |
| pilot-main-r6-1 | 110 | 110 | 110–110 |
| pilot-main-r8-0 | 127 | 127 | 127–127 |
| pilot-main-r8-1 | 127 | 127 | 127–127 |
| pilot-endo_j0-r6-0 | 100 | 100 | 100–100 |
| pilot-endo_j0-r6-1 | 106 | 106 | 106–106 |

Seven fixtures have the same bounded-depth state count as their full-point control. The r=17 fixture has 45 x states versus 48 full-point/null states. All x observations retain maximum scalar ambiguity two (303 two-element fibres plus eight singleton identity fibres across the fixtures); full-point controls have ambiguity one. The state vectors and scalar dictionaries were explicitly enumerated, so these counts do not supply a cheap constructor or public orientation decoder.

## L7/L8 — coefficients and integer receipts

The coefficient diagnostic checked 233,114 target/prefix cases using 116,864 charged truth-table entries across 614 targets. It records 614 detected coefficient mutations, 614 doubled-witness traps, and eight each of the many-solution parity, zero-polynomial orientation and naive-OR traps. ANF degree maxima are the scalar bit lengths 5,6,8; support is explicit rather than assumed small. No cheap coefficient evaluator was constructed.

The separately interpolated Fp count audit records 5,082 singleton prefixes and 228,032 empty prefixes, summing to the same 233,114 cases; these share the L7 truth data and are not independent confirmation. All eight nonnegative Ax–Katz lower-bound exponents are zero. No non-Boolean root of z(z−1) was found in the complete one-coordinate field checks. Eight explicit receipt pairs [0,p] demonstrate the ambiguity of a divisibility-only existence receipt. The polynomial is truth-derived; a gate-polynomial compiler and fast exact-residue constructor are not claimed.

## L9 — exact finite entropy panel

All 164 applicable projection/fixture rows use exact full-pair integer histograms, with numerical log2 for entropy and 99-draw relabeling references. Of these rows, 132 have the sign-pair matched reference; unconditional relabeling is secondary for these negation-invariant projections. Full-point and constant projections both report zero conditional entropy, documenting why entropy alone is not a recovery criterion.

| Fixture | Kummer entropy (bits) | Delta vs unconditional mean | Delta vs matched mean |
| --- | ---: | ---: | ---: |
| pilot-main-r5-0 | 0.897506925 | -0.678716093 | 0 |
| pilot-main-r5-1 | 0.885813149 | -0.642558893 | 0 |
| pilot-main-r6-0 | 0.951814396 | -0.842651632 | 0 |
| pilot-main-r6-1 | 0.957899502 | -0.858079489 | 5.42e-20 |
| pilot-main-r8-0 | 0.990543788 | -0.967105299 | 0 |
| pilot-main-r8-1 | 0.989975001 | -0.965234472 | 0 |
| pilot-endo_j0-r6-0 | 0.946676406 | -0.821349364 | 0 |
| pilot-endo_j0-r6-1 | 0.954029205 | -0.847028201 | 0 |

The recorded Kummer entropies match the known finite-r value (1−1/r)^2 to printed precision. Although their unconditional-reference differences range from −0.967105 to −0.642559 bits, the matched-reference differences are 0 to 5.42×10⁻²⁰ bits. This comparison retains the known sign structure; it is not a new scalar-leakage result.

Other declared panel members retain descriptive gaps. For example, x modulo 7 has recorded primary-reference differences from −0.065459 to −0.001195 bits across the eight fixtures. The single applicable fifth-power-residue row has a −0.206438-bit difference. The full 22-member range table is in the JSON summary. No inferential test, multiplicity adjustment or propagation-decoder experiment was performed, so these values carry no significance or attack claim.

## Practical limits

The admitted run completed the finite pilot and its controls. It did not complete an ECDLP attack, establish novelty, estimate a better exponent, compare full solver cost with rho, or close any unlimited mathematical family. The fixture-level observations and all inapplicable rows are retained; repeated targets and shared truth tables are not independent replications. This same-session summary changes no scientific state and is not independent validation.

\newpage

## Recorded execution and circuit sizes

![RUN-ECDLP-d7f049: actual module start/end intervals. Builds and self-tests ran sequentially first. Different workloads and concurrent host load preclude interpreting these durations as algorithm comparisons.](execution.pdf){width=95%}

![RUN-ECDLP-d7f049: gate-node counts recorded for all eight forward circuits. Blue: main curves; amber: separate j=0 controls. No extrapolation or inversion complexity is inferred.](circuits.pdf){width=95%}

\newpage

## Exact entropy observations and controls

![RUN-ECDLP-d7f049: eight Kummer rows. Observed full-pair entropy is exact apart from numerical logarithms; bars show the spread of the 99 unconditional null draws, not uncertainty on an attack gain. Matched means coincide with observations to roundoff.](kummer-controls.pdf){width=95%}

![RUN-ECDLP-d7f049: all 22 projection families on eight fixtures. Primary reference is sign-pair matched for negation-invariant projections and unconditional otherwise. Gray cells are inapplicable power residues. Differences are descriptive, without significance, multiplicity correction, or scalar-recovery interpretation.](projection-panel.pdf){width=86%}
