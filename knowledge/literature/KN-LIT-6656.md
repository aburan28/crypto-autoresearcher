---
id: KN-LIT-6656
type: literature
title: "Simple Lattice Trapdoor Sampling from a Broad Class of Distributions"
authors:
  - "Vadim Lyubashevsky"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, quantum, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At the center of many lattice-based constructions is an algorithm that samples a short vector s, satisfying [A|AR−HG]s = t mod q where A, AR, H, G are public matrices and R is a trapdoor. Although the algorithm crucially relies on the knowledge of the trapdoor R to perform this sampling efficiently, the distribution it outputs should be independent of R given the public values.

## Key claims (as reported)
- We present a new, simple algorithm for performing this task.
- The main novelty of our sampler is that the distribution of s does not need to be Gaussian, whereas all previous works crucially used the properties of the Gaussian distribution to produce such an s.
- The advantage of using a non-Gaussian distribution is that we are able to avoid the high-precision arithmetic that is inherent in Gaussian sampling over arbitrary lattices.
- So while the norm of our out√ put vector s is on the order of n to n - times larger (the representation length, though, is only a constant factor larger) than in the samplers of Gentry, Peikert, Vaikuntanathan (STOC 2008) and Micciancio, Peikert (EUROCRYPT 2012), the sampling itself can be done very efficiently.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/90200181 (1).pdf`
- `downloads/90200181 (2).pdf`
- `downloads/90200181 (3).pdf`
- `downloads/90200181 (4).pdf`
- `downloads/90200181.pdf`
