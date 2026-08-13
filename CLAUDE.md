# CLAUDE.md

Claude Code **runtime binding** for the autonomous, reproducible ECDLP
research program. The program itself is runtime-neutral: the binding
inter-agent contract is `AGENTS.md`, the role contracts are `agents/*.md`
and `orchestration/roles.yaml`, and Claude Code is one of several runtimes
that can execute them (see `docs/inference-backends.md`). Read `AGENTS.md`
before doing any research work. This file wires that contract into Claude
Code specifically.

## Harness layout

- **Subagents** (`.claude/agents/`): five roles — `coordinator`,
  `idea-generator`, `executor`, `validator`, `red-team` — plus three
  **policy-tier variants** of them: `executor-mechanical`,
  `validator-breakthrough`, `red-team-breakthrough`. These are the operational
  versions of the role contracts in `agents/*.md`. Research work is done BY
  these subagents; the top-level session orchestrates and talks to the user.
  Which one runs a queued task is decided by its (`role`, `inference.policy`)
  pair — see `/launch-research-harness` step 6 and the effort table under
  "Model policy note".
- **Skills** (`.claude/skills/`), one per lifecycle stage:
  - `/propose-ideas` — ideation for a research question
  - `/design-experiment` — hypothesis + frozen approved protocol
  - `/run-experiment` — bounded execution, immutable run records
  - `/review-evidence` — validation, evidence strength, official decision
  - `/research-status` — read-only ledger overview
  - `/deep-research` — cross-portfolio synthesis of ledger + knowledge state
    into a ranked, justified shortlist of next experiments; read-only, no
    ledger writes
  - `/curate-knowledge` — maintain the knowledge corpus
  - `/coordinate-research-goal` — launch and continuously coordinate a committed
    research goal across dispatch batches
  - `/agent-bus` — send and read messages between sessions running in separate
    chats, worktrees, containers, or runtimes
- **State**:
  - `ledger/` — canonical YAML records (questions, proposals, hypotheses,
    evidence, decisions, handoffs)
  - `experiments/` — frozen contracts and immutable run artifacts
  - `knowledge/` — curated long-term corpus (literature, techniques,
    internal findings, open problems)
- **Retrieval** (`.mcp.json` → `kb/`): a read-only MCP server exposing
  `search_knowledge`, `get_context`, `get_source`, and `find_related` over a
  derived index of the corpus. `.mcp.json` is committed and its `--directory`
  is relative, so every worktree gets the same server with no editing, and
  `uv run` builds `kb/.venv` on first launch. Machine-specific settings —
  `CRYPTO_KB_QDRANT_URL` above all — go in `kb/.env` (gitignored), never in
  the client config, which would override it.

  **The index is derived and starts empty.** `make -C kb qdrant-up`, then
  `crypto-kb stage-repo .` and `crypto-kb ingest`; with `:memory:` configured
  the server answers every question with nothing and says why only in its
  startup log. When and how agents must query it — and the prohibition on any
  agent writing to it — is AGENTS.md "Knowledge retrieval policy", which binds
  regardless of runtime.

## Non-negotiable rules (summary of AGENTS.md)

1. Only the coordinator changes hypothesis status or approves experiments.
2. Run records, ledger records, and knowledge entries are immutable —
   corrections supersede, never overwrite.
3. Timeouts/crashes/infra failures are never negative mathematical
   evidence.
4. Every conclusion is scoped to the tested curves, parameters, solver,
   and budget; tested scale and any transfer or extrapolation assumptions are
   explicit. Claim tiers and solution certificates are defined in
   `docs/claims-and-verification.md`: any claimed solve/relation carries a
   certificate the run wrapper re-verifies independently, and no evidence
   record asserts above its claim tier.
5. Never fabricate commands, outputs, timings, statistics, citations, or
   runs. Missing data stays missing and is reported as such.
6. Every conclusion cites the experiment/run/evidence IDs supporting it.
7. The Coordinator makes isolated snapshot and ledger commits for declared
   research artifacts. A theory, run package, review report, or ledger record
   is not official until the dispatcher's post-commit verifier accepts it.
