---
id: KN-LIT-2513
type: literature
title: "Analysis and Improvements of NTRU Encryption Paddings"
authors:
  - "Phong Q. Nguyen"
  - "David Pointcheval"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [lattice, provable-security, quantum, rsa, survey]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
NTRU is an efficient patented public-key cryptosystem proposed in 1996 by Hoffstein, Pipher and Silverman. Although no devastating weakness of NTRU has been found, Jaulmes and Joux presented at Crypto ’00 a simple chosen-ciphertext attack against NTRU as originally described.

## Key claims (as reported)
- This led Hoffstein and Silverman to propose three encryption padding schemes more or less based on previous work by Fujisaki and Okamoto on strengthening encryption schemes.
- It was claimed that these three padding schemes made NTRU secure against adaptive chosen-ciphertext attacks (IND-CCA2) in the random oracle model.
- In this paper, we analyze and compare the three NTRU schemes obtained.
- It turns out that the first one is not even semantically secure (INDCPA).

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/24420210 (1).pdf`
- `downloads/24420210 (2).pdf`
- `downloads/24420210.pdf`
