---
id: KN-LIT-1214
type: literature
title: "CONNECTING KANI’S LEMMA AND PATH-FINDING IN THE BRUHAT-TITS TREE TO COMPUTE SUPERSINGULAR"
authors:
  - "ENDOMORPHISM RINGS"
year: 2024
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2402.05059"
  url: "https://arxiv.org/abs/2402.05059"
tags: [elliptic-curve, endomorphism, factoring, hash, isogeny, mov-fr, pqc, provable-security, sidh-csidh, signature, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We give a deterministic algorithm to compute the endomorphism ring of a supersingular elliptic curve in characteristic p, provided that we are given two noncommuting endomorphisms and the factorization of the discriminant of the ring O0 they generate. The algorithm is polynomial in the largest prime factor of the reduced discriminant of O0 which is not equal to p.

## Key claims (as reported)
- At each prime q for which O0 is not maximal, we compute the endomorphism ring locally by computing a q-maximal order containing it and, when q ̸= p, recovering a path to End(E) ⊗ Zq in the Bruhat-Tits tree.
- We use techniques of higher-dimensional isogenies to navigate towards the local endomorphism ring.
- Our algorithm improves on a previous algorithm which requires a restricted input and runs in subexponential time under certain heuristics.
- Page and Wesolowski give a probabilistic polynomial time reduction between computing a single non-scalar endomorphism and computing the endomorphism ring.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2402.05059v2 (1).pdf`
- `downloads/2402.05059v2.pdf`
