---
id: KN-LIT-5433
type: literature
title: "On the CCA Compatibility of Public-Key Infrastructure"
authors:
  - "Dakshita Khurana"
  - "Brent Waters"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this work, we put forth the notion of compatibility of any key generation or setup algorithm. We focus on the specific case of encryption, and say that a key generation algorithm KeyGen is X-compatible (for X ∈ {CPA, CCA1, CCA2}) if there exist encryption and decryption algorithms that together with KeyGen, result in an X-secure public-key encryption scheme.

## Key claims (as reported)
- We study the following question: Is every CPA-compatible key generation algorithm also CCA-compatible?
- We obtain the following answers: – Every sub-exponentially CPA-compatible KeyGen algorithm is CCA1-compatible, assuming the existence of hinting PRGs and subexponentially secure keyless collision resistant hash functions. – Every sub-exponentially CPA-compatible KeyGen algorithm is also CCA2-compatible, assuming the existence of non-interactive CCA2 secure commitments, in addition to sub-exponential security of the assumptions listed in the previous bullet.
- Here, sub-exponentially CPA-compatible KeyGen refers to any key generation algorithm for which there exist encryption and decryption algorithms that result in a CPA-secure public-key encryption scheme against sub-exponential adversaries.
- This gives a way to perform CCA secure encryption given any public key infrastructure that has been established with only (sub-exponential) CPA security in mind.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/127110122 (1).pdf`
- `downloads/127110122.pdf`
