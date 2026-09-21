---
id: KN-TECH-d1ad97
type: technique
title: "Multiagent proof-search orchestration - variant partitioning, the reachable-limit probe, consolidation cross-pollination, and their required controls"
tags: [methodology, agentic-harness, multiagent, orchestration, proof-search, variant-partitioning, disproof-symmetry, limit-problem, cross-pollination, consolidation, formalization, controls, untested]
confidence: speculative
complexity: >-
  Not an algorithmic cost claim. A set of candidate orchestration patterns with
  no measured effect in this program; the cost that matters is the concurrency
  cost of running the arms, and the control arm is mandatory.
applicability: >-
  Proof-oriented or disproof-oriented campaigns where the truth value of the
  target is genuinely open, several inequivalent formulations exist, and enough
  concurrent capacity exists to run more than one framing at once. Not
  applicable to measurement or benchmarking experiments, where the protocol is
  already frozen and variant framing would simply be protocol drift.
source_refs: [KN-LIT-aa7970, KN-TECH-080, KN-TECH-056]
added: "2026-09-08"
superseded_by: null
---

## Epistemic status - read this before using anything below

This is the program's abstraction of the orchestration described in
`KN-LIT-aa7970`. That source is an unattributed fragment reporting an outcome
with **no proof artifact, no failure denominator, and no ablation**. It is
therefore evidence that someone believes these patterns worked once. It is not
evidence that they work, and it is not evidence that they caused the reported
outcome rather than accompanying it.

Consequently:

- Nothing here is adopted as protocol. `KN-TECH-080` was adopted on its own
  merits; this record is explicitly weaker and is filed as `speculative`.
- No pattern below may be cited in a decision record as justification on the
  strength of the source. It may be cited as the origin of a hypothesis.
- Any use of these patterns in this program is an experiment about the harness,
  runs under the same rules as any other experiment, and needs the controls in
  the last section before it is believed.

## The patterns

### P1. Variant partitioning across the truth value

Give separate agent groups inequivalent framings of the same open question, and
deliberately include framings whose success would produce a **proof** and
framings whose success would produce a **disproof**, so no group's prior is the
portfolio's prior.

Why it is interesting here: it is a structural implementation of the symmetry
this program already claims to want. `docs/inventor-protocol.md` treats premature
closure as a failure mode symmetric with overclaiming, and AGENTS.md rule 9
forbids steering away from a plausible lead - but both are stated as duties on a
single agent's judgment. Partitioning makes the symmetry a property of the
schedule instead, which does not depend on any agent resisting its own prior.

What it costs: the arms are not independent evidence about each other. A
disproof arm returning nothing is not support for the proof arm; it is an
exhausted budget on one framing, and recording it otherwise would violate rule 3
in spirit (absence of a found construction is not a theorem).

In this repository the natural carrier is a goal with disjoint lanes -
`tools/goal_lanes.py open-lane` per framing - not separate goals, so the framings
share one budget and one ledger head.

### P2. The reachable-limit probe

Before or alongside the hard target, run its degenerate or limiting case as a
separate cheap campaign - the case obtained by deleting the term that makes the
hard problem hard - and treat a resolution there as a **prompt** for the hard
target rather than as a partial result on it.

In the source this is Euler as the zero-viscosity limit of Navier-Stokes, with
the Euler resolution then fed to the Navier-Stokes groups.

The transferable shape is: pick a limit in which one obstruction vanishes, solve
that, and reuse the *structure* of the solution, not its conclusion.

What it costs, and this is the sharp edge: **the limit problem's answer does not
transfer, and the more useful it looks the more dangerous it is.** A construction
that blows up when a dissipative or regularizing term is deleted says nothing
about the problem with the term present - the term is precisely what was being
tested. Any use of this pattern must state, in advance, that the limit result is
being used as a source of technique and never as evidence about the target, and
must name the term whose deletion is doing the work.

### P3. Consolidation cross-pollination

