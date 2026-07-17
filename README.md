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
CLAUDE.md                              Claude Code harness wiring and conventions
agents/coordinator.md                  Coordinator authority and decision semantics
agents/idea-generator.md               Hypothesis-generation and novelty discipline
agents/executor.md                     Execution, artifact, and failure semantics
.claude/agents/                        Operational subagent definitions (Claude Code)
.claude/skills/                        Lifecycle skills: /propose-ideas, /design-experiment,
                                       /run-experiment, /review-evidence, /research-status,
                                       /curate-knowledge
docs/task-lifecycle.md                 End-to-end research state machine
docs/evidence-and-reproducibility.md   Evidence hierarchy and reproducibility rules
templates/research-records.md          YAML templates for all shared records
ledger/                                Canonical YAML research records
experiments/                           Frozen contracts and immutable run artifacts
knowledge/                             Curated long-term knowledge corpus
ROADMAP.md                             Initial engineering and ECDLP research roadmap
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

When working in Claude Code, the lifecycle is driven by skills — see
[`CLAUDE.md`](CLAUDE.md):

```text
/research-status → /propose-ideas → /design-experiment → /run-experiment → /review-evidence
```

Manual path:

1. Read [`AGENTS.md`](AGENTS.md).
2. Review the role contract for the agent being instantiated.
3. Create a research question and hypothesis using [`templates/research-records.md`](templates/research-records.md).
4. Freeze an experiment protocol before dispatching it to the Executor.
5. Store every run with its exact command, revision, environment, seed, raw result, logs, and validity status.
6. Record the Coordinator decision that follows from the evidence.

## Status

The semantic foundation is defined. The next implementation milestone is a schema-validated orchestration CLI, immutable run wrapper, coordinator queue, and pluggable agent adapter interface.