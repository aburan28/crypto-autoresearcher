# Red-team report — TASK-20260809-e805f6

Task: `TASK-20260809-e805f6`  
Goal: `GOAL-SSI-001`  
Batch: `BATCH-dbfee9`  
Role: independent Red Team  
Verdict: **CONCUR_WITH_CAVEAT**

The proposed correction survives the arithmetic and scope attack. It correctly
replaces the old `EV-WESO-001` all-budgets/all-fields statement under the
sealed successor's corrected cost law. The verdict is qualified because the
separate `DEC-20260806-a00a28` sentence claiming a crossover near `49.5` is
not the crossover produced by the sealed successor's optimized output, and
must not be carried forward as though it were. The paper-pair sanity control,
dirty-tree execution provenance, legacy stdout heading, unprobe-verified
runtime provenance, and unmodeled practical overheads also remain caveats.

This report makes no attack, security, exponent, parameter-recommendation,
hypothesis-transition, or goal-completion claim.

## Independence, snapshot, and reviewed scope

This was a separate native Codex review session. I read the prior Validator
report because it is a declared input, but I did not adopt its verdict or use
its arithmetic as a substitute for the checks below. I independently parsed
the sealed raw JSON, inspected the source and manifests, verified SHA-256
bindings, and recomputed the crossover and p=256 rows with a read-only local
arithmetic script. No new inference request was made.

The snapshot archive is reachable from the current `HEAD`:

- snapshot commit: `3e6118c356a2454f20bbeb52defe38387994b8b4`
- parent: `cb300984d0bb0e57e159e313646f5ae1ad60f344`
- changed paths: the declared snapshot receipt and the declared correction
  derivation only
- current `HEAD`: `9a865c6109413fbc01e6a728df5e674dd1ee11db`
- snapshot derivation SHA-256: `46e5304907705528e427c30e71d012fb0acfbef7e9790e34dd8b2b0f956778d9`

The snapshot receipt itself intentionally retains `commit_sha: null`,
`parent_sha: null`, and `verification.status: pending_post_commit`. The
dispatch queue contains the post-commit SHA, parent, exact changed paths, and
path hashes, and Git confirms reachability and the exact two-path snapshot
commit. That is sufficient to bind the content for this review, but the
receipt's own post-commit fields are not independently self-contained. A
Coordinator ledger archive should preserve the queue/Git binding and should
not describe the receipt's null fields as a completed standalone verification.

Reviewed paths:

- `AGENTS.md`
- `agents/red-team.md`
- `docs/task-lifecycle.md`
- `docs/dynamic-subagent-dispatch.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-dbfee9/batch_manifest.json`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-dbfee9/dispatch_queue.json`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-dbfee9/dispatch/plan.json`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-dbfee9/archives/TASK-20260809-44fea0/snapshot-receipt.json`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-dbfee9/tasks/TASK-20260809-b34942/correction_derivation.yaml`
- `ledger/evidence/EV-WESO-001.yaml`
- `ledger/decisions/DEC-20260806-a00a28.yaml`
- `experiments/EXP-WESOVOW-001/cost_model.py` (read only; not executed)
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/manifest.yaml`
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/raw-result.json`
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/command.txt`
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/environment.json`
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/execution_report.yaml`
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/stdout.txt`
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/stderr.txt`
- `experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/runtime-session-receipt.json`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-2e6130/reviews/TASK-20260809-038c84/validation_report.yaml`

The input hashes recorded by the correction derivation match the current
committed bytes: `EV-WESO-001` `e72a0c7e...a1ea9fa7c`, corrected source
`714e6366...f4067444842`, successor raw result
`d65442b6...84bf8130c`, and prior validation report
`104180da...29c4d00`. The full hashes are retained in the derivation and were
also recomputed during this session.

## 1. Anchor and cap attack

The successor raw result states the model in logarithmic coordinates:

```text
log2T_full = log2M - log2P0
T(w)        = T_full * sqrt(M / min(w, M))
```

For `log2p=256`, the sealed optimal row is:

```text
log2M       =  93.27781828665178
log2P0      = -15.453071301354399
log2T_full  = 108.73088958800618
```

Thus the anchor is correct in the log domain:
`log2(T_full) = log2(M) - log2(P0)`. It is not a literal subtraction of
quantities in ordinary units. The phrase `T_full = T_optimal - P0` would be
dimensionally misleading unless `T_optimal` and `P0` are explicitly declared
to mean their `log2` values. The raw result and source use the unambiguous
logarithmic form.

The source implementation at `cost_model.py:273-275` applies
`0.5*max(0, log2M-log2w)`. Therefore:

- at `w=M`, the penalty is exactly zero and `log2T(w)=log2T_full`;
- at `w>M`, the `max` branch remains zero and the model is flat at the
  high-memory endpoint;
- for every declared budget below `M`, the penalty is exactly
  `0.5*(log2M-log2w)`.

