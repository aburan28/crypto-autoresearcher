# Crypto Autoresearcher

A multi-agent orchestration framework for rigorous, reproducible ECDLP experimentation.

The project separates research into three primary roles:

- **Coordinator** — owns priorities, experiment approval, state transitions, and synthesis.
- **Idea Generator** — proposes falsifiable mechanisms, predictions, and minimal discriminating tests.
- **Executor** — implements approved protocols, runs experiments, and preserves immutable artifacts.

## Design goals

- prevent speculative ideas from becoming unsupported conclusions;
- make every experiment reproducible from an exact revision and command;
- preserve failed and anomalous runs as research evidence;
- distinguish infrastructure failure from negative empirical evidence;
- scope conclusions to the tested curves, parameters, solver, and compute budget;
- support iterative autonomous research without letting agents silently redefine success.

## Repository map

```text
AGENTS.md                              Global rules and inter-agent contract
agents/coordinator.md                  Coordinator authority and decision semantics
agents/idea-generator.md               Hypothesis-generation and novelty discipline
agents/executor.md                     Execution, artifact, and failure semantics
docs/task-lifecycle.md                 End-to-end research state machine
docs/evidence-and-reproducibility.md   Evidence hierarchy and reproducibility rules
templates/research-records.md          YAML templates for all shared records
ROADMAP.md                             Initial engineering and ECDLP research roadmap
schemas/                               Strict JSON schemas for shared records
src/crypto_autoresearcher/             Validation, ID, ledger, and immutable-run CLI
experiments/                            Frozen protocols, implementations, and run artifacts
tests/                                  Dependency-free unit and toy arithmetic checks
```

## Operating loop

```text
Research question
      ↓
Idea Generator proposals
      ↓
Coordinator selects and specifies a hypothesis
      ↓
Coordinator freezes and approves an experiment protocol
      ↓
Executor implements and runs bounded experiments
      ↓
Executor returns immutable run records and observations
      ↓
Coordinator validates evidence and chooses:
replicate | expand | refine | support | weaken | reject scoped | pause
```

## Fundamental rule

Only the Coordinator may change the official status of a hypothesis. The Idea Generator proposes; the Executor measures; the Coordinator decides what the evidence justifies.

## Getting started

1. Read [`AGENTS.md`](AGENTS.md).
2. Review the role contract for the agent being instantiated.
3. Create a research question and hypothesis using [`templates/research-records.md`](templates/research-records.md).
4. Freeze an experiment protocol before dispatching it to the Executor.
5. Store every run with its exact command, revision, environment, seed, raw result, logs, and validity status.
6. Record the Coordinator decision that follows from the evidence.

## Local CLI

The initial CLI uses only the Python standard library. Run it without installing the package:

```bash
PYTHONPATH=src python3 -m crypto_autoresearcher validate experiments
PYTHONPATH=src python3 -m crypto_autoresearcher new-id EXP ECDLP-ENERGY
PYTHONPATH=src python3 -m crypto_autoresearcher index --output ledger.json
```

Unapproved `draft` experiments may use explicit `--allow-dirty` development
runs. They cannot produce locked receipts and are not canonical evidence:

```bash
PYTHONPATH=src python3 -m crypto_autoresearcher run --allow-dirty \
  --experiment-dir experiments/EXP-DRAFT-001 \
  --run-id RUN-DRAFT-001 --seed 1 --timeout 60 -- \
  python3 experiments/EXP-DRAFT-001/src/run.py
```

An `approved` experiment must declare an execution plan and cannot fall back to
development mode. Canonical launch additionally requires an externally audited
approval file and its expected SHA-256:

```bash
PYTHONPATH=src python3 -m crypto_autoresearcher run \
  --experiment-dir experiments/EXP-NAME-001 \
  --run-id RUN-NAME-001 --seed 1 \
  --approval-lock /absolute/path/execution-approval.json \
  --approval-lock-sha256 <audited-sha256> -- \
  /absolute/path/to/python -I -S -B experiments/EXP-NAME-001/src/run.py
```

The lock binds the approved commit, specification, plan, complete protocol
hashes, Python runtime, and resource policy. Locked runs emit a strict runner
receipt, recheck state after execution, and never overwrite a run ID.

Run the test suite with:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python3 -m unittest discover -s tests -v
```

## First research program

[`EXP-ECDLP-ENERGY-001`](experiments/EXP-ECDLP-ENERGY-001/contract.md) is a verification-first toy preflight for coordinate additive energy, recursive two-/three-sum compilation, five-term decomposition, and fixed-curve preprocessing. It includes matched random and high-energy controls, measured Pollard rho, separate offline/online accounting, and an independent arithmetic verifier. Its protocol explicitly forbids interpreting toy success as a faster-than-rho or deployed-curve result.

## Status

The semantic foundation, schema-validated local CLI, immutable run wrapper, generated ledger index, and first verification-first ECDLP experiment are implemented. Coordinator queues and pluggable agent adapters remain the next orchestration milestone.
