---
id: KN-LIT-4492
type: literature
title: "Indistinguishability Obfuscation from SXDH on 5-Linear Maps and Locality-5 PRGs"
authors:
  - "Huijia Lin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [complexity-theory, lattice, pairing, provable-security, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Two recent works [Lin, EUROCRYPT 2016, Lin and Vaikuntanathan, FOCS 2016] showed how to construct Indistinguishability Obfuscation (IO) from constant degree multilinear maps. However, the concrete degrees of multilinear maps used in their constructions exceed 30.

## Key claims (as reported)
- In this work, we reduce the degree of multilinear maps needed to 5, by giving a new construction of IO from asymmetric L-linear maps and a pseudo-random generator (PRG) with output locality L and polynomial stretch.
- When plugging in a candidate PRG with locality-5 (e.g., [Goldreich, ECCC 2010, Mossel, Shpilka, and Trevisan, FOCS 2013, O’Donnald and Wither, CCC 2014]), we obtain a construction of IO from 5-linear maps.
- Our construction improves the state-of-the-art at two other fronts: First, it relies on “classical” multilinear maps, instead of their powerful generalization of graded encodings.
- Second, it comes with a security reduction to i) the SXDH assumption on algebraic multilinear maps [Boneh and Silverberg, Contemporary Mathematics, Rothblum, TCC 2013], ii) the security of PRG, and iii) sub-exponential LWE, all with sub-exponential hardness.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10401419 (1).pdf`
- `downloads/10401419.pdf`
