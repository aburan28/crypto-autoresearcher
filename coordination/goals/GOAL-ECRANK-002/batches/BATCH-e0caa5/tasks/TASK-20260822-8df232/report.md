# TASK-20260822-8df232 — coset structure of the GOAL-ECRANK-001 twist family

**Executor measurement report. Measurements only.** This report contains no
assessment of whether degree 8 is reachable, no hypothesis or goal status
change, and no evidence or decision record. Interpretation is a separate
Coordinator act.

- Goal `GOAL-ECRANK-002` · Batch `BATCH-e0caa5` · claim epoch 2
- Repo commit at execution: `ebd55b73ea0a4454eb105c3797cedceb792257a4`
  (branch `claude/degree-regularity-polynomial-systems-pssesi`)
- Tree state: no tracked file modified; this task's deliverables are new
  untracked files inside its `write_scope`. Nothing was committed.
- Machine-readable results: `coset_structure.json` (strict JSON, no duplicate
  keys; verified with an `object_pairs_hook` duplicate detector)
- Code: `src/coset_structure.py`,
  sha256 `6a08546ce897d1f578c1e26795d2f9fb0866468db9b86dcc7d26de9def3593b1`
- Runs: `runs/RUN-8df232-001…008`, each with `manifest.yaml`, `command.txt`,
  `environment.json`, `stdout.log`, `stderr.log`, `raw-result.json`

## Provenance and inference

| field | value |
| --- | --- |
| requested policy | `executor-implementation` |
| resolved model | `claude-opus-5` |
| reasoning effort | `medium` — the effort bound to the `executor` subagent, derived from `orchestration/model-policies.yaml`. The handoff records `reasoning_effort: null`. **No cap below the requested policy was applied.** Disclosed per DEC-20260903-16bfc2. |
| fallback used | false |
| backend | not Amazon Bedrock |
| model inference inside a run | none; every run is deterministic Python |

## Determinism and seeds

- The measurement contains **no randomness at all**: it is exact integer and
  `Fraction` arithmetic over committed JSON inputs. `measurement_rng: none`.
- The one RNG in the code drives the transport self-test only:
  `SELFTEST_SEED = 20260904` (recorded in the code, in every manifest, and in
  `coset_structure.json`).
- `PYTHONHASHSEED=0` on every run.
- Repeat check: `RUN-8df232-005-all` was re-executed to a scratch path and
  compared field by field with the deliverable — **identical** outside the
  provenance block.

Exact reproduction:

```sh
cd coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/tasks/TASK-20260822-8df232
TASK_RUN_DIR=runs/RUN-8df232-005-all PYTHONHASHSEED=0 \
  python3 src/coset_structure.py all \
    --repo /home/user/crypto-autoresearcher --out coset_structure.json
```

Environment: Python 3.11, Linux x86_64, **Python standard library only**, no
network. Budget observed: 8 runs of 40; total measured wall time across all
runs ~24 s of the 2400 s limit; peak memory well under 1 GB of the 4 GB limit.

## THE INFRASTRUCTURE FACT THAT SHAPES THIS WHOLE REPORT

**PARI is absent from this execution environment.** No `gp` binary, no
`cypari`, no `cypari2`, no Sage; and the task forbids network access, so
nothing could be installed. The committed pipeline
(`experiments/EXP-ECRANK-e1e30e/source/twist_family.py`) obtains every
per-twist rank lower bound and every point from PARI `ellrank`. **No new
descent could be run in this session.**

This is an `infrastructure_error`. It is **not** mathematical evidence of any
kind, in any direction. Everything below is therefore derived either from
committed per-class certificate data (re-verified here by independent
stdlib-only exact arithmetic) or from the committed scan table — and every
quantity that would have required a new descent is named **OPEN AND
UNATTEMPTED**, never estimated and never presented as screened or negative.

## Inputs actually used (all committed, all read-only)

