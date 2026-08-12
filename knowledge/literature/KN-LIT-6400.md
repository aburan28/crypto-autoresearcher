---
id: KN-LIT-6400
type: literature
title: "Secret Handshakes from CA-Oblivious Encryption"
authors:
  - "Claude Castelluccia"
  - "Stanislaw Jarecki"
  - "Gene Tsudik"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [protocol, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Secret handshakes were recently introduced [BDS+ 03] to allow members of the same group to authenticate each other secretly, in the sense that someone who is not a group member cannot tell, by engaging some party in the handshake protocol, whether that party is a member of this group. On the other hand, any two parties who are members of the same group will recognize each other as members.

## Key claims (as reported)
- Thus, a secret handshake protocol can be used in any scenario where group members need to identify each other without revealing their group affiliations to outsiders.
- The work of [BDS+ 03] constructed secret handshakes secure under the Bilinear Diffie-Hellman (BDH) assumption in the Random Oracle Model (ROM).
- We show how to build secret handshake protocols secure under a more standard cryptographic assumption of Computational Diffie Hellman (CDH), using a novel tool of CA-oblivious public key encryption, which is an encryption scheme s.t. neither the public key nor the ciphertext reveal any information about the Certification Authority (CA) which certified the public key.
- We construct such CA-oblivious encryption, and hence a handshake scheme, based on CDH (in ROM).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/33290290 (1).pdf`
- `downloads/33290290 (2).pdf`
- `downloads/33290290 (3).pdf`
- `downloads/33290290.pdf`