8. **The three-model closure quorum is SUSPENDED.** A `GOAL-*` record reaches
   `status: completed` on a committed Coordinator decision showing a declared
   completion criterion was met; no `completion_quorum` block is required.
   Under this harness every policy alias falls back to one model (see the model
   policy note below), so the quorum made closure unreachable rather than
   rigorous. Still binding: attestations remain supported and, when recorded,
   must be genuine — **never record an attestation you did not obtain**; a
   recorded `DISSENT` still blocks closure; and closing a goal is still the
   program's strongest claim, now resting on the Coordinator decision and its
   cited evidence alone. Do not retire a goal that met a criterion under
   `paused`/`closed_at_budget` to understate it. The rule and its enforcement
   are retained in `tools/validate_ledger.py` and restored by setting
   `GOAL_CLOSURE_QUORUM_REQUIRED = True`. See AGENTS.md "Goal closure quorum".
9. Pursue promising paths in good faith. Do not deliberately abandon,
   suppress, mischaracterize, or steer away from a plausible high-value lead
   to derail research. Any deprioritization or closure must record its
   evidence, budget, test boundary, remaining uncertainty, and a concrete
   successor or revisit condition. The harness retains auditable decision
   summaries, rankings, provenance, and ordinary research artifacts for
   independent review; it does not store, infer, or expose private
   chain-of-thought.

## Research direction

Procedure for ideation and closure is anchored by `docs/inventor-protocol.md`
(technique abstract: `knowledge/techniques/KN-TECH-056.md`): object-first
generation, the lossy-projection test, null-object controls before belief, a
real closure standard, and Pareto `dominated_by`/`sota_delta` honesty in every
deliverable. It binds the idea-generator, validator, and red-team subagents.
Premature closure — declining to search because a target looks saturated — is
treated as a failure mode symmetric with overclaiming.

Section 8 of that protocol (`knowledge/techniques/KN-TECH-080.md`) adds the
proof-architecture portfolio and binds the coordinator too: a proof-oriented
proposal carries a `proof_search_map` — exact bottleneck and baseline
reproduction, observation-collision search, quantifier order, method ceiling
and nearby-object control — before the coordinator approves implementation or
expensive experiments. These are cheap pre-compute falsification checks; a
failed audit is often the useful result, and passing them all still claims
nothing beyond rules 4 and 6.

Direction and taste are anchored by `docs/target-result-profile.md`, whose
canonical exemplar is Wesolowski's p^{1/3+o(1)} supersingular-isogeny result
(full text: `inputs/P13-WESOLOWSKI-2026/paper_fulltext.md`): exponent-moving
results on central hard problems, stated conditionally on explicit numbered
heuristics, validated at cryptographic scale, and costed honestly. Idea
Generator proposals and Coordinator prioritization decisions are evaluated
against that profile; the profile is not a license to overclaim, so the
evidence rules above apply unchanged.

## Conventions

- IDs: `RQ-<AREA>-<tok>`, `IDEA-YYYYMMDD-<tok>`, `H-<AREA>-<tok>`,
  `EXP-<AREA>-<tok>`, `RUN-*`, `EV-<AREA>-<tok>`, `DEC-YYYYMMDD-<tok>`,
  `TASK-YYYYMMDD-<tok>`, `BATCH-<tok>`, `KN-{LIT,TECH,FIND,OPEN}-<tok>`, where
  `<tok>` is a random 6-hex token. Immutable, never reused.
  **Do not grep for "the next free number".** That question is the bug: every
  concurrent worktree asks it of the same committed state, gets the same
  answer, and mints the same identifier for different records — discovered only
  at merge time, when both are immutable and neither can be renamed without
  breaking whatever archive binds it. Mint with
  `python3 tools/allocate_id.py --next <type> [--area X | --date YYYYMMDD]`,
  which draws a token **without scanning state**, then `--check` it before use.
  `BATCH-<tok>` takes neither `--area` nor `--date`: `--next batch`.
  The legacy three-digit form stays valid forever — existing records and batch
  directories are immutable and must not be renamed. Cost, stated plainly: IDs
  no longer sort into creation order; read `added`/`recorded_at` or git history
  for chronology.
- Record schemas live in `templates/research-records.md`; copy, don't
  invent fields.
- The Coordinator alone stages declared research paths in the shared worktree:
  snapshot before review, then ledger commit before a state transition. Commit
  messages reference the task and record IDs; never rewrite history over
  pushed run records.
