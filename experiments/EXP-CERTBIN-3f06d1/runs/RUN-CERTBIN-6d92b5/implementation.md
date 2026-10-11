# implementation.md: RUN-CERTBIN-6d92b5 (EXP-CERTBIN-3f06d1, TASK-20260924-9f15a2)

Written by the executor after the run. It records provenance, protocol deviations,
interpretations of under-determined procedural details, environment events and
unexpected observations. It interprets no result and declares no hypothesis or
heuristic supported, refuted, replicated in the official sense or closed. Claim
tier: toy. No ECDLP cost claim. sota_delta is zero; oracle A (per attempt) and
parallel Pollard rho dominate. Nothing here concerns any n other than 17, any other
curve or V, any other order or pivot rule, regime B, or any deployed curve.

## Provenance

- Specification `experiments/EXP-CERTBIN-3f06d1/specification.yaml`, sha256
  `78c99f8516e5e80f22d327a35d267d38bad59088329b60f5a001cc5715402564`. This equals the
  TASK-20260924-d3a90c snapshot receipt. It was checked before any work and again after
  the run, and it is unmodified.
- Stage-1 inputs (`curve.json`, `references.json`, `targets-F-S3.jsonl.gz` of
  RUN-CERTBIN-3b7e05) match the TASK-20260923-c2e57b receipt (cprov.json `inputs`). They
  were only read.
- The implementation was copied from `experiments/EXP-CERTBIN-4e92d7/impl/` and
  generalised. `impl/impl-provenance.json` (sha256
  `e99211271ed9995d7299b6a3a6596c9c8981c8779135d4f68aaed435c32e768f`) lists, per file, the
  source sha256, the unified diff and the reason. `gf2n.py`, `curve.py`, `elim.py` and
  `stats.py` are byte-identical to Stage 1. Nothing in EXP-CERTBIN-4e92d7 was edited or
  imported.
- Git HEAD at the first driver invocation was `265ae64ff6199039fcf1e61b60bc106d6ec1c207`.
  The Coordinator committed while this task was running (the dispatch was at ec2155778);
  none of the new commits touch this experiment. The tree was dirty with untracked files
  only: this task's impl/, verifier/, trial plan and run directory, plus the two
  concurrent CERTBIN executors' paths (manifest `code.dirty_paths_at_first_driver_invocation`).
- Ordering (manifest `inputs.order_check`):
  1. C-PROV finished at 05:48:45.771Z.
  2. trial-plan-v1.json (sha256
     `46dde32c377918a17064a7a0bf01375c430575ada6c583e616eba90972093849`) was written at
     05:48:45.850Z.
  3. selftest.json was written at 05:48:57-05:48:59Z.
  4. The first frozen stream (R1 S_curve) was drawn at 05:49:00.352Z.
- numpy 2.4.6 and Python 3.11.15; no scipy, no Sage, no compiled helper
  (environment.json).

## Protocol deviations and interpretations (all fixed before the first draw unless stated)

Seeds, counts, thresholds, references, decision rules and the frozen prediction were
not changed. The trial plan lists every procedural interpretation verbatim (I-1..I-40).
The ones below are load-bearing or depart in form from the letter of the contract.

1. **Inference binding.** The requested policy is `executor-implementation`, which the
   adapter binds to `claude-sonnet-5`. This executor ran on `claude-opus-5-5` because
   Claude Code subagents inherit the session model. The manifest records
   `fallback_used: true` and the reason. The handoff sets `fallback_allowed: true`
   (DEC-20260923-4d7a19 R-1). No model is in the computational loop.
2. **Phase-0 order (I-14).** trial_plan_rule requires the plan to be written after
   C-PROV. The frozen command, however, starts with selftest.py and passes the plan to
   the driver as an input. C-PROV therefore ran first, as a separate invocation of the
   new `impl/cprov.py` that draws no random value. The plan was written next, and then
   the frozen command ran. The driver refuses phase 1 unless both cprov.json and
   selftest.json pass. command.txt lists the exact sequence.
