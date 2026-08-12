---
id: KN-LIT-7309
type: literature
title: "Two-Round Concurrent 2PC from Sub-Exponential LWE"
authors:
  - "Behzad Abdolmaleki"
  - "Saikrishna Badrinarayanan⋆"
  - "Rex Fernando⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, pairing, pqc, protocol, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secure computation is a cornerstone of modern cryptography and a rich body of research is devoted to understanding its round complexity. In this work, we consider two-party computation (2PC) protocols (where both parties receive output) that remain secure in the realistic setting where many instances of the protocol are executed in parallel (concurrent security).

## Key claims (as reported)
- We obtain a two-round concurrent-secure 2PC protocol based on a single, standard, post-quantum assumption: The subexponential hardness of the learning-with-errors (LWE) problem.
- Our protocol is in the plain model, i.e., it has no trusted setup, and it is secure in the super-polynomial simulation framework of Pass (EUROCRYPT 2003).
- Since two rounds are minimal for (concurrent) 2PC, this work resolves the round complexity of concurrent 2PC from standard assumptions.
- As immediate applications, our work establishes feasibility results for interesting cryptographic primitives, such as the first two-round password authentication key exchange (PAKE) protocol in the plain model and the first two-round concurrent secure computation protocol for quantum circuits (2PQC).

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14438313 (1).pdf`
- `downloads/14438313.pdf`
