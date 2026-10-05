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
autoresearch campaign autopilot --dry-run
autoresearch campaign autopilot --once --backend local --backend zai
autoresearch campaign autopilot --backend local --backend zai --backend openai
autoresearch campaign autopilot --report
# If `opencode serve` is already running locally:
autoresearch campaign autopilot --attach http://127.0.0.1:4096
```

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
an explicit model. It also uses `--auto` for unattended permission requests;
explicit role `deny` rules remain in force. The dispatcher invokes the
Coordinator subagent for reserved decisions. OpenCode's generated Coordinator
and Executor are subagents and
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

## Continuous local Cairn node

The supervisor above uses OpenCode. `opencode.json` now starts the Cairn MCP
server and the generated Executor/Validator/Red Team bindings grant only their
role's network tools. The Coordinator remains responsible for posting and
funding objectives; the MCP launcher forces `CAIRN_MCP_MAX_SPEND=0` even when
an operator shell sets a higher value. A funded objective still needs a
Coordinator decision and a CLI post. The existing runner's Stage 0 Cairn
certificate check uses its own offline log, so it never opens the live node's
exclusive log a second time. The service sets `CAIRN_BRIDGE_LOG` to its private
`stage0.jsonl`; older standalone runs may still use `CAIRN_LOG`.
The service clears inherited demo epoch, log, bootstrap, validator, and legacy
MCP binary settings so this checkout starts against its own private node.

On macOS, use one clean checkout and one private state directory. Build Cairn
with the reader embedded (`make ui-build` in the Cairn checkout), then create a
signed submitter identity once:

```sh
mkdir -p .cairn-runtime/bin
cp /absolute/path/to/reader-enabled/cairn .cairn-runtime/bin/cairn
.cairn-runtime/bin/cairn identity --out .cairn-runtime/executor.identity.json
python3 tools/cairn_autopilot_service.py \
  --repo . --state-dir .cairn-runtime/campaign \
  --cairn-bin .cairn-runtime/bin/cairn \
  --identity .cairn-runtime/executor.identity.json \
  --cairn-data .cairn-runtime/node \
  --opencode-port 4096 --cairn-serve 127.0.0.1:8081 \
  --cairn-listen 127.0.0.1:9001 --backend local
```

`tools/cairn_autopilot_service.py` keeps `opencode serve` on loopback,
requires its `/mcp` endpoint to report Cairn connected, and attaches the
existing bounded-action supervisor to it. The node and campaign checkpoint
survive individual actions; its state, identity, node log and OpenCode log stay
in `.cairn-runtime/`, which Git ignores. Use a user service manager such as
launchd with restart enabled for reboots and process failures. The command
above runs indefinitely until stopped. `--once` runs one campaign action for
a bounded live check; `--check` only confirms that Cairn connected and then
stops. `--timeout` caps one OpenCode action without treating a
watchdog as research evidence. `autoresearch campaign autopilot --repo .
--state-dir .cairn-runtime/campaign --report` reads its progress.
The service puts OpenCode's XDG data, state, cache, and config under the same
private state directory, so a full system volume or an unrelated global plugin
cannot break this checkout's continuous run.

After `--check` and `--once` succeed, render a launchd agent with the same
paths and ports, then install it for the current macOS user:

```sh
python3 tools/cairn_autopilot_launchd.py --repo . \
  --state-dir .cairn-runtime/campaign \
  --cairn-bin .cairn-runtime/bin/cairn \
  --identity .cairn-runtime/executor.identity.json \
  --cairn-data .cairn-runtime/node \
  --opencode-port 4096 --cairn-serve 127.0.0.1:8081 \
  --cairn-listen 127.0.0.1:9001 --backend local \
  --out .cairn-runtime/campaign/com.crypto-autoresearcher.cairn.plist
mkdir -p ~/Library/LaunchAgents
cp .cairn-runtime/campaign/com.crypto-autoresearcher.cairn.plist \
  ~/Library/LaunchAgents/com.crypto-autoresearcher.cairn.plist
launchctl bootstrap "gui/$(id -u)" \
  ~/Library/LaunchAgents/com.crypto-autoresearcher.cairn.plist
launchctl print "gui/$(id -u)/com.crypto-autoresearcher.cairn"
```

The generated agent restarts after failures and login; its stdout, stderr,
node log, and campaign event log are all in `.cairn-runtime/`. Stop it with
`launchctl bootout "gui/$(id -u)/com.crypto-autoresearcher.cairn"` before
running a manual copy on the same ports and log. Keep this dedicated checkout
and its ignored runtime directory in place while the service is installed.

This first continuous node gives research agents the network tools and makes
the existing Stage 0 certificate check available during runs. A general
automatic route from every approved experiment to a live, funded Cairn
objective is still missing. `tools/exp_to_objective.py` can render certificate
objectives, and `tools/cairn_seam_demo.py` proves one fixed EXP/RUN end to end;
the replay path still needs a read-only wrapper, a Coordinator funding record,
and durable receipt reconciliation before it can be made automatic. Until
then, an action with no posted matching objective must continue its normal
harness work rather than claim it contributed a network result.

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
