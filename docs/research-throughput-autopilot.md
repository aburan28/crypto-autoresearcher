# Research throughput: opt-in continuous supervisor

## Current boundary

`autoresearch loop` measures model eval suites. `autoresearch campaign` previously
observed state but did not select or launch successor actions. The public `$run`
skill executes existing programs and stops when none can execute; `/coordinate`
may design/approve work but cannot launch trials. The `autopilot` command is a
parent process that invokes each skill in its own bounded OpenCode turn. It
does not change an experiment's approval, scientific scope, or claim tier.

## Try it

```sh
scripts/research.sh --list                 # presets and what each needs
scripts/research.sh anthropic-batch --dry-run
scripts/research.sh openrouter --once
scripts/research.sh abliterated            # keeps running
scripts/research.sh local --report
```

`scripts/research.sh <preset> [flags]` is `autoresearch campaign autopilot
--preset <preset> [flags]` with the pinned interpreter chosen for you. The
long form is still there:

```sh
autoresearch campaign autopilot --dry-run
autoresearch campaign autopilot --once --backend local --backend zai
autoresearch campaign autopilot --backend local --backend zai --backend openai
autoresearch campaign autopilot --report
# If `opencode serve` is already running locally:
autoresearch campaign autopilot --attach http://127.0.0.1:4096
```

### Presets: one name for runtime, backends and delivery

A preset fixes three things and nothing else: which agent CLI runs each
action (`--runtime opencode | claude_code | codex_cli`), which backends it
may fail over across (`--backend`, in order), and whether draftable actions
go through the Message Batches API first (`--delivery`). Explicit flags
override the preset. A preset never names a model: models come from
`orchestration/model-bindings.yaml`, from the operator overlay
`orchestration/model-bindings.local.yaml` (gitignored; start from
`model-bindings.local.example.yaml`), or from `--model ID --model-caps
effort=…,context=…,output=…` for one run, which writes an
`operator-supplied` overlay under the state directory and layers it over the
standing one. The resolver still applies the role policy floors to whatever
is bound, so a model whose declared capabilities fall short of the
Coordinator policy is skipped, not downgraded.

| preset | runtime | backends | delivery |
|:--|:--|:--|:--|
| `anthropic` | Claude Code | anthropic | interactive |
| `anthropic-batch` | Claude Code | anthropic | auto (drafts batched) |
| `anthropic-opencode` | OpenCode | anthropic | interactive |
| `openrouter`, `openrouter-batch`, `openrouter-codex` | OpenCode / OpenCode / Codex | openrouter | interactive / auto / interactive |
| `abliterated`, `abliterated-claude`, `abliterated-codex` | OpenCode / Claude Code / Codex | abliteration, abliteration-anthropic, abliteration | interactive |
| `local`, `local-codex` | OpenCode / Codex | local | interactive |
| `zai`, `zai-claude` | OpenCode / Claude Code | zai, zai-anthropic | interactive |
| `fireworks`, `fireworks-claude` | OpenCode / Claude Code | fireworks, fireworks-anthropic | interactive |
| `openai`, `codex` | OpenCode / Codex | openai | interactive |
| `failover` (default) | OpenCode | local, zai, fireworks, openai, anthropic | interactive |

`--list-presets` prints the same table with each preset's prerequisites
(the credential variable and the CLI binary). The repository ships
`openrouter` unbound on purpose: a committed model id is an assertion that
somebody probed it. The `openrouter*` presets therefore refuse to start
until the overlay or `--model` binds one, and say so.

A runtime and a backend must speak the same wire: Claude Code takes the
Anthropic-compatible backends (`anthropic`, `zai-anthropic`,
`fireworks-anthropic`, `abliteration-anthropic`), Codex the OpenAI-compatible
ones, OpenCode both through its own provider catalogue. `providers.yaml`
`runtimes.*.compatible_backends` is the source, and a mismatch is refused
before the first action rather than failing on every model in turn.

