# Outstanding fix — under verdict `fix_already_applied`

Task `TASK-20260904-1f4e2f` · Batch `BATCH-256a94` · Goal `GOAL-SSI-001`

## Citation prohibition (restated verbatim; NOT lifted by this artifact)

> The `P=512` crossover value and its `w=2^80` sign are **NOT
> citation-eligible**. This task does not lift that prohibition. Only a
> committed Coordinator decision on independently reviewed evidence can lift
> it.

## Status

**RG-0 returned `fix_already_applied`.** There is therefore **no unapplied
diff in this file and no proposed protocol amendment**: this section exists to
say so explicitly rather than by omission.

**Nothing was applied. Nothing was edited. Nothing was staged. Nothing was
committed.** `git status --porcelain experiments/` was empty at census time and
no file under `experiments/` was touched by this task at any point. Every write
this task made is inside
`coordination/goals/GOAL-SSI-001/batches/BATCH-256a94/tasks/TASK-20260904-1f4e2f/`.

Per the deliverable contract, what follows is the itemized list of **residual
inconsistencies that are NOT source-law defects** and that a later amendment
*might* address. Each carries its evidence. **No action is taken or requested on
any of them by this task**, and none of them is a reason to touch a frozen
artifact.

---

## R1 — `specification.yaml` `required_artifacts` names only the predecessor run

**Evidence.** `experiments/EXP-WESOVOW-001/specification.yaml:160-167` lists

```yaml
  required_artifacts:
  - specification.yaml
  - cost_model.py
  - runs/RUN-WESOVOW-001/manifest.yaml
  - runs/RUN-WESOVOW-001/raw-result.json
  - runs/RUN-WESOVOW-001/execution_report.yaml
  - runs/RUN-WESOVOW-001/stdout.txt
  - runs/RUN-WESOVOW-001/stderr.txt
```

`RUN-WESOVOW-201692-001` is not listed, although `DEC-20260809-c1066f` accepted
it and `cost_model.py`'s default output path now writes into it.

**Why this is not a defect to fix here.** The specification is a frozen
contract, changeable only by a recorded protocol amendment
(`AGENTS.md`; task-card constraint 1). Amendment `TASK-20260809-ef3e58` lists
`experiments/EXP-WESOVOW-001/specification.yaml` under `immutable_exclusions`
and states it "does not revise the original specification". Leaving the list
pointing at the run the version-1 contract governed is consistent, not
erroneous. Recorded only so a later reader does not mistake the omission for an
oversight.

---

## R2 — `cost_model.py` defaults now name the successor run

**Evidence.** `experiments/EXP-WESOVOW-001/cost_model.py:82-86`:

```python
RAW_PATH = os.environ.get(
    "WESOVOW_RAW_PATH",
    os.path.join(os.path.dirname(os.path.abspath(__file__)),
                 "runs", "RUN-WESOVOW-201692-001", "raw-result.json"),
)
```

and `cost_model.py:229`: `"run_id": "RUN-WESOVOW-201692-001",`.

