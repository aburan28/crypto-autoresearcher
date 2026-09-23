# implementation.md: RUN-CERTBIN-3b7e05 (EXP-CERTBIN-4e92d7, TASK-20260923-6f1ad4)

Written by the executor after the run. It records protocol deviations,
interpretations of under-determined procedural details, environment events and
unexpected observations. It interprets no result. Claim tier: toy. No ECDLP cost
claim is made. sota_delta is zero, and parallel Pollard rho dominates.
certificate.kind is none.

## Provenance

- Specification: `experiments/EXP-CERTBIN-4e92d7/specification.yaml`, sha256
  `ddf540a72dc460abb7fb48488ca0a6b3f38b8f56c49eca457ce52d72d9f169f2`. This equals the
  design-snapshot receipt TASK-20260923-91d4a8 and was verified before any work. It is unmodified.
- Repository HEAD: `4ebf8c0115b0e7fcdac60bf09db27224f4bd865d` (clean before the
  work). The dirty state at run time consisted only of the untracked `impl/` and
  `trial-plan-v1.json` (manifest `code.dirty_paths_at_first_invocation`, and
  the per-file sha256 in `code.impl_sha256`).
- Implementation: written from the specification alone under `impl/` (see
  `impl/README.md`). `src/macaulay_export.py` and `src/ic_first_fall_fast.py`
  were not read or used. The fixed-shape construction is independent of them.
  Nothing under /tmp was read, searched or reused. The top-level session's
  exploratory scratch script and its outputs were not seen.
- trial-plan-v1.json sha256 `b28e3904b7c40b49b4e2937967ea9b21d6c5ad2c9880b8aefa5daa1debd24b7b`,
  written 2026-09-23T16:39:36Z. selftest.json was written 16:39:53Z-16:39:57Z,
  and the first elimination was at 16:40:34Z (manifest `inputs`).

## Protocol deviations

None of the sample counts, seeds, thresholds, decision rules or references
changed. Two items are recorded as deviations of form:

1. **Inference binding.** The handoff requests policy `executor-implementation`
   with `fallback_allowed: false`. The adapter binds it to `claude-sonnet-5`,
   but this executor session ran on `claude-opus-5-5` (Claude Code
   `model: inherit`). The manifest records `fallback_used: true` with this
   reason. The model wrote the code. Every number comes from deterministic code.
2. **Environment setup.** The system python3 had no numpy. Before any run,
   numpy 2.4.6 was installed with `pip install --user numpy` into
   `/root/.local` (outside the repository). No compiled helper exists.

## Interpretations of procedural details

The specification leaves some sampling mechanics unstated. Each resolution
below was fixed before the first draw and is recorded verbatim in
`trial-plan-v1.json` under `interpretations` (I-1 .. I-25). The load-bearing ones:

- I-4: the 1000 test targets are 1000 accepted distinct x_R. Degenerate x_R (in V)
  are kept as the degenerate stratum, not redrawn. That gives 7 in F-S3 and 5 in F-RANDX.
- I-6: F-AFF references come from re-scanning the S_ref stream from its seed,
  classified by each F-AFF draw's own oracle B.
- I-9: F-PLANT is scored against the 5 F-S3 references and the F-S3 modal
  reference, and also against its own modal reference (modal rule "per family").
- I-11: the maximizing reference is the argmax over (U1, U2, U3, modal), with ties
  going to the first. At D = 4 every M1 count is 0, so the tie-break picks U1. All
  per-reference values are reported in decision-rules.json and sizing.json.
  The DR-6 and DR-7 inputs are nearly identical across references (pruned dense
  bytes 1,266,915-1,267,864; saving_set 1.658-1.660; saving_strict 33.6-35.7).
- I-24: DR-2 with a failed consistency clause and no falsifying clause gives
  "between".

## Development testing (disclosed)

