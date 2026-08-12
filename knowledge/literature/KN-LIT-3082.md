---
id: KN-LIT-3082
type: literature
title: "Concurrent Signatures"
authors:
  - "Liqun Chen"
  - "Caroline Kudla"
  - "Kenneth G. Paterson"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, glv-gls, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce the concept of concurrent signatures. These allow two entities to produce two signatures in such a way that, from the point of view of any third party, both signatures are ambiguous with respect to the identity of the signing party until an extra piece of information (the keystone) is released by one of the parties.

## Key claims (as reported)
- Upon release of the keystone, both signatures become binding to their true signers concurrently.
- Concurrent signatures fall just short of providing a full solution to the problem of fair exchange of signatures, but we discuss some applications in which concurrent signatures suffice.
- Concurrent signatures are highly efficient and require neither a trusted arbitrator nor a high degree of interaction between parties.
- We provide a model of security for concurrent signatures, and a concrete scheme which we prove secure in the random oracle model under the discrete logarithm assumption.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/EC04Concurrent (1).pdf`
- `downloads/EC04Concurrent (2).pdf`
- `downloads/EC04Concurrent.pdf`
