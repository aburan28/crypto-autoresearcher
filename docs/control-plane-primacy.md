# Control-Plane Primacy

More than one agent runtime drives this repository. Claude Code and a Codex
session have co-driven the same worktree, and `orchestration/providers.yaml`
now declares four runtimes that can host the same five roles. That is the
point: AGENTS.md rule 13 requires three pairwise-distinct resolved models to
close a goal, and one runtime cannot supply them.

It also creates a failure this program has already met. Two runtimes reading
the same `AGENTS.md` both conclude they are the Coordinator, both act on rule 7
authority, and the ledger takes two conflicting commits. A worktree found 118
commits behind carried a `GOAL-*` record reading `paused` for a goal that was
active — the record was not wrong when written, it was read from a checkout
that had stopped tracking reality.

This document states which runtime decides, and what the others may do.

## The rule

**One canonical control plane at a time.** The canonical plane is the session
holding Coordinator authority. Today that is Claude Code, per
`orchestration/providers.yaml` → `defaults.runtime`.

The canonical plane alone may:

- change official research state — hypothesis status, experiment approval,
  goal status, evidence strength, decisions;
- make the snapshot and ledger commits of rule 7;
- record a terminal task state and admit successor tasks.

Every other runtime driving this worktree is a **secondary plane**. A secondary
may read anything, may produce artifacts under an assigned `write_scope`, and
may return receipts, reports, and attestations. It may not commit to the
ledger, transition a record, or hand itself work.

This is a statement about *sessions*, not about models. A secondary plane
running a stronger model than the canonical one is still a secondary plane.
Authority follows the role contract, never the model.

## Handing over

Primacy is transferred explicitly or not at all:

1. The canonical plane finishes or parks its batch and commits.
2. It records the handover in the coordination history like any other
   transition — which plane, which goal, from which commit.
3. The new canonical plane fetches, confirms it is at or ahead of that commit,
   and only then acts on Coordinator authority.

Two planes both believing they are canonical is the failure this prevents. If
you cannot tell which one is, none is: stop and re-read the coordination
history before writing anything.

## Staleness

A secondary plane must not infer research state from a checkout it has not
refreshed. Before acting on any `GOAL-*`, `H-*`, or `DEC-*` record:

```bash
git fetch --all --prune
git status -sb          # how far behind is this worktree?
git log --oneline -5 origin/main -- ledger/
```

A goal record saying `paused` in a checkout 118 commits behind is evidence
about the checkout, not about the goal. Records are immutable and superseded
rather than overwritten (rule 2), so a stale read is always a *plausible* read
— which is exactly why it has to be refreshed rather than sanity-checked.

## Runtime bindings

Each runtime binds the same five roles its own way. The bindings are generated
from `orchestration/roles.yaml`, never hand-written:

```bash
python3 tools/generate_runtime_agents.py          # write them
python3 tools/generate_runtime_agents.py --check  # fail on drift (in `make check-harness`)
python3 tools/check_runtime_bindings.py --list    # the resolved table
```

| Runtime | Bindings | Enforcement |
|---|---|---|
| `claude_code` | `.claude/agents/<role>.md` | tool list per subagent; hand-written, checked |
| `codex_cli` | `.codex/agents/<role>.toml` | `sandbox_mode`; shell is always granted |
| `opencode` | `.opencode/agent/<role>.md` | `permission:` denies a tool outright |
| `api_direct` | `agents/<role>.md` | tool surface derived at run time; `write_scope` enforced by the tools |

A binding file grants a tool surface and points at `AGENTS.md` and
`agents/<role>.md`. It never restates the contract — prose cannot drift from a
source it does not duplicate — and it never names a model, because that belongs
to `model-policies.yaml` → `model-bindings.yaml` → `orchestration.adapter`.

