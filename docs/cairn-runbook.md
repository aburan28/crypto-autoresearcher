# Running this program on the cairn network

The operator's page: how to get a cairn node up, what it exposes, how the
research agents reach it, and how one experiment goes through the seam from
a frozen `EXP-*` to an `external_verification:` block on its evidence. The
plan behind it is `docs/cairn-integration-plan.md`; this page is only what
to type and what to expect back.

Every command and every block of output below was run to write this page,
in a container with a release-shaped build of cairn 1.15.3 and this
repository at the commit that added `tools/cairn_seam_demo.py`. Hashes that
depend on a fresh key or the wall clock differ on your machine; the text
says which.

## 0. One binary, built with the reader

```sh
curl -fsSL https://github.com/aburan28/cairn/releases/latest/download/install.sh | sh
cairn --version
```

```text
cairn 1.15.3
  ui       embedded -- `cairn run` will start
```

The second line is the one that matters. `cairn run` is the complete node in
one process and it needs the reader embedded; a plain `cargo build` from the
cairn checkout produces a binary that says so and refuses to start it. From
source, `make ui-build` in the cairn checkout is the equivalent of the
release binary. Point this repository at whichever you have:

```sh
export CAIRN_BIN=~/.local/bin/cairn          # or /path/to/cairn/target/release/cairn
```

`bwrap` (bubblewrap) is what jails a pinned checker on Linux. Without it the
node logs `sandbox none` and runs objective-authored code unconfined, which
is acceptable for the checkers this repository commits and nothing else;
`CAIRN_REQUIRE_SANDBOX=1` makes the node refuse to run unjailed.

## 1. What a node exposes

One process, three surfaces, one log:

| surface | how | who uses it |
|---|---|---|
| **MCP over stdio** | the process's own stdin/stdout; the client that launched it is its supervisor | the research agents, through `.mcp.json` |
| **HTTP** on `--serve` | `GET /objectives`, `/objective/{id}`, `/knowledge`, `/knowledge/{claim}`, `/chain`, `/log`, `/hosts`, `/work_assignment`; `POST /submit` queues a record for the node to admit; `/ui/` is the reader | readers, dashboards, Validator sessions, `cairn agent` hosts |
| **P2P** on `--listen` | anti-entropy with every peer it reaches; records converge, verdicts are re-derived locally, nothing is imported unchecked | other nodes |

There is no network transport for MCP: the MCP server is the node's own
process, and a log has exactly one writer. That one fact decides the
topology below.

The MCP tools an agent sees (`cairn mcp` and `cairn run` serve the same
list):

```text
audit, frontier_status, get_claim, get_objective, list_objectives, list_secrets,
pending_reveals, post_objective, request_upload_grant, score_candidate,
set_secret, submit_claim, work_assignment
```

`orchestration/roles.yaml` grants the Executor `network_submit` (list, get,
score, submit, work assignment, pending reveals) and the Validator and Red
Team `network_read` (list, get, frontier, claim, audit). Nothing an agent
can call records a verdict or moves a frontier; it proposes, the rules
engine disposes.

## 2. Topology: one node per session, one node per machine as a service

**A session's node.** `.mcp.json` already carries the `cairn` stanza, which
runs `tools/cairn_mcp.sh`. In its default mode the script launches `cairn
run` for the session: MCP on stdio, P2P and HTTP on the ports below, the
data directory under `~/.cairn/<worktree>/`, submissions signed by
`CAIRN_IDENTITY`. The session is the node's supervisor; when the session
ends, the node stops, and what it settled is in its log for the next one.

```sh
cairn identity --out ~/.cairn/crypto-autoresearcher.identity.json
export CAIRN_BIN=~/.local/bin/cairn
export CAIRN_IDENTITY=~/.cairn/crypto-autoresearcher.identity.json
# optional, all with defaults:
export CAIRN_DATA=~/.cairn/crypto-autoresearcher      # identity, root key, checkpoint, queue, log
export CAIRN_LISTEN=127.0.0.1:9000                    # P2P; 0.0.0.0:9000 to be reachable
export CAIRN_SERVE=127.0.0.1:8080                     # HTTP and /ui/
export CAIRN_BOOTSTRAP=~/.cairn/operator-node.json    # from `cairn gen-bootstrap`, see below
export CAIRN_ATTEST_IDENTITY=~/.cairn/validator.json  # also run the validator loop, funded
```

