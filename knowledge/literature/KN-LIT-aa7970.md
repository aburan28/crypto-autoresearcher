---
id: KN-LIT-aa7970
type: literature
title: "Methodology note on a multiagent resolution of the Navier-Stokes and Euler regularity problems"
authors:
  - "UNATTRIBUTED (institutional first person; names Codex and GPT-6 Astra as internal tools)"
year: 2026
venue: >-
  None. An unattributed ~400-word fragment pasted into a chat session and frozen
  at inputs/NS-AGENT-RESOLUTION-2026/received_text.md
  (SRC-NS-AGENT-RESOLUTION-2026). The bytes are re-readable from this
  repository; the document they came from is not identified and the
  mathematical artifacts they describe were not supplied.
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [methodology, agentic-harness, multiagent, orchestration, proof-search, formalization, lean, navier-stokes, euler-equations, partial-differential-equations, unverified, announcement-level]
confidence: reported
citation_verified: false
source_record: SRC-NS-AGENT-RESOLUTION-2026
added: "2026-09-08"
supersedes: null
superseded_by: null
---

## Why this entry exists

The fragment carries no mathematics. Its only value to this program is
methodological: it is a first-person account of how a large agent population was
organized to attack an open problem, and this repository is itself an agent
harness with a documented interest in proof-search architecture
(`docs/inventor-protocol.md` section 8, `KN-TECH-080`). This entry preserves what
the source asserts, separates the asserted procedure from the asserted result,
and records what cannot be checked. The transferable orchestration patterns are
abstracted separately in `KN-TECH-d1ad97`.

## What the source asserts

Recorded as claims. None is verified here.

1. **System shape.** Agents powered by an unnamed internal model, with tools for
   reading a cached snapshot of the internet and for running code. Agents were
   subdivided into groups; communication was within a group. Group sizes varied.
2. **Scale.** The group that produced the Navier-Stokes resolution is described
   as "on the order of 10,000 concurrent agents".
3. **Safeguards.** The same monitoring and isolation applied to the
   organization's frontier model evaluations was maintained throughout.
4. **Variant partitioning.** For each problem, separate groups received different
   variants of the problem statement, "covering all variants". For Navier-Stokes
   specifically, variants "A" and "B" were framed so that success would yield a
   proof, and "C" and "D" so that success would yield a disproof.
5. **Easier-problem track.** Alongside the full Millennium Prize problems, the
   system was given a set of "easier" problems. One was the regularity problem
   for the Euler equations - the inviscid limit of Navier-Stokes.
6. **Euler result.** The agents are said to have resolved the **unforced**
   variant of Euler regularity, producing a **disproof**. Nearly 100 agents,
   approximately 50 hours. The account attaches a footnote marker here whose
   note was not supplied.
7. **Reallocation.** The Euler result caused a deliberate concentration of
   resources: agents were shifted off the other Millennium Problems onto
   Navier-Stokes and were prompted with the Euler resolution.
8. **Mid-run model upgrade.** A further-trained version of the internal model
   became available during the effort and the agents were updated to it.
9. **Diversity then consolidation.** Groups were encouraged to explore different
   approaches; after some time the groups were "cross-pollinated" by using Codex
   to consolidate the most useful insights from each group into follow-up
   prompts that drew on the agents' own intermediate results. The group that
   found the Navier-Stokes solution is said to have been guided this way.
10. **Timing.** Resolution reached Saturday, September 5, about 88 hours after
    the first agents were launched. Lean formalization and verification took a
    further 17 hours via GPT-6 Astra.
11. **Resource totals.** Across all attempted problems: 4.9 million messages,
    about 300 billion output tokens. For Navier-Stokes alone: 2.7 million
    messages, approximately 130 billion output tokens. (The sentence stating the
    last figure is truncated in the received text.)

## What is not established

- **No mathematical content was supplied.** There is no theorem statement, no
  proof, no proof sketch, no counterexample construction, no Lean file, and no
  pointer to any of these. This entry therefore says nothing about whether
  Navier-Stokes or Euler regularity was in fact resolved, and it must never be
  cited as though it did.
- **No provenance.** The fragment is unattributed and undated as received. The
  internal tool names are consistent with a particular lineage but consistency
  is not attribution.
- **The resource figures are unaudited.** Agent counts, hours, message counts,
  and token totals are self-reported, single-shot, and carry no definition of
  what counts as an agent or a message, no dispersion, and no failed-attempt
  denominator. They support no rate, no cost model, and no scaling law.
- **The base rate is missing, and its absence is the most important gap.** The
  account reports the successes. It does not report how many groups, variants,
  problems, or hours produced nothing, and it does not report what happened to
  the other Millennium Problems after resources were withdrawn. Without that
  denominator, the reported procedure has no measurable success rate, and the
  variant-partitioning design in particular cannot be distinguished from the
  outcome it happened to produce. Compare `KN-LIT-7639`, where a volunteered
  negative base rate was recorded precisely because it was the item of most
  methodological value.
- **Independent verification is not implied by Lean.** Formalization by a model
  in the same system, of a statement chosen by that system, checks the proof
  against the statement; it does not check that the statement is the Millennium
  problem, and no formalization artifact was supplied to inspect either half.

## Relevance to this program

Zero direct relevance. The source discusses fluid PDE regularity and supplies no
ECDLP algorithm, relation generator, descent, cost path, or verifier receipt.
Under AGENTS.md rule 4 nothing here transfers to any curve, parameter, or solver
in this ledger.

Its indirect relevance is to harness design, and it is a **hypothesis source, not
a result**: the orchestration patterns it describes are abstracted in
`KN-TECH-d1ad97` as untested candidates for this program, with the controls that
would be needed before any of them is believed. That abstraction is adopted, if
at all, on its own merits and on this program's own measurements - never on the
strength of the outcome reported here.

## Not verified here

Nothing in the "What the source asserts" section was checked against any primary
document, artifact, or independent report. The received fragment is frozen and
its hash is recomputable; that makes the *intake* reproducible and leaves every
*claim* second-hand. The content status is `reported` and
`citation_verified: false`.
