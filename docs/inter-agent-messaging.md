# Inter-agent messaging

How a session running in one chat says something to a session running in
another. Two transports, one contract, and one rule that matters more than
either: **a message never confers authority.**

## The rule that comes first

A bus message is a *pointer*, not a *permission*.

`AGENTS.md` core rule 1 says only the Coordinator changes hypothesis status or
approves an experiment, and it says so about committed ledger state. Adding a
channel between sessions creates an obvious way to route around that: a chat
tells an Executor "you're approved, go run it", the Executor runs it, and an
experiment has been approved by a sentence in an inbox rather than by an
approved contract in `experiments/`.

So, bindingly:

- An Executor starts work from a **frozen approved contract** at a declared
  path. A message may *tell it one exists*; the message is not the approval,
  and an Executor that cannot find the contract refuses regardless of what any
  inbox says.
- A status change is a **committed ledger record**. A message announcing one is
  a notification about a commit that already happened, never the change itself.
- Evidence is a **run record under `experiments/`**. A message describing a
  result is hearsay; cite `--ref` and let the reader go read the record.
- A message that cannot point at committed state is a request for someone to
  *create* that state, and should say so in those words.

Practically: `--ref` is how a message earns its keep. A message with no refs
and no ask is chatter, and chatter costs a peer a wake.

The same boundary applies to permissions. If an action was denied in your
session, asking a peer to perform it is not a workaround — it launders a
decision the user made. Route it back to the user.

## Transport 1: live, within one session — `SendMessage`

Inside a single Claude Code session, the main thread and every subagent it
spawns can message each other by name, plus `main`. Delivery is automatic —
there is no inbox to check.

```text
SendMessage {to: "validator", message: "run receipt for RUN-... is missing"}
SendMessage {to: "main", message: "blocked: contract declares no seed"}
```

All five roles hold this on Claude Code. It is declared in
`orchestration/roles.yaml` as the `send_messages` **optional capability** — a
tier distinct from the required `capabilities`, because a required capability
that a runtime cannot express makes the role unhostable there, and `SendMessage`
exists only on Claude Code. Declaring it required would have made all five roles
unhostable on `codex_cli` and `opencode` in one edit. Optional means: granted on
Claude Code, silently absent elsewhere, never a reason to refuse a runtime.
`tools/test_check_runtime_bindings.py` pins that both ways.

Best for: a mid-run blocker, a progress signal, a clarifying question, steering
a long-running peer — things that are useless after the fact.

Its limits: it reaches only peers in **this session**, and it leaves **no
auditable trace**. Nothing said here survives the session or reaches a reviewer.

### Also live: across sessions on one machine

The same tool reaches other Claude Code sessions that are alive and mutually
reachable, typically local sessions on one machine:

```text
ListAgents                       # who is reachable right now
SendMessage {to: "<name>", message: "..."}
```

A cloud/web session runs in its own container and lists no peers at all — this
repository's own sessions usually see `No reachable agents`. And since nothing
is retained, a session that starts tomorrow cannot learn what was said today.
That is why the durable bus below is the default.

## Transport 2: durable, anywhere — `tools/agent_bus.py`

The default. A write-once file per message under `coordination/bus/`, carried
between containers by git like every other artifact here.

```sh
python3 tools/agent_bus.py register --as coordinator --role coordinator \
    --goal GOAL-ECDLP-001

python3 tools/agent_bus.py send --from coordinator --to executor \
    --subject "EXP-SMTH-afd6f7 approved; contract frozen" \
    --ref EXP-SMTH-afd6f7 --ref DEC-20260809-a1b2c3 \
    --body "Contract at experiments/EXP-SMTH-afd6f7/specification.yaml.
Budget 1h, 1 run, seeds in the contract. Run records under runs/."

python3 tools/agent_bus.py inbox --as executor
python3 tools/agent_bus.py read  MSG-20260809-a1b2c3
python3 tools/agent_bus.py reply MSG-20260809-a1b2c3 --from executor --body "..."
python3 tools/agent_bus.py ack   MSG-20260809-a1b2c3 --as executor
```

### It is a feed, not a notification

