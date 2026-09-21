---
id: KN-LIT-2779
type: literature
title: "Bounded Key-Dependent Message Security"
authors:
  - "Boaz Barak"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [fhe, lattice, pairing, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We construct the rst public-key encryption scheme that is proven secure (in the standard model, under standard assumptions) even when the attacker gets access to encryptions of arbitrary e cient functions of the secret key. Speci cally, under either the DDH or LWE assumption, and for arbitrary but xed polynomials L and N , we obtain a public-key encryption scheme that resists key-dependent message (KDM) attacks for up to N (k) public keys and functions of circuit size up to L(k), where k denotes the size of the secret key.

## Key claims (as reported)
- We call such a scheme bounded KDM secure.
- Moreover, we show that our scheme su ces for one of the important applications of KDM security: ability to securely instantiate symbolic protocols with axiomatic proofs of security.
- We also observe that any fully homomorphic encryption scheme that additionally enjoys circular security and circuit privacy is fully KDM secure in the sense that its algorithms can be independent of the polynomials L and N as above.
- Thus, the recent fully homomorphic encryption scheme of Gentry (STOC 2009) is fully KDM secure under certain non-standard hardness assumptions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/66320244 (1).pdf`
- `downloads/66320244 (2).pdf`
- `downloads/66320244 (3).pdf`
- `downloads/66320244.pdf`
