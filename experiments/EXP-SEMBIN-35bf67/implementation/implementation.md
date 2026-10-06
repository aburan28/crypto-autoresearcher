# EXP-SEMBIN-35bf67 implementation note (TASK-20261002-530540)

Executor implementation and protocol-deviation note. The reproduction-package convention
puts `implementation.md` at the experiment root; the handoff write_scope does not include
that path, so it lives here (deviation D-1).

## 1. Components (all under implementation/)

| file | role |
|---|---|
| sizes.py | Stage-0 size worksheet (pure arithmetic) |
| builder.py | F_{2^n} arithmetic, minimal-weight / Conway moduli, Weil descent of eq. (5) for t in {2,3}, instance generation (OP-INSTANCE), T11 boolean_null (OP-NULL), EXP-DREG-001 anchor rebuild without Sage |
| sols.c | exact solution count: S-A (S_3 as a quadratic over V or V^2) and S-B (group law on E over F_q / F_{q^2}); separate code paths sharing only base-field helpers |
| exhaust.c | S-C: Gray-code exhaustive evaluation (first/second/third derivatives), prefix-split; plus a naive evaluator ("check") |
| solv4.c | SOLV4 driver shared by both arms: system parsing, monomial indexing (degree-descending columns), Macaulay rows, closure products, compact RREF bookkeeping, early stop, Macaulay-rank and calibration modes |
| kernel.h / kernel_a.c / kernel_b.c | the GF(2) linear-algebra kernels: arm A = M4RI release-20240729 (mzd_addmul, mzd_echelonize_pluq); arm B = executor C (Gray-code four-Russians product, Gauss-Jordan) |
| build.sh | builds M4RI from source at git d0a1ee18 (not the apt 0.0.20200125 package) and all binaries |
| pipeline.py | per-instance orchestration, CPU/RSS caps, dual-arm comparison, resumable records |
| stage1.py / stage23.py / census.py / stats.py / runlib.py | stage drivers, census and mechanical label rule, statistics, run-record helpers |
| dev-log.md | every development test before the Stage-1 gate (not evidence) |
| schedule-allocation.md | session-level allocation fixed before any Stage-1 smoke / Stage-2 outcome |

## 2. How the frozen protocol was implemented

- Stage 0: sizes, preregistered predictions, cell schedule and a sources-read list were
  written and hashed (stage0/FREEZE.json, 2026-10-05T05:20:28Z) before any Stage-1 code
  existed. Files were then made read-only. N1 blindness: EXP-SEMBIN-7e1371 and
  DEC-20261004-df2986 were never opened (stage0/sources-read.md).
- SOLV4 (OP-R4 / OP-SOLV4): degree-4 capped closure in the Boolean ring, columns ordered by
  degree descending so that RREF rows with a degree <= 3 pivot span W n B_{<=3}; each round
  multiplies (snapshot) new low rows by every variable. The RREF of the current space is kept
  compactly (pivot rows restricted to non-pivot columns); because the RREF of a subspace is
  unique, both arms must agree on the rank after every 8,192-row chunk and on per-round digests.
- Exact s (OP-S): S-A and S-B on every primary instance, S-C additionally at N <= 30; solution
  SETS (not only counts) must coincide. The SOLV4 driver re-evaluates every supplied solution
  against every descended equation (points_failing_system).
- Dual rank (OP-DUAL, SR-4): arms run as separate processes on the identical generator file.
- Caps (OP-CAPS): RLIMIT_CPU 28,800 s and an 8 GiB RSS watchdog per arm process.

## 3. Protocol deviations and interpretations (all recorded; none edits the frozen contract)

- D-1 (location). implementation.md / analysis are written under implementation/ and RESULTS.md,
  not at the experiment root, because the handoff write_scope excludes the root paths.
- D-2 (operationalizations, gap G3). 'Arm', instance generation, the R_4 fixpoint, the early-stop
  rule, the null construction and its s method, 'matches' (null), 'separates' (off-diagonal),
  the Kosters condition, the caps reading, the statistics and the single-label precedence were
  not fixed by the contract. They were pre-registered as OP-* in
  stage0/preregistered-predictions.json BEFORE any Stage-1 output and are submitted for
  Coordinator ratification. If any is read differently, results are re-derived from the raw
  records (instances.jsonl) under an amendment.
- D-3 (Stage-3 ladders not run, gap G1/G2). The fixed-k ladders have no (m, t) in the contract
  and arity_m levels {2,3} exclude Semaev's k = 4 rows (m = t = 4); the dphi/dk / dphi/dn fit
  has no model. Not run; recorded in stage3/shortfall.json; amendment requested. The
  off-diagonal gate (fully specified) was run as allocated.
- D-4 (gap G4). H-SEMBIN-d895d9 test_boundary lists B = 1 vs random B, sparse vs random f and
  low-degree vs random V controls 'at one cell'; the specification's controls do not, and no
  cell is named. Not run.
