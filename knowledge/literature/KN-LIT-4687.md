---
id: KN-LIT-4687
type: literature
title: "Leakage-Resilient IBE/ABE with Optimal Leakage Rates from Lattices"
authors:
  - "Qiqi Lai"
  - "Feng-Hao Liu"
  - "Zhedong Wang (Corresponding Author)"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, pqc, quantum, side-channel, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We derive the first adaptively secure IBE and ABE for t-CNF, and selectively secure ABE for general circuits from lattices, with 1−o(1) leakage rates, in the both relative leakage model and bounded retrieval model (BRM). To achieve this, we first identify a new fine-grained security notion for ABE – partially adaptive/selective security, and instantiate this notion from LWE.

## Key claims (as reported)
- Then, by using this notion, we design a new key compressing mechanism for identity-based/attributed-based weak hash proof system (IB/AB-wHPS) for various policy classes, achieving (1) succinct secret keys and (2) adaptive/selective security matching the existing nonleakage resilient lattice-based designs.
- Using the existing connection between weak hash proof system and leakage resilient encryption, the succinctkey IB/AB-wHPS can yield the desired leakage resilient IBE/ABE schemes with the optimal leakage rates in the relative leakage model.
- Finally, by further improving the prior analysis of the compatible locally computable extractors, we can achieve the optimal leakage rates in the BRM.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/131770070 (1).pdf`
- `downloads/131770070.pdf`
