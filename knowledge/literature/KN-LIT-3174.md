---
id: KN-LIT-3174
type: literature
title: "Correlated-Input Secure Hash Functions"
authors:
  - "Vipul Goyal"
  - "Adam O’Neill⋆"
  - "Vanishree Rao⋆"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, pairing, provable-security, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We undertake a general study of hash functions secure under correlated inputs, meaning that security should be maintained when the adversary sees hash values of many related high-entropy inputs. Such a property is satisfied by a random oracle, and its importance is illustrated by study of the “avalanche effect,” a well-known heuristic in cryptographic hash function design.

## Key claims (as reported)
- One can interpret “security” in different ways: e.g., asking for one-wayness or that the hash values look uniformly and independently random; the latter case can be seen as a generalization of correlation-robustness introduced by Ishai et al.
- We give specific applications of these notions to password-based login and efficient search on encrypted data.
- Our main construction achieves them (without random oracles) for inputs related by polynomials over the input space (namely Zp ), based on corresponding variants of the q-Diffie Hellman Inversion assumption.
- Additionally, we show relations between correlated-input secure hash functions and cryptographic primitives secure under related-key attacks.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/65970180 (1).pdf`
- `downloads/65970180 (2).pdf`
- `downloads/65970180 (3).pdf`
- `downloads/65970180.pdf`
