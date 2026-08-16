# Powering this program with cairn

*Proposal. Describes work not yet done. Nothing here is a research claim, no
ledger record depends on it, and adopting it is a Coordinator decision that
needs its own `DEC-*` record plus an `AGENTS.md` amendment — this document
grants no authority by existing.*

Target: `aburan28/distributed-researcher` (the `cairn` crate) becomes the
verification and distribution layer under this program, so that every claimed
solve is re-checked by an independent implementation, every measurement-style
experiment carries a mechanical Pareto frontier, and several worktrees can
search one problem without a coordinator dividing the space by hand.

## 1. Why this is not a new design

`docs/distributed-proof-economy.md` and `docs/global-research-network.md` are
already the design. Both were written as speculation. cairn implements the load
-bearing parts of them:

| this program's design note | cairn, today |
|---|---|
| "pay for verified outputs, never claimed effort" (`global-research-network` §1) | `Objective.verifier` is mandatory; no verifier, no objective |
| "an objective is not admissible until its verifier is runnable and pinned by hash" (§3) | `verifier.checker_sha256`; editing a checker **forks the objective id** |
| V0 NP certificate, mintable deterministically (`distributed-proof-economy` §2) | `verifier.kind: certificate` — pinned `check(artifact) -> bool`, sandboxed |
| V2 bounded re-execution, "only the reproducible fields may back an asset" | `verifier.kind: replay` + `reproducible_fields`, which **refuses machine-dependent fields** — a timing cannot be declared reproducible |
| V3 statistical, pre-registered statistic and threshold | `verifier.kind: statistical`, pinned and seeded |
| V4 judgement, permanently unmintable | `Claim.relations` carries **no money**; `cites` pays and `relations` does not, enforced by a test |
| commit–reveal, "not optional" (§5) | `submit_claim` is two calls across an epoch boundary; nonce never leaves the server |
| demand-gated mint, anti-grinding (§3) | issuance bounded by funded objectives; a duplicate artifact verifies and mints zero |
| "tiers are not fungible; laundering toy into crypto is rule 7 by market microstructure" (§4) | not enforced by cairn — **this program must enforce it by posting one objective per tier** (§4 below) |
| tier-0 staging: "verifiable log, no token… most of the actual value" (§9) | `cairn audit`, signed `checkpoint`, `verify --from` |

The gap is not architecture. It is a bridge, five invariants that must survive
crossing it, and an operational answer for concurrent worktrees.

## 2. The architecture in one sentence

**Git holds the research ledger; cairn holds the verified-results ledger; the
bridge is a receipt record, and it only ever points one way at a time.**

```
  ledger/  experiments/  knowledge/        cairn.jsonl
  ── the interpretation ──                 ── the checkable core ──
  RQ / H / EXP / RUN / EV / DEC            Objective / Claim / verdict / settlement
  scoped, superseded, reviewed             append-only, re-derivable by a stranger
        │                                        ▲
        │  mint: an approved EXP contract ───────┘
        │        becomes an Objective (Coordinator only)
        │
        └─ record: an accepted Claim becomes an `external_verification:`
                   block inside a RUN and the EV that cites it
```

Neither side is the other's source of truth. cairn cannot say a hypothesis is
supported; this program cannot tell cairn a witness verified.

## 3. The mapping

| here | cairn | note |
|---|---|---|
| `GOAL-*` id | `Objective.goal` (free-form string) | put the goal id in verbatim |
| approved `EXP-*` contract | one `Objective` per tier | the contract is already frozen and falsifiable — that is what makes it postable |
| falsification criterion | the pinned checker | translating one into the other is the scarce skill (`global-research-network` §5) |
| `certificate.kind: discrete_log` | `certificate` checker, artifact `{k}` | `examples/ecdlp/checkers/nums_dlog.py` is the working shape |
| `certificate.kind: decomposition` | `certificate` checker, artifact `{target, summands}` | **no cairn example covers this**; a checker must be written (§7) |
| run manifest (commit, seed, env, command) | `replay` spec | `reproducible_fields` = the manifest's non-timing fields, exactly |
| integer metrics: solving degree, relation count, rho steps | `evaluator` + `ratchet` | evaluator scores are **integers only** — which is precisely the set of this program's metrics that `distributed-proof-economy` §2 already says may back an asset |
| wall-clock seconds | nothing | cairn refuses it as a reproducible field; this program already refuses it as evidence. Agreement, not coincidence |
| `EV-*` record | a settled `Claim`, cited by the EV | the claim is the checkable core, the EV is the reading of it |
| Validator / Red Team findings | `relations`: `replicates`, `fails_to_replicate`, `refutes`, `narrows`, `supersedes`, `corrects` | pays nothing, which matches their contract: no authority over state |
| `dominated_by` / `sota_delta` (inventor protocol) | `frontier_status` | cairn makes mechanical the Pareto honesty this program asks for by convention |
| dispatcher `write_scope` non-overlap | `work_assignment` | a pure function of public inputs; no coordinator has to divide anything |
| corrections supersede, never overwrite | append-only log; a forked objective id on any checker edit | same discipline, enforced by hashing rather than by review |

