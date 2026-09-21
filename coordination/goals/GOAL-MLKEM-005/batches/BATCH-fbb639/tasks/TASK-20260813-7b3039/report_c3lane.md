# report_c3lane.md -- TASK-20260813-7b3039 (THE LEAD PRODUCER)

    goal / batch    GOAL-MLKEM-005 / BATCH-fbb639
    role            executor (policy executor-implementation, effort medium)
    governed_by     PREREG-3 (coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-0eb5a3/prereg.md),
                    notarized 3d2eabf8ddfa9e33ed3c9cf5b0cc0d9f14ebcd82, sha256
                    3f64e2688f0d52b93ad2428ffa99883b0234edeb47aff0c242628a6d880c7138 (confirmed
                    by this task via sha256sum, see command.txt line 5)
    claim tier      TOY, unconditionally. Nothing here bears on ML-KEM security, any FIPS 203
                    parameter set, any attack cost or any cost model.
    certificate     kind: none -- no discrete-log solve, no factor-base relation claimed or
                    produced.
    NO REDUCTION OF ANY KIND WAS PERFORMED BY THIS TASK. fpylll is not imported, installed or
    invoked anywhere in this task's own code; python3 -c "import fpylll" in this task's own
    environment raises ModuleNotFoundError (command.txt), confirming the constraint is not
    merely a promise.

---

## (a) RC-1 -- carried verbatim from PREREG-3 section 1, NOT recomputed

> The headline count of BATCH-6b6e78's PREREG-2 measurement is 1,313 changing
> VAR-F cells, not 1,416. The 1,416 figure in the committed results_a1.json
> and report_a1.md of TASK-20260813-2ce014 arose because measure_a1.py's
> binary32 route R4 accumulates the Gram at the working precision
> (Bf @ Bf.T with Bf = B.astype(dt)), which does not match what its own
> route_provenance field declares it does (form the Gram in exact int64 and
> cast once). Under the declared provenance the count is 1,313. This
> supersedes the 1,416 figure and its by-route / by-candidate /
> by-fibre-family decompositions, the FC-3a count of 868 (or 867), the R4
> binary32 K-interval endpoints 5.272e+06 / 1.750e+04, and the binary32
> "6 of 38" diagnostic wherever any of them is quoted without this correction
> in the same sentence.

What is unchanged (also carried, unaltered): the qualitative headline -- 49 of
330 blocks change verdict; concentration on routes R4 and R2 only; zero
contribution from R0, R1, R3, R5 -- is invariant under both readings and is
not touched by this correction. Route R2's own contribution of exactly 20 is
unaffected. Neither this correction nor its predecessor touches
T-A1-FALSIFIED-PARTIAL, which remains the branch that fired.

This task performed NO recomputation. measure_a1.py, results_a1.json and
report_a1.md (commit 4e466c6bf221ea002fe84311baccdb816081a8cd) were not read
for the purpose of re-deriving this number, not edited, and not re-run. The
text above is quoted from PREREG-3 section 1 exactly as frozen.

## (b) RC-2 -- carried verbatim from PREREG-3 section 2, NOT recomputed

> report_a1.md section 10 of TASK-20260813-2ce014, and the archive commit
> message the parent harness session wrote for TASK-20260813-48240d
> (4e466c6bf221ea002fe84311baccdb816081a8cd), both state that "the automated
> P-A12a register line in results_a1.json is mis-scored HELD; corrected to
> FALSIFIED ... with the JSON left unedited." THAT CLAIM IS FALSE AGAINST THE
> COMMITTED ARTIFACT. results_a1.json's
> PREDICTION_REGISTER.items["P-A12a"].OUTCOME reads "FALSIFIED", not "HELD"
> -- the string "HELD" does not occur against P-A12a anywhere in the
> committed file, confirmed independently by the Coordinator that decided
> DEC-20260813-c60bba and by the Validator's finding F-2
> (EV-MLKEM-4ba196.finding_1_narrative_correction). P-A12a's committed
> OUTCOME is, and always was, FALSIFIED. This is a correction of a
> description, never of a measurement: the substantive value -- FALSIFIED at
> 22 cells (X_null 12, rdet 10, both route R2_QR_of_BT) -- was correct
> throughout, in both the JSON and report_a1.md's own corrected table, and
> needs no correction.

The immutable commit 4e466c6bf221ea002fe84311baccdb816081a8cd and its message
are NOT edited, NOT touched, and NOT re-run by this task. This task
independently re-confirmed, by reading only, that results_a1.json's
PREDICTION_REGISTER.items["P-A12a"].OUTCOME is the literal string
"FALSIFIED" (verified with a direct read of the committed file; the string
"HELD" occurs 3 times elsewhere in that file, never against P-A12a). This
confirms -- not recomputes -- PREREG-3 section 2's own reading. No code was
executed for RC-2's numeric content; the confirmation above is a read, not a
measurement, exactly as PREREG-3 section 2 requires.

