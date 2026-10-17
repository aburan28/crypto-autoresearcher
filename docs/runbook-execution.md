# Runbook execution: the mechanical tier runs experiments, and nothing it says is trusted

**Implemented 2026-10-16** (owner request: run experiments on Claude Haiku
5.5, check the mathematics periodically with Sonnet 5.5 or Opus, use Lean in
experiments, and prove that the prescribed computation was done with the
prescribed parameters). Code: `tools/runbook.py`. Tests:
`tests/test_runbook.py`. Worked example: `examples/runbooks/toy-ecdlp-bsgs/`.
Template: `templates/runbook.yaml`. This document changes no approval, no
historical run and no scientific status.

## The problem

The mechanical tier (`executor-mechanical`, Haiku 5.5 at `low`) is cheap, and
weak at judgment. Its characteristic failures are filling an underspecified
step with a guess, reporting a number it did not observe, retrying until
something passes, and miscopying values into a report. Until now it was
allowed only judgment-free re-runs, and every experiment went to
`executor-implementation` (Sonnet 5.5).

Two things make the cheap tier safe for real execution:

1. **Remove every choice from execution.** The runbook is written at design
   time by the Coordinator.
2. **Make the record checkable without trusting the executor.** A tool, not
   the model, writes every record, and an independent audit re-establishes it.

## Layers, and what each one establishes

| Layer | Mechanism | Establishes | Does not establish |
| --- | --- | --- | --- |
| 1. Runbook | `experiments/<EXP>/runbook.yaml`: every command, every bound file digest, every validity condition, every failure's meaning. `lint` refuses vague text, unbound files, shell syntax and retries of non-infrastructure failures. Approval names its sha256. | The operator has no choice to make; what runs is exactly what was approved. | That the design is right. |
| 2. Tool-written record | `tools/runbook.py run` writes a hash-chained `journal.jsonl`, digests every output, computes every metric and generates the report. | No model-typed number exists. An edit, deletion, reorder or insertion after the fact is visible to `verify`. | That the bytes came from an honest execution: a writer controlling every byte can rebuild a consistent chain. |
| 3. Validity post-conditions | Per-unit assertions on the declared outputs, plus the plan's independent checker. | Each output belongs to its unit (`{trial_id}`), echoes its prescribed parameters, and carries a verified certificate. Operation counts match the prescribed algorithm where the checker recounts them. | Anything a checker does not recompute. |
| 4. Deterministic audit | `tools/runbook.py audit`: `verify`, every checker re-run, summary recomputed, units replayed from a nonce drawn after publication. | A fabricated output in a replayed unit is caught. Fabrication at rate `f` escapes a `k`-unit sample with probability at most `(1-f)^k`, stated in `audit.json`. | The unsampled units, or a non-replayable step. |
| 5. Reader screen | `audit-runs` dispatches `validator-sweep` (Sonnet 5.5, `audit-sweep`, `high`), or `validator` (Opus 5.5, `review-adversarial`) on a flag. | The runbook implements its specification. The primary metric re-derives from the specification alone. Certificates check with disjoint code. Lean statements say what their claims need. | A review gate: a screen never satisfies `review-adversarial` or `review-breakthrough`. |
| 6. Lean obligations | `lean` steps run `orchestration.formal.cli verify` on a bound target and theorem. The receipt must report `machine_verified`, a clean axiom audit, and the bound digests. | The kernel checked the premise, for example the coverage identity that makes an unsolved BSGS instance a defect. | The empirical claim; semantic fidelity, which stays a review. |
| 7. Execution proofs | `execution_proof` steps verify each unit's zkVM receipt with a verifier pinned by digest, bound to the unit's parameters and raw-result bytes. | With a real guest: that the prescribed program ran on the prescribed inputs and produced these bytes. | Anything yet: the seam is implemented, the guest is open (below). |

Layers 1 to 6 work today. Layer 7 refuses to report anything stronger than
`unavailable` until a real receipt and verifier exist.

## Who does what, on which model