## 4. Five invariants that must survive the bridge

Each is already true on one side or both. Each has a specific way of being lost
in the crossing, so each gets a check in `tools/validate_ledger.py`.

**(a) A cairn `accept` is evidence, never authority.** AGENTS.md rule 1: only
the Coordinator changes hypothesis status or approves an experiment. A verdict
is an input to a review, exactly like a run record. The same rule this program
already applies to messages — *a message is a pointer, never a permission* —
applies unchanged to verdicts. *Check:* no state transition may cite a claim id
as its sole basis; a `DEC-*` is still required.

**(b) `unavailable` is never negative evidence.** cairn: "a verifier that could
not run says nothing about the artifact." Here: rule 3, timeouts and infra
failures are never negative mathematical evidence. These are the same sentence
in two repositories, and the bridge is where they get collapsed by a `verdict
!= accept` branch written in a hurry. *Check:* an `external_verification` block
with `verdict: unavailable` may not back any `direction`, and may not appear in
`proof_refs`.

**(c) Self-dealing is the default failure here, not an edge case.** This
program generates its own curves and solves them. Posting an objective built
from an instance it already solved is degenerate — `examples/certicom-ecdlp/README.md`
documents exactly this, having found and fixed it in cairn's own `examples/ecdlp/`.
The fix is theirs and is adopted wholesale: nothing-up-my-sleeve instances
derived by hash from a public seed (`tools/nums.py`), the derivation re-checked
by the checker, and any instance whose answer gets published retired to a test
vector rather than left standing as an objective. *Check:* an objective minted
by this program must declare `seed_derivation` and the checker must re-derive
it; an EV citing a claim against a self-chosen instance is refused.

**(d) Tiers are not fungible.** `claim_tier` is derived mechanically from field
bit size (`toy` ≤ 32, `medium` ≤ 96, `crypto` above). cairn has no concept of
tier, so one objective that accepted both a 32-bit and a 256-bit instance would
launder one into the other at settlement. *Check:* one objective per tier, tier
in the statement and pinned by the checker's own parameter bounds; an EV's
`claim_tier` must equal the tier of every objective it cites.

**(e) Negative results earn nothing, and that is not a defect to route
around.** cairn's threat model #25: failed search pays zero. A large fraction of
this program's output is `obstruction` blocks — measured quantities over a
stated scope — and they are among the most reusable things it produces. They
have no witness, so they cannot be certificates and must not be dressed as
them. Obstructions stay in git. The temptation to invent a "we looked and found
nothing" objective is the one cairn names as paying for not looking.

## 5. Concurrency: the part that will actually break

`CLAUDE.md` describes N worktrees writing shared state, and every rule in it
exists because a writer read state it had no reason to read. cairn has the
matching hazard from the other direction: two writers over one `cairn.jsonl`
fork a hash-linked log, both appending entries claiming the same predecessor.

**cairn enforces this at write time**, which is better than this program's own
concurrency story and better than cairn's own documentation claims (§10).
`Ledger::open_exclusive_with` takes an OS lock and refuses rather than
proceeding — a lock that silently does nothing being worse than no lock,
"because it reads as a guarantee". `cairn-mcp` uses it. Verified: a second
server on a held log exits 2 with

> another process is already writing …. Two writers fork a hash-linked log —
> both would append entries claiming the same predecessor. Stop the other
> process, or give this one its own `--log`

So the failure mode is a loud refusal at startup, not a silent fork found later
by `audit`. The operational rule is unchanged and now cheap to hold:
**the log is never in the repository tree.**

- Path `${CAIRN_LOG:-$HOME/.cairn/$(basename "$worktree").jsonl}`, one per
  worktree, resolved by a wrapper (§7) rather than written into `.mcp.json`,
  which is committed and shared.
- `--root` *is* the repo worktree: checkers are pinned by path and hash, so
  they must be committed source under `cairn/checkers/`. Checkers are source;
  the log is not.
