# `coordination/bus/` — inter-session message store

Write-once messages between agent sessions running in separate chats,
worktrees, containers, or runtimes. Managed entirely by
`tools/agent_bus.py`; the contract is `docs/inter-agent-messaging.md`.

**Do not hand-edit anything here.** Records are write-once, exactly as ledger
records are: a correction supersedes by referencing, it never overwrites.

```text
messages/MSG-YYYYMMDD-<6hex>.yaml   write-once   one message
receipts/MSG-...--<addr>.yaml       write-once   one (message, reader) handled
sessions/<addr>.yaml                current      presence; one writer per path
```

One file per fact, named by a random token drawn without scanning state — same
discipline as `tools/allocate_id.py`. A shared mailbox file would conflict on
every concurrent send where there is no semantic conflict at all, which is what
took `knowledge/INDEX.md` and the dispatch plans out of git. These cannot
conflict: no two writers ever choose the same name.

Read state is derived from `receipts/`, never written back into a message, so a
broadcast is acked per reader and one reader cannot hide it from another.

## This is coordination traffic, not evidence

`validate_ledger.py` does not know about these files and nothing here is a
research record. A message may point at ledger state with `refs:`; the state
itself always lives in `ledger/`, `experiments/`, and `knowledge/`. No claim
becomes true by appearing in an inbox, and no experiment is approved by one.

Tracked in git on purpose — that is how a message reaches a session in another
container.

## Quick reference

```sh
python3 tools/agent_bus.py register --as executor --role executor
python3 tools/agent_bus.py inbox --as executor
python3 tools/agent_bus.py sync --push
```
