---
id: KN-LIT-4596
type: literature
title: "Key-Privacy in Public-Key Encryption"
authors:
  - "M. Bellare"
  - "A. Boldyreva"
  - "A. Desai"
  - "D. Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We consider a novel security requirement of encryption schemes that we call “key-privacy” or “anonymity”. It asks that an eavesdropper in possession of a ciphertext not be able to tell which specific key, out of a set of known public keys, is the one under which the ciphertext was created, meaning the receiver is anonymous from the point of view of the adversary.

## Key claims (as reported)
- We investigate the anonymity of known encryption schemes.
- We prove that the El Gamal scheme provides anonymity under chosen-plaintext attack assuming the Decision Diffie-Hellman problem is hard and that the Cramer-Shoup scheme provides anonymity under chosen-ciphertext attack under the same assumption.
- We also consider anonymity for trapdoor permutations.
- Known attacks indicate that the RSA trapdoor permutation is not anonymous and neither are the standard encryption schemes based on it.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/22480568 (1).pdf`
- `downloads/22480568 (2).pdf`
- `downloads/22480568.pdf`
