# Distributed Proof Economy

*Design note. Describes a system that does not exist yet. Nothing here is a
research claim, and no ledger record depends on it.*

How to turn this harness into a distributed research lab in which verified
results are the unit of account — and, more importantly, which parts of that
idea survive contact with the verification rules in
`docs/claims-and-verification.md` and which do not.

The short version: **a research token can only be a bounty-settlement token,
never a mining reward.** Everything below is the argument for why, and the
architecture that follows from it.

## 1. What already exists

This repository is a blockchain with one validator. Not by analogy — by
construction:

| chain concept | where it already lives |
|---|---|
| hash-linked append-only log | the git commit DAG; records are superseded, never overwritten (rule 4) |
| state transition predicate | `tools/validate_ledger.py`, `tools/check_run_immutability.py` |
| transaction receipt | run `manifest.yaml`: command, commit, dirty state, env, seeds, resolved model, timings |
| checkpoint / state root | `latest_verified_commit` in each `GOAL-*` record |
| access-list parallel execution | non-overlapping `write_scope` per dispatched task (`docs/dynamic-subagent-dispatch.md`) |
| commit verification | the dispatcher's post-commit verifier: reachable from HEAD, expected parent, exactly the declared paths, recorded hashes preserved |
| attestation quorum | `completion_quorum`, three pairwise-distinct resolved models (AGENTS.md rule 13) |
| **single sequencer** | `docs/control-plane-primacy.md` — one canonical control plane, by convention |

The last row is the only genuinely centralized part, and the doc that defines
it already records the failure it exists to prevent: two runtimes both
believing they hold Coordinator authority, and a worktree 118 commits behind
reporting a goal as `paused` that was active. That is a consensus failure
described in operational language. Going distributed means replacing a social
rule with a mechanical one.

## 2. The verification ladder

A currency is exactly as sound as the cheapest check that mints it. This
program already stratifies its claims; that stratification is the mint schedule.

| tier | claim shape | who can check, and how | mintable |
|---|---|---|---|
| **V0** | NP certificate: a discrete log `k`, a factor-base relation, a counterexample instance, a collision | anyone, in milliseconds, by recomputation | **yes, deterministically** |
| **V1** | machine-checked proof (Lean/Coq/Isabelle kernel) | anyone, seconds to minutes, kernel is the arbiter | **yes, deterministically** |
| **V2** | bounded re-execution: rerun at the pinned commit, seed, and environment | anyone with the compute, hours; deterministic **only on the reproducible fields** | yes, optimistically (§6) |
| **V3** | statistical validation: empirical CDF vs a predicted distribution, tail checks | anyone, by resampling; agreement is probabilistic | only against a pre-registered test statistic and threshold |
| **V4** | judgement: claim tier, evidence strength, novelty vs literature, "is this direction worth pursuing" | nobody, mechanically. ever. | **no** |

V0 is the load-bearing tier, and this domain is unusually lucky to have it:
ECDLP is in NP, so every *positive* result the program can produce is cheaply
and independently verifiable regardless of how it was found. That is already
the stated ceiling of "proof" available here, and `harness/runner.py` already
re-verifies certificates with code independent of the solver.

V2's split matters. A run's relation count, solving degree, and sample
statistics are reproducible; its wall-clock is not. **Only the reproducible
fields may back an asset.** A cost claim denominated in seconds is a claim
about somebody's hardware, and cannot be settled by re-execution.

V4 is where most of the *intellectual* value of research lives, and it is
permanently unmintable. Any design that forgets this produces a token backed by
vibes with a cryptographic veneer. V4 gets stake and slashing (§7), not
issuance.

## 3. The mint rule, and the attack that kills the naive one

The obvious rule — *mint on any novel verified certificate* — is fatal.

I can generate unlimited fresh 40-bit curves, solve each one, and submit the
certificate. Every submission is genuinely novel (the statement hash is new),
genuinely verified (the witness is real), and genuinely worthless. Supply
becomes unbounded and the currency is worth nothing. Call it the **grinding
attack**; it is the reason "proof of useful work" has never shipped as a mint.

The structural problem: Nakamoto consensus needs work that is (i) tunable to
arbitrary difficulty on demand, (ii) bound to the previous block so it cannot
be precomputed, (iii) progress-free, and (iv) trivially verifiable. Useful
research satisfies (iv) at V0 and fails (i), (ii), and (iii). You cannot order
a discrete-log instance of precisely 2.3× last week's difficulty, and you
cannot bind a useful instance to last block's hash without making it an
instance nobody wanted.

So the mint is demand-gated, not novelty-gated:

