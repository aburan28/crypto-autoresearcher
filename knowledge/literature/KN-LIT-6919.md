---
id: KN-LIT-6919
type: literature
title: "Synchronizable Fair Exchange"
authors:
  - "Ranjit Kumaresan"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, mpc, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Fitzi, Garay, Maurer, and Ostrovsky (J. Cryptology 2005) showed that in the presence of a dishonest majority, no primitive of cardinality n − 1 is complete for realizing an arbitrary n-party functionality with guaranteed output delivery.

## Key claims (as reported)
- In this work, we introduce a new 2-party primitive FSyX (“synchronizable fair exchange”) and show that it is complete for realizing any n-party functionality with fairness in a setting where all parties are pairwise connected by instances of FSyX .
- In the FSyX -hybrid model, the two parties load FSyX with some input, and following this, either party can trigger FSyX with a “witness” at a later time to receive the output from FSyX .
- Crucially the other party also receives output from FSyX when FSyX is triggered.
- The trigger witnesses allow us to synchronize the trigger phases of multiple instances of FSyX , thereby aiding in the design of fair multiparty protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14369039 (1).pdf`
- `downloads/14369039.pdf`
