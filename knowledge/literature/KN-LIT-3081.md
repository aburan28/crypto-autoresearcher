---
id: KN-LIT-3081
type: literature
title: "Concurrent Secure Computation with Optimal Query Complexity"
authors:
  - "Ran Canetti"
  - "Vipul Goyal"
  - "Abhishek Jain"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, protocol, provable-security, quantum, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The multiple ideal query (MIQ) model [Goyal, Jain, and Ostrovsky, Crypto’10] offers a relaxed notion of security for concurrent secure computation, where the simulator is allowed to query the ideal functionality multiple times per session (as opposed to just once in the standard definition). The model provides a quantitative measure for the degradation in security under concurrent self-composition, where the degradation is measured by the number of ideal queries.

## Key claims (as reported)
- However, to date, all known MIQ-secure protocols guarantee only an overall average bound on the number of queries per session throughout the execution, thus allowing the adversary to potentially fully compromise some sessions of its choice.
- Furthermore, [Goyal and Jain, Eurocrypt’13] rule out protocols where the simulator makes only an adversary-independent constant number of ideal queries per session.
- We show the first MIQ-secure protocol with worst-case per-session guarantee.
- Specifically, we show a protocol for any functionality that matches the [GJ13] bound: The simulator makes only a constant number of ideal queries in every session.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160283 (1).pdf`
- `downloads/92160283 (2).pdf`
- `downloads/92160283.pdf`
