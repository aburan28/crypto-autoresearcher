# RG-0 — Source-state census of the EXP-WESOVOW-001 charging law

Task `TASK-20260904-1f4e2f` · Batch `BATCH-256a94` · Goal `GOAL-SSI-001`
Role: Executor. Requested policy `executor-implementation`
(`reasoning_effort: medium`, `fallback_allowed: false`, `degraded_allowed: false`).

## Citation prohibition (restated verbatim; NOT lifted by this artifact)

> The `P=512` crossover value and its `w=2^80` sign are **NOT
> citation-eligible**. This task does not lift that prohibition. Only a
> committed Coordinator decision on independently reviewed evidence can lift
> it.

## Claim boundary

This artifact reports code reading and record reading only. It makes no
security, standardized-parameter, exponent, or asymptotic-complexity claim in
any direction; changes no hypothesis, experiment, or goal status; writes no
ledger record; and commits nothing. Nothing under `experiments/` was modified,
moved, regenerated, reformatted, rerun, or staged.

## VERDICT

**`fix_already_applied`.**

The van Oorschot–Wiener charging-law source defect localized by `BATCH-eb0a7e`
is not present in the committed implementation this task reads. The corrected,
ratio-anchored law is carried by `experiments/EXP-WESOVOW-001/cost_model.py`
and by `runs/RUN-WESOVOW-201692-001/raw-result.json` at `HEAD`, in the working
tree, and on `origin/main`, all three being the same blob. The frozen
predecessor run `RUN-WESOVOW-001` still serializes the defective law, which is
correct and required: that run record is immutable and must not be repaired.

## Committed-versus-worktree discipline

The census claim is about **committed** state. The distinction was checked
explicitly rather than assumed:

| Check | Command | Result |
| --- | --- | --- |
| Working tree clean under `experiments/` | `git status --porcelain experiments/` | empty output |
| Worktree file identical to `HEAD` | `git diff HEAD -- experiments/EXP-WESOVOW-001/cost_model.py` | empty output |
| Worktree blob hash | `git hash-object experiments/EXP-WESOVOW-001/cost_model.py` | `a7ec7fd1ac4a48e7025fe8e7cfee0e46f6344b47` |
| `HEAD` blob hash | `git rev-parse HEAD:experiments/EXP-WESOVOW-001/cost_model.py` | `a7ec7fd1ac4a48e7025fe8e7cfee0e46f6344b47` |
| `origin/main` blob hash | `git rev-parse origin/main:experiments/EXP-WESOVOW-001/cost_model.py` | `a7ec7fd1ac4a48e7025fe8e7cfee0e46f6344b47` |

All three hashes are equal, so every quotation below is simultaneously a
quotation of the working tree, of `HEAD`, and of `origin/main`. `origin` was
fetched (`git fetch origin main`) before the `origin/main` comparisons.

Session HEAD at census time: `27efe0cdc`
(`Merge remote-tracking branch 'origin/main' into
claude/isogeny-search-prime-fields-5xcc2x`), branch
`claude/isogeny-search-prime-fields-5xcc2x`.

## The five required verbatim law quotations

### 1. `cost_model.py`, serialized formulas block

`experiments/EXP-WESOVOW-001/cost_model.py:239`

```python
                "T_w_vOW": "T(w) = T_full * sqrt(M / min(w, M))",
```

### 2. `cost_model.py`, executable expression

`experiments/EXP-WESOVOW-001/cost_model.py:272-275`

```python
                overhead_bits = c * math.sqrt(b2p)
                log2Tw = (log2Tfull
                          + 0.5 * max(0.0, log2M - lw)
                          + overhead_bits)
```

(The overhead line 272 is included because the law's overhead term is not
otherwise visible; the charging expression proper is lines 273–275.)

### 3. `RUN-WESOVOW-001/raw-result.json` — predecessor run

`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/raw-result.json:13`

```json
      "T_w_vOW": "T_full / sqrt(min(w, M))",
```

### 4. `RUN-WESOVOW-201692-001/raw-result.json` — successor run

`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/raw-result.json:13`

```json
      "T_w_vOW": "T(w) = T_full * sqrt(M / min(w, M))",
```

### 5. `specification.yaml` — controls C3 and C4

`experiments/EXP-WESOVOW-001/specification.yaml:145-149`