---

## (c) PART (c) -- THE LEAD MEASUREMENT

### Obligation 0 -- the coverage audit (FIRST, before any comparison)

1. results_relvar.json's per_candidate block. Path-precision note: the field
   actually lives at G_VAR.per_candidate.<X>.per_cell.<L>_<b>.float_sd in the
   committed file, not at a bare top-level per_candidate PREREG-3's prose
   names -- this is a note about where the already-declared value lives, not
   a disagreement about the value itself (measure_c3lane.py reads it from the
   corrected path and the values obtained match PREREG-3 section 4's own
   attributed spot-checks -- lam1n L7 float_sd 0.0434(...), hkz L7
   0.0239(...)/0.0106(...) -- exactly). s_c^fib was read for all 27 cells (9
   per candidate); every read succeeded
   (results_c3lane.json.R-C-OUT-1_per_cell_comparison.*.s_c_fib, none is
   null).

2. results_l7l8.json, L7-only subset. Extracted the 3 L7 betas x 2 candidates
   (lam1n, hkz) from comparison.per_cell, discarding the L8 entries. All 6
   cells: max_abs_deviation = 0.0, n_bit_identical_of_8 = 8 -- i.e. 8 of 8
   matched bases, bit-identical, at every L7 cell for both candidates. See
   results_c3lane.json.R-C-OUT-0_l7l8_l7_only_extract.

3. results_am4.json construction-comparability check -- VERDICT: MATCHES.
   Checked, not assumed, against results_relvar.json's own declared
   construction:
   - (d, k) per lattice, read from results_am4.json's own
     instrument_checks.x9_pipeline_crosscheck block: L7 (d=20,k=6), L9
     (d=30,k=9), L11 (d=40,k=12) -- all three match the frozen family F0
     exactly.
   - Seed formula: results_am4.json declares the basis matrix A built with
     default_rng([1,d,k,i]), textually identical to results_l7l8.json's own
     declared A_seed_recipe = np.random.default_rng([1, d, k, i]).integers(0,
     q, (k, d-k)).
   - AM-9 k-convention: results_am4.json's own top-level k_convention_AM9
     field declares k = |K_I| (identity block), matching the binding carry.
   - Bit-identical cross-check: results_am4.json's gates.<X>.G_REL1.all
     entries for L9/L11 report a single value per lattice (X_lo), read at
     basis index 0 by construction. Compared directly against
     results_relvar.json's own committed G_REL1.<X>.<L>.per_basis[0].X_a:
     bit-identical (abs_deviation = 0.0) at all four checked cells
     (lam1n/L9, lam1n/L11, hkz/L9, hkz/L11) -- see
     results_c3lane.json.R-C-OUT-0_am4_construction_check.basis0_bit_identical_check.

   This is a genuinely independent computation: measure_am4.py (its own
   committed script) imports and runs fpylll directly (BKZ pass + explicit
   HKZ sweeps, the same pipeline shape as measure_relvar.py's, but executed
   in a different environment -- macOS-26.6-arm64 / Python 3.13.1 / numpy
   2.4.0 / scipy 1.15.3 vs. measure_relvar.py's own recorded environment --
   on the same frozen seed/construction. It is not read from
   results_relvar.json.

   Verdict: results_am4.json IS a valid ROUTE-I for lam1n/hkz at L9/L11,
   restricted to the ONE matched basis (index 0) that results_am4.json's
   gates block reports -- results_am4.json reports no per-basis breakdown at
   L9/L11 beyond this single value, so n_matched_bases = 1 (not 8) at every
   L9/L11 covered cell, and this is reported honestly rather than assumed to
   be 8.

4. Broader search, beyond forced_arithmetic. results_relvar.json's
   forced_arithmetic block contains exactly one rawtail-related entry
   (rawtail_T1_ambient_isometry_residual_beta5 = 5.808686864838819e-13, the
   ROUTE-W proxy PREREG-3 section 3.1 already names) and no lam1n/hkz-related
   entry. This task's own broader search (grep for rawtail across
   coordination/goals/GOAL-MLKEM-005) found ONE further candidate PREREG-3
   did not name:
   coordination/goals/GOAL-MLKEM-005/batches/BATCH-4ed139/tasks/TASK-20260812-56b9da/report_gvar2.md
   and its results_gvar2.json, which report a rawtail recomputation labelled
   RD_rawgso_no_reduction reproducing the committed values at 38/38 cells,
   max absolute difference 0.0. It is reported here, with its path, and NOT
   counted as a ROUTE-I: its own report states the underlying functions were
   "TRANSCRIBED VERBATIM" from measure_relvar.py and runs on the SAME
   deterministic raw-basis construction -- a fidelity check on the
   transcription, not an algorithmically independent second computation --
   and its own producing report's prediction table labels it "P-V1 |
   CONSISTENCY CHECK (AM-15(a))", never a route or a prediction. No further
   independent-computation source for any of the three candidates at
   L7/L9/L11 was found by this search; a search that finds nothing is
   reported as having found nothing (see
   results_c3lane.json.R-C-OUT-0_forced_arithmetic_search).

