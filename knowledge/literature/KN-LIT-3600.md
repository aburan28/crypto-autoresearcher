---
id: KN-LIT-3600
type: literature
title: "Efficient Noninteractive Certification of RSA Moduli and Beyond"
authors:
  - "Sharon Goldberg"
  - "Leonid Reyzin"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [factoring, provable-security, rsa, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In many applications, it is important to verify that an RSA public key (N, e) specifies a permutation over the entire space ZN , in order to prevent attacks due to adversarially-generated public keys. We design and implement a simple and efficient noninteractive zero-knowledge protocol (in the random oracle model) for this task.

## Key claims (as reported)
- Applications concerned about adversarial key generation can just append our proof to the RSA public key without any other modifications to existing code or cryptographic libraries.
- Users need only perform a one-time verification of the proof to ensure that raising to the power e is a permutation of the integers modulo N .
- For typical parameter settings, the proof consists of nine integers modulo N ; generating the proof and verifying it both require about nine modular exponentiations.
- We extend our results beyond RSA keys and also provide efficient noninteractive zero-knowledge proofs for other properties of N , which can be used to certify that N is suitable for the Paillier cryptosystem, is a product of two primes, or is a Blum integer.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/119210414 (1).pdf`
- `downloads/119210414.pdf`
