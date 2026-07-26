---
id: KN-LIT-4583
type: literature
title: "Key Recovery Attack against 2.5-round π-Cipher"
authors:
  - "Christina Boura"
  - "Avik Chakraborti"
  - "Gaëtan Leurent"
  - "Goutam Paul"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, protocol, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
In this paper, we propose a guess and determine attack against some variants of the π-Cipher family of authenticated ciphers. This family of ciphers is a second-round candidate of the CAESAR competition.

## Key claims (as reported)
- More precisely, we show a key recovery attack with time complexity little higher than 24ω , and low data complexity, against variants of the cipher with ω-bit words, when the internal permutation is reduced to 2.5 rounds.
- In particular, this gives an attack with time complexity 272 against the variant π16-Cipher096 (using 16-bit words) reduced to 2.5 rounds, while the authors claim 96 bits of security with 3 rounds in their second-round submission.
- Therefore, the security margin for this variant of π-Cipher is very limited.
- The attack can also be applied to lightweight variants that are not included in the CAESAR proposal, and use only two rounds.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/97830509 (1).pdf`
- `downloads/97830509.pdf`
