# Crypto Autoresearcher

A multi-agent orchestration framework for rigorous, reproducible ECDLP experimentation.

The project separates research into primary roles with separate authority:

- **Coordinator** — owns priorities, experiment approval, state transitions, and synthesis.
- **Idea Generator** — proposes falsifiable mechanisms, predictions, and minimal discriminating tests.
- **Executor** — implements approved protocols, runs experiments, and preserves immutable artifacts.
- **Reviewer** — independently challenges claims and proposed state transitions.
- **Validator** — independently verifies receipts, controls, and metric calculations.
- **Red Team** — attacks interpretations, hidden costs, and unjustified scope expansion.

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
CLAUDE.md                              Claude Code runtime binding (one runtime of several)
agents/coordinator.md                  Coordinator authority and decision semantics
agents/idea-generator.md               Hypothesis-generation and novelty discipline
agents/executor.md                     Execution, artifact, and failure semantics
agents/validator.md                    Independent receipt and control validation
agents/red-team.md                     Interpretation and cost-model falsification
.claude/agents/                        Operational subagent definitions (Claude Code)
.claude/skills/                        Lifecycle skills: /propose-ideas, /design-experiment,
                                       /run-experiment, /review-evidence, /research-status,
                                       /curate-knowledge, /coordinate-research-goal
orchestration/roles.yaml               Role authority and tool surface, runtime-neutral
orchestration/model-policies.yaml      What each role needs from a model (no vendors)
orchestration/providers.yaml           Backends, wire protocols, and runtimes
orchestration/model-bindings.yaml      Policy -> concrete model, per backend
orchestration/adapter/                 Strict policy resolution and multi-API transport
docs/inference-backends.md             Backend/runtime setup and resolution semantics
docs/task-lifecycle.md                 End-to-end research state machine
docs/evidence-and-reproducibility.md   Evidence hierarchy and reproducibility rules
docs/dynamic-subagent-dispatch.md      Artifact-driven task dispatch and ownership rules
docs/knowledge-assessment-20260724.md  Audit of corpus, ledger, and artifact completeness
templates/research-records.md          YAML templates for all shared records
templates/subagent-task-queue.json     JSON template for bounded task dispatch
tools/research_dispatch.py             Validates and renders the ready-task plan
tools/check_runtime_bindings.py        Guards role definitions against runtime drift
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

## Choosing an inference backend

Roles, policies, and evidence records name no vendor. Which model answers is a
binding table plus one environment variable — see
[`docs/inference-backends.md`](docs/inference-backends.md):

```sh
python3 -m orchestration.adapter matrix          # what each backend can serve
python3 -m orchestration.adapter doctor --probe  # are the configured ids real?
export AUTORESEARCH_BACKEND=zai                  # run the program on GLM
```

Resolution is strict: a backend that cannot meet a policy's stated
requirements stops the task rather than quietly answering with something
weaker, and every substitution is recorded in the run manifest.

## Getting started

When working in Claude Code, the lifecycle is driven by skills — see
[`CLAUDE.md`](CLAUDE.md):

```text
/research-status → /propose-ideas → /design-experiment → /run-experiment → /review-evidence
```

The skills are one runtime's front end. Under another runtime, the same
lifecycle is driven from the role contracts in `agents/` and the dispatch
queue in `tools/research_dispatch.py`.

Manual path:

1. Read [`AGENTS.md`](AGENTS.md).
2. Review the role contract for the agent being instantiated.
3. Create a research question and hypothesis using [`templates/research-records.md`](templates/research-records.md).
4. Freeze an experiment protocol before dispatching it to the Executor.
5. Store every run with its exact command, revision, environment, seed, raw result, logs, and validity status.
6. Record the Coordinator decision that follows from the evidence.

## Status

The harness now includes a schema-validated dispatch planner with Coordinator
snapshot and ledger-commit gates. The next implementation milestones are an
immutable run wrapper, a goal-batch launcher, and a pluggable agent adapter
interface.

## Focused autoresearch

The executable focus layer keeps the campaign on a few decision-changing
experiments and enforces reproduce-before-expand. Queue v3 also emits an
attention contract, reconciled stage budget, claim-by-claim verdict matrix,
experiment/run DAG, scope deviations, and append-only corrections:

```sh
python3 tools/autoresearch_focus.py focus/focus_queue_20260717.json \
  --output focus/current_plan.json \
  --report focus/current_plan.md
python3 -m unittest tools/test_autoresearch_focus.py
```

See `docs/focused-autoresearch-loop.md` for the scoring and ambiguity policy.

## Dynamic subagent dispatch

The dispatch queue assigns unblocked, bounded work to distinct roles with
exclusive write scopes and independent review. It is deliberately limited to
three concurrent subagent tasks, so capacity cannot outrun review or cause
concurrent mutation of research evidence.

The Coordinator alone makes durable research commits: a snapshot commit freezes
each producer's exact artifacts before review, then a ledger commit records the
reviews, evidence, decision, and any status change. The dispatcher verifies
each archive receipt against the real Git diff and recorded file hashes, so
theories, run packages, review reports, and ledger records cannot be promoted
from an uncommitted working tree.

```sh
python3 tools/research_dispatch.py templates/subagent-task-queue.json \
  --output /tmp/research_dispatch_plan.json \
  --report /tmp/research_dispatch_plan.md
python3 -m unittest tools/test_research_dispatch.py
```

See `docs/dynamic-subagent-dispatch.md` for the state machine and promotion
rules.