3. **Per-cell C-SELF (I-15).** The per-cell C-SELF items need the cell's curve and V.
   They therefore run in phase 1, right after:
   - the cell's curve, points and V streams (S_curve, S_pts or S_V) are drawn;
   - the x(2E) enumeration and C-TR are computed.

   They run before any reference or target stream of the cell is drawn. The generic
   items and C-FIX run in selftest.py before any frozen stream. SR-2 ("C-SELF failure
   stops the run before any frozen stream is drawn") can therefore hold only for the
   generic items. For the per-cell items it holds for the reference and target streams,
   not for the curve and V streams. The randomness of these items comes from
   PCG64(SeedSequence([S_selftest, c])). Every per-cell item passed.
4. **C-TR, applied literally, fails on every curve. This is reported as data, as the
   specification requires.** The control's statement is "for every x in F_{2^17}: x in
   x(2E) iff Tr(x) = Tr(A)". That iff cannot hold over all field elements:
   - Tr(x) = Tr(A) holds for 65,536 values of x;
   - x(2E) has only (q-1)/2 or (q+1)/2 elements (32,634 / 32,717 / 32,603 here).

   Every violation is a twist abscissa, i.e. an x not in x(E) with Tr(x) = Tr(A):
   32,902 at R1, 32,819 at R2 and 32,933 at R3.

   Two related forms were computed and recorded next to the control, without changing
   it:
   - the restricted form, "for x in x(E): x in x(2E) iff Tr(x) = Tr(A)", has 0
     violations at all three cells;
   - the containment x(2E) ⊆ {Tr(x) = Tr(A)} holds at all three cells.

   Per the specification, a C-TR failure invalidates nothing. The measured hull was
   used, and it has dim W = 16 at every cell for F-S3. **Amendment suggestion for the
   Coordinator:** restate C-TR as the restricted form, or as the containment. Neither
   was applied here.
5. **PS0' shortfall at R3.** No non-degenerate unsatisfiable F-S3 target at R3 has 1 in
   R_4 (0/409). There were therefore 0 of the planned 30 certificates at R3. This is
   recorded as a shortfall, not as a PS0' failure, because no certificate failed. R1 and
   R2 have 30/30 certificates each, and all 60 were verified by the separate verifier
   process, which imports nothing from impl/. At R3, PS0' and PS2 are vacuous at D = 4.
6. **F-AFF-1 reference collision at R1 (Stage-1 design I-6, unchanged).** F-AFF-1
   references come from re-scanning the S_ref stream. At R1, the F-AFF-1 reference U3
   has x_R = 27471, which is also F-S3 test target idx 277. That target's F-AFF-1
   instance is therefore byte-identical to the reference. It matches U3 at every
   granularity (T_ops included) and lies in U3's survival coset:
   - Sigma_H ∩ T = {target 277};
   - C-SURV counts it consistently.

   This single self-match is the whole F-AFF-1 D = 4 T_strict count (1/144). As a
   result, M3 at R1 falls under rule (2) (ratio 0) and not rule (1). RR-7 is "E2
   FALSIFIED" either way, since retention_family(F-S3) = 0 < 0.5. The collision is
   recorded in cell-summary `F-AFF-1_reference_x_collisions_with_F-S3_test_targets`
   (R1: 1, R2: 0, R3: 0).
7. **C-NULLS (I-25).**
   - For F-AFF-1, the band check was applied per matrix (E'^0 and the 17 E'^j, 18
     checks); the pooled count is also reported.
   - For F-NULLF2, the pooled count is over every classified instance (reference-scan
     candidates and targets). There are about 1.7 million support positions per cell,
     too many for exact integer summation within the run. That band was therefore
     computed by log-space summation in 80-digit decimal arithmetic (Stirling series
     with 9 Bernoulli terms), which RC-3 allows at 50 or more digits. Before the run,
     this path was checked against exact integer bands at n = 40,001, 50,000 and 77,777,
     and gave identical integers. Bands for n <= 40,000 use exact integers.
   - All C-NULLS checks passed.
8. **Certificate field.** The run schema accepts `result.certificate.kind` only as
   discrete_log, decomposition, key_recovery or none. The manifest therefore records
   `kind: none`, because no solve or relation is claimed. The PS0' instrument
   certificates are under `result.instrument_certificates_PS0prime`
   (unsatisfiability_certificate, 60/60 verified).
9. **Artifact naming.** "references.json per cell" is written as
   `references-<cell>.json`, in compact JSON.
10. **Manifest bookkeeping errata (the numbers themselves are measured correctly).** The
    manifest is written inside phase 9, so three of its fields are incomplete or
    mislabelled:
    - `package_bytes_excluding_checkpoint_at_phase9` (5,644,495) counts only files
      already in the run directory before the phase-9 artifacts were moved in.
    - `checkpoint_bytes` (30,502,543) includes the phase-9 staging directory.
    - `resources.peak_rss_bytes` (309,800,960) excludes the phase-9 invocation's own
      peak of 473,010,176 bytes, which is recorded in `checkpoint/invocations.jsonl`.

    The final package measured by `du -sb` after phase 9 is 36,201,809 bytes (34.5 MiB,
    checkpoint included), under the 80 MiB bound. command.txt and implementation.md
    were added afterwards.

## Development testing (disclosed)

Before the frozen run, the pipeline was exercised with DEVELOPMENT plans outside the
repository (`make_trial_plan.py --dev`):
- one plan had seed base 880000, 40 targets, 12 planted and 20 REV targets;
- one had seed base 990000, 130 targets, 110 planted and 110 REV targets.

None of these seeds is declared. The R3 curve in development was the archived Stage-1
curve, as in the frozen run, and the V was drawn from a development seed.
- selftest.py (S_selftest, which draws no experimental instance) and cprov.py ran in
  development.
- No frozen cell stream was drawn before the frozen run.

Development outputs were used only to fix plumbing and speed:
- the C-TR record gained the violation breakdown;
- the pooled band gained the large-n path;
- Clopper-Pearson now sums the shorter tail;
- references are written in compact JSON;
- the prior-table reading distinguishes "not evaluable";
- RR lines are labelled with cell, granularity and D;
- h_k was added to the pivot-hazards files;
- the manifest was aligned with the run schema (code.command, certificate.kind none).

**Observation made in development (disclosed, acted on in no way):** with the development
V, R3 also showed no unsatisfiable F-S3 target with 1 in R_4. No parameter, threshold,
count, reference choice or decision rule was changed after any development output.

**Infrastructure incident (development only).** The executor's first development
directory lived in the session scratchpad at `scratchpad/dev1`. It was overwritten by a
concurrent executor that used the same path. The executor's own interrupted phase-9
process in that directory was killed. Later development runs used a task-unique
directory. Nothing in the repository was affected, and nothing of the frozen run touched
the scratchpad.

## Run attempts

There was exactly one attempt, with no infrastructure failure, crash, OOM or
watchdog expiry. The two --resume invocations are the declared route to phases 8 and 9.

| step | wall time | peak RSS |
|---|---|---|
| C-PROV | 9.8 s | |
| selftest | 2.5 s | |
| driver phases 1-6 (pid of the first invocation) | 3,678 s | 310 MB |
| phase 7 (separate process) | 82.8 s | |
| phase 8 | 7.8 s | |
| verifier (separate process) | 1.4 s | |
| phase 9 | 15.8 s | 473 MB |

The memory cap was RLIMIT_AS 4 GiB, and one worker was used. stderr.log is empty. Two
other CERTBIN executors shared the 4-core host.

## Unexpected observations (recorded, not interpreted)

- **R3 (Stage-1 curve, random V).**
  - 0 of 409 unsatisfiable F-S3 targets have 1 in R_4 (CP95 [0, 0.0090]).
  - The same holds for F-RANDX (0/358) and F-S3-REV (0/89).
  - At D = 3, no instance of any family at any cell has 1 in R_3.
  - At R1 and R2, the F-S3 unsat rates are 281/379 = 0.741 and 262/308 = 0.851.
- **R1 (h = 2).** The rate's CP95 interval [0.694, 0.785] lies below the Stage-1
  interval [0.799, 0.875].
- **F-RANDX x(2E) split, one-sided exact Fisher p:**
  - R1: p = 0.00909 (62/78 vs 191/294);
  - R2: p = 0.00894 (63/78 vs 183/276). Both are just under the 0.01 cut.
  - R3: every class is 0, so p = 1.
- **Retention, ranks and hazards.**
  - T_strict unsat retention is 0 against every reference, at every cell and at both D.
  - K_rank is 17 for every reference of every affine-route family, at every cell and
    at both D.
  - K_rank_hull equals dim W everywhere: 16 for the curve hulls (F-S3, F-S3-REV,
    F-AFF-1) and 17 for F-PLANT and F-RANDX.
  - dim Sigma_H is 0 everywhere. No scored target lies in Sigma_H, except the F-AFF-1
    self-match in item 6.
  - C-HZERO holds, and every hull-dependent pivot with S_k >= 100 has h = 0. n_rep is 39
    at R1, 181 at R2 and 8 at R3 (F-S3, D = 4).
- **TS1R (F-S3, D = 4).** m = 20 at R1, 24 at R2 and 22 at R3, with o = 0 at every cell.
  Over those measurements the minimum h is 0.406 and the maximum 0.582.
- **R1 hull.** The R1 F-S3 hull does not contain 0 (Tr(A) = 1, h = 2). The R2 and R3
  hulls do.
- **Modal references.** Each cell's F-S3 modal reference is target idx 1: all 100 T_sets
  in the window are distinct, so the tie-break picks the lowest idx. The R2 modal
  instance is satisfiable, and the R1 and R3 modal instances are unsatisfiable.
- **Shared x_R.** Some F-RANDX targets share an x_R with an F-S3 target, as Stage-1 I-12
  permits: 4 at R1, 10 at R2 and 8 at R3. Only secondary cross-scores are affected.
- **UNDERPOWERED unsat arms (SR-3).**
  - F-S3-REV (94, 58 and 89) and F-PLANT (0 by construction) are flagged.
  - Neither enters a primary rule, although C-REV uses F-S3-REV per instance.
  - The primary F-S3 unsat arms have 308-409 targets.
