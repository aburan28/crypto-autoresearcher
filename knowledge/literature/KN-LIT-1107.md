---
id: KN-LIT-1107
type: literature
title: "Fast and Frobenius: Rational Isogeny Evaluation over Finite Fields"
authors:
  - "Gustavo Banegas"
  - "Valerie Gilchrist"
  - "Anaëlle Le Dévéhat"
  - "Benjamin Smith"
year: 2023
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2306.16072"
  url: "https://arxiv.org/abs/2306.16072"
tags: [cryptanalysis, curve-arithmetic, elliptic-curve, finite-field, isogeny, pairing, pqc, protocol, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Consider the problem of efficiently evaluating isogenies φ : E → E /H of elliptic curves over a finite field Fq , where the kernel H = hGi is a cyclic group of odd (prime) order: given E , G, and a point (or several points) P on E , we want to compute φ(P ). This problem is at the heart of efficient implementations of group-action- and isogenybased post-quantum cryptosystems such as CSIDH.

## Key claims (as reported)
- Algorithms based on Vélu’s formulæ give an efficient solution to this problem when the kernel generator G is defined over Fq .
- However, for general isogenies, G is only defined over some extension Fqk , even though hGi as a whole (and thus φ) is defined over the base field Fq ; and the performance of Vélustyle algorithms degrades rapidly as k grows.
- In this article we revisit the isogeny-evaluation problem with a special focus on the case where 1 ≤ k ≤ 12.
- We improve Vélu-style isogeny evaluation for many cases where k = 1 using special addition chains, and combine this with the action of Galois to give greater improvements when k > 1.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2306.16072v1 (1).pdf`
- `downloads/2306.16072v1 (2).pdf`
- `downloads/2306.16072v1.pdf`
