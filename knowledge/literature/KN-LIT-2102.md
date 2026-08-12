---
id: KN-LIT-2102
type: literature
title: "A Lower Bound for One-Round Oblivious RAM"
authors:
  - "David Cash"
  - "Andrew Drucker"
  - "Alexander Hoover"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, fhe, lattice, mov-fr, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We initiate a fine-grained study of the round complexity of Oblivious RAM (ORAM). We prove that any one-round √ balls-in-bins ORAM that√does not duplicate balls must have either Ω( N ) bandwidth or Ω( N ) client memory, where N is the number of memory slots being simulated.

## Key claims (as reported)
- This shows that such schemes are strictly weaker than general (multi-round) ORAMs or those with server computation, and in particular implies that a one-round version of the original square-root ORAM of Goldreich and Ostrovksy (J.
- ACM 1996) is optimal.
- We prove this bound via new techniques that differ from those of Goldreich and Ostrovksy, and of Larsen and Nielsen (CRYPTO 2018), which achieved an Ω(log N ) bound for balls-in-bins and general multi-round ORAMs respectively.
- Finally we give a weaker extension of our bound that allows for limited duplication of balls, and also show that our bound extends to multiple-round ORAMs of a restricted form that include the best known constructions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12550125 (1).pdf`
- `downloads/12550125.pdf`
