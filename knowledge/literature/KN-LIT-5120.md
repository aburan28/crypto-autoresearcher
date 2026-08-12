---
id: KN-LIT-5120
type: literature
title: "New Instantiations of the CRYPTO 2017 Masking Schemes"
authors:
  - "Pierre Karpman"
  - "Daniel S. Roche"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, finite-field, mpc, pairing, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
At CRYPTO 2017, Belaı̈d et al. presented two new private multiplication algorithms over finite fields, to be used in secure masking schemes. To date, these algorithms have the lowest known complexity in terms of bilinear multiplication and random masks respectively, both being linear in the number of shares d + 1.

## Key claims (as reported)
- Yet, a practical drawback of both algorithms is that their safe instantiation relies on finding matrices satisfying certain conditions.
- In their work, Belaı̈d et al. only address these up to d = 2 and 3 for the first and second algorithm respectively, limiting so far the practical usefulness of their constructions.
- In this paper, we use in turn an algebraic, heuristic, and experimental approach to find many more safe instances of Belaı̈d et al.’s algorithms.
- This results in explicit instantiations up to order d = 6 over large fields, and up to d = 4 over practically relevant fields such as F28 .

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/11272107 (1).pdf`
- `downloads/11272107.pdf`