| Actor | Model (anthropic backend) | Does |
| --- | --- | --- |
| `design-experiment` (Coordinator) | Opus 5.5 | Dispatches the director, checks its lint output, approves the runbook sha256 in the `DEC-*`. |
| `experiment-director` | Sonnet 5.5, `high` | Writes the runbook and the task card (`tools/task_card.py`, `docs/model-tiers.md`); assesses the finished session with `check-relay`. |
| `executor-mechanical` | Haiku 5.5, `low` | Runs the eight-command procedure in `.claude/agents/executor-mechanical.md` and relays output verbatim. |
| `tools/runbook.py` | none | Preflight, execution, retries, failure classes, journal, metrics, report, audit. |
| `validator-sweep` | Sonnet 5.5, `high` | The reading half of every audit (`audit-runs`). |
| `validator` | Opus 5.5, `xhigh` | Flagged sessions; sessions an evidence review will cite. |
| `validator-breakthrough` | Fable 5.1, `max` | Unchanged: claimed breaks, closures, contradictions. |

The sweep is Sonnet rather than Haiku because no review tier may think less
than the work it reviews (`tests/test_subagent_policy_tier_variants.py`), and a
model auditing its own tier catches its own blind spots least. The sweep is
not Opus by default because it runs on every session. The deterministic audit
does the counting, so what remains is careful reading, which Sonnet does at a
fraction of the price.

## The runbook

`templates/runbook.yaml` annotates every field, and
`examples/runbooks/toy-ecdlp-bsgs/runbook.yaml` is a complete instance. The
rules that make it executable without judgment:

- **`binds`**: every file whose bytes matter, by sha256. That includes the
  specification, the trial plan, every source, the Lean target and its theorem
  file. Every repository file an argv names must be bound. A runbook never
  binds itself (no hash cycles).
- **`spec_bindings`**: values the runbook restates are checked against the
  specification at JSON pointers, so a copy error is a lint finding.
- **Steps run in order and have exactly four kinds:**
  - `command` (purpose `probe`, `coordination` or `verification`: never
    science);
  - `trials` (the frozen trial plan);
  - `lean`;
  - `execution_proof`.

  Every step has a timeout, operator-facing text that passes the vagueness
  lint, and optional `tell_on_failure` text printed verbatim when it stops.