- D-5 (sample sizes). The frozen targets (>= 100 per arm per decisive cell, >= 50 per arm per
  Stage-3 cell) were not reached at most cells. Counts are what the pre-declared session
  allocation (implementation/schedule-allocation.md) produced; shortfall per cell is in each
  run's raw-result.json and in stage2/census.json. Cells (25,3,3,9), (50,2,2,25) and
  (25,3,3,10) were not executed (allocation 0 h; per-arm cost estimated 1.5-10 h).
- D-6 (null arm). Null s by exhaustive Boolean evaluation only (the point-arithmetic
  cross-check does not exist for a null system). Null arms at N > 42 are O-CENSORED by OP-NULL;
  the (21,3,3,7) null (N = 42, cubic, ~3.4 CPU-h per instance) received zero allocation.
- D-7 (dual-arm independence disclosure, J2). The arms share solv4.c: system parsing, monomial
  indexing, Macaulay/product row generation and the compact-RREF bookkeeping (column maps,
  pext gathers/compaction). They share no GF(2) arithmetic kernel: arm A uses M4RI
  release-20240729 (source build at d0a1ee18; apt 0.0.20200125 never installed or linked),
  arm B uses kernel_b.c. The shared layer is checked against external ground truth (both DREG
  anchors, hash-identical systems; planted-rank calibration with an injected deficiency;
  known-false objects), not by the dual-arm comparison itself.
- D-8 (instance retention). Per-instance system files are not retained (size); each record holds
  system_sha256 and the deterministic seed namespace, so systems are regenerable with
  builder.py. Solution sets (SAT instances) and both arms' JSON outputs are retained.
- D-9 (sub-chunking). Arm A inserts 2,048-row and arm B 1,024-row sub-chunks inside each
  8,192-row trajectory chunk; RREF uniqueness makes the per-chunk rank trajectory comparable.
- D-10 (aborted run). RUN-SEMBIN-5cf90a (first smoke) was stopped by the executor after a
  performance defect in sols.c (dev-log D18), before any SOLV4 computation; retained with status
  aborted_infrastructure; the smoke was rerun as RUN-SEMBIN-814631 on the same seed namespace.
- D-11 (timing context). Two instances x two arms run concurrently on 4 vCPUs; wall times are
  measured under that load (memory-bandwidth contention), CPU seconds are per process.
- D-12 (DREG anchor conventions). Reproducing the EXP-DREG-001 system hashes required Sage's
  Conway modulus, lift_x y-values in ascending order, and PolyBoRi's reversed variable indexing
  under order='degrevlex' (found by exhaustive R_X search, dev-log D2-D6). Recorded as an
  observation about the DREG builder's variable labelling; rank is labelling-invariant.
- D-13 (literal multiplier rule). OP-R4 admits m*f with deg m <= 4 - deg f and closes under
  variable products of degree <= 3 elements. Products m*f whose Boolean degree is <= 4 only
  through x^2 = x cancellation with deg m > 4 - deg f are not admitted separately unless the
  closure reaches them (449d2b's sketch 'deg(m*f) <= 4' read as the standard XL multiplier rule).

## 4. Continuation after the 2026-10-05 container restart (appended by the continuation session)

Entries D-1..D-13 above were written by the first executor session and are left as written.
Some of them (D-3, D-5, D-6) describe the expected end state of the full schedule. Whether
it was reached is shown by the continuation runs listed in continuation-allocation.md.

- D-14 (infrastructure interruption). The container restarted during RUN-SEMBIN-633f0c
  (Stage-2 (40,2,2,20)). Last write 09:33:51Z; host back about 13:17Z. The run directory is left
  exactly as found (no manifest, no raw-result, 4 VALID instance records, 24 classifications).
  The note runs/RUN-SEMBIN-633f0c.INFRA-INTERRUPTION.yaml was added beside it. Class:
  infrastructure_error / failed_infrastructure (SR-8). It is not evidence. The cell was
  re-executed in full as RUN-SEMBIN-cfd1a7 (same stage tag, args, seeds, code and binaries).
  The partial records are not merged into any census.
- D-15 (continuation schedule and run ids). run_schedule.sh is not re-invoked, because its
  in-place resume would modify the completed RUN-SEMBIN-24e9d9. The new
  run_schedule_continue.sh runs items 2-8 with freshly minted ids, and the extras under the
  "wall time remains" reading declared in continuation-allocation.md before any continuation
  output. The run_schedule.sh ids for items 3-8 were never instantiated.
- D-16 (hash bookkeeping). After launch, one comment line (the "Written ..." timestamp) of
  run_schedule_continue.sh was corrected. The running shell kept the original inode. The
  implementation_sha256 of that file differs by this comment only: RUN-SEMBIN-cfd1a7's
  environment.json records the pre-edit value 7d8feedd...97650, and the post-edit value is
  ee29018d...dc750dda. No code that computes anything changed. stage23.py, pipeline.py,
  builder.py, stats.py, runlib.py and the C sources hash identically to RUN-SEMBIN-24e9d9's
  manifest, and the binaries match.