The raw p=256 value `log2M=93.2778` is above the largest declared budget 80,
so the six requested p=256 rows are all genuinely in the uncapped middle
regime. This directly addresses the predecessor defect: the old source used
`T_full / sqrt(min(w,M))`, which omitted the `M` numerator and did not return
to `T_full` at `w=M`. The successor source diff restores that normalization
and the cap.

## 2. Crossover attack and five c=0 values

With overhead `c*sqrt(log2p)`, set the corrected log-law equal to the
memoryless Delfs–Galbraith baseline:

```text
log2T_full + 0.5*(log2M-log2w) + c*sqrt(log2p) = log2T_DG
```

Solving gives exactly the successor equation:

```text
log2w_star = log2M
              + 2*(log2T_full + c*sqrt(log2p) - log2T_DG).
```

At `c=0`, my independent recomputation from the raw `optimal` and baseline
fields produced zero residual against every stored result:

| `log2p` | independently recomputed `log2w_star` | stored value | residual |
|---:|---:|---:|---:|
| 256 | 54.739597462664136 | 54.739597462664136 | 0 |
| 384 | 69.236434224511896 | 69.236434224511896 | 0 |
| 512 | 81.643626153106254 | 81.643626153106254 | 0 |
| 576 | 87.269442257701911 | 87.269442257701911 | 0 |
| 768 | 102.557607297430366 | 102.557607297430366 | 0 |

Each is at or below its corresponding `log2M`, so each is feasible under the
declared model. “Feasible” here means feasible in the model's table-entry
coordinate; it does not mean physically buildable or an implemented attack.

## 3. p=256 budget attack at c=0

The baseline is `log2T_DG=128`. Independent read-only arithmetic reproduced
all six successor rows:

| `log2w` | recomputed `log2T(w)` | delta `log2T_DG-log2T(w)` | beats baseline in model? |
|---:|---:|---:|:---:|
| 30 | 140.369798731332082 | -12.369798731332082 | no |
| 40 | 135.369798731332082 | -7.369798731332082 | no |
| 50 | 130.369798731332082 | -2.369798731332082 | no |
| 60 | 125.369798731332068 | +2.630201268667932 | yes |
| 70 | 120.369798731332068 | +7.630201268667932 | yes |
| 80 | 115.369798731332068 | +12.630201268667932 | yes |

The sign change is consistent with the crossover at `54.7396`: the old
all-budgets statement is false even in the most favorable `c=0` scenario,
because the first three budgets lose to the baseline. This is a cost-model
comparison only.

## 4. The prior “near 49.5” statement is separately stale

`DEC-20260806-a00a28:110-114` says that, once correctly anchored, the
crossover is near `log2 w ~ 49.5`. The sealed successor output contradicts
that number if it is intended to describe the successor's optimized model:
the successor gives `54.739597462664136` at p=256.

The source of the discrepancy is identifiable, not mysterious. Applying the
same crossover equation to the paper-pair anchor recorded in the successor,
`log2T=106.5`, `log2M=92.5`, and `log2T_DG=128`, gives:

```text
92.5 + 2*(106.5 - 128) = 49.5.
```

So `49.5` is a paper-pair-anchor approximation. It is not the sealed
successor's optimized crossover, whose inputs are `log2T_full=108.7309` and
`log2M=93.2778`. This is a separate stale statement in the predecessor
decision, not a reason to reject the present EV-WESO correction. The next
Coordinator ledger record should either supersede that sentence explicitly or
label it as the old paper-pair approximation and state the successor value
separately. The `EV-WESO-001` correction alone does not silently repair
`DEC-20260806-a00a28`.

For clarity, the old erroneous source formula is a third, different quantity:
using the successor p=256 `log2T_full` in the old source's no-`M` crossover
formula would give `2*(108.7309-128)=-38.5382`. Neither `-38.5382` nor `49.5`
is the corrected successor crossover. The corrected value is `54.7396`.

## 5. Scope, paper-pair control, and provenance attacks

The declared field scope is exactly `log2p` in
`{256,384,512,576,768}`. The declared budget scope is `log2w` in
`{30,40,50,60,70,80}` table entries. The overhead scenarios are
`c in {0,0.5,1,2}` with overhead measured as `c*sqrt(log2p)` bits. The raw
model declares cost in `F_{p^2}` operations and memory in table entries. The
baseline is the memoryless `p^{1/2}` Delfs–Galbraith model. No broader field,
budget, scheme, or baseline claim is admitted here.

The paper-pair control remains a material limitation. The successor reports
the following optimized-minus-paper deviations in bits, with the joint
0.75-bit tolerance:

| `log2p` | time deviation | memory deviation | complete row within tolerance? |
|---:|---:|---:|:---:|
| 256 | +2.2308895880 | +0.7778182867 | no |
| 384 | +0.3743903182 | -1.1123464118 | no |
| 512 | +1.9038967394 | +0.1358326743 | no |
| 576 | -0.9187897604 | -2.6929782215 | no |
| 768 | -1.4645643022 | -3.5132640982 | no |

