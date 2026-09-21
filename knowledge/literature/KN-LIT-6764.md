---
id: KN-LIT-6764
type: literature
title: "Speed-Stacking: Fast Sublinear Zero-Knowledge Proofs for Disjunctions"
authors:
  - "Aarushi Goel"
  - "Mathias Hall-Andersen"
  - "Gabriel Kaptchuk"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Building on recent compilers for efficient disjunctive composition (e.g. an OR of multiple clauses) of zero-knowledge proofs (e.g. [EUROCRYPT’22]) we propose a new compiler that, when applied to sublinear-sized proofs, can result in sublinear-size disjunctive zero-knowledge with sublinear proving times (without meaningfully increasing proof sizes).

## Key claims (as reported)
- Our key observation is that simulation in sublinear-size zero-knowledge proof systems can be much faster (both concretely and asymptotically) than the honest prover.
- We study applying our compiler to two classes of O(log n)-round protocols: interactive oracle proofs, specifically Aurora [EUROCRYPT’19] and Fractal [EUROCRYPT’20], and folding arguments, specifically Compressed Σprotocols [CR-YPTO’20, CRYPTO’21] and Bulletproofs [S&P’18].
- This study validates that the compiler can lead to significant savings.
- For example, applying our compiler to Fractal enables us to prove a disjunction of l clauses, each of size N , with only O((N + l) · polylog(N )) computation, versus O(lN · polylog(N )) when proving the disjunction directly.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/14004256 (1).pdf`
- `downloads/14004256.pdf`
