---
id: KN-LIT-5760
type: literature
title: "Permissionless Clock Synchronization with Public Setup"
authors:
  - "Juan Garay⋆"
  - "Aggelos Kiayias"
  - "Yu Shen⋆⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The permissionless clock synchronization problem asks how it is possible for a population of parties to maintain a system-wide synchronized clock, while their participation rate fluctuates —possibly very widely— over time. The underlying assumption is that parties experience the passage of time with roughly the same speed, but however they may disengage and engage with the protocol following arbitrary (and even chosen adversarially) participation patterns.

## Key claims (as reported)
- This (classical) problem has received renewed attention due to the advent of blockchain protocols, and recently it has been solved in the setting of proof of stake, i.e., when parties are assumed to have access to a trusted PKI setup [Badertscher et al., Eurocrypt ’21].
- In this work, we present the first proof-of-work (PoW)-based permissionless clock synchronization protocol.
- Our construction assumes a public setup (e.g., a CRS) and relies on an honest majority of computational power that, for the first time, is described in a fine-grain timing model that does not utilize a global clock that exports the current time to all parties.
- As a secondary result of independent interest, our protocol gives rise to the first PoW-based ledger consensus protocol that does not rely on an external clock for the time-stamping of transactions and adjustment of the PoW difficulty.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137470132 (1).pdf`
- `downloads/137470132.pdf`
