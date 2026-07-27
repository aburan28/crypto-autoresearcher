---
id: KN-LIT-1086
type: literature
title: "Computing supersingular endomorphism rings using inseparable endomorphisms"
authors:
  - "Jenny Fuselier"
  - "Annamaria Iezzi"
  - "Mark Kozek"
  - "Travis Morrison"
  - "Changningphaabi Namoijam"
year: 2023
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2306.03051"
  url: "https://arxiv.org/abs/2306.03051"
tags: [elliptic-curve, endomorphism, finite-field, isogeny, number-theory, provable-security, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give an algorithm for computing an inseparable endomorphism of a supersingular elliptic curve E defined over Fp2 , which, conditional on GRH, runs in expected O(p1/2 (log p)2 (log log p)3 ) bit operations and requires O((log p)2 ) storage. This matches the time and storage complexity of the best conditional algorithms for computing a nontrivial supersingular endomorphism, such as those of Eisenträger–Hallgren– Leonardi–Morrison–Park and Delfs–Galbraith.

## Key claims (as reported)
- Unlike these prior algorithms, which require two paths from E to a curve defined over Fp , the algorithm we introduce only requires one; thus when combined with the algorithm of Corte-Real Santos–Costello–Shi, our algorithm will be faster in practice.
- Moreover, our algorithm produces endomorphisms with predictable discriminants, enabling us to prove properties about the orders they generate.
- With two calls to our algorithm, we can provably compute a Bass suborder of End(E).
- This result is then used in an algorithm for computing a basis for End(E) with the same time complexity, assuming GRH.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2306.03051v2 (1).pdf`
- `downloads/2306.03051v2.pdf`
