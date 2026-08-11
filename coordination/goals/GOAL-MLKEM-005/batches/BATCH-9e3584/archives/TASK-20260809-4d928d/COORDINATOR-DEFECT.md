# Coordinator defect: the producer snapshot's receipt rides outside its commit, and nine declared artifact names do not exist

Recorded 2026-08-11 by the Coordinator adjudicating BATCH-9e3584.
Adjudication: `../../COORDINATOR-ADJUDICATION-20260811.md`.
Sibling defect: `../TASK-20260809-91cf76/COORDINATOR-DEFECT.md`.

This file records defects in **archive bookkeeping**. It adjudicates no
scientific proposition, admits no producer headline, moves no hypothesis and
promotes nothing. Claim tier stays TOY. In particular `R-OUT-1` — quoted in the
committed receipt as *snapshotted, NOT adjudicated* — is not adjudicated here
either, in any direction.

## 1. What the contract required

`TASK-20260809-4d928d` is a snapshot archive with four producer sources
(`TASK-20260809-cda2f6`, `-311784`, `-97d6cf`, `-3eb72c`). Its binding set
(`tools/research_dispatch.py:564`) is its own receipt **plus the 28 source
artifact paths the dispatch queue declares** — **29 paths** — and the declared
commit must change exactly those (`research_dispatch.py:1073-1089`).

## 2. What was committed instead

Commits as reported by the harness-driving session and as recorded in the
immutable `snapshot-receipt.json` beside this file. I hold no shell and ran no
git command.

- `c034ef38` (parent `1aa7db53`) changed exactly the **28 producer files**, and
  does **not** contain this task's receipt.
- `502d15a0` changed **both** snapshot receipts and `dispatch_queue.json`, and
  contains **no** source artifact.

Three defects, of which the second and third are each independently terminal.

**D1 — incomplete bookkeeping (repairable).** `dispatch_queue.json` still carries
`archive.commit_sha: null`, `parent_sha: null`, `path_sha256: {}` for this task,
although the committed receipt carries all three. This is why the harness reports
`completed archive task TASK-20260809-91cf76 requires archive.commit_sha`
(`research_dispatch.py:572-576`), which fires on the sibling task first and
before git is consulted.

**D2 — the receipt rides outside the commit (terminal).** The receipt's own path
is in the binding set and is not in `c034ef38`. Fill the queue honestly and the
verifier reaches `research_dispatch.py:1086` and reports the receipt as
`missing`. Section 4 shows this cannot be repaired.

**D3 — nine declared artifact names do not exist (terminal, and independent of
D2).** Three of the four producers wrote files under names other than the ones
their own frozen task cards declared, in both `deliverables` and
`artifact_paths`. I verified this by listing the task directories and by reading
the committed receipt's `path_sha256` map in this session:

| task | queue declares | committed, and bound by the receipt |
| --- | --- | --- |
| `-311784` | `measure_bnull.py`, `report_bnull.md`, `results_bnull.json` | `measure_nullfam.py`, `report_nullfam.md`, `results_nullfam.json` |
| `-97d6cf` | `measure_ctau.py`, `report_ctau.md`, `results_ctau.json` | `rescore_c1.py`, `report_c1.md`, `results_c1.json` |
| `-3eb72c` | `measure_cposctl.py`, `report_cposctl.md`, `results_cposctl.json` | `posctl_c2.py`, `report_c2.md`, `results_c2.json` |
| `-cda2f6` | `measure_relvar.py`, `report_relvar.md`, `results_relvar.json` | identical — no deviation |

Nineteen of the 28 declared paths match; **nine are missing and nine committed
files are undeclared.** Consequences, all mechanical:

- Filling the queue's `path_sha256` from the receipt now fails *earlier*, at
  `research_dispatch.py:568-571`, with `path_sha256 contains paths outside its
  commit scope` — because 9 of the receipt's 28 paths are outside the queue's
  declared set.
- Even had the receipt ridden inside `c034ef38`, the change-set test would have
  failed with `missing` 10 and `extra` 9. **The producer snapshot could not have
  verified under any commit arrangement**, and that is a fact about the frozen
  contract, not about the commits.
- The receipt binds the files that exist, under their real names, by sha256, and
  **does not disclose the deviation**. That non-disclosure is a Coordinator
  receipt gap and it is mine to record, not the producers'.

## 3. What is NOT damaged

- **Content.** All 28 producer artifacts match their recorded `sha256` at `HEAD`
  exactly — part of the 30-for-30, zero-mismatch check the harness-driving
  session performed. The reports, scripts, results, manifests and the durable
  `command.txt` / `stdout.log` / `stderr.log` of all four producers are present
  and committed. Nothing about D3 changes a byte or a number; it renames nothing
  and loses nothing, provided every downstream citation uses the **committed**
  names above.
