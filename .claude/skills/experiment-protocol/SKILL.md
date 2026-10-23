---
name: experiment-protocol
description: >-
  Design, preregister and freeze an unbiased controlled experiment as an
  experiment.protocol/v1 record before any data is taken, in any of the owner's
  repositories: classify every claim, build reference, baseline, candidate, A/A,
  positive and negative control arms, write the variable ledger that isolates
  every confounder, fix randomization, seeds, blinding, sample size and power,
  precise counted metrics, the isolation level a clock needs, the queue and
  checkpoint policy, stopping and decision rules and a frozen analysis; then
  bind the run's unified experiment.export/v1 to it. Use whenever an experiment,
  benchmark, sweep, training run or measurement is about to be designed or
  launched, and before any comparative or statistical sentence is written.
---

# Experiment protocol

One shape for every experiment in crypto, crypto-autoresearcher, cryptanalysis,
ml-cryptanalysis and cryptanalysis-rl. The rules are
`docs/experiment-protocol.md`; the schema is
`schemas/experiment-protocol.v1.json`; the checker is
`tools/experiment_protocol.py`; the worked example is
`examples/experiment-protocol/ecbench-l2-smoke-subset/`. In this repository a
ledgered experiment also keeps its `specification.yaml` contract
(`design-experiment`): the protocol record is the cross-repository form of the
same decisions, bound by hash in `execution_plan.protocol_hashes`. In crypto the
`controlled-experiment` skill decides whether a claim needs an experiment; this
skill writes the record once it does. Literature first, per the repository's
AGENTS.md: name the sources checked in `literature` with their provenance.

## 1. Write `protocol.json` before any data

Start from the example and fill every block. The ones that remove bias:

- **Claims, each in one class.** `theorem`, `exact_computation`,
  `comparative`, `heuristic_estimate` or `out_of_scope`. A comparative claim
  names the comparison that decides it, and only a `one_factor`, `factorial`
  or `absolute` comparison may decide anything.
- **Arms and controls.** Reference (the best existing method, matched rho for
  an ECDLP cost), baseline (the unmodified code), candidate; an **A/A** arm
  that differs only in a nuisance factor (its spread is the noise floor); a
  **positive control** the detector must find (a planted instance through the
  same code path); a **negative control** drawn from the stated null
  population, matched on everything but the property under test. Each absent
  control carries `not_applicable_reason`; "nothing found" without a passing
  positive control is invalid, not null.
- **Variable ledger.** Every factor that could move a primary metric:
  instrument (commit, build, binary sha256, flags, threads), host (CPU,
  frequency, SMT, NUMA, kernel, hypervisor, co-tenants), memory layout and
  environment, order and warm-up, inputs and seeds, spot preemption, the
  analyst. Each is `fixed`, `randomized`, `crossed` or `measured`; a comparison
  that differs in two of them is `confounded` and decides nothing.
  `same_instrument_as` makes the checker compare commit, binary and threads.
- **Randomization and blinding.** Interleave arms within every round (a
  `fixed` order needs a reason: one-time costs land on the first arm). Seeds
  come from the protocol hash (`seeds --all`), an explicit list written
  before any data, a nonce drawn after the freeze, or the harness's frozen
  rule (`harness_drawn`, with the rule named). Instances are sampled
  independently of arm. Say whether arm labels are masked during analysis
  (`blind` writes a masked analysis copy and a closed key). Withhold the
  original export, protocol and raw artifacts from that analysis; validate
  and review the original after unmasking. The masked copy does not pass
  protocol identity checks, and numerical signatures can still reveal methods.
- **Sample size and power.** Instances, replicates, warmups. For a rank test
  the smallest attainable two-sided p is `2/(N+1)`, which must beat
  `alpha/m` over the family of `m` tests; `power --n N --alpha a --m m` does
  the arithmetic and `validate` refuses a `passes` that disagrees. Time one
  call per arm first and record the fixed and per-sample cost.
