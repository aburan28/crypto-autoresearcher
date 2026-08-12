---
id: KN-LIT-6512
type: literature
title: "Security of Blind Signatures Revisited"
authors:
  - "Dominique Schröder"
  - "Dominique Unruh"
year: null
venue: "Journal of Cryptology"
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mov-fr, pairing, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit the definition of unforgeability of blind signatures as proposed by Pointcheval and Stern (Journal of Cryptology 2000). Surprisingly, we show that this established definition falls short in two ways of what one would intuitively expect from a secure blind signature scheme: It is not excluded that an adversary submits the same message m twice for signing, and then produces a signature for m0 6= m.

## Key claims (as reported)
- The reason is that the forger only succeeds if all messages are distinct.
- Moreover, it is not excluded that an adversary performs k signing queries and produces signatures on k + 1 messages as long as each of these signatures does not pass verification with probability 1.
- Finally, we propose a new definition, honest-user unforgeability, that covers these attacks.
- We give a simple and efficient transformation that transforms any unforgeable blind signature scheme (with deterministic verification) into an honest-user unforgeable one.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/72930662 (1).pdf`
- `downloads/72930662 (2).pdf`
- `downloads/72930662 (3).pdf`
- `downloads/72930662.pdf`