| path | what was taken |
| --- | --- |
| `experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/pool.json` | 497 distinct-*j* base curves with PARI base rank |
| `experiments/EXP-ECRANK-e1e30e/runs/RUN-ECRANK-e1e30e-001/subspace_scan.json` | 502 rows of per-curve k = 3…6 optima |
| `experiments/EXP-ECRANK-e1e30e/certificates/cert_deg8_control.json` | k = 3, 8 classes, per-class points + `r_low` |
| `…/cert_deg16_multiplicity.json` | k = 4, 16 classes |
| `…/cert_deg32_multiplicity.json` | k = 5, 32 classes |
| `…/cert_deg32_eigenspace.json` | k = 5, 32 classes |
| `…/cert_deg64_eigenspace.json` | k = 6, 64 classes |

**Pool actually used**: the committed 497 distinct-*j* curves of PARI rank >= 3
from the small-coefficient enumeration (a1 in {0,1}, a2 in {-1,0,1}, a3 in {0,1},
|a4| <= 20, |a6| <= 50), plus the 5 seed curves prepended by the committed
`scan_pool.py` — 502 rows. Base ranks present over **Q**: 1, 2, 3, 4
(n = 1, 1, 497, 3).

**Support actually used**: `[-1, 2, 3, 5, 7, 11, 13]` — the committed support,
everywhere. No extended support was used anywhere in this report.

---

# OBSERVATIONS

## O0. Arithmetic self-tests (`RUN-8df232-006-selftest`)

The handoff required the XOR coset transport to be got right **and tested**.

- Transport `(u, v) -> (u t^2, v t^3)` sends `E^(D)` to `E^(D t^2)`: verified on
  200 randomised exact instances (`rng_seed = 20260904`) — **all pass**.
- Transport is compatible with the group law: `transport(3P, t) = 3*transport(P, t)`
  checked on the exact rational point `(132, 1188)` of the degree-8 control
  curve for t in {1, 2, 3, 5, -7} — **all pass**.
- Independent F_2 affine-subspace enumerator agrees with the Gaussian binomial
  coefficient and with the expected coset count for (n, k) in {(4,3), (5,3),
  (6,3), (7,3), (5,4), (6,4), (7,4)} — **all pass**, e.g. n = 7, k = 3:
  11811 subspaces, 188976 cosets.

## O1. Independent re-verification of the committed certificates (`RUN-8df232-007-verify-certs`)

Stdlib-only exact arithmetic, sharing no code with the PARI search. Six checks
per certificate: **C1** base short model equals the c4/c6 model of the declared
seed a-invariants twisted by the declared coset representative; **C2** every
point on `E^(d) : v^2 = u^3 + A d^2 u + B d^3`; **C3** every point non-torsion by
Mazur (m*P != O, m = 1…12); **C4** classes pairwise distinct mod squares;
**C5** classes form a coset of a subgroup of dimension k; **C6** declared
transport factor t satisfies `squarefree(d0*d)*t^2 = d0*d`.

