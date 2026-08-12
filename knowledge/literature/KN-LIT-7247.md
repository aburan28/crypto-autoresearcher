---
id: KN-LIT-7247
type: literature
title: "Tradeoff Cryptanalysis of Memory-Hard Functions"
authors:
  - "Alex Biryukov"
  - "Dmitry Khovratovich"
year: null
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, cryptanalysis, hash, implementation, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We explore time-memory and other tradeoffs for memoryhard functions, which are supposed to impose significant computational and time penalties if less memory is used than intended. We analyze three finalists of the Password Hashing Competition: Catena, which was presented at Asiacrypt 2014, yescrypt and Lyra2.

## Key claims (as reported)
- We demonstrate that Catena’s proof of tradeoff resilience is flawed, and attack it with a novel precomputation tradeoff.
- We show that using M 4/5 memory instead of M we have no time penalties and reduce the AT cost by the factor of 25.
- We further generalize our method for a wide class of schemes with predictable memory access.
- For a wide class of datadependent schemes, which addresses memory unpredictably, we develop a novel ranking tradeoff and show how to decrease the time-memory and the time-area product by significant factors.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/94520239 (1).pdf`
- `downloads/94520239.pdf`
