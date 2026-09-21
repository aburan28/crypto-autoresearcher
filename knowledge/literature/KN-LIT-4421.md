---
id: KN-LIT-4421
type: literature
title: "Improved On-line/Off-line Signature Schemes"
authors:
  - "Adi Shamir"
  - "Yael Tauman"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [hash, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The notion of on-line/off-line signature schemes was introduced in 1990 by Even, Goldreich and Micali. They presented a general method for converting any signature scheme into an on-line/off-line signature scheme, but their method is not very practical as it increases the length of each signature by a quadratic factor.

## Key claims (as reported)
- In this paper we use the recently introduced notion of a trapdoor hash function to develop a new paradigm called hash-sign-switch, which can convert any signature scheme into a highly efficient on-line/off-line signature scheme: In its recommended implementation, the on-line complexity is equivalent to about 0.1 modular multiplications, and the size of each signature increases only by a factor of two.
- In addition, the new paradigm enhances the security of the original signature scheme since it is only used to sign random strings chosen off-line by the signer.
- This makes the converted scheme secure against adaptive chosen message attacks even if the original scheme is secure only against generic chosen message attacks or against random message attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/21390353 (1).pdf`
- `downloads/21390353 (2).pdf`
- `downloads/21390353.pdf`