For Claude Code and Codex the supervisor exports the backend's endpoint,
credential and model into the worker's environment (`ANTHROPIC_BASE_URL`,
`ANTHROPIC_AUTH_TOKEN`, `ANTHROPIC_MODEL`; `OPENAI_BASE_URL`,
`OPENAI_API_KEY`, `OPENAI_MODEL`), except that a runtime talking to its own
vendor keeps its own login. Non-interactive Claude Code cannot answer a
permission prompt, so it starts with `--permission-mode acceptEdits`; widen
or replace that with `AUTORESEARCH_CLAUDE_ARGS` (for example
`--allowedTools 'Bash(git:*)'`). Codex starts with `--sandbox
workspace-write`; `AUTORESEARCH_CODEX_ARGS` replaces it. Both choices are
the operator's, recorded in the attempt's command, not the supervisor's.

### The Message Batches lane

With `--delivery auto` or `batch`, a `design` or `portfolio` action is first
submitted to the Anthropic Message Batches API as one tool-less turn: the
role contract as the system prompt, the action prompt plus the proposal and
the record templates as the user turn, and standing instructions to produce
a *draft* -- no approval language, `ID-TBD` for every identifier, provenance
on every citation. The supervisor records the submission in
`coordination/inference-batches/<batch id>/` through the adapter's
write-once registry, excludes the action while the batch runs, and polls
every `--batch-poll-seconds` (default 300). When the batch ends, the draft
is written to the attempt directory as `draft.md` and the *same* action runs
interactively with the path appended and a note that the text is untrusted:
the filing agent verifies every statement against the repository, mints
identifiers with the repository tools, and discards what does not survive.
An errored or expired batch cools the action down for `--retry-seconds` and
is counted in the report's `batch_drafts_failed`.

`run`, `prepare`, `repair` and `review` act on the checkout from their first
tool call, so they are always interactive whatever `--delivery` says. The
lane's backend is `--batch-backend` (default `anthropic`, the only backend
declaring the API); the tool-using half may run on any preset, which is what
`openrouter-batch` does. With `--once` or `--max-actions`, a submitted draft
counts as an action and the process returns with it listed under
`pending_batches`; `--wait-batches SECONDS` keeps polling that long instead.
A batch that is still running when the process exits is collected by the
next invocation with the same state directory, or by `autoresearch adapter
batch collect` by hand. Nothing in the lane writes under `ledger/` or
`experiments/`.

The last command with no action limit keeps running. Run it under a service
manager that restarts the process after host reboot. The local, private
`.git/autoresearch-autopilot/` directory stores an append-only action log,
per-model JSONL output, stderr, and a restart checkpoint. Start one process per
checkout; a nonblocking file lock prevents duplicate local supervisors. Use
`--state-dir` when the checkout's `.git` is not a directory. This does not
replace task claims or machine-resource gates in the experiment runner.
`--attach` reuses the OpenCode server and avoids repeated MCP startup; it
does not claim to lower input tokens. A user service can run the unlimited
command with `Restart=always`, `RestartSec=30`, and the checkout as
`WorkingDirectory`; put credentials in the service environment, not Git.

The selection order is: ready ECC trial plan; proposed ECC idea needing
`/design-experiment`; approved ECC experiment needing a launcher or plan;
reconciliation of ECC partial/invalid plans; then corresponding non-ECC work;
finally one portfolio coordination pass. These
selectors read `tools/newest_experiments.py` and `tools/ecc_priority.py`, so
they inherit the existing ECC area policy. A failed or unchanged action has a
cooldown. If a run returns, a separate Coordinator reconciliation action
comes next before any repeat. A process killed mid-action also reconciles on
restart. The Coordinator must still archive, verify, and publish per AGENTS.md.

