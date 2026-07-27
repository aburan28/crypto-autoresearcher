---
id: KN-LIT-5671
type: literature
title: "Optimistic Asynchronous Atomic Broadcast"
authors:
  - "Klaus Kursawe"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper presents a new protocol for atomic broadcast in an asynchronous network with a maximal number of Byzantine failures. It guarantees both safety and liveness without making any timing assumptions or using any type of “failure detector.” Under normal circumstances, the protocol runs in an “optimistic mode,” with extremely low message and computational complexity — essentially, just performing a Bracha broadcast for each request.

## Key claims (as reported)
- In particular, no potentially expensive public-key cryptographic operations are used.
- In rare circumstances, the protocol may briefly switch to a “pessimistic mode,” where both the message and computational complexity are significantly higher than in the “optimistic mode,” but are still reasonable.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/ks.pdf`
