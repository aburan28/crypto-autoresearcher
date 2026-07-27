---
id: KN-LIT-5266
type: literature
title: "Oblivious Accumulators"
authors:
  - "Foteini Baldimtsi⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, mov-fr, pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
A cryptographic accumulator is a succinct set commitment scheme with efficient (non-)membership proofs that typically supports updates (additions and deletions) on the accumulated set. When elements are added to or deleted from the set, an update message is issued.

## Key claims (as reported)
- The collection of all the update messages essentially leaks the underlying accumulated set which in certain applications is not desirable.
- In this work, we define oblivious accumulators, a set commitment with concise membership proofs that hides the elements and the set size from every entity: an outsider, a verifier or other element holders.
- We formalize this notion of privacy via two properties: element hiding and add-delete indistinguishability.
- We also define almost-oblivious accumulators, that only achieve a weaker notion of privacy called add-delete unlinkability.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602152 (1).pdf`
- `downloads/14602152.pdf`
