---
id: KN-LIT-5846
type: literature
title: "Practical Key Recovery for Discrete-Logarithm Based Authentication Schemes from Random Nonce Bits"
authors:
  - "Aurélie Bauer"
  - "Damien Vergnaud"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, dlp, rsa, side-channel, signature]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We propose statistical cryptanalysis of discrete-logarithm based authentication schemes such as Schnorr identification scheme or Girault-Poupard-Stern identification and signature schemes. We consider two scenarios where an adversary is given some information on the nonces used during the signature generation process or during some identification sessions.

## Key claims (as reported)
- In the first scenario, we assume that some bits of the nonces are known exactly by the adversary, while no information is provided about the other bits.
- We show, for instance, that the GPS scheme with 128-bit security can be broken using only 710 signatures assuming that the adversary knows (on average) one bit per nonce.
- In the second scenario, we assume that all bits of the nonces are obtained from the correct ones by independent bit flipping with some small probability.
- A detailed heuristic analysis is provided, supported by extensive experiments.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/92930279 (1).pdf`
- `downloads/92930279.pdf`
