---
id: KN-FIND-a4d4a4
type: internal_finding
title: Gate-tally equality between a counter and a simulator sharing one builder is a Mode-4 non-discriminating decision rule — demonstrated by a mutation that left the tally bit-identical while simulation caught it 16/16
tags: [methodology, controls, nulls, negative-control, mutation, reversible-circuits, resource-estimation, quantum, decision-rules, null-sufficiency]
confidence: preliminary_empirical
evidence_level: toy_measurement
claim_status: internal_finding
authority: internal_analysis
source_refs: [EV-QRE-45dfe1, DEC-20260813-5cef9c, KN-TECH-1a5b7e, KN-TECH-056, GOAL-QRE-001]
internal_refs: [EV-QRE-45dfe1, DEC-20260813-5cef9c]
proof_status: empirical_only
proof_refs: []
added: '2026-08-13'
superseded_by: null
---

## What was found

A resource-counting package built one reversible-circuit description and fed it
to two sinks: a gate counter and a classical simulator. It reported, as a
correctness assurance, that in all 22 full-circuit configurations **the gate
tally recorded while simulating equalled the tally recorded while counting**.

An independent Validator mutated the ripple adder's MAJ loop order inside the
shared builder and re-ran both sinks. The gate tally came back
**bit-identical** — `{x: 640, cnot: 7264, ccx: 3360}`, peak 30 — while the
simulation caught the defect **16 times out of 16**.

So the tally-equality statistic remained true on a provably broken circuit. It
is a decision rule that cannot discriminate, and it had been carried as an
assurance.

## Why this is an instance, not a new technique

This is **Mode 4 of `KN-TECH-1a5b7e`** — "the decision rule that cannot
discriminate" — reached independently in a domain that entry's worked cases do
not cover. `KN-TECH-1a5b7e`'s failures are lattice contrasts; this one is
reversible-circuit resource counting. The entry already prescribes the remedy
(obligation 5: show the rule can return the other answer), and this case is
recorded because a second, structurally different worked instance is what makes
a methodology entry portable.

**Nothing here supersedes `KN-TECH-1a5b7e` and nothing extends it.** The
finding's whole content is the worked instance and the reason the rule is
vacuous, stated below.

## The mechanism, which is what transfers

The tally is a function of the *emitted gate stream's multiset*. The mutation
permuted the **order** of emissions without changing which gates were emitted.
Any defect that is a permutation, a re-association, or a mis-wiring of the same
gate multiset is therefore invisible to the tally by construction — and
mis-wiring is precisely the defect class reversible-circuit builders produce,
because qubit indices are the thing an ancilla allocator gets wrong.

The generalisation: **when a counter and a checker consume the same
description, agreement between them tests the plumbing, not the object.** It
establishes that the two sinks saw the same stream. It cannot establish that
the stream is correct, because both sinks are downstream of the same defect.

What *did* discriminate was an independent semantic check — simulating the
circuit and comparing its output against the function it was supposed to
compute — plus an end-of-circuit global ancilla-cleanliness assertion.

## Scope and limits

- One worked case, one package, one mutation class (loop-order permutation).
  The claim that *all* permutation-class defects are invisible to the tally is
  argued from the multiset construction above, not measured across a defect
  taxonomy.
- The finding says nothing about whether the counts in that package are
  correct. They were separately validated and independently reproduced
  (`EV-QRE-45dfe1`); the point is only that tally equality was not what
  established it.
- The frontmatter reads `confidence: preliminary_empirical` and
  `evidence_level: toy_measurement`, and both are deliberate. The 16/16 figure
  is 16 repetitions of one mutation inside a single Validator session — it is
  not independent replication, and the circuits are small. A second session has
  not reproduced the demonstration. The underlying counts are separately
  `replicated` (`EV-QRE-45dfe1`); this entry's own claim is not.

## Novelty check — DECLARED INCOMPLETE

The retrieval index was **not searched**: `CRYPTO_KB_QDRANT_URL` is `:memory:`
in this process, so `search_knowledge` returns nothing and reports why. Per
`AGENTS.md` "Knowledge retrieval policy", absence of a search result is not
evidence that something was not tried — and an unavailable index is a reason to
say the corpus was not searched, never a licence to assert it is empty. That
distinction is itself recorded in `CORR-20260813-1a06db`, which arose from
failing to make it earlier in the same campaign.

What was done instead: a grep over `knowledge/findings` and
`knowledge/techniques` for "negative control", "tally", "gate count", "counter
and simulator", "bit-identical", "mutation test", "correctness check". That
grep is what surfaced `KN-TECH-1a5b7e`, which this finding is filed under
rather than beside. A full retrieval pass may surface closer prior art, and
this entry should be re-checked when the index is available.

## Provenance

Produced by `GOAL-QRE-001` `BATCH-973b49`: producer `TASK-20260813-c99166`,
Validator `TASK-20260813-13e948` (`VAL-20260814-0646f4`), snapshot commit
`d931391c2`, ledger archive `TASK-20260813-654347`. The mutation was the
Validator's own initiative; it was not requested by the task handoff, which
asked only whether the simulated circuit *is* the counted circuit.
