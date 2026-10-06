# Measured bounds and frontiers

How a claim about what an algorithm *costs* enters this program's ledger, how
a frontier of such claims is kept honest, and how someone is told "beat this"
in a form the harness can judge.

The measuring instrument lives in the crypto repository:
[`docs/bounds/README.md`](https://github.com/aburan28/crypto/blob/main/docs/bounds/README.md)
defines four sealed records — **bound** (`ECBND1h…`), **frontier**
(`ECFR1h…`), **challenge** (`ECCH1h…`), **verdict** (`ECVD1h…`) — and the
`ecbench bound`, `frontier` and `challenge` commands that produce them from
audited sessions. This page is the other half: what this program does with
them. It grants no new authority. AGENTS.md rules 1 to 6 bind unchanged, and
the claim-tier and certificate rules of `docs/claims-and-verification.md`
apply to a bound exactly as to any other evidence.

## 1. What a bound is here

A bound is **evidence about cost**, scoped: one method configuration, one
problem, one curve family, one target kind, one unit, one tier, named sizes,
named sessions. It states the constant at the declared exponent (`S = gae /
√r`, as a ratio to the generic floor `√(π / 2A)`), the exponent fitted across
sizes (`gae = C · r^α`), both with two-stage bootstrap intervals, the share and
exponent of every phase, the memory stored, and the work counted but not
priced. It is re-derivable: the measuring harness fits it again from the
sessions it names and requires the same id, and its CI does so on every
change.

Four levels exist for a cost change, and a claim names exactly one:

| level | moves | measured by |
|:--|:--|:--|
| exponent `α` | the algorithmic class | disjoint fitted intervals over ≥ 4 sizes |
| constant `C` | the walk, the automorphisms used, table shape | the paired ratio's interval excluding 1 at fixed `α` |
| primitive weights | field operations per group operation (a cheaper formula) | native counters per group operation, in a unit that charges them |
| machine | cycles per primitive | wall time, instructions; never a bound |

The ecbench unit charges a group addition as one unit whatever its field cost,
so a bound in it is blind to the primitive level by design. "One fewer
squaring" is real and belongs at its level; a record that reports it as a
moved exponent has confused levels, and the Coordinator refuses it as such.

## 2. How a bound enters the ledger

A bound is carried by an **evidence record** (`EV-*`, `type: empirical`) in
its `measured_bound` block (`templates/research-records.md`). The block copies
the figures that decide anything — ids, domain, method, level, the ops ratio
to the floor with its interval, `α` with its interval, sizes, verified runs,
whether the figure is bounded by unpriced work — and names the measuring
repository, the commit and the record's path. The record itself stays in the
measuring repository; the ledger carries the pointer and the figures the
Coordinator reasons from.

Rules the validator enforces (`tools/validate_ledger.py`,
`check_measured_bound`):

1. **The tier is the record's tier.** `claim_tier` equals
   `measured_bound.domain.tier`. A `toy` bound is toy evidence. No block may
   carry a `crypto` tier it did not measure.
2. **Wall time is never a bound.** `domain.unit` names a counted unit; a
   time-like unit is refused.
3. **An exponent needs sizes.** `level: exponent` requires
   `alpha.scaling_claim: true` and at least four sizes; otherwise the bound is
   `constant` and `α` is description.
4. **An inadmissible verdict is never negative evidence** (rule 3). An
   evidence record whose verdict is `inadmissible` has `direction: neutral`;
   the session is a timeout, a spec mismatch or an audit failure, not a
   mathematical observation.
5. **A level is a statement about operations.** `verdict.level_moved` is set
   only when the outcome is `advances` and `ops` is among `advances_on`.
6. **Every id is well-formed** (`ECBND1h`, `ECDOM1h`, `ECCH1h`, `ECVD1h`
   followed by 12 hex), and `improves_on` names bounds.

A bound may bear on a hypothesis about cost (`hypothesis_id` set) or stand as
a frontier record (`hypothesis_id` null, documented per the validator's
`DOCUMENTED_NULL_OK` rule). Either way `strength` follows the usual ladder:
one session is `preliminary`; an independent replay on another host class, or
a second epoch, makes it `replicated`.

## 3. How a frontier moves

A **frontier** lists the bounds of a domain no other bound dominates — on
`ops` and `memory` by default, conservatively (disjoint intervals; ties stand).
It is built from the records and never edited. It moves in one way: a
**challenge** names the incumbent and freezes the curves, targets, rounds and
acceptance rule; a candidate runs the challenge's spec for a fresh epoch
(seeds derived from the challenge's nonce and the epoch, so nothing can be
tuned to the targets); the **verdict** audits the session with every run
replayed, pairs the arms on the same workloads, and decides per axis.

| outcome | what it means here |
|:--|:--|
| `advances` | better on some deciding axis, worse on none; the candidate's bound is written with `improves_on` set. Evidence `supports` a hypothesis that predicted it. |
| `trade` | better on some axis, worse on another (fewer operations, a `√r` table). A new Pareto point. Neither a win nor a loss; recorded as such. |
| `matches` | indistinguishable. A null result, recorded; it `weakens` a hypothesis that predicted an improvement, with `strength` by replication. |
| `regresses` | worse. Recorded. |
| `inadmissible` | not a result: wrong spec, failed audit, too few sizes or runs, an unverified run, or the incumbent's recorded bound disagrees with its own fresh measurement. `direction: neutral`, `strength: inconclusive`. |

**The verdict is evidence; the Coordinator decides.** A `DEC-*` with the
existing vocabulary (`support`, `weaken`, `replicate`, `expand`, …) cites the
evidence record, and the frontier page in the measuring repository is rebuilt
from the records in the same PR that lands the verdict. No verdict changes a
hypothesis status, approves anything, or closes a goal (rule 1; cairn
integration plan invariant (a)).

Knowledge promotion follows `knowledge_promotion` as for any decision: an
`advances` or `trade` at `replicated` strength promotes a `KN-FIND`, and the
finding becomes a row of the known-results map
(`knowledge/frontiers/ecdlp/<area>/KR-*.yaml`, `kind: known_bound`,
`status: measured`) whose `cost` quotes the figure with its interval and tier,
whose `sources` cite the finding, and whose `internal` names the evidence
record with `relation: measured`. The map then answers "what does rho cost
here" before an idea proposes to beat a number nobody measured.

## 4. Sub-algorithms

A method is phases, and both the bound and the verdict carry each phase's
share and paired ratio (`stages`), so a change is attributed to the
sub-algorithm that moved. Cost composes across levels as a sum over phases of
counts times unit weights; a composed figure is **derived**, never measured,
and never enters a frontier or an evidence record as a measurement. It is a
prediction for an end-to-end session in that unit, and that session is what
is recorded. This is the inventor protocol's lossy-projection test applied to
cost: a headline that was not measured end to end is a projection.

## 5. On the network

Each domain's frontier is one **ratchet objective** on cairn (`docs/cairn-
integration-plan.md`, Stage 2), with a pinned evaluator that rescores a bound
record from its own per-size counts and returns an integer: parts per million
of the generic floor achieved, higher being closer to the floor.
`cairn/checkers/bound_frontier_prime_toy.py` is the first, for the prime,
planted, toy domain; `cairn/objectives/bound-frontier-ecdlp-prime-toy.json`
pins it. The checker binds the domain by constants in its own text, so one
objective is one domain and one tier (invariant (d)); a second domain is a
copy with other constants, hence another hash, hence another objective.

What the network verifies is **internal consistency and the rules**: the
record's per-size `S` recomputes from its own `gae` and `r`, the ratio to the
floor from `A`, the pooled figure from the sizes, the tier from the field
sizes, the unit is counted, and the record is admissible. What it cannot
verify in a sandbox is that the sessions exist and replay; that is the
measuring repository's CI (`ecbench bound check`, `ecbench verify
--replay-all`) and an independent runner's receipt, cited by hash in the
record and the evidence. A network accept is therefore a receipt for a
well-formed, self-consistent frontier entry, exactly as strong as that and
no stronger, and it backs no `direction` on its own (invariant (b)).

## 6. Beating a bound, as a task

A handoff that asks an Executor to beat a bound names the challenge file, the
epoch to use, and the registry id of the candidate method; nothing else is
free. The Executor runs the challenge's spec, judges it with `--replay-all`,
and returns the verdict and the receipt; the Validator re-derives the
verdict from the session (`ecbench challenge verdict` is deterministic) and
replays on another host class; the Coordinator writes the evidence record and
the decision. A verdict that says `matches` is as complete a deliverable as
one that says `advances`, and is committed the same way.