| certificate | objective | declared | recomputed sum of min(r_low, #pts) | classes with >=1 point | points verified | timed out | C1–C6 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| deg8_control | sum_mult | 20 | **20** | 8 | 20 | 0 | all pass |
| deg16_multiplicity | sum_mult | 32 | **32** | 15 | 32 | 0 | all pass |
| deg32_multiplicity | sum_mult | 52 | **52** | 30 | 52 | 0 | all pass |
| deg32_eigenspace | n_classes | 32 | 32 | **32** | 32 | 0 | all pass |
| deg64_eigenspace | n_classes | 64 | 68 | **64** | 68 | 0 | all pass |

The deg64 row is not a discrepancy: its declared score is the `n_classes`
objective (64 classes each carrying a point, recomputed 64); its multiplicity
sum happens to be 68 and is reported here because this task needs the
per-class multiplicities.

## O2. The k = 3 regression fixture — target 20

The handoff asked to reproduce the k = 3 optimum of 20 on the committed pool
and support. That target decomposes into three distinguishable levels, and
they did **not** all reach the same status here, so they are reported apart.

| level | what it checks | result |
| --- | --- | --- |
| **A — artifact re-derivation** | max over the committed 502-row `subspace_scan.json` of `k3_mult` | **20 — reproduced.** argmax curve `[0, -1, 1, 8, -50]` |
| **B — certificate recomputation** | sum over the 8 classes of the committed degree-8 coset of min(r_low, #points), with every point independently re-verified on-curve and non-torsion | **20 — reproduced.** All of C1–C6 pass; 20 points verified; 0 timed out |
| **C — search reproduction** | re-run `ellrank` over 502 curves x 128 twists to confirm no coset of the pool beats 20 | **BLOCKED (infrastructure).** OPEN AND UNATTEMPTED |

Cross-check: the argmax curve of level A, `[0, -1, 1, 8, -50]`, is the same
base curve as the degree-8 control certificate of level B. The two levels
agree.

The fixture coset itself, in full (support `[-1,2,3,5,7,11,13]`, coset
representative 1, base rank over **Q** = 3, 0 timeouts):

| class d | 1 | -5 | 21 | -105 | -66 | 330 | -154 | 770 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| certified | 3 | 3 | 2 | 2 | 3 | 3 | 2 | 2 |

total 20 · max single class 3 · other seven classes 17.

**What level A is and is not.** Level A re-derives 20 from a committed
*intermediate artifact*; it is not an independent recomputation of the
underlying descents. Level B independently re-verifies the exhibited points,
but the per-class `r_low` values are still PARI's and are not re-derived here.
Level C — the only level that would confirm 20 is a *maximum* — was not run.

## O3. Extended twist support — **OPEN AND UNATTEMPTED**

Handoff deliverable 2 (support beyond 7 primes; re-run k = 3 and k = 4
optimisation) **was not attempted**, because it requires new `ellrank`
descents for every twist of every pool curve over the enlarged support and
PARI is absent with no network.

- support used: **none** — no extended-support number exists in this report
- k = 3 extended optimum: **not measured**
- k = 4 extended optimum: **not measured**
- classification: `infrastructure_error`
- this is **not** "tried", **not** "screened", **not** a negative observation
- what would unblock it: a session with `cypari` (or `gp`); the profiling pass
  is ~502 curves x 256 twists at a 3 s descent alarm

## O4. Coset decomposition: total vs maximum single class (`RUN-8df232-008-cosets`)

Method: each committed certificate supplies a certified vector on a k-dimensional
coset. Every 3-dimensional affine subspace *inside* that coset is a k = 3 coset
whose decomposition is fully determined by committed per-class data. Enumerating
them gives **12431 k = 3 cosets** with exact (total, max single class) pairs.

`others := total - max_single_class` = contribution of the other seven classes.

### Per source

| certificate (objective) | base rank /**Q** | parent k | k = 3 cosets | total min–max | max class min–max | others min–max | others mean | fit total = a*max + b (R^2) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| deg8_control (sum_mult) | 3 | 3 | 1 | 20–20 | 3–3 | 17–17 | 17.00 | n/a (1 point) |
| deg16_multiplicity (sum_mult) | 0 | 4 | 30 | 12–20 | 3–4 | 9–16 | 12.50 | a = 2.133, b = 8.533 (R^2 = 0.267) |
| deg32_multiplicity (sum_mult) | 3 | 5 | 620 | 8–18 | 1–3 | 6–15 | 10.30 | a = 2.161, b = 7.157 (R^2 = 0.262) |
| deg32_eigenspace (n_classes) | 1 | 5 | 620 | 8–8 | 1–1 | 7–7 | 7.00 | n/a (degenerate) |
| deg64_eigenspace (n_classes) | 3 | 6 | 11160 | 8–12 | 1–3 | 7–9 | 7.03 | a = 1.059, b = 6.941 (R^2 = 0.939) |

### Pooled, split by objective

(The pooled-over-everything figure is dominated 11160/12431 by one eigenspace
certificate, so it is reported in the JSON but should not be read first.)

| pool | cosets | total min–max | others min–max | others mean | others spread | fit |
| --- | --- | --- | --- | --- | --- | --- |
| `sum_mult` certificates | 651 | 8–20 | 6–17 | 10.41 | **11** | a = 2.356, b = 6.693, R^2 = 0.315 |
| `n_classes` certificates | 11780 | 8–12 | 7–9 | 7.03 | 2 | a = 1.059, b = 6.941, R^2 = 0.940 |
| all | 12431 | 8–20 | 6–17 | 7.20 | 11 | a = 1.362, b = 6.655, R^2 = 0.668 |

### The separability question, answered from the data

The question posed in the handoff is whether the k = 3 total is approximately
(max single class rank) + (a constant). The complete joint distribution of
(max single class, total) over the measured cosets, as counts:

| certificate | (max \| total): count |
| --- | --- |
| deg8_control | 3\|20: 1 |
| deg16_multiplicity | 3\|12: 2, 3\|14: 6, 3\|16: 5, 3\|18: 2, 4\|14: 2, 4\|16: 5, 4\|18: 6, 4\|20: 2 |
| deg32_multiplicity | 1\|8: 1, 2\|8: 6, 2\|10: 64, 2\|12: 89, 2\|14: 16, 2\|16: 7, 3\|10: 24, 3\|12: 122, 3\|14: 208, 3\|16: 75, 3\|18: 8 |
| deg32_eigenspace | 1\|8: 620 |
| deg64_eigenspace | 1\|8: 8525, 3\|10: 2480, 3\|12: 155 |

Read directly off that table:

1. **The additive-constant form fails on the multiplicity-objective cosets.**
   Fixing max single class = 3 in `deg32_multiplicity`, the total takes the
   values 10, 12, 14, 16, 18 — `others` spans **7 to 15** at one and the same
   max. In `deg16_multiplicity` at max = 3 the total spans 12–18. Over all 651
   `sum_mult` cosets, `others` spans **6 to 17**, a spread of 11 on a quantity
   whose mean is 10.41.
2. **`others` and the max are not independent either**: conditioned on the max,
   the mean of `others` rises 9.49 -> 10.70 -> 13.07 as max goes 2 -> 3 -> 4
   (n = 182, 453, 15). The linear fit total = 2.356*max + 6.693 has
   **R^2 = 0.315**, i.e. the max single class explains about a third of the
   variance in the total across these cosets.
3. **On the eigenspace-objective cosets the additive form looks much tighter**
   — `others` spans only 7–9, R^2 = 0.940, slope 1.059 — but those certificates
   were built to maximise the *number of classes carrying a point*, so almost
   every class contributes exactly 1 by construction. That regime is not
   informative about the multiplicity regime, and the two are reported apart
   for exactly that reason.

So, as measured: **the k = 3 total is not a function of the maximum single
class rank plus a constant** over the multiplicity-objective cosets available
here. The residual term varies over a range of 11 and is itself correlated
with the max. (This is a statement about these 12431 cosets on these five base
curves; see Limitations.)

## O5. The base rank that 31 at k = 3 would require

Three relations, each stated with what it was fitted to. **Every "required"
figure here is MODELED extrapolation, not a measured value.**

| # | relation | fitted to | fit | R^2 | value required for total 31 |
| --- | --- | --- | --- | --- | --- |
| 1 | k3_mult = a*(base rank over **Q**) + b | all 502 scanned curves | a = 1.750, b = 10.487 | **0.023** | **base rank ~ 11.72** |
| 1b | max observed k3_mult at each base rank = a*r0 + b | 4 points (r0 = 1,2,3,4; n = 1,1,497,3) | a = 2.800, b = 9.000 | 0.784 | **base rank ~ 7.86** |
| 2 | total = a*(max single class) + b | 12431 certificate-derived k = 3 cosets | a = 1.362, b = 6.655 | 0.668 | **max single class ~ 17.87** |
| 2' | total = max + mean(others), mean(others) = 7.203 | same 12431 cosets | additive form | — | **max single class ~ 23.80** |

Underlying observed data for relation 1 (measured, not modeled):

| base rank over **Q** | n curves | min k3_mult | mean k3_mult | max k3_mult |
| --- | --- | --- | --- | --- |
| 1 | 1 | 12 | 12.00 | 12 |
| 2 | 1 | 13 | 13.00 | 13 |
| 3 | 497 | 12 | 15.74 | **20** |
| 4 | 3 | 15 | 17.00 | 19 |

Fit quality, stated plainly: relation 1 has **R^2 = 0.023** — base rank
explains ~2% of the variance in k3_mult across the pool, and 497 of 502 curves
sit at a single value of the predictor. Relation 1b has 4 points, two of which
are single curves, and its two highest points are non-monotone (20 at r0 = 3,
19 at r0 = 4). Relation 2 and 2' disagree with each other by 6 units. **These
fits do not agree on an answer**, and the range they span (base rank ~8 to
~12; max single class ~18 to ~24) is the honest width of what was measured.

One purely arithmetic statement, independent of any fit: a k = 3 coset has 8
classes, so **total = 31 requires mean certified rank 3.875 per class**, and
at least one class of certified rank >= 4. The largest single-class certified
rank observed anywhere in the measured cosets is **4** (15 cosets, all inside
`deg16_multiplicity`); the largest k = 3 total observed anywhere here is
**20**.

---

# LIMITATIONS

Stated separately from the observations above, and each scoped exactly.

1. **No new descent was run.** PARI is absent and the network is closed. Every
   per-class `r_low` used here is PARI's, taken from committed certificates.
   This is an `infrastructure_error` and is not evidence about any
   mathematical proposition.
2. **The fixture was reproduced at levels A and B only.** Level C — that 20 is
   the *maximum* over the pool — was not re-executed. Nothing in this report
   independently confirms maximality.
3. **Extended support was not attempted at all** (see O3). There is no
   extended-support number in this report to be misread as one.
4. **The 12431 cosets are not a sample of the pool.** They are all the k = 3
   sub-cosets of five specific certified cosets on five specific base curves —
   `[0,-1,1,8,-50]`, `[1,-1,1,-1,-40]` (twice, coset reps 5 and 1),
   `[1,-1,1,0,0]`, `[1,0,1,4,21]`. They are conditioned on those curves having
   been *selected* as certificate carriers, i.e. on being good. No statistic in
   O4 is a statement about a uniformly drawn k = 3 coset, and none is a
   statement about the other 497 pool curves.
5. **Two objectives are mixed in the source set** and must not be pooled
   naively: 11780 of the 12431 cosets come from `n_classes` certificates whose
   classes carry one point by construction. O4's per-objective split exists to
   keep them apart; the single "all" row is the one to distrust.
6. **`subspace_scan.json` records only per-curve optima**, not per-class
   certified vectors, so the coset structure of any pool curve without a
   committed certificate is unrecoverable from committed data. **OPEN AND
   UNATTEMPTED.**
7. **Base rank coverage is degenerate**: 497 of 502 curves have base rank 3,
   and ranks 1 and 2 are represented by one curve each. Every extrapolation in
   O5 leaves the fitted range immediately, and all of them are labelled
   MODELED.
8. **Certified counts are `min(r_low, #points)`**, the frozen convention of the
   committed run. A class whose descent timed out contributes 0 and is counted
   separately; there were **0 timeouts** in every certificate used here.
9. **Toy scale.** These are small-conductor curves over multiquadratic fields
   of degree <= 64. Nothing here transfers to cryptographic scale, and no
   number here is offered as a cryptographic-scale claim.
10. **No interpretation.** This report does not say whether degree 8 is
    reachable, does not evaluate any hypothesis, and changes no status.

# Certificate discipline

`certificate.kind: none`, recorded explicitly rather than left absent.

This task **claims no discrete-log solve and no factor-base relation**, and it
asserts **no new rank bound**. What it does is re-verify *pre-existing*
committed rank-lower-bound certificates of EXP-ECRANK-e1e30e (checks C1–C6,
O1), using stdlib-only exact arithmetic that shares no code with the PARI
search that produced them. The taxonomy in `docs/claims-and-verification.md`
has no kind covering a Mordell–Weil rank lower bound, which is why the
committed run recorded `none` too; that choice is followed here rather than
inventing a label.

# Protocol deviations and anomalies (all recorded, none discarded)

1. **`coordination/goals/GOAL-ECRANK-002/batches/BATCH-e0caa5/batch.yaml` does
   not exist.** The dispatch instruction named it as required reading. The
   batch's `dispatch_queue.json` is present and was read instead, together with
   the authoritative handoff `ledger/handoffs/TASK-20260822-8df232.yaml`.
2. **PARI absent** — the governing infrastructure fact, detailed above.
3. **Handoff constraint "REGRESSION FIXTURE FIRST … If you cannot reproduce it,
   STOP."** The fixture *did* reproduce at levels A and B and could not be run
   at level C. Level C is the level the constraint's "STOP" clause is about,
   so no extended-support number was produced — which coincides with the
   infrastructure block. Both reasons are recorded; neither is used to hide the
   other.
4. **`RUN-8df232-004-all` superseded.** The first full run inlined the 12431
   coset rows, producing a 7.1 MB deliverable. `RUN-8df232-005-all` writes the
   rows to `runs/RUN-8df232-005-all/k3_coset_rows.json` (nothing summarised
   away; the complete joint distribution is also in the JSON as
   `contingency_max_by_total`). Because the deliverable path is fixed by the
   handoff, run 004's copy of `coset_structure.json` was overwritten by run
   005. Run 004's directory, command and stdout are retained and its manifest
   records this. **No measured number differs between 004 and 005.**
5. **`RUN-8df232-001/002/003` were executed against an intermediate revision of
   `src/coset_structure.py` whose sha256 was not recorded.** They are retained,
   marked superseded, and re-executed at the final sha as
   `RUN-8df232-006/007/008`.
6. **No partial state from the expired epoch-1 claim was found.** None of the
   three deliverables existed on disk or in git before this session; the task
   directory did not exist and was created here.
7. **Nothing was committed, nothing was written outside `write_scope`, and no
   committed record under `experiments/` or `ledger/` was edited.**
8. **A concurrent session committed this task's in-flight files.** While this
   executor was still working, commit `ba9bd1bcd` — *"wip(GOAL-ECRANK-002/BATCH-e0caa5):
   preserve 8df232 run records IN FLIGHT"*, authored 2026-09-04 19:11:56 UTC —
   staged `coset_structure.json`, `src/` and `runs/` from the worktree. **This
   executor issued no `git add`, `git commit`, `git push` or PR operation of any
   kind**; the commit was made by another actor in this worktree
   (`coordinator-aes-1` holds the epoch-2 claim). Consequences, recorded rather
   than smoothed over:
   - The `repo_commit` recorded in every run manifest is `ebd55b73ea…`, which
     was HEAD when the runs executed. That remains correct; HEAD has since moved
     to `ba9bd1bcd` underneath the work.
   - `ba9bd1bcd` captured an **intermediate** task state: `report.md` did not
     yet exist at that commit, so that snapshot is incomplete as a deliverable
     set. `coset_structure.json` at `ba9bd1bcd` is byte-identical to the final
     worktree file (sha256 `a6eda120b352ce3d720e00a26e566a9eca3349915f11fb1f8f5819d87b61cd85`).
   - The authoritative, complete deliverable set is the worktree state described
     at the top of this report. The Coordinator's snapshot archive should bind
     to that, and should note that `ba9bd1bcd` is a partial in-flight capture,
     not this task's archive.
