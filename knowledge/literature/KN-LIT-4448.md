---
id: KN-LIT-4448
type: literature
title: "Improvements of Algebraic Attacks for solving the Rank Decoding and MinRank problems"
authors:
  - "Magali Bardet"
  - "Maxime Bros"
  - "Daniel Cabarcas"
  - "Philippe Gaborit"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, pqc, quantum, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we show how to significantly improve algebraic techniques for solving the MinRank problem, which is ubiquitous in multivariate and rank metric code based cryptography. In the case of the structured MinRank instances arising in the latter, we build upon a recent breakthrough [11] showing that algebraic attacks outperform the combinatorial ones that were considered state of the art up until now.

## Key claims (as reported)
- Through a slight modification of this approach, we completely avoid Gröbner bases computations for certain parameters and are left only with solving linear systems.
- This does not only substantially improve the complexity, but also gives a convincing argument as to why algebraic techniques work in this case.
- When used against the second round NIST-PQC candidates ROLLO-I-128/192/256, our new attack has bit complexity respectively 71, 87, and 151, to be compared to 117, 144, and 197 as obtained in [11].
- The linear systems arise from the nullity of the maximal minors of a certain matrix associated to the algebraic modeling.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/12491265 (1).pdf`
- `downloads/12491265.pdf`
