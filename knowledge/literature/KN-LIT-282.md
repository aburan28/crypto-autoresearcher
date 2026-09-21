---
id: KN-LIT-282
type: literature
title: "Constructing elliptic curve isogenies in quantum subexponential time"
authors:
  - "Andrew M. Childs"
  - "David Jao"
  - "Vladimir Soukharev"
year: 2010
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "1012.4019"
  url: "https://arxiv.org/abs/1012.4019"
tags: [class-group, elliptic-curve, endomorphism, finite-field, isogeny, lattice, number-theory, pqc, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Given two elliptic curves over a finite field having the same cardinality and endomorphism ring, it is known that the curves admit an isogeny between them, but finding such an isogeny is believed to be computationally difficult. The fastest known classical algorithm takes exponential time, and prior to our work no faster quantum algorithm was known.

## Key claims (as reported)
- Recently, public-key cryptosystems based on the presumed hardness of this problem have been proposed as candidates for post-quantum cryptography.
- In this paper, we give a subexponential-time quantum algorithm for constructing isogenies, assuming the Generalized Riemann Hypothesis (but with no other assumptions).
- Our algorithm is based on a reduction to a hidden shift problem, together with a new subexponential-time algorithm for evaluating isogenies from kernel ideals (under only GRH), and represents the first nontrivial application of Kuperberg’s quantum algorithm for the hidden shift problem.
- This result suggests that isogeny-based cryptosystems may be uncompetitive with more mainstream quantum-resistant cryptosystems such as lattice-based cryptosystems.

## Relevance to this program
Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/1012.4019v3 (1).pdf`
- `downloads/1012.4019v3.pdf`
