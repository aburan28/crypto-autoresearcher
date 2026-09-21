---
id: KN-LIT-4352
type: literature
title: "Immunizing Encryption Schemes from Decryption Errors"
authors:
  - "Cynthia Dwork"
  - "Moni Naor"
  - "Omer Reingold"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, fhe, lattice, provable-security]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We provide methods for transforming an encryption scheme susceptible to decryption errors into one that is immune to these errors. Immunity to decryption errors is vital when constructing non-malleable and chosen ciphertext secure encryption schemes via current techniques; in addition, it may help defend against certain cryptanalytic techniques, such as the attack of Proos [33] on the NTRU scheme.

## Key claims (as reported)
- When decryption errors are very infrequent, our transformation is extremely simple and efficient, almost free.
- To deal with significant error probabilities, we apply amplification techniques translated from a related information theoretic setting.
- These techniques allow us to correct even very weak encryption schemes where in addition to decryption errors, an adversary has substantial probability of breaking the scheme by decrypting random messages (without knowledge of the secret key).
- In other words, under these weak encryption schemes, the only guaranteed difference between the legitimate recipient and the adversary is in the frequency of decryption errors.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/dnr (1).pdf`
- `downloads/dnr (2).pdf`
- `downloads/dnr.pdf`
