---
id: KN-LIT-1526
type: literature
title: "A New Construction Method for More Efficient Quadratic One-Time Noisy"
authors:
  - "Multi-Client Functional Encryption"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1033"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1033"
tags: [hash, lattice, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a new construction method for one-time multi-client functional encryption schemes that support noisy quadratic functions, are resistant against corruption and allow for labels. Such schemes can be used as building blocks in many practical applications, e.g., privacy preserving machine learning on arbitrarily split data.

## Key claims (as reported)
- In contrast to earlier constructions, ours uses a different structural design that allows to make use of less complex, hence more efficient building blocks.
- The security of our construction relies solely on its underlying building blocks and no additional hardness assumptions, making it more generic than related work.
- More specifically, the construction itself does not rely on structures given by bilinear groups.
- We present a concrete instantiation, dubbed QUILT, and show in a series of experiments that it outperforms existing comparable schemes by far.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1033.pdf`