- **Metrics with precision.** Counted metrics first (operations, field
  multiplications, instructions): they survive hardware. Each metric states
  unit, kind, definition from event to event, source field, aggregation,
  resolution and uncertainty method. A timed primary metric needs
  `timed_primary_justification` and `isolation_required` of L2 or tier B at
  least; it is read against the session's A/A interval.
- **Execution and checkpointing.** Backend and queue (`measurement_class:
  measurement` goes to an isolated host; `throughput`, `search` and
  `training` go to cheap spot capacity and checkpoint), timeout, the
  checkpoint policy with interval, grace and restore validation, and
  infrastructure-only retries. After a restore counted units are valid and
  the clock is not; the export lint enforces it. Submission mechanics are the
  `queue-experiment` skill in aburan28/crypto.
- **Stopping, decision, analysis.** Fixed-N or a preregistered sequential
  rule; the statistic, interval, multiple-comparison correction and
  effect-size measure; the fixed verdict vocabulary; the analysis script by
  path and sha256, frozen before the data; what is inadmissible.

```sh
python3 tools/experiment_protocol.py validate <dir>/protocol.json
python3 tools/experiment_protocol.py freeze <dir>/protocol.json --commit auto --filed-before-affected-data
python3 tools/experiment_protocol.py seeds <dir>/protocol.json --all
```

Commit the frozen record before the first data point. A change afterwards is
an amendment under a new `version`, dated, saying whether it preceded the data
it affects; both versions are reported. Under Claude Code the run itself goes
through the model tiers (`docs/model-tiers.md`): the director compiles the
frozen protocol into a card, the mechanical tier runs it, and this tier keeps
the design and the reading.

## 2. Export the data in one shape

After the run, write `export.json` (`experiment.export/v1`) beside the raw
records, never inside a sealed session directory:

```sh
python3 tools/experiment_protocol.py from-ecbench <session_dir> --protocol <dir>/protocol.json --out <dir>/export.json --export-id <id>
python3 tools/experiment_protocol.py from-taskq <result.json> --protocol ... --arm <arm> --instance <i> --out ... --export-id <id>
python3 tools/experiment_protocol.py from-rows rows.jsonl --protocol ... --out ... --export-id <id> [--map metric=column]
python3 tools/experiment_protocol.py check-export <dir>/export.json --protocol <dir>/protocol.json --verify-files
python3 tools/experiment_protocol.py flow <dir>/export.json
```

Every execution is a row: arm, instance, seed, replicate, warmup, status and
outcome class, attempts and resumes, counted measurements, clock with
`wall_valid`, rusage, every native counter, isolation tier and blockers,
verification, exclusion rule, artifacts by hash. The `flow` block is the
CONSORT count (planned, attempted, completed, not completed, interrupted,
resumed, excluded by rule). `notes` are observations only; judgments go in
review records (`review-run`). A backend without an adapter writes the shape
directly and runs `check-export` until it passes.

## 3. Report

The run report (`research-visuals`) and the PR cite the protocol hash, the
export, the flow table and the A/A interval. Verdicts use the protocol's
vocabulary. Effect size before significance; a scope sentence; superseded
claims corrected in place with a date. Nothing in the export or the report
promotes a hypothesis: `review-evidence` (here), the validation gate and the
PR (crypto) decide.

## Checklist

- [ ] every claim classed; comparative claims decided by a decisive comparison
- [ ] A/A, positive and negative controls present or each excused in writing
- [ ] variable ledger lists every confounder with its treatment; no decisive comparison is confounded
- [ ] arm order interleaved; seeds derived before data; instance sampling independent of arm; blinding stated
- [ ] power arithmetic passes; pre-flight runtime recorded
- [ ] primary metrics counted; a timed one justified with L2 or better
- [ ] checkpoint policy and after-restore semantics declared
- [ ] stopping and decision rules and the analysis script frozen; inadmissible moves listed
- [ ] `validate` clean, `freeze` done, committed before the first data point
- [ ] `export.json` written, `check-export --verify-files` clean, `flow` in the report
