---
id: KN-LIT-6344
type: literature
title: "RSA meets DPA: Recovering RSA Secret Keys from Noisy Analog Data"
authors:
  - "Noboru Kunihiro"
  - "Junya Honda"
year: null
venue: null
identifiers:
  eprint: null
  doi: null
  arxiv: null
  url: null
tags: [cryptanalysis, rsa, side-channel, symmetric]
confidence: reported
citation_verified: read
added: "2026-07-24"
superseded_by: null
---

## Contribution
We discuss how to recover RSA secret keys from noisy analog data obtained through physical attacks such as cold boot and side channel attacks. Many studies have focused on recovering correct secret keys from noisy binary data.

## Key claims (as reported)
- Obtaining noisy binary keys typically involves first observing the analog data and then obtaining the binary data through quantization process that discards much information pertaining to the correct keys.
- In this paper, we propose two algorithms for recovering correct secret keys from noisy analog data, which are generalized variants of Paterson et al.’s algorithm.
- Our algorithms fully exploit the analog information.
- More precisely, consider observed data which follows the Gaussian distribution with mean (−1)b and variance σ 2 for a secret key bit b.

## Relevance to this program
Recorded for completeness of the local cryptography library. Peripheral to the ECDLP index-calculus program; cite in novelty checks for the tagged areas only.

## Not verified here
Entry generated during the 2026-07-24 bulk seeding pass from the local PDF's first two pages. Title/authors/year/venue were parsed heuristically and may be incomplete or mis-segmented; claims are relayed from the paper's abstract without independent verification. Upgrade to a fully verified entry after a careful read.

## Local copies
- `downloads/87310207 (1).pdf`
- `downloads/87310207 (2).pdf`
- `downloads/87310207 (3).pdf`
- `downloads/87310207.pdf`
