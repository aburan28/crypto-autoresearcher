---
id: KN-LIT-3116
type: literature
title: "Constant-Round Maliciously Secure Two-Party Computation in the RAM Model ? ??"
authors:
  - "Carmit Hazay"
  - "Avishay Yanai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [implementation, mpc, pairing, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The random-access memory (RAM) model of computation allows program constant-time memory lookup and is more applicable in practice today, covering many important algorithms. This is in contrast to the classic setting of secure 2-party computation (2PC) that mostly follows the approach for which the desired functionality must be represented as a boolean circuit.

## Key claims (as reported)
- In this work we design the first constant round maliciously secure two-party protocol in the RAM model.
- Our starting point is the garbled RAM construction of Gentry et al.
- [16] that readily induces a constant round semi-honest two-party protocol for any RAM program assuming identity-based encryption schemes.
- We show how to enhance the security of their construction into the malicious setting while facing several challenges that stem due to handling the data memory.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/99850176 (1).pdf`
- `downloads/99850176.pdf`
