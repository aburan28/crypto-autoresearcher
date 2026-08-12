---
id: KN-LIT-7236
type: literature
title: "Towards Tightly Secure Lattice Short Signature and Id-Based Encryption"
authors:
  - "Xavier Boyen"
  - "Qinyi Li"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, finite-field, hash, lattice, pairing, provable-security, quantum, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Constructing short signatures with tight security from standard assumptions is a long-standing open problem. We present an adaptively secure, short (and stateless) signature scheme, featuring a constant security loss relative to a conservative hardness assumption, Short Integer Solution (SIS), and the security of a concretely instantiated pseudorandom function (PRF).

## Key claims (as reported)
- This gives a class of tightly secure short lattice signature schemes whose security is based on SIS and the underlying assumption of the instantiated PRF.
- Our signature construction further extends to give a class of tightly and adaptively secure “compact” Identity-Based Encryption (IBE) schemes, reducible with constant security loss from Regev’s vanilla Learning With Errors (LWE) hardness assumption and the security of a concretely instantiated PRF.
- Our approach is a novel combination of a number of techniques, including Katz and Wang signature, Agrawal et al. latticebased secure IBE, and Boneh et al. key-homomorphic encryption.
- Our results, at the first time, eliminate the dependency between the number of adversary’s queries and the security of short signature/IBE schemes in the context of lattice-based cryptography.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/10031179 (1).pdf`
- `downloads/10031179.pdf`
