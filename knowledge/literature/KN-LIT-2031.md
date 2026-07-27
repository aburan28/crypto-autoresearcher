---
id: KN-LIT-2031
type: literature
title: "A Differential Fault Attack against Early Rounds of (Triple-)DES"
authors:
  - "Ludger Hemme"
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
Previously proposed differential fault analysis (DFA) techniques against iterated block ciphers mostly exploit computational errors in the last few rounds of the cipher to extract the secret key. In this paper we describe a DFA attack that exploits computational errors in early rounds of a Feistel cipher.

## Key claims (as reported)
- The principle of the attack is to force collisions by inducing faults in intermediate results of the cipher.
- We put this attack into practice against DES implemented on a smart card and extracted the full round key of the first round within a few hours by inducing one bit errors in the second and third round, respectively.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/31560255 (1).pdf`
- `downloads/31560255 (2).pdf`
- `downloads/31560255.pdf`