- **Reviewability.** `c034ef38` is a real, reachable, pushed commit containing
  every producer artifact, made before either review was dispatched — neither
  review has run. A reviewer reading `c034ef38` reads immutable bytes that
  cannot move under them. That is the property the snapshot rule exists to
  create, and it holds.
- **The no-early-durability-commit property.** As reported: the producers ran
  with their output directories untracked and the artifacts first appear at
  `c034ef38`, whose parent is the notarizing commit `1aa7db53`. This is a
  measurement of the harness-driving session's, and it is one the Validator's own
  completion gate requires it to redo independently.
- **Immutability.** The committed receipt is untouched and stays untouched. This
  file supersedes by reference (AGENTS.md rule 4).

## 4. Why the obvious repair is refused

**Revert-and-re-add is refused here too, and on grounds independent of the
pre-registration case.** It is superficially more tempting for this archive,
because neither review has run, so a re-add would still precede review. It is
still refused:

- it would delete committed run records from the tree, which the verifier itself
  treats as disqualifying (`_changed_paths` raises on any `D` status,
  `research_dispatch.py:954-957`);
- it would destroy "each producer artifact first appears at the producer
  snapshot", which is an explicit clause of the **Validator's** own completion
  gate — the repair would break the check the repair exists to enable;
- it would contradict the immutable receipt, which declares `c034ef38`;
- and it would misrepresent when the artifacts became durable, which is the same
  category of harm as the pre-registration case, one degree weaker. Accepting it
  because it is cheaper here would be exactly the asymmetry this program keeps
  recording against itself.

**History rewriting** is forbidden (AGENTS.md "Durable research commits"); the
commits are pushed.

**No future commit can satisfy this contract**, for the reasons set out in the
sibling defect record section 4: `artifact_paths` must be non-empty
(`research_dispatch.py:502`), artifact paths are uniquely owned (`:511-517`), so
a successor archive must own a new receipt that rides with sources which are
already committed and cannot be changed again.

**The content-only fallback must not be manufactured.** It is reachable only when
the declared commit does not resolve or is not an ancestor of `HEAD`
(`research_dispatch.py:1029-1034`, `:1045-1048`). Declaring a sha that does not
resolve, in order to reach it, would be a fabricated commit binding under
AGENTS.md core rule 9.

## 5. What supersedes it

Identical instrument to the sibling record: this file,
`../TASK-20260809-91cf76/COORDINATOR-DEFECT.md` and
`../../COORDINATOR-ADJUDICATION-20260811.md`, carried into the record by a new
coordinator producer task `TASK-20260811-dac670` and a new conforming snapshot
archive `TASK-20260811-998fb8` **(PLACEHOLDERS — mint with
`python3 tools/allocate_id.py --next handoff --date 20260811`, then `--check`)**,
whose receipt rides **inside** its commit carrying `commit_sha: null` in the
receipt body, with the real sha written into `dispatch_queue.json` afterwards.

`TASK-20260809-4d928d` is set to `failed` in the dispatch queue. Its `archive`
block is filled **from the committed receipt and from nothing else** (28 hashes,
`commit_sha c034ef38`, `parent_sha 1aa7db53`); note that this filling makes the
queue raise the `path_sha256 contains paths outside its commit scope` error of
D3, which is the true diagnosis and is the point of recording it. The task id is
not reused, remapped or deleted (AGENTS.md rule 15).

**Binding on every downstream record:** the BATCH-9e3584 evidence record, both
review reports and any citation anywhere must use the **committed** filenames in
the D3 table. A citation of `measure_bnull.py`, `report_bnull.md`,
`results_bnull.json`, `measure_ctau.py`, `report_ctau.md`, `results_ctau.json`,
`measure_cposctl.py`, `report_cposctl.md` or `results_cposctl.json` is a dangling
reference to a file that does not exist.

## 6. Secondary observations, recorded because they were checkable

Read by me from the committed receipt. None is the blocking defect and none is
repairable, the receipt being immutable.

- The completion gate required the receipt to "state the exact artifact COUNT"
  and for that count to agree with the binding `path_sha256` map — the precise
  gate written because BATCH-cbe023's receipt said "twelve" against a map of
  eighteen. **The receipt states no artifact count.** The count is **28**,
  arithmetic of mine from the map (7 paths in each of four producer
  directories), and it agrees with the map by construction.
- The gate required the merge base and merge outcome for `origin/main` to be
  recorded. The receipt records `check_merge_hygiene.py --base origin/main PASS`
  and `validate_ledger.py` OK at 5669 records, but **no base commit and no merge
  outcome**, and **no push or PR statement**. I do not assert the merge or push
  did not happen; the receipt does not record them. PR status: **UNKNOWN to me.**
- The receipt's `what_is_NOT_done_and_it_gates_everything_above` block, its
  `independence` block (procedural, never model-level; rule 12 unmet and
  unwaived; the same session authored the pre-registration and ran the
  producers), and its refusal to adjudicate `R-OUT-1` are all correct as written
  and are unaffected by anything above.
