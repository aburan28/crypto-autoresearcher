---
id: KN-LIT-2852
type: literature
title: "CCA-Secure Keyed-Fully Homomorphic Encryption"
authors:
  - "Junzuo Lai"
  - "Robert H. Deng"
  - "Changshe Ma"
  - "Kouichi Sakurai"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, pairing]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
To simultaneously achieve CCA security and homomorphic property for encryption, Emura et al. introduced a new cryptographic primitive named keyed-homomorphic encryption, in which homomorphic ciphertext manipulations can only be performed by someone holding a devoted evaluation key which, by itself, does not enable decryption. A keyed-homomorphic encryption scheme should provide CCA2 security when the evaluation key is unavailable to the adversary and remain CCA1-secure when the evaluation key is exposed.

## Key claims (as reported)
- While existing keyedhomomorphic encryption schemes only allow simple computations on encrypted data, our goal is to construct CCA-secure keyed-fully homomorphic encryption (keyed-FHE) capable of evaluating any functions on encrypted data with an evaluation key.
- In this paper, we first introduce a new primitive called convertible identitybased fully homomorphic encryption (IBFHE), which is an IBFHE with an additional transformation functionality, and define its security notions.
- Then, we present a generic construction of CCA-secure keyedFHE from IND-sID-CPA-secure convertible IBFHE and strongly EUFCMA-secure signature.
- Finally, we propose a concrete construction of IND-sID-CPA-secure convertible IBFHE, resulting in the first CCA-secure keyed-FHE scheme in the standard model.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/96140160 (1).pdf`
- `downloads/96140160 (2).pdf`
- `downloads/96140160 (3).pdf`
- `downloads/96140160 (4).pdf`
- `downloads/96140160.pdf`