```yaml
  - id: C3-monotonicity
    description: T(w) must be non-increasing in memory budget w for every (p, overhead) scenario;
      T(w) must equal T_full for w >= M.
  - id: C4-vow-asymptote
    description: At w = M, vOW time must equal T_full exactly (cap check).
```

The specification states a **normalisation requirement**, not a closed-form
law. It is quoted here because it is the requirement against which the other
four quotations are judged.

## Agreement analysis of the five quotations

* (1) and (2) agree. `T(w) = T_full * sqrt(M / min(w, M))` in log2 is
  `log2T_full + 0.5*(log2M - min(log2w, log2M))`, and
  `log2M - min(log2w, log2M) = max(0, log2M - log2w)` identically. So the
  serialized text and the executable expression of the current implementation
  are the same law.
* (4) is byte-identical in content to (1). The successor run serializes exactly
  the implementation's law.
* (1)/(2)/(4) satisfy (5): at `log2w = log2M` the penalty term is
  `0.5*max(0, 0) = 0`, so `T(M) = T_full` before overhead (C4), and the term is
  non-increasing in `log2w` and flat for `log2w >= log2M` (C3).
* (3) does **not** satisfy (5). Under the predecessor law,
  `T(M) = T_full - 0.5*log2M` in log2, a deficit of `0.5*log2M` bits. Computed
  from `RUN-WESOVOW-001`'s own committed anchors, that deficit is 46.639 bits
  at `log2p = 256`, 68.744 at 384, 90.718 at 512, 101.654 at 576, and 134.343
  at 768 (`anchor_reconciliation.json` →
  `controls.proves_too_much.object_1_...rows`).

This disagreement between (3) and the other four **is** explained by the
committed record set, so RG-0 does not fall to `indeterminate`: it is exactly
the defect recorded in `CORR-20260806-3ac71e`, repaired under the frozen
protocol amendment `TASK-20260809-ef3e58`, and admitted by
`DEC-20260809-c1066f`. The predecessor run is immutable and retains the law it
actually ran under, which is what an immutable run record is supposed to do.

## The `cost_model.py:236` / `:270` question, answered as required

The `BATCH-eb0a7e` Validator report
(`coordination/goals/GOAL-SSI-001/batches/BATCH-eb0a7e/reviews/TASK-20260824-5b150a/validation_report.md:46`
and `:61`) quotes the defective law at `cost_model.py:236` and `cost_model.py:270`.

**Those quotations are not present at those lines in the file this task reads.**
The file now holds, at exactly those two lines:

```
236:                "log2M": "2*log2X + log2(rho(w)), w = log2X/log2B",
270:            entry = {}
```

Stated without asserting a cause, and then localized by direct `git` evidence:

* At commit `8c5188b90` (`Reissue the P13 identifiers and nest the
  EXP-WESOVOW-001 contract`), the immediate predecessor revision of this file,
  line 236 is `"T_w_vOW": "T_full / sqrt(min(w, M))",` and line 270 is
  `log2Tw = log2Tfull - 0.5 * min(lw, log2M) + overhead_bits`. Both are exactly
  the strings the `BATCH-eb0a7e` Validator quotes, at exactly the line numbers
  it cites.
* The `BATCH-eb0a7e` snapshot receipt
  (`.../archives/TASK-20260824-e8f6b7/snapshot_commit_receipt.json`) records
  `parent_sha: bd47a3f5c6915ed7118f74e679c37e2f580fb95d`. At that commit,
  `cost_model.py:236` and `:270` again hold the defective strings verbatim, and
  `git ls-tree bd47a3f5c experiments/EXP-WESOVOW-001/runs/` lists
  `RUN-WESOVOW-001` only — the successor run directory did not exist there.
* `git merge-base --is-ancestor 7d188a7c3 bd47a3f5c` returns non-zero: the fix
  commit was **not** an ancestor of the `BATCH-eb0a7e` producer's base.

So the `BATCH-eb0a7e` producer and Validator read a genuinely pre-fix revision
of the file, and their localization was correct against the state they could
see. This census contradicts neither of them.

## Where the fix lives, and when it became committed

The repair is commit
`7d188a7c38e1d44b46796fe97b34fe4118628216`
(`archive TASK-20260809-981821 EXP-WESOVOW-001 RUN-WESOVOW-201692-001 corrected
run snapshot`, authored 2026-08-08 23:45:42 -0700). Its diff to
`cost_model.py` is +17/−6 and touches exactly four things:

1. `RAW_PATH` gains a `WESOVOW_RAW_PATH` environment override and its default
   moves from `runs/RUN-WESOVOW-001/raw-result.json` to
   `runs/RUN-WESOVOW-201692-001/raw-result.json`;
2. `"run_id"` moves from `"RUN-WESOVOW-001"` to `"RUN-WESOVOW-201692-001"`;
3. the serialized `T_w_vOW` string moves from `"T_full / sqrt(min(w, M))"` to
   `"T(w) = T_full * sqrt(M / min(w, M))"`;
4. the executable expression moves from
   `log2Tfull - 0.5 * min(lw, log2M) + overhead_bits` to
   `log2Tfull + 0.5 * max(0.0, log2M - lw) + overhead_bits`, and the crossover
   from `2.0 * (log2Tfull + overhead_bits - log2TDG)` to
   `log2M + 2.0 * (log2Tfull + overhead_bits - log2TDG)`.

`git merge-base --is-ancestor 7d188a7c3 origin/main` succeeds: the fix is on
`origin/main`.

**One detail of the Coordinator's prior does not survive checking, and is
reported plainly.** The prior (and the batch's `opening_observation`) describes
the repair as "admitted upstream on 2026-08-09" and reaching this branch "only
in the recent merge". The *decision* `DEC-20260809-c1066f` is indeed dated
2026-08-09. The *source*, however, reached the first-parent line of
`origin/main` only at

```
2675886ea | Mon Aug 24 20:50:28 2026 +0000 | Merge pull request #471 from aburan28/codex/ssi-cost-source-20260809
```

(located by binary search over `git rev-list --first-parent origin/main`).
That is **after** the `BATCH-eb0a7e` producer's snapshot base
`bd47a3f5c` (2026-08-24 11:32:12 -0700 = 18:32 UTC) and after the
`origin/main` value that receipt itself recorded,
`e45861af5395dd6bf7fada25dc518f00c2343554` (2026-08-24 16:41 UTC), of which
`7d188a7c3` is verifiably not an ancestor. The intermediate merge
`efd27d78401ab7962d53cdb70f1cd7bd0c464f67`
(`merge: reconcile origin/main with SSI v6 successor`, 2026-08-09) carried the
fix but was itself not reachable from `origin/main` until the 2026-08-24 20:50
UTC merge.

Consequence for the verdict: none — the fix is committed and on `origin/main`
either way. Consequence for the narrative: the `BATCH-eb0a7e` team was not
working from a stale checkout of an already-upstream fix; the fix was not yet
on `origin/main` when they snapshotted, by roughly two hours. This is recorded
as an observation about repository history, not as a fault attributed to any
task.

## Inventory of the two run directories

`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/` — 5 files:
`manifest.yaml`, `raw-result.json`, `execution_report.yaml`, `stdout.txt`,
`stderr.txt`. `manifest.yaml:18` records
`commit_at_run_time: cf82d44f636d056a492ab415bea19270b7b10a7d` and `:19`
`dirty_tree: true`. Serializes the predecessor law (quotation 3).

`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/` — 11 files:
`command.txt`, `environment.json`, `execution_report.yaml`, `manifest.yaml`,
`manifest_v2.yaml`, `raw-result.json`, `runtime-session-receipt.json`,
`stderr.log`, `stderr.txt`, `stdout.log`, `stdout.txt`. `manifest.yaml:23`
records `commit_at_run_time: 6f8b400d8b70d0c0e36663b9365a3869f239d126` and
`:24` `dirty_tree: true`. Nine of the eleven files arrive in `7d188a7c3`;
`manifest_v2.yaml`, `stdout.log` and `stderr.log` arrive later in
`add98ba2a` (`repair lost ledger supersession bindings`). `stdout.log` and
`stdout.txt` are byte-identical (`diff -q` reports no difference).
`execution_report.yaml:27` records `status: valid`; `:45` records
`C1_paper_pair_sanity: status: partial_fail`; C2, C3 and C4 are recorded
`pass`.

Both run directories are byte-clean against `HEAD` (`git status --porcelain
experiments/` is empty).

## Inventory of the governing committed records

| Record | Path | What it says, as read |
| --- | --- | --- |
| `CORR-20260806-3ac71e` | `ledger/corrections/CORR-20260806-3ac71e.yaml` | Records that three committed artifacts stated three different `T(w)`, and settles the shape from the frozen paper. Names `cost_model.py:270` as reading R1 and `specification.yaml:146-149` as reading R2, and identifies the conflict as a naming collision on `T_full`. |
| `TASK-20260809-ef3e58` | `coordination/goals/GOAL-SSI-001/batches/BATCH-2e6130/tasks/TASK-20260809-ef3e58/protocol_amendment.yaml` | The protocol amendment. **It exists and is git-tracked.** `status: prospective_and_frozen`, `version_from: 1`, `version_to: 2`. Freezes `linear_law: 'T(w) = T_full * sqrt(M / min(w, M))'` and `log2_law: log2(T(w)) = log2(T_full) + 0.5*max(0, log2(M) - log2(w)) + overhead_bits`, the crossover `log2(w_star) = log2(M) + 2*(log2(T_full) + overhead_bits - log2(T_DG))`, and `WESOVOW_RAW_PATH`. Lists `specification.yaml` and `runs/RUN-WESOVOW-001/` under `immutable_exclusions`. |
| `DEC-20260809-c1066f` | `ledger/decisions/DEC-20260809-c1066f.yaml` | `decision: accept_with_caveat`. Accepts the corrected source and `RUN-WESOVOW-201692-001` subject to the C1 partial-fail and stdout-heading qualifications. `snapshot_commit: 7d188a7c38e1d44b46796fe97b34fe4118628216`; `protocol_amendment_task: TASK-20260809-ef3e58`. `official_research_state_changed: false`, `hypothesis_status_transition: none`, experiment stays `approved`. **It does admit the repair the census reports, and the amendment it names does exist.** |
| `EV-SSI-4b17e7` | `ledger/evidence/EV-SSI-4b17e7.yaml` | `claim_tier: not_applicable`. The evidence record for that repair. |
| `DEC-20260809-39eb45` | `ledger/decisions/DEC-20260809-39eb45.yaml` | `decision: supersede`, on `BATCH-dbfee9`. Supersedes `EV-WESO-001`'s all-budgets claim. Its `rationale.corrected_interpretation` names the same law `T(w)=T_full*sqrt(M/min(w,M))`. |
| `EV-SSI-e8cc71` | `ledger/evidence/EV-SSI-e8cc71.yaml` | `claim_tier: not_applicable`. Evidence for the interpretation correction. |
| `CORR-20260808-c792f8` | `ledger/corrections/CORR-20260808-c792f8.yaml` | Supersedes the `EV-WESO-001` "beats DG at every tested budget" clause and its `inference` sentence, recomputing from `PAPER_PAIRS` under `T_A = T_full + 0.5*max(0, L_mem - log2w)`. |
| `EV-SSI-12c22e` | `ledger/evidence/EV-SSI-12c22e.yaml` | `type: arithmetic_review`, `direction: neutral`, `strength: inconclusive`. Accepts the `BATCH-eb0a7e` 240-row package. Its `run_ids` names `RUN-WESOVOW-001` only. |
| `DEC-20260824-384e78` | `ledger/decisions/DEC-20260824-384e78.yaml` | `decision: revise`, `decision_scope: record_acceptance_only`. Preserves the anchor ambiguity explicitly: "the fitted_opt and PAPER_PAIRS records give different P=512 crossover behavior and opposite w=2^80,c=0 signs. No anchor is selected for official interpretation." |
| `EV-WESO-001` | `ledger/evidence/EV-WESO-001.yaml` | `claim_tier: theoretical`. The record corrected by `CORR-20260808-c792f8` and superseded in part by `DEC-20260809-39eb45`. |

## What RG-0 does not establish

* It does not establish that the corrected law is the *right* model of the
  van Oorschot–Wiener tradeoff. That is settled, for this program, by
  `CORR-20260806-3ac71e` reading the frozen paper, and this task neither
  re-derives nor re-litigates it.
* It does not establish that either anchor is the one to cite. See
  `anchor_reconciliation.md`.
* It does not rerun anything. `RG-1` and `RG-2` recompute from committed
  literals; no experiment was executed and no timing was measured.

## Explicitly not cited as support

The `opening_observation` block of
`coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/batch.yaml` is treated as
an unverified Coordinator hypothesis. It is not used as evidence anywhere in
this artifact. Every claim above rests on a `git` command whose output is shown
or on a quoted file:line. Where the hypothesis was checkable it was checked;
where it was wrong in detail (the 2026-08-09 upstream-admission timing) that is
reported above rather than adopted.
