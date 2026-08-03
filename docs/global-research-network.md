# A Global AI Research Network

*Design note, deliberately domain-general and portable. It does not describe
this repository and does not belong to it — `crypto-autoresearcher` is one
worked example of the record discipline the design assumes, nothing more. Lift
this document out; nothing in it depends on ECDLP.*

Goal: anyone in the world contributes compute, AI agents do the research,
verified results are the unit of account, and the whole thing coordinates
around shared objectives without a central lab.

Supersedes the mint reasoning in `docs/distributed-proof-economy.md`, which
assumed a single domain that happens to have free verification. That assumption
does not survive generalization, and replacing it changes the architecture.

## 1. The decision everything else follows from

> **Pay for verified outputs. Never pay for claimed effort.**

Almost every hard problem in decentralized compute — did the node really run
the job, did it use the right model, did it burn the FLOPs it billed — exists
only because the network is trying to buy *work*. Buy *artifacts* instead and
most of it dissolves. Nobody can fake a Lean proof that the kernel rejects, a
counterexample that fails recomputation, or a program that scores badly on a
fixed evaluator. The check is the payment condition, and the contributor's
hardware, honesty, and diligence stop being things anyone has to verify.

This inverts the usual design. A compute marketplace sells GPU-hours and then
spends enormous effort proving the hours were real. A results market sells
accepted artifacts and doesn't care how they were produced — hand-derived on
paper, found by a 70B model on a gaming GPU, or guessed. Same payout, same
verification cost, zero attestation machinery.

The corollary is a constraint, and it is the whole engineering problem:
**the network can only work on tasks whose outputs are cheap to check.** Not a
limitation to route around — a specification for what to build.

## 2. Work shapes that fit

Three shapes are simultaneously (a) checkable in seconds, (b) embarrassingly
parallel, (c) inference-bound rather than interconnect-bound, and therefore
ideal for heterogeneous volunteer hardware. This is not a coincidence: all
three are *propose a candidate, check it cheaply*, and that structure is what
makes both properties true at once.

