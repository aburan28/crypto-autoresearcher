---
id: KN-LIT-6176
type: literature
title: "Recovering RSA Secret Keys from Noisy Key Bits with Erasures and Errors"
authors:
  - "Noboru Kunihiro"
  - "Naoyuki Shinohara"
  - "Tetsuya Izu"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, lattice, provable-security, rsa, side-channel]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We discuss how to recover RSA secret keys from noisy key bits with erasures and errors. There are two known algorithms recovering original secret keys from noisy keys.

## Key claims (as reported)
- At Crypto 2009, Heninger and Shacham proposed a method for the case where an erroneous version of secret keys contains only erasures.
- Subsequently, Henecka et al. proposed a method for an erroneous version containing only errors at Crypto 2010.
- For physical attacks such as side-channel and cold boot attacks, we need to study key recovery from a noisy secret key containing both erasures and errors.
- In this paper, we propose a method to recover a secret key from such an erroneous version and analyze the condition for error and erasure rates so that our algorithm succeeds in finding the correct secret key in polynomial time.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/77780178 (1).pdf`
- `downloads/77780178 (2).pdf`
- `downloads/77780178 (3).pdf`
- `downloads/77780178 (4).pdf`
- `downloads/77780178.pdf`