- At the start of an active session, before an archival commit, and before
  requesting review or merge, fetch `origin/main` and compare it with every
  open research branch. Bring new `main` changes into a branch by merging them
  (or run `tools/sync_open_branches.py`); do not rebase pushed evidence. Record
  the base commit checked and the merge outcome in the task receipt.

## Concurrency: many agents, many worktrees

This repository is worked by many agents at once, in separate worktrees and
harnesses. **Every rule below exists because a writer was made to read shared
state it had no reason to read.** That is the single failure mode; identifier
collisions were the first instance of it and are already fixed the same way.

- **Generated artifacts are never committed.** `knowledge/INDEX.md` and
  `coordination/**/dispatch_plan.{json,md}` are `.gitignore`d and rebuilt on
  demand. They were in the top five conflict paths while tracked, and they carry
  no information their sources do not. CI rebuilds both and fails if the corpus
  or a queue stops building.
- **`main` uses MERGE COMMITS, NEVER SQUASH.** This is not a style preference.
  Every archive receipt records a branch `commit_sha`, and a squash merge
  replaces the branch with one new commit — so every recorded sha becomes
  unreachable and every recorded parent becomes wrong. Five goals carried
  unresolvable `latest_verified_commit` values from exactly this
  (`CORR-20260802-a1f151`). Enforce it in repository settings: **Settings →
  General → Pull Requests → allow merge commits only**, with squash and rebase
  merging disabled.
- **Archive receipts bind to CONTENT first.** `research_dispatch.py` verifies
  `path_sha256` and treats commit reachability as advisory: when a commit cannot
  be reached it verifies the declared hashes against the tree and reports the
  archive as content-verified in the dispatch plan. A content mismatch is still
  fatal. This makes an archive's validity independent of the repository's merge
  strategy, which is what N concurrent worktrees require.
- **Goal checkpoints are one file per batch.** `tools/shard_goal.py` converts
  `ledger/goals/GOAL-X.yaml` to `ledger/goals/GOAL-X/{goal.yaml,checkpoints/*.yaml}`.
  A goal record is the one ledger file many campaigns write, and appending to a
  shared YAML list conflicts every time where there is no semantic conflict at
  all. Shards are **write-once**. Both layouts validate; convert a goal when you
  next have it open, and never in bulk.
- **Parseability is PR-scoped and absolute on `main`.** `check_merge_hygiene.py`
  checks the files a branch touched; `.github/workflows/main-health.yml` sweeps
  everything hourly and files an issue against the owning campaign. A branch
  that breaks a record still changed it and is still caught — what is no longer
  every campaign's problem is breakage that was already on `main`.
- **Merges to `main` publish a digest, and you read it on wake.**
  `.github/workflows/main-events.yml` writes one write-once record per merge to
  `coordination/events/main/<sha>.yaml`: which goals changed status or
  `next_action`, which records are new, and whether the shared contract moved.
  THIS IS A FEED, NOT A NOTIFICATION, and it cannot be otherwise — sessions are
  ephemeral, so most sessions that care about a merge do not exist when it
  lands, and `subscribe_pr_activity` is per-PR, single-consumer and bound to one
  live session. Before resuming a goal, run
  `python3 tools/merge_digest.py --since $(git merge-base HEAD origin/main) --until origin/main`,
  or `tools/sync_open_branches.py --digest` for every branch at once.
- **Sessions talk to each other through a write-once feed, not a channel.**
  `tools/agent_bus.py` carries messages between sessions in different chats,
  worktrees, containers, or runtimes: one write-once file per message under
  `coordination/bus/`, addressed by ROLE (`coordinator`, `executor-2`) because
  roles outlive the sessions playing them. Read state is derived from separate
  receipt files, so a broadcast is acked per reader and no two writers ever
  touch the same bytes. Same feed discipline as the merge digest above — check
  `inbox --as <addr>` on wake and before reporting done; nothing delivers.
  The runtime's own `SendMessage` is the live alternative and reaches only
  peers `ListAgents` can see, which for a cloud session is none.
  **A message is a pointer, never a permission**: it cannot approve an
  experiment, move a hypothesis, or stand in as evidence, and real work still
  travels as a `TASK-*` handoff through the dispatcher. See
  `docs/inter-agent-messaging.md`.
