---
id: KN-LIT-3580
type: literature
title: "Efficient KDM-CCA Secure Public-Key Encryption for Polynomial Functions"
authors:
  - "Shuai Han"
  - "Shengli Liu"
  - "Lin Lyu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [mpc, pairing, provable-security, symmetric, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
KDM[F]-CCA secure public-key encryption (PKE) protects the security of message f (sk), with f ∈ F , that is computed directly from the secret key, even if the adversary has access to a decryption oracle. An efficient KDM[Faff ]-CCA secure PKE scheme for affine functions was proposed by Lu, Li and Jia (LLJ, EuroCrypt2015).

## Key claims (as reported)
- We point out that their security proof cannot go through based on the DDH assumption.
- In this paper, we introduce a new concept Authenticated Encryption with Auxiliary-Input AIAE and define for it new security notions dealing with related-key attacks, namely IND-RKA security and weak INT-RKA security.
- We also construct such an AIAE w.r.t. a set of restricted affine functions from the DDH assumption.
- With our AIAE, – we construct the first efficient KDM[Faff ]-CCA secure PKE w.r.t. affine functions with compact ciphertexts, which consist only of a constant number of group elements; d – we construct the first efficient KDM[Fpoly ]-CCA secure PKE w.r.t. polynomial functions of bounded degree d with almost compact ciphertexts, and the number of group elements in a ciphertext is polynomial in d, independent of the security parameter.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031136 (1).pdf`
- `downloads/10031136.pdf`