Let groups diverge with no cross-talk, then have a *separate* consolidating pass
read the groups' intermediate results and write follow-up prompts that carry the
most useful fragments across group boundaries - rather than letting the groups
talk continuously.

The claimed benefit is that isolation preserves approach diversity while a
periodic consolidation still moves insight, so the population does not converge
early on one line.

This program has the mechanism already and has not used it this way:
`tools/agent_bus.py` is a write-once feed addressed by role, and
`tools/merge_digest.py` is the periodic read. The gap is not plumbing, it is that
nothing currently plays the consolidator.

Two constraints from this repository's own rules bind any attempt:
`docs/inter-agent-messaging.md` - **a message is a pointer, never a permission**,
so a consolidation pass cannot approve, promote, or stand in as evidence; and the
consolidator is a summarizer, so its output inherits the confidence of the
fragments it carries and must cite their record IDs rather than restating them.

### P4. Concentrate on demonstrated traction, and record what was abandoned

The source reports pulling agents off other Millennium Problems onto
Navier-Stokes once Euler resolved. As scheduling this is unremarkable. As a
*record* it is the part this program cannot copy loosely: AGENTS.md rule 9
requires that any deprioritization record its evidence, budget, test boundary,
remaining uncertainty, and a concrete successor or revisit condition, and rule 10
forbids parking the goal at all. So the pattern is admissible here only in the
form "concentrate effort **and** write the impediment/revisit record for what was
deprioritized" - never as a silent reallocation.

### P5. Separate the formalization pass from the discovery pass

The source runs discovery to a claimed resolution, then hands the result to a
different system for Lean formalization and verification, as a distinct 17-hour
stage.

This is the source's closest analogue to what this program already requires:
`docs/claims-and-verification.md` makes every claimed solve carry a certificate
that the run wrapper re-verifies independently. The pattern adds nothing new to
the rule; it is recorded because it corroborates the separation as an
architecture rather than a formality.

The limit is worth stating because the source does not state it: formalizing a
statement chosen by the same system checks the proof against that statement, not
the statement against the problem. The statement-to-problem link stays human.

## What this record deliberately does not carry over

- **No scaling inference.** "On the order of 10,000 concurrent agents", 88 hours,
  2.7 million messages and ~130 billion output tokens are uncontrolled
  self-reported figures for a different model on a different problem. They do not
  imply that more concurrency helps, that this program's population is too small,
  or that any budget here should change. `CLAUDE.md` unlimits ECC budgets on user
  instruction; nothing in this source bears on that either way.
- **No claim that the patterns caused the outcome.** With no ablation and no
  failure denominator, P1-P5 are confounded with each other, with the mid-run
  model upgrade the source also reports, and with the choice of problem.
- **No mathematical transfer.** Nothing about fluid regularity reaches ECDLP.

## Controls required before believing any of this here

Applying `KN-TECH-080`'s own audits to this record:

1. **Null-object control (from `KN-TECH-056`).** Run the orchestration pattern on
   a question with a **known** answer already in this ledger, and on a question
   known to be out of reach. A pattern that reports traction on the second is
   measuring the harness's willingness to report traction, not the pattern.
2. **Single-arm baseline.** P1 is only interesting if partitioned arms beat one
   arm given the same total budget. Without that comparison, partitioning is
   just a budget split with extra bookkeeping.
3. **Method ceiling.** State what the pattern cannot produce. None of P1-P5
   generates a mathematical idea; they schedule, isolate, and route. If a
   campaign's bottleneck is that no viable idea exists, every pattern here is a
   no-op, and running them will still consume the budget.
4. **Quantifier audit on the claim itself.** "Variant partitioning finds
   resolutions" is an existential dressed as a universal: one reported success on
   one problem. The universal reading is unsupported.
5. **Pre-registered failure criterion.** Fix, before running, what result would
   make the program drop the pattern - otherwise a null outcome will be absorbed
   as "the question was hard", which is exactly the premature-closure failure
   mode `docs/inventor-protocol.md` names.
