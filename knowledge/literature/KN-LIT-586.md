---
id: KN-LIT-586
type: literature
title: "A Systematic Study of the Impact of Graphical Models on Inference-based Attacks on AES"
authors:
  - "Joey Green"
  - "Elisabeth Oswald"
  - "Arnab Roy"
year: 2018
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2018/671"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2018/671"
tags: [pairing, provable-security, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Belief propagation, or the sum-product algorithm, is a powerful and well known method for inference on probabilistic graphical models, which has been proposed for the specific use in side channel analysis by Veyrat-Charvillon et al. We define a novel metric to capture the importance of variable nodes in factor graphs, we propose two improvements to the sum-product algorithm for the specific use case in side channel analysis, and we explicitly define and examine different ways of combining information from multiple side channel traces.

## Key claims (as reported)
- With these new considerations we systematically investigate a number of graphical models that “naturally” follow from an implementation of AES.
- Our results are unexpected: neither a larger graph (i.e. more side channel information) nor more connectedness necessarily lead to significantly better attacks.
- In fact our results demonstrate that in practice the (on balance) best choice is to utilise an acyclic graph in an independent graph combination setting, which gives us provable convergence to the correct key distribution.
- We provide evidence using both extensive simulations and a final confirmatory analysis on real trace data.1

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2018-671.pdf`