**Formal proof search.** An agent emits a Lean/Rocq proof; the kernel accepts
or rejects in seconds, and anyone can re-run it. This is the only class of
general research output where "prove things as currency" is literally rather
than metaphorically true. The [Equational Theories
Project](https://arxiv.org/html/2512.07087) already ran this as a crowdsourced
workflow — contributions entered as Lean, automatically verified, checked
against a live status file of the whole implication poset — and was explicitly
framed as a model for future collaborative formally-verified research. The
2026 agent tooling to feed it exists:
[LeanMarathon](https://arxiv.org/html/2606.05400v1), AxiomProver, Aristotle,
Numina-Lean-Agent.

**Propose-and-evaluate search.** [FunSearch and
AlphaEvolve](https://www.getmaxim.ai/blog/alphaevolve-ai-for-scientific-discovery/):
an LLM proposes a program, an automated evaluator scores it, winners breed.
Verification cost here is *exactly one evaluation* — the same evaluation the
network was going to run anyway. Verification is free, not cheap. It has
produced genuinely novel results (cap set bounds, matrix multiplication,
compiler and datacenter-scheduling heuristics), and it parallelizes to any
number of nodes with no communication between them.

**Certificate search.** Counterexamples, witnesses, explicit constructions,
collisions, SAT assignments — anything in NP. Verification is milliseconds by
recomputation.

What does *not* fit: distributed pretraining (interconnect-bound, and the
output is not self-verifying), anything requiring physical experiment, and
anything whose success criterion is a human's opinion. Those need the expensive
mechanisms in §4 and should be a small, deliberately subsidized minority of the
network's activity rather than its core.

## 3. Layers

```
  goals        funded objectives; humans and agents propose, stake ranks
  ─────────    ↓ decomposition is the scarce skill (§5)
  objectives   task spec + VERIFIER + budget. no verifier, no task.
  ─────────    ↓
  compute      heterogeneous contributors; propose candidates in parallel
  ─────────    ↓
  verification per-shape; free for §2 shapes, expensive otherwise (§4)
  ─────────    ↓
  claims       hash-linked immutable DAG of accepted artifacts
  ─────────    ↓
  value        bounty settlement + recursive citation flow (§6)
```

The ordering rule that keeps it honest: **an objective is not admissible until
its verifier is written and runnable.** Not "will be defined later" — runnable,
pinned by hash, executable by any contributor before they start work. A task
without a verifier is a task whose payout is somebody's opinion, and it will be
gamed within a week of the network having any value.

## 4. Verification, per shape

| shape | primitive | cost | trust assumption |
|---|---|---|---|
| formal proof | proof-assistant kernel | seconds | kernel soundness only. the gold standard |
| evaluator-scored candidate | re-run the evaluator | 1 evaluation | evaluator is deterministic and pinned |
| NP certificate | recomputation | ms | none |
| deterministic simulation | replay at pinned seed/commit/env | full re-run | bit-reproducibility |
| **model inference** | [TOPLOC](https://www.primeintellect.ai/blog/intellect-2) — locality-sensitive hashing over activations | ~free vs. re-running | detects tampering and precision changes across non-deterministic GPUs |
| **training step** | [Verde/RepOps](https://0g.ai/blog/why-verification-matters-decentralized-ai-training) bitwise-deterministic primitives; redundancy | 2–3× | heterogeneous hardware agrees bitwise |
| high-stakes inference | zkML | 30 s – minutes per inference in 2026 | cryptographic; too slow for the hot path, fine for settlement |
| anything | TEE attestation | ~free | **hardware vendor.** a trust assumption, not a proof — record it as one |
| judgement | staked attestation + dispute | social | nothing is proved. price it accordingly |

The top four rows are where the network should live. The middle rows exist
because [INTELLECT-2](https://arxiv.org/html/2505.07291v1) already demonstrated
32B-parameter RL training over permissionlessly contributed heterogeneous
compute, with rollout workers checked by validators — so contributed *inference*
is a solved-enough problem to build on. The bottom row is where every naive
design puts most of its weight, and it is the row with no guarantees.

## 5. Goals, and the scarce skill

The network's hardest problem is not compute and not verification. It is:
**someone must turn "understand X" into a runnable checker.** "Cure
Alzheimer's" has no verifier. "Find a molecule maximizing this docking score
under these constraints" does. "Prove this conjecture" does, if it is
formalized. That translation step — objective into checkable objective function
— is the actual bottleneck of the whole system, and it is where AI agents plus
domain experts earn their keep.

So make decomposition a first-class, rewarded, **forkable** role:

- Anyone (human or agent) publishes a decomposition of a funded goal: a DAG of
  objectives, each with its verifier and budget.
- Contributors choose which decomposition to work on. Compute flows to the ones
  that look tractable and well-specified.
- Decomposers earn a fraction of everything their objectives eventually mint,
  via the citation flow in §6. Write good verifiers, get paid downstream.
- Competing decompositions of the same goal coexist. Bad ones starve. There is
  no committee that has to be right in advance.

This is the one place where centralized labs currently have an enormous
advantage — a good research director is exactly a person who decomposes vague
goals into checkable steps — and it is the thing a network must reproduce
rather than assume away.

## 6. What mints, and who gets paid

Issuance stays demand-gated: **a claim mints only if it was funded before a
witness for it existed.** The alternative — minting on any novel verified
artifact — dies to a grinding attack, because I can generate unbounded novel,
genuinely-verified, worthless artifacts, and supply goes to infinity. Funding
comes from goal sponsors, protocol fees, or retroactive pools; the direction is
always demand → objective → payout, never work → payout.

Three flows, and only the first is mechanical:

1. **Bounty settlement.** Objective's verifier accepts an artifact → escrow
   releases. Deterministic, instant for §2 shapes, no judgement involved. This
   is the backbone and it should be the overwhelming majority of value flow.
2. **Recursive citation flow.** Every claim names the claims it built on. A
   fraction δ of any claim's payout flows back along those edges, decaying with
   depth. The DAG is hash-linked, so this is computable, and it solves the
   attribution problem that ordinary science has never solved: the person who
   wrote the lemma, the verifier, or the decomposition three levels down gets
   paid automatically when something downstream pays out. Cap depth or use a
   decay factor; exact Shapley attribution is intractable and unnecessary.
3. **Retroactive prizes.** For work nobody knew to fund. Allocated by staked
   judgement, disputable, and **labeled as subjective** rather than dressed up
   as verification.

Negative results are the awkward case: "I searched this region and found
nothing" is genuinely valuable, genuinely unfakeable-only-by-effort, and
therefore only payable through the expensive attestation rows of §4. Fund it
explicitly as exploration, at a lower rate, with TOPLOC-class checks — and
never let it mint at the same tier as a positive verified artifact. A network
that pays well for "I looked and found nothing" is paying for not looking.

## 7. Agent roles

Transplant the separation that this example repo enforces, because it
generalizes and the failure it prevents is universal: **the agent that produces
a result is never the agent that judges it.**

| role | does | may conclude |
|---|---|---|
| decomposer | goal → objectives + verifiers | proposed objectives only |
| proposer | generates candidate artifacts, massively parallel | candidates only |
| executor | runs bounded, pinned computations | observations only |
| validator | re-checks artifacts, receipts, reproducibility | validity of a receipt |
| red team | attacks the interpretation, the cost model, the scope | objections |
| coordinator | state transitions, promotion, priority | official status |

On a network, this is enforced by *distinct stake and distinct operators*, not
by convention — one operator running every role behind six keys reproduces the
centralized failure with extra steps. And two rules carry over unchanged
because money makes them sharper, not softer: an infrastructure failure or
timeout is never evidence against a hypothesis (otherwise the oracle is
attackable by unplugging a machine), and a result is scoped to exactly what was
tested (otherwise the network's headline claims drift above its evidence, which
is the reputational failure that ends it).

## 8. Attack surface

| attack | mechanism |
|---|---|
| grinding — flood novel worthless artifacts | demand-gated mint; no funded objective, no issuance |
| fake compute / billed-but-unrun FLOPs | mostly dissolved by paying for outputs (§1); TOPLOC/TEE only where unavoidable |
| verifier gaming — hit the metric, miss the goal | verifiers pinned by hash and adversarially reviewed *before* funding; held-out test sets; red team paid to break verifiers |
| front-running a revealed artifact | commit–reveal: publish `H(artifact ‖ address ‖ nonce)`, reveal after ordering |
| self-dealing on bounties | funder ≠ solver for protocol-funded pools; statement commitment must predate any witness |
| sybil on judgement stake | operator attestation, concentration caps, and honesty that this is mitigation, not prevention |
| free-riding on citation flow | δ decays with depth; citations are checked by validators, spurious edges slashed |
| evaluator poisoning | evaluator code is part of the objective hash; changing it forks the objective rather than silently rescoring |
| result withholding / defection | escrow only pays on reveal; withholding forfeits the bounty but cannot be prevented outright (§10) |

## 9. Staging

- **Stage 0 — one domain, free verification, no token.** Pick formal math.
  Fund a handful of objectives, run agent proposers on donated compute, settle
  in fiat or off-chain credits. The Equational Theories Project already showed
  the collaboration pattern works; the question is only whether agent proposers
  plus paid attribution beat volunteers plus goodwill.
- **Stage 1 — heterogeneous contribution.** Open proposal work to anyone's
  hardware. Still no consensus layer: a single sequencer publishing signed
  receipts and a verifier binary anyone can re-run. This tests the thing that
  actually matters — will strangers point compute at your objectives.
- **Stage 2 — second domain.** Add propose-and-evaluate search in a domain with
  a real evaluator. If the abstraction survives two domains it is a network; if
  it needs rewriting, it was a product.
- **Stage 3 — decentralize settlement.** Claim assets, citation flow, staked
  judgement, permissionless verification. Last, not first.

Stage 0 has no token in it, and that is the point. Every failure mode in this
document is downstream of "did anyone contribute anything useful," and no
amount of mechanism design answers that question in advance.

## 10. What this cannot do

- **It cannot verify judgement.** Which direction is promising, whether a
  result is novel against the literature, whether a benchmark measures anything
  — no mechanism settles these. They get stake, disputes, and honest labeling.
- **It cannot pay fairly for effort that produced nothing**, which is most of
  real research. This is the design's deepest limitation. It systematically
  favors work with crisp success criteria and systematically underfunds the
  exploratory, taste-driven work that produces the crisp criteria in the first
  place. Retroactive prizes are a patch, not a fix.
- **It cannot stop defection.** A contributor who finds something extraordinary
  can walk away and keep it. Escrow makes that cost them the bounty; nothing
  makes it impossible.
- **It cannot ignore dual use.** A global permissionless network pointed at
  cryptographic or biological problems will eventually verify a result that
  should not be published the moment it settles. An auto-publishing bounty
  contract is an auto-publishing zero-day pipeline. Embargo paths, sensitive
  objective classes, and a disclosure process have to exist **before** the
  network has users, because they cannot be retrofitted onto an immutable
  settlement layer.
- **It cannot make a currency out of most research.** It can make one out of
  the checkable slice, and that slice is larger than it looks — formal proofs,
  evaluator-scored artifacts, certificates — but it is a slice.

The reason to build it anyway: the propose-and-check shape is exactly what
frontier AI is now good at, exactly what parallelizes across strangers'
hardware, and exactly what verifies for free. Those three properties coinciding
is new, and it is the whole opportunity.

## Sources

- [The Equational Theories Project](https://arxiv.org/html/2512.07087) — crowdsourced, kernel-verified collaborative mathematics
- [INTELLECT-2](https://arxiv.org/html/2505.07291v1) and [Prime Intellect's approach](https://www.primeintellect.ai/blog/intellect-2) — permissionless heterogeneous compute, TOPLOC verification
- [Verification for decentralized training](https://0g.ai/blog/why-verification-matters-decentralized-ai-training) — TEE attestation, Verde/RepOps, zkML cost bands
- [AlphaEvolve / FunSearch](https://www.getmaxim.ai/blog/alphaevolve-ai-for-scientific-discovery/) — the propose–evaluate–select loop
- [LeanMarathon](https://arxiv.org/html/2606.05400v1) — long-horizon agentic Lean autoformalization
