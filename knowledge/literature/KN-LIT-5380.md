---
id: KN-LIT-5380
type: literature
title: "On Proving Equivalence Class Signatures Secure from Non-interactive Assumptions"
authors:
  - "Balthazar Bauer"
  - "Georg Fuchsbauer"
  - "Fabian Regen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, pairing, provable-security, quantum, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Equivalence class signatures (EQS), introduced by Hanser and Slamanig (AC’14, J.Crypto’19), sign vectors of elements from a bilinear group. Their main feature is “adaptivity”: given a signature on a vector, anyone can transform it to a (uniformly random) signature on any multiple of the vector.

## Key claims (as reported)
- A signature thus authenticates equivalence classes and unforgeability is defined accordingly.
- EQS have been used to improve the efficiency of many cryptographic applications, notably (delegatable) anonymous credentials, (round-optimal) blind signatures, group signatures and anonymous tokens.
- EQS security implies strong anonymity (or blindness) guarantees for these schemes which holds against malicious signers without trust assumptions.
- Unforgeability of the original EQS construction is proven directly in the generic group model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602133 (1).pdf`
- `downloads/14602133.pdf`
