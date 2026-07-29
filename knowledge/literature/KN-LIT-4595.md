---
id: KN-LIT-4595
type: literature
title: "Key-Insulated Public Key Cryptosystems"
authors:
  - "Yevgeniy Dodis"
  - "Jonathan Katz"
  - "Shouhuai Xu"
  - "Moti Yung"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, mpc, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
Cryptographic computations (decryption, signature generation, etc.) are often performed on a relatively insecure device (e.g., a mobile device or an Internet-connected host) which cannot be trusted to maintain secrecy of the private key. We propose and investigate the notion of key-insulated security whose goal is to minimize the damage caused by secret-key exposures.

## Key claims (as reported)
- In our model, the secret key(s) stored on the insecure device are refreshed at discrete time periods via interaction with a physically-secure — but computationally-limited — device which stores a “master key”.
- All cryptographic computations are still done on the insecure device, and the public key remains unchanged.
- In a (t, N )-keyinsulated scheme, an adversary who compromises the insecure device and obtains secret keys for up to t periods of his choice is unable to violate the security of the cryptosystem for any of the remaining N − t periods.
- Furthermore, the scheme remains secure (for all time periods) against an adversary who compromises only the physically-secure device.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/dodis-ec02 (1).pdf`
- `downloads/dodis-ec02 (2).pdf`
- `downloads/dodis-ec02.pdf`
