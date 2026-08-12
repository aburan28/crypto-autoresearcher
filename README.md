# Crypto Autoresearcher

A content-addressed migration of the historical Autolab task and result corpus
is bound to the harness by `EXP-ALMIG-001`. The 48 GB byte mirror is a local
working-tree archive rather than GitHub content; the repository carries its
SHA-256 manifests, task catalog, receipts, and materialization tool. See
`docs/autolab-migration-20260802.md`. Verify a local mirror without changing the
canonical receipt with
`python3 tools/migrate_autolab_archive.py --verify-only --no-harness-output
--metadata-dir /tmp/autolab-migration-20260802-r1-verify`.

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

## Research direction

What counts as a target result is defined in
[`docs/target-result-profile.md`](docs/target-result-profile.md). Its canonical
exemplar is Wesolowski's p^{1/3+o(1)} result on the supersingular isogeny
problem (full text in `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`): move the
asymptotic exponent of a central hard problem rather than polish logarithmic
cofactors; state conditional theorems against explicit, numbered heuristics;
validate those heuristics experimentally at cryptographic scale; and disclose
concrete costs, memory requirements, and affected-vs-safe scope honestly. The
orchestration machinery below exists to produce results of that shape — and to
block claims that fall short of its honesty standards.

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
orchestration/agent/                   api_direct runtime: LangGraph tool loop, scope-enforced
orchestration/eval/                    Capability and discipline measurement, with intervals
evals/suites/                          Eval tasks: verifiable answers and trap cases
docs/measuring-the-harness.md          How harness effectiveness is measured, and what it misses
docs/inventor-protocol.md              Object-first ideation, closure, and proof-architecture search
docs/inference-backends.md             Backend/runtime setup and resolution semantics
docs/task-lifecycle.md                 End-to-end research state machine
docs/evidence-and-reproducibility.md   Evidence hierarchy and reproducibility rules
docs/target-result-profile.md          Target result profile: exemplar-anchored direction criteria
docs/dynamic-subagent-dispatch.md      Artifact-driven task dispatch and ownership rules
docs/knowledge-assessment-20260724.md  Audit of corpus, ledger, and artifact completeness
docs/github-automation.md              PR review, @claude agent, and periodic branch sync
REVIEW.md                              Contract for automated pull-request review
tools/sync_open_branches.py            Merges main into stale PR branches; never rebases
templates/research-records.md          YAML templates for all shared records
templates/subagent-task-queue.json     JSON template for bounded task dispatch
orchestration/cli.py                   The `autoresearch` entry point (doctor, loop, status)
pyproject.toml                         Editable install and console scripts
Makefile                               Common local flows; token-spending ones marked
tools/research_dispatch.py             Validates and renders the ready-task plan
tools/check_runtime_bindings.py        Guards role definitions against runtime drift
ledger/                                Canonical YAML research records
experiments/                           Frozen contracts and immutable run artifacts
knowledge/                             Curated long-term knowledge corpus
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

## Running it locally

```sh
git clone <this repo> && cd crypto-autoresearcher
make install          # editable install + all dependencies
make doctor           # what is missing, before anything costs money
```

`doctor` checks the Python version, dependencies, configuration, credentials
per backend, role-binding drift, and suite health, then prints the specific
next command for whatever is blocking. Everything is offline and free.

Amazon Bedrock is disabled as a cost guardrail. OpenCode disables the provider
and defaults to OpenAI models, while the repository adapter rejects any Bedrock
backend, endpoint, or model identifier before inference. Authenticated direct
Codex and Claude Code sessions are allowed when their resolved provider is not
Bedrock, as are configured API backends such as `openai` or `local`; historical
run receipts remain immutable.

```sh
cp .env.example .env                      # fill in one key; .env is gitignored
autoresearch backends                     # endpoints, key variables, what is bound

autoresearch doctor                       # now green
autoresearch adapter doctor --probe       # are the configured model ids real?
autoresearch loop --dry-run               # how many model calls a loop costs
autoresearch loop --trials 5              # run it
```

`make help` lists the rest. Targets that spend tokens are marked as such.

The single entry point wraps the three component CLIs, which remain available
directly: `autoresearch adapter|agent|eval ...`, or `python3 -m
orchestration.{adapter,agent,eval}`.

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

## Measuring whether it works

Two questions, never combined into one number — see
[`docs/measuring-the-harness.md`](docs/measuring-the-harness.md):

```sh
python3 -m orchestration.eval run     --suite evals/suites/capability.yaml --trials 5
python3 -m orchestration.eval run     --suite evals/suites/discipline.yaml --trials 5
python3 -m orchestration.eval compare --suite evals/suites/capability.yaml \
                                      --backends anthropic,zai --trials 10
```

`capability` asks whether it solves problems this repository can verify
arithmetically. `discipline` is the anti-benchmark: every task's correct answer
is "this does not show what it appears to show" — no solution exists, the run
timed out, the certificate fails, the scale does not transfer. A loop that
solves problems but overclaims is more dangerous than one that finds nothing,
so the two are always reported apart, with Wilson intervals and a refusal to
name a winner when they overlap.

## Getting started

When working in Claude Code, the lifecycle is driven by skills — see
[`CLAUDE.md`](CLAUDE.md):

```text
/research-status → /propose-ideas → /design-experiment → /run-experiment → /review-evidence
```

The skills are one runtime's front end. Under another runtime, the same
lifecycle is driven from the role contracts in `agents/` and the dispatch
queue in `tools/research_dispatch.py`. To execute a task without any agent CLI
at all:

```sh
python3 -m orchestration.agent plan --task ledger/handoffs/TASK-....yaml
python3 -m orchestration.agent run  --task ... --backend zai --out <task-dir>/agent
```

That runtime enforces the task's `write_scope` in the tools rather than asking
the model to respect it, and needs `requirements-agent.txt`.

Manual path:

1. Read [`AGENTS.md`](AGENTS.md).
2. Review the role contract for the agent being instantiated.
3. Create a research question and hypothesis using [`templates/research-records.md`](templates/research-records.md).
4. Freeze an experiment protocol before dispatching it to the Executor.
5. Store every run with its exact command, revision, environment, seed, raw result, logs, and validity status.
6. Record the Coordinator decision that follows from the evidence.

## Host plugins

The repository ships a thin, portable
[`crypto-autoresearcher-harness`](plugins/crypto-autoresearcher-harness/README.md)
plugin package for Codex, Claude Code, and OpenCode. It supplies a shared
front-door skill and a read-only preflight; it does not duplicate the role
contracts or create an alternate dispatch path. The checked-in bindings remain
the authority: `.claude/agents/`, `.opencode/agent/`, and `.codex/agents/` are
all generated from `orchestration/roles.yaml`.

Install instructions and host-specific discovery details are in the plugin
README. Every invocation begins with a no-cost readiness check before an agent
can dispatch a task or call a backend.

For multiple local agents, the same package also ships opt-in snippets for a
single loopback-only peer-check-in MCP daemon. It provides advisory presence
only; the ledger, dispatch queue, and Coordinator archive flow remain the sole
authority for research state.

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

The harness includes a schema-validated dispatch planner with Coordinator
snapshot and ledger-commit gates, an immutable run wrapper, and the pluggable
inference adapter: vendor-neutral policies, strict resolution, and three
runtimes over one set of role contracts. The next milestone is a goal-batch
launcher driving `orchestration.agent` across a whole dispatch batch.

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
