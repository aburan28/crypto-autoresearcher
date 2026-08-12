---
id: KN-LIT-7521
type: literature
title: "Witness Encryption and Null-IO from Evasive LWE"
authors:
  - "Vinod Vaikuntanathan"
  - "Hoeteck Wee"
  - "Daniel Wichs"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, pairing, pqc, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Witness encryption (WE) allows us to use an arbitrary NP statement x as a public key to encrypt a message, and the witness w serves as a decryption key. Security ensures that, when the statement x is false, the encrypted message remains computationally hidden.

## Key claims (as reported)
- WE appears to be significantly weaker than indistinguishability obfuscation (iO).
- Indeed, WE is closely related to a highly restricted form of iO that only guarantees security for null circuits (null iO).
- However, all current approaches towards constructing WE under nice assumptions go through iO.
- Such constructions are quite complex and are unlikely to lead to practically instantiable schemes.

## Relevance to this program
Relevant to pairing-based reductions and endomorphism speedups (MOV/Frey-Rück special cases, GLV/GLS) that bound which curve classes are safe baselines.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/137910169 (1).pdf`
- `downloads/137910169.pdf`