Each OpenCode call uses the primary `build` dispatcher with `--format json` and
an explicit model. The dispatcher invokes the Coordinator subagent for reserved
decisions. OpenCode's generated Coordinator and Executor are subagents and
cannot perform the full top-level workflow alone. Their fixed model overrides
were removed so they inherit the selected primary model on failover. The
candidate list comes from the existing model bindings and the role's policy; candidates
missing the policy floor are skipped. A nonzero result can move to the next
backend only if neither a tool call nor checkout change was observed. An
ambiguous partial action goes to reconciliation. The event log records every
attempt, requested policy, resolved model, fallback, wall time, and usage when
OpenCode reports it. The OpenCode CLI's effective reasoning setting is not
attested here; do not infer it from the policy. A `0` exit means only that the
worker returned. The
report leaves verified discoveries and independent relations **null** until
linked scientific receipts provide those values.
If every eligible model fails before a tool or checkout effect, the action
retries after `--retry-seconds` (default five minutes), without inventing a
partial experiment or suppressing the queue for a day.

OpenCode uses `opencode run --model provider/model --format json` ([CLI
reference](https://opencode.ai/docs/cli/)); local vLLM
uses the repo's `vllm` provider ID. Check live model names with
`opencode models --refresh` and the adapter's probe before relying on them.
The repository currently leaves its OpenRouter bindings unbound. The
[`openrouter/free`](https://openrouter.ai/docs/guides/routing/routers/free-router)
chooses dynamically among free models, so its declared
200k context is not proof that each selected model meets the Coordinator's
reasoning and output floors. A free router may draft scoped ideas or run a
shadow comparison; a frozen decision needs an evaluated, eligible binding and
an independent review where required. Do not label a router-selected model as
probe-verified solely because the router endpoint responded. OpenRouter
[provider failover is automatic, while model fallbacks require an explicit
list](https://openrouter.ai/blog/insights/reliability-failover/);
the supervisor's backend failover covers a different failure boundary.

## What to measure every day

| Quantity | Source | Interpretation |
| --- | --- | --- |
| Bounded actions/day and empty-queue recovery | supervisor events | Process activity, not discoveries |
| Candidate protocols approved/day | archived `EXP-*` and approval decisions | Research supply, not a valid result |
| Validated experiments and controls/day | immutable runner and validator receipts | Reproducible observations |
| Verified independent relation rank per charged second | IC benchmark receipts | Primary point-decomposition throughput |
| Complete verified DLPs per charged time/memory | `cryptanalysis/experiments/ic-bench` | End-to-end comparison with rho |
| Input/output tokens, cost, retry rate and source coverage | model JSONL + task manifests | Efficiency; null when missing |
| Median time from result to next ranked action | supervisor and archive timestamps | Continuation latency |

The local report now shows design, run, and total actions over the trailing
24 hours, plus the median delay from a worker finishing to the next action
starting. A run also records the before/after count of hash-validated runner
outputs under the **same frozen trial-plan SHA-256**. The report sums that
signed delta for the last 24 hours, includes its observation coverage, and
shows daily measured model cost with its own coverage. A changed plan or
unavailable receipt leaves the trial delta unknown. It streams the append-only
event log, so a long-running service does not load its entire history into
memory. Runner output validation is not scientific review or publication:
verified discoveries and independent relations remain null until an archive
and benchmark receipt joiner can substantiate them.

Use matched seeds, curves, solver settings, and hardware for factor-base
comparisons. Charge base construction, orbit/phase lookup, failed decomposition
searches, solving, relation verification, sparse rank, descent, and any
preprocessing. Report censored runs as censored, never as zero cost. Separate
measured toy behavior from a projected ECC2K-130 attack. The 131-fold orbit
storage collapse and toy phase-aware gains are useful hypotheses; neither
establishes a relation-generation advantage at n=131.
The existing [`fb-search` measurements](https://github.com/aburan28/cryptanalysis/blob/claude/cryptanalysis-repo-setup-p59kek/experiments/fb-search/README.md)
report about 35% standard deviation in toy collection length, so compare
paired bases across repeated workloads rather than announcing a win from one
seed. The [`crypto` boundary ledger](https://github.com/aburan28/crypto/blob/main/research/notes/index-calculus/RESEARCH_IC_BOUNDARY_LEDGER.md)
already prices full pipelines against matched rho references; use that cost
boundary for attack-level claims.

## Reuse the factor-base archive

The `aburan28/cryptanalysis` repository already has
[`experiments/fb-archive/fbarchive.py`](https://github.com/aburan28/cryptanalysis/tree/claude/cryptanalysis-repo-setup-p59kek/experiments/fb-archive):
canonical `factor_base`, field, curve,
point/column data, SHA-256 digests, an `index.csv`, and S3 for large objects.
Its recipe-only rows correctly leave B and effective columns null. Its current
n=131 builder explicitly rejects enumerated Frobenius-stable subspaces until
the tau-orbit column rule is implemented. Extend that archive and its candidate
ID contract rather than writing a second canonical point store here.

The next archive version should add **content-addressed shards** of orbit
records `(orbit_key, signed_representative, Frobenius_phase,
subgroup_projection, column_id)`, with fixed field encoding/endian, sorted
order, record count, shard hash, and a Merkle/index manifest. Record the
equivalence rule, orbit size, stabilizers, torsion handling, membership
predicate and enumeration mode. Keep recipe-only cardinality null. Include a
separate measurement table keyed by `(factor_base_sha256, candidate_id,
workload_id, run_id, control_id)` carrying phase policy, solver/engine, seeds,
attempts, timeouts, rank increment, charged stage costs, peak memory, and
verification status. This keeps immutable objects separate from repeatable
measurements and permits SQL queries without duplicating billions of points.
Reuse the existing [`ic-bench`](https://github.com/aburan28/cryptanalysis/tree/claude/cryptanalysis-repo-setup-p59kek/experiments/ic-bench)
`candidate_id`, `workload_id`, and `run_id` instead of minting another identity.

First compare four paired toy bases: linear subspace, Frobenius-stable orbit
union, nonlinear low-degree predicate, and matched-size random/control base.
Test fixed-phase linear payload against quotient-key equations on identical
targets. Gate on cost per **verified independent relation**, then complete
DLP cost against the same rho reference. The existing `fb_meter` proposal
`IDEA-20260921-da1896` should provide uniform controls and yield/L/b
measurements; the archive supplies candidate identity and point data.

## Measured control-plane replay

`tests/test_campaign_autopilot.py` contains an empty-queue fixture and a
hash-bound approved trial plan. The selector routes `design -> run`; when the
run directory exists without a validated receipt it routes to `repair`, not a
second launch. A synthetic worker replay performs `design -> run -> review`
in **one supervisor invocation** and produces three logged action receipts.
A restart with an interrupted run goes straight to reconciliation. An
unchanged portfolio pass gets a 24-hour cooldown instead of a paid call every
five minutes. These are measured scheduling behaviors with fake workers:
there is no measured gain yet in discoveries/day, actual provider tokens,
or ECC relation generation. The live comparison is gate 2 below.

## Next implementation gates

1. Replay empty/ready/failed/restart states and compare autonomous handoffs
   per invocation; retain a zero-model-call dry run for queue inspection.
2. Enable a supervised live OpenCode trial only after model probes, a full
   checkout, and resource claims are available. Compare cost and completion
   with the prior manually prompted day using identical work.
3. Join archived experiment IDs to independent review and IC benchmark runs;
   populate the null discovery/relation fields only from verified scientific
   receipts. The runner trial delta is a separate lower-level measure.
4. Benchmark a cheap draft/coordinator candidate against the present strong
   policy on a held-out suite, including state-transition errors and token
   cost. Bind a cheaper Coordinator only after that capability test.
5. Extend `fb-archive` in `cryptanalysis` for orbit/phase shards and bridge its
   candidate IDs into Auto Researcher. Require a measured rank/cost win before
   claiming a new factor base improves the attack.