Coverage table (R-C-OUT-0), summarized -- full table in
results_c3lane.json.R-C-OUT-0_coverage_table:

| candidate | L7 (3 cells) | L9 (3 cells) | L11 (3 cells) | source |
|---|---|---|---|---|
| lam1n | COVERED | COVERED | COVERED | results_l7l8.json (L7); results_am4.json (L9/L11, 1 matched basis) |
| hkz | COVERED | COVERED | COVERED | results_l7l8.json (L7); results_am4.json (L9/L11, 1 matched basis) |
| rawtail | 1 ROUTE-W (L7 b5, non-equivalent proxy, NOT counted) + 2 UNCOVERED | UNCOVERED | UNCOVERED | none valid |

18 of 27 cells COVERED (lam1n 9/9, hkz 9/9, rawtail 0/9 counted). 1 rawtail
cell (L7 b5) has a labelled, non-equivalent ROUTE-W reported separately and
excluded from the tally.

### Obligation 1 -- per-covered-cell comparison, absolute units

D_route(X,L,b) = 0.0 at every one of the 18 covered cells (bit-identical at
all matched bases -- 8/8 at L7, 1/1 at L9/L11). s_c^fib(X,L,b) is strictly
positive at every one of those 18 cells (range: lam1n 0.0388-0.0848; hkz
0.0038-0.0239). Since ties resolve to "DOES NOT EXCEED" and none of these are
ties (s_c^fib > 0.0 = D_route strictly, at every covered cell), all 18
covered cells verdict "EXCEEDS". Full per-cell table (s_c^fib, D_route,
matched-basis count, verdict, source path) is in
results_c3lane.json.R-C-OUT-1_per_cell_comparison.

| candidate | lattice | beta | s_c^fib | D_route | matched bases | verdict |
|---|---|---|---|---|---|---|
| lam1n | L7 | 5/10/15 | 0.043392 | 0.0 | 8 | EXCEEDS |
| lam1n | L9 | 7/15/22 | 0.084759 | 0.0 | 1 | EXCEEDS |
| lam1n | L11 | 10/20/30 | 0.038847 | 0.0 | 1 | EXCEEDS |
| hkz | L7 | 5 | 0.023888 | 0.0 | 8 | EXCEEDS |
| hkz | L7 | 10 | 0.010639 | 0.0 | 8 | EXCEEDS |
| hkz | L7 | 15 | 0.008880 | 0.0 | 8 | EXCEEDS |
| hkz | L9 | 7 | 0.012888 | 0.0 | 1 | EXCEEDS |
| hkz | L9 | 15 | 0.006916 | 0.0 | 1 | EXCEEDS |
| hkz | L9 | 22 | 0.003893 | 0.0 | 1 | EXCEEDS |
| hkz | L11 | 10 | 0.010109 | 0.0 | 1 | EXCEEDS |
| hkz | L11 | 20 | 0.007207 | 0.0 | 1 | EXCEEDS |
| hkz | L11 | 30 | 0.003818 | 0.0 | 1 | EXCEEDS |

rawtail -- 8 cells "NO ROUTE-I: UNCOVERED"; 1 cell (L7 b5) labelled ROUTE-W
(non-equivalent proxy, NOT counted): s_c^fib = 0.15458281304604785 vs.
D_ROUTE-W = 5.808686864838819e-13 (informational only; the residual compares
raw-basis GSO logs under an ambient isometry -- a numerical-stability
control, not a post-reduction rawtail recomputation -- and is never counted
in obligation 2).

### Obligation 2 -- aggregate

COVERED = 18 of 27 cells (9 lam1n + 9 hkz). SOME-EXCEEDS holds: all 18
covered cells verdict EXCEEDS, 0 DOES NOT EXCEED. Coverage fraction: 18/27.
rawtail: 8 cells UNCOVERED, 1 cell ROUTE-W-labelled and excluded from this
tally.

### Obligation 3 -- the termination branch

