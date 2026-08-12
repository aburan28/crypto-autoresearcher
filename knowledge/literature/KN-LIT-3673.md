---
id: KN-LIT-3673
type: literature
title: "Encoding-Free ElGamal Encryption Without Random Oracles"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [dlp, hash, provable-security, rsa]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
ElGamal encryption is the most extensively used alternative to RSA. Easily adaptable to many kinds of cryptographic groups, ElGamal encryption enjoys homomorphic properties while remaining semantically secure providing that the DDH assumption holds on the chosen group.

## Key claims (as reported)
- Its practical use, unfortunately, is intricate: plaintexts have to be encoded into group elements before encryption, thereby requiring awkward and ad hoc conversions which strongly limit the number of plaintext bits or may partially destroy homomorphicity.
- Getting rid of the group encoding (e.g., with a hash function) is known to ruin the standard model security of the system.
- This paper introduces a new alternative to group encodings and hash functions which remains fully compatible with standard model security properties.
- Partially homomorphic in customizable ways, our encryptions are comparable to plain ElGamal in efficiency, and boost the encryption ratio from about 13 for classical parameters to the optimal value of 2.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/39580093 (1).pdf`
- `downloads/39580093 (2).pdf`
- `downloads/39580093 (3).pdf`
- `downloads/39580093.pdf`