- Reconciliation between worktree logs is `cairn-p2p`, which re-derives every
  imported verdict rather than trusting it — the same posture as this program's
  independent-review requirement, and the reason multiple logs are better than
  one shared file rather than merely tolerable.
- Objectives are committed JSON. Their ids cover their bytes, so an objective
  file and its id are checkable against each other in CI and a drifted checker
  is a forked id, not a silent rescore.

## 6. Stages

Ordered by value per unit of new machinery, which is roughly the reverse of the
order these things are usually built in. Each stage is independently useful and
each has an exit criterion that is a command, not an opinion.

### Stage 0 — cairn as an independent verifier. No objectives, no rewards.

The certificate discipline currently re-verifies a claimed solve "with code
independent of the solver" — a different code path, in the same repository, in
the same language, written by the same program. cairn upgrades that to a
different repository, a different language, a different process, in an OS jail,
with the checker pinned by hash.

- Add `cairn/checkers/` with checkers for the two certificate shapes this
  program emits (`discrete_log`, `decomposition`).
- `harness/runner.py` gains an optional post-certificate hook: after the
  internal check passes, score the same artifact through cairn.
- **A disagreement between the internal verifier and the pinned checker is a
  hard failure** — `invalid_measurement`, run refused. Two implementations
  disagreeing about a witness means one is wrong, and cairn's own
  `scripts/differential.sh` exists for precisely this reading.
- No `.mcp.json` change yet; this is a subprocess call, not an agent tool.

*Exit:* every `certificate: verified: true` run in `experiments/` re-checks
clean through `cairn score`, and one deliberately corrupted witness is refused
by both.

### Stage 1 — approved experiments become objectives; the Executor contributes.

- `.mcp.json` gains the `cairn` stanza (§7). Tool surface goes into
  `orchestration/roles.yaml` as a new capability — **not** into
  `.claude/agents/*.md`, which is generated and checked against it.
- **Authority split, and it falls out of cairn's own tool surface:** minting and
  funding an objective is CLI-only (`cairn post`, `cairn fund`) and belongs to
  the Coordinator, because funding is the approval decision. The MCP server
  exposes no posting tool at all — of its nine tools the only one that writes is
  `submit_claim`, and a test asserts exactly that. The Executor gets
  `score_candidate` (free, records nothing, the inner-loop fitness signal) and
  `submit_claim`. Validator and Red Team get read tools plus the ability to
  author `relations`.
- **Submitters are signed from the start.** `cairn-mcp --identity <key>` signs
  both the commitment and the reveal, and the signing key's public half becomes
  the submitter — so a node's claims are provably its own and nobody else can
  wear the name. Give each role-and-worktree its own identity; an unsigned
  server warns that its submitter "authenticates nothing".
- `/run-experiment` gains: score before claiming, always. `/design-experiment`
  gains: a falsification criterion that cannot be written as a runnable checker
  is a criterion this program should notice it cannot test.

*Exit:* one `EXP-*` runs end to end — objective posted, candidates scored,
claim committed, revealed in a later epoch, settled — and its `EV-*` carries the
receipt, with the Coordinator's `DEC-*` still doing the state transition.

### Stage 2 — progressive objectives and a real frontier.

The measurement work — best known bound, lowest solving degree, fewest relations,
smallest rho constant — is `evaluator` + `ratchet` shaped. Payouts telescope, so
partial progress pays and holding a result back gains nothing.

The reason to want this is not the payouts. It is that `frontier_status`
mechanizes `dominated_by` and `sota_delta`: the inventor protocol asks every
deliverable to state honestly what dominates it, and today that is a discipline
a reviewer has to enforce. Under a ratchet it is refused at submission.

The rule is worth stating exactly, because its error message is narrower than
its behaviour. **On an objective with a `ratchet` block, once a frontier
exists, every reveal must cite the frontier holder — improvement or not.** It is
an admission rule checked at reveal time (a submitter can only cite what was
public when they built, so a frontier that advanced while their commitment was
sealed cannot be held against them). Verified: a *worse* artifact, 10 against a
frontier of 20, revealed with no citation, is refused — though it is refused
with the words "an improvement must cite the frontier it improves on", which is
the rule describing itself too narrowly. **A non-ratchet objective has no
frontier and no citation requirement**, so pass/fail experiment objectives get
none of this; that is a reason to prefer ratchet shapes for measurement work,
not an oversight to work around.

*Exit:* a ratchet objective with at least three claims from at least two
sessions, and a rerank that reads `frontier_status` instead of a hand-maintained
Pareto table.