Before the frozen run, the implementation was exercised three times with a
DEVELOPMENT plan (`make_trial_plan.py --dev`: seeds 777000.. and 555000..,
none of which is a declared seed; 30 or 130 targets). The output went to
`/home/user/certbin-dev/` (outside the repository), which the driver enforces
for `--dev`. No frozen seed stream was drawn before the frozen run, except that
selftest.py (seed S_selftest, which draws no experimental instance) ran in
development. Development-run outputs were used only to fix plumbing: an
ElimResult slot bug, a YAML alias in the manifest, the prior-table handling
of missing values, exact rather than rounded hazard ratios in the P2 statistics,
and the addition of an explicit `sat` field, the literal-transcription
elimination self-check and the reference self-replay check. No parameter,
threshold, count or reference choice was changed on the basis of any output.
The development directory is left in place for audit and is not part of this run.

## Run attempts

Exactly one attempt. There was no infrastructure failure, crash, resume after
failure or re-run. The --resume invocation is the declared route to phase 8.
Wall times: selftest 3.1 s; driver phases 1-6 3561 s (pid 1910); phase 7
249 s (separate process, pid 3277); phase 8 17 s (pid 3322). Peak RSS was 287 MB
(cap RLIMIT_AS 4 GiB). One worker was used, so the sharding demonstration
was not needed. stderr.log is empty.

## Unexpected observations (recorded, not interpreted)

- The P2 set (F-S3, D = 4, S_k >= 200, r-dependent over all targets) has 26
  (reference, pivot) pairs. 11 of them have h = 0 exactly (U2 pivots 1, 3, 4;
  U3 pivots 1-3, 5-9). A pivot that is nonconstant over all scored targets never
  fails among the survivors of the earlier pivots. Under an independent
  Binomial(S_k, 1/2) null, the tail probability of the observed minimum is
  2.2e-13 (cell-summary M2 `tail_extremes`).
- U1, S1 and S2 have identical early hazard sequences (S_k = 993, 507, 255;
  h = 0.489, 0.497, 0.514), and U2 starts with the same first pivot hazard.
- K_rank = 17 for every reference of every affine-route family at both D.
  K_sampled is 2668-2671 out of rank 2668-2672 (F-S3, D = 4). No target survived
  any full fixed-schedule replay against its own family's references (C-UNIF
  passes). There is one exception in the SECONDARY cross-scoring: F-RANDX target
  786 survives the full replay of the F-S3 modal reference at both D and matches
  it at every granularity. Its x_R (88878) equals that of F-S3 target 1, the F-S3
  modal instance. The specification does not require F-RANDX targets to exclude
  F-S3 x_R, and 7 F-RANDX targets share an x_R with some F-S3 target (F-RANDX
  idx 16, 73, 567, 679, 786, 943, 961). This affects only the F-RANDX-vs-F-S3
  secondary scores (the sat arm against F-S3:modal). No primary metric is affected.
- As designed, the F-AFF reference scans reuse the S_ref x_R sequence, so some
  F-AFF references share x_R with F-S3 references. None of the F-AFF reference
  x_R equals an F-S3 test-target x_R (cell-summary
  `F-AFF_reference_x_collisions_with_F-S3_test_targets`).
- At D = 4, 84% of the F-S3 unsatisfiable arm has 1 in R_4 (324 of 386; 62 not
  reached). No satisfiable instance of any family does, and no F-AFF or F-NULLF2
  instance does at D <= 4. PS2 is not vacuous for F-S3, F-S3-REV or F-RANDX at
  D = 4, and 0 violations were found.
- saving_strict is about 35 at D = 4, which is above the idea's predicted <= 10 (P8).
- The subgroup has q = 32603, so there are about 16.3k distinct x_R values, and 36
  duplicate x_R were rejected in the 1037 S_test draws. The 1000 targets therefore
  sample about 6% of the available x_R values (a scope fact of this one curve).
- The F-S3-REV per-reference traces differ from F-S3 (different T_strict hashes).
  The ranks are equal, as a row permutation requires.
