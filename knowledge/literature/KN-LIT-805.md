---
id: KN-LIT-805
type: literature
title: "Order-Fairness for Byzantine Consensus"
authors:
  - "Mahimna Kelkar"
  - "Fan Zhang"
  - "Steven Goldfeder"
  - "Ari Juels"
year: 2020
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2020/269"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2020/269"
tags: [pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Decades of research in both cryptography and distributed systems has extensively studied the problem of state machine replication, also known as Byzantine consensus. A consensus protocol must satisfy two properties: consistency and liveness.

## Key claims (as reported)
- These properties ensure that honest participating nodes agree on the same log and dictate when fresh transactions get added.
- They fail, however, to ensure against adversarial manipulation of the actual ordering of transactions in the log.
- Indeed, in leader-based protocols (almost all protocols used today), malicious leaders can directly choose the final transaction ordering.
- To rectify this problem, we propose a third consensus property: transaction order-fairness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12171344 (1).pdf`
- `downloads/12171344.pdf`