> A claim mints if and only if a bounty was escrowed against that exact
> statement hash **before** any witness for it existed on-chain, and the
> submitted witness verifies at V0–V2.

Supply is then bounded by what someone was willing to pay to know. That is a
market clearing, not mining. It also means the token has a demand side from day
one, which is the only thing that ever gives one value. Novelty is still
checked — a duplicate certificate mints nothing, and the check is a hash
lookup — but novelty is a *necessary* condition, never a sufficient one.

Unsolicited discovery is the awkward case: the best results are the ones nobody
knew to ask for. Handle it with a **retroactive prize pool** funded from
protocol fees and allocated by the staked judgement layer (§7) — explicitly a
V4 process, explicitly not a mint, explicitly subjective. Do not pretend a
formula can price surprise.

## 4. Layering: the chain does not do research

Three layers, deliberately boring at the bottom.

```
  claim market      bounties, escrows, prizes, reputation, disputes
  ─────────────     ← where research economics happens
  verification      V0/V1 on-chain predicates; V2/V3 optimistic + fraud proofs
  ─────────────     ← where truth is settled
  settlement        any standard BFT/L2 chain. boring on purpose.
```

The settlement layer must not be secured by research work, for the reasons in
§3. It orders transactions and nothing else. The research lab is an
*application*, and the claims are *assets*, not the consensus mechanism. Every
proposal that tries to collapse these layers has failed on difficulty
adjustment.

An asset carries its provenance in its type, mirroring the existing claim-tier
ceiling: a `toy`-tier certificate and a `crypto`-tier certificate are different
assets and are not fungible. The ceiling is enforced by the same predicate that
enforces it in CI today — derived mechanically from the run's field bit size,
not from the claimant's ambition. Fungibility across tiers would launder toy
evidence into cryptographic evidence at the treasury, which is AGENTS.md rule 7
violated by market microstructure.

## 5. Claim lifecycle

```
  post      bounty escrowed against statement hash H(S); deadline; tier required
  commit    solver publishes H(witness ‖ solver_addr ‖ nonce)   ← anti-front-run
  reveal    witness published after the commit is ordered
  verify    V0/V1: on-chain predicate, immediate
            V2/V3: challenge window opens (§6)
  settle    escrow → solver; claim asset minted at its derived tier
  supersede corrections create new claims citing the old; nothing is deleted
```

Commit-reveal is not optional. A plaintext witness in the mempool is stolen by
the first sequencer or verifier who sees it — the solver did the work and
someone else collects. The repo's pre-registration discipline is the same
primitive applied to a different threat.

Failed verification is a *slashable* event for the submitter's bond, and it is
recorded as `invalid_measurement`, not as negative evidence about the
underlying mathematics. This distinction is already load-bearing here and gets
sharper with money attached: **a timeout is not a refutation, a crash is not a
refutation, and neither may move a market.** An oracle that prices
infrastructure failure as mathematical information is an oracle that can be
attacked by unplugging a machine.

## 6. Making expensive verification actually happen

V2 and V3 cost real compute, which creates the **verifier's dilemma**: a
rational verifier who is paid to attest and not paid to check will attest
without checking. A rubber-stamp verifier set is worse than no verifier set,
because it looks like one.

Four mechanisms, used together:

1. **Interactive fraud proofs.** The run manifest already pins commit, seed,
   environment, and command — so the execution is a well-defined deterministic
   trace, and a challenger can bisect it to a single disputed step that the
   chain adjudicates cheaply. This is why the artifact policy in AGENTS.md is a
   prerequisite for the whole design and not bureaucratic overhead.
2. **Canary claims.** The protocol injects known-invalid claims at a low rate.
   Attesting to one is slashed; catching one is rewarded. Verification becomes
   the profitable strategy rather than the altruistic one.
3. **Bonded challenge windows.** V2/V3 claims settle optimistically after a
   window during which any bonded party can dispute. Escrow is not released
   until the window closes.
4. **Sampled re-execution.** n-of-m verifiers drawn unpredictably per claim,
   with escalation to full re-execution on disagreement.

For V3 specifically, the test statistic and rejection threshold must be
registered *with the bounty*, before any data exists. A statistical claim whose
success criterion is chosen after seeing the samples is unfalsifiable, and on
an open market it is straightforwardly exploitable.

## 7. The judgement layer, and the thing that cannot be proved

V4 questions — is this evidence strong, is this direction promising, is this
novel relative to the literature — have no mechanical answer and must never
mint. They get a bonded attestation market: stake to attest, dispute to
challenge, slash on a losing dispute, and route unresolved disputes to human
referees whose selection is itself staked. This is a governance mechanism
wearing a market's clothing, and it should be labeled as such rather than
dressed up as verification.

