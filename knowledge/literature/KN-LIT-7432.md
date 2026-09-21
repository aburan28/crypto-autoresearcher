---
id: KN-LIT-7432
type: literature
title: "Upper Bounds on the Communication Complexity of Optimally Resilient Cryptographic Multiparty Computation"
authors:
  - "Martin Hirt"
  - "Jesper Buus Nielsen"
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
We give improved upper bounds on the communication complexity of optimally-resilient secure multiparty computation in the cryptographic model. We consider evaluating an n-party randomized function and show that if f can be computed by a circuit of size c, then O(cn2 κ) is an upper bound for active security with optimal resilience t < n/2 and security parameter κ.

## Key claims (as reported)
- This improves on the communication complexity of previous protocols by a factor of at least n.
- This improvement comes from the fact that in the new protocol, only O(n) messages (of size O(κ) each) are broadcast during the whole protocol execution, in contrast to previous protocols which require at least O(n) broadcasts per gate.
- Furthermore, we improve the upper bound on the communication complexity of passive secure multiparty computation with resilience t < n from O(cn2 κ) to O(cnκ).
- This improvement is mainly due to a simple observation.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/079 (1).pdf`
- `downloads/079 (2).pdf`
- `downloads/079 (3).pdf`
- `downloads/079.pdf`
