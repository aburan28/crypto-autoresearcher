---
id: KN-LIT-771
type: literature
title: "Improved quantum circuits for elliptic curve discrete logarithms"
authors:
  - "Thomas Häner"
  - "Samuel Jaques ∗"
  - "Michael Naehrig"
  - "Martin Roetteler"
  - "Mathias Soeken"
year: 2020
venue: "arXiv preprint"
identifiers:
  eprint: null
  doi: null
  arxiv: "2001.09580"
  url: "https://arxiv.org/abs/2001.09580"
tags: [cryptanalysis, curve-arithmetic, dlp, ecdlp, elliptic-curve, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We present improved quantum circuits for elliptic curve scalar multiplication, the most costly component in Shor’s algorithm to compute discrete logarithms in elliptic curve groups. We optimize low-level components such as reversible integer and modular arithmetic through windowing techniques and more adaptive placement of uncomputing steps, and improve over previous quantum circuits for modular inversion by reformulating the binary Euclidean algorithm.

## Key claims (as reported)
- Overall, we obtain an affine Weierstrass point addition circuit that has lower depth and uses fewer T gates than previous circuits.
- While previous work mostly focuses on minimizing the total number of qubits, we present various trade-offs between different cost metrics including the number of qubits, circuit depth and T -gate count.
- Finally, we provide a full implementation of point addition in the Q# quantum programming language that allows unit tests and automatic quantum resource estimation for all components.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2001.09580v1.pdf`
