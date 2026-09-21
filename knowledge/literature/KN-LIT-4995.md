---
id: KN-LIT-4995
type: literature
title: "Multi-Instance Security and its Application to Password-Based Cryptography"
authors:
  - "Mihir Bellare"
  - "Thomas Ristenpart"
  - "Stefano Tessaro"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
This paper develops a theory of multi-instance (mi) security and applies it to provide the first proof-based support for the classical practice of salting in password-based cryptography. Mi-security comes into play in settings (like password-based cryptography) where it is computationally feasible to compromise a single instance, and provides a second line of defense, aiming to ensure (in the case of passwords, via salting) that the effort to compromise all of some large number m of instances grows linearly with m.

## Key claims (as reported)
- The first challenge is definitions, where we suggest LORX-security as a good metric for mi security of encryption and support this claim by showing it implies other natural metrics, illustrating in the process that even lifting simple results from the si setting to the mi one calls for new techniques.
- Next we provide a composition-based framework to transfer standard single-instance (si) security to mi-security with the aid of a key-derivation function.
- Analyzing password-based KDFs from the PKCS#5 standard to show that they meet our indifferentiability-style mi-security definition for KDFs, we are able to conclude with the first proof that per password salts amplify mi-security as hoped in practice.
- We believe that mi-security is of interest in other domains and that this work provides the foundation for its further theoretical development and practical application.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/74170310 (1).pdf`
- `downloads/74170310 (2).pdf`
- `downloads/74170310 (3).pdf`
- `downloads/74170310 (4).pdf`
- `downloads/74170310 (5).pdf`
- `downloads/74170310.pdf`