### Stage 3 — many nodes, one problem.

`work_assignment` is a pure function of public inputs, so N worktrees partition
a search with no coordinator and anyone can recompute a peer's slice. This
replaces a social convention (`write_scope` non-overlap, checked by the
dispatcher at queue time) with arithmetic, for the search-space case only —
write-scope conflict detection on *files* is unaffected and stays.

Run `cairn-p2p` per log. Candidate gossip is opt-in (`--population`); without it
sessions see each other's settled work only.

*Exit:* two worktrees work one objective from disjoint assignments without a
dispatcher entry dividing them, and `audit` verifies both logs.

### Stage 4 — explicitly not planned here.

Goal-closure quorum, staked judgement, retiring `control-plane-primacy.md`.
Recorded so nobody mistakes silence for oversight:

The three-model closure quorum is **suspended** because every policy alias on
this harness falls back to one model. cairn's independent nodes look like a
substitute and are not one. `distributed-proof-economy` §7 already states the
honest version: nothing in a piece of text proves which model produced it, and
an operator running one backend behind three keys collects three attestations
for one correlated judgement. Operator-distinctness is a weaker property than
model-distinctness. If it is ever adopted, it gets renamed to what it is —
weaker and stated beats stronger and false — and it does not by itself restore
`GOAL_CLOSURE_QUORUM_REQUIRED`.

## 7. Work items, by file

**This repository**

- `docs/cairn-integration.md` — this document, promoted to a binding contract by
  a `DEC-*`, with the §4 invariants moved into `AGENTS.md`.
- `cairn/objectives/*.json`, `cairn/checkers/*.py` — committed source. Checker
  paths resolve against `--root`, so they must be in the tree and their hashes
  are their objectives' identity.
- `tools/cairn_bridge.py` — the only module that talks to cairn.
  `mint --exp EXP-*` writes an objective file and prints the `cairn post` line
  **without posting** (cairn's own scaffold draws that boundary deliberately;
  here the funding step is where Coordinator approval happens).
  `record --claim <id>` writes the receipt block. Nothing else crosses.
- `templates/research-records.md`, `schemas/` — an `external_verification:`
  block on Evidence and on the run manifest: `network`, `objective_id`,
  `claim_id`, `verdict`, `checker_sha256`, `node`, `log_head`, `settled`.
  Immutable, superseded not edited, like everything around it.
- `tools/validate_ledger.py` — the four checks in §4 (a, b, c, d).
- `harness/runner.py` — the Stage 0 hook and the disagreement-is-fatal rule.
- `orchestration/roles.yaml` — a `network_submit` capability; per-role tool
  surface; `tools/check_runtime_bindings.py` then regenerates the agent files.
  Runtimes without MCP declare it unsupported and lose only the submit path.
- `tools/cairn_mcp.sh` + `.mcp.json` — cairn wants absolute paths and `.mcp.json`
  is committed and shared across worktrees, so the wrapper resolves
  `git rev-parse --show-toplevel` and the per-worktree log at launch. Same
  reasoning that made the `crypto-kb` stanza use a relative `--directory`.
- `.gitignore` — `cairn.jsonl`, `cairn.pending.json`, and anything else the node
  writes. The log is state, not a generated artifact, and it belongs outside the
  tree entirely (§5).
- `.github/workflows/` — objective ids re-derived from their files; checker
  hashes match their pins; `cairn audit` on the CI node's log.

**distributed-researcher** — small, and all of it is example/checker work rather
than protocol change:

- A `decomposition` certificate checker (factor-base relation: sum the named
  points, compare to the target). This program produces that shape routinely and
  no cairn example covers it.
- A worked `replay`-kind bundle whose `reproducible_fields` are a run manifest's
  fields, as the reference for Stage 1's V2 objectives.
- **`docs/agents.md` "Known limits" is stale in two places, and both mislead in
  the same direction** — they understate what is built, so a reader plans around
  a problem that is already solved. It says the MCP server "does not sign yet";
  `cairn-mcp --identity` signs both halves of a submission and has tests for it.
  It says one-writer-per-log is "unenforced at write time" with "no file lock";
  `Ledger::open_exclusive_with` takes one and `cairn-mcp` calls it. Both cost
  this plan a wrong paragraph before they were checked against the code.

## 8. What this does not buy

- It does not make the research more likely to succeed. It makes a claimed
  success harder to fake, a measurement's frontier mechanical, and a search
  divisible without a coordinator.
