# implementation.md: EXP-CERTBIN-ddfe75 / RUN-CERTBIN-6ebb0e

Executor note for TASK-20260924-7c1fb2. It records how the frozen specification
(version 1, sha256 40ebb628b5119b08e58cd3e991008bd2989474a8032b67483630c602319389be,
byte-identical to HEAD 2b58093c3) was implemented. It also lists every
deviation, reading and unexpected observation. It interprets nothing beyond the
mechanical decision rules.

## Execution summary

- Launch: a single bash script (see command.txt). Steps: phases 0-4, then C-DET
  (separate process), then the verifier (separate process), then `--resume`
  (phase 7). Every step exited 0 and stderr.log is empty. Each invocation is
  logged in checkpoint/invocations.jsonl.
- Wall-clock times: phases 0-4 took 4 min 18 s (engine replay 66.6 s, pytest
  5.2 s, self-test 14.0 s, phase 4 133.6 s). C-DET took 15.7 s, the verifier
  106.4 s and phase 7 7.3 s. The driver's peak RSS is in manifest.yaml.
- Runs used: 1 of maximum_runs 2. There was no infrastructure failure, no
  watchdog expiry and no resume after a crash.
- Machine protection: `ulimit -v 3145728` (3 GiB address space) was set in the
  launch shell, and the driver also calls setrlimit(RLIMIT_AS, 3 GiB).
  CRYPTO_AR_GF2_THREADS=2, lowered from the specification's default of 3
  because another CERTBIN executor (EXP-CERTBIN-060020) was dispatched onto
  the same 4-core machine. One process ran at a time.
- Source state: HEAD 2b58093c3 with a dirty tree. The dirty paths are all
  untracked: this task's impl/, verifier/, trial plan and run directory, plus
  the concurrent executor's experiments/EXP-CERTBIN-060020/impl/ and verifier/.
  No tracked file was modified. The engine package tree equals 934bee5's (tree
  c612830f), and _kernels.c has the pinned sha256. The package's ignored
  `__pycache__/` existed before this task and is recorded in
  engine-provenance/summary.json.

## Deviations from the specification (all disclosed, none changes a threshold, arm, seed or rule)

1. **Fresh-system keys.** The specification writes the key as `"<ARM>:<slot>"`.
   Each slot keeps two systems (unsat and sat), so fresh keys are
   `"<ARM>:<slot>:<role>"`. Archived arms keep the RC-1 keys. NELL-A20 keys are
   `"NELL-A20:<label>"`. Recorded before any data as trial-plan reading R1.
2. **pytest flag.** C-ENGINE (d) ran
   `python3 -m pytest -q -rs -p no:cacheprovider tests/test_gf2_kernels.py`.
   The added `-p no:cacheprovider` stops .pytest_cache from being written into
   the shared worktree. It does not change test selection or outcomes
   (9 passed, 0 failed, 0 skipped).
3. **Certificate lines.** certificates.jsonl.gz has one line per
   (system, closure, format), not one per (system, closure):
   - M_4 flat-v1 (engine);
   - W_4 flat-v1 (engine). It counts toward W_4 only if max |mu| <= 2 and is
     never used for w;
   - W_4 wdag-v1 (extractor). This is the only format counted for w.

   Recorded as trial-plan reading R3.
4. **Order of archived-arm closures.** Phase 1 needs the M_3, M_4 and W_4
   records of the archived arms for C-REG, so it computes them, and phase 4
   reuses them. For archived systems, the rc_b/T5 predictions were therefore
   written after their W_4 had been computed. Those W_4 values were already
   archived (RC-1 and the red team). For every fresh system, rc_b and the T5
   prediction were written and hashed before any M_4 or W_4 was computed on it
   (EX-5). predictions-t5.jsonl.gz sha256 2e6ae615... is in phase-log.jsonl
   before phase 4 starts. Recorded as trial-plan reading R7.
5. **Additional self-test.** The self-test adds
   `extractor_depth_ge2_extra`, which the specification does not require. It
   takes 5 refuted small systems (8 variables, D = 3) whose 1 first appears at
   iteration 2. The wdag extractor is checked on them by the verifier's rules
   in-process, and the literal fixpoint is compared. The 30 specified small
   systems had 5 with fixpoint index >= 2, so no system had to be
   constructed. Their refutations reached depth 0 and 1 only, which is why the
   extra check exists.
6. **Development-only code paths.** common.py and verify_nconv.py read
   NCONV_DEV_SLOTS and NCONV_DEV_SEED_OFFSET. They exist only to debug the
   pipeline in a scratch directory, and both programs refuse to write under
   experiments/ when either is set. Both were unset for this run
   (environment.json; manifest `dev_overrides_unset: true`).