**Over-grants.** Codex always exposes a shell, whatever `sandbox_mode` says, so
a Coordinator or Idea Generator running there is restrained by its prompt
rather than by the harness. Codex and OpenCode both put file creation and
modification behind one switch, so the Idea Generator's "may write, may not
edit" contract cannot be expressed on either. These gaps are recorded in
`roles.yaml` (`runtime_grants_always`, `runtime_capability_coupling`), printed
by `--list` as `OVER-GRANT`, and stated in the affected binding itself. Prefer
`opencode` or `api_direct` for a role whose restrictions must be enforced
rather than requested.

## Obtaining a closure quorum

> **The quorum requirement is suspended** (AGENTS.md rule 13). Closure no longer
> waits on this, precisely because of the arithmetic below: one usable backend
> means a quorum is unobtainable, so the rule blocked every closure rather than
> discriminating between them. This section stays because it still describes
> what a *real* quorum would take, and it is the checklist for restoring the
> requirement — set `GOAL_CLOSURE_QUORUM_REQUIRED = True` in
> `tools/validate_ledger.py` once the matrix below reports three distinct
> resolved models. Attestations remain supported and worth gathering
> voluntarily; they are simply no longer a precondition.

Rule 13 needs three CONCUR attestations whose `resolved_model_id` values are
pairwise distinct. Distinctness is on the resolved model, so three policy
aliases falling back to one model is not a quorum — which is what happens when
three subagents in one Claude Code session all run `model: inherit`.

Distinctness is on the model, so **three runtimes are not three models**. Claude
Code and `api_direct` both pointed at `anthropic` resolve to `claude-opus-5`
twice and count once. What produces a quorum is three *backends* that bind the
review policy to three different models; the runtime only decides where the
session runs.

Check what is actually available before planning a closure:

```bash
python3 -m orchestration.adapter matrix
```

As of this writing that command reports one backend — `anthropic` — serving
`review-adversarial` as written, `zai` and `zai-anthropic` serving it only
`DEGR` (GLM's binding ceiling is `high`, the policy floor is `xhigh`), and
`fireworks`, `openai`, `openrouter`, and `local` unbound (`model: null`).

**So a rule-13 quorum is not obtainable today** — which is why the requirement
is suspended rather than merely unmet — and the runtime bindings are
not what stands in the way. The maximum number of distinct resolved models for
the review policy is one without a recorded downgrade, two with one. Reaching
three requires work in `orchestration/model-bindings.yaml`, not here:

1. Bind `review-adversarial` on at least two further backends and probe each
   (`python3 -m orchestration.adapter models --backend <name>`), so
   `provenance` can move off `operator-supplied`.
2. Or raise a binding's `max_reasoning_effort` where the backend genuinely
   supports it, turning a `DEGR` into an `OK`.
3. Or run a review under `degraded_allowed` — which needs a Coordinator
   inference amendment and is recorded as a downgrade, never silent.

What the runtime bindings did remove is the other obstacle: three subagents
inside one Claude Code session all resolve `model: inherit` to the same model,
so they could never have been three attestations however many backends existed.
Each of the runtimes above is a separate process with its own resolution.

Once the matrix shows three, launch one session per backend:

```bash
eval "$(python3 -m orchestration.adapter env --runtime claude_code --backend anthropic \
    --role validator --independent-session)"
```

Then, for each session, in a session independent of the artifact's producer:

- run the review role (`validator` or `red-team`) against the goal's records;
- record the attestation with all six required fields — `role`,
  `requested_policy`, `resolved_model_id`, `independent_session`,
  `reviewed_record_ids`, `verdict`;
- take `resolved_model_id` from what the runtime actually resolved, never from
  the requested policy alias. If they differ, the run manifest's `inference`
  block sets `fallback_used: true` (CLAUDE.md, model policy note).

`tools/validate_ledger.py` (`check_goals`) enforces the rest: three CONCUR, no
DISSENT, pairwise-distinct models, `independent_session: true` throughout. A
single DISSENT blocks closure until a new decision supersedes it.

If three distinct backends are not available, the goal stays `paused` and the
reason is stated. Never record an attestation you did not obtain — rule 5 is
not suspended because a goal is close to done.