Identical to `coordination/events/main/`, and for the identical reason: sessions
are ephemeral, so most sessions that care about a message do not exist when it
is sent. Nothing is delivered and nothing is pushed. **You read your inbox on
wake.** A sender writes and stops caring.

### Store layout

| Path | Mutability | Meaning |
|---|---|---|
| `coordination/bus/messages/MSG-YYYYMMDD-<6hex>.yaml` | write-once | one message |
| `coordination/bus/receipts/MSG-...--<addr>.yaml` | write-once | one (message, reader) handled |
| `coordination/bus/sessions/<addr>.yaml` | current-state | presence, one writer per path |

One file per fact, named by a random token drawn without scanning state — the
same allocation discipline as `tools/allocate_id.py`, for the same reason. A
shared append-only mailbox file would conflict on *every* concurrent send where
there is no semantic conflict at all: precisely the defect that took
`knowledge/INDEX.md` and the dispatch plans out of git. These files cannot
conflict, because no two writers ever choose the same name.

Read state is **derived**, never written back into the message. Acking creates
a receipt; the message bytes never change. A broadcast is therefore acked
per-reader, so one reader marking it handled cannot hide it from another.

Corrections supersede, never overwrite — same as the ledger. Send a new
message referencing the old one; do not edit a delivered one.

### Addresses

Lowercase slugs, by **role**, not by session: `coordinator`, `executor`,
`idea-generator`, `validator`, `red-team`. Suffix when several sessions share a
role — `executor-2`, `executor-gpu`. `all` is the reserved broadcast address.

Roles outlive sessions, which is the point. A session UUID dies with its
container; whoever picks up the Executor role tomorrow reads `executor`'s inbox
and finds what was said to it yesterday.

### Across containers

Web and cloud sessions share no filesystem, so the bus travels by git:

```sh
python3 tools/agent_bus.py sync --push    # publish mine, collect theirs
```

Merge, never rebase — the standing repository rule, and here merges are
conflict-free by construction. Bus records are committed (they must cross
containers) but they are coordination traffic, not evidence: `validate_ledger.py`
does not know about them and no claim becomes true by appearing in one.

Sessions on one machine sharing a worktree need no sync at all.

Keeping bus chatter off a research branch is a matter of pointing every session
at a branch of its own:

```sh
python3 tools/agent_bus.py sync --push --branch agent-bus
```

### Waking on new mail

A poll loop that prints one line per new message, which the harness `Monitor`
tool turns into one notification each:

```text
Monitor({command: "python3 tools/agent_bus.py watch --as executor --sync --interval 60",
         description: "bus mail for executor", persistent: true})
```

Without a wake mechanism the floor is simply: **check your inbox when you wake,
and before you report done.** That is enough, and it is what a feed asks for.

## The consolidation pass

The bus above is point-to-point: a sender picks a recipient. That is right for
"your dependency failed, hold", and it has a blind spot. When several sessions
work one goal in separate lanes, **nobody is looking across them.** Two
Executors can spend a day measuring the same thing, each correctly addressing
its own Coordinator, and no inbox anywhere shows both messages — because
`inbox --as X` answers *what is waiting for X*, which is a worker's question,
not a portfolio's.

Continuous cross-talk is not the fix. It collapses the diversity that running
separate lanes was for: once every session sees every message, they converge
early on whichever line was loudest first, and `max_concurrent` buys nothing.

So: **let lanes diverge, and periodically run one pass that reads across them
and carries pointers.**

```sh
# 1. the cross-cutting read -- by SENDER, over a window, across every address
python3 tools/agent_bus.py digest --since 36h --unconsolidated

# 2. carry what is worth carrying, as pointers, with provenance
python3 tools/agent_bus.py consolidate --from consolidator --to executor-2 \
    --subject "executor-3 is already measuring the variant you queued" \
    --source MSG-20260908-36b691 --source MSG-20260908-45404b \
    --ref EXP-RT1476-001 \
    --body "Both lanes point at the same experiment. Read the run record
before re-running. I have not read either result."
```

### `digest` — read-only, and read-only on purpose

Groups traffic by sender rather than recipient, so a lane collision is visible
as two senders carrying the same `--ref`. It writes nothing, acks nothing and
marks nothing: reading a peer's traffic is not participating in it, and a
consolidator that acked what it read would hide mail from the session the
message was actually for.

