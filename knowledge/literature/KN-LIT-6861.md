---
id: KN-LIT-6861
type: literature
title: "Sublinear Zero-Knowledge Arguments for RAM Programs"
authors:
  - "Payman Mohassel"
  - "Mike Rosulek"
  - "Alessandra Scafuro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We describe a new succinct zero-knowledge argument protocol with the following properties. The prover commits to a large dataset M , and can thereafter prove many statements of the form ∃w : Ri (M, w) = 1, where Ri is a public function.

## Key claims (as reported)
- The protocol is succinct in the sense that the cost for the verifier (in computation & communication) does not depend on |M |, not even in any initialization phase.
- In each proof, the computation/communication cost for both the prover and the verifier is proportional only to the running time of an oblivious RAM program implementing Ri (in particular, this can be sublinear in |M |).
- The only costs that scale with |M | are the computational costs of the prover in a one-time initial commitment to M .
- Known sublinear zero-knowledge proofs either require an initialization phase where the work of the verifier is proportional to |M | and are therefore sublinear only in an amortized sense, or require that the computational cost for the prover is proportional to |M | upon each proof.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10210334 (1).pdf`
- `downloads/10210334.pdf`