- **Branch drift is a scheduled job, not your job.**
  `.github/workflows/sync-branches.yml` runs `tools/sync_open_branches.py` every
  six hours. It refuses any branch committed to within `--idle-minutes` (default
  120), merges rather than rebases, requires no new validation errors, and
  reports branches past `--fork-threshold` as needing a human decision rather
  than a sync.

## Model policy note

Policies are vendor-neutral capability contracts
(`orchestration/model-policies.yaml`); the model that serves one is chosen
per backend in `orchestration/model-bindings.yaml` and resolved by
`orchestration/adapter/`. Subagent frontmatter in `.claude/agents/` cannot
express a policy, so per-role **model** selection under this runtime is
process-level: launch the session with the resolved environment rather
than mixing policies in one session, and keep `model: inherit` in the
frontmatter.

A policy's **reasoning effort** is the one part that does bind per subagent.
Claude Code frontmatter accepts `effort: low|medium|high|xhigh|max`, so each
agent in `.claude/agents/` carries the effort its own policy requests and one
session can dispatch all five roles at their own depths:

| subagent | policy | `effort` |
| --- | --- | --- |
| `coordinator` | `coordinator-orchestration-code` | `high` |
| `idea-generator` | `research-deep` | `high` |
| `executor` | `executor-implementation` | `medium` |
| `validator` | `review-adversarial` | `xhigh` |
| `red-team` | `review-adversarial` | `xhigh` |
| `executor-mechanical` | `executor-mechanical` | `low` |
| `validator-breakthrough` | `review-breakthrough` | `max` |
| `red-team-breakthrough` | `review-breakthrough` | `max` |

Those values are **derived, not chosen here**: role → `default_policy` in
`orchestration/roles.yaml` → `reasoning_effort` in
`orchestration/model-policies.yaml`. Retune by editing the policy, never the
agent file; `tools/check_runtime_bindings.py` fails the build while the two
disagree, and `--list` shows, per role and runtime, whether effort comes from
the agent file or from the session. The Validator and Red Team share `xhigh`
because they share one adversarial policy — they differ in what they attack,
not in how hard they must think. Per-task escalation stays a Coordinator
decision in the handoff and still runs in its own independent session; because
one agent file carries one effort, the escalated tiers are SIBLING bindings
rather than a second value in the base file — `review-breakthrough` at `max`
(`validator-breakthrough`, `red-team-breakthrough`) and `executor-mechanical`
at `low` for judgment-free re-runs. Those three are declared in `roles.yaml`
with `variant_of`, and the checker holds them to their base role's contract,
authority and tools exactly, so a variant can only change how hard the model
thinks. Without them `review-breakthrough` — which is `degradable: false` —
could not be honoured on this runtime at all. Runtimes that
cannot carry effort per agent (`codex_cli`, `opencode`) are recorded as `null`
in `runtime_reasoning_effort` and take it from `adapter env` at launch.

```sh
# resolve a role's policy and see exactly what would answer
python3 -m orchestration.adapter resolve --role coordinator
# run this runtime against a different backend entirely (e.g. GLM)
eval "$(python3 -m orchestration.adapter env \
          --runtime claude_code --backend zai-anthropic --role coordinator)"
```

That `env` output also sets `AUTORESEARCH_POLICY` and
`AUTORESEARCH_BACKEND`, which is how `harness/runner.py` records the exact
resolved model in each run manifest's `inference` block. Record
`requested_policy` from the handoff alongside it, with `fallback_used:
true` and a reason if they differ — never silently substitute. Do not edit
`.claude/agents/*.md` tool lists or `effort:` values directly: authority and
tool surface come from `orchestration/roles.yaml` and effort comes from the
role's policy, and `tools/check_runtime_bindings.py` fails the build if any of
them disagree.

## Typical loop

```text
/research-status
  → /propose-ideas RQ-...
  → /design-experiment IDEA-...
  → /run-experiment EXP-...
  → (Coordinator snapshot commit + independent validation/red team)
  → /review-evidence EXP-...
  → (knowledge-promotion gate: proven results → /curate-knowledge KN-FIND;
     every decision fills knowledge_promotion or says why not)
  → (Coordinator ledger commit + verified decision)
  → (decision drives next iteration)
```