- It cannot certify a negative result, and this program's negative results are
  a large part of its value (§4e). They stay in git and mint nothing.
- It does not discharge a heuristic. A conditional claim validated at
  cryptographic scale is still conditional, on a ledger exactly as it is here.
- It adds a Rust toolchain to the harness's build surface, and a second sandbox
  to reason about.
- It does not resolve control-plane primacy, closure quorum, or any V4 question.
  Those are Stage 4 and Stage 4 is not planned.

## 9. What to decide first

Three decisions gate the rest, and only the first blocks Stage 0:

1. **Is Stage 0 worth doing alone?** It is the only stage with no protocol, no
   MCP, no objectives, and no rewards — just a second independent implementation
   checking every witness this program has ever claimed. `distributed-proof-economy`
   §9 argues this is most of the value of "distributed" and needs none of the
   machinery. If the answer is yes, everything after it is optional.
2. **Who funds?** Rewards are integer units on a local node with no external
   demand. Until there is a funder who is not this program, `reward` is a
   priority signal, and the honest thing is to say so in the objectives rather
   than to imply a market that does not exist.
3. **One identity per what?** Signing is not a tradeoff — `cairn-mcp --identity`
   signs, so there is no CLI-versus-MCP choice to make and Stage 1 should sign
   from the first submission. What remains is a naming decision with no default:
   one key per worktree, per role, or per goal. Per-worktree matches
   `work_assignment`, whose `node_id` wants to be stable and to equal the
   submitter.

## 10. What was checked before this was written

Every claim in §1 and §4 was run rather than read, against `decb9b3` built from
source. `cargo test --all-targets`: **1396 passed, 0 failed, 1 ignored.**

| claim | how it was checked | result |
|---|---|---|
| certificate path works | posted `examples/ecdlp`, scored the shipped `k` | `accept: verified: k*G = Q`, checker pinned by sha256 |
| a wrong witness is caught | flipped the last hex digit of `k` | `reject: k*G does not equal the target point Q` |
| `score_candidate` records nothing | same two calls | "Nothing was recorded. This was a local check." |
| replay maps to a run manifest | replay objective over a script printing `{solving_degree, relation_count}` | `accept: replay reproduced 2 declared field(s)` |
| a fabricated measurement is caught | claimed degree 5, script prints 7 | `reject: replay disagrees with the claim` |
| **timings cannot back a claim** | declared `wall_clock_seconds` reproducible | `invalid_spec: machine-dependent fields cannot be reproducible` |
| `unavailable` ≠ `reject` (§4b) | scored a `lean` objective with no Lean on PATH | `unavailable: 'lean' not on PATH` + "Do not treat it as a rejection" |
| editing a checker forks the objective | changed one hex digit of `checker_sha256` | `sha256:26dfd158…` → `sha256:172b6878…` |
| two writers are refused (§5) | second `cairn-mcp` on a held log | exit 2, "another process is already writing" |
| MCP surface is 9 tools, one writer | `tools/list` | the 9 named in §7; `no_tool_can_write_a_verdict_or_move_a_frontier` asserts exactly one |
| MCP signs | `cairn-mcp --help`, `claim.signed_with` | `--identity` present, signs commitment and reveal |
| duplicate earns zero | `scripts/ratchet-demo.sh` | eve's verbatim copy: `accept`, `reward 0`, "does not improve" |
| ratchet telescopes and citation flows | same | 300000 + 400000 + 400000 = pool; alice ends at 442857 > her direct 300000 |
| uncited submission refused | worse artifact, no `--cites`, live frontier | `refused: … must cite the frontier` |
| `audit` re-verifies | same run | "log verified: chain intact, every settled claim re-verified" |
| nothing-up-my-sleeve derivation (§4c) | `tools/nums.py verify` on `nums-50` | 10/10 checks, incl. "G is the hash of its seed" |
| `sealed` is refused | posted `confidentiality: "sealed"` | `requires zero-knowledge verification, which is not implemented` |
| **no `replay` example exists** | every objective kind under `examples/` | 26 certificate, 22 evaluator, 2 lean, 2 statistical, **0 replay** |
| **no factor-base checker exists** | searched for decomposition/summand checkers | only tensor decomposition (matrix-multiply), nothing for ECDLP relations |

The two gaps in §7 are confirmed gaps, and everything Stage 0 and Stage 1 depend
on is confirmed present. One id caveat found the hard way: an objective's id is
the digest of its record, **not** the ledger entry's `hash` field — reading the
wrong one gets "unknown objective". Use `list_objectives`.
