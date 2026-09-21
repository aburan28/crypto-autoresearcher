---
id: KN-LIT-3653
type: literature
title: "Efficient Zero-Knowledge Proofs of Non-Algebraic Statements with Sublinear Amortized Cost"
authors:
  - "Zhangxiang Hu"
  - "Payman Mohassel"
  - "Mike Rosulek"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, mpc, pairing, quantum, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a zero-knowledge proof system in which a prover holds a large dataset M and can repeatedly prove NP relations about that dataset. That is, for any (public) relation R and x, the prover can prove that ∃w : R(M, x, w) = 1.

## Key claims (as reported)
- After an initial setup phase (which depends only on M ), each proof requires only a constant number of rounds and has communication/computation cost proportional to that of a random-access machine (RAM) implementation of R, up to polylogarithmic factors.
- In particular, the cost per proof in many applications is sublinear in |M |.
- Additionally, the storage requirement between proofs for the verifier is constant.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92160255 (1).pdf`
- `downloads/92160255 (2).pdf`
- `downloads/92160255.pdf`