One honest failure has to be stated plainly. AGENTS.md rule 13 requires three
**pairwise-distinct resolved models** for goal closure, and is explicit that
distinctness on the resolved model — not the requested policy alias — is the
whole point. *You cannot verify that remotely.* Nothing in a piece of text
proves which model produced it, and an operator who runs one backend behind
three keys collects three rewards for one correlated judgement. That is exactly
the failure the rule was written to prevent, now with a financial incentive
behind it.

There are three responses, and no fourth:

- **Hardware attestation** (TEE) binding an inference session to a model
  identity. This is a *trust assumption* about a vendor's silicon, not a proof;
  say so in the record rather than upgrading it to a guarantee.
- **Substitute stake-distinctness and operator-distinctness** for
  model-distinctness, and rename the property honestly. Independent operators
  is a weaker claim than independent models. Weaker and stated beats stronger
  and false.
- **Keep V4 closure off-chain**, with on-chain settlement only for V0–V2.

The repo's existing instinct applies unchanged: if three distinct models cannot
be resolved, the goal does not close, and an unattested closure is worse than
an open goal. Adding money does not relax that; it raises the payoff for
faking it.

## 8. Attack surface

| attack | mechanism |
|---|---|
| grinding — flood cheap novel claims | demand-gated mint (§3); no bounty, no issuance |
| self-dealing — post a bounty you already solved | statement commitment must predate any witness; bounties funded by external demand; solver ≠ funder for protocol-funded pools |
| front-running the witness | commit–reveal (§5) |
| rubber-stamp verification | canaries, fraud proofs, bonds (§6) |
| sybil across judgement stake | operator attestation; stake-weighted with concentration caps; the honest limit in §7 |
| post-hoc statistics | pre-registered test statistic and threshold in the bounty |
| infrastructure-failure oracle attack | failed/timeout runs settle as `invalid_measurement`, never as mathematical evidence |
| tier laundering | tier derived mechanically from run parameters; tiers not fungible (§4) |
| duplicate claim under a different encoding | canonicalized statement serialization before hashing; canonicalization is consensus-critical |
| censorship of a solver's reveal | forced-inclusion path at the settlement layer |

## 9. Staging

Ordered by value delivered per unit of consensus complexity — which is roughly
the reverse of how these projects are usually built.

- **Stage 0 — verifiable log, no token.** Publish a Merkle root over ledger
  records and run manifests per commit; sign checkpoints; ship a `verify`
  binary that replays `validate_ledger.py` plus certificate re-checks against
  any clone of the history. Anyone can now independently confirm every claim
  this lab has made. **This is most of the actual value of "distributed," and
  it needs no chain, no token, and no consensus.** It is also a prerequisite
  for every later stage.
- **Stage 1 — bounty market, off-chain settlement.** Escrowed bounties,
  commit–reveal, a single sequencer publishing signed receipts. Tests whether
  anyone will actually pay for answers, before spending a year on consensus. If
  demand is zero, stop here; the rest of the design is unbacked.
- **Stage 2 — permissionless V0 verification.** On-chain certificate
  predicates, claim assets typed by tier, fraud proofs and challenge windows
  for V2.
- **Stage 3 — staked judgement, primacy retired.** Only now does
  `control-plane-primacy.md` get replaced by a consensus rule instead of a
  convention.

## 10. What this cannot do

- It cannot make unverifiable research verifiable. It sorts claims by how
  checkable they are and prices only the checkable ones; the rest is a market
  in opinions, honestly labeled.
- It cannot certify a **negative** result. A certificate proves a positive
  witness is real; absence of a witness within budget is a scoped negative
  observation and mints nothing. Rewarding "I looked and found nothing" pays
  for not looking.
- It cannot discharge a heuristic. Cryptographic-scale validation of
  Heuristic N still leaves every claim depending on it conditional, on-chain
  exactly as in the ledger. The conditional qualifier is part of the asset's
  type; dropping it in any market view is a claim-tier violation.
- It cannot prove hardness, or any complexity lower bound. Unchanged.
- It cannot fix incentives on V4. It can only make the subjectivity explicit,
  bonded, and disputable — which is strictly better than an unaccountable
  committee and strictly worse than a proof.

The design is worth building for one reason: this domain has cheap independent
verification of positive results, which almost no research field has. That is a
real asset and it is what makes a proof economy conceivable here at all. It is
also narrow, and the discipline of this program is to keep saying so.
