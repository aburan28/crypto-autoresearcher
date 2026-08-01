---
id: KN-LIT-3652
type: literature
title: "Efficient Zero-Knowledge Proof of Algebraic and Non-Algebraic Statements with Applications to Privacy Preserving Credentials"
authors:
  - "Melissa Chase"
  - "Chaya Ganesh"
  - "Payman Mohassel"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, mpc, pairing, quantum, rsa, survey, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Practical anonymous credential systems are generally built around sigma-protocol ZK proofs. This requires that credentials be based on specially formed signatures.

## Key claims (as reported)
- Here we ask whether we can instead use a standard (say, RSA, or (EC)DSA) signature that includes formatting and hashing messages, as a credential, and still provide privacy.
- Existing techniques do not provide efficient solutions for proving knowledge of such a signature: On the one hand, ZK proofs based on garbled circuits (Jawurek et al.
- 2013) give efficient proofs for checking formatting of messages and evaluating hash functions.
- On the other hand they are expensive for checking algebraic relations such as RSA or discrete-log, which can be done efficiently with sigma protocols.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/98160485 (1).pdf`
- `downloads/98160485.pdf`