**Consequence, stated without asserting it is an error.** A future invocation of
`cost_model.py` with no `WESOVOW_RAW_PATH` set would write into the
`RUN-WESOVOW-201692-001` directory, overwriting a committed run artifact — the
same hazard the amendment identified for `RUN-WESOVOW-001`
(`protocol_amendment.yaml`, `defect.prior_behavior`: "hard-coded the old run's
raw-result.json path, which could overwrite an immutable receipt"). The
amendment's remedy was the environment override, which was applied; the default
was moved rather than removed. Any future successor run must set
`WESOVOW_RAW_PATH` explicitly. **This task did not execute `cost_model.py` and
did not import it.**

---

## R3 — the successor run's stdout retains the predecessor heading

**Evidence.** `cost_model.py:328` prints a hard-coded heading, and
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-201692-001/stdout.txt` line 1
reads

```
EXP-WESOVOW-001 / RUN-WESOVOW-001 — cost model observations
```

while the same run's `raw-result.json:3` reads
`"run_id": "RUN-WESOVOW-201692-001"`.

**Already recorded upstream.** `DEC-20260809-c1066f`
(`rationale.caveats`) names this exactly: "successor stdout retains the legacy
run heading … preserved as limitations; neither is relabeled or repaired by
overwriting an immutable artifact." `DEC-20260809-39eb45` repeats it. Nothing
is added here beyond confirming the string is still what those decisions say it
is.

---

## R4 — C1 remains a partial failure, by design

**Evidence.** `runs/RUN-WESOVOW-201692-001/execution_report.yaml:44-45`:
`C1_paper_pair_sanity: status: partial_fail`, against
`specification.yaml:139` (`tolerance: abs deviation <= 0.75 bit on both time
and memory`). The per-field deviations are tabulated in
`anchor_reconciliation.md`.

**Why this is not a defect.** `specification.yaml:140-141` prescribes exactly
this handling: "record deviation honestly in execution_report; run stays valid
(this is a model-reproduction check, not an implementation check)". C1 is the
`fitted_opt` / `PAPER_PAIRS` divergence measured under its own name. Tuning the
model to close it is forbidden by `specification.yaml:157`.

---

## R5 — `RUN-WESOVOW-001` still serializes the pre-fix law, and must

**Evidence.** `runs/RUN-WESOVOW-001/raw-result.json:13`:
`"T_w_vOW": "T_full / sqrt(min(w, M))"`.

**Why this must not be changed.** Run records are immutable. That run executed
under that law; a record that serialized a law it did not run under would be a
falsified receipt. `protocol_amendment.yaml` lists
`experiments/EXP-WESOVOW-001/runs/RUN-WESOVOW-001/` under
`immutable_exclusions`. Listed here only because it is the one place the
defective law legitimately survives, and a future census will find it again.

---

## R6 — three files in the successor run directory postdate its archive commit

**Evidence.** `git log --oneline -- runs/RUN-WESOVOW-201692-001` returns two
commits: `7d188a7c3` (nine files) and `add98ba2a`
(`repair lost ledger supersession bindings`), which added
`manifest_v2.yaml`, `stdout.log` and `stderr.log`. `stdout.log` and
`stdout.txt` are byte-identical (`diff -q` reports no difference).

Recorded as an observation about the run directory's composition. This task did
not investigate `add98ba2a`'s scope and asserts nothing about whether the
addition was appropriate.

---

## R7 — a timing detail in the `BATCH-256a94` opening hypothesis is not
supported by `git`

**Evidence.** The batch's `opening_observation.leading_hypothesis` and the
handoff's `coordinator_prior` both describe the repair as "admitted upstream on
2026-08-09". The *decision* is dated 2026-08-09; the *source* reached the
first-parent line of `origin/main` at
`2675886ea` (`Merge pull request #471 from aburan28/codex/ssi-cost-source-20260809`,
2026-08-24 20:50:28 UTC). `git merge-base --is-ancestor 7d188a7c3
e45861af5395dd6bf7fada25dc518f00c2343554` returns non-zero, i.e. the fix was
not on the `origin/main` value the `BATCH-eb0a7e` snapshot receipt recorded on
2026-08-24 16:41 UTC. Full derivation in `source_state_census.md`.

**Consequence.** None for the RG-0 verdict. It refines the history: the
`BATCH-eb0a7e` producer was not working from a stale checkout of an already
upstream fix — the fix reached `origin/main` roughly two hours after that
batch's snapshot base. Recorded so no later reader repeats the 2026-08-09
upstream date. No fault is attributed to any task.

---

## R8 — the task card and the dispatching instruction conflict on the
`P=512` cell

**Evidence and handling.** Recorded in full in `anchor_reconciliation.md`
under "Protocol deviation, recorded not discarded". The task card asks for the
cell in prose; the dispatching instruction forbids restating the value or the
sign. The stricter instruction was followed in prose, the numeric rows are
retained and flagged in `anchor_reconciliation.json`, and both are addressable
by locator. Raised here so the Coordinator can resolve the conflict for future
tasks rather than have each Executor resolve it silently.

---

## What would change this file's status

If a future census finds the serialized law at `cost_model.py:239` or the
executable expression at `:273-275` differing from
`log2T_full + 0.5*max(0, log2M - log2w) + overhead_bits`, or finds the
successor run's `raw-result.json:13` no longer matching them, RG-0 would return
`fix_outstanding` and this file would carry an unapplied unified diff plus the
protocol-amendment fields a Coordinator would have to record. It does not, and
it does not.
