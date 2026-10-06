# Research state through a cairn lab

Every rule in CLAUDE.md "Concurrency" exists because sessions share state
through git. Identifiers minted from one committed snapshot collided at merge
time. Files nobody edited in the same place conflicted. Squash merges orphaned
recorded SHAs. News travelled only as fast as a merge digest. A
[cairn lab](https://github.com/aburan28/cairn/blob/main/docs/lab.md) holds the
same files as a set of signed ops that merge like a CRDT:

- **No server, no merge step.** Replicas reconcile with one command, over a
  shared directory, a bundle file, or cairn's encrypted transport.
- **Concurrent edits stay visible.** Two sessions editing one goal head get
  both versions, kept side by side as `PATH.lab-conflict-<id>`, until
  somebody who saw both writes the resolution. Nothing is silently
  overwritten, and nothing is a textual merge.
- **Write-once records cannot be replaced.** Two different first writes of
  one path stay an open conflict for a human to decide.
- **Every op is signed.** Only members a space admin admitted can write.

The lab does **not** change who may write which record, the schemas,
`tools/validate_ledger.py`, or what counts as official. A lab op is a signed
copy of a file, not a decision. Git remains the record that archive receipts
bind until the Coordinator decides otherwise.

## Set up a machine

```sh
cargo install --git https://github.com/aburan28/cairn   # or set CAIRN_BIN
cairn lab identity --out ~/.cairn/lab.identity.json
export CAIRN_LAB_IDENTITY=~/.cairn/lab.identity.json
tools/lab_sync.py doctor
```

The first machine creates the space and imports the state. The policy comes
from `orchestration/lab.yaml`:

```sh
tools/lab_sync.py init
tools/lab_sync.py push      # the first push signs everything in scope
```

Every other machine clones it, and an admin admits its key:

```sh
cairn lab --lab .cairn-lab clone --space <space-id> --dir /shared/lab   # or --peer, --bundle
cairn lab --lab .cairn-lab admit <their-key> --roles writer            # on an admin's machine
```

## Working

```sh
export CAIRN_LAB_REMOTE=dir:/shared/lab     # or peer:<id>@host:9100
tools/lab_sync.py sync                      # push what changed, pull what others did
tools/lab_sync.py conflicts                 # what two sessions wrote concurrently
```

- **`push`** signs every change in scope since the last checkout. An edit
  supersedes exactly the version this checkout saw. Editing a write-once
  record is refused before anything is signed (exit 2), with the reason; add
  a correction instead.
- **`pull`** reconciles, then writes the space into the working tree. It never
  overwrites a file you changed and have not pushed.
- **Exit codes:** 0 clean; 1 open conflicts; 2 something was refused; 3 this
  machine is not set up (no binary, lab or identity).

`tools/agent_bus.py` messages and `tools/goal_lanes.py` claims and lanes are
write-once files in scope. They therefore reach another session on its next
`pull`, with no merge to `main` in between: `git fetch` stops being the
visibility boundary.

## What is in scope

`orchestration/lab.yaml` is the source of truth:

- **In the lab:** `ledger/`, `coordination/`, `experiments/` and `knowledge/`,
  the research state.
- **In git:** code (`tools/`, `harness/`, `orchestration/`, `agents/`), where
  review and CI already live.
- **Never committed:** generated files (`knowledge/INDEX.md`,
  `dispatch_plan.*`) and everything `.gitignore` already excludes.

Write-once is declared only where the program writes once *by construction*:
bus messages and receipts, event digests, claims, releases, lanes and goal
checkpoints. That set was measured against git history; none of these paths
saw an in-place edit from 2026-08-15 on.

Run directories and `ledger/decisions`, `ledger/evidence` and
`ledger/corrections` are deliberately *not* write-once, although they are
immutable once landed. That immutability is relative to `main`:
`tools/check_run_immutability.py` fails a branch that modifies a run already
on `main`. On a branch they are rewritten as the work proceeds. In that window
run files were re-committed in place 490 times (progress logs, checkpoints and
manifests of in-progress runs), and decisions, evidence and corrections 83, 13
and 5 times.

A path glob cannot tell an in-progress run from a finished one. So in the lab
these are mutable registers: a concurrent edit is a visible conflict, never a
silent overwrite. The landed-record rules stay enforced where they are today,
in CI.

## Agents over MCP

`.mcp.json` registers `cairn-lab`, launched by `tools/lab_mcp.sh`. Its tools:

| tool | what it does |
|---|---|
| `lab_read`, `lab_list`, `lab_write`, `lab_conflicts` | files, with optimistic concurrency: pass the `seen` list `lab_read` returned as `expect` |
| `lab_claim`, `lab_release`, `lab_tasks` | leases on tasks |
| `lab_send`, `lab_inbox`, `lab_ack` | messages to role addresses |
| `lab_envs`, `lab_exec`, `lab_runs` | sandboxed runs, below |

A write against a stale read becomes a visible conflict. Writes are signed by
the machine's identity. `CAIRN_LAB_ADDRESS` names the role (for example
`executor-1`). On a machine that is not set up, the server fails to start
with one line saying what is missing, and nothing else depends on it.

## Running experiments in environments

The GFPN gate package failed with `infrastructure_error` because its host had
no Sage at `/opt/conda-sage/envs/sage/bin/python`, the interpreter the anchor
comparator calls. A lab environment carries that path with it. It is a whole
root filesystem, named in the space by a digest of its tree. `cairn lab exec`
runs a command in it under gVisor, falling back to bubblewrap, with:

- a read-only root and read-only inputs;
- one writable `/out`;
- no network;
- a deadline and memory limits;

and records the receipt and outputs as one signed op.

`orchestration/lab.yaml` lists the environments the program uses, and
`tools/lab_sync.py envs` reports which are imported on this machine. Build them
from cairn's `examples/lab/environments/` (`numtheory`; `sage`, which builds
with or without docker), then name them in the space:

```sh
cairn lab env import sage --dir <built-rootfs> --move
cairn lab exec --env sage --input <lab-path>:/work/script.py -- /opt/conda-sage/envs/sage/bin/python /work/script.py
```

**Measured.** The comparator, `k4a_anchor_system.py`, ran in `sage` under
gVisor in 5.1 s. The four msolve systems it wrote are byte-identical to those
recorded for `RUN-GFPN-f5412a`.

The program's own run wrapper does not call `cairn lab exec` yet. Routing
`harness/` through it changes what a run manifest records, so it is a protocol
change for the Coordinator, not a side effect of this bridge.
