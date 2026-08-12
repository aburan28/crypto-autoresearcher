---
id: KN-LIT-3837
type: literature
title: "Faster Explicit Formulas for Computing Pairings over Ordinary Curves Diego F. Aranha1? , Koray Karabina2?"
authors:
  - "Catherine H. Gebotys"
  - "Julio López"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [curve-arithmetic, elliptic-curve, extension-field, implementation, jacobian, mov-fr, pairing, prime-field, provable-security, survey, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe efficient formulas for computing pairings on ordinary elliptic curves over prime fields. First, we generalize lazy reduction techniques, previously considered only for arithmetic in quadratic extensions, to the whole pairing computation, including towering and curve arithmetic.

## Key claims (as reported)
- Second, we introduce a new compressed squaring formula for cyclotomic subgroups and a new technique to avoid performing an inversion in the final exponentiation when the curve is parameterized by a negative integer.
- The techniques are illustrated in the context of pairing computation over Barreto-Naehrig curves, where they have a particularly efficient realization, and are also combined with other important developments in the recent literature.
- The resulting formulas reduce the number of required operations and, consequently, execution time, improving on the state-of-the-art performance of cryptographic pairings by 28%-34% on several popular 64-bit computing platforms.
- In particular, our techniques allow to compute a pairing under 2 million cycles for the first time on such architectures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320047 (1).pdf`
- `downloads/66320047 (2).pdf`
- `downloads/66320047 (3).pdf`
- `downloads/66320047.pdf`