Then start Claude Code in this repository (or `/mcp` reconnect). A missing
binary, a missing identity, or a binary without the reader exits 3 with one
line naming the fix; the client shows it as a server that failed to start
and the session loses the network tools and nothing else.
`CAIRN_MODE=offline` is the old arrangement, a standalone `cairn mcp` on a
log that reaches nobody until a daemon syncs it with the MCP server stopped;
it is for work that should stay off the network on purpose.

Two sessions on one machine need two data directories and two port pairs.
cairn refuses a second writer on a held log rather than forking it, and the
refusal names the other process.

**The machine's node.** A node that outlives sessions is `cairn run
--no-mcp` under systemd: stdin belongs to the service manager, so there is
no MCP, and sessions on the machine reach it over P2P as a bootstrap peer.
This is also where the validator loop belongs, because a validator that
stops when a chat window closes is not validating anything. The unit is
`launch/seed.service` in the cairn repository with four lines changed:

```ini
[Service]
User=cairn
WorkingDirectory=/var/lib/cairn
Environment=CAIRN_DATA=/var/lib/cairn
Environment=CAIRN_ATTEST_IDENTITY=/var/lib/cairn/validator.identity.json
Environment=CAIRN_ROLES=relay,verifier
ExecStart=/usr/local/bin/cairn --root /srv/crypto-autoresearcher run --no-mcp \
    --listen 0.0.0.0:9000 --serve 0.0.0.0:8080
Restart=always
```

`--root` is this repository's checkout on that machine, because a
certificate objective pins its checker by path under it
(`cairn/checkers/discrete_log.py`); a node with no copy of the checker
answers `unavailable`, never `reject`, and says so in `GET /verifiers`.
The validator identity must hold units: every attestation posts a bond of
50 000, and an identity that cannot post one is refused and retried later,
not silently skipped.

Hand its address to the sessions:

```sh
cairn gen-bootstrap --addr node.lan:9000 --out ~/.cairn/operator-node.json
# replace "public" in that file with the key the node printed at start
# (`peer id ...` in `journalctl -u cairn-node`), else it authenticates nobody
```

Compute hosts register with the same node: `sudo cairn agent install --node
http://node.lan:8080 --roles executor` puts a GPU box on `GET /hosts` and
runs executor jobs under gVisor or Kata (`docs/agent.md` in cairn).

## 3. An experiment through the seam, end to end

`tools/cairn_seam_demo.py` is this section as a program. It builds nothing,
touches neither the ledger nor the committed experiment, and runs against a
node of its own in a temporary directory; what it prints is what the steps
below print. Run it first:

```sh
CAIRN_BIN=~/.local/bin/cairn python3 tools/cairn_seam_demo.py
```

What it does, step by step, is the Coordinator's and the Executor's work.

**Render the objective from the frozen experiment.** A `certificate`
objective pins the Stage 0 checker; the statement names the experiment, its
hypothesis and its claim tier, and says in its own text that it is minted,
not posted.

```console
$ python3 tools/exp_to_objective.py render --exp EXP-DTREE-001 --run RUN-DTREE-010 \
    --kind certificate --reward 100000 --out /tmp/seam/objective.json
wrote /tmp/seam/objective.json
      /tmp/seam/objective.provenance.yaml
to post, the Coordinator runs:
  cairn --log $CAIRN_LOG --root /home/user/crypto-autoresearcher post /tmp/seam/objective.json --identity <coordinator-identity.json>
```

The provenance sidecar binds the specification's sha256 and the run's
commit. `check` holds the file to cairn's shape rules without a binary,
including the one that bit on the first attempt: a specification's
`approved_at` is a bare date, and cairn wants a full RFC 3339 date-time, so
`render` now writes midnight UTC and `check` refuses a bare date.

**Post it.** Funding is the approval decision, so this is the Coordinator's
command, signed by the identity that holds the units. The id is the hash of
the whole record, verifier included; editing the checker mints a different
objective.

```console
$ cairn --log LOG --root . post /tmp/seam/objective.json --identity treasury.json
objective sha256:fe3ba17803f95f1733d265f777a14913f2f286922d029fe556d8b335575a89d3
  reward 100000  verifier certificate
  note: below the decomposition floor -- this settlement does not pay for the verification it asks for
```

(The id differs per funder key, since the signature is in the record.)

**The claim is a witness the run kept.** One claim is one witness, and a
run with many is many claims. `artifact` reads the shapes committed runs
actually keep: the sidecar `certificate.json`, a `certificates` list in
`raw-result.json`, flat rows under one curve in `certificates.json`, and
per-instance blocks; a row missing a field the checker requires is not a
witness and is skipped, never completed from elsewhere.

