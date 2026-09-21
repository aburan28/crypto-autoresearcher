---
id: KN-LIT-7189
type: literature
title: "Toward a Fully Secure Authenticated Encryption Scheme From a Pseudorandom Permutation"
authors:
  - "Wonseok Choi"
  - "Byeonghak Lee"
  - "Jooyoung Lee"
  - "Yeongmin Lee"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, mov-fr, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose a new block cipher-based authenticated encryption scheme, dubbed the Synthetic Counter with Masking (SCM) mode. SCM follows the NSIV paradigm proposed by Peyrin and Seurin (CRYPTO 2016), where a keyed hash function accepts a nonce N with associated data and a message, yielding an authentication tag T , and then the message is encrypted by a counter-like mode using both T and N .

## Key claims (as reported)
- Here we move one step further by encrypting nonces; in the encryption part, the inputs to the block cipher are determined by T , counters, and an encrypted nonce, and all its outputs are also masked by an (additional) encrypted nonce, yielding keystream blocks.
- As a result, we obtain, for the first time, a block cipher-based authenticated encryption scheme of rate 1/2 that provides n-bit security with respect to the query complexity (ignoring the influence of message length) in the nonce-respecting setting, and at the same time guarantees graceful security degradation in the faulty nonce model, when the underlying nbit block cipher is modeled as a secure pseudorandom permutation.
- Seen as a slight variant of GCM-SIV, SCM is also parallelizable and inversefree, and its performance is still comparable to GCM-SIV.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900109 (1).pdf`
- `downloads/130900109.pdf`
