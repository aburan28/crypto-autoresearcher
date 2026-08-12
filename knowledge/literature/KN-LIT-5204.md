---
id: KN-LIT-5204
type: literature
title: "Non-Interactive Zero-Knowledge Proofs for Composite Statements"
authors:
  - "Shashank Agrawal"
  - "Chaya Ganesh"
  - "Payman Mohassel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, elliptic-curve, hash, mov-fr, mpc, pairing, quantum, signature, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The two most common ways to design non-interactive zeroknowledge (NIZK) proofs are based on Sigma protocols and QAP-based SNARKs. The former is highly efficient for proving algebraic statements while the latter is superior for arithmetic representations.

## Key claims (as reported)
- Motivated by applications such as privacy-preserving credentials and privacy-preserving audits in cryptocurrencies, we study the design of NIZKs for composite statements that compose algebraic and arithmetic statements in arbitrary ways.
- Specifically, we provide a framework for proving statements that consist of ANDs, ORs and function compositions of a mix of algebraic and arithmetic components.
- This allows us to explore the full spectrum of trade-offs between proof size, prover cost, and CRS size/generation cost.
- This leads to proofs for statements of the form: knowledge of x such that SHA(g x ) = y for some public y where the prover’s work is 500 times fewer exponentiations compared to a QAP-based SNARK at the cost of increasing the proof size to 2404 group and field elements.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10993251 (1).pdf`
- `downloads/10993251.pdf`
