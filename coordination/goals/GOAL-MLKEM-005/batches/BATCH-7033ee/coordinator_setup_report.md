# Coordinator setup report — BATCH-7033ee

    goal            GOAL-MLKEM-005
    batch           BATCH-7033ee
    authority       DEC-20260813-28d7b2's single next_action (2 parts), read fresh
                    from ledger/goals/GOAL-MLKEM-005.yaml
    session         Coordinator, coordinator-orchestration-code policy, high effort
    committed?      NOTHING. Every file below is untracked in the working tree.
    executed?       NOTHING. No measurement, probe, or ledger record was run or
                    written as official.

## 0. Freshness re-check, run immediately before this report

```
git fetch origin && git merge origin/main --no-edit
```

Result: `main` had moved (four branches updated, including `origin/main`
itself, `1aa0724b9..c8399ceac`) since the pre-batch check at the start of
this session. The merge was clean (fast-forward-compatible content merge,
no conflicts) and brought in unrelated work: `GOAL-FRODO-002` and its
opening question/decision/evidence records, and `EXP-ECTD-9e4248`'s
amendment v7 artifacts. **`git log --oneline 1aa0724b9..c8399ceac --
ledger/goals/GOAL-MLKEM-005.yaml ledger/decisions/DEC-20260813-28d7b2.yaml
coordination/goals/GOAL-MLKEM-005/` returned empty — none of the newly
merged commits touched `GOAL-MLKEM-005` in any way.**

Re-read `ledger/goals/GOAL-MLKEM-005.yaml` after the merge:
`current_batch_id: BATCH-fbb639` (unchanged), and the file's sha256
(`c7f18fc2d7a256d745f5ee2b3ed0f8eceba6cc7f6b215020614a7d3589f8cdd6`) matches
what this session read at the start. `next_action`'s text (the ONE
two-part action this batch discharges) is unchanged from the version this
batch was drafted against.

A search for concurrent GOAL-MLKEM-005 activity in open PRs
(`gh pr list --state open`) found **exactly one open PR in the whole
repository**, and it is not GOAL-MLKEM-005-related (no "mlkem" match).
**Nothing moved underneath this batch. The goal had not moved again.**

## 1. What next_action actually required (read in full, not paraphrased)

Two parts that must travel together in the same successor pre-registration:

- **(a)** Discharge RT-2's required correction to `R-C-OUT-0`'s coverage
  table: restate `hkz/L9_b15` and `hkz/L11_b20` as genuinely `UNCOVERED`
  (not `COVERED`), and `hkz/L9_b22` / `hkz/L11_b30` with the corrected
  `TRUE` `beta_hi`-based `D_route` source, numerically unchanged at `0.0`.
  No new computation — both values are already in the Red Team's committed
  `probe_coverage_beta_mismatch_output.json`.
- **(b)** As the successor batch's lead measurement: commission a
  genuinely non-code-shared re-implementation of `ROUTE-I` (`ROUTE-I2`) for
  `lam1n`/`hkz` at `L7`/`L9`/`L11`, written without importing or
  transcribing `make_A`/`build_basis`/`hkz_profile` from
  `measure_am4.py`/`measure_relvar.py`/`replicate_l7l8.py` or any
  descendant, and re-run `PREREG-3` 3.3's exact `D_route` comparison
  against the same already-archived `ROUTE-P` values, at the same frozen
  lattices/betas/`N_BASES = 8`. A termination clause frozen in advance
  interprets the result: near-epsilon `D_route` discharges the
  code-sharing qualification for the cells checked; growth toward
  `s_c^fib`'s scale flags the affected `BATCH-fbb639` cell as
  methodologically unsupported.

## 2. New batch ID

**`BATCH-7033ee`** — minted with `python3 tools/allocate_id.py --next
batch`, confirmed with `--check` (well-formed, 0 occurrences across 6,612
identifier-bearing paths).

## 3. Files created (exact paths)

**Pre-registration and task cards (7 tasks):**

```
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/dispatch_queue.json
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-61dab8/prereg.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-61dab8/task_card.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-30cdca/task_card.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-415c21/task_card.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-5d1920/task_card.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-e04ebc/task_card.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/tasks/TASK-20260813-fe3dec/task_card.md
coordination/goals/GOAL-MLKEM-005/batches/BATCH-7033ee/coordinator_setup_report.md   (this file)
```

**Handoff envelopes (`ledger/handoffs/*.yaml`, one per task, per AGENTS.md's
required handoff envelope):**

```
ledger/handoffs/TASK-20260813-61dab8.yaml   (author PREREG-4)
ledger/handoffs/TASK-20260813-30cdca.yaml   (notarize PREREG-4)
ledger/handoffs/TASK-20260813-415c21.yaml   (lead producer: RC-3 + ROUTE-I2)
ledger/handoffs/TASK-20260813-5d1920.yaml   (snapshot the lead's artifacts)
ledger/handoffs/TASK-20260813-e04ebc.yaml   (validator review)
ledger/handoffs/TASK-20260813-28eb06.yaml   (red-team review)
ledger/handoffs/TASK-20260813-fe3dec.yaml   (ledger archive)
```

**Nothing else was written.** `knowledge/INDEX.md` was not touched. No file
under `ledger/evidence/`, `ledger/decisions/`, or `ledger/goals/` was
created or edited — `EV-MLKEM-bae519` and `DEC-20260813-a7826b` are minted,
`--check`'d, and **reserved** (bound into `TASK-20260813-fe3dec`'s
declared deliverables) but no such files exist yet; they are written only
if and when the ledger-archive task actually runs.

## 4. IDs minted and verified (all `--check`'d individually, 0 occurrences each)