- **`trials` steps run only through the supervisor.**
  - `engine: supervisor` claims the plan's task (`tools/goal_lanes.py claim
    --publish`), runs `tools/experiment_execution.py run` with the claim's
    owner and epoch, and releases `completed` or `failed`. All of the
    supervisor's admission, resource and receipt checks stay.
  - `engine: local` exists only for `EXAMPLE-*` runbooks, which have no queue
    or claim. Lint refuses it anywhere else, so a runbook is never a second
    launcher.
- **`validity`, never `expect`.** Assertions check that an output is
  admissible: it exists, has the right shape, belongs to its unit, echoes its
  parameters, and carries its certificate. They never predict an outcome; a
  capped search that fails to solve is an observation. The example asserts
  `solved` only because BSGS is complete, and that premise is its Lean
  obligation. At the mechanical tier, every trial must have an assertion tying
  its output to its prescribed parameters.
- **`on_failure`**: the first matching rule (`exit_code`, `timed_out`, or
  `validity: false`) sets the failure class and the action. Only
  `infrastructure_error` and `resource_exhaustion` may retry, at most three
  attempts. Anything else is a result or a defect, never noise.
- **`replay`** names the fields a re-execution must reproduce
  (`mode: fields`), or the whole files (`bytes`), or why the step cannot be
  replayed (`exempt` with a reason, reported as `not_covered`).
- **`metrics`** name a step, file, pointer, unit, `measured|derived` label and
  aggregates. The tool computes them over valid non-control units and lists
  the excluded ones.

## Execution semantics

- **Preflight** (an impediment writes nothing):
  - `lint` passes;
  - for `EXP-*` runbooks, the runbook and every bound file byte-match `HEAD`,
    and a committed `ledger/decisions/*.yaml` with `decision: approve` names
    the experiment in `target_ids` and the runbook in `runbook_sha256`;
  - the required programs and Python version are present.
- **One session per runbook.** `session_id` is fixed when the runbook is
  frozen, so archive coverage can name `runbook-sessions/<id>/` in advance.
  - Rerunning the same command resumes the session. An attempt left open by
    a crash is closed as `step_interrupted`, with its files bound, and never
    reused.
  - A session stopped by `infrastructure_error` or `resource_exhaustion` may
    be reopened by rerunning once the cause is fixed (`session_reopened`).
  - Any other stop is terminal. Running again needs an amended runbook with
    a new session id and a new approval.
- **The session directory** is written only by the tool: `journal.jsonl`,
  `steps/<step>.attempt-<n>.*` logs, `outputs/<step>/attempt-<n>/`, and for
  the local engine `units/<RUN>/` with a receipt binding every file in it.
  Supervisor runs stay in `experiments/<EXP>/runs/<RUN>/`.
- **Three independent facts** go in the summary
  (`docs/execution-proof-chain.md`): execution validity, control validity,
  and inferential validity. The third is always `not_assessed`, because the
  evidence review and the Coordinator decide it.

## The journal

Each line is one entry with `seq`, `type`, `time`, its fields, `prev`, and
`hash = sha256("crypto.autoresearch.runbook.journal/v1\n" ||
canonical_json(entry without hash))`, where canonical JSON has sorted keys, no
whitespace and no NaN. The entry types are `session_started` (runbook digest,
binds, preflight facts, owner), `session_resumed`, `session_reopened`,
`step_started`, `step_finished` (status, class, exit code, every output and
log digest), `step_interrupted`, `unit_recorded` (receipt and artifact
digests, validity results, unit statement), and `session_finished` (status,
failure, summary).

`verify` checks:

- the chain links and hashes;
- that the runbook and every bound file are unchanged;
- every recorded digest against the disk;
- every unit, re-evaluated from scratch against its record;
- complete coverage of the plan's trials;
- that no file is in the session that the journal does not account for;
- that the summary recomputes from the outputs.

`--rerun-checks` also re-runs each unit's checker. The adversarial tests show
each check catching the tampering it exists for.

The **unit statement** is
`sha256("crypto.autoresearch.runbook.unit/v1\n" || canonical({plan_sha256,
trial_id, run_id, argv, check_argv}))`. It identifies one prescribed unit of
work. It excludes the runbook digest, because the plan is frozen first, and a
value derived from an argv cannot appear in that argv.

## The audit and its threat model

The primary threat is a sloppy or confabulating executor; the tool-written
record removes it. The residual threat is an executor that controls every
byte it writes and rebuilds a consistent record: an output, its receipt, the
journal entry that bound it, and every link after it. `verify` cannot see
that by construction, and `test_a_consistent_forgery_passes_verify_and_fails_the_audit_replay`
shows exactly that.

Replay is what catches it. The audit re-executes the bound driver, whose
digest the executor cannot change, and compares the declared fields.

- **Sample selection.**
  `challenge_seed = sha256("crypto.autoresearch.runbook.audit/v1\n" ||
  canonical({journal_tip, nonce}))`. Units are ordered by `sha256(seed:step
  || trial_id)` and the first `k` are taken.
- **Where the nonce comes from.** It is fresh randomness the auditor draws
  after the session is published. A nonce derived from the journal alone could
  be ground: the executor would regenerate journals until the sample avoided
  its fabricated units.
- **What the audit records.** The nonce, the seed, every replay and
  comparison, and the miss probability for fabrication rates of 1% to 50%.
- **Where replays write.** Only under the audit directory. A replay is never
  committed as a run.
- **What replay does not catch.** A driver that is itself wrong replays
  identically. That is what the checker, the blind re-derivation (layer 5) and
  Lean (layer 6) are for. Only an execution proof removes the sampling bound
  altogether.

## Lean in experiments

Formalize the premises an experiment's validity rests on: an identity a
checker relies on, a coverage or completeness argument that turns a miss into
a defect, a cost formula a metric uses. Never formalize the empirical claim
itself. The mechanism:

- **Binding.** Bind a `formal/targets/*.yaml` task and its theorem file in the
  runbook, and add a `lean` step.
- **What the step accepts.** It runs `python3 -m orchestration.formal.cli
  verify` (the existing lane: pinned toolchain, axiom audit, `sorry` scan,
  write-once receipt). It then requires all of: `machine_verified`, a passed
  build and axiom audit, no forbidden construct, the bound theorem name, and
  the bound task and theorem digests.
- **Where Lean runs.** Lean is not installed in cloud containers. A `required:
  true` obligation therefore stops the session there with an
  `infrastructure_error`, and must run on a host prepared with
  `formal/setup.sh`. An optional one records `unavailable`. CI's
  `lean-verification` workflow builds every target, including the example's
  `CryptoResearch.Runbook.BsgsCoverage.coverage`.
- **Semantic review.** A receipt's `semantic_review` stays `pending`. The
  sweep screens statement fidelity, and the formal lane's own review stays
  required before any promotion.

## Execution proofs (STARK receipts)

An `execution_proof` step names:

- the trials it covers and the receipt artifact in each unit;
- the backend (`risc0` or `sp1`) and the pinned guest `image_id`;
- the verifier program and its sha256;
- the verifier arguments, using `{receipt}`, `{out}` and `{image_id}`;
- assertions on the verifier's reported public journal.

The verifier must report `verified: true`, `dev_mode: false`, the pinned
image id, the receipt's own sha256, and a journal that echoes the prescribed
parameters and commits to the unit's exact raw-result bytes
(`equals_artifact_sha256`). That is the "same result commitment survives
every edge" requirement of `docs/execution-proof-chain.md`.

These cases are refused and tested:

- `RISC0_DEV_MODE` is set;
- the verifier is missing or is not the pinned binary;
- the receipt is for another image;
- the journal binds another result.

`unavailable` is never reported as verified. The summary's proof chain stays
`incomplete` while the milestones there are open.

What is open, and why it was not built here:

- **The guest is open.** That means a RISC Zero guest for a bounded prescribed
  walk (milestone 2: `ecc2k-23`), and a verifier CLI that emits the report
  above. In this cloud container the RISC Zero toolchain could not be
  installed: GitHub release downloads are refused by the network proxy, and a
  guest build exceeds the session's disk allowance.
- **The statement side of milestone 1 is partly done.** The runbook digest,
  the frozen-plan digest, the unit statement, the bound inputs and sources,
  and the seeds in the frozen argv are the statement components a guest
  journal must commit to. What remains is freezing the wire schema with Cairn
  and the cross-language conformance vectors.
- **The obstruction stays open.** It is tracked in
  `problems/execution-proof-chain-not-enforced.md`.

## Running the audit periodically

`/loop 6h /audit-runs` in a standing session, or a scheduled task that starts
a fresh session with `/audit-runs` every few hours while runbook sessions are
being produced. `python3 tools/runbook.py pending-audits` lists finished
sessions whose current journal tip has no audit. The deterministic half needs
no model and can run anywhere.

## Limits

- A runbook makes an experiment executed as specified, not correct. Design
  errors are the Coordinator's and the reviewers'.
- The vagueness lint is a word list, so it is a forcing function, not a proof
  of clarity.
- The supervisor engine is tested against fake `goal_lanes.py` and
  `experiment_execution.py` with the real interfaces. The first `EXP-*`
  runbook run on the real supervisor is its integration test.
- `newest_experiments.py` does not yet report whether a runbook exists, so
  the run skill checks for `runbook.yaml` directly. While building this, it
  turned up that 17 of the 18 rows it reports `ready` would be refused by the
  supervisor's archive-coverage check (their queue `artifact_paths` omit the
  supervisor's files):
  [`problems/ready-plans-lack-supervisor-archive-coverage.md`](../problems/ready-plans-lack-supervisor-archive-coverage.md).
  `lint` refuses a supervisor runbook whose queue would be refused, so a
  runbook cannot carry that gap.
- The Haiku and Sonnet bindings are `operator-supplied` until `python3 -m
  orchestration.adapter doctor --backend anthropic --probe` confirms them.
