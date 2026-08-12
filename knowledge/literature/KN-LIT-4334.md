---
id: KN-LIT-4334
type: literature
title: "Identity-based Broadcast Encryption with Efficient Revocation"
authors:
  - "Aijun Ge"
  - "Puwen Wei"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, quantum]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Identity-based broadcast encryption (IBBE) is an effective method to protect the data security and privacy in multi-receiver scenarios, which can make broadcast encryption more practical. This paper further expands the study of scalable revocation methodology in the setting of IBBE, where a key authority releases a key update material periodically in such a way that only non-revoked users can update their decryption keys.

## Key claims (as reported)
- Following the binary tree data structure approach, a concrete instantiation of revocable IBBE scheme is proposed using asymmetric pairings of prime order bilinear groups.
- Moreover, this scheme can withstand decryption key exposure, which is proven to be semi-adaptively secure under chosen plaintext attacks in the standard model by reduction to static complexity assumptions.
- In particular, the proposed scheme is very efficient both in terms of computation costs and communication bandwidth, as the ciphertext size is constant, regardless of the number of recipients.
- To demonstrate the practicality, it is further implemented in Charm, a framework for rapid prototyping of cryptographic primitives.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/114420190 (1).pdf`
- `downloads/114420190.pdf`
