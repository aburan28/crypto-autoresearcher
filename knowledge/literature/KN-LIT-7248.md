---
id: KN-LIT-7248
type: literature
title: "Trading One-Wayness against Chosen-Ciphertext Security in Factoring-Based Encryption"
authors:
  - "Pascal Paillier"
  - "Jorge L. Villar"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [pairing, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We revisit a long-lived folklore impossibility result for factoring-based encryption and properly establish that reaching maximally secure one-wayness (i.e. equivalent to factoring) and resisting chosenciphertext attacks (CCA) are incompatible goals for single-key cryptosystems. We pinpoint two tradeoffs between security notions in the standard model that have always remained unnoticed in the Random Oracle (RO) model.

## Key claims (as reported)
- These imply that simple RO-model schemes such as Rabin/RW-SAEP[+]/OAEP[+][+], EPOC-2, etc. admit no instantiation in the standard model which CCA security is equivalent to factoring via a key-preserving reduction.
- We extend this impossibility to arbitrary reductions assuming non-malleable key generation, a property capturing the intuition that factoring a modulus n should not be any easier when given a factoring oracle for moduli n0 6= n.
- The only known countermeasures against our impossibility results, besides malleable key generation, are the inclusion of an additional random string in the public key, or encryption twinning as in Naor-Yung or Dolev-Dwork-Naor constructions.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/42840253 (1).pdf`
- `downloads/42840253 (2).pdf`
- `downloads/42840253 (3).pdf`
- `downloads/42840253.pdf`
