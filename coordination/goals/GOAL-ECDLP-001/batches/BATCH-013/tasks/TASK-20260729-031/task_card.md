# TASK-20260729-031 — Freeze the EXP-YIELD-003 fresh-seed replication contract

**Mirror only.** The authoritative card is the `tasks[]` entry with this id in
`coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/dispatch_queue.json`.
Where this file and the queue disagree, **the queue governs and the
disagreement is a defect to be reported**, not resolved by preference.

- **Goal / batch:** GOAL-ECDLP-001 / BATCH-013
- **Role:** coordinator
- **Depends on:** nothing
- **Archived by:** TASK-20260729-032
- **Budget:** 3600 s, 2 GB, `maximum_runs: 1` (schema rejects 0 — this card
  executes nothing)
- **Inference policy requested:** `coordinator-orchestration-code`

## Objective

Convert RC-21A into ONE frozen contract `EXP-YIELD-003` at
`status: review_required` — the fresh-master-seed re-execution of the
EXP-YIELD-002 REPAIRED arm at all 48 declared tuples, carrying the DEV-4
seed-string repair, the RC-21B high-precision extension to six pre-registered
m = 2 tuples, a known-answer integrity arm, **no success criterion**, the
resume condition carried verbatim, and a mandatory platform-and-interpreter
disclosure clause — plus the observation feasibility table.

## Exact artifact paths

- `experiments/EXP-YIELD-003/specification.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/tasks/TASK-20260729-031/observation_feasibility_table.md`

## Exclusive write scope

- `experiments/EXP-YIELD-003/specification.yaml`
- `coordination/goals/GOAL-ECDLP-001/batches/BATCH-013/tasks/TASK-20260729-031`

## Load-bearing constraints (full list in the queue)

- **No success criterion and no falsification criterion on the primary
  quantity.** The mean, sd and SEM of `z_sem` over the 48 tuples are
  **observations feeding no criterion**. Carry the resume condition verbatim
  from `DEC-20260729-002` NA-1 and state that it disposes of an *instrument
  note* and of nothing else. Do not invent a criterion to make the batch look
  decisive.
- **Fresh master seeds 130301 / 130401 / 130501**, declared disjoint from
  EXP-YIELD-002's 120201, 120301, 120401, 120501 and from BATCH-011's
  110200–110799 block, with an invalidation rule that fires on any derived-seed
  collision.
- **Fix DEV-4 with the named fix and no other:** extend the seed string's
  enumerated arm labels to `HIGHPREC-REPAIRED` and `HIGHPREC-ASRECORDED` so the
  two legs stop sharing a stream, and re-derive the block. The fix repairs
  EXP-YIELD-003 only; the immutable EXP-YIELD-002 difference column stays
  unusable and **may never be quoted as a confirmation of T**.
- **Bind RC-21B in:** six m = 2 tuples by a pre-registered deterministic rule
  at 10 000 replicates, in addition to the four m = 3 INV-4-failing tuples,
  legs seeded separately, labelled as feeding nothing.
- **Do not raise the primary arm's replicate schedule** — exactly the amended
  C-14 schedule (100 / 30 / 10). The point is to reproduce *the same statistic*
  under a fresh seed.
- **Platform clause is mandatory:** record `sys.version`, `sys.executable`,
  `platform.platform()`, `platform.machine()`, `platform.processor()` and
  `numpy.__version__` before the first draw; require the Executor to *attempt*
  a genuinely different interpreter build; require it to say **plainly** if a
  different OS or architecture is unavailable; and write into the boundaries
  clause that a same-platform run separates chance from a seed-independent
  deterministic property of the driver-build-platform combination and separates
  none of those three from each other.
- **RT21-1:** do **not** reproduce or paraphrase the C-20 power sentence and do
  **not** create any clause making a sentence mandatory on downstream records.
  Extend `PRED-ID` so it binds the contract's own power, sensitivity, **count**
  and **magnitude** statements — the cardinality-not-identity failure has now
  recurred three times.
- **Defer RT21-3's structurally exact variant explicitly with its cost stated**
  (order 10⁴ replicates per tuple) as DEFER-BATCH013-001. Do **not** add it as
  an arm. Record that EV-ECDLP-008 O-4 component (d) is untouched and
  unarchived and that this contract does not touch it either.
- RC-E, RC-C, RC-D, RC-G and RC-8 bind unchanged; `confirmatory_status:
  exploratory_only`; `hypothesis_id: null`; claim tier **toy**.
- Zero curve arithmetic anywhere; permitted dependencies are the Python
  standard library and numpy.
- **Make no commit.** TASK-20260729-032 commits these artifacts.
- YAML discipline: any scalar with `#`, `|`, `: ` or a leading quote goes in a
  block scalar or quotes; **a mapping key may never sit at the indent of an
  open block sequence's `- ` entries**.

## Prohibitions

No hypothesis created or moved. No efficiency `E`, no yield ratio (including
0.85). INV-4 not un-fired or re-disposed. INV-5 declared neither way. No cost
model touched. No completion criterion claimed. Nothing above toy tier.
