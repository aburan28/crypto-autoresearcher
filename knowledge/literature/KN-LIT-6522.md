---
id: KN-LIT-6522
type: literature
title: "Security of the AES with a Secret S-box"
authors:
  - "Tyge Tiessen"
  - "Lars R. Knudsen"
  - "Stefan Kölbl"
  - "Martin M. Lauridsen"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
How does the security of the AES change when the S-box is replaced by a secret S-box, about which the adversary has no knowledge? Would it be safe to reduce the number of encryption rounds?

## Key claims (as reported)
- In this paper, we demonstrate attacks based on integral cryptanalysis which allow to recover both the secret key and the secret S-box for respectively four, five, and six rounds of the AES.
- Despite the significantly larger amount of secret information which an adversary needs to recover, the attacks are very efficient with time/data complexities of 217 /216 , 238 /240 and 290 /264 , respectively.
- Another interesting aspect of our attack is that it works both as chosen plaintext and as chosen ciphertext attack.
- Surprisingly, the chosen ciphertext variant has a significantly lower time complexity in the attacks on four and five round, compared to the respective chosen plaintext attacks.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/85400122 (4).pdf`
- `downloads/85400122 (5).pdf`
