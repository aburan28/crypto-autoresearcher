---
id: KN-LIT-5778
type: literature
title: "PointProofs, Revisited"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Vector commitments allow a user to commit to a vector of length n using a constant-size commitment while being able to locally open the commitment to individual vector coordinates. Importantly, the size of position-wise openings should be independent of the dimension n.

## Key claims (as reported)
- Gorbunov, Reyzin, Wee, and Zhang recently proposed PointProofs (CCS 2020), a vector commitment scheme that supports non-interactive aggregation of proofs across multiple commitments, allowing to drastically reduce the cost of block propagation in blockchain smart contracts.
- Gorbunov et al. provide a security analysis combining the algebraic group model and the random oracle model, under the weak n-bilinear DiffieHellman Exponent assumption (n-wBDHE) assumption.
- In this work, we propose a novel analysis that does not rely on the algebraic group model.
- We prove the security in the random oracle model under the nDiffie-Hellman Exponent (n-DHE) assumption, which is implied by the n-wBDHE assumption considered by Gorbunov et al.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910314 (1).pdf`
- `downloads/137910314.pdf`
