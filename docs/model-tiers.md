# Model tiers: frontier and core reason, the director instructs, the mechanical tier executes

**Implemented 2026-10-17** (owner request: use Mythos, Fable and sometimes
Opus for reasoning; delegate to Sonnet to form the experiment instructions;
Sonnet hands them to Haiku, which launches, measures and returns results with
no reasoning of its own; carry the same classes across OpenAI, GLM, Qwen and
the other backends). Code: `orchestration/model-policies.yaml`
(`model_tiers`, `requires.model_tier`, `director-runbook`),
`orchestration/model-bindings.yaml` (`model_tiers`, `tier_exempt_backends`),
`orchestration/adapter/resolver.py`, `tools/task_card.py`,
`agents/experiment-director.md`. Tests: `tests/test_model_tiers.py`,
`tests/test_task_card.py`. This document changes no approval, no historical
run and no scientific status.

## The four tiers

| tier | does | Anthropic | OpenAI | Z.ai / Fireworks / local |
| --- | --- | --- | --- | --- |
| frontier | decisions the program cannot recover from (claimed break, closure, contradiction); cross-goal synthesis | Mythos 5, Fable 5.1 | GPT-6 Sol, GPT-6.1 Sol | none classified yet |
| core | coordination, approvals, state transitions, adversarial review | Opus 5.5 | GPT-5.6 Sol, GPT-5.6 Terra | GLM 5.2, GLM 5.3, Qwen 3.8 2.4T |
| director | writes the mechanical tier's instructions and assesses its runs; bounded generation gated downstream (ideas, pointers, implementation, audit screening) | Sonnet 5.5 | (served by Terra) | (served by GLM) |
| mechanical | executes a linted task card and relays tool output; computes nothing | Haiku 5.5 | GPT-5.6 Luna | Qwen 3.8 27B |

The model-to-tier table is `model_tiers` in `orchestration/model-bindings.yaml`,
the only file that names vendor models. A tier is a capability class, not a
price: a mechanical-class model at `max` effort is still a mechanical-class
model, which is why tiers are a separate floor from reasoning effort.

## Policies and their floors

| policy | tier floor | Anthropic binding | effort |
| --- | --- | --- | --- |
| `review-breakthrough` | frontier | Fable 5.1 (Mythos on `anthropic-mythos`) | max |
| `research-synthesis` | frontier | Fable 5.1 (Mythos on `anthropic-mythos`) | high |
| `coordinator-orchestration-code`, `coordinator-orchestration` | core | Opus 5.5 (Fable or Mythos on their backends) | high |
| `review-adversarial` | core | Opus 5.5 | xhigh |
| `director-runbook` | director | Sonnet 5.5 | high |
| `executor-implementation`, `research-deep`, `consolidation-routing`, `audit-sweep` | director | Sonnet 5.5 | medium to high |
| `executor-mechanical` | mechanical | Haiku 5.5 | low |

A model at or above the floor may serve a policy (Opus may run a Sonnet
policy); one classified below it is refused like any other unmet requirement,
and only `degraded_allowed` with a Coordinator inference amendment lets it
through, recorded on the resolution. `review-breakthrough` is not degradable,
so it is never served below frontier, and never by a model nobody classified.

An unclassified model (a local overlay, an OpenRouter id) is recorded on the
resolution as `model_tier: null` and is not refused, except on the
non-degradable frontier gate. A local overlay may classify a model the
repository has never seen (`model_tiers:` in the overlay) but may not
reclassify one it has. Backends where one operator-chosen model serves every
policy (`local`, `abliteration`) are listed in `tier_exempt_backends`: their
tier gap is recorded on every resolution (`below_model_tier: true`) instead
of enforced.

Selecting `AUTORESEARCH_BACKEND=anthropic-mythos` (or `anthropic-fable`) puts
coordination and both frontier policies on that model; everything else on
those backends is unbound, so pair them with `anthropic` for the lower tiers.

## The delegation topology

```text
  frontier / core  (Coordinator: Opus 5.5; breakthrough review and synthesis: Fable 5.1 / Mythos)
      │  designs and approves the experiment; approves the runbook sha256 in a DEC-*
      ▼
  director         (experiment-director: Sonnet 5.5, effort high)
      │  compile: runbook.yaml (LINT OK) + task card (CARD OK)
      ▼
  main session     relays `tools/task_card.py prompt <card>` verbatim; adds nothing
      ▼
  mechanical       (executor-mechanical: Haiku 5.5, effort low)
      │  the eight-command runbook procedure; tools/runbook.py writes every record
      ▼
  director         assess: check-relay + session summary -> execution assessment
      ▼
  core             /review-evidence decides what the result means
```

