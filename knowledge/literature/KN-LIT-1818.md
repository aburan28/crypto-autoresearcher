---
id: KN-LIT-1818
type: literature
title: "Pseudo-Oil Subspaces and the Geometry of Underdetermined MQ Problems"
authors:
  - "Massimo Ostuzzi"
year: 2026
venue: "IACR Cryptology ePrint Archive"
identifiers:
  eprint: "iacr:2026/1122"
  doi: null
  arxiv: null
  url: "https://eprint.iacr.org/2026/1122"
tags: [finite-field, groebner, lattice, pairing, pqc, signature, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The concrete security of multivariate post-quantum signature schemes is coming under increasing scrutiny as the NIST standardisation process for additional signatures approaches its final stages. Among the leading candidates, the security of MAYO and QR-UOV relies on the hardness of the underdetermined multivariate quadratic (MQ) problem.

## Key claims (as reported)
- This work revisits Hashimoto’s algorithm for solving underdetermined systems of MQ equations, reinterpreting it as a computation of a pseudooil subspace.
- In light of this geometric point of view, we design a new algorithm that, by computing richer pseudo-oil structures, distributes algebraic work across more than two Gröbner Basis steps, subdividing the initial MQ problem into multiple subproblems that can be solved separately, while linearising multiple equations.
- Optimising a set of discrete parameters, we select the best trade-off between algebraic solving and combinatorial search.
- Concretely, our approach lowers the cost of the direct attack against Security Level I parameter sets of MAYO and QR-UOV by 8 and 10 bits, respectively.

## Relevance to this program
Directly relevant to the ECDLP algebraic-attack line (index calculus / summation polynomials / Gröbner methods). Novelty checks for decomposition-based proposals must cite this before claiming new mechanisms. Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/2026-1122.pdf`