Thus zero of five complete rows meets the joint tolerance. This does not
invalidate the narrow algebraic correction of the sealed source output, but it
does prevent describing the output as a successful reproduction of all five
paper pairs. In particular, the p=256 `49.5` value is traceable to the paper
pair, while `54.7396` is traceable to the successor's optimized row; those
anchors must not be conflated.

The successor manifest provides good raw/path identity: it names
`RUN-WESOVOW-201692-001`, records one deterministic invocation with exit code
0, binds the explicit `WESOVOW_RAW_PATH`, and records the source SHA-256. The
following provenance caveats survive:

- the run manifest records `dirty_tree: true` because the corrected source
  and successor artifacts existed at invocation time;
- `stdout.txt` still begins with the legacy literal `RUN-WESOVOW-001`, even
  though the raw result, manifest, command path, and directory identify
  `RUN-WESOVOW-201692-001`;
- `raw-result.json` has no standalone top-level schema field, although its
  structure and identifiers are parseable and internally consistent;
- the snapshot receipt uses the pending/self-reference convention described
  above rather than carrying its own post-commit binding fields.

These are provenance and presentation qualifications, not evidence of a
different numeric result. The old `RUN-WESOVOW-001` bytes remain unchanged in
the declared immutability comparison.

## 6. Hidden overhead and model-assumption attack

The correction is an arithmetic correction conditional on the declared model;
hidden overhead cannot change the algebraic fact that the corrected model's
`c=0` rows have the values above. Hidden overhead can, however, change whether
those modeled crossovers are useful in practice. The main surviving
assumptions are:

1. `c=0` is the most attack-favorable scenario, not a measured default. The
   source also emits c=0.5, 1, and 2, but this review does not calibrate `c`.
2. The overhead is represented only by the chosen
   `2^(c*sqrt(log2p))` factor. Table construction, memory bandwidth, hashing,
   communication, parallel scheduling, distinguished-point management,
   source/relation recovery, target descent, and other end-to-end costs are
   not thereby established.
3. The comparison uses `F_{p^2}` operations and table entries, not equal
   hardware time. The byte conversions in the raw result are accounting
   translations, not a hardware feasibility measurement.
4. `T_full` depends on the finite `B` optimizer grid, the Dickman numerical
   approximation, and the stated smoothness/model assumptions. The raw result
   records the quadrature controls, but this review did not execute the
   source or independently establish a theorem about those assumptions.
5. The five field labels and paper pairs do not imply that a real deployed
   scheme reduces to this exact OneEnd/EndRing cost path. The prior evidence
   itself says the record is conditional and does not cover CSIDH, Pegasis, or
   torsion-based schemes.

Accordingly, these assumptions can invalidate a practical-security or
parameter interpretation, but they do not invalidate the narrow statement
that the sealed successor emits the corrected conditional cost-model values.

## 7. Claim boundary and narrowest supported statement

The strongest supported statement is:

> In the immutable successor package `RUN-WESOVOW-201692-001`, interpreted in
> the declared logarithmic cost model with
> `T(w)=T_full*sqrt(M/min(w,M))`, the old `EV-WESO-001` statement that c=0
> beats Delfs–Galbraith at every tested budget is false as stated. The
> corrected p=256 c=0 crossover is `log2w*=54.739597462664136`, with the
> first three declared budgets below the baseline and the last three above it
> in that model; the other four c=0 crossovers are the four values listed in
> Section 2.

This does not establish an attack, a security margin, an exponent improvement,
a parameter recommendation, a hypothesis transition, or completion of
`GOAL-SSI-001`. It is not a negative result about the mathematical problem;
it is a scoped correction of an interpretation of a deterministic model
output.

## Required follow-up

The Coordinator should create the superseding ledger record without editing
`EV-WESO-001` or `DEC-20260806-a00a28` in place. That record should:

- preserve the corrected successor values and this `CONCUR_WITH_CAVEAT`
  verdict;
- explicitly correct or relabel the separate `49.5` sentence in
  `DEC-20260806-a00a28`;
- retain the C1 paper-pair partial failure and the manifest/provenance caveats;
- preserve the conditional model boundary and make no security, exponent, or
  goal-completion statement.

No new experiment is required for this narrow correction. Any attempt to turn
the modeled crossover into a practical claim requires a separately approved
cost-calibration and end-to-end overhead protocol.

Artifact paths written by this task:

- `coordination/goals/GOAL-SSI-001/batches/BATCH-dbfee9/reviews/TASK-20260809-e805f6/red_team_report.md`
- `coordination/goals/GOAL-SSI-001/batches/BATCH-dbfee9/reviews/TASK-20260809-e805f6/runtime-session-receipt.json`

