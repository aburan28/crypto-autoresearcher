---
id: KN-LIT-5149
type: literature
title: "New Security Results on Encrypted Key Exchange"
authors:
  - "Emmanuel Bresson"
  - "Olivier Chevassut"
  - "David Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, protocol, provable-security, quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Schemes for encrypted key exchange are designed to provide two entities communicating over a public network, and sharing a (short) password only, with a session key to be used to achieve data integrity and/or message confidentiality. An example of a very efficient and “elegant” scheme for encrypted key exchange considered for standardization by the IEEE P1363 Standard working group is AuthA.

## Key claims (as reported)
- This scheme was conjectured secure when the symmetric-encryption primitive is instantiated via either a cipher that closely behaves like an “ideal cipher”, or a mask generation function that is the product of the message with a hash of the password.
- While the security of this scheme in the former case has been recently proven, the latter case was still an open problem.
- For the first time we prove in this paper that this scheme is secure under the assumptions that the hash function closely behaves like a random oracle and that the computational Diffie-Hellman problem is difficult.
- Furthermore, since Denial-of-Service (DoS) attacks have become a common threat we enhance AuthA with a mechanism to protect against them.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/29470143 (1).pdf`
- `downloads/29470143 (2).pdf`
- `downloads/29470143.pdf`
