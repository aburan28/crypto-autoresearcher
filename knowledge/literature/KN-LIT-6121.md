---
id: KN-LIT-6121
type: literature
title: "Random Oracles and Auxiliary Input"
authors:
  - "Dominique Unruh"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, rsa, signature, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We introduce a variant of the random oracle model where oracledependent auxiliary input is allowed. In this setting, the adversary gets an auxiliary input that can contain information about the random oracle.

## Key claims (as reported)
- Using simple examples we show that this model should be preferred over the classical variant where the auxiliary input is independent of the random oracle.
- In the presence of oracle-dependent auxiliary input, the most important proof technique in the random oracle model—lazy sampling—does not apply directly.
- We present a theorem and a variant of the lazy sampling technique that allows one to perform proofs in the new model almost as easily as in the old one.
- As an application of our approach and to illustrate how existing proofs can be adapted, we prove that RSA-OAEP is IND-CCA2 secure in the random oracle model with oracle-dependent auxiliary input.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/46220206 (1).pdf`
- `downloads/46220206 (2).pdf`
- `downloads/46220206 (3).pdf`
- `downloads/46220206.pdf`