7. **Development dry run before the official run (disclosure).** One dry run
   of the whole pipeline ran in the session scratch directory. It used 6 slots
   and every fresh-arm seed offset by +7777, so the seeds were not the frozen
   ones. That dry run previewed dev-seed data: N-CONV 6/6 refuted, N-ELL144
   0/6. No threshold, rule, arm, seed or piece of code that affects results was
   changed after it: no file of impl/ or verifier/ has a modification time
   later than the dry run's manifest, so the official run used the code as it
   stood at the end of the dry run. Its purpose was debugging, and it is not
   part of this run.
8. **C-DET (c).** The same 20 systems as C-DET (b) were recomputed a second
   time with threads = 1 and compared with the threaded run records
   (trial-plan reading R10).
9. **C-VERIFIER kinds** (trial-plan reading R6). A kind is (closure, arm) with
   at least 1 engine refutation under that closure; there are 9 kinds.
   - Type (c) is **vacuous** for M_4|N-CONV and M_4|S3-C20. Neither arm has a
     W_4 flat certificate with max |mu| = 3, because every W_4 refutation there
     is at iteration 0.
   - For M_4|N-CONV17 there is exactly one such certificate
     (N-CONV17:83:unsat). The 3 type-(c) controls are that certificate plus two
     variants of it, each with a cancelling duplicate row pair appended.
   - For W_4 kinds without a max-|mu| = 3 flat certificate, type (c) is a
     wdag with an added degree-4 child used twice with the same v_j (rule (c)
     violated, output still 1).

   The corruptions were chosen by impl/negctl.py's own evaluator, never by
   consulting the verifier. All 102 were rejected, and every source
   certificate verified.
10. **NC-DR-5 population** (trial-plan reading R5). The label is issued on the
    arm's unsatisfiable systems, with sat and "all" reported beside it.
    S3-S62 has only satisfiable systems, so it is reported on "all".
11. **Verifier seeds.** The verifier's seeds are transcribed from the
    specification. It reads no executor-written seed file.
12. **Rejected draws.** A rejected draw would be logged with s = null (reading
    R2). None occurred: no identity, b' = 0 or duplicate rejection in any arm.
    No slot was EXHAUSTED.

## Unexpected observations (preserved; no interpretation)

- N-CONV: all 144 unsatisfiable systems are refuted already by M_4 (verified
  flat-v1 with max |mu| <= 2; W_4 one_first_iteration = 0 on 144/144). At the
  same 82 U62+C20 x_R, S_3 is refuted by M_4 on 20/82 (C20 only) and needs
  W_4 iteration 1 on U62 (62/62). NC-DR-6 is therefore "N-CONV M_4 NOT AT
  STAGE-1 RATE": the rate lies above the interval, since 144/144 has
  CP95 [0.9747, 1] against [0.799, 0.875].
- N-CONV rank M_4 is 2677-2683 and fallen is 982-988. For S3-U62 the values
  are 2659-2673 and 964-978, with P = 1695 in both, as L-TOP requires.
- N-CONV17 has P = 1695 on all 288 systems, the same value as S_3 and N-CONV.
  M_4 refutes 143/144 of its unsat systems, and one (slot 83) is refuted at
  W_4 iteration 1.
- N-CONVL: M_4 refutes 105/144. The other 39 are refuted at W_4 iteration 1.
- Satisfiable controls: codim(W_4) = s on 144/144 for N-CONV, N-CONVL and
  N-CONV17, and on 62/62 for S3-S62. For N-ELL144 the codimension is 886 on
  every satisfiable control, for s from 1 to 6: final_dim is 3162, the
  semi-regular T5 value. So codim > s there, and the C-PS inequality holds.
- The fraction of unsatisfiable draws was about 0.12 in N-CONV, N-CONV17 and
  N-ELL144, and 0.37 in N-CONVL (draw_statistics in cell-summary.json).
- The C-SUPPORT Coordinator reading is true: |S_L| = 317 = 17 * 18 +
  popcount(B).

## Checks run by the executor for the completion gate

- raw-result.json and cell-summary.json agree on MN1-MN3. The check was run in
  phase 7 and its result is in manifest `validity.raw_vs_summary_agree` (all
  true).
- Every required artifact exists. The run package is 7.0 MiB, under 150 MiB,
  so no certificate trimming was needed. Nothing was written outside
  write_scope. The only exceptions are the gf2 native build cache in
  ~/.cache and the scratch directory, both outside the repository.
- The specification is byte-identical to HEAD. No package file changed. No
  hypothesis status was changed, no evidence record was written and no
  knowledge was promoted. Nothing was committed.
