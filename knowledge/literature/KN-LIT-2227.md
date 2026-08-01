---
id: KN-LIT-2227
type: literature
title: "A Signature Scheme as Secure as the Diffie-Hellman Problem"
authors:
  - "Eu-Jin Goh"
  - "StanisÃlaw Jarecki"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, pairing, provable-security, rsa, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We show a signature scheme whose security is tightly related to the Computational Diffie-Hellman (CDH) assumption in the Random Oracle Model. Existing discrete-log based signature schemes, such as ElGamal, DSS, and Schnorr signatures, either require non-standard assumptions, or their security is only loosely related to the discrete logarithm (DL) assumption using Pointcheval and Stern’s “forking” lemma.

## Key claims (as reported)
- Since the hardness of the CDH problem is widely believed to be closely related to the hardness of the DL problem, the signature scheme presented here offers better security guarantees than existing discrete-log based signature schemes.
- Furthermore, the new scheme has comparable efficiency to existing schemes.
- The signature scheme was previously proposed in the cryptographic literature on at least two occasions.
- However, no security analysis was done, probably because the scheme was viewed as a slight modification of Schnorr signatures.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/26560401 (1).pdf`
- `downloads/26560401 (2).pdf`
- `downloads/26560401.pdf`