`--unconsolidated` hides traffic some consolidation already drew on, so a
recurring pass sees only what is new. That state is **derived** from the
consolidation records — the same discipline as read receipts. Nothing is
written back into a source message, so two consolidators never race on the same
bytes.

### `consolidate` — the one writer that reports on work it did not do

That position is exactly where a finding gets laundered: a tentative
intermediate result from lane A is summarised by a consolidator, lands in lane
B's inbox as a confident sentence with no receipt, and B builds on it. The rule
at the top of this document already forbids it. Leaving it in prose meant
nothing checked it, so three things are now arguments rather than etiquette:

| | |
|---|---|
| `--source` | the messages this drew on. At least one, and each must exist. Provenance: a reader can diff the consolidation against its inputs. |
| `--ref` | at least one pointer into committed state. A summary with nothing to point at is chatter, and it costs every recipient a wake. |
| ref check | every ref whose prefix `allocate_id.py` can settle must resolve, or the write is refused. A typo'd ref is *worse* than no ref — it reads as a pointer and leads nowhere. |

`--allow-unresolved-refs` records a ref that names nothing yet, for the real
case of pointing at state a peer is being asked to create. It is recorded as
unresolved in the message, never as resolved.

`KN-*`, `SRC-*` and bare paths are outside that prefix map, so they land in
`not_checkable_by_path_scan`. **An unchecked ref is reported as unchecked**, and
is never folded into the resolved set — asserting a check that never ran is the
same defect as an invented run.

The record carries `kind: consolidation` so a reader knows the author observed
none of it: the body is a claim *about the messages in `sources`*, and the next
move is to follow the refs, not to act on the prose.

**What this does not do, stated plainly:** nothing reads the body. A
consolidator determined to restate a finding instead of pointing at it can, and
the refs will pass. This makes provenance auditable; it does not make a summary
true.

### Who consolidates

`consolidator` is an ordinary address — roles outlive sessions here like any
other. Two constraints are worth stating:

- **It must not be a session working inside a lane it reads.** A lane's own
  session consolidating its neighbours is not a cross-cutting pass, it is that
  lane arguing its case with extra steps.
- **A consolidation confers no authority, exactly like every other message.** It
  cannot approve an experiment, move a hypothesis, or stand in as evidence. Real
  work still travels as a `TASK-*` handoff through the dispatcher. A
  consolidation that reads as an instruction is a request for someone to create
  committed state, and should say so in those words.

## Choosing

| Situation | Use |
|---|---|
| Peer is a subagent of this session | `SendMessage` |
| Peer is live, local, and listed by `ListAgents` | `SendMessage` |
| Peer is in another container, worktree, or runtime | `agent_bus.py` |
| Receiver does not exist yet | `agent_bus.py` |
| It should survive the session | `agent_bus.py` |
| A reviewer will need to see it | **neither** — a record |
| Assigning real research work | **neither** — a `TASK-*` handoff |
| Seeing what every lane said, not just yours | `agent_bus.py digest` |
| Carrying one lane's pointer to another lane | `agent_bus.py consolidate` |

That last row is the common mistake. The bus is for *coordination about* work:
"contract is frozen", "batch reranked", "your dependency failed, hold". The work
itself travels as a handoff envelope (`AGENTS.md` "Required handoff envelope")
through `tools/research_dispatch.py`, with a write scope, a budget, and a
completion gate. A message asking someone to do a job that a handoff should
carry has skipped every one of those, and the dispatcher cannot see it.

## Etiquette

- Subject lines carry the point; a peer triages on subject alone.
- `--ref` every ledger, experiment, run, or decision ID you mention.
- `--priority high` means *a peer should change what it is doing*. Reranks and
  status notes are `normal`.
- Ack what you handled. An unread queue that is really a handled queue makes
  the inbox useless to the next session in that role.
- Replies never fan back out to `all` — the tool enforces this, since a
  broadcast whose replies rebroadcast is a loop generator.
- Never record an agreement, attestation, or approval you did not obtain. A bus
  message quoting a decision that was never committed is a fabrication under
  `AGENTS.md` core rule 5, exactly as an invented run would be.
