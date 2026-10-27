# Runtime relay: moving work between Claude Code and Codex

When one runtime's budget runs out (a Claude Code 5-hour or weekly limit, a
Codex usage limit, an API billing stop), the work moves to the other runtime
without losing what only the stopped session knew. `scripts/relay.py` does it;
it is stdlib Python, so the same file works in every checkout and on any host
(`relay.py install <other-checkout>` copies it).

## Rules for every runtime

- **At session start**, if `.resume/HANDOFF.md` is pending (the SessionStart
  hook announces it), run `python3 scripts/relay.py accept` before anything
  else. It checks that the branch and HEAD still match, prints the handoff and
  claims it. Then read `.resume/RESUME.md`, check runs in flight before
  relaunching anything, and do not redo finished steps.
- **Before you stop with work unfinished** (a limit warning, budget low, a
  turn that must end mid-task), run
  `python3 scripts/relay.py out --to <claude|codex> --note "<what the next runtime most needs>"`.
  Keep `.resume/RESUME.md` current as for any checkpoint (AGENTS.md, "Resume
  checkpoints in S3 before every run").
- A handoff is a pointer to the work, not the record: commits, specs and
  results still land in PRs under AGENTS.md.

## What a handoff contains

Three gitignored files under `.resume/`, rebuilt from facts rather than from
the model's memory:

| File | Content |
|---|---|
| `HANDOFF.md` | what the next runtime reads: why the last one stopped, branch, HEAD, upstream, PR, unpushed commits, uncommitted changes, stashes, the last user request and assistant message (excerpts, secrets redacted), the last shell commands, pointers to `RESUME.md` and the newest session log, relay history, a takeover checklist |
| `handoff.json` | the same, machine-readable (`runtime-relay/v1`), with `status` `draft` → `pending` → `accepted` |
| `relay.jsonl` | append-only hops: from, to, reason, HEAD, checkpoint |

`scripts/checkpoint.sh push` carries all three to S3 under `relay/` in the
checkpoint, and `restore` puts them back, so a takeover on another host works:
`scripts/checkpoint.sh restore <repo>/<branch>` then `relay.py accept` in the
restored worktree.

## How it is triggered

| Runtime | Hook | Effect |
|---|---|---|
| Claude Code | `Stop` (every turn) | refresh the draft handoff (local only, fast) |
| Claude Code | `StopFailure` with `error` `rate_limit` or `billing_error` | mark the handoff pending for Codex, push an S3 checkpoint, log the hop |
| Claude Code | `SessionStart` | announce a pending handoff as session context |
| Codex | `Stop` (every turn), `SessionStart` | the same draft and announcement (`.codex/hooks.json`) |

A pending handoff stays pending until it is accepted: no runtime's per-turn
draft overwrites it, the outgoing session's own included; only a new budget
stop replaces it. Codex has no
`StopFailure` equivalent: when Codex runs out, its last per-turn draft is
current, and `relay.py out --runtime codex --to claude` (or the `run` loop)
marks it pending. Codex project hooks need hooks enabled in your Codex
config; `relay.py doctor` reports what is wired.

## Commands

```bash
python3 scripts/relay.py status                 # current handoff
python3 scripts/relay.py out --to codex --note "step 3 of PLAN.md is next"
python3 scripts/relay.py switch --to codex --exec   # out, then start codex here with the takeover prompt
python3 scripts/relay.py accept                 # incoming runtime claims the handoff
python3 scripts/relay.py prompt                 # print the takeover prompt
python3 scripts/relay.py doctor                 # both runtimes wired? CLIs on PATH?
```

Unattended failover, for a task you want finished whichever account has
budget:

```bash
python3 scripts/relay.py run --prefer claude,codex --max-hops 6 --cooldown 900 -- "<task>"
```

It runs the task headless on the first runtime (`claude -p`, `codex exec`),
tees output to `.resume/relay-runs/`, and on a budget stop (the `StopFailure`
hook's pending handoff, or limit text in the output of a non-zero exit) writes
the handoff and starts the next runtime with the takeover prompt plus the
original task. An ordinary failure is returned, not relayed. When every
runtime is out it waits `--cooldown` seconds and tries again, up to
`--max-hops`.

Commands are configurable for permission flags or wrappers:
`RELAY_CLAUDE_CMD` (default `claude -p`), `RELAY_CODEX_CMD` (`codex exec`),
`RELAY_CLAUDE_TUI` (`claude`), `RELAY_CODEX_TUI` (`codex`); `RELAY_BUDGET_RE`
adds limit text to recognise.

## Limits

- Excerpts come from the transcript tail (last 4 MB), are truncated to 2000
  characters and pass a redaction filter (AWS keys, `sk-`/`gh*_`/`xox*`
  tokens, presigned-URL signatures, `token=`-style assignments, long base64
  runs). Treat `HANDOFF.md` like `RESUME.md`: never paste it into a PR.
- The handoff carries no conversation beyond those excerpts; whatever the next
  runtime needs that is not in git, `RESUME.md` or the note is lost. Write the
  note.
- Runs in flight are not detected; they are listed in `RESUME.md`.