COVERED is non-empty and SOME-EXCEEDS holds (at least one covered cell -- in
fact all 18 -- has s_c^fib > D_route). Under PREREG-3 section 3.5's
precedence, T-C3LANE-NODATA does not fire (COVERED is not empty), and
between T-C3LANE-OBSTRUCTED / T-C3LANE-OPEN, SOME-EXCEEDS takes precedence:

> T-C3LANE-OPEN -- "FIRES WHEN COVERED is non-empty and SOME-EXCEEDS holds
> (dispersion exceeds route disagreement at at least one covered cell)."

Coverage is 18/27 < 27/27, so the -PARTIAL suffix applies per PREREG-3
section 3.5's own rule.

BRANCH FIRED: T-C3LANE-OPEN-PARTIAL.

What this licenses, quoted from PREREG-3 section 3.5, and nothing more: "a
statement that 'a successor assumption analogous to A-1, restricted to the
reduction-dependent candidates and to the covered cells/routes, has a domain
worth stating' -- and nothing stronger."

What this forbids, quoted from PREREG-3 section 3.5: "treating this as A-1
held for lam1n/hkz/rawtail (A-1 was never stated over them and this
measurement does not state it now); specifying any dispersion criterion,
fibre clause or gate on the strength of this branch alone; any claim about
ML-KEM, any FIPS 203 parameter set, any attack cost or any cost model;
closing, pausing or completing GOAL-MLKEM-005."

Relation to the frozen predictions (PREREG-3 section 4, not re-scored here,
only read off): P-C3a (COVERED non-empty) is realized. P-C3b (ALL-CLEAR over
COVERED) is NOT realized -- SOME-EXCEEDS holds instead, at every one of the
18 covered cells, not only the 3 L7 cells PREREG-3 section 4's own
attributed pre-dispatch reading flagged as already-visible. This is reported
as the measured outcome; it is not treated as a surprise to be argued away,
per this task's constraints, and it is not extended into any dispersion
criterion, gate, or working assumption -- T-C3LANE-OPEN's licence is a bare
statement that a domain is worth stating, nothing stronger, exactly as
PREREG-3 states.

Scope, restated. This measurement is q = 3329; d in {20, 30, 40} (L7, L9,
L11 only); the frozen beta grids of PREREG-3 section 3.1; N_BASES = 8 (8 at
L7, 1 matched at L9/L11); binary64 fibre dispersion only. It says nothing
about A-1, the in-scope candidates of PREREG-2 2.4, X_gso_k, any
determinant-only candidate, ML-KEM, any FIPS 203 parameter set, any attack
cost, or any cost model. AM-3 is not retired; BATCH-a44d08 is not rescored;
BATCH-4ed139, BATCH-9e3584, BATCH-cbe023 and BATCH-6b6e78 are not
revalidated by anything read here.

---

## Objection, recorded per instruction and NOT acted on

This task's own read of results_am4.json found only ONE matched basis (index
0) at L9/L11, not the 8 that L7's ROUTE-I provides. PREREG-3 section 3.3
defines D_route as a max over "the matched bases ... or the subset both
routes actually cover -- report the subset size", which this task followed
exactly (n_matched_bases = 1 reported honestly at every L9/L11 covered
cell). The objection: a 1-basis D_route is a weaker disagreement estimate
than an 8-basis one, and a reader could reasonably ask whether EXCEEDS at
L9/L11 would survive an 8-basis ROUTE-I if one existed. PREREG-3 is frozen
and does not ask this task to weight cells by matched-basis count or to
qualify the verdict on that basis, so this task scores the frozen clause
exactly as written and records this asymmetry here rather than adjusting the
verdict or the branch.

---

## Artifacts -- every path this task wrote (SEVEN, all inside write_scope)

    coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/measure_c3lane.py
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/results_c3lane.json
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/report_c3lane.md
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/command.txt
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/stdout.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/stderr.log
    coordination/goals/GOAL-MLKEM-005/batches/BATCH-fbb639/tasks/TASK-20260813-7b3039/run_manifest.yaml

No file was written outside this set. No __pycache__ was created (python3 -B
with PYTHONDONTWRITEBYTECODE=1 throughout; verified by directory listing
after every invocation). task_card.md in this directory pre-existed this
task's run (part of the batch-opening coordination artifacts) and was not
written or modified by this task.

Budget: 1 measurement invocation (measure_c3lane.py), elapsed approx 0.06 s,
peak child RSS approx 17 MB -- far inside the 600 s measurement cap, the
1800 s wall budget, and the 2 GB memory cap. maximum_runs: 1 honored; a
second, reproduction-check invocation to a scratch path OUTSIDE the
repository (byte-identical output, used only to confirm determinism) is
disclosed in run_manifest.yaml per this task's enumerate-every-invocation
instruction.
