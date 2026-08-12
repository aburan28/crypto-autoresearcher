---
id: KN-LIT-4116
type: literature
title: "Gladius: LWR based efficient hybrid public key encryption with distributed decryption"
authors:
  - "Kelong Cong"
  - "Daniele Cozzo"
  - "Varun Maram"
  - "Nigel P. Smart"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, lattice, pqc, zk-proof]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Standard hybrid encryption schemes based on the KEMDEM framework are hard to implement efficiently in a distributed manner whilst maintaining the CCA security property of the scheme. This is because the DEM needs to be decrypted under the key encapsulated by the KEM, before the whole ciphertext is declared valid.

## Key claims (as reported)
- In this paper we present a new variant of the KEM-DEM framework, closely related to Tag-KEMs, which sidesteps this issue.
- We then present a postquantum KEM for this framework based on Learning-with-Rounding, which is designed specifically to have fast distributed decryption.
- Our combined construction of a hybrid encryption scheme with Learningwith-Rounding based KEM, called Gladius, is closely related to the NIST Round 3 candidate called Saber.
- Finally, we give a prototype distributed implementation that achieves a decapsulation time of 4.99 seconds for three parties.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/130900030 (1).pdf`
- `downloads/130900030.pdf`
