---
id: KN-LIT-1382
type: literature
title: "Efficient Algorithms for Isogeny Computation on Hyperelliptic Curves: Their Applications in Post-Quantum Cryptography"
authors:
  - "Mohammed El Baraka"
  - "Siham Ezzouak"
year: 2025
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2504.04559"
  url: "https://arxiv.org/abs/2504.04559"
tags: [dlp, elliptic-curve, factoring, hyperelliptic, index-calculus, isogeny, jacobian, pairing, pqc, provable-security, quantum, sidh-csidh, supersingular]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present efficient algorithms for computing isogenies between hyperelliptic curves, leveraging higher genus curves to enhance cryptographic protocols in the post-quantum context. Our algorithms reduce the computational complexity of isogeny computations from O(g 4 ) to O(g 3 ) operations for genus 2 curves, achieving significant efficiency gains over traditional elliptic curve methods.

## Key claims (as reported)
- Detailed pseudocode and comprehensive complexity analyses demonstrate these improvements both theoretically and empirically.
- Additionally, we provide a thorough security analysis, including proofs of resistance to quantum attacks such as Shor’s and Grover’s algorithms.
- Our findings establish hyperelliptic isogenybased cryptography as a promising candidate for secure and efficient post-quantum cryptographic systems.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to the isogeny cluster: bears on supersingular/isogeny-based constructions and the isogeny-path problems that compete with and inform ECDLP work. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2504.04559v1.pdf`
