---
name: agent-bus
description: >-
  Send, read, and answer messages between agent sessions running in separate
  chats, worktrees, containers, or runtimes. Use when this session needs to
  tell another session something (a contract is frozen, a batch was reranked,
  a dependency failed), when checking for mail on wake, or when the user asks
  to connect or coordinate chats. Durable and write-once; survives the session.
---

# Agent bus

Durable messaging between sessions. Full contract:
`docs/inter-agent-messaging.md`. Read it before anything non-obvious.

**A message is a pointer, never a permission.** It cannot approve an
experiment, change a hypothesis status, or serve as evidence — those live in
committed ledger state and nowhere else. Cite IDs with `--ref` and let the
reader go read the record.

## On wake, before anything else

```sh
python3 tools/agent_bus.py sync                       # skip if no remote
python3 tools/agent_bus.py inbox --as <your-address>
```

Nothing delivers mail. This is a feed: unread messages sit there until a
session in that role asks. Check again before reporting done.

## Register once per session

```sh
python3 tools/agent_bus.py register --as <addr> --role <role> [--goal GOAL-*]
```

Address by **role**, not by session — `coordinator`, `executor`,
`idea-generator`, `validator`, `red-team`; suffix duplicates (`executor-2`).
Sessions die, roles do not, so the next session in a role inherits its inbox.
If the user has not said which role this session is, ask before registering.

## Send

```sh
python3 tools/agent_bus.py send --from <addr> --to <addr>[,<addr>|all] \
    --subject "<the point, triageable alone>" \
    --ref <ID> [--ref <ID>...] [--priority high] \
    --body "<what changed, where it lives, what you want back>"
```

Then publish, or peers in other containers never see it:

```sh
python3 tools/agent_bus.py sync --push
```

## Read, answer, close out

```sh
python3 tools/agent_bus.py read   <MSG-id>
python3 tools/agent_bus.py thread <MSG-id>
python3 tools/agent_bus.py reply  <MSG-id> --from <addr> --body "..."   # also acks
python3 tools/agent_bus.py ack    <MSG-id> --as <addr>                  # handled, no answer needed
python3 tools/agent_bus.py peers                                        # who is registered
```

Ack what you handled. An inbox where unread no longer means unhandled is worth
nothing to the next session in that role.

## Wake on mail

```text
Monitor({command: "python3 tools/agent_bus.py watch --as <addr> --sync --interval 60",
         description: "bus mail for <addr>", persistent: true})
```

## Do not use this for

- **Assigning research work.** That is a `TASK-*` handoff envelope through
  `tools/research_dispatch.py`, which carries a write scope, budget, and
  completion gate. A message asking for a job skips all three and the
  dispatcher cannot see it.
- **Recording findings.** Evidence is a run record under `experiments/`.
- **Anything blocked in this session.** Asking a peer to run what your
  permissions refused launders the user's decision. Route it back to the user.

## Live peers on one machine

When `ListAgents` shows a reachable peer — local sessions only; cloud sessions
list none — `SendMessage` reaches it directly and instantly. Use it for a
question to a session you can see right now. It leaves no record, so anything
that should outlive the session goes on the bus as well.