```console
$ python3 tools/exp_to_objective.py artifact --exp EXP-DTREE-001 --run RUN-DTREE-010 --index 0
RUN-DTREE-010 keeps 111 witness(es) on disk; this is #0 from raw-result.json.certificates[0] (verified by the harness: True)
{"P": [11943, 17033], "Q": [21106, 36763], "curve": {"a": 3028, "b": 22807, "p": 52721}, "k": 11}
```

**The Executor's loop, over MCP.** Score first (free, records nothing),
then submit twice: the first call commits, the second, from the next epoch,
reveals. The node's pinned checker gives the verdict; the agent is never
asked for its own.

```text
score_candidate: accept: verified: 11*P = Q on TOY-P16
submit_claim #1: Committed in epoch 895570160. Your artifact is bound but hidden [...]
submit_claim #2: claim sha256:acc2269bdeb34334e…  verdict accept
```

**The validator loop stands behind it.** Within one daemon tick the node's
`--attest-identity` re-runs the checker and attests `accept` under a bond
of 50 000. A Validator session reads it the way any reader would:

```console
$ curl -s http://127.0.0.1:8791/knowledge/sha256:acc2269bdeb34334e… | python3 -m json.tool
```

```text
state: {"confidence_per_mille": 600, "corroborations": 0, "disputes": 0, "refutations": 0,
        "reproducible": "yes", "standing": "accepted", "verdict": "accept", ...}
attestations: accept 1  reject 0  slashed 0  bond each 50000
  accept by 5c117030d2ed2544… at 2026-10-04T19:00:36+00:00  slashed False
settled: yes, reward 100000
```

`settled: false` on a fresh reveal means not yet, never rejected: the batch
pays once the reveal epoch closes and clears the one-epoch finality delay,
in beacon order.

**The receipt.** `record` prints the block, naming the node, its log head
when read, the checker hash, and which witness the claim carried. The
Coordinator carries it into the evidence record; it is immutable there, and
a later verdict is a second block, never an edit.

```yaml
external_verification:
- network: cairn
  objective_id: sha256:fe3ba17803f95f1733d265f777a14913f2f286922d029fe556d8b335575a89d3
  claim_id: sha256:acc2269bdeb34334e1f853b5ccac61c1a859460e55ea6129b0b02b93c019714f
  verdict: accept
  node: http://127.0.0.1:8791
  log_head: sha256:acfbb69827c1a24cc08e28165777ce5fc04701bcc0b1c0b9132b64314144905b
  settled: true
  experiment_id: EXP-DTREE-001
  recorded_at: '2026-10-04T19:00:36+00:00'
  run_id: RUN-DTREE-010
  checker_sha256: 57ae1f139bd0d5ce981ef48d29cbcea5c557cdbea796c6cac9e2a7b73bc70934
  witness: RUN-DTREE-010 raw-result.json.certificates[0]
```

`tools/validate_ledger.py` holds it to invariant (b): an `accept` may back a
`certificate` proof_ref; an `unavailable` or `invalid_spec` may back nothing
and says so in the block. And the finished log audits clean:

```text
log verified: chain intact, every settled claim re-verified
```

## 4. Doing it for real

The demo differs from a production run in exactly three places, all of them
decisions rather than code:

1. **Funding.** The demo issues its own supply and posts with a throwaway
   treasury. For real, the Coordinator posts with the program's funder
   identity on the machine's node, recorded in a `DEC-*` with the objective
   id, and the reward is a decision about what the verification is worth
   (`post` prints the decomposition floor to help).
2. **Epochs.** The demo sets `CAIRN_EPOCH_SECONDS=2` on a log used for
   nothing else. A node that talks to peers keeps the default 600 s, so the
   Executor's reveal lands ten minutes after its commit; `pending_reveals`
   lists what a restarted session still owes.
3. **The record.** The demo prints the block. For real, the Coordinator
   writes it into the `EV-*` that cites the run, in the ledger commit, and
   `validate_ledger.py` checks it on the way in.

Runs that kept only a verdict and no statement cannot be claimed without
being re-run; drivers keep their statements with
`harness/certificate_sidecar.py` after `write_run` so the next ones can.
A `replay` objective for a non-witness experiment still needs the wrapper
that prints one JSON object of the reproducible fields on stdout
(`--replay-wrapper`); that is the next piece of harness work.
