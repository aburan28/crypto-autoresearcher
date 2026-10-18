# Item 18 protocol: execute the frozen ECDLP contracts

Frozen before any measured run. Source design: section "18" of
`research/blindspots_20261018/EXPERIMENTS.md` (in the sibling repository
`/home/user/crypto`) and its "Rules every item follows". Written by the
experiment-director lane, 2026-10-18, in `crypto-autoresearcher` under its
`AGENTS.md`: run records are immutable, only the Coordinator changes research
state, and this item changes no hypothesis, decision or experiment status.

Class: **execution-debt census plus replica execution** (`REVIEW-UNADDRESSED-
20260807.md` section 3 names the debt: "18 frozen contracts with zero run
directories" in ECDLP core, at the time). It compares no method against an
incumbent, so the verdict vocabulary applies in the degenerate way stated under
"Verdict". The success criterion (`AGENTS.md`, "Every improvement is a
success") is not engaged: running a frozen contract is not an improvement over
the index-calculus baseline, and nothing here is reported as one. No row is a
cross-method comparison, so the section 5a pricing band does not apply; the
only cost unit is counted contracts and recorded exit codes.

## Question

Which frozen ECDLP contracts have never been run, which of those can run on this
host (shared 4-vCPU, 15 GB container, level L0) within 45 minutes and 4 GB, and
what does each runnable one record when its frozen command is executed exactly
as frozen? For each one that cannot run, what is the first blocking reason and
what would unblock it?

## What already exists, and what is reused or not

Read before designing: `REVIEW-UNADDRESSED-20260807.md` section 3;
`plugins/crypto-autoresearcher-harness/skills/run/SKILL.md` (the `run` skill's
contract); `tools/newest_experiments.py` (`execution_progress`,
`_dispatch_queue_ready`, `withheld_state`, `newest_runnable`);
`tools/experiment_execution.py` (`load_plan`, `authorize`, `execute_trial`);
`tools/ecc_priority.py` and `orchestration/research-priority.yaml` (the ECC
area set); `tools/task_card.py` and `docs/model-tiers.md` (the card contract);
the decisions `DEC-20261005-138b51` and `DEC-20261005-98a823` (withheld
contracts); the failed claim of runbook session `RBS-XEDN-a7cd25`;
`problems/ready-plans-lack-supervisor-archive-coverage.md` (open, 2026-10-17:
the supervisor refuses 17 of 18 contracts the selector calls `ready`, because
their executor handoffs omit the files the supervisor itself writes; PR #2382
tried `EXP-ECDLP-f34097` and `EXP-ECDLP-903c48` and was refused before a trial
directory existed).

* **Cited, not re-measured.** The 2026-08-07 count of 18 is superseded by the
  tree at execution time; the instrument recounts it from `experiments/` and the
  report states the recount, never the old figure.
* **Reused result: none, and that is checked.** Every contract this item runs
  has no `RUN-*` directory on this tree, none on any `origin` branch not on
  `origin/main` (`off_main_runs`), and its run ids appear in no committed run
  record. The instrument re-checks the first two at execution time.
* **Design-time reading (not a measurement).** To size the cards, the director
  read the repository with read-only Python helpers (`newest_experiments.py
  --include-blocked --json`, a directory walk) and the trial plans. Nothing was
  executed from any contract. That reading found: 2742 contract directories;
  2186 with zero `RUN-*` entries; 724 of those with `status: approved` in an ECC
  area; 29 of the 724 with a `trial-plan.json`; 19 of the 29 in the ECDLP class
  below; 13 ECDLP-class contracts with a valid dispatch-queue binding
  (`ready`), 6 with a plan but no usable queue (`needs_dispatch_queue`). Of the
  13 `ready` ones, 9 fail the supervisor's archive-coverage check (their
  queue task lists 2 or 3 artifact paths, the supervisor needs 8 more per run);
  4 pass it (`EXP-ICPERF-e467a5`, `EXP-PFDR-ca5e01`, `EXP-SEMBIN-d9767f`,
  `EXP-XEDN-0c0182`, each with a committed runbook that `tools/runbook.py lint`
  already holds to that rule). Of those 4, `EXP-SEMBIN-d9767f` fails the host
  gates (6144 MB, 36000 s to 50400 s) and `EXP-PFDR-ca5e01` has only one trial
  inside 45 minutes and 4 GB (`selftest`: 2048 MB, 1800 s). The Rust instrument recomputes all of
  this; any difference between this reading and the instrument is reported as a
  difference, never edited away.
* **The supervisor path cannot be taken here.** `tools/experiment_execution.py
  run` needs a live claim published to `origin` (`goal_lanes.py claim
  --publish`). The only attempt on record, `RBS-XEDN-a7cd25` (2026-10-17),
  stopped because the publish returned HTTP 403, and this sandbox cannot push.
  Deviation D1 below states what is run instead.

## Definitions (frozen)

**Zero-run contract.** A directory `experiments/EXP-<AREA>-<tail>/` with no
`RUN-*` entry under `runs/` on disk, none tracked by git under
`experiments/<id>/runs/`, and no commit on an `origin` branch outside
`origin/main` touching `experiments/<id>/runs/`.

**ECDLP class.** Contract area token in this set, every member of which is
also in `ecc_areas` of `orchestration/research-priority.yaml` (the instrument
asserts that): ECDLP, ECDLP2M, OAKLEY, CERTBIN, NISTBIN, CRYPTO, PATH, ENDO,
ECTD, PFDR, ISOU, SATIC, DREG, SDEG, SIG, MONO, RELN, ICEX, ICLIFT, XEDN,
SEMBIN, ICPERF, GRUMPY, LHW, FROB, QSP, GFPN, BINSTD, AUXIN. The other ECC
areas (SSI, SSIQ, P13, CSIDH, SQISIGN, SCURVE, ECQ, ECRANK, ECDSA, EDDSA,
TECDSA, PAIR) are isogeny, curves-over-Q, signature or pairing work, not ECDLP;
they are counted per area in `summary.json` and never run by this item.
**Named by the review.** `EXP-IC-002`, `EXP-TLD-0a6b4d`, `EXP-AOM-e057f7`,
`EXP-PMA-001`, `EXP-JMV-001` are rows regardless of area token (the review's
section 3 names them; the policy's area set does not contain `IC`, `TLD`,
`AOM`, `PMA` or `JMV`). The last two already have run directories and appear as
"has runs" rows, which is the finding about them.

**Frozen contract** (the review's word; the repository marks it two ways).
`specification.yaml` has `status: approved` (or `frozen_awaiting_execution`), a
non-empty `approved_by`, `execution_authorized` not `false`, and no other
contract's `supersedes` names it. Contracts approved before the `frozen: true`
flag existed (for example `EXP-IC-002`) are frozen contracts in this sense; the
flag itself is required by the supervisor's loader and is checked in G6. Everything
else is a pre-approval row (counted by status, listed in `contracts.jsonl`,
never run).

**Approval is read, never granted.** A frozen contract has a committed
approval when a decision under `ledger/decisions/` that is tracked and equal to
`HEAD` has `coordinator_decision.decision: approve` and lists the contract in
`target_ids`. When `approved_by` names a `DEC-*`, that decision must be the one
(this is `tools/task_card.py`'s own `_approval_findings` rule). When
`approved_by` is the word `coordinator`, any such decision counts. A contract
without one is listed `no_committed_approval` and is not runnable. This item
approves nothing.

**Gates, applied in this order; the first failing gate is the reason.**

| gate | reason string | passes when |
| --- | --- | --- |
| G1 | `not_frozen:<why>` | the "Frozen contract" definition holds (`<why>` is `status:<s>`, `no_approved_by`, `execution_not_authorized`, `superseded_by:<id>` or `no_specification`) |
| G2 | `has_runs` / `run_elsewhere:<ref>` | zero-run contract (such a row is a finding, not a candidate) |
| G3 | `no_committed_approval` | a committed approval exists |
| G4 | `withheld:<DEC>` | not held by `withheld_contracts` (rule 9 guard honoured exactly as `withheld_state` does: ascending `(decided_at, id)`, later `released_contracts` restore) |
| G5 | `no_launcher` | `trial-plan.json` exists (a `runbook.yaml` alone is not a launcher: it names the plan) |
| G6 | `plan_invalid:<why>` | the plan is `crypto.autoresearch.trial_plan.v1`, `frozen`, its `specification_sha256` equals the spec, every `source_sha256` file is tracked, equal to `HEAD` and has the recorded digest, trials have unique `RUN-*` ids, `argv`/`check_argv` arrays naming a hash-bound source, `manifest.yaml` and `raw-result.json` artifacts, a positive `memory_mb`, and `depends_on` naming earlier trials |
| G7 | `needs_dispatch_queue:<why>` | the plan's queue exists, is `crypto.autoresearch.dispatch_queue.v1`, lists the plan's `task_id`, and the task's `handoff.execution` equals `{mode: experiments, kind: run, experiment_id, trial_plan, trial_plan_sha256, approved_by}` with the plan's current digest. The `run` skill says to report this as a coordination impediment and continue with `ready` rows, and this item follows it. (The dispatcher's deeper `validate_queue` is not re-implemented; that is a limit, reported as such.) |
| G8 | `handoff_archive_coverage:<n>_files_missing` / `handoff_budget:<why>` | the queue task's `artifact_paths` contain, for every trial, `experiments/<id>/runs/<RUN-ID>/<name>` for the eight supervisor-written names (`launch.json`, `execution-receipt.json`, `command.txt`, `environment.json`, `stdout.log`, `stderr.log`, `check.stdout.log`, `check.stderr.log`) and every artifact the trial declares (this is `authorize()`'s own loop); the task's `handoff.budget` has no zero `maximum_runs`/`experiment_maximum_runs` and its `memory_gb`, when present, covers every trial's `memory_mb`. A contract the supervisor would refuse here is **not run and not bypassed** (`run` skill: "a refused launch is reported, never bypassed") |
| G9 | per trial: `memory:<n>MB>4096MB`, `watchdog:<n>s>2700s`, `time_unbounded`, `tool_missing:<x>`, `module_missing:<x>`, `dependency:<trial>` | `memory_mb <= 4096`; the time bound (the plan's `watchdog_seconds`, else the specification's `budget.wall_clock_seconds_per_run`) exists and is `<= 2700`; `argv[0]`, the programs a `runbook.yaml` lists under `environment.programs`, and every third-party Python module the bound `.py` sources import are available on this host; every `depends_on` trial is itself runnable |

A **contract is runnable** when at least one trial passes G9 (and G1 to G8 hold). A contract with
some runnable and some non-runnable trials is `partial`: the runnable trials
run, the others are listed with their reasons. A **trial is run** by this item
only when its contract reaches G9; nothing else is run. The one admission step of
the supervisor that is not replicated is the live claim (`goal_lanes.py claim
--publish`, dispatcher gates, claim visible in `origin` tracking refs): it needs
a push this sandbox cannot make. That is deviation D1.

## Instrument (native Rust, std only)

`research/blindspots_20261018/18-frozen-contracts/instrument/
blindspots_18_contracts.rs`, built with `rustc` (no crate dependency, so no
`Cargo.toml` is touched and no per-item target directory exists).
`AGENTS.md` "Implementation language: no Python" is met by this program; the
frozen contracts' own Python drivers are the objects being executed, not new
code. Modes:

* `selftest`: parser and classifier controls (below). Exit 0 only if every
  control passes.
* `scan`: walk `experiments/`, apply G1 to G9, write `contracts.jsonl` (one row
  per zero-run contract of the ECDLP class, the named rows and the other-ECC
  rows), `trials.jsonl` (one row per trial of every contract that has a plan),
  `summary.json` (counts by class, status and reason; the anchors; probe
  results) and `table.md`.
* `emit-cards`: from the same classification, write the exact task cards into a
  directory (so the committed cards are reproducible and diffable against a
  live derivation).
* `table`: after execution, join `contracts.jsonl`, `trials.jsonl` and the card
  receipts into the output table: contract, runnable, run id, exit, reason.

## Controls

**Negative controls (instrument, synthetic).** A fixture repository built by
`selftest` holds one contract that passes every gate and one contract per gate
that fails exactly that gate (draft status, not frozen, execution not
authorized, superseded, runs present, no approval, withheld, no launcher, plan
spec-hash mismatch, source-hash mismatch, no queue, queue task without the
supervisor's archive paths, memory 8192 MB, watchdog 5000 s, missing tool,
missing Python module, dependency on a non-runnable trial). Each must be classified with exactly its own reason. A wrong reason is a
failed control and `selftest` exits 1.

**Positive controls (instrument).** The all-gates-pass fixture contract must be
`runnable`; SHA-256 must reproduce the two FIPS 180-2 vectors (`abc` and the
56-byte message) and the digest of a known file; the JSON and YAML readers must
reproduce a fixed fixture to the value; the emitted card for the fixture must
contain its `argv` with `{run_dir}` replaced and no other change.

**Anchors on the live tree (frozen contracts are immutable, so these are stable
facts).** `scan` records, and the report must show, that
`EXP-XEDN-0c0182` is runnable with two trials; `EXP-ECDLP-f34097` is
`handoff_archive_coverage` (the open problem record); `EXP-SEMBIN-d9767f` is
not runnable (its trials fail `memory:6144MB>4096MB` and
`watchdog:36000s>2700s`); `EXP-IC-002` is `no_launcher`; `EXP-ECDLP-daee4d`
is `needs_dispatch_queue`; `EXP-PMA-001` is `has_runs`. An anchor mismatch is a reported finding in
`summary.json` (`anchors_ok: false`), not a hidden one.

**Contract-level controls.** The frozen contracts carry their own: each
`check.py` re-derives the run's fields (`EXP-XEDN-0c0182` states that its
checker uses disjoint code, and its second trial is a determinism replicate of
the first). This item records the checker's exit code and does not interpret
it.

**Replica fidelity control.** Each card's run command is the plan's `argv`
byte for byte except for the declared substitutions (D2, D3); the instrument
asserts that equality when it emits a card and `selftest` checks it on the
fixture.

## Arms, cells, unit

There are no arms. A cell is one contract (classification) or one trial
(execution). The unit is a count and a recorded exit code; wall seconds are
descriptive only. Nothing is priced in GAE (nothing is a method comparison).

## Execution: the cards

Cards use `experiment_id: BLINDSPOT-18` (a research-blindspots id, not an
`EXP-*`, so `tools/task_card.py` does not demand an approval decision for the
card itself; the approval of each contract is read by the instrument, G3).
Every card: `kind: frozen_command`, `background: false`, one thread
(`OMP_NUM_THREADS`, `RAYON_NUM_THREADS`, `OPENBLAS_NUM_THREADS`, `MKL_NUM_THREADS`
all `1`), every run argv wrapped in `prlimit --as=<cap>`, the receipt and every
output under `research/blindspots_20261018/18-frozen-contracts/raw/`, every
repository file an argv names bound by sha256, and a worst-case wall time (the
sum of its command timeouts) under 450 seconds.

* **card-01** builds the instrument, runs `selftest`, runs `scan`, runs
  `emit-cards` into `raw/emitted-cards/` (for a later diff against the committed
  cards), then removes the build.
* **card-02 to card-05** run the trials that the design-time reading found
  runnable, one group per card so each stays under the cap: 02
  `EXP-ICPERF-e467a5` (trial `price-ratio-identity`); 03 `EXP-PFDR-ca5e01`
  (trial `selftest` only: its pilot, census and analysis trials fail G9 with
  watchdogs of 3600 s to 43200 s); 04 `EXP-XEDN-0c0182` trial
  `primary-seed-20261016`; 05 the same contract's trial
  `replicate-seed-20261017`. If `scan` at execution time classifies a trial
  differently, the card still runs what it froze and the table shows both;
  nothing is added or removed after freezing. The nine contracts the selector
  calls `ready` that fail G8 (`EXP-ECDLP-20ac31`, `-3c166b`, `-5f4f14`,
  `-903c48`, `-bfbe6f`, `-f34097`; `EXP-OAKLEY-2c0552`, `-4276c4`, `-7f73ef`)
  have no card, and the table gives each its reason and what would unblock it
  (a superseding queue whose executor task lists every supervisor file).

For each trial the run command writes the run directory
`raw/runs/<RUN-ID>/` (the plan's own `run_id`, so the Coordinator can adopt the
directory under `experiments/<id>/runs/` unchanged), then its `check_argv`
runs against that directory. stdout and stderr land in `stdout.log`,
`stderr.log`, `check.stdout.log`, `check.stderr.log` inside it, exactly the
files the supervisor writes. The run command succeeds on exit 0 with every
artifact the plan declares written; the check command succeeds on exit 0 or 1
(a checker's failure is a recorded result, not a reason to abort the card).

Time caps per command: the plan's `watchdog_seconds` (`ICPERF` 60 s), else the
specification's `wall_clock_seconds_per_run`; where that exceeds the card cap
(`selftest` 1800 s, `XEDN` 900 s) the run command is capped at 220 s and the
check command at 220 s (D4). Address
space: the plan's `memory_mb` in bytes, which is what the supervisor sets with
`RLIMIT_AS`.

## Output

`PROTOCOL.md`, the cards, `raw/` (`scan/{contracts.jsonl,trials.jsonl,
summary.json,table.md}`, `selftest.jsonl`, `emitted-cards/`, `runs/<RUN-ID>/`,
`receipt-card-NN.json`), `README.md`, `table.md` (contract, runnable, run id,
exit, reason), one SVG and PNG graph (a bar of contracts by first blocking
reason, and the run exits), and `REPORT.pdf` (research-visuals skill). These
are produced after the cards run, by the assess stage.

## Verdict

No method is compared, so ADVANCES, TRADES, MATCHES and REGRESSES do not
apply. The README states, per contract, **BLOCKED** (level: none, with the
reason and what would unblock it) or "ran, exit codes as recorded". It states
the item as **INCONCLUSIVE at no level** when any runnable contract produced no
run record, and otherwise as "table complete, no level". It does not state that
any contract's hypothesis is supported or refuted, and it does not state a
scientific conclusion for any run. The Coordinator alone adopts the replica
run directories, files evidence and sets statuses.

## Budget

Measured runs: at most 2 CPU-hours (worst case, the sum of every command
timeout across the five cards: about 1900 s, 0.53 hours; typical far lower, the
`XEDN` censuses loop over primes at most 353), one thread, address space
capped per command (4 GB for the build, the plan's `memory_mb` for trials), at
most two lanes at once on the host. Disk: the instrument binary is built under
`raw/build/` and removed at the end of card-01; no scratch above 200 MB.

## Deviations from the design, every one listed

* **D1. Direct execution instead of the supervisor.** The design says to run
  "through the `run` skill's contract". Its claim-and-publish step cannot
  complete here (HTTP 403 on push, observed for `RBS-XEDN-a7cd25`), and a
  frozen-command card cannot hold a claim. For the contracts that pass every
  static admission gate (G1 to G9), the cards run each trial's frozen `argv`
  and `check_argv` directly. What this drops, stated plainly: the claim and
  release, the dispatcher's live gates, the supervisor's
  `execution-receipt.json`, its non-empty-artifact check and the `manifest.yaml`
  run-schema check. A contract the supervisor would refuse on content (G8) is
  not run at all. What replaces it: the card
  receipt (exit codes, timings, stdout and stderr digests, output digests). The
  run directories are therefore *replica run records under `raw/`*, not
  official records under `experiments/*/runs/`; the Coordinator may adopt them
  (move, then run the supervisor's own validation) or discard them. This
  tightens nothing and loosens one thing (the claim); it is listed here
  because it is the only way the design's run step is possible in this
  environment.
* **D2. Run directory.** `{run_dir}` is substituted by
  `research/blindspots_20261018/18-frozen-contracts/raw/runs/<RUN-ID>` (a
  repository-relative path; the supervisor passes an absolute path under
  `experiments/<id>/runs/`). The card contract requires every output under
  `raw/`.
* **D3. Environment.** `PYTHONHASHSEED=0` (the value each contract's own
  `runbook.yaml` sets where it has one, applied to all for uniformity),
  `PYTHONDONTWRITEBYTECODE=1` (so no `__pycache__` appears beside a frozen
  source), and the one-thread variables. The supervisor passes the caller's
  environment unchanged.
* **D4. Card time cap.** Trials whose frozen watchdog exceeds the card cap
  (`PFDR` `selftest` 1800 s, `XEDN` 900 s each) run with a 220 s cap per command. A
  trial cut by that cap is recorded `timed out` and is host protection, not a
  result about its hypothesis; it is rerun by the Coordinator on a long lane.
  This is a tightening of time that can turn a would-be completion into a
  non-completion, so it is listed.
* **D5. ECDLP class.** The design says "ECDLP contracts"; the policy's ECC area
  set is broader. This item narrows to the ECDLP-class list above (a
  tightening) and reports the other ECC areas by count only.
* **D6. Dispatch-queue gate is partial.** G7 and G8 check the queue's schema,
  task, execution binding, archive coverage and handoff budget but not the
  dispatcher's full `validate_queue`. A
  contract G7 passes could still be refused by the dispatcher; one G7 refuses is
  refused for the stated reason.
* **D7. Check exit 1 allowed.** A checker's exit 1 does not stop the card. A run
  command's non-zero exit does stop it (the supervisor's `infrastructure_error`),
  and the remaining trials of that card are reported as not run.

## What this item does not claim

It does not claim that any contract's hypothesis holds. It does not claim that a
replica run equals an official run (D1). It does not claim that a contract
classified `no_launcher` is wrong or unwanted; the 2026-10-05 holds
(`DEC-20261005-138b51`, `DEC-20261005-98a823`) record a Coordinator ruling that
some frozen contracts produce integer identities with no ECDLP bearing, and the
instrument reports them under `withheld:<DEC>` without disagreeing. It does not
resolve the obstruction "execution debt is mostly unimplemented contracts":
about 96 percent of the approved zero-run ECC contracts have no launcher, and
nine of the thirteen that the selector calls `ready` are refused by the
supervisor's archive-coverage check (`problems/ready-plans-lack-supervisor-
archive-coverage.md`). Both are implementation and queue gaps that running
cannot close.