| id | role |
|---|---|
| `BATCH-7033ee` | batch |
| `TASK-20260813-61dab8` | author PREREG-4 (coordinator) |
| `TASK-20260813-30cdca` | notarizing snapshot archive (coordinator) |
| `TASK-20260813-415c21` | lead producer (executor) |
| `TASK-20260813-5d1920` | producer snapshot archive (coordinator) |
| `TASK-20260813-e04ebc` | independent validation (validator) |
| `TASK-20260813-28eb06` | red-team review (red-team) |
| `TASK-20260813-fe3dec` | ledger archive (coordinator) |
| `EV-MLKEM-bae519` | reserved evidence record |
| `DEC-20260813-a7826b` | reserved decision record |

## 5. Role and policy reasoning

Checked `orchestration/model-policies.yaml`'s `routing_rules` against this
batch's actual content, not copied from the prior batch:

- **`unrecoverable-result-review` (→ `review-breakthrough`)**: does this
  batch claim a breakthrough, propose closing anything, or contradict
  prior evidence? **No.** It is a mechanical coverage correction plus a
  diagnostic re-measurement of an existing measurement's second route,
  explicitly forbidden from proposing any lane or goal closure (§2.6's
  every branch says so) and explicitly not a restatement of
  `KN-FIND-9b5df0`. Rule does not fire.
- **`critical-result-review` (→ `review-adversarial`)**: is a
  `supported`/`rejected` state transition proposed? **No** — no hypothesis
  status moves in this batch at all. Rule does not fire directly, but
  `review-adversarial` is the correct tier anyway by this goal's own
  established convention (`BATCH-fbb639` used it for exactly this shape of
  batch — one producer, two independent reviews, no closure attempted),
  and every prior review task in this goal on a non-closure, non-breakthrough
  measurement has used `review-adversarial`. Assigned to `TASK-20260813-e04ebc`
  (validator) and `TASK-20260813-28eb06` (red-team), both `independent_session_required: true`.
- **`coordinator-code-path` (→ `coordinator-orchestration-code`)**: every
  coordinator task in this batch (`TASK-20260813-61dab8`, `-30cdca`,
  `-5d1920`, `-fe3dec`) requires repo orchestration (git commits, ledger
  writes, dispatch-queue authoring) — fires, assigned.
- **`executor-runtime` (→ `executor-implementation`)**: `TASK-20260813-415c21`
  is an implementation/experiment-execution task — fires, assigned,
  `independent_session_required: true` (matching this goal's established
  convention for every claim-relevant producer).

`max_concurrent = 2`, matching `BATCH-fbb639`'s own sizing basis (one
producer, two reviews that may run concurrently as independent sessions).

## 6. Validation performed

- `dispatch_queue.json` parses as valid JSON and **passes**
  `tools/research_dispatch.py`'s validator end to end: all ten dispatch
  gates pass (`concurrency_cap_respected`, `all_selected_dependencies_completed`,
  `selected_write_scopes_do_not_overlap`, `archive_tasks_run_in_isolation`,
  `all_artifact_paths_are_exact_and_scoped`, `archive_artifact_coverage_complete`,
  `completed_archive_commits_verified`, `archive_tasks_are_coordinator_owned`,
  `terminal_noncompleted_tasks_do_not_unblock_successors`,
  `claim_relevant_tasks_have_independent_review`). The rendered plan
  correctly identifies `TASK-20260813-30cdca` as the only currently-ready
  task (it depends on `TASK-20260813-61dab8`, which is marked `completed`
  in this queue because this Coordinator session wrote `prereg.md` itself)
  and defers every other task on its stated dependency, exactly matching
  the split-producer notarization pattern's intended shape. Plan
  SHA-256: `14b98dcb5b7255506fd4184181c910d89fb902a0041cde300218c95a181131a5`.
- All 7 `ledger/handoffs/*.yaml` files parse as valid YAML with a top-level
  `handoff:` key and the required fields (`id`, `objective`, `inputs`,
  `constraints`, `deliverables`, `artifact_paths`, `archived_by`,
  `inference`, `budget`, `completion_gate`).
- `python3 tools/validate_ledger.py` run against the full working tree
  (including every new file): **`OK: validated 5840 records, no new
  violations`** (up from 5833 records before this batch's 7 new handoff
  files were added; the pre-existing baseline notes — 1,210 grandfathered
  legacy errors, 1 stale baseline entry — are unrelated to this batch and
  were not touched).
- Confirmed this environment has **no `fpylll`, no `sympy`** installed
  (`ModuleNotFoundError` on direct import), which is why `PREREG-4` §2.2
  and the dispatch queue's declared gap `G-5` explicitly state that a
  from-scratch LLL + local-block enumeration routine is a **sufficient**
  independence path at `d <= 40`, and size the lead producer's budget
  (7200 s / 4 GB) for that possibility rather than assuming an installed
  library will be available.

## 7. What is deliberately NOT here

- No git commit of any kind. `git status --short` shows every new path as
  untracked (`??`).
- No `RC-3` correction was written as an official ledger record — it
  exists only inside the frozen, uncommitted `PREREG-4` text, exactly as
  `PREREG-3`'s own RC-1/RC-2 lived only in `PREREG-3` until a (not yet run)
  ledger archive task publishes it. `TASK-20260813-fe3dec`'s handoff makes
  this an explicit completion-gate item.
- No measurement was run: no basis was built, no reduction was performed,
  no `D_route_independent` value exists anywhere in this repository.
- `knowledge/INDEX.md` was not written, read for regeneration, or staged.

## 8. Next step (not taken by this session)

Dispatch `TASK-20260813-30cdca` (the notarizing snapshot archive) — the
only task the dispatch plan currently reports as ready. No measuring task
may run before it commits and the post-commit verifier accepts that
commit.
