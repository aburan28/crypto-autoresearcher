---
id: KN-LIT-4824
type: literature
title: "Luby-Rackoff Ciphers from Weak Round Functions?"
authors: []
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [quantum, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
The Feistel-network is a popular structure underlying many block-ciphers where the cipher is constructed from many simpler rounds, each defined by some function which is derived from the secret key. Luby and Rackoff showed that the three-round Feistel-network – each round instantiated with a pseudorandom function secure against adaptive chosen plaintext attacks (CPA) – is a CPA secure pseudorandom permutation, thus giving some confidence in the soundness of using a Feistel-network to design block-ciphers.

## Key claims (as reported)
- But the round functions used in actual block-ciphers are – for efficiency reasons – far from being pseudorandom.
- We investigate the security of the Feistel-network against CPA distinguishers when the only security guarantee we have for the round functions is that they are secure against non-adaptive chosen plaintext attacks (nCPA).
- We show that in the information-theoretic setting, four rounds with nCPA secure round functions are sufficient (and necessary) to get a CPA secure permutation.
- Unfortunately, this result does not translate into the more interesting pseudorandom setting.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/40040397 (1).pdf`
- `downloads/40040397 (2).pdf`
- `downloads/40040397 (3).pdf`
- `downloads/40040397.pdf`
