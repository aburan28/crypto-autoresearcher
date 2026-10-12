---
id: KN-OPEN-ed922d
type: open_problem
title: "Can a prime-field ECDLP advantage remain hidden behind a subgroup-preserving correspondence?"
tags: [ecdlp, trapdoor, prime-field, isogeny, jacobian-transfer, endomorphism-ring, conductor, hidden-structure, evidence-gates, open]
confidence: unverified
status: open
claim_status: question
evidence_level: agent_hypothesis
authority: agent_hypothesis
source_refs: [KN-TECH-0f24d0, KN-LIT-7261, KN-LIT-7635, KN-LIT-309, KN-TECH-028]
related_goals: [GOAL-ECTD-001]
archived_by: TASK-20260930-d2607a
added: "2026-09-30"
superseded_by: null
---

## Question

For an ordinary elliptic curve over a prime field with a large prime-order
subgroup, can auxiliary algebraic information provide a substantial,
fully charged ECDLP advantage that is difficult to reconstruct from the public
curve, while preserving that subgroup?

Separate two questions: does a transfer offer a computational advantage, and
can that advantage remain hidden? A correspondence to a structured Jacobian,
an isogeny endpoint, or ring-assisted navigation is only a candidate mechanism
until both questions have evidence. This entry records a question, not a
construction or an assertion that a hidden weak class exists.

## Existing work and scope

[GOAL-ECTD-001](../../ledger/goals/GOAL-ECTD-001.yaml) already addresses a
prime-field Teske analogue. This is a searchable companion to that goal,
not a new campaign or an authoritative change to its status.

KN-LIT-7261 records a binary composite-extension construction. KN-LIT-7635
records a finite-field multiplicative DLP demonstration, not an ordinary
prime-field ECDLP result. KN-TECH-028 concerns supersingular isogeny problems.
These are comparisons, not missing bridges that have already been proved.

The exact GOAL-ECTD-001 head was read during curation, but its run/evidence
history was not audited here. No claim is made about whether the program's
previous candidate mechanisms succeeded or failed.

## Evidence required for a positive claim

1. **Subgroup preservation.** State the map, field of definition, kernel,
   target subgroup and treatment of identity/exceptional points. Show that
   the transferred problem retains the original discrete log.
2. **Computational advantage.** Compare total setup, transfer, preprocessing,
   relation generation, solving, verification, memory and amortization
   against the applicable public baseline at the same parameters.
3. **Public reconstructability.** Analyze reconstruction from the public
   curve and its invariants separately from endpoint solving. Secret path
   knowledge or difficulty computing a ring does not establish hiddenness.
4. **Scope and scaling.** Distinguish a smaller equation description from
   easier solving, and toy-instance improvements from asymptotic or concrete
   cryptographic claims. Preserve failures and failed assumptions.

A claim that meets only one or two gates remains a scoped observation.
No security conclusion follows from a compact formula or an unpublished
representation alone.

## Candidate-specific falsifiers

| Candidate claim | What defeats that claim |
|---|---|
| An endpoint is much easier after a secret isogeny | Its fully charged solver cost matches or exceeds the applicable public baseline |
| A secret path hides an endpoint's relevant weakness | Public invariants or an affordable public search recover the same useful access |
| Endomorphism-ring knowledge creates the ECDLP advantage | Ring knowledge changes navigation or scalar-multiplication constants without improving ECDLP solving |
| A Jacobian transfer preserves the target DLP | The target subgroup is killed or the transfer cannot be evaluated at the claimed cost |
| Seed manipulation delivers a hidden weak class | No weak class with the stated density and advantage has been established |
| A toy solving gain extends to larger fields | The gain vanishes after setup, failed targets, verification or degree growth are charged |

These falsify particular claims, not the existence of every possible trapdoor.

## Next bounded work

Review the primary sources behind the taxonomy's recalled or abstract-only
claims, and compare this question with the existing ECTD goal's evidence before
proposing new experiments. Produce a literature/evidence matrix with separate
columns for subgroup preservation, solving advantage, and public reconstruction.
Unresolved cells stay unresolved.

Any later empirical claim must identify exact curves using the repository's
curve identity convention. Binary-field comparisons should distinguish the
n=31 development setting, composite n=51 subfield structure, and prime-degree
n=83 and n=131 settings; none is a substitute for a prime-field experiment.

## Current state

Open. This curation ran no cryptanalytic experiment and establishes no hidden
weak curve, private solver, or new speedup. Citation provenance is inherited
from the explicitly limited sources in KN-TECH-0f24d0.
