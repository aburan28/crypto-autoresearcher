---
id: KN-LIT-1167
type: literature
title: "SCALLOP-HD: group action from 2-dimensional isogenies"
authors:
  - "Mingjie Chen"
  - "Antonin Leroux"
  - "Lorenz Panny"
year: 2023
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2023/1488"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2023/1488"
tags: [abelian-variety, class-group, cryptanalysis, elliptic-curve, endomorphism, isogeny, lattice, number-theory, pqc, protocol, quantum, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present SCALLOP-HD, a novel group action that builds upon the recent SCALLOP group action introduced by De Feo, Fouotsa, Kutas, Leroux, Merz, Panny and Wesolowski in 2023. While our group action uses the same √ action of the class group Cl(O) on O-oriented curves where O = Z[f −d] for a large prime f and small d as SCALLOP, we introduce a different orientation representation: The new representation embeds an endomorphism generating O in a 2e -isogeny between abelian varieties of dimension 2 with Kani’s Lemma, and this representation comes with a simple algorithm to compute the class group action.

## Key claims (as reported)
- Our new approach considerably simplifies the SCALLOP framework, potentially surpassing it in efficiency — a claim supported by preliminary implementation results in SageMath.
- Additionally, our approach streamlines parameter selection.
- The new representation allows us to select efficiently a class group Cl(O) of smooth order, enabling polynomial-time generation of the lattice of relation, hence enhancing scalability in contrast to SCALLOP.
- To instantiate our SCALLOP-HD group action, we introduce a new technique to apply Kani’s Lemma in dimension 2 with an isogeny diamond obtained from commuting endomorphisms.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14602134 (1).pdf`
- `downloads/14602134.pdf`
- `downloads/2023-1488.pdf`
