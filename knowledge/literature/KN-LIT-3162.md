---
id: KN-LIT-3162
type: literature
title: "Converting Cryptographic Schemes from Symmetric to Asymmetric Bilinear Groups"
authors:
  - "Masayuki Abe"
  - "Jens Groth⋆"
  - "Miyako Ohkubo"
  - "Takuya Tango"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose a method to convert schemes designed over symmetric bilinear groups into schemes over asymmetric bilinear groups. The conversion assigns variables to one or both of the two source groups in asymmetric bilinear groups so that all original computations in the symmetric bilinear groups go through over asymmetric groups without having to compute isomorphisms between the source groups.

## Key claims (as reported)
- Our approach is to represent dependencies among variables using a directed graph, and split it into two graphs so that variables associated to the nodes in each graph are assigned to one of the source groups.
- Though searching for the best split is cumbersome by hand, our graph-based approach allows us to automate the task with a simple program.
- With the help of the automated search, our conversion method is applied to several existing schemes including one that has been considered hard to convert.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/86160272 (1).pdf`
- `downloads/86160272 (2).pdf`
- `downloads/86160272 (3).pdf`
- `downloads/86160272 (4).pdf`
- `downloads/86160272 (5).pdf`
- `downloads/86160272.pdf`