`model_tiers.delegation` in `model-policies.yaml` is the dispatch table:
frontier dispatches core, director and mechanical; core dispatches director
and mechanical; the director and mechanical tiers dispatch nothing. Subagents
never nest (Codex `max_depth = 1`, OpenCode `task: deny`), so the main session
performs every dispatch, and the director never launches Haiku itself: it
writes the card, the main session relays it, and the director reads the
result back in a fresh dispatch.

The upper tiers' work is the design and the decision. The approval of a
runbook's sha256 stays the Coordinator's, because approval is official state;
everything between approval and evidence review runs on the two lower tiers.

## Well-formed instructions: the task card

A Haiku-class executor's characteristic failures are filling an
underspecified step with a guess, reporting a number it did not observe,
retrying until something passes, and miscopying values into a report. The
runbook (`docs/runbook-execution.md`) removes the choices from execution and
makes the record tool-written. The task card removes the choices from the
dispatch itself, and is checked by `tools/task_card.py`:

- `lint`: every field present; the runbook exists, matches the card's
  sha256, lints clean and is `executor_tier: mechanical`; for an `EXP-*`
  card a committed approval decision names that exact sha256; `write_scope`
  covers the session and report directories; every `stop_when` condition
  and note passes the runbook's vagueness lint and carries no unfilled
  `<placeholder>`. A `frozen_command` card (a re-run with no runbook) lists
  argv arrays with no shell syntax, a timeout and success exit codes per
  command, binds every repository file an argv names by sha256, keeps every
  output, stdout, stderr and receipt path inside `write_scope`, refuses
  secrets in `env`, and cites its approval decision; an optional `commit`
  must exist in the repository.
- `run` (frozen-command cards): the tool, not the executor, executes the
  card. It refuses to start unless the card lints, the pinned `commit` is
  `HEAD` and the receipt does not exist yet; then it runs each argv without
  a shell under its timeout, stops at the first failure, writes stdout and
  stderr where the card says, and writes a write-once receipt (exit codes,
  timings, digests, output tails). It prints a summary derived from the
  receipt alone. The executor runs this one command and relays the summary.
- `prompt`: the exact dispatch text, deterministic in the card's bytes. The
  main session relays it unchanged, so the relay can introduce nothing the
  director did not write.
- `check-relay`: after the run, whether every line of the tool's output
  (`status --brief` for a runbook card, the receipt summary for a
  frozen-command card)
  appears, in order and unedited, in what the executor returned, and whether
  `verify` passes. A paraphrased, rounded or reordered report is
  `executor_deviated`, whatever it says, and goes to a Validator.

`templates/mechanical-task-card.yaml` annotates every field;
`examples/runbooks/toy-ecdlp-bsgs/task-card.yaml` is a complete instance.

## One card format in every repository

crypto-autoresearcher, crypto and cryptanalysis each define an
`experiment-director` and an `executor-mechanical`. When a session has more
than one of them checked out, whichever repository's agent answers a dispatch
must accept the card, so all three use this one format: `tools/task_card.py`
is canonical here and copied byte-identical into the siblings (it needs only
PyYAML). `kind: runbook` needs `tools/runbook.py`, which only this repository
has, and is refused elsewhere; the siblings use `kind: frozen_command`.
Change the tool here and copy it; never edit a copy.

## What each tier never does

- **Mechanical**: chooses a value, repairs a runbook, retries outside the
  tool, types a number, or interprets. It refuses instead.
- **Director**: approves, executes a trial, dispatches, edits an approved
  artifact, supplies a value the specification lacks, or interprets. A
  missing value is a `specification_error` for the Coordinator.
- **Core and frontier**: re-derive a frozen design while relaying a card, or
  run trials (`coordinate` never does). Their tokens go to design, approval,
  review and decision.

## Thinking on the mechanical tier

Claude 5 models think adaptively and cannot turn thinking off; `low` is the
floor, so `executor-mechanical` runs Haiku 5.5 at `low` (Claude Code agent
`effort: low`). What makes the tier reason-free is not the effort setting but
the absence of anything to reason about: a card that lints clean leaves no
choice, and a card that does not lint is never relayed.

## Limits

- Tier classification is an operator assertion, like `capabilities`; the
  resolver cannot detect a model classified above its real class.
- The vagueness lint is a word list: a forcing function, not a proof.
- The Sonnet and Haiku bindings stay `operator-supplied` until `python3 -m
  orchestration.adapter doctor --backend anthropic --probe` confirms them.
