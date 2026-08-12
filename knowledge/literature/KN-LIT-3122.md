---
id: KN-LIT-3122
type: literature
title: "Constant-Size Commitments to Polynomials and Their Applications?"
authors:
  - "Aniket Kate"
  - "Gregory M. Zaverucha"
  - "Ian Goldberg"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, mpc, pairing, quantum, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce and formally define polynomial commitment schemes, and provide two efficient constructions. A polynomial commitment scheme allows a committer to commit to a polynomial with a short string that can be used by a verifier to confirm claimed evaluations of the committed polynomial.

## Key claims (as reported)
- Although the homomorphic commitment schemes in the literature can be used to achieve this goal, the sizes of their commitments are linear in the degree of the committed polynomial.
- On the other hand, polynomial commitments in our schemes are of constant size (single elements).
- The overhead of opening a commitment is also constant; even opening multiple evaluations requires only a constant amount of communication overhead.
- Therefore, our schemes are useful tools to reduce the communication cost in cryptographic protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/6477178 (1).pdf`
- `downloads/6477178 (2).pdf`
- `downloads/6477178 (3).pdf`
- `downloads/6477178.pdf`
